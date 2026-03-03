# Tasks: EP-008 Interface Grafica

**Input**: Design documents from `/specs/008-ep008-graphical-interface/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Tests included as specified in spec.md (ViewModels >= 80%, Views >= 50%)

**Organization**: Tasks grouped by user story to enable independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Source**: `src/backlog_manager/presentation/`
- **Tests Unit**: `tests/unit/presentation/`
- **Tests Integration**: `tests/integration/presentation/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, dependencies, and basic structure

- [X] T001 Update pyproject.toml with PySide6 ^6.6.1, qasync ^0.27.1, pytest-qt ^4.4
- [X] T002 [P] Add entry point in pyproject.toml: backlog-manager = "backlog_manager.presentation.app:main"
- [X] T003 [P] Configure pytest.ini with qt_api = "pyside6"
- [X] T004 Create presentation package structure in src/backlog_manager/presentation/__init__.py
- [X] T005 [P] Create views package in src/backlog_manager/presentation/views/__init__.py
- [X] T006 [P] Create viewmodels package in src/backlog_manager/presentation/viewmodels/__init__.py
- [X] T007 [P] Create tests/unit/presentation/viewmodels/ directory structure
- [X] T008 [P] Create tests/integration/presentation/views/ directory structure

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: DI Container, Entry Point, and Core ViewModels - MUST complete before user stories

**CRITICAL**: All user story work depends on this phase completing

- [X] T009 Implement DIContainer singleton in src/backlog_manager/presentation/container.py
- [X] T010 Implement main() entry point with qasync in src/backlog_manager/presentation/app.py
- [X] T011 [P] Create __main__.py for python -m backlog_manager support in src/backlog_manager/__main__.py
- [X] T012 Implement StoryTableModel(QAbstractTableModel) in src/backlog_manager/presentation/viewmodels/story_table_model.py
- [X] T013 Implement MainWindowViewModel(QObject) with signals in src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py
- [X] T014 [P] Create pytest-qt fixtures for qasync in tests/conftest.py
- [X] T015 [P] Test StoryTableModel in tests/unit/presentation/viewmodels/test_story_table_model.py
- [X] T016 Test MainWindowViewModel in tests/unit/presentation/viewmodels/test_main_window_viewmodel.py

**Checkpoint**: Foundation ready - DIContainer, Entry Point, and Core ViewModels functional

---

## Phase 3: User Story 1 - Visualizar e Gerenciar Backlog (Priority: P1) MVP

**Goal**: Visualizar todas as historias do backlog em tabela ordenada por prioridade

**Independent Test**: Abrir aplicacao com banco contendo historias, verificar tabela exibe colunas (ID, Nome, SP, Status, Feature, Dev, Datas)

### Implementation for User Story 1

- [X] T017 [US1] Implement MainWindow(QMainWindow) base structure in src/backlog_manager/presentation/views/main_window.py
- [X] T018 [US1] Implement StoryTableView(QTableView) in src/backlog_manager/presentation/views/story_table_view.py
- [X] T019 [US1] Add toolbar to MainWindow with action buttons (Nova Historia, Editar, Deletar, etc.)
- [X] T020 [US1] Add QSplitter layout with table and side panels in MainWindow
- [X] T021 [US1] Connect MainWindow to MainWindowViewModel signals (stories_changed, loading, error_occurred)
- [X] T022 [US1] Implement cold start performance optimization (target <= 3s)
- [X] T023 [P] [US1] Integration test MainWindow shows stories in tests/integration/presentation/views/test_main_window.py
- [X] T024 [P] [US1] Integration test startup time <= 3s in tests/integration/presentation/views/test_main_window.py

**Checkpoint**: User Story 1 complete - backlog table visible and functional

---

## Phase 4: User Story 2 - Criar e Editar Historias (Priority: P1)

**Goal**: Criar novas historias e editar existentes atraves de dialogos modais

**Independent Test**: Clicar Nova Historia, preencher campos, salvar, verificar historia na tabela

### Implementation for User Story 2

- [X] T025 [US2] Implement StoryDialogViewModel(QObject) in src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py
- [X] T026 [US2] Implement StoryDialog(QDialog) in src/backlog_manager/presentation/views/story_dialog.py
- [X] T027 [US2] Add Componente, Nome, SP (QComboBox 3,5,8,13), Feature dropdown to StoryDialog
- [X] T028 [US2] Implement create mode for StoryDialog
- [X] T029 [US2] Implement edit mode for StoryDialog with data pre-fill
- [X] T030 [US2] Add field validation with PT-BR error messages in StoryDialog
- [X] T031 [US2] Connect StoryDialog to MainWindowViewModel.create_story/edit_story
- [X] T032 [P] [US2] Unit test StoryDialogViewModel validation in tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py
- [X] T033 [P] [US2] Integration test StoryDialog save/cancel in tests/integration/presentation/views/test_story_dialog.py

**Checkpoint**: User Story 2 complete - CRUD de historias via dialog funcional

---

## Phase 5: User Story 3 - Alterar Prioridade (Priority: P1)

**Goal**: Mover historias para cima ou para baixo na prioridade

**Independent Test**: Selecionar historia, pressionar Alt+Up ou Alt+Down, verificar troca de prioridade

### Implementation for User Story 3

- [X] T034 [US3] Add move_priority_up/down methods to MainWindowViewModel
- [X] T035 [US3] Add Mover Cima/Baixo buttons to MainWindow toolbar
- [X] T036 [US3] Implement Alt+Up shortcut for priority up in MainWindow
- [X] T037 [US3] Implement Alt+Down shortcut for priority down in MainWindow
- [X] T038 [US3] Handle edge cases (first/last priority) with no-op
- [X] T039 [P] [US3] Unit test move_priority in MainWindowViewModel
- [X] T040 [P] [US3] Integration test priority shortcuts in tests/integration/presentation/views/test_main_window.py

**Checkpoint**: User Story 3 complete - priorizacao via botoes e atalhos funcional

---

## Phase 6: User Story 4 - Deletar Historia (Priority: P1)

**Goal**: Deletar historias com confirmacao previa

**Independent Test**: Selecionar historia, pressionar Delete, confirmar, verificar remocao

### Implementation for User Story 4

- [X] T041 [US4] Implement ConfirmDeleteDialog(QDialog) in src/backlog_manager/presentation/views/confirm_delete_dialog.py
- [X] T042 [US4] Add Confirmar/Cancelar buttons with PT-BR labels to ConfirmDeleteDialog
- [X] T043 [US4] Connect Delete button and Delete key to show ConfirmDeleteDialog in MainWindow
- [X] T044 [US4] Implement delete_story flow: confirm -> delete -> refresh table
- [X] T045 [US4] Handle cascading dependency removal on story delete
- [X] T046 [P] [US4] Integration test delete confirmation in tests/integration/presentation/views/test_main_window.py

**Checkpoint**: User Story 4 complete - exclusao com confirmacao funcional

---

## Phase 7: User Story 5 - Gerenciar Desenvolvedores (Priority: P1)

**Goal**: Cadastrar, editar e remover desenvolvedores do time

**Independent Test**: Abrir DeveloperDialog, adicionar dev, editar nome, deletar

### Implementation for User Story 5

- [X] T047 [US5] Implement DeveloperDialog(QDialog) in src/backlog_manager/presentation/views/developer_dialog.py
- [X] T048 [US5] Add developer list (QListWidget) to DeveloperDialog
- [X] T049 [US5] Add Adicionar/Editar/Remover buttons to DeveloperDialog
- [X] T050 [US5] Implement inline add/edit with name validation (nao vazio)
- [X] T051 [US5] Add confirmation before remove developer
- [X] T052 [US5] Connect Desenvolvedores button/menu in MainWindow to DeveloperDialog
- [X] T053 [P] [US5] Integration test DeveloperDialog CRUD in tests/integration/presentation/views/test_developer_dialog.py

**Checkpoint**: User Story 5 complete - gestao de desenvolvedores funcional

---

## Phase 8: User Story 6 - Gerenciar Features e Ondas (Priority: P1)

**Goal**: Criar features com ondas de entrega e associar historias

**Independent Test**: Criar feature onda 1, outra onda 2, verificar ondas unicas

### Implementation for User Story 6

- [X] T054 [US6] Implement FeatureDialog(QDialog) in src/backlog_manager/presentation/views/feature_dialog.py
- [X] T055 [US6] Add feature list (QListWidget) with Nome e Onda columns
- [X] T056 [US6] Add Adicionar/Editar/Remover buttons to FeatureDialog
- [X] T057 [US6] Implement wave uniqueness validation with DuplicateWaveException handling
- [X] T058 [US6] Implement FeatureHasStoriesException handling on delete
- [X] T059 [US6] Connect Features button/menu in MainWindow to FeatureDialog
- [X] T060 [US6] Wire Feature dropdown in StoryDialog to list features
- [X] T061 [P] [US6] Integration test FeatureDialog CRUD in tests/integration/presentation/views/test_feature_dialog.py

**Checkpoint**: User Story 6 complete - gestao de features e ondas funcional

---

## Phase 9: User Story 7 - Gerenciar Dependencias (Priority: P1)

**Goal**: Definir dependencias entre historias com validacao de ciclos

**Independent Test**: Selecionar historia, abrir painel dependencias, adicionar dependencia, verificar rejeicao de ciclos

### Implementation for User Story 7

- [X] T062 [US7] Implement DependencyPanel(QWidget) in src/backlog_manager/presentation/views/dependency_panel.py
- [X] T063 [US7] Add two lists: "Depende de" e "Dependentes" to DependencyPanel
- [X] T064 [US7] Add Adicionar Dependencia button with story selector
- [X] T065 [US7] Add Remover Dependencia button for selected dependency
- [X] T066 [US7] Implement CyclicDependencyException handling with cycle path display
- [X] T067 [US7] Connect DependencyPanel to story_selected signal from MainWindowViewModel
- [X] T068 [US7] Add DependencyPanel to MainWindow side panel
- [X] T069 [P] [US7] Integration test DependencyPanel add/remove in tests/integration/presentation/views/test_dependency_panel.py

**Checkpoint**: User Story 7 complete - gestao de dependencias funcional

---

## Phase 10: User Story 8 - Executar Alocacao Automatica (Priority: P1)

**Goal**: Executar alocacao automatica com feedback visual e metricas

**Independent Test**: Configurar velocidade/data, clicar Alocar, verificar desenvolvedores atribuidos

### Implementation for User Story 8

- [X] T070 [US8] Implement AllocationViewModel(QObject) in src/backlog_manager/presentation/viewmodels/allocation_viewmodel.py
- [X] T071 [US8] Add allocation_started, allocation_completed, allocation_error signals
- [X] T072 [US8] Implement MetricsPanel(QWidget) in src/backlog_manager/presentation/views/metrics_panel.py
- [X] T073 [US8] Display allocation metrics (historias alocadas, tempo, deadlocks) in MetricsPanel
- [X] T074 [US8] Implement WarningsPanel(QWidget) in src/backlog_manager/presentation/views/warnings_panel.py
- [X] T075 [US8] Differentiate DeadlockWarning (red) vs BetweenWavesIdlenessInfo (gray) in WarningsPanel
- [X] T076 [US8] Add Alocar Automaticamente button to MainWindow toolbar
- [X] T077 [US8] Implement Ctrl+Shift+A shortcut for allocation
- [X] T078 [US8] Add loading feedback (cursor, disabled button) during allocation
- [X] T079 [US8] Add MetricsPanel and WarningsPanel to MainWindow side panel
- [X] T080 [P] [US8] Unit test AllocationViewModel in tests/unit/presentation/viewmodels/test_allocation_viewmodel.py
- [X] T081 [P] [US8] Integration test allocation button in tests/integration/presentation/views/test_main_window.py

**Checkpoint**: User Story 8 complete - alocacao automatica com feedback funcional

---

## Phase 11: User Story 9 - Configurar Parametros de Alocacao (Priority: P2)

**Goal**: Configurar velocidade, data inicio e limite de ociosidade

**Independent Test**: Alterar valores no ConfigPanel, executar alocacao, verificar uso dos valores

### Implementation for User Story 9

- [X] T082 [US9] Implement ConfigPanel(QWidget) in src/backlog_manager/presentation/views/config_panel.py
- [X] T083 [US9] Add Velocidade QDoubleSpinBox (min=0.1, default=2.0)
- [X] T084 [US9] Add Data Inicio QDateEdit (default=today)
- [X] T085 [US9] Add Dias Max Ociosos QSpinBox (min=2, max=30, default=3)
- [X] T086 [US9] Implement validation before allocation (in-memory, ADR-007)
- [X] T087 [US9] Wire ConfigPanel values to ExecuteAllocationInputDTO
- [X] T088 [US9] Add ConfigPanel to MainWindow side panel

**Checkpoint**: User Story 9 complete - configuracao de parametros funcional

---

## Phase 12: User Story 10 - Atalhos de Teclado (Priority: P2)

**Goal**: Atalhos de teclado para operacoes frequentes

**Independent Test**: Pressionar cada atalho e verificar acao correspondente

### Implementation for User Story 10

- [X] T089 [US10] Implement Ctrl+N shortcut for new story in MainWindow
- [X] T090 [US10] Implement Enter/F2 shortcuts for edit story in StoryTableView
- [X] T091 [US10] Implement Delete shortcut for delete story in StoryTableView
- [X] T092 [US10] Wire all shortcuts using QShortcut or QAction.setShortcut()
- [X] T093 [P] [US10] Integration test all keyboard shortcuts in tests/integration/presentation/views/test_main_window.py

**Checkpoint**: User Story 10 complete - todos atalhos funcionais

---

## Phase 13: User Story 11 - Acessibilidade Basica (Priority: P3)

**Goal**: Navegacao por Tab e contraste adequado

**Independent Test**: Navegar pela interface apenas com teclado, verificar contraste

### Implementation for User Story 11

- [X] T094 [US11] Ensure Tab/Shift+Tab navigation order is logical across all widgets
- [X] T095 [US11] Add PT-BR tooltips to all toolbar buttons
- [X] T096 [US11] Verify text/background contrast >= 4.5:1 (WCAG AA)
- [X] T097 [US11] Set focus policies correctly on all interactive widgets

**Checkpoint**: User Story 11 complete - acessibilidade basica funcional

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Improvements affecting multiple user stories

- [X] T098 [P] Add comprehensive PT-BR labels to all UI elements (FR-180 to FR-184)
- [X] T099 [P] Implement consistent error handling pattern across all ViewModels (FR-160 to FR-164)
- [X] T100 [P] Add logging for critical operations (Constituicao XVII)
- [X] T101 Code review for MVVM compliance and Clean Architecture
- [X] T102 [P] Run full test suite and verify coverage (ViewModels >= 80%, Views >= 50%)
- [X] T103 [P] Performance testing: cold start <= 3s, CRUD <= 100ms, allocation 100 stories <= 5s
- [X] T104 Run quickstart.md validation with sample data

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - start immediately
- **Foundational (Phase 2)**: Depends on Setup - BLOCKS all user stories
- **User Stories (Phases 3-13)**: All depend on Foundational phase completion
- **Polish (Phase 14)**: Depends on all user stories being complete

### User Story Dependencies

| Story | Priority | Dependencies | Can Parallel With |
|-------|----------|--------------|-------------------|
| US1 - Visualizar Backlog | P1 | Foundational | - |
| US2 - Criar/Editar Historias | P1 | US1 (MainWindow exists) | US3, US4 |
| US3 - Alterar Prioridade | P1 | US1 (MainWindow exists) | US2, US4 |
| US4 - Deletar Historia | P1 | US1 (MainWindow exists) | US2, US3 |
| US5 - Gerenciar Desenvolvedores | P1 | US1 (MainWindow exists) | US6, US7 |
| US6 - Gerenciar Features | P1 | US1 (MainWindow exists) | US5, US7 |
| US7 - Gerenciar Dependencias | P1 | US1 (MainWindow exists) | US5, US6 |
| US8 - Alocacao Automatica | P1 | US5, US6, US7 (need devs, features, deps) | - |
| US9 - Configurar Parametros | P2 | US8 (ConfigPanel feeds allocation) | US10 |
| US10 - Atalhos de Teclado | P2 | US1-US4 (shortcuts need target actions) | US9 |
| US11 - Acessibilidade | P3 | US1-US10 (all widgets exist) | - |

### Critical Path

1. Setup (T001-T008)
2. Foundational (T009-T016) - CRITICAL GATE
3. US1: MainWindow + Table (T017-T024) - MVP Entry Point
4. US2-US4 in parallel: Create/Edit, Priority, Delete
5. US5-US7 in parallel: Developers, Features, Dependencies
6. US8: Allocation (depends on US5-US7)
7. US9-US10 in parallel: Config, Shortcuts
8. US11: Accessibility
9. Polish (T098-T104)

### Parallel Opportunities

**Phase 1 (all parallel)**:
```
T002, T003, T005, T006, T007, T008
```

**Phase 2 (partial parallel)**:
```
T011, T014, T015 after T012
```

**User Stories 2-4 (after US1 complete)**:
```
US2: T025-T033
US3: T034-T040  } All 3 can run in parallel
US4: T041-T046
```

**User Stories 5-7 (after US1 complete)**:
```
US5: T047-T053
US6: T054-T061  } All 3 can run in parallel
US7: T062-T069
```

---

## Parallel Example: User Stories 2-4

```bash
# After US1 complete, launch these 3 user stories in parallel:

# Developer A - US2:
Task: "Implement StoryDialogViewModel in src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py"
Task: "Implement StoryDialog in src/backlog_manager/presentation/views/story_dialog.py"

# Developer B - US3:
Task: "Add move_priority_up/down methods to MainWindowViewModel"
Task: "Implement Alt+Up/Down shortcuts in MainWindow"

# Developer C - US4:
Task: "Implement ConfirmDeleteDialog in src/backlog_manager/presentation/views/confirm_delete_dialog.py"
Task: "Connect Delete button to confirmation flow"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 - Visualizar Backlog
4. **STOP and VALIDATE**: Launch app, verify table displays stories
5. Demo MVP capability

### Incremental Delivery

1. Setup + Foundational -> Foundation ready
2. US1 -> Table visible -> Demo MVP
3. US2-US4 -> Full CRUD -> Demo
4. US5-US7 -> Management dialogs -> Demo
5. US8 -> Allocation working -> Demo
6. US9-US11 -> Polish and accessibility -> Final Demo
7. Each story adds value independently

### Recommended Single Developer Order

1. T001-T008 (Setup)
2. T009-T016 (Foundational - GATE)
3. T017-T024 (US1 - MVP visible)
4. T025-T033 (US2 - Create/Edit)
5. T034-T040 (US3 - Priority)
6. T041-T046 (US4 - Delete)
7. T047-T053 (US5 - Developers)
8. T054-T061 (US6 - Features)
9. T062-T069 (US7 - Dependencies)
10. T070-T081 (US8 - Allocation)
11. T082-T088 (US9 - Config)
12. T089-T093 (US10 - Shortcuts)
13. T094-T097 (US11 - Accessibility)
14. T098-T104 (Polish)

---

## Notes

- [P] tasks = different files, no dependencies within phase
- [USx] label maps task to specific user story for traceability
- Each user story independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All UI text in PT-BR (Constituicao XV)
- Error messages in PT-BR (Constituicao XVI)
