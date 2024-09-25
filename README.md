# SSL 证书生成器

这是一个基于Web的SSL证书生成器，可以创建自签名的根证书和子证书，以及相应的keystore和truststore文件。

## 系统要求

- Python 3.6+
- Flask
- OpenSSL 2.x
- Java（用于keytool命令）

或者

- Docker

## 文件结构

```
.
├── app.py
├── static/
│   ├── styles.css
│   └── script.js
├── templates/
│   └── index.html
├── dist/  (自动创建)
├── Dockerfile
├── .github/
│   └── workflows/
│       └── docker-build-push.yml
└── README.md
```

## 本地安装和运行

1. 克隆此仓库或下载源代码。

2. 安装所需的Python包：

   ```
   pip install flask
   ```

3. 确保系统中已安装OpenSSL 2.x和Java。

4. 运行Flask应用：

   ```
   python app.py
   ```

5. 打开Web浏览器，访问 http://localhost:5000

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

## GitHub Action 自动构建和推送

本项目包含一个GitHub Action，可以自动构建多平台Docker镜像并推送到GitHub Container Registry和Docker Hub。

### 设置步骤

1. 在GitHub仓库中，进入 "Settings" > "Secrets and variables" > "Actions"。

2. 添加以下秘密：
   - `DOCKERHUB_USERNAME`: 你的Docker Hub用户名
   - `DOCKERHUB_TOKEN`: 你的Docker Hub访问令牌（不是密码）

3. 确保你的GitHub账户有权限推送到GitHub Container Registry。如果没有，你可能需要在个人设置中启用它。

4. 推送代码到main分支或创建一个pull request到main分支，这将触发GitHub Action。

5. Action将自动构建x86和ARM架构的Docker镜像，并推送到两个仓库，标签包括日期（格式为YYYYMMDD）和latest。

注意：如果你不想推送到Docker Hub，可以删除或注释掉GitHub Action文件中相关的步骤。

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
- 这个系统目前没有实现用户认证和授权，在生产环境中使用时应该添加这些安全措施。

## 贡献

欢迎提交问题报告和拉取请求来帮助改进这个项目。

## 许可

[MIT License](https://opensource.org/licenses/MIT)