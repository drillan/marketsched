"""Market Protocol definition for market abstraction.

This module defines the Market Protocol which all market implementations must satisfy.
Using Protocol (structural subtyping) instead of ABC allows market implementations
to satisfy the interface without explicit inheritance.
"""

from datetime import date, datetime
from typing import Protocol
from zoneinfo import ZoneInfo

from marketsched.session import TradingSession


class Market(Protocol):
    """Protocol defining the interface for all market implementations.

    Markets provide information about trading calendars, SQ dates, and session times.
    All methods dealing with datetime require timezone-aware datetimes.

    Attributes:
        market_id: Unique identifier for this market (e.g., 'jpx-index').
        name: Human-readable name (e.g., 'JPX Index Futures & Options').
        timezone: The market's native timezone.

    Example:
        >>> market = marketsched.get_market("jpx-index")
        >>> market.is_business_day(date(2026, 2, 6))
        True
    """

    @property
    def market_id(self) -> str:
        """Return the unique market identifier."""
        ...

    @property
    def name(self) -> str:
        """Return the human-readable market name."""
        ...

    @property
    def timezone(self) -> ZoneInfo:
        """Return the market's native timezone."""
        ...

    # Business day methods

    def is_business_day(self, d: date) -> bool:
        """Check if the given date is a business day.

        Args:
            d: The date to check.

        Returns:
            True if the date is a business day, False otherwise.
        """
        ...

    def next_business_day(self, d: date) -> date:
        """Get the next business day after the given date.

        Args:
            d: The starting date (exclusive).

        Returns:
            The next business day after the given date.
        """
        ...

    def previous_business_day(self, d: date) -> date:
        """Get the previous business day before the given date.

        Args:
            d: The starting date (exclusive).

        Returns:
            The previous business day before the given date.
        """
        ...

    def get_business_days(self, start: date, end: date) -> list[date]:
        """Get all business days in the given range.

        Args:
            start: Start date (inclusive).
            end: End date (inclusive).

        Returns:
            List of business days in ascending order.
        """
        ...

    def count_business_days(self, start: date, end: date) -> int:
        """Count business days in the given range.

        Args:
            start: Start date (inclusive).
            end: End date (inclusive).

        Returns:
            Number of business days in the range.
        """
        ...

    # SQ date methods

    def get_sq_date(self, year: int, month: int) -> date:
        """Get the SQ date for the given year and month.

        Args:
            year: The year.
            month: The month (1-12).

        Returns:
            The SQ date.

        Raises:
            SQDataNotFoundError: If SQ data is not available for the period.
            SQNotSupportedError: If the market doesn't support SQ dates.
        """
        ...

    def is_sq_date(self, d: date) -> bool:
        """Check if the given date is an SQ date.

        Args:
            d: The date to check.

        Returns:
            True if the date is an SQ date, False otherwise.
            Returns False for dates outside the available SQ data range.

        Raises:
            SQNotSupportedError: If the market doesn't support SQ dates.

        Note:
            For dates outside the available data range (typically far future
            or distant past), this method returns False rather than raising
            SQDataNotFoundError, since a non-SQ date is a valid answer.
            Use get_sq_date() if you need to verify data availability.
        """
        ...

    def get_sq_dates_for_year(self, year: int) -> list[date]:
        """Get all SQ dates for the given year.

        Args:
            year: The year.

        Returns:
            List of SQ dates for the year in ascending order.

        Raises:
            SQDataNotFoundError: If SQ data is not available for the year.
            SQNotSupportedError: If the market doesn't support SQ dates.
        """
        ...

    # Trading session methods

    def get_session(self, dt: datetime | None = None) -> TradingSession:
        """Get the trading session for the given datetime.

        Args:
            dt: The datetime to check. If None, uses current time.
                Must be timezone-aware.

        Returns:
            The trading session (DAY, NIGHT, or CLOSED).

        Raises:
            TimezoneRequiredError: If dt is naive (no timezone).
        """
        ...

    def is_trading_hours(self, dt: datetime | None = None) -> bool:
        """Check if the market is open at the given datetime.

        Args:
            dt: The datetime to check. If None, uses current time.
                Must be timezone-aware.

        Returns:
            True if trading is active, False otherwise.

        Raises:
            TimezoneRequiredError: If dt is naive (no timezone).
        """
        ...
