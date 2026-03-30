"""Progress Dialog View.

This module provides a modal QDialog for showing operation progress,
with optional cancellation support for long-running operations.
"""

from __future__ import annotations

import asyncio
import logging
from typing import TYPE_CHECKING, Any

from PySide6.QtCore import Qt, QTimer, Signal
from PySide6.QtWidgets import QDialog, QLabel, QProgressBar, QPushButton, QVBoxLayout

if TYPE_CHECKING:
    from PySide6.QtWidgets import QWidget

logger = logging.getLogger(__name__)


class ProgressDialog(QDialog):
    """Modal dialog showing progress of long-running operations.

    Supports both determinate (0-100%) and indeterminate (animation) modes.
    Optionally shows a Cancel button after 2 seconds for cancellable operations.
    """

    cancelled = Signal()

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

        # Cancel button (hidden initially, shown after 2s for cancellable tasks)
        self._cancel_button = QPushButton("Cancelar")
        self._cancel_button.setObjectName("cancel-button")
        self._cancel_button.setVisible(False)
        self._cancel_button.clicked.connect(self._on_cancel)
        layout.addWidget(self._cancel_button)

        self._task: asyncio.Task[Any] | None = None

        # Timer to show cancel button after 2s
        self._cancel_timer = QTimer(self)
        self._cancel_timer.setSingleShot(True)
        self._cancel_timer.setInterval(2000)
        self._cancel_timer.timeout.connect(self._show_cancel_button)

        if indeterminate:
            self._progress_bar.setRange(0, 0)
        else:
            self._progress_bar.setRange(0, 100)
            self._progress_bar.setValue(0)

        logger.debug("ProgressDialog initialized")

    def set_cancellable_task(self, task: asyncio.Task[Any]) -> None:
        """Set the asyncio task that can be cancelled.

        The cancel button will appear after 2 seconds.

        Args:
            task: The asyncio task to cancel on button click.
        """
        self._task = task
        self._cancel_timer.start()

    def _show_cancel_button(self) -> None:
        """Show the cancel button after the timer expires."""
        self._cancel_button.setVisible(True)

    def _on_cancel(self) -> None:
        """Handle cancel button click."""
        if self._task is not None:
            self._task.cancel()
            logger.info("Task cancellation requested")
        self.cancelled.emit()
        self._cancel_button.setEnabled(False)
        self._cancel_button.setText("Cancelando...")

    def close(self) -> bool:
        """Clean up timer on close."""
        self._cancel_timer.stop()
        return super().close()

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
