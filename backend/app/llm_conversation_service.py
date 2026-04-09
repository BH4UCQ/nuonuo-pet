"""
LLM 对话服务核心
负责完整的对话流程协调
"""
import json
import os
import uuid
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from pathlib import Path

from .models import (
    LLMRequest,
    LLMResponse,
    ConversationHistory,
    ConversationMessage,
    ConversationContext,
    ConversationSummary,
    PetProfileResponse,
    MemoryItem
)
from .llm_model_manager import get_model_manager, LLMModelManager
from .llm_providers import LLMProviderFactory, BaseLLMProvider
from .llm_context_builder import get_context_builder, LLMContextBuilder
from .llm_health_check import get_health_checker


class LLMConversationService:
    """LLM 对话服务"""

    def __init__(
        self,
        model_manager: Optional[LLMModelManager] = None,
        context_builder: Optional[LLMContextBuilder] = None,
        data_dir: Optional[str] = None
    ):
        """
        初始化对话服务

        Args:
            model_manager: 模型管理器
            context_builder: 上下文构建器
            data_dir: 数据目录
        """
        self.model_manager = model_manager or get_model_manager()
        self.context_builder = context_builder or get_context_builder()
        self.data_dir = data_dir or os.path.join(os.getcwd(), "data", "conversations")

        # 确保数据目录存在
        Path(self.data_dir).mkdir(parents=True, exist_ok=True)

        # 缓存
        self.conversation_cache: Dict[str, ConversationHistory] = {}
        self.provider_cache: Dict[str, BaseLLMProvider] = {}

    async def chat(self, request: LLMRequest) -> LLMResponse:
        """
        处理对话请求

        Args:
            request: LLM 请求

        Returns:
            LLM 响应
        """
        # 1. 获取或创建对话历史
        conversation = await self._get_or_create_conversation(
            request.pet_id,
            request.conversation_id
        )

        # 2. 获取宠物档案（这里需要从存储中获取，暂时使用模拟数据）
        pet_profile = await self._get_pet_profile(request.pet_id)

        # 3. 获取记忆和事件
        memory_items = await self._get_memory_items(request.pet_id)
        recent_events = await self._get_recent_events(request.pet_id)

        # 4. 构建对话上下文
        context = self.context_builder.build_conversation_context(
            pet_profile=pet_profile,
            memory_items=memory_items,
            recent_events=recent_events,
            conversation_history=conversation.messages,
            user_preferences=request.metadata.get("user_preferences")
        )

        # 5. 构建 LLM 消息列表
        messages = self.context_builder.build_messages_for_llm(
            context=context,
            user_message=request.user_message,
            conversation_history=conversation.messages
        )

        # 6. 选择模型
        routing_decision = self.model_manager.select_model(
            model_id=request.model_id,
            provider_id=request.provider_id
        )

        # 7. 获取模型配置
        model = self.model_manager.get_model(routing_decision.selected_model_id)
        if not model:
            raise ValueError(f"Model {routing_decision.selected_model_id} not found")

        # 8. 获取提供商实例
        provider = await self._get_provider(routing_decision.selected_provider_id)

        # 9. 调用 LLM
        response = await provider.generate(
            messages=messages,
            model=model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            pet_id=request.pet_id,
            conversation_id=conversation.conversation_id
        )

        # 10. 更新对话历史
        await self._update_conversation(
            conversation,
            request.user_message,
            response.response_text
        )

        # 11. 分析响应（提取情绪、动作等）
        emotion, actions = self._analyze_response(response.response_text)
        response.emotion = emotion
        response.actions = actions

        return response

    async def _get_or_create_conversation(
        self,
        pet_id: str,
        conversation_id: Optional[str] = None
    ) -> ConversationHistory:
        """获取或创建对话历史"""
        if conversation_id:
            # 尝试从缓存获取
            if conversation_id in self.conversation_cache:
                return self.conversation_cache[conversation_id]

            # 从文件加载
            conversation = await self._load_conversation(conversation_id)
            if conversation:
                self.conversation_cache[conversation_id] = conversation
                return conversation

        # 创建新对话
        new_conversation_id = str(uuid.uuid4())
        conversation = ConversationHistory(
            conversation_id=new_conversation_id,
            pet_id=pet_id,
            messages=[],
            created_at=datetime.now().isoformat()
        )

        self.conversation_cache[new_conversation_id] = conversation
        return conversation

    async def _load_conversation(self, conversation_id: str) -> Optional[ConversationHistory]:
        """从文件加载对话历史"""
        file_path = os.path.join(self.data_dir, f"{conversation_id}.json")
        if not os.path.exists(file_path):
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return ConversationHistory(**data)

    async def _save_conversation(self, conversation: ConversationHistory):
        """保存对话历史到文件"""
        file_path = os.path.join(self.data_dir, f"{conversation.conversation_id}.json")
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(conversation.dict(), f, indent=2, ensure_ascii=False)

    async def _update_conversation(
        self,
        conversation: ConversationHistory,
        user_message: str,
        assistant_message: str
    ):
        """更新对话历史"""
        # 添加用户消息
        conversation.messages.append(ConversationMessage(
            role="user",
            content=user_message,
            timestamp=datetime.now().isoformat()
        ))

        # 添加助手消息
        conversation.messages.append(ConversationMessage(
            role="assistant",
            content=assistant_message,
            timestamp=datetime.now().isoformat()
        ))

        # 更新时间戳
        conversation.updated_at = datetime.now().isoformat()

        # 保存
        await self._save_conversation(conversation)

    async def _get_provider(self, provider_id: str) -> BaseLLMProvider:
        """获取提供商实例"""
        if provider_id in self.provider_cache:
            return self.provider_cache[provider_id]

        provider = await LLMProviderFactory.create_provider(
            provider_id,
            self.model_manager
        )
        self.provider_cache[provider_id] = provider
        return provider

    async def _get_pet_profile(self, pet_id: str) -> PetProfileResponse:
        """获取宠物档案（模拟数据）"""
        # TODO: 从实际存储中获取
        return PetProfileResponse(
            pet_id=pet_id,
            name="诺诺",
            species_id="cat-default",
            theme_id="cat-gold-day",
            growth_stage="child",
            level=5,
            exp=50,
            mood="happy",
            energy=80,
            hunger=30,
            affection=70
        )

    async def _get_memory_items(self, pet_id: str) -> List[MemoryItem]:
        """获取记忆项（模拟数据）"""
        # TODO: 从实际存储中获取
        return [
            MemoryItem(
                kind="preference",
                text="喜欢吃小鱼干",
                tags=["food", "favorite"],
                created_at=datetime.now().isoformat()
            ),
            MemoryItem(
                kind="event",
                text="今天和主人玩了很久",
                tags=["play", "happy"],
                created_at=datetime.now().isoformat()
            )
        ]

    async def _get_recent_events(self, pet_id: str) -> List[Dict[str, Any]]:
        """获取最近事件（模拟数据）"""
        # TODO: 从实际存储中获取
        return [
            {
                "kind": "feed",
                "text": "主人喂了小鱼干",
                "created_at": datetime.now().isoformat()
            },
            {
                "kind": "play",
                "text": "和主人玩耍",
                "created_at": datetime.now().isoformat()
            }
        ]

    def _analyze_response(self, response_text: str) -> Tuple[str, List[str]]:
        """
        分析响应，提取情绪和动作

        Args:
            response_text: 响应文本

        Returns:
            (情绪, 动作列表)
        """
        # 简单的关键词匹配
        emotion = "neutral"
        actions = []

        text_lower = response_text.lower()

        # 情绪检测
        if any(word in text_lower for word in ["开心", "高兴", "快乐", "happy", "joy"]):
            emotion = "happy"
        elif any(word in text_lower for word in ["难过", "伤心", "sad", "upset"]):
            emotion = "sad"
        elif any(word in text_lower for word in ["饿", "hungry", "食物"]):
            emotion = "hungry"
        elif any(word in text_lower for word in ["累", "疲惫", "tired"]):
            emotion = "tired"
        elif any(word in text_lower for word in ["生气", "angry"]):
            emotion = "angry"

        # 动作检测
        if "摇尾巴" in response_text or "wag" in text_lower:
            actions.append("wag_tail")
        if "蹭" in response_text or "rub" in text_lower:
            actions.append("rub")
        if "叫" in response_text or "meow" in text_lower or "bark" in text_lower:
            actions.append("vocalize")
        if "跳" in response_text or "jump" in text_lower:
            actions.append("jump")
        if "睡" in response_text or "sleep" in text_lower:
            actions.append("sleep")

        return emotion, actions

    async def get_conversation_history(
        self,
        conversation_id: str
    ) -> Optional[ConversationHistory]:
        """获取对话历史"""
        return await self._load_conversation(conversation_id)

    async def list_conversations(
        self,
        pet_id: str,
        limit: int = 10
    ) -> List[ConversationSummary]:
        """列出宠物的所有对话"""
        # TODO: 实现从文件系统扫描和加载
        summaries = []

        # 扫描数据目录
        for filename in os.listdir(self.data_dir):
            if not filename.endswith('.json'):
                continue

            file_path = os.path.join(self.data_dir, filename)
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("pet_id") == pet_id:
                    conversation = ConversationHistory(**data)
                    summary = ConversationSummary(
                        conversation_id=conversation.conversation_id,
                        pet_id=conversation.pet_id,
                        message_count=len(conversation.messages),
                        total_tokens=conversation.total_tokens,
                        first_message_at=conversation.created_at,
                        last_message_at=conversation.updated_at
                    )
                    if conversation.messages:
                        # 获取最后一条用户和助手消息
                        for msg in reversed(conversation.messages):
                            if msg.role == "assistant" and not summary.last_assistant_message:
                                summary.last_assistant_message = msg.content
                            elif msg.role == "user" and not summary.last_user_message:
                                summary.last_user_message = msg.content

                    summaries.append(summary)

        # 按时间排序
        summaries.sort(key=lambda x: x.last_message_at or "", reverse=True)

        return summaries[:limit]

    async def delete_conversation(self, conversation_id: str) -> bool:
        """删除对话"""
        file_path = os.path.join(self.data_dir, f"{conversation_id}.json")
        if os.path.exists(file_path):
            os.remove(file_path)
            if conversation_id in self.conversation_cache:
                del self.conversation_cache[conversation_id]
            return True
        return False


# 全局对话服务实例
_conversation_service: Optional[LLMConversationService] = None


def get_conversation_service() -> LLMConversationService:
    """获取对话服务实例"""
    global _conversation_service
    if _conversation_service is None:
        _conversation_service = LLMConversationService()
    return _conversation_service
