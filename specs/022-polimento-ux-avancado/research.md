# Research: EP-022 — Polimento e UX Avançado

**Date**: 2026-03-30
**Status**: Complete

## R-001: Wave Grouping Strategy in QTableView

**Decision**: Implement wave separators using a custom delegate approach that detects wave boundaries in `StoryTableModel.data()` and paints separator rows via a custom `WaveSeparatorDelegate` or by overriding `StoryTableView.paintEvent()` to draw separator bands between wave groups.

**Rationale**: The stories are already sorted by wave (priority-based). The `FilterProxyModel` already sits between the source model and the view. Drawing separators as visual overlays (via delegate or view painting) avoids modifying the model's row count (which would break index mapping with `FilterProxyModel`). A `QStyledItemDelegate` approach that checks "is this row's wave different from the previous row's wave?" and draws a separator band above the row is the cleanest approach.

**Alternatives considered**:
- **Inserting separator rows into the model**: Rejected — would break `FilterProxyModel` index mapping, complicate row-to-story mapping, and require sentinel values in `StoryOutputDTO`.
- **Using `QTreeView` with grouping**: Rejected — would require rewriting the entire table infrastructure and break existing delegates (StatusBadge, Monospace).
- **Using `QHeaderView` sections**: Rejected — headers are for columns, not row groups.
sim
**Implementation approach**: Override `StoryTableView.paintEvent()` to detect wave boundaries after the default paint, and draw separator bands. Store a `_wave_separators_visible` flag that is True only when sorted by default order (wave column). When sort changes to another column, set flag to False.

---

## R-002: Rich Tooltip Implementation

**Decision**: Use a custom `QWidget` popup (not Qt's built-in tooltip system) positioned near the cursor, shown after a 300ms `QTimer` delay on `mouseMoveEvent`.

**Rationale**: Qt's built-in `QToolTip` is plain text or simple HTML. For a rich mini-card with colored status badges, structured layout, and precise positioning, a custom popup widget provides full control. The popup is a frameless `QWidget` with `Qt.WindowType.ToolTip` flag.

**Alternatives considered**:
- **QToolTip with HTML**: Rejected — limited styling, no custom widgets, poor control over positioning and timing.
- **QWhatsThis**: Rejected — different UX pattern (click-based, not hover).
- **Custom QDialog**: Rejected — dialogs have window decorations and focus behavior inappropriate for tooltips.

**Implementation approach**: Create `RichTooltipWidget(QWidget)` in `presentation/views/`. On `StoryTableView.mouseMoveEvent`, start/restart a 300ms `QTimer`. On timer timeout, create/update the tooltip widget at cursor position. On `leaveEvent`, hide immediately. Track current hovered row to avoid re-creating on same row.

---

## R-003: Blocking Indicator in Dependencies Column

**Decision**: Extend the existing `StoryTableModel.data()` to provide a custom `UserRole+1` (or `DecorationRole`) that returns the blocking state, and use a new `DependencyBlockingDelegate` to render the colored circle icon.

**Rationale**: The model already has access to the full story list via `_stories`. To determine blocking state, we need to check if each dependency_id maps to a story with status != CONCLUIDO. This lookup can be done in the model's `data()` method using a dictionary lookup (`{story.id: story.status}`).

**Alternatives considered**:
- **Computing blocking state in the ViewModel**: Rejected — the model already holds all stories; adding a separate computation layer adds unnecessary complexity.
- **Using `DecorationRole` with `QIcon`**: Viable but `QIcon` with SVG/pixmap is heavier than delegate painting. A delegate with `QPainter.drawEllipse()` is simpler and matches the existing delegate pattern (StatusBadge).

**Implementation approach**: Add `_story_status_map: dict[str, str]` to `StoryTableModel`, updated when stories change. In `data()` for column 8 (Dependencias) with a custom role, return blocking state enum. Create `DependencyIndicatorDelegate` that paints red/green circle + text.

---

## R-004: QSettings for Config Persistence

**Decision**: Use `QSettings` with INI format (`QSettings.Format.IniFormat`) in the `ConfigDialogViewModel` to persist velocity, start_date, and max_idle_days.

**Rationale**: The spec explicitly requires QSettings. The app already sets organization/app names in `app.py` (`"BacklogManager"` / `"Backlog Manager"`), which QSettings uses for storage location. INI format is portable (spec assumption). This complements the in-memory approach (ADR-007) by adding a persistence layer on top.

**Alternatives considered**:
- **Persisting in SQLite Configuration table**: Constitution Principle XVIII says config should be in SQLite. However, the spec explicitly asks for QSettings and the values are UI-level preferences (velocity, start_date, max_idle_days for the allocation dialog), not domain configuration. QSettings is appropriate for UI preferences.
- **JSON file**: Rejected — QSettings is built into Qt and already configured via the app's organization/name.

**Implementation approach**: In `ConfigDialogViewModel.__init__`, load values from QSettings with validation (range checks). In `save()`, write to QSettings after validation. Use group "allocation" with keys "velocity", "start_date", "max_idle_days".

**Constitution note**: Principle XVIII prescribes SQLite for configuration. However, these are UI-level preferences (how the allocation dialog remembers last-used values), not domain configuration. The domain `Configuration` entity and `ConfigurationRepository` remain authoritative for domain logic. QSettings serves as a convenience layer for the presentation layer, consistent with Principle XIX (UI/UX patterns).

---

## R-005: Cancellation of Long-Running Operations

**Decision**: Use `asyncio.CancelledError` with safe cancellation points in the async operation flow. Add a `QPushButton("Cancelar")` to `ProgressDialog` that appears after a 2-second `QTimer`, and connects to task cancellation.

**Rationale**: The app uses `qasync` + `asyncio.create_task()` for async operations. `asyncio.Task.cancel()` raises `CancelledError` at the next `await` point, providing natural safe cancellation. For import (which uses UnitOfWork transactions), the `CancelledError` will propagate and the UnitOfWork context manager will rollback automatically.

**Alternatives considered**:
- **Threading with stop flag**: Rejected — the app is async-based, not threaded. Mixing would add complexity.
- **Custom cancellation token pattern**: Rejected — `asyncio.CancelledError` is the idiomatic Python approach and works with existing `await` points.

**Implementation approach**:
1. Modify `ProgressDialog` to accept an optional `asyncio.Task` reference. Add cancel button (hidden initially, shown after 2s via QTimer).
2. On cancel click: call `task.cancel()`, catch `CancelledError` in the viewmodel, emit appropriate signal.
3. For import: UnitOfWork rollback handles DB consistency.
4. For export: delete partial file in the `CancelledError` handler.
5. For allocation: restore previous state (reload stories).

---

## R-006: SP Breakdown in Status Bar

**Decision**: Extend `StatusBarViewModel` to compute per-status SP aggregation from the stories list, and add a new `SpBreakdownLabel` widget to the status bar.

**Rationale**: The status bar already has `StatsLabel` showing total count/SP. Adding a separate label for the breakdown keeps components focused. The aggregation is trivial (group by status, sum SP).

**Implementation approach**: Add `update_sp_breakdown(stories)` to `StatusBarViewModel` that computes `{status: total_sp}`. Create `SpBreakdownLabel` that displays "X SP Backlog · Y SP Execucao · ..." with tooltip showing percentages. Connect to `stats_changed` signal.

---

## R-007: About Dialog

**Decision**: Create a simple `AboutDialog(QDialog)` showing app name, version (from `importlib.metadata`), Python version, technology list, and database path.

**Rationale**: Standard pattern for desktop apps. `importlib.metadata.version("backlog-manager")` reads from the installed package; fallback to "dev" on `PackageNotFoundError`.

**Implementation approach**: New `AboutDialog` in `presentation/views/about_dialog.py`. Version via `importlib.metadata.version("backlog-manager")` with try/except fallback. DB path from `container.db_path`. Add "Ajuda > Sobre" menu action in MainWindow.

---

## R-008: Responsive Column Hiding

**Decision**: Override `MainWindow.resizeEvent()` to check window width against 1024px threshold and hide/show columns 4 (Componente), 2 (Onda), 12 (Duracao) on the table view.

**Rationale**: `QTableView.setColumnHidden()` is the standard Qt approach for hiding columns. The resize event fires on every size change, providing real-time responsiveness.

**Implementation approach**: In `MainWindow.resizeEvent()`, check `self.width() < 1024`. If True, hide columns 2, 4, 12 and show an indicator. If False, restore. Track hidden state to avoid redundant operations. The indicator can be a small label in the status bar or a tooltip on the table header.
