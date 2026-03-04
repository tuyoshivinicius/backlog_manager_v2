# Quickstart: Excel Import/Export GUI Integration

**Feature**: EP-012 Excel GUI Integration
**Date**: 2026-03-04

## Prerequisites

- Python 3.11+
- EP-009 Excel Integration completed (ExcelViewModel, use cases, DTOs)
- Development environment set up with Poetry

## Setup

\`\`\`bash
# Clone and install
cd backlog_manager_v2
poetry install

# Run tests to verify base functionality
poetry run pytest tests/unit/presentation/viewmodels/test_excel_viewmodel.py -v
\`\`\`

## Implementation Steps

### Step 1: Add Toolbar Actions to MainWindow

File: \`src/backlog_manager/presentation/views/main_window.py\`

\`\`\`python
# In _setup_toolbar method, after Features action:

# Excel group separator
toolbar.addSeparator()

# Import action
self._action_import_excel = QAction("Importar Excel", self)
self._action_import_excel.setShortcut(QKeySequence("Ctrl+I"))
self._action_import_excel.setToolTip("Importar dados de arquivo Excel (Ctrl+I)")
self._action_import_excel.triggered.connect(self._on_import_excel_clicked)
toolbar.addAction(self._action_import_excel)

# Export action
self._action_export_excel = QAction("Exportar Excel", self)
self._action_export_excel.setShortcut(QKeySequence("Ctrl+E"))
self._action_export_excel.setToolTip("Exportar dados para arquivo Excel (Ctrl+E)")
self._action_export_excel.triggered.connect(self._on_export_excel_clicked)
toolbar.addAction(self._action_export_excel)
\`\`\`

### Step 2: Connect ExcelViewModel Signals

\`\`\`python
# In _connect_signals method:

excel_vm = self._container.excel_viewmodel
excel_vm.import_completed.connect(self._on_import_completed)
excel_vm.import_error.connect(self._on_import_error)
excel_vm.export_completed.connect(self._on_export_completed)
excel_vm.export_error.connect(self._on_export_error)
\`\`\`

### Step 3: Implement Import Handler

\`\`\`python
@Slot()
def _on_import_excel_clicked(self) -> None:
    file_path, _ = QFileDialog.getOpenFileName(
        self,
        "Importar Excel",
        "",
        "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)"
    )
    if file_path:
        self._start_excel_operation("Importando dados do Excel...")
        QTimer.singleShot(0, lambda: asyncio.create_task(
            self._container.excel_viewmodel.import_from_file(Path(file_path))
        ))
\`\`\`

### Step 4: Implement Export Handler

\`\`\`python
@Slot()
def _on_export_excel_clicked(self) -> None:
    file_path, _ = QFileDialog.getSaveFileName(
        self,
        "Exportar Excel",
        "backlog_export.xlsx",
        "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)"
    )
    if file_path:
        # Check if file exists for overwrite confirmation
        if Path(file_path).exists():
            reply = QMessageBox.question(
                self,
                "Confirmar Sobrescrita",
                f"O arquivo {file_path} ja existe. Deseja sobrescrever?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._start_excel_operation("Exportando dados para Excel...")
        QTimer.singleShot(0, lambda: asyncio.create_task(
            self._container.excel_viewmodel.export_to_file(Path(file_path))
        ))
\`\`\`

### Step 5: Implement Progress Dialog Helper

\`\`\`python
def _start_excel_operation(self, message: str) -> None:
    self._excel_operation_in_progress = True
    self._action_import_excel.setEnabled(False)
    self._action_export_excel.setEnabled(False)
    self.setCursor(Qt.CursorShape.WaitCursor)

    self._progress_dialog = QProgressDialog(message, None, 0, 0, self)
    self._progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
    self._progress_dialog.setMinimumDuration(0)
    self._progress_dialog.show()

def _end_excel_operation(self) -> None:
    self._excel_operation_in_progress = False
    self._action_import_excel.setEnabled(True)
    self._action_export_excel.setEnabled(True)
    self.unsetCursor()

    if self._progress_dialog:
        self._progress_dialog.close()
        self._progress_dialog = None
\`\`\`

### Step 6: Implement Signal Handlers

\`\`\`python
@Slot(object)
def _on_import_completed(self, result) -> None:
    self._end_excel_operation()
    msg = f"Importacao concluida!\n\n{result.stories_imported} historias importadas\n{result.features_created} features criadas\n{result.developers_created} desenvolvedores criados"
    if result.warnings:
        msg += f"\n{len(result.warnings)} avisos"
    QMessageBox.information(self, "Importacao", msg)
    QTimer.singleShot(0, lambda: asyncio.create_task(self._viewmodel.load_stories()))

@Slot(str)
def _on_import_error(self, error: str) -> None:
    self._end_excel_operation()
    QMessageBox.critical(self, "Erro na Importacao", error)

@Slot(object)
def _on_export_completed(self, result) -> None:
    self._end_excel_operation()
    msg = f"Exportacao concluida!\n\n{result.stories_exported} historias\n{result.features_exported} features\n{result.developers_exported} desenvolvedores\n\nArquivo: {result.file_path}"
    QMessageBox.information(self, "Exportacao", msg)

@Slot(str)
def _on_export_error(self, error: str) -> None:
    self._end_excel_operation()
    QMessageBox.critical(self, "Erro na Exportacao", error)
\`\`\`

## Testing

\`\`\`bash
# Run unit tests
poetry run pytest tests/unit/presentation/viewmodels/test_excel_viewmodel.py -v

# Run integration tests (when created)
poetry run pytest tests/integration/presentation/views/test_main_window_excel.py -v

# Run all tests
poetry run pytest -v
\`\`\`

## Manual Testing

1. Launch application: \`poetry run python -m backlog_manager\`
2. Verify toolbar has "Importar Excel" and "Exportar Excel" buttons
3. Press Ctrl+I - file dialog should open
4. Press Ctrl+E - save dialog should open
5. Import a valid .xlsx file - progress dialog, then success message
6. Export to .xlsx - progress dialog, then success message
7. Try importing invalid file - error message should appear
