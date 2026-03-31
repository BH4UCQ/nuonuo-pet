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
- `status_hint`：同步状态说明
- `last_sync_ok_ms` / `last_sync_fail_ms`：用于降级节奏控制
- `sync_fail_count`：用于决定是否进入恢复/错误态

## 设备端渲染建议

1. 先看 `health_level` 决定颜色
2. 再显示 `summary_line`
3. 如果有 `primary_hint`，放在主区域
4. 如果有 `action_hint`，放底部按钮提示
5. `recommended_action` 留给状态机/自动修复逻辑
6. `status_hint` 可用于“正在恢复 / 网络不可用 / 服务器无响应”之类提示

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
  "status_hint": "sync delayed: offline device detected",
  "online_devices": 1,
  "offline_devices": 1,
  "missing_devices": 0,
  "conflict_count": 1,
  "device_count": 2,
  "last_sync_ok_ms": 123456,
  "last_sync_fail_ms": 123000,
  "sync_fail_count": 2,
  "notes": ["device dev-b offline"]
}
```

## 固件接入建议

如果固件暂时还没有 HTTP 客户端，可以先把这个 JSON 映射到内部结构：

- `health_level` → 状态灯颜色
- `summary_line` → 顶部文案
- `primary_hint` → 主提示
- `action_hint` → 按钮提示
- `status_hint` → 降级提示
- `recommended_action` → 状态机修复动作

### 降级行为建议

- 第 1 次失败：只提示“同步失败，重试中”
- 连续 3 次失败：进入 `Recovering`
- 连续 8 次失败：进入 `Error`
- 恢复成功后：清零失败计数，回到 `Ready`

后续只要把这份结构从 HTTP 拉下来并喂给 `applySyncMini()` 即可。

