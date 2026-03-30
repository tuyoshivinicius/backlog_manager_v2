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
    sp_breakdown_changed = Signal()

    def __init__(self, parent: QObject | None = None) -> None:
        """Initialize the ViewModel."""
        super().__init__(parent)

        self._story_count: int = 0
        self._total_sp: int = 0
        self._last_allocation: datetime | None = None
        self._warning_count: int = 0
        self._warnings: list[str] = []
        self._sp_breakdown: dict[str, int] = {}
        self._sp_total: int = 0
        self._sp_percentages: dict[str, float] = {}

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

    @property
    def sp_breakdown(self) -> dict[str, int]:
        """SP breakdown by status."""
        return self._sp_breakdown.copy()

    @property
    def sp_total(self) -> int:
        """Total SP across all statuses."""
        return self._sp_total

    @property
    def sp_percentages(self) -> dict[str, float]:
        """SP percentages by status."""
        return self._sp_percentages.copy()

    def clear_last_allocation(self) -> None:
        """Clear the last allocation timestamp."""
        self._last_allocation = None
        self.stats_changed.emit()

    def update_sp_breakdown(self, stories: list[StoryOutputDTO]) -> None:
        """Compute and update SP breakdown by status.

        Args:
            stories: Lista de historias.
        """
        breakdown: dict[str, int] = {}
        for story in stories:
            sp = story.story_points or 0
            if sp > 0:
                breakdown[story.status] = breakdown.get(story.status, 0) + sp

        total = sum(breakdown.values())
        percentages: dict[str, float] = {}
        if total > 0:
            percentages = {
                status: round(sp / total * 100, 1) for status, sp in breakdown.items()
            }

        self._sp_breakdown = breakdown
        self._sp_total = total
        self._sp_percentages = percentages
        self.sp_breakdown_changed.emit()
        logger.debug("SP breakdown updated: %s (total=%d)", breakdown, total)
