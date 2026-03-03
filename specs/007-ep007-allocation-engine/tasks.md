# Tasks: EP-007 Motor de Alocacao

**Input**: Design documents from `/specs/007-ep007-allocation-engine/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Test tasks are included as the feature specification mentions pytest and 100% coverage requirement.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `src/backlog_manager/`
- **Tests**: `tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and domain dataclasses/enums

- [X] T000 [PREREQ] Verify exception hierarchy exists: BacklogManagerException, AllocationException, MaxIterationsExceeded, DeadlockWarning, IdlenessWarning, BetweenWavesIdlenessInfo in `src/backlog_manager/domain/exceptions/`. If missing, create them following Constitution XVI.
- [X] T001 Create allocation directory structure: `src/backlog_manager/application/use_cases/allocation/` and `src/backlog_manager/application/dto/allocation/`
- [X] T002 [P] Create `src/backlog_manager/application/use_cases/allocation/__init__.py` (empty package)
- [X] T003 [P] Create `src/backlog_manager/application/dto/allocation/__init__.py` (empty package)
- [X] T004 [P] Define security constants (DEFAULT_MAX_ITERATIONS=1000, MAX_REALLOCATIONS_PER_STORY=3, MAX_STABILIZATION_PASSES=10, MAX_CONFLICT_PASSES=100) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T005 [P] Implement AllocationCriteria enum (LOAD_BALANCING, DEPENDENCY_OWNER) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T006 [P] Implement AllocationConfig dataclass with validation in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T007 [P] Implement AllocationMetrics dataclass (16 fields) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T008 [P] Implement AllocationResult dataclass in `src/backlog_manager/domain/services/allocation_service.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core domain service class and helper methods that ALL user stories depend on

**Warning**: No user story work can begin until this phase is complete

- [X] T009 Create AllocationService class skeleton with docstring in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T010 Implement `_is_eligible(story)` helper method to check eligibility (dev=NULL, dates ok, SP ok) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T011 Implement `_get_story_wave(story, feature_map)` helper to get wave from feature_id (0 if no feature) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T012 Implement `_build_feature_map(features)` helper to create feature_id -> wave dict in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T013 Implement `_group_stories_by_wave(stories, feature_map)` helper in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T014 Implement `allocate_stories()` public method skeleton (signature + docstring) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T015 Export AllocationService, AllocationConfig, AllocationMetrics, AllocationResult, AllocationCriteria from `src/backlog_manager/domain/services/__init__.py`
- [X] T016 Create unit test file `tests/unit/domain/services/test_allocation_service.py` with test fixtures (stories, developers, features)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Executar Alocacao Automatica do Backlog (Priority: P1) MVP

**Goal**: Execute automatic allocation of developers for all eligible stories in the backlog

**Independent Test**: Run allocation with eligible stories and verify all receive developer_id

### Tests for User Story 1

- [X] T017 [P] [US1] Write test_allocate_empty_backlog in `tests/unit/domain/services/test_allocation_service.py`
- [X] T018 [P] [US1] Write test_allocate_single_story_single_dev in `tests/unit/domain/services/test_allocation_service.py`
- [X] T019 [P] [US1] Write test_allocate_story_without_dates_not_allocated in `tests/unit/domain/services/test_allocation_service.py`
- [X] T020 [P] [US1] Write test_allocate_story_already_allocated_maintained in `tests/unit/domain/services/test_allocation_service.py`
- [X] T021 [P] [US1] Write test_allocate_no_eligible_returns_zero in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 1

- [X] T022 [US1] Implement main allocation loop in `allocate_stories()` method in `src/backlog_manager/domain/services/allocation_service.py`
  - Note: This task MUST implement date adjustment (+1 workday) when no dev available (FR-050 to FR-052)
- [X] T023 [US1] Implement story filtering logic (eligible stories only) in `allocate_stories()` in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T024 [US1] Implement metrics collection (stories_processed, stories_allocated, total_time_seconds) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T025 [US1] Verify all US1 tests pass

**Checkpoint**: Basic allocation working - eligible stories receive developer_id

---

## Phase 4: User Story 2 - Balanceamento de Carga entre Desenvolvedores (Priority: P1)

**Goal**: Distribute stories evenly among developers based on story count

**Independent Test**: Create independent stories and verify balanced distribution

### Tests for User Story 2

- [X] T026 [P] [US2] Write test_allocate_balanced_distribution (4 stories, 2 devs -> 2 each) in `tests/unit/domain/services/test_allocation_service.py`
- [X] T027 [P] [US2] Write test_allocate_uneven_distribution (5 stories, 2 devs -> 3,2 or 2,3) in `tests/unit/domain/services/test_allocation_service.py`
- [X] T028 [P] [US2] Write test_load_balancing_tiebreak_random with seed in `tests/unit/domain/services/test_allocation_service.py`
- [X] T029 [P] [US2] Write test_load_balancing_deterministic_with_seed in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 2

- [X] T030 [US2] Implement `_select_developer()` method with LOAD_BALANCING logic in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T031 [US2] Implement dev_count tracking (dict[int, int]) in allocation loop in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T032 [US2] Implement random tiebreak with random.Random(seed) in `_select_developer()` in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T033 [US2] Update metrics (allocations_by_load_balancing) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T034 [US2] Verify all US2 tests pass

**Checkpoint**: Load balancing working - stories distributed evenly among developers

---

## Phase 5: User Story 3 - Processar Historias por Ondas Sequencialmente (Priority: P1)

**Goal**: Process stories wave by wave (wave 0, 1, 2...) ensuring earlier waves are prioritized

**Independent Test**: Create stories in different waves and verify processing order

**Note**: Wave 0 = stories WITHOUT feature (feature_id is NULL). CT-001 scenario uses waves 1,2,3 because all test stories have features assigned. Tests for wave 0 are in T036.

### Tests for User Story 3

- [X] T035 [P] [US3] Write test_allocate_by_wave_order (waves 0,1,2 processed in order) in `tests/unit/domain/services/test_allocation_service.py`
- [X] T036 [P] [US3] Write test_allocate_wave_0_first (stories without feature = wave 0) in `tests/unit/domain/services/test_allocation_service.py`
- [X] T037 [P] [US3] Write test_allocate_multiple_waves_sequential in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 3

- [X] T038 [US3] Implement wave grouping in `allocate_stories()` using `_group_stories_by_wave()` in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T039 [US3] Implement `_allocate_by_wave()` method for processing single wave in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T040 [US3] Update metrics (waves_processed, iterations_per_wave) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T041 [US3] Verify all US3 tests pass

**Checkpoint**: Wave processing working - stories processed in wave order (0, 1, 2...)

---

## Phase 6: User Story 4 - Evitar Conflitos de Periodo (Priority: P1)

**Goal**: Detect and resolve period conflicts automatically so no developer has overlapping stories

**Independent Test**: Create overlapping stories for same dev and verify date adjustment

### Tests for User Story 4

- [X] T042 [P] [US4] Write test_resolve_conflict_simple (2 overlapping stories adjusted) in `tests/unit/domain/services/test_allocation_service.py`
- [X] T043 [P] [US4] Write test_resolve_conflict_cascade (multiple conflicts resolved) in `tests/unit/domain/services/test_allocation_service.py`
- [X] T044 [P] [US4] Write test_no_conflict_no_adjustment in `tests/unit/domain/services/test_allocation_service.py`
- [X] T045 [P] [US4] Write test_conflict_weekend_adjustment (new date on next workday) in `tests/unit/domain/services/test_allocation_service.py`
- [X] T045b [P] [US4] Write test_date_adjustment_when_no_dev_available (FR-050 to FR-052) in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 4

- [X] T046 [US4] Implement `_has_period_overlap(story_a, story_b)` helper in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T047 [US4] Implement `_resolve_allocation_conflicts()` method with MAX_CONFLICT_PASSES limit in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T048 [US4] Integrate SchedulingService.next_workday() and add_workdays() for date adjustments in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T048b [US4] Implement `_adjust_date_for_availability()` helper for FR-050/FR-051/FR-052 (adjust start_date +1 workday when no dev available) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T049 [US4] Update metrics (validation_conflict_fixes) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T050 [US4] Verify all US4 tests pass

**Checkpoint**: Conflict resolution working - no overlapping periods for any developer

---

## Phase 7: User Story 10 - Loop de Estabilizacao Pos-Alocacao (Priority: P1)

**Goal**: Execute validation and stabilization loop after main allocation to ensure final consistency

**Independent Test**: Run allocation and verify stabilization loop corrects inconsistencies

### Tests for User Story 10

- [X] T051 [P] [US10] Write test_stabilization_loop_runs in `tests/unit/domain/services/test_allocation_service.py`
- [X] T052 [P] [US10] Write test_stabilization_max_passes_respected in `tests/unit/domain/services/test_allocation_service.py`
- [X] T053 [P] [US10] Write test_stabilization_stops_when_stable in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 10

- [X] T054 [US10] Implement `_stabilization_loop()` method with 3 steps in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T055 [US10] Implement `_final_dependency_check()` method in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T056 [US10] Integrate stabilization loop at end of `allocate_stories()` in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T057 [US10] Update metrics (validation_dependency_fixes) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T058 [US10] Verify all US10 tests pass

**Checkpoint**: Stabilization loop working - final result is consistent

---

## Phase 8: User Story 5 - Detectar Deadlocks na Alocacao (Priority: P2)

**Goal**: Detect deadlock situations where no story can be allocated and emit warnings

**Independent Test**: Create scenario where no progress is possible and verify DeadlockWarning

### Tests for User Story 5

- [X] T059 [P] [US5] Write test_detect_deadlock_no_developers in `tests/unit/domain/services/test_allocation_service.py`
- [X] T060 [P] [US5] Write test_deadlock_warning_emitted in `tests/unit/domain/services/test_allocation_service.py`
- [X] T061 [P] [US5] Write test_deadlock_proceeds_to_next_wave in `tests/unit/domain/services/test_allocation_service.py`
- [X] T062 [P] [US5] Write test_max_iterations_respected in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 5

- [X] T063 [US5] Implement deadlock detection logic (no progress in iteration) in `_allocate_by_wave()` in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T064 [US5] Emit DeadlockWarning with wave and blocked_stories list in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T065 [US5] Continue to next wave after deadlock detection in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T066 [US5] Update metrics (deadlocks_detected, total_iterations) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T067 [US5] Verify all US5 tests pass

**Checkpoint**: Deadlock detection working - system emits warnings without hanging

---

## Phase 9: User Story 6 - Detectar e Alertar Ociosidade (Priority: P2)

**Goal**: Detect excessive idle periods between stories of the same developer and emit warnings

**Independent Test**: Create stories with large gaps for same dev and verify IdlenessWarning

### Tests for User Story 6

- [X] T068 [P] [US6] Write test_detect_idleness_intra_wave in `tests/unit/domain/services/test_allocation_service.py`
- [X] T069 [P] [US6] Write test_detect_idleness_inter_wave_info in `tests/unit/domain/services/test_allocation_service.py`
- [X] T070 [P] [US6] Write test_no_idleness_warning_within_threshold in `tests/unit/domain/services/test_allocation_service.py`
- [X] T071 [P] [US6] Write test_max_idle_days_config_respected in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 6

- [X] T072 [US6] Implement `_check_idleness()` method using SchedulingService.count_workdays_between() in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T073 [US6] Implement intra-wave vs inter-wave gap detection logic in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T074 [US6] Emit IdlenessWarning for intra-wave gaps > max_idle_days in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T075 [US6] Emit BetweenWavesIdlenessInfo for inter-wave gaps (informative) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T076 [US6] Update metrics (max_idle_violations_detected) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T077 [US6] Verify all US6 tests pass

**Checkpoint**: Idleness detection working - warnings emitted for excessive gaps

---

## Phase 10: User Story 9 - Coletar Metricas de Alocacao (Priority: P2)

**Goal**: Collect detailed metrics after allocation for analysis and diagnostics

**Independent Test**: Run allocation and verify AllocationMetrics structure is complete

### Tests for User Story 9

- [X] T078 [P] [US9] Write test_metrics_all_fields_populated in `tests/unit/domain/services/test_allocation_service.py`
- [X] T079 [P] [US9] Write test_metrics_deadlocks_counted in `tests/unit/domain/services/test_allocation_service.py`
- [X] T080 [P] [US9] Write test_metrics_conflict_fixes_counted in `tests/unit/domain/services/test_allocation_service.py`
- [X] T081 [P] [US9] Write test_metrics_iterations_per_wave_tracked in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 9

- [X] T082 [US9] Review and ensure all 16 metric fields are updated throughout the algorithm in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T083 [US9] Add total_time_seconds measurement using time.perf_counter() in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T084 [US9] Verify all US9 tests pass

**Checkpoint**: Metrics collection complete - all 16 fields populated correctly

---

## Phase 11: User Story 7 - Criterio Proprietario de Dependencia (Priority: P3)

**Goal**: Configure allocation criteria by dependency owner to prioritize context continuity

**Independent Test**: Configure DEPENDENCY_OWNER and verify preferential allocation

### Tests for User Story 7

- [X] T085 [P] [US7] Write test_dependency_owner_allocation in `tests/unit/domain/services/test_allocation_service.py`
- [X] T086 [P] [US7] Write test_dependency_owner_fallback_to_load_balancing in `tests/unit/domain/services/test_allocation_service.py`
- [X] T087 [P] [US7] Write test_dependency_owner_multiple_deps_uses_latest in `tests/unit/domain/services/test_allocation_service.py`
- [X] T088 [P] [US7] Write test_load_balancing_ignores_dependency_owner in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 7

- [X] T089 [US7] Implement `_get_dependency_owner()` method (dev with latest end_date dependency) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T090 [US7] Update `_select_developer()` to support DEPENDENCY_OWNER criteria in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T091 [US7] Implement fallback to LOAD_BALANCING when owner not available in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T092 [US7] Update metrics (allocations_by_dependency_owner) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T093 [US7] Verify all US7 tests pass

**Checkpoint**: Dependency owner criteria working - continuity prioritized when configured

---

## Phase 12: User Story 8 - Realocar para Minimizar Ociosidade (Priority: P3)

**Goal**: Attempt to reallocate stories when excessive idleness is detected to optimize schedule

**Independent Test**: Create idleness scenario and verify reallocation attempt

### Tests for User Story 8

- [X] T094 [P] [US8] Write test_reallocate_on_idleness in `tests/unit/domain/services/test_allocation_service.py`
- [X] T095 [P] [US8] Write test_max_reallocations_per_story_respected in `tests/unit/domain/services/test_allocation_service.py`
- [X] T096 [P] [US8] Write test_failed_reallocation_counted in `tests/unit/domain/services/test_allocation_service.py`
- [X] T097 [P] [US8] Write test_reallocation_recalculates_dates in `tests/unit/domain/services/test_allocation_service.py`

### Implementation for User Story 8

- [X] T098 [US8] Implement reallocation_count tracking (dict[str, int]) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T099 [US8] Implement `_check_and_fix_idle_violations()` method with reallocation logic in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T100 [US8] Implement MAX_REALLOCATIONS_PER_STORY limit check in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T101 [US8] Update metrics (validation_reallocations, max_idle_violations_fixed, failed_reallocations) in `src/backlog_manager/domain/services/allocation_service.py`
- [X] T102 [US8] Verify all US8 tests pass

**Checkpoint**: Reallocation for idleness working - schedule optimized when possible

---

## Phase 13: Application Layer - DTOs

**Purpose**: Pydantic DTOs for use case input/output

- [X] T103 [P] Implement ExecuteAllocationInputDTO in `src/backlog_manager/application/dto/allocation/execute_allocation_dto.py`
- [X] T104 [P] Implement ExecuteAllocationOutputDTO in `src/backlog_manager/application/dto/allocation/execute_allocation_dto.py`
- [X] T105 [P] Implement AllocationMetricsDTO with from_domain() method in `src/backlog_manager/application/dto/allocation/execute_allocation_dto.py`
- [X] T106 Export all DTOs from `src/backlog_manager/application/dto/allocation/__init__.py`
- [X] T107 [P] Write DTO validation tests in `tests/integration/application/use_cases/test_allocation_use_cases.py`

**Checkpoint**: DTOs ready for use case integration

---

## Phase 14: Application Layer - Use Case

**Purpose**: ExecuteAllocationUseCase coordinating domain service and persistence

- [X] T108 Create integration test file `tests/integration/application/use_cases/test_allocation_use_cases.py` with test database setup
- [X] T109 [P] Write test_execute_allocation_success in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T110 [P] Write test_execute_allocation_rollback_on_error in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T111 [P] Write test_execute_allocation_with_dependencies in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T112 [P] Write test_allocation_large_backlog_warning (>500 stories) in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T113 Implement ExecuteAllocationUseCase class with __init__(uow) in `src/backlog_manager/application/use_cases/allocation/execute_allocation.py`
- [X] T114 Implement execute() async method in ExecuteAllocationUseCase in `src/backlog_manager/application/use_cases/allocation/execute_allocation.py`
- [X] T115 Implement data fetching (stories, developers, dependencies, features) via UnitOfWork in `src/backlog_manager/application/use_cases/allocation/execute_allocation.py`
- [X] T116 Implement AllocationConfig creation from InputDTO in `src/backlog_manager/application/use_cases/allocation/execute_allocation.py`
- [X] T117 Implement story persistence loop (StoryRepository.update) in `src/backlog_manager/application/use_cases/allocation/execute_allocation.py`
- [X] T118 Implement backlog size warning (>500 stories) in `src/backlog_manager/application/use_cases/allocation/execute_allocation.py`
- [X] T119 Export ExecuteAllocationUseCase from `src/backlog_manager/application/use_cases/allocation/__init__.py`
- [X] T120 Verify all integration tests pass

**Checkpoint**: Use case working - end-to-end allocation from database

---

## Phase 15: Scenario Tests (CT-001, CT-003, CT-005)

**Purpose**: Validate against SRS test scenarios

- [X] T121 [P] Write test_execute_allocation_ct001 (simple scenario) in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T122 [P] Write test_execute_allocation_ct003 (dependencies scenario) in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T123 [P] Write test_execute_allocation_ct005 (waves scenario) in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T124 [P] Write test_allocation_performance in `tests/integration/application/use_cases/test_allocation_use_cases.py`
- [X] T125 Verify all scenario tests pass

**Checkpoint**: All SRS scenarios validated

---

## Phase 16: Polish & Cross-Cutting Concerns

**Purpose**: Final validation, coverage, and quality checks

- [X] T126 Run pytest with coverage and verify tests pass on allocation_service.py
- [X] T127 Run mypy strict type checking on all allocation files
- [X] T128 Run ruff formatting on all allocation files
- [X] T129 [P] Add docstrings (Google style, Portuguese) to all public methods
- [X] T130 Run quickstart.md validation scenarios via tests
- [X] T131 Final review of AllocationService contract compliance

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-12)**: All depend on Foundational phase completion
  - P1 stories (US1, US2, US3, US4, US10) can proceed first
  - P2 stories (US5, US6, US9) can proceed after P1 or in parallel
  - P3 stories (US7, US8) can proceed after P2 or in parallel
- **Application Layer (Phases 13-14)**: Depends on all domain user stories
- **Scenario Tests (Phase 15)**: Depends on Application Layer
- **Polish (Phase 16)**: Depends on all previous phases

### User Story Dependencies

| User Story | Priority | Dependencies | Notes |
|------------|----------|--------------|-------|
| US1 - Executar Alocacao | P1 | Foundational | Core allocation loop |
| US2 - Balanceamento | P1 | US1 | Builds on allocation loop |
| US3 - Processar por Ondas | P1 | US2 | Adds wave grouping |
| US4 - Evitar Conflitos | P1 | US3 | Adds conflict resolution |
| US10 - Loop Estabilizacao | P1 | US4 | Wraps with stabilization |
| US5 - Detectar Deadlocks | P2 | US3 | Independent detection |
| US6 - Detectar Ociosidade | P2 | US10 | Uses stabilization context |
| US9 - Coletar Metricas | P2 | US1-US6 | Reviews all metrics |
| US7 - Criterio Proprietario | P3 | US2 | Alternative allocation criteria |
| US8 - Realocar Ociosidade | P3 | US6 | Extends idleness handling |

### Parallel Opportunities

Within each phase:
- All tasks marked [P] can run in parallel
- All tests for a user story can be written in parallel
- DTOs can be written in parallel

### Parallel Example: User Story 2 (Load Balancing)

```bash
# Launch all tests for US2 together:
Task: "test_allocate_balanced_distribution"
Task: "test_allocate_uneven_distribution"
Task: "test_load_balancing_tiebreak_random"
Task: "test_load_balancing_deterministic_with_seed"
```

---

## Implementation Strategy

### MVP First (User Stories 1-4, 10)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: US1 - Executar Alocacao
4. Complete Phase 4: US2 - Balanceamento
5. Complete Phase 5: US3 - Processar por Ondas
6. Complete Phase 6: US4 - Evitar Conflitos
7. Complete Phase 7: US10 - Loop Estabilizacao
8. **STOP and VALIDATE**: Test P1 stories independently
9. Deploy/demo MVP if ready

### Incremental Delivery

1. MVP (P1 stories) -> Basic allocation with balancing and conflict resolution
2. Add P2 stories (US5, US6, US9) -> Deadlock detection, idleness detection, metrics
3. Add P3 stories (US7, US8) -> Advanced criteria and reallocation
4. Application layer -> End-to-end integration
5. Each increment adds value without breaking previous functionality

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All domain code is synchronous; use case is async
- SchedulingService and DependencyService are assumed to exist (EP-005, EP-006)
