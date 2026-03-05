# Tasks: Schedule Calculation GUI Integration

**Input**: Design documents from `/specs/013-schedule-gui-integration/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Not explicitly requested in spec.md - excluded from task list.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3, US4)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No setup required - all infrastructure exists

This feature builds on existing infrastructure (DIContainer, MainWindow, use cases). No new setup tasks required.

**Checkpoint**: Setup phase complete - proceed to Foundational

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core ViewModel that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T001 Create ScheduleViewModel with signals in src/backlog_manager/presentation/viewmodels/schedule_viewmodel.py
- [X] T002 Add schedule_viewmodel property to DIContainer in src/backlog_manager/presentation/container.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Calculate Schedule via Toolbar Button (Priority: P1) MVP

**Goal**: Enable users to calculate schedule dates for all backlog stories by clicking a toolbar button

**Independent Test**: Click "Calcular Cronograma" button with valid configuration and verify stories receive calculated dates

### Implementation for User Story 1

- [X] T003 [US1] Add _action_schedule toolbar action with icon in src/backlog_manager/presentation/views/main_window.py
- [X] T004 [US1] Implement _on_calculate_schedule() handler in src/backlog_manager/presentation/views/main_window.py
- [X] T005 [US1] Implement _execute_schedule_calculation() async method in src/backlog_manager/presentation/views/main_window.py
- [X] T006 [US1] Implement _on_schedule_started() signal handler in src/backlog_manager/presentation/views/main_window.py
- [X] T007 [US1] Implement _on_schedule_completed() signal handler with success dialog in src/backlog_manager/presentation/views/main_window.py
- [X] T008 [US1] Connect ScheduleViewModel signals in _setup_signals() in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: User Story 1 complete - toolbar button triggers schedule calculation with success dialog

---

## Phase 4: User Story 2 - Calculate Schedule via Keyboard Shortcut (Priority: P2)

**Goal**: Enable power users to trigger schedule calculation using Ctrl+Shift+C

**Independent Test**: Press Ctrl+Shift+C with application focus and verify schedule calculation executes

### Implementation for User Story 2

- [X] T009 [US2] Add QKeySequence("Ctrl+Shift+C") shortcut to _action_schedule in src/backlog_manager/presentation/views/main_window.py
- [X] T010 [US2] Update tooltip to show keyboard shortcut in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: User Story 2 complete - keyboard shortcut works alongside button

---

## Phase 5: User Story 3 - Receive Clear Feedback on Errors (Priority: P3)

**Goal**: Display clear Portuguese error messages when schedule calculation fails

**Independent Test**: Trigger errors (invalid config, cyclic dependencies) and verify appropriate error dialogs appear

### Implementation for User Story 3

- [X] T011 [US3] Handle CyclicDependencyException in ScheduleViewModel.execute() with Portuguese message in src/backlog_manager/presentation/viewmodels/schedule_viewmodel.py
- [X] T012 [US3] Add validation check before execution in _on_calculate_schedule() using ConfigPanel.validate() in src/backlog_manager/presentation/views/main_window.py
- [X] T013 [US3] Connect schedule_error signal to _on_error handler in _setup_signals() in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: User Story 3 complete - errors display user-friendly Portuguese messages

---

## Phase 6: User Story 4 - View Updated Dates in Table (Priority: P2)

**Goal**: Automatically refresh backlog table after schedule calculation completes

**Independent Test**: Calculate schedule and verify table displays updated start_date and end_date columns

### Implementation for User Story 4

- [X] T014 [US4] Add load_stories() call after schedule completion in _execute_schedule_calculation() in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: User Story 4 complete - table refreshes automatically after calculation

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T015 Run quickstart.md manual validation (add stories, set config, click button, verify dates)
- [X] T016 Verify existing tests pass with new code (python -m pytest tests/ -v)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No tasks - existing infrastructure
- **Foundational (Phase 2)**: No dependencies - can start immediately
- **User Stories (Phase 3-6)**: All depend on Foundational phase completion
  - US1 (P1): Can start after Phase 2
  - US2 (P2): Can start after T003 (toolbar action created)
  - US3 (P3): Can start after T001 (ScheduleViewModel created)
  - US4 (P2): Can start after T005 (_execute_schedule_calculation created)
- **Polish (Phase 7)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Depends on T001, T002 (Foundational) - Core functionality
- **User Story 2 (P2)**: Depends on T003 (toolbar action) - Extends button with shortcut
- **User Story 3 (P3)**: Depends on T001 (ViewModel) - Error handling in ViewModel and View
- **User Story 4 (P2)**: Depends on T005 (async method) - Table refresh after calculation

### Within Each Phase

- Foundational: T001 before T002 (ViewModel must exist before adding to container)
- US1: T003 first (action), then T004-T008 sequentially (handlers depend on action)
- US2: T009, T010 can run together (both modify action properties)
- US3: T011 before T012, T013 (ViewModel error handling enables View handling)
- US4: T014 standalone (single modification)

### Parallel Opportunities

- Phase 2: T001 and T002 must be sequential
- Phase 3-6: User stories have limited parallelism due to file conflicts in main_window.py
- T011 (ViewModel) can run parallel with T012, T013 (different files)

---

## Parallel Example: Foundational + US3

```bash
# After T002 completes, can run in parallel:
Task: T011 - Handle CyclicDependencyException in ScheduleViewModel (viewmodel file)
Task: T012 - Add validation check in _on_calculate_schedule (main_window file)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 2: Foundational (T001-T002)
2. Complete Phase 3: User Story 1 (T003-T008)
3. **STOP and VALIDATE**: Test button click triggers calculation and shows success dialog
4. Deploy/demo if ready

### Incremental Delivery

1. Complete Foundational + US1 -> MVP: Button works with success feedback
2. Add US2 (T009-T010) -> Enhancement: Keyboard shortcut works
3. Add US3 (T011-T013) -> Enhancement: Error handling complete
4. Add US4 (T014) -> Enhancement: Table auto-refresh
5. Complete Polish (T015-T016) -> Final validation

### Recommended Execution Order

Given file conflicts in main_window.py, recommended sequential order:

1. T001, T002 (Foundational)
2. T003, T004, T005, T006, T007, T008 (US1 - complete)
3. T009, T010 (US2 - shortcut)
4. T011 (US3 - ViewModel error handling)
5. T012, T013 (US3 - View error handling)
6. T014 (US4 - table refresh)
7. T015, T016 (Polish)

---

## Notes

- All user stories modify src/backlog_manager/presentation/views/main_window.py - limited parallelism
- ScheduleViewModel follows AllocationViewModel pattern exactly (see research.md)
- Error messages in Portuguese without accents per project convention
- Keyboard shortcut Ctrl+Shift+C does not conflict with existing shortcuts
- Toolbar button positioned before "Alocar Automaticamente" per workflow order
