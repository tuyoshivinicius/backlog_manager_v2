"""E2E tests for responsive column hiding in MainWindow.

Tests verify that columns are hidden/shown based on window width.
"""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSize

from backlog_manager.presentation.views.main_window import MainWindow

pytestmark = [pytest.mark.e2e]


class TestResponsiveColumnHiding:
    """Tests for responsive column hiding on resize."""

    def test_columns_visible_at_wide_width(self, e2e_main_window: MainWindow, qtbot):
        """At >= 1024px width, responsive columns are visible."""
        e2e_main_window.resize(1280, 720)
        qtbot.waitExposed(e2e_main_window)

        table = e2e_main_window._story_table
        for col in e2e_main_window._responsive_columns:
            assert not table.isColumnHidden(col), f"Column {col} should be visible"

    def test_columns_hidden_at_narrow_width(self, e2e_main_window: MainWindow, qtbot):
        """At < 1024px width, responsive columns are hidden."""
        e2e_main_window.resize(900, 720)
        qtbot.waitExposed(e2e_main_window)

        # Process resize event
        from PySide6.QtWidgets import QApplication

        QApplication.processEvents()

        table = e2e_main_window._story_table
        for col in e2e_main_window._responsive_columns:
            assert table.isColumnHidden(col), f"Column {col} should be hidden"

    def test_hidden_columns_label_shown(self, e2e_main_window: MainWindow, qtbot):
        """Hidden columns label is visible when columns are hidden."""
        e2e_main_window.resize(900, 720)

        from PySide6.QtWidgets import QApplication

        QApplication.processEvents()

        label = e2e_main_window._hidden_columns_label
        assert label.isVisible()
        assert "colunas ocultas" in label.text()

    def test_columns_restored_on_widen(self, e2e_main_window: MainWindow, qtbot):
        """Columns are restored when window is widened back."""
        # First narrow
        e2e_main_window.resize(900, 720)
        from PySide6.QtWidgets import QApplication

        QApplication.processEvents()

        # Then widen
        e2e_main_window.resize(1280, 720)
        QApplication.processEvents()

        table = e2e_main_window._story_table
        for col in e2e_main_window._responsive_columns:
            assert not table.isColumnHidden(col), f"Column {col} should be visible"
        assert not e2e_main_window._hidden_columns_label.isVisible()

    def test_responsive_columns_are_correct(self, e2e_main_window: MainWindow):
        """Responsive columns are Onda(2), Componente(4), Duracao(12)."""
        assert e2e_main_window._responsive_columns == [2, 4, 12]
