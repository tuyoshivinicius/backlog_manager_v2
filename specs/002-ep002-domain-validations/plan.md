# Implementation Plan: EP-002 Dominio Core - Entidades e Validacoes

**Branch**: `002-ep002-domain-validations` | **Date**: 2026-02-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-ep002-domain-validations/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Aprimoramento das entidades Story, Developer e Feature com validacoes completas de invariantes, correcao da maquina de estados do StoryStatus para os 5 estados do SRS 6.5 (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO), e implementacao de validacao de auto-dependencia no repositorio. A abordagem tecnica utiliza dataclasses com `__post_init__` para validacoes fail-fast, mantendo a estrutura Clean Architecture existente.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: aiosqlite (async SQLite), aiofiles (async I/O), pydantic (DTOs)
**Storage**: SQLite via aiosqlite (async)
**Testing**: pytest + pytest-asyncio + pytest-cov
**Target Platform**: Windows/Linux (desktop application)
**Project Type**: library (core) + desktop-app (PySide6 - futuro)
**Performance Goals**: <= 100ms para operacoes CRUD simples (RNF-PERF-002)
**Constraints**: Validacoes sincronas no construtor, mensagens em portugues sem acentos
**Scale/Scope**: Single-user desktop application, ~1000 historias

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Mudancas restritas a Domain (entities, value_objects) e Infrastructure (repository). Sem violacao de dependencias. |
| II. DDD | ✅ PASS | Validacoes no `__post_init__` garantem invariantes. Entidades nao sao DTOs. |
| III. Repository Pattern | ✅ PASS | Validacao de auto-dependencia adicionada ao repositorio conforme spec. |
| IV. Dependency Injection | ✅ PASS | Nenhuma nova dependencia introduzida; estrutura existente mantida. |
| V. SQLite | ✅ PASS | Nenhuma mudanca em storage; repositorios existentes reutilizados. |
| VIII. Async | ✅ PASS | Domain permanece sincrono; validacoes no construtor sao sincronas. |
| IX. Simplicidade | ✅ PASS | Validacoes diretas no `__post_init__`, sem abstracoes desnecessarias. |
| X. Type Hints | ✅ PASS | Todos os campos e metodos com type hints. |
| XIV. Testes | ✅ PASS | Meta: 100% cobertura em domain/entities e domain/value_objects. |
| XV. Idioma | ✅ PASS | Codigo em ingles, mensagens de erro em portugues (sem acentos). |
| XVI. Tratamento de Erros | ✅ PASS | ValueError com mensagens descritivas conforme hierarquia definida. |

**Gate Result**: ✅ PASS - Nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

\`\`\`text
specs/002-ep002-domain-validations/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
\`\`\`

### Source Code (repository root)

\`\`\`text
src/backlog_manager/
├── domain/
│   ├── entities/
│   │   ├── story.py           # Validacoes de invariantes (modificar)
│   │   ├── developer.py       # Validacoes existentes (verificar)
│   │   └── feature.py         # Validacoes existentes (verificar)
│   └── value_objects/
│       ├── story_point.py     # StoryPoint enum (verificar)
│       └── story_status.py    # StoryStatus enum (modificar: 4 -> 5 estados)
└── infrastructure/
    └── database/
        └── repositories/
            └── story_dependency_repository.py  # Validacao auto-dependencia (modificar)

tests/
├── unit/
│   └── domain/
│       ├── entities/
│       │   ├── test_story.py       # Testes de validacao (criar/expandir)
│       │   ├── test_developer.py   # Testes de validacao (criar/expandir)
│       │   └── test_feature.py     # Testes de validacao (criar/expandir)
│       └── value_objects/
│           ├── test_story_point.py  # Testes StoryPoint (criar)
│           └── test_story_status.py # Testes StoryStatus (criar)
└── integration/
    └── infrastructure/
        └── database/
            └── repositories/
                └── test_story_dependency_repository.py  # Teste auto-dependencia (expandir)
\`\`\`

**Structure Decision**: Estrutura Clean Architecture existente do EP-001 mantida. Modificacoes focadas em:
1. `domain/value_objects/story_status.py` - Mudanca de 4 para 5 estados
2. `domain/entities/story.py` - Adicionar validacao de duration >= 0
3. `infrastructure/database/repositories/story_dependency_repository.py` - Validacao auto-dependencia

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

Nenhuma violacao identificada. Implementacao segue padroes existentes.

## Constitution Check (Post-Design)

*Re-avaliacao apos conclusao do design (Phase 1)*

| Principio | Status | Justificativa |
|-----------|--------|---------------|
| I. Clean Architecture | ✅ PASS | Design confirma mudancas apenas em Domain e Infrastructure. Sem dependencias cruzadas. |
| II. DDD | ✅ PASS | Validacoes fail-fast em `__post_init__`. Entidades ricas com invariantes. |
| III. Repository Pattern | ✅ PASS | Auto-dependencia validada no repositorio, nao na entidade (corretamente). |
| VIII. Async | ✅ PASS | Validacoes sincronas no construtor. Repository async mantido. |
| IX. Simplicidade | ✅ PASS | Mudancas minimas e focadas. Sem over-engineering. |
| XIV. Testes | ✅ PASS | Plan inclui testes unitarios e integracao para todas as mudancas. |
| XV. Idioma | ✅ PASS | StoryStatus usa valores em PT-BR sem acentos (EXECUCAO, CONCLUIDO). |
| XVI. Tratamento de Erros | ✅ PASS | ValueError com mensagens descritivas em portugues. |

**Post-Design Gate Result**: ✅ PASS - Design alinhado com Constitution.
