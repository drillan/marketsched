# 例外

marketsched で定義されている例外クラスの一覧です。

## 例外階層

```{mermaid}
classDiagram
    direction LR
    Exception <|-- MarketschedError
    MarketschedError <|-- MarketNotFoundError
    MarketschedError <|-- MarketAlreadyRegisteredError
    MarketschedError <|-- ContractMonthParseError
    MarketschedError <|-- SQDataNotFoundError
    MarketschedError <|-- SQNotSupportedError
    MarketschedError <|-- TimezoneRequiredError
    MarketschedError <|-- CacheNotAvailableError
    MarketschedError <|-- DataFetchError
    MarketschedError <|-- InvalidDataFormatError
```

## MarketschedError

全ての marketsched 例外の基底クラスです。
このクラスを `except` で指定することで、marketsched の全エラーを一括でキャッチできます。

```python
import marketsched

try:
    market = marketsched.get_market("jpx-index")
    market.get_sq_date(2026, 3)
except marketsched.MarketschedError as e:
    print(f"marketsched エラー: {e}")
```

## MarketNotFoundError

**発生条件**: `get_market()` に存在しない市場IDを指定した場合

```python
try:
    market = marketsched.get_market("unknown")
except marketsched.MarketNotFoundError as e:
    print(e)  # "Market 'unknown' not found. Available: ['jpx-index']"
```

## MarketAlreadyRegisteredError

**発生条件**: 既に登録済みの市場IDで市場を登録しようとした場合

通常の利用では発生しません。カスタム市場を実装する際に関連します。

## ContractMonthParseError

**発生条件**: `ContractMonth.parse()` でパースに失敗した場合

```python
from marketsched import ContractMonth, ContractMonthParseError

try:
    cm = ContractMonth.parse("invalid")
except ContractMonthParseError as e:
    print(e)
```

## SQDataNotFoundError

**発生条件**: 指定した年月のSQ日データがキャッシュに存在しない場合

```python
try:
    market.get_sq_date(2050, 1)
except marketsched.SQDataNotFoundError as e:
    print(e)
```

**対処方法**: `mks cache update` でキャッシュを更新するか、`update_cache(years=[2050])` で該当年のデータを取得してください。

## SQNotSupportedError

**発生条件**: SQ日機能をサポートしていない市場でSQ日メソッドを呼び出した場合

現在の実装では `jpx-index` はSQ日をサポートしているため、この例外は発生しません。
将来的に追加される市場でSQ日非対応の場合に使用されます。

## TimezoneRequiredError

**発生条件**: `get_session()` または `is_trading_hours()` にタイムゾーンなしの `datetime`（naive datetime）を渡した場合

```python
from datetime import datetime

try:
    market.get_session(datetime(2026, 2, 6, 10, 0))  # タイムゾーンなし
except marketsched.TimezoneRequiredError as e:
    print(e)
```

**対処方法**: `zoneinfo.ZoneInfo` でタイムゾーンを指定してください。

```python
from zoneinfo import ZoneInfo
from datetime import datetime

dt = datetime(2026, 2, 6, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo"))
market.get_session(dt)  # OK
```

## CacheNotAvailableError

**発生条件**: キャッシュが利用できない状態で、キャッシュが必要な操作を実行した場合

**対処方法**: `mks cache update` または `marketsched.update_cache()` でキャッシュを取得してください。

## DataFetchError

**発生条件**: JPX公式サイトからのデータ取得に失敗した場合（ネットワークエラー等）

**対処方法**: インターネット接続を確認し、再度キャッシュ更新を試みてください。

## InvalidDataFormatError

**発生条件**: JPX公式サイトから取得したデータの形式が想定と異なる場合

JPXがExcelファイルの形式を変更した場合に発生する可能性があります。

## エラーハンドリングパターン

### 基本パターン

```python
import marketsched

try:
    market = marketsched.get_market("jpx-index")
    sq = market.get_sq_date(2026, 3)
except marketsched.MarketNotFoundError:
    print("市場が見つかりません")
except marketsched.SQDataNotFoundError:
    print("SQ日データがありません。`mks cache update` を実行してください")
except marketsched.MarketschedError as e:
    print(f"予期しないエラー: {e}")
```

### セッション判定のパターン

```python
from datetime import datetime
from zoneinfo import ZoneInfo

try:
    session = market.get_session(some_datetime)
except marketsched.TimezoneRequiredError:
    # タイムゾーンを付与してリトライ
    dt_with_tz = some_datetime.replace(tzinfo=ZoneInfo("Asia/Tokyo"))
    session = market.get_session(dt_with_tz)
```
