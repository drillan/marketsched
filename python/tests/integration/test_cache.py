"""Integration tests for cache API (T024a).

ruff: noqa: ARG002
"""

from datetime import datetime
from pathlib import Path

import httpx
import pytest
from pytest_httpx import HTTPXMock

from marketsched.cache import clear_cache, get_cache_status, update_cache
from marketsched.exceptions import DataFetchError
from marketsched.jpx.data import CacheInfo

from .conftest import create_holiday_trading_excel, create_sq_dates_excel


@pytest.fixture
def temp_cache_dir(tmp_path: Path) -> Path:
    """Create a temporary cache directory."""
    cache_dir = tmp_path / "cache"
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def mock_cache_dir(temp_cache_dir: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Patch the default cache directory."""
    monkeypatch.setattr(
        "marketsched.cache.ParquetCacheManager.DEFAULT_CACHE_DIR",
        temp_cache_dir,
    )
    return temp_cache_dir


class TestUpdateCache:
    """Tests for update_cache function."""

    def test_update_cache_fetches_and_stores_data(
        self, mock_cache_dir: Path, httpx_mock: HTTPXMock
    ) -> None:
        """update_cache fetches data and stores it in cache."""
        sq_excel = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )
        holiday_excel = create_holiday_trading_excel(
            [
                (datetime(2026, 2, 11), "建国記念の日", "実施する"),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=sq_excel,
        )
        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
            content=holiday_excel,
        )

        result = update_cache(years=[2026])

        assert "sq_dates" in result
        assert "holiday_trading" in result
        assert result["sq_dates"].is_valid is True
        assert result["holiday_trading"].is_valid is True

        # Verify files exist
        assert (mock_cache_dir / "sq_dates.parquet").exists()
        assert (mock_cache_dir / "holiday_trading.parquet").exists()

    def test_update_cache_skips_if_valid_unless_forced(
        self, mock_cache_dir: Path, httpx_mock: HTTPXMock
    ) -> None:
        """update_cache skips fetch if cache is valid, unless force=True."""
        sq_excel = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )
        holiday_excel = create_holiday_trading_excel(
            [
                (datetime(2026, 2, 11), "建国記念の日", "実施する"),
            ]
        )

        # Set up mock for first call (2 requests each for initial + force)
        for _ in range(2):
            httpx_mock.add_response(
                url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
                content=sq_excel,
            )
            httpx_mock.add_response(
                url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
                content=holiday_excel,
            )

        # First call - should fetch
        update_cache(years=[2026])

        # Second call without force - should not fetch (uses cached data)
        result = update_cache(years=[2026], force=False)
        assert result["sq_dates"].is_valid is True

        # With force=True - should fetch again (uses remaining mock responses)
        result = update_cache(years=[2026], force=True)
        assert result["sq_dates"].is_valid is True

    def test_update_cache_network_error_raises_data_fetch_error(
        self, mock_cache_dir: Path, httpx_mock: HTTPXMock
    ) -> None:
        """Network error during update raises DataFetchError."""
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))

        with pytest.raises(DataFetchError):
            update_cache(years=[2026])


class TestClearCache:
    """Tests for clear_cache function."""

    def test_clear_cache_removes_specific_type(
        self, mock_cache_dir: Path, httpx_mock: HTTPXMock
    ) -> None:
        """clear_cache(data_type) removes only specified cache."""
        sq_excel = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )
        holiday_excel = create_holiday_trading_excel(
            [
                (datetime(2026, 2, 11), "建国記念の日", "実施する"),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=sq_excel,
        )
        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
            content=holiday_excel,
        )

        update_cache(years=[2026])

        clear_cache("sq_dates")

        status = get_cache_status()
        assert status["sq_dates"].is_valid is False
        assert status["holiday_trading"].is_valid is True

    def test_clear_cache_removes_all(
        self, mock_cache_dir: Path, httpx_mock: HTTPXMock
    ) -> None:
        """clear_cache() removes all caches."""
        sq_excel = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )
        holiday_excel = create_holiday_trading_excel(
            [
                (datetime(2026, 2, 11), "建国記念の日", "実施する"),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=sq_excel,
        )
        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
            content=holiday_excel,
        )

        update_cache(years=[2026])

        clear_cache()

        status = get_cache_status()
        assert status["sq_dates"].is_valid is False
        assert status["holiday_trading"].is_valid is False


class TestGetCacheStatus:
    """Tests for get_cache_status function."""

    def test_get_cache_status_returns_info_for_all_types(
        self, mock_cache_dir: Path
    ) -> None:
        """get_cache_status returns info for all cache types."""
        status = get_cache_status()

        assert "sq_dates" in status
        assert "holiday_trading" in status
        assert isinstance(status["sq_dates"], CacheInfo)
        assert isinstance(status["holiday_trading"], CacheInfo)

    def test_get_cache_status_shows_valid_after_update(
        self, mock_cache_dir: Path, httpx_mock: HTTPXMock
    ) -> None:
        """After update, cache status shows valid."""
        sq_excel = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )
        holiday_excel = create_holiday_trading_excel(
            [
                (datetime(2026, 2, 11), "建国記念の日", "実施する"),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=sq_excel,
        )
        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
            content=holiday_excel,
        )

        update_cache(years=[2026])

        status = get_cache_status()

        assert status["sq_dates"].is_valid is True
        assert status["sq_dates"].record_count == 1
        assert status["holiday_trading"].is_valid is True
        assert status["holiday_trading"].record_count == 1
