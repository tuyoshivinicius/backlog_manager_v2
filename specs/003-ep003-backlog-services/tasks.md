# Tasks: EP-003 Gestao de Backlog - Servicos e Aplicacao

**Input**: Design documents from `/specs/003-ep003-backlog-services/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included per plan.md requirements (100% cobertura StoryService, 100% use cases)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory structure, and base exports

- [X] T001 Create domain services directory structure with `__init__.py` in `src/backlog_manager/domain/services/__init__.py`
- [X] T002 [P] Create application DTOs story subdirectory with `__init__.py` in `src/backlog_manager/application/dto/story/__init__.py`
- [X] T003 [P] Create application use cases story subdirectory with `__init__.py` in `src/backlog_manager/application/use_cases/story/__init__.py`
- [X] T004 [P] Create test directories for unit tests in `tests/unit/domain/services/` and `tests/unit/application/use_cases/story/`
- [X] T005 [P] Create test directories for integration tests in `tests/integration/infrastructure/database/repositories/`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Repository protocol extensions and implementations that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

### Protocol Extensions

- [X] T006 Extend StoryRepository protocol with `get_max_id_number(component: str) -> int` in `src/backlog_manager/domain/interfaces/repositories.py`
- [X] T007 [P] Extend StoryRepository protocol with `get_max_priority() -> int` in `src/backlog_manager/domain/interfaces/repositories.py`
- [X] T008 [P] Extend StoryRepository protocol with `get_by_priority(priority: int) -> Story | None` in `src/backlog_manager/domain/interfaces/repositories.py`
- [X] T009 [P] Extend StoryDependencyRepository protocol with `remove_all_for_story(story_id: str) -> None` in `src/backlog_manager/domain/interfaces/repositories.py`

### SQLite Repository Implementations

- [X] T010 Implement `get_max_id_number` in SQLite StoryRepository in `src/backlog_manager/infrastructure/database/repositories/story_repository.py`
- [X] T011 [P] Implement `get_max_priority` in SQLite StoryRepository in `src/backlog_manager/infrastructure/database/repositories/story_repository.py`
- [X] T012 [P] Implement `get_by_priority` in SQLite StoryRepository in `src/backlog_manager/infrastructure/database/repositories/story_repository.py`
- [X] T013 [P] Implement `remove_all_for_story` in SQLite StoryDependencyRepository in `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py`

### Integration Tests for Repository Extensions

- [X] T014 [P] Write integration tests for repository extensions in `tests/integration/infrastructure/database/repositories/test_story_repository_extended.py`
- [X] T015 [P] Write integration tests for `remove_all_for_story` in `tests/integration/infrastructure/database/repositories/test_dependency_repository_extended.py`

### Shared DTOs

- [X] T016 Create StoryOutputDTO with `from_entity` method in `src/backlog_manager/application/dto/story/story_output_dto.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Criar Nova Historia com ID Auto-gerado (Priority: P1) MVP

**Goal**: Scrum Master can create new stories with automatically generated ID in format COMPONENTE-NNN

**Independent Test**: Create a story with component "CORE" and verify ID follows pattern CORE-001, CORE-002, etc.

### Tests for User Story 1

- [X] T017 [P] [US1] Write unit tests for `generate_story_id` method in `tests/unit/domain/services/test_story_service.py`
- [X] T018 [P] [US1] Write unit tests for `calculate_initial_priority` method in `tests/unit/domain/services/test_story_service.py`
- [X] T019 [P] [US1] Write unit tests for `create_story` method in `tests/unit/domain/services/test_story_service.py`
- [X] T020 [P] [US1] Write unit tests for CreateStoryUseCase in `tests/unit/application/use_cases/story/test_create_story.py`

### Implementation for User Story 1

- [X] T021 [P] [US1] Create CreateStoryInputDTO with Pydantic validation in `src/backlog_manager/application/dto/story/create_story_dto.py`
- [X] T022 [P] [US1] Create CreateStoryOutputDTO with `from_entity` method in `src/backlog_manager/application/dto/story/create_story_dto.py`
- [X] T023 [US1] Implement StoryService class with constructor and `generate_story_id` method in `src/backlog_manager/domain/services/story_service.py`
- [X] T024 [US1] Implement `calculate_initial_priority` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T025 [US1] Implement `create_story` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T026 [US1] Implement CreateStoryUseCase in `src/backlog_manager/application/use_cases/story/create_story.py`
- [X] T027 [US1] Export StoryService in `src/backlog_manager/domain/services/__init__.py`
- [X] T028 [US1] Export CreateStoryUseCase and DTOs in `src/backlog_manager/application/use_cases/story/__init__.py` and `src/backlog_manager/application/dto/story/__init__.py`

**Checkpoint**: User Story 1 complete - can create stories with auto-generated IDs

---

## Phase 4: User Story 2 - Listar Historias Ordenadas por Prioridade (Priority: P1)

**Goal**: Scrum Master can view all backlog stories ordered by priority

**Independent Test**: Create multiple stories with different priorities and verify ordering

### Tests for User Story 2

- [X] T029 [P] [US2] Write unit tests for `list_stories` method in `tests/unit/domain/services/test_story_service.py`
- [X] T030 [P] [US2] Write unit tests for ListStoriesUseCase in `tests/unit/application/use_cases/story/test_list_stories.py`

### Implementation for User Story 2

- [X] T031 [P] [US2] Create ListStoriesOutputDTO with `from_entities` method in `src/backlog_manager/application/dto/story/list_stories_dto.py`
- [X] T032 [US2] Implement `list_stories` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T033 [US2] Implement ListStoriesUseCase in `src/backlog_manager/application/use_cases/story/list_stories.py`
- [X] T034 [US2] Export ListStoriesUseCase and DTOs in `src/backlog_manager/application/use_cases/story/__init__.py` and `src/backlog_manager/application/dto/story/__init__.py`

**Checkpoint**: User Stories 1 AND 2 complete - can create and list stories

---

## Phase 5: User Story 3 - Editar Historia Existente (Priority: P1)

**Goal**: Scrum Master can edit existing stories while keeping ID immutable

**Independent Test**: Edit story fields and verify changes persist while ID remains unchanged

### Tests for User Story 3

- [X] T035 [P] [US3] Write unit tests for `update_story` method in `tests/unit/domain/services/test_story_service.py`
- [X] T036 [P] [US3] Write unit tests for UpdateStoryUseCase in `tests/unit/application/use_cases/story/test_update_story.py`

### Implementation for User Story 3

- [X] T037 [P] [US3] Create UpdateStoryInputDTO with validation in `src/backlog_manager/application/dto/story/update_story_dto.py`
- [X] T038 [US3] Implement `update_story` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T039 [US3] Implement UpdateStoryUseCase in `src/backlog_manager/application/use_cases/story/update_story.py`
- [X] T040 [US3] Export UpdateStoryUseCase and DTOs in `src/backlog_manager/application/use_cases/story/__init__.py` and `src/backlog_manager/application/dto/story/__init__.py`

**Checkpoint**: User Stories 1, 2, AND 3 complete - can create, list, and edit stories

---

## Phase 6: User Story 4 - Deletar Historia com Limpeza de Dependencias (Priority: P1)

**Goal**: Scrum Master can delete obsolete stories with automatic dependency cleanup

**Independent Test**: Delete a story that is a dependency of another and verify reference is removed

### Tests for User Story 4

- [X] T041 [P] [US4] Write unit tests for `delete_story` method in `tests/unit/domain/services/test_story_service.py`
- [X] T042 [P] [US4] Write unit tests for DeleteStoryUseCase in `tests/unit/application/use_cases/story/test_delete_story.py`

### Implementation for User Story 4

- [X] T043 [US4] Implement `delete_story` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T044 [US4] Implement DeleteStoryUseCase in `src/backlog_manager/application/use_cases/story/delete_story.py`
- [X] T045 [US4] Export DeleteStoryUseCase in `src/backlog_manager/application/use_cases/story/__init__.py`

**Checkpoint**: User Stories 1-4 complete - full CRUD for stories

---

## Phase 7: User Story 5 - Mover Prioridade para Cima/Baixo (Priority: P1)

**Goal**: Scrum Master can reorder stories by moving priority up or down

**Independent Test**: Move a story and verify adjacent priorities are swapped

### Tests for User Story 5

- [X] T046 [P] [US5] Write unit tests for `move_priority` method in `tests/unit/domain/services/test_story_service.py`
- [X] T047 [P] [US5] Write unit tests for MovePriorityUseCase in `tests/unit/application/use_cases/story/test_move_priority.py`

### Implementation for User Story 5

- [X] T048 [P] [US5] Create MovePriorityInputDTO and MovePriorityOutputDTO in `src/backlog_manager/application/dto/story/move_priority_dto.py`
- [X] T049 [US5] Implement `move_priority` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T050 [US5] Implement MovePriorityUseCase in `src/backlog_manager/application/use_cases/story/move_priority.py`
- [X] T051 [US5] Export MovePriorityUseCase and DTOs in `src/backlog_manager/application/use_cases/story/__init__.py` and `src/backlog_manager/application/dto/story/__init__.py`

**Checkpoint**: All P1 user stories complete - core backlog management functional

---

## Phase 8: User Story 6 - Duplicar Historia (Priority: P2)

**Goal**: Scrum Master can duplicate existing stories for quick creation of similar work

**Independent Test**: Duplicate an allocated story and verify copy has new ID, same data, but no allocation

### Tests for User Story 6

- [X] T052 [P] [US6] Write unit tests for `duplicate_story` method in `tests/unit/domain/services/test_story_service.py` (include edge case: feature_id copied as-is, FK validation deferred to DB)
- [X] T053 [P] [US6] Write unit tests for DuplicateStoryUseCase in `tests/unit/application/use_cases/story/test_duplicate_story.py`

### Implementation for User Story 6

- [X] T054 [US6] Implement `duplicate_story` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T055 [US6] Implement DuplicateStoryUseCase in `src/backlog_manager/application/use_cases/story/duplicate_story.py`
- [X] T056 [US6] Export DuplicateStoryUseCase in `src/backlog_manager/application/use_cases/story/__init__.py`

**Checkpoint**: User Story 6 complete - can duplicate stories

---

## Phase 9: User Story 7 - Atribuir/Desatribuir Desenvolvedor (Priority: P2)

**Goal**: Scrum Master can manually assign or unassign developers to stories

**Independent Test**: Assign an existing developer to a story and verify association

### Tests for User Story 7

- [X] T057 [P] [US7] Write unit tests for `assign_developer` method in `tests/unit/domain/services/test_story_service.py` (include edge case: developer_id=0 is valid ID, only None unassigns)
- [X] T058 [P] [US7] Write unit tests for AssignDeveloperUseCase in `tests/unit/application/use_cases/story/test_assign_developer.py`

### Implementation for User Story 7

- [X] T059 [P] [US7] Create AssignDeveloperInputDTO in `src/backlog_manager/application/dto/story/assign_developer_dto.py`
- [X] T060 [US7] Implement `assign_developer` method in StoryService in `src/backlog_manager/domain/services/story_service.py`
- [X] T061 [US7] Implement AssignDeveloperUseCase in `src/backlog_manager/application/use_cases/story/assign_developer.py`
- [X] T062 [US7] Export AssignDeveloperUseCase and DTOs in `src/backlog_manager/application/use_cases/story/__init__.py` and `src/backlog_manager/application/dto/story/__init__.py`

**Checkpoint**: All user stories complete

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final validations and cross-cutting improvements

- [X] T063 Update main application DTO exports in `src/backlog_manager/application/dto/__init__.py`
- [X] T064 [P] Update main use cases exports in `src/backlog_manager/application/use_cases/__init__.py`
- [X] T065 Run full test suite and verify coverage targets (100% StoryService, 100% use cases, 80% repositories)
- [X] T066 Run quickstart.md validation scenarios
- [X] T067 Run linting (ruff check .) and type checking (mypy)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - P1 stories (US1-US5) should be completed first
  - P2 stories (US6-US7) can proceed after foundational
  - User stories can proceed in parallel if staffed
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 4 (P1)**: Can start after Foundational - Uses `remove_all_for_story` from Foundational
- **User Story 5 (P1)**: Can start after Foundational - Uses `get_by_priority` from Foundational
- **User Story 6 (P2)**: Depends on US1 (uses `generate_story_id` and `calculate_initial_priority`)
- **User Story 7 (P2)**: Can start after Foundational - No dependencies on other stories

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- DTOs before services (DTOs needed by use cases)
- Services before use cases
- Implementation before exports
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- Protocol extensions (T006-T009) can run in parallel
- Repository implementations (T010-T013) can run in parallel
- Integration tests (T014-T015) can run in parallel
- Within user stories: Tests marked [P] can run in parallel
- Within user stories: DTOs marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task: "Write unit tests for generate_story_id in tests/unit/domain/services/test_story_service.py"
Task: "Write unit tests for calculate_initial_priority in tests/unit/domain/services/test_story_service.py"
Task: "Write unit tests for create_story in tests/unit/domain/services/test_story_service.py"
Task: "Write unit tests for CreateStoryUseCase in tests/unit/application/use_cases/story/test_create_story.py"

# Launch DTOs together:
Task: "Create CreateStoryInputDTO in src/backlog_manager/application/dto/story/create_story_dto.py"
Task: "Create CreateStoryOutputDTO in src/backlog_manager/application/dto/story/create_story_dto.py"
```

---

## Parallel Example: Foundational Phase

```bash
# Launch all protocol extensions together:
Task: "Extend StoryRepository with get_max_id_number"
Task: "Extend StoryRepository with get_max_priority"
Task: "Extend StoryRepository with get_by_priority"
Task: "Extend StoryDependencyRepository with remove_all_for_story"

# Launch all repository implementations together:
Task: "Implement get_max_id_number in SQLite"
Task: "Implement get_max_priority in SQLite"
Task: "Implement get_by_priority in SQLite"
Task: "Implement remove_all_for_story in SQLite"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Create Story)
4. **STOP and VALIDATE**: Test creating stories with auto-generated IDs
5. Deploy/demo if ready

### P1 Stories First (Core Backlog Management)

1. Complete Setup + Foundational -> Foundation ready
2. Add User Story 1 (Create) -> Test independently
3. Add User Story 2 (List) -> Test independently
4. Add User Story 3 (Edit) -> Test independently
5. Add User Story 4 (Delete) -> Test independently
6. Add User Story 5 (Move Priority) -> Test independently
7. **Core backlog management complete**

### Full Implementation

1. Complete all P1 stories (US1-US5)
2. Add User Story 6 (Duplicate) -> Test independently
3. Add User Story 7 (Assign Developer) -> Test independently
4. Complete Polish phase
5. Full feature complete

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Stories 1 + 2 (Create + List)
   - Developer B: User Stories 3 + 4 (Edit + Delete)
   - Developer C: User Stories 5 + 6 (Move + Duplicate)
   - Developer D: User Story 7 (Assign Developer)
3. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
