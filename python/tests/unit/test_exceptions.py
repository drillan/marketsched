"""Unit tests for custom exception classes."""


class TestMarketschedError:
    """Test cases for base MarketschedError."""

    def test_base_exception_exists(self) -> None:
        """MarketschedError should be importable."""
        from marketsched.exceptions import MarketschedError

        assert MarketschedError is not None

    def test_base_exception_is_exception(self) -> None:
        """MarketschedError should inherit from Exception."""
        from marketsched.exceptions import MarketschedError

        assert issubclass(MarketschedError, Exception)

    def test_base_exception_with_message(self) -> None:
        """MarketschedError should accept and store message."""
        from marketsched.exceptions import MarketschedError

        error = MarketschedError("test message")
        assert str(error) == "test message"

    def test_backwards_compatibility_alias(self) -> None:
        """MarketshedError should be an alias for MarketschedError."""
        from marketsched.exceptions import MarketschedError, MarketshedError

        assert MarketshedError is MarketschedError


class TestMarketNotFoundError:
    """Test cases for MarketNotFoundError."""

    def test_inherits_from_base(self) -> None:
        """MarketNotFoundError should inherit from MarketschedError."""
        from marketsched.exceptions import MarketNotFoundError, MarketschedError

        assert issubclass(MarketNotFoundError, MarketschedError)

    def test_with_market_id(self) -> None:
        """MarketNotFoundError should include market_id in message."""
        from marketsched.exceptions import MarketNotFoundError

        error = MarketNotFoundError("unknown-market")
        assert "unknown-market" in str(error)
        assert error.market_id == "unknown-market"


class TestContractMonthParseError:
    """Test cases for ContractMonthParseError."""

    def test_inherits_from_base(self) -> None:
        """ContractMonthParseError should inherit from MarketschedError."""
        from marketsched.exceptions import ContractMonthParseError, MarketschedError

        assert issubclass(ContractMonthParseError, MarketschedError)

    def test_with_input_text(self) -> None:
        """ContractMonthParseError should include input text in message."""
        from marketsched.exceptions import ContractMonthParseError

        error = ContractMonthParseError("invalid input")
        assert "invalid input" in str(error)
        assert error.input_text == "invalid input"


class TestSQDataNotFoundError:
    """Test cases for SQDataNotFoundError."""

    def test_inherits_from_base(self) -> None:
        """SQDataNotFoundError should inherit from MarketschedError."""
        from marketsched.exceptions import MarketschedError, SQDataNotFoundError

        assert issubclass(SQDataNotFoundError, MarketschedError)

    def test_with_year_month(self) -> None:
        """SQDataNotFoundError should include year and month."""
        from marketsched.exceptions import SQDataNotFoundError

        error = SQDataNotFoundError(2050, 1)
        assert "2050" in str(error)
        assert error.year == 2050
        assert error.month == 1


class TestSQNotSupportedError:
    """Test cases for SQNotSupportedError."""

    def test_inherits_from_base(self) -> None:
        """SQNotSupportedError should inherit from MarketschedError."""
        from marketsched.exceptions import MarketschedError, SQNotSupportedError

        assert issubclass(SQNotSupportedError, MarketschedError)

    def test_with_market_id(self) -> None:
        """SQNotSupportedError should include market_id."""
        from marketsched.exceptions import SQNotSupportedError

        error = SQNotSupportedError("tse-stock")
        assert "tse-stock" in str(error)
        assert error.market_id == "tse-stock"


class TestTimezoneRequiredError:
    """Test cases for TimezoneRequiredError."""

    def test_inherits_from_base(self) -> None:
        """TimezoneRequiredError should inherit from MarketschedError."""
        from marketsched.exceptions import MarketschedError, TimezoneRequiredError

        assert issubclass(TimezoneRequiredError, MarketschedError)

    def test_message(self) -> None:
        """TimezoneRequiredError should have informative message."""
        from marketsched.exceptions import TimezoneRequiredError

        error = TimezoneRequiredError()
        assert "timezone" in str(error).lower()


class TestCacheNotAvailableError:
    """Test cases for CacheNotAvailableError."""

    def test_inherits_from_base(self) -> None:
        """CacheNotAvailableError should inherit from MarketschedError."""
        from marketsched.exceptions import CacheNotAvailableError, MarketschedError

        assert issubclass(CacheNotAvailableError, MarketschedError)

    def test_message(self) -> None:
        """CacheNotAvailableError should provide recovery guidance."""
        from marketsched.exceptions import CacheNotAvailableError

        error = CacheNotAvailableError()
        message = str(error).lower()
        # Should mention cache or online
        assert "cache" in message or "online" in message


class TestDataFetchError:
    """Test cases for DataFetchError."""

    def test_inherits_from_base(self) -> None:
        """DataFetchError should inherit from MarketschedError."""
        from marketsched.exceptions import DataFetchError, MarketschedError

        assert issubclass(DataFetchError, MarketschedError)

    def test_with_url_and_reason(self) -> None:
        """DataFetchError should include URL and reason."""
        from marketsched.exceptions import DataFetchError

        error = DataFetchError("https://example.com", "Connection timeout")
        assert "example.com" in str(error)
        assert error.url == "https://example.com"
        assert error.reason == "Connection timeout"


class TestInvalidDataFormatError:
    """Test cases for InvalidDataFormatError."""

    def test_inherits_from_base(self) -> None:
        """InvalidDataFormatError should inherit from MarketschedError."""
        from marketsched.exceptions import InvalidDataFormatError, MarketschedError

        assert issubclass(InvalidDataFormatError, MarketschedError)

    def test_with_details(self) -> None:
        """InvalidDataFormatError should include details."""
        from marketsched.exceptions import InvalidDataFormatError

        error = InvalidDataFormatError("Expected column 'date' not found")
        assert "date" in str(error)
        assert error.details == "Expected column 'date' not found"


class TestMarketAlreadyRegisteredError:
    """Test cases for MarketAlreadyRegisteredError."""

    def test_inherits_from_base(self) -> None:
        """MarketAlreadyRegisteredError should inherit from MarketschedError."""
        from marketsched.exceptions import (
            MarketAlreadyRegisteredError,
            MarketschedError,
        )

        assert issubclass(MarketAlreadyRegisteredError, MarketschedError)

    def test_with_market_id_and_class(self) -> None:
        """MarketAlreadyRegisteredError should include market_id and existing_class."""
        from marketsched.exceptions import MarketAlreadyRegisteredError

        error = MarketAlreadyRegisteredError("jpx-index", "JPXIndex")
        assert "jpx-index" in str(error)
        assert "JPXIndex" in str(error)
        assert error.market_id == "jpx-index"
        assert error.existing_class == "JPXIndex"
