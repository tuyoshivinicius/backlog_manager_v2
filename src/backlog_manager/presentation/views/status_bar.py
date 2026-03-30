"""Status Bar View Components.

Componentes visuais para a status bar: StatsLabel e WarningsBadge.
"""

from __future__ import annotations

import logging

from PySide6.QtWidgets import QLabel, QPushButton, QWidget

logger = logging.getLogger(__name__)


class StatsLabel(QLabel):
    """Label de estatisticas para a status bar.

    Formato: "X historias · Y SP · Ultima alocacao: DD/MM/YYYY HH:MM"
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the label."""
        super().__init__("0 historias \u00b7 0 SP \u00b7 Sem alocacao", parent)


STATUS_DISPLAY_ORDER = ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"]

STATUS_DISPLAY_NAMES: dict[str, str] = {
    "BACKLOG": "Backlog",
    "EXECUCAO": "Execucao",
    "TESTES": "Testes",
    "CONCLUIDO": "Concluido",
    "IMPEDIDO": "Impedido",
}


class SpBreakdownLabel(QLabel):
    """Label displaying SP breakdown by status in the status bar.

    Format: "X SP Backlog · Y SP Execucao · Z SP Concluido"
    Tooltip: percentage breakdown per status.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the label."""
        super().__init__("0 SP", parent)

    def update_breakdown(
        self,
        breakdown: dict[str, int],
        total: int,
        percentages: dict[str, float],
    ) -> None:
        """Update label text and tooltip with new breakdown data.

        Args:
            breakdown: Map of status -> total SP.
            total: Total SP across all statuses.
            percentages: Map of status -> percentage.
        """
        if not breakdown:
            self.setText("0 SP")
            self.setToolTip("")
            return

        parts = []
        for status in STATUS_DISPLAY_ORDER:
            sp = breakdown.get(status, 0)
            if sp > 0:
                name = STATUS_DISPLAY_NAMES.get(status, status)
                parts.append(f"{sp} SP {name}")

        self.setText(" \u00b7 ".join(parts) if parts else "0 SP")

        tooltip_parts = []
        for status in STATUS_DISPLAY_ORDER:
            if status in percentages:
                name = STATUS_DISPLAY_NAMES.get(status, status)
                tooltip_parts.append(f"{name}: {percentages[status]}%")

        self.setToolTip(" \u00b7 ".join(tooltip_parts))


class WarningsBadge(QPushButton):
    """Badge de warnings para a status bar.

    Exibe "⚠ X avisos" e abre popup ao clicar.
    Oculto quando count == 0.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the badge."""
        super().__init__(parent)
        self.setFlat(True)
        self.setObjectName("warnings-badge")
        self.setVisible(False)

    def update_count(self, count: int) -> None:
        """Atualiza contagem de avisos.

        Args:
            count: Numero de avisos.
        """
        if count > 0:
            self.setText(f"\u26a0 {count} avisos")
            self.setVisible(True)
        else:
            self.setVisible(False)
