"""Parquet cache manager for JPX market data.

This module provides functionality to read and write market data
(SQ dates, holiday trading days) in Parquet format.

Cache location: ~/.cache/marketsched/
"""

import json
import warnings
from datetime import date, datetime
from pathlib import Path
from typing import Any
from zoneinfo import ZoneInfo

import pyarrow as pa
import pyarrow.parquet as pq

from marketsched.exceptions import CacheNotAvailableError, InvalidDataFormatError
from marketsched.jpx.data import CacheMetadata

# Default cache directory
DEFAULT_CACHE_DIR = Path.home() / ".cache" / "marketsched"

# Cache validity period (24 hours)
CACHE_VALIDITY_HOURS = 24

# Parquet file names
SQ_DATES_FILE = "sq_dates.parquet"
HOLIDAYS_FILE = "holidays.parquet"
METADATA_FILE = "metadata.json"

# Expected schemas
SQ_DATES_SCHEMA = pa.schema(
    [
        ("year", pa.int32()),
        ("month", pa.int32()),
        ("sq_date", pa.date32()),
        ("product_type", pa.string()),
    ]
)

HOLIDAYS_SCHEMA = pa.schema(
    [
        ("date", pa.date32()),
        ("holiday_name", pa.string()),
        ("is_trading", pa.bool_()),
        ("is_confirmed", pa.bool_()),
    ]
)


class JPXDataCache:
    """Cache manager for JPX market data.

    Handles reading and writing of SQ dates and holiday trading data
    in Parquet format.

    Attributes:
        cache_dir: Path to the cache directory.
    """

    def __init__(self, cache_dir: Path | None = None) -> None:
        """Initialize the cache manager.

        Args:
            cache_dir: Custom cache directory. Defaults to ~/.cache/marketsched/.
        """
        self.cache_dir = cache_dir or DEFAULT_CACHE_DIR

    def _ensure_cache_dir(self) -> None:
        """Create cache directory if it doesn't exist."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    @property
    def sq_dates_path(self) -> Path:
        """Path to SQ dates Parquet file."""
        return self.cache_dir / SQ_DATES_FILE

    @property
    def holidays_path(self) -> Path:
        """Path to holidays Parquet file."""
        return self.cache_dir / HOLIDAYS_FILE

    @property
    def metadata_path(self) -> Path:
        """Path to metadata JSON file."""
        return self.cache_dir / METADATA_FILE

    def is_cache_available(self) -> bool:
        """Check if cache files exist and are valid.

        Returns:
            True if cache is available and not expired.

        Raises:
            InvalidDataFormatError: If cache metadata is corrupted.
        """
        if not self.metadata_path.exists():
            return False

        try:
            metadata = self.read_metadata()
            now = datetime.now(ZoneInfo("Asia/Tokyo"))
            return now < metadata.cache_valid_until
        except FileNotFoundError:
            return False
        # InvalidDataFormatError is intentionally NOT caught here.
        # Corrupted cache should be reported to the user, not silently ignored.

    def read_metadata(self) -> CacheMetadata:
        """Read cache metadata.

        Returns:
            CacheMetadata instance.

        Raises:
            CacheNotAvailableError: If metadata file doesn't exist.
            InvalidDataFormatError: If metadata format is invalid.
        """
        if not self.metadata_path.exists():
            raise CacheNotAvailableError(
                "キャッシュが存在しません。`mks cache update` を実行してください。"
            )

        try:
            with self.metadata_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return CacheMetadata.model_validate(data)
        except (json.JSONDecodeError, ValueError) as e:
            raise InvalidDataFormatError(
                f"メタデータファイルの形式が不正です: {e}"
            ) from e

    def write_metadata(self, metadata: CacheMetadata) -> None:
        """Write cache metadata.

        Args:
            metadata: CacheMetadata instance to write.
        """
        self._ensure_cache_dir()
        with self.metadata_path.open("w", encoding="utf-8") as f:
            json.dump(metadata.model_dump(mode="json"), f, ensure_ascii=False, indent=2)

    def _validate_schema(
        self, table: pa.Table, expected_schema: pa.Schema, file_name: str
    ) -> None:
        """Validate that table schema matches expected schema.

        Args:
            table: PyArrow table to validate.
            expected_schema: Expected schema.
            file_name: File name for error message.

        Raises:
            InvalidDataFormatError: If schema doesn't match.
        """
        for field in expected_schema:
            if field.name not in table.schema.names:
                raise InvalidDataFormatError(
                    f"{file_name}: 必須カラム '{field.name}' がありません"
                )

    def read_sq_dates(self) -> list[dict[str, Any]]:
        """Read SQ dates from cache.

        Returns:
            List of SQ date records.

        Raises:
            CacheNotAvailableError: If cache doesn't exist.
            InvalidDataFormatError: If data format is invalid.
        """
        if not self.sq_dates_path.exists():
            raise CacheNotAvailableError(
                "SQ日データのキャッシュが存在しません。`mks cache update` を実行してください。"
            )

        try:
            table = pq.read_table(self.sq_dates_path)
            self._validate_schema(table, SQ_DATES_SCHEMA, SQ_DATES_FILE)
            result: list[dict[str, Any]] = table.to_pylist()
            return result
        except pa.ArrowInvalid as e:
            raise InvalidDataFormatError(f"SQ日データの形式が不正です: {e}") from e

    def write_sq_dates(self, records: list[dict[str, Any]]) -> None:
        """Write SQ dates to cache.

        Args:
            records: List of SQ date records with keys:
                - year: int
                - month: int
                - sq_date: date
                - product_type: str
        """
        self._ensure_cache_dir()
        table = pa.Table.from_pylist(records, schema=SQ_DATES_SCHEMA)
        pq.write_table(table, self.sq_dates_path)

    def read_holidays(self) -> list[dict[str, Any]]:
        """Read holiday trading data from cache.

        Returns:
            List of holiday trading records.

        Raises:
            CacheNotAvailableError: If cache doesn't exist.
            InvalidDataFormatError: If data format is invalid.
        """
        if not self.holidays_path.exists():
            raise CacheNotAvailableError(
                "休業日データのキャッシュが存在しません。`mks cache update` を実行してください。"
            )

        try:
            table = pq.read_table(self.holidays_path)
            self._validate_schema(table, HOLIDAYS_SCHEMA, HOLIDAYS_FILE)
            result: list[dict[str, Any]] = table.to_pylist()
            return result
        except pa.ArrowInvalid as e:
            raise InvalidDataFormatError(f"休業日データの形式が不正です: {e}") from e

    def write_holidays(self, records: list[dict[str, Any]]) -> None:
        """Write holiday trading data to cache.

        Args:
            records: List of holiday records with keys:
                - date: date
                - holiday_name: str
                - is_trading: bool
                - is_confirmed: bool
        """
        self._ensure_cache_dir()
        table = pa.Table.from_pylist(records, schema=HOLIDAYS_SCHEMA)
        pq.write_table(table, self.holidays_path)

    def clear(self) -> None:
        """Clear all cache files."""
        for path in [self.sq_dates_path, self.holidays_path, self.metadata_path]:
            if path.exists():
                path.unlink()

    def get_sq_date(
        self, year: int, month: int, product_type: str = "index"
    ) -> date | None:
        """Get SQ date for specific year and month.

        Args:
            year: Year.
            month: Month (1-12).
            product_type: Product type (default: "index").

        Returns:
            SQ date or None if not found.

        Raises:
            CacheNotAvailableError: If cache doesn't exist.
        """
        records = self.read_sq_dates()
        for record in records:
            if (
                record["year"] == year
                and record["month"] == month
                and record["product_type"] == product_type
            ):
                sq_date: date = record["sq_date"]
                return sq_date
        return None

    def get_sq_dates_for_year(
        self, year: int, product_type: str = "index"
    ) -> list[date]:
        """Get all SQ dates for a year.

        Args:
            year: Year.
            product_type: Product type (default: "index").

        Returns:
            List of SQ dates in ascending order.

        Raises:
            CacheNotAvailableError: If cache doesn't exist.
        """
        records = self.read_sq_dates()
        dates = [
            record["sq_date"]
            for record in records
            if record["year"] == year and record["product_type"] == product_type
        ]
        return sorted(dates)

    def is_holiday_trading_day(self, d: date) -> bool:
        """Check if a date is a holiday trading day.

        Args:
            d: Date to check.

        Returns:
            True if the date is a holiday trading day.

        Raises:
            CacheNotAvailableError: If cache doesn't exist.
        """
        records = self.read_holidays()
        return any(record["date"] == d and record["is_trading"] for record in records)

    def is_holiday(self, d: date) -> bool:
        """Check if a date is a holiday (including non-trading holidays).

        Args:
            d: Date to check.

        Returns:
            True if the date is a holiday.

        Raises:
            CacheNotAvailableError: If cache doesn't exist.
        """
        records = self.read_holidays()
        return any(record["date"] == d for record in records)

    def get_non_trading_holidays(self) -> set[date]:
        """Get set of non-trading holiday dates.

        Returns:
            Set of dates that are holidays and NOT trading days.

        Raises:
            CacheNotAvailableError: If cache doesn't exist.
        """
        records = self.read_holidays()
        return {record["date"] for record in records if not record["is_trading"]}


# Global cache instance
_cache: JPXDataCache | None = None


def get_cache(cache_dir: Path | None = None) -> JPXDataCache:
    """Get the global cache instance.

    Args:
        cache_dir: Custom cache directory (only used on first call).
            If the cache is already initialized and cache_dir is provided,
            a warning will be issued and the argument will be ignored.

    Returns:
        JPXDataCache instance.
    """
    global _cache
    if _cache is None:
        _cache = JPXDataCache(cache_dir)
    elif cache_dir is not None:
        warnings.warn(
            f"キャッシュは既に初期化されています。cache_dir={cache_dir} は無視されます。",
            UserWarning,
            stacklevel=2,
        )
    return _cache
