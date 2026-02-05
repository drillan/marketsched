"""Integration tests for JPXIndex market implementation.

These tests verify the business day and SQ date functionality of JPXIndex.
Tests use a temporary cache with ParquetCacheManager to provide predictable test data.
"""

from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from unittest.mock import patch
from zoneinfo import ZoneInfo

import pyarrow as pa
import pytest

from marketsched import SQDataNotFoundError, TimezoneRequiredError
from marketsched.jpx.calendar import JPXCalendar
from marketsched.jpx.data import CacheMetadata, DataType
from marketsched.jpx.data.cache import ParquetCacheManager
from marketsched.jpx.data.query import JPXDataQuery
from marketsched.jpx.index import JPXIndex
from marketsched.session import TradingSession


@pytest.fixture
def cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory."""
    return tmp_path / "cache"


@pytest.fixture
def mock_cache(cache_dir: Path) -> ParquetCacheManager:
    """Create a mock cache with test data."""
    manager = ParquetCacheManager(cache_dir=cache_dir)
    now = datetime.now(UTC)
    expires_at = now + timedelta(hours=24)

    # SQ dates test data (year/month -> contract_month YYYYMM)
    sq_data = [
        ("202601", date(2026, 1, 8), date(2026, 1, 9)),
        ("202602", date(2026, 2, 12), date(2026, 2, 13)),
        ("202603", date(2026, 3, 12), date(2026, 3, 13)),
        ("202604", date(2026, 4, 9), date(2026, 4, 10)),
        ("202605", date(2026, 5, 7), date(2026, 5, 8)),
        ("202606", date(2026, 6, 11), date(2026, 6, 12)),
        ("202607", date(2026, 7, 9), date(2026, 7, 10)),
        ("202608", date(2026, 8, 13), date(2026, 8, 14)),
        ("202609", date(2026, 9, 10), date(2026, 9, 11)),
        ("202610", date(2026, 10, 8), date(2026, 10, 9)),
        ("202611", date(2026, 11, 12), date(2026, 11, 13)),
        ("202612", date(2026, 12, 10), date(2026, 12, 11)),
    ]

    sq_table = pa.table(
        {
            "contract_month": [r[0] for r in sq_data],
            "last_trading_day": [r[1] for r in sq_data],
            "sq_date": [r[2] for r in sq_data],
            "product_category": ["index_futures_options"] * len(sq_data),
        }
    )
    sq_metadata = CacheMetadata(
        data_type=DataType.SQ_DATES,
        source_url="test://sq_dates",
        fetched_at=now,
        expires_at=expires_at,
        schema_version=1,
        record_count=len(sq_data),
    )
    manager.write(DataType.SQ_DATES, sq_table, sq_metadata)

    # Holiday test data
    holiday_table = pa.table(
        {
            "date": [
                date(2025, 12, 31),
                date(2026, 1, 1),
                date(2026, 1, 2),
                date(2026, 1, 3),
                date(2026, 1, 12),
                date(2026, 2, 11),
                date(2026, 2, 23),
            ],
            "holiday_name": [
                "大晦日",
                "元日",
                "正月休み",
                "正月休み",
                "成人の日",
                "建国記念の日",
                "天皇誕生日",
            ],
            "is_trading": [False, False, False, False, True, False, False],
            "is_confirmed": [True, True, True, True, True, True, True],
        }
    )
    holiday_metadata = CacheMetadata(
        data_type=DataType.HOLIDAY_TRADING,
        source_url="test://holidays",
        fetched_at=now,
        expires_at=expires_at,
        schema_version=1,
        record_count=7,
    )
    manager.write(DataType.HOLIDAY_TRADING, holiday_table, holiday_metadata)

    return manager


@pytest.fixture
def market(mock_cache: ParquetCacheManager) -> JPXIndex:
    """Create a JPXIndex with mock cache."""
    data_query = JPXDataQuery(cache_manager=mock_cache)
    calendar = JPXCalendar(data_query=data_query)
    return JPXIndex(calendar)


class TestIsBusinessDay:
    """Test is_business_day() method (US4)."""

    def test_weekday_is_business_day(self, market: JPXIndex) -> None:
        """A regular weekday should be a business day."""
        # Friday, February 6, 2026
        assert market.is_business_day(date(2026, 2, 6)) is True

    def test_saturday_is_not_business_day(self, market: JPXIndex) -> None:
        """Saturday should not be a business day."""
        # Saturday, February 7, 2026
        assert market.is_business_day(date(2026, 2, 7)) is False

    def test_sunday_is_not_business_day(self, market: JPXIndex) -> None:
        """Sunday should not be a business day."""
        # Sunday, February 8, 2026
        assert market.is_business_day(date(2026, 2, 8)) is False

    def test_year_end_holiday_is_not_business_day(self, market: JPXIndex) -> None:
        """Year-end holidays should not be business days."""
        # December 31, 2025 - 大晦日
        assert market.is_business_day(date(2025, 12, 31)) is False
        # January 1, 2026 - 元日
        assert market.is_business_day(date(2026, 1, 1)) is False
        # January 2, 2026 - 正月休み
        assert market.is_business_day(date(2026, 1, 2)) is False
        # January 3, 2026 - 正月休み
        assert market.is_business_day(date(2026, 1, 3)) is False

    def test_holiday_trading_day_is_business_day(self, market: JPXIndex) -> None:
        """Holiday trading days should be business days."""
        # January 12, 2026 - 成人の日 (holiday trading day)
        assert market.is_business_day(date(2026, 1, 12)) is True

    def test_regular_holiday_is_not_business_day(self, market: JPXIndex) -> None:
        """Regular holidays (non-trading) should not be business days."""
        # February 11, 2026 - 建国記念の日 (Wednesday, non-trading holiday)
        assert market.is_business_day(date(2026, 2, 11)) is False
        # February 23, 2026 - 天皇誕生日 (Monday, non-trading holiday)
        assert market.is_business_day(date(2026, 2, 23)) is False


class TestNextBusinessDay:
    """Test next_business_day() method (US4)."""

    def test_next_business_day_from_thursday(self, market: JPXIndex) -> None:
        """Next business day from Thursday should be Friday."""
        # Thursday, February 5, 2026 -> Friday, February 6, 2026
        assert market.next_business_day(date(2026, 2, 5)) == date(2026, 2, 6)

    def test_next_business_day_from_friday(self, market: JPXIndex) -> None:
        """Next business day from Friday should skip weekend to Monday."""
        # Friday, February 6, 2026 -> Monday, February 9, 2026
        assert market.next_business_day(date(2026, 2, 6)) == date(2026, 2, 9)

    def test_next_business_day_from_saturday(self, market: JPXIndex) -> None:
        """Next business day from Saturday should be Monday."""
        # Saturday, February 7, 2026 -> Monday, February 9, 2026
        assert market.next_business_day(date(2026, 2, 7)) == date(2026, 2, 9)

    def test_next_business_day_from_sunday(self, market: JPXIndex) -> None:
        """Next business day from Sunday should be Monday."""
        # Sunday, February 8, 2026 -> Monday, February 9, 2026
        assert market.next_business_day(date(2026, 2, 8)) == date(2026, 2, 9)

    def test_next_business_day_skips_holiday(self, market: JPXIndex) -> None:
        """Next business day should skip non-trading holidays."""
        # Tuesday, February 10, 2026 -> Thursday, February 12, 2026
        # (skips February 11 - 建国記念の日)
        assert market.next_business_day(date(2026, 2, 10)) == date(2026, 2, 12)


class TestPreviousBusinessDay:
    """Test previous_business_day() method (US4)."""

    def test_previous_business_day_from_friday(self, market: JPXIndex) -> None:
        """Previous business day from Friday should be Thursday."""
        # Friday, February 6, 2026 -> Thursday, February 5, 2026
        assert market.previous_business_day(date(2026, 2, 6)) == date(2026, 2, 5)

    def test_previous_business_day_from_monday(self, market: JPXIndex) -> None:
        """Previous business day from Monday should skip weekend to Friday."""
        # Monday, February 9, 2026 -> Friday, February 6, 2026
        assert market.previous_business_day(date(2026, 2, 9)) == date(2026, 2, 6)

    def test_previous_business_day_from_saturday(self, market: JPXIndex) -> None:
        """Previous business day from Saturday should be Friday."""
        # Saturday, February 7, 2026 -> Friday, February 6, 2026
        assert market.previous_business_day(date(2026, 2, 7)) == date(2026, 2, 6)

    def test_previous_business_day_from_sunday(self, market: JPXIndex) -> None:
        """Previous business day from Sunday should be Friday."""
        # Sunday, February 8, 2026 -> Friday, February 6, 2026
        assert market.previous_business_day(date(2026, 2, 8)) == date(2026, 2, 6)

    def test_previous_business_day_skips_holiday(self, market: JPXIndex) -> None:
        """Previous business day should skip non-trading holidays."""
        # Thursday, February 12, 2026 -> Tuesday, February 10, 2026
        # (skips February 11 - 建国記念の日)
        assert market.previous_business_day(date(2026, 2, 12)) == date(2026, 2, 10)


class TestGetSQDate:
    """Test get_sq_date() method (US6)."""

    def test_get_sq_date_march_2026(self, market: JPXIndex) -> None:
        """get_sq_date(2026, 3) should return March SQ date."""
        assert market.get_sq_date(2026, 3) == date(2026, 3, 13)

    def test_get_sq_date_january_2026(self, market: JPXIndex) -> None:
        """get_sq_date(2026, 1) should return January SQ date."""
        assert market.get_sq_date(2026, 1) == date(2026, 1, 9)

    def test_get_sq_date_december_2026(self, market: JPXIndex) -> None:
        """get_sq_date(2026, 12) should return December SQ date."""
        assert market.get_sq_date(2026, 12) == date(2026, 12, 11)

    def test_get_sq_date_not_found(self, market: JPXIndex) -> None:
        """get_sq_date() should raise SQDataNotFoundError for missing data."""
        with pytest.raises(SQDataNotFoundError) as exc_info:
            market.get_sq_date(2050, 1)

        assert "2050" in str(exc_info.value)


class TestIsSQDate:
    """Test is_sq_date() method (US6)."""

    def test_sq_date_returns_true(self, market: JPXIndex) -> None:
        """is_sq_date() should return True for SQ dates."""
        # March 13, 2026 is an SQ date
        assert market.is_sq_date(date(2026, 3, 13)) is True

    def test_non_sq_date_returns_false(self, market: JPXIndex) -> None:
        """is_sq_date() should return False for non-SQ dates."""
        # March 12, 2026 is not an SQ date
        assert market.is_sq_date(date(2026, 3, 12)) is False

    def test_far_future_date_raises_error(self, market: JPXIndex) -> None:
        """is_sq_date() should raise SQDataNotFoundError for dates outside data range."""
        # Far future date - no data available, should raise
        with pytest.raises(SQDataNotFoundError):
            market.is_sq_date(date(2050, 3, 13))


class TestGetSQDatesForYear:
    """Test get_sq_dates_for_year() method (US6)."""

    def test_get_sq_dates_for_year_2026(self, market: JPXIndex) -> None:
        """get_sq_dates_for_year(2026) should return 12 SQ dates."""
        dates = market.get_sq_dates_for_year(2026)
        assert len(dates) == 12

    def test_get_sq_dates_for_year_sorted(self, market: JPXIndex) -> None:
        """get_sq_dates_for_year() should return dates in ascending order."""
        dates = market.get_sq_dates_for_year(2026)
        assert dates == sorted(dates)

    def test_get_sq_dates_for_year_not_found(self, market: JPXIndex) -> None:
        """get_sq_dates_for_year() should raise for missing year."""
        with pytest.raises(SQDataNotFoundError):
            market.get_sq_dates_for_year(2050)


class TestGetSession:
    """Test get_session() method (US7)."""

    def test_day_session_morning(self, market: JPXIndex) -> None:
        """Morning time should be DAY session."""
        # 10:00 JST
        dt = datetime(2026, 2, 6, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.DAY

    def test_day_session_start(self, market: JPXIndex) -> None:
        """08:45 should be DAY session start."""
        dt = datetime(2026, 2, 6, 8, 45, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.DAY

    def test_day_session_end(self, market: JPXIndex) -> None:
        """15:45 should be DAY session end."""
        dt = datetime(2026, 2, 6, 15, 45, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.DAY

    def test_night_session_evening(self, market: JPXIndex) -> None:
        """Evening time should be NIGHT session."""
        # 20:00 JST
        dt = datetime(2026, 2, 6, 20, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.NIGHT

    def test_night_session_start(self, market: JPXIndex) -> None:
        """17:00 should be NIGHT session start."""
        dt = datetime(2026, 2, 6, 17, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.NIGHT

    def test_night_session_midnight(self, market: JPXIndex) -> None:
        """Midnight should be NIGHT session."""
        dt = datetime(2026, 2, 7, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.NIGHT

    def test_night_session_early_morning(self, market: JPXIndex) -> None:
        """05:59 should be NIGHT session."""
        dt = datetime(2026, 2, 7, 5, 59, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.NIGHT

    def test_closed_gap_morning(self, market: JPXIndex) -> None:
        """06:00 - 08:44 should be CLOSED."""
        dt = datetime(2026, 2, 6, 7, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.CLOSED

    def test_closed_gap_afternoon(self, market: JPXIndex) -> None:
        """15:46 - 16:59 should be CLOSED."""
        dt = datetime(2026, 2, 6, 16, 30, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.CLOSED

    def test_timezone_required_error(self, market: JPXIndex) -> None:
        """Naive datetime should raise TimezoneRequiredError."""
        dt = datetime(2026, 2, 6, 10, 0)  # No timezone
        with pytest.raises(TimezoneRequiredError):
            market.get_session(dt)

    def test_utc_timezone_converted(self, market: JPXIndex) -> None:
        """UTC datetime should be converted to JST."""
        # UTC 01:00 = JST 10:00 (DAY session)
        dt = datetime(2026, 2, 6, 1, 0, tzinfo=ZoneInfo("UTC"))
        assert market.get_session(dt) == TradingSession.DAY


class TestGetBusinessDays:
    """Test get_business_days() method (US4)."""

    def test_get_business_days_week(self, market: JPXIndex) -> None:
        """get_business_days() should return weekdays in a week."""
        # Feb 2-6, 2026 (Mon-Fri)
        days = market.get_business_days(date(2026, 2, 2), date(2026, 2, 6))
        assert len(days) == 5
        assert days[0] == date(2026, 2, 2)
        assert days[-1] == date(2026, 2, 6)

    def test_get_business_days_empty_range(self, market: JPXIndex) -> None:
        """get_business_days() should return empty list for invalid range."""
        days = market.get_business_days(date(2026, 2, 6), date(2026, 2, 2))
        assert days == []

    def test_get_business_days_skips_holiday(self, market: JPXIndex) -> None:
        """get_business_days() should skip non-trading holidays."""
        # Feb 9-12, 2026 (Mon-Thu), Feb 11 is holiday
        days = market.get_business_days(date(2026, 2, 9), date(2026, 2, 12))
        assert len(days) == 3
        assert date(2026, 2, 11) not in days

    def test_get_business_days_includes_holiday_trading(self, market: JPXIndex) -> None:
        """get_business_days() should include holiday trading days."""
        # Jan 12, 2026 is a holiday trading day (成人の日)
        days = market.get_business_days(date(2026, 1, 12), date(2026, 1, 12))
        assert days == [date(2026, 1, 12)]


class TestCountBusinessDays:
    """Test count_business_days() method (US4)."""

    def test_count_business_days_week(self, market: JPXIndex) -> None:
        """count_business_days() should count weekdays in a week."""
        # Feb 2-6, 2026 (Mon-Fri)
        count = market.count_business_days(date(2026, 2, 2), date(2026, 2, 6))
        assert count == 5

    def test_count_business_days_empty_range(self, market: JPXIndex) -> None:
        """count_business_days() should return 0 for invalid range."""
        count = market.count_business_days(date(2026, 2, 6), date(2026, 2, 2))
        assert count == 0

    def test_count_business_days_skips_holiday(self, market: JPXIndex) -> None:
        """count_business_days() should not count non-trading holidays."""
        # Feb 9-12, 2026 (Mon-Thu), Feb 11 is holiday
        count = market.count_business_days(date(2026, 2, 9), date(2026, 2, 12))
        assert count == 3


class TestIsTradingHours:
    """Test is_trading_hours() method (US7)."""

    def test_trading_hours_day_session(self, market: JPXIndex) -> None:
        """Should return True during DAY session."""
        dt = datetime(2026, 2, 6, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.is_trading_hours(dt) is True

    def test_trading_hours_night_session(self, market: JPXIndex) -> None:
        """Should return True during NIGHT session."""
        dt = datetime(2026, 2, 6, 20, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.is_trading_hours(dt) is True

    def test_not_trading_hours_gap(self, market: JPXIndex) -> None:
        """Should return False during gap periods."""
        dt = datetime(2026, 2, 6, 16, 30, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.is_trading_hours(dt) is False

    def test_timezone_required_error(self, market: JPXIndex) -> None:
        """is_trading_hours() should raise TimezoneRequiredError for naive datetime."""
        dt = datetime(2026, 2, 6, 10, 0)  # No timezone
        with pytest.raises(TimezoneRequiredError):
            market.is_trading_hours(dt)


class TestCurrentTimeSession:
    """Test get_session() and is_trading_hours() with current time (US7)."""

    def test_get_session_without_argument(self, market: JPXIndex) -> None:
        """get_session() without argument should use current time in market timezone (JST)."""
        # Mock datetime.now to return a known time during DAY session
        mock_now = datetime(2026, 2, 6, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        with patch("marketsched.jpx.index.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now
            session = market.get_session()
            assert session == TradingSession.DAY

    def test_get_session_without_argument_night(self, market: JPXIndex) -> None:
        """get_session() without argument during night session."""
        mock_now = datetime(2026, 2, 6, 20, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        with patch("marketsched.jpx.index.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now
            session = market.get_session()
            assert session == TradingSession.NIGHT

    def test_get_session_without_argument_closed(self, market: JPXIndex) -> None:
        """get_session() without argument during closed period."""
        # Morning gap (06:00-08:44)
        mock_now = datetime(2026, 2, 6, 7, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        with patch("marketsched.jpx.index.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now
            session = market.get_session()
            assert session == TradingSession.CLOSED

    def test_is_trading_hours_without_argument(self, market: JPXIndex) -> None:
        """is_trading_hours() without argument should use current time in market timezone (JST)."""
        # During DAY session
        mock_now = datetime(2026, 2, 6, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        with patch("marketsched.jpx.index.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now
            assert market.is_trading_hours() is True

    def test_is_trading_hours_without_argument_closed(self, market: JPXIndex) -> None:
        """is_trading_hours() without argument during closed period."""
        # During gap period
        mock_now = datetime(2026, 2, 6, 16, 30, tzinfo=ZoneInfo("Asia/Tokyo"))
        with patch("marketsched.jpx.index.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now
            assert market.is_trading_hours() is False

    def test_is_trading_hours_on_weekend_documents_behavior(
        self, market: JPXIndex
    ) -> None:
        """Document behavior: is_trading_hours() checks time only, not business day.

        This test documents the current behavior where is_trading_hours()
        only checks if the time falls within trading hours, without considering
        whether it's a business day. Users should use is_business_day() separately
        if they need to check both conditions.
        """
        # Saturday during DAY session hours
        mock_now = datetime(2026, 2, 7, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        with patch("marketsched.jpx.index.datetime") as mock_datetime:
            mock_datetime.now.return_value = mock_now
            # Current behavior: returns True (time-based only)
            assert market.is_trading_hours() is True


class TestSessionBoundaries:
    """Test edge cases for session boundaries (US7)."""

    def test_night_session_end_boundary_06_00(self, market: JPXIndex) -> None:
        """06:00 exactly should be CLOSED (night session ends at 06:00)."""
        dt = datetime(2026, 2, 7, 6, 0, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.CLOSED

    def test_pre_market_gap_08_44(self, market: JPXIndex) -> None:
        """08:44 should be CLOSED (day session starts at 08:45)."""
        dt = datetime(2026, 2, 6, 8, 44, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.CLOSED

    def test_day_session_end_15_45(self, market: JPXIndex) -> None:
        """15:45 should be DAY session (inclusive end)."""
        dt = datetime(2026, 2, 6, 15, 45, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.DAY

    def test_inter_session_gap_15_46(self, market: JPXIndex) -> None:
        """15:46 should be CLOSED."""
        dt = datetime(2026, 2, 6, 15, 46, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.CLOSED

    def test_inter_session_gap_16_59(self, market: JPXIndex) -> None:
        """16:59 should be CLOSED."""
        dt = datetime(2026, 2, 6, 16, 59, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.CLOSED

    def test_night_session_start_17_00(self, market: JPXIndex) -> None:
        """17:00 should be NIGHT session start."""
        dt = datetime(2026, 2, 6, 17, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.NIGHT

    def test_night_session_05_59(self, market: JPXIndex) -> None:
        """05:59 should still be NIGHT session."""
        dt = datetime(2026, 2, 7, 5, 59, tzinfo=ZoneInfo("Asia/Tokyo"))
        assert market.get_session(dt) == TradingSession.NIGHT
