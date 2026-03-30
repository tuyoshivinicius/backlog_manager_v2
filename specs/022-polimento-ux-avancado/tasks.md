# Tasks: EP-022 — Polimento e UX Avancado

**Input**: Design documents from `/specs/022-polimento-ux-avancado/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contracts.md, quickstart.md

**Tests**: Included — spec mentions pytest + pytest-qt + pytest-asyncio testing requirements.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Foundational models and utilities shared across multiple user stories

- [X] T001 Create `BlockingState` enum in `src/backlog_manager/presentation/viewmodels/story_table_model.py` (BLOCKED, FREE, NONE per data-model.md)
- [X] T002 [P] Add `_story_status_map: dict[str, str]` to `StoryTableModel` in `src/backlog_manager/presentation/viewmodels/story_table_model.py`, updated when stories change
- [X] T003 [P] Add custom data roles (`UserRole+1` for BlockingState, `UserRole+2` for dependency IDs) to `StoryTableModel.data()` for column 8 (Dependencias) in `src/backlog_manager/presentation/viewmodels/story_table_model.py`

**Checkpoint**: Shared model infrastructure ready — user story implementation can begin

---

## Phase 2: User Story 1 — SP Breakdown na Status Bar (Priority: P1) MVP

**Goal**: Display story points breakdown by status in the status bar with tooltip percentages

**Independent Test**: Load stories with different statuses, verify status bar shows "X SP Backlog · Y SP Execucao · Z SP Concluido" with percentage tooltip

### Tests for User Story 1

- [X] T004 [P] [US1] Unit test for `StatusBarViewModel.update_sp_breakdown()` in `tests/unit/presentation/viewmodels/test_status_bar_viewmodel_sp_breakdown.py` — test breakdown computation with mixed statuses, empty backlog, and all 5 statuses
- [X] T005 [P] [US1] Unit test for `SpBreakdownLabel` display format and tooltip in `tests/unit/presentation/views/test_sp_breakdown_label.py` — verify format "X SP Status · Y SP Status", only statuses with SP>0 shown (except BACKLOG always), tooltip percentages

### Implementation for User Story 1

- [X] T006 [P] [US1] Add `sp_breakdown_changed` signal and `update_sp_breakdown(stories)` method to `StatusBarViewModel` in `src/backlog_manager/presentation/viewmodels/status_bar_viewmodel.py` — compute `dict[str, int]` breakdown, `total_sp`, and `dict[str, float]` percentages
- [X] T007 [P] [US1] Create `SpBreakdownLabel(QLabel)` in `src/backlog_manager/presentation/views/status_bar.py` — display "X SP Backlog · Y SP Execucao · ..." format per Contract 1, tooltip with percentages
- [X] T008 [US1] Wire `SpBreakdownLabel` into status bar layout and connect `sp_breakdown_changed` signal in `src/backlog_manager/presentation/views/status_bar.py`
- [X] T009 [US1] Trigger `update_sp_breakdown()` from `MainWindow` when stories are loaded/updated in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: SP breakdown visible in status bar, independently testable

---

## Phase 3: User Story 2 — Indicador de Bloqueio na Coluna Dependencias (Priority: P1)

**Goal**: Show red/green/none blocking indicators in the Dependencies column

**Independent Test**: Create stories with dependencies in different statuses, verify delegate renders correct icon

### Tests for User Story 2

- [X] T010 [P] [US2] Unit test for blocking state resolution in `StoryTableModel` in `tests/unit/presentation/viewmodels/test_story_table_model_blocking.py` — test BLOCKED (dep not CONCLUIDO), FREE (all deps CONCLUIDO), NONE (no deps), missing dep treated as BLOCKED
- [X] T011 [P] [US2] Pytest-qt test for `DependencyIndicatorDelegate` rendering in `tests/e2e/test_ep022_dependency_indicator.py` — verify red circle for BLOCKED, green for FREE, em-dash for NONE

### Implementation for User Story 2

- [X] T012 [US2] Create `DependencyIndicatorDelegate(QStyledItemDelegate)` in `src/backlog_manager/presentation/delegates/dependency_indicator_delegate.py` — paint red (#DC3545) / green (#28A745) filled circle (8px) + dependency IDs text, or em-dash for NONE per Contract 2
- [X] T013 [US2] Wire `DependencyIndicatorDelegate` to column 8 (Dependencias) in `StoryTableView` setup within `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: Blocking indicators visible in Dependencies column, independently testable

---

## Phase 4: User Story 3 — Persistencia de Configuracao via QSettings (Priority: P1)

**Goal**: Persist allocation config (velocity, start_date, max_idle_days) between sessions via QSettings

**Independent Test**: Save values in ConfigDialog, simulate restart, verify values restored; test corrupt values fall back to defaults

### Tests for User Story 3

- [X] T014 [P] [US3] Unit test for QSettings load/save with validation in `tests/unit/presentation/viewmodels/test_config_dialog_viewmodel_qsettings.py` — test save, load, range validation (velocity 0.1-10.0, max_idle_days 2-30), corrupt values use defaults, first run uses defaults

### Implementation for User Story 3

- [X] T015 [US3] Add QSettings load in `ConfigDialogViewModel.__init__()` and save in `save()` method in `src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py` — use INI format, group "allocation", keys "velocity"/"start_date"/"max_idle_days", validate ranges on load per Contract 5 and R-004

**Checkpoint**: Config persistence working, independently testable

---

## Phase 5: User Story 4 — Agrupamento Visual por Onda na Tabela (Priority: P2)

**Goal**: Display visual wave separators between wave groups in the backlog table

**Independent Test**: Load stories from multiple waves, verify separators appear between wave groups with "Onda N" labels

### Tests for User Story 4

- [X] T016 [P] [US4] Pytest-qt test for wave separators in `tests/e2e/test_ep022_wave_separators.py` — verify separators between waves, "Sem Onda" for wave=0, hidden when sorted by non-wave column, visible with active filters, visible when Onda column hidden by resize

### Implementation for User Story 4

- [X] T017 [US4] Override `paintEvent()` in existing `StoryTableView` in `src/backlog_manager/presentation/views/main_window.py` — detect wave boundaries by comparing consecutive rows' wave values, paint 24px separator bands with "Onda N" / "Sem Onda" text per Contract 3
- [X] T018 [US4] Add `_wave_separators_visible` flag tied to sort order in `src/backlog_manager/presentation/views/main_window.py` — True only in default sort (by wave/priority), False when sorted by another column; connect to `QHeaderView.sortIndicatorChanged` signal

**Checkpoint**: Wave separators visible in default sort, hidden otherwise, independently testable

---

## Phase 6: User Story 5 — Tooltip Rico na Tabela (Priority: P2)

**Goal**: Show a rich mini-card popup after 300ms hover with complete story details

**Independent Test**: Hover over table row, verify popup appears after 300ms with all fields (ID, Nome, Status badge, SP, Feature, Dev, Deps, dates)

### Tests for User Story 5

- [X] T019 [P] [US5] Pytest-qt test for `RichTooltipWidget` in `tests/e2e/test_ep022_rich_tooltip.py` — verify content layout, 300ms delay, disappears on mouse leave, empty fields show "-", repositions near window edges

### Implementation for User Story 5

- [X] T020 [US5] Create `RichTooltipWidget(QWidget)` in `src/backlog_manager/presentation/views/rich_tooltip.py` — frameless ToolTip window, max-width 350px, layout per Contract 4 (ID + Status badge, Nome, SP/Feature/Dev/Deps/dates grid), auto-sized
- [X] T021 [US5] Wire tooltip to `StoryTableView` in `src/backlog_manager/presentation/views/main_window.py` — override `mouseMoveEvent` with 300ms QTimer, show tooltip at cursor+10px offset, reposition if near bottom edge, hide on `leaveEvent` or row change; track current hovered row to avoid re-creation

**Checkpoint**: Rich tooltip working on hover, independently testable

---

## Phase 7: User Story 6 — Cancelamento de Operacoes Longas (Priority: P2)

**Goal**: Allow cancellation of long-running operations (allocation, import, export) after 2s

**Independent Test**: Start a simulated long operation, verify Cancel button appears after 2s, clicking it aborts safely

### Tests for User Story 6

- [X] T022 [P] [US6] Pytest-qt test for cancellation flow in `tests/e2e/test_ep022_cancellation.py` — verify Cancel button hidden initially, appears after 2s, `cancelled` signal emitted on click, dialog closes after cancellation; also verify Cancel button does NOT appear for schedule calculation (FR-016 negative case)

### Implementation for User Story 6

- [X] T023 [US6] Add `cancelled` signal, `set_cancellable_task(task)` method, and cancel button with 2s QTimer to `ProgressDialog` in `src/backlog_manager/presentation/views/progress_dialog.py` — button hidden initially, shown after 2s via QTimer, on click calls `task.cancel()` per Contract 5
- [X] T024 [US6] Handle `asyncio.CancelledError` in allocation viewmodel in `src/backlog_manager/presentation/viewmodels/allocation_viewmodel.py` — snapshot stories before allocation, catch CancelledError, restore snapshot to model, rollback UnitOfWork if DB writes occurred, emit cancellation signal
- [X] T025 [P] [US6] Handle `asyncio.CancelledError` in excel viewmodel in `src/backlog_manager/presentation/viewmodels/excel_viewmodel.py` — for import: UnitOfWork rollback handles DB consistency; for export: delete partial file in handler
- [X] T026 [US6] Wire cancellable task to ProgressDialog from MainWindow for allocation, import, and export operations in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: Cancellation working for all 3 operation types, independently testable

---

## Phase 8: User Story 7 — Dialog "Sobre" (Priority: P3)

**Goal**: About dialog showing app name, version, technologies, and database path

**Independent Test**: Open Ajuda > Sobre menu, verify dialog shows name, version, Python version, tech list, DB path

### Tests for User Story 7

- [X] T027 [P] [US7] Pytest-qt test for `AboutDialog` in `tests/e2e/test_ep022_about_dialog.py` — verify content fields, version fallback to "dev", dialog close on Esc

### Implementation for User Story 7

- [X] T028 [US7] Create `AboutDialog(QDialog)` in `src/backlog_manager/presentation/views/about_dialog.py` — fixed 400x300px, show app name "Backlog Manager", version via `importlib.metadata.version("backlog-manager")` with "dev" fallback, Python version via `sys.version`, tech list (Python, PySide6, SQLite, Pydantic, qasync), DB path from container per Contract 6
- [X] T029 [US7] Add "Ajuda > Sobre" menu action in `MainWindow` in `src/backlog_manager/presentation/views/main_window.py` — trigger `AboutDialog` with container reference for db_path

**Checkpoint**: About dialog accessible via menu, independently testable

---

## Phase 9: User Story 8 — Responsividade a Resize (Priority: P3)

**Goal**: Auto-hide non-essential columns when window width < 1024px

**Independent Test**: Resize window below 1024px, verify columns Componente (4), Onda (2), Duracao (12) hidden; resize back, verify restored

### Tests for User Story 8

- [X] T030 [P] [US8] Pytest-qt test for responsive column hiding in `tests/e2e/test_ep022_responsive.py` — verify columns hidden at <1024px, restored at >=1024px, hidden columns indicator visible/hidden

### Implementation for User Story 8

- [X] T031 [US8] Override `resizeEvent()` in `MainWindow` in `src/backlog_manager/presentation/views/main_window.py` — check `self.width() < 1024`, hide columns 2 (Onda), 4 (Componente), 12 (Duracao) via `setColumnHidden()`, track state to avoid redundant ops per Contract 7
- [X] T032 [US8] Add hidden columns indicator label in status bar in `src/backlog_manager/presentation/views/status_bar.py` — show "{N} colunas ocultas" when columns hidden, hide when all restored per Contract 7

**Checkpoint**: Responsive column hiding working, independently testable

---

## Phase 10: User Story 9 — Validacao de Layout em Resolucao Minima (Priority: P3)

**Goal**: Validate layout works at 1024x600 without overlap or clipping in all 5 zones

**Independent Test**: Set window to 1024x600, verify menu bar, toolbar, filter bar, table, and status bar all visible without overlap

### Tests for User Story 9

- [X] T033 [P] [US9] Pytest-qt validation test in `tests/e2e/test_ep022_min_resolution.py` — set window to 1024x600, verify all 5 zones visible and non-overlapping, toolbar overflow handling

### Implementation for User Story 9

- [X] T034 [US9] Validate and fix layout at 1024x600 in `src/backlog_manager/presentation/views/main_window.py` — ensure `setMinimumSize(1024, 600)`, toolbar has horizontal scroll overflow, filter bar chips scrollable, no zone overlap

**Checkpoint**: Layout validated at minimum resolution

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cross-cutting improvements

- [X] T035 Run full test suite to verify 0 regressions in existing tests
- [X] T036 Verify all new visual components respond in <100ms per SC-010
- [X] T037 Run quickstart.md validation — verify all 8 features working together
- [X] T038 Code cleanup — ensure type hints, docstrings on public classes/methods, isort/black/mypy compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US1 SP Breakdown (Phase 2)**: Depends on Phase 1 only for model infrastructure if reusing status map
- **US2 Blocking Indicator (Phase 3)**: Depends on Phase 1 (BlockingState enum, status map, custom roles)
- **US3 Config Persistence (Phase 4)**: Independent — no Phase 1 dependency
- **US4 Wave Separators (Phase 5)**: Independent — uses model data directly
- **US5 Rich Tooltip (Phase 6)**: Independent — reads model data via index
- **US6 Cancellation (Phase 7)**: Independent — modifies ProgressDialog and viewmodels
- **US7 About Dialog (Phase 8)**: Independent — new dialog, new menu action
- **US8 Responsive Resize (Phase 9)**: Independent — resize event + column hiding
- **US9 Min Resolution (Phase 10)**: Depends on US8 (responsive resize must be in place)
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Independence

| Story | Can Start After | Dependencies on Other Stories |
|-------|----------------|-------------------------------|
| US1 (P1) | Phase 1 | None |
| US2 (P1) | Phase 1 | None |
| US3 (P1) | Immediately | None |
| US4 (P2) | Immediately | None |
| US5 (P2) | Immediately | None |
| US6 (P2) | Immediately | None |
| US7 (P3) | Immediately | None |
| US8 (P3) | Immediately | None |
| US9 (P3) | US8 | Responsive resize must exist |

### Within Each User Story

- Tests written first → verify they FAIL
- Model/ViewModel changes before View wiring
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- T001, T002, T003 (Phase 1) can partially run in parallel
- US1, US2 can run in parallel after Phase 1
- US3, US4, US5, US6, US7, US8 can ALL start independently in parallel
- Within US6: T024 and T025 (allocation and excel cancellation handlers) can run in parallel
- Within US1: T004/T005 (tests) and T006/T007 (implementation) can run in parallel across test/impl tracks

---

## Parallel Example: User Stories 1 & 2

```bash
# After Phase 1 completes, launch US1 and US2 in parallel:

# US1 track:
Task: "T006 [US1] Add sp_breakdown_changed signal to StatusBarViewModel"
Task: "T007 [US1] Create SpBreakdownLabel in status_bar.py"

# US2 track (parallel):
Task: "T012 [US2] Create DependencyIndicatorDelegate"
Task: "T013 [US2] Wire delegate to column 8"
```

## Parallel Example: Independent P2/P3 Stories

```bash
# These can ALL run concurrently (different files, no dependencies):
Task: "T017 [US4] Wave separators paintEvent override"
Task: "T020 [US5] RichTooltipWidget creation"
Task: "T023 [US6] ProgressDialog cancel button"
Task: "T028 [US7] AboutDialog creation"
Task: "T031 [US8] Responsive resizeEvent override"
```

---

## Implementation Strategy

### MVP First (P1 Stories: US1 + US2 + US3)

1. Complete Phase 1: Setup (T001-T003)
2. Complete US1: SP Breakdown (T004-T009)
3. Complete US2: Blocking Indicator (T010-T013)
4. Complete US3: Config Persistence (T014-T015)
5. **STOP and VALIDATE**: All P1 features functional and testable
6. Deploy/demo if ready

### Incremental Delivery

1. Phase 1 → Setup ready
2. US1 (SP Breakdown) → Test independently → Status bar enhanced
3. US2 (Blocking Indicator) → Test independently → Dependencies column enhanced
4. US3 (Config Persistence) → Test independently → Config survives restarts
5. US4 (Wave Separators) → Test independently → Table grouping visual
6. US5 (Rich Tooltip) → Test independently → Hover info cards
7. US6 (Cancellation) → Test independently → Long ops cancellable
8. US7 (About Dialog) → Test independently → App info accessible
9. US8 + US9 (Responsive + Min Resolution) → Test together → Layout validated
10. Polish → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story is independently completable and testable
- All changes confined to Presentation layer (views, viewmodels, delegates)
- No domain, application, or infrastructure modifications needed
- No SQLite schema changes — QSettings for config, derived data for everything else
