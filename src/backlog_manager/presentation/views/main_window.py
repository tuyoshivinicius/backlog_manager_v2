"""Main Window View.

This module provides the main application window implementing the
QMainWindow with menu bar, toolbar, story table, and status bar.
Layout vertical de 5 zonas conforme EP-018.
"""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from PySide6.QtCore import QRect, QSize, Qt, QTimer, Slot
from PySide6.QtGui import QAction, QColor, QFont, QKeySequence, QPainter, QShortcut
from PySide6.QtWidgets import (
    QButtonGroup,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QMessageBox,
    QPushButton,
    QTableView,
    QToolBar,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.presentation.delegates import (
    DependencyIndicatorDelegate,
    MonospaceDelegate,
    StatusBadgeDelegate,
)
from backlog_manager.presentation.theme import DESIGN_TOKENS
from backlog_manager.presentation.viewmodels.filter_proxy_model import FilterProxyModel
from backlog_manager.presentation.viewmodels.story_table_model import StoryTableModel
from backlog_manager.presentation.views.confirm_delete_dialog import ConfirmDeleteDialog
from backlog_manager.presentation.views.developer_dialog import DeveloperDialog
from backlog_manager.presentation.views.feature_dialog import FeatureDialog
from backlog_manager.presentation.views.progress_dialog import (
    ProgressDialog as CustomProgressDialog,
)
from backlog_manager.presentation.views.status_bar import SpBreakdownLabel
from backlog_manager.presentation.views.story_dialog import StoryDialog

if TYPE_CHECKING:
    from PySide6.QtCore import QPoint

    from backlog_manager.application.dto.allocation import AllocationMetricsDTO
    from backlog_manager.application.dto.planning.reset_planning_dto import (
        ResetPlanningOutputDTO,
    )
    from backlog_manager.application.dto.scheduling.calculate_schedule_dto import (
        CalculateScheduleOutputDTO,
    )
    from backlog_manager.presentation.container import DIContainer
    from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
        MainWindowViewModel,
    )

logger = logging.getLogger(__name__)


class StoryTableView(QTableView):
    """Custom QTableView for displaying stories.

    Provides selection handling, keyboard shortcuts, wave separators,
    and rich tooltip hover tracking.
    """

    WAVE_SEPARATOR_HEIGHT = 24
    WAVE_SEPARATOR_PADDING = 12

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
        self.setMouseTracking(True)

        # Configure header
        header = self.horizontalHeader()
        if header:
            header.setStretchLastSection(True)
            header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)

        self.verticalHeader().setVisible(False)

        # Wave separator visibility
        self._wave_separators_visible: bool = True

        # Rich tooltip tracking
        self._tooltip_timer = QTimer(self)
        self._tooltip_timer.setSingleShot(True)
        self._tooltip_timer.setInterval(300)
        self._tooltip_timer.timeout.connect(self._show_rich_tooltip)
        self._hovered_row: int = -1
        self._tooltip_widget: QWidget | None = None

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        """Reposition empty state label on resize.

        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        for child in self.children():
            if isinstance(child, QLabel) and child.objectName() == "empty-state-label":
                child.setGeometry(self.viewport().geometry())

    def paintEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        """Paint the table with wave separators between wave groups.

        Args:
            event: The paint event.
        """
        super().paintEvent(event)

        if not self._wave_separators_visible:
            return

        model = self.model()
        if model is None or model.rowCount() == 0:
            return

        painter = QPainter(self.viewport())
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Onda column index = 2
        wave_col = 2
        prev_wave: int | None = None

        for row in range(model.rowCount()):
            index = model.index(row, wave_col)
            wave_text = index.data(Qt.ItemDataRole.DisplayRole)

            # Parse wave value
            try:
                wave_val = int(wave_text) if wave_text and wave_text != "\u2014" else 0
            except (ValueError, TypeError):
                wave_val = 0

            if prev_wave is not None and wave_val != prev_wave:
                # Draw separator band above this row
                row_rect = self.visualRect(model.index(row, 0))
                separator_rect = QRect(
                    0,
                    row_rect.y() - self.WAVE_SEPARATOR_HEIGHT,
                    self.viewport().width(),
                    self.WAVE_SEPARATOR_HEIGHT,
                )

                # Only paint if visible
                if separator_rect.intersects(self.viewport().rect()):
                    # Background
                    bg_color = QColor(DESIGN_TOKENS["neutral-100"])
                    painter.fillRect(separator_rect, bg_color)

                    # Text
                    label = f"Onda {wave_val}" if wave_val > 0 else "Sem Onda"
                    font = painter.font()
                    font.setBold(True)
                    painter.setFont(font)
                    painter.setPen(QColor(DESIGN_TOKENS["neutral-600"]))

                    text_rect = QRect(
                        self.WAVE_SEPARATOR_PADDING,
                        separator_rect.y(),
                        separator_rect.width() - self.WAVE_SEPARATOR_PADDING,
                        separator_rect.height(),
                    )
                    painter.drawText(
                        text_rect,
                        Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter,
                        label,
                    )

                    # Reset font
                    font.setBold(False)
                    painter.setFont(font)

            prev_wave = wave_val

        painter.end()

    def mouseMoveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        """Track hovered row for rich tooltip.

        Args:
            event: The mouse event.
        """
        super().mouseMoveEvent(event)
        index = self.indexAt(event.pos())
        new_row = index.row() if index.isValid() else -1

        if new_row != self._hovered_row:
            self._hovered_row = new_row
            self._tooltip_timer.stop()
            self._hide_rich_tooltip()
            if new_row >= 0:
                self._tooltip_timer.start()

    def leaveEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        """Hide tooltip on mouse leave.

        Args:
            event: The leave event.
        """
        super().leaveEvent(event)
        self._tooltip_timer.stop()
        self._hide_rich_tooltip()
        self._hovered_row = -1

    def _show_rich_tooltip(self) -> None:
        """Show the rich tooltip for the hovered row."""
        if self._hovered_row < 0:
            return

        from backlog_manager.presentation.views.rich_tooltip import RichTooltipWidget

        model = self.model()
        if model is None:
            return

        # Get story data from UserRole
        index = model.index(self._hovered_row, 0)
        story_id = model.data(index, Qt.ItemDataRole.UserRole)
        if not story_id:
            return

        # Collect display data from all columns
        data: dict[str, str] = {}
        col_names = [
            "Prioridade",
            "Feature",
            "Onda",
            "ID",
            "Componente",
            "Nome",
            "Status",
            "Desenvolvedor",
            "Dependencias",
            "SP",
            "Inicio",
            "Fim",
            "Duracao",
        ]
        for col, name in enumerate(col_names):
            val = model.data(
                model.index(self._hovered_row, col), Qt.ItemDataRole.DisplayRole
            )
            data[name] = str(val) if val else "\u2014"

        self._hide_rich_tooltip()
        self._tooltip_widget = RichTooltipWidget(data, self)

        # Position near cursor
        cursor_pos = self.mapFromGlobal(self.cursor().pos())
        global_pos = self.mapToGlobal(cursor_pos)
        tooltip_x = global_pos.x() + 10
        tooltip_y = global_pos.y() + 10

        # Reposition if near bottom edge
        screen = self.screen()
        if screen:
            screen_rect = screen.availableGeometry()
            if (
                tooltip_y + self._tooltip_widget.sizeHint().height()
                > screen_rect.bottom()
            ):
                tooltip_y = (
                    global_pos.y() - self._tooltip_widget.sizeHint().height() - 10
                )

        self._tooltip_widget.move(tooltip_x, tooltip_y)
        self._tooltip_widget.show()

    def _hide_rich_tooltip(self) -> None:
        """Hide and clean up the rich tooltip widget."""
        if self._tooltip_widget is not None:
            self._tooltip_widget.hide()
            self._tooltip_widget.deleteLater()
            self._tooltip_widget = None


class MainWindow(QMainWindow):
    """Main application window.

    Layout vertical de 5 zonas: Menu Bar, Toolbar, Filter Bar (placeholder),
    Story Table, Status Bar. Paineis laterais migrados para dialogs modais.

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
        self._progress_dialog: CustomProgressDialog | None = None

        # Responsive column hiding state
        self._columns_hidden: bool = False
        self._responsive_columns = [2, 4, 12]  # Onda, Componente, Duracao

        # Planning data tracking (R-005)
        self._has_planning_data: bool = False
        self._last_allocation_time: Optional[datetime] = None

        self._setup_window()
        self._setup_toolbar()
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_status_bar()
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

    def resizeEvent(self, event) -> None:  # type: ignore[no-untyped-def]
        """Handle responsive column hiding on window resize.

        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        narrow = self.width() < 1024

        if narrow and not self._columns_hidden:
            for col in self._responsive_columns:
                self._story_table.setColumnHidden(col, True)
            self._columns_hidden = True
            count = len(self._responsive_columns)
            self._hidden_columns_label.setText(f"{count} colunas ocultas")
            self._hidden_columns_label.setVisible(True)
        elif not narrow and self._columns_hidden:
            for col in self._responsive_columns:
                self._story_table.setColumnHidden(col, False)
            self._columns_hidden = False
            self._hidden_columns_label.setVisible(False)

    def _setup_menu_bar(self) -> None:
        """Configura menu bar com 4 menus."""
        menu_bar = self.menuBar()

        # Menu Arquivo
        file_menu = menu_bar.addMenu("&Arquivo")
        file_menu.addAction(self._action_import_excel)
        file_menu.addAction(self._action_export_excel)
        file_menu.addSeparator()
        exit_action = QAction("Sair", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menu Cadastros
        cadastros_menu = menu_bar.addMenu("&Cadastros")
        cadastros_menu.addAction(self._action_new_story)
        cadastros_menu.addAction(self._action_features)
        cadastros_menu.addAction(self._action_developers)
        cadastros_menu.addSeparator()
        self._action_config = QAction("Configuracao", self)
        cadastros_menu.addAction(self._action_config)

        # Menu Ferramentas
        tools_menu = menu_bar.addMenu("&Ferramentas")
        tools_menu.addAction(self._action_new_planning)
        tools_menu.addSeparator()
        tools_menu.addAction(self._action_schedule)
        tools_menu.addAction(self._action_allocate)

        # Menu Ajuda
        help_menu = menu_bar.addMenu("A&juda")
        about_action = QAction("Sobre", self)
        about_action.triggered.connect(self._on_about)
        help_menu.addAction(about_action)

    def _setup_toolbar(self) -> None:
        """Configura toolbar com icones e 5 grupos separados."""
        from backlog_manager.presentation.theme.theme import get_icon_manager

        toolbar = QToolBar("Principal")
        toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setMovable(False)
        self.addToolBar(toolbar)

        icon = get_icon_manager()

        # Grupo 1: CRUD
        self._action_new_story = QAction(icon.get("plus"), "Nova", self)
        self._action_new_story.setShortcut(QKeySequence("Ctrl+N"))
        self._action_new_story.setToolTip("Nova Historia (Ctrl+N)")
        self._action_new_story.triggered.connect(self._on_new_story)
        toolbar.addAction(self._action_new_story)

        self._action_edit_story = QAction(icon.get("pencil-simple"), "Editar", self)
        self._action_edit_story.setShortcut(QKeySequence("F2"))
        self._action_edit_story.setToolTip("Editar Historia (F2)")
        self._action_edit_story.triggered.connect(self._on_edit_story)
        toolbar.addAction(self._action_edit_story)

        self._action_delete_story = QAction(icon.get("trash"), "Deletar", self)
        self._action_delete_story.setShortcut(QKeySequence("Delete"))
        self._action_delete_story.setToolTip("Deletar Historia (Delete)")
        self._action_delete_story.triggered.connect(self._on_delete_story)
        toolbar.addAction(self._action_delete_story)

        self._action_duplicate_story = QAction(icon.get("copy"), "Duplicar", self)
        self._action_duplicate_story.setShortcut(QKeySequence("Ctrl+D"))
        self._action_duplicate_story.setToolTip("Duplicar Historia (Ctrl+D)")
        self._action_duplicate_story.triggered.connect(self._on_duplicate_story)
        toolbar.addAction(self._action_duplicate_story)

        toolbar.addSeparator()

        # Grupo 2: Priorizacao
        self._action_move_up = QAction(icon.get("arrow-up"), "Mover Cima", self)
        self._action_move_up.setToolTip("Mover Prioridade Acima (Alt+Up)")
        self._action_move_up.triggered.connect(self._on_move_up)
        toolbar.addAction(self._action_move_up)

        self._action_move_down = QAction(icon.get("arrow-down"), "Mover Baixo", self)
        self._action_move_down.setToolTip("Mover Prioridade Abaixo (Alt+Down)")
        self._action_move_down.triggered.connect(self._on_move_down)
        toolbar.addAction(self._action_move_down)

        toolbar.addSeparator()

        # Grupo 3: Cadastros
        self._action_developers = QAction(icon.get("users"), "Desenvolvedores", self)
        self._action_developers.setToolTip("Gerenciar Desenvolvedores")
        self._action_developers.triggered.connect(self._on_developers)
        toolbar.addAction(self._action_developers)

        self._action_features = QAction(icon.get("package"), "Features", self)
        self._action_features.setToolTip("Gerenciar Features")
        self._action_features.triggered.connect(self._on_features)
        toolbar.addAction(self._action_features)

        self._action_config_toolbar = QAction(icon.get("gear"), "Configuracao", self)
        self._action_config_toolbar.setToolTip("Configuracao")
        self._action_config_toolbar.triggered.connect(self._on_config)
        toolbar.addAction(self._action_config_toolbar)

        toolbar.addSeparator()

        # Grupo 4: Processamento
        self._action_new_planning = QAction(
            icon.get("arrows-down-up"), "Novo Planejamento", self
        )
        self._action_new_planning.setShortcut(QKeySequence("Ctrl+Shift+N"))
        self._action_new_planning.setToolTip(
            "Limpar dados de planejamento e recomecar do zero (Ctrl+Shift+N)"
        )
        self._action_new_planning.setEnabled(False)
        self._action_new_planning.triggered.connect(self._on_new_planning)
        toolbar.addAction(self._action_new_planning)

        self._action_schedule = QAction(
            icon.get("calendar-check"), "Calcular Cronograma", self
        )
        self._action_schedule.setShortcut(QKeySequence("Ctrl+Shift+C"))
        self._action_schedule.setToolTip("Calcular Cronograma (Ctrl+Shift+C)")
        self._action_schedule.triggered.connect(self._on_calculate_schedule)
        toolbar.addAction(self._action_schedule)

        self._action_allocate = QAction(icon.get("shuffle"), "Alocar", self)
        self._action_allocate.setShortcut(QKeySequence("Ctrl+Shift+A"))
        self._action_allocate.setToolTip("Alocar Desenvolvedores (Ctrl+Shift+A)")
        self._action_allocate.triggered.connect(self._on_allocate)
        toolbar.addAction(self._action_allocate)

        toolbar.addSeparator()

        # Grupo 5: Excel
        self._action_import_excel = QAction(
            icon.get("download-simple"), "Importar", self
        )
        self._action_import_excel.setShortcut(QKeySequence("Ctrl+I"))
        self._action_import_excel.setToolTip("Importar Excel (Ctrl+I)")
        self._action_import_excel.triggered.connect(self._on_import_excel_clicked)
        toolbar.addAction(self._action_import_excel)

        self._action_export_excel = QAction(icon.get("upload-simple"), "Exportar", self)
        self._action_export_excel.setShortcut(QKeySequence("Ctrl+E"))
        self._action_export_excel.setToolTip("Exportar Excel (Ctrl+E)")
        self._action_export_excel.triggered.connect(self._on_export_excel_clicked)
        toolbar.addAction(self._action_export_excel)

    def _setup_central_widget(self) -> None:
        """Configura widget central com layout vertical: filtro + tabela."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Filter bar (zona 3, 36px height)
        self._filter_bar = QWidget()
        self._filter_bar.setFixedHeight(36)
        self._filter_bar.setObjectName("filter-bar")
        layout.addWidget(self._filter_bar)
        self._setup_filter_bar()

        # Story table (stretch para ocupar 100% da largura e altura restante)
        self._story_table = StoryTableView()

        # FilterProxyModel between source model and view (ADR-001)
        self._filter_proxy = FilterProxyModel(self)
        self._filter_proxy.setSourceModel(self._viewmodel.table_model)
        self._story_table.setModel(self._filter_proxy)
        layout.addWidget(self._story_table, stretch=1)

        # Delegates — assign AFTER setModel(proxy) per ADR-001
        self._monospace_delegate = MonospaceDelegate(self._story_table)
        self._status_badge_delegate = StatusBadgeDelegate(self._story_table)
        self._dependency_delegate = DependencyIndicatorDelegate(self._story_table)

        model = self._viewmodel.table_model
        delegate_map = {
            "ID": self._monospace_delegate,
            "Status": self._status_badge_delegate,
            "Dependencias": self._dependency_delegate,
        }
        for col in range(model.columnCount()):
            header_text = model.headerData(col, Qt.Orientation.Horizontal)
            if header_text in delegate_map:
                self._story_table.setItemDelegateForColumn(
                    col, delegate_map[header_text]
                )

        # Configure column widths: fixed for all except Nome (stretch)
        header = self._story_table.horizontalHeader()
        if header:
            header.setStretchLastSection(False)
            for col, width in enumerate(StoryTableModel.COLUMN_WIDTHS):
                if width == -1:
                    header.setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)
                else:
                    header.setSectionResizeMode(col, QHeaderView.ResizeMode.Fixed)
                    header.resizeSection(col, width)

        # Enable text elision for truncated columns
        self._story_table.setTextElideMode(Qt.TextElideMode.ElideRight)

        # Empty state overlay
        self._empty_state_label = QLabel(
            "Nenhuma historia cadastrada. Clique em '+ Nova' ou importe "
            "um arquivo Excel para comecar.",
            self._story_table,
        )
        self._empty_state_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_state_label.setWordWrap(True)
        self._empty_state_label.setObjectName("empty-state-label")
        self._empty_state_label.setVisible(True)

        # Context menu for dependency dialog
        self._story_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._story_table.customContextMenuRequested.connect(
            self._on_table_context_menu
        )

        # Connect table selection
        selection_model = self._story_table.selectionModel()
        if selection_model:
            selection_model.currentRowChanged.connect(self._on_story_selection_changed)

    def _setup_filter_bar(self) -> None:
        """Configure zona 3 filter bar with search field, status chips, and feature combo."""
        layout = QHBoxLayout(self._filter_bar)
        layout.setContentsMargins(8, 2, 8, 2)
        layout.setSpacing(8)

        # SearchField (T004)
        self._search_field = QLineEdit()
        self._search_field.setObjectName("searchField")
        self._search_field.setFixedWidth(240)
        self._search_field.setPlaceholderText("Buscar por ID, nome ou componente...")
        self._search_field.setClearButtonEnabled(True)
        layout.addWidget(self._search_field)

        # Debounce timer (T005)
        self._search_timer = QTimer(self)
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(150)
        self._search_timer.timeout.connect(self._apply_text_filter)
        self._pending_search_text: str = ""
        self._search_field.textChanged.connect(self._on_search_text_changed)

        layout.addSpacing(16)

        # Status filter chips (T007)
        self._chip_group = QButtonGroup(self)
        self._chip_group.setExclusive(True)

        chip_definitions: list[tuple[str, str | None]] = [
            ("Todos", None),
            ("Backlog", "BACKLOG"),
            ("Execucao", "EXECUCAO"),
            ("Testes", "TESTES"),
            ("Concluido", "CONCLUIDO"),
            ("Impedido", "IMPEDIDO"),
        ]

        self._filter_chips: list[tuple[QPushButton, str | None]] = []
        for label, status_value in chip_definitions:
            chip = QPushButton(label)
            chip.setCheckable(True)
            chip.setProperty("class", "filterChip")
            chip.setProperty("status_value", status_value)
            self._chip_group.addButton(chip)
            layout.addWidget(chip)
            self._filter_chips.append((chip, status_value))

        # "Todos" checked by default
        self._filter_chips[0][0].setChecked(True)

        self._chip_group.buttonClicked.connect(self._on_chip_clicked)

        layout.addSpacing(16)

        # Feature combo (T015)
        self._feature_combo = QComboBox()
        self._feature_combo.setMinimumWidth(180)
        self._feature_combo.addItem("Todas as features", None)
        self._feature_combo.currentIndexChanged.connect(self._on_feature_changed)
        layout.addWidget(self._feature_combo)

        layout.addStretch()

    def _on_search_text_changed(self, text: str) -> None:
        """Handle search field text change with debounce."""
        self._pending_search_text = text
        self._search_timer.start()

    @Slot()
    def _apply_text_filter(self) -> None:
        """Apply the pending text filter to the proxy model."""
        self._filter_proxy.set_text_filter(self._pending_search_text)
        self._update_move_actions_state()

    @Slot()
    def _on_chip_clicked(self, button: QPushButton) -> None:
        """Handle status chip click."""
        status_value = button.property("status_value")
        self._filter_proxy.set_status_filter(status_value)
        self._update_move_actions_state()

    @Slot()
    def _on_feature_changed(self) -> None:
        """Handle feature combo selection change."""
        feature_id = self._feature_combo.currentData()
        self._filter_proxy.set_feature_filter(feature_id)
        self._update_move_actions_state()

    def _update_chip_counts(self) -> None:
        """Update chip labels with story counts from unfiltered source."""
        stories = self._viewmodel.stories
        total = len(stories)

        status_counts: dict[str, int] = {}
        for story in stories:
            status_counts[story.status] = status_counts.get(story.status, 0) + 1

        for chip, status_value in self._filter_chips:
            if status_value is None:
                chip.setText(f"Todos ({total})")
            else:
                count = status_counts.get(status_value, 0)
                chip.setText(f"{chip.text().split('(')[0].strip()} ({count})")

    def _update_feature_dropdown(self) -> None:
        """Update feature combo with unique features from stories."""
        current_data = self._feature_combo.currentData()

        self._feature_combo.blockSignals(True)
        self._feature_combo.clear()
        self._feature_combo.addItem("Todas as features", None)

        features: dict[int, tuple[str, int]] = {}
        for story in self._viewmodel.stories:
            if story.feature_id and story.feature_name:
                features[story.feature_id] = (story.feature_name, story.wave)

        for fid, (name, wave) in sorted(features.items(), key=lambda x: x[1][1]):
            self._feature_combo.addItem(f"Onda {wave} - {name}", fid)

        # Restore previous selection if still available
        idx = self._feature_combo.findData(current_data)
        if idx >= 0:
            self._feature_combo.setCurrentIndex(idx)

        self._feature_combo.blockSignals(False)

    def _update_move_actions_state(self) -> None:
        """Update move up/down actions based on filter state and selection."""
        has_filters = self._filter_proxy.has_active_filters
        has_selection = self._viewmodel.selected_story_id is not None
        enabled = not has_filters and has_selection
        self._action_move_up.setEnabled(enabled)
        self._action_move_down.setEnabled(enabled)

    def _setup_status_bar(self) -> None:
        """Configura status bar com estatisticas e badge de warnings."""
        status = self.statusBar()

        # Estatisticas a esquerda
        self._stats_label = QLabel("0 historias \u00b7 0 SP \u00b7 Sem alocacao")
        status.addWidget(self._stats_label, 1)

        # SP breakdown label
        self._sp_breakdown_label = SpBreakdownLabel()
        status.addWidget(self._sp_breakdown_label)

        # Hidden columns indicator (for responsive resize)
        self._hidden_columns_label = QLabel()
        self._hidden_columns_label.setVisible(False)
        status.addWidget(self._hidden_columns_label)

        # Badge de warnings a direita
        self._warnings_badge = QPushButton()
        self._warnings_badge.setFlat(True)
        self._warnings_badge.setObjectName("warnings-badge")
        self._warnings_badge.setVisible(False)
        self._warnings_badge.clicked.connect(self._show_warnings_popup)
        status.addPermanentWidget(self._warnings_badge)

        # Armazena warnings para popup
        self._current_warnings: list[str] = []

    def _setup_shortcuts(self) -> None:
        """Configure keyboard shortcuts."""
        # Alt+Up for priority up
        shortcut_up = QShortcut(QKeySequence("Alt+Up"), self)
        shortcut_up.activated.connect(self._on_move_up)

        # Alt+Down for priority down
        shortcut_down = QShortcut(QKeySequence("Alt+Down"), self)
        shortcut_down.activated.connect(self._on_move_down)

        # Enter for edit
        shortcut_enter = QShortcut(QKeySequence("Return"), self._story_table)
        shortcut_enter.activated.connect(self._on_edit_story)

        # Ctrl+F to focus search field
        shortcut_search = QShortcut(QKeySequence("Ctrl+F"), self)
        shortcut_search.activated.connect(self._search_field.setFocus)

    def _connect_signals(self) -> None:
        """Connect ViewModel signals to view slots."""
        self._viewmodel.stories_changed.connect(self._on_stories_changed)
        self._viewmodel.story_selected.connect(self._on_viewmodel_story_selected)
        self._viewmodel.loading.connect(self._on_loading_changed)
        self._viewmodel.error_occurred.connect(self._on_error)

        # Connect allocation viewmodel signals
        allocation_vm = self._container.allocation_viewmodel
        allocation_vm.allocation_started.connect(self._on_allocation_started)
        allocation_vm.allocation_completed.connect(self._on_allocation_completed)
        allocation_vm.allocation_error.connect(self._on_error)
        allocation_vm.allocation_cancelled.connect(self._on_operation_cancelled)
        allocation_vm.warnings_updated.connect(self._on_warnings_updated)

        # Connect schedule viewmodel signals
        schedule_vm = self._container.schedule_viewmodel
        schedule_vm.schedule_started.connect(self._on_schedule_started)
        schedule_vm.schedule_completed.connect(self._on_schedule_completed)
        schedule_vm.schedule_error.connect(self._on_error)

        # Connect reset planning viewmodel signals
        reset_vm = self._container.reset_planning_viewmodel
        reset_vm.reset_started.connect(self._on_reset_started)
        reset_vm.reset_completed.connect(self._on_reset_completed)
        reset_vm.reset_error.connect(self._on_error)

        # Connect Excel viewmodel signals
        excel_vm = self._container.excel_viewmodel
        excel_vm.import_completed.connect(self._on_import_completed)
        excel_vm.import_error.connect(self._on_import_error)
        excel_vm.import_cancelled.connect(self._on_operation_cancelled)
        excel_vm.export_completed.connect(self._on_export_completed)
        excel_vm.export_error.connect(self._on_export_error)
        excel_vm.export_cancelled.connect(self._on_operation_cancelled)

        # Connect config action from menu to handler
        self._action_config.triggered.connect(self._on_config)

    # --- Story handlers ---

    @Slot()
    def _on_stories_changed(self) -> None:
        """Handle stories_changed signal."""
        self._update_status_bar_stats()
        self._update_sp_breakdown()
        self._update_has_planning_data()
        self._update_empty_state()
        self._update_chip_counts()
        self._update_feature_dropdown()
        self._update_move_actions_state()
        logger.debug("Stories changed, table updated")

    def _update_empty_state(self) -> None:
        """Toggle empty state overlay and processing buttons."""
        has_stories = self._viewmodel.table_model.rowCount() > 0
        self._empty_state_label.setVisible(not has_stories)
        self._action_schedule.setEnabled(has_stories)
        self._action_allocate.setEnabled(has_stories)
        self._action_new_planning.setEnabled(has_stories and self._has_planning_data)

    @Slot(str)
    def _on_viewmodel_story_selected(self, story_id: str) -> None:
        """Handle story selection from ViewModel."""
        pass  # No side panels to update

    @Slot(bool)
    def _on_loading_changed(self, is_loading: bool) -> None:
        """Handle loading state changes."""
        self.setCursor(
            Qt.CursorShape.WaitCursor if is_loading else Qt.CursorShape.ArrowCursor
        )
        self._action_new_story.setEnabled(not is_loading)
        self._action_edit_story.setEnabled(not is_loading)
        self._action_delete_story.setEnabled(not is_loading)
        self._action_duplicate_story.setEnabled(not is_loading)
        self._action_move_up.setEnabled(not is_loading)
        self._action_move_down.setEnabled(not is_loading)
        self._action_allocate.setEnabled(not is_loading)
        self._action_schedule.setEnabled(not is_loading)
        self._action_new_planning.setEnabled(not is_loading and self._has_planning_data)
        logger.debug("Loading state: %s", is_loading)

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error_occurred signal."""
        QMessageBox.warning(self, "Erro", message)
        logger.warning("Error displayed: %s", message)

    @Slot()
    def _on_story_selection_changed(self) -> None:
        """Handle story selection change in table."""
        current_index = self._story_table.currentIndex()
        if current_index.isValid():
            story_id = self._filter_proxy.data(current_index, Qt.ItemDataRole.UserRole)
            if story_id:
                self._viewmodel.select_story(story_id)
        self._update_move_actions_state()

    @Slot()
    def _on_new_story(self) -> None:
        """Handle new story action."""
        logger.debug("New story action triggered")
        dialog = StoryDialog(self._container, self, mode="create")
        if dialog.exec():
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

        dialog = ConfirmDeleteDialog.for_story(story.id, story.name, self)
        if dialog.exec():
            QTimer.singleShot(
                0,
                lambda: asyncio.create_task(
                    self._viewmodel.delete_story(self._viewmodel.selected_story_id)
                ),
            )

    @Slot()
    def _on_duplicate_story(self) -> None:
        """Handle duplicate story action."""
        if not self._viewmodel.selected_story_id:
            return

        story_id = self._viewmodel.selected_story_id
        logger.debug("Duplicate story action triggered for %s", story_id)

        async def _do_duplicate() -> None:
            result = await self._viewmodel.duplicate_story(story_id)
            if result:
                self.statusBar().showMessage(
                    f"Historia duplicada: {story_id} -> {result.id}", 5000
                )

        asyncio.create_task(_do_duplicate())

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
    def _on_config(self) -> None:
        """Handle config action — opens ConfigDialog."""
        from backlog_manager.presentation.views.config_dialog import ConfigDialog

        logger.debug("Config action triggered")
        dialog = ConfigDialog(self._container, self)
        dialog.exec()

    @Slot()
    def _on_about(self) -> None:
        """Handle About dialog action."""
        from backlog_manager.presentation.views.about_dialog import AboutDialog

        dialog = AboutDialog(self._container.db_path, self)
        dialog.exec()

    @Slot()
    def _on_data_changed(self) -> None:
        """Handle data changed from dialogs."""
        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._viewmodel.load_stories())
        )

    # --- Context menu ---

    @Slot()
    def _on_table_context_menu(self, position: QPoint) -> None:
        """Exibe menu de contexto na tabela com 6 acoes."""
        index = self._story_table.indexAt(position)
        if not index.isValid():
            return

        # Select the clicked row
        self._story_table.selectRow(index.row())

        story_id = self._filter_proxy.data(index, Qt.ItemDataRole.UserRole)
        if not story_id:
            return

        menu = QMenu(self)

        # Editar
        edit_action = menu.addAction("Editar\tEnter")
        edit_action.triggered.connect(self._on_edit_story)

        # Duplicar
        duplicate_action = menu.addAction("Duplicar\tCtrl+D")
        duplicate_action.triggered.connect(self._on_duplicate_story)

        menu.addSeparator()

        # Mover Acima / Abaixo — disabled when filters are active
        has_filters = self._filter_proxy.has_active_filters
        move_up_action = menu.addAction("Mover Acima\tAlt+Up")
        move_up_action.setEnabled(not has_filters)
        move_up_action.triggered.connect(self._on_move_up)

        move_down_action = menu.addAction("Mover Abaixo\tAlt+Down")
        move_down_action.setEnabled(not has_filters)
        move_down_action.triggered.connect(self._on_move_down)

        menu.addSeparator()

        # Dependencias
        deps_action = menu.addAction("Dependencias...")
        deps_action.triggered.connect(lambda: self._open_dependency_dialog(story_id))

        menu.addSeparator()

        # Deletar — styled as destructive via property
        delete_action = menu.addAction("Deletar\tDelete")
        delete_action.setProperty("destructive", "true")
        delete_action.triggered.connect(self._on_delete_story)

        menu.exec(self._story_table.viewport().mapToGlobal(position))

    def _open_dependency_dialog(self, story_id: str) -> None:
        """Abre DependencyDialog para a historia selecionada."""
        from backlog_manager.presentation.views.dependency_dialog import (
            DependencyDialog,
        )

        story = None
        for s in self._viewmodel.stories:
            if s.id == story_id:
                story = s
                break

        if not story:
            return

        dialog = DependencyDialog(
            container=self._container,
            story_id=story.id,
            story_name=story.name,
            all_stories=self._viewmodel.stories,
            parent=self,
        )
        dialog.exec()
        # Reload stories to reflect dependency changes
        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._viewmodel.load_stories())
        )

    # --- Reset planning handlers ---

    def _update_has_planning_data(self) -> None:
        """Check if any story has calculated fields and update flag."""
        self._has_planning_data = any(
            s.duration is not None
            or s.start_date is not None
            or s.end_date is not None
            or s.developer_id is not None
            for s in self._viewmodel.stories
        )

    @Slot()
    def _on_new_planning(self) -> None:
        """Handle new planning (reset) action."""
        logger.debug("New planning action triggered")
        QTimer.singleShot(0, lambda: asyncio.create_task(self._execute_new_planning()))

    async def _execute_new_planning(self) -> None:
        """Execute the new planning flow: preview -> confirm -> reset."""
        from backlog_manager.presentation.views.confirm_reset_dialog import (
            ConfirmResetDialog,
        )

        reset_vm = self._container.reset_planning_viewmodel

        # Get preview counts
        counts = await reset_vm.preview()
        if counts is None or counts.total == 0:
            return

        # Show confirmation dialog
        dialog = ConfirmResetDialog(
            with_dates=counts.with_dates,
            with_developer=counts.with_developer,
            parent=self,
        )
        if not dialog.exec():
            return

        # Execute reset
        result = await reset_vm.execute()
        if result and result.success:
            await self._viewmodel.load_stories()

    @Slot()
    def _on_reset_started(self) -> None:
        """Handle reset started signal."""
        self._action_new_planning.setEnabled(False)
        self._action_schedule.setEnabled(False)
        self._action_allocate.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)

    @Slot(object)
    def _on_reset_completed(self, result: ResetPlanningOutputDTO) -> None:
        """Handle reset completed signal."""
        self.setCursor(Qt.CursorShape.ArrowCursor)
        self._action_schedule.setEnabled(True)
        self._action_allocate.setEnabled(True)

        # Update planning data flag
        self._has_planning_data = False
        self._action_new_planning.setEnabled(False)

        # Clear last allocation and show temporary message
        self._last_allocation_time = None
        self._container.status_bar_viewmodel.clear_last_allocation()
        self._update_status_bar_stats()

        # Show temporary reset message in status bar
        self.statusBar().showMessage(
            f"Planejamento resetado: {result.stories_reset} historias", 5000
        )

    # --- Schedule handlers ---

    @Slot()
    def _on_calculate_schedule(self) -> None:
        """Handle schedule calculation action."""
        logger.debug("Schedule calculation action triggered")

        # Get config from ConfigDialogViewModel
        config_vm = self._container.config_dialog_viewmodel
        is_valid, error = config_vm.validate()
        if not is_valid:
            QMessageBox.warning(self, "Configuracao Invalida", error)
            return

        QTimer.singleShot(
            0, lambda: asyncio.create_task(self._execute_schedule_calculation())
        )

    async def _execute_schedule_calculation(self) -> None:
        """Execute schedule calculation with config values."""
        config_vm = self._container.config_dialog_viewmodel
        schedule_vm = self._container.schedule_viewmodel

        await schedule_vm.execute(
            velocity=config_vm.velocity,
            start_date=config_vm.start_date,
        )

        await self._viewmodel.load_stories()

    @Slot()
    def _on_schedule_started(self) -> None:
        """Handle schedule started signal."""
        self._action_schedule.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)

    @Slot(object)
    def _on_schedule_completed(self, result: CalculateScheduleOutputDTO) -> None:
        """Handle schedule completed signal."""
        self._action_schedule.setEnabled(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        if result.stories_updated > 0:
            self._has_planning_data = True
            self._action_new_planning.setEnabled(True)

        QMessageBox.information(
            self,
            "Cronograma Calculado",
            f"{result.stories_updated} historias tiveram datas calculadas.",
        )

    # --- Allocation handlers ---

    @Slot()
    def _on_allocate(self) -> None:
        """Handle automatic allocation action."""
        logger.debug("Allocate action triggered")

        # Get config from ConfigDialogViewModel
        config_vm = self._container.config_dialog_viewmodel
        is_valid, error = config_vm.validate()
        if not is_valid:
            QMessageBox.warning(self, "Configuracao Invalida", error)
            return

        QTimer.singleShot(0, lambda: asyncio.create_task(self._execute_allocation()))

    async def _execute_allocation(self) -> None:
        """Execute allocation with config values and cancellation support."""
        config_vm = self._container.config_dialog_viewmodel
        allocation_vm = self._container.allocation_viewmodel

        # Show progress dialog with cancellation
        progress = CustomProgressDialog("Alocando desenvolvedores...", self)
        progress.show()

        task = asyncio.ensure_future(
            allocation_vm.execute(
                velocity=config_vm.velocity,
                start_date=config_vm.start_date,
                max_idle_days=config_vm.max_idle_days,
            )
        )
        progress.set_cancellable_task(task)

        try:
            await task
        except asyncio.CancelledError:
            pass
        finally:
            progress.close()

        await self._viewmodel.load_stories()

    @Slot()
    def _on_allocation_started(self) -> None:
        """Handle allocation started signal."""
        self._action_allocate.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)

    @Slot(object)
    def _on_allocation_completed(self, metrics: AllocationMetricsDTO) -> None:
        """Handle allocation completed signal. Auto-show MetricsDialog se sucesso."""
        self._action_allocate.setEnabled(True)
        self.setCursor(Qt.CursorShape.ArrowCursor)

        # Update status bar with allocation timestamp
        self._last_allocation_time = datetime.now()
        self._update_status_bar_stats()

        if metrics.stories_allocated > 0:
            self._has_planning_data = True
            self._action_new_planning.setEnabled(True)

        # Auto-show MetricsDialog if stories were allocated (FR-021/FR-022)
        if metrics.stories_allocated > 0:
            from backlog_manager.presentation.views.metrics_dialog import MetricsDialog

            dialog = MetricsDialog(metrics, parent=self)
            dialog.exec()

    @Slot(list)
    def _on_warnings_updated(self, warnings: list[str]) -> None:
        """Handle warnings updated signal."""
        self._current_warnings = warnings
        if warnings:
            self._warnings_badge.setText(f"\u26a0 {len(warnings)} avisos")
            self._warnings_badge.setVisible(True)
        else:
            self._warnings_badge.setVisible(False)

    def _show_warnings_popup(self) -> None:
        """Exibe popup com lista de warnings."""
        if not self._current_warnings:
            return

        text = "\n".join(f"\u2022 {w}" for w in self._current_warnings)
        QMessageBox.information(self, "Avisos da Alocacao", text)

    # --- Status bar ---

    def _update_status_bar_stats(self) -> None:
        """Atualiza label de estatisticas na status bar."""
        stories = self._viewmodel.stories
        story_count = len(stories)
        total_sp = sum(s.story_points or 0 for s in stories)

        allocation_text = "Sem alocacao"
        if self._last_allocation_time is not None:
            allocation_text = (
                f"Ultima alocacao: "
                f"{self._last_allocation_time.strftime('%d/%m/%Y %H:%M')}"
            )

        self._stats_label.setText(
            f"{story_count} historias \u00b7 {total_sp} SP \u00b7 {allocation_text}"
        )

    @Slot()
    def _on_operation_cancelled(self) -> None:
        """Handle operation cancellation from allocation or Excel viewmodels."""
        self._end_excel_operation()
        self._action_allocate.setEnabled(True)
        self.unsetCursor()
        self.statusBar().showMessage("Operacao cancelada", 5000)

    def _update_sp_breakdown(self) -> None:
        """Update SP breakdown label in status bar."""
        stories = self._viewmodel.stories
        vm = self._container.status_bar_viewmodel
        vm.update_sp_breakdown(stories)
        self._sp_breakdown_label.update_breakdown(
            vm.sp_breakdown, vm.sp_total, vm.sp_percentages
        )

    # --- Excel handlers ---

    @property
    def story_table(self) -> StoryTableView:
        """Get the story table view."""
        return self._story_table

    def _start_excel_operation(self, message: str) -> CustomProgressDialog:
        """Start an Excel operation with cancellable progress dialog."""
        self._excel_operation_in_progress = True
        self._action_import_excel.setEnabled(False)
        self._action_export_excel.setEnabled(False)
        self.setCursor(Qt.CursorShape.WaitCursor)

        dialog = CustomProgressDialog(message, self)
        dialog.show()
        self._progress_dialog = dialog
        return dialog

    def _end_excel_operation(self) -> None:
        """End an Excel operation and clean up."""
        self._excel_operation_in_progress = False
        self._action_import_excel.setEnabled(True)
        self._action_export_excel.setEnabled(True)
        self.unsetCursor()

        if self._progress_dialog:
            self._progress_dialog.close()
            self._progress_dialog = None

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
            progress = self._start_excel_operation("Importando dados do Excel...")
            task = asyncio.ensure_future(
                self._container.excel_viewmodel.import_from_file(Path(file_path))
            )
            progress.set_cancellable_task(task)

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
            if Path(file_path).exists():
                reply = QMessageBox.question(
                    self,
                    "Confirmar Substituicao",
                    f"O arquivo {file_path} ja existe. Deseja sobrescrever?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return

            progress = self._start_excel_operation("Exportando dados para Excel...")
            task = asyncio.ensure_future(
                self._container.excel_viewmodel.export_to_file(Path(file_path))
            )
            progress.set_cancellable_task(task)

    @Slot(object)
    def _on_import_completed(self, result) -> None:  # type: ignore[no-untyped-def]
        """Handle import completed signal."""
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
        """Handle import error signal."""
        self._end_excel_operation()
        QMessageBox.critical(self, "Erro na Importacao", error)
        logger.error("Import error: %s", error)

    @Slot(object)
    def _on_export_completed(self, result) -> None:  # type: ignore[no-untyped-def]
        """Handle export completed signal."""
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
        """Handle export error signal."""
        self._end_excel_operation()
        QMessageBox.critical(self, "Erro na Exportacao", error)
        logger.error("Export error: %s", error)
