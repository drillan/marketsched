# キャッシュ管理

marketsched は JPX 公式サイトからデータを取得し、Parquet 形式でローカルにキャッシュします。

## キャッシュの仕組み

- **保存先**: `~/.cache/marketsched/`
- **形式**: Apache Parquet（PyArrow使用）
- **有効期限**: 24時間（デフォルト）
- **自動取得**: 初回アクセス時にデータが自動的に取得されます

## update_cache()

```python
marketsched.update_cache(
    force: bool = False,
    years: list[int] | None = None,
) -> dict[str, CacheInfo]
```

JPX公式サイトからデータを取得してキャッシュを更新します。

force
: `True` の場合、有効期限内のキャッシュも強制更新

years
: SQ日データの取得対象年リスト。`None` の場合はデフォルト年

**戻り値**: `dict[str, CacheInfo]` -- データ種別をキーとするキャッシュ情報

**例外**: `DataFetchError` -- データ取得に失敗した場合

```python
import marketsched

# 通常の更新（期限切れのみ更新）
status = marketsched.update_cache()

# 強制更新
status = marketsched.update_cache(force=True)

# 特定年のSQ日データを取得
status = marketsched.update_cache(years=[2025, 2026, 2027])
```

## clear_cache()

```python
marketsched.clear_cache(
    data_type: DataType | str | None = None,
) -> None
```

キャッシュをクリアします。

data_type
: クリア対象のデータ種別。`None` の場合は全データをクリア。

```python
import marketsched
from marketsched import DataType

# 全キャッシュをクリア
marketsched.clear_cache()

# SQ日データのみクリア
marketsched.clear_cache(DataType.SQ_DATES)

# 文字列でも指定可能
marketsched.clear_cache("sq_dates")
```

## get_cache_status()

```python
marketsched.get_cache_status() -> dict[str, CacheInfo]
```

キャッシュの状態を取得します。

**戻り値**: `dict[str, CacheInfo]` -- データ種別をキーとするキャッシュ情報

```python
import marketsched

status = marketsched.get_cache_status()
for data_type, info in status.items():
    print(f"{data_type}: valid={info.is_valid}, records={info.record_count}")
```

## DataType 列挙型

```python
from marketsched import DataType
```

キャッシュされるデータの種別を表します。

| 値 | 文字列値 | 説明 |
|----|---------|------|
| `DataType.SQ_DATES` | `"sq_dates"` | SQ日（権利行使日）データ |
| `DataType.HOLIDAY_TRADING` | `"holiday_trading"` | 祝日取引実施日データ |

## CacheInfo モデル

キャッシュの状態情報を保持するモデルです。

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `data_type` | `DataType` | データ種別 |
| `cache_path` | `str` | キャッシュファイルのパス |
| `is_valid` | `bool` | キャッシュが有効期限内かどうか |
| `fetched_at` | `datetime \| None` | 最終取得日時（キャッシュなしの場合 `None`） |
| `expires_at` | `datetime \| None` | 有効期限（キャッシュなしの場合 `None`） |
| `record_count` | `int \| None` | レコード数（キャッシュなしの場合 `None`） |

## データソース

| データ種別 | ソース |
|-----------|--------|
| SQ日 | [取引最終日・権利行使日等](https://www.jpx.co.jp/derivatives/rules/last-trading-day/index.html) |
| 祝日取引実施日 | [祝日取引](https://www.jpx.co.jp/derivatives/rules/holidaytrading/index.html) |

## オフライン環境での使用

オフライン環境では、事前にインターネット接続のある環境でキャッシュを取得してください。

```bash
# インターネット接続のある環境で実行
mks cache update
```

キャッシュファイル（`~/.cache/marketsched/` 配下の `.parquet` ファイル）をオフライン環境にコピーすることで使用できます。
