# Tasks: Excel Import/Export GUI Integration

**Input**: Design documents from `/specs/012-excel-gui-integration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included per spec.md Test Scenarios section (pytest-qt tests)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and ExcelViewModel signal connections

- [X] T001 Add ExcelViewModel signal connections in src/backlog_manager/presentation/views/main_window.py
- [X] T002 Add internal state variables (_excel_operation_in_progress, _progress_dialog) to MainWindow in src/backlog_manager/presentation/views/main_window.py
- [X] T003 [P] Create test file skeleton at tests/integration/presentation/views/test_main_window_excel.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core helper methods that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T004 Implement _start_excel_operation helper method in src/backlog_manager/presentation/views/main_window.py
- [X] T005 Implement _end_excel_operation helper method in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Export Backlog to Excel via Toolbar (Priority: P1)

**Goal**: Users can export backlog data to Excel using a toolbar button

**Independent Test**: Click "Exportar Excel" button, select destination file, verify Excel file is created with backlog data

### Tests for User Story 1

- [X] T006 [P] [US1] Test toolbar has export button in tests/integration/presentation/views/test_main_window_excel.py
- [X] T007 [P] [US1] Test export button opens file save dialog in tests/integration/presentation/views/test_main_window_excel.py
- [X] T008 [P] [US1] Test success message after export in tests/integration/presentation/views/test_main_window_excel.py
- [X] T009 [P] [US1] Test overwrite confirmation on export in tests/integration/presentation/views/test_main_window_excel.py

### Implementation for User Story 1

- [X] T010 [US1] Add _action_export_excel QAction to toolbar in src/backlog_manager/presentation/views/main_window.py
- [X] T011 [US1] Implement _on_export_excel_clicked handler with file save dialog in src/backlog_manager/presentation/views/main_window.py
- [X] T012 [US1] Implement _on_export_completed signal handler in src/backlog_manager/presentation/views/main_window.py
- [X] T013 [US1] Implement _on_export_error signal handler in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: Export via toolbar button is fully functional and testable

---

## Phase 4: User Story 2 - Import Backlog from Excel via Toolbar (Priority: P1)

**Goal**: Users can import backlog data from Excel using a toolbar button

**Independent Test**: Click "Importar Excel" button, select a valid Excel file, verify stories are created in the system

### Tests for User Story 2

- [X] T014 [P] [US2] Test toolbar has import button in tests/integration/presentation/views/test_main_window_excel.py
- [X] T015 [P] [US2] Test import button opens file open dialog in tests/integration/presentation/views/test_main_window_excel.py
- [X] T016 [P] [US2] Test success message after import in tests/integration/presentation/views/test_main_window_excel.py
- [X] T017 [P] [US2] Test table refresh after import in tests/integration/presentation/views/test_main_window_excel.py

### Implementation for User Story 2

- [X] T018 [US2] Add _action_import_excel QAction to toolbar in src/backlog_manager/presentation/views/main_window.py
- [X] T019 [US2] Implement _on_import_excel_clicked handler with file open dialog in src/backlog_manager/presentation/views/main_window.py
- [X] T020 [US2] Implement _on_import_completed signal handler with table refresh in src/backlog_manager/presentation/views/main_window.py
- [X] T021 [US2] Implement _on_import_error signal handler in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: Import via toolbar button is fully functional and testable

---

## Phase 5: User Story 3 - Use Keyboard Shortcuts for Import/Export (Priority: P2)

**Goal**: Power users can use Ctrl+I for import and Ctrl+E for export

**Independent Test**: Press Ctrl+I and Ctrl+E in MainWindow, verify appropriate file dialogs open

### Tests for User Story 3

- [X] T022 [P] [US3] Test Ctrl+I shortcut triggers import handler in tests/integration/presentation/views/test_main_window_excel.py
- [X] T023 [P] [US3] Test Ctrl+E shortcut triggers export handler in tests/integration/presentation/views/test_main_window_excel.py
- [X] T024 [P] [US3] Test shortcuts are disabled during operation in tests/integration/presentation/views/test_main_window_excel.py

### Implementation for User Story 3

- [X] T025 [US3] Add Ctrl+I shortcut to _action_import_excel in src/backlog_manager/presentation/views/main_window.py
- [X] T026 [US3] Add Ctrl+E shortcut to _action_export_excel in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: Keyboard shortcuts work for import/export

---

## Phase 6: User Story 4 - Visual Feedback During Operations (Priority: P2)

**Goal**: Users see progress dialog and disabled buttons during operations

**Independent Test**: Import a file with 100+ stories and observe progress dialog during operation

### Tests for User Story 4

- [X] T027 [P] [US4] Test progress dialog shown on import in tests/integration/presentation/views/test_main_window_excel.py
- [X] T028 [P] [US4] Test progress dialog shown on export in tests/integration/presentation/views/test_main_window_excel.py
- [X] T029 [P] [US4] Test buttons disabled during operation in tests/integration/presentation/views/test_main_window_excel.py

### Implementation for User Story 4

- [X] T030 [US4] Ensure _start_excel_operation shows progress dialog with correct message
- [X] T031 [US4] Ensure _start_excel_operation disables import/export actions and sets wait cursor
- [X] T032 [US4] Ensure _end_excel_operation re-enables actions and restores cursor

**Checkpoint**: Visual feedback (progress dialog, disabled buttons, wait cursor) works during operations

---

## Phase 7: User Story 5 - Handle Import Errors Gracefully (Priority: P2)

**Goal**: Users see clear error messages when import fails

**Independent Test**: Import an Excel file with missing required columns, verify clear error message is displayed

### Tests for User Story 5

- [X] T033 [P] [US5] Test error message on import failure in tests/integration/presentation/views/test_main_window_excel.py
- [X] T034 [P] [US5] Test error dialog shows descriptive message in tests/integration/presentation/views/test_main_window_excel.py

### Implementation for User Story 5

- [X] T035 [US5] Ensure _on_import_error displays error from ExcelViewModel in QMessageBox.critical
- [X] T036 [US5] Ensure _on_export_error displays error from ExcelViewModel in QMessageBox.critical

**Checkpoint**: Error handling shows clear, user-friendly messages

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and integration testing

- [X] T037 [P] Integration test for full import flow end-to-end in tests/integration/presentation/views/test_main_window_excel.py
- [X] T038 [P] Integration test for full export flow end-to-end in tests/integration/presentation/views/test_main_window_excel.py
- [X] T039 Run quickstart.md validation (manual test per quickstart.md instructions)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - US1 (Export) and US2 (Import) are P1 and can proceed in parallel
  - US3 (Shortcuts) builds on US1 and US2 actions
  - US4 (Visual Feedback) validates helper methods from Phase 2
  - US5 (Error Handling) depends on signal handlers from US1/US2
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P2)**: Depends on US1 and US2 actions being created (T010, T018)
- **User Story 4 (P2)**: Can start after Foundational - validates helper methods
- **User Story 5 (P2)**: Depends on US1/US2 signal handlers (T012, T013, T020, T021)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Implementation in logical order within story

### Parallel Opportunities

- T003 can run in parallel with T001-T002
- T004 and T005 can run in parallel (different methods)
- All tests marked [P] within a user story can run in parallel
- US1 and US2 can be worked on in parallel after Foundational phase
- All integration tests in Phase 8 can run in parallel

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Test toolbar has export button in tests/integration/presentation/views/test_main_window_excel.py"
Task: "Test export button opens file save dialog in tests/integration/presentation/views/test_main_window_excel.py"
Task: "Test success message after export in tests/integration/presentation/views/test_main_window_excel.py"
Task: "Test overwrite confirmation on export in tests/integration/presentation/views/test_main_window_excel.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Export)
4. Complete Phase 4: User Story 2 (Import)
5. **STOP and VALIDATE**: Test export/import independently
6. Deploy/demo if ready - basic import/export functionality is complete

### Incremental Delivery

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 (Export) -> Test independently -> Deploy/Demo (export only)
3. Add User Story 2 (Import) -> Test independently -> Deploy/Demo (full MVP!)
4. Add User Story 3 (Shortcuts) -> Test independently -> Deploy/Demo
5. Add User Story 4 (Visual Feedback) -> Test independently -> Deploy/Demo
6. Add User Story 5 (Error Handling) -> Test independently -> Deploy/Demo
7. Complete Polish phase -> Final validation

---

## Notes

- All implementation is in a single file: `src/backlog_manager/presentation/views/main_window.py`
- All tests are in a single file: `tests/integration/presentation/views/test_main_window_excel.py`
- ExcelViewModel with signals already exists from EP-009
- DIContainer.excel_viewmodel property already exists from EP-009
- Follow existing patterns from research.md for toolbar actions and async operations
- Messages must be in Portuguese per Constitution principle XV
- Commit after each task or logical group
