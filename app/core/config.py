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

    # ── Base de datos ────────────────────────────────────
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "climai_db"

    # DATABASE_URL se construye en un validator para usar los valores
    # reales del entorno, no los defaults de clase evaluados en tiempo de definición
    DATABASE_URL: str = ""

    # ── Servicios externos ───────────────────────────────
    AEMET_API_KEY: str = ""
    REDIS_URL: str = "redis://redis:6379/0"
    TELEGRAM_BOT_TOKEN: str = ""

    # ── Seguridad JWT ────────────────────────────────────
    SECRET_KEY: str = "cambia_esta_clave_en_produccion_minimo_32_chars"

    # ── CORS ─────────────────────────────────────────────
    ALLOWED_ORIGINS: list[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "allow",
    }

    def model_post_init(self, __context) -> None:
        # Si DATABASE_URL no viene del entorno, la construimos con los valores reales
        if not self.DATABASE_URL:
            object.__setattr__(
                self,
                "DATABASE_URL",
                f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@db:5432/{self.POSTGRES_DB}",
            )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()