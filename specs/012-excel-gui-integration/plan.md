# Implementation Plan: Excel Import/Export GUI Integration

**Branch**: `012-excel-gui-integration` | **Date**: 2026-03-04 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/012-excel-gui-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Integrate Excel import/export functionality into the MainWindow GUI by adding toolbar buttons, keyboard shortcuts (Ctrl+I/Ctrl+E), progress dialogs, and result/error message boxes. Leverages existing ExcelViewModel from EP-009 with its signals (import_completed, import_error, export_completed, export_error) and methods (import_from_file, export_to_file).

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: PySide6, qasync (async/Qt integration), openpyxl (via ExcelService)
**Storage**: SQLite (via aiosqlite) - existing infrastructure
**Testing**: pytest, pytest-qt, pytest-asyncio
**Target Platform**: Desktop (Windows, Linux) - PySide6 GUI application
**Project Type**: Desktop application with MVVM architecture
**Performance Goals**: ≤100ms UI response for CRUD operations (RNF-PERF-002); progress dialog for large files
**Constraints**: Import/export must not block UI; operations use async/await via qasync event loop
**Scale/Scope**: Single user desktop app; support files with 500+ stories per spec edge cases

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Views import only from viewmodels (ExcelViewModel); no direct domain/infrastructure access |
| III. Repository Pattern | ✅ PASS | N/A for this feature - uses ExcelViewModel which handles repositories internally |
| IV. Dependency Injection | ✅ PASS | MainWindow obtains ExcelViewModel via DIContainer.excel_viewmodel property |
| VIII. Async Programming | ✅ PASS | Uses qasync with QTimer.singleShot + asyncio.create_task pattern (existing pattern in MainWindow) |
| IX. Simplicidade | ✅ PASS | Minimal UI additions: 2 toolbar buttons, 2 shortcuts, dialogs for feedback |
| XIV. Estratégia de Testes | ✅ PASS | pytest-qt tests planned; follows existing dialog test patterns |
| XIX. Padrões UI/UX (MVVM) | ✅ PASS | Views contain UI only; logic in ExcelViewModel; signals for data binding |
| XV. Idioma | ✅ PASS | UI messages in Portuguese (tooltips, dialogs); code in English |

**Gate Result**: PASS - No violations requiring justification.

## Project Structure

### Documentation (this feature)

```text
specs/012-excel-gui-integration/
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
├── presentation/
│   ├── viewmodels/
│   │   └── excel_viewmodel.py     # EXISTS - ExcelViewModel with import/export signals
│   └── views/
│       └── main_window.py         # MODIFY - Add toolbar buttons, shortcuts, dialogs
└── [other layers unchanged]

tests/
├── unit/
│   └── presentation/
│       └── viewmodels/            # ExcelViewModel tests (EP-009)
└── integration/
    └── presentation/
        └── test_main_window_excel.py  # NEW - pytest-qt tests for import/export GUI
```

**Structure Decision**: Single project layout per Constitution VII. Only modifies existing MainWindow view file and adds integration tests.

## Complexity Tracking

> No violations - complexity tracking not required.

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| N/A | N/A | N/A |

---

## Post-Design Constitution Re-Check

*Verified after Phase 1 design completion.*

| Principle | Status | Post-Design Notes |
|-----------|--------|-------------------|
| I. Clean Architecture | PASS | Design confirms: MainWindow only imports ExcelViewModel, not domain/infrastructure |
| III. Repository Pattern | PASS | No new repositories; ExcelViewModel handles data access |
| IV. Dependency Injection | PASS | ExcelViewModel obtained via DIContainer.excel_viewmodel |
| VIII. Async Programming | PASS | QTimer.singleShot + asyncio.create_task pattern documented in quickstart.md |
| IX. Simplicidade | PASS | Minimal changes: ~100 lines added to MainWindow |
| X. Type Hints | PASS | All new methods will have type hints (see quickstart.md examples) |
| XI. Docstrings | PASS | Public methods will have docstrings in Portuguese |
| XIV. Estrategia de Testes | PASS | test_main_window_excel.py planned with pytest-qt |
| XV. Idioma | PASS | Messages in Portuguese; code in English |
| XIX. Padroes UI/UX (MVVM) | PASS | Views contain UI only; signals connect to ExcelViewModel |
| XX. Validacao Entrada | PASS | File path validated by QFileDialog; content validation in ExcelViewModel |

**Post-Design Gate Result**: PASS - All principles verified. No violations.
