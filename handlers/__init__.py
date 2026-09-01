"""Aggregate router for all handler modules."""

from __future__ import annotations

from aiogram import Router

from handlers import commands, language, quran

main_router = Router(name="main")
main_router.include_router(commands.router)
main_router.include_router(language.router)
main_router.include_router(quran.router)

__all__ = ["main_router"]
