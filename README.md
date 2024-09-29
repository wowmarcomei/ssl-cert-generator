# SSL Certificate Generator

[中文版](README_cn.md)

This is a web-based SSL certificate generator that can create self-signed root certificates and sub-certificates, as well as corresponding keystore and truststore files. It now supports uploading existing root certificates and keys.

## System Requirements

- Python 3.11+
- Flask
- Flask-Limiter
- Flask-Babel
- OpenSSL 1.1.1f
- Java (for keytool command)

Or

- Docker

## File Structure

```
.
├── app.py
├── config.py
├── cert_generator.py
├── static/
│   ├── styles.css
│   └── script.js
├── templates/
│   └── index.html
├── dist/  (auto-created)
├── Dockerfile
├── Dockerfile.base
├── test_cert_generator.py
├── compile_translations.py
├── translations/
│   ├── en/
│   │   └── LC_MESSAGES/
│   │       ├── messages.po
│   │       └── messages.mo
│   └── zh/
│       └── LC_MESSAGES/
│           ├── messages.po
│           └── messages.mo
├── .github/
│   └── workflows/
│       ├── build-base-image.yml
│       └── build-app-image.yml
└── README.md
```

## File Descriptions

- `app.py`: Main application file containing Flask routes and primary logic
- `config.py`: Configuration file containing application settings
- `cert_generator.py`: Certificate generation logic
- `static/`: Static file directory
- `templates/`: HTML template directory
- `dist/`: Directory for generated certificates and key stores
- `Dockerfile`: Dockerfile for building the application image
- `Dockerfile.base`: Dockerfile for building the base image
- `test_cert_generator.py`: Script for testing certificate generation functionality
- `compile_translations.py`: Script for compiling translation files
- `translations/`: Contains translation files for different languages

## New Features

- Support for uploading existing root certificates and key files
- Custom password setting for keystore and truststore
- More certificate generation options and flexibility
- Optimized Docker build process using a base image for faster builds
- Multi-language support (currently English and Chinese)
- Support for setting certificate default values via environment variables

## Local Installation and Running

1. Clone this repository or download the source code.

2. Install the required Python packages:

   ```
   pip install flask flask-limiter flask-babel
   ```

3. Ensure OpenSSL 1.1.1f and Java are installed on your system.

4. Set environment variables (optional):
   ```
   export DEBUG=True
   export HOST=0.0.0.0
   export PORT=5000
   export CERT_OUTPUT_DIR=dist
   export SECRET_KEY=your-secret-key-here
   export KEYTOOL_PATH=/path/to/keytool  # If keytool is not in the default path
   ```

5. Compile translation files:

   ```
   python compile_translations.py
   ```

6. Run the Flask application:

   ```
   python app.py
   ```

7. Open a web browser and visit http://localhost:5000

## Using Docker

We now use a two-stage build process to optimize Docker image building. If you want to use Docker, follow these steps to build and run the container:

1. Build the base image (only needed for the first build or when the base environment changes):

   ```
   docker build -t ssl-cert-generator-base:latest -f Dockerfile.base .
   ```

2. Build the application image:

   ```
   docker build -t ssl-cert-generator:latest .
   ```

3. Run the Docker container:

   ```
   docker run -p 5000:5000 ssl-cert-generator:latest
   ```

   If you want to set default values for the certificates, you can use environment variables:

   ```
   docker run -p 5000:5000 \
     -e DEFAULT_COUNTRY_CODE=US \
     -e DEFAULT_ORG_NAME=MyOrganization \
     -e DEFAULT_OU_NAME="IT Department" \
     -e DEFAULT_ROOT_CN="My Root CA" \
     -e DEFAULT_SUB_CN=example.com \
     -e DEFAULT_PASSWORD=mysecretpassword \
     -e DEFAULT_DURATION_DAYS=365 \
     ssl-cert-generator:latest
   ```

4. Open a web browser and visit http://localhost:5000

Note: Java and keytool are already configured in the Docker environment, no additional setup is needed.

## Configuring keytool path

By default, the application will try to use keytool from the system PATH. If keytool is not in the default path or you want to use a specific version of keytool, you can set it as follows:

1. Before running the application, set the KEYTOOL_PATH environment variable:
   ```
   export KEYTOOL_PATH=/path/to/your/keytool
   ```

2. If using Docker, you can set the environment variable when running the container using the -e parameter:
   ```
   docker run -p 5000:5000 -e KEYTOOL_PATH=/path/to/your/keytool ssl-cert-generator:latest
   ```

## Translations

This project supports multiple languages, currently including English and Chinese. Translation files are located in the `translations/` directory.

### Adding New Translations

1. Create a subdirectory for the new language in the `translations/` directory, e.g., `translations/fr/` for French.
2. Create an `LC_MESSAGES/` subdirectory in the newly created language directory.
3. Copy the `messages.po` file to the new `LC_MESSAGES/` directory.
4. Edit the `messages.po` file to add translations for the new language.

### Compiling Translation Files

After making changes to translation files, they need to be compiled to generate `.mo` files. You can compile translations as follows:

1. In the local development environment:
   ```
   python compile_translations.py
   ```

2. During the Docker build process:
   Translation files are automatically compiled during Docker image building. No manual operation is required.

## Usage Instructions

1. Access the web interface and fill out the certificate information form.
2. If you have existing root certificates and keys, you can upload them in the corresponding fields.
3. Set the validity period for the certificate (in days), maximum 3650 days.
4. Set passwords for keystore and truststore.
5. Click the "Generate Certificate" button.
6. After generation is complete, you will see a list of generated files, password information, and download links.
7. All generated files are saved in the 'dist' directory.

## GitHub Actions Automatic Build and Push

This project contains two GitHub Actions workflows for automatically building and pushing Docker images to GitHub Container Registry and Docker Hub (if configured).

1. `build-base-image.yml`: Build and push the base image
   - Trigger conditions: When the Dockerfile.base file changes, or manually triggered
   - Function: Build and push the base image
   - Tags:
     - latest
     - Date tag (format: YYYYMMDD, e.g., 20240929)

2. `build-app-image.yml`: Build and push the application image
   - Trigger conditions:
     a) When the build-base-image workflow completes
     b) When code is pushed to the master branch (except for Dockerfile.base changes)
     c) When a pull request is created to the master branch
     d) Manually triggered
   - Function: Build and push the application image, using the latest base image
   - Tags:
     - latest
     - Date tag (format: YYYYMMDD, e.g., 20240929)

This setup ensures that the application image is always built based on the latest base image, while also allowing independent updates to the application image when the base image hasn't changed. Using date tags makes it easy to track different versions of the images.

### Setup Steps

1. Get a Docker Hub access token:
   - Log in to your Docker Hub account
   - Click on your username, then select "Account Settings"
   - In the left menu, click on "Security"
   - In the "Access Tokens" section, click "New Access Token"
   - Give the token a name and select appropriate permissions (at least "Read, Write, Delete" permissions are needed)
   - Click "Generate" and copy the generated token
   - Add this token as the value for `DOCKERHUB_TOKEN` in GitHub Secrets

2. In your GitHub repository, go to "Settings" > "Security" > "Secrets and variables" > "Actions".

3. Add the following secrets:
   - `DOCKERHUB_USERNAME`: Your Docker Hub username
   - `DOCKERHUB_TOKEN`: Your Docker Hub access token (not your password)

   Note: If you don't have a Docker Hub account or don't want to push to Docker Hub, you can skip this step. The Action will automatically only push to GitHub Container Registry.

4. Ensure your GitHub account has permission to push to GitHub Container Registry. If not, you may need to enable it in your personal settings.

5. Push code to the master branch or create a pull request to the master branch, this will trigger GitHub Actions.

6. Actions will automatically build Docker images for x86 and ARM architectures and push them to the configured repositories.

Note: If you haven't set up Docker Hub credentials, Actions will only push to GitHub Container Registry.

## Error Handling

If any problems occur during the certificate generation process, error messages will be displayed on the web page.

To view more detailed error logs:

1. If running locally, check the terminal window running `python app.py`.
2. If using Docker, you can use `docker logs <container_id>` to view logs.

## Notes

- The certificates generated by this system are self-signed and not suitable for production environments. In actual use, you may need to use certificates signed by a trusted certificate authority (CA).
- Ensure you follow relevant security best practices when using this system, especially when handling private keys and passwords.
- This system implements basic rate limiting, but stronger security measures such as user authentication and authorization may be needed when used in a production environment.

## Contributions

Issue reports and pull requests are welcome to help improve this project.

## License

[MIT License](https://opensource.org/licenses/MIT)