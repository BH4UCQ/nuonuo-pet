"""
记忆管理服务
实现分层记忆：短期记忆、长期记忆、事件记忆
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import deque
import json

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_

from app.models.models import Interaction, Pet


@dataclass
class MemoryItem:
    """记忆项"""
    id: Optional[int] = None
    content: str = ""
    role: str = ""  # user, assistant, system
    timestamp: datetime = field(default_factory=datetime.utcnow)
    importance: float = 0.5  # 0-1
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "role": self.role,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "metadata": self.metadata,
        }


@dataclass
class EventMemory:
    """事件记忆"""
    event_type: str
    description: str
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)


class ShortTermMemory:
    """短期记忆 - 最近 N 轮对话"""

    def __init__(self, max_items: int = 10):
        self.max_items = max_items
        self._items: deque[MemoryItem] = deque(maxlen=max_items)

    def add(self, item: MemoryItem):
        """添加记忆项"""
        self._items.append(item)

    def get_all(self) -> List[MemoryItem]:
        """获取所有记忆"""
        return list(self._items)

    def get_recent(self, n: int = 5) -> List[MemoryItem]:
        """获取最近 N 条记忆"""
        return list(self._items)[-n:]

    def clear(self):
        """清空记忆"""
        self._items.clear()

    def to_messages(self) -> List[Dict[str, str]]:
        """转换为 AI 模型消息格式"""
        return [
            {"role": item.role, "content": item.content}
            for item in self._items
        ]


class LongTermMemory:
    """长期记忆 - 持久化存储"""

    def __init__(self, db: AsyncSession, pet_id: int):
        self.db = db
        self.pet_id = pet_id

    async def store(self, item: MemoryItem) -> MemoryItem:
        """存储记忆项"""
        # 存储到数据库
        interaction = Interaction(
            pet_id=self.pet_id,
            type="memory",
            content=item.content,
            response=None,
            metadata={
                "role": item.role,
                "importance": item.importance,
                "timestamp": item.timestamp.isoformat(),
                **item.metadata,
            },
        )
        self.db.add(interaction)
        await self.db.commit()
        await self.db.refresh(interaction)

        item.id = interaction.id
        return item

    async def retrieve(
        self,
        query: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        min_importance: float = 0.0,
        limit: int = 20,
    ) -> List[MemoryItem]:
        """检索记忆"""
        query_stmt = select(Interaction).where(
            Interaction.pet_id == self.pet_id,
            Interaction.type == "memory",
        )

        if start_time:
            query_stmt = query_stmt.where(Interaction.created_at >= start_time)
        if end_time:
            query_stmt = query_stmt.where(Interaction.created_at <= end_time)

        query_stmt = query_stmt.order_by(Interaction.created_at.desc()).limit(limit)

        result = await self.db.execute(query_stmt)
        interactions = result.scalars().all()

        items = []
        for interaction in interactions:
            metadata = interaction.metadata or {}
            items.append(MemoryItem(
                id=interaction.id,
                content=interaction.content,
                role=metadata.get("role", ""),
                timestamp=datetime.fromisoformat(metadata.get("timestamp", interaction.created_at.isoformat())),
                importance=metadata.get("importance", 0.5),
                metadata=metadata,
            ))

        return items

    async def compress(self, max_items: int = 100):
        """压缩记忆 - 保留重要记忆"""
        # 获取所有记忆
        all_items = await self.retrieve(limit=1000)

        if len(all_items) <= max_items:
            return

        # 按重要性排序，保留重要的
        sorted_items = sorted(all_items, key=lambda x: x.importance, reverse=True)
        keep_items = sorted_items[:max_items]

        # 删除其他记忆
        keep_ids = [item.id for item in keep_items if item.id]
        delete_stmt = select(Interaction).where(
            Interaction.pet_id == self.pet_id,
            Interaction.type == "memory",
            Interaction.id.not_in(keep_ids),
        )
        result = await self.db.execute(delete_stmt)
        to_delete = result.scalars().all()

        for interaction in to_delete:
            await self.db.delete(interaction)

        await self.db.commit()


class EventMemoryManager:
    """事件记忆管理器"""

    def __init__(self, db: AsyncSession, pet_id: int):
        self.db = db
        self.pet_id = pet_id

    async def record_event(
        self,
        event_type: str,
        description: str,
        metadata: Dict[str, Any] = None,
    ) -> EventMemory:
        """记录事件"""
        event = Interaction(
            pet_id=self.pet_id,
            type=f"event_{event_type}",
            content=description,
            response=None,
            metadata=metadata or {},
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)

        return EventMemory(
            event_type=event_type,
            description=description,
            timestamp=event.created_at,
            metadata=metadata or {},
        )

    async def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 50,
    ) -> List[EventMemory]:
        """获取事件列表"""
        query_stmt = select(Interaction).where(
            Interaction.pet_id == self.pet_id,
            Interaction.type.like("event_%"),
        )

        if event_type:
            query_stmt = query_stmt.where(Interaction.type == f"event_{event_type}")
        if start_time:
            query_stmt = query_stmt.where(Interaction.created_at >= start_time)
        if end_time:
            query_stmt = query_stmt.where(Interaction.created_at <= end_time)

        query_stmt = query_stmt.order_by(Interaction.created_at.desc()).limit(limit)

        result = await self.db.execute(query_stmt)
        interactions = result.scalars().all()

        return [
            EventMemory(
                event_type=interaction.type.replace("event_", ""),
                description=interaction.content,
                timestamp=interaction.created_at,
                metadata=interaction.metadata or {},
            )
            for interaction in interactions
        ]


class MemoryManager:
    """记忆管理器 - 统一管理所有记忆类型"""

    def __init__(self, db: AsyncSession, pet_id: int, max_short_term: int = 10):
        self.short_term = ShortTermMemory(max_items=max_short_term)
        self.long_term = LongTermMemory(db, pet_id)
        self.events = EventMemoryManager(db, pet_id)
        self.db = db
        self.pet_id = pet_id

    def add_interaction(self, role: str, content: str, importance: float = 0.5):
        """添加交互到短期记忆"""
        item = MemoryItem(
            content=content,
            role=role,
            importance=importance,
        )
        self.short_term.add(item)

        # 如果重要，同时存储到长期记忆
        if importance >= 0.7:
            asyncio.create_task(self.long_term.store(item))

    async def get_context_for_chat(self, max_items: int = 10) -> List[Dict[str, str]]:
        """获取聊天上下文"""
        # 短期记忆
        short_term = self.short_term.get_recent(max_items // 2)

        # 长期记忆
        long_term = await self.long_term.retrieve(limit=max_items // 2)

        # 合并并按时间排序
        all_items = short_term + long_term
        all_items.sort(key=lambda x: x.timestamp)

        return [
            {"role": item.role, "content": item.content}
            for item in all_items[-max_items:]
        ]

    async def record_milestone(self, description: str, metadata: Dict[str, Any] = None):
        """记录里程碑事件"""
        await self.events.record_event(
            event_type="milestone",
            description=description,
            metadata=metadata,
        )

    async def summarize(self) -> Dict[str, Any]:
        """总结记忆状态"""
        short_term_count = len(self.short_term.get_all())
        long_term_items = await self.long_term.retrieve(limit=1000)
        recent_events = await self.events.get_events(limit=10)

        return {
            "short_term_count": short_term_count,
            "long_term_count": len(long_term_items),
            "recent_events": [
                {
                    "type": e.event_type,
                    "description": e.description,
                    "timestamp": e.timestamp.isoformat(),
                }
                for e in recent_events
            ],
        }


import asyncio  # 用于异步任务
