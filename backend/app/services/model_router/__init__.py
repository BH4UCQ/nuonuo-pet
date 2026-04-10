"""
AI 模型路由服务
支持多模型配置、优先级路由、自动回退
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import asyncio
import time
from datetime import datetime

import httpx
from openai import AsyncOpenAI
from anthropic import AsyncAnthropic

from app.core.config import settings
from app.core.exceptions import AllModelsUnavailableError


class ModelProvider(Enum):
    """模型提供方"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


@dataclass
class ModelConfig:
    """模型配置"""
    name: str
    provider: ModelProvider
    model_id: str
    priority: int = 1
    api_key: str = ""
    api_base: str = ""
    max_tokens: int = 2000
    temperature: float = 0.7
    timeout: int = 30
    enabled: bool = True

    # 统计信息
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    total_latency: float = 0.0
    last_error: Optional[str] = None
    last_success_time: Optional[datetime] = None


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str


@dataclass
class ChatRequest:
    """聊天请求"""
    messages: List[ChatMessage]
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    context: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ChatResponse:
    """聊天响应"""
    content: str
    model: str
    provider: str
    tokens_used: int
    latency: float
    success: bool = True
    error: Optional[str] = None


class ModelRouter:
    """模型路由器"""

    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self._init_default_models()
        self._clients: Dict[str, Any] = {}

    def _init_default_models(self):
        """初始化默认模型配置"""
        # OpenAI 主模型
        if settings.OPENAI_API_KEY:
            self.models["openai_primary"] = ModelConfig(
                name="openai_primary",
                provider=ModelProvider.OPENAI,
                model_id=settings.OPENAI_MODEL,
                priority=1,
                api_key=settings.OPENAI_API_KEY,
                api_base=settings.OPENAI_API_BASE,
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=settings.AI_TEMPERATURE,
                timeout=settings.AI_TIMEOUT,
            )

        # Anthropic 备用模型
        if settings.ANTHROPIC_API_KEY:
            self.models["anthropic_fallback"] = ModelConfig(
                name="anthropic_fallback",
                provider=ModelProvider.ANTHROPIC,
                model_id=settings.ANTHROPIC_MODEL,
                priority=2,
                api_key=settings.ANTHROPIC_API_KEY,
                max_tokens=settings.AI_MAX_TOKENS,
                temperature=settings.AI_TEMPERATURE,
                timeout=settings.AI_TIMEOUT,
            )

    def _get_client(self, model: ModelConfig) -> Any:
        """获取模型客户端"""
        if model.name in self._clients:
            return self._clients[model.name]

        if model.provider == ModelProvider.OPENAI:
            client = AsyncOpenAI(
                api_key=model.api_key,
                base_url=model.api_base,
                timeout=model.timeout,
            )
        elif model.provider == ModelProvider.ANTHROPIC:
            client = AsyncAnthropic(
                api_key=model.api_key,
                timeout=model.timeout,
            )
        else:
            client = httpx.AsyncClient(timeout=model.timeout)

        self._clients[model.name] = client
        return client

    def _is_healthy(self, model: ModelConfig) -> bool:
        """检查模型健康状态"""
        if not model.enabled:
            return False

        # 如果最近有错误且失败率过高，认为不健康
        if model.total_requests > 0:
            failure_rate = model.failed_requests / model.total_requests
            if failure_rate > 0.5 and model.last_error:
                return False

        return True

    async def _call_openai(
        self, model: ModelConfig, request: ChatRequest
    ) -> ChatResponse:
        """调用 OpenAI 模型"""
        client = self._get_client(model)

        messages = [{"role": m.role, "content": m.content} for m in request.messages]

        response = await client.chat.completions.create(
            model=model.model_id,
            messages=messages,
            max_tokens=request.max_tokens or model.max_tokens,
            temperature=request.temperature or model.temperature,
        )

        return ChatResponse(
            content=response.choices[0].message.content,
            model=model.model_id,
            provider="openai",
            tokens_used=response.usage.total_tokens,
            latency=0,  # 由调用者计算
        )

    async def _call_anthropic(
        self, model: ModelConfig, request: ChatRequest
    ) -> ChatResponse:
        """调用 Anthropic 模型"""
        client = self._get_client(model)

        # 分离 system 消息
        system_message = ""
        messages = []
        for m in request.messages:
            if m.role == "system":
                system_message = m.content
            else:
                messages.append({"role": m.role, "content": m.content})

        response = await client.messages.create(
            model=model.model_id,
            max_tokens=request.max_tokens or model.max_tokens,
            temperature=request.temperature or model.temperature,
            system=system_message if system_message else None,
            messages=messages,
        )

        return ChatResponse(
            content=response.content[0].text,
            model=model.model_id,
            provider="anthropic",
            tokens_used=response.usage.input_tokens + response.usage.output_tokens,
            latency=0,
        )

    async def route_request(self, request: ChatRequest) -> ChatResponse:
        """路由请求到最佳可用模型"""
        # 按优先级排序
        sorted_models = sorted(
            self.models.values(),
            key=lambda m: m.priority
        )

        errors = []
        for model in sorted_models:
            if not self._is_healthy(model):
                continue

            start_time = time.time()
            model.total_requests += 1

            try:
                if model.provider == ModelProvider.OPENAI:
                    response = await self._call_openai(model, request)
                elif model.provider == ModelProvider.ANTHROPIC:
                    response = await self._call_anthropic(model, request)
                else:
                    continue

                latency = time.time() - start_time
                response.latency = latency

                # 更新统计
                model.successful_requests += 1
                model.total_latency += latency
                model.last_success_time = datetime.utcnow()
                model.last_error = None

                return response

            except Exception as e:
                model.failed_requests += 1
                model.last_error = str(e)
                errors.append(f"{model.name}: {str(e)}")
                continue

        # 所有模型都失败
        raise AllModelsUnavailableError(
            f"All models unavailable. Errors: {'; '.join(errors)}"
        )

    def add_model(self, config: ModelConfig):
        """添加模型配置"""
        self.models[config.name] = config

    def remove_model(self, name: str):
        """移除模型配置"""
        self.models.pop(name, None)
        self._clients.pop(name, None)

    def update_model(self, name: str, **kwargs):
        """更新模型配置"""
        if name in self.models:
            model = self.models[name]
            for key, value in kwargs.items():
                if hasattr(model, key):
                    setattr(model, key, value)
            # 清除客户端缓存以使用新配置
            self._clients.pop(name, None)

    def get_model_stats(self) -> List[Dict[str, Any]]:
        """获取所有模型统计信息"""
        return [
            {
                "name": m.name,
                "provider": m.provider.value,
                "model_id": m.model_id,
                "priority": m.priority,
                "enabled": m.enabled,
                "total_requests": m.total_requests,
                "successful_requests": m.successful_requests,
                "failed_requests": m.failed_requests,
                "success_rate": (
                    m.successful_requests / m.total_requests
                    if m.total_requests > 0 else 0
                ),
                "avg_latency": (
                    m.total_latency / m.successful_requests
                    if m.successful_requests > 0 else 0
                ),
                "last_error": m.last_error,
                "last_success_time": (
                    m.last_success_time.isoformat()
                    if m.last_success_time else None
                ),
            }
            for m in self.models.values()
        ]


# 全局模型路由器实例
model_router = ModelRouter()
