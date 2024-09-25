# 使用官方Python运行时作为父镜像
FROM python:3.9-slim-bullseye

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

# 安装项目依赖和工具，包括 OpenSSL 2.0.27
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends --fix-missing \
        build-essential \
        libssl-dev \
        wget \
        ca-certificates \
        default-jdk \
        && \
    wget https://www.openssl.org/source/openssl-2.0.27.tar.gz && \
    tar -zxf openssl-2.0.27.tar.gz && \
    cd openssl-2.0.27 && \
    ./config --prefix=/usr/local/ssl --openssldir=/usr/local/ssl shared zlib && \
    make && \
    make install && \
    cd .. && \
    rm -rf openssl-2.0.27 openssl-2.0.27.tar.gz && \
    echo "/usr/local/ssl/lib" > /etc/ld.so.conf.d/openssl-2.0.27.conf && \
    ldconfig && \
    pip install --no-cache-dir flask && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置 OpenSSL 环境变量
ENV PATH="/usr/local/ssl/bin:${PATH}"
ENV LD_LIBRARY_PATH="/usr/local/ssl/lib:${LD_LIBRARY_PATH}"

# 创建dist目录
RUN mkdir -p /app/dist

# 暴露端口5000供外部访问
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 运行应用
CMD ["flask", "run"]