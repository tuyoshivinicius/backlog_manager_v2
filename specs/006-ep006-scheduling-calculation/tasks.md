# Tasks: EP-006 Calculo de Cronograma

**Input**: Design documents from `/specs/006-ep006-scheduling-calculation/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/

**Tests**: Tests are included as requested in spec.md (XIV Estrategia de Testes: 100% cobertura para SchedulingService)

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

**Purpose**: Project initialization and basic structure for scheduling feature

- [ ] T001 Create scheduling directories: `src/backlog_manager/application/use_cases/scheduling/` and `src/backlog_manager/application/dto/scheduling/`
- [ ] T002 [P] Create `__init__.py` for `src/backlog_manager/application/use_cases/scheduling/__init__.py`
- [ ] T003 [P] Create `__init__.py` for `src/backlog_manager/application/dto/scheduling/__init__.py`
- [ ] T004 [P] Create `__init__.py` for `src/backlog_manager/domain/value_objects/__init__.py` (if not exists)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core value objects and domain service that ALL user stories depend on

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T005 [P] Implement `BRAZILIAN_HOLIDAYS_2026_2028` frozenset and `get_holidays_for_year()` in `src/backlog_manager/domain/value_objects/brazilian_holidays.py`
- [ ] T006 [P] Create `SchedulingService` class structure with static method signatures in `src/backlog_manager/domain/services/scheduling_service.py`
- [ ] T007 Export `SchedulingService` from `src/backlog_manager/domain/services/__init__.py`
- [ ] T008 Export `BRAZILIAN_HOLIDAYS_2026_2028` and `get_holidays_for_year` from `src/backlog_manager/domain/value_objects/__init__.py`

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Calcular Duracao de Historia Baseada em Story Points (Priority: P1)

**Goal**: Calculate story duration in workdays based on story points and velocity using formula `ceil(SP/velocity)` with minimum 1 day

**Independent Test**: Calculate duration for various SP and velocity combinations, verifying formula is applied correctly

### Tests for User Story 1

- [ ] T009 [P] [US1] Unit test `test_calculate_duration_normal` (SP=5, velocity=2 -> 3) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T010 [P] [US1] Unit test `test_calculate_duration_minimum` (SP=3, velocity=5 -> 1) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T011 [P] [US1] Unit test `test_calculate_duration_exact` (SP=8, velocity=4 -> 2) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T012 [P] [US1] Unit test `test_calculate_duration_invalid_velocity` (velocity=0 -> ValueError) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T013 [P] [US1] Unit test `test_calculate_duration_large_sp` (SP=13, velocity=2 -> 7) in `tests/unit/domain/services/test_scheduling_service.py`

### Implementation for User Story 1

- [ ] T014 [US1] Implement `SchedulingService.calculate_duration(story_points, velocity)` in `src/backlog_manager/domain/services/scheduling_service.py`
- [ ] T015 [P] [US1] Implement `CalculateDurationInputDTO` with Pydantic validation in `src/backlog_manager/application/dto/scheduling/calculate_duration_dto.py`
- [ ] T016 [P] [US1] Implement `CalculateDurationOutputDTO` in `src/backlog_manager/application/dto/scheduling/calculate_duration_dto.py`
- [ ] T017 [US1] Implement `CalculateDurationUseCase` in `src/backlog_manager/application/use_cases/scheduling/calculate_duration.py`
- [ ] T018 [US1] Export DTOs from `src/backlog_manager/application/dto/scheduling/__init__.py`
- [ ] T019 [US1] Export use case from `src/backlog_manager/application/use_cases/scheduling/__init__.py`

**Checkpoint**: Duration calculation works - `ceil(SP/velocity)` with minimum 1 day

---

## Phase 4: User Story 2 - Avancar N Dias Uteis a Partir de Uma Data (Priority: P1)

**Goal**: Calculate end_date by advancing N workdays from start_date, considering only Monday-Friday and excluding Brazilian holidays

**Independent Test**: Advance workdays from specific dates and verify weekends and holidays are skipped

### Tests for User Story 2

- [ ] T020 [P] [US2] Unit test `test_is_workday_monday` (2026-03-02 -> True) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T021 [P] [US2] Unit test `test_is_workday_saturday` (2026-03-07 -> False) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T022 [P] [US2] Unit test `test_is_workday_sunday` (2026-03-08 -> False) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T023 [P] [US2] Unit test `test_is_workday_holiday` (2026-04-21 Tiradentes -> False) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T024 [P] [US2] Unit test `test_add_workdays_same_week` (2026-03-02, 2 days -> 2026-03-03) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T025 [P] [US2] Unit test `test_add_workdays_across_weekend` (2026-03-06, 2 days -> 2026-03-09) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T026 [P] [US2] Unit test `test_add_workdays_with_holiday` (2026-04-20, 2 days -> 2026-04-22) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T027 [P] [US2] Unit test `test_add_workdays_ct004` (2026-04-01, 4 days -> 2026-04-07, Good Friday + weekend) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T028 [P] [US2] Unit test `test_count_workdays_between` (2026-03-02 to 2026-03-06 -> 3) in `tests/unit/domain/services/test_scheduling_service.py`

### Implementation for User Story 2

- [ ] T029 [US2] Implement `SchedulingService.is_workday(d, holidays)` in `src/backlog_manager/domain/services/scheduling_service.py`
- [ ] T030 [US2] Implement `SchedulingService.add_workdays(start_date, workdays, holidays)` in `src/backlog_manager/domain/services/scheduling_service.py`
- [ ] T031 [US2] Implement `SchedulingService.count_workdays_between(start_date, end_date, holidays)` in `src/backlog_manager/domain/services/scheduling_service.py`

**Checkpoint**: Workday arithmetic works - weekends and holidays are correctly skipped

---

## Phase 5: User Story 3 - Ajustar Data de Inicio para Proximo Dia Util (Priority: P1)

**Goal**: Automatically adjust start dates falling on weekends or holidays to the next workday

**Independent Test**: Pass dates on weekends and holidays, verify automatic adjustment

### Tests for User Story 3

- [ ] T032 [P] [US3] Unit test `test_next_workday_already_workday` (2026-03-02 -> 2026-03-02) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T033 [P] [US3] Unit test `test_next_workday_from_saturday` (2026-03-07 -> 2026-03-09) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T034 [P] [US3] Unit test `test_next_workday_from_sunday` (2026-03-08 -> 2026-03-09) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T035 [P] [US3] Unit test `test_next_workday_from_holiday` (2026-04-21 -> 2026-04-22) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T036 [P] [US3] Unit test `test_next_workday_from_good_friday` (2026-04-03 -> 2026-04-06) in `tests/unit/domain/services/test_scheduling_service.py`

### Implementation for User Story 3

- [ ] T037 [US3] Implement `SchedulingService.next_workday(d, holidays)` in `src/backlog_manager/domain/services/scheduling_service.py`

**Checkpoint**: Start date adjustment works - non-workdays are advanced to next workday

---

## Phase 6: User Story 4 - Calcular Datas Respeitando Dependencias (Priority: P1)

**Goal**: Calculate story start_date as next workday after all dependencies finish, respecting dependency order

**Independent Test**: Create stories with dependencies and verify start_date >= max(end_date_deps) + 1 workday

### Tests for User Story 4

- [ ] T038 [P] [US4] Unit test `test_calculate_story_dates_no_dependencies` in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T039 [P] [US4] Unit test `test_calculate_story_dates_single_dependency` (B depends on A, A.end=Wed -> B.start=Thu) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T040 [P] [US4] Unit test `test_calculate_story_dates_multiple_dependencies` (C depends on A and B -> C.start = max(A.end, B.end) + 1) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T041 [P] [US4] Unit test `test_calculate_story_dates_dependency_ends_friday` (A.end=Fri -> B.start=Mon) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T042 [P] [US4] Unit test `test_calculate_story_dates_dependency_ends_before_holiday` (A.end=2026-04-20 -> B.start=2026-04-22) in `tests/unit/domain/services/test_scheduling_service.py`

### Implementation for User Story 4

- [ ] T043 [US4] Implement `SchedulingService.calculate_story_dates(story, velocity, start_date, dependency_end_dates, holidays)` in `src/backlog_manager/domain/services/scheduling_service.py`
- [ ] T044 [P] [US4] Implement `CalculateStoryDatesInputDTO` with Pydantic validation in `src/backlog_manager/application/dto/scheduling/calculate_story_dates_dto.py`
- [ ] T045 [P] [US4] Implement `CalculateStoryDatesOutputDTO` in `src/backlog_manager/application/dto/scheduling/calculate_story_dates_dto.py`
- [ ] T046 [US4] Implement `CalculateStoryDatesUseCase` in `src/backlog_manager/application/use_cases/scheduling/calculate_story_dates.py`
- [ ] T047 [US4] Export DTOs from `src/backlog_manager/application/dto/scheduling/__init__.py`
- [ ] T048 [US4] Export use case from `src/backlog_manager/application/use_cases/scheduling/__init__.py`

**Checkpoint**: Story dates calculation works - dependencies are respected with proper workday advancement

---

## Phase 7: User Story 5 - Ordenar Historias Topologicamente com Desempate por Prioridade (Priority: P2)

**Goal**: Order stories respecting dependencies (dependencies before dependents) with priority tiebreaker using Kahn's algorithm

**Independent Test**: Create dependency graph and verify output order respects dependencies and priorities

### Tests for User Story 5

- [ ] T049 [P] [US5] Unit test `test_topological_sort_linear` (A->B->C -> [A, B, C]) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T050 [P] [US5] Unit test `test_topological_sort_priority_tiebreak` (A.prio=2, B.prio=1, independent -> [B, A]) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T051 [P] [US5] Unit test `test_topological_sort_complex` (A->C, B->C, A.prio=2, B.prio=1 -> [B, A, C]) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T052 [P] [US5] Unit test `test_topological_sort_cycle` (cycle detected -> CyclicDependencyException) in `tests/unit/domain/services/test_scheduling_service.py`
- [ ] T053 [P] [US5] Unit test `test_topological_sort_performance` (100 stories in < 100ms) in `tests/unit/domain/services/test_scheduling_service.py`

### Implementation for User Story 5

- [ ] T054 [US5] Implement `SchedulingService.topological_sort(stories, dependencies)` using Kahn's algorithm with heapq in `src/backlog_manager/domain/services/scheduling_service.py`

**Checkpoint**: Topological sorting works - O(V log V + E) complexity with priority tiebreaker

---

## Phase 8: User Story 6 - Calcular Cronograma Completo do Backlog (Priority: P2)

**Goal**: Calculate start/end dates for all eligible backlog stories in a single operation, respecting dependencies, workdays, and holidays

**Independent Test**: Provide a set of stories and verify all receive correct dates in topological order

### Tests for User Story 6

- [ ] T055 [P] [US6] Integration test `test_calculate_schedule_success` in `tests/integration/application/use_cases/test_scheduling_use_cases.py`
- [ ] T056 [P] [US6] Integration test `test_calculate_schedule_with_dependencies` in `tests/integration/application/use_cases/test_scheduling_use_cases.py`
- [ ] T057 [P] [US6] Integration test `test_calculate_schedule_with_holidays` in `tests/integration/application/use_cases/test_scheduling_use_cases.py`
- [ ] T058 [P] [US6] Integration test `test_calculate_schedule_cycle_detected` (CyclicDependencyException) in `tests/integration/application/use_cases/test_scheduling_use_cases.py`
- [ ] T059 [P] [US6] Integration test `test_calculate_schedule_empty_backlog` (success with 0 processed) in `tests/integration/application/use_cases/test_scheduling_use_cases.py`
- [ ] T060 [P] [US6] Integration test `test_calculate_schedule_invalid_story_points` (warning emitted) in `tests/integration/application/use_cases/test_scheduling_use_cases.py`
- [ ] T061 [P] [US6] Integration test `test_calculate_schedule_dependency_without_end_date` (fallback to project_start_date) in `tests/integration/application/use_cases/test_scheduling_use_cases.py`
- [ ] T062 [P] [US6] Integration test `test_schedule_rollback_on_error` in `tests/integration/application/use_cases/test_scheduling_use_cases.py`

### Implementation for User Story 6

- [ ] T063 [P] [US6] Implement `CalculateScheduleInputDTO` with Pydantic validation in `src/backlog_manager/application/dto/scheduling/calculate_schedule_dto.py`
- [ ] T064 [P] [US6] Implement `CalculateScheduleOutputDTO` in `src/backlog_manager/application/dto/scheduling/calculate_schedule_dto.py`
- [ ] T065 [US6] Implement `CalculateScheduleUseCase` with full workflow in `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py`
- [ ] T066 [US6] Export DTOs from `src/backlog_manager/application/dto/scheduling/__init__.py`
- [ ] T067 [US6] Export use case from `src/backlog_manager/application/use_cases/scheduling/__init__.py`

**Checkpoint**: Complete schedule calculation works - all stories scheduled atomically with warnings for edge cases

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and cleanup

- [ ] T068 Validate all exports in `src/backlog_manager/domain/services/__init__.py`
- [ ] T069 Validate all exports in `src/backlog_manager/domain/value_objects/__init__.py`
- [ ] T070 Validate all exports in `src/backlog_manager/application/dto/scheduling/__init__.py`
- [ ] T071 Validate all exports in `src/backlog_manager/application/use_cases/scheduling/__init__.py`
- [ ] T072 Run quickstart.md validation scenarios
- [ ] T073 Run full test suite and verify 100% coverage for SchedulingService

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-8)**: All depend on Foundational phase completion
  - US1, US2, US3, US4 are P1 priority - do these first
  - US5, US6 are P2 priority - depends on US1-US4 completion
- **Polish (Phase 9)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational - Uses is_workday from US2
- **User Story 4 (P1)**: Depends on US1 (calculate_duration), US2 (add_workdays), US3 (next_workday)
- **User Story 5 (P2)**: Can start after Foundational - No dependencies on other stories
- **User Story 6 (P2)**: Depends on ALL previous stories (US1-US5) - orchestrates everything

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Domain methods before DTOs
- DTOs before Use Cases
- Use Cases after all dependencies

### Parallel Opportunities

**Phase 1 (Setup)**:
```bash
# All directory creation and __init__.py files
T001, T002, T003, T004 in parallel
```

**Phase 2 (Foundational)**:
```bash
# Holidays value object and service structure
T005, T006 in parallel
# Then exports
T007, T008 in parallel
```

**Phase 3 (US1 - Duration)**:
```bash
# All unit tests for US1
T009, T010, T011, T012, T013 in parallel
# Then implementation
T014 (domain method)
# Then DTOs in parallel
T015, T016 in parallel
# Then use case and exports
T017, T018, T019 sequentially
```

**Phase 4 (US2 - Workdays)**:
```bash
# All unit tests for US2
T020, T021, T022, T023, T024, T025, T026, T027, T028 in parallel
# Then implementation sequentially (is_workday -> add_workdays -> count_workdays)
T029, T030, T031 sequentially
```

**Phase 5 (US3 - Next Workday)**:
```bash
# All unit tests for US3
T032, T033, T034, T035, T036 in parallel
# Then implementation
T037
```

**Phase 6 (US4 - Story Dates)**:
```bash
# All unit tests for US4
T038, T039, T040, T041, T042 in parallel
# Then implementation
T043 (domain method)
# Then DTOs in parallel
T044, T045 in parallel
# Then use case and exports
T046, T047, T048 sequentially
```

**Phase 7 (US5 - Topological Sort)**:
```bash
# All unit tests for US5
T049, T050, T051, T052, T053 in parallel
# Then implementation
T054
```

**Phase 8 (US6 - Full Schedule)**:
```bash
# All integration tests for US6
T055, T056, T057, T058, T059, T060, T061, T062 in parallel
# Then DTOs in parallel
T063, T064 in parallel
# Then use case and exports
T065, T066, T067 sequentially
```

---

## Implementation Strategy

### MVP First (User Stories 1-4)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Duration calculation)
4. Complete Phase 4: User Story 2 (Workday arithmetic)
5. Complete Phase 5: User Story 3 (Next workday adjustment)
6. Complete Phase 6: User Story 4 (Story dates with dependencies)
7. **STOP and VALIDATE**: Test individual story date calculations
8. Deploy/demo if ready - basic scheduling is functional

### Full Feature (Add User Stories 5-6)

9. Complete Phase 7: User Story 5 (Topological sorting)
10. Complete Phase 8: User Story 6 (Full schedule calculation)
11. Complete Phase 9: Polish
12. **FINAL VALIDATION**: Run all tests and quickstart scenarios

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. Add US1 -> Test duration calculation -> Increment 1
3. Add US2 + US3 -> Test workday arithmetic -> Increment 2
4. Add US4 -> Test story dates -> Increment 3 (MVP)
5. Add US5 -> Test topological sorting -> Increment 4
6. Add US6 -> Test full schedule -> Increment 5 (Full feature)

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Use `CyclicDependencyException` from EP-005 (do not recreate)
- Use `DependencyService.build_graph()` from EP-005 (do not recreate)
