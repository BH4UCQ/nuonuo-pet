# 部署指南

本文档提供了 nuonuo-pet 项目的详细部署指南。

## 环境要求

### 最低要求
- Python 3.7+
- 2GB RAM
- 1GB 可用磁盘空间
- 网络连接（用于 LLM API 调用）

### 推荐配置
- Python 3.8+
- 4GB RAM
- 2GB 可用磁盘空间
- 稳定的网络连接

## 本地部署

### Windows

1. **下载项目**
   ```bash
   git clone https://github.com/yourusername/nuonuo-pet.git
   cd nuonuo-pet
   ```

2. **运行设置脚本**
   ```bash
   setup.bat
   ```

3. **启动应用**
   ```bash
   start.bat
   ```

4. **访问应用**
   - API 文档: http://localhost:8000/docs
   - Web 界面: http://localhost:8000/

### Linux/Mac

1. **下载项目**
   ```bash
   git clone https://github.com/yourusername/nuonuo-pet.git
   cd nuonuo-pet
   ```

2. **运行设置脚本**
   ```bash
   chmod +x setup.sh start.sh
   ./setup.sh
   ```

3. **启动应用**
   ```bash
   ./start.sh
   ```

4. **访问应用**
   - API 文档: http://localhost:8000/docs
   - Web 界面: http://localhost:8000/

## 服务器部署

### 使用 systemd (Linux)

1. **创建服务文件**
   ```bash
   sudo nano /etc/systemd/system/nuonuo-pet.service
   ```

2. **添加以下内容**
   ```ini
   [Unit]
   Description=nuonuo-pet AI Pet Service
   After=network.target

   [Service]
   Type=simple
   User=youruser
   WorkingDirectory=/path/to/nuonuo-pet
   Environment="PATH=/path/to/nuonuo-pet/.venv-backend/bin"
   ExecStart=/path/to/nuonuo-pet/.venv-backend/bin/uvicorn backend.app.main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **启动服务**
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable nuonuo-pet
   sudo systemctl start nuonuo-pet
   ```

4. **检查状态**
   ```bash
   sudo systemctl status nuonuo-pet
   ```

### 使用 Docker

1. **创建 Dockerfile**
   ```dockerfile
   FROM python:3.8-slim

   WORKDIR /app

   COPY backend/requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY backend/ ./backend/

   EXPOSE 8000

   CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **构建镜像**
   ```bash
   docker build -t nuonuo-pet .
   ```

3. **运行容器**
   ```bash
   docker run -d -p 8000:8000 --name nuonuo-pet nuonuo-pet
   ```

### 使用 Nginx 反向代理

1. **安装 Nginx**
   ```bash
   sudo apt install nginx
   ```

2. **配置 Nginx**
   ```nginx
   server {
       listen 80;
       server_name your-domain.com;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

3. **重启 Nginx**
   ```bash
   sudo systemctl restart nginx
   ```

## 配置 LLM 提供商

### OpenAI 配置

1. 访问 http://localhost:8000/docs
2. 找到 `PUT /api/llm/config/provider/openai`
3. 配置以下参数：
   ```json
   {
     "name": "OpenAI GPT-3.5",
     "api_key": "your-openai-api-key",
     "endpoint": "https://api.openai.com/v1/chat/completions",
     "model_name": "gpt-3.5-turbo",
     "max_tokens": 2000,
     "temperature": 0.7
   }
   ```

### Claude 配置

1. 访问 http://localhost:8000/docs
2. 找到 `PUT /api/llm/config/provider/anthropic`
3. 配置以下参数：
   ```json
   {
     "name": "Anthropic Claude",
     "api_key": "your-anthropic-api-key",
     "endpoint": "https://api.anthropic.com/v1/messages",
     "model_name": "claude-3-sonnet-20240229",
     "max_tokens": 2000,
     "temperature": 0.7
   }
   ```

### 本地模型配置 (Ollama)

1. 安装 Ollama: https://ollama.ai
2. 配置提供商：
   ```json
   {
     "name": "Local Ollama",
     "api_key": "",
     "endpoint": "http://localhost:11434/api/generate",
     "model_name": "llama2",
     "max_tokens": 2000,
     "temperature": 0.7
   }
   ```

## 环境变量

创建 `.env` 文件（可选）：

```env
# 应用配置
APP_NAME=nuonuo-pet
APP_VERSION=1.0.0
DEBUG=False

# 服务器配置
HOST=0.0.0.0
PORT=8000

# LLM 配置
DEFAULT_LLM_PROVIDER=openai
DEFAULT_LLM_MODEL=gpt-3.5-turbo

# 安全配置
SECRET_KEY=your-secret-key-here
ENCRYPTION_KEY=your-encryption-key-here

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/app.log
```

## 数据备份

### 手动备份

```bash
# 备份数据文件
cp -r backend/data/ backups/data_$(date +%Y%m%d_%H%M%S)/

# 备份配置文件
cp backend/data/*.json backups/config_$(date +%Y%m%d_%H%M%S)/
```

### 自动备份脚本

创建 `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据
cp -r backend/data/ $BACKUP_DIR/data_$DATE/

# 保留最近7天的备份
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} \;
```

## 监控和日志

### 查看日志

```bash
# systemd 服务日志
sudo journalctl -u nuonuo-pet -f

# 应用日志
tail -f backend/data/logs/app.log
```

### 健康检查

```bash
# 基本健康检查
curl http://localhost:8000/health

# LLM 健康检查
curl http://localhost:8000/api/llm/health
```

## 故障排查

### 应用无法启动

1. **检查 Python 版本**
   ```bash
   python --version
   ```

2. **检查依赖**
   ```bash
   pip list
   ```

3. **检查端口占用**
   ```bash
   # Linux/Mac
   lsof -i :8000

   # Windows
   netstat -ano | findstr :8000
   ```

### LLM 调用失败

1. **检查 API 密钥**
   - 访问 http://localhost:8000/api/llm/config
   - 验证 API 密钥是否正确

2. **检查网络连接**
   ```bash
   ping api.openai.com
   ```

3. **查看错误日志**
   ```bash
   tail -f backend/data/logs/app.log
   ```

### 性能问题

1. **检查系统资源**
   ```bash
   # CPU 和内存使用
   top

   # 磁盘使用
   df -h
   ```

2. **优化配置**
   - 减少 max_tokens
   - 启用缓存
   - 使用更快的模型

## 安全建议

1. **使用 HTTPS**
   - 配置 SSL 证书
   - 使用 Let's Encrypt

2. **限制访问**
   - 配置防火墙
   - 使用 IP 白名单

3. **定期更新**
   - 更新 Python 依赖
   - 更新系统补丁

4. **备份策略**
   - 定期备份数据
   - 测试恢复流程

## 生产环境检查清单

- [ ] 使用 HTTPS
- [ ] 配置防火墙
- [ ] 设置自动备份
- [ ] 配置日志监控
- [ ] 设置错误告警
- [ ] 性能测试
- [ ] 安全扫描
- [ ] 文档完整

---

**注意**: 部署到生产环境前，请确保：
1. 已更改所有默认密码和密钥
2. 已配置适当的安全措施
3. 已测试所有功能
4. 已准备回滚计划
