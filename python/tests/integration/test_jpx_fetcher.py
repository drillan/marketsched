"""Integration tests for JPX data fetcher (T024)."""

from datetime import date, datetime
from io import BytesIO

import httpx
import pytest
from openpyxl import Workbook
from pytest_httpx import HTTPXMock

from marketsched.exceptions import DataFetchError, InvalidDataFormatError
from marketsched.jpx.data.fetcher import JPXDataFetcher


def create_sq_dates_excel(
    records: list[tuple[str, datetime, datetime, datetime | str]],
) -> bytes:
    """Create a mock SQ dates Excel file.

    Args:
        records: List of (product_name, contract_month, last_trading_day, exercise_date).
                 exercise_date can be datetime or '-' for products without it.

    Returns:
        Excel file content as bytes.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "2026"

    # Header row (row 2 in actual file, but we start at row 1 for simplicity)
    ws.append(
        [
            None,
            "商品",
            "限月取引",
            "9桁コード",
            "限月コード下2桁",
            "取引最終日",
            "権利行使日",
        ]
    )

    for product, contract_month, last_trading_day, exercise_date in records:
        ws.append(
            [
                None,
                product,
                contract_month,
                123456789,
                "-",
                last_trading_day,
                exercise_date,
            ]
        )

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


def create_holiday_trading_excel(records: list[tuple[datetime, str, str]]) -> bytes:
    """Create a mock holiday trading Excel file.

    Args:
        records: List of (date, holiday_name, status).
                 status should be "実施する" or "実施しない".

    Returns:
        Excel file content as bytes.
    """
    wb = Workbook()
    ws = wb.active
    ws.title = "祝日取引日"

    # Header row
    ws.append(["祝日取引の対象日", "名称", "実施有無"])

    for holiday_date, name, status in records:
        ws.append([holiday_date, name, status])

    buffer = BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return buffer.read()


class TestJPXDataFetcherSQDates:
    """Tests for SQ date fetching."""

    def test_fetch_sq_dates_success(self, httpx_mock: HTTPXMock) -> None:
        """Successfully fetches and parses SQ dates from Excel."""
        # Create mock Excel with 日経225オプション data (has exercise dates)
        excel_data = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2026, 1, 1),
                    datetime(2026, 1, 8),
                    datetime(2026, 1, 9),
                ),
                (
                    "日経225オプション",
                    datetime(2026, 2, 1),
                    datetime(2026, 2, 12),
                    datetime(2026, 2, 13),
                ),
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=excel_data,
        )

        fetcher = JPXDataFetcher()
        records = fetcher.fetch_sq_dates(years=[2026])

        assert len(records) == 3
        assert records[0].contract_month == "202601"
        assert records[0].last_trading_day == date(2026, 1, 8)
        assert records[0].sq_date == date(2026, 1, 9)
        assert records[0].product_category == "index_futures_options"

    def test_fetch_sq_dates_filters_by_product(self, httpx_mock: HTTPXMock) -> None:
        """Only extracts SQ dates from 日経225オプション rows."""
        # Mix of products - only 日経225オプション has exercise dates
        excel_data = create_sq_dates_excel(
            [
                ("日経225先物", datetime(2026, 3, 1), datetime(2026, 3, 12), "-"),
                ("日経225mini", datetime(2026, 3, 1), datetime(2026, 3, 12), "-"),
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=excel_data,
        )

        fetcher = JPXDataFetcher()
        records = fetcher.fetch_sq_dates(years=[2026])

        # Should only get the オプション row
        assert len(records) == 1
        assert records[0].contract_month == "202603"

    def test_fetch_sq_dates_multiple_years(self, httpx_mock: HTTPXMock) -> None:
        """Can fetch data for multiple years."""
        excel_2026 = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2026, 3, 1),
                    datetime(2026, 3, 12),
                    datetime(2026, 3, 13),
                ),
            ]
        )
        excel_2027 = create_sq_dates_excel(
            [
                (
                    "日経225オプション",
                    datetime(2027, 3, 1),
                    datetime(2027, 3, 11),
                    datetime(2027, 3, 12),
                ),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=excel_2026,
        )
        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2027_indexfutures_options_1_j.xlsx",
            content=excel_2027,
        )

        fetcher = JPXDataFetcher()
        records = fetcher.fetch_sq_dates(years=[2026, 2027])

        assert len(records) == 2
        assert records[0].contract_month == "202603"
        assert records[1].contract_month == "202703"

    def test_fetch_sq_dates_network_error_raises_data_fetch_error(
        self, httpx_mock: HTTPXMock
    ) -> None:
        """Network errors raise DataFetchError."""
        httpx_mock.add_exception(httpx.ConnectError("Connection refused"))

        fetcher = JPXDataFetcher()

        with pytest.raises(DataFetchError) as exc_info:
            fetcher.fetch_sq_dates(years=[2026])

        assert "2026_indexfutures_options_1_j.xlsx" in str(exc_info.value)


class TestJPXDataFetcherHolidayTrading:
    """Tests for holiday trading data fetching."""

    def test_fetch_holiday_trading_success(self, httpx_mock: HTTPXMock) -> None:
        """Successfully fetches and parses holiday trading data."""
        excel_data = create_holiday_trading_excel(
            [
                (datetime(2026, 2, 11), "建国記念の日", "実施する"),
                (datetime(2026, 2, 23), "天皇誕生日", "実施する"),
                (datetime(2026, 3, 20), "春分の日", "実施しない"),
            ]
        )

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
            content=excel_data,
        )

        fetcher = JPXDataFetcher()
        records = fetcher.fetch_holiday_trading()

        assert len(records) == 3

        # Check trading holiday
        assert records[0].date == date(2026, 2, 11)
        assert records[0].holiday_name == "建国記念の日"
        assert records[0].is_trading is True

        # Check non-trading holiday
        assert records[2].date == date(2026, 3, 20)
        assert records[2].is_trading is False

    def test_fetch_holiday_trading_network_error(self, httpx_mock: HTTPXMock) -> None:
        """Network errors raise DataFetchError."""
        httpx_mock.add_exception(httpx.TimeoutException("Request timed out"))

        fetcher = JPXDataFetcher()

        with pytest.raises(DataFetchError) as exc_info:
            fetcher.fetch_holiday_trading()

        assert "nlsgeu000006jgee.xlsx" in str(exc_info.value)


class TestSchemaValidation:
    """Tests for schema validation (T024b)."""

    def test_sq_dates_invalid_format_raises_error(self, httpx_mock: HTTPXMock) -> None:
        """Invalid Excel format raises InvalidDataFormatError."""
        # Create Excel without required columns
        wb = Workbook()
        ws = wb.active
        ws.append(["Wrong", "Columns", "Here"])
        ws.append(["data1", "data2", "data3"])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=buffer.read(),
        )

        fetcher = JPXDataFetcher()

        with pytest.raises(InvalidDataFormatError):
            fetcher.fetch_sq_dates(years=[2026])

    def test_holiday_trading_invalid_format_raises_error(
        self, httpx_mock: HTTPXMock
    ) -> None:
        """Invalid Excel format raises InvalidDataFormatError."""
        # Create Excel without required columns
        wb = Workbook()
        ws = wb.active
        ws.append(["Wrong", "Columns"])
        ws.append(["data1", "data2"])

        buffer = BytesIO()
        wb.save(buffer)
        buffer.seek(0)

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
            content=buffer.read(),
        )

        fetcher = JPXDataFetcher()

        with pytest.raises(InvalidDataFormatError):
            fetcher.fetch_holiday_trading()

    def test_empty_data_raises_error(self, httpx_mock: HTTPXMock) -> None:
        """Empty data (header only) raises InvalidDataFormatError."""
        # Create Excel with header but no data rows
        excel_data = create_sq_dates_excel([])

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=excel_data,
        )

        fetcher = JPXDataFetcher()

        with pytest.raises(InvalidDataFormatError) as exc_info:
            fetcher.fetch_sq_dates(years=[2026])

        assert "No SQ date records found" in str(exc_info.value)
