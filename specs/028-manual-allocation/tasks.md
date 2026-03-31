# Tasks: Alocacao Manual de Desenvolvedores

**Input**: Design documents from `/specs/028-manual-allocation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Included (plan.md defines test files in project structure).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create package structure for new modules

- [X] T001 Create `__init__.py` files for new packages: `src/backlog_manager/application/dto/allocation/__init__.py` and `src/backlog_manager/application/use_cases/allocation/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: DTOs and Use Case that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [X] T002 [P] Create BlockingStoryDTO and DeveloperAvailabilityDTO in `src/backlog_manager/application/dto/allocation/developer_availability_dto.py`
- [X] T003 [P] Create GetDeveloperAvailabilityInputDTO and GetDeveloperAvailabilityOutputDTO in `src/backlog_manager/application/dto/allocation/get_developer_availability_dto.py`
- [X] T004 Implement GetDeveloperAvailabilityUseCase with full availability calculation flow (overlap check via AllocationService._has_period_overlap, recommendation via AllocationService._select_developer, date recalc via SchedulingService.calculate_story_dates) in `src/backlog_manager/application/use_cases/allocation/get_developer_availability.py`
- [X] T005 Register GetDeveloperAvailabilityUseCase factory (`create_get_developer_availability_use_case`) in `src/backlog_manager/presentation/container.py`

**Checkpoint**: Foundation ready - use case returns developer availability data for any story+date combination

---

## Phase 3: User Story 1 - Abrir Dialog de Alocacao Manual (Priority: P1) MVP

**Goal**: Double-click na coluna "Desenvolvedor" abre dialog exibindo todos os devs classificados em Livres/Ocupados com recomendacao visual

**Independent Test**: Clicar na celula "Desenvolvedor" de qualquer historia e verificar que a dialog abre com lista correta de devs, seus estados e a recomendacao

### Implementation for User Story 1

- [X] T006 [US1] Create ManualAllocationDialogViewModel with `load_developers()` async method (fetches velocity and allocation_criteria from Configuration via existing GetConfigurationUseCase, then calls GetDeveloperAvailabilityUseCase with those values, exposes developers list, recommended_developer_id, story dates) in `src/backlog_manager/presentation/viewmodels/manual_allocation_dialog_viewmodel.py`
- [X] T007 [US1] Register ManualAllocationDialogViewModel as lazy property in `src/backlog_manager/presentation/container.py`
- [X] T008 [US1] Create ManualAllocationDialog (QDialog) with QTreeWidget layout — two sections "Livres"/"Ocupados", developer items with story_count, occupied devs show blocking stories as sub-items, recommended dev highlighted with star icon — per UI contract in `src/backlog_manager/presentation/views/manual_allocation_dialog.py`
- [X] T009 [US1] Connect `doubleClicked(QModelIndex)` signal on StoryTableView — check column == 7 (Desenvolvedor), block if status CONCLUIDO, open ManualAllocationDialog with story data, handle pre-selected developer (FR-012) in `src/backlog_manager/presentation/views/main_window.py`
- [X] T010 [P] [US1] Unit tests for GetDeveloperAvailabilityUseCase (mock repos: story not found, no devs, free/busy classification, recommendation, overlap detection) in `tests/unit/application/test_get_developer_availability.py`
- [X] T011 [P] [US1/US2/US3] Unit tests for ManualAllocationDialogViewModel (load_developers success, error handling, story without dates, confirm_allocation persists developer_id, on_date_changed recalculates availability, confirm with changed date persists all three fields) in `tests/unit/presentation/test_manual_allocation_dialog_viewmodel.py`

**Checkpoint**: Dialog opens via double-click, shows correct developer classification and recommendation. No allocation happens yet.

---

## Phase 4: User Story 2 - Selecionar Desenvolvedor e Confirmar Alocacao (Priority: P1)

**Goal**: Usuario seleciona um dev livre na dialog, confirma, e a tabela de backlog reflete a alocacao

**Independent Test**: Selecionar dev livre, confirmar, verificar que tabela atualiza com o dev selecionado. Cancelar verifica que nada muda.

### Implementation for User Story 2

- [X] T012 [US2] Implement developer selection logic in ManualAllocationDialog — free devs selectable (enable Confirmar button on selection), busy devs greyed out/disabled (Qt.ItemFlag.NoItemFlags), cancel closes without changes in `src/backlog_manager/presentation/views/manual_allocation_dialog.py`
- [X] T013 [US2] Implement `confirm_allocation()` in ManualAllocationDialogViewModel — persist developer_id via existing EditStoryUseCase, expose selected_developer_id/new_start_date/new_end_date properties in `src/backlog_manager/presentation/viewmodels/manual_allocation_dialog_viewmodel.py`
- [X] T014 [US2] Handle dialog result in main_window.py — on accept(), read selected_developer_id/dates from dialog, update story in table model, refresh table display in `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: Full allocation cycle works — open dialog, select free dev, confirm, table updates. Cancel has no effect.

---

## Phase 5: User Story 3 - Alterar Data de Inicio para Recalcular Disponibilidade (Priority: P2)

**Goal**: Usuario altera data de inicio na dialog, disponibilidade dos devs e recalculada dinamicamente, devs movem entre secoes Livres/Ocupados

**Independent Test**: Alterar data de inicio, verificar que dev antes ocupado passa a livre (ou vice-versa), confirmar alocacao persiste nova data

### Implementation for User Story 3

- [X] T015 [US3] Add QDateEdit widget with workday restriction (minimum = next workday, auto-correct weekends/holidays via SchedulingService.next_workday, block past dates) in `src/backlog_manager/presentation/views/manual_allocation_dialog.py`
- [X] T016 [US3] Implement `on_date_changed()` in ManualAllocationDialogViewModel — recalculate end_date via SchedulingService, re-query GetDeveloperAvailabilityUseCase with new date, emit signal to update QTreeWidget sections dynamically in `src/backlog_manager/presentation/viewmodels/manual_allocation_dialog_viewmodel.py`
- [X] T017 [US3] Update confirm flow to persist start_date and recalculated end_date alongside developer_id when date was changed in `src/backlog_manager/presentation/viewmodels/manual_allocation_dialog_viewmodel.py`

**Checkpoint**: Date change triggers dynamic recalculation — devs move between Livres/Ocupados, recommendation updates, confirm persists all three fields.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases and validation

- [X] T018 Handle edge cases in ManualAllocationDialog: no developers registered (show "Nenhum desenvolvedor cadastrado"), story without dates (show "Execute o agendamento antes de alocar manualmente"), story without story_points (show "Defina os story points antes de alocar manualmente"), same date re-selected (skip recalculation) in `src/backlog_manager/presentation/views/manual_allocation_dialog.py`
- [X] T019 Run quickstart.md validation — execute full flow (open app, double-click Developer column, verify dialog, select dev, confirm, verify table update, test date change)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **US1 (Phase 3)**: Depends on Foundational phase — core dialog and display
- **US2 (Phase 4)**: Depends on US1 — selection and confirmation builds on dialog
- **US3 (Phase 5)**: Depends on US2 — date change extends confirm flow
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) — Opens dialog, displays data
- **User Story 2 (P1)**: Depends on US1 — Adds selection and persistence to existing dialog
- **User Story 3 (P2)**: Depends on US2 — Adds date change to existing confirm flow

### Within Each User Story

- ViewModel before View (ViewModel provides data contract)
- View before integration (dialog must exist before wiring to main_window)
- Tests can run in parallel with implementation (after use case exists)

### Parallel Opportunities

- T002 and T003 can run in parallel (different DTO files)
- T010 and T011 can run in parallel (different test files)
- T010/T011 can run in parallel with T008/T009 (tests vs implementation)

---

## Parallel Example: Foundational Phase

```bash
# Launch DTO creation in parallel:
Task: "Create BlockingStoryDTO + DeveloperAvailabilityDTO in developer_availability_dto.py"
Task: "Create Input/Output DTOs in get_developer_availability_dto.py"

# Then sequentially:
Task: "Implement GetDeveloperAvailabilityUseCase (depends on DTOs)"
Task: "Register factory in container.py (depends on use case)"
```

## Parallel Example: User Story 1

```bash
# After ViewModel + Dialog are created, launch tests in parallel:
Task: "Unit test for UseCase in test_get_developer_availability.py"
Task: "Unit test for ViewModel in test_manual_allocation_dialog_viewmodel.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (package structure)
2. Complete Phase 2: Foundational (DTOs + UseCase + container registration)
3. Complete Phase 3: User Story 1 (ViewModel + Dialog + double-click handler)
4. **STOP and VALIDATE**: Dialog opens, shows correct developer classification
5. Demo if ready

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 -> Dialog opens with dev list -> Test independently (MVP!)
3. Add US2 -> Selection + confirmation works -> Test independently
4. Add US3 -> Date change recalculates availability -> Test independently
5. Polish -> Edge cases handled -> Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- US2 depends on US1 (selection requires dialog), US3 depends on US2 (date change extends confirm flow)
- Domain services (AllocationService, SchedulingService) are UNCHANGED — only called, never modified (FR-010/SC-005)
- Persistence uses existing EditStoryUseCase — no new write use case needed
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
