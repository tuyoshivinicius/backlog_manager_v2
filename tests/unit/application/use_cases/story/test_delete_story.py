"""Unit tests for DeleteStoryUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.use_cases.story.delete_story import DeleteStoryUseCase
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects.story_point import StoryPoint
from backlog_manager.domain.value_objects.story_status import StoryStatus


def _make_story(story_id: str = "AUTH-001") -> Story:
    """Create a Story entity for testing."""
    return Story(
        planning_id=1,
        id=story_id,
        component="AUTH",
        name="Test story",
        story_points=StoryPoint.MEDIUM,
        priority=1,
        status=StoryStatus.BACKLOG,
    )


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.remove_all_for_story = AsyncMock()
    return repo


@pytest.fixture
def mock_uow(mock_story_repo, mock_dependency_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    type(uow).dependencies = PropertyMock(return_value=mock_dependency_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return DeleteStoryUseCase(mock_uow)


class TestDeleteStoryUseCase:
    """Tests for DeleteStoryUseCase.execute."""

    async def test_deletes_existing_story(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should delete story and its dependencies."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story

        await use_case.execute(1, "AUTH-001")

        mock_dependency_repo.remove_all_for_story.assert_called_once_with(1, "AUTH-001")
        mock_story_repo.delete.assert_called_once_with(1, "AUTH-001")

    async def test_raises_when_story_not_found(self, use_case, mock_story_repo):
        """Should raise ValueError when story does not exist."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Historia .* nao encontrada"):
            await use_case.execute(1, "AUTH-999")

    async def test_removes_dependencies_before_deleting(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should remove all dependencies before deleting the story."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story

        call_order: list[str] = []
        mock_dependency_repo.remove_all_for_story.side_effect = (
            lambda *a: call_order.append("remove_deps")
        )
        mock_story_repo.delete.side_effect = lambda *a: call_order.append("delete")

        await use_case.execute(1, "AUTH-001")

        assert call_order == ["remove_deps", "delete"]

    async def test_does_not_delete_when_story_missing(
        self, use_case, mock_story_repo, mock_dependency_repo
    ):
        """Should not call delete or remove_all when story not found."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError):
            await use_case.execute(1, "AUTH-999")

        mock_dependency_repo.remove_all_for_story.assert_not_called()
        mock_story_repo.delete.assert_not_called()

    async def test_returns_none(self, use_case, mock_story_repo):
        """Should return None on successful deletion."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story

        result = await use_case.execute(1, "AUTH-001")

        assert result is None

    async def test_validates_story_id_lookup(self, use_case, mock_story_repo):
        """Should look up story by the provided ID."""
        story = _make_story(story_id="CORE-005")
        mock_story_repo.get_by_id.return_value = story

        await use_case.execute(1, "CORE-005")

        mock_story_repo.get_by_id.assert_called_once_with(1, "CORE-005")
