# Research: Excel Import/Export GUI Integration

**Feature**: EP-012 Excel GUI Integration
**Date**: 2026-03-04

## Research Tasks Completed

Since the technical context has no "NEEDS CLARIFICATION" items (the technology stack is well-defined from EP-009 and the existing codebase), research focused on best practices for the specific UI components.

---

## 1. PySide6 QProgressDialog with Async Operations

### Decision
Use QProgressDialog in indeterminate mode (range 0,0) with modal behavior. No cancel button (operations run to completion).

### Rationale
- **Modal behavior**: Prevents user interaction with main window during I/O operations, avoiding data corruption
- **Indeterminate mode**: The Excel operations already emit progress signals (0-100%), but for simplicity, indeterminate mode provides visual feedback without complex progress tracking
- **No cancel**: Per spec edge case, "Operation continues; dialog can be minimized but not cancelled" - simplifies implementation and avoids partial data states

### Alternatives Considered
1. **Progress bar with percentage**: More complex, requires precise progress tracking (already implemented in ExcelViewModel.progress_updated signal). Rejected for MVP; can be added later.
2. **Cancellation support**: Requires asyncio.TaskGroup and proper cleanup. Rejected per spec - cancellation not required.

### Implementation Pattern
```python
# Show progress dialog during async operation
progress = QProgressDialog("Importando dados do Excel...", None, 0, 0, self)
progress.setWindowModality(Qt.WindowModality.ApplicationModal)
progress.setMinimumDuration(0)  # Show immediately
progress.show()
# ... perform async operation via QTimer.singleShot + asyncio.create_task
# ... hide dialog in signal handler
progress.close()
```

---

## 2. PySide6 QFileDialog Patterns

### Decision
Use static methods `QFileDialog.getOpenFileName` and `QFileDialog.getSaveFileName` with Excel filter.

### Rationale
- **Static methods**: Simpler than creating dialog instances; standard pattern in PySide6
- **Native dialogs**: Static methods use native OS file dialogs by default, providing familiar UX
- **Filter syntax**: Standard Qt filter format `"Arquivos Excel (*.xlsx)"` matches spec FR-020/FR-021

### Alternatives Considered
1. **QFileDialog instance with setOption**: More control but unnecessary complexity for this use case
2. **Drag-and-drop import**: Explicitly out of scope per spec

### Implementation Pattern
```python
# Import dialog
file_path, _ = QFileDialog.getOpenFileName(
    self,
    "Importar Excel",
    "",
    "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)"
)

# Export dialog with default filename
file_path, _ = QFileDialog.getSaveFileName(
    self,
    "Exportar Excel",
    "backlog_export.xlsx",  # Default filename per FR-022
    "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)"
)
```

---

## 3. pytest-qt Testing Patterns

### Decision
Use `unittest.mock.patch` to mock QFileDialog and QMessageBox. Use existing `mock_asyncio_create_task` fixture from conftest.py.

### Rationale
- **Consistent with codebase**: Tests in `tests/integration/presentation/views/` already use this pattern
- **No actual file dialogs**: Mocking prevents interactive dialogs during CI
- **Existing fixture**: `mock_asyncio_create_task` already handles async testing

### Alternatives Considered
1. **qtbot.waitSignal for async operations**: Good for signal testing but not needed for dialog tests
2. **QTest.mouseClick simulation**: Too low-level; mocking is cleaner

### Implementation Pattern
```python
from unittest.mock import patch, MagicMock

def test_import_button_opens_file_dialog(main_window, qtbot):
    with patch("PySide6.QtWidgets.QFileDialog.getOpenFileName") as mock_dialog:
        mock_dialog.return_value = ("", "")  # User cancelled
        main_window._action_import_excel.trigger()
        mock_dialog.assert_called_once()
        assert "xlsx" in str(mock_dialog.call_args)
```

---

## 4. Existing Codebase Patterns

### Decision
Follow existing patterns from MainWindow for toolbar actions and from StoryDialog for async operation handling.

### Rationale
Consistency with existing codebase ensures maintainability and follows Constitution principle IX (Simplicidade).

### Key Patterns Found

**Toolbar Action Pattern (MainWindow lines 124-184)**:
```python
self._action_import_excel = QAction("Importar Excel", self)
self._action_import_excel.setShortcut(QKeySequence("Ctrl+I"))
self._action_import_excel.setToolTip("Importar dados de arquivo Excel (Ctrl+I)")
self._action_import_excel.triggered.connect(self._on_import_excel_clicked)
toolbar.addAction(self._action_import_excel)
```

**Async Operation Pattern (MainWindow lines 337-384)**:
```python
@Slot()
def _on_action(self) -> None:
    QTimer.singleShot(0, lambda: asyncio.create_task(self._async_method()))
```

**ViewModel Signal Connection (MainWindow lines 260-277)**:
```python
excel_vm = self._container.excel_viewmodel
excel_vm.import_completed.connect(self._on_import_completed)
excel_vm.import_error.connect(self._on_import_error)
excel_vm.export_completed.connect(self._on_export_completed)
excel_vm.export_error.connect(self._on_export_error)
```

---

## Summary

| Topic | Decision | Key File Reference |
|-------|----------|-------------------|
| Progress Dialog | Indeterminate modal, no cancel | MainWindow + QProgressDialog |
| File Dialogs | Static methods with Excel filter | QFileDialog |
| Testing | Mock dialogs via patch() | conftest.py fixture pattern |
| Async Pattern | QTimer.singleShot + asyncio.create_task | MainWindow:337-384 |
| Signal Pattern | Connect to ExcelViewModel signals | MainWindow:260-277 |
| Toolbar Pattern | QAction with shortcuts | MainWindow:124-184 |

All NEEDS CLARIFICATION items resolved. Ready for Phase 1 design.
