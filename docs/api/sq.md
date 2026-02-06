# SQ日

SQ（Special Quotation = 特別清算指数）に関するメソッド群です。

:::{important}
SQ日は**計算ではなくJPX公式データから参照**されます。
「第2金曜日」のような計算ルールは使用していません。
これはプロジェクトの設計原則に基づくものです。
:::

## get_sq_date()

```python
market.get_sq_date(year: int, month: int) -> date
```

指定年月のSQ日（権利行使日）を取得します。

year
: 年

month
: 月

**戻り値**: `date` -- SQ日

**例外**:
- `SQDataNotFoundError` -- 指定年月のデータが存在しない場合
- `SQNotSupportedError` -- この市場がSQ日機能をサポートしていない場合

```python
market = marketsched.get_market("jpx-index")

sq = market.get_sq_date(2026, 3)
print(sq)  # 2026-03-13
```

## is_sq_date()

```python
market.is_sq_date(d: date) -> bool
```

指定日がSQ日かどうかを判定します。

d
: 判定対象の日付

**戻り値**: `bool` -- SQ日の場合 `True`

**例外**: `SQNotSupportedError` -- この市場がSQ日機能をサポートしていない場合

```python
market.is_sq_date(date(2026, 3, 13))  # True
market.is_sq_date(date(2026, 3, 14))  # False
```

## get_sq_dates_for_year()

```python
market.get_sq_dates_for_year(year: int) -> list[date]
```

指定年の全SQ日リストを取得します。

year
: 年

**戻り値**: `list[date]` -- SQ日のリスト（昇順）

**例外**:
- `SQDataNotFoundError` -- 指定年のデータが存在しない場合
- `SQNotSupportedError` -- この市場がSQ日機能をサポートしていない場合

```python
sq_dates = market.get_sq_dates_for_year(2026)
for d in sq_dates:
    print(d)
# 2026-01-09
# 2026-02-13
# 2026-03-13
# ...
```

## データソース

SQ日データはJPX公式サイトの以下のページから取得されます：

- [取引最終日・権利行使日等](https://www.jpx.co.jp/derivatives/rules/last-trading-day/index.html)

データは Parquet 形式でローカルキャッシュ（`~/.cache/marketsched/`）に保存されます。
キャッシュの管理については {doc}`cache` を参照してください。
