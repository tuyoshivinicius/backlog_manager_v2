# Tasks: Velocidade em SP/Sprint e DatePicker Reutilizavel

**Input**: Design documents from `/specs/029-velocity-sprint-datepicker/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contracts.md, quickstart.md

**Tests**: Included — plan.md explicitly lists test files in project structure (Constitution XIV. Testes ✅ PASS).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `src/backlog_manager/`
- **Tests**: `tests/`

---

## Phase 1: Setup

**Purpose**: No new project setup needed — project already exists with all dependencies (PySide6, qasync, Pydantic, pytest-qt). This phase is a no-op.

**Checkpoint**: Ready for user story implementation.

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No blocking foundational tasks. All changes are scoped to Presentation layer on existing files. User stories can begin immediately.

**Checkpoint**: Foundation ready — user story implementation can begin.

---

## Phase 3: User Story 1 — Configurar Velocidade em SP/Sprint (Priority: P1) 🎯 MVP

**Goal**: Substituir campo de velocidade SP/dia por dois campos (SP/Sprint + Dias Uteis por Sprint) no ConfigDialog e ConfigPanel, com label derivada "= X.X SP/dia" atualizada dinamicamente.

**Independent Test**: Abrir ConfigDialog, preencher SP/Sprint e dias uteis, verificar label derivada, aplicar, e confirmar que alocacao automatica calcula duracoes corretamente com velocity_per_day derivada.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T001 [US1] Add unit tests for sp_per_sprint, workdays_per_sprint properties and velocity_per_day derivation in tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py
- [X] T002 [US1] Add unit tests for validation rules (sp_per_sprint range 1-100, workdays_per_sprint range 1-30, division by zero protection) in tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py

### Implementation for User Story 1

- [X] T003 [US1] Add _sp_per_sprint (int, default 20) and _workdays_per_sprint (int, default 10) fields with properties and velocity_per_day derived property to src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py
- [X] T004 [US1] Add validation rules for sp_per_sprint (1-100) and workdays_per_sprint (1-30) in src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py
- [X] T005 [US1] Replace velocity QDoubleSpinBox with SP/Sprint QSpinBox (range 1-100, suffix " SP/Sprint"), Dias Uteis QSpinBox (range 1-30, suffix " dias"), and derived QLabel ("= X.X SP/dia") in src/backlog_manager/presentation/views/config_dialog.py
- [X] T006 [US1] Connect valueChanged signals of both QSpinBox to update derived label dynamically and wire _on_apply to pass velocity_per_day (sp_per_sprint / workdays_per_sprint) to ViewModel in src/backlog_manager/presentation/views/config_dialog.py
- [X] T007 [US1] Replace velocity QDoubleSpinBox with SP/Sprint QSpinBox, Dias Uteis QSpinBox, and derived QLabel in ConfigPanel; add sp_per_sprint/workdays_per_sprint properties and keep velocity property as derived (retrocompatibility) in src/backlog_manager/presentation/views/config_panel.py

**Checkpoint**: User Story 1 fully functional — ConfigDialog and ConfigPanel show SP/Sprint fields with derived velocity label. ViewModel calculates velocity_per_day correctly.

---

## Phase 4: User Story 2 — Persistencia e Migracao de Velocidade (Priority: P2)

**Goal**: Persistir sp_per_sprint e workdays_per_sprint via QSettings e tratar migracao de configuracoes legadas (velocity em SP/dia) com defaults seguros.

**Independent Test**: Configurar valores, fechar e reabrir dialog, verificar restauracao. Simular QSettings legado (apenas "velocity") e verificar defaults seguros sem crash.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T008 [US2] Add unit tests for QSettings persistence (save/load sp_per_sprint, workdays_per_sprint) in tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py
- [X] T009 [US2] Add unit tests for migration scenarios (empty QSettings → defaults, legacy velocity only → defaults, current format → load values) in tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py

### Implementation for User Story 2

- [X] T010 [US2] Implement _save_to_qsettings to persist sp_per_sprint and workdays_per_sprint in allocation group (do NOT write legacy velocity field) in src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py
- [X] T011 [US2] Implement _load_from_qsettings with migration logic: if sp_per_sprint exists load both fields, else use defaults (20, 10) regardless of legacy velocity value in src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py
- [X] T012 [US2] Wire ConfigDialog to load persisted values from ViewModel on open and populate SP/Sprint and workdays QSpinBox fields in src/backlog_manager/presentation/views/config_dialog.py

**Checkpoint**: User Story 2 complete — values persist across sessions, migration from legacy QSettings works with safe defaults.

---

## Phase 5: User Story 3 — DatePicker Reutilizavel (Priority: P3)

**Goal**: Criar componente DatePicker reutilizavel (subclasse QDateEdit) com estilizacao Design System e substituir QDateEdit inline em ConfigDialog, ConfigPanel e ManualAllocationDialog.

**Independent Test**: Abrir ConfigDialog e ManualAllocationDialog, interagir com campos de data, verificar calendar popup, formato dd/MM/yyyy, restricoes min/max date e estilizacao consistente.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T013 [US3] Create pytest-qt tests for DatePicker: init defaults, display format, calendar popup, min/max date constraints, date_changed signal emission, get_date/set_date methods, and Design System styling in tests/integration/presentation/views/test_date_picker.py

### Implementation for User Story 3

- [X] T014 [US3] Create DatePicker(QDateEdit) component with: calendar_popup=True, display_format="dd/MM/yyyy", optional min_date/max_date, date_changed Signal(object) emitting datetime.date, get_date/set_date methods, and DESIGN_TOKENS styling in src/backlog_manager/presentation/views/date_picker.py
- [X] T015 [US3] Replace QDateEdit inline for start_date field with DatePicker component in src/backlog_manager/presentation/views/config_dialog.py
- [X] T016 [P] [US3] Replace QDateEdit inline for start_date field with DatePicker component in src/backlog_manager/presentation/views/config_panel.py
- [X] T017 [P] [US3] Replace QDateEdit inline for date fields with DatePicker component (with min_date for next business day) in src/backlog_manager/presentation/views/manual_allocation_dialog.py

**Checkpoint**: All date fields use DatePicker with consistent Design System styling. Behavior identical to previous QDateEdit but visually unified.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validation, edge cases, and final verification across all stories.

- [X] T018 Verify edge cases: SP/Sprint=1 with workdays=15 (velocity=0.067), extreme values produce correct allocation durations
- [X] T019 Run quickstart.md validation — execute all manual test scenarios from specs/029-velocity-sprint-datepicker/quickstart.md
- [X] T020 Run full test suite (poetry run pytest -v) and verify no regressions

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No-op — project already configured
- **Foundational (Phase 2)**: No-op — no blocking prerequisites
- **US1 (Phase 3)**: Can start immediately — core velocity logic
- **US2 (Phase 4)**: Depends on US1 (T003-T004 must exist before persistence logic)
- **US3 (Phase 5)**: Independent of US1/US2 — can run in parallel after T014 (DatePicker created)
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **US1 (P1)**: No dependencies — start immediately
- **US2 (P2)**: Depends on US1 ViewModel fields (T003, T004) existing
- **US3 (P3)**: Independent — DatePicker is a new component with no dependency on velocity changes

### Within Each User Story

- Tests FIRST (write, verify they FAIL)
- ViewModel logic before View UI changes
- Core implementation before integration

### Parallel Opportunities

- **US1 + US3**: Can run in parallel (different concerns, different files except config_dialog.py)
  - Recommendation: complete US1 first on config_dialog.py, then US3 modifies same file
- **T016 + T017**: DatePicker integration into ConfigPanel and ManualAllocationDialog are parallel (different files)
- **T001 + T002**: US1 test tasks target same file but different test classes — can be written together
- **T008 + T009**: US2 test tasks target same file — write together

---

## Parallel Example: User Story 3

```bash
# After T014 (DatePicker created), launch integrations in parallel:
Task T016: "Replace QDateEdit in config_panel.py"
Task T017: "Replace QDateEdit in manual_allocation_dialog.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 3: User Story 1 (T001-T007)
2. **STOP and VALIDATE**: ConfigDialog/ConfigPanel show SP/Sprint, derived label works
3. This alone delivers the core value — natural velocity input for agile teams

### Incremental Delivery

1. Add User Story 1 → Test SP/Sprint configuration → MVP ready
2. Add User Story 2 → Test persistence/migration → Values survive app restart
3. Add User Story 3 → Test DatePicker integration → Consistent visual styling
4. Polish → Edge cases, full regression suite

---

## Notes

- All changes confined to Presentation layer (Constitution I. Clean Architecture ✅)
- Domain (AllocationConfig, SchedulingService) receives velocity_per_day (float) unchanged
- ConfigPanel.velocity property maintained for retrocompatibility (R-007)
- QSettings migration uses safe defaults (20 SP/Sprint, 10 days) — no conversion from legacy velocity (R-003)
- DatePicker subclasses QDateEdit (not wrapper) per research decision R-004
