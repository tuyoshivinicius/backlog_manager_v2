# Tasks: EP-017 Design System e Fundacao Visual

**Input**: Design documents from `/specs/017-ep017-design-system/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓

**Tests**: Tests are included in this task list (standard practice for foundation epics).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4, US5)
- Exact file paths included in descriptions

## Path Conventions

- **Source**: `src/backlog_manager/`
- **Tests**: `tests/`
- **Assets**: `src/backlog_manager/assets/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Create directory structure and initialize modules

- [X] T001 Create theme directory at src/backlog_manager/presentation/theme/
- [X] T002 [P] Create __init__.py in src/backlog_manager/presentation/theme/__init__.py
- [X] T003 [P] Create delegates directory at src/backlog_manager/presentation/delegates/
- [X] T004 [P] Create __init__.py in src/backlog_manager/presentation/delegates/__init__.py
- [X] T005 [P] Create assets/icons directory at src/backlog_manager/assets/icons/
- [X] T006 [P] Create test directories at tests/unit/presentation/theme/ and tests/unit/presentation/delegates/
- [X] T007 [P] Create integration test directory at tests/integration/presentation/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core design system infrastructure that MUST be complete before user stories

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T008 Implement DESIGN_TOKENS dictionary with 57 tokens in src/backlog_manager/presentation/theme/theme.py
- [X] T009 Implement StatusConfig dataclass in src/backlog_manager/presentation/theme/theme.py
- [X] T010 Implement STATUS_PALETTE dictionary with 5 status configs in src/backlog_manager/presentation/theme/theme.py
- [X] T011 Implement apply_theme() function with longest-first placeholder substitution in src/backlog_manager/presentation/theme/theme.py
- [X] T012 Implement calculate_contrast_ratio() function for WCAG validation in src/backlog_manager/presentation/theme/theme.py
- [X] T013 [P] Unit test for apply_theme() placeholder substitution in tests/unit/presentation/theme/test_theme.py
- [X] T014 [P] Unit test for calculate_contrast_ratio() correctness in tests/unit/presentation/theme/test_theme.py
- [X] T015 [P] Unit test for STATUS_PALETTE WCAG AA compliance (>= 4.5:1) in tests/unit/presentation/theme/test_theme.py

**Checkpoint**: Foundation ready - design tokens, apply_theme(), and contrast validation available

---

## Phase 3: User Story 1 - Aplicacao Visual Automatica (Priority: P1) 🎯 MVP

**Goal**: All widgets receive modern, consistent styling automatically on startup

**Independent Test**: Start application and verify all widgets display non-default Qt styling

### Tests for User Story 1

- [X] T016 [P] [US1] Unit test for stylesheet.qss placeholder validation (no hardcoded hex) in tests/unit/presentation/theme/test_theme.py
- [X] T017 [P] [US1] Unit test for all @var placeholders have corresponding DESIGN_TOKENS in tests/unit/presentation/theme/test_theme.py
- [X] T018 [P] [US1] Integration test for theme loading and application in tests/integration/presentation/test_theme_integration.py

### Implementation for User Story 1

- [X] T019 [US1] Create stylesheet.qss with placeholder @var syntax in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T020 [US1] Add QSS rules for QMainWindow in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T021 [US1] Add QSS rules for QToolBar and QToolButton (min 32x32px) in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T022 [US1] Add QSS rules for QPushButton (normal, hover, pressed, disabled) in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T023 [US1] Add QSS rules for QLineEdit and QTextEdit in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T024 [US1] Add QSS rules for QComboBox in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T025 [US1] Add QSS rules for QSpinBox and QDateEdit in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T026 [US1] Add QSS rules for QTableView and QHeaderView in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T027 [US1] Add QSS rules for QDialog and QMessageBox in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T028 [US1] Add QSS rules for QScrollBar in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T029 [US1] Add QSS rules for QMenu and QMenuBar in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T030 [US1] Add QSS rules for QTabWidget and QTabBar in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T031 [US1] Add QSS rules for QGroupBox and QLabel in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T032 [US1] Integrate apply_theme() in app startup at src/backlog_manager/presentation/app.py
- [X] T033 [US1] Add error handling for theme loading with fallback in src/backlog_manager/presentation/app.py

**Checkpoint**: Application starts with complete visual styling applied to all widgets

---

## Phase 4: User Story 2 - Badges de Status com Acessibilidade (Priority: P2)

**Goal**: Status column displays colored pill badges with non-chromatic symbols

**Independent Test**: Verify StatusBadgeDelegate renders badges with correct colors and symbols for each status

### Tests for User Story 2

- [X] T034 [P] [US2] Unit test for StatusBadgeDelegate paint() renders correct symbol per status in tests/unit/presentation/delegates/test_status_badge_delegate.py
- [X] T035 [P] [US2] Unit test for StatusBadgeDelegate uses correct colors per status in tests/unit/presentation/delegates/test_status_badge_delegate.py
- [X] T036 [P] [US2] Unit test for StatusBadgeDelegate sizeHint() returns minimum height in tests/unit/presentation/delegates/test_status_badge_delegate.py
- [X] T037 [P] [US2] Unit test for StatusBadgeDelegate handles unknown status gracefully in tests/unit/presentation/delegates/test_status_badge_delegate.py

### Implementation for User Story 2

- [X] T038 [US2] Implement StatusBadgeDelegate class extending QStyledItemDelegate in src/backlog_manager/presentation/delegates/status_badge_delegate.py
- [X] T039 [US2] Implement paint() method with pill shape and symbol rendering in src/backlog_manager/presentation/delegates/status_badge_delegate.py
- [X] T040 [US2] Implement sizeHint() method with minimum badge height in src/backlog_manager/presentation/delegates/status_badge_delegate.py
- [X] T041 [US2] Handle selection state in paint() for proper contrast in src/backlog_manager/presentation/delegates/status_badge_delegate.py
- [X] T042 [US2] Export StatusBadgeDelegate in src/backlog_manager/presentation/delegates/__init__.py

**Checkpoint**: Status badges render with symbols (●▶◆✓✕) and WCAG-compliant colors

---

## Phase 5: User Story 3 - IDs em Fonte Monospace (Priority: P3)

**Goal**: Story IDs display in monospace font for alignment and readability

**Independent Test**: Verify MonospaceDelegate applies correct font family with fallback chain

### Tests for User Story 3

- [X] T043 [P] [US3] Unit test for MonospaceDelegate uses monospace font family in tests/unit/presentation/delegates/test_monospace_delegate.py
- [X] T044 [P] [US3] Unit test for MonospaceDelegate fallback chain (JetBrains Mono -> Cascadia Code -> Consolas) in tests/unit/presentation/delegates/test_monospace_delegate.py

### Implementation for User Story 3

- [X] T045 [US3] Implement MonospaceDelegate class extending QStyledItemDelegate in src/backlog_manager/presentation/delegates/monospace_delegate.py
- [X] T046 [US3] Implement paint() method with monospace font rendering in src/backlog_manager/presentation/delegates/monospace_delegate.py
- [X] T047 [US3] Implement font fallback chain (JetBrains Mono, Cascadia Code, Consolas) in src/backlog_manager/presentation/delegates/monospace_delegate.py
- [X] T048 [US3] Export MonospaceDelegate in src/backlog_manager/presentation/delegates/__init__.py

**Checkpoint**: ID column displays in monospace font with proper fallback

---

## Phase 6: User Story 4 - Focus Ring e Navegacao por Teclado (Priority: P3)

**Goal**: Tab/Shift+Tab navigation shows visible focus indicator (2px solid border)

**Independent Test**: Tab between widgets and verify focus ring appears on each interactive widget

### Tests for User Story 4

- [X] T049 [P] [US4] Unit test for :focus rules present in stylesheet.qss in tests/unit/presentation/theme/test_theme.py

### Implementation for User Story 4

- [X] T050 [US4] Add :focus rules for QPushButton in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T051 [US4] Add :focus rules for QLineEdit in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T052 [US4] Add :focus rules for QComboBox in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T053 [US4] Add :focus rules for QSpinBox and QDateEdit in src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T054 [US4] Add :focus rules for QTableView in src/backlog_manager/presentation/theme/stylesheet.qss

**Checkpoint**: All interactive widgets show 2px solid focus ring on keyboard navigation

---

## Phase 7: User Story 5 - Biblioteca de Icones SVG (Priority: P2)

**Goal**: 16 SVG icons available via IconManager for toolbar and menus

**Independent Test**: Load each icon via QIcon and verify 16x16px rendering without distortion

### Tests for User Story 5

- [X] T055 [P] [US5] Unit test for all 16 SVG files exist in assets/icons/ in tests/unit/presentation/theme/test_theme.py
- [X] T056 [P] [US5] Unit test for IconManager.get() returns valid QIcon for all names in tests/unit/presentation/theme/test_theme.py
- [X] T057 [P] [US5] Unit test for IconManager.get() returns empty QIcon for unknown name in tests/unit/presentation/theme/test_theme.py

### Implementation for User Story 5

- [X] T058 [P] [US5] Download plus.svg from Phosphor Icons to src/backlog_manager/assets/icons/plus.svg
- [X] T059 [P] [US5] Download pencil-simple.svg from Phosphor Icons to src/backlog_manager/assets/icons/pencil-simple.svg
- [X] T060 [P] [US5] Download trash.svg from Phosphor Icons to src/backlog_manager/assets/icons/trash.svg
- [X] T061 [P] [US5] Download arrow-up.svg from Phosphor Icons to src/backlog_manager/assets/icons/arrow-up.svg
- [X] T062 [P] [US5] Download arrow-down.svg from Phosphor Icons to src/backlog_manager/assets/icons/arrow-down.svg
- [X] T063 [P] [US5] Download users.svg from Phosphor Icons to src/backlog_manager/assets/icons/users.svg
- [X] T064 [P] [US5] Download package.svg from Phosphor Icons to src/backlog_manager/assets/icons/package.svg
- [X] T065 [P] [US5] Download gear.svg from Phosphor Icons to src/backlog_manager/assets/icons/gear.svg
- [X] T066 [P] [US5] Download calendar-check.svg from Phosphor Icons to src/backlog_manager/assets/icons/calendar-check.svg
- [X] T067 [P] [US5] Download shuffle.svg from Phosphor Icons to src/backlog_manager/assets/icons/shuffle.svg
- [X] T068 [P] [US5] Download download-simple.svg from Phosphor Icons to src/backlog_manager/assets/icons/download-simple.svg
- [X] T069 [P] [US5] Download upload-simple.svg from Phosphor Icons to src/backlog_manager/assets/icons/upload-simple.svg
- [X] T070 [P] [US5] Download copy.svg from Phosphor Icons to src/backlog_manager/assets/icons/copy.svg
- [X] T071 [P] [US5] Download warning-triangle.svg (warning) from Phosphor Icons to src/backlog_manager/assets/icons/warning-triangle.svg
- [X] T072 [P] [US5] Download link.svg from Phosphor Icons to src/backlog_manager/assets/icons/link.svg
- [X] T073 [P] [US5] Download x.svg from Phosphor Icons to src/backlog_manager/assets/icons/x.svg
- [X] T074 [US5] Implement ICON_NAMES list in src/backlog_manager/presentation/theme/theme.py
- [X] T075 [US5] Implement IconManager class with eager loading in src/backlog_manager/presentation/theme/theme.py
- [X] T076 [US5] Implement IconManager.get(name) method returning QIcon in src/backlog_manager/presentation/theme/theme.py
- [X] T077 [US5] Create icon_manager singleton instance in src/backlog_manager/presentation/theme/theme.py
- [X] T078 [US5] Export IconManager and icon_manager in src/backlog_manager/presentation/theme/__init__.py
- [X] T078.1 [US5] Integrate icon_manager initialization in app startup at src/backlog_manager/presentation/app.py (eager load all 16 icons before MainWindow)

**Checkpoint**: All 16 icons load via icon_manager.get("name") and render at 16x16px. Icons are pre-loaded at app startup (FR-DS-011).

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Integration, validation, and documentation

- [X] T079 [P] Validate zero hardcoded hex values in stylesheet.qss via grep validation in tests/unit/presentation/theme/test_theme.py
- [X] T080 [P] Integration test for delegates with QTableView in tests/integration/presentation/test_delegates_integration.py
- [X] T081 Run all tests and verify 100% pass rate
- [X] T082 Validate quickstart.md examples work correctly
- [X] T083 [P] Performance test: StatusBadgeDelegate renders in <= 16ms per cell

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phases 3-7)**: All depend on Foundational phase completion
  - US1 (Phase 3): Can proceed independently after Foundational
  - US2 (Phase 4): Can proceed independently after Foundational
  - US3 (Phase 5): Can proceed independently after Foundational
  - US4 (Phase 6): Depends on US1 stylesheet.qss existing
  - US5 (Phase 7): Can proceed independently after Foundational
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Foundational only - creates stylesheet.qss used by US4
- **User Story 2 (P2)**: Foundational only - independent
- **User Story 3 (P3)**: Foundational only - independent
- **User Story 4 (P3)**: Depends on US1 (stylesheet.qss must exist)
- **User Story 5 (P2)**: Foundational only - independent

### Within Each User Story

- Tests written and failing before implementation
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1 (Setup)**: T002-T007 all [P] - run in parallel
- **Phase 2 (Foundational)**: T013-T015 all [P] - run in parallel after T008-T012
- **Phase 3 (US1)**: T016-T018 [P] tests in parallel
- **Phase 4 (US2)**: T034-T037 [P] tests in parallel
- **Phase 5 (US3)**: T043-T044 [P] tests in parallel
- **Phase 7 (US5)**: T055-T057 [P] tests, T058-T073 [P] icon downloads all in parallel
- **Cross-Story**: US2, US3, US5 can run in parallel after Foundational

---

## Parallel Example: Phase 7 (User Story 5)

```bash
# Launch all icon downloads in parallel (16 tasks):
Task: "Download plus.svg"
Task: "Download pencil-simple.svg"
Task: "Download trash.svg"
# ... all 16 downloads in parallel

# Then implement IconManager:
Task: "Implement ICON_NAMES list"
Task: "Implement IconManager class"
Task: "Export in __init__.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (7 tasks)
2. Complete Phase 2: Foundational (8 tasks)
3. Complete Phase 3: User Story 1 (18 tasks)
4. **STOP and VALIDATE**: Application displays styled widgets
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test app styling → Demo (MVP!)
3. Add User Story 2 → Test status badges → Demo
4. Add User Story 5 → Test icons → Demo
5. Add User Story 3 → Test monospace IDs → Demo
6. Add User Story 4 → Test focus rings → Demo
7. Polish phase → Final validation

### Parallel Team Strategy

With multiple developers after Foundational:
- Developer A: User Story 1 (stylesheet.qss)
- Developer B: User Story 2 (StatusBadgeDelegate)
- Developer C: User Story 5 (Icons)

Then:
- Developer A: User Story 4 (depends on US1)
- Developer B: User Story 3 (MonospaceDelegate)

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 84 |
| **Setup Tasks** | 7 |
| **Foundational Tasks** | 8 |
| **US1 Tasks** | 18 |
| **US2 Tasks** | 9 |
| **US3 Tasks** | 6 |
| **US4 Tasks** | 6 |
| **US5 Tasks** | 25 |
| **Polish Tasks** | 5 |
| **Parallelizable Tasks** | 54 (65%) |
| **MVP Scope** | Phases 1-3 (33 tasks) |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story independently testable
- Tests before implementation (TDD)
- Commit after each task or logical group
- Stop at any checkpoint to validate independently
