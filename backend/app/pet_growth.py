"""
宠物成长和事件系统增强
提供完整的成长曲线、事件处理和偏好演化
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from .storage import PETS, EVENTS, EventRecord, save_state, now_iso


class GrowthStage:
    """成长阶段定义"""
    EGG = "egg"           # 蛋期 (0-10 exp)
    BABY = "baby"         # 幼年期 (11-50 exp)
    CHILD = "child"       # 童年期 (51-150 exp)
    TEEN = "teen"         # 青少年期 (151-300 exp)
    ADULT = "adult"       # 成年期 (301-500 exp)
    ELDER = "elder"       # 长者期 (501+ exp)


class EventType:
    """事件类型定义"""
    # 互动事件
    CHAT = "chat"                 # 对话
    PLAY = "play"                 # 玩耍
    FEED = "feed"                 # 喂食
    PRAISE = "praise"             # 表扬
    COMFORT = "comfort"           # 安慰
    
    # 状态事件
    WAKE_UP = "wake_up"           # 唤醒
    SLEEP = "sleep"               # 休眠
    LEVEL_UP = "level_up"         # 升级
    EVOLVE = "evolve"             # 进化
    
    # 系统事件
    DEVICE_BIND = "device_bind"   # 设备绑定
    DEVICE_UNBIND = "device_unbind"  # 设备解绑
    SYNC_SUCCESS = "sync_success"    # 同步成功
    SYNC_FAILURE = "sync_failure"    # 同步失败
    
    # 特殊事件
    FESTIVAL = "festival"         # 节日
    BIRTHDAY = "birthday"         # 生日
    MILESTONE = "milestone"       # 里程碑


# 成长曲线配置
GROWTH_CURVES = {
    "cat-default": {
        "stages": {
            GrowthStage.EGG: {"exp_min": 0, "exp_max": 10, "mood_bonus": 0},
            GrowthStage.BABY: {"exp_min": 11, "exp_max": 50, "mood_bonus": 1},
            GrowthStage.CHILD: {"exp_min": 51, "exp_max": 150, "mood_bonus": 2},
            GrowthStage.TEEN: {"exp_min": 151, "exp_max": 300, "mood_bonus": 2},
            GrowthStage.ADULT: {"exp_min": 301, "exp_max": 500, "mood_bonus": 3},
            GrowthStage.ELDER: {"exp_min": 501, "exp_max": 999999, "mood_bonus": 5},
        },
        "preferred_activities": ["play", "chat", "comfort"],
        "growth_rate": 1.0,
    },
    "monkey-default": {
        "stages": {
            GrowthStage.EGG: {"exp_min": 0, "exp_max": 15, "mood_bonus": 0},
            GrowthStage.BABY: {"exp_min": 16, "exp_max": 60, "mood_bonus": 1},
            GrowthStage.CHILD: {"exp_min": 61, "exp_max": 180, "mood_bonus": 2},
            GrowthStage.TEEN: {"exp_min": 181, "exp_max": 350, "mood_bonus": 3},
            GrowthStage.ADULT: {"exp_min": 351, "exp_max": 600, "mood_bonus": 4},
            GrowthStage.ELDER: {"exp_min": 601, "exp_max": 999999, "mood_bonus": 6},
        },
        "preferred_activities": ["play", "feed", "praise"],
        "growth_rate": 1.2,
    },
    "dino-default": {
        "stages": {
            GrowthStage.EGG: {"exp_min": 0, "exp_max": 20, "mood_bonus": 0},
            GrowthStage.BABY: {"exp_min": 21, "exp_max": 70, "mood_bonus": 1},
            GrowthStage.CHILD: {"exp_min": 71, "exp_max": 200, "mood_bonus": 2},
            GrowthStage.TEEN: {"exp_min": 201, "exp_max": 400, "mood_bonus": 3},
            GrowthStage.ADULT: {"exp_min": 401, "exp_max": 700, "mood_bonus": 4},
            GrowthStage.ELDER: {"exp_min": 701, "exp_max": 999999, "mood_bonus": 7},
        },
        "preferred_activities": ["feed", "comfort", "praise"],
        "growth_rate": 0.8,
    },
}


def get_growth_stage(species_id: str, exp: int) -> str:
    """根据经验值获取成长阶段"""
    curve = GROWTH_CURVES.get(species_id, GROWTH_CURVES["cat-default"])
    
    for stage, config in curve["stages"].items():
        if config["exp_min"] <= exp <= config["exp_max"]:
            return stage
    
    return GrowthStage.ADULT


def calculate_level(exp: int) -> int:
    """根据经验值计算等级"""
    # 简单的等级计算公式
    return max(1, int((exp / 10) ** 0.5))


def record_pet_event(
    pet_id: str,
    event_type: str,
    description: str,
    tags: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None,
) -> EventRecord:
    """记录宠物事件"""
    event = EventRecord(
        kind=event_type,
        text=description,
        tags=tags or [],
        created_at=now_iso(),
    )
    
    EVENTS.setdefault(pet_id, []).append(event)
    save_state()
    
    return event


def process_event_effects(pet_id: str, event_type: str, pet_data: Dict[str, Any]) -> Dict[str, Any]:
    """处理事件对宠物的影响"""
    pet = PETS.get(pet_id)
    if not pet:
        return pet_data
    
    # 根据事件类型调整属性
    effects = {
        EventType.CHAT: {"energy": -1, "affection": 1, "exp": 1},
        EventType.PLAY: {"energy": -3, "affection": 2, "exp": 2, "hunger": 2},
        EventType.FEED: {"energy": 2, "hunger": -10, "exp": 1},
        EventType.PRAISE: {"affection": 3, "exp": 2},
        EventType.COMFORT: {"affection": 2, "exp": 1},
        EventType.WAKE_UP: {"energy": 20},
        EventType.SLEEP: {"energy": 30, "hunger": 5},
    }
    
    effect = effects.get(event_type, {})
    
    for attr, change in effect.items():
        if hasattr(pet, attr):
            current = getattr(pet, attr)
            new_value = max(0, min(100, current + change))
            setattr(pet, attr, new_value)
    
    # 更新心情
    if event_type in [EventType.PLAY, EventType.PRAISE, EventType.CHAT]:
        pet.mood = "happy"
    elif event_type == EventType.FEED:
        pet.mood = "neutral" if pet.hunger < 50 else "hungry"
    elif event_type == EventType.SLEEP:
        pet.mood = "sleepy"
    
    save_state()
    
    return pet_data


def evolve_preferences(pet_id: str, activity: str, enjoyment_level: int = 1):
    """演化宠物偏好"""
    pet = PETS.get(pet_id)
    if not pet:
        return
    
    # 增加对应活动的偏好
    if activity in pet.growth_preferences:
        pet.growth_preferences[activity] += enjoyment_level
    
    # 记录偏好变化
    if enjoyment_level > 2:
        note = f"很喜欢{activity}"
        if note not in pet.preference_notes:
            pet.preference_notes.append(note)
    
    save_state()


def get_pet_summary(pet_id: str) -> Dict[str, Any]:
    """获取宠物完整摘要"""
    pet = PETS.get(pet_id)
    if not pet:
        return {}
    
    events = EVENTS.get(pet_id, [])
    
    # 统计事件
    event_stats = {}
    for event in events:
        event_stats[event.kind] = event_stats.get(event.kind, 0) + 1
    
    # 获取成长信息
    stage = get_growth_stage(pet.species_id, pet.exp)
    level = calculate_level(pet.exp)
    
    return {
        "pet_id": pet.pet_id,
        "name": pet.name,
        "species_id": pet.species_id,
        "theme_id": pet.theme_id,
        "growth_stage": stage,
        "level": level,
        "exp": pet.exp,
        "mood": pet.mood,
        "energy": pet.energy,
        "hunger": pet.hunger,
        "affection": pet.affection,
        "preferences": pet.growth_preferences,
        "preference_notes": pet.preference_notes,
        "event_stats": event_stats,
        "total_events": len(events),
        "device_id": pet.device_id,
        "linked_devices": len(pet.linked_device_ids),
    }


def check_milestones(pet_id: str) -> List[Dict[str, Any]]:
    """检查里程碑成就"""
    pet = PETS.get(pet_id)
    if not pet:
        return []
    
    milestones = []
    
    # 等级里程碑
    if pet.level >= 10:
        milestones.append({
            "type": "level",
            "name": "十级达成",
            "description": f"恭喜！{pet.name}已经达到10级！",
            "achieved_at": now_iso(),
        })
    
    # 互动里程碑
    events = EVENTS.get(pet_id, [])
    chat_count = sum(1 for e in events if e.kind == EventType.CHAT)
    
    if chat_count >= 100:
        milestones.append({
            "type": "interaction",
            "name": "对话大师",
            "description": f"{pet.name}已经进行了100次对话！",
            "achieved_at": now_iso(),
        })
    
    # 成长阶段里程碑
    if pet.growth_stage == GrowthStage.ADULT:
        milestones.append({
            "type": "growth",
            "name": "成年礼",
            "description": f"{pet.name}已经成长为成年期！",
            "achieved_at": now_iso(),
        })
    
    return milestones


def get_activity_recommendation(pet_id: str) -> List[str]:
    """根据宠物状态推荐活动"""
    pet = PETS.get(pet_id)
    if not pet:
        return []
    
    recommendations = []
    
    # 基于状态推荐
    if pet.hunger > 70:
        recommendations.append("喂食")
    if pet.energy < 30:
        recommendations.append("休息")
    if pet.affection < 40:
        recommendations.append("互动")
    
    # 基于偏好推荐
    if pet.growth_preferences:
        top_activity = max(pet.growth_preferences.items(), key=lambda x: x[1])
        if top_activity[1] > 5:
            activity_names = {
                "play": "玩耍",
                "chat": "对话",
                "feed": "喂食",
                "comfort": "安慰",
                "praise": "表扬",
            }
            recommendations.append(f"喜欢的{activity_names.get(top_activity[0], top_activity[0])}")
    
    return recommendations[:3]  # 最多返回3个推荐
