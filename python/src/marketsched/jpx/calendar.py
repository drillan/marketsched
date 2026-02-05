"""JPX calendar logic for business day and SQ date determination.

This module provides calendar logic for JPX markets, including:
- Business day determination (weekends, holidays, holiday trading days)
- SQ date lookup from cache

All holiday data is loaded from the cache (Parquet files), following
the Constitution rule that holiday dates must not be hardcoded.
"""

from datetime import date, timedelta

from marketsched.exceptions import SQDataNotFoundError
from marketsched.jpx.data.query import JPXDataQuery

# Maximum days to search for next/previous business day
# Prevents infinite loops in case of corrupted cache data
MAX_SEARCH_DAYS = 365


class JPXCalendar:
    """Calendar logic for JPX markets.

    Provides business day determination and SQ date lookup.

    Attributes:
        data_query: JPXDataQuery instance for data access.
    """

    def __init__(self, data_query: JPXDataQuery | None = None) -> None:
        """Initialize the calendar.

        Args:
            data_query: Custom data query instance. Defaults to JPXDataQuery().
        """
        self._data_query = data_query if data_query is not None else JPXDataQuery()

    @property
    def data_query(self) -> JPXDataQuery:
        """Get the data query instance."""
        return self._data_query

    def _is_weekend(self, d: date) -> bool:
        """Check if date is a weekend.

        Args:
            d: Date to check.

        Returns:
            True if Saturday or Sunday.
        """
        return d.weekday() >= 5  # 5 = Saturday, 6 = Sunday

    def is_business_day(self, d: date) -> bool:
        """Check if the given date is a business day.

        A date is a business day if:
        1. It's not a weekend (Saturday or Sunday)
        2. It's not a non-trading holiday

        Holiday trading days (祝日取引実施日) are considered business days.

        Args:
            d: Date to check.

        Returns:
            True if the date is a business day.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        # Weekends are not business days
        if self._is_weekend(d):
            return False

        # Check if it's a holiday trading day (special trading on holidays)
        if self._data_query.is_holiday_trading_day(d):
            return True

        # Check if it's a non-trading holiday
        non_trading_holidays = self._data_query.get_non_trading_holidays()
        return d not in non_trading_holidays

    def next_business_day(self, d: date) -> date:
        """Get the next business day after the given date.

        Args:
            d: Starting date (exclusive).

        Returns:
            The next business day.

        Raises:
            CacheNotAvailableError: If cache is not available.
            RuntimeError: If no business day found within MAX_SEARCH_DAYS.
        """
        current = d + timedelta(days=1)
        for _ in range(MAX_SEARCH_DAYS):
            if self.is_business_day(current):
                return current
            current += timedelta(days=1)
        raise RuntimeError(f"{d} から {MAX_SEARCH_DAYS} 日以内に営業日が見つかりません")

    def previous_business_day(self, d: date) -> date:
        """Get the previous business day before the given date.

        Args:
            d: Starting date (exclusive).

        Returns:
            The previous business day.

        Raises:
            CacheNotAvailableError: If cache is not available.
            RuntimeError: If no business day found within MAX_SEARCH_DAYS.
        """
        current = d - timedelta(days=1)
        for _ in range(MAX_SEARCH_DAYS):
            if self.is_business_day(current):
                return current
            current -= timedelta(days=1)
        raise RuntimeError(f"{d} から {MAX_SEARCH_DAYS} 日以内に営業日が見つかりません")

    def get_business_days(self, start: date, end: date) -> list[date]:
        """Get all business days in the given range.

        Args:
            start: Start date (inclusive).
            end: End date (inclusive).

        Returns:
            List of business days in ascending order.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        if start > end:
            return []

        result = []
        current = start
        while current <= end:
            if self.is_business_day(current):
                result.append(current)
            current += timedelta(days=1)
        return result

    def count_business_days(self, start: date, end: date) -> int:
        """Count business days in the given range.

        Args:
            start: Start date (inclusive).
            end: End date (inclusive).

        Returns:
            Number of business days.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        return len(self.get_business_days(start, end))

    def get_sq_date(self, year: int, month: int) -> date:
        """Get the SQ date for the given year and month.

        Args:
            year: Year.
            month: Month (1-12).

        Returns:
            SQ date.

        Raises:
            SQDataNotFoundError: If SQ data is not available.
            CacheNotAvailableError: If cache is not available.
        """
        result = self._data_query.get_sq_date(year, month)
        if result is None:
            raise SQDataNotFoundError(year, month)
        return result

    def is_sq_date(self, d: date) -> bool:
        """Check if the given date is an SQ date.

        Args:
            d: Date to check.

        Returns:
            True if the date is an SQ date.

        Raises:
            SQDataNotFoundError: If SQ data is not available for the period.
            CacheNotAvailableError: If cache is not available.
        """
        sq_date = self.get_sq_date(d.year, d.month)
        return sq_date == d

    def get_sq_dates_for_year(self, year: int) -> list[date]:
        """Get all SQ dates for the given year.

        Args:
            year: Year.

        Returns:
            List of SQ dates in ascending order.

        Raises:
            SQDataNotFoundError: If no SQ data is available for the year.
            CacheNotAvailableError: If cache is not available.
        """
        dates = self._data_query.get_sq_dates_for_year(year)
        if not dates:
            raise SQDataNotFoundError(year, 1)
        return dates
