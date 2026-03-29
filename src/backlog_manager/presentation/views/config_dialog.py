"""Config Dialog View.

Dialog modal para configuracao de parametros de alocacao.
Dimensoes: 420x340px (fixo, per FR-015).
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtCore import QDate, Slot
from PySide6.QtWidgets import (
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QDoubleSpinBox,
    QFormLayout,
    QLabel,
    QSpinBox,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ConfigDialog(QDialog):
    """Dialog modal para configuracao de parametros de alocacao.

    Campos: velocity (0.1-10.0), start_date, max_idle_days (2-30).
    """

    def __init__(
        self,
        container: DIContainer,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            container: Dependency injection container.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._container = container
        self._viewmodel = container.config_dialog_viewmodel

        self._setup_ui()
        self._load_values()
        self._connect_signals()

        logger.debug("ConfigDialog initialized")

    def _setup_ui(self) -> None:
        """Cria e configura a UI do dialog."""
        self.setWindowTitle("Configuracao de Alocacao")
        self.setFixedSize(420, 340)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Form layout
        form = QFormLayout()

        # Velocity
        self._velocity_spin = QDoubleSpinBox()
        self._velocity_spin.setMinimum(0.1)
        self._velocity_spin.setMaximum(10.0)
        self._velocity_spin.setSingleStep(0.1)
        self._velocity_spin.setDecimals(1)
        self._velocity_spin.setSuffix(" SP/dia")
        self._velocity_spin.setToolTip("Story Points por dia de trabalho")
        form.addRow("Velocidade:", self._velocity_spin)

        # Start date
        self._start_date_edit = QDateEdit()
        self._start_date_edit.setCalendarPopup(True)
        self._start_date_edit.setToolTip("Data de inicio do projeto")
        form.addRow("Data Inicio:", self._start_date_edit)

        # Max idle days
        self._max_idle_spin = QSpinBox()
        self._max_idle_spin.setMinimum(2)
        self._max_idle_spin.setMaximum(30)
        self._max_idle_spin.setSuffix(" dias")
        self._max_idle_spin.setToolTip("Maximo de dias ociosos antes de gerar aviso")
        form.addRow("Max Dias Ociosos:", self._max_idle_spin)

        layout.addLayout(form)

        # Error label
        self._error_label = QLabel()
        self._error_label.setStyleSheet("color: red;")
        self._error_label.setVisible(False)
        layout.addWidget(self._error_label)

        layout.addStretch()

        # Buttons
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.button(QDialogButtonBox.StandardButton.Ok).setText("Aplicar")
        self._button_box.button(QDialogButtonBox.StandardButton.Cancel).setText(
            "Cancelar"
        )
        layout.addWidget(self._button_box)

    def _load_values(self) -> None:
        """Carrega valores do ViewModel para os widgets."""
        self._velocity_spin.setValue(self._viewmodel.velocity)
        self._start_date_edit.setDate(
            QDate(
                self._viewmodel.start_date.year,
                self._viewmodel.start_date.month,
                self._viewmodel.start_date.day,
            )
        )
        self._max_idle_spin.setValue(self._viewmodel.max_idle_days)

    def _connect_signals(self) -> None:
        """Conecta signals."""
        self._button_box.accepted.connect(self._on_apply)
        self._button_box.rejected.connect(self.reject)
        self._viewmodel.saved.connect(self._on_saved)
        self._viewmodel.error_occurred.connect(self._on_error)

    @Slot()
    def _on_apply(self) -> None:
        """Handle apply button click."""
        # Transfer values to viewmodel
        self._viewmodel.velocity = self._velocity_spin.value()
        qdate = self._start_date_edit.date()
        from datetime import date

        self._viewmodel.start_date = date(qdate.year(), qdate.month(), qdate.day())
        self._viewmodel.max_idle_days = self._max_idle_spin.value()

        # Validate and save
        self._viewmodel.save()

    @Slot()
    def _on_saved(self) -> None:
        """Handle saved signal."""
        self._error_label.setVisible(False)
        self.accept()

    @Slot(str)
    def _on_error(self, message: str) -> None:
        """Handle error signal."""
        self._error_label.setText(message)
        self._error_label.setVisible(True)
