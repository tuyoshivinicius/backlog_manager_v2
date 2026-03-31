# Implementation Plan: CI/CD Pipeline com GitFlow, Quality Gates e PyPI Publish

**Branch**: `031-cicd-gitflow-pipeline` | **Date**: 2026-03-31 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/031-cicd-gitflow-pipeline/spec.md`

## Summary

Implementar pipeline completo de CI/CD baseado em GitFlow com GitHub Actions, substituindo o workflow existente (`tests.yml`) por um novo `ci.yml` reutilizavel com jobs de lint, test (matriz Python 3.11/3.12/3.13) e quality (Codecov + SonarCloud). Adicionar workflow `publish.yml` para publicacao automatizada no PyPI via tags semanticas com OIDC Trusted Publishers. Criar documentacao de contribuicao (CONTRIBUTING.md), guia de setup (SETUP_CI.md), configuracoes de servicos externos (codecov.yml, sonar-project.properties, `.github/release.yml`) e badges no README.md.

## Technical Context

**Language/Version**: Python 3.11/3.12/3.13 (matriz de testes); workflows em YAML (GitHub Actions)
**Primary Dependencies**: GitHub Actions (actions/checkout@v4, actions/setup-python@v5, snok/install-poetry@v1, actions/cache@v4, codecov/codecov-action@v4, SonarSource/sonarqube-scan-action), Poetry (build/publish)
**Storage**: N/A — sem alteracoes de banco de dados
**Testing**: N/A — sem testes automatizados para workflows (validacao manual via PRs de teste)
**Target Platform**: GitHub Actions (ubuntu-latest runners)
**Project Type**: CI/CD pipeline configuration (YAML workflows + documentation)
**Performance Goals**: Pipeline CI completo em < 15 minutos (incluindo matriz 3 versoes Python)
**Constraints**: OIDC Trusted Publishers para PyPI (sem tokens de longa duracao); Codecov/SonarCloud tokens como GitHub Secrets
**Scale/Scope**: 2 workflows, 6 config files, 2 docs, 1 README update

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Aplicavel? | Status | Notas |
|-----------|-----------|--------|-------|
| I. Clean Architecture | Nao | ✅ PASS | Sem alteracoes em camadas da aplicacao |
| II. DDD | Nao | ✅ PASS | Sem alteracoes em entidades/dominio |
| III. Repository Pattern | Nao | ✅ PASS | Sem alteracoes em repositorios |
| IV. Dependency Injection | Nao | ✅ PASS | Sem alteracoes em DI |
| V. SQLite | Nao | ✅ PASS | Sem alteracoes de banco |
| VI. Packaging & Distribution | Sim | ✅ PASS | Complementar metadata do pyproject.toml; Poetry build/publish via CI; versao semantica |
| VII. Estrutura de Diretorios | Nao | ✅ PASS | Sem alteracoes na estrutura src/ |
| VIII. Async | Nao | ✅ PASS | Sem alteracoes em codigo async |
| IX. Simplicidade | Sim | ✅ PASS | Workflows devem ser simples e legiveis; reutilizacao via workflow_call |
| X. Type Hints | Nao | ✅ PASS | Sem alteracoes em codigo Python |
| XI. Docstrings | Nao | ✅ PASS | Sem alteracoes em codigo Python |
| XII. isort | Nao | ✅ PASS | Ja configurado no pre-commit |
| XIII. Nomenclatura | Nao | ✅ PASS | Sem alteracoes em codigo Python |
| XIV. Estrategia de Testes | Sim | ✅ PASS | CI enforça cobertura >= 80%; matriz Python 3.11/3.12/3.13 |
| XV. Idioma | Sim | ✅ PASS | Documentacao (CONTRIBUTING.md, SETUP_CI.md) em portugues; YAML em ingles |
| XVI. Tratamento de Erros | Nao | ✅ PASS | Sem alteracoes em codigo Python |
| XVII. Logging | Nao | ✅ PASS | Sem alteracoes em logging |
| XVIII. Configuracao | Nao | ✅ PASS | Sem alteracoes em Configuration entity |
| XIX. UI/UX | Nao | ✅ PASS | Sem alteracoes em UI |
| XX. Validacao | Nao | ✅ PASS | Sem alteracoes em validacao |
| XXI. CI/CD e Qualidade | Sim | ✅ PASS | Feature IMPLEMENTA este principio: lint (ruff, mypy), testes com cobertura, quality gates |

**Gate Result**: ✅ PASS — Nenhuma violacao. Feature alinha-se com a constituicao, especialmente com o Principio XXI (CI/CD) e VI (Packaging).

**Nota sobre desvio do Principio XXI**: A constituicao menciona `black` como formatador, mas o projeto ja migrou para `ruff format` (evidenciado no workflow existente e pre-commit). O CI usara `ruff format --check` em vez de `black --check`, mantendo consistencia com o estado atual do projeto.

## Project Structure

### Documentation (this feature)

```text
specs/031-cicd-gitflow-pipeline/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── workflow-call.md # Interface do CI reutilizavel
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
backlog_manager_v2/                          # Raiz do repositorio
├── .github/
│   ├── workflows/
│   │   ├── ci.yml                           # [NOVO] Pipeline CI (substitui tests.yml)
│   │   └── publish.yml                      # [NOVO] Pipeline de publish/release
│   └── release.yml                          # [NOVO] Config de release notes categories
├── codecov.yml                              # [NOVO] Configuracao Codecov
├── sonar-project.properties                 # [NOVO] Configuracao SonarCloud
├── CONTRIBUTING.md                          # [NOVO] Guia de contribuicao + GitFlow
├── SETUP_CI.md                              # [NOVO] Guia de setup para mantenedores
├── README.md                                # [ATUALIZAR] Adicionar badges
├── pyproject.toml                           # [ATUALIZAR] Complementar metadata
├── .gitignore                               # [VERIFICAR] dist/, build/, *.egg-info/
└── .github/workflows/tests.yml              # [REMOVER] Substituido por ci.yml
```

**Structure Decision**: Nenhuma alteracao na estrutura de codigo-fonte (`src/`, `tests/`). Todas as mudancas sao em arquivos de configuracao e documentacao na raiz do repositorio e em `.github/`.

## Complexity Tracking

> Nenhuma violacao de constituicao a justificar. Feature e puramente de configuracao CI/CD e documentacao.
