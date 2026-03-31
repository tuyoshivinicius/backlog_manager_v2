"""Unit tests for ConfirmResetDialog."""

from __future__ import annotations

import pytest
from backlog_manager.presentation.views.confirm_reset_dialog import ConfirmResetDialog


@pytest.fixture
def dialog(qtbot):
    """Create a ConfirmResetDialog instance."""
    d = ConfirmResetDialog(with_dates=10, with_developer=5, parent=None)
    qtbot.addWidget(d)
    return d


class TestConfirmResetDialog:
    """Tests for ConfirmResetDialog."""

    def test_confirm_dialog_shows_count(self, dialog):
        """T015: Should display affected story counts."""
        from PySide6.QtWidgets import QLabel

        all_labels = dialog.findChildren(QLabel)
        label_texts = [label.text() for label in all_labels]
        texts_joined = " ".join(label_texts)

        assert "10" in texts_joined
        assert "5" in texts_joined

    def test_confirm_dialog_cancel_default(self, dialog):
        """T016: Cancel button should have default focus."""
        from PySide6.QtWidgets import QPushButton

        cancel_btn = dialog.findChild(QPushButton, "confirm-reset-cancel-button")
        assert cancel_btn is not None
        assert cancel_btn.isDefault() or cancel_btn.hasFocus()
