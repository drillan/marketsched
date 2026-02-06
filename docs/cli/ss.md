# ss -- セッション

取引セッションの判定を行うサブコマンドです。

## ss get

指定時刻の取引セッションを取得します。

```bash
mks ss get [DATETIME]
```

DATETIME
: 判定対象時刻（ISO 8601形式、タイムゾーン必須）。省略時は現在時刻を使用。

:::{important}
`DATETIME` を指定する場合は**タイムゾーンの指定が必須**です。
タイムゾーンなしの値を渡すとエラーになります。
:::

**JSON出力例**:

```bash
# 現在時刻で判定
$ mks ss get
```

```json
{
  "datetime": "2026-02-06T10:00:00+09:00",
  "session": "day",
  "market": "jpx-index"
}
```

```bash
# 日中立会（10:00 JST）
$ mks ss get 2026-02-06T10:00:00+09:00
```

```json
{
  "datetime": "2026-02-06T10:00:00+09:00",
  "session": "day",
  "market": "jpx-index"
}
```

```bash
# ナイトセッション（20:00 JST）
$ mks ss get 2026-02-06T20:00:00+09:00
```

```json
{
  "datetime": "2026-02-06T20:00:00+09:00",
  "session": "night",
  "market": "jpx-index"
}
```

```bash
# ギャップ期間（16:30 JST）
$ mks ss get 2026-02-06T16:30:00+09:00
```

```json
{
  "datetime": "2026-02-06T16:30:00+09:00",
  "session": "closed",
  "market": "jpx-index"
}
```

**Text出力例**:

```bash
$ mks -f text ss get 2026-02-06T10:00:00+09:00
2026-02-06T10:00:00+09:00 は日中立会です
```

**エラー出力（タイムゾーンなし）**:

```bash
$ mks ss get 2026-02-06T10:00:00
```

```json
{
  "error": "TimezoneRequiredError",
  "message": "タイムゾーン情報が必要です。例: 2026-02-06T10:00:00+09:00"
}
```

終了コード: 1

## ss is-trading

指定時刻が取引可能時間かどうかを判定します。

```bash
mks ss is-trading [DATETIME]
```

DATETIME
: 判定対象時刻（ISO 8601形式、タイムゾーン必須）。省略時は現在時刻を使用。

**JSON出力例**:

```bash
# 取引時間内（10:00 JST = 日中立会）
$ mks ss is-trading 2026-02-06T10:00:00+09:00
```

```json
{
  "datetime": "2026-02-06T10:00:00+09:00",
  "is_trading": true,
  "market": "jpx-index"
}
```

```bash
# 取引時間外（16:30 JST = ギャップ期間）
$ mks ss is-trading 2026-02-06T16:30:00+09:00
```

```json
{
  "datetime": "2026-02-06T16:30:00+09:00",
  "is_trading": false,
  "market": "jpx-index"
}
```

```bash
# 現在時刻で判定
$ mks ss is-trading
```

**Text出力例**:

```bash
$ mks -f text ss is-trading 2026-02-06T10:00:00+09:00
取引可能です

$ mks -f text ss is-trading 2026-02-06T16:30:00+09:00
取引時間外です
```

## タイムゾーンの指定方法

ISO 8601形式でタイムゾーンを指定します。

| 形式 | 例 | 説明 |
|------|-----|------|
| `+HH:MM` | `2026-02-06T10:00:00+09:00` | JST（日本標準時） |
| `Z` | `2026-02-06T01:00:00Z` | UTC |
| `+HH:MM` | `2026-02-06T01:00:00+00:00` | UTC（明示的） |

```bash
# JST（日本標準時）で指定
mks ss get 2026-02-06T10:00:00+09:00

# UTCで指定（JST 10:00 = UTC 01:00）
mks ss get 2026-02-06T01:00:00Z
```
