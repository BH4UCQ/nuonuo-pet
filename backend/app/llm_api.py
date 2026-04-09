"""
LLM API 路由
提供 LLM 交互相关的 API 接口
"""
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from .models import (
    LLMRequest,
    LLMResponse,
    LLMConfigResponse,
    LLMConfigUpdateRequest,
    LLMHealthCheckResponse,
    ConversationListResponse,
    ConversationDetailResponse,
    ConversationHistory
)
from .llm_conversation_service import get_conversation_service
from .llm_model_manager import get_model_manager
from .llm_health_check import check_all_providers, check_provider_health


router = APIRouter(prefix="/api/llm", tags=["LLM"])


@router.post("/chat", response_model=LLMResponse)
async def chat(request: LLMRequest):
    """
    与 LLM 进行对话

    Args:
        request: LLM 请求

    Returns:
        LLM 响应
    """
    try:
        service = get_conversation_service()
        response = await service.chat(request)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health", response_model=LLMHealthCheckResponse)
async def health_check():
    """
    检查所有 LLM 提供商的健康状态

    Returns:
        健康检查响应
    """
    try:
        response = await check_all_providers()
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health/{provider_id}")
async def provider_health_check(provider_id: str, model_id: Optional[str] = None):
    """
    检查特定提供商的健康状态

    Args:
        provider_id: 提供商 ID
        model_id: 模型 ID（可选）

    Returns:
        健康状态
    """
    try:
        status = await check_provider_health(provider_id, model_id)
        return status
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=LLMConfigResponse)
async def get_config():
    """
    获取 LLM 配置

    Returns:
        LLM 配置响应
    """
    try:
        manager = get_model_manager()
        return LLMConfigResponse(
            server_time=datetime.now().isoformat(),
            providers=manager.get_all_providers(),
            models=manager.get_all_models(),
            default_provider_id=manager.default_provider_id,
            default_model_id=manager.default_model_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/provider/{provider_id}")
async def update_provider_config(provider_id: str, request: LLMConfigUpdateRequest):
    """
    更新提供商配置

    Args:
        provider_id: 提供商 ID
        request: 配置更新请求

    Returns:
        更新后的提供商配置
    """
    try:
        manager = get_model_manager()
        update_data = request.dict(exclude_unset=True)
        provider = manager.update_provider(provider_id, **update_data)
        return provider
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/model/{model_id}")
async def update_model_config(model_id: str, request: LLMConfigUpdateRequest):
    """
    更新模型配置

    Args:
        model_id: 模型 ID
        request: 配置更新请求

    Returns:
        更新后的模型配置
    """
    try:
        manager = get_model_manager()
        update_data = request.dict(exclude_unset=True)
        model = manager.update_model(model_id, **update_data)
        return model
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/default-model/{model_id}")
async def set_default_model(model_id: str):
    """
    设置默认模型

    Args:
        model_id: 模型 ID
    """
    try:
        manager = get_model_manager()
        manager.set_default_model(model_id)
        return {"ok": True, "default_model_id": model_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversations/{pet_id}", response_model=ConversationListResponse)
async def list_conversations(pet_id: str, limit: int = 10):
    """
    列出宠物的所有对话

    Args:
        pet_id: 宠物 ID
        limit: 返回数量限制

    Returns:
        对话列表
    """
    try:
        service = get_conversation_service()
        summaries = await service.list_conversations(pet_id, limit)
        return ConversationListResponse(
            pet_id=pet_id,
            server_time=datetime.now().isoformat(),
            total=len(summaries),
            items=summaries
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/conversation/{conversation_id}", response_model=ConversationDetailResponse)
async def get_conversation(conversation_id: str):
    """
    获取对话详情

    Args:
        conversation_id: 对话 ID

    Returns:
        对话详情
    """
    try:
        service = get_conversation_service()
        conversation = await service.get_conversation_history(conversation_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return ConversationDetailResponse(
            server_time=datetime.now().isoformat(),
            conversation=conversation
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/conversation/{conversation_id}")
async def delete_conversation(conversation_id: str):
    """
    删除对话

    Args:
        conversation_id: 对话 ID
    """
    try:
        service = get_conversation_service()
        deleted = await service.delete_conversation(conversation_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Conversation not found")

        return {"ok": True, "deleted": True}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
