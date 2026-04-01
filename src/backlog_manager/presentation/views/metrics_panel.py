"""Metrics Panel View.

This module provides a QWidget for displaying allocation metrics.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from PySide6.QtWidgets import QFormLayout, QGroupBox, QLabel, QVBoxLayout, QWidget

from backlog_manager.application.dto.allocation import AllocationMetricsDTO

if TYPE_CHECKING:
    pass  # Required for conditional imports used by type checkers only

logger = logging.getLogger(__name__)


class MetricsPanel(QWidget):
    """Panel for displaying allocation metrics.

    Shows key metrics from the last allocation execution.
    """

    def __init__(self, parent: QWidget | None = None) -> None:
        """Initialize the panel.

        Args:
            parent: Optional parent widget.
        """
        super().__init__(parent)

        self._setup_ui()

        logger.debug("MetricsPanel initialized")

    def _setup_ui(self) -> None:
        """Create and configure the panel UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        # Metrics group
        metrics_group = QGroupBox("Metricas da Alocacao")
        form_layout = QFormLayout(metrics_group)

        # Metrics labels
        self._stories_allocated_label = QLabel("-")
        form_layout.addRow("Historias Alocadas:", self._stories_allocated_label)

        self._time_label = QLabel("-")
        form_layout.addRow("Tempo de Execucao:", self._time_label)

        self._waves_label = QLabel("-")
        form_layout.addRow("Ondas Processadas:", self._waves_label)

        self._iterations_label = QLabel("-")
        form_layout.addRow("Total Iteracoes:", self._iterations_label)

        self._deadlocks_label = QLabel("-")
        form_layout.addRow("Deadlocks Detectados:", self._deadlocks_label)

        self._idle_violations_label = QLabel("-")
        form_layout.addRow("Violacoes Ociosidade:", self._idle_violations_label)

        layout.addWidget(metrics_group)
        layout.addStretch()

    def set_metrics(self, metrics: AllocationMetricsDTO) -> None:
        """Update the panel with allocation metrics.

        Args:
            metrics: Allocation metrics DTO.
        """
        self._stories_allocated_label.setText(
            f"{metrics.stories_allocated} / {metrics.stories_processed}"
        )
        self._time_label.setText(f"{metrics.total_time_seconds:.2f}s")
        self._waves_label.setText(str(metrics.waves_processed))
        self._iterations_label.setText(str(metrics.total_iterations))
        self._deadlocks_label.setText(str(metrics.deadlocks_detected))
        self._idle_violations_label.setText(
            f"{metrics.max_idle_violations_detected} detectadas, "
            f"{metrics.max_idle_violations_fixed} corrigidas"
        )

        logger.debug("Metrics panel updated")

    def clear(self) -> None:
        """Clear all metrics display."""
        self._stories_allocated_label.setText("-")
        self._time_label.setText("-")
        self._waves_label.setText("-")
        self._iterations_label.setText("-")
        self._deadlocks_label.setText("-")
        self._idle_violations_label.setText("-")
