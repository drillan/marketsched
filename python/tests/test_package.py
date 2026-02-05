"""Package integration tests for marketsched.

These tests verify that the package can be imported and the public API
is available as documented.
"""


class TestPackageImport:
    """Test package import (US1)."""

    def test_import_marketsched(self) -> None:
        """import marketsched should not raise errors."""
        import marketsched

        assert marketsched is not None

    def test_version_available(self) -> None:
        """Package version should be available."""
        import marketsched

        assert hasattr(marketsched, "__version__")
        assert isinstance(marketsched.__version__, str)
        assert len(marketsched.__version__) > 0


class TestPublicAPIAvailability:
    """Test public API availability (US1)."""

    def test_market_class_available(self) -> None:
        """Market class should be importable."""
        from marketsched import Market

        assert Market is not None

    def test_contract_month_available(self) -> None:
        """ContractMonth class should be importable."""
        from marketsched import ContractMonth

        assert ContractMonth is not None

    def test_trading_session_available(self) -> None:
        """TradingSession enum should be importable."""
        from marketsched import TradingSession

        assert TradingSession is not None
        assert hasattr(TradingSession, "DAY")
        assert hasattr(TradingSession, "NIGHT")
        assert hasattr(TradingSession, "CLOSED")

    def test_get_market_available(self) -> None:
        """get_market function should be importable."""
        from marketsched import get_market

        assert callable(get_market)

    def test_get_available_markets_available(self) -> None:
        """get_available_markets function should be importable."""
        from marketsched import get_available_markets

        assert callable(get_available_markets)


class TestExceptionImports:
    """Test exception class imports."""

    def test_marketsched_error_available(self) -> None:
        """MarketschedError should be importable."""
        from marketsched import MarketschedError

        assert MarketschedError is not None

    def test_market_not_found_error_available(self) -> None:
        """MarketNotFoundError should be importable."""
        from marketsched import MarketNotFoundError

        assert MarketNotFoundError is not None

    def test_contract_month_parse_error_available(self) -> None:
        """ContractMonthParseError should be importable."""
        from marketsched import ContractMonthParseError

        assert ContractMonthParseError is not None

    def test_sq_data_not_found_error_available(self) -> None:
        """SQDataNotFoundError should be importable."""
        from marketsched import SQDataNotFoundError

        assert SQDataNotFoundError is not None

    def test_timezone_required_error_available(self) -> None:
        """TimezoneRequiredError should be importable."""
        from marketsched import TimezoneRequiredError

        assert TimezoneRequiredError is not None

    def test_cache_not_available_error_available(self) -> None:
        """CacheNotAvailableError should be importable."""
        from marketsched import CacheNotAvailableError

        assert CacheNotAvailableError is not None


class TestJPXModuleImport:
    """Test JPX module import."""

    def test_import_jpx_module(self) -> None:
        """marketsched.jpx should be importable."""
        from marketsched.jpx import JPXIndex

        assert JPXIndex is not None

    def test_jpx_index_registered(self) -> None:
        """JPXIndex should be registered and retrievable."""
        import marketsched

        markets = marketsched.get_available_markets()
        assert "jpx-index" in markets


class TestBasicUsage:
    """Test basic usage patterns from the documentation."""

    def test_get_market_jpx_index(self) -> None:
        """Should be able to get jpx-index market."""
        import marketsched

        market = marketsched.get_market("jpx-index")
        assert market.market_id == "jpx-index"

    def test_contract_month_creation(self) -> None:
        """Should be able to create ContractMonth."""
        from marketsched import ContractMonth

        cm = ContractMonth(year=2026, month=3)
        assert cm.year == 2026
        assert cm.month == 3

    def test_contract_month_parse(self) -> None:
        """Should be able to parse ContractMonth from Japanese string."""
        from marketsched import ContractMonth

        cm = ContractMonth.parse("26年3月限")
        assert cm.year == 2026
        assert cm.month == 3

    def test_contract_month_conversion(self) -> None:
        """Should be able to convert ContractMonth to different formats."""
        from marketsched import ContractMonth

        cm = ContractMonth(year=2026, month=3)
        assert cm.to_yyyymm() == "202603"
        assert cm.to_japanese() == "2026年3月限"
