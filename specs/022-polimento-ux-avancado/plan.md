# Implementation Plan: EP-022 — Polimento e UX Avançado

**Branch**: `022-polimento-ux-avancado` | **Date**: 2026-03-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/022-polimento-ux-avancado/spec.md`

## Summary

EP-022 adds 8 UX polish features to the Backlog Manager: SP breakdown by status in the status bar, blocking indicators in the dependencies column, config persistence via QSettings, visual wave grouping separators, rich hover tooltips, operation cancellation, an About dialog, and responsive column hiding. All changes are confined to the Presentation layer (views, viewmodels, delegates) — no domain, application, or infrastructure modifications are needed.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0
**Storage**: QSettings (INI format) for UI preferences; no SQLite schema changes
**Testing**: pytest + pytest-qt + pytest-asyncio
**Target Platform**: Windows (primary), cross-platform via PySide6
**Project Type**: Desktop application (PySide6 GUI)
**Performance Goals**: All new visual components respond in <100ms; tooltip appears after 300ms (by design)
**Constraints**: Minimum resolution 1024x600; WCAG AA contrast (4.5:1)
**Scale/Scope**: ~500 stories max; 9 user stories across 3 priority levels

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | All changes in Presentation layer only. No cross-layer violations. |
| II. DDD | ✅ PASS | No domain entity changes. BlockingState is a presentation-level enum. |
| III. Repository Pattern | ✅ PASS | No repository changes. |
| IV. Dependency Injection | ✅ PASS | New components receive dependencies via constructor (container). |
| V. SQLite | ✅ PASS | No schema changes. QSettings is for UI preferences, not domain config. |
| VI. Packaging | ✅ PASS | No packaging changes. Version read via importlib.metadata. |
| VII. Directory Structure | ✅ PASS | New files in presentation/views/ and presentation/delegates/. |
| VIII. Async | ✅ PASS | Cancellation uses asyncio.Task.cancel() with qasync. |
| IX. Simplicidade | ✅ PASS | Each feature is self-contained and minimal. |
| X. Type Hints | ✅ PASS | All new code will have type hints. |
| XI. Docstrings | ✅ PASS | All public classes/methods will have docstrings. |
| XII. Imports | ✅ PASS | isort organization maintained. |
| XIII. Nomenclatura | ✅ PASS | PascalCase classes, snake_case methods. |
| XIV. Testes | ✅ PASS | Unit tests for ViewModels, pytest-qt for views. |
| XV. Idioma | ✅ PASS | Code in English, docs in Portuguese, messages in Portuguese. |
| XVI. Tratamento Erros | ✅ PASS | Cancellation errors handled gracefully, no crashes. |
| XVII. Logging | ✅ PASS | New operations will log INFO/DEBUG appropriately. |
| XVIII. Gestão Config | ⚠️ NOTE | QSettings for UI preferences complements (not replaces) domain Configuration entity. See research.md R-004 for justification. |
| XIX. UI/UX (MVVM) | ✅ PASS | New logic in ViewModels, visuals in Views/Delegates. |
| XX. Validação Entrada | ✅ PASS | QSettings values validated on load with range checks. |
| XXI. CI/CD | ✅ PASS | All code passes black, isort, mypy, pytest. |

**Gate Result**: ✅ PASS (Principle XVIII noted — QSettings is for UI preferences, domain Configuration entity unchanged).

### Post-Phase 1 Re-check

| Principle | Status | Notes |
|-----------|--------|-------|
| XVIII. Gestão Config | ✅ PASS | Confirmed: QSettings stores UI preferences only (last-used allocation params). Domain `Configuration` entity and `ConfigurationRepository` remain authoritative. No duplication of responsibility. |

**Gate Result**: ✅ PASS

## Project Structure

### Documentation (this feature)

```text
specs/022-polimento-ux-avancado/
├── plan.md              # This file
├── research.md          # Phase 0 output — 8 research items
├── data-model.md        # Phase 1 output — derived models
├── quickstart.md        # Phase 1 output — implementation guide
├── contracts/
│   └── ui-contracts.md  # Phase 1 output — 7 UI contracts
└── tasks.md             # Phase 2 output (NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
src/backlog_manager/
├── presentation/
│   ├── views/
│   │   ├── main_window.py          # MODIFY: wave separators, responsive resize, about menu, cancellation wiring
│   │   ├── status_bar.py           # MODIFY: add SpBreakdownLabel
│   │   ├── config_dialog.py        # MODIFY: minor (ViewModel handles persistence)
│   │   ├── progress_dialog.py      # MODIFY: add cancel button with 2s delay
│   │   ├── rich_tooltip.py         # NEW: hover mini-card widget
│   │   └── about_dialog.py         # NEW: About dialog
│   ├── viewmodels/
│   │   ├── status_bar_viewmodel.py # MODIFY: add SP breakdown computation
│   │   ├── story_table_model.py    # MODIFY: add blocking state roles, status map
│   │   └── config_dialog_viewmodel.py # MODIFY: add QSettings load/save
│   └── delegates/
│       └── dependency_indicator_delegate.py # NEW: red/green/none blocking delegate
tests/
├── unit/
│   └── presentation/
│       └── viewmodels/             # New tests for SP breakdown, blocking state, config persistence
└── e2e/
    └── test_ep022_*.py             # New pytest-qt tests for visual components
```

**Structure Decision**: Existing single-project src layout maintained. New files follow established patterns in presentation/views/, presentation/delegates/, and tests/.

## Complexity Tracking

No constitution violations requiring justification. All changes are within prescribed patterns.
