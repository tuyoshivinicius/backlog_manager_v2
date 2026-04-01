# Tasks: Resolver Issues SonarQube e Aprovar Quality Gate

**Input**: Design documents from `/specs/034-sonarqube-quality-gate/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Não há tarefas de teste dedicadas — a validação é feita executando a suíte existente (`poetry run pytest`) após cada refatoração.

**Organization**: Tarefas agrupadas por user story para implementação e validação independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: User story associada (US1, US2, US3)
- Caminhos exatos incluídos nas descrições

---

## Phase 1: Setup (Configuração Inicial)

**Purpose**: Configurações de projeto necessárias antes das correções

- [x] T001 Adicionar configuração `sonar.issue.ignore.multicriteria` para suprimir S100/S116 em `tests/headless_mocks.py` no arquivo `sonar-project.properties`

**Checkpoint**: Configuração SonarQube pronta para suprimir naming conventions dos mocks Qt.

---

## Phase 2: Foundational (Correções Rápidas Não-Bloqueantes)

**Purpose**: Code smells simples que devem ser resolvidos antes das refatorações maiores

**⚠️ CRITICAL**: Correções rápidas que eliminam issues MAJOR e MINOR

- [x] T002 [P] Remover bloco de código comentado (S125) em `tests/integration/infrastructure/database/test_schema.py` linha 86
- [x] T003 [P] Adicionar tratamento adequado ao bloco `except` vazio (S2737) — simplificar para `try/finally` removendo o `except asyncio.CancelledError: raise` redundante em `src/backlog_manager/presentation/views/main_window.py` linha 1408
- [x] T004 [P] Remover keyword `async` desnecessária e decorator `@pytest.mark.asyncio` (S7503) em `tests/integration/application/use_cases/test_scheduling_use_cases.py` linha 34
- [x] T005 Executar `poetry run pytest tests/ -v --tb=short` para validar ausência de regressão após correções das fases 1 e 2

**Checkpoint**: Issues MAJOR (S125) e MINOR (S2737, S7503, S100, S116) resolvidas. Testes passando.

---

## Phase 3: User Story 1 — Reduzir Complexidade Cognitiva de Funções Críticas (Priority: P1) 🎯 MVP

**Goal**: Refatorar 6 funções com complexidade cognitiva >15 para ≤15, extraindo sub-funções auxiliares

**Independent Test**: Executar `poetry run pytest tests/ -v` após cada refatoração e verificar no SonarQube que a complexidade de cada função está ≤15

### Implementation for User Story 1

- [x] T006 [US1] Refatorar `_run_allocation_loop` (complexidade 22→≤15) em `src/backlog_manager/domain/services/allocation_service.py` linha 1071 — extrair `_try_allocate_story()` e `_process_with_available_devs()` como sub-funções privadas
- [x] T007 [US1] Executar `poetry run pytest tests/ -v --tb=short` para validar ausência de regressão após refatoração de `allocation_service.py`
- [x] T008 [P] [US1] Refatorar `_find_circular_dependencies` (complexidade 19→≤15) em `scripts/extract_metrics.py` linha 254 — extrair `_register_cycle()` para isolar deduplicação de ciclos
- [x] T009 [P] [US1] Refatorar `_print_blocked_story_detail` (complexidade 17→≤15) em `scripts/extract_metrics.py` linha 557 — extrair `_format_dependencies_section()` e `_format_devs_section()`
- [x] T010 [US1] Executar `poetry run pytest tests/ -v --tb=short` para validar ausência de regressão após refatorações de `extract_metrics.py`
- [x] T011 [P] [US1] Refatorar `_generate_intra_wave_deps` (complexidade 16→≤15) em `scripts/seed_test_backlog.py` linha 563 — extrair `_try_add_intra_wave_dep()` com lógica de seleção e adição
- [x] T012 [P] [US1] Refatorar `_generate_inter_wave_deps` (complexidade 19→≤15) em `scripts/seed_test_backlog.py` linha 600 — extrair `_collect_earlier_wave_stories()` e `_try_add_inter_wave_dep()`
- [x] T013 [US1] Executar `poetry run pytest tests/ -v --tb=short` para validar ausência de regressão após refatorações de `seed_test_backlog.py`
- [x] T014 [US1] Refatorar `_get_display_value` (complexidade 16→≤15) em `src/backlog_manager/presentation/viewmodels/story_table_model.py` linha 230 — extrair helpers `_format_optional_string()`, `_format_date()`, `_format_numeric_field()` ou usar dicionário de mapeamento coluna→formatador
- [x] T015 [US1] Executar `poetry run pytest tests/ -v --tb=short` para validar ausência de regressão após refatoração de `story_table_model.py`

**Checkpoint**: Todas as 6 funções com complexidade cognitiva ≤15. Zero issues CRITICAL (S3776). Testes passando.

---

## Phase 4: User Story 2 — Revisar Security Hotspots para Aprovar Quality Gate (Priority: P1)

**Goal**: Revisar todos os 32 security hotspots e marcá-los com resolução apropriada (SAFE, FIXED, ACKNOWLEDGED)

**Independent Test**: Verificar no SonarQube que Security Hotspots Reviewed = 100% e Quality Gate muda de ERROR para OK

### Implementation for User Story 2

- [x] T016 [P] [US2] Substituir tags de versão por SHA completo de commit em `.github/workflows/ci.yml` — `actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `snok/install-poetry@v1`, `actions/upload-artifact@v4`, `codecov/codecov-action@v5`, `SonarSource/sonarqube-scan-action@v6`
- [x] T017 [P] [US2] Substituir tags de versão por SHA completo de commit em `.github/workflows/publish.yml` — `actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/download-artifact@v4`, `snok/install-poetry@v1`, `pypa/gh-action-pypi-publish@release/v1`
- [x] T018 [US2] Revisar e resolver hotspot de permissão de workflow (`secrets: inherit`) em `.github/workflows/publish.yml` linha 17 — enumerar secrets explicitamente ou marcar como ACKNOWLEDGED com justificativa via SonarCloud
- [x] T019 [US2] Marcar 7 hotspots de pseudo-random (S2245) como SAFE em `scripts/seed_test_backlog.py` via SonarCloud — justificativa: script gera dados fictícios de teste, sem uso criptográfico
- [x] T020 [US2] Marcar 1 hotspot de Regex DoS (S5852) como SAFE em `tests/integration/infrastructure/persistence/test_allocation_logging.py` via SonarCloud — justificativa: regex em teste unitário com input controlado
- [x] T021 [US2] Marcar 17 hotspots de diretórios públicos (S5443) como SAFE em `tests/integration/presentation/viewmodels/test_excel_viewmodel.py` via SonarCloud — justificativa: `tmp_path` do pytest gera diretórios temporários seguros
- [x] T022 [US2] Verificar que os 6 hotspots de SHA de commit (S7637) em `ci.yml` e `publish.yml` foram resolvidos como FIXED após push das alterações T016/T017

**Checkpoint**: 100% dos security hotspots revisados. Quality Gate deve mudar de ERROR para OK.

---

## Phase 5: User Story 3 — Corrigir Code Smells Restantes (Priority: P2)

**Goal**: Resolver code smells MAJOR e MINOR restantes que não foram cobertos nas fases anteriores

**Independent Test**: Verificar no SonarQube que o total de issues OPEN é zero

### Implementation for User Story 3

> **Nota**: Todas as tarefas desta user story já foram realizadas nas fases 1 e 2 (T001–T004). Esta fase serve como checkpoint de validação.

- [x] T023 [US3] Verificar no SonarQube que as 11 issues de naming convention (S100/S116) em `tests/headless_mocks.py` foram suprimidas pela configuração adicionada em T001
- [x] T024 [US3] Verificar no SonarQube que as issues S125 (T002), S2737 (T003) e S7503 (T004) estão resolvidas

**Checkpoint**: Zero issues OPEN no projeto. Zero code smells pendentes.

---

## Phase 6: Polish & Validação Final

**Purpose**: Validação cruzada e confirmação do Quality Gate

- [x] T025 Executar suíte completa de testes `poetry run pytest tests/ -v --tb=short` — confirmar zero falhas
- [x] T026 Executar formatação e linting `poetry run black --check src/ scripts/ tests/` e `poetry run isort --check-only src/ scripts/ tests/`
- [ ] T027 Fazer push da branch `034-sonarqube-quality-gate` e aguardar análise do SonarCloud
- [ ] T028 Verificar no SonarCloud que o Quality Gate mudou de ERROR para OK
- [ ] T029 Verificar métricas finais: Issues OPEN = 0, Security Hotspots Reviewed = 100%, Code Smells resolvidos

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode iniciar imediatamente
- **Foundational (Phase 2)**: T002–T004 podem rodar em paralelo; T005 depende de T001–T004
- **US1 (Phase 3)**: Depende de Phase 2 completa. Refatorações por arquivo podem ser paralelas
- **US2 (Phase 4)**: T016/T017 podem iniciar em paralelo com Phase 3; T019–T022 requerem SonarCloud e podem ser feitos a qualquer momento
- **US3 (Phase 5)**: Depende de Phase 1 (T001) e Phase 2 (T002–T004) — validação apenas
- **Polish (Phase 6)**: Depende de todas as fases anteriores

### User Story Dependencies

- **US1 (P1)**: Independente — apenas refatorações internas sem mudança de interface
- **US2 (P1)**: T016/T017 independentes; T019–T022 requerem acesso ao SonarCloud; T022 depende de T016/T017 terem sido mergeados
- **US3 (P2)**: Depende de T001 (configuração) e T002–T004 (correções) — apenas validação

### Within User Story 1

- T006 → T007 (refatoração → teste de regressão)
- T008 ∥ T009 (paralelos — mesmo arquivo mas funções diferentes)
- T008+T009 → T010 (refatorações → teste de regressão)
- T011 ∥ T012 (paralelos — mesmo arquivo mas funções diferentes)
- T011+T012 → T013 (refatorações → teste de regressão)
- T014 → T015 (refatoração → teste de regressão)

### Parallel Opportunities

- T002 ∥ T003 ∥ T004 (Phase 2 — arquivos diferentes)
- T008 ∥ T009 (extract_metrics.py — funções diferentes)
- T011 ∥ T012 (seed_test_backlog.py — funções diferentes)
- T016 ∥ T017 (GitHub Actions — arquivos diferentes)
- T019 ∥ T020 ∥ T021 (revisão de hotspots no SonarCloud — independentes)

---

## Parallel Example: User Story 1

```bash
# Refatorações em extract_metrics.py (paralelas):
Task T008: "Refatorar _find_circular_dependencies em scripts/extract_metrics.py"
Task T009: "Refatorar _print_blocked_story_detail em scripts/extract_metrics.py"

# Refatorações em seed_test_backlog.py (paralelas):
Task T011: "Refatorar _generate_intra_wave_deps em scripts/seed_test_backlog.py"
Task T012: "Refatorar _generate_inter_wave_deps em scripts/seed_test_backlog.py"
```

---

## Parallel Example: User Story 2

```bash
# Substituição de SHA em GitHub Actions (paralelas):
Task T016: "Substituir tags por SHA em .github/workflows/ci.yml"
Task T017: "Substituir tags por SHA em .github/workflows/publish.yml"

# Revisão de hotspots no SonarCloud (paralelas):
Task T019: "Marcar 7 hotspots pseudo-random como SAFE"
Task T020: "Marcar 1 hotspot Regex DoS como SAFE"
Task T021: "Marcar 17 hotspots diretórios públicos como SAFE"
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (configuração sonar-project.properties)
2. Complete Phase 2: Foundational (code smells simples)
3. Complete Phase 3: US1 — Refatorar complexidade cognitiva
4. Complete Phase 4: US2 — Revisar security hotspots + SHA em Actions
5. **STOP and VALIDATE**: Quality Gate deve estar OK

### Incremental Delivery

1. Setup + Foundational → Code smells simples resolvidos
2. US1 (complexidade cognitiva) → Zero issues CRITICAL → Validar testes
3. US2 (security hotspots) → 100% revisados → Quality Gate OK
4. US3 (validação) → Confirmar zero issues OPEN
5. Polish → Validação final completa

### Execution Order Recomendada

A ordem segue o quickstart.md:
1. Code smells simples (T002–T004) — correções rápidas
2. Naming conventions (T001) — configuração sonar-project.properties
3. Complexidade cognitiva (T006–T015) — refatorações com testes
4. GitHub Actions SHA (T016–T017) — substituição de tags
5. Security hotspots (T018–T022) — revisão no SonarCloud
6. Validação final (T025–T029) — push e verificar Quality Gate

---

## Notes

- [P] tasks = arquivos diferentes, sem dependências
- [Story] label mapeia tarefa à user story específica
- Cada user story é independentemente validável
- Executar testes após cada grupo de refatoração
- Commit após cada tarefa ou grupo lógico
- Refatorações NÃO devem alterar interfaces públicas
- Security hotspots são revisados via interface SonarCloud ou MCP tools
