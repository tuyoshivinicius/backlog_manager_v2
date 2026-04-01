# Data Model: CI/CD Pipeline com GitFlow, Quality Gates e PyPI Publish

**Feature Branch**: `031-cicd-gitflow-pipeline`
**Date**: 2026-03-31

> Esta feature nao altera entidades de dominio, schemas de banco ou DTOs.
> O "data model" descreve os artefatos de configuracao e suas relacoes.

## Entidades (Artefatos de Configuracao)

### 1. CI Workflow (`ci.yml`)

**Localizacao**: `.github/workflows/ci.yml`
**Substitui**: `.github/workflows/tests.yml`

| Campo | Valor |
|-------|-------|
| name | CI |
| triggers | push (develop, main, release/*, hotfix/*), pull_request (develop, main), workflow_call |
| jobs | lint, test, quality |

**Job: lint**
| Campo | Valor |
|-------|-------|
| runner | ubuntu-latest |
| python | 3.11 |
| steps | checkout, setup-python, install-poetry, cache, install deps, version-check, ruff check, ruff format --check, mypy |

**Job: test**
| Campo | Valor |
|-------|-------|
| runner | ubuntu-latest |
| depends_on | lint |
| matrix | python-version: [3.11, 3.12, 3.13] |
| fail-fast | false |
| steps | checkout, setup-python, install-poetry, cache, install deps, install xvfb, unit tests, integration tests, e2e tests (xvfb), coverage (xvfb, apenas Python 3.11), upload coverage artifact |

**Job: quality**
| Campo | Valor |
|-------|-------|
| runner | ubuntu-latest |
| depends_on | test |
| steps | checkout (fetch-depth: 0), download coverage artifact, upload codecov, sonarcloud scan (continue-on-error: true) |

### 2. Publish Workflow (`publish.yml`)

**Localizacao**: `.github/workflows/publish.yml`

| Campo | Valor |
|-------|-------|
| name | Publish |
| triggers | push tags (v*), workflow_dispatch (com input de confirmacao) |
| jobs | ci (reusable), build, publish-testpypi, publish-pypi, github-release |

**Job: ci**
| Campo | Valor |
|-------|-------|
| type | workflow_call |
| uses | ./.github/workflows/ci.yml |
| secrets | inherit |

**Job: build**
| Campo | Valor |
|-------|-------|
| depends_on | ci |
| steps | checkout, setup-python, install-poetry, poetry build, upload dist artifact |

**Job: publish-testpypi**
| Campo | Valor |
|-------|-------|
| depends_on | build |
| condition | tags com sufixo rc/beta/alpha |
| environment | testpypi |
| permissions | id-token: write, contents: read |
| steps | download dist artifact, pypa/gh-action-pypi-publish (repository-url: test.pypi.org) |

**Job: publish-pypi**
| Campo | Valor |
|-------|-------|
| depends_on | build |
| condition | tags SEM sufixo rc/beta/alpha |
| environment | pypi |
| permissions | id-token: write, contents: read |
| steps | download dist artifact, pypa/gh-action-pypi-publish |

**Job: github-release**
| Campo | Valor |
|-------|-------|
| depends_on | publish-pypi |
| condition | tags SEM sufixo (release final) |
| permissions | contents: write |
| steps | checkout, download dist artifact, gh release create --generate-notes com artefatos |

### 3. Codecov Config (`codecov.yml`)

**Localizacao**: `codecov.yml` (raiz)

| Campo | Valor |
|-------|-------|
| coverage.status.project.default.target | 80% |
| coverage.status.patch.default.target | 80% |
| ignore | tests/, specs/, .specify/ |
| comment.layout | reach, diff, flags, files |
| comment.behavior | default |
| comment.require_changes | false |

### 4. SonarCloud Config (`sonar-project.properties`)

**Localizacao**: `sonar-project.properties` (raiz)

| Campo | Valor |
|-------|-------|
| sonar.organization | tuyoshivinicius |
| sonar.projectKey | tuyoshivinicius_backlog_manager_v2 |
| sonar.projectName | Backlog Manager |
| sonar.host.url | https://sonarcloud.io |
| sonar.sources | src/ |
| sonar.tests | tests/ |
| sonar.python.version | 3.11 |
| sonar.python.coverage.reportPaths | coverage.xml |
| sonar.exclusions | **/tests/**, **/migrations/**, **/__pycache__/** |
| sonar.coverage.exclusions | **/tests/**, **/conftest.py |
| sonar.sourceEncoding | UTF-8 |

### 5. Release Notes Config (`.github/release.yml`)

**Localizacao**: `.github/release.yml`

| Categoria | Labels |
|-----------|--------|
| Features | enhancement, feature |
| Bug Fixes | bug, fix |
| Documentation | documentation, docs |
| CI/CD | ci, cd, github-actions |
| Dependencies | dependencies, deps |
| Other Changes | (default — sem label) |

### 6. CONTRIBUTING.md

**Localizacao**: `CONTRIBUTING.md` (raiz)

| Secao | Conteudo |
|-------|----------|
| Fluxo GitFlow | Diagrama textual, descricao de branches (main, develop, feature/*, release/*, hotfix/*) |
| Criando Branches | Exemplos de comandos git para cada tipo |
| Pull Requests | Processo de abertura, review, merge |
| Versionamento | Processo de bump (pyproject.toml + __init__.py), semantica |
| Release | Processo de criacao de tag, publish automatizado |
| Migracao | Notas sobre migracao do branch padrao e cleanup historico |

### 7. SETUP_CI.md

**Localizacao**: `SETUP_CI.md` (raiz)

| Secao | Conteudo |
|-------|----------|
| Pre-requisitos | Conta GitHub, acesso ao repo |
| GitHub Secrets | CODECOV_TOKEN, SONAR_TOKEN — como obter e configurar |
| OIDC Trusted Publishers | Configuracao no PyPI e TestPyPI |
| GitHub Environments | Criar environments pypi e testpypi |
| Branch Protection | Rules para main e develop |
| SonarCloud Setup | Criar projeto, configurar como optional check |
| Migracao de Branches | Consolidar para main/develop |

### 8. pyproject.toml (atualizacao de metadata)

**Campos a adicionar/atualizar**:

| Campo | Valor |
|-------|-------|
| description | "Backlog Manager - Ferramenta de gestao de backlog com alocacao automatica" |
| readme | "README.md" |
| license | "MIT" |
| repository | "https://github.com/tuyoshivinicius/backlog-manager-v2" |
| homepage | "https://github.com/tuyoshivinicius/backlog-manager-v2" |
| classifiers | Development Status :: 3 - Alpha, Framework :: Qt for Python, License :: OSI Approved :: MIT License, Programming Language :: Python :: 3.11/3.12/3.13 |

### 9. README.md (badges)

**Badges a adicionar** (abaixo do titulo):

| Badge | Servico | Link |
|-------|---------|------|
| CI Status | GitHub Actions | workflow/ci.yml |
| Codecov | Codecov | codecov.io/gh/... |
| Quality Gate | SonarCloud | sonarcloud.io/... |
| Maintainability | SonarCloud | sonarcloud.io/... |
| Reliability | SonarCloud | sonarcloud.io/... |
| Security | SonarCloud | sonarcloud.io/... |
| PyPI Version | PyPI | pypi.org/project/zion-backlog-manager |
| PyPI Downloads | PyPI | pypi.org/project/zion-backlog-manager |
| Python Version | Shields.io | pypi python version |
| License | Shields.io | license badge |

## Relacoes entre Entidades

```text
publish.yml ──uses──> ci.yml (workflow_call)
ci.yml ──uploads──> coverage.xml (artifact)
ci.yml/quality ──downloads──> coverage.xml
ci.yml/quality ──sends──> Codecov (codecov.yml config)
ci.yml/quality ──sends──> SonarCloud (sonar-project.properties config)
publish.yml ──reads──> pyproject.toml (version, metadata)
publish.yml ──publishes──> PyPI / TestPyPI (OIDC)
publish.yml ──creates──> GitHub Release (.github/release.yml config)
README.md ──displays──> badges (CI, Codecov, SonarCloud, PyPI)
CONTRIBUTING.md ──references──> SETUP_CI.md
SETUP_CI.md ──references──> GitHub Secrets, Branch Protection, OIDC config
```

## Transicoes de Estado

### Tag Lifecycle (publish.yml)

```text
Tag criada (v*)
  ├─ Se rc/beta/alpha suffix → publish-testpypi
  └─ Se release final (sem suffix)
       ├─ publish-pypi
       └─ github-release (com artefatos e release notes)
```

### CI Status (ci.yml)

```text
Push/PR recebido
  → lint (ruff check, ruff format, mypy, version-check)
    → test (matriz 3.11/3.12/3.13, unit + integration + e2e)
      → quality (codecov upload, sonarcloud scan)
```
