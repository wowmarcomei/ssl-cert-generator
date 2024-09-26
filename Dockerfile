# Use the official Python runtime as the parent image
FROM python:3.11-slim-bullseye

# Set the working directory
WORKDIR /app

# Copy the project files to the working directory
COPY . /app

# Install project dependencies and tools, including OpenSSL 1.1.1f and default-jdk
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends --fix-missing \
        build-essential \
        libssl-dev \
        wget \
        ca-certificates \
        default-jdk \
        zlib1g-dev \
    && \
    wget https://www.openssl.org/source/old/1.1.1/openssl-1.1.1f.tar.gz && \
    tar -zxf openssl-1.1.1f.tar.gz && \
    cd openssl-1.1.1f && \
    ./config --prefix=/usr/local/ssl --openssldir=/usr/local/ssl shared zlib && \
    make && \
    make install && \
    cd .. && \
    rm -rf openssl-1.1.1f openssl-1.1.1f.tar.gz && \
    echo "/usr/local/ssl/lib" > /etc/ld.so.conf.d/openssl-1.1.1f.conf && \
    ldconfig && \
    pip install --no-cache-dir flask flask-limiter flask-babel && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set OpenSSL environment variables
ENV PATH="/usr/local/ssl/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/ssl/lib:${LD_LIBRARY_PATH}"

# Set Java environment variables
ENV JAVA_HOME="/usr/lib/jvm/default-java"
ENV PATH="$JAVA_HOME/bin:${PATH}"

# Create dist directory
RUN mkdir -p /app/dist

# Expose port 5000 for external access
EXPOSE 5000

# Define environment variables
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV PYTHONUNBUFFERED=1

# Run the application
CMD ["python", "app.py"]