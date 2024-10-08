import os
import subprocess
import logging
import shutil
import random
import string

logger = logging.getLogger(__name__)

def run_command(command):
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logger.info(f"Command executed successfully: {' '.join(command)}")
        logger.debug(f"Output: {result.stdout}")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command: {' '.join(command)}")
        logger.error(f"Error output: {e.stderr}")
        raise

def generate_random_name():
    random_bytes = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return f"alias_{random_bytes}"

def generate_certificate(data, cert_output_dir, keytool_path=None):
    try:
        # Clean up the output directory
        for filename in os.listdir(cert_output_dir):
            file_path = os.path.join(cert_output_dir, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                logger.error(f'Failed to delete {file_path}. Reason: {e}')

        # Define file names
        root_crt = 'root.crt'
        root_key = 'root.key'
        sub_crt = "his-ssl-cert.crt"
        sub_key = "his-ssl-cert.key"
        keystore = 'his-server-keystore.pfx'
        truststore = 'his-cacerts.jks'

        # Log the existence of root certificate and key
        logger.info(f"Checking for existing root certificate: {os.path.exists(os.path.join(cert_output_dir, root_crt))}")
        logger.info(f"Checking for existing root key: {os.path.exists(os.path.join(cert_output_dir, root_key))}")

        # Create configuration files
        root_cnf_path = os.path.join(cert_output_dir, 'root.cnf')
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
basicConstraints = critical,CA:TRUE
keyUsage = critical,digitalSignature,keyCertSign,cRLSign
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid:always,issuer
            """)

        sub_cnf_path = os.path.join(cert_output_dir, 'sub.cnf')
        with open(sub_cnf_path, 'w') as f:
            f.write(f"""
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
basicConstraints = critical,CA:FALSE
keyUsage = critical,digitalSignature,keyEncipherment
extendedKeyUsage = serverAuth,clientAuth
subjectKeyIdentifier = hash
authorityKeyIdentifier = keyid,issuer
subjectAltName = @alt_names

[ alt_names ]
DNS.1 = *.{data['cnSub']}
DNS.2 = *.datafabric.svc.cluster.local
DNS.3 = *.headless-datafabric.datafabric.svc.cluster.local
DNS.4 = *.datafabric
DNS.5 = *.headless-datafabric.datafabric
DNS.6 = *.tenant-eureka.his-iam.svc.cluster.local
DNS.7 = *.gaia
DNS.8 = *.gaia-log
DNS.9 = *.gaia-monitoring
DNS.10 = *.his-iam
DNS.11 = *.his-observe
DNS.12 = *.jalor
DNS.13 = *.liveflow
DNS.14 = *.livefunction
DNS.15 = *.liveconnector
DNS.16 = *.monitoring
DNS.17 = *.starling
DNS.18 = *.flashsync
DNS.19 = *.csb
DNS.20 = *.edm
DNS.21 = *.bds
            """)

        result = {}

        # Generate root certificate if not provided
        if not os.path.exists(os.path.join(cert_output_dir, root_crt)) or not os.path.exists(os.path.join(cert_output_dir, root_key)):
            logger.info("Generating new root certificate and key")
            run_command(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-sha256', '-days', str(data['durationDays']),
                        '-keyout', os.path.join(cert_output_dir, root_key), 
                        '-out', os.path.join(cert_output_dir, root_crt), 
                        '-config', root_cnf_path, '-nodes'])
            result['root_crt'] = root_crt
            result['root_key'] = root_key
        else:
            logger.info("Using existing root certificate and key")
            result['root_crt'] = root_crt
            result['root_key'] = root_key

        # Generate sub certificate
        logger.info("Generating sub certificate")
        run_command(['openssl', 'req', '-new', '-newkey', 'rsa:3072', 
                    '-keyout', os.path.join(cert_output_dir, sub_key), 
                    '-out', os.path.join(cert_output_dir, 'sub.csr'),
                    '-config', sub_cnf_path, '-nodes'])
        run_command(['openssl', 'x509', '-req', 
                    '-in', os.path.join(cert_output_dir, 'sub.csr'), 
                    '-CA', os.path.join(cert_output_dir, root_crt), 
                    '-CAkey', os.path.join(cert_output_dir, root_key),
                    '-CAcreateserial', 
                    '-out', os.path.join(cert_output_dir, sub_crt), 
                    '-days', str(data['durationDays']),
                    '-extfile', sub_cnf_path, '-extensions', 'v3_sub'])
        
        result['sub_crt'] = sub_crt
        result['sub_key'] = sub_key

        # Generate Keystore
        logger.info("Generating Keystore")
        alias_name = generate_random_name()
        keystore_password = data.get('keystore_password', ''.join(random.choices(string.ascii_letters + string.digits, k=12)))
        run_command(['openssl', 'pkcs12', '-export', 
                    '-in', os.path.join(cert_output_dir, sub_crt), 
                    '-inkey', os.path.join(cert_output_dir, sub_key),
                    '-out', os.path.join(cert_output_dir, keystore), 
                    '-name', alias_name, '-passout', f'pass:{keystore_password}'])
        
        result['keystore'] = keystore
        result['keystore_password'] = keystore_password
        result['keystore_alias'] = alias_name

        # Generate Truststore if keytool is available
        if keytool_path:
            if not os.path.isfile(keytool_path):
                logger.error(f"Keytool not found at specified path: {keytool_path}")
                raise FileNotFoundError(f"Keytool not found at: {keytool_path}")
            
            root_crt_path = os.path.join(cert_output_dir, root_crt)
            if not os.path.isfile(root_crt_path):
                logger.error(f"Root certificate not found at: {root_crt_path}")
                raise FileNotFoundError(f"Root certificate not found at: {root_crt_path}")
            
            logger.info("Generating Truststore")
            truststore_path = os.path.join(cert_output_dir, truststore)
            keytool_command = [
                keytool_path, '-import', '-alias', alias_name,
                '-file', root_crt_path,
                '-keystore', truststore_path,
                '-storepass', data['password'], '-noprompt'
            ]
            
            try:
                run_command(keytool_command)
                result['truststore'] = truststore
                result['truststore_password'] = data['password']
                result['truststore_alias'] = alias_name
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to generate truststore. Command: {' '.join(keytool_command)}")
                logger.error(f"Error: {str(e)}")
                raise
        else:
            logger.warning("Keytool path not provided. Skipping truststore generation.")

        return result
    except Exception as e:
        logger.exception("Error in generate_certificate function")
        raise