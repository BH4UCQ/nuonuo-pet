# 更新日志

所有重要的更改都将记录在此文件中。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
并且本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [Unreleased]

### 新增
- 初始项目结构
- 前端 Vue 3 项目框架
- 后端 FastAPI 项目框架
- ESP32 固件项目框架
- 完整的项目文档

## [1.0.0] - 2025-04-10

### 新增
- **前端**
  - Vue 3 + Vite + TypeScript 项目结构
  - Element Plus UI 组件库
  - Pinia 状态管理
  - Vue Router 路由管理
  - 登录页面
  - 仪表盘页面
  - 设备管理页面
  - 宠物管理页面
  - 交互记录页面
  - 资源管理页面
  - 系统设置页面
  - API 请求封装
  - WebSocket 连接支持

- **后端**
  - FastAPI 项目结构
  - SQLAlchemy 异步数据库支持
  - JWT 认证系统
  - 用户注册/登录接口
  - 设备管理 API
  - 宠物管理 API
  - 交互记录 API
  - 资源管理 API
  - WebSocket 实时通信
  - 健康检查接口

- **固件**
  - ESP-IDF 项目结构
  - ST77916 显示驱动
  - Wi-Fi 管理模块
  - 配网门户
  - 状态机核心
  - UI 渲染器框架
  - 情绪系统框架
  - 成长系统框架

- **文档**
  - README 项目介绍
  - API 接口文档
  - 部署指南
  - 硬件设计文档
  - 开发指南
  - MIT 开源许可证

### 技术栈
- 前端: Vue 3.4, Vite 5, TypeScript 5, Element Plus 2
- 后端: Python 3.9, FastAPI 0.109, SQLAlchemy 2
- 固件: ESP-IDF 5.0, ESP32-S3
- 数据库: PostgreSQL 14 / SQLite
- 缓存: Redis 7

[Unreleased]: https://github.com/your-username/nuonuo-pet/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/your-username/nuonuo-pet/releases/tag/v1.0.0
