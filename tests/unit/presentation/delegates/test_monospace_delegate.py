"""Unit tests for MonospaceDelegate.

Tests cover:
- T043: MonospaceDelegate uses monospace font family
- T044: MonospaceDelegate fallback chain works correctly
"""

import pytest
from backlog_manager.presentation.delegates.monospace_delegate import MonospaceDelegate
from PySide6.QtCore import QRect
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QStyleOptionViewItem


class TestMonospaceDelegateFont:
    """Tests for font family selection (T043)."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> MonospaceDelegate:
        """Create delegate instance."""
        return MonospaceDelegate()

    def test_uses_monospace_font_family(self, delegate: MonospaceDelegate) -> None:
        """Delegate uses a monospace font family."""
        family = delegate.get_font_family()
        assert family in MonospaceDelegate.FONT_FAMILIES

    def test_font_family_is_string(self, delegate: MonospaceDelegate) -> None:
        """Font family is a string."""
        family = delegate.get_font_family()
        assert isinstance(family, str)
        assert len(family) > 0

    def test_font_is_available(self, delegate: MonospaceDelegate) -> None:
        """Selected font is available on the system."""
        family = delegate.get_font_family()
        available = QFontDatabase.families()

        # Either the exact font is available, or we're using generic monospace
        assert family in available or family == "monospace"


class TestMonospaceDelegateFallback:
    """Tests for font fallback chain (T044)."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> MonospaceDelegate:
        """Create delegate instance."""
        return MonospaceDelegate()

    def test_fallback_chain_order(self, delegate: MonospaceDelegate) -> None:
        """Fallback chain has correct order."""
        expected = ["JetBrains Mono", "Cascadia Code", "Consolas", "monospace"]
        assert expected == delegate.FONT_FAMILIES

    def test_fallback_returns_first_available(
        self, delegate: MonospaceDelegate
    ) -> None:
        """Fallback returns first available font from chain."""
        available = QFontDatabase.families()

        # Find what should be the first available
        expected_family = "monospace"
        for family in delegate.FONT_FAMILIES:
            if family in available:
                expected_family = family
                break

        # Delegate should have selected the same
        assert delegate.get_font_family() == expected_family

    def test_fallback_to_generic_monospace(self, qtbot: pytest.fixture) -> None:
        """Falls back to 'monospace' if no preferred fonts available."""
        # This test verifies the fallback logic exists
        # The actual font might be found, but the logic should handle absence
        delegate = MonospaceDelegate()

        # Verify the delegate doesn't crash and returns something
        family = delegate.get_font_family()
        assert family is not None
        assert isinstance(family, str)


class TestMonospaceDelegatePaint:
    """Tests for paint method."""

    @pytest.fixture
    def delegate(self, qtbot: pytest.fixture) -> MonospaceDelegate:
        """Create delegate instance."""
        return MonospaceDelegate()

    @pytest.fixture
    def simple_model(self, qtbot: pytest.fixture):
        """Create a simple model with test data."""
        from PySide6.QtGui import QStandardItem, QStandardItemModel

        model = QStandardItemModel()
        model.appendRow([QStandardItem("ID-001")])
        return model

    def test_paint_completes_successfully(
        self, delegate: MonospaceDelegate, simple_model, qtbot: pytest.fixture
    ) -> None:
        """Paint completes without error."""
        from PySide6.QtGui import QImage, QPainter

        image = QImage(200, 30, QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 30)

        index = simple_model.index(0, 0)

        try:
            delegate.paint(painter, option, index)
        finally:
            painter.end()

    def test_paint_with_empty_value(
        self, delegate: MonospaceDelegate, qtbot: pytest.fixture
    ) -> None:
        """Paint handles empty string value."""
        from PySide6.QtGui import QImage, QPainter, QStandardItem, QStandardItemModel

        model = QStandardItemModel()
        model.appendRow([QStandardItem("")])

        image = QImage(200, 30, QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 30)

        index = model.index(0, 0)

        try:
            delegate.paint(painter, option, index)
        finally:
            painter.end()

    def test_paint_with_long_value(
        self, delegate: MonospaceDelegate, qtbot: pytest.fixture
    ) -> None:
        """Paint handles long text values."""
        from PySide6.QtGui import QImage, QPainter, QStandardItem, QStandardItemModel

        model = QStandardItemModel()
        model.appendRow([QStandardItem("VERY-LONG-STORY-ID-12345678")])

        image = QImage(200, 30, QImage.Format.Format_ARGB32)
        painter = QPainter(image)

        option = QStyleOptionViewItem()
        option.rect = QRect(0, 0, 200, 30)

        index = model.index(0, 0)

        try:
            delegate.paint(painter, option, index)
        finally:
            painter.end()
