"""Unit tests for StatusBarViewModel."""

from __future__ import annotations

from datetime import datetime

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.status_bar_viewmodel import (
    StatusBarViewModel,
)


def _make_story(story_id: str, sp: int = 3) -> StoryOutputDTO:
    """Create a minimal StoryOutputDTO for testing."""
    return StoryOutputDTO(
        id=story_id,
        component="COMP",
        name=f"Story {story_id}",
        story_points=sp,
        status="BACKLOG",
        priority=1,
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        feature_id=None,
    )


class TestStatusBarViewModelUpdateStats:
    """Tests for update_stats()."""

    def test_update_stats_sets_count_and_sp(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        stories = [_make_story("S1", 3), _make_story("S2", 5)]
        vm.update_stats(stories)

        assert vm.story_count == 2
        assert vm.total_sp == 8

    def test_update_stats_emits_signal(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        with qtbot.waitSignal(vm.stats_changed, timeout=1000):
            vm.update_stats([_make_story("S1")])

    def test_update_stats_empty_list(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        vm.update_stats([])

        assert vm.story_count == 0
        assert vm.total_sp == 0

    def test_update_stats_handles_none_sp(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        story = _make_story("S1", 0)
        story.story_points = None  # type: ignore[assignment]
        vm.update_stats([story])

        assert vm.total_sp == 0


class TestStatusBarViewModelWarnings:
    """Tests for set_warnings()."""

    def test_set_warnings_updates_count(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        vm.set_warnings(["Warning 1", "Warning 2"])

        assert vm.warning_count == 2
        assert len(vm.warnings) == 2

    def test_set_warnings_emits_signal(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        with qtbot.waitSignal(vm.warnings_changed, timeout=1000):
            vm.set_warnings(["W1"])

    def test_set_empty_warnings(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        vm.set_warnings(["W1"])
        vm.set_warnings([])

        assert vm.warning_count == 0
        assert vm.warnings == []

    def test_warnings_returns_copy(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        vm.set_warnings(["W1"])
        warnings = vm.warnings
        warnings.append("W2")
        assert len(vm.warnings) == 1


class TestStatusBarViewModelLastAllocation:
    """Tests for set_last_allocation()."""

    def test_set_last_allocation(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        ts = datetime(2026, 3, 28, 14, 30)
        vm.set_last_allocation(ts)

        assert vm.last_allocation == ts

    def test_set_last_allocation_emits_signal(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        vm = StatusBarViewModel()
        with qtbot.waitSignal(vm.stats_changed, timeout=1000):
            vm.set_last_allocation(datetime.now())
