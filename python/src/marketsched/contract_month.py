"""ContractMonth value object for representing contract months.

A contract month (限月) is a fundamental identifier in futures and options trading.
This module provides the ContractMonth class for creating, parsing, and converting
contract months between different formats.

Example:
    >>> from marketsched import ContractMonth
    >>> cm = ContractMonth.parse("26年3月限")
    >>> cm.year
    2026
    >>> cm.month
    3
    >>> cm.to_yyyymm()
    '202603'
    >>> cm.to_japanese()
    '2026年3月限'
"""

from __future__ import annotations

import re
from functools import total_ordering
from typing_extensions import Self

from pydantic import BaseModel, ConfigDict, field_validator

from marketsched.exceptions import ContractMonthParseError


@total_ordering
class ContractMonth(BaseModel):
    """A value object representing a contract month (限月).

    ContractMonth is immutable (frozen) and can be used as a dict key or in sets.
    It supports comparison operators for sorting by chronological order.

    Attributes:
        year: The full year (e.g., 2026).
        month: The month (1-12).

    Example:
        >>> cm = ContractMonth(year=2026, month=3)
        >>> cm.to_japanese()
        '2026年3月限'
    """

    model_config = ConfigDict(frozen=True)

    year: int
    month: int

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        """Validate that year is non-negative."""
        if v < 0:
            msg = "year must be non-negative"
            raise ValueError(msg)
        return v

    @field_validator("month")
    @classmethod
    def validate_month(cls, v: int) -> int:
        """Validate that month is between 1 and 12."""
        if not 1 <= v <= 12:
            msg = "month must be between 1 and 12"
            raise ValueError(msg)
        return v

    @classmethod
    def parse(cls, text: str) -> Self:
        """Parse contract month from various string formats.

        Supported formats:
        - Japanese: '26年3月限', '2026年3月限'
        - YYYYMM: '202603'
        - YYYY-MM: '2026-03'

        For 2-digit years, the year is interpreted as 20xx (e.g., '99' -> 2099).

        Args:
            text: The string to parse.

        Returns:
            A ContractMonth instance.

        Raises:
            ContractMonthParseError: If the text cannot be parsed.

        Example:
            >>> ContractMonth.parse("26年3月限")
            ContractMonth(year=2026, month=3)
        """
        text = text.strip()

        # Try Japanese format: (2|4桁年)年(月)月限
        japanese_pattern = r"^(\d{2,4})年(\d{1,2})月限$"
        match = re.match(japanese_pattern, text)
        if match:
            year_str, month_str = match.groups()
            year = int(year_str)
            month = int(month_str)

            # Convert 2-digit year to 4-digit (20xx)
            if year < 100:
                year = 2000 + year

            return cls._create_or_raise(year, month, text)

        # Try YYYYMM format
        yyyymm_pattern = r"^(\d{4})(\d{2})$"
        match = re.match(yyyymm_pattern, text)
        if match:
            year_str, month_str = match.groups()
            year = int(year_str)
            month = int(month_str)
            return cls._create_or_raise(year, month, text)

        # Try YYYY-MM format
        yyyy_mm_pattern = r"^(\d{4})-(\d{2})$"
        match = re.match(yyyy_mm_pattern, text)
        if match:
            year_str, month_str = match.groups()
            year = int(year_str)
            month = int(month_str)
            return cls._create_or_raise(year, month, text)

        raise ContractMonthParseError(text)

    @classmethod
    def _create_or_raise(cls, year: int, month: int, original_text: str) -> Self:
        """Create ContractMonth or raise ContractMonthParseError on validation failure."""
        try:
            return cls(year=year, month=month)
        except ValueError as e:
            raise ContractMonthParseError(original_text) from e

    def to_yyyymm(self) -> str:
        """Convert to YYYYMM format string.

        Returns:
            A string in YYYYMM format (e.g., '202603').

        Example:
            >>> cm = ContractMonth(year=2026, month=3)
            >>> cm.to_yyyymm()
            '202603'
        """
        return f"{self.year}{self.month:02d}"

    def to_japanese(self) -> str:
        """Convert to Japanese format string.

        Returns:
            A string in Japanese format (e.g., '2026年3月限').

        Example:
            >>> cm = ContractMonth(year=2026, month=3)
            >>> cm.to_japanese()
            '2026年3月限'
        """
        return f"{self.year}年{self.month}月限"

    def __str__(self) -> str:
        """Return Japanese format string representation."""
        return self.to_japanese()

    def __repr__(self) -> str:
        """Return detailed string representation."""
        return f"ContractMonth(year={self.year}, month={self.month})"

    def __hash__(self) -> int:
        """Return hash based on year and month."""
        return hash((self.year, self.month))

    def __eq__(self, other: object) -> bool:
        """Check equality with another ContractMonth."""
        if not isinstance(other, ContractMonth):
            return NotImplemented
        return self.year == other.year and self.month == other.month

    def __lt__(self, other: object) -> bool:
        """Compare by chronological order (year, then month)."""
        if not isinstance(other, ContractMonth):
            return NotImplemented
        if self.year != other.year:
            return self.year < other.year
        return self.month < other.month
