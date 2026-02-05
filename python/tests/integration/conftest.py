"""Shared fixtures and helpers for integration tests."""

from datetime import datetime
from io import BytesIO

from openpyxl import Workbook


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

    # Header row
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
