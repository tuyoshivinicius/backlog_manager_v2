# Implementation Plan: EP-007 Motor de Alocacao

**Branch**: `007-ep007-allocation-engine` | **Date**: 2026-03-02 | **Spec**: `specs/007-ep007-allocation-engine/spec.md`
**Input**: Feature specification from `/specs/007-ep007-allocation-engine/spec.md`

## Summary

Implementacao do AllocationService como domain service para alocacao automatica de desenvolvedores com:
- Balanceamento de carga por contagem de historias
- Processamento sequencial por ondas (wave 0, 1, 2...)
- Deteccao e resolucao de conflitos de periodo
- Deteccao de deadlocks com emissao de warnings
- Monitoramento de ociosidade
- Loop de estabilizacao pos-alocacao

## Technical Context

**Language/Version**: Python 3.11 + pydantic ^2.0, aiosqlite ^0.19.0, aiofiles ^23.0
**Primary Dependencies**: pydantic (DTOs), aiosqlite (async SQLite), existing SchedulingService, DependencyService
**Storage**: SQLite via aiosqlite (tabela Story ja existente com campos developer_id, start_date, end_date, feature_id)
**Testing**: pytest, pytest-cov, pytest-asyncio
**Target Platform**: Desktop application (Windows/Linux)
**Project Type**: library (Python package via Poetry)
**Performance Goals**: Alocacao de 100 historias com 10 devs em < 5 segundos (RNF-PERF-001)
**Constraints**: Backlog maximo recomendado de 500 historias (warning para > 500)
**Scale/Scope**: Backlogs de 20-500 historias, 1-20 desenvolvedores

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | PASS | AllocationService no dominio (sincrono), ExecuteAllocationUseCase na aplicacao (async) |
| II. DDD | PASS | AllocationService como domain service stateless, AllocationMetrics como dataclass |
| III. Repository Pattern | PASS | Use case busca dados via UnitOfWork, servico recebe dados como parametros |
| IV. Dependency Injection | PASS | Use case recebe UnitOfWork via construtor |
| V. SQLite | PASS | Persistencia de historias alocadas via StoryRepository.update() |
| VI. Packaging | PASS | Codigo em src/backlog_manager/, seguindo estrutura existente |
| VII. Estrutura de Diretorios | PASS | allocation_service.py em domain/services/, use case em application/use_cases/allocation/ |
| VIII. Programacao Assincrona | PASS | Dominio sincrono, application async |
| IX. Simplicidade | PASS | Algoritmo baseado em especificacao clara com constantes nomeadas |
| X. Type Hints | PASS | Todos os metodos com type hints completos |
| XI. Docstrings | PASS | Docstrings Google style em codigo publico |
| XII. isort | PASS | Imports organizados |
| XIII. Nomenclatura | PASS | Classes PascalCase, metodos snake_case, constantes UPPER_SNAKE_CASE |
| XIV. Estrategia de Testes | PASS | 100% cobertura em domain/services/allocation_service.py |
| XV. Idioma | PASS | Codigo em ingles, docstrings em portugues |
| XVI. Tratamento de Erros | PASS | Hierarquia de excecoes ja definida (AllocationException, DeadlockWarning, etc.) |
| XVII. Logging | N/A | Operacoes criticas serao logadas pelo use case |
| XVIII. Gestao de Configuracao | PASS | AllocationConfig recebe parametros, nao acessa repositorio |
| XIX. UI/UX | N/A | EP-008 (Presentation layer) |
| XX. Validacao | PASS | DTOs Pydantic validam entrada, dominio valida invariantes |
| XXI. CI/CD | PASS | Testes em pytest, mypy strict, black, isort |

## Project Structure

### Documentation (this feature)

\`\`\`text
specs/007-ep007-allocation-engine/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command)
\`\`\`

### Source Code (repository root)

\`\`\`text
src/backlog_manager/
├── domain/
│   ├── entities/
│   │   ├── story.py              # Story entity (existing)
│   │   ├── developer.py          # Developer entity (existing)
│   │   └── feature.py            # Feature entity (existing)
│   ├── services/
│   │   ├── scheduling_service.py # SchedulingService (existing, EP-006)
│   │   ├── dependency_service.py # DependencyService (existing, EP-005)
│   │   └── allocation_service.py # AllocationService (NEW - EP-007)
│   ├── exceptions/
│   │   ├── base.py               # BacklogManagerException (existing)
│   │   ├── allocation.py         # AllocationException, MaxIterationsExceeded (existing)
│   │   └── warnings.py           # DeadlockWarning, IdlenessWarning (existing)
│   └── value_objects/
│       └── holidays.py           # BRAZILIAN_HOLIDAYS_2026_2028 (existing)
├── application/
│   ├── use_cases/
│   │   └── allocation/           # NEW - EP-007
│   │       ├── __init__.py
│   │       └── execute_allocation.py
│   └── dto/
│       └── allocation/           # NEW - EP-007
│           ├── __init__.py
│           └── execute_allocation_dto.py
└── infrastructure/
    └── database/
        ├── repositories/
        │   └── sqlite_story_repository.py  # count_by_developer() (existing)
        └── unit_of_work.py                 # SQLiteUnitOfWork (existing)

tests/
├── unit/
│   └── domain/
│       └── services/
│           └── test_allocation_service.py  # NEW - EP-007
└── integration/
    └── application/
        └── use_cases/
            └── test_allocation_use_cases.py  # NEW - EP-007
\`\`\`

**Structure Decision**: Seguindo estrutura existente de Clean Architecture com src layout. AllocationService no dominio seguindo padrao de SchedulingService. Use case coordena persistencia.

## Complexity Tracking

> Nenhuma violacao da constituicao identificada. Design segue padroes estabelecidos nos epicos anteriores (EP-005, EP-006).
