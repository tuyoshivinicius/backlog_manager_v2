"""Integration tests for MainWindow Excel import/export functionality.

This module contains tests for the Excel GUI integration feature (EP-012),
verifying toolbar buttons, keyboard shortcuts, dialogs, and signal handling.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence
from PySide6.QtWidgets import QMessageBox

from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
    MainWindowViewModel,
)
from backlog_manager.presentation.views.main_window import MainWindow


# Mock DTOs for testing
@dataclass
class MockImportExcelOutputDTO:
    """Mock import result DTO."""

    stories_imported: int = 10
    features_created: int = 2
    developers_created: int = 3
    warnings: list[str] | None = None
    errors: list[str] | None = None

    def __post_init__(self) -> None:
        if self.warnings is None:
            self.warnings = []
        if self.errors is None:
            self.errors = []


@dataclass
class MockExportExcelOutputDTO:
    """Mock export result DTO."""

    stories_exported: int = 15
    features_exported: int = 4
    developers_exported: int = 5
    file_path: Path = Path("test_export.xlsx")


class TestMainWindowExcelToolbarButtons:
    """Tests for Excel import/export toolbar buttons (US1, US2 - T006, T014)."""

    def test_toolbar_has_import_excel_button(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that toolbar has Importar Excel action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_import_excel is not None
        assert window._action_import_excel.text() == "Importar"

    def test_toolbar_has_export_excel_button(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that toolbar has Exportar Excel action."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert window._action_export_excel is not None
        assert window._action_export_excel.text() == "Exportar"

    def test_import_button_has_correct_tooltip(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that import button has correct tooltip."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert "Importar Excel" in window._action_import_excel.toolTip()
        assert "Ctrl+I" in window._action_import_excel.toolTip()

    def test_export_button_has_correct_tooltip(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that export button has correct tooltip."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert "Exportar Excel" in window._action_export_excel.toolTip()
        assert "Ctrl+E" in window._action_export_excel.toolTip()


class TestMainWindowExcelFileDialogs:
    """Tests for file dialog behavior (US1, US2 - T007, T015)."""

    def test_import_button_opens_file_open_dialog(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that import button opens file open dialog."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getOpenFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("", "")  # User cancelled
            window._action_import_excel.trigger()
            mock_dialog.assert_called_once()
            # Check filter includes xlsx
            call_args = mock_dialog.call_args
            assert "xlsx" in str(call_args)

    def test_export_button_opens_file_save_dialog(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that export button opens file save dialog."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getSaveFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("", "")  # User cancelled
            window._action_export_excel.trigger()
            mock_dialog.assert_called_once()
            # Check filter includes xlsx and default filename
            call_args = mock_dialog.call_args
            assert "xlsx" in str(call_args)
            assert "backlog_export.xlsx" in str(call_args)

    def test_import_cancelled_does_not_start_operation(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that cancelling import dialog does not start operation."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getOpenFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("", "")  # User cancelled
            window._action_import_excel.trigger()
            assert not window._excel_operation_in_progress

    def test_export_cancelled_does_not_start_operation(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that cancelling export dialog does not start operation."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getSaveFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("", "")  # User cancelled
            window._action_export_excel.trigger()
            assert not window._excel_operation_in_progress


class TestMainWindowExcelSuccessMessages:
    """Tests for success messages after operations (US1, US2 - T008, T016)."""

    def test_import_completed_shows_success_message(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that successful import shows info message."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        result = MockImportExcelOutputDTO()

        with patch(
            "backlog_manager.presentation.views.main_window.QMessageBox.information"
        ) as mock_msgbox:
            window._on_import_completed(result)
            mock_msgbox.assert_called_once()
            call_args = mock_msgbox.call_args
            assert "Importacao Concluida" in str(call_args)
            assert "10 historias importadas" in str(call_args)

    def test_export_completed_shows_success_message(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that successful export shows info message."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        result = MockExportExcelOutputDTO()

        with patch(
            "backlog_manager.presentation.views.main_window.QMessageBox.information"
        ) as mock_msgbox:
            window._on_export_completed(result)
            mock_msgbox.assert_called_once()
            call_args = mock_msgbox.call_args
            assert "Exportacao Concluida" in str(call_args)
            assert "15 historias" in str(call_args)


class TestMainWindowExcelOverwriteConfirmation:
    """Tests for overwrite confirmation on export (US1 - T009)."""

    def test_export_to_existing_file_shows_confirmation(
        self, container: DIContainer, qapp, qtbot, tmp_path
    ) -> None:
        """Test that exporting to existing file shows confirmation dialog."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Create a temporary file
        existing_file = tmp_path / "existing.xlsx"
        existing_file.touch()

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getSaveFileName"
        ) as mock_file_dialog:
            mock_file_dialog.return_value = (str(existing_file), "")
            with patch(
                "backlog_manager.presentation.views.main_window.QMessageBox.question"
            ) as mock_question:
                mock_question.return_value = QMessageBox.StandardButton.No
                window._action_export_excel.trigger()
                mock_question.assert_called_once()
                # Should not start operation if user says No
                assert not window._excel_operation_in_progress


class TestMainWindowExcelTableRefresh:
    """Tests for table refresh after import (US2 - T017)."""

    def test_import_completed_ends_operation_and_triggers_refresh(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that import completion ends operation properly.

        The actual table refresh is triggered via QTimer.singleShot + asyncio.create_task,
        which is already mocked by conftest. We verify the handler completes correctly.
        """
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Start operation to simulate real flow
        window._start_excel_operation("Test import...")
        assert window._excel_operation_in_progress

        result = MockImportExcelOutputDTO()

        with patch(
            "backlog_manager.presentation.views.main_window.QMessageBox.information"
        ):
            window._on_import_completed(result)

        # Verify operation was ended properly
        assert not window._excel_operation_in_progress
        assert window._action_import_excel.isEnabled()


class TestMainWindowExcelKeyboardShortcuts:
    """Tests for keyboard shortcuts (US3 - T022, T023)."""

    def test_import_action_has_ctrl_i_shortcut(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that import action has Ctrl+I shortcut."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        shortcut = window._action_import_excel.shortcut()
        assert shortcut == QKeySequence("Ctrl+I")

    def test_export_action_has_ctrl_e_shortcut(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that export action has Ctrl+E shortcut."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        shortcut = window._action_export_excel.shortcut()
        assert shortcut == QKeySequence("Ctrl+E")

    def test_shortcuts_disabled_during_operation(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that shortcuts are disabled during operation (US3 - T024)."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Start operation
        window._start_excel_operation("Test operation...")

        assert not window._action_import_excel.isEnabled()
        assert not window._action_export_excel.isEnabled()

        # End operation
        window._end_excel_operation()

        assert window._action_import_excel.isEnabled()
        assert window._action_export_excel.isEnabled()


class TestMainWindowExcelProgressDialog:
    """Tests for progress dialog during operations (US4 - T027, T028)."""

    def test_progress_dialog_shown_on_import(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that progress dialog is shown during import."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getOpenFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("test.xlsx", "")
            with patch(
                "backlog_manager.presentation.views.main_window.asyncio.create_task"
            ):
                window._action_import_excel.trigger()
                assert window._progress_dialog is not None
                assert window._progress_dialog.isVisible()

        # Clean up
        window._end_excel_operation()

    def test_progress_dialog_shown_on_export(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that progress dialog is shown during export."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getSaveFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("test.xlsx", "")
            with patch(
                "backlog_manager.presentation.views.main_window.asyncio.create_task"
            ):
                window._action_export_excel.trigger()
                assert window._progress_dialog is not None
                assert window._progress_dialog.isVisible()

        # Clean up
        window._end_excel_operation()


class TestMainWindowExcelButtonsDisabled:
    """Tests for buttons disabled during operation (US4 - T029)."""

    def test_buttons_disabled_during_operation(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that import/export buttons are disabled during operation."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Initially enabled
        assert window._action_import_excel.isEnabled()
        assert window._action_export_excel.isEnabled()

        # Start operation
        window._start_excel_operation("Test...")

        # Should be disabled
        assert not window._action_import_excel.isEnabled()
        assert not window._action_export_excel.isEnabled()

        # Cursor should be wait
        assert window.cursor().shape() == Qt.CursorShape.WaitCursor

        # End operation
        window._end_excel_operation()

        # Should be enabled again
        assert window._action_import_excel.isEnabled()
        assert window._action_export_excel.isEnabled()


class TestMainWindowExcelErrorHandling:
    """Tests for error handling (US5 - T033, T034)."""

    def test_import_error_shows_critical_message(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that import error shows critical message box."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QMessageBox.critical"
        ) as mock_msgbox:
            window._on_import_error("Arquivo invalido")
            mock_msgbox.assert_called_once()
            call_args = mock_msgbox.call_args
            assert "Erro na Importacao" in str(call_args)
            assert "Arquivo invalido" in str(call_args)

    def test_export_error_shows_critical_message(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that export error shows critical message box."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QMessageBox.critical"
        ) as mock_msgbox:
            window._on_export_error("Sem permissao")
            mock_msgbox.assert_called_once()
            call_args = mock_msgbox.call_args
            assert "Erro na Exportacao" in str(call_args)
            assert "Sem permissao" in str(call_args)

    def test_error_ends_operation(self, container: DIContainer, qapp, qtbot) -> None:
        """Test that error handler ends the operation."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        # Start operation
        window._start_excel_operation("Test...")
        assert window._excel_operation_in_progress

        # Trigger error
        with patch(
            "backlog_manager.presentation.views.main_window.QMessageBox.critical"
        ):
            window._on_import_error("Test error")

        # Should have ended operation
        assert not window._excel_operation_in_progress
        assert window._action_import_excel.isEnabled()


class TestMainWindowExcelIntegration:
    """End-to-end integration tests (T037, T038)."""

    def test_full_import_flow_starts_operation(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test import flow starts operation and shows progress.

        Note: The async viewmodel call is mocked by conftest's mock_asyncio_create_task.
        We verify the UI state is correctly set up.
        """
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getOpenFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("test.xlsx", "")
            window._action_import_excel.trigger()

            # Verify operation started
            assert window._excel_operation_in_progress
            assert window._progress_dialog is not None
            assert not window._action_import_excel.isEnabled()
            assert not window._action_export_excel.isEnabled()

        # Clean up
        window._end_excel_operation()

    def test_full_export_flow_starts_operation(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test export flow starts operation and shows progress.

        Note: The async viewmodel call is mocked by conftest's mock_asyncio_create_task.
        We verify the UI state is correctly set up.
        """
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        with patch(
            "backlog_manager.presentation.views.main_window.QFileDialog.getSaveFileName"
        ) as mock_dialog:
            mock_dialog.return_value = ("test_new.xlsx", "")
            window._action_export_excel.trigger()

            # Verify operation started
            assert window._excel_operation_in_progress
            assert window._progress_dialog is not None
            assert not window._action_import_excel.isEnabled()
            assert not window._action_export_excel.isEnabled()

        # Clean up
        window._end_excel_operation()


class TestMainWindowExcelState:
    """Tests for Excel operation state management."""

    def test_initial_state_is_not_in_progress(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that initial state is not in progress."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        assert not window._excel_operation_in_progress
        assert window._progress_dialog is None

    def test_start_operation_sets_in_progress(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that starting operation sets in progress flag."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        window._start_excel_operation("Test...")

        assert window._excel_operation_in_progress
        assert window._progress_dialog is not None

        # Clean up
        window._end_excel_operation()

    def test_end_operation_clears_state(
        self, container: DIContainer, qapp, qtbot
    ) -> None:
        """Test that ending operation clears state."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        window._start_excel_operation("Test...")
        window._end_excel_operation()

        assert not window._excel_operation_in_progress
        assert window._progress_dialog is None
