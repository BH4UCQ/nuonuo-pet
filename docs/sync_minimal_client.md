# 最小同步摘要消费示例

这个接口面向 ESP32 固件和轻量前端：

- `GET /api/pet/{pet_id}/sync/minimal`
- `GET /api/device/{device_id}/sync/minimal`

返回字段刻意压缩，适合直接做 UI 提示和状态机分支。

## 建议字段

- `health_level`：`normal / warning / degraded / critical / idle`
- `summary_line`：一句话总览
- `primary_device_id`：主设备
- `primary_hint`：主设备提示
- `action_hint`：下一步动作提示
- `recommended_action`：机器可读动作
- `occupancy_state`：`free / claimed / conflicted`
- `online_devices` / `offline_devices` / `missing_devices` / `conflict_count`

## 设备端渲染建议

1. 先看 `health_level` 决定颜色
2. 再显示 `summary_line`
3. 如果有 `primary_hint`，放在主区域
4. 如果有 `action_hint`，放底部按钮提示
5. `recommended_action` 留给状态机/自动修复逻辑

## 示例

```json
{
  "subject_id": "pet-a",
  "subject_type": "pet",
  "health_level": "critical",
  "summary_line": "2 device(s), 1 online, 1 offline, 1 conflict",
  "primary_device_id": "dev-a",
  "primary_hint": "主设备 dev-a 存在占用冲突，先处理冲突。",
  "action_hint": "先解除设备冲突，再继续同步。",
  "recommended_action": "resolve_device_conflict",
  "occupancy_state": "conflicted",
  "online_devices": 1,
  "offline_devices": 1,
  "missing_devices": 0,
  "conflict_count": 1,
  "device_count": 2,
  "notes": ["device dev-b offline"]
}
```
