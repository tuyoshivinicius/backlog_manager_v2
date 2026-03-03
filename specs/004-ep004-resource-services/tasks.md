# Tasks: EP-004 Gestao de Recursos - Servicos e Aplicacao

**Input**: Design documents from `/specs/004-ep004-resource-services/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are included as this is a library with 100% coverage requirement per constitution (Principio XIV).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/backlog_manager/`, `tests/` at repository root
- Paths follow structure defined in plan.md

---

## Phase 1: Setup (Repository Extensions)

**Purpose**: Extend repository protocols and implementations with new methods required by services

- [X] T001 Add `get_by_name(name: str) -> Feature | None` method signature to FeatureRepository protocol in src/backlog_manager/domain/interfaces/repositories.py
- [X] T002 Add `count_by_developer(developer_id: int) -> int` method signature to StoryRepository protocol in src/backlog_manager/domain/interfaces/repositories.py
- [X] T003 [P] Implement `get_by_name()` method in src/backlog_manager/infrastructure/database/repositories/feature_repository.py
- [X] T004 [P] Implement `count_by_developer()` method in src/backlog_manager/infrastructure/database/repositories/story_repository.py
- [X] T005 [P] Add integration test for `get_by_name()` in tests/integration/infrastructure/database/repositories/test_feature_repository.py
- [X] T006 [P] Add integration test for `count_by_developer()` in tests/integration/infrastructure/database/repositories/test_story_repository.py

**Checkpoint**: Repository extensions ready - service implementation can begin

---

## Phase 2: Foundational (Domain Services)

**Purpose**: Implement DeveloperService and FeatureService that all use cases depend on

**CRITICAL**: No use case can be implemented until both services are complete

- [X] T007 Create DeveloperService class with constructor in src/backlog_manager/domain/services/developer_service.py
- [X] T008 Implement `create_developer(name: str) -> Developer` method in src/backlog_manager/domain/services/developer_service.py
- [X] T009 Implement `update_developer(developer_id: int, name: str) -> Developer` method in src/backlog_manager/domain/services/developer_service.py
- [X] T010 Implement `delete_developer(developer_id: int) -> int` method in src/backlog_manager/domain/services/developer_service.py
- [X] T011 Implement `list_developers() -> Sequence[Developer]` method in src/backlog_manager/domain/services/developer_service.py
- [X] T012 Update exports in src/backlog_manager/domain/services/__init__.py to include DeveloperService
- [X] T013 [P] Create unit tests for DeveloperService in tests/unit/domain/services/test_developer_service.py
- [X] T014 Create FeatureService class with constructor in src/backlog_manager/domain/services/feature_service.py
- [X] T015 Implement `create_feature(name: str, wave: int) -> Feature` method in src/backlog_manager/domain/services/feature_service.py
- [X] T016 Implement `update_feature(feature_id: int, name: str | None, wave: int | None) -> Feature` method in src/backlog_manager/domain/services/feature_service.py
- [X] T017 Implement `delete_feature(feature_id: int) -> None` method in src/backlog_manager/domain/services/feature_service.py
- [X] T018 Implement `list_features() -> Sequence[Feature]` method in src/backlog_manager/domain/services/feature_service.py
- [X] T019 Update exports in src/backlog_manager/domain/services/__init__.py to include FeatureService
- [X] T020 [P] Create unit tests for FeatureService in tests/unit/domain/services/test_feature_service.py

**Checkpoint**: Domain services ready - use case and DTO implementation can begin

---

## Phase 3: User Story 1 - Cadastrar Novo Desenvolvedor (Priority: P1)

**Goal**: Enable Scrum Master to register developers in the system with auto-generated IDs

**Independent Test**: Create a developer with valid name and verify persistence with auto-generated ID

### DTOs for User Story 1

- [X] T021 [P] [US1] Create src/backlog_manager/application/dto/developer/ directory structure
- [X] T022 [P] [US1] Create CreateDeveloperInputDTO with name validation in src/backlog_manager/application/dto/developer/create_developer_dto.py
- [X] T023 [P] [US1] Create DeveloperOutputDTO with from_entity() method in src/backlog_manager/application/dto/developer/developer_output_dto.py
- [X] T024 [US1] Create __init__.py with exports in src/backlog_manager/application/dto/developer/__init__.py

### Use Case for User Story 1

- [X] T025 [P] [US1] Create src/backlog_manager/application/use_cases/developer/ directory structure
- [X] T026 [US1] Implement CreateDeveloperUseCase in src/backlog_manager/application/use_cases/developer/create_developer.py
- [X] T027 [US1] Create __init__.py with CreateDeveloperUseCase export in src/backlog_manager/application/use_cases/developer/__init__.py

### Tests for User Story 1

- [X] T028 [P] [US1] Create unit test for CreateDeveloperUseCase in tests/unit/application/use_cases/developer/test_create_developer.py

**Checkpoint**: User Story 1 complete - developer creation functional

---

## Phase 4: User Story 2 - Listar Desenvolvedores (Priority: P1)

**Goal**: Enable Scrum Master to view all registered developers sorted alphabetically

**Independent Test**: Register multiple developers and verify they return sorted by name

### DTOs for User Story 2

- [X] T029 [P] [US2] Create ListDevelopersOutputDTO in src/backlog_manager/application/dto/developer/list_developers_dto.py
- [X] T030 [US2] Update __init__.py exports in src/backlog_manager/application/dto/developer/__init__.py

### Use Case for User Story 2

- [X] T031 [US2] Implement ListDevelopersUseCase in src/backlog_manager/application/use_cases/developer/list_developers.py
- [X] T032 [US2] Update __init__.py exports in src/backlog_manager/application/use_cases/developer/__init__.py

### Tests for User Story 2

- [X] T033 [P] [US2] Create unit test for ListDevelopersUseCase in tests/unit/application/use_cases/developer/test_list_developers.py

**Checkpoint**: User Story 2 complete - developer listing functional

---

## Phase 5: User Story 3 - Editar Nome de Desenvolvedor (Priority: P1)

**Goal**: Enable Scrum Master to update developer names

**Independent Test**: Edit a developer's name and verify the change persisted

### DTOs for User Story 3

- [X] T034 [P] [US3] Create UpdateDeveloperInputDTO in src/backlog_manager/application/dto/developer/update_developer_dto.py
- [X] T035 [US3] Update __init__.py exports in src/backlog_manager/application/dto/developer/__init__.py

### Use Case for User Story 3

- [X] T036 [US3] Implement UpdateDeveloperUseCase in src/backlog_manager/application/use_cases/developer/update_developer.py
- [X] T037 [US3] Update __init__.py exports in src/backlog_manager/application/use_cases/developer/__init__.py

### Tests for User Story 3

- [X] T038 [P] [US3] Create unit test for UpdateDeveloperUseCase in tests/unit/application/use_cases/developer/test_update_developer.py

**Checkpoint**: User Story 3 complete - developer editing functional

---

## Phase 6: User Story 4 - Deletar Desenvolvedor com Desalocacao (Priority: P1)

**Goal**: Enable Scrum Master to remove developers with automatic story unassignment

**Independent Test**: Delete a developer with assigned stories and verify stories have developer_id=NULL

### DTOs for User Story 4

- [X] T039 [P] [US4] Create DeleteDeveloperOutputDTO in src/backlog_manager/application/dto/developer/delete_developer_dto.py
- [X] T040 [US4] Update __init__.py exports in src/backlog_manager/application/dto/developer/__init__.py

### Use Case for User Story 4

- [X] T041 [US4] Implement DeleteDeveloperUseCase in src/backlog_manager/application/use_cases/developer/delete_developer.py
- [X] T042 [US4] Update __init__.py exports in src/backlog_manager/application/use_cases/developer/__init__.py

### Tests for User Story 4

- [X] T043 [P] [US4] Create unit test for DeleteDeveloperUseCase in tests/unit/application/use_cases/developer/test_delete_developer.py

**Checkpoint**: User Story 4 complete - developer deletion with unassignment functional

---

## Phase 7: User Story 5 - Criar Nova Feature (Priority: P1)

**Goal**: Enable Product Owner to create features with unique name and wave

**Independent Test**: Create a feature with unique name and wave, verify persistence

### DTOs for User Story 5

- [X] T044 [P] [US5] Create src/backlog_manager/application/dto/feature/ directory structure
- [X] T045 [P] [US5] Create CreateFeatureInputDTO with name and wave validation in src/backlog_manager/application/dto/feature/create_feature_dto.py
- [X] T046 [P] [US5] Create FeatureOutputDTO with from_entity() method in src/backlog_manager/application/dto/feature/feature_output_dto.py
- [X] T047 [US5] Create __init__.py with exports in src/backlog_manager/application/dto/feature/__init__.py

### Use Case for User Story 5

- [X] T048 [P] [US5] Create src/backlog_manager/application/use_cases/feature/ directory structure
- [X] T049 [US5] Implement CreateFeatureUseCase in src/backlog_manager/application/use_cases/feature/create_feature.py
- [X] T050 [US5] Create __init__.py with CreateFeatureUseCase export in src/backlog_manager/application/use_cases/feature/__init__.py

### Tests for User Story 5

- [X] T051 [P] [US5] Create unit test for CreateFeatureUseCase in tests/unit/application/use_cases/feature/test_create_feature.py

**Checkpoint**: User Story 5 complete - feature creation with uniqueness validation functional

---

## Phase 8: User Story 6 - Listar Features (Priority: P1)

**Goal**: Enable Product Owner to view all features sorted by wave

**Independent Test**: Create features with different waves and verify ordered listing

### DTOs for User Story 6

- [X] T052 [P] [US6] Create ListFeaturesOutputDTO in src/backlog_manager/application/dto/feature/list_features_dto.py
- [X] T053 [US6] Update __init__.py exports in src/backlog_manager/application/dto/feature/__init__.py

### Use Case for User Story 6

- [X] T054 [US6] Implement ListFeaturesUseCase in src/backlog_manager/application/use_cases/feature/list_features.py
- [X] T055 [US6] Update __init__.py exports in src/backlog_manager/application/use_cases/feature/__init__.py

### Tests for User Story 6

- [X] T056 [P] [US6] Create unit test for ListFeaturesUseCase in tests/unit/application/use_cases/feature/test_list_features.py

**Checkpoint**: User Story 6 complete - feature listing functional

---

## Phase 9: User Story 7 - Editar Feature (Priority: P1)

**Goal**: Enable Product Owner to edit feature name and wave with uniqueness validation

**Independent Test**: Edit feature name/wave and verify changes with uniqueness enforced

### DTOs for User Story 7

- [X] T057 [P] [US7] Create UpdateFeatureInputDTO with optional name/wave in src/backlog_manager/application/dto/feature/update_feature_dto.py
- [X] T058 [US7] Update __init__.py exports in src/backlog_manager/application/dto/feature/__init__.py

### Use Case for User Story 7

- [X] T059 [US7] Implement UpdateFeatureUseCase in src/backlog_manager/application/use_cases/feature/update_feature.py
- [X] T060 [US7] Update __init__.py exports in src/backlog_manager/application/use_cases/feature/__init__.py

### Tests for User Story 7

- [X] T061 [P] [US7] Create unit test for UpdateFeatureUseCase in tests/unit/application/use_cases/feature/test_update_feature.py

**Checkpoint**: User Story 7 complete - feature editing with uniqueness validation functional

---

## Phase 10: User Story 8 - Deletar Feature (Priority: P1)

**Goal**: Enable Product Owner to delete features only when they have no associated stories

**Independent Test**: Verify feature deletion blocked when stories exist, allowed when empty

### Use Case for User Story 8

- [X] T062 [US8] Implement DeleteFeatureUseCase in src/backlog_manager/application/use_cases/feature/delete_feature.py
- [X] T063 [US8] Update __init__.py exports in src/backlog_manager/application/use_cases/feature/__init__.py

### Tests for User Story 8

- [X] T064 [P] [US8] Create unit test for DeleteFeatureUseCase in tests/unit/application/use_cases/feature/test_delete_feature.py

**Checkpoint**: User Story 8 complete - feature deletion with protection functional

---

## Phase 11: User Story 9 - Associar Historia a Feature (Priority: P2)

**Goal**: Enable Scrum Master to associate stories to features for wave organization

**Note**: This functionality is already implemented via EditStoryUseCase from EP-003 (ADR-005). No new code required - only documentation verification.

- [X] T065 [US9] Verify EditStoryUseCase (EP-003) supports feature_id parameter for story-feature association
- [X] T066 [US9] Document story-feature association workflow in quickstart.md (update if needed)

**Checkpoint**: User Story 9 verified - story-feature association available via EP-003

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories and final validation

- [X] T067 Update src/backlog_manager/application/dto/__init__.py to export all developer and feature DTOs
- [X] T068 Update src/backlog_manager/application/use_cases/__init__.py to export all developer and feature use cases
- [X] T068a [P] Add integration test verifying use case transaction commit on success in tests/integration/application/use_cases/test_transaction_commit.py
- [X] T068b [P] Add integration test verifying use case transaction rollback on validation error in tests/integration/application/use_cases/test_transaction_rollback.py
- [X] T068c [P] Add integration test verifying CreateFeatureUseCase rollback on DuplicateWaveException in tests/integration/application/use_cases/test_transaction_rollback.py
- [X] T069 Run full test suite with `poetry run pytest` and verify 100% coverage for new code
- [X] T070 Run type checking with `poetry run mypy src/backlog_manager` and fix any errors
- [X] T071 Run linting with `poetry run ruff check .` and fix any issues
- [X] T072 Run quickstart.md validation - execute example code and verify outputs

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 completion - BLOCKS all user stories
- **User Stories 1-4 (Phases 3-6)**: Developer CRUD - depend on Phase 2, can run sequentially
- **User Stories 5-8 (Phases 7-10)**: Feature CRUD - depend on Phase 2, can run in parallel with Developer stories
- **User Story 9 (Phase 11)**: Depends on EP-003 - verification only, no new implementation
- **Polish (Phase 12)**: Depends on all user stories being complete

### User Story Dependencies

- **US1-US4 (Developer)**: Sequential within group (DTOs -> Use Cases)
- **US5-US8 (Feature)**: Sequential within group (DTOs -> Use Cases)
- **Developer and Feature groups**: Can run in parallel after Phase 2

### Within Each User Story

- DTOs before use cases (DTOs are inputs/outputs for use cases)
- Implementation before tests pass (tests should fail initially if TDD)
- Story complete before marking checkpoint

### Parallel Opportunities

**Phase 1 (Setup)**:
- T003, T004, T005, T006 can run in parallel (different files)

**Phase 2 (Foundational)**:
- T013, T020 (tests) can run in parallel after services implemented

**Developer Stories (US1-US4)**:
- All DTO tasks marked [P] within each story can run in parallel
- Test tasks marked [P] can run in parallel with other tests

**Feature Stories (US5-US8)**:
- All DTO tasks marked [P] within each story can run in parallel
- Test tasks marked [P] can run in parallel with other tests

**Cross-Group Parallelism**:
- Developer stories (US1-US4) and Feature stories (US5-US8) can progress in parallel

---

## Parallel Example: Phase 1 Setup

```bash
# Launch repository extensions in parallel:
Task: "Implement get_by_name() in feature_repository.py"
Task: "Implement count_by_developer() in story_repository.py"
Task: "Add integration test for get_by_name()"
Task: "Add integration test for count_by_developer()"
```

---

## Parallel Example: Developer vs Feature Groups

```bash
# After Phase 2, launch both groups in parallel:
# Developer Team:
Task: "Create CreateDeveloperInputDTO"
Task: "Create DeveloperOutputDTO"

# Feature Team (same time):
Task: "Create CreateFeatureInputDTO"
Task: "Create FeatureOutputDTO"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4: Developer CRUD)

1. Complete Phase 1: Setup (repository extensions)
2. Complete Phase 2: Foundational (both services)
3. Complete Phases 3-6: User Stories 1-4 (Developer CRUD)
4. **STOP and VALIDATE**: Test Developer CRUD independently
5. Demo developer management functionality

### Full Delivery (Add Feature CRUD)

1. Continue with Phases 7-10: User Stories 5-8 (Feature CRUD)
2. Complete Phase 11: User Story 9 (verification)
3. Complete Phase 12: Polish
4. Full demo with Developer + Feature management

### Parallel Team Strategy

With two developers:

1. Both complete Phase 1 + Phase 2 together
2. Once foundational is done:
   - Developer A: User Stories 1-4 (Developer CRUD)
   - Developer B: User Stories 5-8 (Feature CRUD)
3. Both complete Phase 11-12 together for final validation

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 75 |
| **Setup Tasks** | 6 |
| **Foundational Tasks** | 14 |
| **User Story Tasks** | 46 |
| **Polish Tasks** | 9 |
| **Parallelizable Tasks** | 29 |
| **User Stories** | 9 |

### Tasks per User Story

| User Story | Description | Priority | Task Count |
|------------|-------------|----------|------------|
| US1 | Cadastrar Novo Desenvolvedor | P1 | 8 |
| US2 | Listar Desenvolvedores | P1 | 5 |
| US3 | Editar Nome de Desenvolvedor | P1 | 5 |
| US4 | Deletar Desenvolvedor com Desalocacao | P1 | 5 |
| US5 | Criar Nova Feature | P1 | 8 |
| US6 | Listar Features | P1 | 5 |
| US7 | Editar Feature | P1 | 5 |
| US8 | Deletar Feature | P1 | 3 |
| US9 | Associar Historia a Feature | P2 | 2 |

### MVP Scope

**Recommended MVP**: User Stories 1-4 (Developer CRUD)
- Enables developer registration and management
- Foundation for story allocation (EP-007)
- 23 tasks including setup and foundational

### Format Validation

All 72 tasks follow the required checklist format:
- Checkbox prefix: `- [ ]`
- Task ID: Sequential (T001-T072)
- [P] marker: Present only for parallelizable tasks
- [Story] label: Present for all user story phase tasks (US1-US9)
- File paths: Included in all implementation tasks

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests are included per constitution requirement (100% coverage)
