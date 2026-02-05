"""Market registry for registering and retrieving market implementations.

This module provides a centralized registry for market implementations.
Markets are registered using the @MarketRegistry.register() decorator.
"""

from collections.abc import Callable
from typing import TypeVar

from marketsched.exceptions import MarketNotFoundError
from marketsched.market import Market

# Type variable for market factory functions
M = TypeVar("M", bound=Market)


class MarketRegistry:
    """Registry for market implementations.

    Markets can be registered using the class method decorator:

        @MarketRegistry.register("jpx-index")
        class JPXIndex:
            ...

    And retrieved using:

        market = MarketRegistry.get("jpx-index")
    """

    _markets: dict[str, type[Market]] = {}

    @classmethod
    def register(cls, market_id: str) -> Callable[[type[M]], type[M]]:
        """Register a market implementation with the given ID.

        Args:
            market_id: Unique identifier for the market.

        Returns:
            Decorator that registers the market class.

        Example:
            @MarketRegistry.register("jpx-index")
            class JPXIndex:
                ...
        """

        def decorator(market_class: type[M]) -> type[M]:
            cls._markets[market_id] = market_class
            return market_class

        return decorator

    @classmethod
    def get(cls, market_id: str) -> Market:
        """Get a market instance by ID.

        Args:
            market_id: The market identifier.

        Returns:
            An instance of the requested market.

        Raises:
            MarketNotFoundError: If no market is registered with the given ID.
        """
        if market_id not in cls._markets:
            raise MarketNotFoundError(market_id)
        return cls._markets[market_id]()

    @classmethod
    def get_available_markets(cls) -> list[str]:
        """Get list of all registered market IDs.

        Returns:
            List of market IDs in sorted order.
        """
        return sorted(cls._markets.keys())

    @classmethod
    def clear(cls) -> None:
        """Clear all registered markets. Primarily for testing."""
        cls._markets.clear()
