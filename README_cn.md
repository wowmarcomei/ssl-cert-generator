# SSL 证书生成器

[English Version](README.md)

这是一个基于Web的SSL证书生成器，可以创建自签名的根证书和子证书，以及相应的keystore和truststore文件。现在支持上传现有的根证书和密钥。

## 系统要求

- Python 3.11+
- Flask
- Flask-Limiter
- Flask-Babel
- OpenSSL 1.1.1f
- Java（用于keytool命令）

或者

- Docker

## 文件结构

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
├── dist/  (自动创建)
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

## 文件说明

- `app.py`: 主应用文件，包含Flask路由和主要逻辑
- `config.py`: 配置文件，包含应用程序的设置
- `cert_generator.py`: 证书生成逻辑
- `static/`: 静态文件目录
- `templates/`: HTML模板目录
- `dist/`: 生成的证书和密钥存储目录
- `Dockerfile`: 用于构建应用镜像的Dockerfile
- `Dockerfile.base`: 用于构建基础镜像的Dockerfile
- `test_cert_generator.py`: 用于测试证书生成功能的脚本
- `compile_translations.py`: 用于编译翻译文件的脚本
- `translations/`: 包含不同语言的翻译文件

## 新功能

- 支持上传现有的根证书和密钥文件
- 可以为keystore和truststore设置自定义密码
- 增加了更多的证书生成选项和灵活性
- 优化的Docker构建过程，使用基础镜像加速构建
- 支持多语言（目前支持英语和中文）
- 支持通过环境变量设置证书默认值

## 本地安装和运行

1. 克隆此仓库或下载源代码。

2. 安装所需的Python包：

   ```
   pip install flask flask-limiter flask-babel setuptools
   ```

3. 确保系统中已安装OpenSSL 1.1.1f和Java。

4. 设置环境变量（可选）：
   ```
   export DEBUG=True
   export HOST=0.0.0.0
   export PORT=5000
   export CERT_OUTPUT_DIR=dist
   export SECRET_KEY=your-secret-key-here
   export KEYTOOL_PATH=/path/to/keytool  # 如果keytool不在默认路径
   ```

5. 编译翻译文件：

   ```
   python compile_translations.py
   ```

6. 运行Flask应用：

   ```
   python app.py
   ```

7. 打开Web浏览器，访问 http://localhost:5000

## 使用Docker

我们现在使用两阶段构建过程来优化Docker镜像构建。如果你想使用Docker，可以按照以下步骤构建和运行容器：

1. 构建基础镜像（仅在首次构建或基础环境变更时需要）：

   ```
   docker build -t ssl-cert-generator-base:latest -f Dockerfile.base .
   ```

2. 构建应用镜像：

   ```
   docker build -t ssl-cert-generator:latest .
   ```

3. 运行Docker容器：

   ```
   docker run -d -p 5000:5000 ssl-cert-generator:latest
   ```

   如果你想设置证书的默认值，可以使用环境变量：

   ```
   docker run -d -p 5000:5000 \
     -e DEFAULT_COUNTRY_CODE=US \
     -e DEFAULT_ORG_NAME=MyOrganization \
     -e DEFAULT_OU_NAME="IT Department" \
     -e DEFAULT_ROOT_CN="My Root CA" \
     -e DEFAULT_SUB_CN=example.com \
     -e DEFAULT_PASSWORD=mysecretpassword \
     -e DEFAULT_DURATION_DAYS=365 \
     ssl-cert-generator:latest
   ```

   如果使用我编译好的镜像，可改为：

   ```
   #使用默认参数
   docker run -d -p 5000:5000 wowmarcomei/ssl-cert-generator:latest

   #使用指定参数
   docker run -d -p 5000:5000 \
     -e DEFAULT_COUNTRY_CODE=CN \
     -e DEFAULT_ORG_NAME=MyOrganization \
     -e DEFAULT_OU_NAME="IT Department" \
     -e DEFAULT_ROOT_CN="My Root CA" \
     -e DEFAULT_SUB_CN=example.com \
     -e DEFAULT_PASSWORD=mysecretpassword \
     -e DEFAULT_DURATION_DAYS=365 \
     wowmarcomei/ssl-cert-generator:latest
   ```

4. 打开Web浏览器，访问 http://localhost:5000

注意：Docker环境中已经配置了Java和keytool，无需额外设置。

## 配置keytool路径

默认情况下，应用程序会尝试使用系统PATH中的keytool。如果keytool不在默认路径或你想使用特定版本的keytool，可以通过以下方式设置：

1. 在运行应用程序之前，设置KEYTOOL_PATH环境变量：
   ```
   export KEYTOOL_PATH=/path/to/your/keytool
   ```

2. 如果使用Docker，可以在运行容器时通过-e参数设置环境变量：
   ```
   docker run -p 5000:5000 -e KEYTOOL_PATH=/path/to/your/keytool ssl-cert-generator:latest
   ```

## 翻译

本项目支持多语言，目前包括英语和中文。翻译文件位于 `translations/` 目录下。

### 添加新的翻译

1. 在 `translations/` 目录下为新语言创建一个子目录，例如 `translations/fr/` 用于法语。
2. 在新创建的语言目录中创建 `LC_MESSAGES/` 子目录。
3. 复制 `messages.po` 文件到新的 `LC_MESSAGES/` 目录中。
4. 编辑 `messages.po` 文件，添加新语言的翻译。

### 编译翻译文件

在对翻译文件进行更改后，需要编译它们以生成 `.mo` 文件。可以通过以下方式编译翻译：

1. 在本地开发环境中：
   ```
   python compile_translations.py
   ```

2. 在 Docker 构建过程中：
   翻译文件会在 Docker 镜像构建过程中自动编译。无需手动操作。

## 使用说明

1. 访问Web界面，填写证书信息表单。
2. 如果你有现有的根证书和密钥，可以在相应的字段上传这些文件。
3. 设置证书的有效期（天数），最长为3650天。
4. 为keystore和truststore设置密码。
5. 点击"生成证书"按钮。
6. 生成完成后，你将看到生成的文件列表、密码信息和下载链接。
7. 所有生成的文件都保存在'dist'目录中。

## GitHub Actions 自动构建和推送

本项目包含两个GitHub Actions工作流程，用于自动构建和推送Docker镜像到GitHub Container Registry和Docker Hub（如果配置）。

1. `build-base-image.yml`: 构建和推送基础镜像
   - 触发条件：当 Dockerfile.base 文件发生变化时，或手动触发
   - 作用：构建并推送基础镜像
   - 标签：
     - latest
     - 日期标签（格式：YYYYMMDD，例如 20240929）

2. `build-app-image.yml`: 构建和推送应用镜像
   - 触发条件：
     a) 当 build-base-image 工作流完成时
     b) 当代码推送到 master 分支时（除了 Dockerfile.base 的变化）
     c) 当创建 pull request 到 master 分支时
     d) 手动触发
   - 作用：构建并推送应用镜像，使用最新的基础镜像
   - 标签：
     - latest
     - 日期标签（格式：YYYYMMDD，例如 20240929）

这种设置确保了应用镜像总是基于最新的基础镜像构建，同时也允许在基础镜像没有变化的情况下独立更新应用镜像。使用日期标签可以方便地追踪不同版本的镜像。

### 设置步骤

1. 获取Docker Hub访问令牌：
   - 登录到你的Docker Hub账户
   - 点击你的用户名，然后选择 "Account Settings"
   - 在左侧菜单中，点击 "Security"
   - 在 "Access Tokens" 部分，点击 "New Access Token"
   - 给token起一个名字，选择适当的权限（至少需要"Read, Write, Delete"权限）
   - 点击 "Generate" 并复制生成的token
   - 将这个token作为 `DOCKERHUB_TOKEN` 的值添加到GitHub Secrets中

2. 在GitHub仓库中，进入 "Settings" > "Security" >  "Secrets and variables" > "Actions"。

3. 添加以下secrets：
   - `DOCKERHUB_USERNAME`: 你的Docker Hub用户名
   - `DOCKERHUB_TOKEN`: 你的Docker Hub访问令牌（不是密码）

   注意：如果你没有Docker Hub账号或不想推送到Docker Hub，可以跳过这一步。Action会自动只推送到GitHub Container Registry。

4. 确保你的GitHub账户有权限推送到GitHub Container Registry。如果没有，你可能需要在个人设置中启用它。

5. 推送代码到master分支或创建一个pull request到master分支，这将触发GitHub Actions。

6. Actions将自动构建x86和ARM架构的Docker镜像，并推送到配置的仓库。

注意：如果你没有设置Docker Hub凭证，Actions将只推送到GitHub Container Registry。

## 错误处理

如果在证书生成过程中遇到任何问题，错误信息将显示在Web页面上。

要查看更详细的错误日志：

1. 如果本地运行，检查运行 `python app.py` 的终端窗口。
2. 如果使用Docker，可以使用 `docker logs <container_id>` 查看日志。

## 注意事项

- 这个系统生成的是自签名证书，不适用于生产环境。在实际使用中，你可能需要使用受信任的证书颁发机构（CA）签名的证书。
- 确保在使用此系统时遵守相关的安全最佳实践，特别是在处理私钥和密码时。
- 这个系统实现了基本的速率限制，但在生产环境中使用时可能需要更强大的安全措施，如用户认证和授权。

## 贡献

欢迎提交问题报告和拉取请求来帮助改进这个项目。

## 许可

[MIT License](https://opensource.org/licenses/MIT)