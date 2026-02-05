"""Main CLI application structure.

Provides the main Typer app with global options (--market, --format)
and subcommand registration.
"""

from datetime import date
from enum import StrEnum
from typing import Annotated, Any

import typer

import marketsched


class OutputFormat(StrEnum):
    """Output format options."""

    JSON = "json"
    TEXT = "text"
    TABLE = "table"


# Create main app with callback for global options
app = typer.Typer(
    name="marketsched",
    help="Market calendar, SQ dates, and trading hours management.",
    no_args_is_help=True,
)


def version_callback(value: bool) -> None:
    """Show version and exit."""
    if value:
        typer.echo(f"marketsched {marketsched.__version__}")
        raise typer.Exit()


@app.callback()
def main_callback(
    ctx: typer.Context,
    market: Annotated[
        str,
        typer.Option(
            "--market",
            "-m",
            help="Market ID (default: jpx-index)",
        ),
    ] = "jpx-index",
    output_format: Annotated[
        OutputFormat,
        typer.Option(
            "--format",
            "-f",
            help="Output format (default: json)",
        ),
    ] = OutputFormat.JSON,
    _version: Annotated[  # noqa: ARG001
        bool,
        typer.Option(
            "--version",
            callback=version_callback,
            is_eager=True,
            help="Show version and exit.",
        ),
    ] = False,
) -> None:
    """marketsched CLI - Market calendar management."""
    # Store options in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["market"] = market
    ctx.obj["format"] = output_format


def get_market_from_ctx(ctx: typer.Context) -> marketsched.Market:
    """Get market instance from context."""
    market_id: str = ctx.obj.get("market", "jpx-index")
    return marketsched.get_market(market_id)


def get_format_from_ctx(ctx: typer.Context) -> OutputFormat:
    """Get output format from context."""
    fmt: OutputFormat = ctx.obj.get("format", OutputFormat.JSON)
    return fmt


def parse_date(date_str: str) -> date:
    """Parse date string in YYYY-MM-DD format.

    Args:
        date_str: Date string in YYYY-MM-DD format.

    Returns:
        Parsed date object.

    Raises:
        typer.BadParameter: If the date format is invalid.
    """
    try:
        return date.fromisoformat(date_str)
    except ValueError as e:
        raise typer.BadParameter(
            f"Invalid date format: {date_str}. Use YYYY-MM-DD."
        ) from e


def format_output(data: dict[str, Any], fmt: OutputFormat) -> str:
    """Format data according to output format."""
    if fmt == OutputFormat.JSON:
        import json

        return json.dumps(data, ensure_ascii=False, indent=2)
    elif fmt == OutputFormat.TEXT:
        return _format_text(data)
    elif fmt == OutputFormat.TABLE:
        return _format_table(data)
    return str(data)


def _format_text(data: dict[str, Any]) -> str:
    """Format data as human-readable text."""
    lines: list[str] = []
    for key, value in data.items():
        if isinstance(value, list):
            lines.append(f"{key}:")
            for item in value:
                lines.append(f"  - {item}")
        elif isinstance(value, bool):
            lines.append(f"{key}: {'Yes' if value else 'No'}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _format_table(data: dict[str, Any]) -> str:
    """Format data as a table."""
    # For lists, create a table; for single values, use text format
    for key, value in data.items():
        if isinstance(value, list) and len(value) > 0:
            # Format as table
            lines = [f"{'#':<4} {key}"]
            lines.append("-" * 20)
            for i, item in enumerate(value, 1):
                lines.append(f"{i:<4} {item}")
            return "\n".join(lines)
    # Fall back to text format for non-list data
    return _format_text(data)


def _register_subcommands() -> None:
    """Register all subcommands.

    This is called at module load time to avoid circular import issues
    while ensuring subcommands are registered before the app is used.
    """
    from marketsched.cli.bd import bd_app
    from marketsched.cli.cache import cache_app
    from marketsched.cli.sq import sq_app
    from marketsched.cli.ss import ss_app

    app.add_typer(bd_app, name="bd", help="Business day operations")
    app.add_typer(sq_app, name="sq", help="SQ date operations")
    app.add_typer(ss_app, name="ss", help="Trading session operations")
    app.add_typer(cache_app, name="cache", help="Cache management")


# Register subcommands
_register_subcommands()


def main() -> None:
    """Entry point for CLI."""
    app()
