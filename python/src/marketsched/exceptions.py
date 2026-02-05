"""Custom exceptions for marketsched package.

All custom exceptions inherit from MarketshedError, making it easy to catch
all marketsched-related errors with a single except clause.
"""


class MarketshedError(Exception):
    """Base exception for all marketsched errors.

    All custom exceptions in this package inherit from this class,
    allowing users to catch all marketsched errors with:

        try:
            ...
        except MarketshedError as e:
            handle_error(e)
    """

    pass


class MarketNotFoundError(MarketshedError):
    """Raised when a requested market is not found in the registry.

    Attributes:
        market_id: The market ID that was not found.
    """

    def __init__(self, market_id: str) -> None:
        self.market_id = market_id
        available_hint = (
            "Use marketsched.get_available_markets() to list available markets."
        )
        super().__init__(f"Market '{market_id}' not found. {available_hint}")


class ContractMonthParseError(MarketshedError):
    """Raised when contract month parsing fails.

    Attributes:
        input_text: The input text that could not be parsed.
    """

    def __init__(self, input_text: str) -> None:
        self.input_text = input_text
        formats_hint = "Supported formats: '26年3月限', '2026年3月限', '202603', etc."
        super().__init__(
            f"Failed to parse contract month from '{input_text}'. {formats_hint}"
        )


class SQDataNotFoundError(MarketshedError):
    """Raised when SQ date data is not available for the specified year/month.

    Attributes:
        year: The requested year.
        month: The requested month.
    """

    def __init__(self, year: int, month: int) -> None:
        self.year = year
        self.month = month
        super().__init__(
            f"SQ date data not found for {year}/{month:02d}. "
            f"Try running 'mks cache update' to fetch the latest data."
        )


class SQNotSupportedError(MarketshedError):
    """Raised when SQ operations are attempted on a market that doesn't support SQ.

    Some markets (e.g., stock exchanges) don't have SQ dates.

    Attributes:
        market_id: The market ID that doesn't support SQ.
    """

    def __init__(self, market_id: str) -> None:
        self.market_id = market_id
        super().__init__(
            f"Market '{market_id}' does not support SQ (Special Quotation) dates."
        )


class TimezoneRequiredError(MarketshedError):
    """Raised when a timezone-naive datetime is provided where timezone is required.

    All datetime values passed to marketsched must be timezone-aware.
    Use datetime with tzinfo or ZoneInfo to specify the timezone.
    """

    def __init__(self) -> None:
        super().__init__(
            "Timezone information is required. "
            "Use datetime with tzinfo (e.g., datetime(..., tzinfo=ZoneInfo('Asia/Tokyo')))."
        )


class CacheNotAvailableError(MarketshedError):
    """Raised when cache is not available and online fetch is not possible.

    This typically occurs when:
    - The cache hasn't been initialized yet
    - Network is unavailable and no cached data exists
    """

    def __init__(self) -> None:
        super().__init__(
            "Cache data is not available and cannot be fetched. "
            "Please connect to the internet and run 'mks cache update'."
        )


class DataFetchError(MarketshedError):
    """Raised when fetching data from external sources fails.

    Attributes:
        url: The URL that failed to fetch.
        reason: The reason for the failure.
    """

    def __init__(self, url: str, reason: str) -> None:
        self.url = url
        self.reason = reason
        super().__init__(f"Failed to fetch data from '{url}': {reason}")


class InvalidDataFormatError(MarketshedError):
    """Raised when fetched data has an unexpected format.

    This may indicate that the data source has changed its format.

    Attributes:
        details: Details about what was unexpected.
    """

    def __init__(self, details: str) -> None:
        self.details = details
        super().__init__(
            f"Invalid data format: {details}. "
            f"The data source format may have changed. Please report this issue."
        )
