"""
情绪引擎服务
实现宠物情绪模拟系统
"""
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
import math


class EmotionType(Enum):
    """情绪类型"""
    HAPPY = "happy"        # 开心
    SAD = "sad"            # 悲伤
    ANGRY = "angry"        # 愤怒
    FEAR = "fear"          # 恐惧
    SURPRISE = "surprise"  # 惊讶
    CALM = "calm"          # 平静
    EXCITED = "excited"    # 兴奋
    LONELY = "lonely"      # 孤独


@dataclass
class EmotionState:
    """情绪状态"""
    emotion: EmotionType = EmotionType.CALM
    intensity: float = 0.5  # 0-1
    timestamp: datetime = field(default_factory=datetime.utcnow)

    # 各情绪分量
    values: Dict[str, float] = field(default_factory=lambda: {
        "happy": 0.0,
        "sad": 0.0,
        "angry": 0.0,
        "fear": 0.0,
        "surprise": 0.0,
        "calm": 1.0,
        "excited": 0.0,
        "lonely": 0.0,
    })

    def get_dominant_emotion(self) -> EmotionType:
        """获取主导情绪"""
        max_emotion = max(self.values.items(), key=lambda x: x[1])
        return EmotionType(max_emotion[0])

    def to_dict(self) -> Dict[str, Any]:
        return {
            "emotion": self.emotion.value,
            "intensity": self.intensity,
            "values": self.values,
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class EmotionEvent:
    """情绪事件"""
    event_type: str
    impact: Dict[str, float]  # 对各情绪的影响
    duration: timedelta = timedelta(seconds=0)


class EmotionEngine:
    """情绪引擎"""

    # 情绪衰减率 (每分钟)
    DECAY_RATE = 0.02

    # 情绪影响配置
    EVENT_IMPACTS = {
        "user_interaction": {
            "happy": 0.3,
            "lonely": -0.2,
            "calm": -0.1,
        },
        "user_ignore": {
            "lonely": 0.2,
            "sad": 0.1,
            "happy": -0.1,
        },
        "feed": {
            "happy": 0.2,
            "calm": 0.1,
            "angry": -0.2,
        },
        "play": {
            "happy": 0.3,
            "excited": 0.2,
            "calm": -0.1,
        },
        "touch": {
            "happy": 0.2,
            "calm": 0.1,
            "lonely": -0.1,
        },
        "scold": {
            "sad": 0.3,
            "fear": 0.2,
            "happy": -0.2,
        },
        "praise": {
            "happy": 0.4,
            "excited": 0.2,
            "sad": -0.1,
        },
        "timeout": {
            "lonely": 0.1,
            "calm": 0.1,
        },
        "level_up": {
            "happy": 0.5,
            "excited": 0.3,
        },
        "evolution": {
            "happy": 0.6,
            "excited": 0.4,
            "surprise": 0.3,
        },
    }

    def __init__(self):
        self.state = EmotionState()
        self.last_update = datetime.utcnow()

    def update(self, event: Optional[EmotionEvent] = None) -> EmotionState:
        """更新情绪状态"""
        now = datetime.utcnow()
        elapsed = (now - self.last_update).total_seconds() / 60  # 分钟

        # 情绪衰减
        self._decay(elapsed)

        # 应用事件影响
        if event:
            self._apply_event(event)

        # 更新主导情绪
        self.state.emotion = self.state.get_dominant_emotion()
        self.state.intensity = self.state.values[self.state.emotion.value]
        self.state.timestamp = now
        self.last_update = now

        return self.state

    def _decay(self, elapsed_minutes: float):
        """情绪衰减 - 趋向平静"""
        decay = math.exp(-self.DECAY_RATE * elapsed_minutes)

        for emotion in self.state.values:
            if emotion == "calm":
                # 平静情绪增加
                self.state.values[emotion] = min(
                    1.0,
                    self.state.values[emotion] + (1 - decay) * 0.1
                )
            else:
                # 其他情绪衰减
                self.state.values[emotion] *= decay

        # 归一化
        self._normalize()

    def _apply_event(self, event: EmotionEvent):
        """应用事件影响"""
        for emotion, delta in event.impact.items():
            if emotion in self.state.values:
                self.state.values[emotion] = max(
                    0.0,
                    min(1.0, self.state.values[emotion] + delta)
                )

        self._normalize()

    def _normalize(self):
        """归一化情绪值"""
        total = sum(self.state.values.values())
        if total > 1.0:
            for emotion in self.state.values:
                self.state.values[emotion] /= total

    def process_interaction(self, interaction_type: str) -> EmotionState:
        """处理交互事件"""
        impact = self.EVENT_IMPACTS.get(interaction_type, {})
        event = EmotionEvent(
            event_type=interaction_type,
            impact=impact,
        )
        return self.update(event)

    def get_emotion_for_display(self) -> Dict[str, Any]:
        """获取用于显示的情绪状态"""
        return {
            "emotion": self.state.emotion.value,
            "intensity": self.state.intensity,
            "emoji": self._get_emotion_emoji(),
            "color": self._get_emotion_color(),
        }

    def _get_emotion_emoji(self) -> str:
        """获取情绪对应的 emoji"""
        emojis = {
            EmotionType.HAPPY: "😊",
            EmotionType.SAD: "😢",
            EmotionType.ANGRY: "😠",
            EmotionType.FEAR: "😨",
            EmotionType.SURPRISE: "😲",
            EmotionType.CALM: "😌",
            EmotionType.EXCITED: "🤩",
            EmotionType.LONELY: "🥺",
        }
        return emojis.get(self.state.emotion, "😐")

    def _get_emotion_color(self) -> str:
        """获取情绪对应的颜色"""
        colors = {
            EmotionType.HAPPY: "#FFD700",      # 金色
            EmotionType.SAD: "#4169E1",        # 蓝色
            EmotionType.ANGRY: "#FF4500",      # 红橙色
            EmotionType.FEAR: "#800080",       # 紫色
            EmotionType.SURPRISE: "#FF69B4",   # 粉色
            EmotionType.CALM: "#90EE90",       # 浅绿
            EmotionType.EXCITED: "#FF1493",    # 深粉
            EmotionType.LONELY: "#708090",     # 灰色
        }
        return colors.get(self.state.emotion, "#808080")

    def set_state(self, state: Dict[str, Any]):
        """设置情绪状态 (从数据库恢复)"""
        self.state.emotion = EmotionType(state.get("emotion", "calm"))
        self.state.intensity = state.get("intensity", 0.5)
        self.state.values = state.get("values", self.state.values)
        self.state.timestamp = datetime.fromisoformat(
            state.get("timestamp", datetime.utcnow().isoformat())
        )

    def get_state(self) -> Dict[str, Any]:
        """获取情绪状态 (用于存储)"""
        return self.state.to_dict()


# 情绪引擎工厂
def create_emotion_engine(initial_state: Optional[Dict[str, Any]] = None) -> EmotionEngine:
    """创建情绪引擎"""
    engine = EmotionEngine()
    if initial_state:
        engine.set_state(initial_state)
    return engine
