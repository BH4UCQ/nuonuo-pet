from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Set
import json
import asyncio

router = APIRouter()


class ConnectionManager:
    """WebSocket 连接管理器"""

    def __init__(self):
        # 设备连接: device_id -> WebSocket
        self.device_connections: Dict[str, WebSocket] = {}
        # 用户连接: user_id -> Set[WebSocket]
        self.user_connections: Dict[int, Set[WebSocket]] = {}

    async def connect_device(self, device_id: str, websocket: WebSocket):
        """设备连接"""
        await websocket.accept()
        self.device_connections[device_id] = websocket

    async def disconnect_device(self, device_id: str):
        """设备断开"""
        self.device_connections.pop(device_id, None)

    async def connect_user(self, user_id: int, websocket: WebSocket):
        """用户连接"""
        await websocket.accept()
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(websocket)

    async def disconnect_user(self, user_id: int, websocket: WebSocket):
        """用户断开"""
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(websocket)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

    async def send_to_device(self, device_id: str, message: dict):
        """发送消息给设备"""
        if device_id in self.device_connections:
            await self.device_connections[device_id].send_json(message)

    async def send_to_user(self, user_id: int, message: dict):
        """发送消息给用户的所有连接"""
        if user_id in self.user_connections:
            for connection in self.user_connections[user_id]:
                await connection.send_json(message)

    async def broadcast(self, message: dict):
        """广播消息给所有连接"""
        for connection in self.device_connections.values():
            await connection.send_json(message)
        for connections in self.user_connections.values():
            for connection in connections:
                await connection.send_json(message)


manager = ConnectionManager()


@router.websocket("/ws/device/{device_id}")
async def device_websocket(websocket: WebSocket, device_id: str):
    """设备 WebSocket 连接"""
    await manager.connect_device(device_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理设备消息
            if message.get("type") == "status":
                # 设备状态更新
                await manager.send_to_device(
                    device_id,
                    {"type": "status_ack", "status": "ok"}
                )
            elif message.get("type") == "interaction":
                # 设备交互
                # TODO: 处理交互逻辑
                pass

    except WebSocketDisconnect:
        await manager.disconnect_device(device_id)


@router.websocket("/ws/user/{user_id}")
async def user_websocket(websocket: WebSocket, user_id: int):
    """用户 WebSocket 连接"""
    await manager.connect_user(user_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            # 处理用户消息
            if message.get("type") == "ping":
                await websocket.send_json({"type": "pong"})

    except WebSocketDisconnect:
        await manager.disconnect_user(user_id, websocket)
