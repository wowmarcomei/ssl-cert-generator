# Use the base image we created
FROM wowmarcomei/ssl-cert-generator-base:latest

# Set the working directory
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Install Babel if not already installed
RUN pip install babel

# Compile translations
RUN python compile_translations.py

# Expose the port the app runs on
EXPOSE 5000

# Run the application
CMD ["python", "app.py"]