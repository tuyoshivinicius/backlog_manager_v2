"""Story Table Model for QTableView.

This module provides a QAbstractTableModel implementation for displaying
stories in a table view, following the MVVM pattern.
"""

from __future__ import annotations

from enum import StrEnum
from typing import Any, ClassVar, Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt, Signal
from PySide6.QtGui import QColor

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.theme import WAVE_PALETTE


class BlockingState(StrEnum):
    """Blocking state of a story based on its dependencies."""

    BLOCKED = "BLOCKED"
    FREE = "FREE"
    NONE = "NONE"


# Custom data roles for dependency column
BLOCKING_STATE_ROLE = Qt.ItemDataRole.UserRole + 1
DEPENDENCY_IDS_ROLE = Qt.ItemDataRole.UserRole + 2


class StoryTableModel(QAbstractTableModel):
    """Table model for displaying stories in a QTableView.

    This model provides lazy rendering support for efficient display of
    large numbers of stories (500+).

    Attributes:
        COLUMNS: List of column headers displayed in the table.
    """

    status_change_requested = Signal(str, str)  # (story_id, new_status)

    COLUMNS: ClassVar[list[str]] = [
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

    COLUMN_WIDTHS: ClassVar[list[int]] = [
        60,
        120,
        50,
        100,
        80,
        -1,
        100,
        100,
        120,
        40,
        90,
        90,
        60,
    ]

    CENTER_COLUMNS: ClassVar[set[int]] = {0, 2, 6, 9, 10, 11, 12}

    TOOLTIP_COLUMNS: ClassVar[set[int]] = {1, 5, 7, 8}

    def __init__(self, parent: Any = None) -> None:
        """Initialize the story table model.

        Args:
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        self._stories: list[StoryOutputDTO] = []
        self._story_status_map: dict[str, str] = {}

    def rowCount(self, parent: QModelIndex | None = None) -> int:
        """Return the number of rows in the model.

        Args:
            parent: Parent index (unused for flat table).

        Returns:
            Number of stories in the model.
        """
        if parent is not None and parent.isValid():
            return 0
        return len(self._stories)

    def columnCount(self, parent: QModelIndex | None = None) -> int:
        """Return the number of columns in the model.

        Args:
            parent: Parent index (unused for flat table).

        Returns:
            Number of columns (fixed).
        """
        if parent is not None and parent.isValid():
            return 0
        return len(self.COLUMNS)

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        """Return data for the given index and role.

        Args:
            index: Model index specifying row and column.
            role: Data role (DisplayRole, TextAlignmentRole, etc.).

        Returns:
            Data for the cell, or None if invalid.
        """
        if not index.isValid():
            return None

        row = index.row()
        col = index.column()

        if row < 0 or row >= len(self._stories):
            return None

        story = self._stories[row]

        if role == Qt.ItemDataRole.DisplayRole:
            return self._get_display_value(story, col)
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            return self._get_alignment(col)
        elif role == Qt.ItemDataRole.ToolTipRole:
            return self._get_tooltip(story, col)
        elif role == Qt.ItemDataRole.BackgroundRole:
            return self._get_wave_background(story.wave)
        elif role == Qt.ItemDataRole.UserRole:
            return story.id
        elif role == BLOCKING_STATE_ROLE and col == 8:
            return self._get_blocking_state(story)
        elif role == DEPENDENCY_IDS_ROLE and col == 8:
            return story.dependency_ids

        return None

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        """Return item flags, making the Status column editable."""
        base_flags = super().flags(index)
        if index.isValid() and index.column() == 6:  # Status column
            return base_flags | Qt.ItemFlag.ItemIsEditable
        return base_flags

    def setData(
        self, index: QModelIndex, value: Any, role: int = Qt.ItemDataRole.EditRole
    ) -> bool:
        """Handle inline status edit by emitting a signal."""
        if not index.isValid() or role != Qt.ItemDataRole.EditRole:
            return False
        if index.column() != 6:
            return False
        story = self._stories[index.row()]
        new_status = str(value).upper()
        if new_status == story.status:
            return False
        self.status_change_requested.emit(story.id, new_status)
        return False  # Don't update locally; wait for use case reload

    def _get_display_value(self, story: StoryOutputDTO, column: int) -> str:
        """Get the display value for a story at a given column.

        Args:
            story: The story DTO.
            column: Column index.

        Returns:
            String representation of the value.
        """
        match column:
            case 0:  # Prioridade
                return str(story.priority)
            case 1:  # Feature
                return story.feature_name if story.feature_name else "\u2014"
            case 2:  # Onda
                return str(story.wave) if story.wave > 0 else "\u2014"
            case 3:  # ID
                return story.id
            case 4:  # Componente
                return story.component if story.component else "\u2014"
            case 5:  # Nome
                return story.name
            case 6:  # Status
                return story.status
            case 7:  # Desenvolvedor
                return story.developer_name if story.developer_name else "\u2014"
            case 8:  # Dependencias
                return (
                    ", ".join(story.dependency_ids)
                    if story.dependency_ids
                    else "\u2014"
                )
            case 9:  # SP
                return str(story.story_points)
            case 10:  # Inicio
                return (
                    story.start_date.strftime("%d/%m/%Y")
                    if story.start_date
                    else "\u2014"
                )
            case 11:  # Fim
                return (
                    story.end_date.strftime("%d/%m/%Y") if story.end_date else "\u2014"
                )
            case 12:  # Duracao
                return str(story.duration) if story.duration is not None else "\u2014"
            case _:
                return ""

    def _get_alignment(self, column: int) -> Qt.AlignmentFlag:
        """Get the text alignment for a column.

        Args:
            column: Column index.

        Returns:
            Alignment flag for the column.
        """
        if column in self.CENTER_COLUMNS:
            return Qt.AlignmentFlag.AlignCenter
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

    def _get_tooltip(self, story: StoryOutputDTO, column: int) -> str | None:
        """Get the tooltip text for a story at a given column.

        Args:
            story: The story DTO.
            column: Column index.

        Returns:
            Tooltip text, or None if no tooltip for this column.
        """
        if column not in self.TOOLTIP_COLUMNS:
            return None
        return self._get_display_value(story, column)

    def headerData(
        self,
        section: int,
        orientation: Qt.Orientation,
        role: int = Qt.ItemDataRole.DisplayRole,
    ) -> Any:
        """Return header data for the given section.

        Args:
            section: Row or column index.
            orientation: Horizontal or vertical.
            role: Data role.

        Returns:
            Header text or None.
        """
        if role != Qt.ItemDataRole.DisplayRole:
            return None

        if orientation == Qt.Orientation.Horizontal:
            if 0 <= section < len(self.COLUMNS):
                return self.COLUMNS[section]
        elif orientation == Qt.Orientation.Vertical:
            return str(section + 1)

        return None

    def _get_wave_background(self, wave: int) -> QColor | None:
        """Get the background color for a wave value.

        Args:
            wave: Wave number (0 = no wave).

        Returns:
            QColor for the wave tint, or None for default background.
        """
        if wave <= 0:
            return None
        palette_idx = ((wave - 1) % (len(WAVE_PALETTE) - 1)) + 1
        color_hex = WAVE_PALETTE[palette_idx]
        return QColor(color_hex) if color_hex else None

    def _get_blocking_state(self, story: StoryOutputDTO) -> BlockingState:
        """Get the blocking state of a story based on its dependencies.

        Args:
            story: The story DTO.

        Returns:
            BlockingState enum value.
        """
        if not story.dependency_ids:
            return BlockingState.NONE

        for dep_id in story.dependency_ids:
            dep_status = self._story_status_map.get(dep_id)
            if dep_status is None or dep_status != "CONCLUIDO":
                return BlockingState.BLOCKED

        return BlockingState.FREE

    def set_stories(self, stories: Sequence[StoryOutputDTO]) -> None:
        """Update the model with new story data.

        This method properly signals the view to refresh all data.

        Args:
            stories: Sequence of story DTOs to display.
        """
        self.beginResetModel()
        self._stories = list(stories)
        self._story_status_map = {s.id: s.status for s in self._stories}
        self.endResetModel()

    def get_story_at(self, row: int) -> StoryOutputDTO | None:
        """Get the story at a given row index.

        Args:
            row: Row index.

        Returns:
            Story DTO at the row, or None if invalid.
        """
        if 0 <= row < len(self._stories):
            return self._stories[row]
        return None

    def get_story_by_id(self, story_id: str) -> StoryOutputDTO | None:
        """Get a story by its ID.

        Args:
            story_id: The story ID to find.

        Returns:
            Story DTO if found, or None.
        """
        for story in self._stories:
            if story.id == story_id:
                return story
        return None

    def get_row_for_story(self, story_id: str) -> int:
        """Get the row index for a story ID.

        Args:
            story_id: The story ID to find.

        Returns:
            Row index, or -1 if not found.
        """
        for i, story in enumerate(self._stories):
            if story.id == story_id:
                return i
        return -1

    @property
    def stories(self) -> list[StoryOutputDTO]:
        """Get the current list of stories.

        Returns:
            List of story DTOs.
        """
        return self._stories.copy()
