"""Confirm Delete Dialog View.

This module provides a confirmation dialog for deleting entities
(stories, developers, features).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from backlog_manager.presentation.theme.theme import get_icon_manager

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class ConfirmDeleteDialog(QDialog):
    """Dialog for confirming entity deletion.

    Displays entity information with an alert icon and asks for
    confirmation before deletion.
    """

    def __init__(
        self,
        main_text: str,
        detail_text: str = "Esta acao nao pode ser desfeita.",
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            main_text: Main confirmation text to display.
            detail_text: Detail text shown below the main text.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._main_text = main_text
        self._detail_text = detail_text

        self._setup_ui()

        logger.debug("ConfirmDeleteDialog initialized: %s", main_text)

    @classmethod
    def for_story(
        cls, story_id: str, story_name: str, parent: QWidget | None = None
    ) -> ConfirmDeleteDialog:
        """Create a confirmation dialog for story deletion.

        Args:
            story_id: ID of the story to delete.
            story_name: Name of the story to delete.
            parent: Optional parent widget.

        Returns:
            Configured ConfirmDeleteDialog instance.
        """
        return cls(main_text=f"Excluir {story_id} \u2014 {story_name}?", parent=parent)

    @classmethod
    def for_developer(
        cls, name: str, parent: QWidget | None = None
    ) -> ConfirmDeleteDialog:
        """Create a confirmation dialog for developer deletion.

        Args:
            name: Name of the developer to delete.
            parent: Optional parent widget.

        Returns:
            Configured ConfirmDeleteDialog instance.
        """
        return cls(main_text=f"Excluir {name}?", parent=parent)

    @classmethod
    def for_feature(
        cls, name: str, wave: int, parent: QWidget | None = None
    ) -> ConfirmDeleteDialog:
        """Create a confirmation dialog for feature deletion.

        Args:
            name: Name of the feature to delete.
            wave: Wave number of the feature.
            parent: Optional parent widget.

        Returns:
            Configured ConfirmDeleteDialog instance.
        """
        return cls(main_text=f"Excluir Onda {wave} \u2014 {name}?", parent=parent)

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setObjectName("confirm-delete-dialog")
        self.setWindowTitle("Confirmar Exclusao")
        self.setMinimumWidth(350)
        self.setModal(True)

        main_layout = QVBoxLayout(self)

        # Content row: icon + text
        content_layout = QHBoxLayout()

        # Alert icon
        icon_label = QLabel()
        icon_label.setObjectName("confirm-delete-icon")
        try:
            icon_mgr = get_icon_manager()
            icon = icon_mgr.get("warning-triangle")
            pixmap = icon.pixmap(QSize(32, 32))
            icon_label.setPixmap(pixmap)
        except Exception:  # noqa: BLE001
            logger.debug("Could not load warning-triangle icon")
        icon_label.setFixedSize(QSize(32, 32))
        content_layout.addWidget(icon_label)

        # Text column
        text_layout = QVBoxLayout()

        main_text_label = QLabel(self._main_text)
        main_text_label.setObjectName("confirm-delete-main-text")
        main_text_label.setWordWrap(True)
        text_layout.addWidget(main_text_label)

        detail_text_label = QLabel(self._detail_text)
        detail_text_label.setObjectName("confirm-delete-detail-text")
        detail_text_label.setWordWrap(True)
        text_layout.addWidget(detail_text_label)

        content_layout.addLayout(text_layout)
        main_layout.addLayout(content_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("confirm-delete-cancel-button")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        confirm_button = QPushButton("Confirmar Exclusao")
        confirm_button.setObjectName("confirm-delete-button")
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)

        main_layout.addLayout(button_layout)
