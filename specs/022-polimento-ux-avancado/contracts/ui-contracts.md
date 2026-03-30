# UI Contracts: EP-022 — Polimento e UX Avançado

**Date**: 2026-03-30

## Contract 1: SP Breakdown Label

**Component**: `SpBreakdownLabel(QLabel)` in `presentation/views/status_bar.py`

**Display format**: `"{X} SP Backlog · {Y} SP Execucao · {Z} SP Testes · {W} SP Concluido · {V} SP Impedido"`
- Only statuses with SP > 0 are shown (except BACKLOG which always shows)
- Tooltip: `"Backlog: {pct}% · Execucao: {pct}% · Testes: {pct}% · Concluido: {pct}% · Impedido: {pct}%"`

**Signal binding**: `StatusBarViewModel.sp_breakdown_changed → SpBreakdownLabel.update_breakdown()`

---

## Contract 2: Dependency Indicator Delegate

**Component**: `DependencyIndicatorDelegate(QStyledItemDelegate)` in `presentation/delegates/dependency_indicator_delegate.py`

**Visual spec**:
| State | Icon | Color | Text |
|-------|------|-------|------|
| BLOCKED | Filled circle (8px) | Red (#DC3545) | Comma-separated dependency IDs |
| FREE | Filled circle (8px) | Green (#28A745) | Comma-separated dependency IDs |
| NONE | — | — | "—" (em-dash) |

**Data role**: `Qt.ItemDataRole.UserRole + 1` returns `BlockingState` enum value.
**Data role**: `Qt.ItemDataRole.UserRole + 2` returns `list[str]` of dependency IDs.

---

## Contract 3: Wave Separator

**Component**: Visual separator painted in `StoryTableView.paintEvent()` override

**Visual spec**:
- Height: 24px band above the first row of each new wave
- Background: Design system surface color with slight contrast (e.g., `--color-surface-alt`)
- Text: "Onda {N}" or "Sem Onda" for wave=0, left-aligned with 12px padding
- Font: Bold, same family as table
- Visibility: Only when table is in default sort order (by wave/priority)

**Behavior**:
- On sort by another column → separators hidden
- On return to default sort → separators visible
- With active filters → separators shown only between wave groups present in filtered results
- When Onda column hidden by resize → separators still visible

---

## Contract 4: Rich Tooltip Widget

**Component**: `RichTooltipWidget(QWidget)` in `presentation/views/rich_tooltip.py`

**Layout**:
```
┌──────────────────────────────────┐
│ {ID}                    {Status} │  ← Status as colored badge
│ {Nome}                           │
├──────────────────────────────────┤
│ SP: {X}  Feature: {Y}           │
│ Dev: {Z}                         │
│ Dep: {ids}                       │
│ Inicio: {date}  Fim: {date}     │
└──────────────────────────────────┘
```

**Dimensions**: Auto-sized, max-width 350px
**Timing**: Appears after 300ms hover, disappears immediately on mouse leave or row change
**Positioning**: Below cursor with 10px offset; repositioned above if near bottom edge of window
**Window flags**: `Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint`

---

## Contract 5: Progress Dialog with Cancellation

**Component**: Extended `ProgressDialog` in `presentation/views/progress_dialog.py`

**New behavior**:
- Cancel button: hidden initially, shown after 2 seconds via QTimer
- Button text: "Cancelar"
- On click: calls `asyncio.Task.cancel()` on the linked task
- After cancellation: dialog closes, parent shows "Operação cancelada" message

**Interface**:
```python
class ProgressDialog(QDialog):
    cancelled = Signal()  # New signal

    def set_cancellable_task(self, task: asyncio.Task) -> None: ...
    # Cancel button appears after 2s, cancels task on click
```

**Cancelable operations**: allocation, import Excel, export Excel
**Non-cancelable**: schedule calculation

---

## Contract 6: About Dialog

**Component**: `AboutDialog(QDialog)` in `presentation/views/about_dialog.py`

**Content**:
- Application name: "Backlog Manager"
- Version: from `importlib.metadata.version("backlog-manager")`, fallback "dev"
- Python version: from `sys.version`
- Technologies: Python, PySide6, SQLite, Pydantic, qasync
- Database path: from `container.db_path`

**Dimensions**: Fixed size 400x300px
**Trigger**: Menu Ajuda > Sobre

---

## Contract 7: Responsive Column Management

**Component**: Logic in `MainWindow.resizeEvent()`

**Threshold**: 1024px window width

**Columns hidden when < 1024px**:
| Column Index | Column Name |
|-------------|-------------|
| 2 | Onda |
| 4 | Componente |
| 12 | Duracao |

**Indicator**: Label in status bar: "{N} colunas ocultas" (visible only when columns hidden)

**Restoration**: Columns restored immediately when width >= 1024px, indicator hidden.

---

## ViewModel Signal Additions

### StatusBarViewModel (extended)

```python
class StatusBarViewModel(QObject):
    stats_changed = Signal()        # existing
    warnings_changed = Signal()     # existing
    sp_breakdown_changed = Signal() # NEW

    def update_sp_breakdown(self, stories: list[StoryOutputDTO]) -> None: ...
```

### ProgressDialog (extended)

```python
class ProgressDialog(QDialog):
    cancelled = Signal()  # NEW
```
