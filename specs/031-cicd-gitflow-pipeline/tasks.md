# Tasks: CI/CD Pipeline com GitFlow, Quality Gates e PyPI Publish

**Input**: Design documents from `/specs/031-cicd-gitflow-pipeline/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/workflow-call.md, quickstart.md

**Tests**: Nao incluidos — spec define validacao manual via PRs de teste (sem testes automatizados para workflows).

**Organization**: Tasks agrupadas por user story para permitir implementacao e validacao independente de cada story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Workflows: `.github/workflows/`
- Config files: raiz do repositorio
- Documentacao: raiz do repositorio

---

## Phase 1: Setup

**Purpose**: Preparacao do projeto — verificar pre-condicoes e ajustar configuracoes basicas

- [x] T001 Verificar e atualizar `.gitignore` para incluir `dist/`, `build/`, `*.egg-info/` (FR-023)
- [x] T002 [P] Remover workflow obsoleto `.github/workflows/tests.yml` (FR-005 — substituido por ci.yml)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Artefatos que DEVEM estar prontos antes das user stories — pyproject.toml metadata e estrutura base de workflows

**CRITICAL**: US4 (Publish) e US5 (Badges) dependem da metadata estar completa

- [x] T003 Complementar metadata do `pyproject.toml` com description, readme, license, authors, classifiers, repository, homepage e URLs (FR-022, FR-024)

**Checkpoint**: Metadata pronta — user stories podem comecar

---

## Phase 3: User Story 1 - CI automatizado em cada push/PR (Priority: P1) MVP

**Goal**: Pipeline de CI completa com lint, test (matriz Python 3.11/3.12/3.13) e quality, disparada automaticamente em push/PR

**Independent Test**: Criar PR de teste para `develop` e verificar que os jobs lint, test e quality executam corretamente no GitHub Actions

### Implementation for User Story 1

- [x] T004 [US1] Criar workflow `.github/workflows/ci.yml` com triggers push (develop, main, release/*, hotfix/*), pull_request (develop, main) e workflow_call (FR-005, FR-006, FR-011)
- [x] T005 [US1] Implementar job `lint` no `ci.yml` com steps: checkout, setup-python (3.11), install-poetry, cache Poetry, install deps, version-check (__init__.py vs pyproject.toml), ruff check, ruff format --check, mypy (FR-007, FR-012, FR-029)
- [x] T006 [US1] Implementar job `test` no `ci.yml` dependente de lint, com matrix python-version [3.11, 3.12, 3.13], fail-fast false, steps: checkout, setup-python, install-poetry, cache, install deps, xvfb, pytest (unit + integration + e2e), coverage.xml (apenas Python 3.11 >= 80%), upload coverage artifact (FR-008, FR-009)
- [x] T007 [US1] Implementar job `quality` no `ci.yml` dependente de test, com steps: checkout (fetch-depth 0), download coverage artifact, upload codecov (fail_ci_if_error false), sonarcloud scan (continue-on-error true) (FR-010, FR-014, FR-016)

**Checkpoint**: CI completo e funcional — PRs disparam lint + test + quality automaticamente

---

## Phase 4: User Story 2 - Estrutura GitFlow e documentacao de branching (Priority: P2)

**Goal**: Documentacao completa de estrategia GitFlow e guia de setup para mantenedores

**Independent Test**: Verificar que CONTRIBUTING.md e SETUP_CI.md existem com conteudo completo e instrucoes claras

### Implementation for User Story 2

- [x] T008 [P] [US2] Criar `CONTRIBUTING.md` com secoes: fluxo GitFlow (diagrama textual, descricao de branches main/develop/feature/release/hotfix), criando branches (exemplos git), pull requests (processo), versionamento semantico (bump pyproject.toml + __init__.py), release (processo de tag), migracao (notas sobre branch padrao atual e cleanup historico) (FR-001, FR-003, FR-004, FR-024)
- [x] T009 [P] [US2] Criar `SETUP_CI.md` com secoes: pre-requisitos, GitHub Secrets (CODECOV_TOKEN, SONAR_TOKEN), OIDC Trusted Publishers (PyPI/TestPyPI config), GitHub Environments (pypi, testpypi), branch protection rules (main e develop), SonarCloud setup (informacional/opcional), migracao de branches (FR-002, FR-028)

**Checkpoint**: Documentacao completa — contribuidores e mantenedores tem guias claros

---

## Phase 5: User Story 3 - Quality gates com Codecov e SonarCloud (Priority: P3)

**Goal**: Configuracao dos servicos externos Codecov e SonarCloud para feedback automatico em PRs

**Independent Test**: Abrir PR e verificar que Codecov posta comentario de cobertura e SonarCloud executa analise

### Implementation for User Story 3

- [x] T010 [P] [US3] Criar `codecov.yml` na raiz com targets 80% (projeto e patch), exclusoes (tests/, specs/, .specify/), comentarios em PRs (layout: reach, diff, flags, files) (FR-013)
- [x] T011 [P] [US3] Criar `sonar-project.properties` na raiz com organization (tuyoshivinicius), projectKey (tuyoshivinicius_backlog_manager_v2), sources (src/), tests (tests/), python.version (3.11), coverage.reportPaths (coverage.xml), exclusoes e sourceEncoding UTF-8 (FR-015)

**Checkpoint**: Quality gates configurados — PRs recebem feedback automatico de cobertura e qualidade

---

## Phase 6: User Story 4 - Publicacao automatizada no PyPI via tags (Priority: P4)

**Goal**: Workflow de publish que publica automaticamente no PyPI/TestPyPI ao criar tags semanticas, com validacao CI previa

**Independent Test**: Criar tag `v0.1.1-rc1` e verificar que workflow de publish executa, valida CI, faz build e publica no TestPyPI

### Implementation for User Story 4

- [x] T012 [US4] Criar workflow `.github/workflows/publish.yml` com triggers push tags (v*) e workflow_dispatch (input de confirmacao), job `ci` reutilizando ci.yml via workflow_call com secrets inherit (FR-017, FR-018, FR-021)
- [x] T013 [US4] Implementar job `build` no `publish.yml` dependente de ci, com steps: checkout, setup-python, install-poetry, poetry build, upload dist artifact (FR-018)
- [x] T014 [US4] Implementar job `publish-testpypi` no `publish.yml` dependente de build, condicao tags rc/beta/alpha, environment testpypi, permissions id-token write, pypa/gh-action-pypi-publish com repository-url test.pypi.org e skip-existing true (FR-019, FR-027)
- [x] T015 [US4] Implementar job `publish-pypi` no `publish.yml` dependente de build, condicao tags sem sufixo, environment pypi, permissions id-token write, pypa/gh-action-pypi-publish sem repository-url e skip-existing true (FR-019, FR-027)
- [x] T016 [US4] Implementar job `github-release` no `publish.yml` dependente de publish-pypi, permissions contents write, steps: checkout, download dist, gh release create --generate-notes com artefatos .whl e .tar.gz (FR-020)
- [x] T017 [P] [US4] Criar `.github/release.yml` com categorias: Features (enhancement, feature), Bug Fixes (bug, fix), Documentation (documentation, docs), CI/CD (ci, cd, github-actions), Dependencies (dependencies, deps) (FR-020)

**Checkpoint**: Pipeline de publish completa — tags disparam publicacao automatizada com validacao CI

---

## Phase 7: User Story 5 - Badges de status no README (Priority: P5)

**Goal**: Badges visuais no README mostrando status do CI, cobertura, qualidade, versao PyPI e licenca

**Independent Test**: Verificar que README.md contem badges com links corretos e que renderizam no GitHub

### Implementation for User Story 5

- [x] T018 [US5] Adicionar badges ao `README.md` logo abaixo do titulo: CI Status (GitHub Actions), Codecov, SonarCloud (Quality Gate, Maintainability, Reliability, Security), PyPI (versao, downloads), Python Version, License — cada badge como link clicavel para o servico correspondente (FR-025, FR-026)

**Checkpoint**: README exibe badges funcionais refletindo o estado real do projeto

---

## Phase 8: User Story 6 - Preparacao do pyproject.toml para PyPI (Priority: P6)

> **Nota**: Esta user story foi coberta pela task T003 (Phase 2 - Foundational) por ser pre-requisito de US4 e US5. Nenhuma task adicional necessaria.

**Goal**: pyproject.toml com metadata completa para pagina profissional no PyPI

**Independent Test**: Executar `poetry check` e verificar ausencia de warnings sobre metadata

**Checkpoint**: Coberto por T003

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final e verificacao de consistencia

- [x] T019 Revisar consistencia entre todos os arquivos criados — verificar que referencias cruzadas (CONTRIBUTING.md ↔ SETUP_CI.md, ci.yml ↔ publish.yml, badges ↔ servicos) estao corretas
- [x] T020 Executar validacao do quickstart.md — verificar que todos os passos documentados sao viaveis com os artefatos criados

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — pode comecar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEIA US4 e US5
- **US1 - CI (Phase 3)**: Depende de Setup — BLOQUEIA US3, US4
- **US2 - GitFlow Docs (Phase 4)**: Depende de Setup — independente das demais stories
- **US3 - Quality Gates (Phase 5)**: Depende de US1 (ci.yml precisa existir para referenciar quality jobs)
- **US4 - Publish (Phase 6)**: Depende de US1 (ci.yml para workflow_call) e Foundational (metadata pyproject.toml)
- **US5 - Badges (Phase 7)**: Depende de Foundational (metadata) — badges referenciam servicos configurados
- **US6 - PyPI Metadata (Phase 8)**: Coberta por T003 (Foundational)
- **Polish (Phase 9)**: Depende de todas as stories anteriores

### User Story Dependencies

```text
Setup (T001, T002)
  │
  ├── Foundational (T003) ──────────────────────┐
  │                                              │
  ├── US1: CI (T004→T005→T006→T007) ────────┐   │
  │                                          │   │
  ├── US2: Docs (T008 ∥ T009) [independente] │   │
  │                                          │   │
  │   US3: Quality (T010 ∥ T011) ←───────────┘   │
  │                                          │   │
  │   US4: Publish (T012→T013→T014,T015→T016 + T017) ←──┘
  │         ↑ depende de US1 + Foundational
  │
  │   US5: Badges (T018) ← depende de Foundational
  │
  └── Polish (T019→T020) ← depende de todas
```

### Within Each User Story

- CI (US1): Jobs sequenciais — lint (T005) → test (T006) → quality (T007), todos dentro de ci.yml (T004)
- Docs (US2): CONTRIBUTING.md (T008) e SETUP_CI.md (T009) sao parallelizaveis
- Quality (US3): codecov.yml (T010) e sonar-project.properties (T011) sao parallelizaveis
- Publish (US4): Jobs sequenciais no workflow, mas release.yml (T017) e parallelizavel
- Badges (US5): Task unica (T018)

### Parallel Opportunities

- T001 e T002 podem rodar em paralelo (Setup)
- T008 e T009 podem rodar em paralelo (US2 - arquivos independentes)
- T010 e T011 podem rodar em paralelo (US3 - arquivos independentes)
- T014 e T015 podem rodar em paralelo (US4 - jobs independentes no mesmo workflow)
- T017 pode rodar em paralelo com T012-T016 (US4 - arquivo separado)
- US2 pode rodar em paralelo com US1 (sem dependencias entre si)
- US3 pode rodar em paralelo com US2 (apos US1 estar pronto)

---

## Parallel Example: User Story 1

```bash
# US1 tasks are sequential (all in same file ci.yml):
Task T004: Criar estrutura base do ci.yml
Task T005: Implementar job lint (depende de T004)
Task T006: Implementar job test (depende de T005)
Task T007: Implementar job quality (depende de T006)
```

## Parallel Example: User Story 2

```bash
# US2 tasks are fully parallel (different files):
Task T008: Criar CONTRIBUTING.md
Task T009: Criar SETUP_CI.md
```

## Parallel Example: User Story 3

```bash
# US3 tasks are fully parallel (different files):
Task T010: Criar codecov.yml
Task T011: Criar sonar-project.properties
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001, T002)
2. Complete Phase 2: Foundational (T003)
3. Complete Phase 3: User Story 1 - CI (T004-T007)
4. **STOP and VALIDATE**: Criar PR de teste e verificar que lint, test e quality executam
5. CI funcional — base para todas as demais stories

### Incremental Delivery

1. Setup + Foundational → Base pronta
2. US1 (CI) → Validar com PR de teste → MVP!
3. US2 (Docs) → Validar conteudo do CONTRIBUTING.md e SETUP_CI.md
4. US3 (Quality Gates) → Validar com PR que Codecov e SonarCloud respondem
5. US4 (Publish) → Validar com tag rc no TestPyPI
6. US5 (Badges) → Validar renderizacao no GitHub
7. Polish → Revisao final de consistencia

### Parallel Team Strategy

Com multiplos desenvolvedores:

1. Todos completam Setup + Foundational
2. Apos US1 pronto:
   - Dev A: US2 (Docs) — independente
   - Dev B: US3 (Quality Gates) — depende de US1
   - Dev C: US4 (Publish) — depende de US1 + Foundational
3. US5 (Badges) pode ser feito por qualquer dev apos Foundational

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica
- Cada user story pode ser validada independentemente (exceto dependencias documentadas)
- Sem testes automatizados — validacao manual via PRs e tags de teste
- Commit apos cada task ou grupo logico
- Pare em qualquer checkpoint para validar a story independentemente
