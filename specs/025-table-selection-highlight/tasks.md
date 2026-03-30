# Tasks: Table Selection Highlight

**Input**: Design documents from `/specs/025-table-selection-highlight/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-selection-contract.md

**Tests**: Included — spec explicitly mentions pytest + pytest-qt testing.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Design tokens and QSS foundation required by all visual selection work

- [X] T001 Add selection and hover design tokens (`selection-bg`, `selection-fg`, `selection-border`, `hover-bg`) in src/backlog_manager/presentation/theme/theme.py
- [X] T002 Add QSS rules for `QTableView::item:selected`, `QTableView::item:hover`, and `QTableView::item:selected:hover` in src/backlog_manager/presentation/theme/theme.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Delegate selection-awareness and action state management that ALL user stories depend on

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 [P] Update `StatusBadgeDelegate.paint()` to check `option.state & QStyle.StateFlag.State_Selected` and use `selection-bg` token as cell background when selected in src/backlog_manager/presentation/delegates/status_badge_delegate.py
- [X] T004 [P] Update `DependencyIndicatorDelegate.paint()` to check selection state and use `selection-bg` as cell background when selected in src/backlog_manager/presentation/delegates/dependency_indicator_delegate.py
- [X] T005 [P] Update `MonospaceDelegate.paint()` to check selection state and use `selection-fg` as text foreground when selected in src/backlog_manager/presentation/delegates/monospace_delegate.py

**Checkpoint**: All delegates respect selection state — visual consistency ensured across all columns

---

## Phase 3: User Story 1 — Visual Selection Feedback on Click (Priority: P1) 🎯 MVP

**Goal**: Clicking a row in the backlog table visually highlights it with a distinct background, foreground, and left border. Clicking another row moves the highlight.

**Independent Test**: Click any row → row is visually distinct. Click another row → highlight moves. Previous row returns to normal.

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [P] [US1] Unit test: verify `selected_story_id` is updated when selection changes in tests/unit/presentation/viewmodels/test_main_window_viewmodel.py
- [X] T007 [P] [US1] Integration test: click row → verify highlight applied; click another row → verify highlight moves in tests/integration/presentation/views/test_main_window.py

### Implementation for User Story 1

- [X] T008 [US1] Apply selection QSS stylesheet to `StoryTableView` in `_setup_table()` in src/backlog_manager/presentation/views/main_window.py
- [X] T009 [US1] Ensure `QTableView` selection mode is `SingleSelection` and selection behavior is `SelectRows` in src/backlog_manager/presentation/views/main_window.py
- [X] T010 [US1] Connect `QItemSelectionModel.currentRowChanged` signal to update `selected_story_id` in ViewModel via `story_selected(story_id)` in src/backlog_manager/presentation/views/main_window.py
- [X] T011 [US1] Disable Edit/Delete/Move Up/Move Down actions when `selected_story_id is None` — extend `_update_move_actions_state()` or create `_update_action_states()` in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: US1 complete — clicking rows shows clear visual selection, actions disabled when nothing selected

---

## Phase 4: User Story 2 — Selection Persists During Actions (Priority: P2)

**Goal**: When a story is moved up or down, the selection highlight follows the story to its new row position.

**Independent Test**: Select a story → Move Up → verify selection follows the story to its new position. Same for Move Down.

### Tests for User Story 2

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T012 [P] [US2] Unit test: verify `selected_story_id` is preserved after `load_stories()` in tests/unit/presentation/viewmodels/test_main_window_viewmodel.py
- [X] T013 [P] [US2] Integration test: select row → move up → verify selection follows story; select row → move down → verify selection follows story in tests/integration/presentation/views/test_main_window.py

### Implementation for User Story 2

- [X] T014 [US2] Implement `_restore_selection(story_id: str)` method in MainWindow — iterate model rows via `UserRole` to find matching story_id and call `setCurrentIndex()` in src/backlog_manager/presentation/views/main_window.py
- [X] T015 [US2] Connect `stories_changed` signal to `_restore_selection()` using the preserved `selected_story_id` from ViewModel in src/backlog_manager/presentation/views/main_window.py
- [X] T016 [US2] Ensure `MainWindowViewModel.selected_story_id` is NOT cleared during `load_stories()` so it survives model resets in src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py

**Checkpoint**: US2 complete — selection follows story during move up/down operations without flicker

---

## Phase 5: User Story 3 — Selection Context for Edit and Delete (Priority: P3)

**Goal**: Edit and Delete actions always target the visually highlighted story. After delete, selection moves to the nearest remaining story.

**Independent Test**: Select a story → press Edit → verify dialog shows that story's data. Select a story → press Delete → verify confirmation refers to that story. After delete, verify selection moves to adjacent row.

### Tests for User Story 3

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T017 [P] [US3] Unit test: after delete, verify `selected_story_id` is updated to adjacent story or None (if table empty) in tests/unit/presentation/viewmodels/test_main_window_viewmodel.py
- [X] T018 [P] [US3] Integration test: select row → delete → verify selection moves to adjacent row; delete last story → verify selection clears in tests/integration/presentation/views/test_main_window.py

### Implementation for User Story 3

- [X] T019 [US3] Update `_on_delete_story()` in MainWindow to save row index before delete, then after refresh select `min(old_row, new_row_count - 1)` or clear if table empty in src/backlog_manager/presentation/views/main_window.py
- [X] T020 [US3] Update `MainWindowViewModel` to compute adjacent `story_id` after delete and update `selected_story_id` accordingly in src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py
- [X] T021 [US3] Ensure Edit action reads `selected_story_id` from ViewModel (verify existing implementation targets highlighted row) in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: US3 complete — edit/delete always act on highlighted story, post-delete selection is intuitive

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Edge cases, visual polish, and final validation

- [X] T022 [P] Handle edge case: clear selection when selected story is filtered out by search/filter in src/backlog_manager/presentation/views/main_window.py
- [X] T023 [P] Handle edge case: empty table state — no visual artifacts, all actions disabled in src/backlog_manager/presentation/views/main_window.py
- [X] T024 Verify WCAG AA contrast compliance for selection-bg/selection-fg tokens (ratio ≥ 4.5:1) — visual review per data-model.md calculations
- [X] T025 Run quickstart.md validation commands: `black`, `isort`, `mypy`, full test suite
- [X] T026 Run full application manually — verify visual selection across all scenarios from spec.md acceptance criteria

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **Foundational (Phase 2)**: Depends on Phase 1 (tokens must exist before delegates use them)
- **User Stories (Phase 3+)**: All depend on Foundational phase completion
  - User stories should proceed sequentially in priority order (P1 → P2 → P3) as US2 builds on US1 selection wiring, and US3 builds on US2 restore logic
- **Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Phase 2 — establishes basic selection visual and wiring
- **User Story 2 (P2)**: Depends on US1 (needs selection wiring in place) — adds restore-after-refresh logic
- **User Story 3 (P3)**: Depends on US2 (needs restore logic) — adds post-delete adjacent selection

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- ViewModel logic before View wiring
- Core implementation before edge cases

### Parallel Opportunities

- T003, T004, T005 (all delegates) can run in parallel
- T006, T007 (US1 tests) can run in parallel
- T012, T013 (US2 tests) can run in parallel
- T017, T018 (US3 tests) can run in parallel
- T022, T023 (polish edge cases) can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all delegate updates together (different files, no dependencies):
Task: "T003 Update StatusBadgeDelegate.paint() for selection state"
Task: "T004 Update DependencyIndicatorDelegate.paint() for selection state"
Task: "T005 Update MonospaceDelegate.paint() for selection state"
```

## Parallel Example: User Story 1 Tests

```bash
# Launch both US1 tests together:
Task: "T006 Unit test for selected_story_id update"
Task: "T007 Integration test for click → highlight"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (tokens + QSS)
2. Complete Phase 2: Foundational (delegates)
3. Complete Phase 3: User Story 1 (click → highlight + action disabling)
4. **STOP and VALIDATE**: Click rows, verify visual highlight, verify actions disabled when no selection
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Design tokens and delegates ready
2. Add User Story 1 → Click selection works → MVP!
3. Add User Story 2 → Selection persists during move operations
4. Add User Story 3 → Edit/Delete target correct story, post-delete selection
5. Polish → Edge cases, compliance, final validation
6. Each story adds behavior without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- All changes are in Presentation layer only — no domain/infrastructure changes
- Key files: theme.py (tokens), main_window.py (view), main_window_viewmodel.py (state), delegates (visual consistency)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
