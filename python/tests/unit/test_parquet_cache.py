"""Unit tests for Parquet cache manager (T022).

ruff: noqa: ARG002
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pyarrow as pa
import pyarrow.parquet as pq
import pytest

from marketsched.jpx.data import CacheMetadata, DataType
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
            data_type=DataType.SQ_DATES,
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
        cache_manager.write(DataType.SQ_DATES, sample_table, sample_metadata)

        result = cache_manager.read(DataType.SQ_DATES)

        assert result is not None
        assert result.num_rows == 3
        assert result.column_names == sample_table.column_names
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
            data_type=DataType.SQ_DATES,
            source_url="https://example.com/data.xlsx",
            fetched_at=now,
            expires_at=now + timedelta(hours=24),
            schema_version=1,
            record_count=3,
        )
        cache_manager.write(DataType.SQ_DATES, sample_table, metadata)

        assert cache_manager.is_valid(DataType.SQ_DATES) is True

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
            data_type=DataType.SQ_DATES,
            source_url="https://example.com/data.xlsx",
            fetched_at=past,
            expires_at=expired,
            schema_version=1,
            record_count=3,
        )
        cache_manager.write(DataType.SQ_DATES, sample_table, metadata)

        assert cache_manager.is_valid(DataType.SQ_DATES) is False

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
        cache_manager.write(DataType.SQ_DATES, sample_table, sample_metadata)

        holiday_metadata = CacheMetadata(
            data_type=DataType.HOLIDAY_TRADING,
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
        cache_manager.write(DataType.HOLIDAY_TRADING, holiday_table, holiday_metadata)

        cache_manager.clear(DataType.SQ_DATES)

        assert cache_manager.read(DataType.SQ_DATES) is None
        assert cache_manager.read(DataType.HOLIDAY_TRADING) is not None

    def test_clear_all_removes_all_caches(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
    ) -> None:
        """clear() without argument removes all caches."""
        cache_manager.write(DataType.SQ_DATES, sample_table, sample_metadata)

        cache_manager.clear()

        assert cache_manager.read(DataType.SQ_DATES) is None

    def test_get_info_returns_cache_info(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
    ) -> None:
        """get_info returns CacheInfo with correct data."""
        cache_manager.write(DataType.SQ_DATES, sample_table, sample_metadata)

        info = cache_manager.get_info(DataType.SQ_DATES)

        assert info.data_type == DataType.SQ_DATES
        assert info.is_valid is True
        assert info.fetched_at == sample_metadata.fetched_at
        assert info.expires_at == sample_metadata.expires_at
        assert info.record_count == 3

    def test_get_info_for_nonexistent_cache(
        self, cache_manager: ParquetCacheManager, temp_cache_dir: Path
    ) -> None:
        """get_info for non-existent cache returns info with is_valid=False."""
        info = cache_manager.get_info(DataType.SQ_DATES)

        assert info.data_type == DataType.SQ_DATES
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
        cache_manager.write(DataType.SQ_DATES, sample_table, sample_metadata)

        parquet_path = temp_cache_dir / "sq_dates.parquet"
        table = pa.parquet.read_table(parquet_path)

        assert b"marketsched_metadata" in table.schema.metadata
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
            data_type=DataType.SQ_DATES,
            source_url="https://example.com",
            fetched_at=datetime.now(UTC),
            expires_at=datetime.now(UTC) + timedelta(hours=1),
            schema_version=1,
            record_count=3,
        )

        manager.write(DataType.SQ_DATES, table, metadata)

        assert new_cache_dir.exists()
        assert (new_cache_dir / "sq_dates.parquet").exists()

    def test_write_rejects_data_type_mismatch(
        self,
        cache_manager: ParquetCacheManager,
        sample_table: pa.Table,
        sample_metadata: CacheMetadata,
    ) -> None:
        """write() rejects mismatched data_type and metadata.data_type."""
        with pytest.raises(ValueError, match="data_type mismatch"):
            cache_manager.write(DataType.HOLIDAY_TRADING, sample_table, sample_metadata)

    def test_read_metadata_returns_none_for_no_metadata_key(
        self, cache_manager: ParquetCacheManager, temp_cache_dir: Path
    ) -> None:
        """_read_metadata returns None when Parquet has no marketsched metadata key."""
        table = pa.table({"col": [1, 2, 3]})
        table = table.replace_schema_metadata({b"other_key": b"value"})
        pq.write_table(table, temp_cache_dir / "sq_dates.parquet")

        result = cache_manager._read_metadata(DataType.SQ_DATES)
        assert result is None

    def test_read_metadata_returns_none_for_no_schema_metadata(
        self, cache_manager: ParquetCacheManager, temp_cache_dir: Path
    ) -> None:
        """_read_metadata returns None when Parquet has no schema metadata at all."""
        table = pa.table({"col": [1, 2, 3]})
        pq.write_table(table, temp_cache_dir / "sq_dates.parquet")

        result = cache_manager._read_metadata(DataType.SQ_DATES)
        assert result is None

    def test_falsy_expiry_is_not_replaced_by_default(
        self, temp_cache_dir: Path
    ) -> None:
        """timedelta(0) is preserved, not replaced by default expiry."""
        zero_expiry = timedelta(0)
        manager = ParquetCacheManager(cache_dir=temp_cache_dir, expiry=zero_expiry)
        assert manager.expiry == zero_expiry
