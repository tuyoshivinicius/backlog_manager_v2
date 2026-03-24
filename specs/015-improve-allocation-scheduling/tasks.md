# Tasks: Melhoria Iterativa dos Algoritmos de Alocacao e Cronograma

**Input**: Design documents from `/specs/015-improve-allocation-scheduling/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/logging-contract.md

**Tests**: Tests included per spec.md requirements (cobertura >= 80% mandatorio - SC-006)

**Organization**: Tasks grouped by user story for independent implementation and testing.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

Based on plan.md structure (single project - Clean Architecture):
- Source: `src/backlog_manager/`
- Tests: `tests/`
- Logging: `src/backlog_manager/infrastructure/logging/`
- Domain Services: `src/backlog_manager/domain/services/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Verificar ambiente e estrutura existente

- [X] T001 Verificar infraestrutura de logging existente em src/backlog_manager/infrastructure/logging/logger_config.py
- [X] T002 [P] Verificar AllocationMetrics e AllocationConfig existentes em src/backlog_manager/domain/services/allocation_service.py
- [X] T003 [P] Verificar seed script EP-014 funcional via poetry run python scripts/seed_test_backlog.py --clean

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Garantir que logger existente esta disponivel e configurado corretamente

**⚠️ CRITICAL**: Logging infrastructure must be verified before any user story implementation

- [X] T004 Validar que get_logger() de infrastructure/logging retorna logger configurado conforme Constituicao (rotacao 10MB, 3 backups)
- [X] T005 Criar diretorio specs/015-improve-allocation-scheduling/corrections/ para documentacao de ciclos de melhoria

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Diagnostico de Problemas via Logs Estruturados (Priority: P1) 🎯 MVP

**Goal**: Usuario consegue consultar logs em %APPDATA%/BacklogManager/logs/ e encontra metricas detalhadas (AllocationMetrics) que permitem correlacionar comportamento visual com decisoes internas do algoritmo.

**Independent Test**: Executar alocacao e verificar se logs contem as 16 metricas de AllocationMetrics em formato estruturado.

**Acceptance Criteria** (from spec.md):
1. Log INFO com todas 16 metricas de AllocationMetrics ao final da execucao
2. Logs DEBUG para cada decisao de selecao de desenvolvedor com justificativa
3. Log WARNING para deteccao de deadlock com historias envolvidas

### Tests for User Story 1 ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [X] T006 [P] [US1] Criar test_allocation_logging.py em tests/unit/domain/services/ com teste para log INFO de metricas completas (FR-001)
- [X] T007 [P] [US1] Adicionar teste para log DEBUG de decisao de selecao de desenvolvedor (FR-002) em tests/unit/domain/services/test_allocation_logging.py
- [X] T008 [P] [US1] Adicionar teste para log WARNING de deteccao de deadlock (FR-003) em tests/unit/domain/services/test_allocation_logging.py
- [X] T009 [P] [US1] Adicionar teste para log WARNING de violacao de ociosidade intra-wave (FR-004) em tests/unit/domain/services/test_allocation_logging.py
- [X] T010 [P] [US1] Adicionar teste para log INFO de inicio/fim de onda (FR-005) em tests/unit/domain/services/test_allocation_logging.py

### Implementation for User Story 1

- [X] T011 [US1] Adicionar import de logger no nivel de modulo em src/backlog_manager/domain/services/allocation_service.py usando get_logger("domain.services.allocation_service")
- [X] T012 [US1] Implementar log INFO de inicio de alocacao em allocate_stories() em src/backlog_manager/domain/services/allocation_service.py
- [X] T013 [US1] Implementar log INFO de sumario de metricas ao final de allocate_stories() com todos 16 campos de AllocationMetrics em src/backlog_manager/domain/services/allocation_service.py
- [X] T014 [US1] Implementar log DEBUG de decisao de selecao de desenvolvedor em _select_developer() ou _allocate_by_wave() em src/backlog_manager/domain/services/allocation_service.py
- [X] T015 [US1] Implementar log WARNING de deteccao de deadlock em _allocate_by_wave() em src/backlog_manager/domain/services/allocation_service.py
- [X] T016 [US1] Implementar log WARNING/INFO de violacao de ociosidade em _check_idleness() em src/backlog_manager/domain/services/allocation_service.py
- [X] T017 [US1] Implementar log INFO de inicio/fim de onda em _allocate_by_wave() em src/backlog_manager/domain/services/allocation_service.py
- [X] T018 [US1] Adicionar guards logger.isEnabledFor(logging.DEBUG) em loops apertados conforme research.md em src/backlog_manager/domain/services/allocation_service.py

**Checkpoint**: User Story 1 complete - logs estruturados disponiveis para diagnostico

---

## Phase 4: User Story 2 - Reproducao de Cenarios com Dados de Teste (Priority: P2)

**Goal**: Usuario reproduz problemas identificados usando seed script EP-014 com dados deterministicos (random seed 42).

**Independent Test**: Executar seed script duas vezes com --clean e verificar banco identico.

**Acceptance Criteria** (from spec.md):
1. Seed script gera exatamente 7 devs, 7 features, ~190 historias, ~102 dependencias
2. Alocacao produz resultados identicos para mesmos dados de entrada

### Tests for User Story 2 ⚠️

- [X] T019 [P] [US2] Adicionar teste de reproducibilidade de alocacao em tests/integration/infrastructure/test_allocation_integration.py verificando que duas execucoes com mesmo seed produzem mesmo resultado

### Implementation for User Story 2

- [X] T020 [US2] Verificar que AllocationConfig.random_seed e usado corretamente em src/backlog_manager/domain/services/allocation_service.py para garantir determinismo
- [X] T021 [US2] Documentar procedimento de reproducao em quickstart.md (ja existente - verificar completude)

**Checkpoint**: User Story 2 complete - cenarios reproduziveis via seed script

---

## Phase 5: User Story 3 - Ciclo de Melhoria Iterativa Colaborativa (Priority: P2)

**Goal**: Usuario descreve problema usando protocolo de 6 etapas e Claude Code analisa logs, propoe correcao, e valida sem regressoes.

**Independent Test**: Simular ciclo completo de descricao-analise-correcao-validacao.

**Acceptance Criteria** (from spec.md):
1. Logs permitem correlacionar comportamento visual com metricas internas
2. Plano de correcao inclui arquivos, mudancas e impacto esperado
3. Suite de testes passa sem regressoes apos correcao

### Tests for User Story 3 ⚠️

- [X] T022 [P] [US3] Adicionar teste verificando que logs contem informacao suficiente para correlacionar com comportamento visual em tests/integration/infrastructure/test_allocation_integration.py

### Implementation for User Story 3

- [X] T023 [US3] Criar template de Log de Correcao em specs/015-improve-allocation-scheduling/corrections/TEMPLATE.md com campos: problema, diagnostico, mudanca, resultado
- [X] T024 [US3] Verificar que formato de descricao de problema em quickstart.md (Etapa 2) esta completo

**Checkpoint**: User Story 3 complete - protocolo de melhoria iterativa estabelecido

---

## Phase 6: User Story 4 - Validacao de Performance Apos Correcao (Priority: P3)

**Goal**: Validar que performance permanece <= 5s para 100 historias e <= 30s para 500 historias apos cada correcao.

**Independent Test**: Executar alocacao com 100 historias e medir tempo total.

**Acceptance Criteria** (from spec.md):
1. AllocationMetrics.total_time_seconds <= 5.0 para 100 historias
2. Variacao de performance documentada no log de correcao
3. Correcao revertida ou otimizada se degradar performance

### Tests for User Story 4 ⚠️

- [X] T025 [P] [US4] Adicionar teste de performance para 100 historias (SC-003: <= 5s) em tests/integration/infrastructure/test_allocation_integration.py
- [X] T026 [P] [US4] Adicionar teste de performance para 190 historias seed (SC-002: <= 5s) em tests/integration/infrastructure/test_allocation_integration.py
- [X] T027 [P] [US4] Adicionar teste de performance para 500 historias (SC-009: <= 30s) em tests/integration/infrastructure/test_allocation_integration.py

### Implementation for User Story 4

- [X] T028 [US4] Verificar que AllocationMetrics.total_time_seconds e calculado corretamente em src/backlog_manager/domain/services/allocation_service.py
- [X] T029 [US4] Adicionar secao de metricas de performance no template de Log de Correcao

**Checkpoint**: User Story 4 complete - metricas de performance validaveis

---

## Phase 7: User Story 5 - Validacao de Cobertura e Complexidade Apos Correcao (Priority: P3)

**Goal**: Validar cobertura >= 80% e complexidade ciclomatica <= 15 apos cada correcao.

**Independent Test**: Executar pytest --cov e radon cc.

**Acceptance Criteria** (from spec.md):
1. Cobertura total >= 80%
2. Complexidade ciclomatica de funcoes modificadas <= 15
3. Correcao ajustada se metricas violadas

### Tests for User Story 5 ⚠️

- [X] T030 [P] [US5] Verificar que radon esta disponivel para analise de complexidade via poetry run radon cc src/backlog_manager/ -a -s

### Implementation for User Story 5

- [X] T031 [US5] Adicionar comandos de validacao de qualidade no quickstart.md (cobertura e complexidade)
- [X] T032 [US5] Adicionar checklist de validacao de qualidade no template de Log de Correcao

**Checkpoint**: User Story 5 complete - metricas de qualidade validaveis

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final e documentacao

- [X] T033 Executar suite completa de testes via poetry run pytest tests/ -v --cov=src/backlog_manager --cov-report=term-missing
- [X] T034 [P] Verificar cobertura >= 80% (SC-006)
- [X] T035 [P] Verificar complexidade ciclomatica <= 15 em allocation_service.py via poetry run radon cc src/backlog_manager/domain/services/allocation_service.py -a -s
- [X] T036 Executar validacao de quickstart.md conforme protocolo de 6 etapas
- [X] T037 Verificar conformidade de logs com contracts/logging-contract.md usando regex patterns definidos

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - verificacao inicial
- **Foundational (Phase 2)**: Depends on Setup - prepara infraestrutura
- **User Story 1 (Phase 3)**: Depends on Foundational - BLOCKS demais user stories (MVP)
- **User Story 2 (Phase 4)**: Depends on Phase 2 - pode rodar em paralelo com US1
- **User Story 3 (Phase 5)**: Depends on US1 (logs necessarios para correlacao)
- **User Stories 4-5 (Phases 6-7)**: Depends on Phase 2 - podem rodar em paralelo
- **Polish (Phase 8)**: Depends on all user stories complete

### User Story Dependencies

```
Phase 2 (Foundational)
    ├── US1 (P1) - MVP - CRITICAL for US3
    ├── US2 (P2) - Independent
    ├── US3 (P2) - Depends on US1 logs
    ├── US4 (P3) - Independent
    └── US5 (P3) - Independent
```

### Parallel Opportunities

**Within User Story 1**:
- T006, T007, T008, T009, T010 (tests) can run in parallel
- Implementation tasks T011-T018 must be sequential (same file)

**Across User Stories** (after Foundational):
- US2, US4, US5 can run in parallel (independent)
- US3 must wait for US1 (needs logs for correlation)

---

## Parallel Example: User Story 1 Tests

```bash
# Launch all tests for User Story 1 together:
Task: "Criar test_allocation_logging.py em tests/unit/domain/services/"
Task: "Adicionar teste para log DEBUG de decisao de selecao"
Task: "Adicionar teste para log WARNING de deteccao de deadlock"
Task: "Adicionar teste para log WARNING de violacao de ociosidade"
Task: "Adicionar teste para log INFO de inicio/fim de onda"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T005)
3. Complete Phase 3: User Story 1 (T006-T018)
4. **STOP and VALIDATE**: Test US1 independently
   - Verify logs appear in %APPDATA%/BacklogManager/logs/
   - Verify all 16 metrics logged
   - Verify deadlock/idleness warnings appear when appropriate
5. Deploy/demo if ready - logging infrastructure complete!

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Complete** (logs estruturados)
3. Add User Story 2 → Test independently → Reproducibilidade garantida
4. Add User Story 3 → Test independently → Protocolo de melhoria estabelecido
5. Add User Stories 4-5 → Test independently → Validacao de qualidade completa
6. Polish → Validacao final e documentacao

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story
- Each user story should be independently completable and testable
- All logging must be in Portuguese per Constitution (Principio XV)
- Log format must match contracts/logging-contract.md
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
