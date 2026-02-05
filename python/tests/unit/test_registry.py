"""Unit tests for MarketRegistry."""

from datetime import date, datetime
from zoneinfo import ZoneInfo

import pytest

from marketsched.exceptions import MarketAlreadyRegisteredError, MarketNotFoundError
from marketsched.registry import MarketRegistry
from marketsched.session import TradingSession


class MockMarket:
    """Mock market implementation for testing."""

    @property
    def market_id(self) -> str:
        return "mock-market"

    @property
    def name(self) -> str:
        return "Mock Market"

    @property
    def timezone(self) -> ZoneInfo:
        return ZoneInfo("Asia/Tokyo")

    def is_business_day(self, d: date) -> bool:
        return d.weekday() < 5

    def next_business_day(self, d: date) -> date:
        return d

    def previous_business_day(self, d: date) -> date:
        return d

    def get_business_days(self, _start: date, _end: date) -> list[date]:
        return []

    def count_business_days(self, _start: date, _end: date) -> int:
        return 0

    def get_sq_date(self, year: int, month: int) -> date:
        return date(year, month, 1)

    def is_sq_date(self, _d: date) -> bool:
        return False

    def get_sq_dates_for_year(self, _year: int) -> list[date]:
        return []

    def get_session(self, _dt: datetime | None = None) -> TradingSession:
        return TradingSession.CLOSED

    def is_trading_hours(self, _dt: datetime | None = None) -> bool:
        return False


@pytest.fixture(autouse=True)
def clear_registry() -> None:
    """Clear registry before and after each test."""
    MarketRegistry.clear()
    yield
    MarketRegistry.clear()


class TestMarketRegistryRegister:
    """Test cases for MarketRegistry.register() decorator."""

    def test_register_market(self) -> None:
        """Should register a market class with decorator."""

        @MarketRegistry.register("test-market")
        class TestMarket(MockMarket):
            pass

        assert "test-market" in MarketRegistry.get_available_markets()

    def test_register_returns_original_class(self) -> None:
        """Decorator should return the original class unchanged."""

        @MarketRegistry.register("test-market")
        class TestMarket(MockMarket):
            pass

        assert TestMarket.__name__ == "TestMarket"

    def test_register_duplicate_raises_error(self) -> None:
        """Should raise MarketAlreadyRegisteredError on duplicate registration."""

        @MarketRegistry.register("duplicate-market")
        class FirstMarket(MockMarket):
            pass

        with pytest.raises(MarketAlreadyRegisteredError) as exc_info:

            @MarketRegistry.register("duplicate-market")
            class SecondMarket(MockMarket):
                pass

        assert "duplicate-market" in str(exc_info.value)
        assert exc_info.value.market_id == "duplicate-market"
        assert exc_info.value.existing_class == "FirstMarket"


class TestMarketRegistryGet:
    """Test cases for MarketRegistry.get() method."""

    def test_get_registered_market(self) -> None:
        """Should return instance of registered market."""

        @MarketRegistry.register("test-market")
        class TestMarket(MockMarket):
            pass

        market = MarketRegistry.get("test-market")
        assert isinstance(market, TestMarket)

    def test_get_unregistered_market_raises_error(self) -> None:
        """Should raise MarketNotFoundError for unregistered market."""
        with pytest.raises(MarketNotFoundError) as exc_info:
            MarketRegistry.get("nonexistent-market")

        assert "nonexistent-market" in str(exc_info.value)
        assert exc_info.value.market_id == "nonexistent-market"

    def test_get_creates_new_instance_each_call(self) -> None:
        """Each call to get() should create a new instance."""

        @MarketRegistry.register("test-market")
        class TestMarket(MockMarket):
            pass

        market1 = MarketRegistry.get("test-market")
        market2 = MarketRegistry.get("test-market")
        assert market1 is not market2


class TestMarketRegistryGetAvailableMarkets:
    """Test cases for MarketRegistry.get_available_markets() method."""

    def test_returns_empty_list_when_no_markets(self) -> None:
        """Should return empty list when no markets registered."""
        assert MarketRegistry.get_available_markets() == []

    def test_returns_sorted_list(self) -> None:
        """Should return market IDs in sorted order."""

        @MarketRegistry.register("charlie")
        class CharlieMarket(MockMarket):
            pass

        @MarketRegistry.register("alpha")
        class AlphaMarket(MockMarket):
            pass

        @MarketRegistry.register("bravo")
        class BravoMarket(MockMarket):
            pass

        markets = MarketRegistry.get_available_markets()
        assert markets == ["alpha", "bravo", "charlie"]


class TestMarketRegistryClear:
    """Test cases for MarketRegistry.clear() method."""

    def test_clear_removes_all_markets(self) -> None:
        """Clear should remove all registered markets."""

        @MarketRegistry.register("market-1")
        class Market1(MockMarket):
            pass

        @MarketRegistry.register("market-2")
        class Market2(MockMarket):
            pass

        assert len(MarketRegistry.get_available_markets()) == 2

        MarketRegistry.clear()

        assert MarketRegistry.get_available_markets() == []

    def test_can_register_after_clear(self) -> None:
        """Should be able to register markets after clear."""

        @MarketRegistry.register("first-market")
        class FirstMarket(MockMarket):
            pass

        MarketRegistry.clear()

        @MarketRegistry.register("first-market")
        class NewMarket(MockMarket):
            pass

        assert "first-market" in MarketRegistry.get_available_markets()
