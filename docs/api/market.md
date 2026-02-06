# Market -- 市場プロトコル

## get_market()

```python
marketsched.get_market(market_id: str) -> Market
```

指定されたIDの市場オブジェクトを取得します。

market_id
: 市場識別子（例: `"jpx-index"`）

**戻り値**: `Market` -- 市場オブジェクト

**例外**: `MarketNotFoundError` -- 指定されたIDの市場が存在しない場合

```python
import marketsched

market = marketsched.get_market("jpx-index")
print(market.name)       # "JPX Index Futures & Options"
print(market.market_id)  # "jpx-index"
```

## get_available_markets()

```python
marketsched.get_available_markets() -> list[str]
```

利用可能な市場IDのリストを取得します。

**戻り値**: `list[str]` -- 市場IDのソート済みリスト

```python
import marketsched

markets = marketsched.get_available_markets()
print(markets)  # ['jpx-index']
```

## Market Protocol

`Market` は市場を抽象化するプロトコル（構造的部分型）です。
`typing.Protocol` を使用しており、明示的な継承なしに実装できます。

### プロパティ

| プロパティ | 型 | 説明 |
|-----------|-----|------|
| `market_id` | `str` | 市場識別子（例: `"jpx-index"`） |
| `name` | `str` | 市場名（例: `"JPX Index Futures & Options"`） |
| `timezone` | `ZoneInfo` | 市場のタイムゾーン（例: `ZoneInfo("Asia/Tokyo")`） |

### メソッド

Market Protocol は以下のメソッドを定義しています。
各メソッドの詳細は個別ページを参照してください。

| メソッド | 説明 | 詳細 |
|---------|------|------|
| `is_business_day(d)` | 営業日判定 | {doc}`business-day` |
| `next_business_day(d)` | 翌営業日取得 | {doc}`business-day` |
| `previous_business_day(d)` | 前営業日取得 | {doc}`business-day` |
| `get_business_days(start, end)` | 期間内営業日リスト | {doc}`business-day` |
| `count_business_days(start, end)` | 期間内営業日数 | {doc}`business-day` |
| `get_sq_date(year, month)` | SQ日取得 | {doc}`sq` |
| `is_sq_date(d)` | SQ日判定 | {doc}`sq` |
| `get_sq_dates_for_year(year)` | 年間SQ日リスト | {doc}`sq` |
| `get_session(dt)` | セッション取得 | {doc}`session` |
| `is_trading_hours(dt)` | 取引可能判定 | {doc}`session` |

## 利用可能な市場実装

### JPXIndex

| プロパティ | 値 |
|-----------|-----|
| `market_id` | `"jpx-index"` |
| `name` | `"JPX Index Futures & Options"` |
| `timezone` | `ZoneInfo("Asia/Tokyo")` |

JPX（日本取引所グループ）の指数先物・オプション市場の実装です。
日経225先物、TOPIX先物等の営業日・SQ日・取引セッションを管理します。

```python
market = marketsched.get_market("jpx-index")
print(market.timezone)  # zoneinfo.ZoneInfo(key='Asia/Tokyo')
```
