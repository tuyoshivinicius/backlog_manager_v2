# Tasks: Column Resize

**Input**: Design documents from `/specs/027-column-resize/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-interactions.md

**Tests**: Included (plan.md constitution check XIV confirms pytest + pytest-qt).

**Organization**: Tasks grouped by user story (US1=drag resize, US2=persist widths, US3=restore defaults).

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Add constants and prepare shared configuration needed by all user stories

- [x] T001 Add `MINIMUM_COLUMN_WIDTH = 30` constant to `src/backlog_manager/presentation/viewmodels/story_table_model.py`
- [x] T002 [P] Add QSettings constants `QSETTINGS_GROUP = "column_widths"` and `QSETTINGS_KEY = "header_state"` to `src/backlog_manager/presentation/views/main_window.py` (in `StoryTableView` or `MainWindow` class)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Change resize mode from Fixed to Interactive — MUST complete before any user story can function

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T003 Change `ResizeMode.Fixed` to `ResizeMode.Interactive` for all columns except "Nome" (index 5, stays Stretch) in `src/backlog_manager/presentation/views/main_window.py` method `_setup_table_columns`
- [x] T004 Set `header.setMinimumSectionSize(30)` using `MINIMUM_COLUMN_WIDTH` constant in `src/backlog_manager/presentation/views/main_window.py` method `_setup_table_columns`

**Checkpoint**: Foundation ready — columns are now draggable but widths are not yet persisted

---

## Phase 3: User Story 1 — Redimensionar colunas arrastando a borda (Priority: P1) 🎯 MVP

**Goal**: Permitir que o usuario arraste a borda direita dos cabecalhos para redimensionar colunas, com cursor de indicacao e largura minima de 30px

**Independent Test**: Abrir a tabela do backlog e arrastar a borda direita de qualquer cabecalho de coluna para alterar sua largura. Coluna "Nome" deve permanecer flexivel.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T005 [US1] Create test file and test that columns use `ResizeMode.Interactive` (except "Nome" which uses Stretch) in `tests/unit/presentation/test_column_resize.py`
- [x] T006 [US1] Test that minimum section size is 30px in `tests/unit/presentation/test_column_resize.py`
- [x] T007 [US1] Test that "Nome" column (index 5) cannot be manually resized (stays Stretch) in `tests/unit/presentation/test_column_resize.py`

### Implementation for User Story 1

- [x] T008 [US1] Verify that `_setup_table_columns` correctly sets Interactive mode for all columns except "Nome" and that cursor changes to `SplitHCursor` on header borders in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: User Story 1 complete — columns are draggable with min width and correct cursor. "Nome" stays flexible.

---

## Phase 4: User Story 2 — Persistir larguras personalizadas entre sessoes (Priority: P2)

**Goal**: Salvar automaticamente as larguras personalizadas via QSettings e restaurar ao reabrir o aplicativo

**Independent Test**: Redimensionar colunas, fechar o aplicativo e reabrir para verificar que as larguras foram preservadas. Na primeira execucao, deve usar larguras padrao.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US2] Test `_save_column_widths` saves header state to QSettings group `"column_widths"` key `"header_state"` in `tests/unit/presentation/test_column_resize.py`
- [x] T010 [P] [US2] Test `_restore_column_widths` loads saved state from QSettings and applies via `restoreState()` in `tests/unit/presentation/test_column_resize.py`
- [x] T011 [P] [US2] Test that first launch (no saved state) applies default `COLUMN_WIDTHS` in `tests/unit/presentation/test_column_resize.py`

### Implementation for User Story 2

- [x] T012 [US2] Implement `_save_column_widths` method using `QHeaderView.saveState()` and QSettings in `src/backlog_manager/presentation/views/main_window.py`
- [x] T013 [US2] Connect `sectionResized` signal to `_save_column_widths` in `src/backlog_manager/presentation/views/main_window.py` method `_setup_table_columns`
- [x] T014 [US2] Implement `_restore_column_widths` method using `QHeaderView.restoreState()` from QSettings in `src/backlog_manager/presentation/views/main_window.py`
- [x] T015 [US2] Call `_restore_column_widths` at startup in `_setup_table_columns` — if no saved state exists, fall through to default `COLUMN_WIDTHS` in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: User Story 2 complete — widths persist between sessions. First launch uses defaults.

---

## Phase 5: User Story 3 — Restaurar larguras padrao (Priority: P3)

**Goal**: Oferecer opcao de restaurar larguras padrao via menu de contexto do cabecalho e auto-fit via duplo-clique

**Independent Test**: Redimensionar varias colunas, clicar direito no cabecalho e selecionar "Restaurar larguras padrao" — todas voltam ao original. Duplo-clique na borda ajusta ao conteudo.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T016 [P] [US3] Test that header has `CustomContextMenu` policy and context menu contains "Restaurar larguras padrão" action in `tests/unit/presentation/test_column_resize.py`
- [x] T017 [P] [US3] Test `_restore_default_widths` applies `COLUMN_WIDTHS` defaults and removes saved state from QSettings in `tests/unit/presentation/test_column_resize.py`
- [x] T018 [P] [US3] Test double-click on header border triggers `resizeSectionToContents` and saves state in `tests/unit/presentation/test_column_resize.py`

### Implementation for User Story 3

- [x] T019 [US3] Set `header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)` and connect `customContextMenuRequested` signal in `src/backlog_manager/presentation/views/main_window.py`
- [x] T020 [US3] Implement `_show_header_context_menu` method with "Restaurar larguras padrão" action in `src/backlog_manager/presentation/views/main_window.py`
- [x] T021 [US3] Implement `_restore_default_widths` method — apply `COLUMN_WIDTHS`, remove QSettings key, re-set Interactive modes in `src/backlog_manager/presentation/views/main_window.py`
- [x] T022 [US3] Connect `sectionDoubleClicked` signal to handler that calls `resizeSectionToContents(logicalIndex)` followed by `_save_column_widths` in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: All user stories complete — drag resize, persistence, restore defaults, and auto-fit all functional.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation and cleanup across all stories

- [x] T023 Run all tests in `tests/unit/presentation/test_column_resize.py` and fix any failures
- [x] T024 Run quickstart.md manual validation (drag, persist, double-click auto-fit, restore defaults)
- [x] T025 Verify edge cases: minimum width enforcement, "Nome" stays Stretch after restore, window resize responsivity with saved widths

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001 for constant) — BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (Phase 2) completion
- **User Story 2 (Phase 4)**: Depends on Foundational (Phase 2) — independent of US1
- **User Story 3 (Phase 5)**: Depends on US2 (uses `_save_column_widths` from T012)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) — Independent of US1
- **User Story 3 (P3)**: Depends on US2 (`_save_column_widths` method and `_restore_column_widths` pattern) — Cannot start until US2 is complete

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Signal connections after method implementations
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel (different files)
- T009, T010, T011 can run in parallel (independent test methods)
- T016, T017, T018 can run in parallel (independent test methods)
- US1 and US2 can start in parallel after Foundational phase (but both touch main_window.py — coordinate changes)

---

## Parallel Example: User Story 2

```bash
# Launch all tests for User Story 2 together:
Task: "Test _save_column_widths saves header state to QSettings" (T009)
Task: "Test _restore_column_widths loads saved state" (T010)
Task: "Test first launch applies default COLUMN_WIDTHS" (T011)
```

## Parallel Example: User Story 3

```bash
# Launch all tests for User Story 3 together:
Task: "Test context menu contains restore action" (T016)
Task: "Test _restore_default_widths applies defaults" (T017)
Task: "Test double-click triggers resizeSectionToContents" (T018)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T004)
3. Complete Phase 3: User Story 1 (T005-T008)
4. **STOP and VALIDATE**: Columns are draggable — test independently
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Columns draggable (foundation ready)
2. Add User Story 1 → Test drag resize → MVP!
3. Add User Story 2 → Test persistence → Widths survive restart
4. Add User Story 3 → Test restore + auto-fit → Full feature complete
5. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All implementation in 2 existing files (`main_window.py`, `story_table_model.py`) + 1 new test file
- QSettings persistence is synchronous — no async considerations
- `saveState()`/`restoreState()` is the idiomatic Qt approach (per research.md R2)
- Existing responsiveness logic (hide columns < 1024px) coexists with `saveState` (per research.md R5)
