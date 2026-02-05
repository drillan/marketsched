"""Unit tests for JPXDataQuery bridge layer."""

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pyarrow as pa
import pytest

from marketsched.exceptions import CacheNotAvailableError
from marketsched.jpx.data import CacheMetadata, DataType
from marketsched.jpx.data.cache import ParquetCacheManager
from marketsched.jpx.data.query import JPXDataQuery


@pytest.fixture
def cache_manager(tmp_path: Path) -> ParquetCacheManager:
    """Create a ParquetCacheManager with test data."""
    manager = ParquetCacheManager(cache_dir=tmp_path)
    now = datetime.now(UTC)
    expires_at = now + timedelta(hours=24)

    # SQ dates
    sq_table = pa.table(
        {
            "contract_month": ["202601", "202602", "202603"],
            "last_trading_day": [
                date(2026, 1, 8),
                date(2026, 2, 12),
                date(2026, 3, 12),
            ],
            "sq_date": [
                date(2026, 1, 9),
                date(2026, 2, 13),
                date(2026, 3, 13),
            ],
            "product_category": [
                "index_futures_options",
                "index_futures_options",
                "index_futures_options",
            ],
        }
    )
    sq_metadata = CacheMetadata(
        data_type=DataType.SQ_DATES,
        source_url="test://sq",
        fetched_at=now,
        expires_at=expires_at,
        schema_version=1,
        record_count=3,
    )
    manager.write(DataType.SQ_DATES, sq_table, sq_metadata)

    # Holidays
    holiday_table = pa.table(
        {
            "date": [date(2026, 1, 1), date(2026, 1, 12), date(2026, 2, 11)],
            "holiday_name": ["元日", "成人の日", "建国記念の日"],
            "is_trading": [False, True, False],
            "is_confirmed": [True, True, True],
        }
    )
    holiday_metadata = CacheMetadata(
        data_type=DataType.HOLIDAY_TRADING,
        source_url="test://holidays",
        fetched_at=now,
        expires_at=expires_at,
        schema_version=1,
        record_count=3,
    )
    manager.write(DataType.HOLIDAY_TRADING, holiday_table, holiday_metadata)

    return manager


@pytest.fixture
def query(cache_manager: ParquetCacheManager) -> JPXDataQuery:
    """Create a JPXDataQuery with test data."""
    return JPXDataQuery(cache_manager=cache_manager)


@pytest.fixture
def empty_query(tmp_path: Path) -> JPXDataQuery:
    """Create a JPXDataQuery with empty cache."""
    manager = ParquetCacheManager(cache_dir=tmp_path / "empty")
    return JPXDataQuery(cache_manager=manager)


class TestGetSQDate:
    """Tests for get_sq_date."""

    def test_returns_date_for_existing_month(self, query: JPXDataQuery) -> None:
        result = query.get_sq_date(2026, 3)
        assert result == date(2026, 3, 13)

    def test_returns_none_for_missing_month(self, query: JPXDataQuery) -> None:
        result = query.get_sq_date(2026, 12)
        assert result is None

    def test_raises_when_cache_missing(self, empty_query: JPXDataQuery) -> None:
        with pytest.raises(CacheNotAvailableError):
            empty_query.get_sq_date(2026, 1)


class TestGetSQDatesForYear:
    """Tests for get_sq_dates_for_year."""

    def test_returns_sorted_dates(self, query: JPXDataQuery) -> None:
        dates = query.get_sq_dates_for_year(2026)
        assert len(dates) == 3
        assert dates == sorted(dates)
        assert dates[0] == date(2026, 1, 9)
        assert dates[2] == date(2026, 3, 13)

    def test_returns_empty_for_missing_year(self, query: JPXDataQuery) -> None:
        dates = query.get_sq_dates_for_year(2050)
        assert dates == []

    def test_raises_when_cache_missing(self, empty_query: JPXDataQuery) -> None:
        with pytest.raises(CacheNotAvailableError):
            empty_query.get_sq_dates_for_year(2026)


class TestIsHolidayTradingDay:
    """Tests for is_holiday_trading_day."""

    def test_returns_true_for_trading_holiday(self, query: JPXDataQuery) -> None:
        # 成人の日 (is_trading=True)
        assert query.is_holiday_trading_day(date(2026, 1, 12)) is True

    def test_returns_false_for_non_trading_holiday(self, query: JPXDataQuery) -> None:
        # 元日 (is_trading=False)
        assert query.is_holiday_trading_day(date(2026, 1, 1)) is False

    def test_returns_false_for_non_holiday(self, query: JPXDataQuery) -> None:
        # Regular weekday
        assert query.is_holiday_trading_day(date(2026, 2, 6)) is False

    def test_raises_when_cache_missing(self, empty_query: JPXDataQuery) -> None:
        with pytest.raises(CacheNotAvailableError):
            empty_query.is_holiday_trading_day(date(2026, 1, 1))


class TestGetNonTradingHolidays:
    """Tests for get_non_trading_holidays."""

    def test_returns_non_trading_dates(self, query: JPXDataQuery) -> None:
        holidays = query.get_non_trading_holidays()
        assert date(2026, 1, 1) in holidays  # 元日 (non-trading)
        assert date(2026, 2, 11) in holidays  # 建国記念の日 (non-trading)
        assert date(2026, 1, 12) not in holidays  # 成人の日 (trading)

    def test_returns_correct_count(self, query: JPXDataQuery) -> None:
        holidays = query.get_non_trading_holidays()
        assert len(holidays) == 2

    def test_raises_when_cache_missing(self, empty_query: JPXDataQuery) -> None:
        with pytest.raises(CacheNotAvailableError):
            empty_query.get_non_trading_holidays()
