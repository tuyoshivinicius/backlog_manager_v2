"""Open Planning Dialog View.

This module provides a dialog for listing, selecting, renaming,
and deleting plannings.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from backlog_manager.application.dto.planning.planning_dto import PlanningListItem

logger = logging.getLogger(__name__)

_COL_NAME = 0
_COL_STORIES = 1
_COL_MODIFIED = 2
_COL_ACTIONS = 3


class _ActionWidget(QWidget):
    """Widget containing edit and delete action buttons for a planning row."""

    edit_clicked = Signal()
    delete_clicked = Signal()

    def __init__(self, show_delete: bool = True, parent: QWidget | None = None) -> None:
        """Initialize action buttons.

        Args:
            show_delete: Whether to show the delete button.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 0, 2, 0)
        layout.setSpacing(4)

        self._edit_button = QPushButton("\u270f")
        self._edit_button.setObjectName("planning-action-edit")
        self._edit_button.setFixedSize(28, 28)
        self._edit_button.setToolTip("Renomear")
        self._edit_button.clicked.connect(self.edit_clicked)
        layout.addWidget(self._edit_button)

        if show_delete:
            self._delete_button = QPushButton("\U0001f5d1")
            self._delete_button.setObjectName("planning-action-delete")
            self._delete_button.setFixedSize(28, 28)
            self._delete_button.setToolTip("Excluir")
            self._delete_button.clicked.connect(self.delete_clicked)
            layout.addWidget(self._delete_button)

        layout.addStretch()


class OpenPlanningDialog(QDialog):
    """Dialog for opening/selecting a planning.

    Displays a table of plannings with inline rename and delete actions.
    The active planning is marked with a bullet prefix and cannot be deleted.

    Signals:
        rename_requested: Emitted when a rename is confirmed (planning_id, new_name).
        delete_requested: Emitted when delete is clicked (planning_id).
    """

    rename_requested = Signal(int, str)
    delete_requested = Signal(int)

    def __init__(
        self,
        plannings: list[PlanningListItem],
        active_planning_id: int,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            plannings: List of planning items to display.
            active_planning_id: ID of the currently active planning.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._plannings = plannings
        self._active_planning_id = active_planning_id
        self._selected_planning_id: int | None = None
        self._editing_row: int | None = None

        self._setup_ui()
        self._populate_table()

        logger.debug(
            "OpenPlanningDialog initialized: %d plannings, active_id=%d",
            len(plannings),
            active_planning_id,
        )

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setObjectName("open-planning-dialog")
        self.setWindowTitle("Abrir Planejamento")
        self.setMinimumWidth(550)
        self.setMinimumHeight(350)
        self.setModal(True)

        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Abrir Planejamento")
        title_label.setObjectName("open-planning-title")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Empty state label
        self._empty_label = QLabel("Nenhum planejamento encontrado")
        self._empty_label.setObjectName("open-planning-empty-label")
        self._empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._empty_label.hide()
        main_layout.addWidget(self._empty_label)

        # Table
        self._table = QTableWidget()
        self._table.setObjectName("open-planning-table")
        self._table.setColumnCount(4)
        self._table.setHorizontalHeaderLabels(
            ["Nome", "Historias", "Modificado", "Acoes"]
        )
        self._table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._table.verticalHeader().setVisible(False)
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.horizontalHeader().setSectionResizeMode(
            _COL_NAME, QHeaderView.ResizeMode.Stretch
        )
        self._table.horizontalHeader().setSectionResizeMode(
            _COL_STORIES, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            _COL_MODIFIED, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.horizontalHeader().setSectionResizeMode(
            _COL_ACTIONS, QHeaderView.ResizeMode.ResizeToContents
        )
        self._table.doubleClicked.connect(self._on_double_click)
        self._table.itemSelectionChanged.connect(self._on_selection_changed)
        self._table.itemChanged.connect(self._on_item_changed)
        main_layout.addWidget(self._table)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("open-planning-cancel-button")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        self._open_button = QPushButton("Abrir")
        self._open_button.setObjectName("open-planning-open-button")
        self._open_button.setDefault(True)
        self._open_button.setEnabled(False)
        self._open_button.clicked.connect(self._on_open_clicked)
        button_layout.addWidget(self._open_button)

        main_layout.addLayout(button_layout)

    def _populate_table(self) -> None:
        """Populate the table with planning data."""
        if not self._plannings:
            self._table.hide()
            self._empty_label.show()
            return

        self._empty_label.hide()
        self._table.show()
        self._table.setRowCount(len(self._plannings))

        for row, planning in enumerate(self._plannings):
            is_active = planning.id == self._active_planning_id

            # Name column
            display_name = f"\u25cf {planning.name}" if is_active else planning.name
            name_item = QTableWidgetItem(display_name)
            name_item.setData(Qt.ItemDataRole.UserRole, planning.id)
            name_item.setFlags(name_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, _COL_NAME, name_item)

            # Story count column
            stories_item = QTableWidgetItem(str(planning.story_count))
            stories_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            stories_item.setFlags(stories_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, _COL_STORIES, stories_item)

            # Modified column
            modified_text = (
                planning.updated_at.strftime("%d/%m/%Y %H:%M")
                if planning.updated_at
                else "-"
            )
            modified_item = QTableWidgetItem(modified_text)
            modified_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            modified_item.setFlags(modified_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
            self._table.setItem(row, _COL_MODIFIED, modified_item)

            # Actions column
            action_widget = _ActionWidget(show_delete=not is_active)
            action_widget.edit_clicked.connect(lambda r=row: self._on_edit_clicked(r))
            if not is_active:
                action_widget.delete_clicked.connect(
                    lambda pid=planning.id: self._on_delete_clicked(pid)
                )
            self._table.setCellWidget(row, _COL_ACTIONS, action_widget)

    def _get_planning_id_for_row(self, row: int) -> int | None:
        """Get planning ID for a table row.

        Args:
            row: Table row index.

        Returns:
            Planning ID or None if not found.
        """
        item = self._table.item(row, _COL_NAME)
        if item is None:
            return None
        return item.data(Qt.ItemDataRole.UserRole)

    def _get_raw_name(self, row: int) -> str:
        """Get the raw planning name without bullet prefix.

        Args:
            row: Table row index.

        Returns:
            The planning name without any prefix.
        """
        planning_id = self._get_planning_id_for_row(row)
        for planning in self._plannings:
            if planning.id == planning_id:
                return planning.name
        return ""

    @Slot()
    def _on_selection_changed(self) -> None:
        """Handle table selection changes."""
        selected_rows = self._table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self._selected_planning_id = self._get_planning_id_for_row(row)
        else:
            self._selected_planning_id = None
        self._open_button.setEnabled(self._selected_planning_id is not None)

    @Slot()
    def _on_double_click(self) -> None:
        """Handle double-click on a table row."""
        selected_rows = self._table.selectionModel().selectedRows()
        if selected_rows:
            row = selected_rows[0].row()
            self._selected_planning_id = self._get_planning_id_for_row(row)
            self.accept()

    @Slot()
    def _on_open_clicked(self) -> None:
        """Handle open button click."""
        if self._selected_planning_id is not None:
            self.accept()

    def _on_edit_clicked(self, row: int) -> None:
        """Start inline editing of a planning name.

        Args:
            row: Table row to edit.
        """
        self._editing_row = row
        name_item = self._table.item(row, _COL_NAME)
        if name_item is None:
            return

        # Set the raw name (without bullet) for editing
        raw_name = self._get_raw_name(row)
        name_item.setFlags(name_item.flags() | Qt.ItemFlag.ItemIsEditable)

        self._table.blockSignals(True)
        name_item.setText(raw_name)
        self._table.blockSignals(False)

        self._table.editItem(name_item)

    def _on_delete_clicked(self, planning_id: int) -> None:
        """Handle delete button click.

        Args:
            planning_id: ID of the planning to delete.
        """
        logger.debug("Delete requested for planning id=%d", planning_id)
        self.delete_requested.emit(planning_id)

    @Slot(QTableWidgetItem)
    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        """Handle item content changes (inline rename).

        Args:
            item: The changed table item.
        """
        if item.column() != _COL_NAME:
            return
        if self._editing_row is None:
            return

        row = item.row()
        if row != self._editing_row:
            return

        self._editing_row = None
        new_name = item.text().strip()
        planning_id = self._get_planning_id_for_row(row)

        # Restore non-editable flag
        item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEditable)

        if not new_name or planning_id is None:
            # Restore original name
            is_active = planning_id == self._active_planning_id
            raw_name = self._get_raw_name(row)
            display_name = f"\u25cf {raw_name}" if is_active else raw_name
            self._table.blockSignals(True)
            item.setText(display_name)
            self._table.blockSignals(False)
            return

        # Check if name actually changed
        old_name = self._get_raw_name(row)
        if new_name == old_name:
            is_active = planning_id == self._active_planning_id
            display_name = f"\u25cf {new_name}" if is_active else new_name
            self._table.blockSignals(True)
            item.setText(display_name)
            self._table.blockSignals(False)
            return

        # Restore display with bullet if active
        is_active = planning_id == self._active_planning_id
        display_name = f"\u25cf {new_name}" if is_active else new_name
        self._table.blockSignals(True)
        item.setText(display_name)
        self._table.blockSignals(False)

        logger.debug(
            "Rename requested: planning_id=%d, new_name='%s'", planning_id, new_name
        )
        self.rename_requested.emit(planning_id, new_name)

    def get_selected_planning_id(self) -> int | None:
        """Get the ID of the selected planning.

        Returns:
            The selected planning ID if accepted, None otherwise.
        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self._selected_planning_id
        return None
