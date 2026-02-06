# marketsched ドキュメント

**marketsched** は、金融市場のスケジュール管理を行うPythonライブラリです。
営業日判定・SQ日取得・取引セッション判定を、市場に依存しない統一的なAPIで提供します。

## 主な機能

- **営業日判定** -- 祝日・休業日・祝日取引実施日を考慮した正確な判定
- **SQ日取得・判定** -- JPX公式データに基づく権利行使日の参照
- **取引セッション判定** -- 日中立会・ナイトセッション・取引時間外の判定
- **限月の正規化と変換** -- 日本語表記（「26年3月限」）⇔ YYYYMM形式
- **CLIツール** -- `mks` / `marketsched` コマンドによるターミナル操作

## 対応市場

| 市場ID | 名称 | タイムゾーン |
|--------|------|-------------|
| `jpx-index` | JPX指数先物・オプション | Asia/Tokyo |

## 簡単な使用例

```python
import marketsched
from datetime import date

market = marketsched.get_market("jpx-index")
market.is_business_day(date(2026, 2, 6))  # True
market.get_sq_date(2026, 3)               # date(2026, 3, 13)
```

```{toctree}
:maxdepth: 2
:caption: ガイド

getting-started
architecture
```

```{toctree}
:maxdepth: 2
:caption: APIリファレンス

api/index
api/market
api/business-day
api/sq
api/session
api/contract-month
api/cache
api/exceptions
```

```{toctree}
:maxdepth: 2
:caption: CLIリファレンス

cli/index
cli/bd
cli/sq
cli/ss
cli/cache
```
