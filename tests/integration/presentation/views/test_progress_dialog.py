"""Integration tests for ProgressDialog."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel, QProgressBar

from backlog_manager.presentation.views.progress_dialog import ProgressDialog


class TestProgressDialog:
    """Tests for ProgressDialog (US7)."""

    def test_progress_dialog_creation(self, qapp, qtbot) -> None:
        """Test bar and message label present."""
        dialog = ProgressDialog("Processando...")
        qtbot.addWidget(dialog)

        bar = dialog.findChild(QProgressBar, "progress-bar")
        assert bar is not None

        msg = dialog.findChild(QLabel, "progress-message")
        assert msg is not None
        assert msg.text() == "Processando..."

    def test_progress_dialog_update(self, qapp, qtbot) -> None:
        """Test values reflect parameters."""
        dialog = ProgressDialog("Iniciando...", indeterminate=False)
        qtbot.addWidget(dialog)

        dialog.update_progress(50, "Metade concluida")

        bar = dialog.findChild(QProgressBar, "progress-bar")
        assert bar is not None
        assert bar.value() == 50

        msg = dialog.findChild(QLabel, "progress-message")
        assert msg is not None
        assert msg.text() == "Metade concluida"
