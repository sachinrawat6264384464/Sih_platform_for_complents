from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
import os


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "AICTE NEXUS - Intelligent Institution Complaint Monitoring & Coordination Platform"

    # Security
    SECRET_KEY: str = "aicte_nexus_super_secret_development_key_change_in_production_min32chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Database
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5433
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "aicte_nexus"
    
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5433/aicte_nexus"
    SYNC_DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5433/aicte_nexus"

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def validate_async_db_url(cls, v: str) -> str:
        # If external env var is pointing to cloud or postgres://, enforce local postgres or normalize
        if not v or "localhost:5433" not in v:
            return "postgresql+asyncpg://postgres:postgres@localhost:5433/aicte_nexus"
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql+asyncpg://", 1)
        elif v.startswith("postgresql://") and not v.startswith("postgresql+asyncpg://"):
            v = v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    @field_validator("SYNC_DATABASE_URL", mode="before")
    @classmethod
    def validate_sync_db_url(cls, v: str) -> str:
        if not v or "localhost:5433" not in v:
            return "postgresql://postgres:postgres@localhost:5433/aicte_nexus"
        if v.startswith("postgres://"):
            v = v.replace("postgres://", "postgresql://", 1)
        elif "+asyncpg" in v:
            v = v.replace("+asyncpg", "")
        return v

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_LOCAL_PATH: str = "./uploads"
    MAX_FILE_SIZE_MB: int = 25

    # CORS
    ALLOWED_ORIGINS: Union[str, List[str]] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Overlap & RAG Weights
    HYBRID_BM25_WEIGHT: float = 0.4
    HYBRID_VECTOR_WEIGHT: float = 0.6
    OVERLAP_SIMILARITY_THRESHOLD: float = 0.75
    CONFIRMED_OVERLAP_THRESHOLD: float = 0.88

    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
