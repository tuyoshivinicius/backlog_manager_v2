# Research: EP-023 — Novo Planejamento (Reset de Cronograma e Alocacao)

## R-001: Story Entity Field Modification Pattern

**Decision**: Use `object.__setattr__()` to set calculated fields to `None`

**Rationale**: The Story entity is a dataclass. The codebase already uses `object.__setattr__()` extensively in `calculate_schedule.py` and `execute_allocation.py` to modify fields like `start_date`, `end_date`, `duration`, and `developer_id`. This is the established mutation pattern.

**Alternatives considered**:
- Creating new Story instances with cleared fields — rejected because Story has many fields and the existing codebase uses setattr consistently
- Adding a `clear_planning_data()` method to Story entity — rejected per YAGNI, the use case handles this logic

## R-002: Atomicity via Unit of Work

**Decision**: Use existing `SQLiteUnitOfWork` context manager for atomic reset

**Rationale**: The `SQLiteUnitOfWork` already provides automatic commit on success and rollback on exception via `__aexit__`. All story updates within a single `async with` block are atomic. This is identical to how `calculate_schedule.py` and `execute_allocation.py` persist their changes.

**Alternatives considered**:
- Manual transaction management — rejected because UoW already handles this
- Batch SQL UPDATE statement — rejected because it bypasses the repository pattern and violates Constitution Principle III

## R-003: Preview/Count Before Reset

**Decision**: Separate `CountAffectedStoriesUseCase` for preview, distinct from `ResetPlanningUseCase`

**Rationale**: The preview must count affected stories WITHOUT modifying any data. Separating into its own use case follows SRP and allows the dialog to display accurate counts before the user confirms. The count use case opens its own UoW (read-only) while the reset use case opens a separate UoW (write).

**Alternatives considered**:
- Single use case with a `dry_run` flag — rejected because it couples two responsibilities
- Count in the ViewModel without a use case — rejected because it would put business logic in the presentation layer

## R-004: Icon Selection

**Decision**: Create `arrows-down-up.svg` from Phosphor Icons set

**Rationale**: The spec designates `arrows-down-up.svg` which does not currently exist in `src/backlog_manager/assets/icons/`. All existing icons are from the Phosphor Icons set (confirmed by checking arrow-up.svg, arrow-down.svg patterns). The arrows-down-up icon from Phosphor visually suggests "reset/reorder" which aligns with "new planning".

**Alternatives considered**:
- Reusing existing `shuffle.svg` — rejected because it's already used for allocation
- Using a custom icon — rejected for consistency with the Phosphor set

## R-005: Button Disabled State Tracking

**Decision**: Use `CountAffectedStoriesUseCase` result to determine if button should be enabled (planning data exists)

**Rationale**: After loading stories and after schedule/allocation operations, the main window needs to know if any stories have planning data. The simplest approach is to call `preview()` from the ViewModel during `_update_actions_state()` events. However, since this is async, an alternative is to track `has_planning_data` as a flag that updates when stories are loaded or after schedule/allocation/reset operations.

**Decision refined**: Track `_has_planning_data: bool` in MainWindow, updated when:
1. Stories are loaded (check if any story has calculated fields)
2. After schedule/allocation completes (set to True)
3. After reset completes (set to False)

This avoids an async call in the synchronous `_update_actions_state()`.

## R-006: Status Bar Temporary Message

**Decision**: Use `QTimer.singleShot(5000, ...)` to clear the temporary message after 5 seconds

**Rationale**: The status bar's `StatsLabel` can be temporarily overridden with the reset message, then restored after 5 seconds via a single-shot timer. This follows standard Qt patterns for temporary status messages.

**Alternatives considered**:
- Using `QStatusBar.showMessage(msg, timeout)` — the app uses a custom status bar, not QMainWindow's built-in one
- Using a separate toast/notification widget — over-engineering for this use case
