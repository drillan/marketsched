# Research: marketsched Python 実装

**Feature Branch**: `002-marketsched-python`
**Research Date**: 2026-02-05

## 1. JPX公式データ取得

### 1.1 データソース分析

| データ種別 | URL | 形式 | 取得方法 |
|-----------|-----|------|---------|
| 取引最終日（SQ日） | [last-trading-day](https://www.jpx.co.jp/derivatives/rules/last-trading-day/index.html) | **Excel (.xlsx)** | httpx + openpyxl |
| 祝日取引実施日 | [holidaytrading](https://www.jpx.co.jp/derivatives/rules/holidaytrading/index.html) | **Excel (.xlsx)** | httpx + openpyxl |
| 立会時間 | [trading-hours](https://www.jpx.co.jp/derivatives/rules/trading-hours/index.html) | 複雑な構造 | 市場定義の定数 |

**Excelファイル直接リンク**:
- SQ日: `https://www.jpx.co.jp/derivatives/rules/last-trading-day/tvdivq0000004gz8-att/2026_indexfutures_options_1_j.xlsx`
- 祝日取引: `https://www.jpx.co.jp/derivatives/rules/holidaytrading/nlsgeu000006hweb-att/nlsgeu000006jgee.xlsx`

### 1.2 robots.txt 確認結果

- **スクレイピング許可**: `Disallow`フィールドが空のため、技術的には許可
- **Sitemap**: https://www.jpx.co.jp/sitemap.xml が提供
- **推奨**: 適切なUser-Agent設定とリクエスト間隔を設ける

### 1.3 データ取得方針

**Decision**: httpx + openpyxl のスタックを採用

**Rationale**:
- SQ日・祝日取引実施日の両方がExcel形式で提供されている
- openpyxl でExcelファイルを直接解析
- 立会時間はページ構造が複雑なため、市場定義モジュール内に定数として定義（変更頻度が低く、制度改革時のみ更新）

**Alternatives considered**:
- BeautifulSoup: HTMLスクレイピング不要のため却下
- pandas.read_excel(): openpyxlで十分、依存を最小化
- requests: httpxの方がasync対応で将来拡張しやすい（今回はsync使用）

### 1.4 データ更新頻度

| データ | 更新頻度 | キャッシュ有効期限推奨 |
|--------|---------|---------------------|
| SQ日 | 年度ごと | 24時間（デフォルト） |
| 祝日取引実施日 | 毎年2月頃 | 24時間 |
| 立会時間 | 制度改革時のみ | コード内定数 |

---

## 2. Parquetキャッシュ実装

### 2.1 PyArrowによる実装方針

**Decision**: pyarrow.parquet で単純な読み書きを実装

**Rationale**:
- 高速読み込み、型保持、圧縮効率のバランスが良い
- メタデータにスクレイピング日時を記録可能
- pandasへの変換も容易

### 2.2 キャッシュファイル構造

```
~/.cache/marketsched/
├── jpx-index/
│   ├── sq_dates.parquet      # SQ日データ
│   ├── holiday_trading.parquet  # 祝日取引実施日
│   └── metadata.json         # 最終更新日時等
```

### 2.3 メタデータ設計

```json
{
  "last_updated": "2026-02-05T10:00:00+09:00",
  "version": "1.0.0",
  "source_urls": {
    "sq_dates": "https://www.jpx.co.jp/...",
    "holiday_trading": "https://www.jpx.co.jp/..."
  }
}
```

---

## 3. Typer CLI設計

### 3.1 サブコマンド構造

**Decision**: `app.add_typer()` による階層化

```
marketsched (mks)
├── bd (営業日)
│   ├── is <date>
│   ├── next <date>
│   ├── prev <date>
│   ├── list <start> <end>
│   └── count <start> <end>
├── sq (SQ日)
│   ├── get <year> [month] または <YYYYMM> または <YYYY-MM>
│   ├── list <year>
│   └── is <date>
├── ss (セッション)
│   ├── get [datetime]
│   └── is-trading [datetime]
└── cache
    ├── update
    ├── clear
    └── status
```

### 3.2 エイリアス実装

**Decision**: pyproject.toml で複数エントリポイント定義

```toml
[project.scripts]
marketsched = "marketsched.cli:main"
mks = "marketsched.cli:main"
```

**Rationale**:
- 最もシンプルで追加依存なし
- OSレベルで両コマンドが利用可能

### 3.3 出力形式

**Decision**: Rich ライブラリ統合

| 形式 | 実装 |
|------|------|
| JSON（デフォルト） | `console.print_json()` |
| text | `console.print()` |
| table | `rich.table.Table` |

---

## 4. モジュール構造

### 4.1 パッケージレイアウト

**Decision**: 取引所単位でサブモジュール分離

```
src/marketsched/
├── __init__.py           # 公開API（get_market, get_available_markets）
├── py.typed              # 型チェッカーシグナル
├── market.py             # Market Protocol定義
├── contract_month.py     # ContractMonth値オブジェクト
├── session.py            # TradingSession列挙型
├── exceptions.py         # カスタム例外クラス
├── jpx/                  # JPX取引所サブモジュール
│   ├── __init__.py       # jpx公開API
│   ├── index.py          # JPXIndex市場実装
│   ├── calendar.py       # 営業日・SQ日ロジック
│   ├── session.py        # セッション定義
│   └── data/             # データ取得・キャッシュ
│       ├── __init__.py
│       ├── fetcher.py    # JPX公式サイトからの取得
│       └── cache.py      # Parquetキャッシュ
└── cli/                  # CLIモジュール
    ├── __init__.py
    ├── main.py           # エントリポイント
    ├── bd.py             # 営業日コマンド
    ├── sq.py             # SQ日コマンド
    ├── ss.py             # セッションコマンド
    └── cache.py          # キャッシュコマンド
```

### 4.2 import構造

```python
# ユーザー向けAPI
import marketsched
market = marketsched.get_market("jpx-index")

from marketsched import ContractMonth, TradingSession
from marketsched.jpx import JPXIndex  # 直接インポートも可能
```

---

## 5. Protocol/ABC設計

### 5.1 インターフェース選択

**Decision**: Protocol を採用（ABCは補完的に使用）

**Rationale**:
- 構造的部分型により、継承なしで市場実装が可能
- 型チェッカー（mypy, pyright）との親和性が高い
- 将来の市場追加時に既存コード変更不要

### 5.2 Market Protocol定義

```python
from typing import Protocol
from datetime import datetime, date
from zoneinfo import ZoneInfo

class Market(Protocol):
    market_id: str
    name: str
    timezone: ZoneInfo

    def is_business_day(self, d: date) -> bool: ...
    def next_business_day(self, d: date) -> date: ...
    def previous_business_day(self, d: date) -> date: ...
    def get_business_days(self, start: date, end: date) -> list[date]: ...
    def count_business_days(self, start: date, end: date) -> int: ...
    def get_sq_date(self, year: int, month: int) -> date: ...
    def is_sq_date(self, d: date) -> bool: ...
    def get_sq_dates_for_year(self, year: int) -> list[date]: ...
    def get_session(self, dt: datetime | None = None) -> TradingSession: ...
    def is_trading_hours(self, dt: datetime | None = None) -> bool: ...
```

### 5.3 市場レジストリ

**Decision**: デコレータベースの自動登録パターン

```python
@MarketRegistry.register("jpx-index")
class JPXIndex:
    ...

# 使用
market = marketsched.get_market("jpx-index")
markets = marketsched.get_available_markets()  # ["jpx-index"]
```

---

## 6. タイムゾーン処理

### 6.1 ナイーブdatetime拒否

**Decision**: 明示的な検証関数で拒否

```python
def validate_aware_datetime(dt: datetime) -> datetime:
    if dt.tzinfo is None or dt.tzinfo.utcoffset(dt) is None:
        raise TimezoneRequiredError(
            "タイムゾーン情報が必要です。例: datetime.now(ZoneInfo('Asia/Tokyo'))"
        )
    return dt
```

### 6.2 タイムゾーン変換

**Decision**: `astimezone()` による変換

```python
def convert_to_market_tz(dt: datetime, market_tz: ZoneInfo) -> datetime:
    """任意のタイムゾーン付きdatetimeを市場TZに変換"""
    return dt.astimezone(market_tz)
```

### 6.3 現在時刻の取得

```python
def get_current_market_time(market_tz: ZoneInfo) -> datetime:
    """現在時刻を市場TZで取得"""
    return datetime.now(market_tz)
```

---

## 7. 依存関係

### 7.1 本番依存

| パッケージ | 用途 | バージョン |
|-----------|------|-----------|
| pydantic | データモデル・バリデーション | >=2.0.0 |
| typer | CLI | >=0.9.0 |
| rich | 出力フォーマット（Typer同梱） | - |
| httpx | HTTPクライアント | >=0.27.0 |
| pyarrow | Parquetキャッシュ | >=15.0.0 |
| openpyxl | Excel解析（SQ日・祝日取引） | >=3.1.0 |

**削除した依存**:
- ~~beautifulsoup4~~: 祝日取引データもExcel提供のため不要
- ~~lxml~~: BeautifulSoup不要のため不要

### 7.2 開発依存

| パッケージ | 用途 |
|-----------|------|
| pytest | テスト |
| mypy | 型チェック |
| ruff | リンター・フォーマッター |

---

## 8. Pydantic v2 採用方針

### 8.1 採用判断

**Decision**: Pydantic v2 を部分的に採用

**Rationale**:
- 関連プロジェクト marketschema との一貫性
- `AwareDatetime` 型によるタイムゾーン強制（Constitution III準拠）
- バリデーションとシリアライゼーションの自動化
- CLI出力（JSON）との親和性

### 8.2 採用対象

| エンティティ | Pydantic | 理由 |
|-------------|----------|------|
| ContractMonth | ✅ 採用 | バリデーション（1-12月）、frozen、シリアライズ |
| CacheMetadata | ✅ 採用 | AwareDatetime、JSONシリアライズ |
| CacheInfo | ✅ 採用 | CLI出力用、構造化データ |
| TradingSession | ❌ 不採用 | 単純なEnum、標準ライブラリで十分 |
| Market Protocol | ❌ 不採用 | Protocol定義、Pydantic不向き |
| JPXIndex | ❌ 不採用 | ビジネスロジックが主 |

### 8.3 実装パターン

```python
from pydantic import BaseModel, ConfigDict, Field, AwareDatetime

# 値オブジェクト（イミュータブル）
class ContractMonth(BaseModel):
    model_config = ConfigDict(frozen=True)

    year: int = Field(ge=2000, le=2099)
    month: int = Field(ge=1, le=12)

# タイムゾーン強制
class CacheMetadata(BaseModel):
    last_updated: AwareDatetime  # naive datetime を拒否
    version: str
    source_urls: dict[str, str]
```

### 8.4 marketschema との連携

将来的に marketschema と marketsched を組み合わせて使用する場合、
両方が Pydantic v2 を使用しているため、モデル間の変換が自然に行える。

```python
# 将来の連携イメージ
from marketschema.models import Quote
from marketsched import get_market

market = get_market("jpx-index")
if market.is_trading_hours():
    # marketschema のモデルと組み合わせ
    quote: Quote = fetch_quote("N225")
```

---

## 9. 未解決事項

### 8.1 立会時間データの取得

**Status**: 市場定義モジュールに定数として定義

JPX立会時間ページは画像・テーブル・テキスト混合で自動取得が困難。
日経225先物・オプションの立会時間は変更頻度が低いため、`marketsched.jpx.session` モジュールに定数として定義。

```python
# marketsched/jpx/session.py
from datetime import time

class JPXIndexSessionTimes:
    """JPX指数先物・オプションの立会時間定数"""

    DAY_START = time(8, 45)
    DAY_END = time(15, 45)
    NIGHT_START = time(17, 0)
    NIGHT_END = time(6, 0)  # 翌日
```

将来的に取引時間が変更された場合は定数を更新。

### 8.2 Pythonバージョン

**Decision**: Python 3.10以上をサポート

現状のpyproject.tomlは3.13を指定しているが、仕様書では3.10以上。
ZoneInfo（3.9+）、match文（3.10+）、型ユニオン演算子（3.10+）を考慮し、3.10に変更。

---

## References

- [JPX 取引最終日](https://www.jpx.co.jp/derivatives/rules/last-trading-day/index.html)
- [JPX 祝日取引](https://www.jpx.co.jp/derivatives/rules/holidaytrading/index.html)
- [JPX 立会時間](https://www.jpx.co.jp/derivatives/rules/trading-hours/index.html)
- [Typer Documentation](https://typer.tiangolo.com/)
- [PyArrow Parquet](https://arrow.apache.org/docs/python/parquet.html)
- [PEP 544 - Protocols](https://peps.python.org/pep-0544/)
- [PEP 561 - py.typed](https://peps.python.org/pep-0561/)
