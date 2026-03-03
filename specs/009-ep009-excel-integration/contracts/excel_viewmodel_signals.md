# Contract: ExcelViewModel Signals

**Location**: `src/backlog_manager/presentation/viewmodels/excel_viewmodel.py`
**Type**: Qt Signals (Observer Pattern)
**Layer**: Presentation (ViewModels)

## Overview

ExcelViewModel exposes Qt Signals for UI components to react to import/export operations. This contract defines the signals emitted and their payloads, enabling loose coupling between ViewModel and Views.

## Signal Definitions

```python
from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.excel.import_excel_dto import ImportExcelOutputDTO
from backlog_manager.application.dto.excel.export_excel_dto import ExportExcelOutputDTO


class ExcelViewModel(QObject):
    """ViewModel para operacoes de import/export Excel.

    Signals:
        import_started: Emitido quando import inicia.
        import_completed: Emitido quando import termina com sucesso.
        import_error: Emitido quando import falha.
        export_started: Emitido quando export inicia.
        export_completed: Emitido quando export termina com sucesso.
        export_error: Emitido quando export falha.
        progress_updated: Emitido durante operacao com percentual (0-100).
    """

    # Import signals
    import_started = Signal()
    import_completed = Signal(object)  # ImportExcelOutputDTO
    import_error = Signal(str)

    # Export signals
    export_started = Signal()
    export_completed = Signal(object)  # ExportExcelOutputDTO
    export_error = Signal(str)

    # Progress signal
    progress_updated = Signal(int)  # 0-100 percentage
```

## Signal Contracts

### import_started

| Aspect | Specification |
|--------|---------------|
| **Payload** | None |
| **Emitted When** | Import operation begins |
| **Expected UI Response** | Show progress dialog, disable buttons |

### import_completed

| Aspect | Specification |
|--------|---------------|
| **Payload** | `ImportExcelOutputDTO` |
| **Emitted When** | Import finishes successfully (may have warnings) |
| **Expected UI Response** | Close progress, show summary, refresh table |

**Payload Structure**:
```python
class ImportExcelOutputDTO:
    stories_imported: int
    features_created: int
    warnings: list[str]
    errors: list[str]  # Empty for success
```

### import_error

| Aspect | Specification |
|--------|---------------|
| **Payload** | `str` - Error message (Portuguese) |
| **Emitted When** | Import fails with critical error |
| **Expected UI Response** | Close progress, show error QMessageBox |

**Example Messages**:
- "Coluna obrigatoria 'Nome' nao encontrada na linha 1"
- "Ciclo de dependencia detectado: A -> B -> A"
- "Arquivo invalido ou corrompido"

### export_started

| Aspect | Specification |
|--------|---------------|
| **Payload** | None |
| **Emitted When** | Export operation begins |
| **Expected UI Response** | Show wait cursor, disable buttons |

### export_completed

| Aspect | Specification |
|--------|---------------|
| **Payload** | `ExportExcelOutputDTO` |
| **Emitted When** | Export finishes successfully |
| **Expected UI Response** | Show success message with counts |

**Payload Structure**:
```python
class ExportExcelOutputDTO:
    file_path: Path
    stories_exported: int
    developers_exported: int
    features_exported: int
```

### export_error

| Aspect | Specification |
|--------|---------------|
| **Payload** | `str` - Error message (Portuguese) |
| **Emitted When** | Export fails |
| **Expected UI Response** | Show error QMessageBox |

**Example Messages**:
- "Sem permissao para escrever arquivo"
- "Erro ao criar arquivo Excel"

### progress_updated

| Aspect | Specification |
|--------|---------------|
| **Payload** | `int` - Percentage 0-100 |
| **Emitted When** | During import (per row processed) |
| **Expected UI Response** | Update QProgressDialog value |

**Emission Frequency**:
- Import: Once per row processed (enables granular progress)
- Export: At 0% (start), 50% (after data fetch), 100% (after write complete)

## Method Contracts

### import_from_file

```python
async def import_from_file(self, file_path: Path) -> None:
    """Importa dados de arquivo Excel.

    Emite signals durante operacao:
    1. import_started
    2. progress_updated (0-100%)
    3. import_completed OR import_error

    Args:
        file_path: Caminho para arquivo .xlsx.
    """
```

**Signal Sequence (Success)**:
```
import_started
  |
progress_updated(0)
progress_updated(10)
  ...
progress_updated(100)
  |
import_completed(dto)
```

**Signal Sequence (Error)**:
```
import_started
  |
progress_updated(0)
  ...
  |
import_error("mensagem de erro")
```

### export_to_file

```python
async def export_to_file(self, file_path: Path) -> None:
    """Exporta dados para arquivo Excel.

    Emite signals durante operacao:
    1. export_started
    2. progress_updated (0, 100)
    3. export_completed OR export_error

    Args:
        file_path: Caminho de destino .xlsx.
    """
```

**Signal Sequence (Success)**:
```
export_started
  |
progress_updated(0)
  |
progress_updated(100)
  |
export_completed(dto)
```

## UI Integration Example

```python
class MainWindow(QMainWindow):
    def __init__(self, excel_viewmodel: ExcelViewModel):
        super().__init__()
        self._excel_vm = excel_viewmodel
        self._progress_dialog: QProgressDialog | None = None

        # Connect signals
        self._excel_vm.import_started.connect(self._on_import_started)
        self._excel_vm.import_completed.connect(self._on_import_completed)
        self._excel_vm.import_error.connect(self._on_import_error)
        self._excel_vm.progress_updated.connect(self._on_progress_updated)

    def _on_import_started(self) -> None:
        self._progress_dialog = QProgressDialog(
            "Importando...", "Cancelar", 0, 100, self
        )
        self._progress_dialog.setWindowModality(Qt.WindowModal)
        self._progress_dialog.show()
        self._import_btn.setEnabled(False)
        self._export_btn.setEnabled(False)

    def _on_progress_updated(self, percent: int) -> None:
        if self._progress_dialog:
            self._progress_dialog.setValue(percent)

    def _on_import_completed(self, dto: ImportExcelOutputDTO) -> None:
        if self._progress_dialog:
            self._progress_dialog.close()
        self._import_btn.setEnabled(True)
        self._export_btn.setEnabled(True)

        msg = f"{dto.stories_imported} historias importadas"
        if dto.warnings:
            msg += f"\n{len(dto.warnings)} avisos"
        QMessageBox.information(self, "Import Concluido", msg)

        # Refresh table
        asyncio.create_task(self._main_vm.load_stories())

    def _on_import_error(self, error_msg: str) -> None:
        if self._progress_dialog:
            self._progress_dialog.close()
        self._import_btn.setEnabled(True)
        self._export_btn.setEnabled(True)
        QMessageBox.critical(self, "Erro no Import", error_msg)
```

## Error Handling Contract

The ViewModel MUST NOT propagate exceptions to Views. All exceptions are caught and converted to error signals:

| Exception Type | Signal | Message Source |
|----------------|--------|----------------|
| `ExcelFileNotFoundException` | `import_error` | Exception message |
| `ExcelFileCorruptedException` | `import_error` | Exception message |
| `ExcelMissingHeaderException` | `import_error` | Exception message |
| `ExcelCycleDetectedException` | `import_error` | Exception message |
| `ExcelPermissionException` | `import_error`/`export_error` | Exception message |
| `Exception` (generic) | `import_error`/`export_error` | "Erro inesperado" |
