"""
LLM 模型管理模块
负责模型路由配置、模型选择、降级策略等
"""
import json
import os
from typing import Dict, List, Optional, Any
from datetime import datetime
from pathlib import Path

from .models import (
    LLMProviderConfig,
    LLMModelConfig,
    ModelRoutingDecision,
    LLMHealthStatus
)
try:
    from .security import decrypt_api_key, encrypt_api_key
except ImportError:
    from .security_simple import decrypt_api_key, encrypt_api_key


class LLMModelManager:
    """LLM 模型管理器"""

    def __init__(self, config_dir: Optional[str] = None):
        """
        初始化模型管理器

        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir or os.path.join(os.getcwd(), "data", "llm_config")
        self.providers: Dict[str, LLMProviderConfig] = {}
        self.models: Dict[str, LLMModelConfig] = {}
        self.default_provider_id: Optional[str] = None
        self.default_model_id: Optional[str] = None
        self.fallback_chain: List[str] = []

        # 确保配置目录存在
        Path(self.config_dir).mkdir(parents=True, exist_ok=True)

        # 加载配置
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        providers_file = os.path.join(self.config_dir, "providers.json")
        models_file = os.path.join(self.config_dir, "models.json")
        config_file = os.path.join(self.config_dir, "config.json")

        # 加载提供商配置
        if os.path.exists(providers_file):
            with open(providers_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("providers", []):
                    provider = LLMProviderConfig(**item)
                    self.providers[provider.provider_id] = provider

        # 加载模型配置
        if os.path.exists(models_file):
            with open(models_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for item in data.get("models", []):
                    model = LLMModelConfig(**item)
                    self.models[model.model_id] = model

        # 加载全局配置
        if os.path.exists(config_file):
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.default_provider_id = data.get("default_provider_id")
                self.default_model_id = data.get("default_model_id")
                self.fallback_chain = data.get("fallback_chain", [])

        # 如果没有配置，初始化默认配置
        if not self.providers:
            self._init_default_config()

    def _init_default_config(self):
        """初始化默认配置"""
        # 默认 OpenAI 提供商
        openai_provider = LLMProviderConfig(
            provider_id="openai",
            provider_name="OpenAI",
            api_base_url="https://api.openai.com/v1",
            default_model="gpt-3.5-turbo",
            max_tokens=2000,
            temperature=0.7,
            enabled=True,
            created_at=datetime.now().isoformat()
        )
        self.providers["openai"] = openai_provider

        # 默认模型配置
        gpt35_model = LLMModelConfig(
            model_id="gpt-3.5-turbo",
            model_name="GPT-3.5 Turbo",
            provider_id="openai",
            context_window=4096,
            max_output_tokens=2000,
            supports_streaming=True,
            supports_functions=True,
            cost_per_1k_tokens=0.002,
            latency_tier="fast",
            quality_tier="balanced",
            enabled=True
        )
        self.models["gpt-3.5-turbo"] = gpt35_model

        gpt4_model = LLMModelConfig(
            model_id="gpt-4",
            model_name="GPT-4",
            provider_id="openai",
            context_window=8192,
            max_output_tokens=2000,
            supports_streaming=True,
            supports_functions=True,
            cost_per_1k_tokens=0.03,
            latency_tier="balanced",
            quality_tier="premium",
            enabled=True
        )
        self.models["gpt-4"] = gpt4_model

        # 设置默认值
        self.default_provider_id = "openai"
        self.default_model_id = "gpt-3.5-turbo"
        self.fallback_chain = ["gpt-3.5-turbo"]

        # 保存配置
        self._save_config()

    def _save_config(self):
        """保存配置文件"""
        providers_file = os.path.join(self.config_dir, "providers.json")
        models_file = os.path.join(self.config_dir, "models.json")
        config_file = os.path.join(self.config_dir, "config.json")

        # 保存提供商配置
        providers_data = {
            "providers": [p.dict() for p in self.providers.values()]
        }
        with open(providers_file, 'w', encoding='utf-8') as f:
            json.dump(providers_data, f, indent=2, ensure_ascii=False)

        # 保存模型配置
        models_data = {
            "models": [m.dict() for m in self.models.values()]
        }
        with open(models_file, 'w', encoding='utf-8') as f:
            json.dump(models_data, f, indent=2, ensure_ascii=False)

        # 保存全局配置
        config_data = {
            "default_provider_id": self.default_provider_id,
            "default_model_id": self.default_model_id,
            "fallback_chain": self.fallback_chain
        }
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=2, ensure_ascii=False)

    def get_provider(self, provider_id: str) -> Optional[LLMProviderConfig]:
        """获取提供商配置"""
        return self.providers.get(provider_id)

    def get_model(self, model_id: str) -> Optional[LLMModelConfig]:
        """获取模型配置"""
        return self.models.get(model_id)

    def get_all_providers(self) -> List[LLMProviderConfig]:
        """获取所有提供商"""
        return list(self.providers.values())

    def get_all_models(self) -> List[LLMModelConfig]:
        """获取所有模型"""
        return list(self.models.values())

    def get_enabled_providers(self) -> List[LLMProviderConfig]:
        """获取所有启用的提供商"""
        return [p for p in self.providers.values() if p.enabled]

    def get_enabled_models(self) -> List[LLMModelConfig]:
        """获取所有启用的模型"""
        return [m for m in self.models.values() if m.enabled]

    def select_model(
        self,
        model_id: Optional[str] = None,
        provider_id: Optional[str] = None,
        prefer_fast: bool = False,
        prefer_quality: bool = False,
        health_status: Optional[Dict[str, LLMHealthStatus]] = None
    ) -> ModelRoutingDecision:
        """
        选择模型

        Args:
            model_id: 指定的模型 ID
            provider_id: 指定的提供商 ID
            prefer_fast: 是否优先选择快速模型
            prefer_quality: 是否优先选择高质量模型
            health_status: 健康状态字典

        Returns:
            模型路由决策
        """
        # 如果指定了模型，直接使用
        if model_id:
            model = self.models.get(model_id)
            if model and model.enabled:
                provider = self.providers.get(model.provider_id)
                if provider and provider.enabled:
                    return ModelRoutingDecision(
                        selected_model_id=model.model_id,
                        selected_provider_id=provider.provider_id,
                        route_id=model_id,
                        fallback_used=False
                    )

        # 如果指定了提供商，从该提供商选择模型
        if provider_id:
            provider = self.providers.get(provider_id)
            if provider and provider.enabled:
                # 选择该提供商的默认模型
                model = self.models.get(provider.default_model)
                if model and model.enabled:
                    return ModelRoutingDecision(
                        selected_model_id=model.model_id,
                        selected_provider_id=provider.provider_id,
                        fallback_used=False
                    )

        # 使用默认模型
        if self.default_model_id:
            model = self.models.get(self.default_model_id)
            if model and model.enabled:
                provider = self.providers.get(model.provider_id)
                if provider and provider.enabled:
                    return ModelRoutingDecision(
                        selected_model_id=model.model_id,
                        selected_provider_id=provider.provider_id,
                        fallback_used=False
                    )

        # 尝试降级链
        for fallback_model_id in self.fallback_chain:
            model = self.models.get(fallback_model_id)
            if model and model.enabled:
                provider = self.providers.get(model.provider_id)
                if provider and provider.enabled:
                    return ModelRoutingDecision(
                        selected_model_id=model.model_id,
                        selected_provider_id=provider.provider_id,
                        fallback_used=True,
                        fallback_reason="Default model unavailable"
                    )

        # 如果所有都失败，返回第一个可用的模型
        for model in self.get_enabled_models():
            provider = self.providers.get(model.provider_id)
            if provider and provider.enabled:
                return ModelRoutingDecision(
                    selected_model_id=model.model_id,
                    selected_provider_id=provider.provider_id,
                    fallback_used=True,
                    fallback_reason="No configured models available"
                )

        raise ValueError("No available models found")

    def update_provider(self, provider_id: str, **kwargs) -> LLMProviderConfig:
        """更新提供商配置"""
        provider = self.providers.get(provider_id)
        if not provider:
            raise ValueError(f"Provider {provider_id} not found")

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(provider, key):
                if key == "api_key":
                    # 加密 API key
                    value = encrypt_api_key(value)
                    setattr(provider, "api_key_encrypted", value)
                else:
                    setattr(provider, key, value)

        provider.updated_at = datetime.now().isoformat()
        self._save_config()
        return provider

    def update_model(self, model_id: str, **kwargs) -> LLMModelConfig:
        """更新模型配置"""
        model = self.models.get(model_id)
        if not model:
            raise ValueError(f"Model {model_id} not found")

        # 更新字段
        for key, value in kwargs.items():
            if hasattr(model, key):
                setattr(model, key, value)

        self._save_config()
        return model

    def add_provider(self, provider: LLMProviderConfig) -> LLMProviderConfig:
        """添加提供商"""
        if provider.provider_id in self.providers:
            raise ValueError(f"Provider {provider.provider_id} already exists")

        provider.created_at = datetime.now().isoformat()
        self.providers[provider.provider_id] = provider
        self._save_config()
        return provider

    def add_model(self, model: LLMModelConfig) -> LLMModelConfig:
        """添加模型"""
        if model.model_id in self.models:
            raise ValueError(f"Model {model.model_id} already exists")

        self.models[model.model_id] = model
        self._save_config()
        return model

    def set_default_model(self, model_id: str):
        """设置默认模型"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")

        self.default_model_id = model_id
        model = self.models[model_id]
        self.default_provider_id = model.provider_id
        self._save_config()

    def set_fallback_chain(self, model_ids: List[str]):
        """设置降级链"""
        for model_id in model_ids:
            if model_id not in self.models:
                raise ValueError(f"Model {model_id} not found")

        self.fallback_chain = model_ids
        self._save_config()

    def get_decrypted_api_key(self, provider_id: str) -> Optional[str]:
        """获取解密后的 API key"""
        provider = self.providers.get(provider_id)
        if not provider or not provider.api_key_encrypted:
            return None

        return decrypt_api_key(provider.api_key_encrypted)


# 全局模型管理器实例
_model_manager: Optional[LLMModelManager] = None


def get_model_manager() -> LLMModelManager:
    """获取模型管理器实例"""
    global _model_manager
    if _model_manager is None:
        _model_manager = LLMModelManager()
    return _model_manager
