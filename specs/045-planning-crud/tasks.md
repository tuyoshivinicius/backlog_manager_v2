# Tasks: Modulo de Planejamentos (CRUD Completo)

**Input**: Design documents from `/specs/045-planning-crud/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/planning-ui-contract.md

**Tests**: Incluidos conforme quickstart.md e plan.md indicam testes unitarios e de integracao.

**Organization**: Tasks agrupadas por user story para implementacao e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story a que pertence (US1–US7)
- Caminhos exatos incluidos nas descricoes

---

## Phase 1: Setup

**Purpose**: Criar estrutura de diretorios para novos arquivos do modulo Planning

- [X] T001 Criar diretorio `src/backlog_manager/application/use_cases/planning/` com `__init__.py`
- [X] T002 [P] Criar diretorio `src/backlog_manager/application/dto/planning/` com `__init__.py`
- [X] T003 [P] Criar diretorio `src/backlog_manager/domain/exceptions/` com `__init__.py` (se nao existir)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Entidade Planning, schema, migracao, repositorios e modificacoes na Story — BLOQUEIA todas as user stories

**⚠️ CRITICAL**: Nenhuma user story pode comecar ate esta fase estar completa

- [X] T004 Criar entidade de dominio Planning com validacoes de nome (vazio, max 200 chars) em `src/backlog_manager/domain/entities/planning.py`
- [X] T005 [P] Criar excecoes de dominio: PlanningException(BacklogManagerException) como base, DuplicatePlanningNameException(PlanningException) e ActivePlanningDeletionException(PlanningException), importando BacklogManagerException de `domain.exceptions.base` em `src/backlog_manager/domain/exceptions/planning_exceptions.py`
- [X] T006 [P] Adicionar PlanningRepository Protocol (add, get_by_id, get_by_name, get_all, update, delete, exists, count_stories, update_timestamp) em `src/backlog_manager/domain/interfaces/repositories.py`
- [X] T007 Modificar entidade Story adicionando campo obrigatorio `planning_id: int` em `src/backlog_manager/domain/entities/story.py`
- [X] T008 Criar DTOs de Planning (CreatePlanningInput, UpdatePlanningInput, PlanningOutput, PlanningListItem) em `src/backlog_manager/application/dto/planning/planning_dto.py`
- [X] T009 Atualizar schema SQL: criar tabela Planning, alterar Story com planning_id e composite PK (planning_id, id), alterar Story_Dependency com planning_id em `src/backlog_manager/infrastructure/database/schema.sql`
- [X] T010 Implementar logica de migracao automatica (deteccao schema antigo via PRAGMA table_info, criacao "Planejamento Inicial", rename+copy+drop pattern) em `src/backlog_manager/infrastructure/database/sqlite_connection.py`
- [X] T011 Implementar SQLitePlanningRepository (todos os metodos do Protocol) em `src/backlog_manager/infrastructure/database/repositories/planning_repository.py`
- [X] T012 Modificar SQLiteStoryRepository: adicionar planning_id como parametro em todos os metodos de query (get_all, get_by_id, exists, get_by_status, get_by_developer, get_by_feature, get_max_id_number, get_max_priority, get_by_priority, count_by_developer, delete) e composite key em add/update em `src/backlog_manager/infrastructure/database/repositories/story_repository.py`
- [X] T013 Modificar SQLiteStoryDependencyRepository: adicionar planning_id em todos os metodos para scoping intra-planejamento em `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py`
- [X] T014 Modificar UnitOfWork: adicionar propriedade `plannings: PlanningRepository` em `src/backlog_manager/infrastructure/database/unit_of_work.py`
- [X] T015 Registrar novos use cases (CreatePlanning, ListPlannings, UpdatePlanning, DeletePlanning, GetActivePlanning, SetActivePlanning, MigrateOrphanStories), PlanningRepository e PlanningViewModel no DIContainer em `src/backlog_manager/presentation/container.py`

### Testes Foundational

- [X] T016 [P] Criar testes unitarios da entidade Planning (validacao nome vazio, nome longo, criacao valida) em `tests/unit/domain/test_planning.py`
- [X] T017 [P] Criar testes de integracao do SQLitePlanningRepository (add, get_by_id, get_by_name, get_all, update, delete, count_stories, update_timestamp) em `tests/integration/infrastructure/test_planning_repository.py`
- [X] T018 [P] Criar testes de integracao da migracao automatica (schema antigo detectado, "Planejamento Inicial" criado, historias orfas migradas, schema novo correto) em `tests/integration/infrastructure/test_planning_migration.py`

- [X] T066 Garantir que updated_at do Planning eh atualizado em todas as operacoes que modificam historias (criar, editar, excluir, importar, alocar, agendar, resetar) via chamada a PlanningRepository.update_timestamp nos use cases relevantes

**Checkpoint**: Fundacao pronta — implementacao de user stories pode comecar

---

## Phase 3: User Story 1 — Criar um Novo Planejamento (Priority: P1) 🎯 MVP

**Goal**: Usuario cria planejamento nomeado via menu, sistema o define como ativo, titulo da janela reflete o planejamento

**Independent Test**: Criar planejamento, verificar na lista e no titulo da janela

### Implementation

- [X] T019 [US1] Implementar CreatePlanningUseCase (valida unicidade de nome, cria entidade, persiste via repositorio, retorna PlanningOutput) em `src/backlog_manager/application/use_cases/planning/create_planning.py`
- [X] T020 [US1] Criar PlanningViewModel com signal planning_created(int, str) e metodo async create_planning(name) em `src/backlog_manager/presentation/viewmodels/planning_viewmodel.py`
- [X] T021 [US1] Criar CreatePlanningDialog (QDialog modal com campo nome, validacao vazio/max 200, botoes Cancelar/Criar, retorna str|None) em `src/backlog_manager/presentation/views/create_planning_dialog.py`
- [X] T022 [US1] Adicionar menu "Arquivo > Novo Planejamento" (Ctrl+N) na MainWindow conectado ao CreatePlanningDialog em `src/backlog_manager/presentation/views/main_window.py`
- [X] T023 [US1] Adicionar signal active_planning_changed(int, str) no MainWindowViewModel e metodo para atualizar titulo da janela com nome do planejamento ativo em `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`
- [X] T024 [US1] Conectar MainWindow para atualizar titulo no formato "Backlog Manager — {nome}" ao receber active_planning_changed em `src/backlog_manager/presentation/views/main_window.py`

### Testes US1

- [X] T025 [P] [US1] Criar testes unitarios do CreatePlanningUseCase (criacao valida, nome duplicado, nome vazio) em `tests/unit/application/test_planning_use_cases.py`

**Checkpoint**: Usuario consegue criar planejamentos e ver o nome no titulo

---

## Phase 4: User Story 7 — Comportamento Inicial sem Planejamento (Priority: P1)

**Goal**: Primeiro uso exige criacao de planejamento; reaberturas restauram ultimo planejamento ativo via QSettings

**Independent Test**: Iniciar com banco vazio → dialogo de criacao forcado; iniciar com planejamento salvo → restaurado automaticamente

### Implementation

- [X] T026 [US7] Implementar GetActivePlanningUseCase (le last_active_id do QSettings, verifica existencia no banco, retorna PlanningOutput|None) em `src/backlog_manager/application/use_cases/planning/get_active_planning.py`
- [X] T027 [US7] Implementar SetActivePlanningUseCase (valida existencia, persiste planning_id no QSettings) em `src/backlog_manager/application/use_cases/planning/set_active_planning.py`
- [X] T028 [US7] Adicionar logica de bootstrap no MainWindowViewModel.initialize(): verificar planejamentos existentes, carregar ultimo ativo ou forcar criacao em `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`
- [X] T029 [US7] Modificar CreatePlanningDialog para ocultar botao "Cancelar" no modo bootstrap (primeiro uso, banco vazio) em `src/backlog_manager/presentation/views/create_planning_dialog.py`
- [X] T030 [US7] Integrar bootstrap na MainWindow: exibir CreatePlanningDialog modal antes de carregar historias quando nenhum planejamento existe em `src/backlog_manager/presentation/views/main_window.py`

### Testes US7

- [X] T031 [P] [US7] Criar testes unitarios do GetActivePlanningUseCase e SetActivePlanningUseCase em `tests/unit/application/test_planning_use_cases.py`

**Checkpoint**: Aplicacao inicializa corretamente em primeiro uso e reaberturas

---

## Phase 5: User Story 2 — Abrir/Restaurar Planejamento Existente (Priority: P1)

**Goal**: Dialogo lista planejamentos (nome, qtd historias, data modificacao) com selecao para ativar e carregar historias

**Independent Test**: Criar dois planejamentos com historias diferentes, alternar e verificar tabela

### Implementation

- [X] T032 [US2] Implementar ListPlanningsUseCase (retorna lista de PlanningListItem com nome, story_count, updated_at) em `src/backlog_manager/application/use_cases/planning/list_plannings.py`
- [X] T033 [US2] Adicionar metodos list_plannings() e activate_planning(planning_id) no PlanningViewModel em `src/backlog_manager/presentation/viewmodels/planning_viewmodel.py`
- [X] T034 [US2] Criar OpenPlanningDialog (QDialog com QTableWidget: colunas Nome/Historias/Modificado/Acoes, selecao unica, duplo-clique abre, planejamento ativo com bullet e sem botao excluir, lista vazia com mensagem) em `src/backlog_manager/presentation/views/open_planning_dialog.py`
- [X] T035 [US2] Adicionar menu "Arquivo > Abrir Planejamento" (Ctrl+O) na MainWindow conectado ao OpenPlanningDialog em `src/backlog_manager/presentation/views/main_window.py`
- [X] T036 [US2] Implementar troca de planejamento ativo: ao selecionar no dialogo, atualizar QSettings, recarregar historias scoped na tabela principal, atualizar titulo em `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`

### Testes US2

- [X] T037 [P] [US2] Criar testes unitarios do ListPlanningsUseCase em `tests/unit/application/test_planning_use_cases.py`

**Checkpoint**: Usuario alterna entre planejamentos e ve historias corretas

---

## Phase 6: User Story 3 — Associacao de Historias ao Planejamento Ativo (Priority: P1)

**Goal**: Historias criadas/importadas/duplicadas associadas ao planejamento ativo; tabela exibe apenas historias do ativo

**Independent Test**: Criar historias em planejamentos diferentes, verificar isolamento

### Implementation

- [X] T038 [US3] Modificar CreateStoryUseCase para receber e persistir planning_id do planejamento ativo em `src/backlog_manager/application/use_cases/story/create_story.py`
- [X] T039 [US3] Modificar ImportExcelUseCase para associar todas as historias importadas ao planning_id ativo em `src/backlog_manager/application/use_cases/excel/import_excel_use_case.py`
- [X] T040 [US3] Modificar DuplicateStoryUseCase para associar a copia ao planning_id ativo em `src/backlog_manager/application/use_cases/story/duplicate_story.py`
- [X] T041 [US3] Modificar ListStoriesUseCase para filtrar por planning_id ativo em `src/backlog_manager/application/use_cases/story/list_stories.py` e propagar no carregamento da tabela em `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`
- [X] T042 [US3] Adicionar planning_id como parametro nos seguintes use cases para scoping intra-planejamento:
  - `src/backlog_manager/application/use_cases/allocation/execute_allocation.py` (ExecuteAllocationUseCase)
  - `src/backlog_manager/application/use_cases/allocation/get_developer_availability.py` (GetDeveloperAvailabilityUseCase)
  - `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py` (CalculateScheduleUseCase)
  - `src/backlog_manager/application/use_cases/scheduling/calculate_story_dates.py` (CalculateStoryDatesUseCase)
  - `src/backlog_manager/application/use_cases/scheduling/calculate_duration.py` (CalculateDurationUseCase)
  - `src/backlog_manager/application/use_cases/dependency/add_dependency.py` (AddDependencyUseCase)
  - `src/backlog_manager/application/use_cases/dependency/remove_dependency.py` (RemoveDependencyUseCase)
  - `src/backlog_manager/application/use_cases/dependency/get_dependencies.py` (GetDependenciesUseCase)
  - `src/backlog_manager/application/use_cases/dependency/get_dependents.py` (GetDependentsUseCase)

### Testes US3

- [X] T063 [P] [US3] Criar testes unitarios do fluxo de criacao de historia com planning_id (CreateStoryUseCase recebe planning_id, historia persiste com referencia correta) em `tests/unit/application/test_story_planning_scope.py`
- [X] T064 [P] [US3] Criar testes unitarios do fluxo de importacao Excel com planning_id (ImportExcelUseCase associa historias importadas ao planning_id ativo) em `tests/unit/application/test_story_planning_scope.py`
- [X] T065 [P] [US3] Criar teste de integracao de isolamento entre planejamentos (criar historias em dois planejamentos, verificar que load_stories retorna apenas historias do ativo, IDs repetidos entre planejamentos nao conflitam) em `tests/integration/infrastructure/test_story_planning_isolation.py`

**Checkpoint**: Historias isoladas por planejamento, tabela exibe apenas ativo

---

## Phase 7: User Story 4 — Editar Planejamento (Priority: P2)

**Goal**: Renomear planejamento via edicao inline no dialogo "Abrir Planejamento"

**Independent Test**: Renomear planejamento, verificar nome no titulo e na lista

### Implementation

- [X] T043 [US4] Implementar UpdatePlanningUseCase (valida unicidade do novo nome, atualiza entidade, persiste, atualiza updated_at) em `src/backlog_manager/application/use_cases/planning/update_planning.py`
- [X] T044 [US4] Adicionar metodo rename_planning(planning_id, new_name) e signal planning_renamed(int, str) no PlanningViewModel em `src/backlog_manager/presentation/viewmodels/planning_viewmodel.py`
- [X] T045 [US4] Implementar edicao inline de nome no OpenPlanningDialog: botao editar torna celula editavel, salva ao perder foco/Enter, exibe erro se nome duplicado em `src/backlog_manager/presentation/views/open_planning_dialog.py`
- [X] T046 [US4] Atualizar titulo da janela se o planejamento renomeado for o ativo em `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`

### Testes US4

- [X] T047 [P] [US4] Criar testes unitarios do UpdatePlanningUseCase (rename valido, nome duplicado) em `tests/unit/application/test_planning_use_cases.py`

**Checkpoint**: Planejamentos podem ser renomeados com validacao

---

## Phase 8: User Story 5 — Excluir Planejamento (Priority: P2)

**Goal**: Excluir planejamento inativo com confirmacao e cascade de historias

**Independent Test**: Excluir planejamento com historias, verificar remocao completa do banco

### Implementation

- [X] T048 [US5] Implementar DeletePlanningUseCase (impede exclusao do ativo, confirma contagem de historias, deleta em cascata) em `src/backlog_manager/application/use_cases/planning/delete_planning.py`
- [X] T049 [US5] Adicionar metodo delete_planning(planning_id) e signal planning_deleted(int) no PlanningViewModel em `src/backlog_manager/presentation/viewmodels/planning_viewmodel.py`
- [X] T050 [US5] Implementar botao excluir no OpenPlanningDialog: oculto para planejamento ativo, QMessageBox de confirmacao com contagem de historias, remove da lista apos exclusao em `src/backlog_manager/presentation/views/open_planning_dialog.py`
- [X] T051 [US5] Implementar MigrateOrphanStoriesUseCase (se necessario para cenario de exclusao do ultimo planejamento → bootstrap) em `src/backlog_manager/application/use_cases/planning/migrate_orphan_stories.py`

### Testes US5

- [X] T052 [P] [US5] Criar testes unitarios do DeletePlanningUseCase (exclusao valida, impedir exclusao do ativo, cascade de historias) em `tests/unit/application/test_planning_use_cases.py`

**Checkpoint**: Planejamentos inativos podem ser excluidos com seguranca

---

## Phase 9: User Story 6 — Renomear "Novo Planejamento" para "Reiniciar Planejamento" (Priority: P2)

**Goal**: Evitar confusao renomeando a funcionalidade existente no menu Ferramentas

**Independent Test**: Verificar label "Reiniciar Planejamento" no menu e funcionalidade de reset operando sobre historias do ativo

### Implementation

- [X] T053 [US6] Renomear item de menu "Novo Planejamento" para "Reiniciar Planejamento" e alterar shortcut de Ctrl+Shift+N para Ctrl+Shift+R em `src/backlog_manager/presentation/views/main_window.py`
- [X] T054 [US6] Modificar ResetPlanningUseCase (ou equivalente) para receber planning_id e operar somente sobre historias do planejamento ativo em `src/backlog_manager/application/use_cases/planning/reset_planning.py` (ou arquivo existente)
- [X] T055 [US6] Modificar CountAffectedStoriesUseCase para receber planning_id e contar apenas historias do planejamento ativo em `src/backlog_manager/application/use_cases/planning/count_affected_stories.py` (ou arquivo existente)
- [X] T056 [US6] Desabilitar opcao "Reiniciar Planejamento" no menu quando nao ha planejamento ativo em `src/backlog_manager/presentation/views/main_window.py`

### Testes US6

- [X] T067 [P] [US6] Criar testes unitarios do ResetPlanningUseCase scoped por planning_id (reset limpa apenas historias do planejamento ativo, nao afeta outros planejamentos) em `tests/unit/application/test_reset_planning_scoped.py`
- [X] T068 [P] [US6] Criar testes unitarios do CountAffectedStoriesUseCase scoped por planning_id (conta apenas historias do planejamento ativo) em `tests/unit/application/test_reset_planning_scoped.py`

**Checkpoint**: Menu renomeado, reset scoped ao planejamento ativo

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias que afetam multiplas user stories

- [X] T057 [P] Adicionar logging em operacoes criticas (criacao, exclusao, migracao, troca de planejamento) nos use cases relevantes
- [X] T058 [P] Revisar que docstrings e type hints estao presentes em classes/metodos publicos novos de Phase 10
- [X] T059 [P] Revisar e atualizar docstrings em todas as classes/metodos publicos novos
- [X] T060 Executar validacao do quickstart.md (fluxo completo: primeiro uso → criar planejamento → cadastrar historias → criar segundo planejamento → alternar → editar → excluir → reiniciar)
- [X] T061 [P] Garantir type hints em todas as assinaturas novas e modificadas
- [X] T062 Rodar suite de testes completa e corrigir regressoes causadas pela mudanca de PK do Story

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — pode comecar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEIA todas as user stories
- **US1 (Phase 3)**: Depende de Foundational — ponto de entrada do modulo
- **US7 (Phase 4)**: Depende de US1 (usa CreatePlanningDialog)
- **US2 (Phase 5)**: Depende de Foundational — pode rodar em paralelo com US1
- **US3 (Phase 6)**: Depende de Foundational + US7 (precisa do planning ativo definido)
- **US4 (Phase 7)**: Depende de US2 (edicao ocorre dentro do OpenPlanningDialog)
- **US5 (Phase 8)**: Depende de US2 (exclusao ocorre dentro do OpenPlanningDialog)
- **US6 (Phase 9)**: Depende de Foundational — independente das demais stories
- **Polish (Phase 10)**: Depende de todas as user stories desejadas estarem completas

### User Story Dependencies

- **US1 (P1)**: Foundational → pode comecar apos Phase 2
- **US7 (P1)**: Foundational + US1 → depende do CreatePlanningDialog
- **US2 (P1)**: Foundational → pode comecar apos Phase 2 (paralelo com US1)
- **US3 (P1)**: Foundational + bootstrap funcional (US7)
- **US4 (P2)**: US2 → requer OpenPlanningDialog
- **US5 (P2)**: US2 → requer OpenPlanningDialog
- **US6 (P2)**: Foundational → independente

### Within Each User Story

- Use cases antes de viewmodels
- Viewmodels antes de views/dialogs
- Core implementation antes de integracao com MainWindow
- Testes podem rodar em paralelo entre si

### Parallel Opportunities

- T001, T002, T003 (Setup) podem rodar em paralelo
- T004, T005, T006 (entidade, excecoes, protocol) podem rodar em paralelo
- T016, T017, T018 (testes foundational) podem rodar em paralelo
- US1 e US2 podem comecar em paralelo apos Foundational
- US4 e US5 podem rodar em paralelo (ambos no OpenPlanningDialog mas em areas diferentes)
- US6 eh independente e pode rodar em paralelo com US4/US5
- Todos os testes marcados [P] podem rodar em paralelo

---

## Parallel Example: Foundational

```bash
# Launch entity + exceptions + protocol in parallel:
Task T004: "Criar entidade Planning em domain/entities/planning.py"
Task T005: "Criar excecoes em domain/exceptions/planning_exceptions.py"
Task T006: "Adicionar PlanningRepository Protocol em domain/interfaces/repositories.py"

# Launch all foundational tests in parallel:
Task T016: "Testes unitarios entidade Planning"
Task T017: "Testes integracao PlanningRepository"
Task T018: "Testes integracao migracao"
```

## Parallel Example: User Stories P1

```bash
# After Foundational, launch US1 and US2 in parallel:
# Stream 1 (US1): T019 → T020 → T021 → T022 → T023 → T024
# Stream 2 (US2): T032 → T033 → T034 → T035 → T036
```

---

## Implementation Strategy

### MVP First (US1 + US7 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL — bloqueia tudo)
3. Complete Phase 3: US1 — Criar Planejamento
4. Complete Phase 4: US7 — Bootstrap
5. **STOP and VALIDATE**: Testar criacao de planejamento e primeiro uso
6. Deploy/demo se pronto

### Incremental Delivery

1. Setup + Foundational → Base pronta
2. US1 → Criar planejamentos → Validar (MVP!)
3. US7 → Bootstrap correto → Validar
4. US2 → Abrir/restaurar planejamentos → Validar
5. US3 → Historias scoped por planejamento → Validar
6. US4 + US5 + US6 → CRUD completo → Validar
7. Polish → Qualidade final

### Parallel Team Strategy

Com multiplos desenvolvedores apos Foundational:

1. Equipe completa Setup + Foundational juntos
2. Apos Foundational:
   - Dev A: US1 → US7 (criar + bootstrap)
   - Dev B: US2 → US4/US5 (abrir + editar/excluir)
   - Dev C: US3 + US6 (scoping + rename)
3. Stories completam e integram independentemente

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica
- Cada user story deve ser completavel e testavel independentemente
- Commit apos cada task ou grupo logico
- Pare em qualquer checkpoint para validar story independentemente
- A mudanca de PK composta (planning_id, id) no Story eh a maior area de risco — testes de integracao (T017, T018) sao criticos
