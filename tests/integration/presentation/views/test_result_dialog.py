"""Integration tests for ResultDialog."""

from __future__ import annotations

import pytest
from PySide6.QtWidgets import QLabel

from backlog_manager.presentation.views.result_dialog import ResultDialog


class TestResultDialog:
    """Tests for ResultDialog (US7)."""

    def test_result_dialog_import(self, qapp, qtbot) -> None:
        """Test labels show formatted counts."""
        dialog = ResultDialog.for_import(
            stories_count=10, features_count=3, warnings_count=2
        )
        qtbot.addWidget(dialog)

        title = dialog.findChild(QLabel, "result-title")
        assert title is not None
        assert "Importacao" in title.text()

        details = dialog.findChild(QLabel, "result-details")
        assert details is not None
        assert "10" in details.text()
        assert "3" in details.text()

    def test_result_dialog_export(self, qapp, qtbot) -> None:
        """Test label shows file path."""
        dialog = ResultDialog.for_export(file_path="C:/exports/backlog.xlsx")
        qtbot.addWidget(dialog)

        details = dialog.findChild(QLabel, "result-details")
        assert details is not None
        assert "C:/exports/backlog.xlsx" in details.text()
