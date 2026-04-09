"""
LLM 健康检查模块
负责监控模型健康状态、执行健康检查等
"""
import asyncio
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import httpx

from .models import LLMHealthStatus, LLMHealthCheckResponse
from .llm_model_manager import get_model_manager, LLMModelManager


class LLMHealthChecker:
    """LLM 健康检查器"""

    def __init__(self, model_manager: Optional[LLMModelManager] = None):
        """
        初始化健康检查器

        Args:
            model_manager: 模型管理器实例
        """
        self.model_manager = model_manager or get_model_manager()
        self.health_status: Dict[str, LLMHealthStatus] = {}
        self.check_interval_seconds = 300  # 5分钟
        self.timeout_seconds = 10
        self.max_error_count = 3

    async def check_provider_health(
        self,
        provider_id: str,
        model_id: Optional[str] = None
    ) -> LLMHealthStatus:
        """
        检查提供商健康状态

        Args:
            provider_id: 提供商 ID
            model_id: 模型 ID（可选）

        Returns:
            健康状态
        """
        provider = self.model_manager.get_provider(provider_id)
        if not provider:
            return LLMHealthStatus(
                provider_id=provider_id,
                model_id=model_id,
                is_healthy=False,
                last_check_at=datetime.now().isoformat(),
                last_error="Provider not found"
            )

        # 获取之前的健康状态
        status_key = f"{provider_id}:{model_id or 'default'}"
        previous_status = self.health_status.get(status_key)

        # 执行健康检查
        start_time = time.time()
        try:
            is_healthy = await self._perform_health_check(provider, model_id)
            response_time_ms = int((time.time() - start_time) * 1000)

            # 更新健康状态
            status = LLMHealthStatus(
                provider_id=provider_id,
                model_id=model_id,
                is_healthy=is_healthy,
                last_check_at=datetime.now().isoformat(),
                response_time_ms=response_time_ms,
                error_count=0 if is_healthy else (previous_status.error_count + 1 if previous_status else 1),
                last_error=None if is_healthy else "Health check failed"
            )

        except Exception as e:
            response_time_ms = int((time.time() - start_time) * 1000)
            error_count = (previous_status.error_count + 1) if previous_status else 1

            status = LLMHealthStatus(
                provider_id=provider_id,
                model_id=model_id,
                is_healthy=False,
                last_check_at=datetime.now().isoformat(),
                response_time_ms=response_time_ms,
                error_count=error_count,
                last_error=str(e)
            )

        # 保存健康状态
        self.health_status[status_key] = status
        return status

    async def _perform_health_check(
        self,
        provider,
        model_id: Optional[str] = None
    ) -> bool:
        """
        执行实际的健康检查

        Args:
            provider: 提供商配置
            model_id: 模型 ID

        Returns:
            是否健康
        """
        if not provider.enabled:
            return False

        # 根据提供商类型执行不同的检查
        if provider.provider_id == "openai":
            return await self._check_openai_health(provider, model_id)
        elif provider.provider_id == "anthropic":
            return await self._check_anthropic_health(provider, model_id)
        else:
            return await self._check_generic_health(provider, model_id)

    async def _check_openai_health(self, provider, model_id: Optional[str]) -> bool:
        """检查 OpenAI 健康状态"""
        api_key = self.model_manager.get_decrypted_api_key(provider.provider_id)
        if not api_key:
            return False

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                # 简单的 models 列表请求来验证 API key
                response = await client.get(
                    f"{provider.api_base_url}/models",
                    headers={"Authorization": f"Bearer {api_key}"}
                )
                return response.status_code == 200
        except Exception:
            return False

    async def _check_anthropic_health(self, provider, model_id: Optional[str]) -> bool:
        """检查 Anthropic 健康状态"""
        api_key = self.model_manager.get_decrypted_api_key(provider.provider_id)
        if not api_key:
            return False

        try:
            # Anthropic 没有简单的健康检查端点
            # 我们尝试一个最小的请求
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.post(
                    f"{provider.api_base_url}/v1/messages",
                    headers={
                        "x-api-key": api_key,
                        "anthropic-version": "2023-06-01",
                        "content-type": "application/json"
                    },
                    json={
                        "model": model_id or provider.default_model or "claude-3-sonnet-20240229",
                        "max_tokens": 1,
                        "messages": [{"role": "user", "content": "hi"}]
                    }
                )
                # 200 或 429 (rate limit) 都表示服务可用
                return response.status_code in [200, 429]
        except Exception:
            return False

    async def _check_generic_health(self, provider, model_id: Optional[str]) -> bool:
        """检查通用提供商健康状态"""
        if not provider.api_base_url:
            return False

        try:
            async with httpx.AsyncClient(timeout=self.timeout_seconds) as client:
                response = await client.get(provider.api_base_url)
                return response.status_code < 500
        except Exception:
            return False

    async def check_all_providers(self) -> LLMHealthCheckResponse:
        """
        检查所有提供商的健康状态

        Returns:
            健康检查响应
        """
        providers = self.model_manager.get_enabled_providers()
        tasks = []

        for provider in providers:
            # 检查提供商的默认模型
            if provider.default_model:
                tasks.append(self.check_provider_health(provider.provider_id, provider.default_model))
            else:
                tasks.append(self.check_provider_health(provider.provider_id))

        statuses = await asyncio.gather(*tasks, return_exceptions=True)

        # 处理结果
        health_statuses = []
        for status in statuses:
            if isinstance(status, Exception):
                # 创建一个失败的状态
                health_statuses.append(LLMHealthStatus(
                    provider_id="unknown",
                    is_healthy=False,
                    last_check_at=datetime.now().isoformat(),
                    last_error=str(status)
                ))
            else:
                health_statuses.append(status)

        # 统计健康和不健康的数量
        healthy_count = sum(1 for s in health_statuses if s.is_healthy)
        unhealthy_count = len(health_statuses) - healthy_count

        return LLMHealthCheckResponse(
            server_time=datetime.now().isoformat(),
            providers=health_statuses,
            overall_healthy=unhealthy_count == 0,
            healthy_count=healthy_count,
            unhealthy_count=unhealthy_count
        )

    def get_cached_health_status(
        self,
        provider_id: str,
        model_id: Optional[str] = None
    ) -> Optional[LLMHealthStatus]:
        """
        获取缓存的健康状态

        Args:
            provider_id: 提供商 ID
            model_id: 模型 ID

        Returns:
            健康状态（如果存在）
        """
        status_key = f"{provider_id}:{model_id or 'default'}"
        return self.health_status.get(status_key)

    def is_provider_healthy(
        self,
        provider_id: str,
        model_id: Optional[str] = None,
        max_age_seconds: int = 300
    ) -> bool:
        """
        检查提供商是否健康（使用缓存）

        Args:
            provider_id: 提供商 ID
            model_id: 模型 ID
            max_age_seconds: 最大缓存时间

        Returns:
            是否健康
        """
        status = self.get_cached_health_status(provider_id, model_id)
        if not status:
            return True  # 如果没有状态，假设健康

        # 检查缓存是否过期
        if status.last_check_at:
            last_check = datetime.fromisoformat(status.last_check_at)
            if datetime.now() - last_check > timedelta(seconds=max_age_seconds):
                return True  # 缓存过期，假设健康

        return status.is_healthy and status.error_count < self.max_error_count

    def clear_health_status(self, provider_id: Optional[str] = None):
        """
        清除健康状态缓存

        Args:
            provider_id: 提供商 ID（可选，如果不提供则清除所有）
        """
        if provider_id:
            keys_to_remove = [k for k in self.health_status.keys() if k.startswith(provider_id)]
            for key in keys_to_remove:
                del self.health_status[key]
        else:
            self.health_status.clear()


# 全局健康检查器实例
_health_checker: Optional[LLMHealthChecker] = None


def get_health_checker() -> LLMHealthChecker:
    """获取健康检查器实例"""
    global _health_checker
    if _health_checker is None:
        _health_checker = LLMHealthChecker()
    return _health_checker


async def check_provider_health(provider_id: str, model_id: Optional[str] = None) -> LLMHealthStatus:
    """检查提供商健康状态（便捷函数）"""
    return await get_health_checker().check_provider_health(provider_id, model_id)


async def check_all_providers() -> LLMHealthCheckResponse:
    """检查所有提供商健康状态（便捷函数）"""
    return await get_health_checker().check_all_providers()
