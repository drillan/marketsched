# CLI リファレンス

marketsched は `marketsched` コマンド（短縮形: `mks`）としてターミナルから利用できます。

## 基本構文

```bash
mks [グローバルオプション] <サブコマンド> <アクション> [引数]
```

## グローバルオプション

グローバルオプションは**サブコマンドの前に**指定します。

| オプション | 短縮形 | 型 | デフォルト | 説明 |
|-----------|--------|-----|-----------|------|
| `--market` | `-m` | string | `jpx-index` | 対象市場 |
| `--format` | `-f` | string | `json` | 出力形式 |
| `--help` | | | | ヘルプを表示 |
| `--version` | | | | バージョンを表示 |

```bash
# 正しい指定順序
mks --format text bd is 2026-02-06
mks -m jpx-index -f json sq get 2026 3

# ヘルプ表示
mks --help
mks bd --help
```

## 出力形式

`--format` / `-f` オプションで出力形式を選択できます。

### JSON（デフォルト）

```bash
$ mks bd is 2026-02-06
```

```json
{
  "date": "2026-02-06",
  "is_business_day": true,
  "market": "jpx-index"
}
```

### Text

```bash
$ mks -f text bd is 2026-02-06
```

```
2026-02-06 は営業日です
```

### Table

リスト系コマンドで有効です。

```bash
$ mks -f table bd list 2026-02-01 2026-02-10
```

## サブコマンド一覧

| コマンド | 説明 | 詳細 |
|---------|------|------|
| `bd` | 営業日操作 | {doc}`bd` |
| `sq` | SQ日操作 | {doc}`sq` |
| `ss` | セッション判定 | {doc}`ss` |
| `cache` | キャッシュ管理 | {doc}`cache` |

## 終了コード

| コード | 説明 |
|--------|------|
| 0 | 成功 |
| 1 | エラー（入力不正、データ未存在等） |
| 2 | 不正なコマンドまたは引数 |

## エラー出力

エラー発生時、JSON形式の場合は以下の形式で出力されます：

```json
{
  "error": "ErrorClassName",
  "message": "エラーの詳細メッセージ"
}
```
