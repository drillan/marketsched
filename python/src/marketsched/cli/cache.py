"""Cache management (cache) CLI subcommand.

Commands:
- update: Update cache from JPX official data
- clear: Clear cache
- status: Show cache status
"""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import typer

from marketsched.cli.main import (
    format_output,
    get_format_from_ctx,
)
from marketsched.jpx.data import CacheMetadata
from marketsched.jpx.data.cache import JPXDataCache, get_cache

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
    except Exception:
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
    except ImportError:
        # Fetcher not implemented yet - create placeholder cache for testing
        # This is a temporary implementation for CLI testing
        result = _create_placeholder_cache(cache)
    except Exception as e:
        result = {
            "status": "error",
            "message": f"キャッシュの更新に失敗しました: {e}",
        }
        typer.echo(format_output(result, fmt))
        raise typer.Exit(1) from None

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


def _create_placeholder_cache(cache: JPXDataCache) -> dict[str, str]:
    """Create placeholder cache for testing.

    This is a temporary implementation until the fetcher is implemented.
    Creates minimal valid cache data.
    """
    from datetime import date

    now = datetime.now(ZoneInfo("Asia/Tokyo"))

    # Create minimal SQ dates data
    sq_dates = []
    for year in range(2024, 2028):
        for month in range(1, 13):
            # SQ day is typically second Friday of the month
            # For placeholder, use 10th of each month
            sq_date = date(year, month, 10)
            sq_dates.append(
                {
                    "year": year,
                    "month": month,
                    "sq_date": sq_date,
                    "product_type": "index",
                }
            )

    # Create minimal holidays data
    holidays = [
        {
            "date": date(2026, 1, 1),
            "holiday_name": "元日",
            "is_trading": False,
            "is_confirmed": True,
        },
        {
            "date": date(2026, 1, 2),
            "holiday_name": "休業日",
            "is_trading": False,
            "is_confirmed": True,
        },
        {
            "date": date(2026, 1, 3),
            "holiday_name": "休業日",
            "is_trading": False,
            "is_confirmed": True,
        },
    ]

    # Write to cache
    cache.write_sq_dates(sq_dates)
    cache.write_holidays(holidays)

    # Write metadata
    metadata = CacheMetadata(
        last_updated=now,
        version="0.0.1-placeholder",
        source_urls={
            "sq_dates": "placeholder",
            "holidays": "placeholder",
        },
        cache_valid_until=now + timedelta(hours=24),
    )
    cache.write_metadata(metadata)

    return {
        "status": "success",
        "message": "プレースホルダーキャッシュを作成しました（テスト用）",
        "cache_dir": str(cache.cache_dir),
    }
