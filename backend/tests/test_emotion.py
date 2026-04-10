"""
情绪引擎测试
"""
import pytest
from datetime import datetime, timedelta

from app.services.emotion import (
    EmotionEngine,
    EmotionType,
    EmotionState,
    EmotionEvent,
    create_emotion_engine,
)


class TestEmotionEngine:
    """情绪引擎测试类"""

    def test_initialization(self):
        """测试初始化"""
        engine = EmotionEngine()
        
        assert engine.state.emotion == EmotionType.CALM
        assert engine.state.intensity == 0.5
        assert engine.state.values[EmotionType.CALM.value] == 1.0

    def test_process_interaction_chat(self):
        """测试聊天交互"""
        engine = EmotionEngine()
        
        state = engine.process_interaction("chat")
        
        # 聊天应该增加开心情绪
        assert engine.state.values["happy"] > 0
        # 聊天应该减少孤独情绪
        assert engine.state.values["lonely"] < 1.0

    def test_process_interaction_touch(self):
        """测试触摸交互"""
        engine = EmotionEngine()
        
        state = engine.process_interaction("touch")
        
        # 触摸应该增加开心情绪
        assert engine.state.values["happy"] > 0

    def test_process_interaction_feed(self):
        """测试喂食交互"""
        engine = EmotionEngine()
        
        state = engine.process_interaction("feed")
        
        # 喂食应该增加开心情绪
        assert engine.state.values["happy"] > 0

    def test_process_interaction_play(self):
        """测试玩耍交互"""
        engine = EmotionEngine()
        
        state = engine.process_interaction("play")
        
        # 玩耍应该增加开心和兴奋情绪
        assert engine.state.values["happy"] > 0
        assert engine.state.values["excited"] > 0

    def test_emotion_decay(self):
        """测试情绪衰减"""
        engine = EmotionEngine()
        
        # 设置一个高开心值
        engine.state.values["happy"] = 0.8
        engine.state.values["calm"] = 0.2
        
        # 更新情绪（无事件，触发衰减）
        import time
        time.sleep(0.1)  # 等待一小段时间
        state = engine.update()
        
        # 开心情绪应该衰减
        assert engine.state.values["happy"] < 0.8
        # 平静情绪应该增加
        assert engine.state.values["calm"] > 0.2

    def test_get_dominant_emotion(self):
        """测试获取主导情绪"""
        engine = EmotionEngine()
        
        # 设置情绪值
        engine.state.values["happy"] = 0.7
        engine.state.values["sad"] = 0.2
        engine.state.values["calm"] = 0.1
        
        dominant = engine.state.get_dominant_emotion()
        assert dominant == EmotionType.HAPPY

    def test_get_emotion_for_display(self):
        """测试获取显示情绪"""
        engine = EmotionEngine()
        engine.process_interaction("chat")
        
        display = engine.get_emotion_for_display()
        
        assert "emotion" in display
        assert "intensity" in display
        assert "emoji" in display
        assert "color" in display

    def test_state_serialization(self):
        """测试状态序列化"""
        engine = EmotionEngine()
        engine.process_interaction("chat")
        
        state_dict = engine.get_state()
        
        assert "emotion" in state_dict
        assert "intensity" in state_dict
        assert "values" in state_dict
        
        # 从状态恢复
        new_engine = create_emotion_engine(state_dict)
        assert new_engine.state.emotion == engine.state.emotion

    def test_multiple_interactions(self):
        """测试多次交互"""
        engine = EmotionEngine()
        
        # 多次交互
        for _ in range(5):
            engine.process_interaction("chat")
        
        # 开心情绪应该累积
        assert engine.state.values["happy"] > 0.5
