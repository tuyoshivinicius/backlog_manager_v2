"""Confirm Delete Dialog View.

This module provides a confirmation dialog for deleting stories.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QVBoxLayout

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class ConfirmDeleteDialog(QDialog):
    """Dialog for confirming story deletion.

    Displays story information and asks for confirmation before deletion.
    """

    def __init__(
        self,
        story_id: str,
        story_name: str,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            story_id: ID of the story to delete.
            story_name: Name of the story to delete.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._story_id = story_id
        self._story_name = story_name

        self._setup_ui()

        logger.debug("ConfirmDeleteDialog initialized for story: %s", story_id)

    @property
    def story_id(self) -> str:
        """Get the story ID to delete.

        Returns:
            The story ID.
        """
        return self._story_id

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setWindowTitle("Confirmar Exclusao")
        self.setMinimumWidth(350)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Warning message
        message = QLabel(
            f"Deseja realmente excluir a historia?\n\n"
            f"ID: {self._story_id}\n"
            f"Nome: {self._story_name}\n\n"
            f"Esta acao nao pode ser desfeita."
        )
        message.setWordWrap(True)
        layout.addWidget(message)

        # Button box
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Yes | QDialogButtonBox.StandardButton.No
        )
        button_box.button(QDialogButtonBox.StandardButton.Yes).setText("Confirmar")
        button_box.button(QDialogButtonBox.StandardButton.No).setText("Cancelar")

        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
