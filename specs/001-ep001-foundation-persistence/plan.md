# Implementation Plan: EP-001 Fundacao e Persistencia

**Branch**: `001-ep001-foundation-persistence` | **Date**: 2026-02-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-ep001-foundation-persistence/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementacao da fundacao do Backlog Manager: estrutura de projeto Python em 4 camadas (Clean Architecture), banco de dados SQLite com schema completo (4 tabelas: Story, Story_Dependency, Developer, Feature), hierarquia de excecoes customizadas, sistema de logging com rotacao, e pipeline de qualidade de codigo (black, isort, pytest, pre-commit).

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Poetry (packaging), aiosqlite (async SQLite), aiofiles (async I/O), pydantic (DTOs), PySide6 (GUI - futuro)
**Storage**: SQLite em `%APPDATA%/BacklogManager/data/backlog.db`
**Testing**: pytest com pytest-cov para cobertura, meta 80%+
**Target Platform**: Windows 10/11
**Project Type**: library (pip installable) com futura GUI desktop
**Performance Goals**: Latencia <=100ms para operacoes CRUD, suporte a 500 historias sem degradacao
**Constraints**: Arquivo unico de banco (SQLite), zero dependencias de servidor externo
**Scale/Scope**: Aplicacao single-user desktop, ~500 historias, ~50 desenvolvedores

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Requisito | Status | Notas |
|-----------|-----------|--------|-------|
| I. Clean Architecture | 4 camadas: Presentation → Infrastructure → Application → Domain | ✅ CONFORME | Estrutura definida na spec: UI, Services, Domain, Repository |
| II. DDD | Entidades ricas, invariantes no construtor | ✅ CONFORME | Story, Developer, Feature como entidades de dominio |
| III. Repository Pattern | Interfaces como Protocol na camada Domain | ✅ CONFORME | Repositorios definidos em domain/interfaces/ |
| IV. Dependency Injection | Container configurado na raiz de composicao | ✅ CONFORME | DIContainer na presentation ou entry point |
| V. SQLite | Banco em %APPDATA%, schema versionado | ✅ CONFORME | FR-004 define localizacao, schema.sql definido |
| VI. Packaging | Poetry, pip installable, src layout | ✅ CONFORME | FR-002 define entry point via pip install -e . |
| VII. Estrutura de Diretorios | src/backlog_manager/, tests/ na raiz | ✅ CONFORME | Estrutura alinhada com template da constitution |
| VIII. Async | Application e Infrastructure async, Domain sync | ✅ CONFORME | aiosqlite para DB, aiofiles para I/O |
| IX. Simplicidade | KISS, DRY, YAGNI | ✅ CONFORME | Scope limitado a fundacao essencial |
| X. Type Hints | Mypy strict, 100% type hints | ✅ CONFORME | Incluso no pipeline de qualidade |
| XI. Docstrings | Google style em codigo publico | ✅ CONFORME | pydocstyle configurado |
| XIV. Testes | pytest, 80%+ cobertura | ✅ CONFORME | SC-007 define 80% minimo |
| XVI. Tratamento de Erros | Hierarquia BacklogManagerException | ✅ CONFORME | FR-014 a FR-024 definem hierarquia completa |
| XVII. Logging | Arquivo em AppData, rotacao 10MB | ✅ CONFORME | FR-025 a FR-028 definem sistema de logging |
| XXI. CI/CD | black, isort, mypy, pytest-cov | ✅ CONFORME | FR-029 a FR-034 definem pipeline |

**Gate Status**: ✅ PASSED - Todos os principios constitucionais atendidos

## Project Structure

### Documentation (this feature)

\`\`\`text
specs/001-ep001-foundation-persistence/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
\`\`\`

### Source Code (repository root)

\`\`\`text
src/
└── backlog_manager/               # Pacote importavel
    ├── __init__.py
    ├── domain/
    │   ├── __init__.py
    │   ├── entities/              # Story, Developer, Feature
    │   ├── value_objects/         # StoryPoint, StoryStatus
    │   ├── services/              # Domain services
    │   ├── interfaces/            # Repository Protocols
    │   └── exceptions/            # BacklogManagerException hierarchy
    ├── application/
    │   ├── __init__.py
    │   ├── use_cases/
    │   ├── dto/                   # Pydantic DTOs
    │   └── interfaces/
    ├── infrastructure/
    │   ├── __init__.py
    │   ├── database/
    │   │   ├── __init__.py
    │   │   ├── repositories/      # SQLite implementations
    │   │   ├── migrations/        # Schema migrations
    │   │   ├── schema.sql         # Database schema
    │   │   ├── sqlite_connection.py
    │   │   └── unit_of_work.py
    │   └── logging/
    │       ├── __init__.py
    │       └── logger_config.py   # Logging setup
    └── presentation/
        ├── __init__.py
        ├── viewmodels/            # MVVM ViewModels
        └── views/                 # PySide6 views (futuro)

tests/
├── __init__.py
├── unit/                          # Rapidos (< 1ms), sem I/O
│   ├── __init__.py
│   ├── domain/
│   │   ├── entities/
│   │   ├── value_objects/
│   │   └── exceptions/
│   └── application/
└── integration/                   # Com I/O real (SQLite)
    ├── __init__.py
    └── infrastructure/
        └── database/
\`\`\`

**Structure Decision**: Clean Architecture com src layout (Poetry). Estrutura alinhada com Constitution VII, separando domain, application, infrastructure e presentation. Testes fora de src/ conforme padrao Poetry.

## Complexity Tracking

> **Nenhuma violacao identificada - estrutura alinha 100% com Constitution**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Post-Design Constitution Re-Check

*Re-avaliacao apos finalizacao do Phase 1 Design*

| Principio | Status Pre-Design | Status Pos-Design | Notas |
|-----------|-------------------|-------------------|-------|
| I. Clean Architecture | ✅ CONFORME | ✅ CONFORME | data-model.md define entidades na camada correta |
| II. DDD | ✅ CONFORME | ✅ CONFORME | Invariantes definidas em __post_init__ das entidades |
| III. Repository Pattern | ✅ CONFORME | ✅ CONFORME | Protocols definidos em contracts/repository-protocols.md |
| V. SQLite | ✅ CONFORME | ✅ CONFORME | Schema completo em data-model.md com indices |
| VIII. Async | ✅ CONFORME | ✅ CONFORME | Todos os metodos de repository sao async |
| XVI. Tratamento de Erros | ✅ CONFORME | ✅ CONFORME | Hierarquia completa em contracts/exception-hierarchy.md |

**Post-Design Gate Status**: ✅ PASSED - Design alinhado com todos os principios constitucionais

---

## Generated Artifacts

| Artefato | Caminho | Status |
|----------|---------|--------|
| plan.md | specs/001-ep001-foundation-persistence/plan.md | ✅ Gerado |
| research.md | specs/001-ep001-foundation-persistence/research.md | ✅ Gerado |
| data-model.md | specs/001-ep001-foundation-persistence/data-model.md | ✅ Gerado |
| quickstart.md | specs/001-ep001-foundation-persistence/quickstart.md | ✅ Gerado |
| repository-protocols.md | specs/001-ep001-foundation-persistence/contracts/repository-protocols.md | ✅ Gerado |
| exception-hierarchy.md | specs/001-ep001-foundation-persistence/contracts/exception-hierarchy.md | ✅ Gerado |
| CLAUDE.md | CLAUDE.md | ✅ Atualizado |
