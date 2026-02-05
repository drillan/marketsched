"""High-level query interface for JPX cached data.

This module bridges ParquetCacheManager (low-level table I/O) with
domain-specific queries needed by JPXCalendar.

Example:
    >>> from marketsched.jpx.data.query import JPXDataQuery
    >>> query = JPXDataQuery()
    >>> sq = query.get_sq_date(2026, 3)
"""

from datetime import date

from marketsched.contract_month import ContractMonth
from marketsched.exceptions import CacheNotAvailableError
from marketsched.jpx.data import DataType
from marketsched.jpx.data.cache import ParquetCacheManager

__all__ = ["JPXDataQuery"]


class JPXDataQuery:
    """High-level query interface for JPX market data.

    Wraps ParquetCacheManager and provides domain-specific query methods
    for SQ dates and holiday trading data.

    Attributes:
        cache_manager: The underlying ParquetCacheManager instance.
    """

    def __init__(self, cache_manager: ParquetCacheManager | None = None) -> None:
        """Initialize the query interface.

        Args:
            cache_manager: Custom cache manager. Defaults to ParquetCacheManager().
        """
        self._cache_manager = (
            cache_manager if cache_manager is not None else ParquetCacheManager()
        )

    @property
    def cache_manager(self) -> ParquetCacheManager:
        """Return the underlying cache manager."""
        return self._cache_manager

    def _read_sq_dates(self) -> list[dict[str, object]]:
        """Read SQ dates from cache as list of dicts.

        Raises:
            CacheNotAvailableError: If SQ dates cache does not exist.
        """
        table = self._cache_manager.read(DataType.SQ_DATES)
        if table is None:
            raise CacheNotAvailableError(
                "SQ日データのキャッシュが存在しません。`mks cache update` を実行してください。"
            )
        result: list[dict[str, object]] = table.to_pylist()
        return result

    def _read_holidays(self) -> list[dict[str, object]]:
        """Read holiday trading data from cache as list of dicts.

        Raises:
            CacheNotAvailableError: If holiday trading cache does not exist.
        """
        table = self._cache_manager.read(DataType.HOLIDAY_TRADING)
        if table is None:
            raise CacheNotAvailableError(
                "休業日データのキャッシュが存在しません。`mks cache update` を実行してください。"
            )
        result: list[dict[str, object]] = table.to_pylist()
        return result

    def get_sq_date(self, year: int, month: int) -> date | None:
        """Get SQ date for a specific year and month.

        Args:
            year: Year.
            month: Month (1-12).

        Returns:
            SQ date, or None if not found for the given year/month.

        Raises:
            CacheNotAvailableError: If cache does not exist.
        """
        records = self._read_sq_dates()
        target = ContractMonth(year=year, month=month).to_yyyymm()
        for record in records:
            if record["contract_month"] == target:
                sq_date: date = record["sq_date"]  # type: ignore[assignment]
                return sq_date
        return None

    def get_sq_dates_for_year(self, year: int) -> list[date]:
        """Get all SQ dates for a year.

        Args:
            year: Year.

        Returns:
            List of SQ dates in ascending order.

        Raises:
            CacheNotAvailableError: If cache does not exist.
        """
        records = self._read_sq_dates()
        year_prefix = str(year)
        dates: list[date] = [
            record["sq_date"]  # type: ignore[misc]
            for record in records
            if str(record["contract_month"]).startswith(year_prefix)
        ]
        return sorted(dates)

    def is_holiday_trading_day(self, d: date) -> bool:
        """Check if a date is a holiday trading day.

        Args:
            d: Date to check.

        Returns:
            True if the date is a holiday with trading enabled.

        Raises:
            CacheNotAvailableError: If cache does not exist.
        """
        records = self._read_holidays()
        return any(record["date"] == d and record["is_trading"] for record in records)

    def get_non_trading_holidays(self) -> set[date]:
        """Get set of non-trading holiday dates.

        Returns:
            Set of dates that are holidays without trading.

        Raises:
            CacheNotAvailableError: If cache does not exist.
        """
        records = self._read_holidays()
        return {
            record["date"]  # type: ignore[misc]
            for record in records
            if not record["is_trading"]
        }
