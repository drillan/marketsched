"""Shared pytest fixtures for marketsched tests."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest


@pytest.fixture
def jst() -> ZoneInfo:
    """Return JST timezone."""
    return ZoneInfo("Asia/Tokyo")


@pytest.fixture
def utc() -> ZoneInfo:
    """Return UTC timezone."""
    return ZoneInfo("UTC")


@pytest.fixture
def sample_business_day() -> date:
    """Return a known business day (Friday, 2026-02-06)."""
    return date(2026, 2, 6)


@pytest.fixture
def sample_weekend() -> date:
    """Return a known weekend day (Saturday, 2026-02-07)."""
    return date(2026, 2, 7)


@pytest.fixture
def sample_day_session_time(jst: ZoneInfo) -> datetime:
    """Return a datetime during DAY session (10:00 JST)."""
    return datetime(2026, 2, 6, 10, 0, tzinfo=jst)


@pytest.fixture
def sample_night_session_time(jst: ZoneInfo) -> datetime:
    """Return a datetime during NIGHT session (20:00 JST)."""
    return datetime(2026, 2, 6, 20, 0, tzinfo=jst)


@pytest.fixture
def sample_closed_time(jst: ZoneInfo) -> datetime:
    """Return a datetime during CLOSED period (16:30 JST gap)."""
    return datetime(2026, 2, 6, 16, 30, tzinfo=jst)
