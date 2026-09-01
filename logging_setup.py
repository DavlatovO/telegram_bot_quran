"""Central logging configuration."""

from __future__ import annotations

import logging

from config import settings

_CONFIGURED = False


def setup_logging() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    logging.basicConfig(
        level=settings.log_level.upper(),
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # aiohttp logs one line per request at INFO; keep the noise down.
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
    _CONFIGURED = True
