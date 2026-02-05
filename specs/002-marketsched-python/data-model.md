# Data Model: marketsched Python 実装

**Feature Branch**: `002-marketsched-python`
**Created**: 2026-02-05

## Implementation Note

本プロジェクトでは **Pydantic v2** を部分的に採用する。
関連プロジェクト [marketschema](https://github.com/driller/marketschema) との一貫性、
および `AwareDatetime` 型によるタイムゾーン強制（Constitution III準拠）のため。

| エンティティ | Pydantic | 実装方式 |
|-------------|----------|---------|
| ContractMonth | ✅ | `BaseModel` (frozen) |
| CacheMetadata | ✅ | `BaseModel` |
| CacheInfo | ✅ | `BaseModel` |
| TradingSession | ❌ | 標準 `Enum` |
| Market | ❌ | 標準 `Protocol` |

## Entities

### 1. ContractMonth（限月） - Pydantic BaseModel

**Description**: 先物・オプション契約の満期月を表す値オブジェクト

**Implementation**: `pydantic.BaseModel` with `frozen=True`

```python
from pydantic import BaseModel, ConfigDict, Field

class ContractMonth(BaseModel):
    model_config = ConfigDict(frozen=True)

    year: int = Field(ge=2000, le=2099, description="西暦年（4桁）")
    month: int = Field(ge=1, le=12, description="月")
```

| Field | Type | Description | Constraints |
|-------|------|-------------|-------------|
| year | int | 西暦年（4桁） | ge=2000, le=2099 |
| month | int | 月 | ge=1, le=12 |

**Validation Rules**:
- Pydantic Field constraints による自動バリデーション
- 2桁年号は `parse()` メソッドで2000年代として解釈

**State Transitions**: なし（frozen=True でイミュータブル）

**Operations**:
- `parse(text: str) -> ContractMonth`: 日本語表記からパース（classmethod）
- `to_yyyymm() -> str`: "202603" 形式に変換
- `to_japanese() -> str`: "2026年3月限" 形式に変換
- 比較演算（`__lt__`, `__le__`, `__gt__`, `__ge__` を実装）
- ハッシュ可能（frozen=True により自動）

---

### 2. TradingSession（取引セッション）

**Description**: 取引セッション種別を表す列挙型

| Value | Description |
|-------|-------------|
| DAY | 日中立会（08:45-15:45） |
| NIGHT | ナイトセッション（17:00-翌06:00） |
| CLOSED | 取引時間外 |
| PRE_OPEN | プレオープニング |
| AUCTION | オークション |

**Note**: PRE_OPEN, AUCTION は将来拡張用。初期実装ではDAY, NIGHT, CLOSEDのみ。

---

### 3. Market（市場 - Protocol）

**Description**: 市場を抽象化するインターフェース

| Property | Type | Description |
|----------|------|-------------|
| market_id | str | 市場識別子（例: "jpx-index"） |
| name | str | 市場名（例: "JPX指数先物・オプション"） |
| timezone | ZoneInfo | 市場のタイムゾーン |

**Methods**:
| Method | Return Type | Description |
|--------|-------------|-------------|
| is_business_day(d: date) | bool | 営業日判定 |
| next_business_day(d: date) | date | 翌営業日取得 |
| previous_business_day(d: date) | date | 前営業日取得 |
| get_business_days(start, end) | list[date] | 期間内営業日リスト |
| count_business_days(start, end) | int | 期間内営業日数 |
| get_sq_date(year, month) | date | SQ日取得 |
| is_sq_date(d: date) | bool | SQ日判定 |
| get_sq_dates_for_year(year) | list[date] | 年間SQ日リスト |
| get_session(dt: datetime \| None) | TradingSession | セッション取得 |
| is_trading_hours(dt: datetime \| None) | bool | 取引可能判定 |

---

### 4. JPXIndex（JPX指数先物・オプション市場）

**Description**: JPX指数先物・オプション市場の具体実装

| Property | Value |
|----------|-------|
| market_id | "jpx-index" |
| name | "JPX指数先物・オプション" |
| timezone | ZoneInfo("Asia/Tokyo") |

**Business Day Rules**:
- 土日は休場
- 祝日は休場（祝日取引実施日を除く）
- 12月31日〜1月3日は休場

**Trading Sessions (JST)**:
| Session | Start | End |
|---------|-------|-----|
| DAY | 08:45 | 15:45 |
| NIGHT | 17:00 | 06:00 (翌日) |

**Gap Periods (CLOSED)**:
- 06:01 〜 08:44
- 15:46 〜 16:59

---

### 4.1 JPXIndexSessionTimes（立会時間定数）

**Description**: JPX指数先物・オプションの立会時間を定義する定数クラス

**Implementation**: `marketsched.jpx.session` モジュールに定義

```python
from datetime import time

class JPXIndexSessionTimes:
    """JPX指数先物・オプションの立会時間定数"""

    # 日中立会
    DAY_START = time(8, 45)
    DAY_END = time(15, 45)

    # ナイトセッション
    NIGHT_START = time(17, 0)
    NIGHT_END = time(6, 0)  # 翌日
```

| Constant | Type | Value | Description |
|----------|------|-------|-------------|
| DAY_START | time | 08:45 | 日中立会開始 |
| DAY_END | time | 15:45 | 日中立会終了 |
| NIGHT_START | time | 17:00 | ナイトセッション開始 |
| NIGHT_END | time | 06:00 | ナイトセッション終了（翌日） |

**Note**: 立会時間はJPX公式サイトの構造が複雑なため、定数として定義。変更頻度は低く、制度改革時のみ更新が必要。

**休業日判定**: 土日 + JPX公式Excelデータに基づく（年末年始・祝日のハードコード禁止）
- データソース: https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx

---

### 5. SQDate（SQ日データ）

**Description**: Parquetキャッシュに保存されるSQ日データ

| Column | Type | Description |
|--------|------|-------------|
| year | int32 | 年 |
| month | int32 | 月 |
| sq_date | date | SQ日 |
| product_type | string | 商品種別（"index"等） |

---

### 6. HolidayTrading（祝日取引実施日データ）

**Description**: Parquetキャッシュに保存される祝日取引実施日データ

| Column | Type | Description |
|--------|------|-------------|
| date | date | 対象日 |
| holiday_name | string | 祝日名 |
| is_trading | bool | 取引実施フラグ |
| is_confirmed | bool | 確定/予定フラグ |

---

### 7. CacheMetadata（キャッシュメタデータ） - Pydantic BaseModel

**Description**: キャッシュの状態を管理するメタデータ

**Implementation**: `pydantic.BaseModel` with `AwareDatetime`

```python
from pydantic import BaseModel, AwareDatetime

class CacheMetadata(BaseModel):
    last_updated: AwareDatetime
    version: str
    source_urls: dict[str, str]
    cache_valid_until: AwareDatetime
```

| Field | Type | Description |
|-------|------|-------------|
| last_updated | AwareDatetime | 最終更新日時（タイムゾーン必須） |
| version | str | データバージョン |
| source_urls | dict[str, str] | データソースURL |
| cache_valid_until | AwareDatetime | キャッシュ有効期限（タイムゾーン必須） |

**Note**: `AwareDatetime` により naive datetime を自動的に拒否（Constitution III準拠）

---

### 8. CacheInfo（キャッシュ情報） - Pydantic BaseModel

**Description**: CLI出力用のキャッシュ状態情報

**Implementation**: `pydantic.BaseModel`

```python
from pathlib import Path
from pydantic import BaseModel, AwareDatetime

class CacheInfo(BaseModel):
    market: str
    last_updated: AwareDatetime | None
    is_valid: bool
    size_bytes: int
    cache_path: Path
```

| Field | Type | Description |
|-------|------|-------------|
| market | str | 市場ID |
| last_updated | AwareDatetime \| None | 最終更新日時（キャッシュなしの場合None） |
| is_valid | bool | キャッシュが有効かどうか |
| size_bytes | int | キャッシュサイズ（バイト） |
| cache_path | Path | キャッシュファイルのパス |

---

## Exception Hierarchy

```
MarketshedError (base)
├── MarketNotFoundError       # 市場が見つからない
├── ContractMonthParseError   # 限月の解析に失敗
├── SQDataNotFoundError       # SQ日データが存在しない
├── SQNotSupportedError       # SQ日機能がサポートされていない市場
├── TimezoneRequiredError     # タイムゾーン情報が必要
├── CacheNotAvailableError    # キャッシュが利用不可
├── DataFetchError            # データ取得に失敗
└── InvalidDataFormatError    # データ形式が不正
```

---

## Relationships

```
                    ┌──────────────┐
                    │   Market     │◄──── Protocol
                    │  (Protocol)  │
                    └──────────────┘
                           ▲
                           │ implements
                           │
                    ┌──────────────┐
                    │   JPXIndex   │
                    └──────────────┘
                           │
                           │ uses
                           ▼
         ┌─────────────────┼─────────────────┐
         │                 │                 │
         ▼                 ▼                 ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│   SQDate     │  │HolidayTrading│  │TradingSession│
│  (Parquet)   │  │  (Parquet)   │  │   (Enum)     │
└──────────────┘  └──────────────┘  └──────────────┘

┌──────────────┐
│ContractMonth │ ─── 独立した値オブジェクト
│(Value Object)│
└──────────────┘
```

---

## Data Flow

```
JPX公式サイト
     │
     │ httpx + openpyxl
     ▼
┌─────────────┐
│  Fetcher    │──────► DataFetchError (ネットワークエラー)
└─────────────┘        InvalidDataFormatError (形式エラー)
     │
     │ pyarrow
     ▼
┌─────────────┐
│   Cache     │──────► CacheNotAvailableError (オフライン時)
│  (Parquet)  │
└─────────────┘
     │
     │ pyarrow
     ▼
┌─────────────┐
│  JPXIndex   │──────► SQDataNotFoundError (データなし)
│   Market    │        TimezoneRequiredError (TZなし)
└─────────────┘
     │
     │ Market Protocol
     ▼
┌─────────────┐
│    CLI      │──────► MarketNotFoundError (市場なし)
│  (Typer)    │
└─────────────┘
```
