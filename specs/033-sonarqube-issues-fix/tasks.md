# Tasks: Resolucao de Issues SonarQube

**Input**: Design documents from `/specs/033-sonarqube-issues-fix/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Nao solicitados. As tarefas de teste referem-se a correcao de issues em arquivos de teste existentes, nao a criacao de novos testes.

**Organization**: Tasks agrupadas por user story (US1-US10) seguindo prioridade da spec. Todas as correcoes sao in-place em arquivos existentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode executar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story associada (US1-US10)
- Caminhos relativos a `src/backlog_manager/` e `tests/`

---

## Phase 1: Setup

**Purpose**: Verificar baseline antes de iniciar correcoes

- [X] T001 Executar `poetry run pytest` e confirmar que todos os testes passam (baseline)
- [X] T002 Executar `poetry run ruff check .` e registrar estado atual de linting

**Checkpoint**: Baseline registrado — correcoes podem iniciar

---

## Phase 2: User Story 1 - Correcao de Bug Potencial por Retorno Constante (Priority: P1) :dart: MVP

**Goal**: Corrigir BLOCKER S3516 onde `setData()` sempre retorna False

**Independent Test**: Executar testes existentes de `story_table_model` e verificar que o metodo retorna True quando sinal e emitido com sucesso

- [X] T003 [US1] Corrigir retorno de `setData()` em `src/backlog_manager/presentation/viewmodels/story_table_model.py` linha ~194: alterar `return False` para `return True` apos emissao bem-sucedida do sinal `status_change_requested` (conforme research R1)
- [X] T004 [US1] Executar testes existentes de `story_table_model` para validar que comportamento e preservado

**Checkpoint**: BLOCKER resolvido — 0 issues BLOCKER no projeto

---

## Phase 3: User Story 2 - Correcao de Tasks Async sem Referencia (Priority: P2)

**Goal**: Implementar padrao `_create_task()` em Views/ViewModels para evitar garbage collection prematura de tasks asyncio

**Independent Test**: Verificar que todas as tasks asyncio sao armazenadas em `_pending_tasks` e completam sem serem coletadas

### Implementacao

- [X] T005 [US2] Implementar metodo `_create_task()` e atributo `_pending_tasks` em `src/backlog_manager/presentation/viewmodels/manual_allocation_dialog_viewmodel.py` — substituir `asyncio.ensure_future()` nas linhas ~95 e ~145 (2 issues S7502 + outras instancias)
- [X] T006 [P] [US2] Implementar metodo `_create_task()` e atributo `_pending_tasks` em `src/backlog_manager/presentation/views/main_window.py` — substituir `asyncio.create_task()` / `asyncio.ensure_future()` nas linhas ~1003/1097/1104/1113 (4 issues S7502 + ~25 outras instancias)
- [X] T007 [P] [US2] Implementar metodo `_create_task()` e atributo `_pending_tasks` em `src/backlog_manager/presentation/views/developer_dialog.py` — substituir chamadas nas linhas ~201/245/288 (3 issues S7502)
- [X] T008 [P] [US2] Implementar metodo `_create_task()` e atributo `_pending_tasks` em `src/backlog_manager/presentation/views/feature_dialog.py` — substituir chamadas nas linhas ~211/278/345 (3 issues S7502)
- [X] T009 [P] [US2] Implementar metodo `_create_task()` e atributo `_pending_tasks` em `src/backlog_manager/presentation/views/story_dialog.py` — substituir todas as instancias de tasks sem referencia
- [X] T010 [US2] Executar `poetry run pytest` para validar que todas as alteracoes preservam comportamento

**Checkpoint**: Todas as 12 issues S7502 + instancias adicionais resolvidas

---

## Phase 4: User Story 3 - Correcao de CancelledError Silenciado (Priority: P3)

**Goal**: Re-raise `CancelledError` apos limpeza de recursos em todos os handlers

**Independent Test**: Verificar que CancelledError e propagado corretamente e estados sao limpos

- [X] T011 [P] [US3] Corrigir handler de CancelledError em `src/backlog_manager/presentation/viewmodels/allocation_viewmodel.py` linha ~155: adicionar `raise` apos limpeza e remover `return None` morto
- [X] T012 [P] [US3] Corrigir handler de CancelledError em `src/backlog_manager/presentation/viewmodels/excel_viewmodel.py` linha ~187 (import cancelado): adicionar `raise` apos emit
- [X] T013 [P] [US3] Corrigir handler de CancelledError em `src/backlog_manager/presentation/viewmodels/excel_viewmodel.py` linha ~242 (export cancelado): adicionar `raise` apos delete partial + emit
- [X] T014 [P] [US3] Corrigir handler de CancelledError em `src/backlog_manager/presentation/views/main_window.py` linha ~1400: substituir `pass` por `raise`
- [X] T015 [US3] Executar `poetry run pytest` para validar que alteracoes nao quebram testes existentes

**Checkpoint**: Todas as 4 issues S7497 resolvidas

---

## Phase 5: User Story 4 - Reducao de Complexidade Cognitiva em Codigo de Producao (Priority: P4)

**Goal**: Reduzir complexidade cognitiva de 12 metodos de producao para <= 15

**Independent Test**: Executar testes unitarios de cada modulo refatorado e verificar que passam sem alteracao

### Borderline (CC 15-20) — Decomposicao leve

- [X] T016 [P] [US4] Refatorar `Story.__init__()` em `src/backlog_manager/domain/entities/story.py` linha ~44 (CC=18): extrair validacoes de campos em metodos privados
- [X] T017 [P] [US4] Refatorar metodo em `src/backlog_manager/domain/services/allocation_service.py` linha ~846 (CC=17): aplicar early returns para reduzir aninhamento
- [X] T018 [P] [US4] Refatorar `data()` em `src/backlog_manager/presentation/viewmodels/story_table_model.py` linha ~196 (CC=16): extrair formatacao de celulas por tipo em metodos privados

### Altos (CC 20-50) — Decomposicao moderada

- [X] T019 [P] [US4] Refatorar metodo em `src/backlog_manager/domain/services/scheduling_service.py` linha ~180 (CC=20): extrair calculo de datas uteis em submethods
- [X] T020 [P] [US4] Refatorar metodo em `src/backlog_manager/infrastructure/excel/excel_service.py` linha ~50 (CC=22): extrair processamento de celulas em submethods
- [X] T021 [P] [US4] Refatorar `execute()` em `src/backlog_manager/application/use_cases/story/list_stories.py` linha ~67 (CC=23): extrair filtragem e ordenacao
- [X] T022 [P] [US4] Refatorar metodo em `src/backlog_manager/domain/services/allocation_service.py` linha ~558 (CC=23): extrair verificacoes de estado
- [X] T023 [P] [US4] Refatorar metodo em `src/backlog_manager/domain/services/allocation_service.py` linha ~635 (CC=25): extrair logica de resolucao de conflitos
- [X] T024 [P] [US4] Refatorar `execute()` em `src/backlog_manager/application/use_cases/allocation/get_developer_availability.py` linha ~51 (CC=26): extrair calculo de disponibilidade por periodo
- [X] T025 [P] [US4] Refatorar `execute()` em `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py` linha ~50 (CC=28): extrair iteracao de ondas e calculo de datas
- [X] T026 [P] [US4] Refatorar metodo em `src/backlog_manager/domain/services/allocation_service.py` linha ~404 (CC=34): extrair validacao e preparacao
- [X] T027 [P] [US4] Refatorar metodo em `src/backlog_manager/domain/services/allocation_service.py` linha ~740 (CC=36): extrair logica de ondas em submethods
- [X] T028 [P] [US4] Refatorar `execute()` em `src/backlog_manager/application/use_cases/excel/import_excel_use_case.py` linha ~57 (CC=39): extrair validacao de linhas e processamento de colunas

### Critico (CC > 50) — Decomposicao profunda

- [X] T029 [US4] Refatorar metodo em `src/backlog_manager/domain/services/allocation_service.py` linha ~926 (CC=79): decompor em etapas do algoritmo de alocacao com submethods privados
- [X] T030 [US4] Executar `poetry run pytest` para validar que TODOS os testes passam apos refatoracao de producao

**Checkpoint**: 12 metodos de producao com CC <= 15

---

## Phase 6: User Story 5 - Reducao de Complexidade Cognitiva em Scripts (Priority: P5)

**Goal**: Reduzir complexidade cognitiva de 5 funcoes em scripts utilitarios para <= 15

**Independent Test**: Executar scripts refatorados e verificar que produzem mesmos resultados

- [X] T031 [P] [US5] Refatorar funcao em `scripts/seed_test_backlog.py` linha ~516 (CC=69): decompor em funcoes por tipo de entidade criada
- [X] T032 [P] [US5] Refatorar funcao em `scripts/extract_metrics.py` linha ~69 (CC=72): decompor em funcoes por secao do relatorio
- [X] T033 [P] [US5] Refatorar funcao em `scripts/extract_metrics.py` linha ~299 (CC=96): decompor em funcoes por tipo de metrica extraida
- [X] T034 [US5] Executar `poetry run pytest` para validar que testes relacionados a scripts passam

**Checkpoint**: 5 funcoes de scripts com CC <= 15

---

## Phase 7: User Story 6 - Correcao de Literal Duplicado e Type Hint (Priority: P6)

**Goal**: Extrair literal duplicado para constante e corrigir type hint incorreto

**Independent Test**: Verificar que constante e usada em todos os locais e type hint e aceito por verificador

- [X] T035 [P] [US6] Extrair string `"UnitOfWork must be used as context manager"` para constante de classe `_CONTEXT_MANAGER_ERROR_MSG` em `src/backlog_manager/infrastructure/database/unit_of_work.py` e substituir as 4 ocorrencias (S1192)
- [X] T036 [P] [US6] Corrigir type hint em `src/backlog_manager/presentation/theme/theme.py` linha ~385: alterar para `Optional[IconManager]` ou `IconManager | None` (S5890)

**Checkpoint**: Issues S1192 e S5890 resolvidas

---

## Phase 8: User Story 7 - Adicao de Docstrings em Metodos Vazios de Testes (Priority: P7)

**Goal**: Adicionar docstrings explicativas em 19 metodos vazios de mocks e fixtures

**Independent Test**: Verificar que cada metodo vazio tem docstring e issues S1186 sao resolvidas

- [X] T037 [P] [US7] Adicionar docstrings em 3 metodos vazios em `tests/conftest.py` linhas ~237/250/253: documentar que sao stubs intencionais
- [X] T038 [P] [US7] Adicionar docstrings em 12 metodos vazios em `tests/headless_mocks.py` linhas ~21/24/48/51/54/73/76/79/82/85/95/116: documentar que simulam interface Qt
- [X] T039 [P] [US7] Adicionar docstrings em 4 metodos vazios em `tests/unit/presentation/viewmodels/test_filter_proxy_model.py` linhas ~144/147/150/153: documentar que sao stubs intencionais

**Checkpoint**: Todas as 19 issues S1186 resolvidas

---

## Phase 9: User Story 8 - Correcao de Comparacoes Float em Testes (Priority: P8)

**Goal**: Substituir 15 comparacoes diretas de float por `pytest.approx()`

**Independent Test**: Executar testes corrigidos multiplas vezes para confirmar consistencia

- [X] T040 [P] [US8] Substituir 5 comparacoes float por `pytest.approx()` em `tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py` linhas ~134/137/181/187/200 (garantir import de pytest.approx)
- [X] T041 [P] [US8] Substituir 5 comparacoes float por `pytest.approx()` em `tests/unit/presentation/viewmodels/test_config_dialog_viewmodel_qsettings.py` linhas ~76/129/140/149/159
- [X] T042 [P] [US8] Substituir 2 comparacoes float por `pytest.approx()` em `tests/unit/domain/services/test_status_bar_viewmodel_sp_breakdown.py` linhas ~113/114
- [X] T043 [P] [US8] Substituir 1 comparacao float por `pytest.approx()` em `tests/unit/presentation/viewmodels/test_schedule_viewmodel.py` linha ~84
- [X] T044 [P] [US8] Substituir 1 comparacao float por `pytest.approx()` em `tests/unit/domain/services/test_allocation_service.py` linha ~1573
- [X] T045 [P] [US8] Verificar se `presentation/views/story_dialog.py` linha ~418 tem comparacao float e corrigir se necessario (mencionado no plan com ressalva)

**Checkpoint**: Todas as 15 issues S1244 resolvidas

---

## Phase 10: User Story 9 - Limpeza de Codigo (Priority: P9)

**Goal**: Resolver blocos vazios, parametros/variaveis nao usados e codigo comentado

**Independent Test**: Verificar que codigo removido/alterado nao era utilizado e testes passam

### S108 - Blocos vazios (8 issues)

- [X] T046 [P] [US9] Adicionar comentario explicativo ou logging em bloco vazio em `src/backlog_manager/presentation/app.py` linha ~34
- [X] T047 [P] [US9] Adicionar comentario explicativo em bloco vazio em `src/backlog_manager/presentation/views/config_panel.py` linha ~24
- [X] T048 [P] [US9] Adicionar comentario explicativo em bloco vazio em `src/backlog_manager/presentation/views/metrics_panel.py` linha ~16
- [X] T049 [P] [US9] Adicionar comentario explicativo em bloco vazio em `src/backlog_manager/presentation/views/warnings_panel.py` linha ~22
- [X] T050 [P] [US9] Adicionar logging de warning em bloco vazio em `src/backlog_manager/infrastructure/database/sqlite_connection.py` linha ~12
- [X] T051 [P] [US9] Adicionar comentario explicativo em bloco vazio em `scripts/seed_test_backlog.py` linha ~39
- [X] T052 [P] [US9] Adicionar comentario explicativo em bloco vazio em `tests/integration/infrastructure/test_allocation_integration.py` linha ~24
- [X] T053 [P] [US9] Adicionar comentario explicativo em bloco vazio em `tests/integration/test_seed_backlog.py` linha ~21

### S1172 - Parametros nao usados (4 issues)

- [X] T054 [P] [US9] Prefixar parametro `input_dto` com `_` em `src/backlog_manager/application/use_cases/planning/reset_planning.py` linha ~34 (faz parte da interface UseCase)
- [X] T055 [P] [US9] Resolver parametro nao usado `wave_to_feature` em `scripts/seed_test_backlog.py` linha ~644: remover ou prefixar `_`
- [X] T056 [P] [US9] Resolver parametro nao usado `strict` em `scripts/validate_allocation_data.py` linha ~267: remover ou prefixar `_`
- [X] T057 [P] [US9] Prefixar parametro `with_dependencies` com `_` em `tests/factories.py` linha ~19

### S1854 - Variaveis nao usadas (3 issues)

- [X] T058 [P] [US9] Remover atribuicao nao usada de `new_start` em `src/backlog_manager/domain/services/allocation_service.py` linha ~447
- [X] T059 [P] [US9] Substituir variavel `wb` por `_` em `tests/integration/infrastructure/excel/test_excel_service.py` linha ~179
- [X] T060 [P] [US9] Substituir variavel `cycle` por `_` em `tests/unit/domain/services/test_dependency_service.py` linha ~102

### S125 - Codigo comentado (1 issue)

- [X] T061 [P] [US9] Remover codigo comentado em `tests/integration/infrastructure/database/test_schema.py` linha ~86

**Checkpoint**: Todas as issues S108/S1172/S1854/S125 resolvidas

---

## Phase 11: User Story 10 - Adequacao a Convencoes e Otimizacoes Menores (Priority: P10)

**Goal**: Resolver naming conventions, async desnecessario, dict.fromkeys, variaveis locais e list() desnecessario

**Independent Test**: Verificar que convencoes sao aplicadas, falsos positivos suprimidos, e testes passam

### S100/S116 - Naming conventions em headless_mocks.py (12 issues)

- [X] T062 [US10] Adicionar comentarios `# noqa: N802` e docstrings em metodos camelCase que sao overrides Qt em `tests/headless_mocks.py` (10 issues S100 + 2 issues S116): documentar que sao overrides obrigatorios da API Qt

### S7503 - Funcoes async desnecessarias (7 issues)

- [X] T063 [US10] Remover `async` de `CalculateDurationUseCase.execute()` em `src/backlog_manager/application/use_cases/scheduling/calculate_duration.py` linha ~27 e atualizar TODOS os call sites para remover `await` (verificar `main_window.py`, `feature_dialog.py`, `developer_dialog.py`)
- [X] T064 [P] [US10] Remover `async` de `DeveloperService.create_developer()` em `src/backlog_manager/domain/services/developer_service.py` linha ~37 e atualizar call sites (`create_developer.py:44`, testes)
- [X] T065 [P] [US10] Remover `async` de `StoryService.swap_priorities()` em `src/backlog_manager/domain/services/story_service.py` linha ~87 e atualizar call sites (`move_priority.py:56/93`, testes)
- [X] T066 [P] [US10] Remover `async` de `StoryService.validate_can_move_up()` em `src/backlog_manager/domain/services/story_service.py` linha ~96 e atualizar call sites (`move_priority.py:47`, testes)
- [X] T067 [P] [US10] Remover `async` de 2 funcoes de teste em `tests/unit/presentation/viewmodels/test_excel_viewmodel.py` linhas ~265/386
- [X] T068 [P] [US10] Remover `async` de 1 funcao de teste em `tests/unit/presentation/viewmodels/test_schedule_viewmodel.py` linha ~110

### S7519 - dict.fromkeys() (3 issues)

- [X] T069 [P] [US10] Substituir construcao de dicionario por `dict.fromkeys()` em `src/backlog_manager/domain/services/dependency_service.py` linhas ~131/132 (2 instancias)
- [X] T070 [P] [US10] Substituir construcao de dicionario por `dict.fromkeys()` em `tests/integration/test_seed_backlog.py` linha ~123

### S1481 - Variaveis locais nao usadas em testes (9 issues)

- [X] T071 [P] [US10] Substituir 4 variaveis `msg` nao usadas por `_` em `tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py` linhas ~59/84/221/246
- [X] T072 [P] [US10] Resolver variavel `pattern` nao usada em `tests/unit/domain/services/test_allocation_logging.py` linha ~403
- [X] T073 [P] [US10] Substituir 4 variaveis `end` nao usadas por `_` em `tests/unit/domain/services/test_scheduling_service.py` linhas ~230/244/258/273

### S7504 - list() desnecessario (1 issue)

- [X] T074 [P] [US10] Remover `list()` desnecessario em `tests/unit/presentation/test_container.py` linha ~285

**Checkpoint**: Todas as 31 issues MINOR resolvidas

---

## Phase 12: Polish & Validacao Final

**Purpose**: Validacao cruzada e garantia de qualidade

- [X] T075 Executar `poetry run ruff check .` e corrigir quaisquer erros de linting introduzidos
- [X] T076 Executar `poetry run pytest` completo e garantir 0 falhas
- [X] T077 Executar `poetry run ruff check --fix .` para auto-correcoes de formatacao se necessario
- [X] T078 Validar via SonarQube MCP que issues foram resolvidas (usar `search_sonar_issues_in_projects` e `get_project_quality_gate_status`)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — iniciar imediatamente
- **US1 (Phase 2)**: Depende de Setup — correcao isolada em 1 arquivo
- **US2 (Phase 3)**: Depende de Setup — pode iniciar em paralelo com US1
- **US3 (Phase 4)**: Depende de US2 (arquivos compartilhados: `main_window.py`, `excel_viewmodel.py`)
- **US4 (Phase 5)**: Depende de US2 e US3 (arquivos compartilhados: `allocation_service.py`, `main_window.py`)
- **US5 (Phase 6)**: Pode iniciar em paralelo com US4 (scripts independentes)
- **US6 (Phase 7)**: Pode iniciar em paralelo com US4/US5 (arquivos independentes)
- **US7 (Phase 8)**: Pode iniciar em paralelo com US4/US5/US6 (arquivos de teste independentes)
- **US8 (Phase 9)**: Pode iniciar em paralelo com US7 (arquivos de teste diferentes)
- **US9 (Phase 10)**: Depende de US4 (compartilha `allocation_service.py`), resto paralelo
- **US10 (Phase 11)**: Depende de US2/US4 (call sites de async em arquivos ja modificados)
- **Polish (Phase 12)**: Depende de TODAS as fases anteriores

### User Story Dependencies

```
US1 ──────────────────────────────────────────────────── ▶ Polish
US2 ──┬──▶ US3 ──┬──▶ US4 ──┬──────────────────────── ▶ Polish
      │          │          ├──▶ US9 (allocation_service) ▶ Polish
      │          │          └──▶ US10 (async call sites)  ▶ Polish
      │          │
US5 ──┼──────────┼────────────────────────────────────── ▶ Polish
US6 ──┼──────────┼────────────────────────────────────── ▶ Polish
US7 ──┼──────────┼────────────────────────────────────── ▶ Polish
US8 ──┘          └────────────────────────────────────── ▶ Polish
```

### Parallel Opportunities

- **Setup**: T001 e T002 sequenciais (baseline)
- **US2**: T006, T007, T008, T009 em paralelo (arquivos diferentes)
- **US3**: T011, T012, T013, T014 em paralelo (locais diferentes)
- **US4**: T016-T028 em paralelo (exceto T029 que depende de entendimento dos outros metodos de allocation_service)
- **US5**: T031, T032, T033 em paralelo
- **US6**: T035, T036 em paralelo
- **US7**: T037, T038, T039 em paralelo
- **US8**: T040-T045 em paralelo
- **US9**: T046-T061 em paralelo (todos em arquivos diferentes)
- **US10**: T064-T074 em paralelo (exceto T063 que tem muitos call sites)
- **Cross-story**: US5, US6, US7, US8 podem executar em paralelo entre si

---

## Parallel Example: User Story 4

```bash
# Todas as refatoracoes em arquivos diferentes podem executar em paralelo:
Task: "Refatorar Story.__init__() em domain/entities/story.py"
Task: "Refatorar scheduling_service.py linha ~180"
Task: "Refatorar excel_service.py linha ~50"
Task: "Refatorar list_stories.py linha ~67"
Task: "Refatorar calculate_schedule.py linha ~50"
Task: "Refatorar get_developer_availability.py linha ~51"
Task: "Refatorar import_excel_use_case.py linha ~57"
Task: "Refatorar story_table_model.py linha ~196"

# allocation_service.py tem 6 metodos — executar sequencialmente dentro do mesmo arquivo:
Task: "Refatorar allocation_service.py linha ~846 (CC=17)"
Task: "Refatorar allocation_service.py linha ~558 (CC=23)"
Task: "Refatorar allocation_service.py linha ~635 (CC=25)"
Task: "Refatorar allocation_service.py linha ~404 (CC=34)"
Task: "Refatorar allocation_service.py linha ~740 (CC=36)"
Task: "Refatorar allocation_service.py linha ~926 (CC=79)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (baseline)
2. Complete Phase 2: US1 — correcao BLOCKER S3516
3. **STOP e VALIDAR**: 0 issues BLOCKER no SonarQube
4. Push para validacao automatica

### Incremental Delivery

1. US1 (BLOCKER) → Validar → 0 BLOCKER
2. US2 + US3 (bugs async) → Validar → Tasks rastreadas + CancelledError propagado
3. US4 + US5 (complexidade) → Validar → CC <= 15 em todos os metodos
4. US6 + US7 + US8 (quick fixes) → Validar → Literais, type hints, docstrings, floats
5. US9 + US10 (limpeza + convencoes) → Validar → Codigo limpo
6. Polish → Quality Gate OK

### Execucao Otimizada (paralelo)

```
Fase A: US1 (blocker)
Fase B: US2 + US5 + US6 + US7 + US8 (paralelo — arquivos independentes)
Fase C: US3 (depende de US2 para main_window.py / excel_viewmodel.py)
Fase D: US4 (depende de US2/US3 para arquivos compartilhados)
Fase E: US9 + US10 (depende de US4 para allocation_service.py e call sites)
Fase F: Polish & validacao final
```

---

## Notes

- Todas as correcoes sao in-place — nenhum arquivo novo criado
- Interface publica de TODOS os metodos DEVE ser preservada
- allocation_service.py e o arquivo mais critico: 6 metodos S3776 + 1 S1854 — requer atencao especial
- main_window.py tambem e critico: 4 issues S7502 + 1 S7497 + ~25 instancias de task tracking
- Convencao camelCase em headless_mocks.py sao falsos positivos (overrides Qt) — suprimir, nao renomear
- Remocao de `async` (S7503) DEVE atualizar TODOS os call sites simultaneamente
