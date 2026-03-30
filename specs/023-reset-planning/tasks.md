# Tasks: Novo Planejamento (Reset de Cronograma e Alocacao)

**Input**: Design documents from `/specs/023-reset-planning/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contract.md

**Tests**: Included per spec.md test specifications.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and package init files for the planning feature

- [X] T001 Create planning DTO package directory with `src/backlog_manager/application/dto/planning/__init__.py`
- [X] T002 [P] Create planning use cases package directory with `src/backlog_manager/application/use_cases/planning/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: DTOs and icon asset shared by all user stories

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Create ResetPlanningInputDTO, ResetPlanningOutputDTO, and CountAffectedStoriesOutputDTO in `src/backlog_manager/application/dto/planning/reset_planning_dto.py`
- [X] T004 [P] Create arrows-down-up.svg icon (Phosphor Icons style) in `src/backlog_manager/assets/icons/arrows-down-up.svg`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Resetar Planejamento Completo (Priority: P1) MVP

**Goal**: Implement the core atomic reset operation that clears calculated fields (duration, start_date, end_date, developer_id) from all affected stories while preserving user data, status, and dependencies.

**Independent Test**: Create stories with planning data, execute ResetPlanningUseCase, verify calculated fields are None and user data is intact.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T005 [P] [US1] Write test_reset_planning_clears_calculated_fields in `tests/unit/application/use_cases/planning/test_reset_planning.py`
- [X] T006 [P] [US1] Write test_reset_planning_preserves_user_data in `tests/unit/application/use_cases/planning/test_reset_planning.py`
- [X] T007 [P] [US1] Write test_reset_planning_preserves_dependencies in `tests/unit/application/use_cases/planning/test_reset_planning.py`
- [X] T008 [P] [US1] Write test_reset_planning_preserves_status in `tests/unit/application/use_cases/planning/test_reset_planning.py`
- [X] T009 [P] [US1] Write test_reset_planning_atomic_on_failure in `tests/unit/application/use_cases/planning/test_reset_planning.py`
- [X] T010 [P] [US1] Write test_reset_planning_empty_backlog in `tests/unit/application/use_cases/planning/test_reset_planning.py`
- [X] T011 [P] [US1] Write test_reset_planning_no_planning_data in `tests/unit/application/use_cases/planning/test_reset_planning.py`
- [X] T012 [P] [US1] Write test_reset_planning_partial_data (only developer_id or only dates) in `tests/unit/application/use_cases/planning/test_reset_planning.py`

### Implementation for User Story 1

- [X] T013 [US1] Implement ResetPlanningUseCase in `src/backlog_manager/application/use_cases/planning/reset_planning.py` — fetch all stories via UoW repository, filter stories with any calculated field filled, clear duration/start_date/end_date/developer_id using `object.__setattr__()`, persist via repository.update() atomically, return ResetPlanningOutputDTO

**Checkpoint**: ResetPlanningUseCase works and all US1 unit tests pass

---

## Phase 4: User Story 2 - Confirmacao com Preview antes do Reset (Priority: P2)

**Goal**: Implement the count/preview use case and confirmation dialog that shows affected story counts before executing the reset.

**Independent Test**: Verify CountAffectedStoriesUseCase returns correct counts. Verify dialog displays counts and cancel closes without modification.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T014 [P] [US2] Write test_count_affected_stories (total, with_dates, with_developer counts) in `tests/unit/application/use_cases/planning/test_count_affected_stories.py`
- [X] T015 [P] [US2] Write test_confirm_dialog_shows_count in `tests/unit/presentation/views/test_confirm_reset_dialog.py`
- [X] T016 [P] [US2] Write test_confirm_dialog_cancel_default (Cancel button has initial focus) in `tests/unit/presentation/views/test_confirm_reset_dialog.py`

### Implementation for User Story 2

- [X] T017 [US2] Implement CountAffectedStoriesUseCase in `src/backlog_manager/application/use_cases/planning/count_affected_stories.py` — fetch stories via UoW repository, count total affected / with_dates / with_developer, return CountAffectedStoriesOutputDTO without modifying data
- [X] T018 [US2] Create ConfirmResetDialog in `src/backlog_manager/presentation/views/confirm_reset_dialog.py` — modal QDialog following ConfirmDeleteDialog pattern, warning-triangle.svg icon, display "{N} historias terao datas e duracoes removidas" and "{M} historias terao desenvolvedores desalocados", Cancel button with default focus, Confirm button with destructive/error color style

**Checkpoint**: CountAffectedStoriesUseCase returns correct counts, dialog renders correctly with cancel as default

---

## Phase 5: User Story 3 - Feedback Visual apos Reset (Priority: P3)

**Goal**: Implement the ViewModel with signals and status bar integration so the UI updates after a reset: table reloads, status bar shows temporary message, last allocation info is cleared.

**Independent Test**: Execute reset via ViewModel, verify reset_started/reset_completed signals emit, verify status bar shows temporary message and clears last allocation.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T019 [P] [US3] Write test_reset_planning_viewmodel_signals (reset_started, reset_completed emitted) in `tests/unit/presentation/viewmodels/test_reset_planning_viewmodel.py`
- [X] T020 [P] [US3] Write test_reset_planning_viewmodel_error_signal (reset_error emitted on failure) in `tests/unit/presentation/viewmodels/test_reset_planning_viewmodel.py`
- [X] T021 [P] [US3] Write test_status_bar_updated_after_reset (temporary message shown, last allocation cleared) in `tests/unit/presentation/viewmodels/test_reset_planning_viewmodel.py`

### Implementation for User Story 3

- [X] T022 [US3] Implement ResetPlanningViewModel in `src/backlog_manager/presentation/viewmodels/reset_planning_viewmodel.py` — signals: reset_started, reset_completed(object), reset_error(str); property: is_running; method preview() using CountAffectedStoriesUseCase; method execute() using ResetPlanningUseCase with async pattern matching ScheduleViewModel
- [X] T023 [US3] Modify StatusBarViewModel in `src/backlog_manager/presentation/viewmodels/status_bar_viewmodel.py` — add method to clear last allocation info and show temporary reset message "Planejamento resetado: {N} historias" for 5 seconds via QTimer.singleShot

**Checkpoint**: ViewModel emits correct signals, status bar shows temporary message and clears last allocation

---

## Phase 6: User Story 4 - Botao Desabilitado e Integracao MainWindow (Priority: P3)

**Goal**: Wire everything into MainWindow: create the QAction with icon/shortcut/tooltip, add to menu Ferramentas and Toolbar, implement the async handler connecting dialog + viewmodel + status bar, and manage enabled/disabled state based on stories loaded / operation running / planning data exists.

**Independent Test**: Verify button is disabled with no stories, during operations, and with no planning data. Verify button enables after schedule calculation.

### Tests for User Story 4

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T024 [P] [US4] Write test_button_disabled_during_operation in `tests/e2e/test_ep023_reset_planning.py`
- [X] T025 [P] [US4] Write test_button_disabled_no_planning_data in `tests/e2e/test_ep023_reset_planning.py`
- [X] T026 [P] [US4] Write test_button_enabled_after_schedule in `tests/e2e/test_ep023_reset_planning.py`

### Implementation for User Story 4

- [X] T027 [US4] Register use cases and ViewModel in DI container in `src/backlog_manager/presentation/container.py` — add factory methods create_reset_planning_use_case(uow), create_count_affected_stories_use_case(uow), and lazy property reset_planning_viewmodel
- [X] T028 [US4] Add _new_planning_action QAction to MainWindow in `src/backlog_manager/presentation/views/main_window.py` — icon arrows-down-up.svg, shortcut Ctrl+Shift+N, tooltip per UI contract, add to Ferramentas menu before "Calcular Cronograma", add to Toolbar group 4 before "Cronograma" button
- [X] T029 [US4] Implement _on_new_planning() async handler in `src/backlog_manager/presentation/views/main_window.py` — call preview() to get counts, show ConfirmResetDialog, on confirm call execute(), connect reset_completed signal to reload table + update status bar + set _has_planning_data=False, connect reset_error signal to show error message
- [X] T030 [US4] Implement _has_planning_data tracking and _update_actions_state() integration in `src/backlog_manager/presentation/views/main_window.py` — track _has_planning_data flag; on load_stories() completion set flag by checking if any story has duration/start_date/end_date/developer_id not None; set True on schedule_completed / allocation_completed signals; set False on reset_completed signal; disable _new_planning_action when no stories or loading or _has_planning_data is False

**Checkpoint**: Full feature works end-to-end: button state correct, dialog shows counts, reset executes, UI updates

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: E2E tests covering the full flow and cross-story validation

- [X] T031 [P] Write E2E test for full reset flow (load stories -> schedule -> reset -> verify) in `tests/e2e/test_ep023_reset_planning.py`
- [X] T032 [P] Write E2E test for cancel flow (dialog cancel preserves data) in `tests/e2e/test_ep023_reset_planning.py`
- [X] T033 [P] Write E2E test for double reset (second reset shows 0 affected, button disabled) in `tests/e2e/test_ep023_reset_planning.py`
- [X] T034 Run full regression test suite to verify no regressions: `pytest tests/ -v`
- [X] T035 Run quickstart.md validation steps manually

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational (Phase 2) - core reset logic
- **US2 (Phase 4)**: Depends on Foundational (Phase 2) - can run in parallel with US1
- **US3 (Phase 5)**: Depends on US1 (Phase 3) and US2 (Phase 4) - ViewModel uses both use cases
- **US4 (Phase 6)**: Depends on US2 (Phase 4) and US3 (Phase 5) - MainWindow wires everything
- **Polish (Phase 7)**: Depends on US4 (Phase 6) completion

### User Story Dependencies

- **US1 (P1)**: Can start after Foundational - No dependencies on other stories
- **US2 (P2)**: Can start after Foundational - No dependencies on other stories. **Can run in parallel with US1**
- **US3 (P3)**: Depends on US1 and US2 (ViewModel uses both ResetPlanningUseCase and CountAffectedStoriesUseCase)
- **US4 (P3)**: Depends on US3 (MainWindow needs ViewModel) and US2 (needs ConfirmResetDialog)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Use cases before ViewModels
- ViewModels before Views
- Core implementation before integration

### Parallel Opportunities

- T001 and T002 (Setup) can run in parallel
- T003 and T004 (Foundational) can run in parallel
- All US1 tests (T005-T012) can run in parallel
- US1 and US2 can be implemented in parallel after Foundational
- All US2 tests (T014-T016) can run in parallel
- All US3 tests (T019-T021) can run in parallel
- All US4 tests (T024-T026) can run in parallel
- All E2E tests (T031-T033) can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all US1 tests together (they all go in the same file):
Task T005-T012: All unit tests for ResetPlanningUseCase in tests/unit/application/use_cases/planning/test_reset_planning.py

# After tests fail, implement:
Task T013: ResetPlanningUseCase in src/backlog_manager/application/use_cases/planning/reset_planning.py
```

## Parallel Example: User Stories 1 + 2

```bash
# After Foundational phase, launch in parallel:
# Stream A (US1): T005-T012 tests -> T013 implementation
# Stream B (US2): T014-T016 tests -> T017 CountUseCase -> T018 Dialog
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002)
2. Complete Phase 2: Foundational (T003-T004)
3. Complete Phase 3: User Story 1 (T005-T013)
4. **STOP and VALIDATE**: Run unit tests for ResetPlanningUseCase
5. Core reset logic works at the use case level

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. US1 (Reset logic) -> Test at use case level (MVP!)
3. US2 (Preview + Dialog) -> Test dialog rendering and counts
4. US3 (ViewModel + Status bar) -> Test signal emission and feedback
5. US4 (MainWindow integration) -> Full feature works end-to-end
6. Polish (E2E + regression) -> Ship-ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Pattern references: ScheduleViewModel, ConfirmDeleteDialog, calculate_schedule.py (see plan.md Key Patterns)
- Use `object.__setattr__()` for Story field mutation (R-001)
- Use SQLiteUnitOfWork for atomicity (R-002)
- Track _has_planning_data as sync flag to avoid async in _update_actions_state (R-005)
- Temporary message via QTimer.singleShot(5000, ...) (R-006)
