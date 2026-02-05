"""Unit tests for cache-related Pydantic models (T023)."""

from datetime import UTC, date, datetime, timedelta
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from marketsched.contract_month import ContractMonth
from marketsched.jpx.data import (
    CacheInfo,
    CacheMetadata,
    DataType,
    HolidayTradingRecord,
    SQDateRecord,
)


class TestCacheMetadata:
    """Tests for CacheMetadata model."""

    def test_create_valid_metadata(self, utc: ZoneInfo) -> None:
        """Can create valid CacheMetadata with all required fields."""
        now = datetime.now(utc)
        expires = now + timedelta(hours=24)

        metadata = CacheMetadata(
            data_type=DataType.SQ_DATES,
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=expires,
            schema_version=1,
            record_count=100,
        )

        assert metadata.data_type == DataType.SQ_DATES
        assert metadata.source_url == "https://example.com/data.xlsx"
        assert metadata.fetched_at == now
        assert metadata.expires_at == expires
        assert metadata.schema_version == 1
        assert metadata.record_count == 100

    def test_frozen_model_is_immutable(self, utc: ZoneInfo) -> None:
        """CacheMetadata is immutable (frozen=True)."""
        now = datetime.now(utc)
        metadata = CacheMetadata(
            data_type=DataType.SQ_DATES,
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=now + timedelta(hours=24),
            schema_version=1,
            record_count=100,
        )

        with pytest.raises(ValidationError):
            metadata.data_type = DataType.HOLIDAY_TRADING  # type: ignore[misc]

    def test_requires_aware_datetime_for_fetched_at(self) -> None:
        """Rejects naive datetime for fetched_at."""
        naive_dt = datetime(2026, 2, 6, 10, 0, 0)  # No tzinfo

        with pytest.raises(ValidationError) as exc_info:
            CacheMetadata(
                data_type=DataType.SQ_DATES,
                source_url="https://example.com/data.xlsx",
                fetched_at=naive_dt,
                expires_at=datetime.now(UTC) + timedelta(hours=24),
                schema_version=1,
                record_count=100,
            )

        assert "fetched_at" in str(exc_info.value)

    def test_requires_aware_datetime_for_expires_at(self) -> None:
        """Rejects naive datetime for expires_at."""
        naive_dt = datetime(2026, 2, 6, 10, 0, 0)  # No tzinfo

        with pytest.raises(ValidationError) as exc_info:
            CacheMetadata(
                data_type=DataType.SQ_DATES,
                source_url="https://example.com/data.xlsx",
                fetched_at=datetime.now(UTC),
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
            data_type=DataType.SQ_DATES,
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=expires,
            schema_version=1,
            record_count=100,
        )

        json_str = original.model_dump_json()
        restored = CacheMetadata.model_validate_json(json_str)

        assert restored == original

    def test_rejects_expires_at_before_fetched_at(self, utc: ZoneInfo) -> None:
        """Rejects expires_at that is before or equal to fetched_at."""
        now = datetime.now(utc)

        with pytest.raises(ValidationError, match="expires_at must be after"):
            CacheMetadata(
                data_type=DataType.SQ_DATES,
                source_url="https://example.com/data.xlsx",
                fetched_at=now,
                expires_at=now - timedelta(hours=1),
                schema_version=1,
                record_count=100,
            )

    def test_rejects_negative_record_count(self, utc: ZoneInfo) -> None:
        """Rejects negative record_count."""
        now = datetime.now(utc)

        with pytest.raises(ValidationError, match="record_count must be non-negative"):
            CacheMetadata(
                data_type=DataType.SQ_DATES,
                source_url="https://example.com/data.xlsx",
                fetched_at=now,
                expires_at=now + timedelta(hours=24),
                schema_version=1,
                record_count=-1,
            )

    def test_rejects_zero_schema_version(self, utc: ZoneInfo) -> None:
        """Rejects schema_version < 1."""
        now = datetime.now(utc)

        with pytest.raises(ValidationError, match="schema_version must be >= 1"):
            CacheMetadata(
                data_type=DataType.SQ_DATES,
                source_url="https://example.com/data.xlsx",
                fetched_at=now,
                expires_at=now + timedelta(hours=24),
                schema_version=0,
                record_count=100,
            )

    def test_data_type_is_enum(self, utc: ZoneInfo) -> None:
        """data_type accepts DataType enum and string values."""
        now = datetime.now(utc)
        metadata = CacheMetadata(
            data_type=DataType.SQ_DATES,
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=now + timedelta(hours=24),
            schema_version=1,
            record_count=100,
        )
        # StrEnum is comparable to string
        assert metadata.data_type == "sq_dates"
        assert metadata.data_type == DataType.SQ_DATES


class TestCacheInfo:
    """Tests for CacheInfo model."""

    def test_create_valid_cache_info(self, utc: ZoneInfo) -> None:
        """Can create valid CacheInfo with all fields."""
        now = datetime.now(utc)
        expires = now + timedelta(hours=24)

        info = CacheInfo(
            data_type=DataType.SQ_DATES,
            cache_path="/home/user/.cache/marketsched/sq_dates.parquet",
            is_valid=True,
            fetched_at=now,
            expires_at=expires,
            record_count=100,
        )

        assert info.data_type == DataType.SQ_DATES
        assert info.is_valid is True
        assert info.record_count == 100

    def test_optional_fields_can_be_none(self) -> None:
        """Optional fields (fetched_at, expires_at, record_count) can be None when invalid."""
        info = CacheInfo(
            data_type=DataType.SQ_DATES,
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
        now = datetime.now(utc)
        info = CacheInfo(
            data_type=DataType.SQ_DATES,
            cache_path="/home/user/.cache/marketsched/sq_dates.parquet",
            is_valid=True,
            fetched_at=now,
            expires_at=now + timedelta(hours=24),
            record_count=100,
        )

        with pytest.raises(ValidationError):
            info.is_valid = False  # type: ignore[misc]

    def test_rejects_valid_with_none_fields(self, utc: ZoneInfo) -> None:
        """is_valid=True requires all optional fields to be non-None."""
        with pytest.raises(ValidationError, match="is_valid=True requires"):
            CacheInfo(
                data_type=DataType.SQ_DATES,
                cache_path="/home/user/.cache/marketsched/sq_dates.parquet",
                is_valid=True,
                fetched_at=None,
                expires_at=None,
                record_count=None,
            )


class TestSQDateRecord:
    """Tests for SQDateRecord model."""

    def test_create_valid_sq_date_record(self) -> None:
        """Can create valid SQDateRecord."""
        cm = ContractMonth(year=2026, month=3)
        record = SQDateRecord(
            contract_month=cm,
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )

        assert record.contract_month == cm
        assert record.contract_month.to_yyyymm() == "202603"
        assert record.last_trading_day == date(2026, 3, 12)
        assert record.sq_date == date(2026, 3, 13)
        assert record.product_category == "index_futures_options"

    def test_frozen_model_is_immutable(self) -> None:
        """SQDateRecord is immutable (frozen=True)."""
        record = SQDateRecord(
            contract_month=ContractMonth(year=2026, month=3),
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )

        with pytest.raises(ValidationError):
            record.sq_date = date(2026, 3, 14)  # type: ignore[misc]

    def test_hashable_for_set_usage(self) -> None:
        """SQDateRecord is hashable and can be used in sets."""
        record1 = SQDateRecord(
            contract_month=ContractMonth(year=2026, month=3),
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )
        record2 = SQDateRecord(
            contract_month=ContractMonth(year=2026, month=3),
            last_trading_day=date(2026, 3, 12),
            sq_date=date(2026, 3, 13),
            product_category="index_futures_options",
        )
        record3 = SQDateRecord(
            contract_month=ContractMonth(year=2026, month=4),
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
