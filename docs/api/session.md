# 取引セッション

取引セッションの判定に関するメソッドと列挙型です。

## TradingSession 列挙型

```python
from marketsched import TradingSession
```

| 値 | 文字列値 | 説明 |
|----|---------|------|
| `TradingSession.DAY` | `"day"` | 日中立会 |
| `TradingSession.NIGHT` | `"night"` | ナイトセッション |
| `TradingSession.CLOSED` | `"closed"` | 取引時間外 |

## JPX指数先物・オプションの立会時間

| セッション | 開始 | 終了 | 備考 |
|-----------|------|------|------|
| NIGHT（前日分） | 00:00 | 06:00 | 前取引日のナイトセッション継続 |
| CLOSED（ギャップ） | 06:00 | 08:45 | プレマーケット |
| DAY | 08:45 | 15:45 | 日中立会 |
| CLOSED（ギャップ） | 15:45 | 17:00 | セッション間 |
| NIGHT | 17:00 | 翌06:00 | ナイトセッション |

:::{note}
ナイトセッションは日付をまたぎます。取引日 D の 17:00 から翌日 D+1 の 06:00 までは、取引日 D のナイトセッションとして扱われます。
:::

## get_session()

```python
market.get_session(dt: datetime | None = None) -> TradingSession
```

指定時刻の取引セッションを取得します。

dt
: 判定対象の時刻（タイムゾーン付き）。`None` の場合は現在時刻を使用。

**戻り値**: `TradingSession` -- 取引セッション

**例外**: `TimezoneRequiredError` -- `dt` にタイムゾーン情報がない場合

```python
from datetime import datetime
from zoneinfo import ZoneInfo

jst = ZoneInfo("Asia/Tokyo")
market = marketsched.get_market("jpx-index")

# 日中立会（10:00 JST）
market.get_session(datetime(2026, 2, 6, 10, 0, tzinfo=jst))
# TradingSession.DAY

# ナイトセッション（20:00 JST）
market.get_session(datetime(2026, 2, 6, 20, 0, tzinfo=jst))
# TradingSession.NIGHT

# ギャップ期間（16:30 JST）
market.get_session(datetime(2026, 2, 6, 16, 30, tzinfo=jst))
# TradingSession.CLOSED

# 引数省略で現在時刻を使用
market.get_session()
# TradingSession.DAY / NIGHT / CLOSED（現在時刻による）
```

### UTCで指定する場合

```python
import marketsched
from datetime import datetime, timezone

market = marketsched.get_market("jpx-index")

# UTC 01:00 = JST 10:00（日中立会）
dt_utc = datetime(2026, 2, 6, 1, 0, tzinfo=timezone.utc)
market.get_session(dt_utc)  # TradingSession.DAY
```

## is_trading_hours()

```python
market.is_trading_hours(dt: datetime | None = None) -> bool
```

指定時刻が取引可能時間かどうかを判定します。
`get_session()` の結果が `CLOSED` でなければ `True` を返します。

dt
: 判定対象の時刻（タイムゾーン付き）。`None` の場合は現在時刻を使用。

**戻り値**: `bool` -- 取引可能時間の場合 `True`

**例外**: `TimezoneRequiredError` -- `dt` にタイムゾーン情報がない場合

```python
jst = ZoneInfo("Asia/Tokyo")

# 日中立会中
market.is_trading_hours(datetime(2026, 2, 6, 10, 0, tzinfo=jst))
# True

# ギャップ期間
market.is_trading_hours(datetime(2026, 2, 6, 16, 30, tzinfo=jst))
# False

# 引数省略で現在時刻を使用
market.is_trading_hours()
# True / False（現在時刻による）
```

## タイムゾーンに関する注意

`get_session()` と `is_trading_hours()` はタイムゾーン付きの `datetime` を要求します。
タイムゾーンなしの `datetime`（naive datetime）を渡すと `TimezoneRequiredError` が発生します。

```python
from datetime import datetime

# これはエラーになる
try:
    market.get_session(datetime(2026, 2, 6, 10, 0))  # タイムゾーンなし
except TimezoneRequiredError as e:
    print(e)  # "タイムゾーン情報が必要です..."
```

タイムゾーンの指定には標準ライブラリの `zoneinfo.ZoneInfo` を使用してください：

```python
from zoneinfo import ZoneInfo

jst = ZoneInfo("Asia/Tokyo")
utc = ZoneInfo("UTC")
```
