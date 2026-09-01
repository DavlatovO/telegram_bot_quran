"""Inline keyboard builders."""

from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

LANGUAGES: dict[str, str] = {
    "en": "English 🇬🇧",
    "ar": "Arabic 🇸🇦",
    "uz": "Uzbek 🇺🇿",
}


def language_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for code, label in LANGUAGES.items():
        builder.button(text=label, callback_data=f"lang:{code}")
    builder.adjust(1)
    return builder.as_markup()


def navigation_kb(surah: int, index: int, total: int) -> InlineKeyboardMarkup | None:
    """Prev/Next row for verse ``index`` of ``total``; ``None`` when a single verse."""
    if total <= 1:
        return None
    row: list[InlineKeyboardButton] = []
    if index > 0:
        row.append(
            InlineKeyboardButton(text="<< Previous", callback_data=f"nav:{surah}:{index - 1}")
        )
    if index < total - 1:
        row.append(
            InlineKeyboardButton(text="Next >>", callback_data=f"nav:{surah}:{index + 1}")
        )
    return InlineKeyboardMarkup(inline_keyboard=[row])
