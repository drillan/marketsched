"""Unit tests for JPX data fetcher parser methods."""

from datetime import date, datetime

import pytest

from marketsched.contract_month import ContractMonth
from marketsched.exceptions import InvalidDataFormatError
from marketsched.jpx.data.fetcher import JPXDataFetcher


class TestParseContractMonth:
    """Tests for _parse_contract_month method."""

    def test_parse_from_datetime(self) -> None:
        """Parse contract month from datetime."""
        fetcher = JPXDataFetcher()
        result = fetcher._parse_contract_month(datetime(2026, 3, 15))
        assert result == ContractMonth(year=2026, month=3)

    def test_parse_from_date(self) -> None:
        """Parse contract month from date."""
        fetcher = JPXDataFetcher()
        result = fetcher._parse_contract_month(date(2026, 3, 1))
        assert result == ContractMonth(year=2026, month=3)

    def test_parse_none_raises_error(self) -> None:
        """None value raises InvalidDataFormatError."""
        fetcher = JPXDataFetcher()
        with pytest.raises(
            InvalidDataFormatError, match="Contract month value is None"
        ):
            fetcher._parse_contract_month(None)

    def test_parse_string_raises_error(self) -> None:
        """String value raises InvalidDataFormatError."""
        fetcher = JPXDataFetcher()
        with pytest.raises(
            InvalidDataFormatError, match="Unexpected contract month type: str"
        ):
            fetcher._parse_contract_month("202603")

    def test_parse_int_raises_error(self) -> None:
        """Int value raises InvalidDataFormatError."""
        fetcher = JPXDataFetcher()
        with pytest.raises(
            InvalidDataFormatError, match="Unexpected contract month type: int"
        ):
            fetcher._parse_contract_month(202603)  # type: ignore[arg-type]


class TestParseDate:
    """Tests for _parse_date method."""

    def test_parse_from_datetime(self) -> None:
        """Parse date from datetime."""
        fetcher = JPXDataFetcher()
        result = fetcher._parse_date(datetime(2026, 3, 13, 10, 30))
        assert result == date(2026, 3, 13)

    def test_parse_from_date(self) -> None:
        """Parse date from date object."""
        fetcher = JPXDataFetcher()
        result = fetcher._parse_date(date(2026, 3, 13))
        assert result == date(2026, 3, 13)

    def test_parse_none_raises_error(self) -> None:
        """None value raises InvalidDataFormatError."""
        fetcher = JPXDataFetcher()
        with pytest.raises(InvalidDataFormatError, match="Date value is None"):
            fetcher._parse_date(None)

    def test_parse_dash_raises_error(self) -> None:
        """Dash string raises InvalidDataFormatError."""
        fetcher = JPXDataFetcher()
        with pytest.raises(InvalidDataFormatError, match="Date value is '-'"):
            fetcher._parse_date("-")

    def test_parse_unknown_string_raises_error(self) -> None:
        """Unknown string raises InvalidDataFormatError."""
        fetcher = JPXDataFetcher()
        with pytest.raises(
            InvalidDataFormatError, match="Cannot parse date from string"
        ):
            fetcher._parse_date("2026-03-13")

    def test_parse_int_raises_error(self) -> None:
        """Int value raises InvalidDataFormatError."""
        fetcher = JPXDataFetcher()
        with pytest.raises(InvalidDataFormatError, match="Unexpected date type: int"):
            fetcher._parse_date(20260313)  # type: ignore[arg-type]
