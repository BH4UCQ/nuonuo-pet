# Backend API Draft

## Base concepts

- `device_id`: 设备唯一标识
- `pet_id`: 宠物唯一标识
- `owner_id`: 用户唯一标识
- `bind_code`: 临时绑定码

## Current implemented endpoints

- `GET /health`
- `GET /api/protocol`
- `POST /api/device/register`
- `POST /api/device/bind/request`
- `POST /api/device/bind/confirm`
- `GET /api/device/{device_id}/health`
- `GET /api/device/{device_id}/events`
- `POST /api/device/heartbeat`
- `POST /api/device/{device_id}/event`
- `POST /api/device/state`
- `GET /api/species/templates`
- `GET /api/model/routes/config`
- `PATCH /api/model/routes/config`
- `POST /api/model/routes/resolve`
- `POST /api/model/routes/apply/{pet_id}`
- `GET /api/resource/packs`
- `GET /api/resource/packs/{pack_id}`
- `POST /api/resource/packs/import`
- `PATCH /api/resource/packs/{pack_id}/enable`
- `POST /api/resource/packs/{pack_id}/rollback`
- `GET /api/theme/packs`
- `GET /api/theme/compatibility`
- `POST /api/theme/validate`
- `GET /api/resource/packs`
- `GET /api/resource/packs/{pack_id}`
- `POST /api/resource/packs/import`
- `PATCH /api/resource/packs/{pack_id}/enable`
- `POST /api/resource/packs/{pack_id}/rollback`
- `GET /api/resource/manifest/sample`
- `POST /api/resource/validate`
- `GET /api/device/capability/grade`
- `GET /api/device/capability/summary`
- `POST /api/device/capability/summary`
- `GET /api/preview/{species_id}/{theme_id}`
- `GET /api/preview/sample`
- `POST /api/pet/create`
- `GET /api/pet/{pet_id}`
- `PATCH /api/pet/{pet_id}`
- `GET /api/device/{device_id}/pet`
- `GET /api/pet/{pet_id}/devices`
- `POST /api/pet/{pet_id}/devices/link`
- `POST /api/pet/{pet_id}/devices/unlink`
- `POST /api/pet/{pet_id}/devices/primary`
- `GET /api/pet/{pet_id}/sync`
- `GET /api/pet/{pet_id}/sync/minimal`
- `GET /api/device/{device_id}/sync`
- `GET /api/device/{device_id}/sync/minimal`
- `POST /api/pet/{pet_id}/event`
- `GET /api/pet/{pet_id}/memory/summary`
- `GET /api/pet/{pet_id}/events`
- `POST /api/chat`
- `GET /api/memory/{pet_id}`
- `POST /api/memory/{pet_id}`
- `GET /api/assets/manifest`
- `GET /api/assets/manifest/sample`

## Responses

Most endpoints return `server_time` so the client can align logs and sync windows.

## Current behavior notes

- Species templates constrain theme selection.
- Model routes are normalized into `model_provider` and `model_name`.
- Pet events can change mood, energy, hunger, affection, exp, and level.
- Memory writes can also influence experience and bonding.
- Theme validation checks species compatibility and slot mapping.
- Resource validation checks slot rules, size bounds, and format rules.
- 设备能力可以先做粗分级：lcd / oled / voice / rich / unknown。
- `preview/sample` 会返回推荐的 `display_mode` 和 `display_hint`。
- 预览接口返回 palette、ui_slots、layers、notes，并尽量保持模板安全。
- `sync/minimal` 返回适合固件/UI 的压缩摘要，便于直接渲染状态和按钮提示。

## Suggested next additions

- resource pack upload endpoint
- event log endpoint
- pet growth summary endpoint
- template preview endpoint
