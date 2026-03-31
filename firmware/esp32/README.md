# ESP32 firmware for nuonuo-pet

This folder contains the first-pass PlatformIO scaffold.

## Files

- `platformio.ini`
- `src/main.cpp`
- `include/state_machine.h`
- `include/pet_app.h`
- `include/device_profile.h`
- `include/sync_summary.h`
- `include/sync_client.h`

## 最简日志约定

第一版建议使用串口输出固定前缀，便于后续调试和脚本抓取：

- `[nuonuo] boot`
- `[nuonuo] device=...`
- `[nuonuo] fw=...`
- `[nuonuo] state=... mood=... reason=...`

## 固件状态机自检

可以先在宿主机上跑：

```bash
python3 scripts/firmware_state_selftest.py
```

这个脚本用于验证状态流转逻辑是否符合设计文档，即使当前环境没有 PlatformIO 也能先完成逻辑检查。

## 最小同步摘要消费建议

后端提供 `GET /api/pet/{pet_id}/sync/minimal` 和 `GET /api/device/{device_id}/sync/minimal`。

建议固件侧直接按以下顺序消费：

1. `health_level` 决定主色/状态灯
2. `summary_line` 作为顶部状态栏
3. `primary_hint` 作为主文案
4. `action_hint` 作为底部提示或按钮文案
5. `recommended_action` 供状态机自动处理

这样可以把复杂同步逻辑留给后端，ESP32 只负责展示与最小决策。

## HTTP 拉取骨架

当前固件已预留 `SyncClient`：

- 默认后端地址见 `device_profile.h`
- 默认宠物 ID 为 `NUONUO_DEFAULT_PET_ID`
- 固件会定期请求 `GET /api/pet/{pet_id}/sync/minimal`
- 成功后调用 `applySyncMini()` 进入显示/提示逻辑

这一步先把数据流打通，后续再替换成更完整的联网、鉴权和重试策略。

