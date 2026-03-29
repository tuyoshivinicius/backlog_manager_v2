# Tasks: EP-020 — Busca, Filtros e Menu de Contexto

**Input**: Design documents from `/specs/020-busca-filtros-menu-contexto/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/ui-contracts.md, research.md, quickstart.md

**Tests**: Included — spec requires >= 80% coverage for FilterProxyModel (SC-008) and constitution mandates tests (Principio XIV).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `src/backlog_manager/presentation/`
- **Tests**: `tests/unit/presentation/`, `tests/integration/presentation/`

---

## Phase 1: Setup

**Purpose**: No setup needed — project structure, dependencies, and DuplicateStoryUseCase already exist from prior EPs.

*(No tasks — EP-018/019 provide all prerequisites)*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Create FilterProxyModel and integrate proxy into MainWindow — MUST be complete before ANY user story can be implemented.

**CRITICAL**: No user story work can begin until this phase is complete.

- [x] T001 Create FilterProxyModel with text/status/feature filters and AND logic in `src/backlog_manager/presentation/viewmodels/filter_proxy_model.py`
  - Subclass QSortFilterProxyModel
  - Resolve column indices via StoryTableModel.COLUMNS.index() in __init__ (_col_id, _col_component, _col_name, _col_status, _col_feature)
  - Implement set_text_filter(text: str), set_status_filter(status: str | None), set_feature_filter(feature_id: int | None) — each calls invalidateFilter()
  - Implement filterAcceptsRow() with AND logic: text filter checks ID/Nome/Componente (case-insensitive), status checks Status column, feature uses source_model.get_story_at(source_row).feature_id
  - Property has_active_filters: bool — True if any filter != default
- [x] T002 Write unit tests for FilterProxyModel in `tests/unit/presentation/test_filter_proxy_model.py`
  - Test text filter (case-insensitive, multi-column match)
  - Test status filter (exact match, None = all)
  - Test feature filter (by feature_id, None = all)
  - Test AND combination of all 3 filters
  - Test has_active_filters property
  - Test invalidateFilter is called on each set_*_filter
  - Target >= 80% coverage (SC-008)
- [x] T003 Integrate FilterProxyModel into MainWindow in `src/backlog_manager/presentation/views/main_window.py`
  - Create FilterProxyModel instance in _setup_central_widget()
  - Call proxy.setSourceModel(viewmodel.table_model)
  - Call view.setModel(proxy) BEFORE configuring delegates
  - Reconfigure delegates (MonospaceDelegate col 3, StatusBadgeDelegate col 6) AFTER setModel(proxy) per ADR-001
  - Verify existing selection/data flows work through proxy (use proxy.data(index, UserRole) for story_id)

**Checkpoint**: FilterProxyModel created, tested, and integrated. Delegates render correctly. All existing functionality preserved.

---

## Phase 3: User Story 1 — Busca Incremental por Texto (Priority: P1) MVP

**Goal**: User types in search field to filter stories by ID, name, or component in real-time with 150ms debounce.

**Independent Test**: Type text in search field and verify table shows only matching stories (case-insensitive across ID, Nome, Componente columns).

### Implementation for User Story 1

- [x] T004 [US1] Add SearchField widget to zona 3 (_filter_bar) in `src/backlog_manager/presentation/views/main_window.py`
  - Create QLineEdit with objectName="searchField", fixedWidth=240, placeholderText="Buscar por ID, nome ou componente...", clearButtonEnabled=True
  - Add search icon via search_field.addAction(QIcon.fromTheme("edit-find"), QLineEdit.LeadingPosition) or local theme icon
  - Add QHBoxLayout to existing _filter_bar widget (zona 3, 36px height per ADR-006)
  - Add SearchField as first widget in the layout
- [x] T005 [US1] Implement debounce timer and connect search to proxy in `src/backlog_manager/presentation/views/main_window.py`
  - Create QTimer (singleShot=True, interval=150ms) per R-002
  - Connect QLineEdit.textChanged → store pending text + timer.start()
  - Connect timer.timeout → proxy.set_text_filter(pending_text)
- [x] T006 [US1] Add Ctrl+F shortcut to focus SearchField in `src/backlog_manager/presentation/views/main_window.py`
  - Register QShortcut(Ctrl+F) → search_field.setFocus()

**Checkpoint**: User Story 1 fully functional — search field filters table in real-time with debounce.

---

## Phase 4: User Story 2 — Filtro Rapido por Status (Priority: P1)

**Goal**: User clicks status chips to filter stories by state. Each chip shows total count.

**Independent Test**: Click each chip and verify table shows only stories of that status, with correct counts.

### Implementation for User Story 2

- [x] T007 [US2] Add 6 FilterChip buttons and QButtonGroup to zona 3 in `src/backlog_manager/presentation/views/main_window.py`
  - Create 6 QPushButton (checkable=True) with setProperty("class", "filterChip") for QSS matching: Todos(None), Backlog("BACKLOG"), Execucao("EXECUCAO"), Testes("TESTES"), Concluido("CONCLUIDO"), Impedido("IMPEDIDO")
  - Add to QButtonGroup with exclusive=True
  - "Todos" checked by default
  - Add chips to zona 3 layout after SearchField with spacer between
- [x] T008 [US2] Connect chips to proxy filter and implement count updates in `src/backlog_manager/presentation/views/main_window.py`
  - Connect QButtonGroup.buttonClicked → proxy.set_status_filter(chip.property("status_value"))
  - Connect ViewModel.stories_changed → _update_chip_counts()
  - _update_chip_counts(): iterate ViewModel.stories, count per status, update chip text "Label (N)" per ADR-002

**Checkpoint**: User Story 2 fully functional — status chips filter table and show correct counts.

---

## Phase 5: User Story 3 — Menu de Contexto na Tabela (Priority: P2)

**Goal**: Right-click on table row opens context menu with Edit, Duplicate, Move Up/Down, Dependencies, Delete actions.

**Independent Test**: Right-click on a row and verify menu appears with 6 actions, correct separators, and each action triggers the expected operation.

### Implementation for User Story 3

- [x] T009 [US3] Implement context menu with 6 actions in `src/backlog_manager/presentation/views/main_window.py` (Depends on: T014 — _on_duplicate_story slot must exist)
  - Set customContextMenuPolicy on StoryTableView
  - Connect customContextMenuRequested → _on_context_menu(pos)
  - _on_context_menu: validate index, select row, create ephemeral QMenu per R-005
  - Add actions: Editar (Enter), Duplicar (Ctrl+D), separator, Mover Acima (Alt+Up), Mover Abaixo (Alt+Down), separator, Dependencias..., separator, Deletar (Delete)
  - "Deletar" action: set property destructive="true" for QSS styling
  - Mover Acima/Abaixo: setEnabled(not proxy.has_active_filters) per R-007
  - Connect each action to existing slots (_on_edit_story, _on_duplicate_story, _on_move_up, _on_move_down, _open_dependency_dialog, _on_delete_story)
  - Do NOT show menu on right-click in empty area (check index.isValid())
- [x] T010 [US3] Implement delete confirmation dialog in `src/backlog_manager/presentation/views/main_window.py`
  - Add QMessageBox.question before all delete paths (toolbar, Delete key, menu de contexto) per C-006
  - Title: "Confirmar exclusao", text: "Deseja realmente excluir a historia {story_id}?"
  - Default button: No. Only proceed if Yes.
- [x] T011 [US3] Implement move actions state management in `src/backlog_manager/presentation/views/main_window.py`
  - Create _update_move_actions_state() method per C-005
  - Disable _action_move_up and _action_move_down when proxy.has_active_filters or no selection
  - Call _update_move_actions_state() after each filter change and selection change

**Checkpoint**: User Story 3 fully functional — context menu works with all 6 actions, delete has confirmation, move disabled with active filters.

---

## Phase 6: User Story 4 — Duplicar Historia (Priority: P2)

**Goal**: User duplicates selected story via toolbar button, context menu, or Ctrl+D with feedback in Status Bar.

**Independent Test**: Select a story, press Ctrl+D, verify new story appears with correct data and Status Bar shows feedback.

### Implementation for User Story 4

- [x] T012 [US4] Add duplicate_story() async method to MainWindowViewModel in `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`
  - Follow identical pattern to create_story/edit_story/delete_story per ADR-004 and R-008
  - async def duplicate_story(self, story_id: str) -> StoryOutputDTO | None
  - Use DuplicateStoryUseCase from DIContainer
  - Try/except with _set_loading(), _handle_error(), stories_changed.emit()
  - Return the duplicated StoryOutputDTO
- [x] T013 [US4] Write unit tests for duplicate_story in `tests/unit/presentation/test_main_window_viewmodel.py`
  - Test successful duplication returns new DTO
  - Test stories_changed signal emitted after duplication
  - Test error handling on duplication failure
- [x] T014 [US4] Add Duplicar QAction to toolbar and connect Ctrl+D shortcut in `src/backlog_manager/presentation/views/main_window.py`
  - Add QAction "Duplicar" with copy icon to toolbar Grupo 1 (beside "Nova Historia") per ADR-008
  - Set shortcut Ctrl+D on the QAction
  - Connect to _on_duplicate_story() slot
  - _on_duplicate_story: check selection, get story_id, asyncio.create_task(viewmodel.duplicate_story(story_id))
  - On success: Status Bar shows "Historia duplicada: {id_original} -> {id_copia}" per FR-019
  - If no selection: noop

**Checkpoint**: User Story 4 fully functional — duplicate works from toolbar/menu/shortcut with Status Bar feedback.

---

## Phase 7: User Story 5 — Filtro por Feature/Onda (Priority: P3)

**Goal**: User selects feature from dropdown to filter stories. Features grouped by wave as "Onda N - Nome".

**Independent Test**: Select a feature in dropdown and verify table shows only stories of that feature.

### Implementation for User Story 5

- [x] T015 [US5] Add FeatureCombo (QComboBox) to zona 3 and connect to proxy in `src/backlog_manager/presentation/views/main_window.py`
  - Create QComboBox in zona 3 layout (after chips, with spacer)
  - First item: "Todas as features" (data=None)
  - Connect currentIndexChanged → proxy.set_feature_filter(combo.currentData())
  - Connect ViewModel.stories_changed → _update_feature_dropdown()
  - _update_feature_dropdown(): extract unique (feature_id, feature_name, wave) from ViewModel.stories, sort by wave, populate combo as "Onda N - Nome" per R-004 and ADR-005

**Checkpoint**: User Story 5 fully functional — feature dropdown filters table by feature/wave.

---

## Phase 8: User Story 6 — Filtros Compostos (Priority: P3)

**Goal**: Text, status, and feature filters combine with AND logic. All three can be active simultaneously.

**Independent Test**: Apply text search + status chip + feature dropdown simultaneously and verify only stories matching ALL criteria appear.

### Implementation for User Story 6

- [x] T016 [US6] Write integration tests for composite filters in `tests/integration/presentation/test_main_window_filters.py`
  - Test text + status filter combination (AND)
  - Test text + feature filter combination (AND)
  - Test status + feature filter combination (AND)
  - Test all three filters simultaneously (AND)
  - Test clearing one filter while others remain active
  - Test chip counts remain total (not filtered) when other filters active
  - Test move actions disabled with any combination of active filters
- [x] T017 [US6] Verify and fix composite filter interactions in `src/backlog_manager/presentation/views/main_window.py`
  - Ensure all filter changes route through same proxy instance
  - Ensure _update_move_actions_state() called on every filter change
  - Ensure chip counts always use ViewModel.stories (unfiltered source of truth)

**Checkpoint**: User Story 6 verified — all filter combinations work correctly with AND logic.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: QSS styles, visual polish, and final validation

- [x] T018 [P] Add QSS styles for search field, filter chips, and destructive menu action in `src/backlog_manager/presentation/theme/stylesheet.qss`
  - #searchField: padding-left for icon, min-width/max-width 240px
  - QPushButton[class="filterChip"]: bg @surface, text @text-secondary, border-radius @radius-full, padding @spacing-1 @spacing-3, font-size @font-size-xs
  - QPushButton[class="filterChip"]:checked: bg @primary, text white, border @primary
  - QPushButton[class="filterChip"]:hover:!checked: bg @neutral-100, border @neutral-300
  - QMenu::item[destructive="true"]: color @error-fg
- [x] T019 Run quickstart.md validation — execute all test commands and verify all acceptance scenarios pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: N/A — already complete from prior EPs
- **Foundational (Phase 2)**: BLOCKS all user stories — FilterProxyModel + proxy integration must be done first
- **US1 (Phase 3)**: Depends on Phase 2 — text search requires FilterProxyModel
- **US2 (Phase 4)**: Depends on Phase 2 — status chips require FilterProxyModel
- **US3 (Phase 5)**: Depends on Phase 2 — move disable requires has_active_filters. Also depends on US4 (T012) for _on_duplicate_story slot
- **US4 (Phase 6)**: Depends on Phase 2 only — duplicate is independent of filters
- **US5 (Phase 7)**: Depends on Phase 2 — feature dropdown requires FilterProxyModel
- **US6 (Phase 8)**: Depends on US1, US2, US5 — composite filters test all three
- **Polish (Phase 9)**: Can start QSS (T018) after Phase 2; validation (T019) after all phases

### User Story Dependencies

- **US1 (P1)**: Phase 2 only — independent of other stories
- **US2 (P1)**: Phase 2 only — independent of other stories
- **US3 (P2)**: Phase 2 + US4 (needs _on_duplicate_story slot from T014)
- **US4 (P2)**: Phase 2 only — independent of other stories
- **US5 (P3)**: Phase 2 only — independent of other stories
- **US6 (P3)**: US1 + US2 + US5 — validates integration of all filters

### Within Each User Story

- Tests written alongside or after implementation
- Proxy model (Phase 2) before filter widgets (Phases 3-7)
- ViewModel methods (T012) before View slots (T014)
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run sequentially (T002 tests T001)
- T004, T005, T006 within US1 are sequential (same file, dependent)
- US1 (Phase 3) and US2 (Phase 4) can run in parallel after Phase 2 (different parts of zona 3)
- US4 (Phase 6) can run in parallel with US1/US2 (different files: viewmodel vs view)
- T012 [US4] and T007 [US2] can run in parallel (different files)
- T018 (QSS) can run in parallel with any implementation phase after Phase 2

---

## Parallel Example: After Phase 2

```bash
# These can run in parallel (different files or independent areas):
# Stream A: US1 — SearchField + debounce in main_window.py (zona 3)
# Stream B: US4 — duplicate_story() in main_window_viewmodel.py
# Stream C: T018 — QSS styles in stylesheet.qss

# After US1 + US2 + US5 complete:
# US6 integration tests validate all filters together
```

---

## Implementation Strategy

### MVP First (US1 + US2)

1. Complete Phase 2: FilterProxyModel + proxy integration
2. Complete Phase 3: US1 — Busca Incremental
3. Complete Phase 4: US2 — Filtro por Status
4. **STOP and VALIDATE**: Search + status filter work independently
5. Continue with US3/US4 (menu de contexto + duplicar)

### Incremental Delivery

1. Phase 2 (FilterProxyModel) → Foundation ready
2. US1 (busca) → Search works independently
3. US2 (status chips) → Status filter works independently
4. US4 (duplicar) → Duplication works from toolbar
5. US3 (menu contexto) → Context menu with all actions
6. US5 (feature dropdown) → Feature filter works independently
7. US6 (compostos) → All filters validated together
8. Phase 9 (polish) → QSS styles + final validation

---

## Summary

- **Total tasks**: 19
- **Phase 2 (Foundational)**: 3 tasks (T001-T003)
- **US1 (Busca)**: 3 tasks (T004-T006)
- **US2 (Status)**: 2 tasks (T007-T008)
- **US3 (Menu Contexto)**: 3 tasks (T009-T011)
- **US4 (Duplicar)**: 3 tasks (T012-T014)
- **US5 (Feature/Onda)**: 1 task (T015)
- **US6 (Compostos)**: 2 tasks (T016-T017)
- **Polish**: 2 tasks (T018-T019)
- **Parallel opportunities**: US1/US2/US4 after Phase 2; T018 (QSS) anytime after Phase 2
- **Suggested MVP**: Phase 2 + US1 + US2 (8 tasks)

## Notes

- All source modifications are in Presentation layer only — no Domain/Application/Infrastructure changes
- Only 1 new production file: filter_proxy_model.py. All other changes modify existing files
- DuplicateStoryUseCase already exists — only ViewModel integration needed
- Proxy model indices: use StoryTableModel.COLUMNS.index() — never hardcode column numbers
- Delegates must be configured AFTER view.setModel(proxy) — order matters (ADR-001)
