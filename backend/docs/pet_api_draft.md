# 宠物 API 草案

## 宠物基础

- `POST /api/pet/create`
- `GET /api/pet/{pet_id}`
- `PATCH /api/pet/{pet_id}`

## 宠物事件

- `POST /api/pet/{pet_id}/event`
- `GET /api/pet/{pet_id}/memory/summary`

## 设计说明

宠物档案与设备档案分离：

- 设备可以更换
- 宠物不会丢
- 事件和记忆可以单独演化

## 当前第一版字段

- `name`
- `species_id`
- `theme_id`
- `growth_stage`
- `level`
- `exp`
- `mood`
- `energy`
- `hunger`
- `affection`
