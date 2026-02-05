"""JPX trading session time definitions.

This module defines the trading hours for JPX derivative markets.
Session times are based on JPX official trading hours:
https://www.jpx.co.jp/derivatives/rules/trading-hours/index.html

Note:
    Times are in JST (Asia/Tokyo). The night session spans across midnight
    (17:00 to 06:00 next day).
"""

from datetime import time
from typing import NamedTuple


class SessionTime(NamedTuple):
    """Represents a trading session with start and end times.

    Attributes:
        start: Session start time (inclusive).
        end: Session end time (inclusive for same-day, exclusive for overnight).
    """

    start: time
    end: time


class JPXIndexSessionTimes:
    """Trading session times for JPX Index derivatives.

    Based on JPX official trading hours for index futures and options.

    Trading Schedule (JST):
        Day Session: 08:45 - 15:45
        Night Session: 17:00 - 06:00 (next day)

    Gap periods (market closed):
        - 06:00 - 08:45 (pre-market gap)
        - 15:45 - 17:00 (inter-session gap)

    Note:
        Night session starting at 17:00 on date D belongs to trading date D.
        The portion from 00:00 to 06:00 on date D+1 also belongs to trading date D.
    """

    # Day session: 08:45 - 15:45 JST
    DAY_START = time(8, 45)
    DAY_END = time(15, 45)
    DAY = SessionTime(start=DAY_START, end=DAY_END)

    # Night session: 17:00 - 06:00 (next day) JST
    NIGHT_START = time(17, 0)
    NIGHT_END = time(6, 0)
    NIGHT = SessionTime(start=NIGHT_START, end=NIGHT_END)

    # Gap periods
    PRE_MARKET_GAP_END = DAY_START  # 06:00 - 08:45
    INTER_SESSION_GAP_START = DAY_END  # 15:45 - 17:00
    INTER_SESSION_GAP_END = NIGHT_START

    @classmethod
    def is_day_session(cls, t: time) -> bool:
        """Check if time is within day session.

        Args:
            t: Time to check.

        Returns:
            True if within day session (08:45 <= t <= 15:45).
        """
        return cls.DAY_START <= t <= cls.DAY_END

    @classmethod
    def is_night_session(cls, t: time) -> bool:
        """Check if time is within night session.

        Night session spans midnight: 17:00 - 06:00 next day.

        Args:
            t: Time to check.

        Returns:
            True if within night session.
        """
        # 17:00 <= t or t < 06:00
        return t >= cls.NIGHT_START or t < cls.NIGHT_END

    @classmethod
    def is_trading_time(cls, t: time) -> bool:
        """Check if time is within any trading session.

        Args:
            t: Time to check.

        Returns:
            True if market is open at this time.
        """
        return cls.is_day_session(t) or cls.is_night_session(t)
