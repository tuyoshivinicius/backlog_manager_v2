# Tasks: Script de Seed para Teste de Alocação

**Input**: Design documents from `/specs/014-seed-test-backlog/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Integration tests included as specified in plan.md (tests/integration/test_seed_backlog.py)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `scripts/` for utilities, `tests/integration/` for tests
- Paths based on plan.md structure

---

## Phase 1: Setup

**Purpose**: Project structure verification and script initialization

- [X] T001 Verify existing infrastructure (sqlite_connection.py, init_database) is available for import
- [X] T002 Create script file scripts/seed_test_backlog.py with CLI argument parsing (argparse: --clean, --db-path, -h)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core script infrastructure that MUST be complete before user story features

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Implement seed constants (DEVELOPERS, WAVES, SP_WEIGHTS) in scripts/seed_test_backlog.py
- [X] T004 Implement database initialization wrapper using init_database from backlog_manager.infrastructure.database.sqlite_connection in scripts/seed_test_backlog.py
- [X] T005 Implement logging setup with Portuguese messages (INFO level) in scripts/seed_test_backlog.py
- [X] T006 Implement transaction management (atomic BEGIN/COMMIT/ROLLBACK) in scripts/seed_test_backlog.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Gerar Backlog de Teste Completo (Priority: P1) 🎯 MVP

**Goal**: Execute script to populate database with realistic backlog of 150-200 stories, 7 developers, ~30 features in 7 waves

**Independent Test**: Execute script and verify entity counts in database

### Implementation for User Story 1

- [X] T007 [US1] Implement generate_developers() function to create 7 fixed developers (Ana, Bruno, Carlos, Diana, Eduardo, Fernanda, Gabriel) in scripts/seed_test_backlog.py
- [X] T008 [US1] Implement generate_features() function to create ~30 features in 7 waves (4-5 per wave with domains: AUTH, USER, PROD, CART, PAY, REPORT, NOTIF/API) in scripts/seed_test_backlog.py
- [X] T009 [US1] Implement generate_stories() function to create 150-200 stories with ID format COMPONENTE-NNN, SP distribution (3:30%, 5:35%, 8:25%, 13:10%), status=BACKLOG, developer_id=NULL in scripts/seed_test_backlog.py
- [X] T010 [US1] Implement seed_database() async main function orchestrating all generation in scripts/seed_test_backlog.py
- [X] T011 [US1] Implement main() entry point with asyncio.run() in scripts/seed_test_backlog.py

**Checkpoint**: Script generates developers, features, and stories (without dependencies)

---

## Phase 4: User Story 2 - Garantir Integridade de Dependências (Priority: P1)

**Goal**: Generate 80-120 dependencies without cycles, respecting wave rules (60% intra-wave, 40% inter-wave)

**Independent Test**: Execute cycle detection on dependency graph after seed; verify wave rules

### Implementation for User Story 2

- [X] T012 [US2] Implement topological ordering logic ensuring dependencies only point to earlier stories (lower wave or same wave with lower priority) in scripts/seed_test_backlog.py
- [X] T013 [US2] Implement generate_dependencies() function creating 80-120 dependencies (60% intra-wave, 40% inter-wave, max 3 per story, wave 1 has no deps) in scripts/seed_test_backlog.py
- [X] T014 [US2] Add dependency generation to seed_database() orchestration in scripts/seed_test_backlog.py

**Checkpoint**: Script generates valid DAG of dependencies

---

## Phase 5: User Story 3 - Limpar Dados Existentes (Priority: P2)

**Goal**: Support --clean flag to remove existing data before seeding

**Independent Test**: Execute seed with --clean on database with existing data; verify replacement

### Implementation for User Story 3

- [X] T015 [US3] Implement check_existing_data() function to detect if database has data in scripts/seed_test_backlog.py
- [X] T016 [US3] Implement clean_data() function deleting in FK order (Story_Dependency → Story → Feature → Developer) in scripts/seed_test_backlog.py
- [X] T017 [US3] Integrate --clean flag handling in main seed flow (fail if data exists without --clean) in scripts/seed_test_backlog.py

**Checkpoint**: Script supports data cleanup before re-seeding

---

## Phase 6: User Story 4 - Especificar Banco de Dados Customizado (Priority: P2)

**Goal**: Support --db-path argument for custom database file location

**Independent Test**: Execute with --db-path pointing to temporary file; verify data in specified location

### Implementation for User Story 4

- [X] T018 [US4] Integrate --db-path argument into database initialization and connection in scripts/seed_test_backlog.py
- [X] T019 [US4] Add validation for --db-path (directory must exist) with clear error message in scripts/seed_test_backlog.py

**Checkpoint**: Script supports custom database paths

---

## Phase 7: User Story 5 - Acompanhar Progresso da Geração (Priority: P3)

**Goal**: Display progress messages during execution and summary at end

**Independent Test**: Observe terminal output during execution

### Implementation for User Story 5

- [X] T020 [US5] Add progress log messages for each generation stage (desenvolvedores, features, histórias, dependências) in scripts/seed_test_backlog.py
- [X] T021 [US5] Add final summary log with total counts of created entities in scripts/seed_test_backlog.py

**Checkpoint**: Script provides clear progress feedback

---

## Phase 8: User Story 6 - Garantir Reproducibilidade (Priority: P2)

**Goal**: Ensure identical data generation across executions using fixed random seed (42)

**Independent Test**: Execute script twice on different databases and compare data

### Implementation for User Story 6

- [X] T022 [US6] Implement random seed initialization (seed=42) at start of generation in scripts/seed_test_backlog.py
- [X] T023 [US6] Verify all random operations use seeded random module in scripts/seed_test_backlog.py

**Checkpoint**: Script produces deterministic, reproducible output

---

## Phase 9: Integration Tests

**Purpose**: Validate script functionality with integration tests

- [X] T024 [P] Create test file tests/integration/test_seed_backlog.py with pytest-asyncio fixtures
- [X] T025 [P] Implement test_seed_creates_expected_entities() verifying: (a) developer/feature/story/dependency counts, (b) story IDs match COMPONENTE-NNN format (FR-012), (c) all stories have status=BACKLOG and developer_id=NULL (FR-013) in tests/integration/test_seed_backlog.py
- [X] T026 [P] Implement test_no_cycles_in_dependencies() with cycle detection algorithm in tests/integration/test_seed_backlog.py
- [X] T027 Implement test_wave_rules_respected() verifying inter-wave dependencies point to earlier waves in tests/integration/test_seed_backlog.py
- [X] T027b Implement test_critical_scenarios() verifying: (a) at least one dependency chain crosses 3+ waves, (b) at least one story has 3 dependencies, (c) wave density varies (PROD denser than REPORT) per FR-014 in tests/integration/test_seed_backlog.py
- [X] T028 Implement test_clean_flag_removes_data() verifying --clean behavior in tests/integration/test_seed_backlog.py
- [X] T029 Implement test_reproducibility() comparing two executions for identical output in tests/integration/test_seed_backlog.py

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [X] T030 Run script and verify performance < 5 seconds (SC-001)
- [X] T031 Run quickstart.md commands to validate script usage
- [X] T032 Verify all type hints are complete (Principle X)
- [X] T033 Verify all public functions have Google-style docstrings (Principle XI)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - US1 and US2 are both P1 and can proceed in parallel if staffed
  - US3, US4, US6 are P2 and can proceed in parallel after US1/US2
  - US5 is P3 and can proceed after P2 stories
- **Integration Tests (Phase 9)**: Can proceed after US1 completes; additional tests as user stories complete
- **Polish (Phase 10)**: Depends on all user stories and tests being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 (needs stories to exist before creating dependencies)
- **User Story 3 (P2)**: Can start after Foundational - Independent of other stories
- **User Story 4 (P2)**: Can start after Foundational - Independent of other stories
- **User Story 5 (P3)**: Can start after Foundational - Independent but best after US1/US2
- **User Story 6 (P2)**: Can start after Foundational - Independent of other stories

### Within Each User Story

- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- Setup tasks T001-T002 can run in parallel
- Foundational tasks T003-T006 can run sequentially (same file)
- Integration tests T024-T026 marked [P] can run in parallel
- US3 and US4 can be developed in parallel (different functionality)
- US5 and US6 can be developed in parallel (different functionality)

---

## Parallel Example: Integration Tests

```bash
# Launch all initial tests together:
Task: "Create test file tests/integration/test_seed_backlog.py"
Task: "Implement test_seed_creates_expected_entities()"
Task: "Implement test_no_cycles_in_dependencies()"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (generate entities)
4. Complete Phase 4: User Story 2 (generate dependencies)
5. **STOP and VALIDATE**: Test script generates valid backlog
6. Run integration tests to verify

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 + 2 → Test with integration tests → MVP ready!
3. Add User Story 3 (--clean) → Test independently
4. Add User Story 4 (--db-path) → Test independently
5. Add User Story 6 (reproducibility) → Test independently
6. Add User Story 5 (progress logs) → Test independently
7. Polish phase → Complete validation

### Single Developer Strategy

Since this is a single-file script:

1. Complete phases sequentially (T001 → T033)
2. Commit after each phase completion
3. Run integration tests after Phase 4 (MVP)
4. Add remaining features incrementally

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All implementation is in single file: scripts/seed_test_backlog.py
- Tests are in single file: tests/integration/test_seed_backlog.py
- Verify tests fail before implementing (for integration tests)
- Commit after each phase or logical group
- Stop at any checkpoint to validate functionality
