# Implementation Plan: EP-009 Excel Integration

**Branch**: `009-ep009-excel-integration` | **Date**: 2026-03-03 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/009-ep009-excel-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Implementação da capacidade de integração Excel (Import/Export) para o Backlog Manager, permitindo interoperabilidade com outras ferramentas e mecanismo de backup manual. O recurso adiciona ExcelService na camada Infrastructure (openpyxl), ImportExcelUseCase e ExportExcelUseCase na Application layer, com integração UI via ExcelViewModel e botões/atalhos na MainWindow. Segue arquitetura Clean Architecture existente com processamento async via asyncio.to_thread().

## Technical Context

**Language/Version**: Python 3.11+ (>=3.11,<3.15 per pyproject.toml)
**Primary Dependencies**: PySide6 ^6.10.0 (UI), aiosqlite ^0.19.0 (DB), pydantic ^2.0 (DTOs), qasync ^0.27.1 (async Qt), openpyxl ^3.1.0 (NEW - Excel)
**Storage**: SQLite (via aiosqlite, existing schema with Story, Developer, Feature, Story_Dependency tables)
**Testing**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23, pytest-qt ^4.4
**Target Platform**: Windows (primary), with %APPDATA%/BacklogManager/ paths
**Project Type**: Desktop application (PySide6 GUI) distributed as Python library
**Performance Goals**: Import 100 stories < 10s, Export 500 stories < 15s (SC-001, SC-002)
**Constraints**: UI must remain responsive during I/O (asyncio.to_thread), max 500 stories per RNF-PERF-001
**Scale/Scope**: Single-user desktop app, max 500 stories backlog

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| §I Clean Architecture | ✅ PASS | ExcelService in Infrastructure, Protocol in Application, Use Cases coordinate |
| §II DDD | ✅ PASS | No new domain entities (Excel is I/O concern), uses existing Story/Feature/Developer |
| §III Repository Pattern | ✅ PASS | Uses existing UnitOfWork and repositories via Use Cases |
| §IV Dependency Injection | ✅ PASS | ExcelService and Use Cases registered in DIContainer |
| §V SQLite | ✅ PASS | No schema changes required, uses existing tables |
| §VI Packaging | ✅ PASS | openpyxl added to pyproject.toml dependencies |
| §VII Directory Structure | ✅ PASS | `infrastructure/excel/`, `application/use_cases/excel/`, `application/dto/excel/` |
| §VIII Async | ✅ PASS | asyncio.to_thread() for openpyxl (sync lib), async Use Cases |
| §IX Simplicity | ✅ PASS | Minimal implementation per spec, no over-engineering |
| §X Type Hints | ✅ PASS | Strict mypy compliance required |
| §XI Docstrings | ✅ PASS | Google-style docstrings on public APIs |
| §XII Import Organization | ✅ PASS | isort compliance |
| §XIII Naming Conventions | ✅ PASS | PascalCase classes, snake_case functions |
| §XIV Testing | ✅ PASS | Unit tests for Use Cases (mocked), Integration tests for ExcelService |
| §XV Idioma | ✅ PASS | Code in English, docs/logs in Portuguese |
| §XVI Error Handling | ✅ PASS | Domain exceptions for validation, Application exceptions for I/O |
| §XVII Logging | ✅ PASS | INFO/WARNING/ERROR logs per FR-120 to FR-126 |
| §XVIII Configuration | N/A | No new configuration parameters |
| §XIX UI/UX MVVM | ✅ PASS | ExcelViewModel with signals, Views for dialogs |
| §XX Input Validation | ✅ PASS | Excel headers, SP values, dependency cycles validated |
| §XXI CI/CD | ✅ PASS | Pre-commit hooks, mypy, pytest coverage gates |

**Gate Result**: ✅ PASS - No constitution violations identified

**Post-Design Re-evaluation (2026-03-03)**: All 21 principles re-verified after Phase 1 design artifacts (data-model.md, contracts/, quickstart.md). Design decisions remain compliant:
- ExcelService correctly placed in Infrastructure with Protocol in Application
- DTOs use Pydantic BaseModel per existing patterns
- No new domain entities introduced (Excel is I/O concern)
- Exception hierarchy extends BacklogManagerException
- Async pattern uses asyncio.to_thread() for sync openpyxl operations
- ViewModel signals follow existing MVVM pattern

## Project Structure

### Documentation (this feature)

```text
specs/009-ep009-excel-integration/
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
│   ├── entities/           # Existing: Story, Developer, Feature (no changes)
│   ├── value_objects/      # Existing: StoryPoint, StoryStatus (no changes)
│   ├── services/           # Existing: DependencyService, StoryService (used by import)
│   ├── interfaces/         # Existing: Repository protocols (no changes)
│   └── exceptions/         # Existing: BacklogManagerException hierarchy (no changes)
├── application/
│   ├── use_cases/
│   │   └── excel/          # NEW: Import/Export use cases
│   │       ├── __init__.py
│   │       ├── import_excel_use_case.py
│   │       └── export_excel_use_case.py
│   ├── dto/
│   │   └── excel/          # NEW: Excel DTOs
│   │       ├── __init__.py
│   │       ├── import_excel_dto.py
│   │       └── export_excel_dto.py
│   └── interfaces/
│       └── excel_service.py  # NEW: ExcelServiceProtocol
├── infrastructure/
│   ├── database/           # Existing: SQLite repos, UoW (no changes)
│   └── excel/              # NEW: Excel I/O implementation
│       ├── __init__.py
│       └── excel_service.py
└── presentation/
    ├── viewmodels/
    │   └── excel_viewmodel.py  # NEW: Excel operations ViewModel
    ├── views/
    │   └── main_window.py      # MODIFIED: Add import/export buttons, shortcuts
    └── container.py            # MODIFIED: Register Excel dependencies

tests/
├── unit/
│   └── application/
│       └── use_cases/
│           └── excel/      # NEW: Unit tests for Import/Export use cases
│               ├── test_import_excel_use_case.py
│               └── test_export_excel_use_case.py
└── integration/
    └── infrastructure/
        └── excel/          # NEW: Integration tests for ExcelService
            └── test_excel_service.py
```

**Structure Decision**: Follows existing Clean Architecture pattern with new `excel/` subdirectories in Application (use_cases, dto, interfaces) and Infrastructure layers. Presentation layer extends existing components (MainWindow, DIContainer) rather than creating new views since import/export use standard Qt file dialogs.

## Complexity Tracking

> **No constitution violations to justify** - All requirements fit within existing architecture patterns.
