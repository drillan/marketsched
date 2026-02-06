# sq -- SQ日

SQ日（特別清算指数算出日）に関する操作を行うサブコマンドです。

## sq get

指定年月のSQ日を取得します。年月の指定には複数の形式が使えます。

```bash
mks sq get <YEAR> <MONTH>   # 2引数形式
mks sq get <YYYYMM>         # YYYYMM形式
mks sq get <YYYY-MM>        # YYYY-MM形式
```

**2引数形式**:

YEAR
: 年

MONTH
: 月

**1引数形式**:

YEAR_MONTH
: 年月（`YYYYMM` または `YYYY-MM` 形式）

**JSON出力例**:

```bash
$ mks sq get 2026 3
```

```json
{
  "year": 2026,
  "month": 3,
  "sq_date": "2026-03-13"
}
```

```bash
# YYYYMM形式でも同じ結果
$ mks sq get 202603

# YYYY-MM形式でも同じ結果
$ mks sq get 2026-03
```

**Text出力例**:

```bash
$ mks -f text sq get 2026 3
year: 2026
month: 3
sq_date: 2026-03-13
```

## sq list

指定年の全SQ日リストを取得します。

```bash
mks sq list <YEAR>
```

YEAR
: 年

**JSON出力例**:

```bash
$ mks sq list 2026
```

```json
{
  "year": 2026,
  "sq_dates": [
    "2026-01-09",
    "2026-02-13",
    "2026-03-13"
  ]
}
```

**Text出力例**:

```bash
$ mks -f text sq list 2026
year: 2026
sq_dates:
  - 2026-01-09
  - 2026-02-13
  - 2026-03-13
```

## sq is

指定日がSQ日かどうかを判定します。

```bash
mks sq is <DATE>
```

DATE
: 判定対象日（`YYYY-MM-DD` 形式）

**JSON出力例**:

```bash
$ mks sq is 2026-03-13
```

```json
{
  "date": "2026-03-13",
  "is_sq_date": true
}
```

**Text出力例**:

```bash
$ mks -f text sq is 2026-03-13
date: 2026-03-13
is_sq_date: Yes

$ mks -f text sq is 2026-03-14
date: 2026-03-14
is_sq_date: No
```
