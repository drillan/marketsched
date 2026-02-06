# ContractMonth -- 限月

先物・オプション契約の満期月を表す値オブジェクトです。

## 概要

`ContractMonth` は Pydantic `BaseModel` として実装されており、以下の特性を持ちます：

- **イミュータブル**（`frozen=True`）-- 作成後に変更不可
- **比較可能** -- `<`, `<=`, `>`, `>=`, `==` で比較可能
- **ハッシュ可能** -- `dict` のキーや `set` の要素として使用可能
- **バリデーション付き** -- 不正な値は自動的に拒否

```python
from marketsched import ContractMonth
```

## コンストラクタ

```python
ContractMonth(year: int, month: int)
```

year
: 西暦年（4桁、2000〜2099）

month
: 月（1〜12）

**例外**: `ValidationError` -- `year` または `month` が範囲外の場合

```python
cm = ContractMonth(year=2026, month=3)
print(cm.year)   # 2026
print(cm.month)  # 3
```

## parse() クラスメソッド

```python
ContractMonth.parse(text: str) -> ContractMonth
```

文字列から `ContractMonth` を生成します。複数の形式に対応しています。

text
: 限月を表す文字列

**戻り値**: `ContractMonth` -- パースされた限月オブジェクト

**例外**: `ContractMonthParseError` -- パースに失敗した場合

### 対応形式

| 入力文字列 | 結果 |
|-----------|------|
| `"26年3月限"` | `ContractMonth(year=2026, month=3)` |
| `"2026年3月限"` | `ContractMonth(year=2026, month=3)` |
| `"2026年03月限"` | `ContractMonth(year=2026, month=3)` |
| `"202603"` | `ContractMonth(year=2026, month=3)` |
| `"2026-03"` | `ContractMonth(year=2026, month=3)` |

:::{note}
2桁年号（例: `"26年"`）は2000年代として解釈されます。
:::

```python
# 日本語表記からパース
cm = ContractMonth.parse("26年3月限")
print(cm)  # ContractMonth(year=2026, month=3)

# YYYYMM形式
cm = ContractMonth.parse("202603")

# YYYY-MM形式
cm = ContractMonth.parse("2026-03")
```

## 変換メソッド

### to_yyyymm()

```python
cm.to_yyyymm() -> str
```

YYYYMM形式の文字列に変換します。

```python
cm = ContractMonth(year=2026, month=3)
cm.to_yyyymm()  # "202603"
```

### to_japanese()

```python
cm.to_japanese() -> str
```

日本語形式の文字列に変換します。

```python
cm = ContractMonth(year=2026, month=3)
cm.to_japanese()  # "2026年3月限"
```

## 比較とソート

`ContractMonth` は完全順序付け（total ordering）をサポートしています。
年 → 月の順序で比較されます。

```python
cm1 = ContractMonth(year=2026, month=3)
cm2 = ContractMonth(year=2026, month=6)
cm3 = ContractMonth(year=2027, month=1)

cm1 < cm2   # True
cm2 < cm3   # True
cm1 == cm1  # True

# ソート
sorted([cm3, cm1, cm2])
# [ContractMonth(year=2026, month=3),
#  ContractMonth(year=2026, month=6),
#  ContractMonth(year=2027, month=1)]
```

## dict/set での使用

`frozen=True` のためハッシュ可能で、辞書のキーや集合の要素として使用できます。

```python
prices = {
    ContractMonth(year=2026, month=3): 39500,
    ContractMonth(year=2026, month=6): 39800,
}

active_months = {
    ContractMonth(year=2026, month=3),
    ContractMonth(year=2026, month=6),
}
```

## エラー

パースに失敗すると `ContractMonthParseError` が発生します。

```python
from marketsched import ContractMonthParseError

try:
    cm = ContractMonth.parse("invalid")
except ContractMonthParseError as e:
    print(e)
```
