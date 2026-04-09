"""
LLM 上下文构建器
负责整合记忆、性格、状态等信息构建对话上下文
"""
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import (
    ConversationContext,
    ConversationMessage,
    MemoryItem,
    PetProfileResponse
)


class LLMContextBuilder:
    """LLM 上下文构建器"""

    def __init__(self):
        """初始化上下文构建器"""
        self.max_memory_items = 10
        self.max_recent_events = 5
        self.max_history_messages = 20

    def build_system_prompt(
        self,
        pet_profile: PetProfileResponse,
        personality_traits: Optional[List[str]] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """
        构建系统提示词

        Args:
            pet_profile: 宠物档案
            personality_traits: 性格特征
            custom_prompt: 自定义提示词

        Returns:
            系统提示词
        """
        if custom_prompt:
            return custom_prompt

        # 基础提示词
        prompt_parts = [
            f"你是 {pet_profile.name}，一只可爱的电子宠物。",
            f"你的物种是 {pet_profile.species_id}。",
            f"你现在的成长阶段是 {pet_profile.growth_stage}，等级 {pet_profile.level}。",
        ]

        # 添加状态信息
        prompt_parts.append(f"你的心情是 {pet_profile.mood}。")
        prompt_parts.append(f"你的能量值是 {pet_profile.energy}/100。")
        prompt_parts.append(f"你的饥饿度是 {pet_profile.hunger}/100。")
        prompt_parts.append(f"你的亲密度是 {pet_profile.affection}/100。")

        # 添加性格特征
        if personality_traits:
            traits_str = "、".join(personality_traits)
            prompt_parts.append(f"你的性格特征包括：{traits_str}。")

        # 添加行为指导
        prompt_parts.extend([
            "请以宠物的身份与主人互动，表现出可爱、活泼的性格。",
            "根据你的状态（心情、能量、饥饿度）调整你的回应方式。",
            "如果能量低或饥饿度高，可以表现出疲惫或需要照顾的样子。",
            "如果亲密度高，可以表现出更亲密、粘人的行为。",
            "保持回应简洁、自然，符合宠物的说话风格。",
        ])

        return "\n".join(prompt_parts)

    def build_conversation_context(
        self,
        pet_profile: PetProfileResponse,
        memory_items: Optional[List[MemoryItem]] = None,
        recent_events: Optional[List[Dict[str, Any]]] = None,
        conversation_history: Optional[List[ConversationMessage]] = None,
        user_preferences: Optional[Dict[str, Any]] = None,
        custom_system_prompt: Optional[str] = None
    ) -> ConversationContext:
        """
        构建对话上下文

        Args:
            pet_profile: 宠物档案
            memory_items: 记忆项
            recent_events: 最近事件
            conversation_history: 对话历史
            user_preferences: 用户偏好
            custom_system_prompt: 自定义系统提示词

        Returns:
            对话上下文
        """
        # 获取性格特征
        personality_traits = self._extract_personality_traits(pet_profile)

        # 构建系统提示词
        system_prompt = self.build_system_prompt(
            pet_profile,
            personality_traits,
            custom_system_prompt
        )

        # 构建当前状态
        current_state = {
            "mood": pet_profile.mood,
            "energy": pet_profile.energy,
            "hunger": pet_profile.hunger,
            "affection": pet_profile.affection,
            "growth_stage": pet_profile.growth_stage,
            "level": pet_profile.level,
            "exp": pet_profile.exp,
        }

        # 限制记忆项数量
        limited_memory = []
        if memory_items:
            limited_memory = memory_items[:self.max_memory_items]

        # 限制最近事件数量
        limited_events = []
        if recent_events:
            limited_events = recent_events[:self.max_recent_events]

        return ConversationContext(
            pet_id=pet_profile.pet_id,
            system_prompt=system_prompt,
            personality_traits=personality_traits,
            current_state=current_state,
            memory_items=limited_memory,
            recent_events=limited_events,
            user_preferences=user_preferences or {}
        )

    def build_messages_for_llm(
        self,
        context: ConversationContext,
        user_message: str,
        conversation_history: Optional[List[ConversationMessage]] = None
    ) -> List[ConversationMessage]:
        """
        构建 LLM 消息列表

        Args:
            context: 对话上下文
            user_message: 用户消息
            conversation_history: 对话历史

        Returns:
            消息列表
        """
        messages = []

        # 添加系统提示词
        if context.system_prompt:
            messages.append(ConversationMessage(
                role="system",
                content=context.system_prompt,
                timestamp=datetime.now().isoformat()
            ))

        # 添加记忆上下文
        if context.memory_items:
            memory_context = self._build_memory_context(context.memory_items)
            if memory_context:
                messages.append(ConversationMessage(
                    role="system",
                    content=f"记忆信息：\n{memory_context}",
                    timestamp=datetime.now().isoformat()
                ))

        # 添加最近事件上下文
        if context.recent_events:
            events_context = self._build_events_context(context.recent_events)
            if events_context:
                messages.append(ConversationMessage(
                    role="system",
                    content=f"最近发生的事情：\n{events_context}",
                    timestamp=datetime.now().isoformat()
                ))

        # 添加对话历史
        if conversation_history:
            # 限制历史消息数量
            limited_history = conversation_history[-self.max_history_messages:]
            messages.extend(limited_history)

        # 添加用户消息
        messages.append(ConversationMessage(
            role="user",
            content=user_message,
            timestamp=datetime.now().isoformat()
        ))

        return messages

    def _extract_personality_traits(self, pet_profile: PetProfileResponse) -> List[str]:
        """
        提取性格特征

        Args:
            pet_profile: 宠物档案

        Returns:
            性格特征列表
        """
        traits = []

        # 根据物种添加基础特征
        if "cat" in pet_profile.species_id.lower():
            traits.extend(["独立", "优雅", "好奇"])
        elif "dog" in pet_profile.species_id.lower():
            traits.extend(["忠诚", "活泼", "友善"])
        else:
            traits.extend(["可爱", "友善"])

        # 根据状态调整特征
        if pet_profile.mood == "happy":
            traits.append("开心")
        elif pet_profile.mood == "sad":
            traits.append("需要安慰")
        elif pet_profile.mood == "hungry":
            traits.append("饥饿")

        if pet_profile.affection > 80:
            traits.append("非常亲密")
        elif pet_profile.affection < 30:
            traits.append("需要更多关爱")

        return traits

    def _build_memory_context(self, memory_items: List[MemoryItem]) -> str:
        """
        构建记忆上下文

        Args:
            memory_items: 记忆项列表

        Returns:
            记忆上下文字符串
        """
        if not memory_items:
            return ""

        context_parts = []
        for item in memory_items:
            tags_str = ", ".join(item.tags) if item.tags else ""
            context_parts.append(f"- {item.text} (标签: {tags_str})")

        return "\n".join(context_parts)

    def _build_events_context(self, events: List[Dict[str, Any]]) -> str:
        """
        构建事件上下文

        Args:
            events: 事件列表

        Returns:
            事件上下文字符串
        """
        if not events:
            return ""

        context_parts = []
        for event in events:
            kind = event.get("kind", "unknown")
            text = event.get("text", "")
            created_at = event.get("created_at", "")

            if created_at:
                try:
                    dt = datetime.fromisoformat(created_at)
                    time_str = dt.strftime("%H:%M")
                except:
                    time_str = created_at
            else:
                time_str = "未知时间"

            context_parts.append(f"- [{time_str}] {kind}: {text}")

        return "\n".join(context_parts)

    def update_context_with_response(
        self,
        context: ConversationContext,
        response_text: str,
        emotion: Optional[str] = None
    ) -> ConversationContext:
        """
        用响应更新上下文

        Args:
            context: 原始上下文
            response_text: 响应文本
            emotion: 情绪

        Returns:
            更新后的上下文
        """
        # 更新当前状态
        updated_state = context.current_state.copy()

        if emotion:
            updated_state["current_emotion"] = emotion

        # 添加响应到最近事件
        updated_events = context.recent_events.copy()
        updated_events.insert(0, {
            "kind": "assistant_response",
            "text": response_text,
            "created_at": datetime.now().isoformat(),
            "emotion": emotion
        })

        # 限制事件数量
        updated_events = updated_events[:self.max_recent_events]

        return ConversationContext(
            pet_id=context.pet_id,
            conversation_id=context.conversation_id,
            system_prompt=context.system_prompt,
            personality_traits=context.personality_traits,
            current_state=updated_state,
            memory_items=context.memory_items,
            recent_events=updated_events,
            user_preferences=context.user_preferences
        )


# 全局上下文构建器实例
_context_builder: Optional[LLMContextBuilder] = None


def get_context_builder() -> LLMContextBuilder:
    """获取上下文构建器实例"""
    global _context_builder
    if _context_builder is None:
        _context_builder = LLMContextBuilder()
    return _context_builder
