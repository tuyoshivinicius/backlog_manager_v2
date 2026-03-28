"""Unit tests for StatusBadgeDelegate.

Tests cover:
- T034: paint() renders correct symbol per status
- T035: uses correct colors per status
- T036: sizeHint() returns minimum height
- T037: handles unknown status gracefully
"""

from unittest.mock import MagicMock, patch

import pytest
from PySide6.QtCore import QModelIndex, QRect, QSize, Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import QStyleOptionViewItem

from backlog_manager.presentation.delegates.status_badge_delegate import (
    StatusBadgeDelegate,
)
from backlog_manager.presentation.theme import STATUS_PALETTE


class TestStatusBadgeDelegateSymbols:
    """Tests for symbol rendering (T034)."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> StatusBadgeDelegate:
        """Create delegate instance."""
        return StatusBadgeDelegate()

    def test_backlog_symbol(self, delegate: StatusBadgeDelegate) -> None:
        """BACKLOG status uses ● symbol."""
        config = STATUS_PALETTE.get("BACKLOG")
        assert config is not None
        assert config.symbol == "●"

    def test_execucao_symbol(self, delegate: StatusBadgeDelegate) -> None:
        """EXECUCAO status uses ▶ symbol."""
        config = STATUS_PALETTE.get("EXECUCAO")
        assert config is not None
        assert config.symbol == "▶"

    def test_testes_symbol(self, delegate: StatusBadgeDelegate) -> None:
        """TESTES status uses ◆ symbol."""
        config = STATUS_PALETTE.get("TESTES")
        assert config is not None
        assert config.symbol == "◆"

    def test_concluido_symbol(self, delegate: StatusBadgeDelegate) -> None:
        """CONCLUIDO status uses ✓ symbol."""
        config = STATUS_PALETTE.get("CONCLUIDO")
        assert config is not None
        assert config.symbol == "✓"

    def test_impedido_symbol(self, delegate: StatusBadgeDelegate) -> None:
        """IMPEDIDO status uses ✕ symbol."""
        config = STATUS_PALETTE.get("IMPEDIDO")
        assert config is not None
        assert config.symbol == "✕"


class TestStatusBadgeDelegateColors:
    """Tests for color usage (T035)."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> StatusBadgeDelegate:
        """Create delegate instance."""
        return StatusBadgeDelegate()

    def test_backlog_colors(self, delegate: StatusBadgeDelegate) -> None:
        """BACKLOG uses gray background with dark text."""
        config = STATUS_PALETTE.get("BACKLOG")
        assert config is not None
        assert config.background == "#E5E5E5"
        assert config.foreground == "#525252"

    def test_execucao_colors(self, delegate: StatusBadgeDelegate) -> None:
        """EXECUCAO uses blue background with dark blue text."""
        config = STATUS_PALETTE.get("EXECUCAO")
        assert config is not None
        assert config.background == "#DBEAFE"
        assert config.foreground == "#1E40AF"

    def test_testes_colors(self, delegate: StatusBadgeDelegate) -> None:
        """TESTES uses amber background with dark amber text."""
        config = STATUS_PALETTE.get("TESTES")
        assert config is not None
        assert config.background == "#FEF3C7"
        assert config.foreground == "#B45309"

    def test_concluido_colors(self, delegate: StatusBadgeDelegate) -> None:
        """CONCLUIDO uses green background with dark green text."""
        config = STATUS_PALETTE.get("CONCLUIDO")
        assert config is not None
        assert config.background == "#DDF3E4"
        assert config.foreground == "#18794E"

    def test_impedido_colors(self, delegate: StatusBadgeDelegate) -> None:
        """IMPEDIDO uses red background with dark red text."""
        config = STATUS_PALETTE.get("IMPEDIDO")
        assert config is not None
        assert config.background == "#FECACA"
        # Dark red for WCAG AA compliance
        assert config.foreground == "#991B1B"


class TestStatusBadgeDelegateSizeHint:
    """Tests for sizeHint (T036)."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> StatusBadgeDelegate:
        """Create delegate instance."""
        return StatusBadgeDelegate()

    def test_size_hint_returns_qsize(self, delegate: StatusBadgeDelegate) -> None:
        """sizeHint returns QSize instance."""
        option = QStyleOptionViewItem()
        index = MagicMock(spec=QModelIndex)

        result = delegate.sizeHint(option, index)

        assert isinstance(result, QSize)

    def test_size_hint_minimum_height(self, delegate: StatusBadgeDelegate) -> None:
        """sizeHint returns at least MIN_BADGE_HEIGHT."""
        option = QStyleOptionViewItem()
        index = MagicMock(spec=QModelIndex)

        result = delegate.sizeHint(option, index)

        assert result.height() >= delegate.MIN_BADGE_HEIGHT

    def test_size_hint_minimum_width(self, delegate: StatusBadgeDelegate) -> None:
        """sizeHint returns at least MIN_BADGE_WIDTH."""
        option = QStyleOptionViewItem()
        index = MagicMock(spec=QModelIndex)

        result = delegate.sizeHint(option, index)

        assert result.width() >= delegate.MIN_BADGE_WIDTH


class TestStatusBadgeDelegateUnknownStatus:
    """Tests for unknown status handling (T037)."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> StatusBadgeDelegate:
        """Create delegate instance."""
        return StatusBadgeDelegate()

    def test_unknown_status_uses_default_config(
        self, delegate: StatusBadgeDelegate
    ) -> None:
        """Unknown status falls back to default configuration."""
        # Default config is set in delegate's __init__
        assert delegate._default_config is not None
        assert delegate._default_config.symbol == "?"
        assert delegate._default_config.background == "#E5E5E5"
        assert delegate._default_config.foreground == "#525252"

    def test_unknown_status_does_not_raise(
        self, delegate: StatusBadgeDelegate, qtbot: pytest.fixture
    ) -> None:
        """Unknown status does not raise exception in paint."""
        from PySide6.QtGui import QImage, QPainter

        # Create minimal context for paint
        image = QImage(200, 50, QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 50)

        index = MagicMock(spec=QModelIndex)
        index.data.return_value = "UNKNOWN_STATUS"

        # Should not raise
        try:
            delegate.paint(painter, option, index)
        finally:
            painter.end()

    def test_none_value_delegates_to_super(
        self, delegate: StatusBadgeDelegate, qtbot: pytest.fixture
    ) -> None:
        """None value delegates to parent class paint."""
        from PySide6.QtGui import QImage, QPainter, QStandardItem, QStandardItemModel

        # Create a model with an empty item (will return None for display role)
        model = QStandardItemModel()
        item = QStandardItem()
        item.setData(None, Qt.ItemDataRole.DisplayRole)
        model.appendRow([item])

        image = QImage(200, 50, QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 50)

        index = model.index(0, 0)

        # Should not raise
        try:
            delegate.paint(painter, option, index)
        finally:
            painter.end()


class TestStatusBadgeDelegatePaint:
    """Tests for paint method."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> StatusBadgeDelegate:
        """Create delegate instance."""
        return StatusBadgeDelegate()

    def test_paint_known_status(
        self, delegate: StatusBadgeDelegate, qtbot: pytest.fixture
    ) -> None:
        """Paint completes successfully for known status."""
        from PySide6.QtGui import QImage, QPainter

        image = QImage(200, 50, QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 50)

        index = MagicMock(spec=QModelIndex)
        index.data.return_value = "BACKLOG"

        try:
            delegate.paint(painter, option, index)
        finally:
            painter.end()

    def test_paint_case_insensitive(
        self, delegate: StatusBadgeDelegate, qtbot: pytest.fixture
    ) -> None:
        """Paint handles lowercase status values."""
        from PySide6.QtGui import QImage, QPainter

        image = QImage(200, 50, QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 50)

        index = MagicMock(spec=QModelIndex)
        index.data.return_value = "backlog"  # lowercase

        try:
            delegate.paint(painter, option, index)
        finally:
            painter.end()
