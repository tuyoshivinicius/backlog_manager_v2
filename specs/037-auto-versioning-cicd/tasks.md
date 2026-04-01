# Tasks: Versionamento Automatico com Git Tags e CI/CD Gitflow

**Input**: Design documents from `/specs/037-auto-versioning-cicd/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/, quickstart.md

**Tests**: Nao solicitados na especificacao. Validacao via dry-run e testes manuais de workflow.

**Organization**: Tasks agrupadas por user story para permitir implementacao e teste independente de cada historia.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: Qual user story a task pertence (ex: US1, US2, US3)
- Caminhos exatos incluidos nas descricoes

## Path Conventions

- Workflows: `.github/workflows/`
- Configuracao: `pyproject.toml` (raiz)
- Versao: `src/backlog_manager/__init__.py`

---

## Phase 1: Setup (Infraestrutura Compartilhada)

**Purpose**: Configuracao do projeto para suportar versionamento automatico e fluxo Gitflow

- [x] T001 Adicionar python-semantic-release como dev dependency via `poetry add --group dev python-semantic-release` em `pyproject.toml`
- [x] T002 Configurar secao `[tool.semantic_release]` no `pyproject.toml` com version_toml, version_variables, branch, commit_message, tag_format, commit_parser e opcoes de parser conforme research.md
- [x] T003 Configurar secao `[tool.semantic_release.remote]` no `pyproject.toml` com type=github e token via env GH_TOKEN
- [x] T004 Configurar secao `[tool.semantic_release.publish]` no `pyproject.toml` com upload_to_vcs_release=false

**Checkpoint**: Configuracao PSR pronta — semantic-release pode ser executado localmente com `--noop`

---

## Phase 2: Foundational (Pre-requisitos Bloqueantes)

**Purpose**: Modificacoes em workflows existentes e criacao da branch develop — DEVEM ser completadas antes de qualquer user story

**CRITICAL**: Nenhuma user story pode comecar antes desta fase estar completa

- [x] T005 Modificar `.github/workflows/ci.yml`: remover bloco `push` inteiro do trigger `on` (manter apenas `pull_request` e `workflow_call`) conforme contrato ci-modifications.yml
- [x] T006 Atualizar condicao do job `quality` em `.github/workflows/ci.yml`: ajustar o `if` para funcionar sem push triggers diretos (manter workflow_call como trigger principal para quality gate)

**Checkpoint**: ci.yml modificado — novos workflows podem chamar CI via workflow_call sem duplicacao

---

## Phase 3: User Story 4 - Configuracao de Conventional Commits e Semantic Release (Priority: P2) - MVP

**Goal**: Projeto configurado com python-semantic-release para versionamento automatico baseado em Conventional Commits

**Independent Test**: Executar `semantic-release --noop version --print` localmente e verificar que o calculo de versao funciona corretamente

> Nota: Apesar de ser P2 na spec, esta story e uma dependencia tecnica para todas as stories P1. Deve ser implementada primeiro.

### Implementation for User Story 4

- [x] T007 [US4] Validar que `src/backlog_manager/__init__.py` possui `__version__` no formato correto para PSR (`__version__ = "X.Y.Z"`)
- [x] T008 [US4] Executar `semantic-release --noop version --print` para validar configuracao PSR (dry-run local)

**Checkpoint**: PSR configurado e validado — calculo de versao funciona corretamente

---

## Phase 4: User Story 1 - Fluxo Automatico Feature-to-Develop (Priority: P1)

**Goal**: Push em feature branch dispara CI e cria PR automatica para develop com auto-merge

**Independent Test**: Criar feature branch, fazer push, verificar que PR e criada automaticamente para develop com titulo adequado

### Implementation for User Story 1

- [x] T009 [US1] Criar workflow `.github/workflows/feature-ci.yml` com trigger push (branches-ignore: main, develop), concurrency group com cancel-in-progress: true, e permissions (contents: read, pull-requests: write)
- [x] T010 [US1] Adicionar job `ci` em `feature-ci.yml` que reutiliza `./.github/workflows/ci.yml` via workflow_call com secrets: inherit
- [x] T011 [US1] Adicionar job `auto-pr` em `feature-ci.yml` (needs: ci) com steps: checkout, extrair descricao da branch (remover prefixo numerico, substituir hifens por espacos), verificar PR existente via `gh pr list --head <branch> --base develop`, criar PR via `gh pr create` se nao existir
- [x] T012 [US1] Adicionar step de auto-merge em `feature-ci.yml`: habilitar auto-merge via `gh pr merge --auto --squash` na PR criada/existente

**Checkpoint**: Feature branches com CI automatico e PR auto-criada para develop

---

## Phase 5: User Story 2 - Calculo de Versao e PR Automatica para Main (Priority: P1)

**Goal**: Merge na develop calcula proxima versao e cria PR para main com versao no titulo

**Independent Test**: Mergear PR na develop e verificar que PR e criada para main com versao correta no titulo e lista de mudancas no body

### Implementation for User Story 2

- [x] T013 [US2] Criar workflow `.github/workflows/develop-merge.yml` com trigger push em develop, concurrency group com cancel-in-progress: false, e permissions (contents: read, pull-requests: write)
- [x] T014 [US2] Adicionar job `ci` em `develop-merge.yml` que reutiliza `./.github/workflows/ci.yml` via workflow_call com secrets: inherit
- [x] T015 [US2] Adicionar job `calculate-version` em `develop-merge.yml` (needs: ci) com steps: setup Python, instalar PSR via pip, executar `semantic-release --noop version --print` e capturar NEXT_VERSION; definir outputs next_version e has_bump
- [x] T016 [US2] Adicionar job `auto-pr-to-main` em `develop-merge.yml` (needs: calculate-version, condition: has_bump == true) com steps: gerar changelog dos commits desde ultima tag, verificar PR existente via `gh pr list --head develop --base main`, criar PR com titulo "release: vX.Y.Z" e body com changelog

**Checkpoint**: Merges na develop geram PR de release automatica para main

---

## Phase 6: User Story 3 - Release Automatico na Main com Tag e Publicacao (Priority: P1)

**Goal**: Merge na main atualiza versao, cria tag, dispara publicacao no PyPI e cria backmerge para develop

**Independent Test**: Mergear PR na main e verificar que arquivos de versao sao atualizados, tag e criada e workflow de publicacao e disparado

### Implementation for User Story 3

- [x] T017 [US3] Criar workflow `.github/workflows/main-release.yml` com trigger push em main, concurrency group com cancel-in-progress: false, e permissions (contents: write, pull-requests: write, actions: write)
- [x] T018 [US3] Adicionar job `ci` em `main-release.yml` que reutiliza `./.github/workflows/ci.yml` via workflow_call com secrets: inherit
- [x] T019 [US3] Adicionar job `release` em `main-release.yml` (needs: ci) com steps: checkout com fetch-depth 0, setup Python, instalar PSR via pip, configurar git user, executar `semantic-release version --push`; definir outputs version, tag e released
- [x] T020 [US3] Adicionar job `dispatch-publish` em `main-release.yml` (needs: release, condition: released == true) com step: `gh workflow run publish.yml --ref v$VERSION -f confirm=yes`
- [x] T021 [US3] Adicionar job `backmerge` em `main-release.yml` (needs: release, condition: released == true) com steps: criar PR via `gh pr create --title "chore: backmerge vX.Y.Z" --head main --base develop`, habilitar auto-merge via `gh pr merge --auto --merge`

**Checkpoint**: Releases automaticos com tag, publicacao e backmerge funcionando

---

## Phase 7: User Story 5 - Compatibilidade com Fluxo Manual Existente (Priority: P2)

**Goal**: Tags manuais continuam funcionando e workflows existentes nao quebram

**Independent Test**: Criar tag manual `vX.Y.Z` e verificar que publish.yml e disparado normalmente

### Implementation for User Story 5

- [x] T022 [US5] Verificar que `publish.yml` nao foi modificado e que triggers `push: tags: v*` e `workflow_dispatch` continuam intactos
- [x] T023 [US5] Verificar que ci.yml manteve triggers `pull_request` e `workflow_call` funcionais apos modificacao da Phase 2

**Checkpoint**: Fluxo manual de tags continua compativel com automacao

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final e documentacao

- [x] T024 [P] Validar todos os workflows YAML com linter (actionlint ou yamllint) para garantir sintaxe correta
- [x] T025 Executar dry-run completo do fluxo: verificar que PSR calcula versao corretamente com `semantic-release --noop version --print`
- [x] T026 Revisar permissoes de todos os workflows para garantir principio de menor privilegio (contents: read onde possivel, write apenas onde necessario)
- [x] T027 Validar cenarios do quickstart.md contra implementacao final

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — pode comecar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEIA todas as user stories
- **US4 (Phase 3)**: Depende de Setup (Phase 1) — BLOQUEIA US1, US2, US3 (dependencia tecnica)
- **US1 (Phase 4)**: Depende de Phase 2 e Phase 3
- **US2 (Phase 5)**: Depende de Phase 2 e Phase 3
- **US3 (Phase 6)**: Depende de Phase 2 e Phase 3
- **US5 (Phase 7)**: Depende de Phase 2 (verificacao pos-modificacao)
- **Polish (Phase 8)**: Depende de todas as user stories completas

### User Story Dependencies

- **US4 (P2 — Setup tecnico)**: Primeira a ser implementada — e pre-requisito tecnico para US1/US2/US3
- **US1 (P1 — Feature→Develop)**: Pode comecar apos Phase 2+3 — independente de US2/US3
- **US2 (P1 — Develop→Main)**: Pode comecar apos Phase 2+3 — independente de US1/US3
- **US3 (P1 — Main→Release)**: Pode comecar apos Phase 2+3 — independente de US1/US2
- **US5 (P2 — Compatibilidade)**: Verificacao — pode rodar apos Phase 2

### Within Each User Story

- Workflow structure (triggers, concurrency, permissions) antes de jobs
- Job CI antes de jobs dependentes
- Jobs com `needs` respeitam ordem sequencial

### Parallel Opportunities

- T001–T004 (Setup) sao sequenciais (mesmo arquivo pyproject.toml)
- T005–T006 (Foundational) sao sequenciais (mesmo arquivo ci.yml)
- T009–T012 (US1), T013–T016 (US2), T017–T021 (US3) podem rodar em paralelo entre si (arquivos diferentes)
- T022–T023 (US5) podem rodar em paralelo com US1/US2/US3
- T024–T027 (Polish) parcialmente paralelizaveis

---

## Parallel Example: User Stories 1, 2, 3

```bash
# Apos Phase 2 e Phase 3 completas, lancar em paralelo:

# Developer A: User Story 1 (feature-ci.yml)
Task: T009 — Criar workflow feature-ci.yml
Task: T010 — Job CI via workflow_call
Task: T011 — Job auto-pr
Task: T012 — Step auto-merge

# Developer B: User Story 2 (develop-merge.yml)
Task: T013 — Criar workflow develop-merge.yml
Task: T014 — Job CI via workflow_call
Task: T015 — Job calculate-version
Task: T016 — Job auto-pr-to-main

# Developer C: User Story 3 (main-release.yml)
Task: T017 — Criar workflow main-release.yml
Task: T018 — Job CI via workflow_call
Task: T019 — Job release
Task: T020 — Job dispatch-publish
Task: T021 — Job backmerge
```

---

## Implementation Strategy

### MVP First (US4 + US1)

1. Complete Phase 1: Setup (PSR no pyproject.toml)
2. Complete Phase 2: Foundational (ci.yml modificado)
3. Complete Phase 3: US4 (validacao PSR)
4. Complete Phase 4: US1 (feature-ci.yml)
5. **STOP and VALIDATE**: Push uma feature branch e verificar PR automatica

### Incremental Delivery

1. Setup + Foundational + US4 → PSR configurado e ci.yml ajustado
2. Add US1 → Feature branches criam PRs automaticamente (MVP!)
3. Add US2 → Develop calcula versao e cria PR para main
4. Add US3 → Main faz release com tag e publicacao
5. Add US5 → Verificacao de compatibilidade
6. Cada story adiciona valor sem quebrar as anteriores

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica
- Cada user story e independentemente completavel e testavel
- Commit apos cada task ou grupo logico
- Pare em qualquer checkpoint para validar story independentemente
- US4 (P2) foi promovida antes das P1 por ser dependencia tecnica
