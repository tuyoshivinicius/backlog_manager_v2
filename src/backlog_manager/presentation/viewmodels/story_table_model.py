"""Story Table Model for QTableView.

This module provides a QAbstractTableModel implementation for displaying
stories in a table view, following the MVVM pattern.
"""

from __future__ import annotations

from typing import Any, ClassVar, Sequence

from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt

from backlog_manager.application.dto.story import StoryOutputDTO


class StoryTableModel(QAbstractTableModel):
    """Table model for displaying stories in a QTableView.

    This model provides lazy rendering support for efficient display of
    large numbers of stories (500+).

    Attributes:
        COLUMNS: List of column headers displayed in the table.
    """

    COLUMNS: ClassVar[list[str]] = [
        "ID",
        "Nome",
        "SP",
        "Status",
        "Feature",
        "Dev",
        "Inicio",
        "Fim",
    ]

    def __init__(self, parent: Any = None) -> None:
        """Initialize the story table model.

        Args:
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        self._stories: list[StoryOutputDTO] = []

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
        elif role == Qt.ItemDataRole.UserRole:
            # Return the story ID for selection handling
            return story.id

        return None

    def _get_display_value(self, story: StoryOutputDTO, column: int) -> str:
        """Get the display value for a story at a given column.

        Args:
            story: The story DTO.
            column: Column index.

        Returns:
            String representation of the value.
        """
        match column:
            case 0:  # ID
                return story.id
            case 1:  # Nome
                return story.name
            case 2:  # SP
                return str(story.story_points)
            case 3:  # Status
                return story.status
            case 4:  # Feature
                return str(story.feature_id) if story.feature_id else "-"
            case 5:  # Dev
                return str(story.developer_id) if story.developer_id else "-"
            case 6:  # Inicio
                return (
                    story.start_date.strftime("%d/%m/%Y") if story.start_date else "-"
                )
            case 7:  # Fim
                return story.end_date.strftime("%d/%m/%Y") if story.end_date else "-"
            case _:
                return ""

    def _get_alignment(self, column: int) -> Qt.AlignmentFlag:
        """Get the text alignment for a column.

        Args:
            column: Column index.

        Returns:
            Alignment flag for the column.
        """
        # Center-align numeric and date columns
        if column in (2, 4, 5, 6, 7):  # SP, Feature, Dev, Inicio, Fim
            return Qt.AlignmentFlag.AlignCenter
        return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter

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

    def set_stories(self, stories: Sequence[StoryOutputDTO]) -> None:
        """Update the model with new story data.

        This method properly signals the view to refresh all data.

        Args:
            stories: Sequence of story DTOs to display.
        """
        self.beginResetModel()
        self._stories = list(stories)
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
