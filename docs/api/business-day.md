# 営業日

営業日に関するメソッド群です。全て `Market` オブジェクトのメソッドとして呼び出します。

## 営業日の判定ルール

- **土日**は休場
- **JPX公式休業日**に含まれる日は休場
- ただし**祝日取引実施日**（祝日であっても取引が行われる日）は**営業日として判定**

:::{note}
営業日判定にはキャッシュされた公式データが必要です。
キャッシュが未取得の場合、初回アクセス時に自動的にデータが取得されます。
:::

## is_business_day()

```python
market.is_business_day(d: date) -> bool
```

指定日が営業日かどうかを判定します。

d
: 判定対象の日付

**戻り値**: `bool` -- 営業日の場合 `True`

```python
from datetime import date

market = marketsched.get_market("jpx-index")

market.is_business_day(date(2026, 2, 6))   # True（金曜日）
market.is_business_day(date(2026, 2, 7))   # False（土曜日）
market.is_business_day(date(2026, 2, 11))  # False（建国記念の日）
market.is_business_day(date(2026, 1, 12))  # True（成人の日 = 祝日取引実施日）
```

## next_business_day()

```python
market.next_business_day(d: date) -> date
```

指定日の翌営業日を取得します。
指定日自体が営業日かどうかに関わらず、翌日以降で最初の営業日を返します。

d
: 基準日

**戻り値**: `date` -- 翌営業日

```python
# 金曜日 → 月曜日（土日をスキップ）
market.next_business_day(date(2026, 2, 6))   # date(2026, 2, 9)

# 火曜日 → 木曜日（祝日をスキップ）
market.next_business_day(date(2026, 2, 10))  # date(2026, 2, 12)
# （2/11 は建国記念の日のためスキップ）
```

## previous_business_day()

```python
market.previous_business_day(d: date) -> date
```

指定日の前営業日を取得します。
指定日自体が営業日かどうかに関わらず、前日以前で最後の営業日を返します。

d
: 基準日

**戻り値**: `date` -- 前営業日

```python
# 月曜日 → 金曜日（土日をスキップ）
market.previous_business_day(date(2026, 2, 9))  # date(2026, 2, 6)
```

## get_business_days()

```python
market.get_business_days(start: date, end: date) -> list[date]
```

期間内の営業日リストを取得します。

start
: 開始日（含む）

end
: 終了日（含む）

**戻り値**: `list[date]` -- 営業日のリスト（昇順）

```python
days = market.get_business_days(date(2026, 2, 1), date(2026, 2, 10))
# [date(2026, 2, 2), date(2026, 2, 3), date(2026, 2, 4),
#  date(2026, 2, 5), date(2026, 2, 6), date(2026, 2, 9), date(2026, 2, 10)]
```

## count_business_days()

```python
market.count_business_days(start: date, end: date) -> int
```

期間内の営業日数をカウントします。

start
: 開始日（含む）

end
: 終了日（含む）

**戻り値**: `int` -- 営業日数

```python
count = market.count_business_days(date(2026, 2, 1), date(2026, 2, 28))
print(count)  # 19
```
