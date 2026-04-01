"""Unit tests for MovePriorityUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.use_cases.story.move_priority import (
    MovePriorityUseCase,
)
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects.story_point import StoryPoint
from backlog_manager.domain.value_objects.story_status import StoryStatus


def _make_story(
    story_id: str = "AUTH-001",
    priority: int = 5,
    component: str = "AUTH",
    name: str = "Test story",
    story_points: StoryPoint = StoryPoint.MEDIUM,
) -> Story:
    """Create a Story entity for testing."""
    return Story(
        id=story_id,
        component=component,
        name=name,
        story_points=story_points,
        priority=priority,
        status=StoryStatus.BACKLOG,
    )


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.get_by_priority = AsyncMock()
    repo.update = AsyncMock()
    repo.get_max_priority = AsyncMock(return_value=10)
    return repo


@pytest.fixture
def mock_uow(mock_story_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return MovePriorityUseCase(mock_uow)


class TestMoveUp:
    """Tests for MovePriorityUseCase.move_up."""

    async def test_raises_when_story_not_found(self, use_case, mock_story_repo):
        """Should raise ValueError when story does not exist."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Historia .* nao encontrada"):
            await use_case.move_up("AUTH-999")

    async def test_raises_when_already_at_top(self, use_case, mock_story_repo):
        """Should raise ValueError when story is already at priority 0."""
        story = _make_story(priority=0)
        mock_story_repo.get_by_id.return_value = story

        with pytest.raises(ValueError, match="ja esta no topo"):
            await use_case.move_up("AUTH-001")

    async def test_swaps_with_adjacent_story(self, use_case, mock_story_repo):
        """Should swap priorities when adjacent story exists."""
        story = _make_story(story_id="AUTH-001", priority=3)
        adjacent = _make_story(story_id="AUTH-002", priority=2)
        mock_story_repo.get_by_id.return_value = story
        mock_story_repo.get_by_priority.return_value = adjacent

        result = await use_case.move_up("AUTH-001")

        assert story.priority == 2
        assert adjacent.priority == 3
        assert mock_story_repo.update.call_count == 2
        assert result.id == "AUTH-001"
        assert result.priority == 2

    async def test_decrements_when_no_adjacent(self, use_case, mock_story_repo):
        """Should decrement priority when no adjacent story (gap)."""
        story = _make_story(priority=5)
        mock_story_repo.get_by_id.return_value = story
        mock_story_repo.get_by_priority.return_value = None

        result = await use_case.move_up("AUTH-001")

        assert story.priority == 4
        assert mock_story_repo.update.call_count == 1
        assert result.priority == 4

    async def test_returns_story_output_dto(self, use_case, mock_story_repo):
        """Should return a StoryOutputDTO with updated data."""
        story = _make_story(priority=2)
        adjacent = _make_story(story_id="AUTH-002", priority=1)
        mock_story_repo.get_by_id.return_value = story
        mock_story_repo.get_by_priority.return_value = adjacent

        result = await use_case.move_up("AUTH-001")

        assert result.id == "AUTH-001"
        assert result.component == "AUTH"


class TestMoveDown:
    """Tests for MovePriorityUseCase.move_down."""

    async def test_raises_when_story_not_found(self, use_case, mock_story_repo):
        """Should raise ValueError when story does not exist."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Historia .* nao encontrada"):
            await use_case.move_down("AUTH-999")

    async def test_raises_when_already_at_bottom(self, use_case, mock_story_repo):
        """Should raise ValueError when no story exists below."""
        story = _make_story(priority=10)
        mock_story_repo.get_by_id.return_value = story
        # validate_can_move_down checks get_by_priority(priority+1)
        # First call is from validate_can_move_down, returns None meaning can't move
        mock_story_repo.get_by_priority.return_value = None

        with pytest.raises(ValueError, match="ja esta no fim"):
            await use_case.move_down("AUTH-001")

    async def test_swaps_with_adjacent_story(self, use_case, mock_story_repo):
        """Should swap priorities when adjacent story exists below."""
        story = _make_story(story_id="AUTH-001", priority=3)
        adjacent = _make_story(story_id="AUTH-002", priority=4)
        mock_story_repo.get_by_id.return_value = story
        # Both validate_can_move_down and the adjacent lookup use get_by_priority(4)
        mock_story_repo.get_by_priority.return_value = adjacent

        result = await use_case.move_down("AUTH-001")

        assert story.priority == 4
        assert adjacent.priority == 3
        assert mock_story_repo.update.call_count == 2
        assert result.priority == 4

    async def test_increments_when_no_adjacent_after_validation(
        self, use_case, mock_story_repo
    ):
        """Should increment priority when validation passes but no adjacent found."""
        story = _make_story(story_id="AUTH-001", priority=3)
        adjacent_for_validation = _make_story(story_id="AUTH-002", priority=4)
        mock_story_repo.get_by_id.return_value = story
        # First call (validate_can_move_down) returns a story, second call returns None
        mock_story_repo.get_by_priority.side_effect = [
            adjacent_for_validation,
            None,
        ]

        result = await use_case.move_down("AUTH-001")

        assert story.priority == 4
        assert mock_story_repo.update.call_count == 1
        assert result.priority == 4

    async def test_returns_story_output_dto(self, use_case, mock_story_repo):
        """Should return a StoryOutputDTO with updated data."""
        story = _make_story(priority=2)
        adjacent = _make_story(story_id="AUTH-002", priority=3)
        mock_story_repo.get_by_id.return_value = story
        mock_story_repo.get_by_priority.return_value = adjacent

        result = await use_case.move_down("AUTH-001")

        assert result.id == "AUTH-001"
        assert result.component == "AUTH"
