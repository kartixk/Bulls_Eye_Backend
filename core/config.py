"""Centralised env-backed configuration."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")


@dataclass(frozen=True)
class Settings:
    SUPABASE_URL: str = os.getenv("SUPABASE_URL", "")
    SUPABASE_SERVICE_ROLE_KEY: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    ANGEL_ONE_API_KEY: str = os.getenv("ANGEL_ONE_API_KEY", "")
    ANGEL_ONE_CLIENT_ID: str = os.getenv("ANGEL_ONE_CLIENT_ID", "")
    ANGEL_ONE_PIN: str = os.getenv("ANGEL_ONE_PIN", "")
    ANGEL_ONE_TOTP_SECRET: str = os.getenv("ANGEL_ONE_TOTP_SECRET", "")
    TELEGRAM_BOT_TOKEN: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    TELEGRAM_CHAT_ID: str = os.getenv("TELEGRAM_CHAT_ID", "")
    FLASK_SECRET_KEY: str = os.getenv("FLASK_SECRET_KEY", "dev-only")
    INTERNAL_API_KEY: str = os.getenv("INTERNAL_API_KEY", "")
    CORS_ORIGINS: str = os.getenv("CORS_ORIGINS", "*")
    OWNER_USER_ID: str = os.getenv("OWNER_USER_ID", "")
    TZ: str = os.getenv("TZ", "Asia/Kolkata")


settings = Settings()
