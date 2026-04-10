from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    """应用配置"""

    # Application
    APP_NAME: str = "Nuonuo Pet"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = "sqlite+aiosqlite:///./nuonuo_pet.db"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # JWT
    JWT_SECRET: str = "your-super-secret-key"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 1440

    # AI Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_API_BASE: str = "https://api.openai.com/v1"
    OPENAI_MODEL: str = "gpt-4"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-3-opus-20240229"

    # AI Settings
    AI_TEMPERATURE: float = 0.7
    AI_MAX_TOKENS: int = 2000
    AI_TIMEOUT: int = 30

    # CORS
    CORS_ORIGINS: List[str] = ["http://localhost:5173"]

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
