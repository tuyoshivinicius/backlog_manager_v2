# Feature Specification: Excel Import/Export GUI Integration

**Feature Branch**: `012-excel-gui-integration`
**Created**: 2026-03-04
**Status**: Draft
**Input**: User description: "implemente a funcionalidade de importar e export excel no GUI"

## Out of Scope

- **Backend Excel logic**: Use cases, services, DTOs, and protocols already implemented in EP-009
- **New Excel file formats**: Only .xlsx is supported (defined in EP-009)
- **Excel editing functionality**: System imports/exports only, no inline editing
- **Batch operations UI**: No queue for multiple import/export operations
- **Drag-and-drop import**: Only file dialog selection is supported

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Export Backlog to Excel via Toolbar (Priority: P1)

As a Scrum Master, I need to export my entire backlog to an Excel file using a toolbar button, so I can share the data with stakeholders or create manual backups without navigating through menus.

**Why this priority**: Export is the most common operation for sharing data with external stakeholders. Users need immediate access to this function for reporting and backup purposes.

**Independent Test**: Can be tested by clicking the "Exportar Excel" button in the toolbar, selecting a destination file, and verifying that the Excel file is created with all backlog data.

**Acceptance Scenarios**:

1. **Given** MainWindow is open with backlog data, **When** I click "Exportar Excel" button in toolbar, **Then** a file save dialog opens with filter for .xlsx files
2. **Given** file save dialog is open, **When** I select a destination and confirm, **Then** a progress indicator appears during export operation
3. **Given** export completes successfully, **When** operation finishes, **Then** a success message displays showing count of exported entities (stories, developers, features)
4. **Given** export destination file already exists, **When** I confirm export, **Then** system shows confirmation dialog before overwriting

---

### User Story 2 - Import Backlog from Excel via Toolbar (Priority: P1)

As a Scrum Master, I need to import backlog data from an Excel file using a toolbar button, so I can migrate data from existing spreadsheets or restore from manual backups.

**Why this priority**: Import is essential for data migration and backup restoration. Together with export, it completes the roundtrip functionality.

**Independent Test**: Can be tested by clicking the "Importar Excel" button, selecting a valid Excel file, and verifying that stories are created in the system.

**Acceptance Scenarios**:

1. **Given** MainWindow is open, **When** I click "Importar Excel" button in toolbar, **Then** a file open dialog appears with filter for .xlsx files
2. **Given** file dialog is open, **When** I select a valid Excel file and confirm, **Then** a progress indicator appears during import operation
3. **Given** import completes with warnings, **When** operation finishes, **Then** a result dialog displays showing count of imported stories and list of warnings
4. **Given** import completes successfully, **When** result dialog is closed, **Then** the story table automatically refreshes to show imported data

---

### User Story 3 - Use Keyboard Shortcuts for Import/Export (Priority: P2)

As a power user, I need to use keyboard shortcuts (Ctrl+I for import, Ctrl+E for export), so I can quickly access import/export functionality without using the mouse.

**Why this priority**: Keyboard shortcuts improve efficiency for frequent users but are not essential for basic functionality. Users can always use toolbar buttons.

**Independent Test**: Can be tested by pressing Ctrl+I and Ctrl+E in MainWindow and verifying that the appropriate file dialogs open.

**Acceptance Scenarios**:

1. **Given** MainWindow has focus, **When** I press Ctrl+I, **Then** the file open dialog for Excel import opens
2. **Given** MainWindow has focus, **When** I press Ctrl+E, **Then** the file save dialog for Excel export opens
3. **Given** an import/export operation is in progress, **When** I press the shortcut again, **Then** nothing happens (prevents duplicate operations)

---

### User Story 4 - Visual Feedback During Operations (Priority: P2)

As a user, I need to see visual feedback during import/export operations, so I know the system is working and approximately how long it will take for large files.

**Why this priority**: Visual feedback improves user experience but operations work without it. More important for large backlog files.

**Independent Test**: Can be tested by importing a file with 100+ stories and observing that a progress dialog appears during the operation.

**Acceptance Scenarios**:

1. **Given** import/export operation starts, **When** operation is in progress, **Then** a progress dialog appears with operation description
2. **Given** operation is in progress, **When** I observe the UI, **Then** toolbar buttons for import/export are disabled to prevent concurrent operations
3. **Given** operation is in progress, **When** I observe the cursor, **Then** it shows wait cursor indicating busy state

---

### User Story 5 - Handle Import Errors Gracefully (Priority: P2)

As a user, I need to see clear error messages when import fails, so I can understand what went wrong and fix the issue.

**Why this priority**: Error handling improves user experience but basic import functionality works without detailed error presentation.

**Independent Test**: Can be tested by attempting to import an Excel file with missing required columns and verifying that a clear error message is displayed.

**Acceptance Scenarios**:

1. **Given** Excel file has missing required columns, **When** I import, **Then** error dialog displays "Coluna obrigatoria '[NAME]' nao encontrada"
2. **Given** Excel file has cycle in dependencies, **When** I import, **Then** error dialog displays cycle path and indicates no data was imported
3. **Given** import fails due to file permissions, **When** operation fails, **Then** error dialog displays clear permission-related message
4. **Given** import completes with some invalid rows, **When** I view result dialog, **Then** I can see which lines were skipped and why

---

### Edge Cases

- What happens when user cancels the file dialog? System returns to normal state without any action.
- What happens when user closes the progress dialog during operation? Operation continues; dialog can be minimized but not cancelled.
- What happens when export fails due to disk full? System displays clear error message about disk space.
- What happens when import file is very large (500+ stories)? Progress dialog shows operation is working; UI remains responsive.
- What happens when system is already loading stories? Import/export buttons are disabled during loading state.

## Requirements *(mandatory)*

### Functional Requirements

#### MainWindow - Toolbar Integration

- **FR-001**: MainWindow MUST add "Importar Excel" action to the toolbar with tooltip "Importar dados de arquivo Excel (Ctrl+I)"
- **FR-002**: MainWindow MUST add "Exportar Excel" action to the toolbar with tooltip "Exportar dados para arquivo Excel (Ctrl+E)"
- **FR-003**: Toolbar MUST display Import/Export buttons after "Features" button and before separator (if any) or at the end of existing actions
- **FR-004**: Import/Export actions MUST be visually grouped with a separator from other toolbar actions

#### MainWindow - Keyboard Shortcuts

- **FR-010**: MainWindow MUST register Ctrl+I shortcut for import operation
- **FR-011**: MainWindow MUST register Ctrl+E shortcut for export operation
- **FR-012**: Shortcuts MUST trigger the same handlers as toolbar button clicks

#### MainWindow - File Dialogs

- **FR-020**: System MUST use QFileDialog.getOpenFileName for import file selection with filter "Arquivos Excel (*.xlsx)"
- **FR-021**: System MUST use QFileDialog.getSaveFileName for export file destination with filter "Arquivos Excel (*.xlsx)"
- **FR-022**: Export dialog MUST default to filename "backlog_export.xlsx" if no filename provided
- **FR-023**: If selected export file already exists, system MUST show QMessageBox confirmation before overwriting

#### MainWindow - Progress Indication

- **FR-030**: System MUST display QProgressDialog during import with message "Importando dados do Excel..."
- **FR-031**: System MUST display QProgressDialog during export with message "Exportando dados para Excel..."
- **FR-032**: Progress dialog MUST be modal to prevent user interaction with main window
- **FR-033**: System MUST disable Import/Export toolbar buttons during operation
- **FR-034**: System MUST show wait cursor during import/export operations

#### MainWindow - Result Dialogs

- **FR-040**: After successful import, system MUST display QMessageBox with summary: "[N] historias importadas, [M] features criadas, [W] warnings"
- **FR-041**: If import has warnings, result dialog MUST include "Ver Detalhes" button to show warning list
- **FR-042**: After successful export, system MUST display QMessageBox with summary: "[N] historias, [M] desenvolvedores, [K] features exportados para [path]"
- **FR-043**: After import completes, system MUST automatically refresh the story table

#### MainWindow - Error Handling

- **FR-050**: Import errors MUST be displayed in QMessageBox.critical with descriptive message
- **FR-051**: Export errors MUST be displayed in QMessageBox.critical with descriptive message
- **FR-052**: Error messages MUST come from ImportExcelOutputDTO.errors or ExportExcelOutputDTO errors
- **FR-053**: If import has critical errors (header missing, cycle detected), system MUST NOT refresh table since no data was imported

#### ViewModel Integration

- **FR-060**: MainWindow MUST obtain ExcelViewModel from DIContainer
- **FR-061**: MainWindow MUST connect to ExcelViewModel signals: import_completed, import_error, export_completed, export_error
- **FR-062**: MainWindow MUST call ExcelViewModel.import_from_file(path) when import is triggered
- **FR-063**: MainWindow MUST call ExcelViewModel.export_to_file(path) when export is triggered

#### State Management

- **FR-070**: Import/Export buttons MUST be disabled when loading property is True on MainWindowViewModel
- **FR-071**: System MUST set internal flag to track ongoing import/export operation
- **FR-072**: System MUST ignore shortcut/button triggers while operation is in progress

### Key Entities

- **QAction (Import/Export)**: Toolbar actions that trigger file dialogs and operations
- **QShortcut (Ctrl+I, Ctrl+E)**: Keyboard shortcuts bound to import/export handlers
- **QProgressDialog**: Modal dialog showing operation progress
- **QFileDialog**: Standard dialogs for file selection (open for import, save for export)
- **QMessageBox**: Result and error dialogs for user feedback

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can access import/export functionality within 2 clicks (toolbar button + file selection)
- **SC-002**: Users can trigger import/export using keyboard shortcuts without mouse interaction
- **SC-003**: Users receive clear feedback within 1 second of starting an operation (progress dialog appears)
- **SC-004**: After import completes, users see imported data in the table without manual refresh
- **SC-005**: 100% of import/export errors display user-friendly messages explaining the issue
- **SC-006**: Operations do not block UI - window remains responsive during import/export
- **SC-007**: 95% of first-time users successfully complete import/export using only UI hints (tooltips, labels)

## Assumptions

- EP-009 Excel integration is fully implemented (ExcelService, ImportExcelUseCase, ExportExcelUseCase, ExcelViewModel, DTOs)
- DIContainer already exposes excel_viewmodel property (FR-083 from EP-009)
- ExcelViewModel emits signals: import_started, import_completed, import_error, export_started, export_completed, export_error
- MainWindowViewModel.loading property is available to check current loading state
- PySide6 QFileDialog, QProgressDialog, QMessageBox are available and configured for the application
- Import/Export use cases handle async execution via asyncio.to_thread() as specified in EP-009

## Test Scenarios

### UI Tests (pytest-qt)

1. **test_toolbar_has_import_button**: MainWindow toolbar contains "Importar Excel" action with correct tooltip
2. **test_toolbar_has_export_button**: MainWindow toolbar contains "Exportar Excel" action with correct tooltip
3. **test_ctrl_i_shortcut_registered**: Ctrl+I shortcut is registered and triggers import handler
4. **test_ctrl_e_shortcut_registered**: Ctrl+E shortcut is registered and triggers export handler
5. **test_import_button_opens_file_dialog**: Clicking import button opens QFileDialog with .xlsx filter
6. **test_export_button_opens_file_dialog**: Clicking export button opens QFileDialog (save mode) with .xlsx filter
7. **test_progress_dialog_shown_on_import**: Progress dialog appears when import operation starts
8. **test_progress_dialog_shown_on_export**: Progress dialog appears when export operation starts
9. **test_buttons_disabled_during_operation**: Import/Export buttons are disabled while operation is in progress
10. **test_success_message_after_import**: QMessageBox with summary appears after successful import
11. **test_success_message_after_export**: QMessageBox with summary appears after successful export
12. **test_error_message_on_import_failure**: QMessageBox.critical appears when import fails
13. **test_table_refresh_after_import**: Story table data is reloaded after successful import
14. **test_overwrite_confirmation_on_export**: Confirmation dialog appears when export file exists

### Integration Tests

1. **test_import_flow_end_to_end**: Full import flow from button click to data appearing in table
2. **test_export_flow_end_to_end**: Full export flow from button click to file creation
3. **test_shortcut_import_flow**: Import via Ctrl+I shortcut works same as button
4. **test_shortcut_export_flow**: Export via Ctrl+E shortcut works same as button
