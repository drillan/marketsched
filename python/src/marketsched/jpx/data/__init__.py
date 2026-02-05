"""JPX data models and cache infrastructure.

This module defines the data models for JPX market data and provides
cache functionality for storing data in Parquet format.
"""

from pathlib import Path

from pydantic import AwareDatetime, BaseModel


class CacheMetadata(BaseModel):
    """Metadata for cache state management.

    All datetime fields require timezone information (AwareDatetime)
    to comply with Constitution III (no naive datetimes).
    """

    last_updated: AwareDatetime
    version: str
    source_urls: dict[str, str]
    cache_valid_until: AwareDatetime


class CacheInfo(BaseModel):
    """Cache status information for CLI output."""

    market: str
    last_updated: AwareDatetime | None
    is_valid: bool
    size_bytes: int
    cache_path: Path


__all__ = ["CacheMetadata", "CacheInfo"]
