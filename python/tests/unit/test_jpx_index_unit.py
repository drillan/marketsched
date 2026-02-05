"""Unit tests for JPXIndex market implementation.

These tests verify the JPXIndex class properties and ensure it satisfies
the Market Protocol.
"""

from zoneinfo import ZoneInfo

import pytest

from marketsched.jpx.index import JPXIndex


class TestJPXIndexProperties:
    """Test JPXIndex basic properties (US3)."""

    @pytest.fixture
    def market(self) -> JPXIndex:
        """Create a JPXIndex instance for testing."""
        return JPXIndex()

    def test_market_id(self, market: JPXIndex) -> None:
        """market_id should be 'jpx-index'."""
        assert market.market_id == "jpx-index"

    def test_name(self, market: JPXIndex) -> None:
        """name should be the human-readable market name."""
        assert market.name == "JPX Index Futures & Options"

    def test_timezone(self, market: JPXIndex) -> None:
        """timezone should be Asia/Tokyo."""
        assert market.timezone == ZoneInfo("Asia/Tokyo")

    def test_timezone_is_zoneinfo(self, market: JPXIndex) -> None:
        """timezone should return a ZoneInfo instance."""
        assert isinstance(market.timezone, ZoneInfo)


class TestJPXIndexMarketProtocol:
    """Test that JPXIndex satisfies the Market Protocol."""

    def test_has_market_id_property(self) -> None:
        """JPXIndex should have market_id property."""
        market = JPXIndex()
        assert hasattr(market, "market_id")
        assert isinstance(market.market_id, str)

    def test_has_name_property(self) -> None:
        """JPXIndex should have name property."""
        market = JPXIndex()
        assert hasattr(market, "name")
        assert isinstance(market.name, str)

    def test_has_timezone_property(self) -> None:
        """JPXIndex should have timezone property."""
        market = JPXIndex()
        assert hasattr(market, "timezone")
        assert isinstance(market.timezone, ZoneInfo)

    def test_has_business_day_methods(self) -> None:
        """JPXIndex should have all business day methods."""
        market = JPXIndex()
        assert hasattr(market, "is_business_day")
        assert hasattr(market, "next_business_day")
        assert hasattr(market, "previous_business_day")
        assert hasattr(market, "get_business_days")
        assert hasattr(market, "count_business_days")

    def test_has_sq_methods(self) -> None:
        """JPXIndex should have all SQ date methods."""
        market = JPXIndex()
        assert hasattr(market, "get_sq_date")
        assert hasattr(market, "is_sq_date")
        assert hasattr(market, "get_sq_dates_for_year")

    def test_has_session_methods(self) -> None:
        """JPXIndex should have all session methods."""
        market = JPXIndex()
        assert hasattr(market, "get_session")
        assert hasattr(market, "is_trading_hours")
