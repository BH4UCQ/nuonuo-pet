"""
成长引擎测试
"""
import pytest

from app.services.growth import (
    GrowthEngine,
    GrowthStage,
    GrowthState,
    create_growth_engine,
)


class TestGrowthEngine:
    """成长引擎测试类"""

    def test_initialization(self):
        """测试初始化"""
        engine = GrowthEngine()
        
        assert engine.state.level == 1
        assert engine.state.experience == 0
        assert engine.state.stage == GrowthStage.BABY

    def test_add_experience(self):
        """测试添加经验值"""
        engine = GrowthEngine()
        
        result = engine.add_experience(100, "test")
        
        assert engine.state.experience == 100
        assert result["xp_gained"] == 100

    def test_level_up(self):
        """测试升级"""
        engine = GrowthEngine()
        
        # 添加足够经验值升级
        result = engine.add_experience(150, "test")
        
        # 应该升到 2 级
        assert engine.state.level == 2
        assert result["level_up"] == True
        assert result["new_level"] == 2

    def test_add_interaction(self):
        """测试添加交互"""
        engine = GrowthEngine()
        
        result = engine.add_interaction("chat")
        
        assert engine.state.total_interactions == 1
        assert engine.state.experience > 0  # 应该获得经验值

    def test_interaction_xp_rewards(self):
        """测试不同交互的经验值奖励"""
        engine = GrowthEngine()
        
        # 聊天
        engine.add_interaction("chat")
        chat_xp = engine.state.experience
        
        # 玩耍（应该给更多经验值）
        engine.add_interaction("play")
        play_xp = engine.state.experience - chat_xp
        
        assert play_xp > chat_xp

    def test_evolution_baby_to_child(self):
        """测试进化：幼年期到少年期"""
        engine = GrowthEngine()
        
        # 满足进化条件
        engine.state.level = 3
        engine.state.total_interactions = 50
        engine.state.total_days = 7
        
        result = engine.add_experience(0, "test")
        
        # 应该进化到少年期
        assert engine.state.stage == GrowthStage.CHILD

    def test_achievement(self):
        """测试成就系统"""
        engine = GrowthEngine()
        
        result = engine.add_achievement(1, "First Steps")
        
        assert result["added"] == True
        assert 1 in engine.state.achievements
        # 成就应该奖励经验值
        assert engine.state.experience > 0

    def test_duplicate_achievement(self):
        """测试重复成就"""
        engine = GrowthEngine()
        
        engine.add_achievement(1, "First Steps")
        result = engine.add_achievement(1, "First Steps")
        
        assert result["added"] == False

    def test_get_progress(self):
        """测试获取进度"""
        engine = GrowthEngine()
        engine.add_interaction("chat")
        
        progress = engine.get_progress()
        
        assert "level" in progress
        assert "experience" in progress
        assert "stage" in progress
        assert "total_interactions" in progress

    def test_state_serialization(self):
        """测试状态序列化"""
        engine = GrowthEngine()
        engine.add_interaction("chat")
        engine.add_interaction("play")
        
        state_dict = engine.get_state()
        
        assert "level" in state_dict
        assert "experience" in state_dict
        assert "stage" in state_dict
        
        # 从状态恢复
        new_engine = create_growth_engine(state_dict)
        assert new_engine.state.level == engine.state.level
        assert new_engine.state.experience == engine.state.experience

    def test_max_level(self):
        """测试最大等级"""
        engine = GrowthEngine()
        
        # 添加大量经验值
        engine.add_experience(10000, "test")
        
        # 不应该超过 10 级
        assert engine.state.level <= 10
