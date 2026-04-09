"""
模型路由和调用实现
支持多模型切换、降级、健康检查
"""

from __future__ import annotations

import asyncio
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
import httpx
from .storage import MODEL_ROUTES, MODEL_ROUTE_CONFIG


class ModelCallError(Exception):
    """模型调用错误"""
    def __init__(self, message: str, model_id: Optional[str] = None, provider: Optional[str] = None):
        super().__init__(message)
        self.model_id = model_id
        self.provider = provider


class ModelHealthChecker:
    """模型健康检查器"""
    
    def __init__(self):
        self.health_status: Dict[str, Dict[str, Any]] = {}
        self.last_check_time: Dict[str, float] = {}
        self.check_interval = 300  # 5分钟检查一次
    
    def is_healthy(self, model_id: str) -> bool:
        """检查模型是否健康"""
        if model_id not in self.health_status:
            return True  # 默认健康
        
        status = self.health_status[model_id]
        return status.get("healthy", True)
    
    def record_success(self, model_id: str, latency_ms: float):
        """记录成功调用"""
        self.health_status[model_id] = {
            "healthy": True,
            "last_success": datetime.now(timezone.utc).isoformat(),
            "latency_ms": latency_ms,
            "consecutive_failures": 0,
        }
        self.last_check_time[model_id] = time.time()
    
    def record_failure(self, model_id: str, error: str):
        """记录失败调用"""
        current = self.health_status.get(model_id, {})
        consecutive_failures = current.get("consecutive_failures", 0) + 1
        
        # 连续失败3次标记为不健康
        healthy = consecutive_failures < 3
        
        self.health_status[model_id] = {
            "healthy": healthy,
            "last_failure": datetime.now(timezone.utc).isoformat(),
            "error": error,
            "consecutive_failures": consecutive_failures,
        }
        self.last_check_time[model_id] = time.time()
    
    def get_status(self) -> Dict[str, Any]:
        """获取所有模型健康状态"""
        return {
            "models": self.health_status,
            "check_interval": self.check_interval,
            "last_check": self.last_check_time,
        }


# 全局健康检查器
health_checker = ModelHealthChecker()


class ModelCaller:
    """模型调用器"""
    
    def __init__(self, timeout: float = 30.0):
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)
    
    async def call_local_model(
        self,
        model_name: str,
        prompt: str,
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """调用本地模型"""
        start_time = time.time()
        
        try:
            # 本地模型调用（示例实现）
            # 实际项目中应该连接到本地LLM服务
            
            # 模拟本地模型响应
            await asyncio.sleep(0.1)  # 模拟处理时间
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response": f"[本地模型 {model_name}] 收到消息: {prompt[:50]}...",
                "model_name": model_name,
                "provider": "local",
                "latency_ms": latency_ms,
                "tokens_used": len(prompt.split()),
            }
            
        except Exception as e:
            raise ModelCallError(
                f"本地模型调用失败: {str(e)}",
                model_id=model_name,
                provider="local"
            )
    
    async def call_cloud_model(
        self,
        model_name: str,
        prompt: str,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        context: Optional[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """调用云端模型"""
        start_time = time.time()
        
        try:
            # 云端模型调用（示例实现）
            # 实际项目中应该调用真实的API
            
            # 模拟云端模型响应
            await asyncio.sleep(0.3)  # 模拟网络延迟
            
            latency_ms = (time.time() - start_time) * 1000
            
            return {
                "success": True,
                "response": f"[云端模型 {model_name}] 我理解了你的意思。{prompt[:30]}...",
                "model_name": model_name,
                "provider": "cloud",
                "latency_ms": latency_ms,
                "tokens_used": len(prompt.split()) * 2,  # 云端通常消耗更多token
            }
            
        except Exception as e:
            raise ModelCallError(
                f"云端模型调用失败: {str(e)}",
                model_id=model_name,
                provider="cloud"
            )
    
    async def call_with_fallback(
        self,
        prompt: str,
        preferred_route_id: Optional[str] = None,
        fallback_route_ids: Optional[List[str]] = None,
        context: Optional[str] = None,
        **kwargs
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """
        带降级的模型调用
        返回: (响应结果, 路由信息)
        """
        from .main import resolve_model_route
        
        # 解析模型路由
        route, is_fallback, reason, available_ids = resolve_model_route(
            preferred_route_id,
            fallback_route_ids,
            prefer_enabled=True,
            allow_fallback=True
        )
        
        if route is None:
            raise ModelCallError("没有可用的模型路由")
        
        route_info = {
            "route_id": route.get("id"),
            "provider": route.get("provider"),
            "model_name": route.get("model_name"),
            "is_fallback": is_fallback,
            "reason": reason,
            "available_routes": available_ids,
        }
        
        model_id = route.get("id", "unknown")
        
        # 检查健康状态
        if not health_checker.is_healthy(model_id):
            # 尝试降级到其他模型
            for fallback_id in fallback_route_ids or []:
                fallback_route, _, _, _ = resolve_model_route(
                    fallback_id,
                    prefer_enabled=True,
                    allow_fallback=False
                )
                
                if fallback_route and health_checker.is_healthy(fallback_route.get("id", "")):
                    route = fallback_route
                    route_info["route_id"] = route.get("id")
                    route_info["provider"] = route.get("provider")
                    route_info["model_name"] = route.get("model_name")
                    route_info["is_fallback"] = True
                    route_info["reason"] = f"原模型 {model_id} 不健康，降级到 {fallback_id}"
                    model_id = fallback_route.get("id", "")
                    break
        
        # 执行调用
        provider = route.get("provider", "local")
        model_name = route.get("model_name", "unknown")
        
        try:
            if provider == "local":
                result = await self.call_local_model(
                    model_name,
                    prompt,
                    context=context,
                    **kwargs
                )
            elif provider == "cloud":
                result = await self.call_cloud_model(
                    model_name,
                    prompt,
                    context=context,
                    **kwargs
                )
            else:
                raise ModelCallError(f"未知的模型提供者: {provider}")
            
            # 记录成功
            health_checker.record_success(model_id, result.get("latency_ms", 0))
            
            return result, route_info
            
        except ModelCallError as e:
            # 记录失败
            health_checker.record_failure(model_id, str(e))
            
            # 尝试降级
            if not is_fallback:
                # 递归调用，尝试降级
                remaining_fallbacks = [
                    fid for fid in (fallback_route_ids or [])
                    if fid != preferred_route_id
                ]
                
                if remaining_fallbacks:
                    return await self.call_with_fallback(
                        prompt,
                        preferred_route_id=remaining_fallbacks[0],
                        fallback_route_ids=remaining_fallbacks[1:],
                        context=context,
                        **kwargs
                    )
            
            raise
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# 全局调用器
model_caller = ModelCaller()


async def chat_with_model(
    pet_id: str,
    message: str,
    context: Optional[str] = None,
    preferred_route_id: Optional[str] = None,
) -> Tuple[str, Dict[str, Any]]:
    """
    与模型对话
    返回: (响应文本, 元数据)
    """
    from .memory_enhanced import get_memory_context_for_chat
    
    # 获取记忆上下文
    if not context:
        context = get_memory_context_for_chat(pet_id, max_tokens=300)
    
    # 构建完整提示
    full_prompt = f"{context}\n\n用户: {message}\n助手:" if context else message
    
    # 调用模型
    result, route_info = await model_caller.call_with_fallback(
        full_prompt,
        preferred_route_id=preferred_route_id,
        fallback_route_ids=MODEL_ROUTE_CONFIG.get("fallback_route_ids", []),
        context=context,
    )
    
    # 返回响应和元数据
    metadata = {
        "model_route": route_info,
        "tokens_used": result.get("tokens_used", 0),
        "latency_ms": result.get("latency_ms", 0),
        "provider": result.get("provider"),
        "model_name": result.get("model_name"),
    }
    
    return result.get("response", ""), metadata


def get_model_health_status() -> Dict[str, Any]:
    """获取模型健康状态"""
    return health_checker.get_status()
