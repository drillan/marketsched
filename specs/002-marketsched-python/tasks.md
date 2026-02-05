# Tasks: marketsched Python 実装

**Input**: Design documents from `/specs/002-marketsched-python/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: TDD必須（CLAUDE.md規定）。テストを先に書き、失敗を確認してから実装する。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

```text
python/
├── pyproject.toml
├── src/marketsched/
└── tests/
```

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create project structure per plan.md (python/, src/marketsched/, tests/)
- [ ] T002 Initialize Python project with pyproject.toml (Python 3.10+, pydantic, typer, httpx, pyarrow, openpyxl)
- [ ] T003 [P] Configure ruff and mypy in pyproject.toml
- [ ] T004 [P] Create py.typed marker in python/src/marketsched/py.typed
- [ ] T005 [P] Create conftest.py with shared fixtures in python/tests/conftest.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Tests for Foundational Phase

- [ ] T006 [P] Unit test for TradingSession enum in python/tests/unit/test_session.py
- [ ] T007 [P] Unit test for all exception classes in python/tests/unit/test_exceptions.py

### Implementation for Foundational Phase

- [ ] T008 [P] Implement TradingSession enum (DAY, NIGHT, CLOSED) in python/src/marketsched/session.py
- [ ] T009 [P] Implement all exception classes in python/src/marketsched/exceptions.py
- [ ] T010 Define Market Protocol in python/src/marketsched/market.py
- [ ] T011 Implement market registry with @register decorator in python/src/marketsched/registry.py
- [ ] T012 Create package __init__.py with public API exports in python/src/marketsched/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 2 - 限月オブジェクトの生成と変換 (Priority: P1)

**Goal**: ContractMonth値オブジェクトで限月を表現し、各種形式に変換できる

**Independent Test**: ContractMonthの生成・変換・比較がPythonインタープリタで完結

### Tests for User Story 2

- [ ] T013 [P] [US2] Unit test for ContractMonth creation and validation in python/tests/unit/test_contract_month.py
- [ ] T014 [P] [US2] Unit test for ContractMonth.parse() with Japanese formats in python/tests/unit/test_contract_month.py
- [ ] T015 [P] [US2] Unit test for ContractMonth conversion methods (to_yyyymm, to_japanese) in python/tests/unit/test_contract_month.py
- [ ] T016 [P] [US2] Unit test for ContractMonth comparison and hashing in python/tests/unit/test_contract_month.py

### Implementation for User Story 2

- [ ] T017 [US2] Implement ContractMonth Pydantic model with validation in python/src/marketsched/contract_month.py
- [ ] T018 [US2] Implement ContractMonth.parse() for Japanese formats in python/src/marketsched/contract_month.py
- [ ] T019 [US2] Implement ContractMonth.to_yyyymm() and to_japanese() in python/src/marketsched/contract_month.py
- [ ] T020 [US2] Implement comparison operators (__lt__, __le__, __gt__, __ge__) in python/src/marketsched/contract_month.py
- [ ] T021 [US2] Export ContractMonth from package __init__.py

**Checkpoint**: ContractMonth is fully functional and independently testable

---

## Phase 4: User Story 11 - データキャッシュの管理 (Priority: P1)

**Goal**: JPX公式サイトからデータを取得しParquetキャッシュに保存できる

**Independent Test**: `mks cache update/status/clear` でキャッシュ操作が完結

**Note**: User Story 4, 6 が依存するため、先に実装

### Tests for User Story 11

- [ ] T022 [P] [US11] Unit test for Parquet cache read/write in python/tests/unit/test_cache.py
- [ ] T023 [P] [US11] Unit test for CacheMetadata and CacheInfo models in python/tests/unit/test_cache.py
- [ ] T024 [P] [US11] Integration test for JPX data fetcher (mock HTTP) in python/tests/integration/test_jpx_fetcher.py
- [ ] T024a [P] [US11] Unit test for auto-fetch on first access (FR-DM-003) in python/tests/integration/test_cache.py
- [ ] T024b [P] [US11] Unit test for InvalidDataFormatError on schema mismatch in python/tests/unit/test_cache.py

### Implementation for User Story 11

- [ ] T025 [US11] Implement CacheMetadata and CacheInfo Pydantic models in python/src/marketsched/jpx/data/__init__.py
- [ ] T026 [US11] Implement Parquet cache manager in python/src/marketsched/jpx/data/cache.py
- [ ] T027 [US11] Implement JPX SQ date fetcher (httpx + openpyxl) with schema validation in python/src/marketsched/jpx/data/fetcher.py (raise InvalidDataFormatError on schema mismatch)
- [ ] T028 [US11] Implement JPX holiday trading fetcher with schema validation in python/src/marketsched/jpx/data/fetcher.py (raise InvalidDataFormatError on schema mismatch)
- [ ] T029 [US11] Implement cache API (update_cache, clear_cache, get_cache_status) in python/src/marketsched/cache.py
- [ ] T030 [US11] Export cache functions from package __init__.py

**Checkpoint**: Cache infrastructure is ready for market implementations

---

## Phase 5: User Story 3 - 市場オブジェクトの取得と情報参照 (Priority: P1)

**Goal**: get_market() で市場を取得し、基本情報を参照できる

**Independent Test**: 市場の取得と情報参照がPythonインタープリタで完結

### Tests for User Story 3

- [ ] T031 [P] [US3] Unit test for JPXIndex properties (market_id, name, timezone) in python/tests/unit/test_jpx_index.py
- [ ] T032 [P] [US3] Integration test for market registry in python/tests/integration/test_registry.py

### Implementation for User Story 3

- [ ] T033 [US3] Create jpx submodule structure in python/src/marketsched/jpx/__init__.py
- [ ] T034 [US3] Implement JPXIndexSessionTimes constants in python/src/marketsched/jpx/session.py
- [ ] T035 [US3] Implement JPXIndex class skeleton (properties only) in python/src/marketsched/jpx/index.py
- [ ] T036 [US3] Register JPXIndex with @MarketRegistry.register("jpx-index") decorator
- [ ] T037 [US3] Implement get_market() and get_available_markets() in python/src/marketsched/__init__.py

**Checkpoint**: Market retrieval is functional

---

## Phase 6: User Story 4 - 営業日判定の実行 (Priority: P1)

**Goal**: 指定日の営業日判定、前後営業日取得ができる

**Independent Test**: 営業日判定がPythonインタープリタで完結

**Depends on**: US11 (cache), US3 (market)

### Tests for User Story 4

- [ ] T038 [P] [US4] Unit test for is_business_day with weekends in python/tests/integration/test_jpx_index.py
- [ ] T039 [P] [US4] Unit test for is_business_day with year-end holidays in python/tests/integration/test_jpx_index.py
- [ ] T040 [P] [US4] Unit test for is_business_day with holiday trading days in python/tests/integration/test_jpx_index.py
- [ ] T041 [P] [US4] Unit test for next_business_day and previous_business_day in python/tests/integration/test_jpx_index.py

### Implementation for User Story 4

- [ ] T042 [US4] Implement JPX calendar logic (weekend, year-end) in python/src/marketsched/jpx/calendar.py
- [ ] T043 [US4] Implement holiday trading check using cache data in python/src/marketsched/jpx/calendar.py
- [ ] T044 [US4] Implement JPXIndex.is_business_day() in python/src/marketsched/jpx/index.py
- [ ] T045 [US4] Implement JPXIndex.next_business_day() in python/src/marketsched/jpx/index.py
- [ ] T046 [US4] Implement JPXIndex.previous_business_day() in python/src/marketsched/jpx/index.py

**Checkpoint**: Business day functions are independently testable

---

## Phase 7: User Story 6 - SQ日の取得と判定 (Priority: P1)

**Goal**: 指定年月のSQ日を取得し、SQ日判定ができる

**Independent Test**: SQ日取得がPythonインタープリタで完結

**Depends on**: US11 (cache), US3 (market)

### Tests for User Story 6

- [ ] T047 [P] [US6] Unit test for get_sq_date in python/tests/integration/test_jpx_index.py
- [ ] T048 [P] [US6] Unit test for is_sq_date in python/tests/integration/test_jpx_index.py
- [ ] T049 [P] [US6] Unit test for get_sq_dates_for_year in python/tests/integration/test_jpx_index.py
- [ ] T050 [P] [US6] Unit test for SQDataNotFoundError when data missing in python/tests/integration/test_jpx_index.py

### Implementation for User Story 6

- [ ] T051 [US6] Implement SQ date lookup from cache in python/src/marketsched/jpx/calendar.py
- [ ] T052 [US6] Implement JPXIndex.get_sq_date() in python/src/marketsched/jpx/index.py
- [ ] T053 [US6] Implement JPXIndex.is_sq_date() in python/src/marketsched/jpx/index.py
- [ ] T054 [US6] Implement JPXIndex.get_sq_dates_for_year() in python/src/marketsched/jpx/index.py

**Checkpoint**: SQ date functions are independently testable

---

## Phase 8: User Story 1 - パッケージのインストールとインポート (Priority: P1) 🎯 MVP

**Goal**: pip install marketsched でインストールし、import marketsched でインポートできる

**Independent Test**: pip install / import の動作確認

**Note**: Phase 2-7完了後に、パッケージとしての統合テスト

### Tests for User Story 1

- [ ] T055 [P] [US1] Test package import in python/tests/test_package.py
- [ ] T056 [P] [US1] Test public API availability (Market, ContractMonth, TradingSession) in python/tests/test_package.py

### Implementation for User Story 1

- [ ] T057 [US1] Verify all public exports in python/src/marketsched/__init__.py
- [ ] T058 [US1] Add package metadata (version, description) to pyproject.toml
- [ ] T059 [US1] Run full test suite and fix any issues

**Checkpoint**: MVP complete - Core Python library is functional

---

## Phase 9: User Story 5 - 期間内営業日の取得 (Priority: P2)

**Goal**: 期間内の営業日リストと営業日数を取得できる

**Independent Test**: 期間指定の営業日取得がPythonインタープリタで完結

### Tests for User Story 5

- [ ] T060 [P] [US5] Unit test for get_business_days in python/tests/integration/test_jpx_index.py
- [ ] T061 [P] [US5] Unit test for count_business_days in python/tests/integration/test_jpx_index.py

### Implementation for User Story 5

- [ ] T062 [US5] Implement JPXIndex.get_business_days() in python/src/marketsched/jpx/index.py
- [ ] T063 [US5] Implement JPXIndex.count_business_days() in python/src/marketsched/jpx/index.py

**Checkpoint**: Period business day functions are independently testable

---

## Phase 10: User Story 7 - 取引セッション判定 (Priority: P2)

**Goal**: 指定時刻がどの取引セッションに属するかを判定できる

**Independent Test**: セッション判定がPythonインタープリタで完結

### Tests for User Story 7

- [ ] T064 [P] [US7] Unit test for get_session with DAY session in python/tests/integration/test_jpx_index.py
- [ ] T065 [P] [US7] Unit test for get_session with NIGHT session in python/tests/integration/test_jpx_index.py
- [ ] T066 [P] [US7] Unit test for get_session with CLOSED (gap period) in python/tests/integration/test_jpx_index.py
- [ ] T067 [P] [US7] Unit test for is_trading_hours in python/tests/integration/test_jpx_index.py
- [ ] T068 [P] [US7] Unit test for TimezoneRequiredError with naive datetime in python/tests/integration/test_jpx_index.py
- [ ] T069 [P] [US7] Unit test for timezone conversion (UTC to JST) in python/tests/integration/test_jpx_index.py

### Implementation for User Story 7

- [ ] T070 [US7] Implement timezone validation helper in python/src/marketsched/jpx/index.py
- [ ] T071 [US7] Implement session time checking logic in python/src/marketsched/jpx/index.py (handle night session date boundary: 17:00 JST belongs to current date, 00:00-06:00 JST belongs to previous trading date)
- [ ] T072 [US7] Implement JPXIndex.get_session() in python/src/marketsched/jpx/index.py
- [ ] T073 [US7] Implement JPXIndex.is_trading_hours() in python/src/marketsched/jpx/index.py

**Checkpoint**: Session functions are independently testable

---

## Phase 11: User Story 8 - CLIによる営業日判定 (Priority: P2)

**Goal**: mks bd コマンドで営業日判定ができる

**Independent Test**: CLI実行で完結

### Tests for User Story 8

- [ ] T074 [P] [US8] CLI test for `mks bd is` in python/tests/cli/test_bd.py
- [ ] T075 [P] [US8] CLI test for `mks bd next` in python/tests/cli/test_bd.py
- [ ] T076 [P] [US8] CLI test for `mks bd prev` in python/tests/cli/test_bd.py
- [ ] T077 [P] [US8] CLI test for `mks bd list` in python/tests/cli/test_bd.py
- [ ] T078 [P] [US8] CLI test for `mks bd count` in python/tests/cli/test_bd.py

### Implementation for User Story 8

- [ ] T078a [P] [US8] CLI test for `mks --help` and `mks --version` in python/tests/cli/test_main.py
- [ ] T079 [US8] Create CLI main app structure with Typer in python/src/marketsched/cli/main.py (include --help and --version options per FR-CLI-006/007)
- [ ] T080 [US8] Implement bd subcommand group in python/src/marketsched/cli/bd.py
- [ ] T081 [US8] Implement output formatters (JSON, text, table) in python/src/marketsched/cli/main.py
- [ ] T082 [US8] Add CLI entry points (marketsched, mks) to pyproject.toml

**Checkpoint**: Business day CLI is functional

---

## Phase 12: User Story 9 - CLIによるSQ日取得 (Priority: P2)

**Goal**: mks sq コマンドでSQ日を取得できる

**Independent Test**: CLI実行で完結

### Tests for User Story 9

- [ ] T083 [P] [US9] CLI test for `mks sq get` with multiple formats in python/tests/cli/test_sq.py
- [ ] T084 [P] [US9] CLI test for `mks sq list` in python/tests/cli/test_sq.py
- [ ] T085 [P] [US9] CLI test for `mks sq is` in python/tests/cli/test_sq.py

### Implementation for User Story 9

- [ ] T086 [US9] Implement sq subcommand group in python/src/marketsched/cli/sq.py
- [ ] T087 [US9] Implement year-month parsing (2 args, YYYYMM, YYYY-MM) in python/src/marketsched/cli/sq.py

**Checkpoint**: SQ date CLI is functional

---

## Phase 13: User Story 10 - CLIによるセッション判定 (Priority: P2)

**Goal**: mks ss コマンドでセッション判定ができる

**Independent Test**: CLI実行で完結

### Tests for User Story 10

- [ ] T088 [P] [US10] CLI test for `mks ss get` with datetime in python/tests/cli/test_ss.py
- [ ] T089 [P] [US10] CLI test for `mks ss get` without datetime (current time) in python/tests/cli/test_ss.py
- [ ] T090 [P] [US10] CLI test for `mks ss is-trading` in python/tests/cli/test_ss.py
- [ ] T091 [P] [US10] CLI test for timezone error handling in python/tests/cli/test_ss.py

### Implementation for User Story 10

- [ ] T092 [US10] Implement ss subcommand group in python/src/marketsched/cli/ss.py
- [ ] T093 [US10] Implement ISO 8601 datetime parsing with timezone validation in python/src/marketsched/cli/ss.py

**Checkpoint**: Session CLI is functional

---

## Phase 14: User Story 11 CLI - CLIによるキャッシュ管理 (Priority: P2)

**Goal**: mks cache コマンドでキャッシュを管理できる

**Independent Test**: CLI実行で完結

### Tests for User Story 11 CLI

- [ ] T094 [P] [US11] CLI test for `mks cache update` in python/tests/cli/test_cache.py
- [ ] T095 [P] [US11] CLI test for `mks cache clear` in python/tests/cli/test_cache.py
- [ ] T096 [P] [US11] CLI test for `mks cache status` in python/tests/cli/test_cache.py

### Implementation for User Story 11 CLI

- [ ] T097 [US11] Implement cache subcommand group in python/src/marketsched/cli/cache.py
- [ ] T098 [US11] Create cli/__init__.py with app assembly in python/src/marketsched/cli/__init__.py

**Checkpoint**: Cache CLI is functional, CLI MVP complete

---

## Phase 15: Polish & Cross-Cutting Concerns

**Purpose**: Quality improvements and documentation

- [ ] T099 [P] Add docstrings to all public APIs
- [ ] T100 [P] Run mypy --strict and fix type issues
- [ ] T101 [P] Run ruff check and fix linting issues
- [ ] T102 Create README.md with quickstart guide in python/README.md
- [ ] T103 Run quickstart.md validation (all examples work)
- [ ] T104 Verify test coverage >= 90%

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1: Setup
    ↓
Phase 2: Foundational (exceptions, session, market protocol)
    ↓
Phase 3: US2 ContractMonth (独立)
    ↓
Phase 4: US11 Cache (独立)
    ↓
Phase 5: US3 Market (depends on Phase 2)
    ↓
Phase 6: US4 Business Day (depends on US3, US11)
Phase 7: US6 SQ Date (depends on US3, US11) [parallel with Phase 6]
    ↓
Phase 8: US1 Package Integration (depends on all P1 stories) 🎯 MVP
    ↓
Phase 9-10: US5, US7 (P2 Python API)
    ↓
Phase 11-14: US8, US9, US10, US11-CLI (P2 CLI)
    ↓
Phase 15: Polish
```

### User Story Dependencies

| Story | Depends On | Can Parallelize With |
|-------|-----------|---------------------|
| US2 (ContractMonth) | Foundational | US11 (Cache) |
| US11 (Cache) | Foundational | US2 (ContractMonth) |
| US3 (Market) | Foundational | - |
| US4 (BusinessDay) | US3, US11 | US6 (SQ) |
| US6 (SQ) | US3, US11 | US4 (BusinessDay) |
| US1 (Package) | US2, US3, US4, US6, US11 | - |
| US5 (Period BD) | US4 | US7 (Session) |
| US7 (Session) | US3 | US5 (Period BD) |
| US8 (CLI BD) | US4, CLI main | US9, US10 |
| US9 (CLI SQ) | US6, CLI main | US8, US10 |
| US10 (CLI SS) | US7, CLI main | US8, US9 |
| US11-CLI | US11, CLI main | US8, US9, US10 |

### Parallel Opportunities

**Phase 2 (Foundational)**:
```
T006, T007 → T008, T009 (tests and implementations can pair)
```

**Phase 3-4 (P1 independent stories)**:
```
US2 (ContractMonth) || US11 (Cache)
```

**Phase 6-7 (P1 dependent stories)**:
```
US4 (BusinessDay) || US6 (SQ)
```

**Phase 9-10 (P2 Python API)**:
```
US5 (Period BD) || US7 (Session)
```

**Phase 11-14 (P2 CLI)**:
```
US8 (CLI BD) || US9 (CLI SQ) || US10 (CLI SS) || US11-CLI
```

---

## Parallel Example: Phase 11-14 (All CLI Commands)

```bash
# After CLI main structure (T079-T081) is complete:

# Launch all CLI tests in parallel:
pytest python/tests/cli/test_bd.py &
pytest python/tests/cli/test_sq.py &
pytest python/tests/cli/test_ss.py &
pytest python/tests/cli/test_cache.py &

# Then implement in parallel:
# Developer A: bd.py
# Developer B: sq.py
# Developer C: ss.py
# Developer D: cache.py
```

---

## Implementation Strategy

### MVP First (P1 Stories Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: US2 ContractMonth
4. Complete Phase 4: US11 Cache
5. Complete Phase 5: US3 Market
6. Complete Phase 6-7: US4 + US6 (parallel)
7. Complete Phase 8: US1 Package Integration
8. **STOP and VALIDATE**: Run all tests, verify quickstart examples

**MVP Deliverable**: Python library with ContractMonth, Market (JPXIndex), business day, SQ date functions

### Incremental Delivery

1. MVP (P1) → Python library usable via `import marketsched`
2. P2 Python API → Period business days, session judgment
3. P2 CLI → All `mks` commands functional
4. Polish → Documentation, coverage, type checking

### TDD Enforcement

For each task group:
1. Write tests first (T0xx tests)
2. Run tests - verify they FAIL
3. Implement code
4. Run tests - verify they PASS
5. Refactor if needed
6. Commit

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- TDD required: Always write and run tests BEFORE implementation
- Quality gates before commit: `uv run ruff check . && uv run mypy src && uv run pytest`
- Avoid naive datetime anywhere in the codebase (Constitution III)
