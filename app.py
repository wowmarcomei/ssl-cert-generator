import os
import subprocess
import logging
from datetime import datetime
import shutil
import zipfile
import tempfile
from flask import Flask, request, jsonify, send_file, render_template, g, session
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import Babel, gettext as _
import re
from werkzeug.utils import secure_filename
from config import Config
from cert_generator import generate_certificate

app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object(Config)
app.secret_key = 'your_secret_key_here'  # Add this line for session support

# Set up rate limiting
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per day", "50 per hour"])
limiter.init_app(app)

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure certificate output directory exists
if not os.path.exists(app.config['CERT_OUTPUT_DIR']):
    os.makedirs(app.config['CERT_OUTPUT_DIR'])

# Get keytool path from environment variable or use default
KEYTOOL_PATH = os.environ.get('KEYTOOL_PATH', '/usr/bin/keytool')

def get_locale():
    if 'language' in session:
        return session['language']
    return request.accept_languages.best_match(['en', 'zh'])

# Set up Babel
babel = Babel(app, locale_selector=get_locale)

# Make get_locale available to templates
app.jinja_env.globals.update(get_locale=get_locale)

@app.route('/set_language/<language>')
def set_language(language):
    session['language'] = language
    return jsonify({'success': True})

@app.route('/get_translations')
def get_translations():
    translations = {
        'Generating certificate, please wait...': _('Generating certificate, please wait...'),
        'Unknown error': _('Unknown error'),
        'An error occurred while generating the certificate: ': _('An error occurred while generating the certificate: '),
        'Certificate generation successful!': _('Certificate generation successful!'),
        'Generated files:': _('Generated files:'),
        'Download': _('Download'),
        'No file chosen': _('No file chosen'),
        'Choose File': _('Choose File'),
        'Two-letter country code (e.g., CN for China)': _('Two-letter country code (e.g., CN for China)'),
        'Your organization name': _('Your organization name'),
        'Your department or unit name': _('Your department or unit name'),
        'Common name for the root certificate': _('Common name for the root certificate'),
        'Common name for the sub certificate (usually your domain name)': _('Common name for the sub certificate (usually your domain name)'),
        'Password for keystore and truststore': _('Password for keystore and truststore'),
        'Validity period of the certificate (in days, maximum 3650 days)': _('Validity period of the certificate (in days, maximum 3650 days)'),
        'If you have an existing root certificate, you can upload it': _('If you have an existing root certificate, you can upload it'),
        'If you uploaded a root certificate, please also upload the corresponding key': _('If you uploaded a root certificate, please also upload the corresponding key'),
        'Download Log': _('Download Log'),
        'Download All Files': _('Download All Files'),
    }
    return jsonify(translations)

def validate_input(data):
    """Validate user input data"""
    required_fields = ['countryName', 'orgName', 'ouName', 'cnRoot', 'cnSub', 'durationDays', 'password']
    if not all(key in data for key in required_fields):
        raise ValueError(_("Missing required fields"))
    
    if not re.match(r'^[A-Z]{2}$', data['countryName']):
        raise ValueError(_("Invalid country name. Must be 2 uppercase letters."))
    
    if not re.match(r'^[a-zA-Z0-9\s]{1,64}$', data['orgName']):
        raise ValueError(_("Invalid organization name"))
    
    if not re.match(r'^[a-zA-Z0-9\s]{1,64}$', data['ouName']):
        raise ValueError(_("Invalid organizational unit name"))
    
    if not re.match(r'^[a-zA-Z0-9.-]{1,64}$', data['cnRoot']):
        raise ValueError(_("Invalid root common name"))
    
    if not re.match(r'^[a-zA-Z0-9.-]{1,64}$', data['cnSub']):
        raise ValueError(_("Invalid sub common name"))
    
    try:
        duration_days = int(data['durationDays'])
        if duration_days <= 0 or duration_days > 3650:
            raise ValueError(_("Invalid duration. Must be a positive integer not exceeding 3650 days."))
    except ValueError:
        raise ValueError(_("Invalid duration. Must be a positive integer not exceeding 3650 days."))
    
    if len(data['password']) < 8:
        raise ValueError(_("Password must be at least 8 characters long"))

def save_log(log_content):
    """Save log content to a file in Markdown format"""
    log_filename = f"cert_generation_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    log_path = os.path.join(app.config['CERT_OUTPUT_DIR'], log_filename)
    with open(log_path, 'w') as log_file:
        log_file.write(f"# Certificate Generation Log\n\n")
        log_file.write(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        log_file.write("## Input Data\n\n")
        for key, value in log_content['input_data'].items():
            log_file.write(f"- **{key}**: {value}\n")
        log_file.write("\n## Generated Files\n\n")
        for key, value in log_content['generated_files'].items():
            log_file.write(f"- **{key}**: {value}\n")
    return log_filename

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@limiter.limit("10 per minute")
def generate():
    try:
        data = request.form.to_dict()
        validate_input(data)
        
        # Handle file uploads
        if 'root_cert' in request.files:
            root_cert = request.files['root_cert']
            if root_cert.filename != '':
                root_cert_path = os.path.join(app.config['CERT_OUTPUT_DIR'], secure_filename(root_cert.filename))
                root_cert.save(root_cert_path)
                data['existing_root_cert'] = root_cert_path

        if 'root_key' in request.files:
            root_key = request.files['root_key']
            if root_key.filename != '':
                root_key_path = os.path.join(app.config['CERT_OUTPUT_DIR'], secure_filename(root_key.filename))
                root_key.save(root_key_path)
                data['existing_root_key'] = root_key_path

        # Convert durationDays to int after validation
        data['durationDays'] = int(data['durationDays'])
        
        files = generate_certificate(data, app.config['CERT_OUTPUT_DIR'], KEYTOOL_PATH)
        
        # Generate and save log
        log_content = {
            'input_data': data,
            'generated_files': files
        }
        log_filename = save_log(log_content)
        
        files['log'] = log_filename
        return jsonify({'success': True, 'data': files}), 200
    except ValueError as ve:
        logger.warning(f"Input validation error: {str(ve)}")
        return jsonify({'success': False, 'error': str(ve)}), 400
    except subprocess.CalledProcessError as ce:
        logger.error(f"Command execution error: {ce.stderr}")
        return jsonify({'success': False, 'error': _('Certificate generation failed. Please check your inputs and try again.')}), 500
    except Exception as e:
        logger.exception("Unexpected error in generate route")
        return jsonify({'success': False, 'error': _('An unexpected error occurred. Please try again later.')}), 500

@app.route('/download/<filename>', methods=['GET'])
@limiter.limit("50 per minute")
def download(filename):
    try:
        file_path = os.path.join(app.config['CERT_OUTPUT_DIR'], filename)
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {filename}")
            return jsonify({'success': False, 'error': _('File not found')}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.exception(f"Error downloading file: {filename}")
        return jsonify({'success': False, 'error': _('An error occurred while downloading the file')}), 500

@app.route('/download_all', methods=['POST'])
@limiter.limit("10 per minute")
def download_all():
    try:
        files = request.json.get('files', [])
        if not files:
            return jsonify({'success': False, 'error': _('No files to download')}), 400

        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            with zipfile.ZipFile(temp_file, 'w') as zipf:
                for filename in files:
                    file_path = os.path.join(app.config['CERT_OUTPUT_DIR'], filename)
                    if os.path.exists(file_path):
                        zipf.write(file_path, filename)

        return send_file(temp_file.name, as_attachment=True, download_name='all_certificates.zip')
    except Exception as e:
        logger.exception("Error creating zip file")
        return jsonify({'success': False, 'error': _('An error occurred while creating the zip file')}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'success': False, 'error': _('Rate limit exceeded. Please try again later.')}), 429

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])