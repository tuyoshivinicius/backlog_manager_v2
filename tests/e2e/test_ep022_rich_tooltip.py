"""E2E tests for RichTooltipWidget.

Tests verify tooltip layout, content display, and design token usage.
"""

from __future__ import annotations

import pytest
from backlog_manager.presentation.theme import DESIGN_TOKENS
from backlog_manager.presentation.views.rich_tooltip import RichTooltipWidget
from PySide6.QtCore import Qt

pytestmark = [pytest.mark.e2e]


@pytest.fixture
def sample_data() -> dict[str, str]:
    """Sample story data for tooltip."""
    return {
        "ID": "TEST-001",
        "Nome": "Implementar login",
        "Status": "EXECUCAO",
        "SP": "5",
        "Feature": "Auth",
        "Desenvolvedor": "Dev 1",
        "Dependencias": "TEST-002",
        "Inicio": "2026-01-15",
        "Fim": "2026-01-20",
    }


class TestRichTooltipWidget:
    """Tests for RichTooltipWidget."""

    def test_tooltip_creates_successfully(self, qtbot, sample_data):
        """Tooltip widget can be created with sample data."""
        tooltip = RichTooltipWidget(sample_data)
        qtbot.addWidget(tooltip)
        assert tooltip is not None

    def test_tooltip_max_width(self, qtbot, sample_data):
        """Tooltip respects MAX_WIDTH constraint."""
        tooltip = RichTooltipWidget(sample_data)
        qtbot.addWidget(tooltip)
        assert tooltip.maximumWidth() == RichTooltipWidget.MAX_WIDTH

    def test_tooltip_has_frameless_hint(self, qtbot, sample_data):
        """Tooltip has ToolTip and FramelessWindowHint flags."""
        tooltip = RichTooltipWidget(sample_data)
        qtbot.addWidget(tooltip)
        flags = tooltip.windowFlags()
        assert flags & Qt.WindowType.FramelessWindowHint

    def test_tooltip_uses_design_tokens_in_stylesheet(self, qtbot, sample_data):
        """Tooltip stylesheet uses DESIGN_TOKENS colors."""
        tooltip = RichTooltipWidget(sample_data)
        qtbot.addWidget(tooltip)
        stylesheet = tooltip.styleSheet()
        assert DESIGN_TOKENS["background"] in stylesheet
        assert DESIGN_TOKENS["neutral-300"] in stylesheet

    def test_tooltip_shows_status_badge(self, qtbot, sample_data):
        """Tooltip displays status with correct palette colors."""
        from backlog_manager.presentation.theme import STATUS_PALETTE

        tooltip = RichTooltipWidget(sample_data)
        qtbot.addWidget(tooltip)

        # Find QLabels containing status text
        from PySide6.QtWidgets import QLabel

        labels = tooltip.findChildren(QLabel)
        status_labels = [l for l in labels if l.text() == "EXECUCAO"]
        assert len(status_labels) >= 1

        config = STATUS_PALETTE["EXECUCAO"]
        assert config.background in status_labels[0].styleSheet()

    def test_tooltip_shows_em_dash_for_missing_data(self, qtbot):
        """Missing fields show em-dash placeholder."""
        tooltip = RichTooltipWidget({"ID": "X-001"})
        qtbot.addWidget(tooltip)

        from PySide6.QtWidgets import QLabel

        labels = tooltip.findChildren(QLabel)
        texts = [l.text() for l in labels]
        # Nome and other fields should default to em-dash
        assert "\u2014" in texts

    def test_tooltip_size_hint(self, qtbot, sample_data):
        """sizeHint width does not exceed MAX_WIDTH."""
        tooltip = RichTooltipWidget(sample_data)
        qtbot.addWidget(tooltip)
        assert tooltip.sizeHint().width() <= RichTooltipWidget.MAX_WIDTH
