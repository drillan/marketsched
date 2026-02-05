"""Parquet cache manager for JPX data.

This module provides a cache manager that stores data in Parquet format
with metadata for expiration tracking.

Example:
    >>> from marketsched.jpx.data.cache import ParquetCacheManager
    >>> manager = ParquetCacheManager()
    >>> if manager.is_valid("sq_dates"):
    ...     table = manager.read("sq_dates")
"""

from datetime import UTC, datetime, timedelta
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from marketsched.jpx.data import CacheInfo, CacheMetadata, DataType

__all__ = ["ParquetCacheManager"]


class ParquetCacheManager:
    """Manages Parquet-based cache for JPX market data.

    This class handles reading, writing, and validating cached data.
    Metadata is stored within the Parquet file's custom metadata field.

    Attributes:
        cache_dir: Directory where cache files are stored.
        expiry: Duration after which cache is considered expired.

    Example:
        >>> manager = ParquetCacheManager()
        >>> table = manager.read("sq_dates")
        >>> if table is None:
        ...     # Fetch and cache new data
        ...     pass
    """

    DEFAULT_CACHE_DIR = Path.home() / ".cache" / "marketsched"
    DEFAULT_EXPIRY = timedelta(hours=24)
    METADATA_KEY = b"marketsched_metadata"

    def __init__(
        self,
        cache_dir: Path | None = None,
        expiry: timedelta | None = None,
    ) -> None:
        """Initialize the cache manager.

        Args:
            cache_dir: Directory for cache files. Defaults to ~/.cache/marketsched/.
            expiry: Cache expiration duration. Defaults to 24 hours.
        """
        self._cache_dir = cache_dir if cache_dir is not None else self.DEFAULT_CACHE_DIR
        self._expiry = expiry if expiry is not None else self.DEFAULT_EXPIRY

    @property
    def cache_dir(self) -> Path:
        """Return the cache directory path."""
        return self._cache_dir

    @property
    def expiry(self) -> timedelta:
        """Return the cache expiry duration."""
        return self._expiry

    def _get_cache_path(self, data_type: DataType | str) -> Path:
        """Get the file path for a cache type."""
        return self._cache_dir / f"{data_type}.parquet"

    def read(self, data_type: DataType | str) -> pa.Table | None:
        """Read cached data from Parquet file.

        Args:
            data_type: Type identifier (e.g., DataType.SQ_DATES).

        Returns:
            PyArrow Table with the cached data, or None if cache doesn't exist.
        """
        cache_path = self._get_cache_path(data_type)
        if not cache_path.exists():
            return None

        return pq.read_table(cache_path)

    def write(
        self,
        data_type: DataType | str,
        table: pa.Table,
        metadata: CacheMetadata,
    ) -> None:
        """Write data to cache with metadata.

        The metadata is stored in the Parquet file's custom metadata field.

        Args:
            data_type: Type identifier (e.g., DataType.SQ_DATES).
            table: PyArrow Table containing the data to cache.
            metadata: CacheMetadata with fetch and expiry information.

        Raises:
            ValueError: If data_type does not match metadata.data_type.
        """
        data_type_str = str(data_type)
        metadata_type_str = str(metadata.data_type)
        if data_type_str != metadata_type_str:
            msg = f"data_type mismatch: argument={data_type_str}, metadata={metadata_type_str}"
            raise ValueError(msg)

        self._cache_dir.mkdir(parents=True, exist_ok=True)

        existing_metadata = table.schema.metadata or {}
        new_metadata = {
            **existing_metadata,
            self.METADATA_KEY: metadata.model_dump_json().encode(),
        }
        table = table.replace_schema_metadata(new_metadata)

        cache_path = self._get_cache_path(data_type)
        pq.write_table(table, cache_path)

    def _read_metadata(self, data_type: DataType | str) -> CacheMetadata | None:
        """Read metadata from cached Parquet file.

        Uses pq.read_schema to read only the file footer, avoiding
        loading the entire dataset into memory.

        Args:
            data_type: Type identifier.

        Returns:
            CacheMetadata if cache exists and has metadata, None otherwise.
        """
        cache_path = self._get_cache_path(data_type)
        if not cache_path.exists():
            return None

        schema = pq.read_schema(cache_path)
        if schema.metadata is None:
            return None

        metadata_json = schema.metadata.get(self.METADATA_KEY)
        if metadata_json is None:
            return None

        return CacheMetadata.model_validate_json(metadata_json)

    def is_valid(self, data_type: DataType | str) -> bool:
        """Check if cache exists and is within expiry period.

        Args:
            data_type: Type identifier (e.g., DataType.SQ_DATES).

        Returns:
            True if cache exists and hasn't expired, False otherwise.
        """
        metadata = self._read_metadata(data_type)
        if metadata is None:
            return False

        now = datetime.now(UTC)
        return now < metadata.expires_at

    def get_info(self, data_type: DataType | str) -> CacheInfo:
        """Get information about a cache entry.

        Args:
            data_type: Type identifier (e.g., DataType.SQ_DATES).

        Returns:
            CacheInfo with cache status and metadata.
        """
        cache_path = self._get_cache_path(data_type)
        metadata = self._read_metadata(data_type)

        data_type_enum = (
            DataType(data_type) if isinstance(data_type, str) else data_type
        )

        if metadata is None:
            return CacheInfo(
                data_type=data_type_enum,
                cache_path=str(cache_path),
                is_valid=False,
                fetched_at=None,
                expires_at=None,
                record_count=None,
            )

        now = datetime.now(UTC)
        is_valid = now < metadata.expires_at

        return CacheInfo(
            data_type=data_type_enum,
            cache_path=str(cache_path),
            is_valid=is_valid,
            fetched_at=metadata.fetched_at,
            expires_at=metadata.expires_at,
            record_count=metadata.record_count,
        )

    def clear(self, data_type: DataType | str | None = None) -> None:
        """Clear cached data.

        Args:
            data_type: Type to clear. If None, clears all caches.
        """
        if data_type is not None:
            cache_path = self._get_cache_path(data_type)
            if cache_path.exists():
                cache_path.unlink()
        else:
            if self._cache_dir.exists():
                for parquet_file in self._cache_dir.glob("*.parquet"):
                    parquet_file.unlink()
