"""Slash-command handlers: /start, /help, /languages."""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards import language_kb

router = Router(name="commands")

_WELCOME = (
    "Hello! This bot is all about the <b>Qur'an</b>.\n"
    "Type any chapter and verse, e.g. <code>78:8</code>, <code>17</code>, "
    "<code>al-baqara</code>, or <code>baqara 5</code>."
)


@router.message(CommandStart())
async def start(message: Message) -> None:
    await message.answer(_WELCOME)
    await message.answer(
        "<b>Please choose a language to get started:</b>", reply_markup=language_kb()
    )


@router.message(Command("help"))
async def help_(message: Message) -> None:
    await message.answer("Contact: <b>@Bestoftheplayers</b>")


@router.message(Command("languages"))
async def languages(message: Message) -> None:
    await message.answer("<b>Choose a language:</b>", reply_markup=language_kb())
