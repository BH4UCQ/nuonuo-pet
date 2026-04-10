from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from app.core.database import Base


class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    devices = relationship("Device", back_populates="user")
    pets = relationship("Pet", back_populates="user")


class Device(Base):
    """设备模型"""
    __tablename__ = "devices"

    id = Column(String(50), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    name = Column(String(100), nullable=False)
    model = Column(String(50), default="NUONUO-PET-V1")
    firmware_version = Column(String(20), default="1.0.0")
    status = Column(String(20), default="pending")  # pending, online, offline
    last_online = Column(DateTime, nullable=True)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="devices")
    pet = relationship("Pet", back_populates="device", uselist=False)


class Pet(Base):
    """宠物模型"""
    __tablename__ = "pets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=True)
    name = Column(String(50), nullable=False)
    species = Column(String(50), default="cat")  # cat, dog, rabbit, etc.
    level = Column(Integer, default=1)
    experience = Column(Integer, default=0)

    # 情绪状态
    emotion = Column(String(20), default="calm")  # happy, sad, angry, calm, excited
    emotion_intensity = Column(Float, default=0.5)

    # 需求值
    hunger = Column(Integer, default=50)  # 0-100
    happiness = Column(Integer, default=50)
    energy = Column(Integer, default=50)

    # 成长数据
    total_interactions = Column(Integer, default=0)
    total_chat_messages = Column(Integer, default=0)

    # 自定义配置
    theme = Column(String(50), default="default")
    custom_data = Column(JSON, default={})

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="pets")
    device = relationship("Device", back_populates="pet")
    interactions = relationship("Interaction", back_populates="pet")


class Interaction(Base):
    """交互记录模型"""
    __tablename__ = "interactions"

    id = Column(Integer, primary_key=True, index=True)
    pet_id = Column(Integer, ForeignKey("pets.id"), nullable=False)
    device_id = Column(String(50), ForeignKey("devices.id"), nullable=True)

    type = Column(String(20), nullable=False)  # chat, touch, feed, play
    content = Column(Text, nullable=True)  # 用户输入
    response = Column(Text, nullable=True)  # 宠物响应

    # 情绪变化
    emotion_before = Column(String(20), nullable=True)
    emotion_after = Column(String(20), nullable=True)
    emotion_delta = Column(Float, default=0)

    # AI 相关
    model_used = Column(String(50), nullable=True)
    tokens_used = Column(Integer, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)

    pet = relationship("Pet", back_populates="interactions")


class Resource(Base):
    """资源模型"""
    __tablename__ = "resources"

    id = Column(Integer, primary_key=True, index=True)
    type = Column(String(20), nullable=False)  # species, theme, sound
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    file_path = Column(String(255), nullable=True)
    metadata = Column(JSON, default={})
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
