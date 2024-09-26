# SSL 证书生成器

这是一个基于Web的SSL证书生成器，可以创建自签名的根证书和子证书，以及相应的keystore和truststore文件。

## 系统要求

- Python 3.11+
- Flask
- Flask-Limiter
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
├── test_cert_generator.py
├── .github/
│   └── workflows/
│       └── docker-build-push.yml
└── README.md
```

## 文件说明

- `app.py`: 主应用文件，包含Flask路由和主要逻辑
- `config.py`: 配置文件，包含应用程序的设置
- `cert_generator.py`: 证书生成逻辑
- `static/`: 静态文件目录
- `templates/`: HTML模板目录
- `dist/`: 生成的证书和密钥存储目录
- `test_cert_generator.py`: 用于测试证书生成功能的脚本

## 本地安装和运行

1. 克隆此仓库或下载源代码。

2. 安装所需的Python包：

   ```
   pip install flask flask-limiter
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

5. 运行Flask应用：

   ```
   python app.py
   ```

6. 打开Web浏览器，访问 http://localhost:5000

## 使用Docker

如果你prefer使用Docker，可以按照以下步骤构建和运行容器：

1. 构建Docker镜像：

   ```
   docker build -t ssl-cert-generator .
   ```

2. 运行Docker容器：

   ```
   docker run -p 5000:5000 ssl-cert-generator
   ```

3. 打开Web浏览器，访问 http://localhost:5000

注意：Docker环境中已经配置了Java和keytool，无需额外设置。

## 配置keytool路径

默认情况下，应用程序会尝试使用系统PATH中的keytool。如果keytool不在默认路径或你想使用特定版本的keytool，可以通过以下方式设置：

1. 在运行应用程序之前，设置KEYTOOL_PATH环境变量：
   ```
   export KEYTOOL_PATH=/path/to/your/keytool
   ```

2. 如果使用Docker，可以在运行容器时通过-e参数设置环境变量：
   ```
   docker run -p 5000:5000 -e KEYTOOL_PATH=/path/to/your/keytool ssl-cert-generator
   ```

## GitHub Action 自动构建和推送

本项目包含一个GitHub Action，可以自动构建多平台Docker镜像并推送到GitHub Container Registry和Docker Hub。

### 设置步骤

1. 在GitHub仓库中，进入 "Settings" > "Secrets and variables" > "Actions"。

2. 添加以下secrets：
   - `DOCKERHUB_USERNAME`: 你的Docker Hub用户名
   - `DOCKERHUB_TOKEN`: 你的Docker Hub访问令牌（不是密码）

   注意：如果你没有Docker Hub账号或不想推送到Docker Hub，可以跳过这一步。Action会自动只推送到GitHub Container Registry。

3. 获取Docker Hub访问令牌：
   - 登录到你的Docker Hub账户
   - 点击你的用户名，然后选择 "Account Settings"
   - 在左侧菜单中，点击 "Security"
   - 在 "Access Tokens" 部分，点击 "New Access Token"
   - 给token起一个名字，选择适当的权限（至少需要"Read, Write, Delete"权限）
   - 点击 "Generate" 并复制生成的token
   - 将这个token作为 `DOCKERHUB_TOKEN` 的值添加到GitHub Secrets中

4. 确保你的GitHub账户有权限推送到GitHub Container Registry。如果没有，你可能需要在个人设置中启用它。

5. 推送代码到main分支或创建一个pull request到main分支，这将触发GitHub Action。

6. Action将自动构建x86和ARM架构的Docker镜像，并推送到配置的仓库，标签包括日期（格式为YYYYMMDD）和latest。

注意：如果你没有设置Docker Hub凭证，Action将只推送到GitHub Container Registry。

## 使用说明

1. 填写表单并点击"生成证书"按钮。

2. 生成完成后，你将看到生成的文件列表和下载链接。

3. 所有生成的文件都保存在'dist'目录中。

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