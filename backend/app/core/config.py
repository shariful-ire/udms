import json
from pydantic_settings import BaseSettings
from pydantic import AnyHttpUrl, MySQLDsn, RedisDsn, field_validator
from typing import Any, List, Optional, Union
from functools import lru_cache


def _parse_list(v: Any) -> Any:
    if isinstance(v, str):
        v = v.strip()
        if v.startswith("["):
            return json.loads(v)
        return [item.strip() for item in v.split(",") if item.strip()]
    return v


class Settings(BaseSettings):
    # ─── Application ────────────────────────────────────────────────────────
    APP_NAME: str = "University Dining Management System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    SECRET_KEY: str = "dev-secret-key-change-in-production-minimum-32chars"
    API_PREFIX: str = "/api/v1"
    ALLOWED_HOSTS: List[str] = ["*"]

    @field_validator("ALLOWED_HOSTS", "CORS_ORIGINS", "CORS_ALLOW_METHODS", "CORS_ALLOW_HEADERS", "ALLOWED_IMAGE_TYPES", mode="before")
    @classmethod
    def parse_list_fields(cls, v: Any) -> Any:
        return _parse_list(v)

    # ─── Database ────────────────────────────────────────────────────────────
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_NAME: str = "udms"
    DB_USER: str = "udms_user"
    DB_PASSWORD: str
    DB_POOL_SIZE: int = 10
    DB_MAX_OVERFLOW: int = 20
    DB_POOL_RECYCLE: int = 3600

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    @property
    def DATABASE_URL_SYNC(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}?charset=utf8mb4"

    # ─── Redis ───────────────────────────────────────────────────────────────
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 20

    @property
    def REDIS_URL(self) -> str:
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    # ─── JWT / Auth ───────────────────────────────────────────────────────────
    JWT_SECRET_KEY: str = "dev-jwt-secret-key-change-in-production-minimum-32chars"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    OTP_EXPIRE_MINUTES: int = 15
    PASSWORD_RESET_OTP_EXPIRE_MINUTES: int = 10
    OTP_RESEND_COOLDOWN_SECONDS: int = 60

    # ─── Security / Rate Limiting ─────────────────────────────────────────────
    MAX_LOGIN_ATTEMPTS: int = 5
    ACCOUNT_LOCKOUT_MINUTES: int = 15
    RATE_LIMIT_LOGIN: str = "10/15minutes"
    RATE_LIMIT_REGISTER: str = "5/hour"
    RATE_LIMIT_PASSWORD_RESET: str = "3/hour"
    RATE_LIMIT_GLOBAL: str = "300/minute"

    # ─── CORS ─────────────────────────────────────────────────────────────────
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ─── Email ────────────────────────────────────────────────────────────────
    MAIL_USERNAME: str = ""
    MAIL_PASSWORD: str = ""
    MAIL_FROM: str = "noreply@university.edu"
    MAIL_FROM_NAME: str = "University Dining System"
    MAIL_PORT: int = 587
    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False
    MAIL_USE_CREDENTIALS: bool = True
    MAIL_VALIDATE_CERTS: bool = True

    # ─── Celery ───────────────────────────────────────────────────────────────
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None

    @property
    def CELERY_BROKER(self) -> str:
        return self.CELERY_BROKER_URL or self.REDIS_URL

    @property
    def CELERY_BACKEND(self) -> str:
        return self.CELERY_RESULT_BACKEND or self.REDIS_URL

    # ─── File Upload ──────────────────────────────────────────────────────────
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE_MB: int = 5
    ALLOWED_IMAGE_TYPES: List[str] = ["image/jpeg", "image/png", "image/webp"]

    # ─── Pagination ───────────────────────────────────────────────────────────
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ─── Argon2 ───────────────────────────────────────────────────────────────
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 2
    ARGON2_HASH_LEN: int = 32
    ARGON2_SALT_LEN: int = 16

    # ─── Frontend URL ─────────────────────────────────────────────────────────
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
