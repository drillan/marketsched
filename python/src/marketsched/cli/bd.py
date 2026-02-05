"""Business day (bd) CLI subcommand.

Commands:
- is: Check if date is a business day
- next: Get next business day
- prev: Get previous business day
- list: List business days in range
- count: Count business days in range
"""

from datetime import date
from typing import Annotated

import typer

from marketsched.cli.main import (
    format_output,
    get_format_from_ctx,
    get_market_from_ctx,
)

bd_app = typer.Typer(no_args_is_help=True)


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format."""
    try:
        return date.fromisoformat(date_str)
    except ValueError as e:
        raise typer.BadParameter(
            f"Invalid date format: {date_str}. Use YYYY-MM-DD."
        ) from e


@bd_app.command("is")
def bd_is(
    ctx: typer.Context,
    date_str: Annotated[str, typer.Argument(help="Date to check (YYYY-MM-DD)")],
) -> None:
    """Check if a date is a business day."""
    d = parse_date(date_str)
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    is_bd = market.is_business_day(d)
    result = {
        "date": d.isoformat(),
        "is_business_day": is_bd,
    }
    typer.echo(format_output(result, fmt))


@bd_app.command("next")
def bd_next(
    ctx: typer.Context,
    date_str: Annotated[str, typer.Argument(help="Starting date (YYYY-MM-DD)")],
) -> None:
    """Get the next business day after a date."""
    d = parse_date(date_str)
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    next_bd = market.next_business_day(d)
    result = {
        "date": d.isoformat(),
        "next_business_day": next_bd.isoformat(),
    }
    typer.echo(format_output(result, fmt))


@bd_app.command("prev")
def bd_prev(
    ctx: typer.Context,
    date_str: Annotated[str, typer.Argument(help="Starting date (YYYY-MM-DD)")],
) -> None:
    """Get the previous business day before a date."""
    d = parse_date(date_str)
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    prev_bd = market.previous_business_day(d)
    result = {
        "date": d.isoformat(),
        "previous_business_day": prev_bd.isoformat(),
    }
    typer.echo(format_output(result, fmt))


@bd_app.command("list")
def bd_list(
    ctx: typer.Context,
    start_str: Annotated[str, typer.Argument(help="Start date (YYYY-MM-DD)")],
    end_str: Annotated[str, typer.Argument(help="End date (YYYY-MM-DD)")],
) -> None:
    """List all business days in a date range."""
    start = parse_date(start_str)
    end = parse_date(end_str)
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    days = market.get_business_days(start, end)
    result = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "business_days": [d.isoformat() for d in days],
        "count": len(days),
    }
    typer.echo(format_output(result, fmt))


@bd_app.command("count")
def bd_count(
    ctx: typer.Context,
    start_str: Annotated[str, typer.Argument(help="Start date (YYYY-MM-DD)")],
    end_str: Annotated[str, typer.Argument(help="End date (YYYY-MM-DD)")],
) -> None:
    """Count business days in a date range."""
    start = parse_date(start_str)
    end = parse_date(end_str)
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    count = market.count_business_days(start, end)
    result = {
        "start_date": start.isoformat(),
        "end_date": end.isoformat(),
        "count": count,
    }
    typer.echo(format_output(result, fmt))
