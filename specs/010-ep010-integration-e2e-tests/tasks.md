# Tasks: EP-010 Testes de Integracao E2E

**Input**: Design documents from `/specs/010-ep010-integration-e2e-tests/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Este epico E SOBRE testes, portanto todos os tasks sao de implementacao de testes E2E.

**Organization**: Tasks agrupadas por user story para permitir implementacao e teste independente de cada story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: Qual user story este task pertence (US1, US2, etc.)
- Caminhos exatos incluidos nas descricoes

## Path Conventions

- **Testes**: `tests/e2e/` para testes E2E
- **Source**: `src/backlog_manager/` (codigo sendo testado)
- **CI/CD**: `.github/workflows/`

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Inicializacao do projeto de testes E2E e estrutura basica

- [x] T001 Create tests/e2e/ directory structure with __init__.py
- [x] T002 Configure pytest markers (e2e, perf, slow) in pyproject.toml
- [x] T003 [P] Add pytest-qt ^4.4 and qasync ^0.27.1 to dev dependencies in pyproject.toml

---

## Phase 2: Foundational (Prerequisitos Bloqueantes)

**Purpose**: Fixtures e factories que DEVEM estar completos antes de qualquer user story

**⚠️ CRITICAL**: Nenhum teste E2E pode ser escrito ate esta fase estar completa

- [x] T004 Create qasync_loop fixture in tests/e2e/conftest.py
- [x] T005 Create e2e_app fixture (QApplication + DIContainer) in tests/e2e/conftest.py
- [x] T006 Create e2e_main_window fixture in tests/e2e/conftest.py
- [x] T007 Create e2e_populated_db fixture in tests/e2e/conftest.py
- [x] T008 [P] Create create_stories factory function in tests/e2e/factories.py
- [x] T009 [P] Create create_developers factory function in tests/e2e/factories.py
- [x] T010 [P] Create create_features factory function in tests/e2e/factories.py
- [x] T011 [P] Create create_cyclic_graph factory function in tests/e2e/factories.py
- [x] T012 Validate fixtures work by running empty test file tests/e2e/test_smoke.py
- [x] T012a Configure pytest timeout=30 for E2E tests in pyproject.toml (FR-100)
- [x] T012b Add fixture teardown for Qt state cleanup in tests/e2e/conftest.py (FR-101, FR-102)
- [x] T012c Document test isolation strategy in tests/e2e/conftest.py docstring (FR-103)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Validar Suite Completa de Testes E2E (Priority: P1) 🎯 MVP

**Goal**: Suite de testes E2E que valida todas as funcionalidades do sistema de ponta a ponta

**Independent Test**: Executar `pytest tests/e2e/ -v` e verificar que todos os testes passam

### Implementation for User Story 1

- [x] T013 [P] [US1] Create test_uc001_criar_priorizar_backlog.py with test_criar_historia_com_sucesso (FR-030) in tests/e2e/
- [x] T014 [P] [US1] Add test_uc001_rejeitar_sp_invalido (FR-031) in tests/e2e/test_uc001_criar_priorizar_backlog.py
- [x] T015 [P] [US1] Add test_uc001_alterar_prioridade (FR-032) in tests/e2e/test_uc001_criar_priorizar_backlog.py
- [x] T016 [P] [US1] Create test_uc002_alocacao_automatica.py with test_alocar_com_dependencias (FR-033) in tests/e2e/
- [x] T017 [P] [US1] Add test_uc002_excluir_feriados (FR-034) in tests/e2e/test_uc002_alocacao_automatica.py
- [x] T018 [P] [US1] Add test_uc002_balancear_carga (FR-035) in tests/e2e/test_uc002_alocacao_automatica.py
- [x] T019 [P] [US1] Create test_uc003_detectar_resolver_deadlock.py with test_detectar_ciclo_direto (FR-036) in tests/e2e/
- [x] T020 [P] [US1] Add test_uc003_detectar_ciclo_indireto (FR-037) in tests/e2e/test_uc003_detectar_resolver_deadlock.py
- [x] T021 [P] [US1] Create test_uc004_importar_excel.py with test_importar_arquivo_valido (FR-038) in tests/e2e/
- [x] T022 [P] [US1] Add test_uc004_rejeitar_ciclo_import (FR-039) in tests/e2e/test_uc004_importar_excel.py
- [x] T023 [P] [US1] Create test_uc005_gerenciar_ondas.py with test_processar_ondas_em_ordem (FR-040) in tests/e2e/

**Checkpoint**: UC-001 a UC-005 have E2E tests validating main flows

---

## Phase 4: User Story 2 - Executar Testes E2E via GUI com pytest-qt (Priority: P1)

**Goal**: Testes E2E executam fluxos completos via interface grafica usando pytest-qt

**Independent Test**: Executar `pytest tests/e2e/test_uc001_criar_priorizar_backlog.py` e verificar que acoes de GUI disparam fluxos corretos

### Implementation for User Story 2

- [ ] T024 [US2] Enhance test_uc001_criar_historia to use qtbot.mouseClick for button interactions in tests/e2e/test_uc001_criar_priorizar_backlog.py
- [ ] T025 [US2] Add qtbot.waitSignal usage for async operations in tests/e2e/test_uc001_criar_priorizar_backlog.py
- [ ] T026 [US2] Implement modal dialog handling with QTimer.singleShot pattern in tests/e2e/conftest.py
- [ ] T027 [US2] Add qtbot.waitUntil for UI condition checks across test files in tests/e2e/
- [ ] T028 [US2] Verify no time.sleep() usage in any E2E test file (grep validation)

**Checkpoint**: All E2E tests use proper pytest-qt patterns without time.sleep()

---

## Phase 5: User Story 3 - Validar Cenarios de Teste CT-001 a CT-005 (Priority: P1)

**Goal**: Cenarios de teste do SRS implementados como testes automatizados

**Independent Test**: Cada CT pode ser executado independentemente via `pytest tests/e2e/test_ct00X_*.py`

### Implementation for User Story 3

- [x] T029 [P] [US3] Create test_ct001_backlog_completo.py with 20 stories, 5 devs setup in tests/e2e/
- [x] T030 [P] [US3] Add test_ct001_tempo_menor_5s assertion in tests/e2e/test_ct001_backlog_completo.py
- [x] T031 [P] [US3] Add test_ct001_todas_alocadas assertion in tests/e2e/test_ct001_backlog_completo.py
- [x] T032 [P] [US3] Add test_ct001_distribuicao_balanceada assertion in tests/e2e/test_ct001_backlog_completo.py
- [x] T033 [P] [US3] Create test_ct002_ciclo_grafo_grande.py with 50-node graph in tests/e2e/
- [x] T034 [P] [US3] Add test_ct002_cyclic_exception_em_100ms in tests/e2e/test_ct002_ciclo_grafo_grande.py
- [x] T035 [P] [US3] Create test_ct003_deadlock_devs.py with 1 dev, 2 concurrent stories in tests/e2e/
- [x] T036 [P] [US3] Add test_ct003_ajuste_data_sem_crash in tests/e2e/test_ct003_deadlock_devs.py
- [x] T037 [P] [US3] Create test_ct004_feriados_sequencia.py with Sexta-Santa 03/04/2026 in tests/e2e/
- [x] T038 [P] [US3] Add test_ct004_pula_feriado_corretamente in tests/e2e/test_ct004_feriados_sequencia.py
- [x] T039 [P] [US3] Create test_ct005_balanceamento.py with 2 devs, unequal SPs in tests/e2e/
- [x] T040 [P] [US3] Add test_ct005_distribuicao_por_contagem in tests/e2e/test_ct005_balanceamento.py

**Checkpoint**: All CT-001 to CT-005 scenarios are implemented and pass

---

## Phase 6: User Story 4 - Validar Testes de Performance RNF-PERF (Priority: P2)

**Goal**: Testes que validam requisitos de performance RNF-PERF-001 e RNF-PERF-002

**Independent Test**: Executar `pytest tests/e2e/test_performance.py -v`

### Implementation for User Story 4

- [x] T041 [P] [US4] Create test_performance.py with @pytest.mark.perf marker in tests/e2e/
- [x] T042 [US4] Implement test_perf_alocacao_100_historias_5s with time.perf_counter() in tests/e2e/test_performance.py
- [x] T043 [US4] Implement test_perf_crud_latencia_100ms in tests/e2e/test_performance.py
- [x] T044 [US4] Add performance metric reporting on failure (elapsed time, memory) in tests/e2e/test_performance.py

**Checkpoint**: Performance tests validate RNF-PERF-001 (<=5s) and RNF-PERF-002 (<=100ms)

---

## Phase 7: User Story 5 - Garantir Roundtrip Excel Completo (Priority: P2)

**Goal**: Teste de roundtrip Excel (export -> limpar -> import) valida integridade total dos dados

**Independent Test**: Executar `pytest tests/e2e/test_excel_roundtrip.py`

### Implementation for User Story 5

- [x] T045 [P] [US5] Create test_excel_roundtrip.py in tests/e2e/
- [x] T046 [US5] Implement test_excel_roundtrip_completo with export/clear/reimport flow in tests/e2e/test_excel_roundtrip.py
- [x] T047 [US5] Add assertions for 100% data equality after roundtrip in tests/e2e/test_excel_roundtrip.py
- [x] T048 [US5] Add dependency graph comparison pre/post roundtrip in tests/e2e/test_excel_roundtrip.py

**Checkpoint**: Excel roundtrip preserves 100% of data including dependencies

---

## Phase 8: User Story 6 - Configurar CI/CD com Testes E2E (Priority: P2)

**Goal**: Configuracao CI/CD que executa testes E2E com display virtual

**Independent Test**: Push de PR e verificacao do workflow GitHub Actions

### Implementation for User Story 6

- [x] T049 [P] [US6] Create .github/workflows/tests.yml with Python 3.11 setup
- [x] T050 [US6] Add Poetry installation and caching in .github/workflows/tests.yml
- [x] T051 [US6] Add xvfb installation and Qt dependencies in .github/workflows/tests.yml
- [x] T052 [US6] Configure xvfb-run with pytest --cov --cov-fail-under=80 in .github/workflows/tests.yml
- [ ] T053 [US6] Add retry mechanism for flaky tests (pytest-rerunfailures) in .github/workflows/tests.yml
- [x] T054 [US6] Configure workflow to run on push and pull_request to main branches

**Checkpoint**: CI/CD workflow runs E2E tests with xvfb and enforces 80% coverage

---

## Phase 9: User Story 7 - Corrigir Bugs Revelados pelos Testes (Priority: P1)

**Goal**: Bugs revelados pelos testes E2E corrigidos conforme politica de criticidade

**Independent Test**: Cada bug corrigido tem teste correspondente que passa apos correcao

### Implementation for User Story 7

- [ ] T055 [US7] Run full E2E test suite and document any failing tests in tests/e2e/
- [ ] T056 [US7] Fix simple bugs inline (commit: fix: [description]) as they are found
- [ ] T057 [US7] Add TODO comments for medium criticality bugs found during testing
- [ ] T058 [US7] Create GitHub issues for critical bugs with root cause analysis template
- [ ] T059 [US7] Verify all E2E tests pass after bug fixes

**Checkpoint**: All revealed bugs are fixed or documented per criticality policy

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias que afetam multiplas user stories

- [ ] T060 [P] Configure coverage reporting per module in pyproject.toml (domain 100%, application 100%, infrastructure 80%, views 50%)
- [ ] T061 [P] Add timeout=30 configuration for E2E tests in pyproject.toml
- [ ] T062 Validate total coverage >= 80% with pytest --cov=src/backlog_manager --cov-fail-under=80
- [ ] T063 [P] Add screenshot_on_failure debug fixture in tests/e2e/conftest.py (optional)
- [ ] T064 Run quickstart.md validation steps to ensure documentation is accurate
- [ ] T065 Final validation: run pytest tests/e2e/ -v and confirm all tests pass in < 5 minutes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-9)**: All depend on Foundational phase completion
  - US1 (Phase 3) and US2 (Phase 4) and US3 (Phase 5) are all P1 - can proceed in parallel
  - US4 (Phase 6), US5 (Phase 7), US6 (Phase 8) are P2 - can proceed after P1 or in parallel
  - US7 (Phase 9) should run after initial tests are written to find bugs
- **Polish (Phase 10)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - Creates base UC tests
- **User Story 2 (P1)**: Can start after Foundational - Enhances US1 tests with proper pytest-qt patterns
- **User Story 3 (P1)**: Can start after Foundational - Creates CT scenario tests (independent of US1/US2)
- **User Story 4 (P2)**: Can start after Foundational - Performance tests (independent)
- **User Story 5 (P2)**: Can start after Foundational - Excel roundtrip (independent)
- **User Story 6 (P2)**: Can start after Foundational - CI/CD config (independent of test implementation)
- **User Story 7 (P1)**: Should run after US1-US3 to find and fix bugs revealed by tests

### Parallel Opportunities

**Within Phase 2 (Foundational)**:
```bash
# Parallel - Factory functions (T008-T011):
Task: "Create create_stories factory function in tests/e2e/factories.py"
Task: "Create create_developers factory function in tests/e2e/factories.py"
Task: "Create create_features factory function in tests/e2e/factories.py"
Task: "Create create_cyclic_graph factory function in tests/e2e/factories.py"
```

**Within Phase 3 (US1 - UC Tests)**:
```bash
# Parallel - All UC test files can be created simultaneously:
Task: "Create test_uc001_criar_priorizar_backlog.py in tests/e2e/"
Task: "Create test_uc002_alocacao_automatica.py in tests/e2e/"
Task: "Create test_uc003_detectar_resolver_deadlock.py in tests/e2e/"
Task: "Create test_uc004_importar_excel.py in tests/e2e/"
Task: "Create test_uc005_gerenciar_ondas.py in tests/e2e/"
```

**Within Phase 5 (US3 - CT Tests)**:
```bash
# Parallel - All CT test files can be created simultaneously:
Task: "Create test_ct001_backlog_completo.py in tests/e2e/"
Task: "Create test_ct002_ciclo_grafo_grande.py in tests/e2e/"
Task: "Create test_ct003_deadlock_devs.py in tests/e2e/"
Task: "Create test_ct004_feriados_sequencia.py in tests/e2e/"
Task: "Create test_ct005_balanceamento.py in tests/e2e/"
```

**Across User Stories (after Foundational)**:
```bash
# Different team members can work on different stories in parallel:
Developer A: User Story 1 (UC tests)
Developer B: User Story 3 (CT tests)
Developer C: User Story 6 (CI/CD)
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2 + 3)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (UC-001 to UC-005 basic tests)
4. Complete Phase 4: User Story 2 (Enhance with proper pytest-qt patterns)
5. Complete Phase 5: User Story 3 (CT-001 to CT-005 scenario tests)
6. **STOP and VALIDATE**: Run `pytest tests/e2e/ -v` - all should pass
7. Run Phase 9: User Story 7 (Fix any bugs found)

### Incremental Delivery

1. Setup + Foundational → Test infrastructure ready
2. Add US1 (UC tests) → Basic E2E coverage
3. Add US2 (pytest-qt patterns) → Stable, non-flakey tests
4. Add US3 (CT scenarios) → SRS scenarios validated
5. Add US4 (Performance) → RNF-PERF validated
6. Add US5 (Excel roundtrip) → Data integrity validated
7. Add US6 (CI/CD) → Automated validation on every PR
8. US7 (Bug fixes) → All issues resolved
9. Polish → Coverage >= 80%, all documentation accurate

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 68 |
| **Phase 1 (Setup)** | 3 tasks |
| **Phase 2 (Foundational)** | 12 tasks |
| **Phase 3 (US1 - UC Tests)** | 11 tasks |
| **Phase 4 (US2 - pytest-qt)** | 5 tasks |
| **Phase 5 (US3 - CT Tests)** | 12 tasks |
| **Phase 6 (US4 - Performance)** | 4 tasks |
| **Phase 7 (US5 - Excel)** | 4 tasks |
| **Phase 8 (US6 - CI/CD)** | 6 tasks |
| **Phase 9 (US7 - Bug Fixes)** | 5 tasks |
| **Phase 10 (Polish)** | 6 tasks |
| **Parallel Opportunities** | 35 tasks marked [P] |
| **MVP Scope** | Phases 1-5 + Phase 9 (US1, US2, US3, US7) |

### Independent Test Criteria per Story

| Story | Independent Test Command | Success Criteria |
|-------|-------------------------|------------------|
| US1 | `pytest tests/e2e/test_uc*.py -v` | All UC tests pass |
| US2 | `grep -r "time.sleep" tests/e2e/` | No matches found |
| US3 | `pytest tests/e2e/test_ct*.py -v` | All CT tests pass |
| US4 | `pytest tests/e2e/test_performance.py -v` | Metrics within limits |
| US5 | `pytest tests/e2e/test_excel_roundtrip.py -v` | 100% data preserved |
| US6 | Push PR and check GitHub Actions | Workflow passes |
| US7 | `pytest tests/e2e/ -v` | All tests pass after fixes |

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- **Constitution XIV compliance**: No time.sleep() in E2E tests
- **Performance target**: Full E2E suite < 5 minutes
- **Coverage target**: >= 80% overall
