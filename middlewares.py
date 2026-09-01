"""Aiogram middlewares."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject
from cachetools import TTLCache

from config import settings


class ThrottlingMiddleware(BaseMiddleware):
    """Drop updates from a user that arrive faster than ``throttle_seconds``."""

    def __init__(self, rate: float | None = None) -> None:
        self._seen: TTLCache[int, bool] = TTLCache(
            maxsize=10_000, ttl=rate or settings.throttle_seconds
        )

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = data.get("event_from_user")
        if user is not None:
            if user.id in self._seen:
                if isinstance(event, CallbackQuery):
                    await event.answer("Please slow down.")
                elif isinstance(event, Message):
                    await event.reply("Please slow down a little. ⏳")
                return None
            self._seen[user.id] = True
        return await handler(event, data)
