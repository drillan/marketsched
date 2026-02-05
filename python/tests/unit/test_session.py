"""Unit tests for TradingSession enum."""


class TestTradingSession:
    """Test cases for TradingSession enum."""

    def test_day_session_exists(self) -> None:
        """TradingSession should have DAY member."""
        from marketsched.session import TradingSession

        assert hasattr(TradingSession, "DAY")
        assert TradingSession.DAY.name == "DAY"

    def test_night_session_exists(self) -> None:
        """TradingSession should have NIGHT member."""
        from marketsched.session import TradingSession

        assert hasattr(TradingSession, "NIGHT")
        assert TradingSession.NIGHT.name == "NIGHT"

    def test_closed_session_exists(self) -> None:
        """TradingSession should have CLOSED member."""
        from marketsched.session import TradingSession

        assert hasattr(TradingSession, "CLOSED")
        assert TradingSession.CLOSED.name == "CLOSED"

    def test_session_values_are_distinct(self) -> None:
        """Each session type should have a distinct value."""
        from marketsched.session import TradingSession

        sessions = [TradingSession.DAY, TradingSession.NIGHT, TradingSession.CLOSED]
        values = [s.value for s in sessions]
        assert len(values) == len(set(values))

    def test_session_is_enum(self) -> None:
        """TradingSession should be an enum type."""
        from enum import Enum

        from marketsched.session import TradingSession

        assert issubclass(TradingSession, Enum)

    def test_session_string_representation(self) -> None:
        """TradingSession should have meaningful string representation."""
        from marketsched.session import TradingSession

        assert str(TradingSession.DAY) == "TradingSession.DAY"
        assert repr(TradingSession.DAY) == "<TradingSession.DAY: 'day'>"

    def test_session_from_value(self) -> None:
        """TradingSession should be creatable from value."""
        from marketsched.session import TradingSession

        assert TradingSession("day") == TradingSession.DAY
        assert TradingSession("night") == TradingSession.NIGHT
        assert TradingSession("closed") == TradingSession.CLOSED

    def test_session_is_trading(self) -> None:
        """TradingSession should have is_trading property."""
        from marketsched.session import TradingSession

        assert TradingSession.DAY.is_trading is True
        assert TradingSession.NIGHT.is_trading is True
        assert TradingSession.CLOSED.is_trading is False
