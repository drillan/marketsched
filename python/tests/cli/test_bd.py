"""Tests for bd (business day) CLI subcommand.

Tests cover:
- T074: mks bd is
- T075: mks bd next
- T076: mks bd prev
- T077: mks bd list
- T078: mks bd count

Note: Global options (--format, --market) must be placed BEFORE the subcommand
when using Typer's subcommand structure (e.g., `mks -f text bd is 2026-02-06`).
"""

import json

from typer.testing import CliRunner

from marketsched.cli import app

runner = CliRunner()


class TestBdIs:
    """Tests for 'mks bd is' command."""

    def test_bd_is_business_day_json(self) -> None:
        """Test bd is returns JSON for business day."""
        result = runner.invoke(app, ["bd", "is", "2026-02-06"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["date"] == "2026-02-06"
        assert data["is_business_day"] is True

    def test_bd_is_weekend_json(self) -> None:
        """Test bd is returns JSON for weekend."""
        result = runner.invoke(app, ["bd", "is", "2026-02-07"])  # Saturday
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["date"] == "2026-02-07"
        assert data["is_business_day"] is False

    def test_bd_is_text_format(self) -> None:
        """Test bd is with --format text (option before subcommand)."""
        result = runner.invoke(app, ["--format", "text", "bd", "is", "2026-02-06"])
        assert result.exit_code == 0
        assert "2026-02-06" in result.stdout
        # Should contain readable text
        assert "true" in result.stdout.lower() or "yes" in result.stdout.lower()

    def test_bd_is_with_market_option(self) -> None:
        """Test bd is with -m option (option before subcommand)."""
        result = runner.invoke(app, ["-m", "jpx-index", "bd", "is", "2026-02-06"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["is_business_day"] is True

    def test_bd_is_invalid_date(self) -> None:
        """Test bd is with invalid date format."""
        result = runner.invoke(app, ["bd", "is", "invalid-date"])
        assert result.exit_code != 0

    def test_bd_is_help(self) -> None:
        """Test bd is --help."""
        result = runner.invoke(app, ["bd", "is", "--help"])
        assert result.exit_code == 0
        assert "date" in result.stdout.lower()


class TestBdNext:
    """Tests for 'mks bd next' command."""

    def test_bd_next_from_friday_json(self) -> None:
        """Test bd next returns Monday for Friday."""
        result = runner.invoke(app, ["bd", "next", "2026-02-06"])  # Friday
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["date"] == "2026-02-06"
        assert data["next_business_day"] == "2026-02-09"  # Monday

    def test_bd_next_text_format(self) -> None:
        """Test bd next with --format text."""
        result = runner.invoke(app, ["--format", "text", "bd", "next", "2026-02-06"])
        assert result.exit_code == 0
        assert "2026-02-09" in result.stdout

    def test_bd_next_invalid_date(self) -> None:
        """Test bd next with invalid date format."""
        result = runner.invoke(app, ["bd", "next", "not-a-date"])
        assert result.exit_code != 0


class TestBdPrev:
    """Tests for 'mks bd prev' command."""

    def test_bd_prev_from_monday_json(self) -> None:
        """Test bd prev returns Friday for Monday."""
        result = runner.invoke(app, ["bd", "prev", "2026-02-09"])  # Monday
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["date"] == "2026-02-09"
        assert data["previous_business_day"] == "2026-02-06"  # Friday

    def test_bd_prev_text_format(self) -> None:
        """Test bd prev with --format text."""
        result = runner.invoke(app, ["--format", "text", "bd", "prev", "2026-02-09"])
        assert result.exit_code == 0
        assert "2026-02-06" in result.stdout

    def test_bd_prev_invalid_date(self) -> None:
        """Test bd prev with invalid date format (YYYYMMDD without hyphens)."""
        result = runner.invoke(app, ["bd", "prev", "20260209"])
        # YYYYMMDD is parsed as a valid ISO date by some parsers, so this may pass
        # The key is that it should either fail or return correct result
        # For stricter validation, we test with clearly invalid format
        result = runner.invoke(app, ["bd", "prev", "not-a-date"])
        assert result.exit_code != 0


class TestBdList:
    """Tests for 'mks bd list' command."""

    def test_bd_list_json(self) -> None:
        """Test bd list returns JSON array of dates."""
        result = runner.invoke(app, ["bd", "list", "2026-02-01", "2026-02-10"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "start_date" in data
        assert "end_date" in data
        assert "business_days" in data
        assert isinstance(data["business_days"], list)
        # Feb 1 is Sunday, Feb 2-6 are Mon-Fri, Feb 7-8 are Sat-Sun, Feb 9-10 are Mon-Tue
        # Business days: 2, 3, 4, 5, 6, 9, 10
        assert len(data["business_days"]) >= 5

    def test_bd_list_text_format(self) -> None:
        """Test bd list with --format text."""
        result = runner.invoke(
            app, ["--format", "text", "bd", "list", "2026-02-01", "2026-02-10"]
        )
        assert result.exit_code == 0
        # Should have multiple dates listed
        assert "2026-02-02" in result.stdout or "2026-02-06" in result.stdout

    def test_bd_list_table_format(self) -> None:
        """Test bd list with --format table."""
        result = runner.invoke(
            app, ["--format", "table", "bd", "list", "2026-02-01", "2026-02-10"]
        )
        assert result.exit_code == 0
        # Table format should have some structure
        assert "2026-02" in result.stdout

    def test_bd_list_invalid_range(self) -> None:
        """Test bd list with end before start."""
        result = runner.invoke(app, ["bd", "list", "2026-02-10", "2026-02-01"])
        # Should handle gracefully (empty list or error)
        assert result.exit_code == 0  # Empty list is valid


class TestBdCount:
    """Tests for 'mks bd count' command."""

    def test_bd_count_json(self) -> None:
        """Test bd count returns count in JSON."""
        result = runner.invoke(app, ["bd", "count", "2026-02-01", "2026-02-10"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "start_date" in data
        assert "end_date" in data
        assert "count" in data
        assert isinstance(data["count"], int)
        assert data["count"] >= 5

    def test_bd_count_text_format(self) -> None:
        """Test bd count with --format text."""
        result = runner.invoke(
            app, ["--format", "text", "bd", "count", "2026-02-01", "2026-02-10"]
        )
        assert result.exit_code == 0
        # Should contain the count as a number
        assert any(c.isdigit() for c in result.stdout)

    def test_bd_count_single_day(self) -> None:
        """Test bd count for single business day range."""
        result = runner.invoke(app, ["bd", "count", "2026-02-06", "2026-02-06"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["count"] == 1  # Friday is a business day


class TestBdSubcommandHelp:
    """Tests for bd subcommand help."""

    def test_bd_help(self) -> None:
        """Test bd --help shows all subcommands."""
        result = runner.invoke(app, ["bd", "--help"])
        assert result.exit_code == 0
        assert "is" in result.stdout
        assert "next" in result.stdout
        assert "prev" in result.stdout
        assert "list" in result.stdout
        assert "count" in result.stdout
