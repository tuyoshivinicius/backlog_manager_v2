# Data Model: Excel Import/Export GUI Integration

**Feature**: EP-012 Excel GUI Integration
**Date**: 2026-03-04

## Overview

This feature adds UI components to MainWindow for Excel import/export. No new domain entities or DTOs are required - all data structures exist from EP-009. This document defines the UI state model and event flows.

---

## Existing Data Structures (from EP-009)

### ImportExcelOutputDTO
\`\`\`python
@dataclass
class ImportExcelOutputDTO:
    stories_imported: int
    features_created: int
    developers_created: int
    warnings: list[str]
    errors: list[str]
\`\`\`

### ExportExcelOutputDTO
\`\`\`python
@dataclass
class ExportExcelOutputDTO:
    stories_exported: int
    features_exported: int
    developers_exported: int
    file_path: Path
\`\`\`

### ExcelViewModel Signals
\`\`\`python
# Already defined in excel_viewmodel.py
import_started = Signal()
import_completed = Signal(object)  # ImportExcelOutputDTO
import_error = Signal(str)
export_started = Signal()
export_completed = Signal(object)  # ExportExcelOutputDTO
export_error = Signal(str)
progress_updated = Signal(int)  # 0-100
\`\`\`

---

## UI State Model

### MainWindow Excel State

| State Variable | Type | Default | Description |
|----------------|------|---------|-------------|
| _excel_operation_in_progress | bool | False | True when import or export is running |
| _progress_dialog | QProgressDialog or None | None | Reference to active progress dialog |

### State Transitions

\`\`\`
IDLE --> (import clicked) --> FILE_DIALOG_IMPORT --> (cancel) --> IDLE
                                                 --> (file selected) --> IMPORTING --> SUCCESS --> RESULT_DIALOG --> refresh table --> IDLE
                                                                                   --> ERROR --> ERROR_DIALOG --> IDLE

IDLE --> (export clicked) --> FILE_DIALOG_EXPORT --> (cancel) --> IDLE
                                                 --> (file selected) --> EXPORTING --> SUCCESS --> RESULT_DIALOG --> IDLE
                                                                                   --> ERROR --> ERROR_DIALOG --> IDLE
\`\`\`

---

## UI Components

### Toolbar Actions

| Action | Text | Shortcut | Tooltip |
|--------|------|----------|---------|
| _action_import_excel | Importar Excel | Ctrl+I | Importar dados de arquivo Excel (Ctrl+I) |
| _action_export_excel | Exportar Excel | Ctrl+E | Exportar dados para arquivo Excel (Ctrl+E) |

### Dialogs

| Dialog | Type | Purpose | Modality |
|--------|------|---------|----------|
| Import file dialog | QFileDialog.getOpenFileName | Select .xlsx file to import | Application modal |
| Export file dialog | QFileDialog.getSaveFileName | Select destination for export | Application modal |
| Progress dialog | QProgressDialog | Show operation in progress | Application modal |
| Result dialog | QMessageBox.information | Show import/export summary | Application modal |
| Error dialog | QMessageBox.critical | Show error message | Application modal |
| Overwrite confirm | QMessageBox.question | Confirm file overwrite | Application modal |

---

## Validation Rules

### Import
- File path must be non-empty (user selected a file)
- File must have .xlsx extension (enforced by dialog filter)
- File content validation handled by ExcelViewModel/UseCase

### Export
- File path must be non-empty (user selected a destination)
- If file exists, user must confirm overwrite
- Write permission validation handled by ExcelViewModel/UseCase

---

## Message Templates (Portuguese)

### Success Messages

**Import Success**: Importacao concluida! {stories_imported} historias importadas, {features_created} features criadas, {developers_created} desenvolvedores criados, {warnings_count} avisos

**Export Success**: Exportacao concluida! {stories_exported} historias, {features_exported} features, {developers_exported} desenvolvedores exportados para {file_path}

### Progress Messages
- Import: Importando dados do Excel...
- Export: Exportando dados para Excel...

---

## Dependencies

- **ExcelViewModel**: container.excel_viewmodel (existing from EP-009)
- **MainWindowViewModel**: viewmodel.loading property for button state
- **DIContainer**: Access to ExcelViewModel
