# アーキテクチャ

marketsched の設計原則とアーキテクチャについて解説します。

## 設計原則

### 1. 一次情報参照（Authoritative Data First）

SQ日・祝日休業日のデータは**計算ではなく公式データを参照**します。
「第2金曜日」のような計算ルールは使用せず、JPX公式サイトが公開するExcelファイルから正確なデータを取得します。

### 2. 市場の抽象化（Market Abstraction）

`Market` プロトコルにより、市場固有のルールを差し替え可能な設計としています。
新しい市場を追加する場合でも、既存コードの変更は不要です。

### 3. タイムゾーン明示（Explicit Timezone）

全ての `datetime` はタイムゾーン付きであることを要求します。
naive datetime（タイムゾーンなし）は `TimezoneRequiredError` で拒否されます。

### 4. シンプルさ優先（Simplicity First）

80%のユースケースに最適化し、過度な抽象化を避けます。
YAGNI（You Aren't Gonna Need It）原則に従います。

### 5. スタンドアロン動作（Standalone Operation）

ローカルキャッシュにより、実行時の外部API依存がありません。
初回のデータ取得以降はオフラインでも動作します。

## パッケージ構造

```{mermaid}
graph TD
    A["marketsched<br>__init__.py"] --> B["market.py<br>Market Protocol"]
    A --> C["registry.py<br>MarketRegistry"]
    A --> D["contract_month.py<br>ContractMonth"]
    A --> E["session.py<br>TradingSession"]
    A --> F["cache.py<br>Cache API"]
    A --> G["exceptions.py"]
    A --> H["cli/"]
    A --> I["jpx/"]

    I --> J["index.py<br>JPXIndex"]
    I --> K["calendar.py<br>JPXCalendar"]
    I --> L["session.py<br>SessionTimes"]
    I --> M["data/"]

    M --> N["cache.py<br>ParquetCacheManager"]
    M --> O["fetcher.py<br>JPXDataFetcher"]
    M --> P["query.py<br>JPXDataQuery"]

    H --> Q["main.py<br>Typer App"]
    H --> R["bd.py / sq.py<br>ss.py / cache.py"]
```

### レイヤー構成

| レイヤー | モジュール | 役割 |
|---------|-----------|------|
| CLI層 | `cli/` | Typerコマンド、入出力フォーマット |
| API層 | `__init__.py`, `cache.py` | パッケージ公開API |
| ドメイン層 | `market.py`, `jpx/` | ビジネスロジック（営業日・SQ日・セッション） |
| データ層 | `jpx/data/` | キャッシュ管理、データ取得・解析 |
| 共通 | `contract_month.py`, `session.py`, `exceptions.py` | 値オブジェクト、列挙型、例外 |

## データフロー

```{mermaid}
flowchart LR
    JPX["JPX公式サイト<br>Excel/HTML"] -->|"httpx + openpyxl"| Fetcher["JPXDataFetcher"]
    Fetcher -->|"pyarrow"| Cache["Parquetキャッシュ<br>~/.cache/marketsched/"]
    Cache -->|"pyarrow"| Query["JPXDataQuery"]
    Query --> Calendar["JPXCalendar"]
    Calendar --> Index["JPXIndex<br>(Market)"]
    Index --> API["Python API"]
    Index --> CLI["CLI (Typer)"]
```

### データ取得フロー

1. **初回アクセス時**: キャッシュが存在しない場合、JPX公式サイトからExcelファイルを自動取得
2. **パース**: openpyxl でExcelを解析し、SQ日・祝日取引実施日のレコードを抽出
3. **キャッシュ保存**: PyArrow を使用して Parquet 形式で保存（メタデータ含む）
4. **読み取り**: 以降のアクセスではキャッシュから高速に読み取り
5. **有効期限**: 24時間経過後のアクセスで自動的に再取得

## Market Protocol パターン

```{mermaid}
classDiagram
    class Market {
        <<Protocol>>
        +market_id: str
        +name: str
        +timezone: ZoneInfo
        +is_business_day(d) bool
        +next_business_day(d) date
        +previous_business_day(d) date
        +get_business_days(start, end) list~date~
        +count_business_days(start, end) int
        +get_sq_date(year, month) date
        +is_sq_date(d) bool
        +get_sq_dates_for_year(year) list~date~
        +get_session(dt) TradingSession
        +is_trading_hours(dt) bool
    }

    class JPXIndex {
        +market_id = "jpx-index"
        +name = "JPX Index Futures & Options"
        +timezone = Asia/Tokyo
    }

    Market <|.. JPXIndex : implements
```

`Market` は `typing.Protocol` を使用した構造的部分型です。
明示的な継承なしに、必要なメソッドとプロパティを実装するだけで `Market` として扱えます。

## MarketRegistry パターン

市場の登録と取得を管理するレジストリパターンを採用しています。

```python
# 市場の登録（デコレータ）
@MarketRegistry.register("jpx-index")
class JPXIndex:
    ...

# 市場の取得
market = MarketRegistry.get("jpx-index")  # JPXIndex のインスタンス
```

`marketsched.get_market()` は内部で `MarketRegistry.get()` を呼び出します。

## JPX立会時間

```{mermaid}
gantt
    title JPX指数先物・オプション 立会時間 (JST)
    dateFormat HH:mm
    axisFormat %H:%M
    section 取引セッション
    ナイトセッション(前日分) : active, ns1, 00:00, 06:00
    プレマーケット : crit, gap1, 06:00, 08:45
    日中立会 : active, day, 08:45, 15:45
    セッション間 : crit, gap2, 15:45, 17:00
    ナイトセッション : active, ns2, 17:00, 23:59
```

| 時間帯 | セッション | `is_trading_hours()` |
|--------|-----------|---------------------|
| 00:00 - 06:00 | NIGHT（前日分） | `True` |
| 06:00 - 08:45 | CLOSED | `False` |
| 08:45 - 15:45 | DAY | `True` |
| 15:45 - 17:00 | CLOSED | `False` |
| 17:00 - 24:00 | NIGHT | `True` |

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

エラーは発生箇所に応じた具体的な例外クラスで報告されます。
`MarketschedError` を基底として使用することで、全ての marketsched エラーを一括でキャッチできます。

詳細は {doc}`api/exceptions` を参照してください。

## キャッシュ機構

### 保存形式

データは [Apache Parquet](https://parquet.apache.org/) 形式で保存されます。

- **メタデータ**: Parquet ファイルのカスタムメタデータ（`b"marketsched_metadata"` キー）にJSON形式で格納
- **スキーマバージョン**: メタデータにバージョン番号を含み、形式変更時の互換性を管理

### キャッシュファイル

| ファイル | データ種別 | 内容 |
|---------|-----------|------|
| `sq_dates.parquet` | SQ日データ | 限月、最終取引日、権利行使日 |
| `holiday_trading.parquet` | 祝日取引データ | 祝日、取引実施有無 |

### 有効期限

キャッシュの有効期限はデフォルトで24時間です。
期限切れのキャッシュは次回アクセス時に自動的に再取得されます。

## 新しい市場の追加

新しい市場を追加する場合の手順：

1. `marketsched/` 配下に市場固有のモジュールを作成（例: `cme/`）
2. `Market` プロトコルに準拠したクラスを実装
3. `@MarketRegistry.register("market-id")` で登録
4. 必要に応じてデータ取得・キャッシュ機構を実装

既存の `jpx/` モジュールを参考にしてください。
