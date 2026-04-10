from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Device, Pet
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User

router = APIRouter()


class DeviceCreate(BaseModel):
    id: str
    name: str
    model: str = "NUONUO-PET-V1"


class DeviceUpdate(BaseModel):
    name: Optional[str] = None
    config: Optional[dict] = None


class DeviceResponse(BaseModel):
    id: str
    name: str
    model: str
    status: str
    last_online: Optional[datetime]
    pet_id: Optional[int]
    pet_name: Optional[str]

    class Config:
        from_attributes = True


class DeviceListResponse(BaseModel):
    items: List[DeviceResponse]
    total: int


@router.get("", response_model=DeviceListResponse)
async def get_devices(
    page: int = 1,
    size: int = 10,
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备列表"""
    query = select(Device).options(selectinload(Device.pet))

    if search:
        query = query.where(Device.name.contains(search))

    # 计算总数
    count_query = select(Device)
    if search:
        count_query = count_query.where(Device.name.contains(search))
    total_result = await db.execute(count_query)
    total = len(total_result.scalars().all())

    # 分页
    query = query.offset((page - 1) * size).limit(size)
    result = await db.execute(query)
    devices = result.scalars().all()

    items = []
    for device in devices:
        items.append(DeviceResponse(
            id=device.id,
            name=device.name,
            model=device.model,
            status=device.status,
            last_online=device.last_online,
            pet_id=device.pet.id if device.pet else None,
            pet_name=device.pet.name if device.pet else None,
        ))

    return {"items": items, "total": total}


@router.post("", response_model=DeviceResponse)
async def create_device(
    device_data: DeviceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """注册设备"""
    # 检查设备ID是否已存在
    result = await db.execute(select(Device).where(Device.id == device_data.id))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="设备ID已存在")

    device = Device(
        id=device_data.id,
        name=device_data.name,
        model=device_data.model,
        user_id=current_user.id,
        status="pending",
    )
    db.add(device)
    await db.commit()
    await db.refresh(device)

    return DeviceResponse(
        id=device.id,
        name=device.name,
        model=device.model,
        status=device.status,
        last_online=device.last_online,
        pet_id=None,
        pet_name=None,
    )


@router.get("/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取设备详情"""
    result = await db.execute(
        select(Device).where(Device.id == device_id).options(selectinload(Device.pet))
    )
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    return DeviceResponse(
        id=device.id,
        name=device.name,
        model=device.model,
        status=device.status,
        last_online=device.last_online,
        pet_id=device.pet.id if device.pet else None,
        pet_name=device.pet.name if device.pet else None,
    )


@router.put("/{device_id}", response_model=DeviceResponse)
async def update_device(
    device_id: str,
    device_data: DeviceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """更新设备"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    if device_data.name:
        device.name = device_data.name
    if device_data.config:
        device.config = device_data.config

    await db.commit()
    await db.refresh(device)

    return DeviceResponse(
        id=device.id,
        name=device.name,
        model=device.model,
        status=device.status,
        last_online=device.last_online,
        pet_id=None,
        pet_name=None,
    )


@router.delete("/{device_id}")
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除设备"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    await db.delete(device)
    await db.commit()

    return {"message": "设备已删除"}


@router.post("/{device_id}/heartbeat")
async def device_heartbeat(
    device_id: str,
    db: AsyncSession = Depends(get_db)
):
    """设备心跳"""
    result = await db.execute(select(Device).where(Device.id == device_id))
    device = result.scalar_one_or_none()

    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    device.status = "online"
    device.last_online = datetime.utcnow()
    await db.commit()

    return {"status": "ok"}
