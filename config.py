import os

class Config:
    # Flask settings
    DEBUG = os.environ.get('DEBUG', 'False').lower() == 'true'
    HOST = os.environ.get('HOST', '0.0.0.0')
    PORT = int(os.environ.get('PORT', 5000))

    # Certificate settings
    CERT_OUTPUT_DIR = os.environ.get('CERT_OUTPUT_DIR', 'dist')

    # Security settings
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your-secret-key-here')  # Change this in production!

    # Rate limiting settings
    RATELIMIT_STORAGE_URL = os.environ.get('RATELIMIT_STORAGE_URL', 'memory://')

    # Logging settings
    LOG_LEVEL = os.environ.get('LOG_LEVEL', 'INFO')

    # OpenSSL settings
    OPENSSL_CONFIG_DIR = os.environ.get('OPENSSL_CONFIG_DIR', '/etc/ssl')

    # Java keytool settings
    JAVA_HOME = os.environ.get('JAVA_HOME', '/usr/lib/jvm/default-java')