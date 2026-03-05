# Implementation Plan: Schedule Calculation GUI Integration

**Branch**: `013-schedule-gui-integration` | **Date**: 2026-03-04 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/013-schedule-gui-integration/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Expose the existing `CalculateScheduleUseCase` in the GUI by adding a toolbar button ("Calcular Cronograma") with keyboard shortcut (Ctrl+Shift+C). Follow the established "Alocar Automaticamente" pattern for async operations, visual feedback, and error handling. The implementation involves creating a ScheduleViewModel with appropriate Qt signals, adding the toolbar action, and wiring success/error dialogs.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: PySide6, pydantic ^2.0, aiosqlite ^0.19.0, qasync
**Storage**: SQLite (via aiosqlite)
**Testing**: pytest, pytest-qt, pytest-cov
**Target Platform**: Windows/Linux desktop
**Project Type**: desktop-app (library-first with PySide6 GUI)
**Performance Goals**: Schedule calculation for 100 stories < 500ms (SC-002)
**Constraints**: UI latency <= 100ms for CRUD operations (RNF-PERF-002)
**Scale/Scope**: Single-user desktop application, up to hundreds of stories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Clean Architecture | Presentation depends only on Application, not Domain | PASS | ScheduleViewModel will use CalculateScheduleUseCase via DI container |
| II. DDD | Domain entities immutable, business logic in domain | PASS | No new domain code needed - using existing SchedulingService |
| III. Repository Pattern | Repositories return entities, not DTOs | PASS | Using existing StoryRepository via UoW |
| IV. Dependency Injection | Dependencies via DIContainer | PASS | Will add schedule_viewmodel property to container |
| VIII. Async Programming | Application/Infrastructure async, Domain sync | PASS | ScheduleViewModel will use async/await pattern |
| XIV. Testing Strategy | 80%+ coverage, pytest-qt for GUI | PASS | Will add unit tests for ViewModel, integration test for flow |
| XIX. UI/UX (PySide6) | MVVM pattern, Views import only ViewModels/DTOs | PASS | Following AllocationViewModel as template |
| XVI. Error Handling | Clear Portuguese messages, no crashes | PASS | Will handle CyclicDependencyException and validation errors |
| XVII. Logging | INFO for operations, ERROR for exceptions | PASS | Will log schedule calculation events |

**Pre-Design Gate**: PASSED - No constitution violations anticipated

## Project Structure

### Documentation (this feature)

```text
specs/013-schedule-gui-integration/
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
│   ├── entities/              # Story, Developer, Feature, Configuration
│   ├── value_objects/         # StoryPoint, StoryStatus
│   ├── services/              # SchedulingService (already exists)
│   ├── interfaces/            # Repository interfaces (Protocols)
│   └── exceptions/            # CyclicDependencyException (already exists)
├── application/
│   ├── use_cases/
│   │   └── scheduling/
│   │       └── calculate_schedule.py  # CalculateScheduleUseCase (already exists)
│   └── dto/
│       └── scheduling/
│           └── calculate_schedule_dto.py  # Input/Output DTOs (already exist)
├── infrastructure/
│   └── database/
│       └── unit_of_work.py    # SQLiteUnitOfWork (already exists)
└── presentation/
    ├── viewmodels/
    │   └── schedule_viewmodel.py  # NEW: ScheduleViewModel
    ├── views/
    │   └── main_window.py     # MODIFY: Add toolbar action
    └── container.py           # MODIFY: Add schedule_viewmodel property

tests/
├── unit/
│   └── presentation/
│       └── viewmodels/
│           └── test_schedule_viewmodel.py  # NEW
└── integration/
    └── presentation/
        └── test_schedule_gui_integration.py  # NEW
```

**Structure Decision**: Clean Architecture structure following existing patterns. New files only in presentation layer (ScheduleViewModel). Minimal modifications to existing files (MainWindow toolbar, DIContainer).

## Complexity Tracking

> No constitution violations to justify - implementation follows established patterns.

| Aspect | Decision | Rationale |
|--------|----------|-----------|
| Pattern | Follow AllocationViewModel pattern | Proven async operation pattern with signals |
| Validation | Reuse ConfigPanel.validate() | velocity and start_date already validated |
| Error Handling | Map CyclicDependencyException to dialog | Clear user feedback for cycle detection |

## Post-Design Constitution Re-Check

*Re-evaluated after Phase 1 design completion.*

| Principle | Requirement | Status | Notes |
|-----------|-------------|--------|-------|
| I. Clean Architecture | Presentation depends only on Application | PASS | ScheduleViewModel uses only DTOs and use case via container |
| II. DDD | No new domain code | PASS | All domain logic reused from existing services |
| III. Repository Pattern | N/A | PASS | No new repository code |
| IV. Dependency Injection | DIContainer updated | PASS | schedule_viewmodel property added lazily |
| VIII. Async Programming | Async ViewModel pattern | PASS | execute() is async, signals for UI updates |
| X. Type Hints | All new code typed | PASS | Full type annotations in ScheduleViewModel |
| XI. Docstrings | Public methods documented | PASS | Google-style docstrings included |
| XIV. Testing Strategy | Test files identified | PASS | Unit + integration tests planned |
| XV. Language | Code in English, messages in Portuguese | PASS | Error messages without accents |
| XVI. Error Handling | CyclicDependencyException mapped | PASS | User-friendly error dialog |
| XVII. Logging | INFO/ERROR logging | PASS | Logging in execute() method |
| XIX. UI/UX (PySide6) | MVVM respected | PASS | View only connects signals, no business logic |

**Post-Design Gate**: PASSED - Design follows all constitution principles
