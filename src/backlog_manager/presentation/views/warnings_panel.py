"""Warnings Panel View.

This module provides a QWidget for displaying allocation warnings.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor
from PySide6.QtWidgets import (
    QGroupBox,
    QListWidget,
    QListWidgetItem,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    pass  # Required for conditional imports used by type checkers only

logger = logging.getLogger(__name__)


class WarningsPanel(QWidget):
    """Panel for displaying allocation warnings.

    Shows warnings from the last allocation with color coding:
    - Deadlock warnings: Red
    - Idleness info (between waves): Gray
    - Other warnings: Orange
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the panel.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._setup_ui()

        logger.debug("WarningsPanel initialized")

    def _setup_ui(self) -> None:
        """Create and configure the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Warnings group
        warnings_group = QGroupBox("Avisos")
        warnings_layout = QVBoxLayout(warnings_group)

        self._warnings_list = QListWidget()
        self._warnings_list.setMaximumHeight(150)
        warnings_layout.addWidget(self._warnings_list)

        layout.addWidget(warnings_group)
        layout.addStretch()

    def set_warnings(self, warnings: list[str]) -> None:
        """Update the panel with warnings.

        Args:
            warnings: List of warning messages.
        """
        self._warnings_list.clear()

        for warning in warnings:
            item = QListWidgetItem(warning)
            item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsSelectable)

            # Color code by warning type
            if "deadlock" in warning.lower():
                item.setForeground(QColor("red"))
            elif (
                "ociosidade entre ondas" in warning.lower()
                or "between" in warning.lower()
            ):
                item.setForeground(QColor("gray"))
            elif "ociosidade" in warning.lower() or "idle" in warning.lower():
                item.setForeground(QColor("orange"))
            else:
                item.setForeground(QColor("orange"))

            self._warnings_list.addItem(item)

        logger.debug("Warnings panel updated with %d warnings", len(warnings))

    def clear(self) -> None:
        """Clear all warnings."""
        self._warnings_list.clear()

    @property
    def warning_count(self) -> int:
        """Get the number of warnings displayed.

        Returns:
            Number of warning items.
        """
        return self._warnings_list.count()
