"""Confirm Reset Dialog View.

This module provides a confirmation dialog for the reset planning operation.
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


class ConfirmResetDialog(QDialog):
    """Dialog for confirming planning reset operation.

    Displays affected story counts and asks for confirmation
    before executing the reset.
    """

    def __init__(
        self,
        with_dates: int,
        with_developer: int,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            with_dates: Number of stories with dates/duration to clear.
            with_developer: Number of stories with developer to clear.
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._with_dates = with_dates
        self._with_developer = with_developer

        self._setup_ui()

        logger.debug(
            "ConfirmResetDialog initialized: dates=%d, developer=%d",
            with_dates,
            with_developer,
        )

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setObjectName("confirm-reset-dialog")
        self.setWindowTitle("Novo Planejamento")
        self.setMinimumWidth(400)
        self.setModal(True)

        main_layout = QVBoxLayout(self)

        # Content row: icon + text
        content_layout = QHBoxLayout()

        # Warning icon
        icon_label = QLabel()
        icon_label.setObjectName("confirm-reset-icon")
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

        main_text_label = QLabel("Deseja limpar todos os dados de planejamento?")
        main_text_label.setObjectName("confirm-reset-main-text")
        main_text_label.setWordWrap(True)
        text_layout.addWidget(main_text_label)

        detail1_label = QLabel(
            f"{self._with_dates} historias terao datas e duracoes removidas"
        )
        detail1_label.setObjectName("confirm-reset-detail1")
        detail1_label.setWordWrap(True)
        text_layout.addWidget(detail1_label)

        detail2_label = QLabel(
            f"{self._with_developer} historias terao desenvolvedores desalocados"
        )
        detail2_label.setObjectName("confirm-reset-detail2")
        detail2_label.setWordWrap(True)
        text_layout.addWidget(detail2_label)

        warning_label = QLabel("Esta acao nao pode ser desfeita.")
        warning_label.setObjectName("confirm-reset-warning")
        warning_label.setWordWrap(True)
        text_layout.addWidget(warning_label)

        content_layout.addLayout(text_layout)
        main_layout.addLayout(content_layout)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        cancel_button = QPushButton("Cancelar")
        cancel_button.setObjectName("confirm-reset-cancel-button")
        cancel_button.setDefault(True)
        cancel_button.setFocus()
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)

        confirm_button = QPushButton("Confirmar")
        confirm_button.setObjectName("confirm-reset-button")
        confirm_button.setProperty("class", "destructive")
        confirm_button.clicked.connect(self.accept)
        button_layout.addWidget(confirm_button)

        main_layout.addLayout(button_layout)
