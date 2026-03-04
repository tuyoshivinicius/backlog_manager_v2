"""Main Window View.

This module provides the main application window implementing the
QMainWindow with toolbar, story table, and side panels.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, QTimer, Slot
from PySide6.QtGui import QAction, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QMainWindow,
    QMessageBox,
    QProgressDialog,
    QSplitter,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.presentation.views.config_panel import ConfigPanel
from backlog_manager.presentation.views.confirm_delete_dialog import ConfirmDeleteDialog
from backlog_manager.presentation.views.dependency_panel import DependencyPanel
from backlog_manager.presentation.views.developer_dialog import DeveloperDialog
from backlog_manager.presentation.views.feature_dialog import FeatureDialog
from backlog_manager.presentation.views.metrics_panel import MetricsPanel
from backlog_manager.presentation.views.story_dialog import StoryDialog
from backlog_manager.presentation.views.warnings_panel import WarningsPanel

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer
    from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
        MainWindowViewModel,
    )

logger = logging.getLogger(__name__)


class StoryTableView(QTableView):
    """Custom QTableView for displaying stories.

    Provides selection handling and keyboard shortcuts for story operations.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the story table view.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        # Configure table behavior
        self.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(False)  # Sorting handled by priority
        self.setShowGrid(True)

        # Configure header
        header = self.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.verticalHeader().setVisible(False)


class MainWindow(QMainWindow):
    """Main application window.

    Displays the story backlog table with toolbar and side panels for
    managing stories, developers, features, dependencies, and allocation.

    Attributes:
        viewmodel: The MainWindowViewModel instance.
    """

    # Window dimensions as per FR-007
    INITIAL_WIDTH = 1280
    INITIAL_HEIGHT = 720
    MIN_WIDTH = 1024
    MIN_HEIGHT = 600

    def __init__(self, viewmodel: MainWindowViewModel) -> None:
        """Initialize the main window.

        Args:
            viewmodel: The MainWindowViewModel to bind to.
        """
        super().__init__()

        self._viewmodel = viewmodel
        self._container: DIContainer = viewmodel._container

        # Excel operation state
        self._excel_operation_in_progress: bool = False
        self._progress_dialog: QProgressDialog | None = None

        self._setup_window()
        self._setup_toolbar()
        self._setup_central_widget()
        self._setup_shortcuts()
        self._connect_signals()

        logger.info("MainWindow initialized")

    @property
    def viewmodel(self) -> MainWindowViewModel:
        """Get the ViewModel.

        Returns:
            The MainWindowViewModel instance.
        """
        return self._viewmodel

    def _setup_window(self) -> None:
        """Configure window properties."""
        self.setWindowTitle("Backlog Manager")
        self.resize(self.INITIAL_WIDTH, self.INITIAL_HEIGHT)
        self.setMinimumSize(self.MIN_WIDTH, self.MIN_HEIGHT)

    def _setup_toolbar(self) -> None:
        """Create and configure the main toolbar."""
        toolbar = QToolBar("Acoes Principais")
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        # Nova Historia action
        self._action_new_story = QAction("Nova Historia", self)
        self._action_new_story.setToolTip("Criar nova historia (Ctrl+N)")
        self._action_new_story.setShortcut(QKeySequence("Ctrl+N"))
        self._action_new_story.triggered.connect(self._on_new_story)
        toolbar.addAction(self._action_new_story)

        # Editar action
        self._action_edit_story = QAction("Editar", self)
        self._action_edit_story.setToolTip("Editar historia selecionada (Enter/F2)")
        self._action_edit_story.triggered.connect(self._on_edit_story)
        toolbar.addAction(self._action_edit_story)

        # Deletar action
        self._action_delete_story = QAction("Deletar", self)
        self._action_delete_story.setToolTip("Deletar historia selecionada (Delete)")
        self._action_delete_story.triggered.connect(self._on_delete_story)
        toolbar.addAction(self._action_delete_story)

        toolbar.addSeparator()

        # Mover Cima action
        self._action_move_up = QAction("Mover Cima", self)
        self._action_move_up.setToolTip("Aumentar prioridade (Alt+Up)")
        self._action_move_up.triggered.connect(self._on_move_up)
        toolbar.addAction(self._action_move_up)

        # Mover Baixo action
        self._action_move_down = QAction("Mover Baixo", self)
        self._action_move_down.setToolTip("Diminuir prioridade (Alt+Down)")
        self._action_move_down.triggered.connect(self._on_move_down)
        toolbar.addAction(self._action_move_down)

        toolbar.addSeparator()

        # Desenvolvedores action
        self._action_developers = QAction("Desenvolvedores", self)
        self._action_developers.setToolTip("Gerenciar desenvolvedores")
        self._action_developers.triggered.connect(self._on_developers)
        toolbar.addAction(self._action_developers)

        # Features action
        self._action_features = QAction("Features", self)
        self._action_features.setToolTip("Gerenciar features")
        self._action_features.triggered.connect(self._on_features)
        toolbar.addAction(self._action_features)

        toolbar.addSeparator()

        # Alocar Automaticamente action
        self._action_allocate = QAction("Alocar Automaticamente", self)
        self._action_allocate.setToolTip("Executar alocacao automatica (Ctrl+Shift+A)")
        self._action_allocate.setShortcut(QKeySequence("Ctrl+Shift+A"))
        self._action_allocate.triggered.connect(self._on_allocate)
        toolbar.addAction(self._action_allocate)

        toolbar.addSeparator()

        # Importar Excel action
        self._action_import_excel = QAction("Importar Excel", self)
        self._action_import_excel.setToolTip("Importar dados de arquivo Excel (Ctrl+I)")
        self._action_import_excel.setShortcut(QKeySequence("Ctrl+I"))
        self._action_import_excel.triggered.connect(self._on_import_excel_clicked)
        toolbar.addAction(self._action_import_excel)

        # Exportar Excel action
        self._action_export_excel = QAction("Exportar Excel", self)
        self._action_export_excel.setToolTip(
            "Exportar dados para arquivo Excel (Ctrl+E)"
        )
        self._action_export_excel.setShortcut(QKeySequence("Ctrl+E"))
        self._action_export_excel.triggered.connect(self._on_export_excel_clicked)
        toolbar.addAction(self._action_export_excel)

    def _setup_central_widget(self) -> None:
        """Create and configure the central widget with splitter layout."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)

        # Create splitter for table and side panels
        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        # Story table (left side)
        self._story_table = StoryTableView()
        self._story_table.setModel(self._viewmodel.table_model)
        self._splitter.addWidget(self._story_table)

        # Side panel container (right side)
        self._side_panel = QWidget()
        side_layout = QVBoxLayout(self._side_panel)
        side_layout.setContentsMargins(5, 0, 0, 0)

        # Config Panel
        self._config_panel = ConfigPanel()
        side_layout.addWidget(self._config_panel)

        # Dependency Panel
        self._dependency_panel = DependencyPanel(self._container)
        side_layout.addWidget(self._dependency_panel)

        # Metrics Panel
        self._metrics_panel = MetricsPanel()
        side_layout.addWidget(self._metrics_panel)

        # Warnings Panel
        self._warnings_panel = WarningsPanel()
        side_layout.addWidget(self._warnings_panel)

        side_layout.addStretch()

        self._splitter.addWidget(self._side_panel)

        # Set initial splitter sizes (70% table, 30% side panel)
        self._splitter.setSizes([700, 300])

        main_layout.addWidget(self._splitter)

        # Connect table selection
        selection_model = self._story_table.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self._on_story_selection_changed)

    def _setup_shortcuts(self) -> None:
        """Configure keyboard shortcuts."""
        # Alt+Up for priority up
        shortcut_up = QShortcut(QKeySequence("Alt+Up"), self)
        shortcut_up.activated.connect(self._on_move_up)

        # Alt+Down for priority down
        shortcut_down = QShortcut(QKeySequence("Alt+Down"), self)
        shortcut_down.activated.connect(self._on_move_down)

        # Delete key for delete
        shortcut_delete = QShortcut(QKeySequence("Delete"), self)
        shortcut_delete.activated.connect(self._on_delete_story)

        # Enter for edit
        shortcut_enter = QShortcut(QKeySequence("Return"), self._story_table)
        shortcut_enter.activated.connect(self._on_edit_story)

        # F2 for edit
        shortcut_f2 = QShortcut(QKeySequence("F2"), self._story_table)
        shortcut_f2.activated.connect(self._on_edit_story)

    def _connect_signals(self) -> None:
        """Connect ViewModel signals to view slots."""
        self._viewmodel.stories_changed.connect(self._on_stories_changed)
        self._viewmodel.story_selected.connect(self._on_viewmodel_story_selected)
        self._viewmodel.loading.connect(self._on_loading_changed)
        self._viewmodel.error_occurred.connect(self._on_error)

        # Connect dependency panel signals
        self._dependency_panel.dependency_added.connect(self._on_dependency_changed)
        self._dependency_panel.dependency_removed.connect(self._on_dependency_changed)
        self._dependency_panel.error_occurred.connect(self._on_error)

        # Connect allocation viewmodel signals
        allocation_vm = self._container.allocation_viewmodel
        allocation_vm.allocation_started.connect(self._on_allocation_started)
        allocation_vm.allocation_completed.connect(self._on_allocation_completed)
        allocation_vm.allocation_error.connect(self._on_error)
        allocation_vm.warnings_updated.connect(self._on_warnings_updated)

        # Connect Excel viewmodel signals
        excel_vm = self._container.excel_viewmodel
        excel_vm.import_completed.connect(self._on_import_completed)
        excel_vm.import_error.connect(self._on_import_error)
        excel_vm.export_completed.connect(self._on_export_completed)
        excel_vm.export_error.connect(self._on_export_error)

    @Slot()
    def _on_stories_changed(self) -> None:
        """Handle stories_changed signal."""
        # Table model is already updated by ViewModel
        # Resize columns to content
        self._story_table.resizeColumnsToContents()

        # Update dependency panel with current stories
        self._dependency_panel.set_stories(self._viewmodel.stories)

        logger.debug("Stories changed, table updated")

    @Slot(str)
    def _on_viewmodel_story_selected(self, story_id: str) -> None:
        """Handle story selection from ViewModel."""
        self._dependency_panel.set_current_story(story_id)

    @Slot(bool)
    def _on_loading_changed(self, is_loading: bool) -> None:
        """Handle loading state changes.

        Args:
            is_loading: True if loading, False otherwise.
        """
        self.setCursor(
            Qt.CursorShape.WaitCursor if is_loading else Qt.CursorShape.ArrowCursor
        )
        self._action_allocate.setEnabled(not is_loading)
        logger.debug("Loading state: %s", is_loading)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error_occurred signal.

        Args:
            message: Error message to display.
        """
        QMessageBox.warning(self, "Erro", message)
        logger.warning("Error displayed: %s", message)

    @Slot()
    def _on_story_selection_changed(self) -> None:
        """Handle story selection change in table."""
        current_index = self._story_table.currentIndex()
        if current_index.isValid():
            story_id = self._viewmodel.table_model.data(
                current_index, Qt.ItemDataRole.UserRole
            )
            if story_id:
                self._viewmodel.select_story(story_id)

    @Slot()
    def _on_new_story(self) -> None:
        """Handle new story action."""
        logger.debug("New story action triggered")
        dialog = StoryDialog(self._container, self, mode="create")
        if dialog.exec():
            # Reload stories after creation
            QTimer.singleShot(
                0, lambda: asyncio.create_task(self._viewmodel.load_stories())
            )

    @Slot()
    def _on_edit_story(self) -> None:
        """Handle edit story action."""
        if not self._viewmodel.selected_story_id:
            QMessageBox.information(
                self, "Aviso", "Selecione uma historia para editar."
            )
            return

        story = self._viewmodel.selected_story
        if not story:
            return

        logger.debug(
            "Edit story action triggered for %s", self._viewmodel.selected_story_id
        )
        dialog = StoryDialog(self._container, self, mode="edit", story=story)
        if dialog.exec():
            # Reload stories after edit
            QTimer.singleShot(
                0, lambda: asyncio.create_task(self._viewmodel.load_stories())
            )

    @Slot()
    def _on_delete_story(self) -> None:
        """Handle delete story action."""
        if not self._viewmodel.selected_story_id:
            QMessageBox.information(
                self, "Aviso", "Selecione uma historia para deletar."
            )
            return

        story = self._viewmodel.selected_story
        if not story:
            return

        logger.debug(
            "Delete story action triggered for %s", self._viewmodel.selected_story_id
        )

        dialog = ConfirmDeleteDialog(story.id, story.name, self)
        if dialog.exec():
            QTimer.singleShot(
                0,
                lambda: asyncio.create_task(
                    self._viewmodel.delete_story(self._viewmodel.selected_story_id)
                ),
            )

    @Slot()
    def _on_move_up(self) -> None:
        """Handle move priority up action."""
        if not self._viewmodel.selected_story_id:
            return
        asyncio.create_task(
            self._viewmodel.move_priority_up(self._viewmodel.selected_story_id)
        )

    @Slot()
    def _on_move_down(self) -> None:
        """Handle move priority down action."""
        if not self._viewmodel.selected_story_id:
            return
        asyncio.create_task(
            self._viewmodel.move_priority_down(self._viewmodel.selected_story_id)
        )

    @Slot()
    def _on_developers(self) -> None:
        """Handle developers action."""
        logger.debug("Developers action triggered")
        dialog = DeveloperDialog(self._container, self)
        dialog.developers_changed.connect(self._on_data_changed)
        dialog.exec()

    @Slot()
    def _on_features(self) -> None:
        """Handle features action."""
        logger.debug("Features action triggered")
        dialog = FeatureDialog(self._container, self)
        dialog.features_changed.connect(self._on_data_changed)
        dialog.exec()

    @Slot()
    def _on_data_changed(self) -> None:
        """Handle data changed from dialogs."""
        # Reload stories to reflect changes
        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._viewmodel.load_stories())
        )

    @Slot(str, str)
    def _on_dependency_changed(self, story_id: str, depends_on_id: str) -> None:
        """Handle dependency added/removed."""
        # Reload stories to reflect dependency changes
        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._viewmodel.load_stories())
        )

    @Slot()
    def _on_allocate(self) -> None:
        """Handle automatic allocation action."""
        logger.debug("Allocate action triggered")

        # Validate config
        is_valid, error = self._config_panel.validate()
        if not is_valid:
            QMessageBox.warning(self, "Configuracao Invalida", error)
            return

        # Execute allocation
        QTimer.singleShot(0, lambda: asyncio.create_task(self._execute_allocation()))

    async def _execute_allocation(self) -> None:
        """Execute allocation with config panel values."""
        allocation_vm = self._container.allocation_viewmodel

        await allocation_vm.execute(
            velocity=self._config_panel.velocity,
            start_date=self._config_panel.start_date,
            max_idle_days=self._config_panel.max_idle_days,
        )

        # Reload stories after allocation
        await self._viewmodel.load_stories()

    @Slot()
    def _on_allocation_started(self) -> None:
        """Handle allocation started signal."""
        self._action_allocate.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)
        self._metrics_panel.clear()
        self._warnings_panel.clear()

    @Slot(object)
    def _on_allocation_completed(self, metrics) -> None:  # type: ignore[no-untyped-def]
        """Handle allocation completed signal."""
        self._action_allocate.setEnabled(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._metrics_panel.set_metrics(metrics)

        QMessageBox.information(
            self,
            "Alocacao Concluida",
            f"Alocacao concluida com sucesso!\n\n"
            f"Historias alocadas: {metrics.stories_allocated}\n"
            f"Tempo: {metrics.total_time_seconds:.2f}s",
        )

    @Slot(list)
    def _on_warnings_updated(self, warnings: list[str]) -> None:
        """Handle warnings updated signal."""
        self._warnings_panel.set_warnings(warnings)

    @property
    def story_table(self) -> StoryTableView:
        """Get the story table view.

        Returns:
            The StoryTableView widget.
        """
        return self._story_table

    # Excel operation helper methods

    def _start_excel_operation(self, message: str) -> None:
        """Start an Excel operation with progress dialog.

        Args:
            message: Progress dialog message.
        """
        self._excel_operation_in_progress = True
        self._action_import_excel.setEnabled(False)
        self._action_export_excel.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)

        self._progress_dialog = QProgressDialog(message, None, 0, 0, self)
        self._progress_dialog.setWindowModality(Qt.WindowModality.ApplicationModal)
        self._progress_dialog.setMinimumDuration(0)
        self._progress_dialog.show()

    def _end_excel_operation(self) -> None:
        """End an Excel operation and clean up."""
        self._excel_operation_in_progress = False
        self._action_import_excel.setEnabled(True)
        self._action_export_excel.setEnabled(True)
        self.unsetCursor()

        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None

    # Excel import/export handlers

    @Slot()
    def _on_import_excel_clicked(self) -> None:
        """Handle import Excel action."""
        logger.debug("Import Excel action triggered")

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar Excel",
            "",
            "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)",
        )
        if file_path:
            self._start_excel_operation("Importando dados do Excel...")
            QTimer.singleShot(
                0,
                lambda: asyncio.create_task(
                    self._container.excel_viewmodel.import_from_file(Path(file_path))
                ),
            )

    @Slot()
    def _on_export_excel_clicked(self) -> None:
        """Handle export Excel action."""
        logger.debug("Export Excel action triggered")

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar Excel",
            "backlog_export.xlsx",
            "Arquivos Excel (*.xlsx);;Todos os arquivos (*.*)",
        )
        if file_path:
            # Check if file exists for overwrite confirmation
            if Path(file_path).exists():
                reply = QMessageBox.question(
                    self,
                    "Confirmar Substituicao",
                    f"O arquivo {file_path} ja existe. Deseja sobrescrever?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            self._start_excel_operation("Exportando dados para Excel...")
            QTimer.singleShot(
                0,
                lambda: asyncio.create_task(
                    self._container.excel_viewmodel.export_to_file(Path(file_path))
                ),
            )

    @Slot(object)
    def _on_import_completed(self, result) -> None:  # type: ignore[no-untyped-def]
        """Handle import completed signal.

        Args:
            result: ImportExcelOutputDTO with import results.
        """
        self._end_excel_operation()
        msg = (
            f"Importacao concluida!\n\n"
            f"{result.stories_imported} historias importadas\n"
            f"{result.features_created} features criadas\n"
            f"{result.developers_created} desenvolvedores criados"
        )
        if result.warnings:
            msg += f"\n{len(result.warnings)} avisos"
        QMessageBox.information(self, "Importacao Concluida", msg)
        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._viewmodel.load_stories())
        )

    @Slot(str)
    def _on_import_error(self, error: str) -> None:
        """Handle import error signal.

        Args:
            error: Error message.
        """
        self._end_excel_operation()
        QMessageBox.critical(self, "Erro na Importacao", error)
        logger.error("Import error: %s", error)

    @Slot(object)
    def _on_export_completed(self, result) -> None:  # type: ignore[no-untyped-def]
        """Handle export completed signal.

        Args:
            result: ExportExcelOutputDTO with export results.
        """
        self._end_excel_operation()
        msg = (
            f"Exportacao concluida!\n\n"
            f"{result.stories_exported} historias\n"
            f"{result.features_exported} features\n"
            f"{result.developers_exported} desenvolvedores\n\n"
            f"Arquivo: {result.file_path}"
        )
        QMessageBox.information(self, "Exportacao Concluida", msg)

    @Slot(str)
    def _on_export_error(self, error: str) -> None:
        """Handle export error signal.

        Args:
            error: Error message.
        """
        self._end_excel_operation()
        QMessageBox.critical(self, "Erro na Exportacao", error)
        logger.error("Export error: %s", error)
