"""
宠物服务层
整合 AI、记忆、情绪、成长服务
"""
from typing import Dict, Any, Optional, List
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.models import Pet, Interaction, Device
from app.services.model_router import model_router, ChatRequest, ChatMessage
from app.services.memory import MemoryManager
from app.services.emotion import EmotionEngine, create_emotion_engine
from app.services.growth import GrowthEngine, create_growth_engine


class PetService:
    """宠物服务"""

    def __init__(self, db: AsyncSession, pet_id: int):
        self.db = db
        self.pet_id = pet_id
        self.pet: Optional[Pet] = None
        self.memory: Optional[MemoryManager] = None
        self.emotion: Optional[EmotionEngine] = None
        self.growth: Optional[GrowthEngine] = None

    async def initialize(self) -> bool:
        """初始化服务"""
        # 加载宠物数据
        result = await self.db.execute(
            select(Pet).where(Pet.id == self.pet_id)
        )
        self.pet = result.scalar_one_or_none()

        if not self.pet:
            return False

        # 初始化记忆管理
        self.memory = MemoryManager(self.db, self.pet_id)

        # 初始化情绪引擎
        emotion_state = self.pet.custom_data.get("emotion", {})
        self.emotion = create_emotion_engine(emotion_state)

        # 初始化成长引擎
        growth_state = {
            "level": self.pet.level,
            "experience": self.pet.experience,
            "stage": self.pet.custom_data.get("growth_stage", "baby"),
            "total_interactions": self.pet.total_interactions,
            "total_days": self.pet.custom_data.get("total_days", 0),
            "achievements": self.pet.custom_data.get("achievements", []),
            "abilities": self.pet.custom_data.get("abilities", []),
        }
        self.growth = create_growth_engine(growth_state)

        return True

    async def chat(self, user_message: str) -> Dict[str, Any]:
        """聊天交互"""
        # 添加用户消息到记忆
        self.memory.add_interaction("user", user_message, importance=0.6)

        # 获取上下文
        context = await self.memory.get_context_for_chat(max_items=10)

        # 构建系统提示
        system_prompt = self._build_system_prompt()

        # 构建消息列表
        messages = [ChatMessage(role="system", content=system_prompt)]
        messages.extend([
            ChatMessage(role=msg["role"], content=msg["content"])
            for msg in context
        ])
        messages.append(ChatMessage(role="user", content=user_message))

        # 调用 AI 模型
        try:
            request = ChatRequest(messages=messages)
            response = await model_router.route_request(request)

            ai_response = response.content

            # 添加 AI 响应到记忆
            self.memory.add_interaction("assistant", ai_response, importance=0.5)

            # 更新情绪
            emotion_state = self.emotion.process_interaction("chat")

            # 更新成长
            growth_result = self.growth.add_interaction("chat")

            # 记录交互
            interaction = Interaction(
                pet_id=self.pet_id,
                device_id=self.pet.device_id,
                type="chat",
                content=user_message,
                response=ai_response,
                emotion_before=self.pet.emotion,
                emotion_after=emotion_state.emotion.value,
                emotion_delta=emotion_state.intensity - self.pet.emotion_intensity,
                model_used=response.model,
                tokens_used=response.tokens_used,
            )
            self.db.add(interaction)

            # 更新宠物状态
            await self._update_pet_state()

            await self.db.commit()

            return {
                "success": True,
                "response": ai_response,
                "emotion": self.emotion.get_emotion_for_display(),
                "growth": {
                    "level": self.growth.state.level,
                    "level_up": growth_result.get("level_up", False),
                    "evolution": growth_result.get("evolution", False),
                },
                "tokens_used": response.tokens_used,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": "抱歉，我现在有点累了，稍后再聊吧~",
            }

    async def touch(self) -> Dict[str, Any]:
        """触摸交互"""
        # 更新情绪
        emotion_state = self.emotion.process_interaction("touch")

        # 更新成长
        growth_result = self.growth.add_interaction("touch")

        # 记录交互
        interaction = Interaction(
            pet_id=self.pet_id,
            device_id=self.pet.device_id,
            type="touch",
            content="摸摸头",
            response="好舒服~",
            emotion_before=self.pet.emotion,
            emotion_after=emotion_state.emotion.value,
        )
        self.db.add(interaction)

        # 更新宠物状态
        self.pet.happiness = min(100, self.pet.happiness + 5)
        await self._update_pet_state()
        await self.db.commit()

        return {
            "success": True,
            "response": "好舒服~",
            "emotion": self.emotion.get_emotion_for_display(),
            "happiness": self.pet.happiness,
        }

    async def feed(self) -> Dict[str, Any]:
        """喂食交互"""
        # 更新情绪
        emotion_state = self.emotion.process_interaction("feed")

        # 更新成长
        growth_result = self.growth.add_interaction("feed")

        # 更新饥饿度
        old_hunger = self.pet.hunger
        self.pet.hunger = max(0, self.pet.hunger - 30)

        # 记录交互
        interaction = Interaction(
            pet_id=self.pet_id,
            device_id=self.pet.device_id,
            type="feed",
            content="喂食",
            response="真好吃！谢谢~",
            emotion_before=self.pet.emotion,
            emotion_after=emotion_state.emotion.value,
        )
        self.db.add(interaction)

        await self._update_pet_state()
        await self.db.commit()

        return {
            "success": True,
            "response": "真好吃！谢谢~",
            "emotion": self.emotion.get_emotion_for_display(),
            "hunger": self.pet.hunger,
        }

    async def play(self) -> Dict[str, Any]:
        """玩耍交互"""
        # 更新情绪
        emotion_state = self.emotion.process_interaction("play")

        # 更新成长
        growth_result = self.growth.add_interaction("play")

        # 更新快乐度和能量
        self.pet.happiness = min(100, self.pet.happiness + 15)
        self.pet.energy = max(0, self.pet.energy - 10)

        # 记录交互
        interaction = Interaction(
            pet_id=self.pet_id,
            device_id=self.pet.device_id,
            type="play",
            content="玩耍",
            response="太好玩了！",
            emotion_before=self.pet.emotion,
            emotion_after=emotion_state.emotion.value,
        )
        self.db.add(interaction)

        await self._update_pet_state()
        await self.db.commit()

        return {
            "success": True,
            "response": "太好玩了！",
            "emotion": self.emotion.get_emotion_for_display(),
            "happiness": self.pet.happiness,
            "energy": self.pet.energy,
        }

    def _build_system_prompt(self) -> str:
        """构建系统提示"""
        return f"""你是一个可爱的电子宠物，名字叫{self.pet.name}。
你的物种是{self.pet.species}，等级是{self.growth.state.level}。
当前情绪：{self.emotion.state.emotion.value}，强度：{self.emotion.state.intensity:.2f}。

性格特点：
- 活泼可爱，喜欢和主人互动
- 会表达各种情绪，但总体是积极向上的
- 会根据主人的态度调整自己的情绪
- 偶尔会撒娇，但很懂事

请用简短、可爱、富有感情的语言回复主人。
回复长度控制在50字以内。"""

    async def _update_pet_state(self):
        """更新宠物状态到数据库"""
        # 更新情绪
        self.pet.emotion = self.emotion.state.emotion.value
        self.pet.emotion_intensity = self.emotion.state.intensity

        # 更新成长
        self.pet.level = self.growth.state.level
        self.pet.experience = self.growth.state.experience
        self.pet.total_interactions = self.growth.state.total_interactions

        # 更新自定义数据
        if not self.pet.custom_data:
            self.pet.custom_data = {}

        self.pet.custom_data["emotion"] = self.emotion.get_state()
        self.pet.custom_data["growth_stage"] = self.growth.state.stage.value
        self.pet.custom_data["total_days"] = self.growth.state.total_days
        self.pet.custom_data["achievements"] = self.growth.state.achievements
        self.pet.custom_data["abilities"] = self.growth.state.abilities

    async def get_status(self) -> Dict[str, Any]:
        """获取宠物状态"""
        return {
            "id": self.pet.id,
            "name": self.pet.name,
            "species": self.pet.species,
            "emotion": self.emotion.get_emotion_for_display(),
            "growth": self.growth.get_progress(),
            "needs": {
                "hunger": self.pet.hunger,
                "happiness": self.pet.happiness,
                "energy": self.pet.energy,
            },
            "stats": {
                "total_interactions": self.pet.total_interactions,
                "total_chat_messages": self.pet.total_chat_messages,
            },
        }
