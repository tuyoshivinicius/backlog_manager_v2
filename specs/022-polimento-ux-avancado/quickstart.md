# Quickstart: EP-022 — Polimento e UX Avançado

**Date**: 2026-03-30

## Overview

EP-022 adds 8 UX polish features to the Backlog Manager desktop app:
1. SP breakdown by status in status bar (P1)
2. Blocking indicator in dependencies column (P1)
3. Config persistence via QSettings (P1)
4. Wave grouping visual separators (P2)
5. Rich tooltip on table hover (P2)
6. Cancellation of long operations (P2)
7. About dialog (P3)
8. Responsive column hiding (P3)

## Architecture Decisions

- **No schema changes**: All new data is derived from existing `StoryOutputDTO` or persisted via QSettings (outside SQLite).
- **Presentation layer only**: This epic modifies only `presentation/` — views, viewmodels, and delegates. No domain/application/infrastructure changes.
- **MVVM compliance**: New logic in ViewModels, new visuals in Views/Delegates.
- **Constitution compliance**: QSettings for UI preferences complements (not replaces) domain Configuration entity.

## Key Files to Modify

| File | Changes |
|------|---------|
| `presentation/views/status_bar.py` | Add `SpBreakdownLabel` |
| `presentation/viewmodels/status_bar_viewmodel.py` | Add `update_sp_breakdown()`, `sp_breakdown_changed` signal |
| `presentation/viewmodels/story_table_model.py` | Add blocking state roles, story status map |
| `presentation/delegates/dependency_indicator_delegate.py` | **NEW** — red/green circle delegate |
| `presentation/views/main_window.py` | Wire new delegates, wave separators, responsive resize, about menu, cancellation |
| `presentation/viewmodels/config_dialog_viewmodel.py` | Add QSettings load/save |
| `presentation/views/progress_dialog.py` | Add cancel button with 2s delay |
| `presentation/views/rich_tooltip.py` | **NEW** — hover mini-card widget |
| `presentation/views/about_dialog.py` | **NEW** — About dialog |

## Key Files to Create

| File | Purpose |
|------|---------|
| `presentation/delegates/dependency_indicator_delegate.py` | Blocking state delegate |
| `presentation/views/rich_tooltip.py` | Rich tooltip popup widget |
| `presentation/views/about_dialog.py` | About dialog |

## Testing Approach

- **Unit tests**: ViewModel logic (SP breakdown, blocking state, config validation/persistence)
- **Integration tests**: QSettings read/write with validation
- **E2E tests (pytest-qt)**: Visual components (delegates, tooltip, dialogs, responsive behavior)
- No domain or infrastructure tests needed (no changes to those layers)

## Implementation Order

1. P1 features first (SP breakdown → Blocking indicator → Config persistence)
2. P2 features (Wave grouping → Rich tooltip → Cancellation)
3. P3 features (About dialog → Responsive resize)
4. Layout validation at minimum resolution
