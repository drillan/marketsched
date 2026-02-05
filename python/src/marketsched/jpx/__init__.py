"""JPX (Japan Exchange Group) market implementations.

This module provides market implementations for JPX derivatives markets.
Currently supports:
- jpx-index: Index futures and options (Nikkei 225, TOPIX, etc.)

Future implementations:
- jpx-equity-options: Equity options
- jpx-bond: Bond futures

Example:
    >>> import marketsched
    >>> market = marketsched.get_market("jpx-index")
    >>> market.name
    'JPX Index Futures & Options'
"""

from marketsched.jpx.index import JPXIndex

__all__ = ["JPXIndex"]
