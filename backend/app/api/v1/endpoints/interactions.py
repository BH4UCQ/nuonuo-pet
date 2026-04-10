from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Interaction
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User

router = APIRouter()


class InteractionResponse(BaseModel):
    id: int
    pet_id: int
    device_id: Optional[str]
    type: str
    content: Optional[str]
    response: Optional[str]
    emotion_delta: float
    created_at: datetime

    class Config:
        from_attributes = True


@router.get("")
async def get_interactions(
    page: int = 1,
    size: int = 20,
    pet_id: Optional[int] = None,
    interaction_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取交互记录列表"""
    query = select(Interaction)

    if pet_id:
        query = query.where(Interaction.pet_id == pet_id)
    if interaction_type:
        query = query.where(Interaction.type == interaction_type)

    query = query.order_by(Interaction.created_at.desc())
    query = query.offset((page - 1) * size).limit(size)

    result = await db.execute(query)
    interactions = result.scalars().all()

    return {
        "items": [
            InteractionResponse(
                id=i.id,
                pet_id=i.pet_id,
                device_id=i.device_id,
                type=i.type,
                content=i.content,
                response=i.response,
                emotion_delta=i.emotion_delta,
                created_at=i.created_at,
            )
            for i in interactions
        ]
    }
