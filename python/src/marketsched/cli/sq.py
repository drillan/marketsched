"""SQ date (sq) CLI subcommand.

Commands:
- get: Get SQ date for a year-month
- list: List SQ dates for a year
- is: Check if date is an SQ date
"""

import re
from datetime import date
from typing import Annotated

import typer

from marketsched.cli.main import (
    format_output,
    get_format_from_ctx,
    get_market_from_ctx,
)

sq_app = typer.Typer(no_args_is_help=True)


def parse_year_month(args: list[str]) -> tuple[int, int]:
    """Parse year-month from various formats.

    Supported formats:
    - Two arguments: "2026" "3"
    - YYYYMM: "202603"
    - YYYY-MM: "2026-03"
    """
    if len(args) == 2:
        # Two argument format: year month
        try:
            year = int(args[0])
            month = int(args[1])
        except ValueError as e:
            raise typer.BadParameter(f"Invalid year/month: {args[0]} {args[1]}") from e
    elif len(args) == 1:
        arg = args[0]
        # Try YYYYMM format
        if re.match(r"^\d{6}$", arg):
            year = int(arg[:4])
            month = int(arg[4:6])
        # Try YYYY-MM format
        elif re.match(r"^\d{4}-\d{2}$", arg):
            parts = arg.split("-")
            year = int(parts[0])
            month = int(parts[1])
        else:
            raise typer.BadParameter(
                f"Invalid format: {arg}. Use YYYY MM, YYYYMM, or YYYY-MM."
            )
    else:
        raise typer.BadParameter("Specify year-month as: YYYY MM, YYYYMM, or YYYY-MM")

    # Validate month
    if not 1 <= month <= 12:
        raise typer.BadParameter(f"Invalid month: {month}. Must be 1-12.")

    return year, month


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return date.fromisoformat(date_str)
    except ValueError as e:
        raise typer.BadParameter(
            f"Invalid date format: {date_str}. Use YYYY-MM-DD."
        ) from e


@sq_app.command("get")
def sq_get(
    ctx: typer.Context,
    year_month: Annotated[
        list[str],
        typer.Argument(help="Year-month: YYYY MM, YYYYMM, or YYYY-MM"),
    ],
) -> None:
    """Get the SQ date for a year-month."""
    year, month = parse_year_month(year_month)
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    sq_date = market.get_sq_date(year, month)
    result = {
        "year": year,
        "month": month,
        "sq_date": sq_date.isoformat(),
    }
    typer.echo(format_output(result, fmt))


@sq_app.command("list")
def sq_list(
    ctx: typer.Context,
    year: Annotated[int, typer.Argument(help="Year to list SQ dates for")],
) -> None:
    """List all SQ dates for a year."""
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    sq_dates = market.get_sq_dates_for_year(year)
    result = {
        "year": year,
        "sq_dates": [d.isoformat() for d in sq_dates],
    }
    typer.echo(format_output(result, fmt))


@sq_app.command("is")
def sq_is(
    ctx: typer.Context,
    date_str: Annotated[str, typer.Argument(help="Date to check (YYYY-MM-DD)")],
) -> None:
    """Check if a date is an SQ date."""
    d = parse_date(date_str)
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    is_sq = market.is_sq_date(d)
    result = {
        "date": d.isoformat(),
        "is_sq_date": is_sq,
    }
    typer.echo(format_output(result, fmt))
