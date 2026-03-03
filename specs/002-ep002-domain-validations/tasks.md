# Tasks: EP-002 Dominio Core - Entidades e Validacoes

**Input**: Design documents from `/specs/002-ep002-domain-validations/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Incluidos conforme solicitado na spec.md (TDD, cobertura 100% em validacoes).

**Organization**: Tasks organizadas por user story para permitir implementacao e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: Qual user story esta task pertence (e.g., US1, US2, US3)
- Caminhos exatos incluidos nas descricoes

---

## Phase 1: Setup

**Purpose**: Verificacao do ambiente e estado atual do projeto

- [X] T001 Verificar ambiente Python 3.11+ e Poetry instalados
- [X] T002 Executar `poetry install` para garantir dependencias atualizadas
- [X] T003 Executar `poetry run pytest -v` para verificar que todos os testes EP-001 passam

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Mudanca no enum StoryStatus que DEVE ser completada antes de qualquer user story

**⚠️ CRITICAL**: StoryStatus e usado por todas as entidades Story. Deve ser modificado primeiro.

- [X] T004 [P] Modificar StoryStatus de 4 para 5 estados em src/backlog_manager/domain/value_objects/story_status.py
- [X] T005 [P] Criar testes unitarios para StoryStatus em tests/unit/domain/value_objects/test_story_status.py

**Checkpoint**: StoryStatus com 5 estados (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) e testes passando

---

## Phase 3: User Story 1 - Validacao de Story Points (Priority: P1) 🎯 MVP

**Goal**: Garantir que apenas valores Fibonacci {3, 5, 8, 13} sejam aceitos para story_points

**Independent Test**: Criar Stories com diferentes valores de story_points e verificar aceitacao/rejeicao

### Tests for User Story 1

> **NOTE: Escrever testes PRIMEIRO, garantir que FALHAM antes da implementacao**

- [ ] T006 [P] [US1] Criar/expandir testes para StoryPoint enum em tests/unit/domain/value_objects/test_story_point.py
- [ ] T007 [P] [US1] Adicionar testes de story_points validos em tests/unit/domain/entities/test_story.py
- [ ] T008 [P] [US1] Adicionar testes de story_points invalidos (1, 2, 4, 7, 10, 20) em tests/unit/domain/entities/test_story.py

### Implementation for User Story 1

- [ ] T009 [US1] Verificar que StoryPoint enum em src/backlog_manager/domain/value_objects/story_point.py possui valores {3, 5, 8, 13}
- [X] T010 [US1] Verificar/ajustar conversao automatica int -> StoryPoint em src/backlog_manager/domain/entities/story.py
- [X] T011 [US1] Executar `poetry run pytest tests/unit/domain -v` para validar US1

**Checkpoint**: Story rejeita valores de story_points fora de {3, 5, 8, 13} com ValueError

---

## Phase 4: User Story 2 - Maquina de Estados do Status (Priority: P1)

**Goal**: StoryStatus com 5 estados conforme SRS 6.5 e transicoes livres

**Independent Test**: Verificar enum StoryStatus e transicoes em Story

### Tests for User Story 2

- [X] T012 [P] [US2] Verificar testes de StoryStatus incluem todos os 5 estados em tests/unit/domain/value_objects/test_story_status.py
- [X] T013 [P] [US2] Adicionar testes de transicoes de status em tests/unit/domain/entities/test_story.py

### Implementation for User Story 2

- [X] T014 [US2] Verificar que Story usa BACKLOG como status padrao em src/backlog_manager/domain/entities/story.py
- [X] T015 [US2] Executar `poetry run pytest tests/unit/domain -v` para validar US2

**Checkpoint**: Story aceita todos os 5 estados e permite transicoes livres

---

## Phase 5: User Story 3 - Validacao de Invariantes da Entidade Story (Priority: P1)

**Goal**: Validar todos os invariantes de Story no construtor

**Independent Test**: Criar Stories com diferentes combinacoes de campos invalidos

### Tests for User Story 3

- [X] T016 [P] [US3] Adicionar teste para ID vazio em tests/unit/domain/entities/test_story.py
- [X] T017 [P] [US3] Adicionar teste para ID fora do padrao COMPONENTE-NNN em tests/unit/domain/entities/test_story.py
- [X] T018 [P] [US3] Adicionar teste para component vazio em tests/unit/domain/entities/test_story.py
- [X] T019 [P] [US3] Adicionar teste para component > 50 chars em tests/unit/domain/entities/test_story.py
- [X] T020 [P] [US3] Adicionar teste para name vazio em tests/unit/domain/entities/test_story.py
- [X] T021 [P] [US3] Adicionar teste para name > 200 chars em tests/unit/domain/entities/test_story.py
- [X] T022 [P] [US3] Adicionar teste para priority negativa em tests/unit/domain/entities/test_story.py
- [X] T023 [P] [US3] Adicionar teste para start_date > end_date em tests/unit/domain/entities/test_story.py

### Implementation for User Story 3

- [X] T024 [US3] Verificar que todas as validacoes existem em src/backlog_manager/domain/entities/story.py __post_init__
- [X] T025 [US3] Executar `poetry run pytest tests/unit/domain/entities/test_story.py -v` para validar US3

**Checkpoint**: Story rejeita todas as combinacoes de campos invalidos com mensagens descritivas

---

## Phase 6: User Story 4 - Validacao de Duracao (Priority: P2)

**Goal**: Validar que duration >= 0 quando definido

**Independent Test**: Criar Stories com diferentes valores de duration

### Tests for User Story 4

- [X] T026 [P] [US4] Adicionar teste para duration = None (valido) em tests/unit/domain/entities/test_story.py
- [X] T027 [P] [US4] Adicionar teste para duration = 0 (valido) em tests/unit/domain/entities/test_story.py
- [X] T028 [P] [US4] Adicionar teste para duration = 3 (valido) em tests/unit/domain/entities/test_story.py
- [X] T029 [P] [US4] Adicionar teste para duration = -1 (invalido) em tests/unit/domain/entities/test_story.py

### Implementation for User Story 4

- [X] T030 [US4] Adicionar validacao `duration >= 0` no __post_init__ em src/backlog_manager/domain/entities/story.py
- [X] T031 [US4] Executar `poetry run pytest tests/unit/domain/entities/test_story.py -v` para validar US4

**Checkpoint**: Story rejeita duration negativo com ValueError "Duracao deve ser >= 0: {value}"

---

## Phase 7: User Story 5 - Validacao de Auto-dependencia (Priority: P2)

**Goal**: Repositorio rejeita story_id == depends_on_id

**Independent Test**: Tentar adicionar dependencia de historia para ela mesma

### Tests for User Story 5

- [X] T032 [P] [US5] Adicionar teste de auto-dependencia rejeitada em tests/integration/infrastructure/database/repositories/test_story_dependency_repository.py
- [X] T033 [P] [US5] Adicionar teste de dependencia valida (A -> B) aceita em tests/integration/infrastructure/database/repositories/test_story_dependency_repository.py

### Implementation for User Story 5

- [X] T034 [US5] Adicionar validacao de auto-dependencia no metodo add() em src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py
- [X] T035 [US5] Executar `poetry run pytest tests/integration -v` para validar US5

**Checkpoint**: Repositorio rejeita auto-dependencia com ValueError "Historia nao pode depender de si mesma"

---

## Phase 8: User Story 6 - Validacao de Entidade Developer (Priority: P2)

**Goal**: Validar invariantes de Developer (name nao vazio, max 100 chars)

**Independent Test**: Criar Developers com diferentes valores de name

### Tests for User Story 6

- [X] T036 [P] [US6] Adicionar teste para name valido em tests/unit/domain/entities/test_developer.py
- [X] T037 [P] [US6] Adicionar teste para name vazio em tests/unit/domain/entities/test_developer.py
- [X] T038 [P] [US6] Adicionar teste para name apenas espacos em tests/unit/domain/entities/test_developer.py
- [X] T039 [P] [US6] Adicionar teste para name > 100 chars em tests/unit/domain/entities/test_developer.py

### Implementation for User Story 6

- [X] T040 [US6] Verificar validacoes existentes em src/backlog_manager/domain/entities/developer.py __post_init__
- [X] T041 [US6] Executar `poetry run pytest tests/unit/domain/entities/test_developer.py -v` para validar US6

**Checkpoint**: Developer rejeita name vazio ou > 100 chars com ValueError

---

## Phase 9: User Story 7 - Validacao de Entidade Feature (Priority: P2)

**Goal**: Validar invariantes de Feature (name nao vazio, max 100 chars, wave > 0)

**Independent Test**: Criar Features com diferentes valores de name e wave

### Tests for User Story 7

- [X] T042 [P] [US7] Adicionar teste para name valido e wave valida em tests/unit/domain/entities/test_feature.py
- [X] T043 [P] [US7] Adicionar teste para name vazio em tests/unit/domain/entities/test_feature.py
- [X] T044 [P] [US7] Adicionar teste para name > 100 chars em tests/unit/domain/entities/test_feature.py
- [X] T045 [P] [US7] Adicionar teste para wave = 0 em tests/unit/domain/entities/test_feature.py
- [X] T046 [P] [US7] Adicionar teste para wave = -1 em tests/unit/domain/entities/test_feature.py

### Implementation for User Story 7

- [X] T047 [US7] Verificar validacoes existentes em src/backlog_manager/domain/entities/feature.py __post_init__
- [X] T048 [US7] Executar `poetry run pytest tests/unit/domain/entities/test_feature.py -v` para validar US7

**Checkpoint**: Feature rejeita name vazio/longo ou wave <= 0 com ValueError

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final e verificacao de qualidade

- [X] T049 Executar `poetry run pytest -v` - todos os testes devem passar
- [X] T050 Executar `poetry run pytest --cov=src/backlog_manager --cov-report=term-missing` - verificar cobertura >= 80%
- [X] T051 Executar `poetry run mypy src/backlog_manager` - verificar sem erros de tipo
- [X] T052 Executar `poetry run ruff check src/backlog_manager` - verificar sem erros de lint
- [X] T053 Revisar que todas as mensagens de erro estao em portugues sem acentos
- [X] T054 Executar quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - pode iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup - BLOQUEIA todas as user stories
- **User Stories (Phase 3-9)**: Todas dependem de Foundational (Phase 2)
  - US1, US2, US3 sao P1 - devem ser completadas primeiro
  - US4, US5, US6, US7 sao P2 - podem ser feitas apos P1
- **Polish (Phase 10)**: Depende de todas as user stories completadas

### User Story Dependencies

| User Story | Priority | Depende de | Pode ser paralelo com |
|------------|----------|------------|----------------------|
| US1 (Story Points) | P1 | Foundational | US2, US3 |
| US2 (Status) | P1 | Foundational | US1, US3 |
| US3 (Invariantes) | P1 | Foundational | US1, US2 |
| US4 (Duration) | P2 | Foundational | US5, US6, US7 |
| US5 (Auto-dep) | P2 | Foundational | US4, US6, US7 |
| US6 (Developer) | P2 | Foundational | US4, US5, US7 |
| US7 (Feature) | P2 | Foundational | US4, US5, US6 |

### Within Each User Story

- Testes DEVEM ser escritos e FALHAR antes da implementacao
- Verificar implementacao existente
- Adicionar validacoes faltantes
- Story completa antes de mover para proxima prioridade

### Parallel Opportunities

- T004, T005 (Foundational) podem rodar em paralelo
- Todos os testes de uma user story marcados [P] podem rodar em paralelo
- User stories de mesma prioridade podem ser trabalhadas em paralelo

---

## Parallel Example: User Story 3 (Invariantes)

```bash
# Launch all tests for User Story 3 together:
Task: "T016 [P] [US3] Adicionar teste para ID vazio"
Task: "T017 [P] [US3] Adicionar teste para ID fora do padrao"
Task: "T018 [P] [US3] Adicionar teste para component vazio"
Task: "T019 [P] [US3] Adicionar teste para component > 50 chars"
Task: "T020 [P] [US3] Adicionar teste para name vazio"
Task: "T021 [P] [US3] Adicionar teste para name > 200 chars"
Task: "T022 [P] [US3] Adicionar teste para priority negativa"
Task: "T023 [P] [US3] Adicionar teste para start_date > end_date"
```

---

## Implementation Strategy

### MVP First (User Stories P1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (StoryStatus 5 estados)
3. Complete Phase 3: User Story 1 (Story Points)
4. Complete Phase 4: User Story 2 (Status)
5. Complete Phase 5: User Story 3 (Invariantes)
6. **STOP and VALIDATE**: Testar independentemente
7. Deploy/demo se pronto

### Incremental Delivery

1. Setup + Foundational → Base pronta
2. Add US1 → Story Points validados → Test (MVP!)
3. Add US2 → Status 5 estados funcionando → Test
4. Add US3 → Invariantes completos → Test
5. Add US4-US7 → Validacoes completas → Test
6. Cada story adiciona valor sem quebrar anteriores

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica
- Cada user story deve ser independentemente completavel e testavel
- Verificar que testes FALHAM antes de implementar
- Commit apos cada task ou grupo logico
- Parar em qualquer checkpoint para validar story independentemente
- Evitar: tasks vagas, conflitos de mesmo arquivo, dependencias cross-story

---

## Summary

| Metrica | Valor |
|---------|-------|
| Total de Tasks | 54 |
| Tasks Phase 1 (Setup) | 3 |
| Tasks Phase 2 (Foundational) | 2 |
| Tasks US1 (Story Points) | 6 |
| Tasks US2 (Status) | 4 |
| Tasks US3 (Invariantes) | 10 |
| Tasks US4 (Duration) | 6 |
| Tasks US5 (Auto-dep) | 4 |
| Tasks US6 (Developer) | 6 |
| Tasks US7 (Feature) | 7 |
| Tasks Phase 10 (Polish) | 6 |
| Oportunidades Paralelas | 33 tasks marcadas [P] |
| MVP Scope | Setup + Foundational + US1 + US2 + US3 (25 tasks) |
