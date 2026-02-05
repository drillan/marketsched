# marketsched

市場カレンダー・SQ日・立会時間を管理するパッケージ。

## 機能

- 営業日判定
- SQ日算出
- 立会時間管理
- 限月正規化（例: 「26年3月限」→「202603」）

## インストール

```bash
uv add marketsched
```

## 使用例

```python
from marketsched import get_market
from datetime import date

# 市場を取得
market = get_market("jpx-index")

# 営業日判定
market.is_business_day(date(2026, 2, 6))  # True

# SQ日取得
market.get_sq_date(2026, 3)  # date(2026, 3, 13)
```

> 詳細な使用例は実装完了後に更新予定です。
