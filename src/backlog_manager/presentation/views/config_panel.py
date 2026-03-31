"""Config Panel View.

This module provides a QWidget for allocation configuration parameters.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QFormLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

from backlog_manager.presentation.views.date_picker import DatePicker

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

        # SP per Sprint input
        self._sp_per_sprint_spin = QSpinBox()
        self._sp_per_sprint_spin.setMinimum(1)
        self._sp_per_sprint_spin.setMaximum(100)
        self._sp_per_sprint_spin.setValue(20)
        self._sp_per_sprint_spin.setSuffix(" SP/Sprint")
        self._sp_per_sprint_spin.setToolTip("Story Points por sprint")
        form_layout.addRow("Velocidade (SP/Sprint):", self._sp_per_sprint_spin)

        # Workdays per Sprint input
        self._workdays_per_sprint_spin = QSpinBox()
        self._workdays_per_sprint_spin.setMinimum(1)
        self._workdays_per_sprint_spin.setMaximum(30)
        self._workdays_per_sprint_spin.setValue(10)
        self._workdays_per_sprint_spin.setSuffix(" dias")
        self._workdays_per_sprint_spin.setToolTip("Dias uteis por sprint")
        form_layout.addRow("Dias Uteis por Sprint:", self._workdays_per_sprint_spin)

        # Derived velocity label
        self._velocity_label = QLabel("= 2.0 SP/dia")
        self._velocity_label.setStyleSheet("color: gray;")
        form_layout.addRow("", self._velocity_label)

        self._sp_per_sprint_spin.valueChanged.connect(self._update_velocity_label)
        self._workdays_per_sprint_spin.valueChanged.connect(self._update_velocity_label)

        # Start date input
        self._start_date_edit = DatePicker()
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

    def _update_velocity_label(self) -> None:
        """Recalcula e atualiza label derivada de velocidade."""
        sp = self._sp_per_sprint_spin.value()
        wd = self._workdays_per_sprint_spin.value()
        velocity = sp / wd if wd > 0 else 0
        self._velocity_label.setText(f"= {velocity:.1f} SP/dia")

    @property
    def velocity(self) -> float:
        """Velocidade derivada em SP/dia (retrocompatibilidade)."""
        return self._sp_per_sprint_spin.value() / self._workdays_per_sprint_spin.value()

    @velocity.setter
    def velocity(self, value: float) -> None:
        """Set velocity via sp_per_sprint assuming current workdays."""
        self._sp_per_sprint_spin.setValue(
            int(value * self._workdays_per_sprint_spin.value())
        )

    @property
    def sp_per_sprint(self) -> int:
        """Get the configured story points per sprint."""
        return self._sp_per_sprint_spin.value()

    @sp_per_sprint.setter
    def sp_per_sprint(self, value: int) -> None:
        self._sp_per_sprint_spin.setValue(value)

    @property
    def workdays_per_sprint(self) -> int:
        """Get the configured workdays per sprint."""
        return self._workdays_per_sprint_spin.value()

    @workdays_per_sprint.setter
    def workdays_per_sprint(self, value: int) -> None:
        self._workdays_per_sprint_spin.setValue(value)

    @property
    def start_date(self) -> date:
        """Get the configured start date."""
        return self._start_date_edit.get_date()

    @start_date.setter
    def start_date(self, value: date) -> None:
        """Set the start date value."""
        self._start_date_edit.set_date(value)

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
