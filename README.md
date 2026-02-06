# marketsched

金融市場のスケジュール管理ライブラリ -- 営業日・SQ日・取引セッションを統一的に扱います。

## プロジェクト構成

| ディレクトリ | 内容 |
|-------------|------|
| `python/` | Pythonパッケージ（marketsched） |
| `docs/` | ドキュメント（Sphinx） |
| `specs/` | 設計仕様書 |

## クイックスタート

### インストール

```bash
# 開発版（PyPI 未公開）
git clone https://github.com/drillan/marketsched.git
cd marketsched && uv pip install -e ./python
```

### 使い方

```python
import marketsched
from datetime import date

market = marketsched.get_market("jpx-index")

market.is_business_day(date(2026, 2, 6))  # True
market.next_business_day(date(2026, 2, 6))  # date(2026, 2, 9)
market.get_sq_date(2026, 3)  # date(2026, 3, 13)
```

```bash
mks bd is 2026-02-06
mks sq get 2026 3
mks ss get
```

## ドキュメント

- **パッケージ詳細**: [python/README.md](python/README.md)
- **ドキュメントサイト**: ビルド方法 → `cd docs && make html`

## ライセンス

MIT License
