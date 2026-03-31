"""Integration tests for Status Bar components."""

from __future__ import annotations

from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.viewmodels.main_window_viewmodel import (
    MainWindowViewModel,
)
from backlog_manager.presentation.views.main_window import MainWindow
from backlog_manager.presentation.views.status_bar import StatsLabel, WarningsBadge


class TestStatsLabel:
    """Tests for StatsLabel formatting."""

    def test_initial_text(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        """Test initial label text."""
        label = StatsLabel()
        qtbot.addWidget(label)

        assert "0 historias" in label.text()
        assert "0 SP" in label.text()
        assert "Sem alocacao" in label.text()


class TestWarningsBadge:
    """Tests for WarningsBadge."""

    def test_initially_hidden(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        """Test badge is hidden initially."""
        badge = WarningsBadge()
        qtbot.addWidget(badge)

        assert not badge.isVisible()

    def test_visible_when_count_positive(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        """Test badge becomes visible with positive count."""
        badge = WarningsBadge()
        qtbot.addWidget(badge)

        badge.update_count(3)
        assert badge.isVisible()
        assert "3 avisos" in badge.text()

    def test_hidden_when_count_zero(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        """Test badge is hidden when count is zero."""
        badge = WarningsBadge()
        qtbot.addWidget(badge)

        badge.update_count(5)
        assert badge.isVisible()

        badge.update_count(0)
        assert not badge.isVisible()


class TestStatusBarInMainWindow:
    """Tests for status bar integration in MainWindow."""

    def test_empty_backlog_shows_zero(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test empty backlog shows '0 historias · 0 SP · Sem alocacao'."""
        viewmodel = MainWindowViewModel(container)
        window = MainWindow(viewmodel)
        qtbot.addWidget(window)

        text = window._stats_label.text()
        assert "0 historias" in text
        assert "0 SP" in text
        assert "Sem alocacao" in text
