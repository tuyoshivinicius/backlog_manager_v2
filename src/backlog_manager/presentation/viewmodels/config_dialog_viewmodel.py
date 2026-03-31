"""Config Dialog ViewModel.

Gerencia estado e validacao dos parametros de configuracao de alocacao.
"""

from __future__ import annotations

import logging
from datetime import date
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, QSettings, Signal

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

        self._sp_per_sprint: int = 20
        self._workdays_per_sprint: int = 10
        self._start_date: date = date.today()
        self._max_idle_days: int = 3

        self._load_from_qsettings()
        logger.debug("ConfigDialogViewModel initialized")

    @property
    def sp_per_sprint(self) -> int:
        """Story points por sprint."""
        return self._sp_per_sprint

    @sp_per_sprint.setter
    def sp_per_sprint(self, value: int) -> None:
        self._sp_per_sprint = value

    @property
    def workdays_per_sprint(self) -> int:
        """Dias uteis por sprint."""
        return self._workdays_per_sprint

    @workdays_per_sprint.setter
    def workdays_per_sprint(self, value: int) -> None:
        self._workdays_per_sprint = value

    @property
    def velocity_per_day(self) -> float:
        """Velocidade derivada em SP/dia (read-only)."""
        return self._sp_per_sprint / self._workdays_per_sprint

    @property
    def velocity(self) -> float:
        """Velocidade em SP/dia (retrocompatibilidade)."""
        return self.velocity_per_day

    @velocity.setter
    def velocity(self, value: float) -> None:
        """Define velocidade (retrocompatibilidade — ignora, usa sp_per_sprint)."""
        pass

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
        if self._sp_per_sprint < 1 or self._sp_per_sprint > 100:
            return False, "SP/Sprint deve estar entre 1 e 100."
        if self._workdays_per_sprint < 1 or self._workdays_per_sprint > 30:
            return False, "Dias uteis por sprint deve estar entre 1 e 30."
        if self._max_idle_days < 2 or self._max_idle_days > 30:
            return False, "Dias ociosos deve estar entre 2 e 30."
        return True, ""

    def _get_qsettings(self) -> QSettings:
        """Get QSettings instance for allocation preferences."""
        return QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "BacklogManager",
            "Backlog Manager",
        )

    def _load_from_qsettings(self) -> None:
        """Load values from QSettings with validation and defaults."""
        settings = self._get_qsettings()
        settings.beginGroup("allocation")

        # SP per sprint and workdays (new format)
        try:
            val = settings.value("sp_per_sprint")
            if val is not None:
                sp = int(val)
                if 1 <= sp <= 100:
                    self._sp_per_sprint = sp
        except (ValueError, TypeError):
            pass

        try:
            val = settings.value("workdays_per_sprint")
            if val is not None:
                wd = int(val)
                if 1 <= wd <= 30:
                    self._workdays_per_sprint = wd
        except (ValueError, TypeError):
            pass

        # Start date
        try:
            val = settings.value("start_date")
            if val is not None:
                self._start_date = date.fromisoformat(str(val))
        except (ValueError, TypeError):
            pass

        # Max idle days
        try:
            val = settings.value("max_idle_days")
            if val is not None:
                max_idle = int(val)
                if 2 <= max_idle <= 30:
                    self._max_idle_days = max_idle
        except (ValueError, TypeError):
            pass

        settings.endGroup()
        logger.debug(
            "Config loaded from QSettings: sp_per_sprint=%d, workdays=%d, velocity=%.1f, start=%s, max_idle=%d",
            self._sp_per_sprint,
            self._workdays_per_sprint,
            self.velocity_per_day,
            self._start_date,
            self._max_idle_days,
        )

    def _save_to_qsettings(self) -> None:
        """Persist current values to QSettings."""
        settings = self._get_qsettings()
        settings.beginGroup("allocation")
        settings.setValue("sp_per_sprint", self._sp_per_sprint)
        settings.setValue("workdays_per_sprint", self._workdays_per_sprint)
        settings.setValue("start_date", self._start_date.isoformat())
        settings.setValue("max_idle_days", self._max_idle_days)
        settings.endGroup()
        settings.sync()

    def save(self) -> None:
        """Salva os valores atuais (emite signal saved).

        Se validacao falhar, emite error_occurred.
        """
        is_valid, error = self.validate()
        if not is_valid:
            self.error_occurred.emit(error)
            return

        self._save_to_qsettings()
        self.saved.emit()
        logger.info(
            "Config saved: sp_per_sprint=%d, workdays=%d, velocity=%.1f, start=%s, max_idle=%d",
            self._sp_per_sprint,
            self._workdays_per_sprint,
            self.velocity_per_day,
            self._start_date,
            self._max_idle_days,
        )
