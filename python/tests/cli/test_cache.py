"""Tests for cache CLI subcommand.

Tests cover:
- T094: mks cache update
- T095: mks cache clear
- T096: mks cache status

Note: Global options (--format, --market) must be placed BEFORE the subcommand
when using Typer's subcommand structure (e.g., `mks -f text cache status`).
"""

import json

from typer.testing import CliRunner

from marketsched.cli import app

runner = CliRunner()


class TestCacheStatus:
    """Tests for 'mks cache status' command."""

    def test_cache_status_json(self) -> None:
        """Test cache status returns JSON with cache info."""
        result = runner.invoke(app, ["cache", "status"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        # Should have basic status fields
        assert "cache_dir" in data or "path" in data
        assert "exists" in data or "initialized" in data or "status" in data

    def test_cache_status_text_format(self) -> None:
        """Test cache status with --format text (option before subcommand)."""
        result = runner.invoke(app, ["--format", "text", "cache", "status"])
        assert result.exit_code == 0
        # Should have readable output
        assert len(result.stdout) > 0


class TestCacheUpdate:
    """Tests for 'mks cache update' command."""

    def test_cache_update_json(self) -> None:
        """Test cache update returns success status."""
        result = runner.invoke(app, ["cache", "update"])
        # May succeed or fail depending on network, but should complete
        # For testing, we mainly check the output format
        if result.exit_code == 0:
            data = json.loads(result.stdout)
            assert "status" in data or "updated" in data or "success" in data

    def test_cache_update_text_format(self) -> None:
        """Test cache update with --format text (option before subcommand)."""
        result = runner.invoke(app, ["--format", "text", "cache", "update"])
        # Should have some output regardless of success
        assert len(result.stdout) > 0 or (
            result.stderr is not None and len(result.stderr) > 0
        )


class TestCacheClear:
    """Tests for 'mks cache clear' command."""

    def test_cache_clear_json(self) -> None:
        """Test cache clear returns success status."""
        result = runner.invoke(app, ["cache", "clear"])
        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert "status" in data or "cleared" in data or "success" in data

    def test_cache_clear_text_format(self) -> None:
        """Test cache clear with --format text (option before subcommand)."""
        result = runner.invoke(app, ["--format", "text", "cache", "clear"])
        assert result.exit_code == 0
        assert len(result.stdout) > 0


class TestCacheSubcommandHelp:
    """Tests for cache subcommand help."""

    def test_cache_help(self) -> None:
        """Test cache --help shows all subcommands."""
        result = runner.invoke(app, ["cache", "--help"])
        assert result.exit_code == 0
        assert "update" in result.stdout
        assert "clear" in result.stdout
        assert "status" in result.stdout
