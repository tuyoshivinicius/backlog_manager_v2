# Tasks: EP-009 Excel Integration

**Input**: Design documents from `/specs/009-ep009-excel-integration/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests are included per Test Scenarios section of spec.md (Unit and Integration tests).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependency installation, and basic structure creation

- [x] T001 Add openpyxl ^3.1.0 to pyproject.toml dependencies
- [x] T002 Run poetry install to update lock file and install openpyxl
- [x] T003 [P] Create src/backlog_manager/application/dto/excel/__init__.py
- [x] T004 [P] Create src/backlog_manager/application/use_cases/excel/__init__.py
- [x] T005 [P] Create src/backlog_manager/infrastructure/excel/__init__.py
- [x] T006 [P] Create tests/unit/application/use_cases/excel/__init__.py
- [x] T007 [P] Create tests/integration/infrastructure/excel/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**Critical**: No user story work can begin until this phase is complete

### DTOs (No Dependencies)

- [x] T008 [P] Implement ExcelReadResult dataclass in src/backlog_manager/application/dto/excel/import_excel_dto.py
- [x] T009 [P] Implement ImportExcelInputDTO with Pydantic validation in src/backlog_manager/application/dto/excel/import_excel_dto.py
- [x] T010 [P] Implement ImportExcelOutputDTO with success property in src/backlog_manager/application/dto/excel/import_excel_dto.py
- [x] T011 [P] Implement ExcelExportData dataclass in src/backlog_manager/application/dto/excel/export_excel_dto.py
- [x] T012 [P] Implement ExportExcelInputDTO with Pydantic validation in src/backlog_manager/application/dto/excel/export_excel_dto.py
- [x] T013 [P] Implement ExportExcelOutputDTO in src/backlog_manager/application/dto/excel/export_excel_dto.py

### Exception Hierarchy

- [x] T014 Add ExcelException base class in src/backlog_manager/application/exceptions/excel_exceptions.py (extends BacklogManagerException)
- [x] T015 [P] Add ExcelFileNotFoundException in src/backlog_manager/application/exceptions/excel_exceptions.py
- [x] T016 [P] Add ExcelFileCorruptedException in src/backlog_manager/application/exceptions/excel_exceptions.py
- [x] T017 [P] Add ExcelMissingHeaderException in src/backlog_manager/application/exceptions/excel_exceptions.py
- [x] T018 [P] Add ExcelCycleDetectedException in src/backlog_manager/application/exceptions/excel_exceptions.py
- [x] T019 [P] Add ExcelPermissionException in src/backlog_manager/application/exceptions/excel_exceptions.py

### Protocol Interface (Depends on DTOs)

- [x] T020 Implement ExcelServiceProtocol in src/backlog_manager/application/interfaces/excel_service.py per contracts/excel_service_protocol.md

### Infrastructure ExcelService (Depends on Protocol, DTOs, Exceptions)

- [x] T021 Implement ExcelService._read_stories_sync method for openpyxl reading in src/backlog_manager/infrastructure/excel/excel_service.py
- [x] T022 Implement ExcelService.read_stories_from_file async wrapper with asyncio.to_thread in src/backlog_manager/infrastructure/excel/excel_service.py
- [x] T023 [P] Implement ExcelService._write_workbook_sync method for openpyxl writing in src/backlog_manager/infrastructure/excel/excel_service.py
- [x] T024 [P] Implement ExcelService.write_workbook async wrapper with asyncio.to_thread in src/backlog_manager/infrastructure/excel/excel_service.py
- [x] T025 [P] Implement ExcelService._write_sheet helper method in src/backlog_manager/infrastructure/excel/excel_service.py
- [x] T026 Add REQUIRED_HEADERS constant and header validation in src/backlog_manager/infrastructure/excel/excel_service.py
- [x] T027 Add logging (INFO/ERROR) to ExcelService per FR-124-126 in src/backlog_manager/infrastructure/excel/excel_service.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Importar Backlog Completo do Excel (Priority: P1) MVP

**Goal**: Allow Scrum Master to import an existing backlog from Excel file without manual re-entry

**Independent Test**: Create Excel file with expected format (headers row 1: ID, Componente, Nome, SP, Feature, Dependencias), import it, verify all stories created correctly

### Unit Tests for User Story 1

- [x] T028 [P] [US1] Create test_import_excel_use_case.py in tests/unit/application/use_cases/excel/
- [x] T029 [P] [US1] Implement test_import_valid_file - import valid file creates all stories
- [x] T030 [P] [US1] Implement test_import_auto_generate_id - line without ID generates COMPONENTE-NNN format
- [x] T031 [P] [US1] Implement test_import_create_feature - non-existent Feature auto-created with wave=1
- [x] T032 [P] [US1] Implement test_import_dependencies_second_pass - dependencies created after all stories
- [x] T033 [P] [US1] Implement test_import_empty_file - empty file returns output with zero counts
- [x] T033a [P] [US1] Implement test_import_skip_existing_id - existing ID in database generates warning "ID '[ID]' ja existe" and skips row per FR-032

### Integration Tests for User Story 1

- [x] T034 [P] [US1] Create test_excel_service.py in tests/integration/infrastructure/excel/
- [x] T035 [P] [US1] Implement test_excel_service_read_valid_file - read valid file returns correct data
- [x] T036 [P] [US1] Implement test_excel_service_read_missing_file - missing file raises ExcelFileNotFoundException
- [x] T037 [P] [US1] Implement test_excel_service_read_corrupted_file - corrupted file raises ExcelFileCorruptedException

### Implementation for User Story 1

- [x] T038 [US1] Implement ImportExcelUseCase.__init__ with UoW, ExcelService, progress_callback in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T039 [US1] Implement ImportExcelUseCase._process_pass_one - create stories and features in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T040 [US1] Implement ImportExcelUseCase._generate_id_if_needed using StoryService.generate_story_id in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T041 [US1] Implement ImportExcelUseCase._create_feature_if_needed with wave=1 default in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T042 [US1] Implement ImportExcelUseCase._process_pass_two - create dependencies after cycle validation in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T043 [US1] Implement ImportExcelUseCase._parse_dependencies for semicolon-separated IDs in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T044 [US1] Implement ImportExcelUseCase.execute coordinating both passes in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T045 [US1] Add logging (INFO at start/end, WARNING for skipped rows) per FR-120-123 in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py

**Checkpoint**: User Story 1 complete - import functionality works with valid files

---

## Phase 4: User Story 2 - Validar Arquivo Excel na Importacao (Priority: P1)

**Goal**: Validate Excel file before import to prevent data corruption from malformed files

**Independent Test**: Try importing files with missing headers, invalid SP, dependency cycles; verify system rejects or warns as expected

### Unit Tests for User Story 2

- [x] T046 [P] [US2] Implement test_import_missing_header - missing header raises exception, no data persisted
- [x] T047 [P] [US2] Implement test_import_invalid_sp_warning - invalid SP generates warning, line skipped
- [x] T048 [P] [US2] Implement test_import_cycle_detection - cycle detected triggers rollback
- [x] T049 [P] [US2] Implement test_import_missing_dependency_warning - missing dependency generates warning
- [x] T050 [P] [US2] Implement test_import_partial_success - file with some errors imports valid lines

### Implementation for User Story 2

- [x] T051 [US2] Implement SP validation (3, 5, 8, 13 only) with warning for invalid in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T052 [US2] Implement cycle detection using DependencyService.build_graph and detect_cycle in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T053 [US2] Implement rollback on cycle detection via UnitOfWork in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T054 [US2] Implement warning for missing dependency ID (skip dependency, continue import) in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T055 [US2] Implement warning for empty Nome or ID+Componente (skip row) in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T056 [US2] Add ERROR logging for critical validation failures (header missing, cycle) per FR-122-123 in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py

**Checkpoint**: User Story 2 complete - validation protects data integrity

---

## Phase 5: User Story 3 - Exportar Backlog Completo para Excel (Priority: P1)

**Goal**: Export entire backlog to Excel file for sharing with stakeholders and manual backup

**Independent Test**: Create stories, developers, features in system; export to Excel; open in Microsoft Excel and verify content in 3 sheets

### Unit Tests for User Story 3

- [x] T057 [P] [US3] Create test_export_excel_use_case.py in tests/unit/application/use_cases/excel/
- [x] T058 [P] [US3] Implement test_export_stories - export generates Stories sheet with correct columns
- [x] T059 [P] [US3] Implement test_export_developers - export generates Developers sheet
- [x] T060 [P] [US3] Implement test_export_features - export generates Features sheet with wave
- [x] T061 [P] [US3] Implement test_export_dependencies_format - dependencies formatted with semicolon separator
- [x] T062 [P] [US3] Implement test_export_empty_backlog - empty backlog exports file with headers only

### Integration Tests for User Story 3

- [x] T063 [P] [US3] Implement test_excel_service_write_workbook - write creates file with 3 sheets
- [x] T064 [P] [US3] Implement test_excel_service_write_permission_error - write without permission raises exception

### Implementation for User Story 3

- [x] T065 [US3] Implement ExportExcelUseCase.__init__ with UoW and ExcelService in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T066 [US3] Implement ExportExcelUseCase._build_stories_data with Feature name and Desenvolvedor name lookups in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T067 [US3] Implement ExportExcelUseCase._build_developers_data in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T068 [US3] Implement ExportExcelUseCase._build_features_data in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T069 [US3] Implement ExportExcelUseCase._format_dependencies for semicolon-joined IDs in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T070 [US3] Implement ExportExcelUseCase.execute building ExcelExportData and calling write_workbook in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T071 [US3] Add logging (INFO at start/end with counts) per FR-124-125 in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py

**Checkpoint**: User Story 3 complete - export functionality works

---

## Phase 6: User Story 4 - Garantir Roundtrip Export-Import (Priority: P1)

**Goal**: Ensure exported file can be reimported without data loss for reliable backup

**Independent Test**: Export complete backlog, clear database, reimport file, verify all data restored identically

### Integration Tests for User Story 4

- [x] T072 [P] [US4] Implement test_roundtrip_complete - export then import in clean DB restores all data
- [x] T073 [P] [US4] Implement test_import_with_existing_data - incremental import adds to existing backlog
- [x] T074 [P] [US4] Implement test_import_with_existing_dependencies - import can reference existing IDs

### Implementation for User Story 4

- [x] T075 [US4] Verify Stories export includes all fields needed for reimport (ID, Componente, Nome, SP, Feature, Dependencias) in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T076 [US4] Verify Features export includes Wave for accurate restoration in src/backlog_manager/application/use_cases/excel/export_excel_use_case.py
- [x] T077 [US4] Verify ImportExcelUseCase handles existing stories gracefully (skip or update) in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py

**Checkpoint**: User Story 4 complete - roundtrip backup mechanism reliable

---

## Phase 7: User Story 5 - Usar Atalhos de Teclado para Import/Export (Priority: P2)

**Goal**: Provide keyboard shortcuts Ctrl+I (import) and Ctrl+E (export) for power users

**Independent Test**: Press Ctrl+I and Ctrl+E, verify file dialogs open with .xlsx filter

### Implementation for User Story 5

- [x] T078 [US5] Add QShortcut for Ctrl+I triggering import dialog in src/backlog_manager/presentation/views/main_window.py
- [x] T079 [US5] Add QShortcut for Ctrl+E triggering export dialog in src/backlog_manager/presentation/views/main_window.py
- [x] T080 [US5] Connect shortcuts to _on_import_clicked and _on_export_clicked handlers in src/backlog_manager/presentation/views/main_window.py
- [x] T081 [US5] Ensure shortcuts are disabled during ongoing operations in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: User Story 5 complete - keyboard shortcuts functional

---

## Phase 8: User Story 6 - Visualizar Feedback Durante Operacoes (Priority: P2)

**Goal**: Show visual feedback during import/export of large files so users know operation is in progress

**Independent Test**: Import file with 100+ stories, verify progress dialog displays percentage during operation

### Implementation for User Story 6

- [x] T082 [US6] Implement ExcelViewModel per contracts/excel_viewmodel_signals.md in src/backlog_manager/presentation/viewmodels/excel_viewmodel.py
- [x] T083 [US6] Implement ExcelViewModel.import_from_file emitting signals in sequence in src/backlog_manager/presentation/viewmodels/excel_viewmodel.py
- [x] T084 [US6] Implement ExcelViewModel.export_to_file emitting signals in sequence in src/backlog_manager/presentation/viewmodels/excel_viewmodel.py
- [x] T085 [US6] Add exception handling in ViewModel emitting error signals instead of propagating in src/backlog_manager/presentation/viewmodels/excel_viewmodel.py
- [x] T086 [US6] Add QProgressDialog display during import in src/backlog_manager/presentation/views/main_window.py
- [x] T087 [US6] Add cursor wait and button disable during export in src/backlog_manager/presentation/views/main_window.py
- [x] T088 [US6] Add QMessageBox summary after import completion showing stories imported count and expandable warning list in src/backlog_manager/presentation/views/main_window.py
- [x] T089 [US6] Add QMessageBox confirmation before overwriting existing file on export in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: User Story 6 complete - user feedback operational

---

## Phase 9: UI Integration & DI Container

**Purpose**: Wire all components together via DI Container and MainWindow

### UI Integration

- [x] T090 Add "Importar Excel" toolbar button with icon in src/backlog_manager/presentation/views/main_window.py
- [x] T091 Add "Exportar Excel" toolbar button with icon in src/backlog_manager/presentation/views/main_window.py
- [x] T092 Implement _on_import_clicked opening QFileDialog (filter: "Arquivos Excel (*.xlsx)") in src/backlog_manager/presentation/views/main_window.py
- [x] T093 Implement _on_export_clicked opening QFileDialog save (filter: "Arquivos Excel (*.xlsx)") in src/backlog_manager/presentation/views/main_window.py
- [x] T094 Connect ExcelViewModel signals to MainWindow handlers in src/backlog_manager/presentation/views/main_window.py
- [x] T095 Implement table refresh after import_completed signal in src/backlog_manager/presentation/views/main_window.py

### DI Container Extension

- [x] T096 Register ExcelService in DIContainer in src/backlog_manager/presentation/container.py
- [x] T097 Implement create_import_excel_use_case factory in DIContainer in src/backlog_manager/presentation/container.py
- [x] T098 Implement create_export_excel_use_case factory in DIContainer in src/backlog_manager/presentation/container.py
- [x] T099 Expose excel_viewmodel property in DIContainer in src/backlog_manager/presentation/container.py

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, performance tests, edge case handling

### Performance Tests

- [x] T100 [P] Implement test_export_large_backlog - 500 stories exports in < 15s
- [x] T101 [P] Implement test_import_large_file - 500 stories imports in < 10s

### Edge Case Handling

- [x] T102 Handle > 500 stories warning per RNF-PERF-001 in src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
- [x] T103 Handle file permission errors with user-friendly messages in ExcelService
- [x] T104 Handle user cancel during import (no partial data persisted) via UoW rollback

### Final Validation

- [x] T105 Run all unit tests with pytest
- [x] T106 Run all integration tests with pytest
- [x] T107 Verify mypy type checking passes
- [x] T108 Run quickstart.md manual testing scenarios

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-8)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can start after Foundational
  - US2 (Phase 4): Can start after Foundational (but logically extends US1)
  - US3 (Phase 5): Can start after Foundational (independent of US1/US2)
  - US4 (Phase 6): Depends on US1 and US3 completion (tests roundtrip)
  - US5 (Phase 7): Depends on Phase 9 UI components
  - US6 (Phase 8): Depends on Phase 9 UI components
- **UI Integration (Phase 9)**: Depends on US1 and US3 implementation
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundation only - MVP import
- **User Story 2 (P1)**: Foundation only - extends US1 validation
- **User Story 3 (P1)**: Foundation only - MVP export
- **User Story 4 (P1)**: Requires US1 + US3 - roundtrip validation
- **User Story 5 (P2)**: Requires UI Integration - shortcuts
- **User Story 6 (P2)**: Requires UI Integration - feedback

### Within Each User Story

- Tests marked [P] can run in parallel
- Implementation tasks follow dependency order
- Core implementation before integration

### Parallel Opportunities

- All Setup tasks T003-T007 marked [P] can run in parallel
- All DTO tasks T008-T013 marked [P] can run in parallel
- All Exception tasks T015-T019 marked [P] can run in parallel
- Tests within each user story marked [P] can run in parallel
- US1, US2, US3 can be worked in parallel after Foundation (if team capacity allows)

---

## Parallel Example: User Story 1

```bash
# Launch all unit tests for US1 together:
Task: "Create test_import_excel_use_case.py in tests/unit/application/use_cases/excel/"
Task: "Implement test_import_valid_file"
Task: "Implement test_import_auto_generate_id"
Task: "Implement test_import_create_feature"
Task: "Implement test_import_dependencies_second_pass"
Task: "Implement test_import_empty_file"

# Launch all integration tests for US1 together:
Task: "Create test_excel_service.py in tests/integration/infrastructure/excel/"
Task: "Implement test_excel_service_read_valid_file"
Task: "Implement test_excel_service_read_missing_file"
Task: "Implement test_excel_service_read_corrupted_file"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Import
4. Complete Phase 5: User Story 3 - Export
5. **STOP and VALIDATE**: Test import/export independently
6. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 (Import) -> Test independently -> MVP Import!
3. Add US2 (Validation) -> Harden import -> Safer Import!
4. Add US3 (Export) -> Test independently -> MVP Export!
5. Add US4 (Roundtrip) -> Test backup/restore -> Backup Ready!
6. Add Phase 9 (UI Integration) -> Wire UI
7. Add US5 + US6 (Shortcuts + Feedback) -> Polish!
8. Phase 10 (Polish) -> Final validation

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 + User Story 2 (Import + Validation)
   - Developer B: User Story 3 (Export)
3. After US1 + US3: Developer A handles US4 (Roundtrip)
4. After Phase 9: Developer B handles US5 + US6 (Shortcuts + Feedback)

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Tasks** | 109 |
| **Setup Phase** | 7 |
| **Foundational Phase** | 20 |
| **US1 Tasks** | 19 |
| **US2 Tasks** | 11 |
| **US3 Tasks** | 15 |
| **US4 Tasks** | 6 |
| **US5 Tasks** | 4 |
| **US6 Tasks** | 8 |
| **UI Integration** | 10 |
| **Polish Phase** | 9 |
| **Parallelizable Tasks** | 48 |

### MVP Scope (Recommended)

- Phase 1: Setup (7 tasks)
- Phase 2: Foundational (20 tasks)
- Phase 3: User Story 1 (18 tasks)
- Phase 5: User Story 3 (15 tasks)
- Phase 9: UI Integration (10 tasks - partial, buttons only)

**MVP Total**: ~60 tasks for basic import/export functionality

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
