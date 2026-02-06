# bd -- 営業日

営業日に関する操作を行うサブコマンドです。

## bd is

指定日が営業日かどうかを判定します。

```bash
mks bd is <DATE>
```

DATE
: 判定対象日（`YYYY-MM-DD` 形式）

**JSON出力例**:

```bash
$ mks bd is 2026-02-06
```

```json
{
  "date": "2026-02-06",
  "is_business_day": true
}
```

**Text出力例**:

```bash
$ mks -f text bd is 2026-02-06
date: 2026-02-06
is_business_day: Yes

$ mks -f text bd is 2026-02-07
date: 2026-02-07
is_business_day: No
```

## bd next

指定日の翌営業日を取得します。

```bash
mks bd next <DATE>
```

DATE
: 基準日（`YYYY-MM-DD` 形式）

**JSON出力例**:

```bash
$ mks bd next 2026-02-06
```

```json
{
  "date": "2026-02-06",
  "next_business_day": "2026-02-09"
}
```

**Text出力例**:

```bash
$ mks -f text bd next 2026-02-06
date: 2026-02-06
next_business_day: 2026-02-09
```

## bd prev

指定日の前営業日を取得します。

```bash
mks bd prev <DATE>
```

DATE
: 基準日（`YYYY-MM-DD` 形式）

**JSON出力例**:

```bash
$ mks bd prev 2026-02-09
```

```json
{
  "date": "2026-02-09",
  "previous_business_day": "2026-02-06"
}
```

**Text出力例**:

```bash
$ mks -f text bd prev 2026-02-09
date: 2026-02-09
previous_business_day: 2026-02-06
```

## bd list

期間内の営業日リストを取得します。

```bash
mks bd list <START> <END>
```

START
: 開始日（`YYYY-MM-DD` 形式、含む）

END
: 終了日（`YYYY-MM-DD` 形式、含む）

**JSON出力例**:

```bash
$ mks bd list 2026-02-01 2026-02-10
```

```json
{
  "start_date": "2026-02-01",
  "end_date": "2026-02-10",
  "business_days": [
    "2026-02-02",
    "2026-02-03",
    "2026-02-04",
    "2026-02-05",
    "2026-02-06",
    "2026-02-09",
    "2026-02-10"
  ],
  "count": 7
}
```

**Text出力例**:

```bash
$ mks -f text bd list 2026-02-01 2026-02-10
start_date: 2026-02-01
end_date: 2026-02-10
business_days:
  - 2026-02-02
  - 2026-02-03
  - 2026-02-04
  - 2026-02-05
  - 2026-02-06
  - 2026-02-09
  - 2026-02-10
count: 7
```

## bd count

期間内の営業日数をカウントします。

```bash
mks bd count <START> <END>
```

START
: 開始日（`YYYY-MM-DD` 形式、含む）

END
: 終了日（`YYYY-MM-DD` 形式、含む）

**JSON出力例**:

```bash
$ mks bd count 2026-02-01 2026-02-28
```

```json
{
  "start_date": "2026-02-01",
  "end_date": "2026-02-28",
  "count": 19
}
```

**Text出力例**:

```bash
$ mks -f text bd count 2026-02-01 2026-02-28
start_date: 2026-02-01
end_date: 2026-02-28
count: 19
```
