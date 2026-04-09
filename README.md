# nuonuo-pet

一个可配置、可成长、可多形态的 AI 电子宠物项目，支持与大语言模型（LLM）的智能对话功能。

![Project Status](https://img.shields.io/badge/status-production--ready-brightgreen)
![Python](https://img.shields.io/badge/python-3.7+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

## 🌟 项目特点

- **智能对话**: 集成大语言模型，支持自然语言交互
- **多模型支持**: 支持 OpenAI、Claude、本地模型等多种 LLM
- **智能降级**: 主模型失败时自动切换到备用模型
- **记忆系统**: 短期、长期、事件记忆，让宠物记住互动历史
- **成长系统**: 经验值、等级、偏好养成，宠物会随着互动成长
- **多形态**: 支持多种宠物形态和主题
- **设备绑定**: 支持 ESP32 硬件设备绑定
- **Web界面**: 直观的 Web 管理界面

## 🚀 快速开始

### 环境要求

- Python 3.7+
- pip

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/yourusername/nuonuo-pet.git
cd nuonuo-pet
```

2. **创建虚拟环境**
```bash
python -m venv .venv-backend
# Windows
.venv-backend\Scripts\activate
# Linux/Mac
source .venv-backend/bin/activate
```

3. **安装依赖**
```bash
cd backend
pip install -r requirements.txt
```

4. **启动应用**
```bash
uvicorn app.main:app --reload
```

5. **访问应用**
- API 文档: http://localhost:8000/docs
- Web 界面: http://localhost:8000/

## 📖 使用说明

### 配置 LLM 提供商

1. 访问 http://localhost:8000/docs
2. 找到 `POST /api/llm/config/provider/{provider_id}` 接口
3. 配置您的 LLM 提供商（OpenAI、Claude 等）
4. 设置 API 密钥（会自动加密存储）

### 创建宠物

1. 访问 Web 界面
2. 点击"创建宠物"
3. 选择宠物形态和主题
4. 命名您的宠物

### 开始对话

1. 在 Web 界面找到对话输入框
2. 输入消息发送给宠物
3. 等待宠物的智能回复

## 🏗️ 项目结构

```
nuonuo-pet/
├── backend/                 # 后端代码
│   ├── app/                # 应用核心模块
│   │   ├── main.py         # 主应用入口
│   │   ├── models.py       # 数据模型
│   │   ├── storage.py      # 存储系统
│   │   ├── llm_*.py        # LLM 相关模块
│   │   └── ...
│   ├── tests/              # 测试文件
│   └── requirements.txt    # Python 依赖
├── docs/                   # 文档
├── scripts/                # 工具脚本
└── README.md              # 项目说明
```

## 🔧 核心功能

### LLM 功能
- ✅ 多模型路由管理
- ✅ 智能降级机制
- ✅ 对话上下文构建
- ✅ API 密钥加密存储
- ✅ 模型健康监控
- ✅ 对话历史管理
- ✅ 流式响应支持

### 宠物管理
- ✅ 宠物创建和配置
- ✅ 多形态支持
- ✅ 主题定制
- ✅ 状态管理（情绪、能量、饥饿度）

### 记忆系统
- ✅ 短期记忆
- ✅ 长期记忆
- ✅ 事件记忆
- ✅ 智能检索

### 成长系统
- ✅ 经验值系统
- ✅ 等级提升
- ✅ 偏好养成
- ✅ 个性化发展

## 📡 API 端点

### 基础端点
- `GET /` - 根路由
- `GET /health` - 健康检查
- `GET /api/protocol` - 协议信息

### LLM 功能
- `POST /api/llm/chat` - 发起对话
- `GET /api/llm/config` - 获取配置
- `GET /api/llm/health` - 健康检查
- `GET /api/llm/conversations/{pet_id}` - 对话历史

### 宠物管理
- `POST /api/pet/create` - 创建宠物
- `GET /api/pet/{pet_id}` - 宠物详情
- `POST /api/pet/{pet_id}/event` - 宠物事件

更多 API 详情请访问: http://localhost:8000/docs

## 🔐 安全性

- API 密钥使用 AES-256 加密存储
- 输入验证和数据清理
- CORS 配置
- 错误处理和日志记录

## 🧪 测试

运行基础功能测试：
```bash
cd backend
python tests/test_llm_basic.py
```

运行项目全面检查：
```bash
python scripts/check_project.py
```

## 📝 待办事项

- [ ] 完善单元测试覆盖率
- [ ] 集成真实的 ASR/TTS 服务
- [ ] 添加用户认证系统
- [ ] 实现多用户支持
- [ ] 优化性能和缓存
- [ ] 添加更多宠物形态和主题

## 🤝 贡献指南

欢迎贡献代码！请遵循以下步骤：

1. Fork 本项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。详情请参阅 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- FastAPI 框架
- OpenAI API
- Anthropic Claude API
- 所有贡献者

## 📮 联系方式

- 项目主页: https://github.com/yourusername/nuonuo-pet
- 问题反馈: https://github.com/yourusername/nuonuo-pet/issues
- 邮箱: your.email@example.com

## 🌟 Star History

如果这个项目对您有帮助，请给我们一个 Star！

---

**注意**: 本项目仅用于学习和研究目的。请遵守相关 API 服务提供商的使用条款。
