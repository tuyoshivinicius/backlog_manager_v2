"""Config Dialog ViewModel.

Gerencia estado e validacao dos parametros de configuracao de alocacao.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

if TYPE_CHECKING:
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ConfigDialogViewModel(QObject):
    """ViewModel para o ConfigDialog.

    Gerencia parametros de alocacao: velocity, start_date, max_idle_days.
    Valores sao mantidos em memoria (sem persistencia per ADR-007).

    Signals:
        saved: Emitido quando valores sao salvos com sucesso.
        error_occurred: Emitido quando ocorre erro de validacao.
    """

    saved = Signal()
    error_occurred = Signal(str)

    def __init__(self, container: DIContainer, parent: QObject | None = None) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
            parent: Optional parent QObject.
        """
        super().__init__(parent)
        self._container = container

        self._velocity: float = 2.0
        self._start_date: date = date.today()
        self._max_idle_days: int = 3

        logger.debug("ConfigDialogViewModel initialized")

    @property
    def velocity(self) -> float:
        """Velocidade em SP/dia."""
        return self._velocity

    @velocity.setter
    def velocity(self, value: float) -> None:
        """Define velocidade."""
        self._velocity = value

    @property
    def start_date(self) -> date:
        """Data de inicio do projeto."""
        return self._start_date

    @start_date.setter
    def start_date(self, value: date) -> None:
        """Define data de inicio."""
        self._start_date = value

    @property
    def max_idle_days(self) -> int:
        """Maximo de dias ociosos."""
        return self._max_idle_days

    @max_idle_days.setter
    def max_idle_days(self, value: int) -> None:
        """Define maximo de dias ociosos."""
        self._max_idle_days = value

    def validate(self) -> tuple[bool, str]:
        """Valida os parametros de configuracao.

        Returns:
            Tuple de (is_valid, error_message).
        """
        if self._velocity < 0.1 or self._velocity > 10.0:
            return False, "Velocidade deve estar entre 0.1 e 10.0 SP/dia."
        if self._max_idle_days < 2 or self._max_idle_days > 30:
            return False, "Dias ociosos deve estar entre 2 e 30."
        return True, ""

    def save(self) -> None:
        """Salva os valores atuais (emite signal saved).

        Se validacao falhar, emite error_occurred.
        """
        is_valid, error = self.validate()
        if not is_valid:
            self.error_occurred.emit(error)
            return

        self.saved.emit()
        logger.info(
            "Config saved: velocity=%.1f, start=%s, max_idle=%d",
            self._velocity,
            self._start_date,
            self._max_idle_days,
        )
