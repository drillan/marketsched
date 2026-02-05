# CLI API Contract: marketsched (mks)

**Version**: 1.0.0
**Feature Branch**: `002-marketsched-python`

## Overview

marketsched CLI は `marketsched` および短縮形 `mks` コマンドとして提供される。

## Global Options

| Option | Short | Type | Default | Description |
|--------|-------|------|---------|-------------|
| `--market` | `-m` | string | `jpx-index` | 対象市場 |
| `--format` | `-f` | string | `json` | 出力形式（json/text/table） |
| `--help` | | | | ヘルプを表示 |
| `--version` | | | | バージョンを表示 |

---

## Commands

### bd (Business Day - 営業日)

#### bd is

営業日かどうかを判定する。

```bash
mks bd is <DATE>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| DATE | date | Yes | 判定対象日（YYYY-MM-DD形式） |

**Examples**:
```bash
mks bd is 2026-02-06
mks bd is 2026-02-06 --format text
mks bd is 2026-02-06 -m jpx-index
```

**JSON Output**:
```json
{
  "date": "2026-02-06",
  "is_business_day": true,
  "market": "jpx-index"
}
```

**Text Output**:
```
2026-02-06 は営業日です
```

---

#### bd next

翌営業日を取得する。

```bash
mks bd next <DATE>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| DATE | date | Yes | 基準日（YYYY-MM-DD形式） |

**Examples**:
```bash
mks bd next 2026-02-06
mks bd next 2026-02-06 --format text
```

**JSON Output**:
```json
{
  "base_date": "2026-02-06",
  "next_business_day": "2026-02-09",
  "market": "jpx-index"
}
```

**Text Output**:
```
2026-02-06 の翌営業日は 2026-02-09 です
```

---

#### bd prev

前営業日を取得する。

```bash
mks bd prev <DATE>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| DATE | date | Yes | 基準日（YYYY-MM-DD形式） |

**Examples**:
```bash
mks bd prev 2026-02-09
mks bd prev 2026-02-09 --format text
```

**JSON Output**:
```json
{
  "base_date": "2026-02-09",
  "previous_business_day": "2026-02-06",
  "market": "jpx-index"
}
```

---

#### bd list

期間内の営業日リストを取得する。

```bash
mks bd list <START> <END>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| START | date | Yes | 開始日（YYYY-MM-DD形式） |
| END | date | Yes | 終了日（YYYY-MM-DD形式） |

**Examples**:
```bash
mks bd list 2026-02-01 2026-02-28
mks bd list 2026-02-01 2026-02-28 --format table
```

**JSON Output**:
```json
{
  "start": "2026-02-01",
  "end": "2026-02-28",
  "business_days": ["2026-02-02", "2026-02-03", "..."],
  "count": 19,
  "market": "jpx-index"
}
```

**Table Output**:
```
┌────────────┐
│ Date       │
├────────────┤
│ 2026-02-02 │
│ 2026-02-03 │
│ ...        │
└────────────┘
Total: 19 business days
```

---

#### bd count

期間内の営業日数をカウントする。

```bash
mks bd count <START> <END>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| START | date | Yes | 開始日（YYYY-MM-DD形式） |
| END | date | Yes | 終了日（YYYY-MM-DD形式） |

**Examples**:
```bash
mks bd count 2026-02-01 2026-02-28
```

**JSON Output**:
```json
{
  "start": "2026-02-01",
  "end": "2026-02-28",
  "count": 19,
  "market": "jpx-index"
}
```

---

### sq (SQ Day - SQ日)

#### sq get

指定年月のSQ日を取得する。

```bash
mks sq get <YEAR_MONTH>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| YEAR_MONTH | string | Yes | 年月（複数形式対応） |

**Supported Formats**:
- 2引数形式: `2026 3`
- YYYYMM形式: `202603`
- YYYY-MM形式: `2026-03`

**Examples**:
```bash
mks sq get 2026 3
mks sq get 202603
mks sq get 2026-03
mks sq get 2026-03 --format text
```

**JSON Output**:
```json
{
  "year": 2026,
  "month": 3,
  "sq_date": "2026-03-13",
  "market": "jpx-index"
}
```

**Text Output**:
```
2026年3月のSQ日は 2026-03-13 です
```

---

#### sq list

指定年の全SQ日リストを取得する。

```bash
mks sq list <YEAR>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| YEAR | int | Yes | 年 |

**Examples**:
```bash
mks sq list 2026
mks sq list 2026 --format table
```

**JSON Output**:
```json
{
  "year": 2026,
  "sq_dates": [
    {"month": 1, "date": "2026-01-09"},
    {"month": 2, "date": "2026-02-13"},
    "..."
  ],
  "market": "jpx-index"
}
```

---

#### sq is

指定日がSQ日かどうかを判定する。

```bash
mks sq is <DATE>
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| DATE | date | Yes | 判定対象日（YYYY-MM-DD形式） |

**Examples**:
```bash
mks sq is 2026-03-13
mks sq is 2026-03-13 --format text
```

**JSON Output**:
```json
{
  "date": "2026-03-13",
  "is_sq_date": true,
  "market": "jpx-index"
}
```

**Text Output**:
```
2026-03-13 はSQ日です
```

---

### ss (Session - セッション)

#### ss get

指定時刻のセッションを取得する。

```bash
mks ss get [DATETIME]
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| DATETIME | datetime | No | 判定対象時刻（ISO 8601形式、タイムゾーン必須） |

**Note**: DATETIME を省略した場合は現在時刻を使用。

**Examples**:
```bash
mks ss get
mks ss get 2026-02-06T10:00:00+09:00
mks ss get 2026-02-06T01:00:00Z  # UTC
```

**JSON Output**:
```json
{
  "datetime": "2026-02-06T10:00:00+09:00",
  "session": "day",
  "session_name": "日中立会",
  "market": "jpx-index"
}
```

**Text Output**:
```
2026-02-06T10:00:00+09:00 は日中立会です
```

**Error (No timezone)**:
```bash
mks ss get 2026-02-06T10:00:00
```
```json
{
  "error": "TimezoneRequiredError",
  "message": "タイムゾーン情報が必要です。例: 2026-02-06T10:00:00+09:00"
}
```
Exit code: 1

---

#### ss is-trading

指定時刻が取引可能時間かどうかを判定する。

```bash
mks ss is-trading [DATETIME]
```

**Arguments**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| DATETIME | datetime | No | 判定対象時刻（ISO 8601形式、タイムゾーン必須） |

**Note**: DATETIME を省略した場合は現在時刻を使用。

**Examples**:
```bash
mks ss is-trading
mks ss is-trading 2026-02-06T10:00:00+09:00
mks ss is-trading 2026-02-06T16:30:00+09:00  # ギャップ期間
```

**JSON Output**:
```json
{
  "datetime": "2026-02-06T10:00:00+09:00",
  "is_trading": true,
  "market": "jpx-index"
}
```

**JSON Output (Gap period)**:
```json
{
  "datetime": "2026-02-06T16:30:00+09:00",
  "is_trading": false,
  "market": "jpx-index"
}
```

---

### cache (Cache Management - キャッシュ管理)

#### cache update

キャッシュを更新する。

```bash
mks cache update
```

**Examples**:
```bash
mks cache update
mks cache update -m jpx-index
```

**JSON Output (Success)**:
```json
{
  "status": "success",
  "market": "jpx-index",
  "updated_at": "2026-02-05T10:00:00+09:00"
}
```

**JSON Output (Error)**:
```json
{
  "status": "error",
  "error": "DataFetchError",
  "message": "JPX公式サイトからのデータ取得に失敗しました"
}
```
Exit code: 1

---

#### cache clear

キャッシュをクリアする。

```bash
mks cache clear
```

**Examples**:
```bash
mks cache clear
mks cache clear -m jpx-index
```

**JSON Output**:
```json
{
  "status": "success",
  "market": "jpx-index",
  "cleared_at": "2026-02-05T10:00:00+09:00"
}
```

---

#### cache status

キャッシュの状態を表示する。

```bash
mks cache status
```

**Examples**:
```bash
mks cache status
mks cache status --format table
```

**JSON Output**:
```json
{
  "caches": [
    {
      "market": "jpx-index",
      "last_updated": "2026-02-05T10:00:00+09:00",
      "is_valid": true,
      "size_bytes": 12345,
      "cache_path": "/home/user/.cache/marketsched/jpx-index/"
    }
  ]
}
```

**JSON Output (No cache)**:
```json
{
  "caches": [
    {
      "market": "jpx-index",
      "last_updated": null,
      "is_valid": false,
      "size_bytes": 0,
      "cache_path": "/home/user/.cache/marketsched/jpx-index/"
    }
  ]
}
```

**Table Output**:
```
┌───────────┬─────────────────────────┬───────┬───────────┐
│ Market    │ Last Updated            │ Valid │ Size      │
├───────────┼─────────────────────────┼───────┼───────────┤
│ jpx-index │ 2026-02-05T10:00:00+09  │ Yes   │ 12.3 KB   │
└───────────┴─────────────────────────┴───────┴───────────┘
```

---

## Exit Codes

| Code | Description |
|------|-------------|
| 0 | Success |
| 1 | Error (invalid input, data not found, etc.) |
| 2 | Invalid command or arguments |

---

## Error Handling

全てのエラーは以下の形式で出力される（JSON形式の場合）：

```json
{
  "error": "ErrorClassName",
  "message": "エラーの詳細メッセージ"
}
```

| Error | Description |
|-------|-------------|
| MarketNotFoundError | 指定された市場が存在しない |
| SQDataNotFoundError | SQ日データが存在しない |
| TimezoneRequiredError | タイムゾーン情報が必要 |
| CacheNotAvailableError | キャッシュが利用不可 |
| DataFetchError | データ取得に失敗 |
| InvalidDataFormatError | データ形式が不正 |
