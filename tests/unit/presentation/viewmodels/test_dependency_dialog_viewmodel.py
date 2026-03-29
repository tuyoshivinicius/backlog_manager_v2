"""Unit tests for DependencyDialogViewModel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.dependency_dialog_viewmodel import (
    DependencyDialogViewModel,
)


def _make_story(story_id: str, name: str = "Story") -> StoryOutputDTO:
    """Create a minimal StoryOutputDTO for testing."""
    return StoryOutputDTO(
        id=story_id,
        component="COMP",
        name=f"{name} {story_id}",
        story_points=3,
        status="BACKLOG",
        priority=1,
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        feature_id=None,
    )


def _make_vm(qapp) -> DependencyDialogViewModel:  # type: ignore[no-untyped-def]
    """Create a DependencyDialogViewModel with mock container."""
    container = MagicMock()
    return DependencyDialogViewModel(container)


class TestDependencyDialogViewModelSetStory:
    """Tests for set_story()."""

    def test_set_story_sets_properties(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        stories = [_make_story("S1"), _make_story("S2"), _make_story("S3")]
        vm.set_story("S1", "Story S1", stories)

        assert vm.story_id == "S1"
        assert vm.story_name == "Story S1"
        assert len(vm.available_stories) == 2  # S2 and S3 (not S1)

    def test_set_story_excludes_current(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        stories = [_make_story("S1"), _make_story("S2")]
        vm.set_story("S1", "Story S1", stories)

        ids = [s.id for s in vm.available_stories]
        assert "S1" not in ids
        assert "S2" in ids

    def test_set_story_clears_cycle_error(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm._has_cycle_error = True
        vm._cycle_error_message = "Old error"
        vm.set_story("S1", "Story S1", [])

        assert not vm.has_cycle_error
        assert vm.cycle_error_message == ""


class TestDependencyDialogViewModelProperties:
    """Tests for readonly properties."""

    def test_initial_state(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        assert vm.story_id == ""
        assert vm.story_name == ""
        assert vm.depends_on == []
        assert vm.dependents == []
        assert not vm.has_cycle_error
