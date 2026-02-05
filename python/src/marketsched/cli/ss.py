"""Session (ss) CLI subcommand.

Commands:
- get: Get trading session for a datetime
- is-trading: Check if market is open
"""

from datetime import datetime
from typing import Annotated

import typer

from marketsched.cli.main import (
    format_output,
    get_format_from_ctx,
    get_market_from_ctx,
)
from marketsched.exceptions import TimezoneRequiredError

ss_app = typer.Typer(no_args_is_help=True)


def parse_datetime(dt_str: str | None) -> datetime | None:
    """Parse ISO 8601 datetime string.

    Returns None if dt_str is None (use current time).
    Raises error if timezone is missing.
    """
    if dt_str is None:
        return None

    try:
        dt = datetime.fromisoformat(dt_str)
    except ValueError as e:
        raise typer.BadParameter(
            f"Invalid datetime format: {dt_str}. Use ISO 8601 (e.g., 2026-02-06T10:00:00+09:00)."
        ) from e

    # Check for timezone
    if dt.tzinfo is None:
        raise typer.BadParameter(
            f"Timezone required: {dt_str}. Add timezone offset (e.g., +09:00 or +00:00)."
        )

    return dt


@ss_app.command("get")
def ss_get(
    ctx: typer.Context,
    datetime_str: Annotated[
        str | None,
        typer.Argument(
            help="Datetime (ISO 8601 with timezone). Omit for current time."
        ),
    ] = None,
) -> None:
    """Get the trading session for a datetime."""
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    dt = parse_datetime(datetime_str)

    try:
        session = market.get_session(dt)
    except TimezoneRequiredError as e:
        raise typer.BadParameter(
            "Timezone required. Add timezone offset (e.g., +09:00)."
        ) from e

    # Format datetime for output
    if dt is None:
        dt = datetime.now(market.timezone)

    result = {
        "datetime": dt.isoformat(),
        "session": session.value,
    }
    typer.echo(format_output(result, fmt))


@ss_app.command("is-trading")
def ss_is_trading(
    ctx: typer.Context,
    datetime_str: Annotated[
        str | None,
        typer.Argument(
            help="Datetime (ISO 8601 with timezone). Omit for current time."
        ),
    ] = None,
) -> None:
    """Check if the market is open at a given time."""
    market = get_market_from_ctx(ctx)
    fmt = get_format_from_ctx(ctx)

    dt = parse_datetime(datetime_str)

    try:
        is_trading = market.is_trading_hours(dt)
    except TimezoneRequiredError as e:
        raise typer.BadParameter(
            "Timezone required. Add timezone offset (e.g., +09:00)."
        ) from e

    # Format datetime for output
    if dt is None:
        dt = datetime.now(market.timezone)

    result = {
        "datetime": dt.isoformat(),
        "is_trading": is_trading,
    }
    typer.echo(format_output(result, fmt))
