"""Test environment: provide config values before anything imports `config`."""

from __future__ import annotations

import os

os.environ.setdefault("bot_token", "test:token")
os.environ.setdefault("USE_POLLING", "true")
