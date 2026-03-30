"""Unit tests for StatusBarViewModel.update_sp_breakdown()."""

from __future__ import annotations

from PySide6.QtCore import QObject

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.status_bar_viewmodel import (
    StatusBarViewModel,
)


def _make_story(
    story_id: str = "US-001",
    status: str = "BACKLOG",
    story_points: int = 5,
) -> StoryOutputDTO:
    """Create a minimal StoryOutputDTO for testing."""
    return StoryOutputDTO(
        id=story_id,
        component="comp",
        name="Test Story",
        story_points=story_points,
        priority=1,
        status=status,
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        feature_id=None,
    )


class TestSpBreakdownComputation:
    """Tests for SP breakdown computation in StatusBarViewModel."""

    def test_breakdown_with_mixed_statuses(self) -> None:
        """SP breakdown correctly aggregates points by status."""
        vm = StatusBarViewModel()
        stories = [
            _make_story("US-001", "BACKLOG", 5),
            _make_story("US-002", "BACKLOG", 3),
            _make_story("US-003", "EXECUCAO", 8),
            _make_story("US-004", "CONCLUIDO", 2),
            _make_story("US-005", "TESTES", 4),
        ]

        vm.update_sp_breakdown(stories)

        assert vm.sp_breakdown == {
            "BACKLOG": 8,
            "EXECUCAO": 8,
            "TESTES": 4,
            "CONCLUIDO": 2,
        }
        assert vm.sp_total == 22

    def test_breakdown_with_empty_backlog(self) -> None:
        """SP breakdown handles empty story list."""
        vm = StatusBarViewModel()
        vm.update_sp_breakdown([])

        assert vm.sp_breakdown == {}
        assert vm.sp_total == 0

    def test_breakdown_with_all_statuses(self) -> None:
        """SP breakdown includes all 5 statuses when present."""
        vm = StatusBarViewModel()
        stories = [
            _make_story("US-001", "BACKLOG", 10),
            _make_story("US-002", "EXECUCAO", 8),
            _make_story("US-003", "TESTES", 6),
            _make_story("US-004", "CONCLUIDO", 4),
            _make_story("US-005", "IMPEDIDO", 2),
        ]

        vm.update_sp_breakdown(stories)

        assert vm.sp_breakdown == {
            "BACKLOG": 10,
            "EXECUCAO": 8,
            "TESTES": 6,
            "CONCLUIDO": 4,
            "IMPEDIDO": 2,
        }
        assert vm.sp_total == 30

    def test_percentages(self) -> None:
        """SP percentages computed correctly."""
        vm = StatusBarViewModel()
        stories = [
            _make_story("US-001", "BACKLOG", 50),
            _make_story("US-002", "EXECUCAO", 50),
        ]

        vm.update_sp_breakdown(stories)

        assert vm.sp_percentages["BACKLOG"] == 50.0
        assert vm.sp_percentages["EXECUCAO"] == 50.0

    def test_percentages_empty(self) -> None:
        """SP percentages are empty for no stories."""
        vm = StatusBarViewModel()
        vm.update_sp_breakdown([])

        assert vm.sp_percentages == {}

    def test_signal_emitted(self, qtbot) -> None:
        """sp_breakdown_changed signal emitted on update."""
        vm = StatusBarViewModel()
        stories = [_make_story("US-001", "BACKLOG", 5)]

        with qtbot.waitSignal(vm.sp_breakdown_changed, timeout=1000):
            vm.update_sp_breakdown(stories)

    def test_zero_sp_statuses_excluded(self) -> None:
        """Statuses with 0 SP are not in breakdown."""
        vm = StatusBarViewModel()
        stories = [
            _make_story("US-001", "BACKLOG", 0),
            _make_story("US-002", "EXECUCAO", 10),
        ]

        vm.update_sp_breakdown(stories)

        assert "BACKLOG" not in vm.sp_breakdown
        assert vm.sp_breakdown == {"EXECUCAO": 10}
