# app/core/config.py
import os
from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # ── Aplicación ───────────────────────────────────────
    PROJECT_NAME: str = "ClimAI"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    # ── Base de datos (Persona 1) ────────────────────────
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "password")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "climai_db")
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        f"postgresql+asyncpg://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"
)

    # ── Servicios externos (Persona 1) ───────────────────
    AEMET_API_KEY: str = os.getenv("AEMET_API_KEY", "")
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://redis:6379/0")

    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")

    # ── Seguridad JWT (tu responsabilidad) ───────────────
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "cambia_esta_clave_en_produccion_minimo_32_chars"
    )

    # ── CORS (tu responsabilidad) ────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()