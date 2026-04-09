# 资源系统

nuonuo-pet 的资源系统采用“模板 + 槽位”模式。

## 约定

- 物种模板：定义轮廓、表情、动作、阶段
- 主题包：定义颜色、边框、背景、装饰
- 槽位：定义某张图、某个音效、某个动画资源应该放在哪里
- 资源包：按 manifest 组织，可被校验和预览

## 第一版目标

- 不支持任意大资源自由塞入
- 支持受限尺寸的导入与校验
- 支持资源 manifest
- 支持主题包校验
- 支持按物种限制主题

## 建议目录

- `species/`
- `themes/`
- `audio/`
- `sprites/`
- `previews/`

## 资源包示例字段

- `pack_id`
- `pack_type`
- `version`
- `species_id`
- `theme_id`
- `slots[]`

- `GET /api/theme/packs`
- `GET /api/theme/compatibility`
- `POST /api/theme/validate`
- `GET /api/resource/packs`
- `GET /api/resource/packs/{pack_id}`
- `POST /api/resource/packs/import`
- `PATCH /api/resource/packs/{pack_id}/enable`
- `POST /api/resource/packs/{pack_id}/rollback`

## 设计说明

- 资源包记录会保存 `active_version`、`enabled` 和 `previous_versions`
- 导入时先校验 manifest 和 slot 规则
- 启用/禁用与回滚都走统一记录结构，方便后续做 UI 版本切换
