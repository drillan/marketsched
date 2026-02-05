# Quickstart Guide: marketsched Python

## Installation

```bash
pip install marketsched
```

または uv を使用する場合：

```bash
uv pip install marketsched
```

## Python ライブラリとして使用

### 基本的な使い方

```python
import marketsched
from datetime import date, datetime
from zoneinfo import ZoneInfo

# 市場を取得
market = marketsched.get_market("jpx-index")

# 営業日判定
print(market.is_business_day(date(2026, 2, 6)))  # True

# 翌営業日を取得
print(market.next_business_day(date(2026, 2, 6)))  # 2026-02-09

# SQ日を取得
print(market.get_sq_date(2026, 3))  # 2026年3月のSQ日

# セッション判定（タイムゾーン必須）
jst = ZoneInfo("Asia/Tokyo")
dt = datetime(2026, 2, 6, 10, 0, tzinfo=jst)
print(market.get_session(dt))  # TradingSession.DAY

# 現在時刻でのセッション判定
print(market.get_session())  # 現在のセッション
```

### 限月の扱い

```python
from marketsched import ContractMonth

# 日本語表記からパース
cm = ContractMonth.parse("26年3月限")

# 直接生成
cm = ContractMonth(2026, 3)

# 変換
print(cm.to_yyyymm())    # "202603"
print(cm.to_japanese())  # "2026年3月限"

# 比較
print(cm < ContractMonth(2026, 6))  # True
```

## CLI として使用

### 営業日判定

```bash
# 営業日かどうか判定
mks bd is 2026-02-06

# 翌営業日を取得
mks bd next 2026-02-06

# 前営業日を取得
mks bd prev 2026-02-09

# 期間内の営業日リスト
mks bd list 2026-02-01 2026-02-28

# 期間内の営業日数
mks bd count 2026-02-01 2026-02-28
```

### SQ日

```bash
# SQ日を取得（複数形式対応）
mks sq get 2026 3       # 2引数形式
mks sq get 202603       # YYYYMM形式
mks sq get 2026-03      # YYYY-MM形式

# 年間SQ日リスト
mks sq list 2026

# SQ日判定
mks sq is 2026-03-13
```

### セッション判定

```bash
# 現在時刻でのセッション
mks ss get

# 指定時刻でのセッション（タイムゾーン必須）
mks ss get 2026-02-06T10:00:00+09:00

# 取引可能判定
mks ss is-trading
mks ss is-trading 2026-02-06T10:00:00+09:00
```

### キャッシュ管理

```bash
# キャッシュを更新
mks cache update

# キャッシュをクリア
mks cache clear

# キャッシュ状態を確認
mks cache status
```

### 出力形式の変更

```bash
# JSON（デフォルト）
mks bd is 2026-02-06

# テキスト
mks bd is 2026-02-06 --format text

# テーブル
mks bd list 2026-02-01 2026-02-28 --format table
```

## 対応市場

| 市場ID | 市場名 |
|--------|--------|
| `jpx-index` | JPX指数先物・オプション |

## 次のステップ

- [Python API リファレンス](contracts/python-api.md)
- [CLI リファレンス](contracts/cli-api.md)
- [データモデル](data-model.md)
