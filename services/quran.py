"""Async client for the fawazahmed0 Quran API, with an in-process TTL cache."""

from __future__ import annotations

import html
import logging
from typing import Any

import aiohttp
from cachetools import TTLCache

from config import settings

log = logging.getLogger(__name__)

_API_ROOT = "https://cdn.jsdelivr.net/gh/fawazahmed0/quran-api@1/editions"
_ARABIC_EDITION = "ara-quranuthmanienc"

_session: aiohttp.ClientSession | None = None
# Keyed by full URL -> parsed JSON. Surah payloads change rarely, so a day-long
# TTL keeps navigation and repeat lookups free of upstream calls.
_cache: TTLCache[str, Any] = TTLCache(maxsize=settings.cache_maxsize, ttl=settings.cache_ttl)


class QuranError(Exception):
    """Carries a message safe to show directly to the user."""


async def init_session() -> None:
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=settings.request_timeout),
            headers={"User-Agent": "telegram-bot-quran"},
        )


async def close_session() -> None:
    global _session
    if _session is not None and not _session.closed:
        await _session.close()
    _session = None


def _get_session() -> aiohttp.ClientSession:
    if _session is None or _session.closed:
        raise QuranError("Service is starting up, please try again in a moment.")
    return _session


async def _fetch_surah(edition: str, surah: int) -> list[dict[str, Any]]:
    """Return the list of verse dicts ({chapter, verse, text}) for a surah."""
    url = f"{_API_ROOT}/{edition}/{surah}.json"
    cached = _cache.get(url)
    if cached is not None:
        return cached

    try:
        async with _get_session().get(url) as resp:
            resp.raise_for_status()
            data = await resp.json(content_type=None)
    except aiohttp.ClientResponseError as exc:
        if exc.status == 404:
            raise QuranError(
                "That translation or surah is not available. Please check your input."
            ) from exc
        log.warning("Quran API error %s for %s", exc.status, url)
        raise QuranError(
            "The Quran service is unavailable right now. Please try again later."
        ) from exc
    except aiohttp.ClientError as exc:
        log.warning("Quran API request failed for %s: %s", url, exc)
        raise QuranError("Could not reach the Quran service. Please try again later.") from exc

    try:
        verses = data["chapter"]
    except (KeyError, TypeError) as exc:
        raise QuranError("Unexpected response from the Quran service.") from exc
    if not verses:
        raise QuranError("No verses were returned for that surah.")

    _cache[url] = verses
    return verses


def _validate_surah(surah: int) -> None:
    if not 1 <= surah <= 114:
        raise QuranError("The surah number must be between 1 and 114.")


def _fmt(text: str) -> str:
    return html.escape(str(text))


async def get_ayah(edition: str, surah: int, ayah: int) -> str:
    """Formatted HTML string for a single ayah (Arabic + translation)."""
    _validate_surah(surah)
    if ayah < 1:
        raise QuranError("The ayah number must be a positive number.")

    arabic = await _fetch_surah(_ARABIC_EDITION, surah)
    translation = await _fetch_surah(edition, surah)

    if ayah > len(arabic):
        raise QuranError(
            f"Surah {surah} has only {len(arabic)} verses. Please try a smaller number."
        )

    a = arabic[ayah - 1]
    t = translation[ayah - 1] if ayah - 1 < len(translation) else {"text": ""}
    ref = f"{a['chapter']}:{a['verse']}"
    return (
        f"📖 <b>{_fmt(a['text'])}</b> ({ref})\n\n"
        f"<blockquote><i>{_fmt(t['text'])}</i> <b>({ref})</b>.</blockquote>"
    )


async def get_surah(edition: str, surah: int) -> list[str]:
    """List of formatted HTML strings, one per verse, for a whole surah."""
    _validate_surah(surah)

    arabic = await _fetch_surah(_ARABIC_EDITION, surah)
    translation = await _fetch_surah(edition, surah)

    verses: list[str] = []
    for i, a in enumerate(arabic):
        ref = f"{a['chapter']}:{a['verse']}"
        t = translation[i] if i < len(translation) else {"text": ""}
        verses.append(
            f"📖 <b>{_fmt(a['text'])}</b> <b>({ref})</b>\n\n\n"
            f"       <i>{_fmt(t['text'])}</i> <b>({ref}).</b>\n"
        )
    return verses
