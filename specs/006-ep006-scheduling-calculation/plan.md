# Implementation Plan: EP-006 Calculo de Cronograma

**Branch**: `006-ep006-scheduling-calculation` | **Date**: 2026-03-02 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/006-ep006-scheduling-calculation/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementacao do SchedulingService como domain service stateless para calculo de cronogramas de historias do backlog. O servico calcula duracao baseada em story points e velocidade, avanca datas considerando apenas dias uteis (segunda a sexta) excluindo feriados brasileiros (2026-2028), e ordena historias topologicamente via Kahn's algorithm com desempate por prioridade. Reutiliza DependencyService.build_graph() do EP-005 para construcao do grafo e CyclicDependencyException para deteccao de ciclos.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: pydantic ^2.0, aiosqlite ^0.19.0, aiofiles ^23.0 (existentes via EP-005)
**Storage**: SQLite (via aiosqlite, tabelas Story e Story_Dependency existentes)
**Testing**: pytest com pytest-cov, pytest-asyncio
**Target Platform**: Desktop (Windows/Linux)
**Project Type**: Desktop application (library-first com UI PySide6)
**Performance Goals**: Ordenacao topologica de 100 historias em < 100ms com complexidade O(V+E)
**Constraints**: Calculos sincronos no dominio; I/O assincrono na aplicacao; transacoes atomicas via UnitOfWork
**Scale/Scope**: Single-user, backlogs de ate 500 historias, feriados 2026-2028

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Conformidade | Notas |
|-----------|--------------|-------|
| I Clean Architecture | CONFORME | SchedulingService no dominio (sincrono), use cases na aplicacao (async), DTOs com Pydantic |
| II DDD | CONFORME | Domain service stateless recebe dados como parametros; invariantes no construtor das entidades |
| III Repository Pattern | CONFORME | Reutiliza StoryRepository e StoryDependencyRepository existentes via UnitOfWork |
| IV Dependency Injection | CONFORME | Use cases recebem UnitOfWork via construtor |
| V SQLite | CONFORME | Reutiliza tabelas Story e Story_Dependency existentes |
| VII Estrutura de Diretorios | CONFORME | Domain service em domain/services/, use cases em application/use_cases/scheduling/ |
| VIII Programacao Assincrona | CONFORME | Domain sincrono; Application e Infrastructure async |
| X Type Hints | CONFORME | Todos os metodos terao type hints completos |
| XIV Estrategia de Testes | CONFORME | 100% cobertura para SchedulingService (domain); use cases testados com repos mockados |
| XVI Tratamento de Erros | CONFORME | Reutiliza CyclicDependencyException; ValueError para velocity invalida |
| XVIII Gestao de Configuracao | CONFORME | velocity recebida como parametro (nao acessa Configuration diretamente) |
| XX Validacao de Entrada | CONFORME | DTOs Pydantic validam velocity > 0, story_points in {3,5,8,13} |

**Resultado Pre-Phase 0**: Todos os gates passam. Nenhuma violacao identificada.

**Resultado Pos-Phase 1 (Re-check)**: Design confirmado em conformidade com a Constituicao. Artefatos gerados (research.md, data-model.md, contracts/, quickstart.md) seguem os principios estabelecidos:
- SchedulingService e domain service puro e sincrono (I, II, VIII)
- Use cases sao async e usam UnitOfWork (III, IV, VIII)
- DTOs Pydantic com validacoes (XX)
- Estrutura de diretorios conforme padrao (VII)
- Testes planejados com 100% cobertura para dominio (XIV)

## Project Structure

### Documentation (this feature)

```text
specs/006-ep006-scheduling-calculation/
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
│   │   ├── __init__.py                    # Exportar SchedulingService
│   │   ├── dependency_service.py          # Existente (EP-005) - reutilizar build_graph
│   │   └── scheduling_service.py          # NOVO - domain service para cronograma
│   ├── value_objects/
│   │   ├── __init__.py                    # Exportar BRAZILIAN_HOLIDAYS_2026_2028
│   │   └── brazilian_holidays.py          # NOVO - feriados 2026-2028
│   └── exceptions/
│       └── dependency.py                  # Existente - CyclicDependencyException
├── application/
│   ├── use_cases/
│   │   └── scheduling/                    # NOVO diretorio
│   │       ├── __init__.py
│   │       ├── calculate_schedule.py      # NOVO - CalculateScheduleUseCase
│   │       ├── calculate_duration.py      # NOVO - CalculateDurationUseCase
│   │       └── calculate_story_dates.py   # NOVO - CalculateStoryDatesUseCase
│   └── dto/
│       └── scheduling/                    # NOVO diretorio
│           ├── __init__.py
│           ├── calculate_schedule_dto.py  # NOVO - Input/Output DTOs
│           ├── calculate_duration_dto.py  # NOVO - Input/Output DTOs
│           └── calculate_story_dates_dto.py # NOVO - Input/Output DTOs

tests/
├── unit/
│   └── domain/
│       └── services/
│           └── test_scheduling_service.py # NOVO - testes unitarios 100%
└── integration/
    └── application/
        └── use_cases/
            └── test_scheduling_use_cases.py # NOVO - testes de integracao
```

**Structure Decision**: Segue o layout Clean Architecture existente do projeto (Constitution VII). Domain service em `domain/services/`, value object em `domain/value_objects/`, use cases em `application/use_cases/scheduling/`, DTOs em `application/dto/scheduling/`.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Nenhuma violacao identificada. Nao ha complexity tracking necessario.
