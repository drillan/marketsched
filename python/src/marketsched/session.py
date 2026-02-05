"""Trading session enumeration for market trading periods."""

from enum import Enum


class TradingSession(Enum):
    """Represents the trading session status.

    Trading sessions define the time periods when trading is active:
    - DAY: Day session (typically morning to afternoon)
    - NIGHT: Night session (evening to early morning)
    - CLOSED: Market is closed (gap periods, holidays, weekends)
    """

    DAY = "day"
    NIGHT = "night"
    CLOSED = "closed"

    @property
    def is_trading(self) -> bool:
        """Return True if this session allows trading.

        Returns:
            bool: True for DAY and NIGHT sessions, False for CLOSED.

        Example:
            >>> TradingSession.DAY.is_trading
            True
            >>> TradingSession.CLOSED.is_trading
            False
        """
        return self in (TradingSession.DAY, TradingSession.NIGHT)
