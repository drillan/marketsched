# API リファレンス

marketsched パッケージの Python API リファレンスです。

## パッケージレベル関数

| 関数 | 説明 |
|------|------|
| {func}`~marketsched.get_market` | 市場オブジェクトを取得 |
| {func}`~marketsched.get_available_markets` | 利用可能な市場IDリストを取得 |
| {func}`~marketsched.update_cache` | キャッシュを更新 |
| {func}`~marketsched.clear_cache` | キャッシュをクリア |
| {func}`~marketsched.get_cache_status` | キャッシュ状態を取得 |

詳細は {doc}`market`（市場取得）および {doc}`cache`（キャッシュ管理）を参照してください。

## 型・クラス

| クラス | 説明 | 詳細 |
|--------|------|------|
| `Market` | 市場プロトコル（インターフェース） | {doc}`market` |
| `ContractMonth` | 限月値オブジェクト（Pydantic BaseModel） | {doc}`contract-month` |
| `TradingSession` | 取引セッション列挙型 | {doc}`session` |
| `DataType` | キャッシュデータ種別列挙型 | {doc}`cache` |

## メソッド一覧（Market Protocol）

### 営業日

| メソッド | 戻り値 | 説明 |
|---------|--------|------|
| `is_business_day(d)` | `bool` | 営業日判定 |
| `next_business_day(d)` | `date` | 翌営業日取得 |
| `previous_business_day(d)` | `date` | 前営業日取得 |
| `get_business_days(start, end)` | `list[date]` | 期間内営業日リスト |
| `count_business_days(start, end)` | `int` | 期間内営業日数 |

詳細は {doc}`business-day` を参照してください。

### SQ日

| メソッド | 戻り値 | 説明 |
|---------|--------|------|
| `get_sq_date(year, month)` | `date` | SQ日取得 |
| `is_sq_date(d)` | `bool` | SQ日判定 |
| `get_sq_dates_for_year(year)` | `list[date]` | 年間SQ日リスト |

詳細は {doc}`sq` を参照してください。

### セッション

| メソッド | 戻り値 | 説明 |
|---------|--------|------|
| `get_session(dt)` | `TradingSession` | セッション取得 |
| `is_trading_hours(dt)` | `bool` | 取引可能判定 |

詳細は {doc}`session` を参照してください。

## 例外

| 例外 | 説明 |
|------|------|
| `MarketschedError` | 全エラーの基底クラス |
| `MarketNotFoundError` | 市場が見つからない |
| `MarketAlreadyRegisteredError` | 市場が既に登録済み |
| `ContractMonthParseError` | 限月解析失敗 |
| `SQDataNotFoundError` | SQデータなし |
| `SQNotSupportedError` | SQ非対応市場 |
| `TimezoneRequiredError` | タイムゾーン必須 |
| `CacheNotAvailableError` | キャッシュ利用不可 |
| `DataFetchError` | データ取得失敗 |
| `InvalidDataFormatError` | データ形式不正 |

詳細は {doc}`exceptions` を参照してください。
