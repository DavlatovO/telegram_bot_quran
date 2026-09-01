"""Unit tests for query parsing and surah-name resolution."""

from __future__ import annotations

import pytest

from handlers.quran import Query, parse_query
from models.surah_list import resolve_surah


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("112", Query("surah", 112)),
        ("  17 ", Query("surah", 17)),
        ("2:255", Query("ayah", 2, 255)),
        ("al-fatiha", Query("surah", 1)),
        ("AL-FATIHA", Query("surah", 1)),
        ("baqara 5", Query("ayah", 2, 5)),
        ("baqara 5-oyat", Query("ayah", 2, 5)),
        ("ixlos", Query("surah", 112)),
    ],
)
def test_parse_query_valid(text: str, expected: Query) -> None:
    assert parse_query(text) == expected


@pytest.mark.parametrize("text", ["zzz", "zzz 9", "notasurah 3"])
def test_parse_query_bad_name_returns_message(text: str) -> None:
    result = parse_query(text)
    assert isinstance(result, str) and "surah name" in result.lower()


@pytest.mark.parametrize("text", ["", "   ", "hello world foo", "2:255:1", "!!!"])
def test_parse_query_unrecognised(text: str) -> None:
    assert parse_query(text) is None


def test_resolve_surah() -> None:
    assert resolve_surah("Al-Baqara") == 2
    assert resolve_surah(" baqara ") == 2
    assert resolve_surah("an-nas-oyat") == 114
    assert resolve_surah("nope") is None
