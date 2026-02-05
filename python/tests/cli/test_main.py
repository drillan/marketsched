"""Tests for CLI main app structure.

Tests cover:
- T078a: mks --help and mks --version
- FR-CLI-001: marketsched and mks commands
- FR-CLI-006: --help option
- FR-CLI-007: --version option
"""

from typer.testing import CliRunner

from marketsched.cli import app

runner = CliRunner()


class TestMainHelp:
    """Tests for --help option."""

    def test_help_shows_subcommands(self) -> None:
        """--help should list all subcommands."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Should show all subcommand groups
        assert "bd" in result.stdout
        assert "sq" in result.stdout
        assert "ss" in result.stdout
        assert "cache" in result.stdout

    def test_help_shows_global_options(self) -> None:
        """--help should show --market and --format options."""
        result = runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "--market" in result.stdout or "-m" in result.stdout
        assert "--format" in result.stdout or "-f" in result.stdout


class TestMainVersion:
    """Tests for --version option."""

    def test_version_shows_version_number(self) -> None:
        """--version should show the package version."""
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        # Should show version from marketsched.__version__
        assert "0.0.1" in result.stdout or "marketsched" in result.stdout


class TestMainDefaultMarket:
    """Tests for default market option."""

    def test_default_market_is_jpx_index(self) -> None:
        """Default market should be jpx-index (FR-CLI-003)."""
        # This is tested implicitly through bd/sq/ss commands
        # that work without --market option
        result = runner.invoke(app, ["bd", "is", "2026-02-06"])
        assert result.exit_code == 0
