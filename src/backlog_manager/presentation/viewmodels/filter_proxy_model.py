"""Filter Proxy Model for story table filtering.

This module provides a QSortFilterProxyModel that filters stories
by text, status, and feature with AND logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QSortFilterProxyModel

from backlog_manager.presentation.viewmodels.story_table_model import StoryTableModel

if TYPE_CHECKING:
    from PySide6.QtCore import QObject


class FilterProxyModel(QSortFilterProxyModel):
    """Proxy model that filters StoryTableModel by text, status, and feature.

    Applies filters with AND logic without modifying the source model.
    Column indices are resolved dynamically from StoryTableModel.COLUMNS.
    """

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the filter proxy model.

        Args:
            parent: Optional parent QObject.
        """
        super().__init__(parent)

        self._text_filter: str = ""
        self._status_filter: str | None = None
        self._feature_filter: int | None = None

        # Resolve column indices from StoryTableModel
        self._col_id: int = StoryTableModel.COLUMNS.index("ID")
        self._col_component: int = StoryTableModel.COLUMNS.index("Componente")
        self._col_name: int = StoryTableModel.COLUMNS.index("Nome")
        self._col_status: int = StoryTableModel.COLUMNS.index("Status")

    def set_text_filter(self, text: str) -> None:
        """Set the text filter (case-insensitive). Searches ID, Nome, Componente.

        Args:
            text: Text to filter by. Empty string clears the filter.
        """
        self._text_filter = text.strip().lower()
        self.invalidateFilter()

    def set_status_filter(self, status: str | None) -> None:
        """Set the status filter. None means all statuses.

        Args:
            status: Status string to filter by, or None for all.
        """
        self._status_filter = status
        self.invalidateFilter()

    def set_feature_filter(self, feature_id: int | None) -> None:
        """Set the feature filter. None means all features.

        Args:
            feature_id: Feature ID to filter by, or None for all.
        """
        self._feature_filter = feature_id
        self.invalidateFilter()

    @property
    def has_active_filters(self) -> bool:
        """Check if any filter is currently active.

        Returns:
            True if text, status, or feature filter is active.
        """
        return bool(
            self._text_filter
            or self._status_filter is not None
            or self._feature_filter is not None
        )

    def filterAcceptsRow(
        self, source_row: int, source_parent: QModelIndex | QPersistentModelIndex
    ) -> bool:
        """Apply AND logic of all 3 filters to determine if a row is visible.

        Args:
            source_row: Row index in the source model.
            source_parent: Parent index in the source model.

        Returns:
            True if the row passes all active filters.
        """
        source_model = self.sourceModel()
        if not isinstance(source_model, StoryTableModel):
            return True

        # Text filter: check ID, Nome, Componente (case-insensitive)
        if self._text_filter:
            text = self._text_filter
            id_val = self._get_source_data(source_model, source_row, self._col_id)
            name_val = self._get_source_data(source_model, source_row, self._col_name)
            comp_val = self._get_source_data(
                source_model, source_row, self._col_component
            )

            if not (
                text in id_val.lower()
                or text in name_val.lower()
                or text in comp_val.lower()
            ):
                return False

        # Status filter: exact match
        if self._status_filter is not None:
            status_val = self._get_source_data(
                source_model, source_row, self._col_status
            )
            if status_val != self._status_filter:
                return False

        # Feature filter: check feature_id via get_story_at
        if self._feature_filter is not None:
            story = source_model.get_story_at(source_row)
            if story is None or story.feature_id != self._feature_filter:
                return False

        return True

    def _get_source_data(
        self, source_model: StoryTableModel, row: int, column: int
    ) -> str:
        """Get display data from the source model.

        Args:
            source_model: The source StoryTableModel.
            row: Row index.
            column: Column index.

        Returns:
            Display string value, or empty string if None.
        """
        from PySide6.QtCore import Qt

        index = source_model.index(row, column)
        value = source_model.data(index, Qt.ItemDataRole.DisplayRole)
        return str(value) if value is not None else ""
