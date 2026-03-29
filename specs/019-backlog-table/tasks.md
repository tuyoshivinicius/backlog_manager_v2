# Tasks: EP-019 — Tabela de Backlog (GUI-003)

**Input**: Design documents from `/specs/019-backlog-table/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/table-model-contract.md, quickstart.md

**Tests**: Included — US5 explicitly requests unit tests (FR-024, FR-025).

**Organization**: Tasks grouped by user story. US1/US2 are P1 (core), US3/US4/US5 are P2 (polish/quality).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project setup needed — existing codebase. Verify branch and dependencies.

- [x] T001 Verify branch `019-backlog-table` is up-to-date with main and `poetry install` succeeds

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Enrich StoryOutputDTO with resolved names and update ListStoriesUseCase. ALL user stories depend on enriched DTOs.

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T002 Add fields `developer_name: str | None = None`, `feature_name: str | None = None`, `wave: int = 0`, `dependency_ids: list[str] = Field(default_factory=list)` to StoryOutputDTO in `src/backlog_manager/application/dto/story/story_output_dto.py`
- [x] T003 Update `ListStoriesUseCase.execute()` to build developer/feature lookup maps and populate enriched DTO fields (developer_name, feature_name, wave, dependency_ids) in `src/backlog_manager/application/use_cases/story/list_stories.py` — reference `ExportExcelUseCase._build_stories_data()` pattern

**Checkpoint**: Foundation ready — enriched DTOs available for all stories

---

## Phase 3: User Story 1 — Visualizacao completa do backlog em 13 colunas (Priority: P1) 🎯 MVP

**Goal**: Expand StoryTableModel from 8 to 13 columns with correct formatting, alignment, and tooltips

**Independent Test**: Load stories into model and verify all 13 columns display correct data with proper formatting (dates DD/MM/YYYY, IDs COMPONENTE-NNN, resolved names, "—" for missing values)

### Implementation for User Story 1

- [x] T004 [US1] Update `COLUMNS` constant to 13 headers in new order (Prioridade, Feature, Onda, ID, Componente, Nome, Status, Desenvolvedor, Dependencias, SP, Inicio, Fim, Duracao) in `src/backlog_manager/presentation/viewmodels/story_table_model.py`
- [x] T005 [US1] Add constants `COLUMN_WIDTHS`, `CENTER_COLUMNS`, `TOOLTIP_COLUMNS` as defined in data-model.md in `src/backlog_manager/presentation/viewmodels/story_table_model.py`
- [x] T006 [US1] Rewrite `_get_display_value()` (or equivalent data method) to format all 13 columns: dates as DD/MM/YYYY, dependency_ids joined by ", ", resolved names, "—" for None/empty in `src/backlog_manager/presentation/viewmodels/story_table_model.py`
- [x] T007 [US1] Update `data()` for `TextAlignmentRole` to use `CENTER_COLUMNS` set (indices 0,2,6,9,10,11,12 → AlignCenter, others → AlignLeft|AlignVCenter) in `src/backlog_manager/presentation/viewmodels/story_table_model.py`
- [x] T008 [US1] Add `ToolTipRole` support in `data()` returning full text for columns in `TOOLTIP_COLUMNS` (indices 1,5,7,8) in `src/backlog_manager/presentation/viewmodels/story_table_model.py`
- [x] T009 [US1] Add `UserRole` support in `data()` returning `story.id` for all columns in `src/backlog_manager/presentation/viewmodels/story_table_model.py`

**Checkpoint**: StoryTableModel exposes 13 columns with correct data — model layer complete

---

## Phase 4: User Story 2 — Larguras, alinhamentos e delegates corretos por coluna (Priority: P1)

**Goal**: Configure column widths (fixed + stretch), reposition delegates to new indices, enable text elision with tooltips

**Independent Test**: Verify MonospaceDelegate at column 3 (ID), StatusBadgeDelegate at column 6 (Status), fixed widths applied, Nome column stretches

### Implementation for User Story 2

- [x] T010 [US2] Update delegate assignment to use dynamic header text lookup ("ID" → MonospaceDelegate, "Status" → StatusBadgeDelegate) instead of hardcoded indices in `src/backlog_manager/presentation/views/main_window.py`
- [x] T011 [US2] Configure `QHeaderView` with `ResizeMode.Fixed` for all columns except Nome (index 5) which uses `ResizeMode.Stretch`, set `setStretchLastSection(False)`, and apply widths from `COLUMN_WIDTHS` in `src/backlog_manager/presentation/views/main_window.py`
- [x] T012 [US2] Enable text elision mode (`setTextElideMode(Qt.ElideRight)`) on the table view for truncated columns in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: Table visually displays 13 columns with correct widths, delegates, and elision

---

## Phase 5: User Story 3 — Estado vazio orientativo (Priority: P2)

**Goal**: Show guidance message when backlog is empty, disable processing buttons

**Independent Test**: Open app with no stories — verify overlay message appears and "Calcular Cronograma"/"Alocar" buttons are disabled; add a story — verify message disappears

### Implementation for User Story 3

- [x] T013 [US3] Create `QLabel` overlay widget as child of central area with text "Nenhuma historia cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para comecar." styled with neutral-500 color, 14px font, centered in `src/backlog_manager/presentation/views/main_window.py`
- [x] T014 [US3] Implement empty state toggle logic: on `stories_changed` signal (or after `set_stories`), show overlay and disable `_action_schedule`/`_action_allocate` when `rowCount() == 0`, hide overlay and enable buttons when `rowCount() > 0` in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: Empty state UX complete — new users see guidance, buttons reflect state

---

## Phase 6: User Story 4 — Estilizacao visual consistente (Priority: P2)

**Goal**: Ensure zebra striping, selection highlight (#E6F0FA with dark text), and styled header

**Independent Test**: Visual inspection — alternating row colors, blue selection without color inversion, header with weight 600 and bottom border

### Implementation for User Story 4

- [x] T015 [US4] Verify `setAlternatingRowColors(True)` is active and QSS defines alternating row background colors in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [x] T016 [US4] Verify/adjust QSS for `QTableView::item:selected` to use background `#E6F0FA` with dark text (no color inversion) in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [x] T017 [US4] Verify/adjust QSS for `QHeaderView::section` to use font-weight 600, secondary text color, and bottom border in `src/backlog_manager/presentation/theme/stylesheet.qss`
- [x] T018 [US4] Set selection mode to single row (`setSelectionBehavior(QAbstractItemView.SelectRows)`, `setSelectionMode(QAbstractItemView.SingleSelection)`) in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: Table styling matches design system — zebra, selection, header all correct

---

## Phase 7: User Story 5 — Testes unitarios para o modelo expandido (Priority: P2)

**Goal**: Unit tests covering StoryTableModel with >= 80% coverage, plus integration test updates

**Independent Test**: Run test suite — all pass, coverage >= 80% for story_table_model.py

### Tests for User Story 5

- [x] T019 [P] [US5] Test `columnCount() == 13` and `headerData()` returns correct names for all 13 columns in `tests/unit/presentation/viewmodels/test_story_table_model.py`
- [x] T020 [P] [US5] Test `data(DisplayRole)` for each column with fully populated DTO (dates as DD/MM/YYYY, IDs formatted, names resolved) in `tests/unit/presentation/viewmodels/test_story_table_model.py`
- [x] T021 [P] [US5] Test `data(DisplayRole)` for missing/None values returns "—" for optional columns (feature_name, developer_name, dependency_ids, start_date, end_date, duration, component) in `tests/unit/presentation/viewmodels/test_story_table_model.py`
- [x] T022 [P] [US5] Test `data(TextAlignmentRole)` returns AlignCenter for columns {0,2,6,9,10,11,12} and AlignLeft|AlignVCenter for others in `tests/unit/presentation/viewmodels/test_story_table_model.py`
- [x] T023 [P] [US5] Test `data(ToolTipRole)` returns full text only for columns {1,5,7,8} and None for others in `tests/unit/presentation/viewmodels/test_story_table_model.py`
- [x] T024 [P] [US5] Test empty state: `rowCount() == 0` when no stories set in `tests/unit/presentation/viewmodels/test_story_table_model.py`
- [x] T025[US5] Update integration tests for delegate indices (MonospaceDelegate → column 3, StatusBadgeDelegate → column 6) and verify no regressions with 13 columns in `tests/integration/presentation/test_delegates_integration.py`
- [x] T025b [US5] Test empty state view behavior with pytest-qt: (1) overlay QLabel visible and buttons disabled when rowCount()==0, (2) overlay hidden and buttons enabled after set_stories() with data, (3) overlay reappears after removing last story — covers FR-017/FR-018/FR-019/FR-020 in `tests/integration/presentation/test_empty_state_view.py`
- [x] T025c [P] [US5] Test edge cases in StoryTableModel: (1) developer_id with no matching developer → "—", (2) feature_id with no matching feature → "—"/"—", (3) dependency_ids with orphaned IDs displayed as-is, (4) empty component → "—", (5) None duration → "—" in `tests/unit/presentation/viewmodels/test_story_table_model.py`
- [x] T025d [P] [US5] Test long text edge case: story.name with >500 chars returns full text in ToolTipRole and truncated display via elipsis in `tests/unit/presentation/viewmodels/test_story_table_model.py`

**Checkpoint**: Test suite green, coverage >= 80% for StoryTableModel, zero regressions

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cross-cutting improvements

- [x] T026 Run full test suite (`poetry run pytest -v`) and verify zero regressions across entire project
- [x] T027 Run coverage report (`poetry run pytest --cov=src/backlog_manager/presentation/viewmodels/story_table_model --cov-report=term-missing`) and verify >= 80%
- [x] T028 Run quickstart.md visual verification checklist (13 columns, widths, delegates, zebra, empty state)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — verify environment
- **Foundational (Phase 2)**: Depends on Phase 1 — BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Phase 2 — model layer must have enriched DTOs
- **US2 (Phase 4)**: Depends on Phase 3 — view configuration requires 13-column model
- **US3 (Phase 5)**: Depends on Phase 3 — empty state logic uses table model
- **US4 (Phase 6)**: Depends on Phase 4 — styling applies to configured table
- **US5 (Phase 7)**: Depends on Phase 3 + Phase 4 — tests validate final model and view
- **Polish (Phase 8)**: Depends on all previous phases

### User Story Dependencies

- **US1 (P1)**: Depends only on Foundational (Phase 2). Core model changes.
- **US2 (P1)**: Depends on US1 (needs 13-column model to assign delegates/widths correctly)
- **US3 (P2)**: Depends on US1 (empty state checks rowCount of expanded model). Can parallel with US2.
- **US4 (P2)**: Depends on US2 (styling applies to configured view). Can parallel with US3.
- **US5 (P2)**: Depends on US1 + US2 (tests validate final behavior). Can parallel with US3/US4.

### Within Each User Story

- Constants/schema before formatting logic
- Model layer before view layer
- Core implementation before tests

### Parallel Opportunities

- **Phase 2**: T002 and T003 are sequential (T003 depends on T002's new fields)
- **Phase 3**: T004 + T005 can run in parallel (constants), then T006-T009 sequentially (depend on constants)
- **Phase 4**: T010, T011, T012 can run in parallel (different concerns in same file but independent sections)
- **Phase 5**: T013 and T014 are sequential (T014 depends on T013's overlay widget)
- **Phase 6**: T015, T016, T017 can run in parallel (different QSS selectors), T018 parallel with all
- **Phase 7**: T019-T024 can ALL run in parallel (independent test functions in same file), T025 independent

---

## Parallel Example: User Story 5

```bash
# Launch all unit tests in parallel (different test functions, same file):
Task: T019 "Test columnCount and headerData"
Task: T020 "Test data(DisplayRole) with populated DTO"
Task: T021 "Test data(DisplayRole) with missing values"
Task: T022 "Test data(TextAlignmentRole)"
Task: T023 "Test data(ToolTipRole)"
Task: T024 "Test empty state"

# Then sequential:
Task: T025 "Update integration tests" (after unit tests pass)
```

---

## Implementation Strategy

### MVP First (US1 + US2 Only)

1. Complete Phase 1: Setup verification
2. Complete Phase 2: Foundational (enrich DTO + use case)
3. Complete Phase 3: US1 — 13-column model
4. Complete Phase 4: US2 — widths, delegates, elision
5. **STOP and VALIDATE**: Table displays 13 columns correctly with delegates
6. This is a functional MVP — users see all data

### Incremental Delivery

1. Phase 1 + 2 → Enriched DTOs ready
2. US1 → Model exposes 13 columns → Validate data correctness
3. US2 → View configured properly → Validate visual layout (MVP!)
4. US3 → Empty state → Validate first-use experience
5. US4 → Styling polish → Validate design system compliance
6. US5 → Tests → Validate quality gate (>= 80% coverage)
7. Polish → Full regression check

---

## Notes

- [P] tasks = different files or independent sections, no dependencies
- [Story] label maps task to specific user story for traceability
- All file paths are relative to repository root
- Key files: `story_output_dto.py`, `list_stories.py`, `story_table_model.py`, `main_window.py`, `stylesheet.qss`
- Reference `ExportExcelUseCase` for DTO enrichment pattern (R-001)
- Reference R-002 for dynamic delegate lookup by header text
- Reference R-004 for QHeaderView resize mode configuration
