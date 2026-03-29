"""Status Bar ViewModel.

Gerencia estado dos contadores e avisos exibidos na status bar.
"""

from __future__ import annotations

import logging
from datetime import datetime

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.story import StoryOutputDTO

logger = logging.getLogger(__name__)


class StatusBarViewModel(QObject):
    """ViewModel para a Status Bar.

    Signals:
        stats_changed: Emitido quando estatisticas mudam.
        warnings_changed: Emitido quando avisos mudam.
    """

    stats_changed = Signal()
    warnings_changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the ViewModel."""
        super().__init__(parent)

        self._story_count: int = 0
        self._total_sp: int = 0
        self._last_allocation: datetime | None = None
        self._warning_count: int = 0
        self._warnings: list[str] = []

    @property
    def story_count(self) -> int:
        """Numero de historias."""
        return self._story_count

    @property
    def total_sp(self) -> int:
        """Total de story points."""
        return self._total_sp

    @property
    def last_allocation(self) -> datetime | None:
        """Timestamp da ultima alocacao."""
        return self._last_allocation

    @property
    def warning_count(self) -> int:
        """Numero de avisos."""
        return self._warning_count

    @property
    def warnings(self) -> list[str]:
        """Lista de avisos."""
        return self._warnings.copy()

    def update_stats(self, stories: list[StoryOutputDTO]) -> None:
        """Atualiza estatisticas baseado na lista de historias.

        Args:
            stories: Lista de historias.
        """
        self._story_count = len(stories)
        self._total_sp = sum(s.story_points or 0 for s in stories)
        self.stats_changed.emit()

    def set_last_allocation(self, timestamp: datetime) -> None:
        """Define timestamp da ultima alocacao.

        Args:
            timestamp: Timestamp da alocacao.
        """
        self._last_allocation = timestamp
        self.stats_changed.emit()

    def set_warnings(self, warnings: list[str]) -> None:
        """Define lista de avisos.

        Args:
            warnings: Lista de mensagens de aviso.
        """
        self._warnings = warnings
        self._warning_count = len(warnings)
        self.warnings_changed.emit()
