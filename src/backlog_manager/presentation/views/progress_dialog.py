"""Progress Dialog View.

This module provides a modal QDialog for showing operation progress.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QVBoxLayout

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class ProgressDialog(QDialog):
    """Modal dialog showing progress of long-running operations.

    Supports both determinate (0-100%) and indeterminate (animation) modes.
    """

    def __init__(
        self,
        message: str,
        parent: QWidget | None = None,
        indeterminate: bool = True,
    ) -> None:
        """Initialize the dialog.

        Args:
            message: Initial message to display.
            parent: Optional parent widget.
            indeterminate: Whether to start in indeterminate mode.
        """
        super().__init__(parent)

        self.setObjectName("progress-dialog")
        self.setWindowTitle("Progresso")
        self.setMinimumWidth(350)
        self.setModal(True)
        self.setWindowFlag(Qt.WindowType.WindowCloseButtonHint, False)

        layout = QVBoxLayout(self)

        self._message_label = QLabel(message)
        self._message_label.setObjectName("progress-message")
        self._message_label.setWordWrap(True)
        layout.addWidget(self._message_label)

        self._progress_bar = QProgressBar()
        self._progress_bar.setObjectName("progress-bar")
        layout.addWidget(self._progress_bar)

        if indeterminate:
            self._progress_bar.setRange(0, 0)
        else:
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)

        logger.debug("ProgressDialog initialized")

    def update_progress(self, value: int, message: str | None = None) -> None:
        """Update progress bar and optional message.

        Switches to determinate mode if currently indeterminate.

        Args:
            value: Progress value (0-100).
            message: Optional new message.
        """
        if self._progress_bar.maximum() == 0:
            self._progress_bar.setRange(0, 100)
        self._progress_bar.setValue(value)
        if message is not None:
            self._message_label.setText(message)

    def set_indeterminate(self, indeterminate: bool) -> None:
        """Toggle between determinate and indeterminate modes.

        Args:
            indeterminate: True for indeterminate, False for determinate.
        """
        if indeterminate:
            self._progress_bar.setRange(0, 0)
        else:
            self._progress_bar.setRange(0, 100)
