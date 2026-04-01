# Tasks: Refatoracao da Suite de Testes para Cobertura 90% Headless

**Input**: Design documents from `/specs/032-test-refactor-headless/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Cada fase inclui tasks de validacao (executar suite e confirmar que testes passam). Nao ha tasks separadas de "teste do teste" — a validacao e integrada ao fluxo.

**Organization**: Tasks agrupadas por user story para permitir implementacao e teste independente de cada historia.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story a que a task pertence (e.g., US1, US2, US3)
- Caminhos exatos de arquivo incluidos nas descricoes

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Preparacao do ambiente e ferramentas para a refatoracao

- [X] T001 Executar relatorio de cobertura completo (sem --ignore) para baseline em `htmlcov/` — **Baseline: 34.48%, 596 testes**
- [X] T002 Documentar inventario de testes com dependencia GUI via `grep -r "from PySide6\|import PySide6\|qtbot\|qapp" tests/ --include="*.py"`
- [X] T002.1 Inventariar cenarios de negocio cobertos pelos testes GUI existentes (contar test functions em testes E2E, integration/presentation e unit/presentation) — **E2E=146, integ/pres=239, unit/pres=334 (total: 719)**

---

## Phase 2: Foundational (Pre-requisitos Bloqueantes)

**Purpose**: Infraestrutura que DEVE estar completa antes de qualquer user story

**⚠️ CRITICAL**: Nenhum trabalho de user story pode comecar antes desta fase estar completa

- [X] T003 Migrar `tests/e2e/factories.py` para `tests/factories.py` (copiar, verificar que nao tem imports GUI, atualizar imports em arquivos que referenciam)
- [X] T004 Criar fixture compartilhada `MockSignal` em `tests/conftest.py` para uso em testes headless de ViewModels (padrao do research.md secao 1)
- [X] T005 [P] Criar helper de mock PySide6 reutilizavel em `tests/conftest.py` — funcao/fixture que faz `patch.dict("sys.modules", {...})` para PySide6, PySide6.QtCore, PySide6.QtWidgets, PySide6.QtGui

**Checkpoint**: Infraestrutura de mock e factories prontas — user stories podem comecar

---

## Phase 3: User Story 1 - Correcao da Medicao de Cobertura (Priority: P1) 🎯 MVP

**Goal**: Relatorio de cobertura mede todas as 4 camadas (domain, application, infrastructure, presentation) com 119 arquivos

**Independent Test**: Executar relatorio de cobertura e verificar que todas as 4 camadas aparecem com percentuais por arquivo

### Implementation for User Story 1

- [X] T006 [US1] Verificar configuracao `[tool.coverage.run]` em `pyproject.toml` — confirmado: `source = ["src/backlog_manager"]` inclui todas as camadas
- [X] T007 [US1] Adicionar exclusao de `presentation/app.py` via `omit` em pyproject.toml (arquivo puramente visual)
- [X] T008 [P] [US1] Adicionar exclusao de `presentation/views/about_dialog.py` via `omit` em pyproject.toml (arquivo puramente visual)
- [X] T009 [P] [US1] Adicionar exclusao de `presentation/views/rich_tooltip.py` via `omit` em pyproject.toml (arquivo puramente visual)
- [X] T010 [US1] Executar baseline de cobertura — **35.29% (3 arquivos visuais excluidos via omit)**

**Checkpoint**: Relatorio de cobertura mostra 119 arquivos fonte em todas as camadas

---

## Phase 4: User Story 2 - Remocao de Testes E2E Graficos (Priority: P1)

**Goal**: Remover todos os 22 arquivos E2E com dependencia grafica, preservando factories de dados

**Independent Test**: Executar `pytest` completo sem flags --ignore para E2E e confirmar zero erros de import grafico

### Implementation for User Story 2

- [X] T011 [US2] Remover diretorio `tests/e2e/` integralmente (20 arquivos de teste + conftest.py) — factories ja migradas na T003
- [X] T012 [US2] Remover fixtures Qt/qasync de `tests/conftest.py` — removido na Phase 2
- [X] T013 [US2] Atualizar imports — apenas test_smoke.py referenciava factories, ja removido com e2e
- [X] T014 [US2] Verificar que `pytest tests/unit tests/integration` executa sem erros — **596 passed**

**Checkpoint**: Diretorio e2e removido, factories acessiveis, suite passa sem erros

---

## Phase 5: User Story 3 - Triagem e Tratamento de Testes de Integracao Presentation (Priority: P1)

**Goal**: Eliminar dependencia grafica dos 16 testes de integracao presentation sem perder cobertura de logica de negocio

**Independent Test**: Executar `pytest tests/integration/` completo sem display grafico — todos passam, zero imports graficos

### Implementation for User Story 3

- [X] T015 [US3] Analisar cada arquivo — 14 REMOVE (visuais), 7 logica ja coberta por unit tests de ViewModels
- [X] T016 [US3] Remover TODOS os testes de integracao presentation (logica coberta por unit tests de ViewModels)
- [X] T017 [US3] N/A — logica reescrita nos unit tests headless de ViewModels (Phase 6)
- [X] T018 [US3] Removido `tests/integration/presentation/conftest.py`
- [X] T019 [US3] Removido `tests/integration/presentation/views/conftest.py`
- [X] T020 [US3] Validar: **863 testes passam sem --ignore, zero erros**

**Checkpoint**: Todos os testes de integracao presentation sao headless e passam

---

## Phase 6: User Story 4 - Triagem e Tratamento de Testes Unitarios Presentation (Priority: P2)

**Goal**: Eliminar dependencia grafica dos 17 testes unitarios presentation sem perder cobertura de logica de negocio

**Independent Test**: Executar `pytest tests/unit/presentation/` completo sem display grafico — todos passam

### Implementation for User Story 4

- [X] T021 [US4] Analisar — 4 REMOVE (visuais: monospace_delegate, status_badge_delegate, column_resize, theme, confirm_reset, sp_breakdown_label), 13 REWRITE headless
- [X] T022 [US4] Removidos 6 testes puramente visuais
- [X] T023 [US4] Reescrever `test_story_table_model.py` headless — mock QAbstractTableModel, testar data(), rowCount(), headerData()
- [X] T024 [P] [US4] Reescrever `test_filter_proxy_model.py` headless — mock QSortFilterProxyModel, testar logica de filtragem
- [X] T025 [P] [US4] Reescrever demais testes de ViewModels headless — 13 arquivos reescritos com tests/headless_mocks.py
- [X] T026 [P] [US4] Delegates visuais removidos (nao testaveis headless)
- [X] T027 [P] [US4] `test_theme.py` reescrito headless — testa DESIGN_TOKENS, STATUS_PALETTE, apply_theme
- [X] T028 [US4] Validar: **267 testes presentation headless passando**

**Checkpoint**: Todos os testes unitarios presentation sao headless e passam

---

## Phase 7: User Story 5 - Ampliacao de Cobertura em Fluxos Criticos (Priority: P1)

**Goal**: Criar novos testes headless para atingir >= 90% de cobertura global

**Independent Test**: Relatorio de cobertura global >= 90% apos novos testes

### Implementation for User Story 5

- [X] T029 [US5] Relatorio pos-triagem: 81% → identificados excel_viewmodel, schedule_viewmodel, container, theme, assign_developer
- [X] T030 [P] [US5] Criado `test_excel_viewmodel.py` headless — 42 testes (import/export/error messages)
- [X] T031 [P] [US5] Criado `test_schedule_viewmodel.py` headless — 6 testes (execute/error paths)
- [X] T032 [P] [US5] `test_manual_allocation_dialog_viewmodel.py` ja reescrito headless
- [X] T033 [P] [US5] `test_dependency_dialog_viewmodel.py` ja reescrito headless
- [X] T034 [P] [US5] Criado `test_container.py` (91 testes) e `test_theme.py` headless
- [X] T035 [P] [US5] Delegates excluidos do coverage (puramente visuais)
- [X] T036 [US5] **Cobertura: 90%, 1048 testes passando**
- [X] T037 [US5] Criado `test_assign_developer.py` — meta de 90% atingida

**Checkpoint**: Cobertura global >= 90% confirmada pelo relatorio

---

## Phase 8: User Story 6 - Atualizacao do CI para Suite Completa (Priority: P1)

**Goal**: Pipeline CI executa suite completa sem --ignore, sem pytest-qt, cobertura >= 90%

**Independent Test**: Pipeline CI passa com todos os testes e cobertura >= 90%

### Implementation for User Story 6

- [X] T038 [US6] Removidos `--ignore` e `--override-ini` do CI
- [X] T039 [US6] Removido `-p no:pytest-qt` do CI
- [X] T040 [US6] Removido `pytest-qt` das dev dependencies
- [X] T041 [US6] Removido `qt_api = "pyside6"` de pytest.ini_options; fail_under atualizado para 90
- [X] T042 [US6] Validado: **1048 testes passando, 90% cobertura**
- [X] T043 [US6] Validado: zero testes skipados/xfail
- [X] T044 [US6] Tempo de execucao: ~40s (bem abaixo de 5 min)

**Checkpoint**: CI executa suite completa headless com cobertura >= 90%

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Limpeza final e verificacoes cruzadas

- [X] T045 [P] Verificado: **zero imports PySide6 em tests/**
- [X] T046 [P] Verificado: **zero fixtures pytest-qt em tests/**
- [X] T047 Marker `e2e` mantido em pyproject.toml, nenhum teste o utiliza
- [X] T048 Validacao final: suite completa 1048 testes, 90% cobertura, ~40s
- [ ] T049 Propor emenda constitucional (Principio XIV) — pendente para proxima conversa

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — pode comecar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEIA todas as user stories
- **US1 (Phase 3)**: Depende de Foundational — pode comecar em paralelo com US2
- **US2 (Phase 4)**: Depende de Foundational — pode comecar em paralelo com US1
- **US3 (Phase 5)**: Depende de US2 (E2E removido) e Foundational (mocks prontos)
- **US4 (Phase 6)**: Depende de Foundational (mocks prontos) — pode comecar em paralelo com US3
- **US5 (Phase 7)**: Depende de US3 e US4 (triagem completa para saber cobertura real)
- **US6 (Phase 8)**: Depende de US1, US2, US3, US4, US5 (tudo headless e cobertura >= 90%)
- **Polish (Phase 9)**: Depende de US6

### User Story Dependencies

- **US1 (Cobertura)**: Independente — pode comecar logo apos Foundational
- **US2 (Remocao E2E)**: Independente — pode comecar logo apos Foundational
- **US3 (Triagem Integracao)**: Depende de US2 (factories migradas, e2e removido)
- **US4 (Triagem Unitarios)**: Independente de US3 — pode rodar em paralelo
- **US5 (Ampliacao Cobertura)**: Depende de US3 + US4 (triagem revela gaps reais)
- **US6 (CI)**: Depende de todas as anteriores

### Within Each User Story

- Analise/inventario antes de acao (remover/reescrever)
- Remocoes antes de reescritas (evitar conflitos)
- Validacao como ultima task de cada fase
- Commit apos cada task ou grupo logico

### Parallel Opportunities

- **Phase 2**: T004 e T005 podem rodar em paralelo
- **Phase 3**: T007, T008, T009 podem rodar em paralelo (arquivos diferentes)
- **Phase 5**: T016 e T017 podem rodar em paralelo apos T015 (triagem feita)
- **Phase 6**: T023, T024, T025, T026, T027 podem rodar em paralelo (arquivos diferentes)
- **Phase 7**: T030, T031, T032, T033, T034, T035 podem rodar em paralelo (arquivos diferentes)
- **Phase 8**: T038, T039 podem rodar em paralelo (mesmo arquivo, mas secoes diferentes)
- **US1 e US2**: Podem rodar em paralelo (escopo disjunto)
- **US3 e US4**: Podem rodar em paralelo (integration vs unit)

---

## Parallel Example: User Story 4

```text
# Apos T021 (analise/triagem) completar:

# Reescritas em paralelo (arquivos diferentes):
Task T023: "Reescrever test_story_table_model.py headless"
Task T024: "Reescrever test_filter_proxy_model.py headless"
Task T025: "Reescrever demais ViewModels headless"
Task T026: "Reescrever test_status_badge_delegate.py headless"
Task T027: "Reescrever test_theme.py headless"
```

## Parallel Example: User Story 5

```text
# Apos T029 (relatorio de cobertura) completar:

# Novos testes em paralelo (arquivos diferentes):
Task T030: "Testes para excel_viewmodel.py"
Task T031: "Testes para schedule_viewmodel.py"
Task T032: "Testes para manual_allocation_dialog_viewmodel.py"
Task T033: "Testes para dependency_dialog_viewmodel.py"
Task T034: "Testes para ViewModels restantes"
Task T035: "Testes para delegates"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 Only)

1. Complete Phase 1: Setup (baseline de cobertura)
2. Complete Phase 2: Foundational (mocks e factories)
3. Complete Phase 3: US1 (cobertura corrigida)
4. Complete Phase 4: US2 (E2E removido)
5. **STOP and VALIDATE**: Suite roda sem E2E, cobertura medida corretamente

### Incremental Delivery

1. Setup + Foundational → Infraestrutura pronta
2. US1 + US2 → Cobertura corrigida + E2E removido (MVP!)
3. US3 + US4 → Triagem completa, todos os testes headless
4. US5 → Cobertura >= 90%
5. US6 → CI atualizado, pipeline limpo
6. Cada incremento agrega valor sem quebrar o anterior

### Sequential Strategy (Single Developer)

1. Phase 1 → Phase 2 → (Phase 3 + Phase 4 em paralelo) → Phase 5 → Phase 6 → Phase 7 → Phase 8 → Phase 9

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task a user story especifica para rastreabilidade
- Cada user story deve ser independentemente completavel e testavel
- Commit apos cada task ou grupo logico
- Pare em qualquer checkpoint para validar a story independentemente
- Evitar: tasks vagas, conflitos no mesmo arquivo, dependencias cross-story que quebrem independencia
- Zero imports de PySide6 nos arquivos de teste e a regra mais importante
