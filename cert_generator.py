import os
import subprocess
import logging
import shutil

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
DNS.2 = {data['cnSub']}
            """)

        # Generate root certificate
        run_command(['openssl', 'req', '-x509', '-newkey', 'rsa:4096', '-sha256', '-days', str(data['durationDays']),
                    '-keyout', os.path.join(cert_output_dir, 'root.key'), 
                    '-out', os.path.join(cert_output_dir, 'root.crt'), 
                    '-config', root_cnf_path, '-nodes'])

        # Generate sub certificate
        run_command(['openssl', 'req', '-new', '-newkey', 'rsa:3072', 
                    '-keyout', os.path.join(cert_output_dir, 'his-ssl-cert.key'), 
                    '-out', os.path.join(cert_output_dir, 'sub.csr'),
                    '-config', sub_cnf_path, '-nodes'])
        run_command(['openssl', 'x509', '-req', 
                    '-in', os.path.join(cert_output_dir, 'sub.csr'), 
                    '-CA', os.path.join(cert_output_dir, 'root.crt'), 
                    '-CAkey', os.path.join(cert_output_dir, 'root.key'),
                    '-CAcreateserial', 
                    '-out', os.path.join(cert_output_dir, 'his-ssl-cert.crt'), 
                    '-days', str(data['durationDays']),
                    '-extfile', sub_cnf_path, '-extensions', 'v3_sub'])

        # Generate Keystore
        run_command(['openssl', 'pkcs12', '-export', 
                    '-in', os.path.join(cert_output_dir, 'his-ssl-cert.crt'), 
                    '-inkey', os.path.join(cert_output_dir, 'his-ssl-cert.key'),
                    '-out', os.path.join(cert_output_dir, 'his-server-keystore.pfx'), 
                    '-name', 'alias', '-passout', f'pass:{data["password"]}'])

        result = {
            'root_crt': 'root.crt',
            'root_key': 'root.key',
            'sub_crt': 'his-ssl-cert.crt',
            'sub_key': 'his-ssl-cert.key',
            'keystore': 'his-server-keystore.pfx'
        }

        # Generate Truststore if keytool is available
        if keytool_path:
            try:
                run_command([keytool_path, '-import', '-alias', 'alias', 
                            '-file', os.path.join(cert_output_dir, 'root.crt'), 
                            '-keystore', os.path.join(cert_output_dir, 'his-cacerts.jks'),
                            '-storepass', data['password'], '-noprompt'])
                result['truststore'] = 'his-cacerts.jks'
            except Exception as e:
                logger.warning(f"Failed to generate truststore: {str(e)}")
        else:
            logger.warning("Keytool path not provided. Skipping truststore generation.")

        return result
    except Exception as e:
        logger.exception("Error in generate_certificate function")
        raise