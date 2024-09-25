# 使用官方Python运行时作为父镜像
FROM python:3.9-slim-buster

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

# 安装项目依赖和编译工具
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        wget \
        default-jdk \
        && \
    pip install --no-cache-dir flask && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 下载并安装 OpenSSL 2.0.9
RUN wget https://github.com/openssl/openssl/archive/refs/tags/OpenSSL_2_0_9.tar.gz && \
    tar -zxf OpenSSL_2_0_9.tar.gz && \
    cd openssl-OpenSSL_2_0_9 && \
    ./config && \
    make && \
    make install && \
    cd .. && \
    rm -rf openssl-OpenSSL_2_0_9 OpenSSL_2_0_9.tar.gz && \
    ldconfig

# 创建dist目录
RUN mkdir -p /app/dist

# 暴露端口5000供外部访问
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV LD_LIBRARY_PATH=/usr/local/lib

# 运行应用
CMD ["flask", "run"]