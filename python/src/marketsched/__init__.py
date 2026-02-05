"""marketsched: Market calendar, SQ dates, and trading hours management.

This package provides tools for managing market calendars, SQ dates,
and trading hours for Japanese financial markets.

Example:
    Once market implementations are registered, you can use them like this::

        >>> from datetime import date
        >>> import marketsched
        >>> market = marketsched.get_market("jpx-index")  # requires jpx-index impl
        >>> market.is_business_day(date(2026, 2, 6))
        True
"""

from marketsched.contract_month import ContractMonth
from marketsched.exceptions import (
    CacheNotAvailableError,
    ContractMonthParseError,
    DataFetchError,
    InvalidDataFormatError,
    MarketAlreadyRegisteredError,
    MarketNotFoundError,
    MarketschedError,
    MarketshedError,  # Backwards compatibility alias
    SQDataNotFoundError,
    SQNotSupportedError,
    TimezoneRequiredError,
)
from marketsched.market import Market
from marketsched.registry import MarketRegistry
from marketsched.session import TradingSession

__version__ = "0.0.1"

__all__ = [
    # Core types
    "Market",
    "ContractMonth",
    "TradingSession",
    # Functions
    "get_market",
    "get_available_markets",
    # Exceptions
    "MarketschedError",
    "MarketshedError",  # Backwards compatibility alias
    "MarketNotFoundError",
    "MarketAlreadyRegisteredError",
    "ContractMonthParseError",
    "SQDataNotFoundError",
    "SQNotSupportedError",
    "TimezoneRequiredError",
    "CacheNotAvailableError",
    "DataFetchError",
    "InvalidDataFormatError",
]


def get_market(market_id: str) -> Market:
    """Get a market instance by ID.

    Args:
        market_id: The market identifier (e.g., 'jpx-index').

    Returns:
        An instance of the requested market.

    Raises:
        MarketNotFoundError: If no market is registered with the given ID.

    Example:
        >>> market = marketsched.get_market("jpx-index")
        >>> market.name
        'JPX Index Futures & Options'
    """
    return MarketRegistry.get(market_id)


def get_available_markets() -> list[str]:
    """Get list of all available market IDs.

    Returns:
        List of market IDs in sorted order.

    Example:
        >>> marketsched.get_available_markets()
        ['jpx-index']
    """
    return MarketRegistry.get_available_markets()
