"""Integration tests for JPX data fetcher (T024)."""

from datetime import date, datetime
from io import BytesIO

import httpx
import pytest
from openpyxl import Workbook
from pytest_httpx import HTTPXMock

from marketsched.contract_month import ContractMonth
from marketsched.exceptions import DataFetchError, InvalidDataFormatError
from marketsched.jpx.data.fetcher import JPXDataFetcher

from .conftest import create_holiday_trading_excel, create_sq_dates_excel


class TestJPXDataFetcherSQDates:
    """Tests for SQ date fetching."""

    def test_fetch_sq_dates_success(self, httpx_mock: HTTPXMock) -> None:
        """Successfully fetches and parses SQ dates from Excel."""
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
        assert records[0].contract_month == ContractMonth(year=2026, month=1)
        assert records[0].last_trading_day == date(2026, 1, 8)
        assert records[0].sq_date == date(2026, 1, 9)
        assert records[0].product_category == "index_futures_options"

    def test_fetch_sq_dates_filters_by_product(self, httpx_mock: HTTPXMock) -> None:
        """Only extracts SQ dates from 日経225オプション rows."""
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

        assert len(records) == 1
        assert records[0].contract_month == ContractMonth(year=2026, month=3)

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
        assert records[0].contract_month == ContractMonth(year=2026, month=3)
        assert records[1].contract_month == ContractMonth(year=2027, month=3)

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

        assert records[0].date == date(2026, 2, 11)
        assert records[0].holiday_name == "建国記念の日"
        assert records[0].is_trading is True

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

    def test_empty_sq_data_raises_error(self, httpx_mock: HTTPXMock) -> None:
        """Empty data (header only) raises InvalidDataFormatError."""
        excel_data = create_sq_dates_excel([])

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=excel_data,
        )

        fetcher = JPXDataFetcher()

        with pytest.raises(InvalidDataFormatError) as exc_info:
            fetcher.fetch_sq_dates(years=[2026])

        assert "No SQ date records found" in str(exc_info.value)

    def test_empty_holiday_data_raises_error(self, httpx_mock: HTTPXMock) -> None:
        """Empty holiday data raises InvalidDataFormatError."""
        excel_data = create_holiday_trading_excel([])

        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx",
            content=excel_data,
        )

        fetcher = JPXDataFetcher()

        with pytest.raises(InvalidDataFormatError) as exc_info:
            fetcher.fetch_holiday_trading()

        assert "No holiday trading records found" in str(exc_info.value)


class TestHTTPErrors:
    """Tests for HTTP error responses."""

    def test_http_404_raises_data_fetch_error(self, httpx_mock: HTTPXMock) -> None:
        """HTTP 404 response raises DataFetchError."""
        httpx_mock.add_response(status_code=404)

        fetcher = JPXDataFetcher()
        with pytest.raises(DataFetchError):
            fetcher.fetch_sq_dates(years=[2026])

    def test_http_500_raises_data_fetch_error(self, httpx_mock: HTTPXMock) -> None:
        """HTTP 500 response raises DataFetchError."""
        httpx_mock.add_response(status_code=500)

        fetcher = JPXDataFetcher()
        with pytest.raises(DataFetchError):
            fetcher.fetch_sq_dates(years=[2026])

    def test_non_excel_content_raises_error(self, httpx_mock: HTTPXMock) -> None:
        """Non-Excel content (e.g., HTML error page) raises InvalidDataFormatError."""
        httpx_mock.add_response(
            url="https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx",
            content=b"<html><body>Not Found</body></html>",
        )

        fetcher = JPXDataFetcher()
        with pytest.raises(InvalidDataFormatError, match="Failed to load Excel"):
            fetcher.fetch_sq_dates(years=[2026])
