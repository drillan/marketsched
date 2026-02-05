"""Data models for JPX cache management.

This module provides Pydantic models for cache metadata and data records.
All models are immutable (frozen=True) for hashability and to prevent
accidental modification.

Example:
    >>> from marketsched.jpx.data import CacheMetadata, DataType, SQDateRecord
    >>> from datetime import datetime, timedelta, timezone
    >>> now = datetime.now(timezone.utc)
    >>> metadata = CacheMetadata(
    ...     data_type=DataType.SQ_DATES,
    ...     source_url="https://example.com/data.xlsx",
    ...     fetched_at=now,
    ...     expires_at=now + timedelta(hours=24),
    ...     schema_version=1,
    ...     record_count=100,
    ... )
"""

from datetime import date
from enum import StrEnum
from typing import Self

from pydantic import AwareDatetime, BaseModel, ConfigDict, model_validator

from marketsched.contract_month import ContractMonth

__all__ = [
    "DataType",
    "CacheMetadata",
    "CacheInfo",
    "SQDateRecord",
    "HolidayTradingRecord",
]


class DataType(StrEnum):
    """Cache data type identifiers."""

    SQ_DATES = "sq_dates"
    HOLIDAY_TRADING = "holiday_trading"


class CacheMetadata(BaseModel):
    """Metadata for a cached Parquet file.

    This model stores information about when data was fetched, its expiration,
    and schema version for validation.

    Attributes:
        data_type: Type identifier for the cached data.
        source_url: URL(s) from which the data was fetched.
        fetched_at: Timestamp when data was fetched (must be timezone-aware).
        expires_at: Timestamp when cache expires (must be timezone-aware).
        schema_version: Version of the data schema for compatibility checks.
        record_count: Number of records in the cached data.
    """

    model_config = ConfigDict(frozen=True)

    data_type: DataType
    source_url: str
    fetched_at: AwareDatetime
    expires_at: AwareDatetime
    schema_version: int
    record_count: int

    @model_validator(mode="after")
    def validate_metadata(self) -> Self:
        """Validate metadata constraints."""
        if self.expires_at <= self.fetched_at:
            msg = "expires_at must be after fetched_at"
            raise ValueError(msg)
        if self.record_count < 0:
            msg = "record_count must be non-negative"
            raise ValueError(msg)
        if self.schema_version < 1:
            msg = "schema_version must be >= 1"
            raise ValueError(msg)
        return self


class CacheInfo(BaseModel):
    """User-facing cache status information.

    This model provides a simplified view of cache state for users
    and CLI output.

    Attributes:
        data_type: Type identifier for the cached data.
        cache_path: File system path to the cache file.
        is_valid: Whether the cache is within its validity period.
        fetched_at: Timestamp when data was fetched (None if no cache exists).
        expires_at: Timestamp when cache expires (None if no cache exists).
        record_count: Number of records in the cache (None if no cache exists).
    """

    model_config = ConfigDict(frozen=True)

    data_type: DataType
    cache_path: str
    is_valid: bool
    fetched_at: AwareDatetime | None
    expires_at: AwareDatetime | None
    record_count: int | None

    @model_validator(mode="after")
    def validate_consistency(self) -> Self:
        """Ensure is_valid=True implies all optional fields are non-None."""
        if self.is_valid and (
            self.fetched_at is None
            or self.expires_at is None
            or self.record_count is None
        ):
            msg = "is_valid=True requires fetched_at, expires_at, and record_count to be set"
            raise ValueError(msg)
        return self


class SQDateRecord(BaseModel):
    """A record representing SQ (Special Quotation) date information.

    SQ (Special Quotation) is the reference price used for final settlement
    of index futures and options contracts. This record stores the exercise
    date parsed from JPX official data for 日経225オプション rows.

    Attributes:
        contract_month: Contract month as a ContractMonth value object.
        last_trading_day: Last trading day before SQ.
        sq_date: The SQ date (exercise date for options).
        product_category: Product category identifier (e.g., "index_futures_options").
    """

    model_config = ConfigDict(frozen=True)

    contract_month: ContractMonth
    last_trading_day: date
    sq_date: date
    product_category: str


class HolidayTradingRecord(BaseModel):
    """A record representing holiday trading status.

    Some Japanese holidays have special trading sessions.
    This model tracks which holidays have trading enabled.

    Attributes:
        date: The holiday date.
        holiday_name: Name of the holiday in Japanese.
        is_trading: Whether trading is available on this holiday.
        is_confirmed: Whether this trading status is confirmed (vs. tentative).
    """

    model_config = ConfigDict(frozen=True)

    date: date
    holiday_name: str
    is_trading: bool
    is_confirmed: bool
