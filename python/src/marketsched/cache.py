"""Public cache API for marketsched.

This module provides user-facing functions for managing the data cache.
It handles fetching data from JPX and storing it locally in Parquet format.

Example:
    >>> import marketsched
    >>> # Update cache
    >>> marketsched.update_cache()
    >>> # Check cache status
    >>> status = marketsched.get_cache_status()
    >>> print(status)
    >>> # Clear cache
    >>> marketsched.clear_cache()
"""

from datetime import datetime, timezone

import pyarrow as pa

from marketsched.jpx.data import (
    CacheInfo,
    CacheMetadata,
    HolidayTradingRecord,
    SQDateRecord,
)
from marketsched.jpx.data.cache import ParquetCacheManager
from marketsched.jpx.data.fetcher import JPXDataFetcher

__all__ = [
    "update_cache",
    "clear_cache",
    "get_cache_status",
]

# Cache data types
CACHE_TYPES = ["sq_dates", "holiday_trading"]

# Default years to fetch for SQ dates
DEFAULT_YEARS = [2026, 2027]


def _get_cache_manager() -> ParquetCacheManager:
    """Get a cache manager instance."""
    return ParquetCacheManager()


def _get_fetcher() -> JPXDataFetcher:
    """Get a fetcher instance."""
    return JPXDataFetcher()


def _sq_records_to_table(records: list[SQDateRecord]) -> pa.Table:
    """Convert SQ date records to PyArrow Table."""
    return pa.table(
        {
            "contract_month": [r.contract_month for r in records],
            "last_trading_day": [r.last_trading_day for r in records],
            "sq_date": [r.sq_date for r in records],
            "product_category": [r.product_category for r in records],
        }
    )


def _holiday_records_to_table(records: list[HolidayTradingRecord]) -> pa.Table:
    """Convert holiday trading records to PyArrow Table."""
    return pa.table(
        {
            "date": [r.date for r in records],
            "holiday_name": [r.holiday_name for r in records],
            "is_trading": [r.is_trading for r in records],
            "is_confirmed": [r.is_confirmed for r in records],
        }
    )


def update_cache(
    force: bool = False,
    years: list[int] | None = None,
) -> dict[str, CacheInfo]:
    """Update the cache by fetching data from JPX.

    This function downloads the latest data from JPX official website
    and stores it in the local cache.

    Args:
        force: If True, update even if cache is still valid.
        years: Years to fetch SQ date data for. Defaults to [2026, 2027].

    Returns:
        Dictionary mapping cache type to CacheInfo.

    Raises:
        DataFetchError: If network request fails.
        InvalidDataFormatError: If data format is unexpected.

    Example:
        >>> result = update_cache()
        >>> print(result["sq_dates"].record_count)
    """
    cache_manager = _get_cache_manager()
    fetcher = _get_fetcher()
    years = years or DEFAULT_YEARS

    now = datetime.now(timezone.utc)
    expires_at = now + cache_manager.expiry

    # Update SQ dates if needed
    if force or not cache_manager.is_valid("sq_dates"):
        sq_records = fetcher.fetch_sq_dates(years=years)
        sq_table = _sq_records_to_table(sq_records)

        sq_metadata = CacheMetadata(
            data_type="sq_dates",
            source_url=fetcher.BASE_URL + fetcher.SQ_DATES_PATH.format(year=years[0]),
            fetched_at=now,
            expires_at=expires_at,
            schema_version=1,
            record_count=len(sq_records),
        )
        cache_manager.write("sq_dates", sq_table, sq_metadata)

    # Update holiday trading if needed
    if force or not cache_manager.is_valid("holiday_trading"):
        holiday_records = fetcher.fetch_holiday_trading()
        holiday_table = _holiday_records_to_table(holiday_records)

        holiday_metadata = CacheMetadata(
            data_type="holiday_trading",
            source_url=fetcher.HOLIDAY_TRADING_URL,
            fetched_at=now,
            expires_at=expires_at,
            schema_version=1,
            record_count=len(holiday_records),
        )
        cache_manager.write("holiday_trading", holiday_table, holiday_metadata)

    return get_cache_status()


def clear_cache(data_type: str | None = None) -> None:
    """Clear the cache.

    Args:
        data_type: Specific cache type to clear ("sq_dates" or "holiday_trading").
                   If None, clears all caches.

    Example:
        >>> clear_cache()  # Clear all
        >>> clear_cache("sq_dates")  # Clear only SQ dates
    """
    cache_manager = _get_cache_manager()
    cache_manager.clear(data_type)


def get_cache_status() -> dict[str, CacheInfo]:
    """Get the status of all caches.

    Returns:
        Dictionary mapping cache type ("sq_dates", "holiday_trading") to CacheInfo.

    Example:
        >>> status = get_cache_status()
        >>> if not status["sq_dates"].is_valid:
        ...     update_cache()
    """
    cache_manager = _get_cache_manager()
    return {data_type: cache_manager.get_info(data_type) for data_type in CACHE_TYPES}
