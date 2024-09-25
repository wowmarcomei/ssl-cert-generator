# 使用官方Python运行时作为父镜像
FROM python:3.9-slim-bullseye

# 设置工作目录
WORKDIR /app

# 复制项目文件到工作目录
COPY . /app

# 安装项目依赖和工具
RUN set -ex; \
    apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y --no-install-recommends --fix-missing \
        build-essential \
        libssl-dev \
        wget \
        ca-certificates \
        && \
    apt-get install -y --no-install-recommends --fix-missing \
        default-jdk \
        && \
    pip install --no-cache-dir flask && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 创建dist目录
RUN mkdir -p /app/dist

# 暴露端口5000供外部访问
EXPOSE 5000

# 定义环境变量
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 运行应用
CMD ["flask", "run"]