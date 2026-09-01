"""Entrypoint: builds the bot and runs it behind a webhook (or long polling)."""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from config import settings
from data import db
from handlers import main_router
from logging_setup import setup_logging
from middlewares import ThrottlingMiddleware
from services import admin, quran

log = logging.getLogger(__name__)

BOT_COMMANDS = [
    BotCommand(command="start", description="Restart and choose a language"),
    BotCommand(command="languages", description="Change translation language"),
    BotCommand(command="help", description="Contact / help"),
]


def build_dispatcher() -> Dispatcher:
    dp = Dispatcher()
    throttle = ThrottlingMiddleware()
    dp.message.middleware(throttle)
    dp.callback_query.middleware(throttle)
    dp.include_router(main_router)
    return dp


async def _startup(bot: Bot) -> None:
    await db.connect()
    await quran.init_session()
    await admin.init_session()
    await bot.set_my_commands(BOT_COMMANDS)


async def _shutdown(bot: Bot) -> None:
    await admin.close_session()
    await quran.close_session()
    await db.close()
    await bot.session.close()


async def run_polling(bot: Bot, dp: Dispatcher) -> None:
    await _startup(bot)
    await bot.delete_webhook(drop_pending_updates=True)
    log.info("Starting long polling")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await _shutdown(bot)


def run_webhook(bot: Bot, dp: Dispatcher) -> None:
    async def _on_startup(_app: web.Application) -> None:
        await _startup(bot)
        await bot.set_webhook(
            settings.webhook_url,
            secret_token=settings.webhook_secret,
            drop_pending_updates=True,
            allowed_updates=dp.resolve_used_update_types(),
        )
        log.info("Webhook set to %s", settings.webhook_url)

    async def _on_cleanup(_app: web.Application) -> None:
        await _shutdown(bot)

    app = web.Application()
    app.router.add_get("/", lambda _: web.Response(text="Bot is running!"))
    app.on_startup.append(_on_startup)
    app.on_cleanup.append(_on_cleanup)

    SimpleRequestHandler(
        dispatcher=dp, bot=bot, secret_token=settings.webhook_secret
    ).register(app, path=settings.webhook_path)
    setup_application(app, dp, bot=bot)

    log.info("Listening on 0.0.0.0:%s", settings.port)
    web.run_app(app, host="0.0.0.0", port=settings.port, print=None)


def main() -> None:
    setup_logging()
    bot = Bot(
        token=settings.bot_token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = build_dispatcher()

    if settings.use_polling:
        asyncio.run(run_polling(bot, dp))
    else:
        run_webhook(bot, dp)


if __name__ == "__main__":
    main()
