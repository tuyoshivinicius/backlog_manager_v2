"""Unit tests for blocking state resolution in StoryTableModel."""

from __future__ import annotations

from PySide6.QtCore import Qt

from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.viewmodels.story_table_model import (
    BLOCKING_STATE_ROLE,
    DEPENDENCY_IDS_ROLE,
    BlockingState,
    StoryTableModel,
)


def _make_story(
    story_id: str = "US-001",
    status: str = "BACKLOG",
    dependency_ids: list[str] | None = None,
) -> StoryOutputDTO:
    """Create a minimal StoryOutputDTO for testing."""
    return StoryOutputDTO(
        id=story_id,
        component="comp",
        name="Test Story",
        story_points=5,
        priority=1,
        status=status,
        duration=None,
        start_date=None,
        end_date=None,
        developer_id=None,
        feature_id=None,
        dependency_ids=dependency_ids or [],
    )


class TestBlockingStateResolution:
    """Tests for blocking state computation in StoryTableModel."""

    def test_no_dependencies_returns_none(self) -> None:
        """Story with no dependencies has NONE blocking state."""
        model = StoryTableModel()
        model.set_stories([_make_story("US-001", "BACKLOG", [])])

        index = model.index(0, 8)  # Dependencias column
        state = model.data(index, BLOCKING_STATE_ROLE)
        assert state == BlockingState.NONE

    def test_all_deps_concluido_returns_free(self) -> None:
        """Story with all deps CONCLUIDO has FREE blocking state."""
        model = StoryTableModel()
        model.set_stories(
            [
                _make_story("US-001", "CONCLUIDO"),
                _make_story("US-002", "BACKLOG", ["US-001"]),
            ]
        )

        index = model.index(1, 8)
        state = model.data(index, BLOCKING_STATE_ROLE)
        assert state == BlockingState.FREE

    def test_dep_not_concluido_returns_blocked(self) -> None:
        """Story with dep not CONCLUIDO has BLOCKED state."""
        model = StoryTableModel()
        model.set_stories(
            [
                _make_story("US-001", "EXECUCAO"),
                _make_story("US-002", "BACKLOG", ["US-001"]),
            ]
        )

        index = model.index(1, 8)
        state = model.data(index, BLOCKING_STATE_ROLE)
        assert state == BlockingState.BLOCKED

    def test_missing_dep_treated_as_blocked(self) -> None:
        """Story with missing dependency ID treated as BLOCKED."""
        model = StoryTableModel()
        model.set_stories(
            [
                _make_story("US-002", "BACKLOG", ["US-999"]),
            ]
        )

        index = model.index(0, 8)
        state = model.data(index, BLOCKING_STATE_ROLE)
        assert state == BlockingState.BLOCKED

    def test_mixed_deps_some_not_concluido(self) -> None:
        """Story with mixed dep statuses returns BLOCKED."""
        model = StoryTableModel()
        model.set_stories(
            [
                _make_story("US-001", "CONCLUIDO"),
                _make_story("US-002", "EXECUCAO"),
                _make_story("US-003", "BACKLOG", ["US-001", "US-002"]),
            ]
        )

        index = model.index(2, 8)
        state = model.data(index, BLOCKING_STATE_ROLE)
        assert state == BlockingState.BLOCKED

    def test_dependency_ids_role_returns_list(self) -> None:
        """DEPENDENCY_IDS_ROLE returns the list of dependency IDs."""
        model = StoryTableModel()
        model.set_stories(
            [
                _make_story("US-001", "BACKLOG", ["US-002", "US-003"]),
            ]
        )

        index = model.index(0, 8)
        ids = model.data(index, DEPENDENCY_IDS_ROLE)
        assert ids == ["US-002", "US-003"]

    def test_blocking_state_role_wrong_column_returns_none(self) -> None:
        """BLOCKING_STATE_ROLE on non-dependency column returns None."""
        model = StoryTableModel()
        model.set_stories([_make_story("US-001", "BACKLOG", ["US-002"])])

        index = model.index(0, 0)  # Prioridade column
        state = model.data(index, BLOCKING_STATE_ROLE)
        assert state is None
