"""Integration tests for market registry with JPXIndex.

These tests verify that JPXIndex is properly registered and can be
retrieved through the public API.
"""

from zoneinfo import ZoneInfo

import pytest

import marketsched
from marketsched import Market, MarketNotFoundError
from marketsched.jpx import JPXIndex


class TestMarketRegistryIntegration:
    """Test market registry with JPXIndex."""

    def test_get_market_returns_jpx_index(self) -> None:
        """get_market('jpx-index') should return a JPXIndex instance."""
        market = marketsched.get_market("jpx-index")
        assert isinstance(market, JPXIndex)

    def test_get_market_jpx_index_properties(self) -> None:
        """get_market('jpx-index') should return market with correct properties."""
        market = marketsched.get_market("jpx-index")
        assert market.market_id == "jpx-index"
        assert market.name == "JPX Index Futures & Options"
        assert market.timezone == ZoneInfo("Asia/Tokyo")

    def test_get_available_markets_includes_jpx_index(self) -> None:
        """get_available_markets() should include 'jpx-index'."""
        markets = marketsched.get_available_markets()
        assert "jpx-index" in markets

    def test_get_available_markets_returns_sorted_list(self) -> None:
        """get_available_markets() should return sorted list."""
        markets = marketsched.get_available_markets()
        assert markets == sorted(markets)

    def test_get_market_unknown_raises_error(self) -> None:
        """get_market() with unknown ID should raise MarketNotFoundError."""
        with pytest.raises(MarketNotFoundError) as exc_info:
            marketsched.get_market("unknown-market")

        assert "unknown-market" in str(exc_info.value)

    def test_market_protocol_compliance(self) -> None:
        """JPXIndex should satisfy the Market Protocol.

        This is a structural subtyping check - JPXIndex doesn't need to
        explicitly inherit from Market, just have the right methods.
        """
        market = marketsched.get_market("jpx-index")

        # Check that it can be used where Market is expected
        # (This is a runtime check; mypy would catch protocol violations at type check time)
        def accepts_market(m: Market) -> str:
            return m.market_id

        result = accepts_market(market)
        assert result == "jpx-index"


class TestMultipleMarketInstances:
    """Test that multiple get_market calls work correctly."""

    def test_get_market_returns_new_instances(self) -> None:
        """Each get_market call should return a new instance."""
        market1 = marketsched.get_market("jpx-index")
        market2 = marketsched.get_market("jpx-index")

        # Different instances
        assert market1 is not market2

        # But same properties
        assert market1.market_id == market2.market_id
        assert market1.name == market2.name
        assert market1.timezone == market2.timezone
