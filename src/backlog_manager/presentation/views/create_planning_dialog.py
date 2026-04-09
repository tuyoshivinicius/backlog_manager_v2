"""Create Planning Dialog View.

This module provides a dialog for creating a new planning.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Slot
from PySide6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
)

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class CreatePlanningDialog(QDialog):
    """Dialog for creating a new planning.

    Provides a name input field with validation.
    In bootstrap mode, the Cancel button is hidden.
    """

    def __init__(
        self,
        parent: QWidget | None = None,
        bootstrap_mode: bool = False,
    ) -> None:
        """Initialize the dialog.

        Args:
            parent: Optional parent widget.
            bootstrap_mode: If True, hides the Cancel button.
        """
        super().__init__(parent)

        self._bootstrap_mode = bootstrap_mode
        self._setup_ui()

        logger.debug(
            "CreatePlanningDialog initialized: bootstrap_mode=%s", bootstrap_mode
        )

    def _setup_ui(self) -> None:
        """Create and configure the dialog UI."""
        self.setObjectName("create-planning-dialog")
        self.setWindowTitle("Novo Planejamento")
        self.setMinimumWidth(400)
        self.setModal(True)

        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("Novo Planejamento")
        title_label.setObjectName("create-planning-title")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        main_layout.addWidget(title_label)

        # Name input
        name_label = QLabel("Nome:")
        name_label.setObjectName("create-planning-name-label")
        main_layout.addWidget(name_label)

        self._name_input = QLineEdit()
        self._name_input.setObjectName("create-planning-name-input")
        self._name_input.setMaxLength(200)
        self._name_input.setPlaceholderText("Digite o nome do planejamento")
        self._name_input.textChanged.connect(self._on_name_changed)
        main_layout.addWidget(self._name_input)

        # Error label
        self._error_label = QLabel()
        self._error_label.setObjectName("create-planning-error-label")
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setWordWrap(True)
        self._error_label.hide()
        main_layout.addWidget(self._error_label)

        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()

        self._cancel_button = QPushButton("Cancelar")
        self._cancel_button.setObjectName("create-planning-cancel-button")
        self._cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(self._cancel_button)

        if self._bootstrap_mode:
            self._cancel_button.hide()

        self._create_button = QPushButton("Criar")
        self._create_button.setObjectName("create-planning-create-button")
        self._create_button.setDefault(True)
        self._create_button.setEnabled(False)
        self._create_button.clicked.connect(self.accept)
        button_layout.addWidget(self._create_button)

        main_layout.addLayout(button_layout)

        self._name_input.setFocus()

    @Slot(str)
    def _on_name_changed(self, text: str) -> None:
        """Handle name input text changes.

        Args:
            text: Current text in the name input.
        """
        has_text = bool(text.strip())
        self._create_button.setEnabled(has_text)
        if has_text:
            self._error_label.hide()

    def set_error(self, message: str) -> None:
        """Display an error message.

        Args:
            message: Error message to display.
        """
        self._error_label.setText(message)
        self._error_label.show()

    def get_name(self) -> str | None:
        """Get the entered planning name.

        Returns:
            The planning name if accepted, None if cancelled.
        """
        if self.result() == QDialog.DialogCode.Accepted:
            return self._name_input.text().strip()
        return None
