# Tasks: EP-018 — Layout Principal e Migração de Painéis

**Input**: Design documents from `/specs/018-ep018-layout-migracao-paineis/`
**Prerequisites**: plan.md, spec.md, data-model.md, research.md, quickstart.md

**Tests**: Included — project constitution (Princípio XIV) requires tests, and plan.md explicitly lists test files to create/modify.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare stylesheet and container for new components

- [X] T001 Add QMenuBar, QToolBar, QStatusBar, and dialog styles to src/backlog_manager/presentation/theme/stylesheet.qss
- [X] T002 [P] Register ConfigDialogViewModel, DependencyDialogViewModel, and StatusBarViewModel in src/backlog_manager/presentation/container.py

---

## Phase 2: US2 — Layout Vertical com Tabela Expandida (Priority: P1) 🎯 MVP

**Goal**: Refatorar MainWindow para layout vertical de 5 zonas, removendo QSplitter horizontal e painéis laterais, tabela ocupando 100% da largura.

**Independent Test**: Iniciar a aplicação e verificar que a tabela ocupa toda a largura da área central sem divisores laterais.

### Implementation for User Story 2

- [X] T003 [US2] Refactor _setup_central_widget() in src/backlog_manager/presentation/views/main_window.py — remove QSplitter horizontal, remove ConfigPanel/DependencyPanel/MetricsPanel/WarningsPanel imports and instantiation. Verify per FR-025: legacy files (config_panel.py, dependency_panel.py, metrics_panel.py, warnings_panel.py) are kept on disk but no longer imported
- [X] T004 [US2] Implement QVBoxLayout in central widget with filter bar placeholder (36px QWidget) and StoryTableView (stretch) in src/backlog_manager/presentation/views/main_window.py
- [X] T005 [US2] Update tests/integration/presentation/views/test_main_window.py — adapt existing layout tests for new 5-zone vertical structure

**Checkpoint**: Layout vertical funcional, tabela 100% largura, sem painéis laterais. Aplicação inicia e exibe tabela corretamente.

---

## Phase 3: US1 — Navegação por Menu Bar (Priority: P1)

**Goal**: Adicionar Menu Bar profissional com 4 menus (Arquivo, Cadastros, Ferramentas, Ajuda) e atalhos de teclado visíveis.

**Independent Test**: Navegar pelos 4 menus e verificar que cada ação executa corretamente com atalhos funcionais.

### Implementation for User Story 1

- [X] T006 [US1] Implement _setup_menu_bar() in src/backlog_manager/presentation/views/main_window.py — create 4 menus (Arquivo, Cadastros, Ferramentas, Ajuda) with QActions and QKeySequence shortcuts per data-model.md sections 3.1-3.4
- [X] T007 [US1] Connect menu actions to existing handler methods (_import_action, _export_action, _new_story_action, _features_action, _developers_action, _schedule_action, _allocate_action) in src/backlog_manager/presentation/views/main_window.py — NOTE: _config_action will be a stub (no-op or pass) until T019 connects it to ConfigDialog in Phase 6
- [X] T008 [US1] Add Sair action (close) and Sobre placeholder (disabled) in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: Menu Bar funcional com 4 menus, todos atalhos de teclado (Ctrl+N, Ctrl+I, Ctrl+E, Ctrl+Shift+C, Ctrl+Shift+A) funcionando.

---

## Phase 4: US3 — Toolbar com Ícones e Grupos (Priority: P2)

**Goal**: Refatorar toolbar com ícones SVG do design system, botões com texto ao lado, e 5 grupos separados por separadores visuais.

**Independent Test**: Verificar que cada botão da toolbar exibe ícone + texto, com separadores visíveis entre os 5 grupos.

### Implementation for User Story 3

- [X] T009 [US3] Refactor _setup_toolbar() in src/backlog_manager/presentation/views/main_window.py — set ToolButtonTextBesideIcon style, iconSize 20x20, add icons via IconManager.get() for all buttons per data-model.md section 4 (Toolbar Groups)
- [X] T010 [US3] Add toolbar separators between 5 groups (CRUD, Priorização, Cadastros, Processamento, Excel) and set tooltips per FR-008 format "Descrição (Atalho)" (e.g., "Nova História (Ctrl+N)") for all buttons with shortcuts in src/backlog_manager/presentation/views/main_window.py

**Checkpoint**: Toolbar exibe 12 botões com ícones SVG em 5 grupos separados, tooltips incluem atalhos.

---

## Phase 5: US4 — Status Bar com Contadores e Avisos (Priority: P2)

**Goal**: Criar Status Bar com contadores de backlog à esquerda e badge de warnings à direita, substituindo WarningsPanel.

**Independent Test**: Executar uma alocação e verificar que contadores e avisos aparecem na Status Bar.

### Implementation for User Story 4

- [X] T011 [P] [US4] Create StatusBarViewModel in src/backlog_manager/presentation/viewmodels/status_bar_viewmodel.py — properties: story_count, total_sp, last_allocation, warning_count, warnings; signals: stats_changed, warnings_changed; methods: update_stats(), set_last_allocation(), set_warnings()
- [X] T012 [P] [US4] Create status bar view components (StatsLabel, WarningsBadge) in src/backlog_manager/presentation/views/status_bar.py — StatsLabel format "X histórias · Y SP · Última alocação: DD/MM/YYYY HH:MM", WarningsBadge as QPushButton with popup, hidden when count == 0
- [X] T013 [US4] Implement _setup_status_bar() in src/backlog_manager/presentation/views/main_window.py — add StatsLabel via addWidget() and WarningsBadge via addPermanentWidget()
- [X] T014 [US4] Connect status bar signals: stories_changed → update stats, warnings_updated → update badge, badge click → show warnings popup in src/backlog_manager/presentation/views/main_window.py
- [X] T015 [P] [US4] Create unit tests in tests/unit/presentation/viewmodels/test_status_bar_viewmodel.py — test update_stats(), set_warnings(), stats_changed signal, warnings visibility
- [X] T016 [US4] Create integration tests in tests/integration/presentation/views/test_status_bar.py — test label formatting, badge visibility toggle, popup interaction. Edge cases: empty backlog shows "0 histórias · 0 SP · Sem alocação", large warnings list has scroll in popup

**Checkpoint**: Status Bar exibe contadores atualizados em tempo real, badge de warnings funcional com popup.

---

## Phase 6: US5 — ConfigDialog Modal (Priority: P2)

**Goal**: Criar dialog modal para configuração de parâmetros de alocação (velocidade, data início, max dias ociosos), acessível pelo menu Cadastros.

**Independent Test**: Abrir ConfigDialog via menu, alterar valores e verificar que são aplicados.

### Implementation for User Story 5

- [X] T017 [P] [US5] Create ConfigDialogViewModel in src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py — properties: velocity (0.1-10.0), start_date, max_idle_days (2-30); methods: validate(), save(); signals: saved, error_occurred
- [X] T018 [US5] Create ConfigDialog in src/backlog_manager/presentation/views/config_dialog.py — modal 420x340px, QDoubleSpinBox for velocity, QDateEdit for start_date, QSpinBox for max_idle_days, Aplicar/Cancelar buttons, validation error display
- [X] T019 [US5] Connect _config_action in menu Cadastros to open ConfigDialog in src/backlog_manager/presentation/views/main_window.py
- [X] T020 [P] [US5] Create unit tests in tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py — test validate() boundaries, save(), error signals
- [X] T021 [US5] Create integration tests in tests/integration/presentation/views/test_config_dialog.py — test dialog open/close, apply valid values, reject invalid velocity (0)

**Checkpoint**: ConfigDialog acessível via menu, validação funcional, valores aplicados corretamente.

---

## Phase 7: US6 — DependencyDialog Modal (Priority: P2)

**Goal**: Criar dialog modal para gestão de dependências de uma história, acessível via menu de contexto (right-click) na tabela.

**Independent Test**: Selecionar história, abrir DependencyDialog via right-click, adicionar/remover dependências e verificar detecção de ciclos.

### Implementation for User Story 6

- [X] T022 [P] [US6] Create DependencyDialogViewModel in src/backlog_manager/presentation/viewmodels/dependency_dialog_viewmodel.py — properties: story_id, story_name, depends_on, dependents, available_stories, has_cycle_error; methods: async load_dependencies(), async add_dependency(), async remove_dependency(); signals: dependencies_changed, cycle_detected
- [X] T023 [US6] Create DependencyDialog in src/backlog_manager/presentation/views/dependency_dialog.py — modal 500x420px, title "Dependências: {ID} - {Name}", QListWidget for depends_on (editable) and dependents (readonly), QComboBox for available_stories, cycle error with red background (#FFEEEE)
- [X] T024 [US6] Implement context menu on StoryTableView in src/backlog_manager/presentation/views/main_window.py — setContextMenuPolicy(CustomContextMenu), customContextMenuRequested → show QMenu with "Dependências" option → open DependencyDialog for selected story
- [X] T025 [P] [US6] Create unit tests in tests/unit/presentation/viewmodels/test_dependency_dialog_viewmodel.py — test load_dependencies(), add/remove dependency, cycle detection signal
- [X] T026 [US6] Update tests in tests/integration/presentation/views/test_dependency_dialog.py — test dialog open with story context, add/remove dependencies, cycle error display

**Checkpoint**: DependencyDialog funcional via right-click, detecção de ciclos com feedback visual.

---

## Phase 8: US7 — MetricsDialog Auto-Show Pós-Alocação (Priority: P3)

**Goal**: Criar dialog modal que exibe métricas da alocação automaticamente após execução bem-sucedida.

**Independent Test**: Executar alocação bem-sucedida e verificar que MetricsDialog surge automaticamente com métricas.

### Implementation for User Story 7

- [X] T027 [US7] Create MetricsDialog in src/backlog_manager/presentation/views/metrics_dialog.py — modal 440x380px, grid display for: stories_allocated, execution_time, waves_processed, total_iterations, deadlocks_detected, idle_violations (per data-model.md section 1.4). NOTE: No ViewModel needed — dialog is read-only display, receives data via constructor args (Princípio IX Simplicidade)
- [X] T028 [US7] Connect allocation_completed signal to auto-show MetricsDialog in src/backlog_manager/presentation/views/main_window.py — only show if stories_allocated > 0, do NOT show on error or 0 allocations (FR-021/FR-022). Verify FR-026: EP-008 progress indicator behavior is preserved during allocation execution
- [X] T029 [US7] Create integration tests in tests/integration/presentation/views/test_metrics_dialog.py — test dialog displays metrics correctly, auto-show on success, no-show on failure/zero allocations

**Checkpoint**: MetricsDialog surge automaticamente após alocação bem-sucedida com todas as métricas visíveis.

---

## Phase 9: US8 — Integração de Delegates na Tabela (Priority: P3)

**Goal**: Aplicar delegates de formatação profissional nas colunas da tabela: ID em monospace, Status como badges coloridos.

**Independent Test**: Verificar que coluna ID usa fonte monospace e coluna Status renderiza badges coloridos.

### Implementation for User Story 8

- [X] T030 [US8] Integrate StatusBadgeDelegate and MonospaceDelegate in _setup_central_widget() of src/backlog_manager/presentation/views/main_window.py — lookup column indices dynamically from StoryTableModel (do NOT hardcode indices). Apply MonospaceDelegate for ID column, StatusBadgeDelegate for Status column

**Checkpoint**: Coluna ID em monospace (JetBrains Mono ou fallback), Status como badges coloridos com símbolos.

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Validação final e ajustes que afetam múltiplas user stories

- [X] T031 Validate layout at minimum resolution 1366x768 — verify no cuts or overlaps (SC-006)
- [X] T032 [P] Verify all keyboard shortcuts work without conflicts on Windows (SC-001)
- [X] T033 [P] Verify dialog open time ≤ 100ms for ConfigDialog, DependencyDialog, MetricsDialog (SC-003)
- [X] T034 Verify cold start time ≤ 3s with new layout (SC-004)
- [X] T035 Run quickstart.md validation checklist — all items pass

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — can start immediately
- **US2 Layout (Phase 2)**: Depends on Setup — BLOCKS all other user stories (foundational layout refactoring)
- **US1 Menu Bar (Phase 3)**: Depends on US2 (layout must exist to add menu bar)
- **US3 Toolbar (Phase 4)**: Depends on US2 (toolbar refactoring needs new layout context)
- **US4 Status Bar (Phase 5)**: Depends on US2 (status bar added to new layout)
- **US5 ConfigDialog (Phase 6)**: Depends on US1 (menu action triggers dialog) + Setup (ViewModel registered)
- **US6 DependencyDialog (Phase 7)**: Depends on US2 (context menu on table) + Setup (ViewModel registered)
- **US7 MetricsDialog (Phase 8)**: Depends on US2 (allocation signal connection)
- **US8 Delegates (Phase 9)**: Depends on US2 (table must be in new layout)
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **US2 (P1)**: Foundational — must complete first. No dependencies on other stories.
- **US1 (P1)**: Depends on US2 layout. No dependencies on other stories.
- **US3 (P2)**: Depends on US2 layout. Can run in parallel with US1, US4, US5, US6.
- **US4 (P2)**: Depends on US2 layout. Can run in parallel with US1, US3, US5, US6.
- **US5 (P2)**: Depends on US1 (menu) + US2 (layout). Can run in parallel with US3, US4, US6.
- **US6 (P2)**: Depends on US2 layout. Can run in parallel with US1, US3, US4, US5.
- **US7 (P3)**: Depends on US2 layout. Can run in parallel with US8.
- **US8 (P3)**: Depends on US2 layout. Can run in parallel with US7.

### Within Each User Story

- ViewModels before Views (ViewModel is dependency of View)
- Views before main_window.py integration
- Implementation before tests (tests validate implementation)
- Story complete before moving to next priority

### Parallel Opportunities

- **Phase 1**: T001 and T002 can run in parallel (different files)
- **Phase 5 (US4)**: T011 and T012 can run in parallel (different files: ViewModel vs View)
- **Phase 6 (US5)**: T017 can run in parallel with T022 (different files: ConfigDialogVM vs DependencyDialogVM)
- **Phase 7 (US6)**: T022 can run in parallel with T017 (different ViewModels)
- **After US2 completes**: US1, US3, US4, US6, US7, US8 can all start (though US3/US4 modify main_window.py so should be sequential with each other)
- **P3 stories**: US7 and US8 can run fully in parallel (different files)

---

## Parallel Example: After US2 Completes

```text
# Parallel track A (main_window.py modifications — sequential):
T006-T008: US1 Menu Bar
T009-T010: US3 Toolbar
T013-T014: US4 Status Bar integration
T024: US6 Context menu
T028: US7 MetricsDialog auto-show
T030: US8 Delegates

# Parallel track B (new files — can run alongside track A):
T011+T012: US4 StatusBarViewModel + status_bar.py
T017: US5 ConfigDialogViewModel
T018: US5 ConfigDialog view
T022: US6 DependencyDialogViewModel
T023: US6 DependencyDialog view
T027: US7 MetricsDialog view
```

---

## Implementation Strategy

### MVP First (US2 + US1 Only)

1. Complete Phase 1: Setup (stylesheet + container)
2. Complete Phase 2: US2 Layout Vertical (foundational refactoring)
3. Complete Phase 3: US1 Menu Bar
4. **STOP and VALIDATE**: Aplicação inicia com layout vertical, menu bar funcional, tabela 100% largura
5. Demo-ready com navegação profissional

### Incremental Delivery

1. Setup + US2 Layout → Foundational layout ready
2. Add US1 Menu Bar → Professional navigation → **MVP!**
3. Add US3 Toolbar + US4 Status Bar → Visual polish + live feedback
4. Add US5 ConfigDialog + US6 DependencyDialog → Panels migrated to dialogs
5. Add US7 MetricsDialog + US8 Delegates → Final experience improvements
6. Polish → Validation and performance verification

### Suggested Execution Order (Single Developer)

1. T001-T002 (Setup)
2. T003-T005 (US2 Layout — foundational)
3. T006-T008 (US1 Menu Bar)
4. T009-T010 (US3 Toolbar)
5. T011-T016 (US4 Status Bar)
6. T017-T021 (US5 ConfigDialog)
7. T022-T026 (US6 DependencyDialog)
8. T027-T029 (US7 MetricsDialog)
9. T030 (US8 Delegates)
10. T031-T035 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Legacy panels (config_panel.py, dependency_panel.py, metrics_panel.py, warnings_panel.py) are kept but removed from imports per FR-025
- Icons from EP-017 (assets/icons/) are assumed available and functional
- StatusBadgeDelegate and MonospaceDelegate from EP-017 are assumed implemented
- Filter bar (36px placeholder) will be implemented in EP-020
- Menu Ajuda > Sobre will be implemented in EP-022
