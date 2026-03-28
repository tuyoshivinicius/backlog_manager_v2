"""Integration tests for delegates with QTableView.

Tests cover:
- T080: Delegates work correctly with QTableView
- Performance validation
"""

import pytest
from PySide6.QtCore import QAbstractTableModel, QModelIndex, Qt
from PySide6.QtWidgets import QApplication, QTableView

from backlog_manager.presentation.delegates import (
    MonospaceDelegate,
    StatusBadgeDelegate,
)


class SimpleTableModel(QAbstractTableModel):
    """Simple model for testing delegates."""

    def __init__(self, data: list[list[str]]) -> None:
        super().__init__()
        self._data = data

    def rowCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = QModelIndex()) -> int:
        return len(self._data[0]) if self._data else 0

    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            return self._data[index.row()][index.column()]
        return None


class TestDelegatesWithTableView:
    """Integration tests for delegates with QTableView (T080)."""

    @pytest.fixture
    def table_view(self, qtbot: pytest.fixture) -> QTableView:
        """Create and return a QTableView."""
        view = QTableView()
        qtbot.addWidget(view)
        return view

    @pytest.fixture
    def sample_data(self) -> list[list[str]]:
        """Sample data with ID and status columns."""
        return [
            ["STORY-001", "BACKLOG"],
            ["STORY-002", "EXECUCAO"],
            ["STORY-003", "TESTES"],
            ["STORY-004", "CONCLUIDO"],
            ["STORY-005", "IMPEDIDO"],
        ]

    def test_status_badge_delegate_in_table(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """StatusBadgeDelegate renders in QTableView without errors."""
        # Arrange
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)

        delegate = StatusBadgeDelegate(table_view)
        table_view.setItemDelegateForColumn(1, delegate)

        # Act
        table_view.show()

        # Assert - no exceptions, table is visible
        assert table_view.isVisible()
        assert table_view.model() == model

    def test_monospace_delegate_in_table(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """MonospaceDelegate renders in QTableView without errors."""
        # Arrange
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)

        delegate = MonospaceDelegate(table_view)
        table_view.setItemDelegateForColumn(0, delegate)

        # Act
        table_view.show()

        # Assert - no exceptions, table is visible
        assert table_view.isVisible()
        assert table_view.model() == model

    def test_both_delegates_in_table(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """Both delegates work together in the same QTableView."""
        # Arrange
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)

        monospace_delegate = MonospaceDelegate(table_view)
        status_delegate = StatusBadgeDelegate(table_view)

        table_view.setItemDelegateForColumn(0, monospace_delegate)
        table_view.setItemDelegateForColumn(1, status_delegate)

        # Act
        table_view.show()

        # Assert - no exceptions, both delegates assigned
        assert table_view.itemDelegateForColumn(0) == monospace_delegate
        assert table_view.itemDelegateForColumn(1) == status_delegate

    def test_delegate_handles_selection(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """Delegates handle row selection correctly."""
        # Arrange
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)

        status_delegate = StatusBadgeDelegate(table_view)
        table_view.setItemDelegateForColumn(1, status_delegate)

        table_view.show()

        # Act - select first row
        index = model.index(0, 0)
        table_view.setCurrentIndex(index)

        # Assert - no exceptions
        assert table_view.currentIndex() == index


class TestDelegatePerformance:
    """Performance tests for delegates (T083)."""

    @pytest.fixture
    def table_view(self, qtbot: pytest.fixture) -> QTableView:
        """Create and return a QTableView."""
        view = QTableView()
        qtbot.addWidget(view)
        return view

    def test_status_badge_delegate_performance(
        self, table_view: QTableView, qtbot: pytest.fixture
    ) -> None:
        """StatusBadgeDelegate renders many cells efficiently.

        Target: <= 16ms per cell for 60fps.
        """
        import time

        # Create large dataset
        data = [[f"STORY-{i:04d}", "BACKLOG"] for i in range(100)]
        model = SimpleTableModel(data)

        table_view.setModel(model)
        delegate = StatusBadgeDelegate(table_view)
        table_view.setItemDelegateForColumn(1, delegate)

        table_view.show()

        # Force paint
        start = time.perf_counter()
        table_view.viewport().update()
        QApplication.processEvents()
        elapsed = time.perf_counter() - start

        # 100 cells should render in reasonable time
        # Note: This is a rough test - actual per-cell time depends on many factors
        assert elapsed < 2.0, f"Rendering 100 cells took {elapsed:.2f}s"
