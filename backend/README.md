# 后端 README

后端采用 FastAPI，职责是：

- 设备注册与绑定
- 状态同步
- 宠物记忆读写
- 模型路由
- 资源清单与版本管理

## 启动目标

后续计划提供：

- `GET /health`
- `POST /api/device/register`
- `POST /api/device/bind/request`
- `POST /api/device/bind/confirm`
- `POST /api/device/state`
- `POST /api/chat`
- `GET /api/memory/{pet_id}`
- `POST /api/memory/{pet_id}`
- `GET /api/assets/manifest`

## 绑定联调自检

可直接运行：

```bash
python3 scripts/binding_flow_selftest.py
```

这个脚本不依赖 FastAPI，用于在轻量环境里快速验证注册、申请绑定码、确认绑定、生成宠物和状态回写的基本链路。

## 当前状态

这是骨架阶段的收口说明：接口形状、核心模型、成长摘要和端到端自检都已经补齐；结合 ESP32 固件编译通过，nuonuo-pet 的 v0.1.0 开发计划已经完成。
