"""Tests for ss (session) CLI subcommand.

Tests cover:
- T088: mks ss get with datetime
- T089: mks ss get without datetime (current time)
- T090: mks ss is-trading
- T091: mks ss timezone error handling

Note: Global options (--format, --market) must be placed BEFORE the subcommand
when using Typer's subcommand structure (e.g., `mks -f text ss get`).
"""

import json

from typer.testing import CliRunner

from marketsched.cli import app

runner = CliRunner()


class TestSsGet:
    """Tests for 'mks ss get' command."""

    def test_ss_get_day_session_json(self) -> None:
        """Test ss get returns 'day' for day session time."""
        result = runner.invoke(app, ["ss", "get", "2026-02-06T10:00:00+09:00"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "datetime" in data
        assert "session" in data
        assert data["session"] == "day"

    def test_ss_get_night_session_json(self) -> None:
        """Test ss get returns 'night' for night session time."""
        result = runner.invoke(app, ["ss", "get", "2026-02-06T20:00:00+09:00"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["session"] == "night"

    def test_ss_get_closed_session_json(self) -> None:
        """Test ss get returns 'closed' for gap period."""
        result = runner.invoke(app, ["ss", "get", "2026-02-06T16:30:00+09:00"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["session"] == "closed"

    def test_ss_get_text_format(self) -> None:
        """Test ss get with --format text (option before subcommand)."""
        result = runner.invoke(
            app, ["--format", "text", "ss", "get", "2026-02-06T10:00:00+09:00"]
        )
        assert result.exit_code == 0
        assert "DAY" in result.stdout.upper() or "日中" in result.stdout

    def test_ss_get_no_datetime_uses_current(self) -> None:
        """Test ss get without datetime uses current time."""
        result = runner.invoke(app, ["ss", "get"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "datetime" in data
        assert "session" in data
        # Session should be one of day, night, or closed
        assert data["session"] in ["day", "night", "closed"]

    def test_ss_get_utc_timezone(self) -> None:
        """Test ss get with UTC timezone (converts to JST)."""
        # UTC 01:00 = JST 10:00 (DAY session)
        result = runner.invoke(app, ["ss", "get", "2026-02-06T01:00:00+00:00"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["session"] == "day"


class TestSsGetTimezoneError:
    """Tests for ss get timezone error handling."""

    def test_ss_get_naive_datetime_error(self) -> None:
        """Test ss get with naive datetime returns error."""
        # No timezone offset - this should fail
        result = runner.invoke(app, ["ss", "get", "2026-02-06T10:00:00"])
        assert result.exit_code != 0
        # Should have error message about timezone
        output = result.stdout + (result.stderr or "")
        assert "timezone" in output.lower()


class TestSsIsTrading:
    """Tests for 'mks ss is-trading' command."""

    def test_ss_is_trading_during_day_session(self) -> None:
        """Test is-trading returns True during day session."""
        result = runner.invoke(app, ["ss", "is-trading", "2026-02-06T10:00:00+09:00"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "datetime" in data
        assert "is_trading" in data
        assert data["is_trading"] is True

    def test_ss_is_trading_during_night_session(self) -> None:
        """Test is-trading returns True during night session."""
        result = runner.invoke(app, ["ss", "is-trading", "2026-02-06T20:00:00+09:00"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["is_trading"] is True

    def test_ss_is_trading_during_closed(self) -> None:
        """Test is-trading returns False during gap period."""
        result = runner.invoke(app, ["ss", "is-trading", "2026-02-06T16:30:00+09:00"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["is_trading"] is False

    def test_ss_is_trading_text_format(self) -> None:
        """Test is-trading with --format text (option before subcommand)."""
        result = runner.invoke(
            app,
            ["--format", "text", "ss", "is-trading", "2026-02-06T10:00:00+09:00"],
        )
        assert result.exit_code == 0
        assert (
            "true" in result.stdout.lower()
            or "yes" in result.stdout.lower()
            or "取引可" in result.stdout
        )

    def test_ss_is_trading_no_datetime_uses_current(self) -> None:
        """Test is-trading without datetime uses current time."""
        result = runner.invoke(app, ["ss", "is-trading"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "datetime" in data
        assert "is_trading" in data
        assert isinstance(data["is_trading"], bool)

    def test_ss_is_trading_naive_datetime_error(self) -> None:
        """Test is-trading with naive datetime returns error."""
        result = runner.invoke(app, ["ss", "is-trading", "2026-02-06T10:00:00"])
        assert result.exit_code != 0


class TestSsSubcommandHelp:
    """Tests for ss subcommand help."""

    def test_ss_help(self) -> None:
        """Test ss --help shows all subcommands."""
        result = runner.invoke(app, ["ss", "--help"])
        assert result.exit_code == 0
        assert "get" in result.stdout
        assert "is-trading" in result.stdout
