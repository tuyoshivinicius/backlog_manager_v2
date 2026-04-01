# Tasks: Cobertura de Testes 90% e Quality Gate SonarQube

**Input**: Design documents from `/specs/036-test-coverage-90/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Esta feature E sobre testes. As tasks de implementacao SAO tasks de teste. Testes sao o entregavel principal.

**Organization**: Tasks agrupadas por user story para permitir implementacao e validacao independente de cada story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story a que pertence (US1, US2, US3)
- Caminhos exatos incluidos nas descricoes

---

## Phase 1: Setup

**Purpose**: Garantir que o ambiente esta pronto e entender o baseline de cobertura atual.

- [x] T001 Executar `poetry run pytest --cov=src/backlog_manager --cov-report=term-missing -m "not slow"` e registrar baseline de cobertura local atual
- [x] T002 Verificar configuracao atual de exclusoes em `sonar-project.properties` e comparar com `[tool.coverage.run].omit` em `pyproject.toml`

**Checkpoint**: Baseline documentado, divergencias entre SonarQube e pytest-cov confirmadas.

---

## Phase 2: User Story 1 - Alinhamento de Exclusoes de Cobertura (Priority: P1) MVP

**Goal**: Alinhar `sonar.coverage.exclusions` com as exclusoes do pytest-cov para eliminar divergencia de metricas (56.7% SonarQube vs ~94% local).

**Independent Test**: Executar analise SonarQube e verificar que cobertura reportada subiu de 56.7% para ~94%.

### Implementation for User Story 1

- [x] T003 [US1] Atualizar `sonar.coverage.exclusions` em `sonar-project.properties` adicionando: `**/__init__.py`, `**/presentation/app.py`, `**/presentation/views/**`, `**/presentation/delegates/**`, `**/__main__.py`, `**/domain/interfaces/**`, `**/presentation/constants.py`
- [x] T004 [US1] Validar que os padroes glob adicionados em `sonar-project.properties` sao semanticamente equivalentes aos padroes fnmatch em `pyproject.toml` secao `[tool.coverage.run].omit`
- [x] T005 [US1] Executar `poetry run pytest --cov=src/backlog_manager --cov-report=term-missing -m "not slow"` e confirmar que cobertura local permanece >= 90%

**Checkpoint**: Exclusoes alinhadas. Cobertura SonarQube deve subir para ~94% no proximo push.

---

## Phase 3: User Story 2 - Testes para Codigo Parcialmente Coberto (Priority: P2)

**Goal**: Adicionar testes unitarios para os 16 arquivos prioritarios com cobertura abaixo de 90%, cobrindo ~139 linhas de codigo testavel.

**Independent Test**: Executar `pytest-cov` e verificar que cada arquivo listado atingiu >= 90% de cobertura individual.

### Tier 1 - Impacto Critico (cobertura < 70%)

- [x] T006 [P] [US2] Expandir testes em `tests/unit/application/test_edit_story.py` para cobrir caminhos de edicao parcial, validacao de campos opcionais e error paths do `src/backlog_manager/application/use_cases/story/edit_story.py` (44.4% -> 100%)
- [x] T007 [P] [US2] Expandir testes em `tests/unit/application/test_edit_story_dto.py` para cobrir validacao de DTOs com campos opcionais/nulos do `src/backlog_manager/application/dto/story/edit_story_dto.py` (69.8% -> 100%)
- [x] T008 [P] [US2] Expandir testes em `tests/unit/application/test_list_stories_sort.py` para cobrir filtros, ordenacao e paginacao do `src/backlog_manager/application/use_cases/story/list_stories.py` (69.4% -> 100%)
- [x] T009 [P] [US2] Expandir testes em `tests/unit/infrastructure/test_directory_creation.py` para cobrir error handling de conexao e retry logic do `src/backlog_manager/infrastructure/database/sqlite_connection.py` (65.6% -> 100%)

### Tier Viewmodel - Cobertura Muito Baixa (atencao especial)

- [x] T010 [P] [US2] excel_viewmodel.py ja estava em 100% — nenhuma acao necessaria
- [x] T011 [P] [US2] schedule_viewmodel.py ja estava em 100% — nenhuma acao necessaria
- [x] T012 [P] [US2] dependency_dialog_viewmodel.py ja estava em 99% — nenhuma acao necessaria

### Tier 2 - Impacto Alto (cobertura 70-85%)

- [x] T013 [P] [US2] Expandir testes em `tests/unit/infrastructure/test_log_format.py` para cobrir configuracao de rotacao e formatacao do `src/backlog_manager/infrastructure/logging/logger_config.py` (74.1% -> 100%)
- [x] T014 [P] [US2] Expandir testes em `tests/unit/presentation/test_story_table_model.py` com mock headless para cobrir roleNames, data() e flags() do `src/backlog_manager/presentation/viewmodels/story_table_model.py` (82.2% -> 99%)
- [x] T015 [P] [US2] Expandir testes em `tests/unit/presentation/test_main_window_viewmodel.py` com mock headless para cobrir comandos de menu e estados do `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` (83.2% -> 99%)
- [x] T016 [P] [US2] Expandir testes em `tests/unit/domain/test_allocation_service.py` para cobrir edge cases de alocacao, deadlock e idleness do `src/backlog_manager/domain/services/allocation_service.py` (84.9% -> 98%)
- [x] T017 [P] [US2] Expandir testes em `tests/unit/presentation/test_filter_proxy_model.py` com mock headless para cobrir filterAcceptsRow edge cases do `src/backlog_manager/presentation/viewmodels/filter_proxy_model.py` (84.6% -> 100%)
- [x] T018 [P] [US2] Expandir testes em `tests/unit/presentation/test_manual_allocation_dialog_viewmodel.py` com mock headless para cobrir validacao de datas do `src/backlog_manager/presentation/viewmodels/manual_allocation_dialog_viewmodel.py` (85.3% -> 100%)

### Tier 3 - Gap Minimo (cobertura 85-90%)

- [x] T019 [P] [US2] Expandir testes em `tests/unit/application/test_execute_allocation.py` para cobrir error paths do `src/backlog_manager/application/use_cases/allocation/execute_allocation.py` (87% -> 100%)
- [x] T020 [P] [US2] Expandir testes em `tests/unit/application/test_import_excel_use_case.py` para cobrir validacao de formato invalido do `src/backlog_manager/application/use_cases/excel/import_excel_use_case.py` (89% -> 98%)
- [x] T021 [P] [US2] Expandir testes em `tests/unit/presentation/test_theme.py` para cobrir fallback de tema do `src/backlog_manager/presentation/theme/theme.py` (89.3% -> 97%)
- [x] T022 [P] [US2] Expandir testes em `tests/unit/application/test_calculate_schedule.py` para cobrir schedule com zero stories do `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py` (89.5% -> 99%)
- [x] T023 [P] [US2] Expandir testes em `tests/unit/application/test_get_developer_availability.py` para cobrir developer sem alocacoes do `src/backlog_manager/application/use_cases/allocation/get_developer_availability.py` (89.5% -> 98%)

### Validacao da User Story 2

- [x] T024 [US2] Executar `poetry run pytest --cov=src/backlog_manager --cov-report=term-missing -m "not slow"` e confirmar que TODOS os 16 arquivos prioritarios atingiram >= 90% de cobertura individual
- [x] T025 [US2] Confirmar zero regressao: todos os testes pre-existentes continuam passando (1241 passed, 0 failed)

**Checkpoint**: Todos os 16 arquivos prioritarios com >= 90% de cobertura. Zero regressao.

---

## Phase 4: User Story 3 - Garantia de Cobertura em Novo Codigo (Priority: P3)

**Goal**: Verificar que todo codigo novo/modificado nesta feature atinge cobertura >= 80% (threshold do Quality Gate) e que o Quality Gate passa.

**Independent Test**: Verificar no SonarQube que `new_coverage` >= 80% e Quality Gate status OK.

### Implementation for User Story 3

- [x] T026 [US3] Executar suite completa de testes e gerar relatorio de cobertura XML: `poetry run pytest --cov=src/backlog_manager --cov-report=xml --cov-report=term-missing -m "not slow"`
- [x] T027 [US3] Verificar que cobertura total local esta >= 90% (97.90%) e que todos os 16 arquivos prioritarios estao >= 90%
- [ ] T028 [US3] Push para branch `036-test-coverage-90` e verificar que o Quality Gate do SonarQube passa com status OK
- [ ] T029 [US3] Confirmar no SonarQube: 0 bugs, 0 vulnerabilidades, 0 code smells novos, 0% duplicacao nova, cobertura de novo codigo >= 80%

**Checkpoint**: Quality Gate OK. Todas as metricas de qualidade atingidas.

---

## Phase 5: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final e limpeza

- [x] T030 Executar validacao completa conforme `specs/036-test-coverage-90/quickstart.md`
- [ ] T031 Verificar que diferenca entre cobertura local (pytest-cov) e SonarQube e inferior a 5 pontos percentuais

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias - pode comecar imediatamente
- **US1 (Phase 2)**: Depende de Setup - configuracao de exclusoes
- **US2 (Phase 3)**: Pode comecar apos Setup (independente de US1), mas US1 deve estar completa para validacao final no SonarQube
- **US3 (Phase 4)**: Depende de US1 e US2 completas - e a validacao final
- **Polish (Phase 5)**: Depende de todas as user stories completas

### User Story Dependencies

- **User Story 1 (P1)**: Independente - apenas configuracao
- **User Story 2 (P2)**: Independente de US1 para escrita de testes - depende de US1 para metricas SonarQube corretas
- **User Story 3 (P3)**: Depende de US1 + US2 - e a validacao end-to-end

### Within User Story 2

- Todas as tasks T006-T023 sao marcadas [P] e podem rodar em paralelo (arquivos diferentes, sem dependencias)
- T024-T025 (validacao) dependem de T006-T023

### Parallel Opportunities

- **Maximo paralelismo**: Todas as 18 tasks de teste (T006-T023) podem ser executadas simultaneamente
- **Por tier**: Tier 1 (4 tasks), Tier Viewmodel (3 tasks), Tier 2 (6 tasks), Tier 3 (5 tasks) podem ser agrupadas
- **US1 + US2 parcial**: US1 (config) pode rodar em paralelo com escrita de testes de US2

---

## Parallel Example: User Story 2

```bash
# Todas estas tasks podem ser lancadas em paralelo (arquivos independentes):
Task T006: "Expandir testes edit_story.py"
Task T007: "Expandir testes edit_story_dto.py"
Task T008: "Expandir testes list_stories_sort.py"
Task T009: "Expandir testes directory_creation.py"
Task T010: "Expandir testes excel_viewmodel.py"
Task T011: "Expandir testes schedule_viewmodel.py"
Task T012: "Expandir testes dependency_dialog_viewmodel.py"
# ... e todas as demais T013-T023
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup (baseline)
2. Completar Phase 2: US1 (alinhar exclusoes)
3. **STOP e VALIDAR**: Push e verificar SonarQube - cobertura deve subir de 56.7% para ~94%
4. Se Quality Gate ja passa: MVP entregue!

### Incremental Delivery

1. Setup + US1 -> Exclusoes alinhadas, metricas consistentes (MVP!)
2. US2 Tier 1 + Viewmodel -> Arquivos criticos cobertos (maior impacto)
3. US2 Tier 2 -> Arquivos de impacto alto cobertos
4. US2 Tier 3 -> Todos os gaps fechados
5. US3 -> Validacao final, Quality Gate confirmado

### Parallel Team Strategy

Com multiplos desenvolvedores:

1. **Dev A**: US1 (config) - rapido, ~30 min
2. **Dev B-D**: US2 tasks em paralelo (cada dev pega um tier)
3. Apos US1 + US2: qualquer dev executa US3 (validacao)

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica
- Cada user story pode ser validada independentemente
- Padroes de teste: seguir `tests/conftest.py` (fixtures), `tests/factories.py` (builders), `tests/headless_mocks.py` (mocks PySide6)
- Todos os testes devem rodar headless (sem display/servidor X)
- Zero alteracao em codigo de producao exceto ajustes minimos de testabilidade
- Commit apos cada task ou grupo logico
