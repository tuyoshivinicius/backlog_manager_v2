# Tasks: EP-005 Gestao de Dependencias - Servicos e Aplicacao

**Input**: Design documents from `/specs/005-ep005-dependency-services/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests ARE requested - spec.md defines unit tests for DependencyService (100% coverage) and integration tests for use cases (SC-008, SC-009).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and directory structure for dependency management

- [X] T001 Create directory structure for use cases in src/backlog_manager/application/use_cases/dependency/
- [X] T002 [P] Create directory structure for DTOs in src/backlog_manager/application/dto/dependency/
- [X] T003 [P] Create test directory structure in tests/unit/domain/services/ (if not exists)
- [X] T004 [P] Create test directory structure in tests/unit/application/use_cases/dependency/
- [X] T005 [P] Create test directory structure in tests/integration/application/use_cases/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T006 Implement DependencyService class in src/backlog_manager/domain/services/dependency_service.py with DFS constants (WHITE=0, GRAY=1, BLACK=2)
- [X] T007 Implement build_graph method in src/backlog_manager/domain/services/dependency_service.py
- [X] T008 Implement would_create_cycle method with iterative DFS in src/backlog_manager/domain/services/dependency_service.py
- [X] T009 Implement detect_cycle method in src/backlog_manager/domain/services/dependency_service.py
- [X] T010 Implement validate_wave_dependency method in src/backlog_manager/domain/services/dependency_service.py
- [X] T011 Update __init__.py to export DependencyService from src/backlog_manager/domain/services/__init__.py

### Foundational Tests

- [X] T012 [P] Unit test for build_graph in tests/unit/domain/services/test_dependency_service.py
- [X] T013 [P] Unit test for detect_cycle_direct (A->B, B->A) in tests/unit/domain/services/test_dependency_service.py
- [X] T014 [P] Unit test for detect_cycle_indirect (A->B->C->A) in tests/unit/domain/services/test_dependency_service.py
- [X] T015 [P] Unit test for no_cycle_dag in tests/unit/domain/services/test_dependency_service.py
- [X] T016 [P] Unit test for performance_50_nodes (<100ms) in tests/unit/domain/services/test_dependency_service.py
- [X] T017 [P] Unit test for validate_wave_valid and invalid in tests/unit/domain/services/test_dependency_service.py

**Checkpoint**: DependencyService ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Adicionar Dependencia entre Historias (Priority: P1) 🎯 MVP

**Goal**: Scrum Master can add dependency between two stories with full validation

**Independent Test**: Add dependency between two existing stories and verify it's persisted in database

### DTOs for User Story 1

- [X] T0*18 [P] [US1] Create AddDependencyInputDTO in src/backlog_manager/application/dto/dependency/add_dependency_dto.py
- [X] T0*19 [P] [US1] Create AddDependencyOutputDTO in src/backlog_manager/application/dto/dependency/add_dependency_dto.py
- [X] T0*20 [P] [US1] Create InvalidWaveDependencyWarningDTO in src/backlog_manager/application/dto/dependency/add_dependency_dto.py
- [X] T0*21 [US1] Create __init__.py with exports in src/backlog_manager/application/dto/dependency/__init__.py

### Implementation for User Story 1

- [X] T0*22 [US1] Implement AddDependencyUseCase class structure in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*23 [US1] Implement story existence validation via StoryRepository.exists() in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*24 [US1] Implement self-dependency check (story_id != depends_on_id) in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*25 [US1] Implement duplicate dependency check in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*26 [US1] Implement graph building and cycle detection via DependencyService in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*27 [US1] Implement wave calculation and validation in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*28 [US1] Implement dependency persistence via StoryDependencyRepository.add() in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*29 [US1] Create __init__.py with exports in src/backlog_manager/application/use_cases/dependency/__init__.py

### Tests for User Story 1

- [X] T0*30 [P] [US1] Unit test for AddDependencyUseCase success flow in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*31 [P] [US1] Unit test for story_not_found error in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*32 [P] [US1] Unit test for self_dependency error in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*33 [P] [US1] Unit test for duplicate_dependency error in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*34 [P] [US1] Integration test for add_dependency_success in tests/integration/application/use_cases/test_dependency_use_cases.py

**Checkpoint**: User Story 1 complete - adding dependencies with existence validation works

---

## Phase 4: User Story 2 - Detectar e Rejeitar Ciclos de Dependencia (Priority: P1)

**Goal**: System automatically detects and rejects cycles with informative error message

**Independent Test**: Try creating A->B->A cycle and verify CyclicDependencyException with correct path

### Implementation for User Story 2

- [X] T0*35 [US2] Integrate CyclicDependencyException raising with path in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*36 [US2] Ensure cycle path format follows spec ["A", "B", "C", "A"] in src/backlog_manager/domain/services/dependency_service.py

### Tests for User Story 2

- [X] T0*37 [P] [US2] Unit test for direct cycle detection (A->B, B->A) in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*38 [P] [US2] Unit test for indirect cycle detection (A->B->C->A) in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*39 [P] [US2] Unit test for complex cycle with multiple paths in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*40 [P] [US2] Integration test for cycle_detection in tests/integration/application/use_cases/test_dependency_use_cases.py

**Checkpoint**: User Story 2 complete - cycle detection prevents invalid dependencies

---

## Phase 5: User Story 3 - Validar Dependencias entre Ondas (Priority: P2)

**Goal**: Product Owner gets warning when story depends on higher wave

**Independent Test**: Create dependency from wave 1 story to wave 2 story and verify warning is returned

### Implementation for User Story 3

- [X] T0*41 [US3] Implement wave lookup via FeatureRepository.get_by_id() in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*42 [US3] Implement warning generation for cross-wave dependencies in src/backlog_manager/application/use_cases/dependency/add_dependency.py
- [X] T0*43 [US3] Handle stories without feature (wave=0) in src/backlog_manager/application/use_cases/dependency/add_dependency.py

### Tests for User Story 3

- [X] T0*44 [P] [US3] Unit test for wave_warning when depends_on higher wave in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*45 [P] [US3] Unit test for no_warning when depends_on lower wave in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*46 [P] [US3] Unit test for no_warning when same wave in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*47 [P] [US3] Unit test for wave_warning with story without feature (wave=0) in tests/unit/application/use_cases/dependency/test_add_dependency.py
- [X] T0*48 [P] [US3] Integration test for wave_warning in tests/integration/application/use_cases/test_dependency_use_cases.py

**Checkpoint**: User Story 3 complete - cross-wave warnings help planning

---

## Phase 6: User Story 4 - Remover Dependencia entre Historias (Priority: P2)

**Goal**: Scrum Master can remove invalid dependencies when requirements change

**Independent Test**: Remove existing dependency and verify it's gone from get_dependencies

### DTOs for User Story 4

- [X] T0*49 [P] [US4] Create RemoveDependencyInputDTO in src/backlog_manager/application/dto/dependency/remove_dependency_dto.py
- [X] T0*50 [P] [US4] Create RemoveDependencyOutputDTO in src/backlog_manager/application/dto/dependency/remove_dependency_dto.py
- [X] T0*51 [US4] Update __init__.py with Remove DTO exports in src/backlog_manager/application/dto/dependency/__init__.py

### Implementation for User Story 4

- [X] T0*52 [US4] Implement RemoveDependencyUseCase class in src/backlog_manager/application/use_cases/dependency/remove_dependency.py
- [X] T0*53 [US4] Implement dependency existence check before removal in src/backlog_manager/application/use_cases/dependency/remove_dependency.py
- [X] T0*54 [US4] Implement dependency removal via StoryDependencyRepository.remove() in src/backlog_manager/application/use_cases/dependency/remove_dependency.py
- [X] T0*55 [US4] Update __init__.py with RemoveDependencyUseCase export in src/backlog_manager/application/use_cases/dependency/__init__.py

### Tests for User Story 4

- [X] T0*56 [P] [US4] Unit test for remove_dependency_success in tests/unit/application/use_cases/dependency/test_remove_dependency.py
- [X] T0*57 [P] [US4] Unit test for remove_dependency_not_found in tests/unit/application/use_cases/dependency/test_remove_dependency.py
- [X] T0*58 [P] [US4] Unit test for remove_preserves_other_dependencies in tests/unit/application/use_cases/dependency/test_remove_dependency.py
- [X] T0*59 [P] [US4] Integration test for remove_dependency in tests/integration/application/use_cases/test_dependency_use_cases.py

**Checkpoint**: User Story 4 complete - dependencies can be removed

---

## Phase 7: User Story 5 - Consultar Dependencias de uma Historia (Priority: P2)

**Goal**: Scrum Master can query dependencies and dependents for planning

**Independent Test**: Add dependencies and query via get_dependencies/get_dependents

### DTOs for User Story 5

- [X] T0*60 [P] [US5] Create GetDependenciesInputDTO in src/backlog_manager/application/dto/dependency/get_dependency_dto.py
- [X] T0*61 [P] [US5] Create GetDependenciesOutputDTO in src/backlog_manager/application/dto/dependency/get_dependency_dto.py
- [X] T0*62 [P] [US5] Create GetDependentsInputDTO in src/backlog_manager/application/dto/dependency/get_dependency_dto.py
- [X] T0*63 [P] [US5] Create GetDependentsOutputDTO in src/backlog_manager/application/dto/dependency/get_dependency_dto.py
- [X] T0*64 [US5] Update __init__.py with Get DTO exports in src/backlog_manager/application/dto/dependency/__init__.py

### Implementation for User Story 5

- [X] T0*65 [US5] Implement GetDependenciesUseCase in src/backlog_manager/application/use_cases/dependency/get_dependencies.py
- [X] T0*66 [US5] Implement GetDependentsUseCase in src/backlog_manager/application/use_cases/dependency/get_dependents.py
- [X] T0*67 [US5] Update __init__.py with Get use case exports in src/backlog_manager/application/use_cases/dependency/__init__.py

### Tests for User Story 5

- [X] T0*68 [P] [US5] Unit test for get_dependencies_success in tests/unit/application/use_cases/dependency/test_get_dependencies.py
- [X] T0*69 [P] [US5] Unit test for get_dependencies_empty in tests/unit/application/use_cases/dependency/test_get_dependencies.py
- [X] T0*70 [P] [US5] Unit test for get_dependents_success in tests/unit/application/use_cases/dependency/test_get_dependents.py
- [X] T0*71 [P] [US5] Unit test for get_dependents_empty in tests/unit/application/use_cases/dependency/test_get_dependents.py
- [X] T0*72 [P] [US5] Integration test for get_dependencies and get_dependents in tests/integration/application/use_cases/test_dependency_use_cases.py

**Checkpoint**: User Story 5 complete - all query operations work

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and code quality

- [X] T0*73 [P] Run mypy type checking on all new files
- [X] T0*74 [P] Run black/isort formatting on all new files
- [X] T0*75 [P] Verify test coverage >= 80% for DependencyService
- [X] T0*76 [P] Verify test coverage >= 80% for use cases
- [X] T0*77 Run all unit tests and verify 100% pass
- [X] T0*78 Run all integration tests and verify 100% pass
- [X] T0*79 Validate quickstart.md example works end-to-end

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup (T001-T005) - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational (T006-T017)
- **User Story 2 (Phase 4)**: Depends on User Story 1 (P1 priority, adds cycle exception)
- **User Story 3 (Phase 5)**: Depends on User Story 1 (adds wave validation)
- **User Story 4 (Phase 6)**: Depends on Foundational only (independent removal)
- **User Story 5 (Phase 7)**: Depends on Foundational only (independent queries)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Core add functionality - required by US2 and US3
- **User Story 2 (P1)**: Extends US1 with cycle detection - must follow US1
- **User Story 3 (P2)**: Extends US1 with wave validation - can follow US1 or US2
- **User Story 4 (P2)**: Independent remove functionality - only needs Foundational
- **User Story 5 (P2)**: Independent query functionality - only needs Foundational

### Within Each User Story

- DTOs can be created in parallel [P]
- DTOs must be complete before Use Case implementation
- Use Case core logic → validation → persistence → tests
- Tests marked [P] can run in parallel

### Parallel Opportunities

- All Setup tasks (T001-T005) can run in parallel
- DependencyService tests (T012-T017) can run in parallel
- User Stories 4 and 5 can run in parallel (no shared dependencies)
- All test tasks marked [P] within a story can run in parallel
- All DTO tasks marked [P] within a story can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# After T006-T011 complete, launch all DependencyService tests together:
Task: "Unit test for build_graph in tests/unit/domain/services/test_dependency_service.py"
Task: "Unit test for detect_cycle_direct in tests/unit/domain/services/test_dependency_service.py"
Task: "Unit test for detect_cycle_indirect in tests/unit/domain/services/test_dependency_service.py"
Task: "Unit test for no_cycle_dag in tests/unit/domain/services/test_dependency_service.py"
Task: "Unit test for performance_50_nodes in tests/unit/domain/services/test_dependency_service.py"
Task: "Unit test for validate_wave_valid in tests/unit/domain/services/test_dependency_service.py"
```

## Parallel Example: User Story 4 & 5 (After Foundational)

```bash
# User Story 4 and 5 can run in parallel after Foundational completes:
# Team Member A: User Story 4 (Remove)
Task: "Create RemoveDependencyInputDTO"
Task: "Implement RemoveDependencyUseCase"

# Team Member B: User Story 5 (Query)
Task: "Create GetDependenciesInputDTO"
Task: "Implement GetDependenciesUseCase"
```

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (DependencyService)
3. Complete Phase 3: User Story 1 (Add Dependency)
4. Complete Phase 4: User Story 2 (Cycle Detection)
5. **STOP and VALIDATE**: Test adding dependencies and cycle detection
6. Deploy/demo if ready - core value delivered

### Incremental Delivery

1. Setup + Foundational → DependencyService ready
2. Add User Story 1 → Can add dependencies (MVP!)
3. Add User Story 2 → Cycle detection protects integrity
4. Add User Story 3 → Wave warnings improve planning
5. Add User Story 4 → Can remove dependencies
6. Add User Story 5 → Query operations complete the feature
7. Each story adds value without breaking previous stories

### Recommended Priority Order

1. **Must Have (MVP)**: US1 (Add) + US2 (Cycles) - P1
2. **Should Have**: US4 (Remove) + US5 (Query) - P2
3. **Nice to Have**: US3 (Wave Validation) - P2

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Tests follow TDD approach where applicable
- DependencyService uses iterative DFS to avoid stack overflow
- Performance target: <100ms for 50-node graphs (CT-002)
- All DTOs use Pydantic validation
- All use cases receive UnitOfWork via constructor
