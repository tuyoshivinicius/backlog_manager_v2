# Implementation Plan: EP-005 Gestao de Dependencias - Servicos e Aplicacao

**Branch**: `005-ep005-dependency-services` | **Date**: 2026-03-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-ep005-dependency-services/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementar DependencyService (domain service) com deteccao de ciclos via DFS iterativo O(V+E), validacao cross-wave, e Use Cases completos (Add/Remove/Get Dependencies) com DTOs Pydantic. O servico de dominio sera sincrono (recebendo dados via parametros), enquanto os use cases coordenam operacoes assincronas via UnitOfWork.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: pydantic ^2.0, aiosqlite ^0.19.0, aiofiles ^23.0
**Storage**: SQLite (via aiosqlite, tabela Story_Dependency existente)
**Testing**: pytest ^8.0 com pytest-asyncio ^0.23, pytest-cov ^4.0
**Target Platform**: Windows/Linux desktop application
**Project Type**: Library Python (pip install) com UI PySide6 futura
**Performance Goals**: Deteccao de ciclo em grafo de 50 nos < 100ms (CT-002)
**Constraints**: DFS iterativo (evitar stack overflow em grafos profundos)
**Scale/Scope**: Backlogs de ate 500 historias, grafo de dependencias em memoria

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | DependencyService em domain/services/, Use Cases em application/use_cases/dependency/, DTOs em application/dto/dependency/ |
| II. DDD | ✅ PASS | DependencyService como domain service stateless, excecoes de dominio ja existem (CyclicDependencyException, InvalidWaveDependencyException) |
| III. Repository Pattern | ✅ PASS | Usa StoryDependencyRepository existente (Protocol), FeatureRepository para waves, StoryRepository para validacao |
| IV. Dependency Injection | ✅ PASS | Use Cases recebem UnitOfWork via construtor |
| V. SQLite | ✅ PASS | Tabela Story_Dependency ja existe, operacoes via aiosqlite |
| VII. Estrutura de Diretorios | ✅ PASS | Segue src layout: domain/services/, application/use_cases/, application/dto/ |
| VIII. Programacao Assincrona | ✅ PASS | Use Cases async, DependencyService sincrono (sem I/O) |
| IX. Simplicidade | ✅ PASS | DFS iterativo padrao, sem overengineering |
| X. Type Hints | ✅ PASS | Todos parametros e retornos tipados, mypy strict |
| XI. Docstrings | ✅ PASS | Google style em classes e metodos publicos |
| XIV. Estrategia de Testes | ✅ PASS | Unit tests para DependencyService (100%), integration tests para Use Cases |
| XVI. Tratamento de Erros | ✅ PASS | CyclicDependencyException, InvalidWaveDependencyException ja definidas, ValueError para validacoes |

## Project Structure

### Documentation (this feature)

```text
specs/005-ep005-dependency-services/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── domain/
│   ├── services/
│   │   ├── __init__.py
│   │   └── dependency_service.py     # NEW: DFS cycle detection, wave validation
│   └── exceptions/
│       └── dependency.py             # EXISTS: CyclicDependencyException, InvalidWaveDependencyException
├── application/
│   ├── use_cases/
│   │   └── dependency/               # NEW: Directory
│   │       ├── __init__.py
│   │       ├── add_dependency.py     # NEW: AddDependencyUseCase
│   │       ├── remove_dependency.py  # NEW: RemoveDependencyUseCase
│   │       ├── get_dependencies.py   # NEW: GetDependenciesUseCase
│   │       └── get_dependents.py     # NEW: GetDependentsUseCase
│   └── dto/
│       └── dependency/               # NEW: Directory
│           ├── __init__.py
│           ├── add_dependency_dto.py
│           ├── remove_dependency_dto.py
│           └── get_dependency_dto.py

tests/
├── unit/
│   ├── domain/
│   │   └── services/
│   │       └── test_dependency_service.py  # NEW
│   └── application/
│       └── use_cases/
│           └── dependency/                  # NEW: Directory
│               ├── __init__.py
│               ├── test_add_dependency.py
│               ├── test_remove_dependency.py
│               ├── test_get_dependencies.py
│               └── test_get_dependents.py
└── integration/
    └── application/
        └── use_cases/
            └── test_dependency_use_cases.py  # NEW
```

**Structure Decision**: Clean Architecture com separacao clara entre domain services (sincrono, regras de negocio puras) e application use cases (async, coordenacao). Segue padrao estabelecido nos EPs anteriores (001-004).

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Nenhuma violacao identificada. O design segue todos os principios da constituicao.


## Post-Design Constitution Re-check

*Re-evaluated after Phase 1 design completion.*

| Principio | Status | Notas Post-Design |
|-----------|--------|-------------------|
| I. Clean Architecture | CONFIRMED | Estrutura definida em Project Structure segue camadas corretamente |
| II. DDD | CONFIRMED | DependencyService e stateless, metodos recebem dados como parametros |
| VIII. Programacao Assincrona | CONFIRMED | Domain service sincrono, use cases async - conforme Principio VIII |
| XIV. Estrategia de Testes | CONFIRMED | Testes unitarios para domain service, testes de integracao para use cases |
| XVI. Tratamento de Erros | CONFIRMED | Excecoes existentes reutilizadas, ValueError para validacoes simples |

**Resultado**: Todos os principios verificados e confirmados. Pronto para Phase 2 (tasks.md via /speckit.tasks).
