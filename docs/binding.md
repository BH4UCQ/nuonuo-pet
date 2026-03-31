# 绑定协议

nuonuo-pet 的绑定流程采用“设备先注册，再请求绑定码，再由用户确认”的方式。

## 流程

1. 设备启动后调用 `POST /api/device/register`
2. 后端返回 `binding_required` 与 `next_step`
3. 设备再调用 `POST /api/device/bind/request`
4. 后端生成 `bind_code` 和过期时间
5. 用户在 App / 网页里输入或扫码确认
6. App 调用 `POST /api/device/bind/confirm`
7. 绑定成功后，设备进入 `Ready`

## 设计要点

- 绑定码只短期有效
- 设备详情接口可查询绑定状态
- 所有响应都尽量带 `server_time`
- 设备端只负责执行状态机，不承担复杂确认逻辑

## 当前接口

- `GET /api/protocol`
- `POST /api/device/register`
- `POST /api/device/bind/request`
- `POST /api/device/bind/confirm`
- `GET /api/device/{device_id}`
- `POST /api/device/state`
