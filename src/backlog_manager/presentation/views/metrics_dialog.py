"""Metrics Dialog View.

Dialog modal para exibicao de metricas da alocacao.
Dimensoes: 440x380px (fixo, per FR-020).
Auto-show apos allocation_completed se stories_allocated > 0.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

if TYPE_CHECKING:
    from backlog_manager.application.dto.allocation import AllocationMetricsDTO

logger = logging.getLogger(__name__)


class MetricsDialog(QDialog):
    """Dialog modal para exibicao de metricas de alocacao.

    Nao necessita ViewModel — dialog e somente leitura,
    recebe dados via construtor (Principio IX Simplicidade).
    """

    def __init__(
        self,
        metrics: AllocationMetricsDTO,
        parent: QWidget | None = None,
    ) -> None:
        """Initialize the dialog.

        Args:
            metrics: Metricas da alocacao.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self._metrics = metrics

        self._setup_ui()

        logger.debug("MetricsDialog initialized")

    def _setup_ui(self) -> None:
        """Cria e configura a UI do dialog."""
        self.setWindowTitle("Metricas da Alocacao")
        self.setFixedSize(440, 380)
        self.setModal(True)

        layout = QVBoxLayout(self)

        # Metrics grid
        form = QFormLayout()

        m = self._metrics

        form.addRow(
            "Historias Alocadas:",
            QLabel(f"{m.stories_allocated} / {m.stories_processed}"),
        )
        form.addRow(
            "Tempo de Execucao:",
            QLabel(f"{m.total_time_seconds:.2f}s"),
        )
        form.addRow(
            "Ondas Processadas:",
            QLabel(f"{m.waves_processed} ondas"),
        )
        form.addRow(
            "Total Iteracoes:",
            QLabel(f"{m.total_iterations} iteracoes"),
        )
        form.addRow(
            "Deadlocks Detectados:",
            QLabel(f"{m.deadlocks_detected} deadlocks"),
        )
        form.addRow(
            "Violacoes Ociosidade:",
            QLabel(
                f"{m.max_idle_violations_detected} detectados, "
                f"{m.max_idle_violations_fixed} corrigidos"
            ),
        )

        layout.addLayout(form)
        layout.addStretch()

        # OK button
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept)
        layout.addWidget(button_box)
