"""Unit tests for Parquet cache manager (T022).

ruff: noqa: ARG002
"""

from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import pyarrow as pa
import pytest

from marketsched.jpx.data import CacheMetadata
from marketsched.jpx.data.cache import ParquetCacheManager


class TestParquetCacheManager:
    """Tests for ParquetCacheManager."""

    @pytest.fixture
    def temp_cache_dir(self, tmp_path: Path) -> Path:
        """Create a temporary cache directory."""
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        return cache_dir

    @pytest.fixture
    def cache_manager(self, temp_cache_dir: Path) -> ParquetCacheManager:
        """Create a cache manager with temporary directory."""
        return ParquetCacheManager(cache_dir=temp_cache_dir)

    @pytest.fixture
    def sample_table(self) -> pa.Table:
        """Create a sample PyArrow table for testing."""
        return pa.table(
            {
                "contract_month": ["202603", "202604", "202605"],
                "last_trading_day": [
                    datetime(2026, 3, 12).date(),
                    datetime(2026, 4, 9).date(),
                    datetime(2026, 5, 7).date(),
                ],
                "sq_date": [
                    datetime(2026, 3, 13).date(),
                    datetime(2026, 4, 10).date(),
                    datetime(2026, 5, 8).date(),
                ],
                "product_category": [
                    "index_futures_options",
                    "index_futures_options",
                    "index_futures_options",
                ],
            }
        )

    @pytest.fixture
    def sample_metadata(self, utc: ZoneInfo) -> CacheMetadata:
        """Create sample cache metadata."""
        now = datetime.now(utc)
        return CacheMetadata(
            data_type="sq_dates",
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=now + timedelta(hours=24),
            schema_version=1,
            record_count=3,
        )

    def test_write_and_read_roundtrip(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
    ) -> None:
        """Data written to cache can be read back correctly."""
        # Write
        cache_manager.write("sq_dates", sample_table, sample_metadata)

        # Read
        result = cache_manager.read("sq_dates")

        assert result is not None
        assert result.num_rows == 3
        assert result.column_names == sample_table.column_names
        # Compare data
        assert result.to_pydict() == sample_table.to_pydict()

    def test_read_nonexistent_returns_none(
        self, cache_manager: ParquetCacheManager
    ) -> None:
        """Reading non-existent cache returns None."""
        result = cache_manager.read("nonexistent")
        assert result is None

    def test_is_valid_returns_true_within_expiry(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        utc: ZoneInfo,
    ) -> None:
        """is_valid returns True when cache is within expiry period."""
        now = datetime.now(utc)
        metadata = CacheMetadata(
            data_type="sq_dates",
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=now + timedelta(hours=24),
            schema_version=1,
            record_count=3,
        )
        cache_manager.write("sq_dates", sample_table, metadata)

        assert cache_manager.is_valid("sq_dates") is True

    def test_is_valid_returns_false_after_expiry(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        utc: ZoneInfo,
    ) -> None:
        """is_valid returns False when cache has expired."""
        past = datetime.now(utc) - timedelta(hours=48)
        expired = past + timedelta(hours=24)  # Still in the past
        metadata = CacheMetadata(
            data_type="sq_dates",
            source_url="https://example.com/data.xlsx",
            fetched_at=past,
            expires_at=expired,
            schema_version=1,
            record_count=3,
        )
        cache_manager.write("sq_dates", sample_table, metadata)

        assert cache_manager.is_valid("sq_dates") is False

    def test_is_valid_returns_false_for_nonexistent(
        self, cache_manager: ParquetCacheManager
    ) -> None:
        """is_valid returns False for non-existent cache."""
        assert cache_manager.is_valid("nonexistent") is False

    def test_clear_removes_specific_cache(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
    ) -> None:
        """clear(data_type) removes only the specified cache."""
        # Write two caches
        cache_manager.write("sq_dates", sample_table, sample_metadata)

        holiday_metadata = CacheMetadata(
            data_type="holiday_trading",
            source_url="https://example.com/holiday.xlsx",
            fetched_at=sample_metadata.fetched_at,
            expires_at=sample_metadata.expires_at,
            schema_version=1,
            record_count=5,
        )
        holiday_table = pa.table(
            {
                "date": [datetime(2026, 2, 11).date()],
                "holiday_name": ["建国記念の日"],
                "is_trading": [True],
                "is_confirmed": [True],
            }
        )
        cache_manager.write("holiday_trading", holiday_table, holiday_metadata)

        # Clear only sq_dates
        cache_manager.clear("sq_dates")

        # sq_dates should be gone
        assert cache_manager.read("sq_dates") is None
        # holiday_trading should remain
        assert cache_manager.read("holiday_trading") is not None

    def test_clear_all_removes_all_caches(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
    ) -> None:
        """clear() without argument removes all caches."""
        # Write cache
        cache_manager.write("sq_dates", sample_table, sample_metadata)

        # Clear all
        cache_manager.clear()

        assert cache_manager.read("sq_dates") is None

    def test_get_info_returns_cache_info(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
    ) -> None:
        """get_info returns CacheInfo with correct data."""
        cache_manager.write("sq_dates", sample_table, sample_metadata)

        info = cache_manager.get_info("sq_dates")

        assert info.data_type == "sq_dates"
        assert info.is_valid is True
        assert info.fetched_at == sample_metadata.fetched_at
        assert info.expires_at == sample_metadata.expires_at
        assert info.record_count == 3

    def test_get_info_for_nonexistent_cache(
        self, cache_manager: ParquetCacheManager, temp_cache_dir: Path
    ) -> None:
        """get_info for non-existent cache returns info with is_valid=False."""
        info = cache_manager.get_info("nonexistent")

        assert info.data_type == "nonexistent"
        assert info.is_valid is False
        assert info.fetched_at is None
        assert info.expires_at is None
        assert info.record_count is None

    def test_metadata_stored_in_parquet_file(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
        temp_cache_dir: Path,
    ) -> None:
        """Metadata is stored within the Parquet file's custom metadata."""
        cache_manager.write("sq_dates", sample_table, sample_metadata)

        # Read file directly to verify metadata storage
        parquet_path = temp_cache_dir / "sq_dates.parquet"
        table = pa.parquet.read_table(parquet_path)

        assert b"marketsched_metadata" in table.schema.metadata
        # Verify it's valid JSON that can be parsed back
        metadata_json = table.schema.metadata[b"marketsched_metadata"]
        restored = CacheMetadata.model_validate_json(metadata_json)
        assert restored.data_type == sample_metadata.data_type

    def test_custom_expiry_duration(self, temp_cache_dir: Path) -> None:
        """Cache manager respects custom expiry duration."""
        short_expiry = timedelta(minutes=30)
        manager = ParquetCacheManager(cache_dir=temp_cache_dir, expiry=short_expiry)

        assert manager.expiry == short_expiry

    def test_default_cache_dir(self) -> None:
        """Default cache directory is ~/.cache/marketsched/."""
        manager = ParquetCacheManager()
        expected = Path.home() / ".cache" / "marketsched"
        assert manager.cache_dir == expected

    def test_creates_cache_dir_if_not_exists(self, tmp_path: Path) -> None:
        """Cache directory is created if it doesn't exist."""
        new_cache_dir = tmp_path / "new" / "cache" / "dir"
        assert not new_cache_dir.exists()

        manager = ParquetCacheManager(cache_dir=new_cache_dir)
        table = pa.table({"col": [1, 2, 3]})
        metadata = CacheMetadata(
            data_type="test",
            source_url="https://example.com",
            fetched_at=datetime.now(timezone.utc),
            expires_at=datetime.now(timezone.utc) + timedelta(hours=1),
            schema_version=1,
            record_count=3,
        )

        manager.write("test", table, metadata)

        assert new_cache_dir.exists()
        assert (new_cache_dir / "test.parquet").exists()
