"""JPX Index Futures & Options market implementation.

This module provides the JPXIndex class which implements the Market Protocol
for JPX index derivatives (Nikkei 225 futures/options, TOPIX futures, etc.).
"""

from datetime import date, datetime
from zoneinfo import ZoneInfo

from marketsched.exceptions import TimezoneRequiredError
from marketsched.jpx.calendar import JPXCalendar, get_calendar
from marketsched.jpx.session import JPXIndexSessionTimes
from marketsched.registry import MarketRegistry
from marketsched.session import TradingSession


@MarketRegistry.register("jpx-index")
class JPXIndex:
    """JPX Index Futures & Options market implementation.

    This class implements the Market Protocol for JPX index derivatives.
    It provides business day determination, SQ date lookup, and trading
    session information based on JPX official data.

    Attributes:
        market_id: "jpx-index"
        name: "JPX Index Futures & Options"
        timezone: Asia/Tokyo (JST)

    Example:
        >>> import marketsched
        >>> market = marketsched.get_market("jpx-index")
        >>> market.is_business_day(date(2026, 2, 6))
        True
    """

    _MARKET_ID = "jpx-index"
    _NAME = "JPX Index Futures & Options"
    _TIMEZONE = ZoneInfo("Asia/Tokyo")

    def __init__(self, calendar: JPXCalendar | None = None) -> None:
        """Initialize JPXIndex.

        Args:
            calendar: Custom calendar instance for testing.
                     If None, uses the global calendar.
        """
        self._calendar = calendar

    @property
    def _cal(self) -> JPXCalendar:
        """Get the calendar instance."""
        if self._calendar is None:
            self._calendar = get_calendar()
        return self._calendar

    @property
    def market_id(self) -> str:
        """Return the unique market identifier."""
        return self._MARKET_ID

    @property
    def name(self) -> str:
        """Return the human-readable market name."""
        return self._NAME

    @property
    def timezone(self) -> ZoneInfo:
        """Return the market's native timezone (Asia/Tokyo)."""
        return self._TIMEZONE

    # Business day methods

    def is_business_day(self, d: date) -> bool:
        """Check if the given date is a business day.

        A date is a business day if:
        - It's not a weekend (Saturday or Sunday)
        - It's not a JPX official holiday
        - OR it's a holiday trading day (special trading on holidays)

        Args:
            d: The date to check.

        Returns:
            True if the date is a business day, False otherwise.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        return self._cal.is_business_day(d)

    def next_business_day(self, d: date) -> date:
        """Get the next business day after the given date.

        Args:
            d: The starting date (exclusive).

        Returns:
            The next business day after the given date.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        return self._cal.next_business_day(d)

    def previous_business_day(self, d: date) -> date:
        """Get the previous business day before the given date.

        Args:
            d: The starting date (exclusive).

        Returns:
            The previous business day before the given date.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        return self._cal.previous_business_day(d)

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
        return self._cal.get_business_days(start, end)

    def count_business_days(self, start: date, end: date) -> int:
        """Count business days in the given range.

        Args:
            start: Start date (inclusive).
            end: End date (inclusive).

        Returns:
            Number of business days in the range.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        return self._cal.count_business_days(start, end)

    # SQ date methods

    def get_sq_date(self, year: int, month: int) -> date:
        """Get the SQ date for the given year and month.

        SQ (Special Quotation) is the final settlement price for index
        derivatives, determined on the second Friday of each month.

        Args:
            year: The year.
            month: The month (1-12).

        Returns:
            The SQ date.

        Raises:
            SQDataNotFoundError: If SQ data is not available for the period.
            CacheNotAvailableError: If cache is not available.
        """
        return self._cal.get_sq_date(year, month)

    def is_sq_date(self, d: date) -> bool:
        """Check if the given date is an SQ date.

        Args:
            d: The date to check.

        Returns:
            True if the date is an SQ date, False otherwise.
            Returns False for dates outside the available SQ data range.

        Raises:
            CacheNotAvailableError: If cache is not available.
        """
        return self._cal.is_sq_date(d)

    def get_sq_dates_for_year(self, year: int) -> list[date]:
        """Get all SQ dates for the given year.

        Args:
            year: The year.

        Returns:
            List of SQ dates for the year in ascending order.

        Raises:
            SQDataNotFoundError: If SQ data is not available for the year.
            CacheNotAvailableError: If cache is not available.
        """
        return self._cal.get_sq_dates_for_year(year)

    # Trading session methods

    def _validate_timezone(self, dt: datetime) -> None:
        """Validate that datetime has timezone info.

        Args:
            dt: The datetime to validate.

        Raises:
            TimezoneRequiredError: If dt is naive (no timezone).
        """
        if dt.tzinfo is None:
            raise TimezoneRequiredError()

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
        if dt is None:
            dt = datetime.now(self._TIMEZONE)
        else:
            self._validate_timezone(dt)
            # Convert to market timezone
            dt = dt.astimezone(self._TIMEZONE)

        t = dt.time()

        # Check day session (08:45 - 15:45)
        if JPXIndexSessionTimes.is_day_session(t):
            return TradingSession.DAY

        # Check night session (17:00 - 06:00 next day)
        if JPXIndexSessionTimes.is_night_session(t):
            return TradingSession.NIGHT

        return TradingSession.CLOSED

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
        session = self.get_session(dt)
        return session != TradingSession.CLOSED
