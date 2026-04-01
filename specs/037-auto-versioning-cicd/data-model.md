# Data Model: Versionamento Automático com Git Tags e CI/CD Gitflow

**Feature**: 037-auto-versioning-cicd
**Date**: 2026-04-01

> Este feature é puramente CI/CD — não há entidades de domínio, banco de dados ou código de produção envolvido. O "data model" aqui representa as entidades conceituais do pipeline e seus estados.

## Entidades do Pipeline

### 1. Workflow

Representa um arquivo de GitHub Actions workflow.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| name | string | Nome do workflow |
| file | string | Caminho relativo (.github/workflows/) |
| triggers | list[Trigger] | Eventos que disparam o workflow |
| jobs | list[Job] | Jobs do workflow |
| concurrency | ConcurrencyGroup | Grupo de concorrência |

### 2. Trigger

Evento que dispara um workflow.

| Campo | Tipo | Valores |
|-------|------|---------|
| event | enum | `push`, `pull_request`, `workflow_call`, `workflow_dispatch` |
| branches | list[string] | Branches filtradas (quando aplicável) |
| tags | list[string] | Padrões de tag (quando aplicável) |
| inputs | dict[string, Input] | Inputs para workflow_dispatch |

### 3. SemanticVersion

Representação da versão semântica calculada pelo PSR.

| Campo | Tipo | Exemplo |
|-------|------|---------|
| major | int | 0 |
| minor | int | 2 |
| patch | int | 0 |
| prerelease | string? | "rc.1", "beta.1", null |
| tag | string | "v0.2.0" |

**Regras de Bump**:
- `fix:` / `perf:` → patch++
- `feat:` → minor++, patch=0
- `BREAKING CHANGE:` / `feat!:` → major++, minor=0, patch=0
- Sem commits convencionais → sem bump (nenhuma ação)

### 4. PullRequest (Automática)

PR criada automaticamente por um workflow.

| Campo | Tipo | Descrição |
|-------|------|-----------|
| head | string | Branch de origem |
| base | string | Branch de destino |
| title | string | Título formatado |
| body | string | Descrição com changelog |
| auto_merge | bool | Se deve auto-mergear |
| requires_review | bool | Se requer revisão manual |

**Tipos de PR Automática**:

| Tipo | head → base | Título | Auto-merge | Review |
|------|-------------|--------|------------|--------|
| Feature | feature → develop | "feat: \<desc\>" | Sim (se CI passa) | Não |
| Release | develop → main | "release: vX.Y.Z" | Não | Sim |
| Backmerge | main → develop | "chore: backmerge vX.Y.Z" | Sim | Não |

## Diagrama de Estados: Fluxo Gitflow Automatizado

```
┌─────────────┐    push     ┌──────────────┐   CI passa   ┌──────────────────┐
│ Feature      │───────────→│ feature-ci    │────────────→│ PR auto           │
│ Branch       │            │ .yml          │              │ feature→develop   │
└─────────────┘            └──────────────┘              └────────┬─────────┘
                                                                  │ auto-merge
                                                                  ▼
┌─────────────┐  merge PR   ┌──────────────┐  calcula    ┌──────────────────┐
│ develop     │←────────────│ develop-merge │  versão     │ PR auto           │
│ branch      │────────────→│ .yml          │───────────→│ develop→main      │
└─────────────┘            └──────────────┘              └────────┬─────────┘
                                                                  │ merge manual
                                                                  ▼
┌─────────────┐  merge PR   ┌──────────────┐  tag+push   ┌──────────────────┐
│ main        │←────────────│ main-release  │────────────→│ gh workflow run   │
│ branch      │             │ .yml          │              │ publish.yml       │
└─────────────┘            └──────┬───────┘              └────────┬─────────┘
                                  │                               │
                                  │ backmerge PR                  ▼
                                  │ main→develop           ┌──────────────┐
                                  └───────────────────────→│ PyPI/TestPyPI│
                                                           └──────────────┘
```

## Mapa de Workflows

### Workflows Novos

| Workflow | Trigger | Responsabilidade |
|----------|---------|-----------------|
| `feature-ci.yml` | push em branches (exceto main/develop) | CI + auto-PR para develop |
| `develop-merge.yml` | push em develop | Calcular versão + auto-PR para main |
| `main-release.yml` | push em main | Release (bump, tag, dispatch publish, backmerge) |

### Workflows Existentes (Modificados/Mantidos)

| Workflow | Modificação | Detalhes |
|----------|------------|---------|
| `ci.yml` | Remover push triggers | Manter apenas `pull_request` + `workflow_call` |
| `publish.yml` | Nenhuma | Já suporta `workflow_dispatch` + tags |

## Arquivos de Versão

| Arquivo | Campo | Formato |
|---------|-------|---------|
| `pyproject.toml` | `tool.poetry.version` | `"X.Y.Z"` |
| `src/backlog_manager/__init__.py` | `__version__` | `"X.Y.Z"` |

Ambos são atualizados atomicamente pelo `semantic-release version` antes do commit de release.

## Permissões por Workflow

| Workflow | contents | pull-requests | id-token |
|----------|----------|---------------|----------|
| `feature-ci.yml` | read | write | — |
| `develop-merge.yml` | read | write | — |
| `main-release.yml` | write | write | — |
| `ci.yml` | read | — | — |
| `publish.yml` | write/read | — | write |
