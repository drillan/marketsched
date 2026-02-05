# Python API Contract: marketsched

**Version**: 1.0.0
**Feature Branch**: `002-marketsched-python`

## Module: marketsched

### Public Functions

#### get_market

```python
def get_market(market_id: str) -> Market:
    """
    指定されたIDの市場オブジェクトを取得する。

    Args:
        market_id: 市場識別子（例: "jpx-index"）

    Returns:
        Market: 市場オブジェクト

    Raises:
        MarketNotFoundError: 指定されたIDの市場が存在しない場合

    Example:
        >>> market = marketsched.get_market("jpx-index")
        >>> market.name
        'JPX指数先物・オプション'
    """
```

#### get_available_markets

```python
def get_available_markets() -> list[str]:
    """
    利用可能な市場IDのリストを取得する。

    Returns:
        list[str]: 市場IDのリスト

    Example:
        >>> marketsched.get_available_markets()
        ['jpx-index']
    """
```

---

## Class: ContractMonth (Pydantic BaseModel)

### Definition

```python
from pydantic import BaseModel, ConfigDict, Field

class ContractMonth(BaseModel):
    """
    限月を表す値オブジェクト。

    Pydantic BaseModel として実装され、frozen=True によりイミュータブル。
    バリデーションは Field constraints により自動的に行われる。

    Example:
        >>> cm = ContractMonth(year=2026, month=3)
        >>> cm.year
        2026
        >>> cm.month
        3

    Raises:
        ValidationError: year または month が範囲外の場合
    """

    model_config = ConfigDict(frozen=True)

    year: int = Field(ge=2000, le=2099, description="西暦年（4桁）")
    month: int = Field(ge=1, le=12, description="月")
```

### Class Methods

```python
@classmethod
def parse(cls, text: str) -> ContractMonth:
    """
    日本語表記の限月文字列をパースする。

    サポートする形式:
    - "26年3月限" (2桁年号)
    - "2026年3月限" (4桁年号)
    - "2026年03月限" (ゼロパディング)

    Args:
        text: 限月を表す日本語文字列

    Returns:
        ContractMonth: パースされた限月オブジェクト

    Raises:
        ContractMonthParseError: パースに失敗した場合

    Example:
        >>> cm = ContractMonth.parse("26年3月限")
        >>> cm.year
        2026
        >>> cm.month
        3
    """
```

### Instance Methods

```python
def to_yyyymm(self) -> str:
    """
    YYYYMM形式の文字列に変換する。

    Returns:
        str: "YYYYMM" 形式の文字列

    Example:
        >>> cm = ContractMonth(2026, 3)
        >>> cm.to_yyyymm()
        '202603'
    """

def to_japanese(self) -> str:
    """
    日本語形式の文字列に変換する。

    Returns:
        str: "YYYY年M月限" 形式の文字列

    Example:
        >>> cm = ContractMonth(2026, 3)
        >>> cm.to_japanese()
        '2026年3月限'
    """
```

### Special Methods

```python
def __eq__(self, other: object) -> bool: ...
def __lt__(self, other: ContractMonth) -> bool: ...
def __le__(self, other: ContractMonth) -> bool: ...
def __gt__(self, other: ContractMonth) -> bool: ...
def __ge__(self, other: ContractMonth) -> bool: ...
def __hash__(self) -> int: ...
def __repr__(self) -> str: ...
def __str__(self) -> str: ...
```

---

## Protocol: Market

```python
from typing import Protocol
from datetime import datetime, date
from zoneinfo import ZoneInfo

class Market(Protocol):
    """市場を表すプロトコル"""

    @property
    def market_id(self) -> str:
        """市場識別子"""
        ...

    @property
    def name(self) -> str:
        """市場名"""
        ...

    @property
    def timezone(self) -> ZoneInfo:
        """市場のタイムゾーン"""
        ...

    def is_business_day(self, d: date) -> bool:
        """
        指定日が営業日かどうかを判定する。

        祝日取引実施日に該当する祝日は営業日として判定される。

        Args:
            d: 判定対象の日付

        Returns:
            bool: 営業日の場合True
        """
        ...

    def next_business_day(self, d: date) -> date:
        """
        指定日の翌営業日を取得する。

        Args:
            d: 基準日

        Returns:
            date: 翌営業日
        """
        ...

    def previous_business_day(self, d: date) -> date:
        """
        指定日の前営業日を取得する。

        Args:
            d: 基準日

        Returns:
            date: 前営業日
        """
        ...

    def get_business_days(self, start: date, end: date) -> list[date]:
        """
        期間内の営業日リストを取得する。

        Args:
            start: 開始日（含む）
            end: 終了日（含む）

        Returns:
            list[date]: 営業日のリスト（昇順）
        """
        ...

    def count_business_days(self, start: date, end: date) -> int:
        """
        期間内の営業日数をカウントする。

        Args:
            start: 開始日（含む）
            end: 終了日（含む）

        Returns:
            int: 営業日数
        """
        ...

    def get_sq_date(self, year: int, month: int) -> date:
        """
        指定年月のSQ日を取得する。

        Args:
            year: 年
            month: 月

        Returns:
            date: SQ日

        Raises:
            SQDataNotFoundError: 指定年月のデータが存在しない場合
            SQNotSupportedError: この市場がSQ日機能をサポートしていない場合
        """
        ...

    def is_sq_date(self, d: date) -> bool:
        """
        指定日がSQ日かどうかを判定する。

        Args:
            d: 判定対象の日付

        Returns:
            bool: SQ日の場合True

        Raises:
            SQNotSupportedError: この市場がSQ日機能をサポートしていない場合
        """
        ...

    def get_sq_dates_for_year(self, year: int) -> list[date]:
        """
        指定年の全SQ日リストを取得する。

        Args:
            year: 年

        Returns:
            list[date]: SQ日のリスト（昇順）

        Raises:
            SQDataNotFoundError: 指定年のデータが存在しない場合
            SQNotSupportedError: この市場がSQ日機能をサポートしていない場合
        """
        ...

    def get_session(self, dt: datetime | None = None) -> TradingSession:
        """
        指定時刻の取引セッションを取得する。

        Args:
            dt: 判定対象の時刻（タイムゾーン付き）
                Noneの場合は現在時刻を使用

        Returns:
            TradingSession: 取引セッション

        Raises:
            TimezoneRequiredError: dtにタイムゾーン情報がない場合
        """
        ...

    def is_trading_hours(self, dt: datetime | None = None) -> bool:
        """
        指定時刻が取引可能時間かどうかを判定する。

        Args:
            dt: 判定対象の時刻（タイムゾーン付き）
                Noneの場合は現在時刻を使用

        Returns:
            bool: 取引可能時間の場合True

        Raises:
            TimezoneRequiredError: dtにタイムゾーン情報がない場合
        """
        ...
```

---

## Enum: TradingSession

```python
from enum import Enum

class TradingSession(Enum):
    """取引セッションを表す列挙型"""

    DAY = "day"
    """日中立会"""

    NIGHT = "night"
    """ナイトセッション"""

    CLOSED = "closed"
    """取引時間外"""
```

---

## Exceptions

```python
class MarketshedError(Exception):
    """marketsched の基底例外クラス"""
    pass

class MarketNotFoundError(MarketshedError):
    """指定された市場が見つからない場合の例外"""
    pass

class ContractMonthParseError(MarketshedError):
    """限月文字列のパースに失敗した場合の例外"""
    pass

class SQDataNotFoundError(MarketshedError):
    """指定された年月のSQ日データが存在しない場合の例外"""
    pass

class SQNotSupportedError(MarketshedError):
    """市場がSQ日機能をサポートしていない場合の例外"""
    pass

class TimezoneRequiredError(MarketshedError):
    """タイムゾーン情報が必要な場合の例外"""
    pass

class CacheNotAvailableError(MarketshedError):
    """キャッシュが利用できない場合の例外（オフライン時等）"""
    pass

class DataFetchError(MarketshedError):
    """データ取得に失敗した場合の例外"""
    pass

class InvalidDataFormatError(MarketshedError):
    """取得したデータの形式が不正な場合の例外"""
    pass
```

---

## Cache Management

```python
# marketsched.cache モジュール
from pathlib import Path
from pydantic import AwareDatetime, BaseModel

def update_cache(market_id: str | None = None) -> None:
    """
    キャッシュを更新する。

    Args:
        market_id: 更新対象の市場ID（Noneの場合は全市場）

    Raises:
        DataFetchError: データ取得に失敗した場合
        MarketNotFoundError: 指定された市場が存在しない場合
    """

def clear_cache(market_id: str | None = None) -> None:
    """
    キャッシュをクリアする。

    Args:
        market_id: クリア対象の市場ID（Noneの場合は全市場）

    Raises:
        MarketNotFoundError: 指定された市場が存在しない場合
    """

def get_cache_status(market_id: str | None = None) -> dict[str, CacheInfo]:
    """
    キャッシュの状態を取得する。

    Args:
        market_id: 対象の市場ID（Noneの場合は全市場）

    Returns:
        dict[str, CacheInfo]: 市場IDをキーとするキャッシュ情報の辞書

    Raises:
        MarketNotFoundError: 指定された市場が存在しない場合
    """

class CacheInfo(BaseModel):
    """キャッシュ情報（Pydantic BaseModel）"""

    market: str
    """市場ID"""

    last_updated: AwareDatetime | None
    """最終更新日時（キャッシュなしの場合None、タイムゾーン付き）"""

    is_valid: bool
    """キャッシュが有効かどうか"""

    cache_path: Path
    """キャッシュファイルのパス"""

    size_bytes: int
    """キャッシュサイズ（バイト）"""
```

---

## Usage Examples

### Basic Usage

```python
import marketsched
from datetime import date, datetime
from zoneinfo import ZoneInfo

# 市場の取得
market = marketsched.get_market("jpx-index")

# 営業日判定
print(market.is_business_day(date(2026, 2, 6)))  # True (金曜日)
print(market.is_business_day(date(2026, 2, 7)))  # False (土曜日)

# 翌営業日・前営業日
print(market.next_business_day(date(2026, 2, 6)))  # 2026-02-09 (月曜日)
print(market.previous_business_day(date(2026, 2, 9)))  # 2026-02-06 (金曜日)

# SQ日
print(market.get_sq_date(2026, 3))  # 2026年3月のSQ日
print(market.is_sq_date(date(2026, 3, 13)))  # True or False

# セッション判定
jst = ZoneInfo("Asia/Tokyo")
dt = datetime(2026, 2, 6, 10, 0, tzinfo=jst)
print(market.get_session(dt))  # TradingSession.DAY
print(market.is_trading_hours(dt))  # True

# 現在時刻でのセッション判定
print(market.get_session())  # 現在のセッション
```

### ContractMonth Usage

```python
from marketsched import ContractMonth

# 生成
cm = ContractMonth(2026, 3)
cm2 = ContractMonth.parse("26年3月限")

# 変換
print(cm.to_yyyymm())  # "202603"
print(cm.to_japanese())  # "2026年3月限"

# 比較
print(cm == cm2)  # True
print(cm < ContractMonth(2026, 6))  # True
```

### Error Handling

```python
from marketsched import get_market
from marketsched.exceptions import (
    MarketNotFoundError,
    SQDataNotFoundError,
    TimezoneRequiredError,
)

# 存在しない市場
try:
    market = get_market("unknown")
except MarketNotFoundError as e:
    print(f"市場が見つかりません: {e}")

# データが存在しない年月
try:
    market.get_sq_date(2050, 1)
except SQDataNotFoundError as e:
    print(f"SQ日データがありません: {e}")

# タイムゾーンなしのdatetime
from datetime import datetime
try:
    market.get_session(datetime(2026, 2, 6, 10, 0))  # naive datetime
except TimezoneRequiredError as e:
    print(f"タイムゾーンが必要です: {e}")
```
