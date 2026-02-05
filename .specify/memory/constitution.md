<!--
SYNC IMPACT REPORT
==================
Version Change: 0.0.0 → 1.0.0

Modified Principles:
- (初版のため該当なし)

Added Sections:
- Mission
- Core Principles (I〜V)
- Scope Definition
- Compatibility Policy
- Defaults and Extensibility
- Development Workflow (TDD)
- Prohibited Practices
- Quality Standards
- Priority of Principles
- Governance

Removed Sections:
- (初版のため該当なし)

Templates Requiring Updates:
- .specify/templates/plan-template.md ✅ (Constitution Check セクションは動的に評価)
- .specify/templates/spec-template.md ✅ (変更不要)
- .specify/templates/tasks-template.md ✅ (変更不要)

Follow-up TODOs:
- なし
==================
-->

# marketsched Constitution

プロジェクトの基本原則を定義する。すべての設計判断はこの原則に基づいて行う。

## Mission

> 金融市場のスケジュール管理（営業日、取引時間、限月、SQ日等）を、市場に依存しない統一的な方法で行えるようにする

## Core Principles

### I. 一次情報参照 (Authoritative Data First)

公式データが単一の真実の源（Single Source of Truth）である。

- SQ日、休日、祝日取引実施日は計算で導出せず、公式データを参照する
- データは利用者が用意し、システムに設定する
- 公式データと異なる結果を返すことを許容しない

**Rationale**: 金融市場のルールは例外が多く、計算による導出は誤りを招く。
JPXの「第2金曜日」ルールですら、祝日移動等で例外が発生する。

### II. 市場の抽象化 (Market Abstraction)

市場（Market）インターフェースにより、市場固有のルールを差し替え可能にする。

- すべての機能は市場を引数として受け取る
- 市場固有のルール（営業日、立会時間、SQ日等）は市場実装に委譲する
- 新しい市場の追加は、既存コードを変更せずに可能とする

**Rationale**: JPX、東証、CME、NYSE等、市場ごとにルールが異なる。
抽象化により、ユーザーは使い慣れたAPIで異なる市場を扱える。

### III. タイムゾーン明示 (Explicit Timezone)

全ての時刻はタイムゾーンを明示する。

- タイムゾーン情報のない時刻（naive datetime）を受け付けない
- 入力はUTCまたは任意のタイムゾーンを許容し、内部で市場固有のタイムゾーンに変換する
- 出力は市場固有のタイムゾーンで返す

**Rationale**: 金融市場は複数のタイムゾーンにまたがる。
タイムゾーンの曖昧さはバグの温床であり、特にナイトセッションの日付跨ぎで問題となる。

### IV. シンプルさ優先 (Simplicity First)

80% のユースケースに最適化する。

- 複雑な要件は、ユーザーによるオーバーライドで対応
- 過度な抽象化・汎用化を避ける
- 「動くコード」を「美しいコード」より優先する
- YAGNI: 必要になるまで作らない

**Rationale**: シンプルなAPIは学習コストを下げ、採用障壁を低くする。

### V. スタンドアロン動作 (Standalone Operation)

実行時の外部API依存なし。

- データ参照はローカルファイルのみ
- ネットワーク接続なしで全機能が動作する
- データ取得・更新は利用者の責任とする

**Rationale**: 取引システムにおいて、外部依存による障害は致命的。
公式データは年数回の更新で十分であり、リアルタイム取得は不要。

## Scope Definition

### In Scope

| カテゴリ | 内容 |
|---------|------|
| 市場抽象化 | Market インターフェース、市場一覧、市場取得 |
| 営業日機能 | 営業日判定、前後営業日取得、営業日リスト、営業日数カウント |
| SQ日機能 | SQ日取得、SQ日判定、SQ日一覧 |
| 取引セッション | セッション判定、取引可能時間判定、セッション時間取得 |
| 限月機能 | 正規化、形式変換（YYYYMM、日本語表記等） |
| タイムゾーン | 任意TZ→市場TZ変換 |
| 初期対応市場 | JPXデリバティブ（日経225先物/mini/マイクロ/オプション） |

### Out of Scope

| カテゴリ | 理由 |
|---------|------|
| 価格データ取得 | 別ドメイン（marketschema の領域） |
| 発注・約定管理 | 別ドメイン |
| リスク計算 | 別ドメイン |
| データ取得・変換 | 利用者の責任（公式サイトから手動取得） |
| リアルタイム更新 | スタンドアロン原則に反する |

## Compatibility Policy

セマンティックバージョニング（SemVer）を採用する。

### Version Number Semantics

| バージョン | 変更内容 |
|-----------|---------|
| MAJOR (x.0.0) | 破壊的変更（後方互換性なし） |
| MINOR (0.x.0) | 機能追加（後方互換性あり） |
| PATCH (0.0.x) | バグ修正（後方互換性あり） |

### Breaking Change Rules

- 破壊的変更はメジャーバージョンでのみ行う
- 非推奨化（deprecation）から削除まで最低1メジャーバージョンの猶予を設ける
- 破壊的変更は CHANGELOG に明記する

### Backward Compatible Changes

以下はマイナーバージョンで行える：

- 新しいオプショナルパラメータの追加
- 新しい市場の追加
- 新しいセッション種別の追加
- 新しい限月形式のサポート

## Defaults and Extensibility

「合理的なデフォルト」を提供しつつ、ユーザーによるオーバーライドを可能にする。

| 項目 | デフォルト | オーバーライド方法 |
|------|-----------|-------------------|
| タイムゾーン | 市場固有TZ | 入力時に任意TZを指定 |
| 出力形式 | 市場固有TZ | 変換関数で任意TZに変換 |
| データファイル | なし（必須設定） | 市場ごとにパスを設定 |
| 限月2桁年号 | 2000〜2099年 | 4桁年号を使用 |

## Development Workflow

Kent Beck の TDD（テスト駆動開発）サイクルに従う。

```
    ┌─────────────────────────────────────┐
    │                                     │
    ▼                                     │
┌───────┐     ┌───────┐     ┌──────────┐  │
│  Red  │────▶│ Green │────▶│ Refactor │──┘
└───────┘     └───────┘     └──────────┘
```

### Red（レッド）

失敗するテストを先に書く。

- 実装前にテストを書くことで、仕様を明確にする
- テストが失敗することを確認してから次へ進む

### Green（グリーン）

テストを通す最小限のコードを書く。

- 「動くコード」を最優先
- 完璧を目指さない。まず通すことに集中

### Refactor（リファクタ）

テストが通る状態を維持しながら、コードを改善する。

- 重複を排除
- 可読性を向上
- テストが壊れたら即座に修正

### TDD Application Scope

| 対象 | TDD適用 |
|------|---------|
| コアライブラリ | 必須 |
| 市場実装 | 必須 |
| 変換関数 | 必須 |
| データパーサー | 推奨 |

## Prohibited Practices

### タイムゾーン省略の禁止

タイムゾーン情報のない時刻を受け付けてはならない。

```python
# NG: naive datetime
def get_session(market, dt: datetime):
    return market.get_session(dt)  # TZがない

# OK: aware datetime
def get_session(market, dt: datetime):
    if dt.tzinfo is None:
        raise ValueError("Timezone-aware datetime required")
    return market.get_session(dt)
```

**原則:**

- 全ての公開APIでタイムゾーン付き時刻を要求する
- 内部でも naive datetime を使用しない

### SQ日計算の禁止

SQ日を計算で導出してはならない。

```python
# NG: 計算による導出
def get_sq_date(year: int, month: int) -> date:
    # 第2金曜日を計算
    first_day = date(year, month, 1)
    first_friday = ...
    return first_friday + timedelta(days=7)  # 例外を考慮していない

# OK: 公式データ参照
def get_sq_date(market, year: int, month: int) -> date:
    return market.sq_calendar.get(year, month)
```

**原則:**

- SQ日は公式データから読み込む
- 公式データにない年月はエラーとする

### 暗黙的フォールバックの禁止

エラーを握りつぶしてデフォルト値で処理してはならない。

```python
# NG: 暗黙的フォールバック
def get_sq_date(market, year: int, month: int) -> date | None:
    try:
        return market.sq_calendar.get(year, month)
    except KeyError:
        return None  # エラーを隠蔽している

# OK: 明示的なエラー
def get_sq_date(market, year: int, month: int) -> date:
    try:
        return market.sq_calendar.get(year, month)
    except KeyError:
        raise DataNotFoundError(f"SQ date not found for {year}-{month:02d}")
```

**原則:**

- 失敗は明示的に報告する
- None を返す設計の場合は、関数名・型で明示する（例: `get_sq_date_or_none`）

### ハードコードの禁止

マジックナンバーや固定値をコードに埋め込んではならない。

```python
# NG: ハードコード
def is_holiday(dt: date) -> bool:
    return dt.month == 12 and dt.day == 31  # 12/31 がハードコード

# OK: 市場定義で外部化
class JPXDerivativesMarket:
    FIXED_HOLIDAYS = [(12, 31), (1, 2)]

    def is_holiday(self, dt: date) -> bool:
        return (dt.month, dt.day) in self.FIXED_HOLIDAYS
```

**原則:**

- 市場固有のルールは市場定義に集約する
- 設定値は引数または設定で外部化する

## Quality Standards

### Market Implementation

- Market インターフェースを完全に実装する
- 公式データと100%一致する結果を返す
- エッジケース（年末年始、日付跨ぎ等）を網羅的にテストする

### Code

- 各言語のイディオム・規約に従う
- 型ヒント / 型注釈を必須とする
- タイムゾーン処理は標準ライブラリまたは確立されたライブラリを使用

### Error Handling

- ユーザーが問題を理解できるエラーメッセージを返す
- データ未設定時は対処方法を含むエラーメッセージを返す
- 市場がサポートしない機能は明示的なエラーとする

## Priority of Principles

設計判断で迷った場合、以下の優先順位に従う：

1. **正確性** - 公式データと一致すること
2. **明示性** - タイムゾーン、エラー、制約が明示されていること
3. **シンプルさ** - 理解しやすく、使いやすいこと
4. **拡張性** - 新しい市場を追加しやすいこと
5. **パフォーマンス** - 十分に高速であること

## Governance

### Amendment Procedure

1. 変更提案は Issue または PR で提出する
2. 変更理由と影響範囲を明記する
3. レビューを経て承認後、憲法を更新する
4. 更新後は依存ドキュメント（テンプレート等）も同期する

### Versioning Policy

憲法のバージョニングは SemVer に従う：

- **MAJOR**: 原則の削除、非互換な再定義
- **MINOR**: 新しい原則・セクションの追加、大幅な拡張
- **PATCH**: 文言修正、タイポ修正、非意味的な改善

### Compliance Review

- すべての PR/レビューは憲法への準拠を確認する
- 複雑さを追加する場合は正当化が必要
- 原則に違反する場合は、明示的な例外として文書化する

**Version**: 1.0.0 | **Ratified**: 2026-02-05 | **Last Amended**: 2026-02-05
