# Implementation Plan: Resolucao de Issues SonarQube

**Branch**: `033-sonarqube-issues-fix` | **Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/033-sonarqube-issues-fix/spec.md`

## Summary

Resolucao de 117 issues SonarQube abertas no projeto `tuyoshivinicius_backlog_manager_v2`, organizadas por severidade (1 BLOCKER, 37 CRITICAL, 48 MAJOR, 31 MINOR). O Quality Gate esta em **ERROR** (new_reliability_rating=3, security_hotspots_reviewed=0%). As correcoes incluem: refatoracao de complexidade cognitiva, correcao de bugs potenciais (retorno constante, tasks async sem referencia, CancelledError silenciado), limpeza de codigo (blocos vazios, parametros/variaveis nao usados, codigo comentado), adequacao a convencoes (naming, type hints, literais duplicados) e otimizacoes menores (async desnecessario, dict.fromkeys).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite, aiofiles, openpyxl
**Storage**: SQLite (sem alteracoes de schema)
**Testing**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23, pytest-qt, unittest.mock
**Target Platform**: Windows (desktop), compativel Linux
**Project Type**: Desktop app (library-first, publicavel via PyPI)
**Performance Goals**: N/A (refactoring sem alteracao de comportamento)
**Constraints**: Todas as correcoes DEVEM preservar comportamento existente. Nenhum teste deve falhar.
**Scale/Scope**: 117 issues em ~40 arquivos distintos

## SonarQube Status Atual

**Quality Gate**: ERROR
- `new_reliability_rating`: ERROR (atual: 3, limite: 1)
- `new_security_rating`: OK (atual: 1)
- `new_maintainability_rating`: OK (atual: 1)
- `new_duplicated_lines_density`: OK (atual: 2.5%, limite: 3%)
- `new_security_hotspots_reviewed`: ERROR (atual: 0%, limite: 100%)

### Inventario Completo de Issues (117 total)

#### BLOCKER (1)
| Regra | Arquivo | Linha | Descricao |
|-------|---------|-------|-----------|
| S3516 | `presentation/viewmodels/story_table_model.py` | 178 | Metodo sempre retorna mesmo valor |

#### CRITICAL (37)
| Regra | Qtd | Arquivos |
|-------|-----|----------|
| S3776 (Complexidade Cognitiva) | 17 | `domain/services/allocation_service.py` (6: linhas 404/558/635/740/846/926), `application/use_cases/scheduling/calculate_schedule.py` (1: linha 50), `domain/services/scheduling_service.py` (1: linha 180), `domain/entities/story.py` (1: linha 44), `application/use_cases/excel/import_excel_use_case.py` (1: linha 57), `infrastructure/excel/excel_service.py` (1: linha 50), `application/use_cases/story/list_stories.py` (1: linha 67), `presentation/viewmodels/story_table_model.py` (1: linha 196), `application/use_cases/allocation/get_developer_availability.py` (1: linha 51), `scripts/extract_metrics.py` (2: linhas 69/299), `scripts/seed_test_backlog.py` (1: linha 516) |
| S1186 (Metodos vazios) | 19 | `tests/conftest.py` (3: linhas 237/250/253), `tests/headless_mocks.py` (12: linhas 21/24/48/51/54/73/76/79/82/85/95/116), `tests/unit/.../test_filter_proxy_model.py` (4: linhas 144/147/150/153) |
| S1192 (Literal duplicado) | 1 | `infrastructure/database/unit_of_work.py` (linha 56) |

#### MAJOR (48)
| Regra | Qtd | Arquivos |
|-------|-----|----------|
| S7502 (Task async sem ref) | 12 | `presentation/viewmodels/manual_allocation_dialog_viewmodel.py` (2: 95/145), `presentation/views/main_window.py` (4: 1003/1097/1104/1113), `presentation/views/developer_dialog.py` (3: 201/245/288), `presentation/views/feature_dialog.py` (3: 211/278/345) |
| S1244 (Float equality) | 15 | `tests/.../test_config_dialog_viewmodel.py` (5: 134/137/181/187/200), `tests/.../test_config_dialog_viewmodel_qsettings.py` (5: 76/129/140/149/159), `tests/.../test_status_bar_viewmodel_sp_breakdown.py` (2: 113/114), `tests/.../test_schedule_viewmodel.py` (1: 84), `tests/.../test_allocation_service.py` (1: 1573), `presentation/views/story_dialog.py` (1: 418 - verificar) |
| S7497 (CancelledError) | 4 | `presentation/viewmodels/allocation_viewmodel.py` (1: 155), `presentation/viewmodels/excel_viewmodel.py` (2: 187/242), `presentation/views/main_window.py` (1: 1400) |
| S108 (Bloco vazio) | 8 | `presentation/app.py` (1: 34), `presentation/views/config_panel.py` (1: 24), `presentation/views/metrics_panel.py` (1: 16), `presentation/views/warnings_panel.py` (1: 22), `infrastructure/database/sqlite_connection.py` (1: 12), `scripts/seed_test_backlog.py` (1: 39), `tests/integration/infrastructure/test_allocation_integration.py` (1: 24), `tests/integration/test_seed_backlog.py` (1: 21) |
| S1172 (Parametro nao usado) | 4 | `application/use_cases/planning/reset_planning.py` (1: 34), `scripts/seed_test_backlog.py` (1: 644), `scripts/validate_allocation_data.py` (1: 267), `tests/factories.py` (1: 19) |
| S1854 (Variavel nao usada) | 3 | `domain/services/allocation_service.py` (1: 447), `tests/.../test_excel_service.py` (1: 179), `tests/.../test_dependency_service.py` (1: 102) |
| S5890 (Type hint incorreto) | 1 | `presentation/theme/theme.py` (385) |
| S125 (Codigo comentado) | 1 | `tests/integration/.../test_schema.py` (86) |

#### MINOR (31)
| Regra | Qtd | Arquivos |
|-------|-----|----------|
| S100 (Naming camelCase) | 10 | `tests/headless_mocks.py` (10: 70/73/76/79/82/85/98/101/104 + beginGroup/endGroup/setValue) |
| S116 (Field naming) | 2 | `tests/headless_mocks.py` (2: 120/123 - IniFormat/UserScope) |
| S7503 (Async desnecessario) | 7 | `application/use_cases/scheduling/calculate_duration.py` (1: 27), `domain/services/developer_service.py` (1: 37), `domain/services/story_service.py` (2: 87/96), `tests/.../test_excel_viewmodel.py` (2: 265/386), `tests/.../test_schedule_viewmodel.py` (1: 110) |
| S1481 (Variavel local nao usada) | 9 | `tests/.../test_config_dialog_viewmodel.py` (4: 59/84/221/246), `tests/.../test_allocation_logging.py` (1: 403), `tests/.../test_scheduling_service.py` (4: 230/244/258/273) |
| S7519 (dict.fromkeys) | 3 | `domain/services/dependency_service.py` (2: 131/132), `tests/integration/test_seed_backlog.py` (1: 123) |
| S7504 (list() desnecessario) | 1 | `tests/unit/presentation/test_container.py` (285) |

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | PASS | Refactoring nao altera fluxo de dependencias entre camadas. Decomposicao de metodos ocorre dentro da mesma camada. |
| II. Domain-Driven Design | PASS | Invariantes de entidades preservadas. Refatoracao de `Story.__init__` (S3776) decompora validacoes em metodos privados, mantendo fail-fast. |
| III. Repository Pattern | PASS | Sem alteracoes em interfaces de repositorio. |
| IV. Dependency Injection | PASS | Sem alteracoes no DI Container. |
| V. SQLite como BD | PASS | Sem alteracoes de schema ou queries. |
| VI. Packaging & Distribution | PASS | Sem alteracoes em pyproject.toml ou empacotamento. |
| VII. Estrutura de Diretorios | PASS | Sem movimentacao de arquivos entre diretorios. |
| VIII. Programacao Assincrona | ATENCAO | S7503 requer remover `async` de funcoes que nao usam await. Constitui melhoria de conformidade — Domain DEVE ser sincrono. Verificar todos os call sites antes da remocao. |
| IX. Simplicidade e Legibilidade | PASS | Reducao de complexidade cognitiva, extracao de constantes e limpeza de codigo alinham diretamente com KISS/DRY. |
| X. Type Hints Obrigatorios | PASS | Correcao de S5890 (type hint incorreto) melhora conformidade. |
| XI. Docstrings em Codigo Publico | PASS | Adicao de docstrings em metodos vazios melhora conformidade. |
| XII. Organizacao de Imports | PASS | ruff check validara organizacao apos alteracoes. |
| XIII. Convencoes de Nomenclatura | PASS | S100/S116 em headless_mocks.py sao falsos positivos (overrides Qt camelCase). Serao suprimidos com comentario. |
| XIV. Estrategia de Testes | PASS | Comparacoes float corrigidas com pytest.approx(). Limpeza de variaveis nao usadas. Nenhum teste removido. |
| XV. Idioma | PASS | Sem alteracoes de idioma. |
| XVI. Tratamento de Erros | PASS | S7497 (CancelledError) melhora conformidade com propagacao correta de excecoes. |
| XVII. Logging e Observabilidade | PASS | Sem alteracoes em logging. |
| XVIII. Gestao de Configuracao | PASS | Sem alteracoes de configuracao. |
| XIX. Padroes de UI/UX | PASS | Correcoes em ViewModels/Views preservam padrao MVVM. |
| XX. Validacao e Sanitizacao | PASS | Sem alteracoes em validacao de entrada. |
| XXI. CI/CD e Qualidade Continua | PASS | Resolucao de issues SonarQube melhora conformidade com gates de qualidade. |

**Gate Result**: PASS (sem violacoes). Principio VIII requer atencao na remocao de async — verificar call sites.

## Project Structure

### Documentation (this feature)

```text
specs/033-sonarqube-issues-fix/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output (N/A - refactoring)
├── quickstart.md        # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (repository root)

```text
src/
└── backlog_manager/
    ├── domain/
    │   ├── entities/story.py                    # S3776 (CC=18)
    │   └── services/
    │       ├── allocation_service.py            # S3776 x6, S1854
    │       ├── scheduling_service.py            # S3776 (CC=20)
    │       ├── dependency_service.py            # S7519 x2
    │       ├── developer_service.py             # S7503
    │       └── story_service.py                 # S7503 x2
    ├── application/
    │   └── use_cases/
    │       ├── allocation/get_developer_availability.py  # S3776 (CC=26)
    │       ├── excel/import_excel_use_case.py            # S3776 (CC=39)
    │       ├── scheduling/
    │       │   ├── calculate_schedule.py                 # S3776 (CC=28)
    │       │   └── calculate_duration.py                 # S7503
    │       ├── story/list_stories.py                     # S3776 (CC=23)
    │       └── planning/reset_planning.py                # S1172
    ├── infrastructure/
    │   ├── database/
    │   │   ├── unit_of_work.py                  # S1192 (literal dup 4x)
    │   │   └── sqlite_connection.py             # S108
    │   └── excel/excel_service.py               # S3776 (CC=22)
    └── presentation/
        ├── app.py                               # S108
        ├── theme/theme.py                       # S5890
        ├── viewmodels/
        │   ├── story_table_model.py             # S3516 (BLOCKER), S3776
        │   ├── allocation_viewmodel.py          # S7497
        │   ├── excel_viewmodel.py               # S7497 x2
        │   └── manual_allocation_dialog_viewmodel.py  # S7502 x2
        └── views/
            ├── main_window.py                   # S7502 x4, S7497
            ├── developer_dialog.py              # S7502 x3
            ├── feature_dialog.py                # S7502 x3
            ├── story_dialog.py                  # S7502
            ├── config_panel.py                  # S108
            ├── metrics_panel.py                 # S108
            └── warnings_panel.py                # S108

scripts/
├── extract_metrics.py                           # S3776 x2 (CC=72/96)
├── seed_test_backlog.py                         # S3776, S108, S1172
└── validate_allocation_data.py                  # S1172

tests/
├── conftest.py                                  # S1186 x3
├── headless_mocks.py                            # S1186 x12, S100 x10, S116 x2
├── factories.py                                 # S1172
├── integration/
│   ├── infrastructure/
│   │   ├── test_allocation_integration.py       # S108
│   │   ├── database/test_schema.py              # S125
│   │   └── excel/test_excel_service.py          # S1854
│   └── test_seed_backlog.py                     # S108, S7519
└── unit/
    ├── domain/services/
    │   ├── test_allocation_service.py           # S1244
    │   ├── test_allocation_logging.py           # S1481
    │   ├── test_dependency_service.py           # S1854
    │   └── test_scheduling_service.py           # S1481 x4
    └── presentation/
        ├── test_container.py                    # S7504
        └── viewmodels/
            ├── test_config_dialog_viewmodel.py          # S1244 x5, S1481 x4
            ├── test_config_dialog_viewmodel_qsettings.py # S1244 x5
            ├── test_excel_viewmodel.py                  # S7503 x2
            ├── test_filter_proxy_model.py               # S1186 x4
            ├── test_schedule_viewmodel.py               # S1244, S7503
            └── test_status_bar_viewmodel_sp_breakdown.py # S1244 x2
```

**Structure Decision**: Nenhuma alteracao estrutural. Todas as correcoes ocorrem in-place nos arquivos existentes.

## Complexity Tracking

> Sem violacoes da constituicao. Tabela vazia.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |
