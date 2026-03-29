"""Integration tests for delegates with QTableView.

Tests cover:
- T080: Delegates work correctly with QTableView
- T025: Updated delegate indices for 13-column model
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
    """Simple model for testing delegates with 13 columns."""

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


def _make_13col_data() -> list[list[str]]:
    """Create sample 13-column data matching the new column order."""
    return [
        [
            "1",
            "Feature A",
            "1",
            "STORY-001",
            "COMP",
            "Story Name",
            "BACKLOG",
            "Dev 1",
            "DEP-001",
            "5",
            "15/01/2026",
            "16/01/2026",
            "2",
        ],
        [
            "2",
            "Feature B",
            "2",
            "STORY-002",
            "API",
            "Another Story",
            "EXECUCAO",
            "Dev 2",
            "\u2014",
            "8",
            "\u2014",
            "\u2014",
            "\u2014",
        ],
        [
            "3",
            "\u2014",
            "\u2014",
            "STORY-003",
            "UI",
            "Third Story",
            "TESTES",
            "\u2014",
            "\u2014",
            "3",
            "17/01/2026",
            "20/01/2026",
            "4",
        ],
        [
            "4",
            "Feature A",
            "1",
            "STORY-004",
            "COMP",
            "Fourth Story",
            "CONCLUIDO",
            "Dev 1",
            "STORY-001, STORY-002",
            "13",
            "21/01/2026",
            "25/01/2026",
            "5",
        ],
        [
            "5",
            "\u2014",
            "\u2014",
            "STORY-005",
            "DB",
            "Fifth Story",
            "IMPEDIDO",
            "\u2014",
            "\u2014",
            "5",
            "\u2014",
            "\u2014",
            "\u2014",
        ],
    ]


class TestDelegatesWithTableView:
    """Integration tests for delegates with QTableView."""

    @pytest.fixture
    def table_view(self, qtbot: pytest.fixture) -> QTableView:
        view = QTableView()
        qtbot.addWidget(view)
        return view

    @pytest.fixture
    def sample_data(self) -> list[list[str]]:
        return _make_13col_data()

    def test_status_badge_delegate_at_column_6(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """StatusBadgeDelegate renders at column 6 (Status) without errors."""
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)
        delegate = StatusBadgeDelegate(table_view)
        table_view.setItemDelegateForColumn(6, delegate)
        table_view.show()
        assert table_view.isVisible()
        assert table_view.itemDelegateForColumn(6) == delegate

    def test_monospace_delegate_at_column_3(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """MonospaceDelegate renders at column 3 (ID) without errors."""
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)
        delegate = MonospaceDelegate(table_view)
        table_view.setItemDelegateForColumn(3, delegate)
        table_view.show()
        assert table_view.isVisible()
        assert table_view.itemDelegateForColumn(3) == delegate

    def test_both_delegates_at_new_indices(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """Both delegates work at new indices (ID=3, Status=6) in 13-column table."""
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)

        monospace_delegate = MonospaceDelegate(table_view)
        status_delegate = StatusBadgeDelegate(table_view)

        table_view.setItemDelegateForColumn(3, monospace_delegate)
        table_view.setItemDelegateForColumn(6, status_delegate)

        table_view.show()

        assert table_view.itemDelegateForColumn(3) == monospace_delegate
        assert table_view.itemDelegateForColumn(6) == status_delegate
        assert model.columnCount() == 13

    def test_delegate_handles_selection(
        self,
        table_view: QTableView,
        sample_data: list[list[str]],
        qtbot: pytest.fixture,
    ) -> None:
        """Delegates handle row selection correctly."""
        model = SimpleTableModel(sample_data)
        table_view.setModel(model)
        status_delegate = StatusBadgeDelegate(table_view)
        table_view.setItemDelegateForColumn(6, status_delegate)
        table_view.show()

        index = model.index(0, 0)
        table_view.setCurrentIndex(index)
        assert table_view.currentIndex() == index


class TestDelegatePerformance:
    """Performance tests for delegates."""

    @pytest.fixture
    def table_view(self, qtbot: pytest.fixture) -> QTableView:
        view = QTableView()
        qtbot.addWidget(view)
        return view

    def test_status_badge_delegate_performance(
        self, table_view: QTableView, qtbot: pytest.fixture
    ) -> None:
        """StatusBadgeDelegate renders many cells efficiently."""
        import time

        statuses = ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"]
        data = [
            [
                str(i),
                "\u2014",
                "\u2014",
                f"STORY-{i:04d}",
                "COMP",
                "Name",
                statuses[i % 5],
                "\u2014",
                "\u2014",
                "5",
                "\u2014",
                "\u2014",
                "\u2014",
            ]
            for i in range(100)
        ]
        model = SimpleTableModel(data)
        table_view.setModel(model)
        delegate = StatusBadgeDelegate(table_view)
        table_view.setItemDelegateForColumn(6, delegate)
        table_view.show()

        start = time.perf_counter()
        table_view.viewport().update()
        QApplication.processEvents()
        elapsed = time.perf_counter() - start

        assert elapsed < 2.0, f"Rendering 100 cells took {elapsed:.2f}s"
