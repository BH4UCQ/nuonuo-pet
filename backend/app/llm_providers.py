"""
LLM 模型提供商适配器
支持 OpenAI、Anthropic Claude、本地模型等
"""
import asyncio
import time
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, AsyncIterator
import httpx
import json

from .models import (
    LLMProviderConfig,
    LLMModelConfig,
    ConversationMessage,
    LLMResponse
)
from .llm_model_manager import get_model_manager


class BaseLLMProvider(ABC):
    """LLM 提供商基类"""

    def __init__(self, config: LLMProviderConfig):
        self.config = config

    @abstractmethod
    async def generate(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """生成响应"""
        pass

    @abstractmethod
    async def generate_stream(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成响应"""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI 提供商"""

    def __init__(self, config: LLMProviderConfig, api_key: str):
        super().__init__(config)
        self.api_key = api_key

    async def generate(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """生成响应"""
        start_time = time.time()

        # 转换消息格式
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # 构建请求
        request_data = {
            "model": model.model_name,
            "messages": formatted_messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
        }

        # 添加额外参数
        if kwargs.get("functions"):
            request_data["functions"] = kwargs["functions"]
        if kwargs.get("function_call"):
            request_data["function_call"] = kwargs["function_call"]

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    f"{self.config.api_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                response.raise_for_status()
                data = response.json()

                # 解析响应
                choice = data["choices"][0]
                content = choice["message"]["content"]
                finish_reason = choice.get("finish_reason", "stop")

                # 计算延迟
                latency_ms = int((time.time() - start_time) * 1000)

                # 估算 token 使用量
                tokens_used = data.get("usage", {}).get("total_tokens", 0)

                return LLMResponse(
                    pet_id=kwargs.get("pet_id", ""),
                    conversation_id=kwargs.get("conversation_id", ""),
                    response_text=content,
                    model_id=model.model_id,
                    provider_id=self.config.provider_id,
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    finish_reason=finish_reason,
                    metadata={"raw_response": data}
                )

        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {e}")

    async def generate_stream(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成响应"""
        # 转换消息格式
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # 构建请求
        request_data = {
            "model": model.model_name,
            "messages": formatted_messages,
            "temperature": temperature or self.config.temperature,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": True
        }

        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            async with client.stream(
                "POST",
                f"{self.config.api_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=request_data
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except json.JSONDecodeError:
                            continue


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude 提供商"""

    def __init__(self, config: LLMProviderConfig, api_key: str):
        super().__init__(config)
        self.api_key = api_key

    async def generate(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """生成响应"""
        start_time = time.time()

        # 转换消息格式（Anthropic 格式不同）
        system_message = None
        formatted_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # 构建请求
        request_data = {
            "model": model.model_name,
            "messages": formatted_messages,
            "max_tokens": max_tokens or self.config.max_tokens,
        }

        if system_message:
            request_data["system"] = system_message

        if temperature is not None:
            request_data["temperature"] = temperature

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    f"{self.config.api_base_url}/v1/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json=request_data
                )
                response.raise_for_status()
                data = response.json()

                # 解析响应
                content = data["content"][0]["text"]
                stop_reason = data.get("stop_reason", "end_turn")

                # 计算延迟
                latency_ms = int((time.time() - start_time) * 1000)

                # 获取 token 使用量
                tokens_used = data.get("usage", {}).get("total_tokens", 0)

                return LLMResponse(
                    pet_id=kwargs.get("pet_id", ""),
                    conversation_id=kwargs.get("conversation_id", ""),
                    response_text=content,
                    model_id=model.model_id,
                    provider_id=self.config.provider_id,
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    finish_reason=stop_reason,
                    metadata={"raw_response": data}
                )

        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {e}")

    async def generate_stream(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成响应"""
        # 转换消息格式
        system_message = None
        formatted_messages = []

        for msg in messages:
            if msg.role == "system":
                system_message = msg.content
            else:
                formatted_messages.append({
                    "role": msg.role,
                    "content": msg.content
                })

        # 构建请求
        request_data = {
            "model": model.model_name,
            "messages": formatted_messages,
            "max_tokens": max_tokens or self.config.max_tokens,
            "stream": True
        }

        if system_message:
            request_data["system"] = system_message

        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            async with client.stream(
                "POST",
                f"{self.config.api_base_url}/v1/messages",
                headers={
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                    "Content-Type": "application/json"
                },
                json=request_data
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        try:
                            data = json.loads(data_str)
                            if data.get("type") == "content_block_delta":
                                delta = data.get("delta", {})
                                if "text" in delta:
                                    yield delta["text"]
                        except json.JSONDecodeError:
                            continue


class LocalModelProvider(BaseLLMProvider):
    """本地模型提供商（如 Ollama）"""

    def __init__(self, config: LLMProviderConfig):
        super().__init__(config)

    async def generate(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> LLMResponse:
        """生成响应"""
        start_time = time.time()

        # 转换消息格式
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # 构建请求（Ollama 格式）
        request_data = {
            "model": model.model_name,
            "messages": formatted_messages,
            "stream": False,
            "options": {
                "temperature": temperature or self.config.temperature,
                "num_predict": max_tokens or self.config.max_tokens,
            }
        }

        try:
            async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
                response = await client.post(
                    f"{self.config.api_base_url}/api/chat",
                    json=request_data
                )
                response.raise_for_status()
                data = response.json()

                # 解析响应
                content = data["message"]["content"]

                # 计算延迟
                latency_ms = int((time.time() - start_time) * 1000)

                # 估算 token 使用量
                tokens_used = data.get("eval_count", 0) + data.get("prompt_eval_count", 0)

                return LLMResponse(
                    pet_id=kwargs.get("pet_id", ""),
                    conversation_id=kwargs.get("conversation_id", ""),
                    response_text=content,
                    model_id=model.model_id,
                    provider_id=self.config.provider_id,
                    tokens_used=tokens_used,
                    latency_ms=latency_ms,
                    metadata={"raw_response": data}
                )

        except Exception as e:
            raise RuntimeError(f"Local model API call failed: {e}")

    async def generate_stream(
        self,
        messages: List[ConversationMessage],
        model: LLMModelConfig,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """流式生成响应"""
        # 转换消息格式
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        # 构建请求
        request_data = {
            "model": model.model_name,
            "messages": formatted_messages,
            "stream": True,
            "options": {
                "temperature": temperature or self.config.temperature,
                "num_predict": max_tokens or self.config.max_tokens,
            }
        }

        async with httpx.AsyncClient(timeout=self.config.timeout_seconds) as client:
            async with client.stream(
                "POST",
                f"{self.config.api_base_url}/api/chat",
                json=request_data
            ) as response:
                response.raise_for_status()

                async for line in response.aiter_lines():
                    try:
                        data = json.loads(line)
                        if "message" in data and "content" in data["message"]:
                            yield data["message"]["content"]
                    except json.JSONDecodeError:
                        continue


class LLMProviderFactory:
    """LLM 提供商工厂"""

    @staticmethod
    async def create_provider(
        provider_id: str,
        model_manager=None
    ) -> BaseLLMProvider:
        """
        创建提供商实例

        Args:
            provider_id: 提供商 ID
            model_manager: 模型管理器实例

        Returns:
            提供商实例
        """
        if model_manager is None:
            model_manager = get_model_manager()

        provider = model_manager.get_provider(provider_id)
        if not provider:
            raise ValueError(f"Provider {provider_id} not found")

        # 根据提供商类型创建实例
        if provider_id == "openai":
            api_key = model_manager.get_decrypted_api_key(provider_id)
            if not api_key:
                raise ValueError(f"API key not found for provider {provider_id}")
            return OpenAIProvider(provider, api_key)

        elif provider_id == "anthropic":
            api_key = model_manager.get_decrypted_api_key(provider_id)
            if not api_key:
                raise ValueError(f"API key not found for provider {provider_id}")
            return AnthropicProvider(provider, api_key)

        elif provider_id == "local":
            return LocalModelProvider(provider)

        else:
            # 默认使用 OpenAI 兼容接口
            api_key = model_manager.get_decrypted_api_key(provider_id)
            if api_key:
                return OpenAIProvider(provider, api_key)
            else:
                return LocalModelProvider(provider)
