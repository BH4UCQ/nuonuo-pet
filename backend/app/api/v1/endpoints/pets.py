from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Pet, Device, Interaction
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User
from app.services.pet_service import PetService

router = APIRouter()


class PetCreate(BaseModel):
    name: str
    species: str = "cat"
    device_id: Optional[str] = None


class PetUpdate(BaseModel):
    name: Optional[str] = None
    theme: Optional[str] = None


class InteractionRequest(BaseModel):
    type: str
    content: str


class PetResponse(BaseModel):
    id: int
    name: str
    species: str
    level: int
    emotion: str
    hunger: int
    happiness: int
    device_id: Optional[str]
    device_name: Optional[str]

    class Config:
        from_attributes = True


class PetListResponse(BaseModel):
    items: List[PetResponse]
    total: int


@router.get("", response_model=PetListResponse)
async def get_pets(
    page: int = 1,
    size: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取宠物列表"""
    query = select(Pet).options(selectinload(Pet.device))

    # 计算总数
    total_result = await db.execute(select(Pet))
    total = len(total_result.scalars().all())

    # 分页
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    pets = result.scalars().all()

    items = [
        PetResponse(
            id=pet.id,
            name=pet.name,
            species=pet.species,
            level=pet.level,
            emotion=pet.emotion,
            hunger=pet.hunger,
            happiness=pet.happiness,
            device_id=pet.device_id,
            device_name=pet.device.name if pet.device else None,
        )
        for pet in pets
    ]

    return {"items": items, "total": total}


@router.post("", response_model=PetResponse)
async def create_pet(
    pet_data: PetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建宠物"""
    pet = Pet(
        user_id=current_user.id,
        name=pet_data.name,
        species=pet_data.species,
        device_id=pet_data.device_id,
    )
    db.add(pet)
    await db.commit()
    await db.refresh(pet)

    return PetResponse(
        id=pet.id,
        name=pet.name,
        species=pet.species,
        level=pet.level,
        emotion=pet.emotion,
        hunger=pet.hunger,
        happiness=pet.happiness,
        device_id=pet.device_id,
        device_name=None,
    )


@router.get("/{pet_id}", response_model=PetResponse)
async def get_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取宠物详情"""
    result = await db.execute(
        select(Pet).where(Pet.id == pet_id).options(selectinload(Pet.device))
    )
    pet = result.scalar_one_or_none()

    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    return PetResponse(
        id=pet.id,
        name=pet.name,
        species=pet.species,
        level=pet.level,
        emotion=pet.emotion,
        hunger=pet.hunger,
        happiness=pet.happiness,
        device_id=pet.device_id,
        device_name=pet.device.name if pet.device else None,
    )


@router.post("/{pet_id}/interact")
async def interact(
    pet_id: int,
    interaction_data: InteractionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """与宠物交互"""
    # 初始化宠物服务
    service = PetService(db, pet_id)
    if not await service.initialize():
        raise HTTPException(status_code=404, detail="宠物不存在")

    # 根据交互类型调用不同方法
    if interaction_data.type == "chat":
        result = await service.chat(interaction_data.content)
    elif interaction_data.type == "touch":
        result = await service.touch()
    elif interaction_data.type == "feed":
        result = await service.feed()
    elif interaction_data.type == "play":
        result = await service.play()
    else:
        raise HTTPException(status_code=400, detail="不支持的交互类型")

    return result


@router.get("/{pet_id}/status")
async def get_pet_status(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取宠物完整状态"""
    service = PetService(db, pet_id)
    if not await service.initialize():
        raise HTTPException(status_code=404, detail="宠物不存在")

    return await service.get_status()


@router.get("/{pet_id}/history")
async def get_history(
    pet_id: int,
    page: int = 1,
    size: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取交互历史"""
    query = (
        select(Interaction)
        .where(Interaction.pet_id == pet_id)
        .order_by(Interaction.created_at.desc())
    )

    # 分页
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    interactions = result.scalars().all()

    return {
        "items": [
            {
                "id": i.id,
                "type": i.type,
                "content": i.content,
                "response": i.response,
                "emotion_delta": i.emotion_delta,
                "created_at": i.created_at,
            }
            for i in interactions
        ]
    }


@router.delete("/{pet_id}")
async def delete_pet(
    pet_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除宠物"""
    result = await db.execute(select(Pet).where(Pet.id == pet_id))
    pet = result.scalar_one_or_none()

    if not pet:
        raise HTTPException(status_code=404, detail="宠物不存在")

    await db.delete(pet)
    await db.commit()

    return {"message": "宠物已删除"}
