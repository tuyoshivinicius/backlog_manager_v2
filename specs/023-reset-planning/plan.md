# Implementation Plan: Novo Planejamento (Reset de Cronograma e Alocacao)

**Branch**: `023-reset-planning` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/023-reset-planning/spec.md`

## Summary

Add a "Novo Planejamento" action that atomically resets all calculated planning fields (duration, start_date, end_date, developer_id) from stories while preserving user data and dependencies. Accessible via menu Ferramentas, Toolbar, and Ctrl+Shift+N. Includes confirmation dialog with preview counts and visual feedback via status bar.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite
**Storage**: SQLite (no schema changes — only sets existing columns to NULL)
**Testing**: pytest + pytest-qt + qasync
**Target Platform**: Windows desktop
**Project Type**: Desktop app (Clean Architecture, MVVM)
**Performance Goals**: Reset < 500ms for backlogs up to 500 stories
**Constraints**: Atomic operation (all or nothing), no UI freeze
**Scale/Scope**: Typical backlogs < 500 stories

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Pre-Design | Post-Design | Notes |
|-----------|-----------|-------------|-------|
| I. Clean Architecture | PASS | PASS | Use case in Application, ViewModel in Presentation |
| II. DDD | PASS | PASS | Uses `object.__setattr__()` established pattern |
| III. Repository Pattern | PASS | PASS | Uses existing StoryRepository.update() via UoW |
| IV. DI | PASS | PASS | Container wires use cases and viewmodel |
| V. SQLite | PASS | PASS | No schema changes |
| VIII. Async | PASS | PASS | Use cases async, domain stays sync |
| IX. Simplicidade | PASS | PASS | Follows existing patterns exactly |
| XIV. Testes | PASS | PASS | Unit + integration + e2e planned |
| XV. Idioma | PASS | PASS | Code English, UI Portuguese |
| XVI. Tratamento de Erros | PASS | PASS | Signals for error propagation to UI |

No violations. No complexity tracking needed.

## Project Structure

### Documentation (this feature)

```text
specs/023-reset-planning/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── ui-contract.md
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── application/
│   ├── dto/
│   │   └── planning/                       # NEW directory
│   │       ├── __init__.py
│   │       └── reset_planning_dto.py       # DTOs
│   └── use_cases/
│       └── planning/                       # NEW directory
│           ├── __init__.py
│           ├── reset_planning.py           # ResetPlanningUseCase
│           └── count_affected_stories.py   # CountAffectedStoriesUseCase
├── presentation/
│   ├── container.py                        # MODIFY
│   ├── viewmodels/
│   │   ├── reset_planning_viewmodel.py     # NEW
│   │   └── status_bar_viewmodel.py         # MODIFY
│   └── views/
│       ├── confirm_reset_dialog.py         # NEW
│       └── main_window.py                  # MODIFY
└── assets/icons/
    └── arrows-down-up.svg                  # NEW

tests/
├── unit/
│   ├── application/use_cases/planning/     # NEW directory
│   │   ├── test_reset_planning.py
│   │   └── test_count_affected_stories.py
│   └── presentation/
│       ├── viewmodels/
│       │   └── test_reset_planning_viewmodel.py  # NEW
│       └── views/
│           └── test_confirm_reset_dialog.py      # NEW
└── e2e/
    └── test_ep023_reset_planning.py        # NEW
```

**Structure Decision**: Follows existing project structure. New `planning/` subdirectories mirror existing `scheduling/` and `allocation/` organization.

## Implementation Order

| Step | Component | Files | Depends On |
|------|-----------|-------|------------|
| 1 | DTOs | `dto/planning/reset_planning_dto.py` + `__init__.py` | — |
| 2 | Use Cases | `use_cases/planning/reset_planning.py`, `count_affected_stories.py` + `__init__.py` | Step 1 |
| 3 | Icon | `assets/icons/arrows-down-up.svg` | — (parallel) |
| 4 | ViewModel | `viewmodels/reset_planning_viewmodel.py` | Steps 1, 2 |
| 5 | StatusBar VM | `viewmodels/status_bar_viewmodel.py` (modify) | — |
| 6 | Container | `container.py` (modify) | Steps 2, 4 |
| 7 | Dialog | `views/confirm_reset_dialog.py` | Step 3 |
| 8 | MainWindow | `views/main_window.py` (modify) | Steps 4, 6, 7 |
| 9 | Unit Tests | `tests/unit/...` | Steps 1-8 |
| 10 | E2E Tests | `tests/e2e/test_ep023_reset_planning.py` | Steps 1-8 |

## Key Patterns to Reuse

| Pattern | Source File |
|---------|------------|
| Use case (async, UoW, setattr) | `application/use_cases/scheduling/calculate_schedule.py` |
| ViewModel (signals, is_running) | `presentation/viewmodels/schedule_viewmodel.py` |
| Container (factory + lazy prop) | `presentation/container.py` |
| Dialog (icon, text, buttons) | `presentation/views/confirm_delete_dialog.py` |
| Toolbar action | `presentation/views/main_window.py:402-415` |
| Async handler | `presentation/views/main_window.py` (QTimer.singleShot pattern) |

## Complexity Tracking

No violations to justify. All patterns reuse existing architecture.
