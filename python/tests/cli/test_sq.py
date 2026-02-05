"""Tests for sq (SQ date) CLI subcommand.

Tests cover:
- T083: mks sq get with multiple formats
- T084: mks sq list
- T085: mks sq is

Note: Global options (--format, --market) must be placed BEFORE the subcommand
when using Typer's subcommand structure (e.g., `mks -f text sq get 2026 3`).
"""

import json

from typer.testing import CliRunner

from marketsched.cli import app

runner = CliRunner()


class TestSqGet:
    """Tests for 'mks sq get' command."""

    def test_sq_get_two_args_json(self) -> None:
        """Test sq get with 2 arguments (year month)."""
        result = runner.invoke(app, ["sq", "get", "2026", "3"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "year" in data
        assert "month" in data
        assert "sq_date" in data
        assert data["year"] == 2026
        assert data["month"] == 3
        # SQ date should be in March 2026
        assert data["sq_date"].startswith("2026-03")

    def test_sq_get_yyyymm_format(self) -> None:
        """Test sq get with YYYYMM format."""
        result = runner.invoke(app, ["sq", "get", "202603"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["year"] == 2026
        assert data["month"] == 3
        assert data["sq_date"].startswith("2026-03")

    def test_sq_get_yyyy_mm_format(self) -> None:
        """Test sq get with YYYY-MM format."""
        result = runner.invoke(app, ["sq", "get", "2026-03"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["year"] == 2026
        assert data["month"] == 3
        assert data["sq_date"].startswith("2026-03")

    def test_sq_get_text_format(self) -> None:
        """Test sq get with --format text (option before subcommand)."""
        result = runner.invoke(app, ["--format", "text", "sq", "get", "2026", "3"])
        assert result.exit_code == 0
        assert "2026" in result.stdout
        assert "3" in result.stdout or "03" in result.stdout

    def test_sq_get_invalid_format(self) -> None:
        """Test sq get with invalid year-month format."""
        result = runner.invoke(app, ["sq", "get", "invalid"])
        assert result.exit_code != 0

    def test_sq_get_invalid_month(self) -> None:
        """Test sq get with invalid month."""
        result = runner.invoke(app, ["sq", "get", "2026", "13"])
        assert result.exit_code != 0


class TestSqList:
    """Tests for 'mks sq list' command."""

    def test_sq_list_json(self) -> None:
        """Test sq list returns JSON array of SQ dates."""
        result = runner.invoke(app, ["sq", "list", "2026"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "year" in data
        assert "sq_dates" in data
        assert data["year"] == 2026
        assert isinstance(data["sq_dates"], list)
        # Should have 12 SQ dates for a full year
        assert len(data["sq_dates"]) == 12

    def test_sq_list_text_format(self) -> None:
        """Test sq list with --format text (option before subcommand)."""
        result = runner.invoke(app, ["--format", "text", "sq", "list", "2026"])
        assert result.exit_code == 0
        # Should have multiple dates
        assert result.stdout.count("2026") >= 10

    def test_sq_list_table_format(self) -> None:
        """Test sq list with --format table (option before subcommand)."""
        result = runner.invoke(app, ["--format", "table", "sq", "list", "2026"])
        assert result.exit_code == 0
        # Table should have header or structure
        assert "2026" in result.stdout


class TestSqIs:
    """Tests for 'mks sq is' command."""

    def test_sq_is_sq_date_json(self) -> None:
        """Test sq is returns True for actual SQ date."""
        # First get an actual SQ date
        get_result = runner.invoke(app, ["sq", "get", "2026", "3"])
        sq_data = json.loads(get_result.stdout)
        sq_date = sq_data["sq_date"]

        result = runner.invoke(app, ["sq", "is", sq_date])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["date"] == sq_date
        assert data["is_sq_date"] is True

    def test_sq_is_non_sq_date_json(self) -> None:
        """Test sq is returns False for non-SQ date."""
        result = runner.invoke(app, ["sq", "is", "2026-03-01"])  # Not an SQ date
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data["date"] == "2026-03-01"
        assert data["is_sq_date"] is False

    def test_sq_is_text_format(self) -> None:
        """Test sq is with --format text (option before subcommand)."""
        result = runner.invoke(app, ["--format", "text", "sq", "is", "2026-03-01"])
        assert result.exit_code == 0
        assert "2026-03-01" in result.stdout

    def test_sq_is_invalid_date(self) -> None:
        """Test sq is with invalid date format."""
        result = runner.invoke(app, ["sq", "is", "not-a-date"])
        assert result.exit_code != 0


class TestSqSubcommandHelp:
    """Tests for sq subcommand help."""

    def test_sq_help(self) -> None:
        """Test sq --help shows all subcommands."""
        result = runner.invoke(app, ["sq", "--help"])
        assert result.exit_code == 0
        assert "get" in result.stdout
        assert "list" in result.stdout
        assert "is" in result.stdout
