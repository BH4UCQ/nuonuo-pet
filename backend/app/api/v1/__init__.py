from fastapi import APIRouter

from app.api.v1.endpoints import auth, devices, pets, interactions, resources

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["认证"])
api_router.include_router(devices.router, prefix="/devices", tags=["设备"])
api_router.include_router(pets.router, prefix="/pets", tags=["宠物"])
api_router.include_router(interactions.router, prefix="/interactions", tags=["交互"])
api_router.include_router(resources.router, prefix="/resources", tags=["资源"])
