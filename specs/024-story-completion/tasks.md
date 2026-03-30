# Tasks: Story Completion Status

**Input**: Design documents from `/specs/024-story-completion/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅ (no external contracts), quickstart.md ✅

**Tests**: Not explicitly requested in feature specification — test tasks omitted.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: No new project setup needed — feature builds on existing codebase. This phase covers the foundational domain artifact needed by all user stories.

- [x] T001 Create `IncompleteDependencyException` class in `src/backlog_manager/domain/exceptions/dependency.py` with attributes `story_id: str` and `incomplete_dependencies: list[tuple[str, str, str]]`, inheriting from `DependencyException`
- [x] T002 Export `IncompleteDependencyException` in `src/backlog_manager/domain/exceptions/__init__.py`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Fix pre-existing bug that blocks status transitions via DTO

**⚠️ CRITICAL**: The DTO validator bug prevents any status transition to "CONCLUIDO" — must be fixed before any user story work

- [x] T003 Fix status validator in `src/backlog_manager/application/dto/story/edit_story_dto.py` — replace `("BACKLOG", "IN_PROGRESS", "DONE", "BLOCKED")` with `("BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO")` to match `StoryStatus` enum values

**Checkpoint**: Foundation ready — DTO accepts correct status values, domain exception available

---

## Phase 3: User Story 1 — Mark Story as Completed (Priority: P1) 🎯 MVP

**Goal**: Enable marking a story as "Concluído" when all direct dependencies are satisfied, with validation in the use case layer.

**Independent Test**: Select a story with no dependencies (or all dependencies completed) and change its status to "Concluído". The status should update and persist successfully.

### Implementation for User Story 1

- [x] T004 [US1] Add dependency validation logic in `src/backlog_manager/application/use_cases/story/edit_story.py` — before applying status change to CONCLUIDO: fetch dependencies via `StoryDependencyRepository.get_dependencies()`, check each dependency's status via `StoryRepository.get_by_id()`, raise `IncompleteDependencyException` if any dependency is not CONCLUIDO
- [x] T005 [US1] Ensure transitions FROM CONCLUIDO to any other status are unrestricted (no validation) in `src/backlog_manager/application/use_cases/story/edit_story.py`

**Checkpoint**: Stories can be marked as Concluído with dependency validation. Transitions from Concluído are free.

---

## Phase 4: User Story 2 — Dependency Validation on Completion (Priority: P1)

**Goal**: Reject completion of a story when any direct dependency is not yet completed, enforcing workflow integrity.

**Independent Test**: Create Story B depending on Story A (status "Backlog"). Attempt to mark Story B as "Concluído" — system must reject with `IncompleteDependencyException`.

> **Note**: The core validation logic is implemented in US1 (T004). This phase ensures the validation covers all edge cases specified in spec.md.

### Implementation for User Story 2

- [x] T006 [US2] Verify and ensure the validation in `src/backlog_manager/application/use_cases/story/edit_story.py` correctly handles: multiple incomplete dependencies (all are listed), mix of complete and incomplete dependencies (only incomplete are flagged), and only direct dependencies are checked (FR-007)

**Checkpoint**: Dependency validation is complete — all direct dependency scenarios are handled correctly.

---

## Phase 5: User Story 3 — Exclude Completed Stories from Scheduling and Allocation (Priority: P1)

**Goal**: Completed stories are ignored by scheduling and allocation engines so they don't consume developer capacity or affect date calculations.

**Independent Test**: Mark a story as "Concluído", run allocation, verify the completed story is excluded from capacity calculations and its existing dates/developer are preserved.

### Implementation for User Story 3

- [x] T007 [US3] Add status filter in `AllocationService._is_eligible()` in `src/backlog_manager/domain/services/allocation_service.py` — return `False` when `story.status == StoryStatus.CONCLUIDO` to exclude completed stories from allocation (FR-004)
- [x] T008 [US3] Verify that `CalculateScheduleUseCase` in `src/backlog_manager/application/use_cases/` already excludes CONCLUIDO stories via existing `status != BACKLOG` filter (no code change expected — document confirmation)
- [x] T009 [US3] Verify that completed stories preserve existing `developer_id`, `start_date`, and `end_date` unchanged after allocation runs (FR-005) — no clearing of data upon completion in `src/backlog_manager/application/use_cases/story/edit_story.py`

**Checkpoint**: Completed stories are fully excluded from scheduling/allocation while preserving historical data.

---

## Phase 6: User Story 4 — Clear Feedback on Blocked Completion (Priority: P2)

**Goal**: Display a clear, informative message listing all blocking dependencies when completion is rejected.

**Independent Test**: Attempt to complete a story with multiple incomplete dependencies — verify the UI displays all blocking stories with their current statuses.

### Implementation for User Story 4

- [x] T010 [US4] Handle `IncompleteDependencyException` in `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` — catch the exception in `edit_story()` and format a user-facing message in Portuguese listing each incomplete dependency's ID, name, and current status
- [x] T011 [US4] Display the formatted error message in the UI via appropriate PySide6 dialog (e.g., `QMessageBox.warning`) in `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`

**Checkpoint**: Users see a clear message listing all blocking dependencies with their statuses when completion is rejected.

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and edge case verification

- [x] T012 Run `poetry run pytest tests/ -x -q` to verify all existing tests pass with new changes
- [x] T013 Run quickstart.md validation sequence to confirm end-to-end feature works

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Can run in parallel with Phase 1 (different files)
- **US1 (Phase 3)**: Depends on Phase 1 (exception class) and Phase 2 (DTO fix)
- **US2 (Phase 4)**: Depends on Phase 3 (validation logic from US1)
- **US3 (Phase 5)**: Depends on Phase 1 only (exception class) — can run in parallel with US1/US2
- **US4 (Phase 6)**: Depends on Phase 3 (exception must be raised to be caught in UI)
- **Polish (Phase 7)**: Depends on all previous phases

### User Story Dependencies

- **US1 (P1)**: Core — implements the completion + validation logic. All other stories build on this.
- **US2 (P1)**: Extends US1 — ensures validation covers all edge cases. Sequential after US1.
- **US3 (P1)**: Independent of US1/US2 — only touches allocation_service.py. Can run in parallel with US1/US2.
- **US4 (P2)**: Depends on US1 — needs the exception to be raised to handle it in the UI.

### Within Each User Story

- Domain changes before Application changes
- Application changes before Presentation changes
- Core logic before edge cases

### Parallel Opportunities

- T001 and T003 can run in parallel (different files)
- T007 (US3 allocation filter) can run in parallel with T004/T005 (US1 use case changes) — different files
- T010/T011 (US4 UI) must wait for T004 (US1 validation logic)

---

## Parallel Example: Phase 1 + Phase 2

```bash
# These tasks touch different files and can run in parallel:
Task T001: "Create IncompleteDependencyException in domain/exceptions/dependency.py"
Task T003: "Fix status validator in application/dto/story/edit_story_dto.py"
```

## Parallel Example: US1 + US3

```bash
# After Phase 1+2, these user stories touch different files:
Task T004: "Add dependency validation in use_cases/story/edit_story.py" (US1)
Task T007: "Add status filter in domain/services/allocation_service.py" (US3)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003)
3. Complete Phase 3: User Story 1 (T004, T005)
4. **STOP and VALIDATE**: Test marking a story as Concluído with and without dependencies
5. Core feature is usable

### Incremental Delivery

1. Phase 1 + 2 → Foundation ready
2. US1 (Phase 3) → Can mark stories as completed with validation → **MVP!**
3. US2 (Phase 4) → Edge cases verified → Robust validation
4. US3 (Phase 5) → Scheduling/allocation respects completion → Full planning integration
5. US4 (Phase 6) → Clear user feedback → Complete UX
6. Polish (Phase 7) → Final validation

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- No schema changes — feature uses existing `status VARCHAR(20)` column
- Scheduling (`CalculateScheduleUseCase`) already excludes non-BACKLOG stories — only allocation needs a filter change
- Bug fix in T003 is a prerequisite discovered during research (Decision 6)
