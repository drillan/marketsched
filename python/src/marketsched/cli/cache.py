"""Cache management (cache) CLI subcommand.

Commands:
- update: Update cache from JPX official data
- clear: Clear cache
- status: Show cache status
"""

import typer

from marketsched.cache import clear_cache, get_cache_status, update_cache
from marketsched.cli.main import (
    format_output,
    get_format_from_ctx,
)
from marketsched.exceptions import DataFetchError, InvalidDataFormatError

cache_app = typer.Typer(no_args_is_help=True)


@cache_app.command("status")
def cache_status(ctx: typer.Context) -> None:
    """Show cache status."""
    fmt = get_format_from_ctx(ctx)
    status = get_cache_status()

    result = {}
    for data_type, info in status.items():
        result[data_type] = {
            "cache_path": info.cache_path,
            "is_valid": info.is_valid,
            "fetched_at": info.fetched_at.isoformat() if info.fetched_at else None,
            "expires_at": info.expires_at.isoformat() if info.expires_at else None,
            "record_count": info.record_count,
        }

    typer.echo(format_output(result, fmt))


@cache_app.command("update")
def cache_update(ctx: typer.Context) -> None:
    """Update cache from JPX official data.

    Downloads the latest data from JPX official website and updates
    the local cache.
    """
    fmt = get_format_from_ctx(ctx)

    try:
        status = update_cache(force=True)

        result: dict[str, object] = {
            "status": "success",
            "message": "キャッシュを更新しました",
        }
        for data_type, info in status.items():
            result[f"{data_type}_record_count"] = info.record_count

    except (DataFetchError, InvalidDataFormatError) as e:
        error_result: dict[str, str] = {
            "status": "error",
            "message": f"キャッシュの更新に失敗しました: {e}",
        }
        typer.echo(format_output(error_result, fmt), err=True)
        raise typer.Exit(1) from e

    typer.echo(format_output(result, fmt))


@cache_app.command("clear")
def cache_clear(ctx: typer.Context) -> None:
    """Clear all cached data."""
    fmt = get_format_from_ctx(ctx)

    clear_cache()

    result = {
        "status": "success",
        "cleared": True,
        "message": "キャッシュをクリアしました",
    }
    typer.echo(format_output(result, fmt))
