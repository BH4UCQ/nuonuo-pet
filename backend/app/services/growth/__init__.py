"""
成长引擎服务
实现宠物成长和进化机制
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class GrowthStage(Enum):
    """成长阶段"""
    BABY = "baby"          # 幼年期
    CHILD = "child"        # 少年期
    TEEN = "teen"          # 青年期
    ADULT = "adult"        # 成年期
    ELDER = "elder"        # 长老期


@dataclass
class LevelConfig:
    """等级配置"""
    level: int
    experience_required: int
    title: str
    unlocks: List[str] = field(default_factory=list)


@dataclass
class EvolutionConfig:
    """进化配置"""
    from_stage: GrowthStage
    to_stage: GrowthStage
    required_level: int
    required_interactions: int
    required_days: int
    bonus_abilities: List[str] = field(default_factory=list)


@dataclass
class GrowthState:
    """成长状态"""
    level: int = 1
    experience: int = 0
    stage: GrowthStage = GrowthStage.BABY
    total_interactions: int = 0
    total_days: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)

    # 成就
    achievements: List[str] = field(default_factory=list)

    # 能力
    abilities: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "level": self.level,
            "experience": self.experience,
            "stage": self.stage.value,
            "total_interactions": self.total_interactions,
            "total_days": self.total_days,
            "created_at": self.created_at.isoformat(),
            "achievements": self.achievements,
            "abilities": self.abilities,
        }


class GrowthEngine:
    """成长引擎"""

    # 等级配置
    LEVELS: List[LevelConfig] = [
        LevelConfig(1, 0, "新手", []),
        LevelConfig(2, 100, "学徒", ["basic_emotions"]),
        LevelConfig(3, 300, "见习", ["advanced_emotions"]),
        LevelConfig(4, 600, "熟练", ["custom_themes"]),
        LevelConfig(5, 1000, "精通", ["special_abilities"]),
        LevelConfig(6, 1500, "专家", ["evolution_preview"]),
        LevelConfig(7, 2100, "大师", ["all_themes"]),
        LevelConfig(8, 2800, "宗师", ["legendary_skins"]),
        LevelConfig(9, 3600, "传奇", ["special_evolutions"]),
        LevelConfig(10, 4500, "神话", ["god_mode"]),
    ]

    # 进化配置
    EVOLUTIONS: List[EvolutionConfig] = [
        EvolutionConfig(
            from_stage=GrowthStage.BABY,
            to_stage=GrowthStage.CHILD,
            required_level=3,
            required_interactions=50,
            required_days=7,
            bonus_abilities=["faster_growth"],
        ),
        EvolutionConfig(
            from_stage=GrowthStage.CHILD,
            to_stage=GrowthStage.TEEN,
            required_level=5,
            required_interactions=200,
            required_days=30,
            bonus_abilities=["advanced_ai"],
        ),
        EvolutionConfig(
            from_stage=GrowthStage.TEEN,
            to_stage=GrowthStage.ADULT,
            required_level=7,
            required_interactions=500,
            required_days=90,
            bonus_abilities=["full_customization"],
        ),
        EvolutionConfig(
            from_stage=GrowthStage.ADULT,
            to_stage=GrowthStage.ELDER,
            required_level=10,
            required_interactions=1000,
            required_days=365,
            bonus_abilities=["wisdom_bonus"],
        ),
    ]

    # 经验值获取配置
    XP_REWARDS = {
        "chat": 10,
        "touch": 5,
        "feed": 8,
        "play": 15,
        "daily_login": 20,
        "achievement": 50,
        "evolution": 100,
    }

    def __init__(self):
        self.state = GrowthState()

    def add_experience(self, amount: int, source: str = "interaction") -> Dict[str, Any]:
        """增加经验值"""
        self.state.experience += amount

        result = {
            "xp_gained": amount,
            "source": source,
            "level_up": False,
            "new_level": self.state.level,
            "evolution": False,
            "new_stage": self.state.stage.value,
        }

        # 检查升级
        if self._check_level_up():
            result["level_up"] = True
            result["new_level"] = self.state.level
            result["unlocks"] = self._get_level_unlocks(self.state.level)

        # 检查进化
        evolution_result = self._check_evolution()
        if evolution_result:
            result["evolution"] = True
            result["new_stage"] = self.state.stage.value
            result["evolution_bonus"] = evolution_result

        return result

    def add_interaction(self, interaction_type: str) -> Dict[str, Any]:
        """添加交互"""
        self.state.total_interactions += 1

        # 获取经验值
        xp = self.XP_REWARDS.get(interaction_type, 5)
        return self.add_experience(xp, interaction_type)

    def update_days(self, days: int):
        """更新天数"""
        self.state.total_days = days

    def _check_level_up(self) -> bool:
        """检查是否升级"""
        current_config = self._get_level_config(self.state.level)
        next_config = self._get_level_config(self.state.level + 1)

        if not next_config:
            return False

        if self.state.experience >= next_config.experience_required:
            self.state.level = next_config.level
            self.state.abilities.extend(next_config.unlocks)
            return True

        return False

    def _check_evolution(self) -> Optional[Dict[str, Any]]:
        """检查是否可以进化"""
        for evolution in self.EVOLUTIONS:
            if evolution.from_stage != self.state.stage:
                continue

            if (
                self.state.level >= evolution.required_level
                and self.state.total_interactions >= evolution.required_interactions
                and self.state.total_days >= evolution.required_days
            ):
                # 执行进化
                self.state.stage = evolution.to_stage
                self.state.abilities.extend(evolution.bonus_abilities)

                # 进化奖励
                self.add_experience(self.XP_REWARDS["evolution"], "evolution")

                return {
                    "from_stage": evolution.from_stage.value,
                    "to_stage": evolution.to_stage.value,
                    "bonus_abilities": evolution.bonus_abilities,
                }

        return None

    def _get_level_config(self, level: int) -> Optional[LevelConfig]:
        """获取等级配置"""
        for config in self.LEVELS:
            if config.level == level:
                return config
        return None

    def _get_level_unlocks(self, level: int) -> List[str]:
        """获取等级解锁内容"""
        config = self._get_level_config(level)
        return config.unlocks if config else []

    def add_achievement(self, achievement_id: str, name: str) -> Dict[str, Any]:
        """添加成就"""
        if achievement_id in self.state.achievements:
            return {"added": False, "reason": "already_achieved"}

        self.state.achievements.append(achievement_id)
        xp_result = self.add_experience(self.XP_REWARDS["achievement"], "achievement")

        return {
            "added": True,
            "achievement_id": achievement_id,
            "name": name,
            "xp_gained": self.XP_REWARDS["achievement"],
            **xp_result,
        }

    def get_progress(self) -> Dict[str, Any]:
        """获取成长进度"""
        current_config = self._get_level_config(self.state.level)
        next_config = self._get_level_config(self.state.level + 1)

        progress = {
            "level": self.state.level,
            "level_title": current_config.title if current_config else "",
            "experience": self.state.experience,
            "experience_required": next_config.experience_required if next_config else None,
            "experience_progress": 0.0,
            "stage": self.state.stage.value,
            "total_interactions": self.state.total_interactions,
            "total_days": self.state.total_days,
            "achievements": self.state.achievements,
            "abilities": self.state.abilities,
        }

        if next_config and current_config:
            xp_in_level = self.state.experience - current_config.experience_required
            xp_for_level = next_config.experience_required - current_config.experience_required
            progress["experience_progress"] = min(1.0, xp_in_level / xp_for_level)

        # 进化进度
        evolution_progress = self._get_evolution_progress()
        if evolution_progress:
            progress["evolution_progress"] = evolution_progress

        return progress

    def _get_evolution_progress(self) -> Optional[Dict[str, Any]]:
        """获取进化进度"""
        for evolution in self.EVOLUTIONS:
            if evolution.from_stage != self.state.stage:
                continue

            return {
                "to_stage": evolution.to_stage.value,
                "level_progress": min(1.0, self.state.level / evolution.required_level),
                "interaction_progress": min(1.0, self.state.total_interactions / evolution.required_interactions),
                "day_progress": min(1.0, self.state.total_days / evolution.required_days),
            }

        return None

    def set_state(self, state: Dict[str, Any]):
        """设置成长状态 (从数据库恢复)"""
        self.state.level = state.get("level", 1)
        self.state.experience = state.get("experience", 0)
        self.state.stage = GrowthStage(state.get("stage", "baby"))
        self.state.total_interactions = state.get("total_interactions", 0)
        self.state.total_days = state.get("total_days", 0)
        self.state.achievements = state.get("achievements", [])
        self.state.abilities = state.get("abilities", [])

        if "created_at" in state:
            self.state.created_at = datetime.fromisoformat(state["created_at"])

    def get_state(self) -> Dict[str, Any]:
        """获取成长状态 (用于存储)"""
        return self.state.to_dict()


# 成长引擎工厂
def create_growth_engine(initial_state: Optional[Dict[str, Any]] = None) -> GrowthEngine:
    """创建成长引擎"""
    engine = GrowthEngine()
    if initial_state:
        engine.set_state(initial_state)
    return engine
