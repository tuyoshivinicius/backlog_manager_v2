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
