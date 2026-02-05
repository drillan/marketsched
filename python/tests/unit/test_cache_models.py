"""Unit tests for cache-related Pydantic models (T023)."""

from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from marketsched.jpx.data import (
    CacheInfo,
    CacheMetadata,
    HolidayTradingRecord,
    SQDateRecord,
)


class TestCacheMetadata:
    """Tests for CacheMetadata model."""

    def test_create_valid_metadata(self, utc: ZoneInfo) -> None:
        """Can create valid CacheMetadata with all required fields."""
        now = datetime.now(utc)
        expires = datetime(2026, 2, 7, 0, 0, 0, tzinfo=utc)

        metadata = CacheMetadata(
            data_type="sq_dates",
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=expires,
            schema_version=1,
            record_count=100,
        )

        assert metadata.data_type == "sq_dates"
        assert metadata.source_url == "https://example.com/data.xlsx"
        assert metadata.fetched_at == now
        assert metadata.expires_at == expires
        assert metadata.schema_version == 1
        assert metadata.record_count == 100

    def test_frozen_model_is_immutable(self, utc: ZoneInfo) -> None:
        """CacheMetadata is immutable (frozen=True)."""
        now = datetime.now(utc)
        metadata = CacheMetadata(
            data_type="sq_dates",
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=now,
            schema_version=1,
            record_count=100,
        )

        with pytest.raises(ValidationError):
            metadata.data_type = "holiday_trading"  # type: ignore[misc]

    def test_requires_aware_datetime_for_fetched_at(self) -> None:
        """Rejects naive datetime for fetched_at."""
        naive_dt = datetime(2026, 2, 6, 10, 0, 0)  # No tzinfo

        with pytest.raises(ValidationError) as exc_info:
            CacheMetadata(
                data_type="sq_dates",
                source_url="https://example.com/data.xlsx",
                fetched_at=naive_dt,
                expires_at=datetime.now(timezone.utc),
                schema_version=1,
                record_count=100,
            )

        assert "fetched_at" in str(exc_info.value)

    def test_requires_aware_datetime_for_expires_at(self) -> None:
        """Rejects naive datetime for expires_at."""
        naive_dt = datetime(2026, 2, 6, 10, 0, 0)  # No tzinfo

        with pytest.raises(ValidationError) as exc_info:
            CacheMetadata(
                data_type="sq_dates",
                source_url="https://example.com/data.xlsx",
                fetched_at=datetime.now(timezone.utc),
                expires_at=naive_dt,
                schema_version=1,
                record_count=100,
            )

        assert "expires_at" in str(exc_info.value)

    def test_json_serialization_roundtrip(self, utc: ZoneInfo) -> None:
        """CacheMetadata can be serialized to JSON and back."""
        now = datetime(2026, 2, 6, 10, 0, 0, tzinfo=utc)
        expires = datetime(2026, 2, 7, 10, 0, 0, tzinfo=utc)

        original = CacheMetadata(
            data_type="sq_dates",
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=expires,
            schema_version=1,
            record_count=100,
        )

        json_str = original.model_dump_json()
        restored = CacheMetadata.model_validate_json(json_str)

        assert restored == original


class TestCacheInfo:
    """Tests for CacheInfo model."""

    def test_create_valid_cache_info(self, utc: ZoneInfo) -> None:
        """Can create valid CacheInfo with all fields."""
        now = datetime.now(utc)
        expires = datetime(2026, 2, 7, 0, 0, 0, tzinfo=utc)

        info = CacheInfo(
            data_type="sq_dates",
            cache_path="/home/user/.cache/marketsched/sq_dates.parquet",
            is_valid=True,
            fetched_at=now,
            expires_at=expires,
            record_count=100,
        )

        assert info.data_type == "sq_dates"
        assert info.is_valid is True
        assert info.record_count == 100

    def test_optional_fields_can_be_none(self) -> None:
        """Optional fields (fetched_at, expires_at, record_count) can be None."""
        info = CacheInfo(
            data_type="sq_dates",
            cache_path="/home/user/.cache/marketsched/sq_dates.parquet",
            is_valid=False,
            fetched_at=None,
            expires_at=None,
            record_count=None,
        )

        assert info.fetched_at is None
        assert info.expires_at is None
        assert info.record_count is None

    def test_frozen_model_is_immutable(self, utc: ZoneInfo) -> None:
        """CacheInfo is immutable (frozen=True)."""
        info = CacheInfo(
            data_type="sq_dates",
            cache_path="/home/user/.cache/marketsched/sq_dates.parquet",
            is_valid=True,
            fetched_at=datetime.now(utc),
            expires_at=datetime.now(utc),
            record_count=100,
        )

        with pytest.raises(ValidationError):
            info.is_valid = False  # type: ignore[misc]


class TestSQDateRecord:
    """Tests for SQDateRecord model."""

    def test_create_valid_sq_date_record(self) -> None:
        """Can create valid SQDateRecord."""
        record = SQDateRecord(
            contract_month="202603",
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )

        assert record.contract_month == "202603"
        assert record.last_trading_day == date(2026, 3, 12)
        assert record.sq_date == date(2026, 3, 13)
        assert record.product_category == "index_futures_options"

    def test_frozen_model_is_immutable(self) -> None:
        """SQDateRecord is immutable (frozen=True)."""
        record = SQDateRecord(
            contract_month="202603",
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )

        with pytest.raises(ValidationError):
            record.sq_date = date(2026, 3, 14)  # type: ignore[misc]

    def test_hashable_for_set_usage(self) -> None:
        """SQDateRecord is hashable and can be used in sets."""
        record1 = SQDateRecord(
            contract_month="202603",
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )
        record2 = SQDateRecord(
            contract_month="202603",
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )
        record3 = SQDateRecord(
            contract_month="202604",
            last_trading_day=date(2026, 4, 9),
            sq_date=date(2026, 4, 10),
            product_category="index_futures_options",
        )

        record_set = {record1, record2, record3}
        assert len(record_set) == 2  # record1 and record2 are equal


class TestHolidayTradingRecord:
    """Tests for HolidayTradingRecord model."""

    def test_create_valid_holiday_trading_record(self) -> None:
        """Can create valid HolidayTradingRecord."""
        record = HolidayTradingRecord(
            date=date(2026, 2, 11),
            holiday_name="建国記念の日",
            is_trading=True,
            is_confirmed=True,
        )

        assert record.date == date(2026, 2, 11)
        assert record.holiday_name == "建国記念の日"
        assert record.is_trading is True
        assert record.is_confirmed is True

    def test_frozen_model_is_immutable(self) -> None:
        """HolidayTradingRecord is immutable (frozen=True)."""
        record = HolidayTradingRecord(
            date=date(2026, 2, 11),
            holiday_name="建国記念の日",
            is_trading=True,
            is_confirmed=True,
        )

        with pytest.raises(ValidationError):
            record.is_trading = False  # type: ignore[misc]

    def test_non_trading_holiday(self) -> None:
        """Can represent a holiday with no trading."""
        record = HolidayTradingRecord(
            date=date(2026, 1, 1),
            holiday_name="元日",
            is_trading=False,
            is_confirmed=True,
        )

        assert record.is_trading is False
