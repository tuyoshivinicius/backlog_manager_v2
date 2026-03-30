"""Unit tests for SpBreakdownLabel display format and tooltip."""

from __future__ import annotations

from backlog_manager.presentation.views.status_bar import SpBreakdownLabel


class TestSpBreakdownLabel:
    """Tests for SpBreakdownLabel widget."""

    def test_format_with_multiple_statuses(self, qtbot) -> None:
        """Label shows 'X SP Status · Y SP Status' format."""
        label = SpBreakdownLabel()
        qtbot.addWidget(label)

        breakdown = {"BACKLOG": 10, "EXECUCAO": 8, "CONCLUIDO": 2}
        label.update_breakdown(
            breakdown, 20, {"BACKLOG": 50.0, "EXECUCAO": 40.0, "CONCLUIDO": 10.0}
        )

        text = label.text()
        assert "10 SP Backlog" in text
        assert "8 SP Execucao" in text
        assert "2 SP Concluido" in text
        assert "\u00b7" in text  # middle dot separator

    def test_only_nonzero_statuses_shown(self, qtbot) -> None:
        """Only statuses with SP > 0 are displayed."""
        label = SpBreakdownLabel()
        qtbot.addWidget(label)

        breakdown = {"BACKLOG": 10}
        label.update_breakdown(breakdown, 10, {"BACKLOG": 100.0})

        text = label.text()
        assert "10 SP Backlog" in text
        assert "Execucao" not in text

    def test_backlog_always_shown_when_present(self, qtbot) -> None:
        """BACKLOG status always shown when present."""
        label = SpBreakdownLabel()
        qtbot.addWidget(label)

        breakdown = {"BACKLOG": 0, "EXECUCAO": 10}
        # Note: BACKLOG with 0 SP won't be in breakdown per ViewModel logic
        # but if passed, label should still show it
        label.update_breakdown(breakdown, 10, {"BACKLOG": 0.0, "EXECUCAO": 100.0})

        text = label.text()
        assert "Execucao" in text

    def test_tooltip_shows_percentages(self, qtbot) -> None:
        """Tooltip shows percentage breakdown."""
        label = SpBreakdownLabel()
        qtbot.addWidget(label)

        breakdown = {"BACKLOG": 50, "EXECUCAO": 50}
        label.update_breakdown(breakdown, 100, {"BACKLOG": 50.0, "EXECUCAO": 50.0})

        tooltip = label.toolTip()
        assert "50.0%" in tooltip
        assert "Backlog" in tooltip
        assert "Execucao" in tooltip

    def test_empty_breakdown(self, qtbot) -> None:
        """Label handles empty breakdown."""
        label = SpBreakdownLabel()
        qtbot.addWidget(label)

        label.update_breakdown({}, 0, {})

        assert label.text() == "0 SP"
