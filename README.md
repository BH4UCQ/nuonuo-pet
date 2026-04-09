# nuonuo-pet

nuonuo-pet 是一个可配置、可成长、可多形态的 AI 电子宠物项目。

## 快速开始

如果你是第一次打开这个仓库，建议先看：

- `docs/github_beginner_guide.md`：GitHub 小白友好的完整使用说明
- `docs/roadmap.md`：项目路线图
- `firmware/esp32/README.md`：正式业务固件结构、联网和显示抽象说明
- `firmware/esp32_idf_display_baseline/README.md`：Waveshare 1.85 屏幕已验证可亮屏的官方 IDF 基线说明

如果你暂时不接真机，也可以先运行这些脚本做基础检查：

- `python3 scripts/firmware_state_selftest.py`
- `python3 scripts/display_scene_selftest.py`
- `python3 scripts/home_screen_mode_selftest.py`

## 后端本地验证

在仓库根目录执行：

```bash
python3 -m venv .venv-backend
. .venv-backend/bin/activate
pip install -r backend/requirements.txt pytest
pytest -q backend/tests/test_ui_smoke.py
python backend/tests/run_ui_smoke.py
```

如果需要手动打开调试后台：

```bash
. .venv-backend/bin/activate
uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8000
```

默认可访问：

- `/ui`：内嵌调试后台首页
- `/docs`：Swagger
- `/health`：健康检查 JSON

## 当前目标

- 设备端：ESP32 负责显示、音频、状态机、绑定与基础交互
- 服务端：FastAPI 负责模型路由、记忆、设备管理、资源清单、模型路由配置与回退
- 玩法层：宠物情绪、成长、物种模板、皮肤资源槽、事件与日志

## 当前固件现实状态

当前仓库中与屏幕相关的路径分成两类：

- `firmware/esp32_idf_display_baseline/`：基于官方 Waveshare demo/ESP-IDF 路径整理出的最小显示基线，**已经在真机上确认可显示红/绿/蓝/白/黑循环**。
- `firmware/esp32/`：`nuonuo-pet` 正式业务固件，已经具备 Wi‑Fi、配网门户、状态机、后端接口消费和显示抽象层，但屏幕底座仍处于向官方路径收敛的过程中。

因此，当前设备端工作的正确推进方向是：

1. 以 `esp32_idf_display_baseline` 作为已知正确的屏幕底座
2. 将板级控制和 ST77916 面板层模块化
3. 再把正式业务 UI 和显示抽象层重新接到这个已验证底座上

## 第一版原则

- 不强行依赖固定后端
- 模型提供方可配置
- 记忆分层，支持短期/长期/事件记忆
- UI 资源按模板与槽位加载，适配 ESP32 资源限制
- 物种与主题解耦，支持猫、猴子、鼠、恐龙等扩展

## 目录概览

- `backend/`：后端服务骨架
- `firmware/`：ESP32 固件骨架
- `app/`：桌面/网页辅助工具占位
- `assets/`：资源模板与导入说明
- `docs/`：设计文档
- `docs/reports/`：阶段性导出报告与对照表
- `docs/device_summary_consumer.md`：设备汇总接口消费示例
- `scripts/`：检查与辅助脚本
- `release_build/`：版本交付物与打包产物归档

## v0.1.0 交付物

- `release_build/v0.1.0/release_notes_v0.1.0.html`
- `release_build/v0.1.0/release_notes_v0.1.0.docx`
- `release_build/v0.1.0/nuonuo-pet_v0.1.0_release_bundle.zip`
- `release_build/v0.1.0/RELEASE_MANIFEST.txt`
- `CHANGELOG.md`
- `docs/roadmap.md`

## 下一阶段

- 参考 `docs/v0.2.0_plan.md`
- 模型路由配置与回退、资源包导入/启用/回滚、主题版本兼容已完成
- 当前重点转到设备端联网稳态：Wi‑Fi 连接、离线降级、同步退避与恢复
- 路线图中的 `M5` 已预留给 v0.2.0 产品化增强


## 验证脚本

- `python3 scripts/firmware_state_selftest.py`
- `python3 scripts/display_scene_selftest.py`
- `python3 scripts/binding_flow_selftest.py`
- `python3 scripts/e2e_selftest.py`

这些脚本可以在没有真机或没有完整联网环境时，先把核心逻辑跑一遍。
