# はじめに

## インストール

```bash
pip install marketsched
```

または [uv](https://docs.astral.sh/uv/) を使用する場合：

```bash
uv add marketsched
```

## 動作要件

- Python 3.13 以上
- インターネット接続（初回キャッシュ取得時のみ）

## Pythonライブラリとして使用

### 市場オブジェクトの取得

```python
import marketsched

# 市場を取得
market = marketsched.get_market("jpx-index")

# 利用可能な市場一覧
marketsched.get_available_markets()  # ['jpx-index']
```

### 営業日判定

```python
from datetime import date

market = marketsched.get_market("jpx-index")

# 営業日かどうか判定
market.is_business_day(date(2026, 2, 6))  # True（金曜日）
market.is_business_day(date(2026, 2, 7))  # False（土曜日）

# 前後の営業日を取得
market.next_business_day(date(2026, 2, 6))      # date(2026, 2, 9)（月曜日）
market.previous_business_day(date(2026, 2, 9))  # date(2026, 2, 6)（金曜日）

# 期間内の営業日を取得
market.get_business_days(date(2026, 2, 1), date(2026, 2, 28))  # リストで返却
market.count_business_days(date(2026, 2, 1), date(2026, 2, 28))  # 営業日数
```

### SQ日の取得

```python
# SQ日を取得
market.get_sq_date(2026, 3)  # date(2026, 3, 13)

# SQ日かどうか判定
market.is_sq_date(date(2026, 3, 13))  # True

# 年間のSQ日リスト
market.get_sq_dates_for_year(2026)  # [date(2026, 1, 9), ...]
```

### 取引セッション判定

```python
from datetime import datetime
from zoneinfo import ZoneInfo

jst = ZoneInfo("Asia/Tokyo")

# タイムゾーン付きdatetimeが必須
dt = datetime(2026, 2, 6, 10, 0, tzinfo=jst)
market.get_session(dt)       # TradingSession.DAY
market.is_trading_hours(dt)  # True

# 引数を省略すると現在時刻で判定
market.get_session()       # 現在のセッション
market.is_trading_hours()  # 現在取引可能か
```

:::{important}
`get_session()` と `is_trading_hours()` に渡す `datetime` は**タイムゾーン付き**である必要があります。
タイムゾーンなしの `datetime` を渡すと `TimezoneRequiredError` が発生します。
:::

### 限月の操作

```python
from marketsched import ContractMonth

# 日本語表記からパース
cm = ContractMonth.parse("26年3月限")

# 直接生成
cm = ContractMonth(year=2026, month=3)

# 変換
cm.to_yyyymm()    # "202603"
cm.to_japanese()  # "2026年3月限"

# 比較・ソート可能
cm1 = ContractMonth(year=2026, month=3)
cm2 = ContractMonth(year=2026, month=6)
cm1 < cm2  # True
sorted([cm2, cm1])  # [cm1, cm2]
```

## CLIとして使用

`marketsched`（短縮形: `mks`）コマンドが利用できます。

### 営業日コマンド

```bash
mks bd is 2026-02-06                 # 営業日判定
mks bd next 2026-02-06               # 翌営業日
mks bd prev 2026-02-06               # 前営業日
mks bd list 2026-02-01 2026-02-28    # 期間内営業日リスト
mks bd count 2026-02-01 2026-02-28   # 期間内営業日数
```

### SQ日コマンド

```bash
mks sq get 2026 3                    # 2引数形式
mks sq get 202603                    # YYYYMM形式
mks sq get 2026-03                   # YYYY-MM形式
mks sq list 2026                     # 年間SQ日リスト
mks sq is 2026-03-13                 # SQ日判定
```

### セッションコマンド

```bash
mks ss get                           # 現在時刻でセッション判定
mks ss get 2026-02-06T10:00:00+09:00 # 指定時刻でセッション判定
mks ss is-trading                    # 現在時刻で取引可能判定
```

### キャッシュ管理

```bash
mks cache status                     # キャッシュ状態を表示
mks cache update                     # キャッシュを更新
mks cache clear                      # キャッシュをクリア
```

### 出力形式の変更

```bash
# JSON（デフォルト）
mks bd is 2026-02-06

# テキスト（--format はサブコマンドの前に指定）
mks --format text bd is 2026-02-06
mks -f text bd is 2026-02-06

# テーブル
mks --format table bd list 2026-02-01 2026-02-28
```

## データソース

本パッケージはJPX公式データを使用しています：

- [取引最終日（SQ日）](https://www.jpx.co.jp/derivatives/rules/last-trading-day/index.html)
- [祝日取引実施日](https://www.jpx.co.jp/derivatives/rules/holidaytrading/index.html)
- [立会時間](https://www.jpx.co.jp/derivatives/rules/trading-hours/index.html)

初回使用時に自動的にキャッシュが作成されます。オフライン環境では事前に `mks cache update` でデータを取得してください。

## 次のステップ

- {doc}`api/index` -- Python APIの詳細なリファレンス
- {doc}`cli/index` -- CLIコマンドの完全なリファレンス
- {doc}`architecture` -- 設計原則とアーキテクチャの解説
