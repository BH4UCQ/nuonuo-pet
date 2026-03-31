# 状态机设计

## 状态

- `Booting`：上电初始化
- `Connecting`：联网准备中
- `Binding`：等待绑定
- `Ready`：正常交互
- `Sleeping`：休眠或深睡
- `LowPower`：低电量保护
- `Error`：异常状态

## 宠物维度

- 情绪：Neutral / Happy / Curious / Sleepy / Hungry / Lonely / Sad / Angry
- 活动：Idle / Listening / Talking / Playing / Eating / Sleeping / Recovering

## 转移原则

- 联网成功后，若未绑定则进入 `Binding`
- 绑定成功后进入 `Ready`
- 能量过低时进入 `LowPower`
- 能量耗尽时进入 `Sleeping`
- 错误状态需保留恢复路径
