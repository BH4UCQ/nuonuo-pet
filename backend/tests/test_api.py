"""
API 端点测试
"""
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.models import User, Pet, Device
from app.core.security import create_access_token


@pytest.mark.asyncio
class TestAuthAPI:
    """认证 API 测试"""

    async def test_register(self, db_session: AsyncSession):
        """测试用户注册"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/register",
                json={
                    "username": "newuser",
                    "email": "new@example.com",
                    "password": "password123",
                },
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"

    async def test_login(self, test_user: User):
        """测试用户登录"""
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/auth/login",
                data={
                    "username": "testuser",
                    "password": "testpass123",
                },
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.asyncio
class TestDeviceAPI:
    """设备 API 测试"""

    async def test_get_devices(self, test_user: User, test_device: Device):
        """测试获取设备列表"""
        token = create_access_token({"sub": test_user.username, "user_id": test_user.id})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/devices",
                headers={"Authorization": f"Bearer {token}"},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_create_device(self, test_user: User):
        """测试创建设备"""
        token = create_access_token({"sub": test_user.username, "user_id": test_user.id})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/devices",
                json={
                    "id": "new-device-001",
                    "name": "New Device",
                    "model": "NUONUO-PET-V1",
                },
                headers={"Authorization": f"Bearer {token}"},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "new-device-001"


@pytest.mark.asyncio
class TestPetAPI:
    """宠物 API 测试"""

    async def test_get_pets(self, test_user: User, test_pet: Pet):
        """测试获取宠物列表"""
        token = create_access_token({"sub": test_user.username, "user_id": test_user.id})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                "/api/v1/pets",
                headers={"Authorization": f"Bearer {token}"},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    async def test_create_pet(self, test_user: User, test_device: Device):
        """测试创建宠物"""
        token = create_access_token({"sub": test_user.username, "user_id": test_user.id})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.post(
                "/api/v1/pets",
                json={
                    "name": "新宠物",
                    "species": "dog",
                    "device_id": test_device.id,
                },
                headers={"Authorization": f"Bearer {token}"},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "新宠物"
        assert data["species"] == "dog"

    async def test_get_pet_detail(self, test_user: User, test_pet: Pet):
        """测试获取宠物详情"""
        token = create_access_token({"sub": test_user.username, "user_id": test_user.id})
        
        async with AsyncClient(app=app, base_url="http://test") as client:
            response = await client.get(
                f"/api/v1/pets/{test_pet.id}",
                headers={"Authorization": f"Bearer {token}"},
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_pet.id
        assert data["name"] == test_pet.name
