# marketsched

市場カレンダー・SQ日・立会時間を管理するPythonパッケージ。

## 機能

- 営業日判定（祝日・休業日考慮）
- SQ日取得・判定（JPX公式データ参照）
- 取引セッション判定（日中・夜間・クローズ）
- 限月正規化（例: 「26年3月限」→「202603」）
- CLIツール（`mks` / `marketsched`）

## インストール

```bash
pip install marketsched
# または
uv add marketsched
```

## クイックスタート

### Pythonライブラリとして使用

```python
import marketsched
from marketsched import ContractMonth, TradingSession
from datetime import date, datetime
from zoneinfo import ZoneInfo

# 市場を取得
market = marketsched.get_market("jpx-index")

# 営業日判定
market.is_business_day(date(2026, 2, 6))  # True（金曜日）
market.is_business_day(date(2026, 2, 7))  # False（土曜日）

# 前後の営業日を取得
market.next_business_day(date(2026, 2, 6))      # date(2026, 2, 9)（月曜日）
market.previous_business_day(date(2026, 2, 9))  # date(2026, 2, 6)（金曜日）

# 期間内の営業日を取得
market.get_business_days(date(2026, 2, 1), date(2026, 2, 28))  # リストで返却
market.count_business_days(date(2026, 2, 1), date(2026, 2, 28))  # 営業日数

# SQ日取得
market.get_sq_date(2026, 3)  # date(2026, 3, 13)
market.is_sq_date(date(2026, 3, 13))  # True
market.get_sq_dates_for_year(2026)  # 2026年の全SQ日リスト

# 取引セッション判定（タイムゾーン必須）
jst = ZoneInfo("Asia/Tokyo")
dt = datetime(2026, 2, 6, 10, 0, tzinfo=jst)
market.get_session(dt)  # TradingSession.DAY
market.is_trading_hours(dt)  # True

# 現在時刻で判定（引数省略可）
market.get_session()  # 現在のセッション
market.is_trading_hours()  # 現在取引可能か

# 限月の操作
cm = ContractMonth.parse("26年3月限")  # 2桁年号もOK
cm.year   # 2026
cm.month  # 3
cm.to_yyyymm()    # "202603"
cm.to_japanese()  # "2026年3月限"

# 限月は比較・ソート可能
cm1 = ContractMonth(year=2026, month=3)
cm2 = ContractMonth(year=2026, month=6)
cm1 < cm2  # True
sorted([cm2, cm1])  # [cm1, cm2]
```

### CLIとして使用

```bash
# 営業日判定
mks bd is 2026-02-06                 # JSON形式で出力
mks -f text bd is 2026-02-06         # テキスト形式で出力
mks bd next 2026-02-06               # 翌営業日
mks bd prev 2026-02-06               # 前営業日
mks bd list 2026-02-01 2026-02-28    # 期間内営業日リスト
mks bd count 2026-02-01 2026-02-28   # 期間内営業日数

# SQ日
mks sq get 2026 3                    # 2引数形式
mks sq get 202603                    # YYYYMM形式
mks sq get 2026-03                   # YYYY-MM形式
mks sq list 2026                     # 年間SQ日リスト
mks sq is 2026-03-13                 # SQ日判定

# 取引セッション
mks ss get                           # 現在時刻でセッション判定
mks ss get 2026-02-06T10:00:00+09:00 # 指定時刻でセッション判定
mks ss is-trading                    # 現在時刻で取引可能判定

# キャッシュ管理
mks cache status                     # キャッシュ状態を表示
mks cache update                     # キャッシュを更新
mks cache clear                      # キャッシュをクリア

# ヘルプ
mks --help
mks bd --help
```

## 対応市場

| 市場ID | 名称 | 説明 |
|--------|------|------|
| `jpx-index` | JPX Index Futures & Options | 指数先物・オプション（日経225先物、TOPIX先物等） |

## エラーハンドリング

```python
from marketsched import (
    MarketschedError,       # 全エラーの基底クラス
    MarketNotFoundError,    # 市場が見つからない
    ContractMonthParseError, # 限月解析失敗
    SQDataNotFoundError,    # SQデータなし
    TimezoneRequiredError,  # タイムゾーン必須
    CacheNotAvailableError, # キャッシュ利用不可
)

try:
    market = marketsched.get_market("unknown")
except MarketNotFoundError as e:
    print(f"市場が見つかりません: {e}")

try:
    market.get_session(datetime(2026, 2, 6, 10, 0))  # タイムゾーンなし
except TimezoneRequiredError as e:
    print(f"タイムゾーンが必要です: {e}")
```

## データソース

本パッケージはJPX公式データを使用しています：

- [取引最終日（SQ日）](https://www.jpx.co.jp/derivatives/rules/last-trading-day/index.html)
- [祝日取引実施日](https://www.jpx.co.jp/derivatives/rules/holidaytrading/index.html)
- [立会時間](https://www.jpx.co.jp/derivatives/rules/trading-hours/index.html)

初回使用時に自動的にキャッシュが作成されます。オフライン環境では `mks cache update` でデータを事前取得してください。

## 開発

```bash
# 開発環境セットアップ
uv sync

# テスト実行
uv run pytest

# 型チェック
uv run mypy src --strict

# リンター
uv run ruff check .
uv run ruff format .
```

## 詳細ドキュメント

APIリファレンス・CLIリファレンス・アーキテクチャガイドは [docs/](../docs/) を参照してください。

```bash
# ドキュメントのビルド
cd docs && make html
```

## ライセンス

MIT License
