"""E2E tests for AboutDialog.

Tests verify dialog content, layout, and design token usage.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from backlog_manager.presentation.views.about_dialog import AboutDialog
from PySide6.QtWidgets import QLabel

pytestmark = [pytest.mark.e2e]


class TestAboutDialog:
    """Tests for AboutDialog."""

    def test_dialog_creates_with_db_path(self, qtbot):
        """Dialog initializes with given database path."""
        db_path = Path("/tmp/test.db")
        dialog = AboutDialog(db_path)
        qtbot.addWidget(dialog)
        assert dialog.windowTitle() == "Sobre"

    def test_dialog_fixed_size(self, qtbot):
        """Dialog has fixed size 400x300."""
        dialog = AboutDialog(Path("/tmp/test.db"))
        qtbot.addWidget(dialog)
        assert dialog.width() == 400
        assert dialog.height() == 300

    def test_dialog_shows_app_name(self, qtbot):
        """Dialog displays 'Backlog Manager' as title."""
        dialog = AboutDialog(Path("/tmp/test.db"))
        qtbot.addWidget(dialog)

        labels = dialog.findChildren(QLabel)
        texts = [l.text() for l in labels]
        assert any("Backlog Manager" in t for t in texts)

    def test_dialog_shows_version(self, qtbot):
        """Dialog displays version info."""
        dialog = AboutDialog(Path("/tmp/test.db"))
        qtbot.addWidget(dialog)

        labels = dialog.findChildren(QLabel)
        texts = [l.text() for l in labels]
        assert any("Versao:" in t for t in texts)

    def test_dialog_shows_python_version(self, qtbot):
        """Dialog displays Python version."""
        dialog = AboutDialog(Path("/tmp/test.db"))
        qtbot.addWidget(dialog)

        labels = dialog.findChildren(QLabel)
        texts = [l.text() for l in labels]
        assert any("Python:" in t for t in texts)

    def test_dialog_shows_db_path(self, qtbot):
        """Dialog displays database path."""
        db_path = Path("/tmp/my_database.db")
        dialog = AboutDialog(db_path)
        qtbot.addWidget(dialog)

        labels = dialog.findChildren(QLabel)
        texts = [l.text() for l in labels]
        assert any("my_database.db" in t for t in texts)

    def test_dialog_shows_technologies(self, qtbot):
        """Dialog lists technologies used."""
        dialog = AboutDialog(Path("/tmp/test.db"))
        qtbot.addWidget(dialog)

        labels = dialog.findChildren(QLabel)
        texts = [l.text() for l in labels]
        assert any("PySide6" in t for t in texts)

    def test_dialog_uses_design_tokens(self, qtbot):
        """DB path label uses DESIGN_TOKENS for color."""
        from backlog_manager.presentation.theme import DESIGN_TOKENS

        dialog = AboutDialog(Path("/tmp/test.db"))
        qtbot.addWidget(dialog)

        labels = dialog.findChildren(QLabel)
        db_labels = [l for l in labels if "Banco de dados" in l.text()]
        assert len(db_labels) == 1
        assert DESIGN_TOKENS["text-muted"] in db_labels[0].styleSheet()
