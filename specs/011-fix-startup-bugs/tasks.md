# Tasks: Corrigir Bugs de Inicialização

**Input**: Design documents from `/specs/011-fix-startup-bugs/`
**Prerequisites**: plan.md ✓, spec.md ✓, research.md ✓, data-model.md ✓, quickstart.md ✓

**Tests**: Not explicitly requested - no test tasks included.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: No setup required - this feature modifies existing files only

*No new files or project initialization needed. Skip to Phase 2.*

---

## Phase 2: Foundational

**Purpose**: No foundational tasks required - using existing infrastructure

*All necessary infrastructure (init_database, QTimer) already exists. Skip to User Story phases.*

---

## Phase 3: User Story 1 - Inicialização Automática do Banco de Dados (Priority: P1) 🎯 MVP

**Goal**: Garantir que ao iniciar a aplicação, todas as tabelas do banco de dados sejam criadas automaticamente

**Independent Test**: Deletar o arquivo `backlog_manager.db` e iniciar a aplicação. O sistema deve iniciar sem erros.

### Implementation for User Story 1

- [X] T001 [US1] Add import for init_database in src/backlog_manager/presentation/app.py
- [X] T002 [US1] Add init_database() call before DIContainer.initialize() in run_application() in src/backlog_manager/presentation/app.py

**Checkpoint**: Aplicação deve iniciar sem erros mesmo sem banco de dados pré-existente

---

## Phase 4: User Story 2 - Diálogos Funcionam Sem Travamentos (Priority: P1)

**Goal**: Garantir que operações CRUD via diálogos funcionem sem conflitos de event loop asyncio/qasync

**Independent Test**: Abrir qualquer diálogo, realizar operação e fechar. A aplicação deve continuar funcionando normalmente.

### Implementation for User Story 2

- [X] T003 [P] [US2] Add QTimer import and fix create_task calls in _on_new_story, _on_edit_story, _on_delete_story, _on_data_changed, _on_dependency_changed, _on_allocate in src/backlog_manager/presentation/views/main_window.py
- [X] T004 [P] [US2] Add QTimer import and fix create_task call in __init__ in src/backlog_manager/presentation/views/story_dialog.py
- [X] T005 [P] [US2] Add QTimer import and fix create_task call in __init__ in src/backlog_manager/presentation/views/developer_dialog.py
- [X] T006 [P] [US2] Add QTimer import and fix create_task call in __init__ in src/backlog_manager/presentation/views/feature_dialog.py
- [X] T007 [P] [US2] Add QTimer import and fix create_task calls in __init__, _on_add_dependency, _on_remove_dependency in src/backlog_manager/presentation/views/dependency_panel.py

**Checkpoint**: Todas as operações CRUD (criar, editar, deletar histórias, gerenciar desenvolvedores/features, alocação) devem completar sem erros

---

## Phase 5: User Story 3 - Encerramento Limpo da Aplicação (Priority: P2)

**Goal**: Garantir que a aplicação encerre sem erros de tasks pendentes

**Independent Test**: Fechar a aplicação após realizar operações. Não devem aparecer erros no console.

### Implementation for User Story 3

*Note: This story is addressed by the QTimer.singleShot changes in US2. The async tasks scheduled with QTimer will naturally complete or be properly cancelled when the event loop closes.*

- [X] T008 [US3] Verify clean shutdown behavior after US2 changes (validation only):
  1. Start application
  2. Open and close each dialog type (story, developer, feature)
  3. Execute auto-allocation
  4. Close application window
  5. Verify console shows no "Task was destroyed but it is pending" errors
  6. Verify no event loop warnings in logs

**Checkpoint**: Aplicação encerra sem mensagens de erro sobre tasks pendentes ou event loop

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Final validation

- [X] T009 Run existing test suite to ensure no regressions with poetry run pytest -v
- [X] T010 Manual validation following quickstart.md scenarios

---

## Out of Scope (per spec.md)

The following edge cases are explicitly excluded from this feature:

- Directory permissions for database file
- Application close during active database operation
- Multiple application instances accessing same database
- Async operation failure during modal dialog

These scenarios may be addressed in future maintenance tasks if user feedback indicates need.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: Skipped - no setup needed
- **Phase 2 (Foundational)**: Skipped - existing infrastructure
- **Phase 3 (US1)**: Can start immediately - database initialization fix
- **Phase 4 (US2)**: Can start in parallel with US1 - event loop fixes
- **Phase 5 (US3)**: Depends on US2 completion - validation only
- **Phase 6 (Polish)**: Depends on US1, US2, US3 completion

### User Story Dependencies

- **User Story 1 (P1)**: No dependencies - can start immediately
- **User Story 2 (P1)**: No dependencies - can start immediately (parallel with US1)
- **User Story 3 (P2)**: Depends on US2 - validation only

### Within Each User Story

- T001 → T002 (sequential - import before use)
- T003, T004, T005, T006, T007 (all parallel - different files)
- T008 (depends on T003-T007 completion)

### Parallel Opportunities

Within US2, all tasks (T003-T007) can be executed in parallel:

```bash
# Launch all US2 fixes together:
Task: "Fix main_window.py"
Task: "Fix story_dialog.py"
Task: "Fix developer_dialog.py"
Task: "Fix feature_dialog.py"
Task: "Fix dependency_panel.py"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete T001-T002: Database initialization fix
2. Complete T003-T007: Event loop conflict fixes (parallel)
3. **STOP and VALIDATE**: Test both stories independently
4. Complete T008-T010: Validation and testing

### Summary

| User Story | Tasks | Priority | Independent |
|------------|-------|----------|-------------|
| US1 - DB Init | T001-T002 | P1 | ✅ |
| US2 - Event Loop | T003-T007 | P1 | ✅ |
| US3 - Clean Shutdown | T008 | P2 | Depends on US2 |
| Polish | T009-T010 | - | Depends on all |

---

## Notes

- All changes modify existing files - no new files created
- All US2 tasks are parallelizable (different files)
- US1 tasks are sequential (same file, dependency order)
- US3 is primarily validation - no additional code needed
- Pattern for event loop fix: `QTimer.singleShot(0, lambda: asyncio.create_task(...))`
