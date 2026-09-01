"""Typed application configuration, loaded from environment / ``.env``."""

from __future__ import annotations

import sys
from functools import lru_cache
from pathlib import Path

from pydantic import Field, ValidationError, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=BASE_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # --- Telegram -----------------------------------------------------------
    # Kept lowercase for backwards compatibility with the existing ``.env``
    # (``bot_token=...``); env lookup is case-insensitive either way.
    bot_token: str = Field(..., alias="bot_token")

    # --- HTTP server ------------------------------------------------------------
    port: int = 8080

    # --- Webhook ----------------------------------------------------------------
    # Public HTTPS origin Telegram will POST updates to, e.g.
    # ``https://my-app.example.com`` (no trailing slash).
    webhook_base_url: str | None = None
    webhook_path: str = "/webhook"
    # Verified against the ``X-Telegram-Bot-Api-Secret-Token`` header on every
    # incoming update so forged requests are rejected.
    webhook_secret: str | None = None
    # Local-dev escape hatch: run long polling instead of a webhook.
    use_polling: bool = False

    # --- Admin notifications (optional) ---------------------------------------
    admin_bot_token: str | None = None
    # A numeric id or an @username / @channel handle - kept as a string.
    admin_chat_id: str | None = None

    # --- Storage -------------------------------------------------------------
    db_path: Path = BASE_DIR / "data" / "data_collection.db"

    # --- Upstream Quran API ------------------------------------------------------
    request_timeout: float = 10.0
    cache_ttl: int = 86_400
    cache_maxsize: int = 512

    # --- Abuse control ------------------------------------------------------
    throttle_seconds: float = 0.7

    # --- Logging ----------------------------------------------------------------
    log_level: str = "INFO"

    @property
    def webhook_url(self) -> str:
        assert self.webhook_base_url is not None  # guarded by _check_webhook
        return f"{self.webhook_base_url.rstrip('/')}{self.webhook_path}"

    @model_validator(mode="after")
    def _check_webhook(self) -> Settings:
        if not self.use_polling and not (self.webhook_base_url and self.webhook_secret):
            raise ValueError(
                "Webhook mode requires WEBHOOK_BASE_URL and WEBHOOK_SECRET. "
                "Set both, or set USE_POLLING=true for local development."
            )
        return self


@lru_cache
def get_settings() -> Settings:
    try:
        return Settings()  # type: ignore[call-arg]
    except ValidationError as exc:
        # Report field names and messages only - never echo the values,
        # which include the bot token.
        problems = "\n".join(
            f"  - {'.'.join(str(p) for p in err['loc']) or '(config)'}: {err['msg']}"
            for err in exc.errors()
        )
        sys.exit(
            f"Invalid configuration:\n{problems}\n\n"
            "See .env.example for the expected variables."
        )


settings = get_settings()
