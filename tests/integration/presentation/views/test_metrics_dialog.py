"""Integration tests for MetricsDialog."""

from __future__ import annotations

from backlog_manager.application.dto.allocation import AllocationMetricsDTO
from backlog_manager.presentation.views.metrics_dialog import MetricsDialog


def _make_metrics(**kwargs) -> AllocationMetricsDTO:  # type: ignore[no-untyped-def]
    """Create a minimal AllocationMetricsDTO for testing."""
    defaults = {
        "total_time_seconds": 1.23,
        "stories_processed": 10,
        "stories_allocated": 8,
        "waves_processed": 3,
        "total_iterations": 15,
        "deadlocks_detected": 1,
        "max_idle_violations_detected": 2,
        "max_idle_violations_fixed": 1,
    }
    defaults.update(kwargs)
    return AllocationMetricsDTO(**defaults)


class TestMetricsDialogDisplay:
    """Tests for MetricsDialog display."""

    def test_dialog_title(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        """Test dialog has correct title."""
        metrics = _make_metrics()
        dialog = MetricsDialog(metrics)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Metricas da Alocacao"

    def test_dialog_fixed_size(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        """Test dialog has fixed size 440x380."""
        metrics = _make_metrics()
        dialog = MetricsDialog(metrics)
        qtbot.addWidget(dialog)

        assert dialog.width() == 440
        assert dialog.height() == 380

    def test_dialog_is_modal(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        """Test dialog is modal."""
        metrics = _make_metrics()
        dialog = MetricsDialog(metrics)
        qtbot.addWidget(dialog)

        assert dialog.isModal()
