# marketsched Development Guidelines

## Constitution

プロジェクトの詳細な原則は `.specify/memory/constitution.md` を参照してください。

## Python使用ルール

- システムの`python3`コマンドを直接使用しないこと
- `uv run` を使用:
  ```bash
  uv run python
  uv run pytest
  ```

## Coding Rules

### 禁止事項

1. **タイムゾーン省略禁止**: naive datetime を受け付けない
2. **SQ日計算禁止**: 公式データを参照する
3. **暗黙的フォールバック禁止**: エラーを握りつぶさない
4. **ハードコード禁止**: マジックナンバーには名前を付ける
5. **一時ファイルの配置**: `ai_working/` ディレクトリに配置

### Quality Standards

- 型ヒント / 型注釈は必須
- タイムゾーン処理は標準ライブラリ（zoneinfo）を使用

### Quality Checks

コミット前に以下のチェックがすべて通ることを確認:
```bash
uv run ruff check .
uv run ruff format --check .
uv run mypy src
uv run pytest
```

### 判断の優先順位

1. 正確性 → 2. 明示性 → 3. シンプルさ → 4. 拡張性 → 5. パフォーマンス

## Development Workflow

TDD サイクル（Red → Green → Refactor）に従う。コアライブラリと市場実装は TDD 必須。

## Active Technologies

- Python 3.13+（ZoneInfo、match文、型ユニオン演算子、StrEnum使用） + Pydantic, Typer, httpx, pyarrow, openpyxl (002-marketsched-python)
- Parquetファイル（~/.cache/marketsched/） (002-marketsched-python)

## Recent Changes

- 002-marketsched-python: Added Python 3.13+（ZoneInfo、match文、型ユニオン演算子、StrEnum使用） + Pydantic, Typer, httpx, pyarrow, openpyxl

<!-- MANUAL ADDITIONS START -->
<!-- MANUAL ADDITIONS END -->
