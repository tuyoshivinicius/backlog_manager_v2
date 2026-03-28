# Implementation Plan: EP-003 Gestao de Backlog - Servicos e Aplicacao

**Branch**: `003-ep003-backlog-services` | **Date**: 2026-02-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-ep003-backlog-services/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementacao da camada de servico de dominio (StoryService) e camada de aplicacao (Use Cases e DTOs) para gestao completa do backlog de historias. Inclui extensoes aos protocols de repositorio para suportar operacoes como geracao automatica de ID (COMPONENTE-NNN), calculo de prioridade inicial, limpeza de dependencias em cascata, e troca de prioridades. Arquitetura Clean Architecture com inversao de dependencias via UnitOfWork.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: pydantic ^2.0 (DTOs), aiosqlite ^0.19.0, aiofiles ^23.0
**Storage**: SQLite via aiosqlite (ja configurado em EP-001)
**Testing**: pytest ^8.0 + pytest-asyncio ^0.23 + pytest-cov ^4.0
**Target Platform**: Desktop (Windows/Linux), biblioteca Python
**Project Type**: Library (pip install)
**Performance Goals**: <= 100ms para operacoes CRUD simples (RNF-PERF-002)
**Constraints**: Transacoes atomicas via UnitOfWork, rollback automatico em falhas
**Scale/Scope**: Single-user desktop application, ~100-500 historias por backlog

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Pre-Design Evaluation

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Architecture | PASS | StoryService em domain/services/, Use Cases em application/use_cases/, DTOs em application/dto/ |
| II. DDD | PASS | Domain Service stateless, entidades ricas com validacoes, fail-fast no construtor |
| III. Repository Pattern | PASS | Extensoes aos Protocols existentes em domain/interfaces/, implementacoes em infrastructure/ |
| IV. Dependency Injection | PASS | Use Cases recebem UnitOfWork factory via construtor |
| V. SQLite | PASS | Utiliza infraestrutura SQLite existente |
| VI. Packaging | PASS | Codigo em src/backlog_manager/, testes em tests/ |
| VII. Estrutura de Diretorios | PASS | Segue layout existente do projeto |
| VIII. Programacao Assincrona | PASS | Domain sync, Application/Infrastructure async |
| IX. Simplicidade | PASS | Um service, 7 use cases, DTOs minimos |
| X. Type Hints | PASS | Mypy strict habilitado |
| XI. Docstrings | PASS | Google style obrigatorio |
| XII. Imports | PASS | isort configurado |
| XIII. Nomenclatura | PASS | PascalCase classes, snake_case funcoes |
| XIV. Testes | PASS | 100% cobertura em domain/services e application/use_cases |
| XV. Idioma | PASS | Codigo ingles, docs portugues |
| XVI. Tratamento de Erros | PASS | ValueError para validacoes, mensagens em portugues |
| XVII. Logging | N/A | Nao aplicavel nesta fase |
| XVIII. Configuracao | N/A | Nao aplicavel nesta fase |
| XIX. UI/UX | N/A | Nao aplicavel (sem UI neste EP) |
| XX. Validacao de Entrada | PASS | DTOs Pydantic validam entrada |
| XXI. CI/CD | PASS | Pre-commit hooks existentes |

**Gate Result**: PASS - Nenhuma violacao identificada

## Project Structure

### Documentation (this feature)

\`\`\`text
specs/003-ep003-backlog-services/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
\`\`\`

### Source Code (repository root)

\`\`\`text
src/backlog_manager/
├── domain/
│   ├── interfaces/
│   │   └── repositories.py      # Extensoes: get_max_id_number, get_max_priority, get_by_priority, remove_all_for_story
│   └── services/
│       └── story_service.py     # NOVO: StoryService domain service
├── application/
│   ├── dto/
│   │   └── story/               # NOVO: DTOs Pydantic para historias
│   │       ├── __init__.py
│   │       ├── create_story_dto.py
│   │       ├── update_story_dto.py
│   │       ├── story_output_dto.py
│   │       ├── list_stories_dto.py
│   │       ├── move_priority_dto.py
│   │       └── assign_developer_dto.py
│   └── use_cases/
│       └── story/               # NOVO: Use cases de historias
│           ├── __init__.py
│           ├── create_story_dto.py
│           ├── update_story_dto.py
│           ├── delete_story.py
│           ├── duplicate_story.py
│           ├── list_stories_dto.py
│           ├── move_priority_dto.py
│           └── assign_developer_dto.py
└── infrastructure/
    └── database/
        └── repositories/
            ├── story_repository.py           # Extensao: novos metodos
            └── story_dependency_repository.py # Extensao: remove_all_for_story

tests/
├── unit/
│   ├── domain/
│   │   └── services/
│   │       └── test_story_service.py         # NOVO: Testes unitarios StoryService
│   └── application/
│       └── use_cases/
│           └── story/
│               ├── test_create_story.py      # NOVO
│               ├── test_update_story.py      # NOVO
│               ├── test_delete_story.py      # NOVO
│               ├── test_duplicate_story.py   # NOVO
│               ├── test_list_stories.py      # NOVO
│               ├── test_move_priority.py     # NOVO
│               └── test_assign_developer.py  # NOVO
└── integration/
    └── infrastructure/
        └── database/
            └── repositories/
                ├── test_story_repository.py  # Extensao: novos metodos
                └── test_story_dependency_repository.py # Extensao
\`\`\`

**Structure Decision**: Utiliza a estrutura Clean Architecture existente do projeto, adicionando StoryService na camada de dominio e Use Cases na camada de aplicacao. DTOs organizados por feature (story/) seguindo padrao estabelecido.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Nenhuma violacao identificada - tabela nao aplicavel.

### Post-Design Evaluation

Apos completar Phase 0 (research.md) e Phase 1 (data-model.md, contracts/, quickstart.md):

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Architecture | PASS | Design confirmado: StoryService em domain/services/, Use Cases em application/use_cases/, DTOs em application/dto/story/ |
| II. DDD | PASS | StoryService e domain service stateless, coordena operacoes entre entidades e repositorios |
| III. Repository Pattern | PASS | 4 novos metodos nos protocols: get_max_id_number, get_max_priority, get_by_priority, remove_all_for_story |
| IV. Dependency Injection | PASS | Use Cases recebem Callable[[], UnitOfWork] como factory |
| VIII. Programacao Assincrona | PASS | StoryService com metodos async que recebem UnitOfWork |
| IX. Simplicidade | PASS | 1 domain service, 7 use cases, DTOs minimos com validacao Pydantic |
| XIV. Testes | PASS | Estrutura definida: unit/ para service e use cases, integration/ para repositorios |
| XVI. Tratamento de Erros | PASS | ValueError com mensagens em portugues conforme spec |
| XX. Validacao de Entrada | PASS | DTOs Pydantic com field_validators para component, story_points, etc. |

**Post-Design Gate Result**: PASS - Design alinhado com constituicao
