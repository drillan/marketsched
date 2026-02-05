"""Shared fixtures for CLI tests."""

from collections.abc import Generator
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pyarrow as pa
import pytest

from marketsched.jpx.data import CacheMetadata, DataType
from marketsched.jpx.data.cache import ParquetCacheManager


@pytest.fixture(autouse=True)
def setup_test_cache(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[ParquetCacheManager]:
    """Set up a test cache with sample data for all CLI tests.

    This fixture automatically runs for all CLI tests and provides
    a temporary cache directory with valid test data.
    """
    cache_dir = tmp_path / "marketsched"

    # Monkeypatch DEFAULT_CACHE_DIR so all default-constructed managers use tmp
    monkeypatch.setattr(
        ParquetCacheManager,
        "DEFAULT_CACHE_DIR",
        cache_dir,
    )

    manager = ParquetCacheManager(cache_dir=cache_dir)
    now = datetime.now(UTC)
    expires_at = now + timedelta(hours=24)

    # Create test SQ dates data
    contract_months = []
    last_trading_days = []
    sq_dates = []
    product_categories = []

    for year in range(2024, 2028):
        for month in range(1, 13):
            # Calculate second Friday of each month (approximate SQ date)
            first_day = date(year, month, 1)
            days_until_friday = (4 - first_day.weekday()) % 7
            first_friday = first_day.replace(day=1 + days_until_friday)
            second_friday = first_friday.replace(day=first_friday.day + 7)

            contract_months.append(f"{year}{month:02d}")
            last_trading_days.append(second_friday - timedelta(days=1))
            sq_dates.append(second_friday)
            product_categories.append("index_futures_options")

    sq_table = pa.table(
        {
            "contract_month": contract_months,
            "last_trading_day": last_trading_days,
            "sq_date": sq_dates,
            "product_category": product_categories,
        }
    )
    sq_metadata = CacheMetadata(
        data_type=DataType.SQ_DATES,
        source_url="test://sq_dates",
        fetched_at=now,
        expires_at=expires_at,
        schema_version=1,
        record_count=len(contract_months),
    )
    manager.write(DataType.SQ_DATES, sq_table, sq_metadata)

    # Create test holidays data
    holiday_table = pa.table(
        {
            "date": [
                date(2026, 1, 1),
                date(2026, 1, 2),
                date(2026, 1, 3),
                date(2026, 1, 12),
                date(2026, 2, 11),
                date(2026, 2, 23),
            ],
            "holiday_name": [
                "元日",
                "休業日",
                "休業日",
                "成人の日",
                "建国記念の日",
                "天皇誕生日",
            ],
            "is_trading": [False, False, False, False, False, False],
            "is_confirmed": [True, True, True, True, True, True],
        }
    )
    holiday_metadata = CacheMetadata(
        data_type=DataType.HOLIDAY_TRADING,
        source_url="test://holidays",
        fetched_at=now,
        expires_at=expires_at,
        schema_version=1,
        record_count=6,
    )
    manager.write(DataType.HOLIDAY_TRADING, holiday_table, holiday_metadata)

    yield manager
