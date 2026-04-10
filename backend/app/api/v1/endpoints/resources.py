from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_db
from app.models.models import Resource
from app.api.v1.endpoints.auth import get_current_user
from app.models.models import User

router = APIRouter()


class ResourceCreate(BaseModel):
    type: str
    name: str
    description: Optional[str] = None
    file_path: Optional[str] = None
    metadata: dict = {}


class ResourceResponse(BaseModel):
    id: int
    type: str
    name: str
    description: Optional[str]
    file_path: Optional[str]
    metadata: dict
    is_active: bool

    class Config:
        from_attributes = True


@router.get("")
async def get_resources(
    type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """获取资源列表"""
    query = select(Resource).where(Resource.is_active == True)

    if type:
        query = query.where(Resource.type == type)

    result = await db.execute(query)
    resources = result.scalars().all()

    return {
        "items": [
            ResourceResponse(
                id=r.id,
                type=r.type,
                name=r.name,
                description=r.description,
                file_path=r.file_path,
                metadata=r.metadata,
                is_active=r.is_active,
            )
            for r in resources
        ]
    }


@router.post("", response_model=ResourceResponse)
async def create_resource(
    resource_data: ResourceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建资源"""
    resource = Resource(
        type=resource_data.type,
        name=resource_data.name,
        description=resource_data.description,
        file_path=resource_data.file_path,
        metadata=resource_data.metadata,
    )
    db.add(resource)
    await db.commit()
    await db.refresh(resource)

    return ResourceResponse(
        id=resource.id,
        type=resource.type,
        name=resource.name,
        description=resource.description,
        file_path=resource.file_path,
        metadata=resource.metadata,
        is_active=resource.is_active,
    )


@router.delete("/{resource_id}")
async def delete_resource(
    resource_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """删除资源"""
    result = await db.execute(select(Resource).where(Resource.id == resource_id))
    resource = result.scalar_one_or_none()

    if not resource:
        raise HTTPException(status_code=404, detail="资源不存在")

    resource.is_active = False
    await db.commit()

    return {"message": "资源已删除"}
