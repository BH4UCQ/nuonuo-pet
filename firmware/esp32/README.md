# ESP32 firmware for nuonuo-pet

This folder contains the first-pass PlatformIO scaffold.

## Files

- `platformio.ini`
- `src/main.cpp`
- `include/state_machine.h`
- `include/pet_app.h`
- `include/device_profile.h`

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
