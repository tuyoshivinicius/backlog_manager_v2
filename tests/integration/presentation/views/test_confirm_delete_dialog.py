"""Integration tests for ConfirmDeleteDialog."""

from __future__ import annotations

from backlog_manager.presentation.views.confirm_delete_dialog import ConfirmDeleteDialog
from PySide6.QtWidgets import QLabel, QPushButton


class TestConfirmDeleteDialog:
    """Tests for entity-specific confirmation dialogs (US6)."""

    def test_confirm_delete_dialog_story(self, qapp, qtbot) -> None:
        """Test text 'Excluir {id} — {nome}?' for stories."""
        dialog = ConfirmDeleteDialog.for_story("API-001", "Criar endpoint")
        qtbot.addWidget(dialog)

        main_text = dialog.findChild(QLabel, "confirm-delete-main-text")
        assert main_text is not None
        assert "Excluir API-001" in main_text.text()
        assert "Criar endpoint" in main_text.text()

    def test_confirm_delete_dialog_developer(self, qapp, qtbot) -> None:
        """Test text 'Excluir {nome}?' for developers."""
        dialog = ConfirmDeleteDialog.for_developer("Joao Silva")
        qtbot.addWidget(dialog)

        main_text = dialog.findChild(QLabel, "confirm-delete-main-text")
        assert main_text is not None
        assert "Excluir Joao Silva?" in main_text.text()

    def test_confirm_delete_dialog_feature(self, qapp, qtbot) -> None:
        """Test text 'Excluir Onda {N} — {nome}?' for features."""
        dialog = ConfirmDeleteDialog.for_feature("Login", 2)
        qtbot.addWidget(dialog)

        main_text = dialog.findChild(QLabel, "confirm-delete-main-text")
        assert main_text is not None
        assert "Excluir Onda 2" in main_text.text()
        assert "Login" in main_text.text()

    def test_confirm_delete_dialog_red_button(self, qapp, qtbot) -> None:
        """Test confirm button has danger style."""
        dialog = ConfirmDeleteDialog.for_story("API-001", "Test")
        qtbot.addWidget(dialog)

        confirm_btn = dialog.findChild(QPushButton, "confirm-delete-button")
        assert confirm_btn is not None
        assert confirm_btn.text() == "Confirmar Exclusao"
