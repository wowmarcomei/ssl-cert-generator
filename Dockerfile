# Use the base image we created
FROM wowmarcomei/ssl-cert-generator-base:latest

# Set the working directory
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Install setuptools and Babel
RUN pip install setuptools
RUN pip install babel

# Compile translations
RUN python compile_translations.py

# Expose the port the app runs on
EXPOSE 5000

# Environment variables that can be set at runtime:
# DEFAULT_COUNTRY_CODE
# DEFAULT_ORG_NAME
# DEFAULT_OU_NAME
# DEFAULT_ROOT_CN
# DEFAULT_SUB_CN
# DEFAULT_PASSWORD
# DEFAULT_DURATION_DAYS

# Run the application
CMD ["python", "app.py"]