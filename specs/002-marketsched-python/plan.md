# Implementation Plan: marketsched Python 実装

**Branch**: `002-marketsched-python` | **Date**: 2026-02-05 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-marketsched-python/spec.md`

## Summary

marketsched コアライブラリ仕様（001-marketsched-core）のPython実装。Market Protocol による市場抽象化、JPX指数先物・オプション市場の具体実装、Typer CLI、JPX公式サイトからのデータ取得とParquetキャッシュ機構を提供する。

## Technical Context

**Language/Version**: Python 3.10+（ZoneInfo、match文、型ユニオン演算子使用）
**Primary Dependencies**: Pydantic v2, Typer, httpx, pyarrow, openpyxl
**Storage**: Parquetファイル（~/.cache/marketsched/）
**Testing**: pytest
**Target Platform**: Linux/macOS/Windows（Python 3.10+環境）
**Project Type**: Single（Python パッケージ）
**Performance Goals**: 全API応答 1秒以内
**Constraints**: オフライン時はキャッシュ必須、タイムゾーンなしdatetime拒否
**Scale/Scope**: 初期は jpx-index のみ、将来的に複数市場追加

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. 一次情報参照 | ✅ Pass | SQ日・祝日取引は JPX公式サイトから取得 |
| II. 市場の抽象化 | ✅ Pass | Market Protocol で抽象化 |
| III. タイムゾーン明示 | ✅ Pass | naive datetime 拒否、astimezone() で変換 |
| IV. シンプルさ優先 | ✅ Pass | 80%ユースケースに最適化、YAGNI遵守 |
| V. スタンドアロン動作 | ✅ Pass | キャッシュ済みデータでオフライン動作 |

**Re-check after Phase 1**: ✅ All gates pass

## Project Structure

### Documentation (this feature)

```text
specs/002-marketsched-python/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   ├── python-api.md    # Python API contract
│   └── cli-api.md       # CLI API contract
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
python/
├── pyproject.toml       # パッケージ設定
├── README.md            # パッケージドキュメント
├── src/
│   └── marketsched/
│       ├── __init__.py           # 公開API
│       ├── py.typed              # 型チェッカーシグナル
│       ├── market.py             # Market Protocol
│       ├── contract_month.py     # ContractMonth 値オブジェクト
│       ├── session.py            # TradingSession 列挙型
│       ├── exceptions.py         # カスタム例外
│       ├── registry.py           # 市場レジストリ
│       ├── jpx/                  # JPX取引所サブモジュール
│       │   ├── __init__.py
│       │   ├── index.py          # JPXIndex 市場実装
│       │   ├── calendar.py       # 営業日・SQ日ロジック
│       │   ├── session.py        # 立会時間定数（JPXIndexSessionTimes）
│       │   └── data/             # データ取得・キャッシュ
│       │       ├── __init__.py
│       │       ├── fetcher.py    # JPX公式サイトからの取得
│       │       └── cache.py      # Parquetキャッシュ
│       ├── cli/                  # CLI モジュール
│       │   ├── __init__.py
│       │   ├── main.py           # エントリポイント
│       │   ├── bd.py             # 営業日コマンド
│       │   ├── sq.py             # SQ日コマンド
│       │   ├── ss.py             # セッションコマンド
│       │   └── cache.py          # キャッシュコマンド
│       └── cache.py              # キャッシュ管理API
└── tests/
    ├── conftest.py
    ├── unit/
    │   ├── test_contract_month.py
    │   ├── test_session.py
    │   └── test_exceptions.py
    ├── integration/
    │   ├── test_jpx_index.py
    │   ├── test_cache.py
    │   └── test_registry.py
    └── cli/
        ├── test_bd.py
        ├── test_sq.py
        ├── test_ss.py
        └── test_cache.py
```

**Structure Decision**: Single project structure。Python パッケージとして `src/marketsched/` にソースを配置し、取引所ごとにサブモジュール（`jpx/`）を分離。

## Complexity Tracking

> **No violations found** - Constitution Check passed without requiring justifications.

## Key Design Decisions

### 1. Pydantic v2 採用

**Decision**: Pydantic v2 を部分的に採用
**Rationale**:
- 関連プロジェクト marketschema との一貫性
- `AwareDatetime` 型によるタイムゾーン強制（Constitution III準拠）
- バリデーションとシリアライゼーションの自動化

**採用対象**: ContractMonth, CacheMetadata, CacheInfo
**不採用**: TradingSession (Enum), Market (Protocol), JPXIndex (実装)

### 2. Protocol vs ABC

**Decision**: Protocol を採用
**Rationale**: 構造的部分型により、継承なしで市場実装が可能。型チェッカーとの親和性が高く、将来の市場追加時に既存コード変更不要。

### 3. データ取得方式

**Decision**: httpx + openpyxl
**Rationale**: SQ日・祝日取引データの両方がExcel形式で提供されている。HTMLスクレイピング不要。httpx は async 対応で将来拡張しやすい。

### 4. キャッシュ形式

**Decision**: Parquet（pyarrow）
**Rationale**: 高速読み込み、型保持、圧縮効率のバランスが良い。メタデータにスクレイピング日時を記録可能。

### 5. CLI フレームワーク

**Decision**: Typer + Rich
**Rationale**: 型ヒントベースのCLI定義、自動ヘルプ生成、Rich統合による美しい出力。

### 6. コマンドエイリアス

**Decision**: pyproject.toml で複数エントリポイント
**Rationale**: 最もシンプルで追加依存なし。OSレベルで両コマンド（marketsched, mks）が利用可能。

## Dependencies

### Production

```toml
dependencies = [
    "pydantic>=2.0.0",
    "typer>=0.9.0",
    "httpx>=0.27.0",
    "pyarrow>=15.0.0",
    "openpyxl>=3.1.0",
]
```

### Development

```toml
[dependency-groups]
dev = [
    "pytest>=8.0.0",
    "mypy>=1.8.0",
    "ruff>=0.2.0",
]
```

## Related Artifacts

- **Parent Spec**: [001-marketsched-core/spec.md](../001-marketsched-core/spec.md)
- **Feature Spec**: [spec.md](./spec.md)
- **Research**: [research.md](./research.md)
- **Data Model**: [data-model.md](./data-model.md)
- **Python API Contract**: [contracts/python-api.md](./contracts/python-api.md)
- **CLI API Contract**: [contracts/cli-api.md](./contracts/cli-api.md)
- **Quickstart**: [quickstart.md](./quickstart.md)
