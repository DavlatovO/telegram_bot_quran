"""Best-effort forwarding of inbound user messages to an admin chat."""

from __future__ import annotations

import html
import logging

import aiohttp

from config import settings

log = logging.getLogger(__name__)

_session: aiohttp.ClientSession | None = None


def _configured() -> bool:
    return bool(settings.admin_bot_token and settings.admin_chat_id)


async def init_session() -> None:
    global _session
    if _configured() and (_session is None or _session.closed):
        _session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.request_timeout)
        )


async def close_session() -> None:
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
    _session = None


async def notify_admin(username: str | None, user_id: int, message_text: str | None) -> None:
    if not _configured():
        return
    if _session is None or _session.closed:
        log.debug("Admin session not initialised; skipping notification.")
        return

    text = (
        f"New message from <b>@{html.escape(str(username or 'N/A'))}</b> "
        f"(<code>{user_id}</code>):\n"
        f"<blockquote>{html.escape(str(message_text or ''))}</blockquote>"
    )
    url = f"https://api.telegram.org/bot{settings.admin_bot_token}/sendMessage"
    try:
        async with _session.post(
            url,
            data={"chat_id": settings.admin_chat_id, "text": text, "parse_mode": "HTML"},
        ) as resp:
            resp.raise_for_status()
    except aiohttp.ClientError as exc:
        log.warning("Failed to notify admin: %s", exc)
