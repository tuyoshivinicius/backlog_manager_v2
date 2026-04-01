"""Headless tests for StatusBarViewModel."""

from __future__ import annotations

from datetime import datetime
from unittest.mock import patch

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.status_bar_viewmodel import (
        StatusBarViewModel,
    )

from backlog_manager.application.dto.story import StoryOutputDTO  # noqa: E402

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests — update_stats
# ---------------------------------------------------------------------------


class TestStatusBarViewModelUpdateStats:
    """Tests for update_stats()."""

    def test_update_stats_sets_count_and_sp(self) -> None:
        vm = StatusBarViewModel()
        stories = [_make_story("S1", 3), _make_story("S2", 5)]
        vm.update_stats(stories)

        assert vm.story_count == 2
        assert vm.total_sp == 8

    def test_update_stats_emits_signal(self) -> None:
        vm = StatusBarViewModel()
        vm.update_stats([_make_story("S1")])

        assert len(vm.stats_changed.emissions) == 1

    def test_update_stats_empty_list(self) -> None:
        vm = StatusBarViewModel()
        vm.update_stats([])

        assert vm.story_count == 0
        assert vm.total_sp == 0

    def test_update_stats_handles_none_sp(self) -> None:
        vm = StatusBarViewModel()
        story = _make_story("S1", 0)
        story.story_points = None  # type: ignore[assignment]
        vm.update_stats([story])

        assert vm.total_sp == 0


# ---------------------------------------------------------------------------
# Tests — set_warnings
# ---------------------------------------------------------------------------


class TestStatusBarViewModelWarnings:
    """Tests for set_warnings()."""

    def test_set_warnings_updates_count(self) -> None:
        vm = StatusBarViewModel()
        vm.set_warnings(["Warning 1", "Warning 2"])

        assert vm.warning_count == 2
        assert len(vm.warnings) == 2

    def test_set_warnings_emits_signal(self) -> None:
        vm = StatusBarViewModel()
        vm.set_warnings(["W1"])

        assert len(vm.warnings_changed.emissions) == 1

    def test_set_empty_warnings(self) -> None:
        vm = StatusBarViewModel()
        vm.set_warnings(["W1"])
        vm.set_warnings([])

        assert vm.warning_count == 0
        assert vm.warnings == []

    def test_warnings_returns_copy(self) -> None:
        vm = StatusBarViewModel()
        vm.set_warnings(["W1"])
        warnings = vm.warnings
        warnings.append("W2")
        assert len(vm.warnings) == 1


# ---------------------------------------------------------------------------
# Tests — set_last_allocation
# ---------------------------------------------------------------------------


class TestStatusBarViewModelLastAllocation:
    """Tests for set_last_allocation()."""

    def test_set_last_allocation(self) -> None:
        vm = StatusBarViewModel()
        ts = datetime(2026, 3, 28, 14, 30)
        vm.set_last_allocation(ts)

        assert vm.last_allocation == ts

    def test_set_last_allocation_emits_signal(self) -> None:
        vm = StatusBarViewModel()
        vm.set_last_allocation(datetime.now())

        assert len(vm.stats_changed.emissions) == 1

    def test_clear_last_allocation(self) -> None:
        vm = StatusBarViewModel()
        vm.set_last_allocation(datetime.now())
        vm.clear_last_allocation()

        assert vm.last_allocation is None
        # Two emissions: one from set, one from clear
        assert len(vm.stats_changed.emissions) == 2
