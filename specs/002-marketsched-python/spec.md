# Feature Specification: marketsched Python 実装

**Feature Branch**: `002-marketsched-python`
**Created**: 2026-02-05
**Status**: Draft
**Input**: User description: "specs/001-marketsched-core/spec.mdを親仕様として、python実装 002-marketsched-python を定義してください"

**Parent Specification**: [001-marketsched-core](../001-marketsched-core/spec.md)

## Clarifications

### Session 2026-02-05

- Q: CLIで提供する機能の範囲は？ → A: 営業日判定、SQ日取得、セッション判定の3機能
- Q: CLIの出力形式は？ → A: JSONデフォルト + `--format`オプションでtext/table選択可
- Q: データの提供方法は？ → A: キャッシュのみ（JPX公式サイトから取得してローカルキャッシュ、同梱データなし、オフライン時はエラー）
- Q: コマンド構造は？ → A: サブコマンド構造（例: `mks bd is 2026-02-06`）
- Q: 取引所・商品の指定方法は？ → A: `--market` / `-m` オプション（デフォルトはJPXデリバティブ）
- Q: パッケージコマンドの短縮形は？ → A: `mks`（marketsched と mks の両方を提供）
- Q: システム時刻でセッション判定できるか？ → A: 時刻引数を省略した場合、現在のシステム時刻を使用する
- Q: 営業日判定が祝日取引データを参照しているか？ → A: 参照する（祝日取引実施日リストに含まれる祝日は営業日として判定）
- Q: `mks sq get` の年月指定形式は？ → A: `2026 3`（2引数）、`202603`（YYYYMM）、`2026-03`（YYYY-MM）の3形式をサポート
- Q: 市場IDの粒度は？ → A: 商品カテゴリ単位でID分離（`jpx-index`, `jpx-equity-options`, `jpx-bond` 等）。初期実装は `jpx-index`（指数先物・オプション）
- Q: キャッシュのデータ形式は？ → A: Parquet形式（高速読み込み、型保持、圧縮効率のため）
- Q: パッケージのモジュール構造は？ → A: 取引所単位でサブモジュール分離（`marketsched.jpx`）。JPX内で祝日カレンダー等の共通ロジックを共有

## 概要

本仕様は、[marketsched コアライブラリ仕様](../001-marketsched-core/spec.md)（001-marketsched-core）のPython実装を定義する。コア仕様で定められた全ての機能要件（市場抽象化、限月正規化、営業日判定、SQ日参照、取引セッション管理、タイムゾーン変換）をPython言語で実装し、Pythonエコシステムのベストプラクティスに従ったパッケージとして提供する。

### 対象機能（コア仕様より）

- Market インターフェースの実装
- JPXデリバティブ市場の実装
- 限月の正規化と変換
- 営業日判定（前後営業日取得、期間内営業日リスト）
- SQ日参照（月次・年間SQ日取得、SQ日判定）
- 取引セッション管理（セッション判定、取引可能時間判定）
- タイムゾーン変換（UTC→市場固有TZ）

### Python実装固有の機能

- **CLI（コマンドラインインターフェース）**: Typerを使用した `mks` / `marketsched` コマンドを提供
  - サブコマンド構造: `bd`（営業日）、`sq`（SQ日）、`ss`（セッション）、`cache`（キャッシュ）
  - `--market` / `-m` オプションで市場指定（デフォルト: jpx-index）
  - JSON出力（デフォルト）、`--format` / `-f` オプションで text/table 選択可能
- **データキャッシュ機構**: JPX公式サイトからデータを取得しローカルにキャッシュ
  - 同梱データなし（オフライン時はエラー）
  - `mks cache update/clear/status` によるキャッシュ管理

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - パッケージのインストールとインポート (Priority: P1)

Pythonユーザーが、marketsched パッケージをインストールし、プロジェクトにインポートして利用を開始したい。

**Why this priority**: ユーザーが最初に行う操作であり、これが機能しなければ他の全ての機能を利用できない。

**Independent Test**: パッケージのインストールとインポートのみで完結し、テスト可能。

**Acceptance Scenarios**:

1. **Given** Python環境（3.10以上）, **When** `pip install marketsched` または `uv pip install marketsched` を実行, **Then** パッケージがインストールされる
2. **Given** インストール済み環境, **When** `import marketsched` を実行, **Then** エラーなくインポートできる
3. **Given** インストール済み環境, **When** `from marketsched import Market, JPXIndex` を実行, **Then** 主要なクラスをインポートできる

---

### User Story 2 - 限月オブジェクトの生成と変換 (Priority: P1)

Pythonユーザーが、日本語表記の限月から限月オブジェクトを生成し、各種形式に変換したい。

**Why this priority**: 限月は先物・オプション取引の基本識別子であり、全機能の基盤となる。

**Independent Test**: 限月の生成と変換のみで完結し、他の機能に依存せずテスト可能。

**Acceptance Scenarios**:

1. **Given** 文字列「26年3月限」, **When** `ContractMonth.parse("26年3月限")` を実行, **Then** year=2026, month=3 の限月オブジェクトが返される
2. **Given** 限月オブジェクト（year=2026, month=3）, **When** `.to_yyyymm()` を実行, **Then** 文字列「202603」が返される
3. **Given** 限月オブジェクト（year=2026, month=3）, **When** `.to_japanese()` を実行, **Then** 文字列「2026年3月限」が返される
4. **Given** 数値指定 year=2026, month=3, **When** `ContractMonth(2026, 3)` を実行, **Then** 正しい限月オブジェクトが生成される
5. **Given** 不正な文字列「3月限」, **When** `ContractMonth.parse("3月限")` を実行, **Then** `ContractMonthParseError` が発生する

---

### User Story 3 - 市場オブジェクトの取得と情報参照 (Priority: P1)

Pythonユーザーが、利用する市場を取得し、市場の基本情報を参照したい。

**Why this priority**: 市場オブジェクトは全ての機能の起点であり、必須の基盤。

**Independent Test**: 市場の取得と情報参照のみで完結し、テスト可能。

**Acceptance Scenarios**:

1. **Given** marketsched パッケージ, **When** `markets = marketsched.get_available_markets()` を実行, **Then** 利用可能な市場のリストが返される
2. **Given** marketsched パッケージ, **When** `market = marketsched.get_market("jpx-index")` を実行, **Then** JPX指数先物・オプション市場オブジェクトが返される
3. **Given** JPXデリバティブ市場オブジェクト, **When** `market.timezone` を参照, **Then** JST（Asia/Tokyo）が返される
4. **Given** JPXデリバティブ市場オブジェクト, **When** `market.name` を参照, **Then** 「JPXデリバティブ」が返される
5. **Given** 存在しない市場ID, **When** `marketsched.get_market("unknown")` を実行, **Then** `MarketNotFoundError` が発生する

---

### User Story 4 - 営業日判定の実行 (Priority: P1)

Pythonユーザーが、指定した日付が営業日かどうかを判定し、前後の営業日を取得したい。

**Why this priority**: 注文タイミング、決済日計算に不可欠な基本機能。

**Independent Test**: 日付と市場を入力し、営業日判定のみで完結。

**Acceptance Scenarios**:

1. **Given** JPXデリバティブ市場と `date(2026, 2, 6)`（金曜日、祝日でない）, **When** `market.is_business_day(date(2026, 2, 6))` を実行, **Then** `True` が返される
2. **Given** JPXデリバティブ市場と `date(2026, 2, 7)`（土曜日）, **When** `market.is_business_day(date(2026, 2, 7))` を実行, **Then** `False` が返される
3. **Given** JPXデリバティブ市場と祝日だが祝日取引実施日リストに含まれる日, **When** `market.is_business_day(holiday_trading_date)` を実行, **Then** `True` が返される
4. **Given** JPXデリバティブ市場と祝日で祝日取引実施日リストに含まれない日, **When** `market.is_business_day(regular_holiday)` を実行, **Then** `False` が返される
5. **Given** JPXデリバティブ市場と `date(2026, 2, 6)`（金曜日）, **When** `market.next_business_day(date(2026, 2, 6))` を実行, **Then** `date(2026, 2, 9)`（月曜日）が返される
6. **Given** JPXデリバティブ市場と `date(2026, 2, 9)`（月曜日）, **When** `market.previous_business_day(date(2026, 2, 9))` を実行, **Then** `date(2026, 2, 6)`（金曜日）が返される
7. **Given** JPXデリバティブ市場と `date(2026, 12, 31)`, **When** `market.is_business_day(date(2026, 12, 31))` を実行, **Then** `False` が返される（年末休場）

---

### User Story 5 - 期間内営業日の取得 (Priority: P2)

Pythonユーザーが、指定した期間内の営業日リストや営業日数を取得したい。

**Why this priority**: 期間計算はスケジュール管理に必要だが、単日判定より優先度は低い。

**Independent Test**: 期間と市場を入力し、営業日リスト取得のみで完結。

**Acceptance Scenarios**:

1. **Given** JPXデリバティブ市場と期間 `date(2026, 2, 1)` から `date(2026, 2, 28)`, **When** `market.get_business_days(start, end)` を実行, **Then** 期間内の全営業日がリストで返される
2. **Given** JPXデリバティブ市場と期間 `date(2026, 2, 1)` から `date(2026, 2, 28)`, **When** `market.count_business_days(start, end)` を実行, **Then** 期間内の営業日数が整数で返される
3. **Given** 返される営業日リスト, **When** リストを確認, **Then** 昇順（日付順）でソートされている

---

### User Story 6 - SQ日の取得と判定 (Priority: P1)

Pythonユーザーが、指定した年月のSQ日を取得し、特定の日付がSQ日かどうかを判定したい。

**Why this priority**: SQ日はポジション管理に直接影響する重要日付。

**Independent Test**: 年月と市場を入力し、SQ日取得のみで完結。

**Acceptance Scenarios**:

1. **Given** JPXデリバティブ市場と年月（2026, 3）, **When** `market.get_sq_date(2026, 3)` を実行, **Then** 2026年3月のSQ日が `date` オブジェクトで返される
2. **Given** JPXデリバティブ市場とSQ日である日付, **When** `market.is_sq_date(sq_date)` を実行, **Then** `True` が返される
3. **Given** JPXデリバティブ市場とSQ日でない日付, **When** `market.is_sq_date(non_sq_date)` を実行, **Then** `False` が返される
4. **Given** JPXデリバティブ市場と年（2026）, **When** `market.get_sq_dates_for_year(2026)` を実行, **Then** 12ヶ月分のSQ日リストが昇順で返される
5. **Given** データが存在しない年月（例: 2050, 1）, **When** `market.get_sq_date(2050, 1)` を実行, **Then** `SQDataNotFoundError` が発生する

---

### User Story 7 - 取引セッション判定 (Priority: P2)

Pythonユーザーが、指定した時刻または現在時刻がどの取引セッションに属するかを判定したい。

**Why this priority**: リアルタイム判断に必要だが、日付機能より優先度は低い。

**Independent Test**: 時刻と市場を入力し、セッション判定のみで完結。

**Acceptance Scenarios**:

1. **Given** JPXデリバティブ市場と時刻 `datetime(2026, 2, 6, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo"))`, **When** `market.get_session(dt)` を実行, **Then** `TradingSession.DAY` が返される
2. **Given** JPXデリバティブ市場と時刻 `datetime(2026, 2, 6, 20, 0, tzinfo=ZoneInfo("Asia/Tokyo"))`, **When** `market.get_session(dt)` を実行, **Then** `TradingSession.NIGHT` が返される
3. **Given** JPXデリバティブ市場とギャップ期間の時刻 `datetime(2026, 2, 6, 16, 30, tzinfo=ZoneInfo("Asia/Tokyo"))`, **When** `market.is_trading_hours(dt)` を実行, **Then** `False` が返される
4. **Given** タイムゾーン情報のない datetime, **When** `market.get_session(naive_dt)` を実行, **Then** `TimezoneRequiredError` が発生する
5. **Given** UTC時刻 `datetime(2026, 2, 6, 1, 0, tzinfo=timezone.utc)`（= JST 10:00）, **When** `market.get_session(utc_dt)` を実行, **Then** `TradingSession.DAY` が返される
6. **Given** JPXデリバティブ市場と時刻引数なし, **When** `market.get_session()` を実行, **Then** 現在のシステム時刻に基づくセッションが返される
7. **Given** JPXデリバティブ市場と時刻引数なし, **When** `market.is_trading_hours()` を実行, **Then** 現在のシステム時刻で取引可能かどうかが返される

---

### User Story 8 - CLIによる営業日判定 (Priority: P2)

ターミナルユーザーが、コマンドラインから営業日判定を実行したい。

**Why this priority**: CLIはライブラリ機能の補助的なインターフェースであり、コア機能実装後に提供する。

**Independent Test**: CLIコマンドの実行のみで完結し、テスト可能。

**Acceptance Scenarios**:

1. **Given** インストール済み環境, **When** `mks bd is 2026-02-06` を実行, **Then** JSON形式で結果が出力される
2. **Given** インストール済み環境, **When** `mks bd is 2026-02-06 --format text` を実行, **Then** 人間可読なテキスト形式で結果が出力される
3. **Given** インストール済み環境, **When** `mks bd next 2026-02-06` を実行, **Then** 翌営業日がJSON形式で出力される
4. **Given** インストール済み環境, **When** `mks bd list 2026-02-01 2026-02-28` を実行, **Then** 期間内の営業日リストがJSON形式で出力される
5. **Given** インストール済み環境, **When** `mks bd is 2026-02-06 -m jpx-index` を実行, **Then** 指定市場での結果が出力される

---

### User Story 9 - CLIによるSQ日取得 (Priority: P2)

ターミナルユーザーが、コマンドラインからSQ日を取得したい。

**Why this priority**: CLIはライブラリ機能の補助的なインターフェースである。

**Independent Test**: CLIコマンドの実行のみで完結し、テスト可能。

**Acceptance Scenarios**:

1. **Given** インストール済み環境, **When** `mks sq get 2026 3` を実行, **Then** 2026年3月のSQ日がJSON形式で出力される
2. **Given** インストール済み環境, **When** `mks sq get 202603` を実行, **Then** 2026年3月のSQ日がJSON形式で出力される（YYYYMM形式）
3. **Given** インストール済み環境, **When** `mks sq get 2026-03` を実行, **Then** 2026年3月のSQ日がJSON形式で出力される（YYYY-MM形式）
4. **Given** インストール済み環境, **When** `mks sq list 2026` を実行, **Then** 2026年の全SQ日リストがJSON形式で出力される
5. **Given** インストール済み環境, **When** `mks sq is 2026-03-13` を実行, **Then** SQ日判定結果がJSON形式で出力される

---

### User Story 10 - CLIによるセッション判定 (Priority: P2)

ターミナルユーザーが、コマンドラインから取引セッションを判定したい。

**Why this priority**: CLIはライブラリ機能の補助的なインターフェースである。

**Independent Test**: CLIコマンドの実行のみで完結し、テスト可能。

**Acceptance Scenarios**:

1. **Given** インストール済み環境, **When** `mks ss get 2026-02-06T10:00:00+09:00` を実行, **Then** セッション（DAY等）がJSON形式で出力される
2. **Given** インストール済み環境, **When** `mks ss is-trading 2026-02-06T10:00:00+09:00` を実行, **Then** 取引可能判定結果がJSON形式で出力される
3. **Given** タイムゾーンなしの時刻, **When** `mks ss get 2026-02-06T10:00:00` を実行, **Then** エラーメッセージが出力される
4. **Given** インストール済み環境, **When** `mks ss get` を時刻引数なしで実行, **Then** 現在時刻でのセッションがJSON形式で出力される
5. **Given** インストール済み環境, **When** `mks ss is-trading` を時刻引数なしで実行, **Then** 現在時刻での取引可能判定結果がJSON形式で出力される

---

### User Story 11 - データキャッシュの管理 (Priority: P1)

ユーザーが、JPX公式データをキャッシュして利用したい。

**Why this priority**: データなしでは全機能が動作しないため、キャッシュ機構は必須。

**Independent Test**: キャッシュ操作のみで完結し、テスト可能。

**Acceptance Scenarios**:

1. **Given** 初回起動時, **When** データを必要とする機能を呼び出す, **Then** JPX公式サイトからデータを取得しキャッシュされる
2. **Given** キャッシュ済み環境, **When** `mks cache update` を実行, **Then** キャッシュが最新データで更新される
3. **Given** キャッシュ済み環境, **When** `mks cache clear` を実行, **Then** キャッシュがクリアされる
4. **Given** キャッシュ済み環境, **When** `mks cache status` を実行, **Then** キャッシュの状態（最終更新日時等）が表示される
5. **Given** オフライン環境でキャッシュなし, **When** データを必要とする機能を呼び出す, **Then** `CacheNotAvailableError` が発生し、オンライン接続が必要な旨が案内される

---

### Edge Cases

- `ContractMonth(2026, 13)` や `ContractMonth(2026, 0)` は `ValueError` を発生させる
- 2桁年号（例: 99年）は2099年として解釈される
- `date(2028, 2, 29)`（閏年）の営業日判定が正しく動作する
- 年末年始境界で正しく判定される（JPXデリバティブ休場日: 12/31, 1/1, 1/2, 1/3）
- ナイトセッションの日付跨ぎ（17:00〜翌06:00）が正しく処理される
- UTC時刻が日付境界をまたぐ場合（UTC 15:00 = JST 翌日00:00）、正しくJSTで判定される
- オフライン環境でキャッシュなしの場合、`CacheNotAvailableError` が発生する
- JPX公式サイトのデータ形式が変更された場合、`InvalidDataFormatError` が発生する
- ネットワークエラー時は `DataFetchError` が発生し、既存キャッシュがあればそれを使用する

---

## Requirements *(mandatory)*

### Functional Requirements

#### パッケージ構成 (PKG)

- **FR-PKG-001**: パッケージは `pip install marketsched` でインストール可能でなければならない
- **FR-PKG-002**: パッケージは Python 3.10 以上をサポートしなければならない
- **FR-PKG-003**: パッケージは外部依存を最小化しなければならない（許可される依存: Pydantic, Typer, httpx, pyarrow, openpyxl）
- **FR-PKG-004**: パッケージは型ヒント（Type Hints）を完全にサポートしなければならない
- **FR-PKG-005**: パッケージは `py.typed` マーカーを含み、型チェッカーと互換性を持たなければならない
- **FR-PKG-006**: パッケージは取引所単位でサブモジュールを分離しなければならない（例: `marketsched.jpx`）
- **FR-PKG-007**: 取引所サブモジュール内で共通ロジック（祝日カレンダー、データ取得等）を共有しなければならない

#### Market 実装 (MKT)

- **FR-MKT-001**: コア仕様の Market インターフェースを Python の Protocol または ABC として実装しなければならない
- **FR-MKT-002**: `marketsched.get_market(market_id: str) -> Market` で市場を取得できなければならない
- **FR-MKT-003**: `marketsched.get_available_markets() -> list[str]` で利用可能な市場IDリストを取得できなければならない
- **FR-MKT-004**: 市場オブジェクトは `timezone`, `name` プロパティを持たなければならない

#### 限月実装 (CM)

- **FR-CM-001**: `ContractMonth` クラスを実装し、year と month を属性として持たなければならない
- **FR-CM-002**: `ContractMonth.parse(text: str) -> ContractMonth` で日本語表記から生成できなければならない
- **FR-CM-003**: `ContractMonth.to_yyyymm() -> str` でYYYYMM形式に変換できなければならない
- **FR-CM-004**: `ContractMonth.to_japanese() -> str` で日本語形式に変換できなければならない
- **FR-CM-005**: `ContractMonth` は比較演算（<, <=, ==, !=, >=, >）をサポートしなければならない
- **FR-CM-006**: `ContractMonth` はハッシュ可能で、dict のキーや set の要素として使用可能でなければならない

#### 営業日実装 (BD)

- **FR-BD-001**: `market.is_business_day(date: date) -> bool` を実装しなければならない
- **FR-BD-002**: `market.next_business_day(date: date) -> date` を実装しなければならない
- **FR-BD-003**: `market.previous_business_day(date: date) -> date` を実装しなければならない
- **FR-BD-004**: `market.get_business_days(start: date, end: date) -> list[date]` を実装しなければならない
- **FR-BD-005**: `market.count_business_days(start: date, end: date) -> int` を実装しなければならない
- **FR-BD-006**: 営業日判定は祝日データおよび祝日取引実施日データを参照しなければならない（祝日取引実施日は営業日として判定）

#### SQ日実装 (SQ)

- **FR-SQ-001**: `market.get_sq_date(year: int, month: int) -> date` を実装しなければならない
- **FR-SQ-002**: `market.is_sq_date(date: date) -> bool` を実装しなければならない
- **FR-SQ-003**: `market.get_sq_dates_for_year(year: int) -> list[date]` を実装しなければならない
- **FR-SQ-004**: SQ日機能を持たない市場では `SQNotSupportedError` を発生させなければならない

#### 取引セッション実装 (TS)

- **FR-TS-001**: `TradingSession` 列挙型（DAY, NIGHT, CLOSED 等）を実装しなければならない
- **FR-TS-002**: `market.get_session(dt: datetime | None = None) -> TradingSession` を実装しなければならない
- **FR-TS-003**: `market.is_trading_hours(dt: datetime | None = None) -> bool` を実装しなければならない
- **FR-TS-004**: 時刻引数が `None` の場合、現在のシステム時刻（市場のタイムゾーンで）を使用しなければならない
- **FR-TS-005**: 明示的にタイムゾーン情報のない datetime が渡された場合は `TimezoneRequiredError` を発生させなければならない
- **FR-TS-006**: UTC やその他のタイムゾーンで渡された時刻は市場のタイムゾーンに変換して判定しなければならない

#### データ管理実装 (DM)

- **FR-DM-001**: データはJPX公式サイトから取得し、キャッシュ機構を通じて提供しなければならない
- **FR-DM-002**: 手動でのデータファイル設定APIは提供しない（キャッシュ機構のみ）
- **FR-DM-003**: キャッシュが存在しない場合、初回アクセス時に自動取得を試みなければならない

#### CLI 実装 (CLI)

- **FR-CLI-001**: Typerを使用したCLIを `marketsched` および短縮形 `mks` コマンドとして提供しなければならない
- **FR-CLI-002**: サブコマンド構造を採用し、以下のコマンドグループを実装しなければならない:
  - `bd`（営業日）: `is`, `next`, `prev`, `list`, `count`
  - `sq`（SQ日）: `get`, `list`, `is`
  - `ss`（セッション）: `get`, `is-trading`
  - `cache`（キャッシュ）: `update`, `clear`, `status`
- **FR-CLI-003**: `--market` / `-m` オプションで市場を指定可能にし、デフォルトは `jpx-index` とする
- **FR-CLI-004**: 出力形式はJSONをデフォルトとし、`--format` / `-f` オプションで `text`, `table` を選択可能にしなければならない
- **FR-CLI-005**: エラー時は適切な終了コード（非ゼロ）とエラーメッセージを返さなければならない
- **FR-CLI-006**: `--help` オプションで各コマンドの使用方法を表示しなければならない
- **FR-CLI-007**: `--version` オプションでバージョン情報を表示しなければならない
- **FR-CLI-008**: `mks sq get` コマンドは年月を以下の形式で受け付けなければならない:
  - 2引数形式: `2026 3`
  - YYYYMM形式: `202603`
  - YYYY-MM形式: `2026-03`

#### データキャッシュ実装 (CACHE)

- **FR-CACHE-001**: JPX公式サイトからデータを取得する機能を実装しなければならない
- **FR-CACHE-002**: 取得したデータをローカルファイルシステムにキャッシュしなければならない
- **FR-CACHE-003**: キャッシュの保存先は `~/.cache/marketsched/` または環境に応じた適切な場所とする
- **FR-CACHE-004**: `marketsched cache update` コマンドでキャッシュを手動更新できなければならない
- **FR-CACHE-005**: `marketsched cache clear` コマンドでキャッシュをクリアできなければならない
- **FR-CACHE-006**: `marketsched cache status` コマンドでキャッシュ状態を確認できなければならない
- **FR-CACHE-007**: オフライン時かつキャッシュなしの場合、`CacheNotAvailableError` を発生させなければならない
- **FR-CACHE-008**: キャッシュデータの有効期限を設定可能にしなければならない（デフォルト: 24時間）
- **FR-CACHE-009**: キャッシュデータはParquet形式で保存しなければならない（高速読み込み、型保持、圧縮効率のため）

#### エラーハンドリング (ERR)

- **FR-ERR-001**: 全てのカスタム例外は `MarketshedError` 基底クラスを継承しなければならない
- **FR-ERR-002**: 例外メッセージは問題の原因と対処方法を含まなければならない
- **FR-ERR-003**: 以下の例外クラスを定義しなければならない:
  - `MarketNotFoundError`: 市場が見つからない
  - `ContractMonthParseError`: 限月の解析に失敗
  - `SQDataNotFoundError`: SQ日データが存在しない（指定年月のデータなし）
  - `SQNotSupportedError`: SQ日機能がサポートされていない市場
  - `TimezoneRequiredError`: タイムゾーン情報が必要
  - `CacheNotAvailableError`: キャッシュが利用不可（オフライン時かつキャッシュなし）
  - `DataFetchError`: JPX公式サイトからのデータ取得に失敗
  - `InvalidDataFormatError`: 取得したデータの形式が不正

---

### Key Entities

- **Market (Protocol/ABC)**: 市場を抽象化するインターフェース。timezone, name, 営業日判定、SQ日取得、セッション判定のメソッドを定義。
- **JPXIndex (Market実装)**: JPX指数先物・オプション市場の具体実装（初期スコープ）。将来的に `JPXEquityOptions`, `JPXBond` 等を追加予定。
- **ContractMonth**: 限月を表す値オブジェクト。year（int）、month（int）を持つ。
- **TradingSession (Enum)**: 取引セッションを表す列挙型。DAY, NIGHT, CLOSED など。
- **MarketshedError**: 全てのカスタム例外の基底クラス。

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: ユーザーは `pip install marketsched` でパッケージをインストールできる
- **SC-002**: ユーザーは1行のインポート文で主要機能にアクセスできる
- **SC-003**: 全ての公開APIに型ヒントが付与され、mypy --strict でエラーが出ない
- **SC-004**: コア仕様（001-marketsched-core）の全てのAcceptance Scenarioがテストでカバーされている
- **SC-005**: テストカバレッジが90%以上である
- **SC-006**: エラー発生時、ユーザーは例外メッセージから問題の原因と対処方法を理解できる
- **SC-007**: ドキュメント（docstring）が全ての公開API に付与されている
- **SC-008**: README.md にクイックスタートガイドが含まれている
- **SC-009**: ユーザーは `marketsched --help` で利用可能なコマンド一覧を確認できる
- **SC-010**: CLIコマンドの出力が `jq` 等のJSONツールでパース可能である
- **SC-011**: 初回実行時、データキャッシュが自動的に作成され、以降の実行で再利用される

---

## Assumptions

- Python 3.10 以上を対象とする（match文、|演算子による型ユニオン等の機能を使用可能）
- 日付・時刻処理には標準ライブラリの `datetime`, `zoneinfo` を使用する
- 初期実装ではJPXデリバティブ市場のみを実装する
- パッケージ名は `marketsched` とする
- PyPI への公開を前提とする
- CLI実装には Typer を使用する
- HTTP通信には httpx を使用する（JPX公式サイトからのデータ取得用）
- キャッシュデータはユーザーのローカルファイルシステムに保存する
- キャッシュデータ形式には Parquet を使用する（pyarrow による読み書き）
- JPX公式サイトのデータ形式が大きく変更されないことを前提とする

---

## Scope Boundaries

### In Scope

- `marketsched` パッケージの実装
- Market Protocol/ABC の定義
- JPXIndex 市場クラスの実装（指数先物・オプション、初期スコープ）
- ContractMonth 値オブジェクトの実装
- TradingSession 列挙型の実装
- 全てのカスタム例外クラスの実装
- **Typer による CLI 実装**（営業日判定、SQ日取得、セッション判定）
- **JPX公式サイトからのデータ取得機能**
- **ローカルキャッシュ機構**
- 型ヒントの完全サポート
- pytest によるユニットテスト
- 基本的なドキュメント（docstring、README）

### Out of Scope

- JPX指数先物・オプション以外の商品カテゴリ実装（株式オプション、債券先物等は将来拡張）
- JPX以外の取引所実装（東証株式、米国市場等）
- GUI やWeb インターフェース
- 非同期（async）API
- データベース連携
- ロギング設定のカスタマイズ
- データの同梱（キャッシュ機構で対応）

---

## JPX公式データソース

キャッシュ機構が参照するJPX公式データソース：

| データ種別 | URL | 用途 |
|-----------|-----|------|
| 取引最終日（SQ日） | https://www.jpx.co.jp/derivatives/rules/last-trading-day/index.html | SQ日の取得・判定 |
| 祝日取引実施日 | https://www.jpx.co.jp/derivatives/rules/holidaytrading/index.html | 祝日でも取引がある日の判定 |
| 立会時間 | https://www.jpx.co.jp/derivatives/rules/trading-hours/index.html | 取引セッションの判定 |

**注**: 祝日データは日本の祝日法に基づき、標準ライブラリまたは計算ロジックで対応する。

---

## API Summary

### Python ライブラリ

```python
import marketsched
from marketsched import Market, ContractMonth, TradingSession
from marketsched.markets import JPXIndex

# 市場の取得
market = marketsched.get_market("jpx-index")
markets = marketsched.get_available_markets()

# 限月
cm = ContractMonth.parse("26年3月限")
cm = ContractMonth(2026, 3)
cm.to_yyyymm()      # "202603"
cm.to_japanese()    # "2026年3月限"

# 営業日
market.is_business_day(date(2026, 2, 6))
market.next_business_day(date(2026, 2, 6))
market.previous_business_day(date(2026, 2, 6))
market.get_business_days(start, end)
market.count_business_days(start, end)

# SQ日
market.get_sq_date(2026, 3)
market.is_sq_date(date(2026, 3, 13))
market.get_sq_dates_for_year(2026)

# 取引セッション
market.get_session()  # 現在時刻で判定
market.get_session(datetime(2026, 2, 6, 10, 0, tzinfo=ZoneInfo("Asia/Tokyo")))  # 指定時刻で判定
market.is_trading_hours()  # 現在時刻で判定
market.is_trading_hours(dt)  # 指定時刻で判定
```

### CLI コマンド（mks / marketsched）

```bash
# 営業日 (bd)
mks bd is 2026-02-06                      # 営業日判定
mks bd is 2026-02-06 -f text              # テキスト形式出力
mks bd is 2026-02-06 -m jpx-index         # 市場指定
mks bd next 2026-02-06                    # 翌営業日
mks bd prev 2026-02-06                    # 前営業日
mks bd list 2026-02-01 2026-02-28         # 期間内営業日リスト
mks bd count 2026-02-01 2026-02-28        # 期間内営業日数

# SQ日 (sq)
mks sq get 2026 3                         # 指定年月のSQ日取得（2引数）
mks sq get 202603                         # 指定年月のSQ日取得（YYYYMM形式）
mks sq get 2026-03                        # 指定年月のSQ日取得（YYYY-MM形式）
mks sq list 2026                          # 年間SQ日リスト
mks sq is 2026-03-13                      # SQ日判定

# セッション (ss)
mks ss get                                # 現在時刻でセッション取得
mks ss get 2026-02-06T10:00:00+09:00      # 指定時刻でセッション取得
mks ss is-trading                         # 現在時刻で取引可能判定
mks ss is-trading 2026-02-06T10:00:00+09:00  # 指定時刻で取引可能判定

# キャッシュ (cache)
mks cache update                          # キャッシュ更新
mks cache clear                           # キャッシュクリア
mks cache status                          # キャッシュ状態表示

# ヘルプ・バージョン
mks --help
mks --version
mks bd --help
```
