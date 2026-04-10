"""
pytest 配置文件
"""
import pytest
import asyncio
from typing import Generator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.core.database import Base
from app.models.models import User, Pet, Device


# 测试数据库 URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop():
    """创建事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def db_session() -> AsyncSession:
    """创建测试数据库会话"""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    async_session = async_sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """创建测试用户"""
    from app.core.security import get_password_hash
    
    user = User(
        username="testuser",
        email="test@example.com",
        password_hash=get_password_hash("testpass123"),
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_device(db_session: AsyncSession, test_user: User) -> Device:
    """创建测试设备"""
    device = Device(
        id="test-device-001",
        user_id=test_user.id,
        name="Test Device",
        model="NUONUO-PET-V1",
        status="online",
    )
    db_session.add(device)
    await db_session.commit()
    await db_session.refresh(device)
    return device


@pytest.fixture
async def test_pet(db_session: AsyncSession, test_user: User, test_device: Device) -> Pet:
    """创建测试宠物"""
    pet = Pet(
        user_id=test_user.id,
        device_id=test_device.id,
        name="小诺",
        species="cat",
        level=1,
        emotion="calm",
        hunger=50,
        happiness=50,
    )
    db_session.add(pet)
    await db_session.commit()
    await db_session.refresh(pet)
    return pet
