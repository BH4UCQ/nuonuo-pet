"""
增强的记忆系统功能
提供记忆检索、摘要、过期清理等高级功能
"""

from __future__ import annotations

from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional
from .storage import MEMORY, MemoryRecord, save_state


def get_memory_stats(pet_id: str) -> Dict[str, Any]:
    """获取记忆统计信息"""
    items = MEMORY.get(pet_id, [])

    # 按类型统计
    short_term = [item for item in items if item.kind == "short"]
    long_term = [item for item in items if item.kind == "long"]
    event_memories = [item for item in items if item.kind == "event"]

    # 按时间统计
    now = datetime.now(timezone.utc)
    recent_24h = []
    recent_7d = []

    for item in items:
        try:
            created = datetime.fromisoformat(item.created_at.replace('Z', '+00:00'))
            age = now - created

            if age < timedelta(hours=24):
                recent_24h.append(item)
            if age < timedelta(days=7):
                recent_7d.append(item)
        except (ValueError, AttributeError):
            continue

    # 标签统计
    tag_counts: Dict[str, int] = {}
    for item in items:
        for tag in item.tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "total": len(items),
        "short_term": len(short_term),
        "long_term": len(long_term),
        "event_memories": len(event_memories),
        "recent_24h": len(recent_24h),
        "recent_7d": len(recent_7d),
        "top_tags": sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10],
    }


def search_memory(pet_id: str, query: str, limit: int = 20) -> List[MemoryRecord]:
    """搜索记忆内容"""
    items = MEMORY.get(pet_id, [])
    if not query:
        return items[-limit:]

    query_lower = query.lower()
    scored_items = []

    for item in items:
        score = 0

        # 文本匹配
        if query_lower in item.text.lower():
            score += 10

        # 标签匹配
        for tag in item.tags:
            if query_lower in tag.lower():
                score += 5

        # 精确匹配加分
        if query_lower == item.text.lower():
            score += 20

        if score > 0:
            scored_items.append((score, item))

    # 按分数排序，分数相同则按时间排序
    scored_items.sort(key=lambda x: (x[0], x[1].created_at), reverse=True)

    return [item for score, item in scored_items[:limit]]


def get_memory_summary(pet_id: str, max_items: int = 5) -> Dict[str, Any]:
    """生成记忆摘要，用于AI上下文"""
    items = MEMORY.get(pet_id, [])

    # 获取最近的短期记忆
    short_term = [item for item in items if item.kind == "short"][-max_items:]

    # 获取所有长期记忆
    long_term = [item for item in items if item.kind == "long"]

    # 获取最近的事件记忆
    events = [item for item in items if item.kind == "event"][-max_items:]

    return {
        "pet_id": pet_id,
        "short_term_count": len(short_term),
        "long_term_count": len(long_term),
        "event_count": len(events),
        "recent_short_term": [
            {"text": item.text, "tags": item.tags, "created_at": item.created_at}
            for item in short_term
        ],
        "long_term": [
            {"text": item.text, "tags": item.tags, "created_at": item.created_at}
            for item in long_term
        ],
        "recent_events": [
            {"text": item.text, "tags": item.tags, "created_at": item.created_at}
            for item in events
        ],
    }


def cleanup_old_memories(pet_id: str, max_age_days: int = 30, keep_long_term: bool = True) -> int:
    """清理过期记忆"""
    items = MEMORY.get(pet_id, [])
    if not items:
        return 0

    now = datetime.now(timezone.utc)
    cutoff = now - timedelta(days=max_age_days)

    cleaned_count = 0
    new_items = []

    for item in items:
        try:
            created = datetime.fromisoformat(item.created_at.replace('Z', '+00:00'))

            # 保留长期记忆
            if keep_long_term and item.kind == "long":
                new_items.append(item)
                continue

            # 保留未过期的记忆
            if created > cutoff:
                new_items.append(item)
                continue

            cleaned_count += 1

        except (ValueError, AttributeError):
            # 保留无法解析时间的记忆
            new_items.append(item)

    if cleaned_count > 0:
        MEMORY[pet_id] = new_items
        save_state()

    return cleaned_count


def merge_memories(pet_id: str, source_items: List[MemoryRecord]) -> int:
    """合并记忆（用于导入或同步）"""
    existing = MEMORY.get(pet_id, [])
    existing_texts = {item.text for item in existing}

    merged_count = 0
    for item in source_items:
        # 避免重复
        if item.text not in existing_texts:
            existing.append(item)
            existing_texts.add(item.text)
            merged_count += 1

    if merged_count > 0:
        MEMORY[pet_id] = existing
        save_state()

    return merged_count


def export_memories(pet_id: str, kind: Optional[str] = None) -> List[Dict[str, Any]]:
    """导出记忆（用于备份或迁移）"""
    items = MEMORY.get(pet_id, [])

    if kind:
        items = [item for item in items if item.kind == kind]

    return [
        {
            "kind": item.kind,
            "text": item.text,
            "tags": list(item.tags),
            "created_at": item.created_at,
        }
        for item in items
    ]


def get_memory_context_for_chat(pet_id: str, max_tokens: int = 500) -> str:
    """生成用于聊天的记忆上下文"""
    summary = get_memory_summary(pet_id, max_items=3)

    context_parts = []

    # 添加长期记忆
    if summary["long_term"]:
        context_parts.append("长期记忆:")
        for item in summary["long_term"][:3]:  # 最多3条长期记忆
            context_parts.append(f"- {item['text']}")

    # 添加最近的短期记忆
    if summary["recent_short_term"]:
        context_parts.append("\n最近互动:")
        for item in summary["recent_short_term"]:
            context_parts.append(f"- {item['text']}")

    # 添加最近事件
    if summary["recent_events"]:
        context_parts.append("\n最近事件:")
        for item in summary["recent_events"]:
            context_parts.append(f"- {item['text']}")

    context = "\n".join(context_parts)

    # 简单的token限制（假设平均每个token约4个字符）
    if len(context) > max_tokens * 4:
        context = context[:max_tokens * 4]

    return context
