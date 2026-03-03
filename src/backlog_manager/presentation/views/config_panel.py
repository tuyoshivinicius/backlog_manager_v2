"""Config Panel View.

This module provides a QWidget for allocation configuration parameters.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Slot
from PySide6.QtWidgets import (
    QDateEdit,
    QDoubleSpinBox,
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)


class ConfigPanel(QWidget):
    """Panel for allocation configuration parameters.

    Provides inputs for velocity, start date, and max idle days.
    Values are kept in memory (no persistence per ADR-007).
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the panel.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._setup_ui()

        logger.debug("ConfigPanel initialized")

    def _setup_ui(self) -> None:
        """Create and configure the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Configuration group
        config_group = QGroupBox("Configuracao de Alocacao")
        form_layout = QFormLayout(config_group)

        # Velocity input
        self._velocity_spinbox = QDoubleSpinBox()
        self._velocity_spinbox.setMinimum(0.1)
        self._velocity_spinbox.setMaximum(10.0)
        self._velocity_spinbox.setValue(2.0)
        self._velocity_spinbox.setSingleStep(0.1)
        self._velocity_spinbox.setDecimals(1)
        self._velocity_spinbox.setSuffix(" SP/dia")
        self._velocity_spinbox.setToolTip("Story Points por dia de trabalho")
        form_layout.addRow("Velocidade:", self._velocity_spinbox)

        # Start date input
        self._start_date_edit = QDateEdit()
        self._start_date_edit.setCalendarPopup(True)
        self._start_date_edit.setDate(QDate.currentDate())
        self._start_date_edit.setToolTip("Data de inicio do projeto")
        form_layout.addRow("Data Inicio:", self._start_date_edit)

        # Max idle days input
        self._max_idle_spinbox = QSpinBox()
        self._max_idle_spinbox.setMinimum(2)
        self._max_idle_spinbox.setMaximum(30)
        self._max_idle_spinbox.setValue(3)
        self._max_idle_spinbox.setSuffix(" dias")
        self._max_idle_spinbox.setToolTip("Maximo de dias ociosos antes de gerar aviso")
        form_layout.addRow("Max Dias Ociosos:", self._max_idle_spinbox)

        layout.addWidget(config_group)
        layout.addStretch()

    @property
    def velocity(self) -> float:
        """Get the configured velocity.

        Returns:
            Velocity in story points per day.
        """
        return self._velocity_spinbox.value()

    @velocity.setter
    def velocity(self, value: float) -> None:
        """Set the velocity value.

        Args:
            value: Velocity in story points per day.
        """
        self._velocity_spinbox.setValue(value)

    @property
    def start_date(self) -> date:
        """Get the configured start date.

        Returns:
            Project start date.
        """
        qdate = self._start_date_edit.date()
        return date(qdate.year(), qdate.month(), qdate.day())

    @start_date.setter
    def start_date(self, value: date) -> None:
        """Set the start date value.

        Args:
            value: Project start date.
        """
        self._start_date_edit.setDate(QDate(value.year, value.month, value.day))

    @property
    def max_idle_days(self) -> int:
        """Get the configured max idle days.

        Returns:
            Maximum idle days threshold.
        """
        return self._max_idle_spinbox.value()

    @max_idle_days.setter
    def max_idle_days(self, value: int) -> None:
        """Set the max idle days value.

        Args:
            value: Maximum idle days threshold.
        """
        self._max_idle_spinbox.setValue(value)

    def validate(self) -> tuple[bool, str]:
        """Validate the configuration values.

        Returns:
            Tuple of (is_valid, error_message).
        """
        if self.velocity <= 0:
            return False, "Velocidade deve ser maior que zero."
        if self.max_idle_days < 2 or self.max_idle_days > 30:
            return False, "Dias ociosos deve estar entre 2 e 30."
        return True, ""
