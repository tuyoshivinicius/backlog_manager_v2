"""Componente DatePicker reutilizavel com estilizacao Design System."""

from __future__ import annotations

from datetime import date

from PySide6.QtCore import QDate, Signal, Slot
from PySide6.QtWidgets import QDateEdit, QWidget

from backlog_manager.presentation.theme import DESIGN_TOKENS


class DatePicker(QDateEdit):
    """Componente DatePicker reutilizavel com estilizacao Design System.

    Herda QDateEdit com configuracao padrao e estilizacao consistente.

    Signals:
        date_changed: Emitido quando a data selecionada muda (emite datetime.date).
    """

    date_changed = Signal(object)

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        display_format: str = "dd/MM/yyyy",
        min_date: date | None = None,
        max_date: date | None = None,
    ) -> None:
        """Initialize DatePicker with optional format and date constraints."""
        super().__init__(parent)

        self.setCalendarPopup(True)
        self.setDisplayFormat(display_format)
        self.setDate(QDate.currentDate())

        if min_date is not None:
            self.setMinimumDate(QDate(min_date.year, min_date.month, min_date.day))
        if max_date is not None:
            self.setMaximumDate(QDate(max_date.year, max_date.month, max_date.day))

        self._apply_styling()
        self.dateChanged.connect(self._on_date_changed)

    def get_date(self) -> date:
        """Retorna a data selecionada como datetime.date."""
        qd = self.date()
        return date(qd.year(), qd.month(), qd.day())

    def set_date(self, value: date) -> None:
        """Define a data selecionada a partir de datetime.date."""
        self.setDate(QDate(value.year, value.month, value.day))

    @Slot(QDate)
    def _on_date_changed(self, qdate: QDate) -> None:
        """Emite date_changed com datetime.date."""
        self.date_changed.emit(date(qdate.year(), qdate.month(), qdate.day()))

    def _apply_styling(self) -> None:
        """Aplica estilizacao do Design System."""
        self.setStyleSheet(
            f"""
            QDateEdit {{
                font-family: {DESIGN_TOKENS["font-family"]};
                font-size: {DESIGN_TOKENS["font-size-base"]};
                border: 1px solid {DESIGN_TOKENS["border"]};
                border-radius: {DESIGN_TOKENS["radius-md"]};
                padding: 4px 8px;
            }}
            QDateEdit:focus {{
                border: {DESIGN_TOKENS["focus-ring"]};
            }}
            QCalendarWidget QAbstractItemView {{
                background: {DESIGN_TOKENS["background"]};
                selection-background-color: {DESIGN_TOKENS["primary"]};
                selection-color: white;
            }}
            """
        )
