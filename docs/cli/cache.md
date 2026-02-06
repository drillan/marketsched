# cache -- キャッシュ管理

データキャッシュの状態確認・更新・クリアを行うサブコマンドです。

## cache status

キャッシュの状態を表示します。

```bash
mks cache status
```

**JSON出力例**:

```bash
$ mks cache status
```

```json
{
  "sq_dates": {
    "cache_path": "/home/user/.cache/marketsched/sq_dates.parquet",
    "is_valid": true,
    "fetched_at": "2026-02-05T10:00:00+09:00",
    "expires_at": "2026-02-06T10:00:00+09:00",
    "record_count": 48
  },
  "holiday_trading": {
    "cache_path": "/home/user/.cache/marketsched/holiday_trading.parquet",
    "is_valid": true,
    "fetched_at": "2026-02-05T10:00:00+09:00",
    "expires_at": "2026-02-06T10:00:00+09:00",
    "record_count": 15
  }
}
```

**キャッシュなしの場合**:

```json
{
  "sq_dates": {
    "cache_path": "/home/user/.cache/marketsched/sq_dates.parquet",
    "is_valid": false,
    "fetched_at": null,
    "expires_at": null,
    "record_count": null
  },
  "holiday_trading": {
    "cache_path": "/home/user/.cache/marketsched/holiday_trading.parquet",
    "is_valid": false,
    "fetched_at": null,
    "expires_at": null,
    "record_count": null
  }
}
```

## cache update

JPX公式サイトからデータを取得し、キャッシュを更新します。

```bash
mks cache update
```

**JSON出力例（成功）**:

```bash
$ mks cache update
```

```json
{
  "status": "success",
  "message": "キャッシュを更新しました",
  "sq_dates_record_count": 48,
  "holiday_trading_record_count": 15
}
```

**JSON出力例（エラー）**:

```json
{
  "status": "error",
  "message": "キャッシュの更新に失敗しました: ..."
}
```

終了コード: 1

:::{tip}
オフライン環境で使用する場合は、事前にインターネット接続のある環境で `mks cache update` を実行してください。
:::

## cache clear

キャッシュをクリアします。

```bash
mks cache clear
```

**JSON出力例**:

```bash
$ mks cache clear
```

```json
{
  "status": "success",
  "cleared": true,
  "message": "キャッシュをクリアしました"
}
```

:::{warning}
キャッシュをクリアすると、次回の操作時にデータの再取得が必要になります。
オフライン環境ではキャッシュのクリアにご注意ください。
:::
