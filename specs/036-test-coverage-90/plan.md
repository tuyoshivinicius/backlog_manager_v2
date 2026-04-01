# Implementation Plan: Cobertura de Testes 90% e Quality Gate SonarQube

**Branch**: `036-test-coverage-90` | **Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/036-test-coverage-90/spec.md`

## Summary

Alinhar as exclusões de cobertura do SonarQube com as do pytest-cov para eliminar a divergência entre métricas locais (~94%) e SonarQube (56.7%), e adicionar testes unitários para os 16 arquivos prioritários com cobertura abaixo de 90%, garantindo que o Quality Gate passe com status OK.

## Technical Context

**Language/Version**: Python 3.11+ (runtime), Python 3.13 (SonarQube analysis)
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite, aiofiles, openpyxl, pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23
**Storage**: N/A — sem alterações de schema SQLite
**Testing**: pytest + pytest-cov (cobertura), pytest-asyncio (async), unittest.mock (stdlib)
**Target Platform**: Windows (primário), Linux (CI)
**Project Type**: Desktop app (PySide6) com library-first packaging
**Performance Goals**: N/A — feature de configuração e testes
**Constraints**: Testes headless (sem display/servidor X); zero alteração em código de produção exceto ajustes mínimos de testabilidade
**Scale/Scope**: ~16 arquivos prioritários, ~139 linhas de código testável a cobrir, 1 arquivo de configuração SonarQube

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ OK | Testes seguem a estrutura de camadas; sem alterações em dependências entre camadas |
| II. DDD | ✅ OK | Sem alterações em entidades ou lógica de domínio |
| III. Repository Pattern | ✅ OK | Testes usam mocks de repositórios existentes |
| IV. Dependency Injection | ✅ OK | Testes usam DIContainer existente via fixtures |
| V. SQLite | ✅ OK | Sem alterações de schema |
| VI. Packaging | ✅ OK | Sem alterações em pyproject.toml exceto configuração de cobertura |
| VII. Estrutura de Diretórios | ✅ OK | Novos testes em tests/unit/ e tests/integration/ conforme padrão |
| VIII. Async | ✅ OK | Testes async usam pytest-asyncio conforme padrão |
| IX. Simplicidade | ✅ OK | Testes diretos, sem abstrações desnecessárias |
| X. Type Hints | ✅ OK | Testes seguem type hints existentes |
| XI. Docstrings | ✅ OK | Testes usam docstrings descritivas quando necessário |
| XII. isort | ✅ OK | Imports organizados com isort |
| XIII. Nomenclatura | ✅ OK | snake_case para funções/variáveis, PascalCase para classes |
| XIV. Estratégia de Testes | ✅ OK | Meta de 90% alinhada com constituição (80%+ mínimo, 100% para core) |
| XV. Idioma | ✅ OK | Código em inglês, documentação em português |
| XVI. Tratamento de Erros | ✅ OK | Testes validam exceções existentes |
| XVII. Logging | ✅ OK | Sem alterações em logging |
| XVIII. Gestão de Configuração | ✅ OK | Sem alterações na entidade Configuration |
| XIX. Padrões UI/UX | ✅ OK | Sem alterações em views; viewmodel tests usam mocks headless |
| XX. Validação | ✅ OK | Sem alterações em validação |
| XXI. CI/CD | ✅ OK | Configuração SonarQube alinhada com pytest-cov; CI continua funcionando |

**Resultado**: ✅ Todos os gates passam. Nenhuma violação identificada.

## Project Structure

### Documentation (this feature)

```text
specs/036-test-coverage-90/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
└── quickstart.md        # Phase 1 output
```

### Source Code (repository root)

```text
# Arquivos de configuração modificados
sonar-project.properties          # Alinhar sonar.coverage.exclusions

# Novos testes (tests/unit/)
tests/unit/application/
├── test_edit_story.py             # Expandir cobertura (44.4% → 90%+)
├── test_list_stories_sort.py      # Expandir cobertura (69.4% → 90%+)
├── test_import_excel_use_case.py  # Expandir cobertura (89% → 90%+)
├── test_execute_allocation.py     # Expandir cobertura (87% → 90%+)
├── test_calculate_schedule.py     # Expandir cobertura (89.5% → 90%+)
└── test_get_developer_availability.py  # Expandir cobertura (89.5% → 90%+)

tests/unit/domain/
└── test_allocation_service.py     # Expandir cobertura (84.9% → 90%+)

tests/unit/infrastructure/
├── test_log_format.py             # Expandir cobertura (74.1% → 90%+)
└── test_directory_creation.py     # Expandir cobertura (65.6% → 90%+)

tests/unit/presentation/
├── test_main_window_viewmodel.py  # Expandir cobertura (83.2% → 90%+)
├── test_story_table_model.py      # Expandir cobertura (82.2% → 90%+)
├── test_filter_proxy_model.py     # Expandir cobertura (84.6% → 90%+)
├── test_manual_allocation_dialog_viewmodel.py  # Expandir (85.3% → 90%+)
├── test_excel_viewmodel.py        # Expandir cobertura (27.6% → 90%+)
├── test_schedule_viewmodel.py     # Expandir cobertura (37.7% → 90%+)
└── test_dependency_dialog_viewmodel.py  # Expandir cobertura (46.9% → 90%+)

# DTO
tests/unit/application/
└── test_edit_story_dto.py         # Novo ou expandir (69.8% → 90%+)

# Tema
tests/unit/presentation/
└── test_theme.py                  # Novo (89.3% → 90%+)
```

**Structure Decision**: Testes adicionais seguem a estrutura existente em `tests/unit/` e `tests/integration/`, espelhando a organização de camadas do código fonte. Nenhum novo diretório necessário.

## Complexity Tracking

> Nenhuma violação de constituição identificada. Tabela não aplicável.
