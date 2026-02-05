"""Cache management (cache) CLI subcommand.

Commands:
- update: Update cache from JPX official data
- clear: Clear cache
- status: Show cache status
"""

import typer

from marketsched.cli.main import (
    format_output,
    get_format_from_ctx,
)
from marketsched.jpx.data.cache import get_cache

cache_app = typer.Typer(no_args_is_help=True)


@cache_app.command("status")
def cache_status(ctx: typer.Context) -> None:
    """Show cache status."""
    fmt = get_format_from_ctx(ctx)
    cache = get_cache()

    # Check if cache exists and is valid
    try:
        metadata = cache.read_metadata()
        exists = True
        is_valid = cache.is_cache_available()
        last_updated = metadata.last_updated.isoformat()
        cache_valid_until = metadata.cache_valid_until.isoformat()
    except FileNotFoundError:
        # キャッシュファイルが存在しない - 正常なケース
        exists = False
        is_valid = False
        last_updated = None
        cache_valid_until = None
    except (PermissionError, OSError) as e:
        typer.echo(f"警告: キャッシュの読み取りに失敗しました: {e}", err=True)
        exists = False
        is_valid = False
        last_updated = None
        cache_valid_until = None

    # Get cache size
    total_size = 0
    for path in [cache.sq_dates_path, cache.holidays_path, cache.metadata_path]:
        if path.exists():
            total_size += path.stat().st_size

    result = {
        "cache_dir": str(cache.cache_dir),
        "exists": exists,
        "is_valid": is_valid,
        "last_updated": last_updated,
        "cache_valid_until": cache_valid_until,
        "size_bytes": total_size,
    }
    typer.echo(format_output(result, fmt))


@cache_app.command("update")
def cache_update(ctx: typer.Context) -> None:
    """Update cache from JPX official data.

    Downloads the latest data from JPX official website and updates
    the local cache.
    """
    fmt = get_format_from_ctx(ctx)
    cache = get_cache()

    try:
        # Import fetcher here to avoid import errors if not implemented yet
        from marketsched.jpx.data.fetcher import (  # type: ignore[import-not-found]
            fetch_and_update_cache,
        )

        fetch_and_update_cache(cache)

        result: dict[str, str] = {
            "status": "success",
            "message": "キャッシュを更新しました",
            "cache_dir": str(cache.cache_dir),
        }
    except ImportError as e:
        result = {
            "status": "error",
            "message": "キャッシュ更新機能が未実装です。",
        }
        typer.echo(format_output(result, fmt), err=True)
        raise typer.Exit(1) from e
    except Exception as e:
        result = {
            "status": "error",
            "message": f"キャッシュの更新に失敗しました: {e}",
        }
        typer.echo(format_output(result, fmt), err=True)
        raise typer.Exit(1) from e

    typer.echo(format_output(result, fmt))


@cache_app.command("clear")
def cache_clear(ctx: typer.Context) -> None:
    """Clear all cached data."""
    fmt = get_format_from_ctx(ctx)
    cache = get_cache()

    cache.clear()

    result = {
        "status": "success",
        "cleared": True,
        "message": "キャッシュをクリアしました",
    }
    typer.echo(format_output(result, fmt))
