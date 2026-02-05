"""Shared fixtures for CLI tests."""

from collections.abc import Generator
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from marketsched.jpx.data import CacheMetadata
from marketsched.jpx.data.cache import JPXDataCache


@pytest.fixture(autouse=True)
def setup_test_cache(tmp_path: Path) -> Generator[JPXDataCache, None, None]:
    """Set up a test cache with sample data for all CLI tests.

    This fixture automatically runs for all CLI tests and provides
    a temporary cache directory with valid test data.
    """
    from zoneinfo import ZoneInfo

    import marketsched.jpx.data.cache as cache_module

    # Save original cache
    original_cache = cache_module._cache

    # Create test cache in temp directory
    cache = JPXDataCache(cache_dir=tmp_path / "marketsched")
    cache_module._cache = cache

    # Create test SQ dates data
    sq_dates = []
    for year in range(2024, 2028):
        for month in range(1, 13):
            # Calculate second Friday of each month (approximate SQ date)
            first_day = date(year, month, 1)
            # Find first Friday
            days_until_friday = (4 - first_day.weekday()) % 7
            first_friday = first_day.replace(day=1 + days_until_friday)
            # Second Friday is 7 days later
            sq_date = first_friday.replace(day=first_friday.day + 7)

            sq_dates.append(
                {
                    "year": year,
                    "month": month,
                    "sq_date": sq_date,
                    "product_type": "index",
                }
            )

    # Create test holidays data
    holidays = [
        # 2026 holidays
        {
            "date": date(2026, 1, 1),
            "holiday_name": "元日",
            "is_trading": False,
            "is_confirmed": True,
        },
        {
            "date": date(2026, 1, 2),
            "holiday_name": "休業日",
            "is_trading": False,
            "is_confirmed": True,
        },
        {
            "date": date(2026, 1, 3),
            "holiday_name": "休業日",
            "is_trading": False,
            "is_confirmed": True,
        },
        {
            "date": date(2026, 1, 12),
            "holiday_name": "成人の日",
            "is_trading": False,
            "is_confirmed": True,
        },
        {
            "date": date(2026, 2, 11),
            "holiday_name": "建国記念の日",
            "is_trading": False,
            "is_confirmed": True,
        },
        {
            "date": date(2026, 2, 23),
            "holiday_name": "天皇誕生日",
            "is_trading": False,
            "is_confirmed": True,
        },
    ]

    # Write test data
    cache.write_sq_dates(sq_dates)
    cache.write_holidays(holidays)

    # Write metadata
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    metadata = CacheMetadata(
        last_updated=now,
        version="0.0.1-test",
        source_urls={
            "sq_dates": "test://sq_dates",
            "holidays": "test://holidays",
        },
        cache_valid_until=now + timedelta(hours=24),
    )
    cache.write_metadata(metadata)

    yield cache

    # Restore original cache
    cache_module._cache = original_cache
