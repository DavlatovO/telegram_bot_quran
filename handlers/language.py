"""Language-selection callback handler."""

from __future__ import annotations

import logging

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery

from data import db
from keyboards import LANGUAGES

log = logging.getLogger(__name__)
router = Router(name="language")


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery) -> None:
    code = callback.data.split(":", 1)[1]
    if code not in LANGUAGES:
        await callback.answer("Unknown language.")
        return

    await db.set_language(callback.from_user.id, code)

    try:
        if callback.message is not None:
            await callback.message.edit_text(f"You selected <b>{LANGUAGES[code]}</b>")
    except TelegramBadRequest as exc:
        log.debug("Could not edit language message: %s", exc)
    await callback.answer()
