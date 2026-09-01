"""Verse/surah lookup: text queries and Prev/Next navigation."""

from __future__ import annotations

import asyncio
import logging
import re
from dataclasses import dataclass
from typing import Literal, NamedTuple

from aiogram import F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, Message, User
from cachetools import TTLCache

from data import db
from keyboards import navigation_kb
from models.surah_list import resolve_surah
from services.admin import notify_admin
from services.quran import QuranError, get_surah

log = logging.getLogger(__name__)
router = Router(name="quran")

# Language code -> fawazahmed0 edition slug.
EDITIONS: dict[str, str] = {
    "ar": "ara-quran-la1",
    "uz": "uzb-muhammadsodikmu",
    "en": "eng-abdelhaleem",
}

_NUMBER = re.compile(r"\d+")
_REF = re.compile(r"(\d+):(\d+)")
_NAME = re.compile(r"[a-zA-Z-]+(?:\s+\d+(?:-oyat)?)?")

_bg_tasks: set[asyncio.Task] = set()


class OpenSurah(NamedTuple):
    surah: int
    verses: list[str]


# The whole rendered surah the user is currently reading, downloaded once when
# they open it. Prev/Next then slice this in-memory list and never touch the
# Quran API (or the DB) again. Keyed by user id; bounded and time-limited, so
# the only thing that forces a re-download is a bot restart or a very long idle.
_open: TTLCache[int, OpenSurah] = TTLCache(maxsize=1000, ttl=2 * 3600)


@dataclass(frozen=True)
class Query:
    kind: Literal["surah", "ayah"]
    surah: int
    ayah: int | None = None


def parse_query(text: str) -> Query | str | None:
    """Interpret a user query.

    Returns a :class:`Query`, a ``str`` error message for input that has the
    right shape but is invalid (e.g. an unknown surah name), or ``None`` when
    the text is not a recognisable query at all.
    """
    text = text.strip()
    if not text:
        return None

    if _NUMBER.fullmatch(text):
        return Query("surah", int(text))

    m = _REF.fullmatch(text)
    if m:
        return Query("ayah", int(m.group(1)), int(m.group(2)))

    if _NAME.fullmatch(text):
        parts = text.lower().split()
        surah = resolve_surah(parts[0])
        if surah is None:
            return "<b>Invalid surah name.</b> Please provide a valid surah name."
        if len(parts) == 2:
            try:
                return Query("ayah", surah, int(parts[1].removesuffix("-oyat")))
            except ValueError:
                return (
                    "<b>Invalid ayah number.</b> Use <code>surah</code>, "
                    "<code>surah number</code>, or <code>surah number-oyat</code>."
                )
        return Query("surah", surah)

    return None


def _spawn(coro) -> None:
    task = asyncio.create_task(coro)
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


async def _record(user: User, text: str | None) -> None:
    try:
        await db.upsert_user(user.id, user.username, user.first_name)
    except Exception:  # noqa: BLE001 - side effect must never break the reply
        log.exception("Failed to persist user %s", user.id)
    try:
        await notify_admin(user.username, user.id, text)
    except Exception:  # noqa: BLE001
        log.exception("Failed to notify admin for user %s", user.id)


@router.message(F.text)
async def handle_text(message: Message) -> None:
    user = message.from_user
    _spawn(_record(user, message.text))

    lang = await db.get_language(user.id)
    if lang is None:
        await message.reply("Please choose a language first — send /languages")
        return
    edition = EDITIONS[lang]

    result = parse_query(message.text)
    if result is None:
        await message.reply("<b>Please check the input again.</b>")
        return
    if isinstance(result, str):
        await message.reply(result)
        return

    # Always download the whole surah once; a single-ayah query just opens it
    # at that verse. Navigation from here on is pure in-memory slicing.
    try:
        verses = await get_surah(edition, result.surah)
    except QuranError as exc:
        await message.reply(str(exc))
        return

    if result.kind == "ayah":
        assert result.ayah is not None
        if not 1 <= result.ayah <= len(verses):
            await message.reply(
                f"Surah {result.surah} has {len(verses)} verses — pick 1–{len(verses)}."
            )
            return
        index = result.ayah - 1
    else:
        index = 0

    _open[user.id] = OpenSurah(result.surah, verses)
    await message.reply(
        verses[index], reply_markup=navigation_kb(result.surah, index, len(verses))
    )


@router.message()
async def handle_non_text(message: Message) -> None:
    if message.from_user is not None:
        _spawn(_record(message.from_user, None))
    await message.reply(
        "Please send a text query, e.g. <code>2:255</code>, <code>17</code>, "
        "or <code>al-fatiha</code>."
    )


@router.callback_query(F.data.startswith("nav:"))
async def navigate(callback: CallbackQuery) -> None:
    try:
        _, surah_s, index_s = callback.data.split(":")
        surah, index = int(surah_s), int(index_s)
    except ValueError:
        await callback.answer()
        return

    uid = callback.from_user.id
    cached = _open.get(uid)

    if cached is not None and cached.surah == surah:
        verses = cached.verses  # in-memory hit: no API, no DB
    else:
        # Only reason we get here: the bot restarted or the view idled out.
        log.info("Surah %s not held for user %s — downloading once", surah, uid)
        lang = await db.get_language(uid)
        if lang is None:
            await callback.answer("Please choose a language first — send /languages")
            return
        try:
            verses = await get_surah(EDITIONS[lang], surah)
        except QuranError as exc:
            await callback.answer(str(exc)[:190])
            return

    _open[uid] = OpenSurah(surah, verses)  # store / refresh TTL
    index = max(0, min(index, len(verses) - 1))

    async def _edit() -> None:
        if callback.message is None:
            return
        try:
            await callback.message.edit_text(
                verses[index], reply_markup=navigation_kb(surah, index, len(verses))
            )
        except TelegramBadRequest as exc:
            log.debug("Navigation edit failed: %s", exc)

    # Fire the edit and the callback ack together - one round-trip, not two.
    await asyncio.gather(_edit(), callback.answer())
