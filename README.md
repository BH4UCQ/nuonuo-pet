# Nuonuo Pet - AI 电子宠物系统

<div align="center">

![Nuonuo Pet](docs/images/logo.png)

**一个完整的 AI 电子宠物生态系统**

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![ESP32](https://img.shields.io/badge/platform-ESP32-orange.svg)](https://www.espressif.com/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/)
[![Vue](https://img.shields.io/badge/vue-3.x-green.svg)](https://vuejs.org/)

[功能特性](#功能特性) • [快速开始](#快速开始) • [项目结构](#项目结构) • [文档](#文档) • [贡献指南](#贡献指南)

</div>

---

## 项目简介

Nuonuo Pet 是一个基于 AI 的电子宠物系统，包含硬件设备、后端服务和前端管理界面。通过 AI 技术，电子宠物能够与用户进行智能对话、情绪交互，并具有成长系统和多种物种形态。

### 核心亮点

- **智能对话**: 集成多种 AI 模型，支持自然语言交互
- **情绪系统**: 宠物具有真实的情绪反应和变化
- **成长系统**: 宠物会随时间成长，解锁新形态和能力
- **多物种支持**: 支持多种宠物类型，可扩展
- **离线可用**: 支持离线模式，保证基本功能
- **开源免费**: 完全开源，可自由定制

---

## 功能特性

### 设备端 (ESP32)

- **高清显示**: 360x360 圆形 LCD 屏幕，流畅动画
- **触摸交互**: 电容触摸，支持手势操作
- **音频输出**: 高质量语音合成和音效
- **Wi-Fi 连接**: 自动配网，断线重连
- **离线模式**: 本地缓存，离线可用

### 后端服务 (FastAPI)

- **RESTful API**: 完整的设备、宠物、交互接口
- **WebSocket**: 实时双向通信
- **AI 路由**: 多模型支持，智能回退
- **记忆系统**: 短期/长期记忆管理
- **数据同步**: 设备状态同步，历史记录

### 前端界面 (Vue 3)

- **管理后台**: 设备管理、用户管理
- **监控面板**: 实时状态监控
- **数据可视化**: 交互历史、成长曲线
- **资源管理**: 物种、主题、皮肤管理

---

## 项目结构

```
nuonuo-pet/
├── frontend/          # Vue 3 前端项目
│   ├── src/
│   │   ├── views/     # 页面组件
│   │   ├── components/# 通用组件
│   │   ├── api/       # API 调用
│   │   ├── stores/    # 状态管理
│   │   └── utils/     # 工具函数
│   └── package.json
│
├── backend/           # FastAPI 后端项目
│   ├── app/
│   │   ├── api/       # API 路由
│   │   ├── services/  # 业务服务
│   │   ├── models/    # 数据模型
│   │   └── core/      # 核心模块
│   └── requirements.txt
│
├── firmware/          # ESP32 固件项目
│   └── esp32/
│       ├── main/      # 主程序
│       │   ├── core/  # 核心模块
│       │   ├── drivers/# 硬件驱动
│       │   ├── network/# 网络模块
│       │   └── ui/    # UI 模块
│       └── CMakeLists.txt
│
├── docs/              # 项目文档
│   ├── api/           # API 文档
│   ├── hardware/      # 硬件文档
│   └── deployment/    # 部署文档
│
├── resources/         # 资源文件
│   ├── species/       # 物种资源包
│   ├── themes/        # 主题资源包
│   └── sounds/        # 音效资源
│
└── scripts/           # 工具脚本
    ├── build/         # 构建脚本
    └── deploy/        # 部署脚本
```

---

## 快速开始

### 环境要求

- **前端**: Node.js 18+
- **后端**: Python 3.9+
- **固件**: ESP-IDF v5.0+
- **数据库**: PostgreSQL 14+ / SQLite

### 安装步骤

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/nuonuo-pet.git
cd nuonuo-pet
```

#### 2. 启动后端

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 配置数据库和 AI API
python run.py
```

后端服务将在 http://localhost:8000 启动

#### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

前端界面将在 http://localhost:5173 启动

#### 4. 编译固件

```bash
cd firmware/esp32
# 配置 ESP-IDF 环境
. $HOME/esp/esp-idf/export.sh
# 编译
idf.py build
# 烧录
idf.py -p /dev/ttyUSB0 flash monitor
```

---

## 配置说明

### 后端配置 (backend/.env)

```env
# 数据库
DATABASE_URL=postgresql://user:password@localhost:5432/nuonuo_pet

# AI API
OPENAI_API_KEY=your_openai_key
OPENAI_API_BASE=https://api.openai.com/v1

# JWT
JWT_SECRET=your_secret_key
JWT_ALGORITHM=HS256

# 服务配置
HOST=0.0.0.0
PORT=8000
DEBUG=true
```

### 固件配置 (firmware/esp32/sdkconfig)

- Wi-Fi SSID 和密码
- 后端服务器地址
- 显示和音频参数

---

## 文档

- [API 文档](docs/api/README.md)
- [硬件设计](docs/hardware/README.md)
- [部署指南](docs/deployment/README.md)
- [开发指南](docs/development/README.md)

---

## 技术栈

| 组件 | 技术 | 版本 |
|------|------|------|
| 前端框架 | Vue 3 | 3.x |
| 构建工具 | Vite | 5.x |
| 状态管理 | Pinia | 2.x |
| 后端框架 | FastAPI | 0.100+ |
| 数据库 | PostgreSQL | 14+ |
| 缓存 | Redis | 7+ |
| 固件框架 | ESP-IDF | 5.0+ |
| AI 模型 | OpenAI/Claude | - |

---

## 贡献指南

我们欢迎所有形式的贡献！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

请确保代码通过所有测试并遵循代码规范。

---

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件

---

## 致谢

- [ESP-IDF](https://github.com/espressif/esp-idf) - ESP32 开发框架
- [FastAPI](https://fastapi.tiangolo.com/) - 现代 Python Web 框架
- [Vue.js](https://vuejs.org/) - 渐进式 JavaScript 框架
- [OpenAI](https://openai.com/) - AI 模型支持

---

<div align="center">

**Made with ❤️ by Nuonuo Pet Team**

</div>
