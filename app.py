import os
import subprocess
import logging
import shutil
from flask import Flask, request, jsonify, send_file, render_template

app = Flask(__name__, static_url_path='', static_folder='static')

# 设置日志
logging.basicConfig(level=logging.DEBUG)

# 设置证书输出目录
CERT_OUTPUT_DIR = 'dist'
if not os.path.exists(CERT_OUTPUT_DIR):
    os.makedirs(CERT_OUTPUT_DIR)

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(f"Command executed successfully: {' '.join(command)}")
        logging.debug(f"Output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        logging.error(f"Error executing command: {' '.join(command)}")
        logging.error(f"Error output: {e.stderr}")
        raise

def generate_certificate(data):
    try:
        # 清理dist目录
        for filename in os.listdir(CERT_OUTPUT_DIR):
            file_path = os.path.join(CERT_OUTPUT_DIR, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logging.error(f'Failed to delete {file_path}. Reason: {e}')

        # 创建配置文件
        root_cnf_path = os.path.join(CERT_OUTPUT_DIR, 'root.cnf')
        with open(root_cnf_path, 'w') as f:
            f.write(f"""
[ req ]
distinguished_name = req_distinguished_name
x509_extensions = v3_ca
prompt = no

[ req_distinguished_name ]
C = {data['countryName']}
O = {data['orgName']}
OU = {data['ouName']}
CN = {data['cnRoot']}

[ v3_ca ]
basicConstraints = CA:TRUE
keyUsage = digitalSignature, keyCertSign, cRLSign
            """)

        sub_cnf_path = os.path.join(CERT_OUTPUT_DIR, 'sub.cnf')
        with open(sub_cnf_path, 'w') as f:
            f.write(f"""
[ CA_default ]
certificate = root.crt
private_key = root.key

[ req ]
distinguished_name = req_distinguished_name
x509_extensions = v3_sub
prompt = no

[ req_distinguished_name ]
C = {data['countryName']}
O = {data['orgName']}
OU = {data['ouName']}
CN = *.{data['cnSub']}

[ v3_sub ]
basicConstraints = CA:FALSE
keyUsage = nonRepudiation, digitalSignature, keyEncipherment, dataEncipherment, keyAgreement
extendedKeyUsage = serverAuth, clientAuth
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = *.{data['cnSub']}
            """)

        # 生成根证书
        run_command(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-sha256', '-days', str(data['durationDays']),
                    '-keyout', os.path.join(CERT_OUTPUT_DIR, 'root.key'), 
                    '-out', os.path.join(CERT_OUTPUT_DIR, 'root.crt'), 
                    '-config', root_cnf_path, '-nodes'])

        # 生成子证书
        run_command(['openssl', 'req', '-new', '-newkey', 'rsa:3072', 
                    '-keyout', os.path.join(CERT_OUTPUT_DIR, 'his-ssl-cert.key'), 
                    '-out', os.path.join(CERT_OUTPUT_DIR, 'sub.csr'),
                    '-config', sub_cnf_path, '-nodes'])
        run_command(['openssl', 'x509', '-req', 
                    '-in', os.path.join(CERT_OUTPUT_DIR, 'sub.csr'), 
                    '-CA', os.path.join(CERT_OUTPUT_DIR, 'root.crt'), 
                    '-CAkey', os.path.join(CERT_OUTPUT_DIR, 'root.key'),
                    '-CAcreateserial', 
                    '-out', os.path.join(CERT_OUTPUT_DIR, 'his-ssl-cert.crt'), 
                    '-days', str(data['durationDays']),
                    '-extensions', 'v3_sub', '-extfile', sub_cnf_path])

        # 生成 Keystore
        run_command(['openssl', 'pkcs12', '-export', 
                    '-in', os.path.join(CERT_OUTPUT_DIR, 'his-ssl-cert.crt'), 
                    '-inkey', os.path.join(CERT_OUTPUT_DIR, 'his-ssl-cert.key'),
                    '-out', os.path.join(CERT_OUTPUT_DIR, 'his-server-keystore.pfx'), 
                    '-name', 'alias', '-passout', f'pass:{data["password"]}'])

        # 生成 Truststore
        run_command(['keytool', '-import', '-alias', 'alias', 
                    '-file', os.path.join(CERT_OUTPUT_DIR, 'root.crt'), 
                    '-keystore', os.path.join(CERT_OUTPUT_DIR, 'his-cacerts.jks'),
                    '-storepass', data['password'], '-noprompt'])

        return {
            'root_crt': 'root.crt',
            'root_key': 'root.key',
            'sub_crt': 'his-ssl-cert.crt',
            'sub_key': 'his-ssl-cert.key',
            'keystore': 'his-server-keystore.pfx',
            'truststore': 'his-cacerts.jks'
        }
    except Exception as e:
        logging.exception("Error in generate_certificate function")
        raise

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate():
    data = request.json
    try:
        files = generate_certificate(data)
        return jsonify(files), 200
    except Exception as e:
        logging.exception("Error in generate route")
        return jsonify({'error': str(e)}), 500

@app.route('/download/<filename>', methods=['GET'])
def download(filename):
    try:
        return send_file(os.path.join(CERT_OUTPUT_DIR, filename), as_attachment=True)
    except Exception as e:
        logging.exception(f"Error downloading file: {filename}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)