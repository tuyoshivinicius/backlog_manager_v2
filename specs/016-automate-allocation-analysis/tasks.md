# Tasks: Automacao do Ciclo de Analise de Alocacao (EP-016)

**Input**: Design documents from `/specs/016-automate-allocation-analysis/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/skill-contract.md, quickstart.md

**Tests**: Not explicitly requested in the feature specification. This EP implements a Claude Code Skill (markdown-based), not Python code - no Python tests required.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Skill file**: `.claude/commands/analyze-allocation.md`
- **Correction template**: `specs/016-automate-allocation-analysis/corrections/TEMPLATE.md`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure for the skill

- [X] T001 Create corrections directory structure at specs/016-automate-allocation-analysis/corrections/
- [X] T002 Create correction log template at specs/016-automate-allocation-analysis/corrections/TEMPLATE.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core skill file structure that MUST be complete before user story features can be added

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T003 Create skill file with frontmatter (description, allowed-tools) at .claude/commands/analyze-allocation.md
- [X] T004 Add pre-requisite verification section (poetry, dependencies) to .claude/commands/analyze-allocation.md
- [X] T005 Add argument parsing logic for --logs-only flag to .claude/commands/analyze-allocation.md
- [X] T006 Add log file location detection (Windows/Linux paths) to .claude/commands/analyze-allocation.md
- [X] T007 Add error handling pattern (halt + actionable message, no retry) to .claude/commands/analyze-allocation.md

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Execucao Automatizada do Ciclo de Analise (Priority: P1) 🎯 MVP

**Goal**: Usuario invoca `/analyze-allocation` e Claude Code automaticamente executa seed script, roda alocacao, coleta logs, analisa metricas e apresenta relatorio.

**Independent Test**: Invocar o skill e verificar que o relatorio final contem as 16 metricas de AllocationMetrics extraidas dos logs e identificacao de anomalias (se houver).

### Implementation for User Story 1

- [X] T008 [US1] Add seed script execution step (poetry run python scripts/seed_test_backlog.py --clean) to .claude/commands/analyze-allocation.md
- [X] T009 [US1] Add allocation tests execution step (poetry run pytest tests/integration/ -k allocation -v) to .claude/commands/analyze-allocation.md
- [X] T010 [US1] Add log collection step (read most recent log file) to .claude/commands/analyze-allocation.md
- [X] T011 [US1] Add metrics extraction logic for all 16 AllocationMetrics fields to .claude/commands/analyze-allocation.md
- [X] T012 [US1] Add anomaly detection logic with thresholds (deadlocks_detected>0=CRITICAL, max_idle_violations_detected>5=HIGH, max_idle_violations_detected>0=MEDIUM, skill_match_ratio<0.5=MEDIUM where skill_match_ratio=allocations_by_dependency_owner/(allocations_by_dependency_owner+allocations_by_load_balancing)) to .claude/commands/analyze-allocation.md
- [X] T013 [US1] Add structured report generation (timestamp, mode, metrics table, anomalies, recommendations) to .claude/commands/analyze-allocation.md

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Analise de Logs Existentes Sem Re-execucao (Priority: P2)

**Goal**: Usuario invoca `/analyze-allocation --logs-only` e Claude Code analisa logs existentes sem re-executar seed script ou testes.

**Independent Test**: Ter logs pre-existentes e invocar com flag `--logs-only`, verificando que relatorio e gerado sem executar seed script.

### Implementation for User Story 2

- [X] T014 [US2] Add conditional branch for --logs-only mode (skip seed/tests) to .claude/commands/analyze-allocation.md
- [X] T015 [US2] Add log existence validation with informative error message to .claude/commands/analyze-allocation.md
- [X] T016 [US2] Add most recent log file selection logic (handle log rotation) to .claude/commands/analyze-allocation.md

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Proposta Automatica de Correcao com Pre-aprovacao (Priority: P2)

**Goal**: Apos identificar anomalia, Claude Code propoe correcao com codigo especifico, lista arquivos a modificar e impacto esperado. Correcao so aplicada apos aprovacao explicita.

**Independent Test**: Identificar problema conhecido (via logs com anomalia) e verificar que proposta de correcao e formatada corretamente com codigo e impacto.

### Implementation for User Story 3

- [X] T017 [US3] Add correction proposal generation logic (problem, files, code, expected impact) to .claude/commands/analyze-allocation.md
- [X] T018 [US3] Add user approval flow (present proposal, wait for approve/reject/modify) to .claude/commands/analyze-allocation.md
- [X] T019 [US3] Add correction application step (apply code changes after approval) to .claude/commands/analyze-allocation.md
- [X] T020 [US3] Add rejection/modification handling (adjust or abandon) to .claude/commands/analyze-allocation.md

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently

---

## Phase 6: User Story 4 - Validacao Pos-Correcao Automatizada (Priority: P3)

**Goal**: Apos aplicar correcao, Claude Code executa suite de testes, verifica cobertura >= 80%, CC <= 15, e re-executa alocacao para comparar metricas antes/depois.

**Independent Test**: Aplicar correcao mock e verificar que suite de testes e executada e metricas comparadas.

### Implementation for User Story 4

- [X] T021 [US4] Add test suite execution step (poetry run pytest tests/ -v --cov=src/backlog_manager) to .claude/commands/analyze-allocation.md
- [X] T022 [US4] Add coverage verification step (>= 80%) with alert on failure to .claude/commands/analyze-allocation.md
- [X] T023 [US4] Add cyclomatic complexity check step (poetry run radon cc src/ -a -nc, verify no function exceeds CC=15 per constitution XXI) to .claude/commands/analyze-allocation.md
- [X] T024 [US4] Add metrics re-collection step (re-run seed + tests) to .claude/commands/analyze-allocation.md
- [X] T025 [US4] Add before/after metrics comparison table generation to .claude/commands/analyze-allocation.md
- [X] T026 [US4] Add rollback suggestion logic when validation fails to .claude/commands/analyze-allocation.md

**Checkpoint**: At this point, User Stories 1-4 should all work independently

---

## Phase 7: User Story 5 - Documentacao Automatica de Correcao (Priority: P3)

**Goal**: Ao concluir ciclo de correcao validado, Claude Code automaticamente preenche template de Log de Correcao com todos os dados coletados.

**Independent Test**: Completar ciclo de correcao e verificar que arquivo corrections/CORRECAO-{timestamp}.md e criado com campos preenchidos.

### Implementation for User Story 5

- [X] T027 [US5] Add correction log file creation step (CORRECAO-{timestamp}.md) to .claude/commands/analyze-allocation.md
- [X] T028 [US5] Add template field population logic (problem, diagnosis, change, result) to .claude/commands/analyze-allocation.md
- [X] T029 [US5] Add metrics before/after table with deltas to correction log to .claude/commands/analyze-allocation.md
- [X] T030 [US5] Add validation status (tests, coverage, CC) to correction log to .claude/commands/analyze-allocation.md

**Checkpoint**: All user stories should now be independently functional

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Final validation and improvements

- [X] T031 [P] Add correlation table reference (behavior-to-metric mapping from quickstart) to .claude/commands/analyze-allocation.md
- [X] T032 [P] Add troubleshooting guidance section (seed fails, logs missing, tests fail) to .claude/commands/analyze-allocation.md
- [X] T033 Run quickstart.md validation (full cycle test)
- [X] T034 Verify skill handles all edge cases from spec.md (corrupted logs, cancelled cycle, multiple anomalies)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can proceed sequentially in priority order (P1 → P2 → P3)
- **Polish (Phase 8)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after US1 - Shares log reading infrastructure from US1
- **User Story 3 (P2)**: Can start after US1 - Builds on anomaly detection from US1
- **User Story 4 (P3)**: Can start after US3 - Depends on correction application from US3
- **User Story 5 (P3)**: Can start after US4 - Depends on validation results from US4

### Within Each User Story

- Each task builds sequentially on previous tasks (same file being edited)
- Story complete before moving to next priority

### Parallel Opportunities

- T001 and T002 can run in parallel (different directories)
- T031 and T032 can run in parallel (different sections of same file)
- Note: Most tasks modify the same skill file, limiting parallel execution within phases

---

## Parallel Example: Phase 1 Setup

```bash
# Launch both setup tasks together:
Task: "Create corrections directory at specs/016-automate-allocation-analysis/corrections/"
Task: "Create correction template at specs/016-automate-allocation-analysis/corrections/TEMPLATE.md"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (corrections directory + template)
2. Complete Phase 2: Foundational (skill file with prereqs + args + error handling)
3. Complete Phase 3: User Story 1 (full execution cycle + metrics + report)
4. **STOP and VALIDATE**: Test `/analyze-allocation` produces report with all 16 metrics
5. Deploy/demo if ready

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test full cycle → Deploy (MVP!)
3. Add User Story 2 → Test --logs-only mode
4. Add User Story 3 → Test correction proposals
5. Add User Story 4 → Test validation flow
6. Add User Story 5 → Test documentation generation
7. Each story adds value without breaking previous stories

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- This EP implements a Claude Code Skill (markdown file), not Python code
- All tasks modify the same skill file (.claude/commands/analyze-allocation.md) except setup tasks
- Skill follows pattern of existing speckit.* skills in the project
- No Python tests required - skill is tested by invocation
- Commit after each phase or logical group
- Stop at any checkpoint to validate story independently
