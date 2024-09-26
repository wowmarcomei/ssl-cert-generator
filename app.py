import os
import subprocess
import logging
import shutil
from flask import Flask, request, jsonify, send_file, render_template
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import re
from config import Config
from cert_generator import generate_certificate

app = Flask(__name__, static_url_path='', static_folder='static')
app.config.from_object(Config)

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

def validate_input(data):
    """Validate user input data"""
    if not all(key in data for key in ['countryName', 'orgName', 'ouName', 'cnRoot', 'cnSub', 'durationDays', 'password']):
        raise ValueError("Missing required fields")
    
    if not re.match(r'^[A-Z]{2}$', data['countryName']):
        raise ValueError("Invalid country name. Must be 2 uppercase letters.")
    
    if not re.match(r'^[a-zA-Z0-9\s]{1,64}$', data['orgName']):
        raise ValueError("Invalid organization name")
    
    if not re.match(r'^[a-zA-Z0-9\s]{1,64}$', data['ouName']):
        raise ValueError("Invalid organizational unit name")
    
    if not re.match(r'^[a-zA-Z0-9.-]{1,64}$', data['cnRoot']):
        raise ValueError("Invalid root common name")
    
    if not re.match(r'^[a-zA-Z0-9.-]{1,64}$', data['cnSub']):
        raise ValueError("Invalid sub common name")
    
    try:
        duration_days = int(data['durationDays'])
        if duration_days <= 0 or duration_days > 3650:
            raise ValueError("Invalid duration. Must be a positive integer not exceeding 3650 days.")
    except ValueError:
        raise ValueError("Invalid duration. Must be a positive integer not exceeding 3650 days.")
    
    if len(data['password']) < 8:
        raise ValueError("Password must be at least 8 characters long")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
@limiter.limit("10 per minute")
def generate():
    data = request.json
    try:
        validate_input(data)
        # Convert durationDays to int after validation
        data['durationDays'] = int(data['durationDays'])
        files = generate_certificate(data, app.config['CERT_OUTPUT_DIR'], KEYTOOL_PATH)
        return jsonify(files), 200
    except ValueError as ve:
        logger.warning(f"Input validation error: {str(ve)}")
        return jsonify({'error': str(ve)}), 400
    except subprocess.CalledProcessError as ce:
        logger.error(f"Command execution error: {ce.stderr}")
        return jsonify({'error': 'Certificate generation failed. Please check your inputs and try again.'}), 500
    except Exception as e:
        logger.exception("Unexpected error in generate route")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500

@app.route('/download/<filename>', methods=['GET'])
@limiter.limit("50 per minute")
def download(filename):
    try:
        file_path = os.path.join(app.config['CERT_OUTPUT_DIR'], filename)
        if not os.path.exists(file_path):
            logger.warning(f"File not found: {filename}")
            return jsonify({'error': 'File not found'}), 404
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.exception(f"Error downloading file: {filename}")
        return jsonify({'error': 'An error occurred while downloading the file'}), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    return jsonify({'error': 'Rate limit exceeded. Please try again later.'}), 429

if __name__ == '__main__':
    app.run(debug=app.config['DEBUG'], host=app.config['HOST'], port=app.config['PORT'])