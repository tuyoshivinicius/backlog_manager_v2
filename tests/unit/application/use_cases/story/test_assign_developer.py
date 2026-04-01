"""Unit tests for AssignDeveloperUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.use_cases.story.assign_developer import (
    AssignDeveloperUseCase,
)
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects.story_point import StoryPoint
from backlog_manager.domain.value_objects.story_status import StoryStatus


def _make_story(
    story_id: str = "AUTH-001",
    priority: int = 1,
    developer_id: int | None = None,
) -> Story:
    """Create a Story entity for testing."""
    return Story(
        id=story_id,
        component="AUTH",
        name="Test story",
        story_points=StoryPoint.MEDIUM,
        priority=priority,
        status=StoryStatus.BACKLOG,
        developer_id=developer_id,
    )


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_developer_repo():
    """Create mock developer repository."""
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def mock_uow(mock_story_repo, mock_developer_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    type(uow).developers = PropertyMock(return_value=mock_developer_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return AssignDeveloperUseCase(mock_uow)


class TestAssign:
    """Tests for AssignDeveloperUseCase.assign."""

    async def test_assigns_developer_to_story(
        self, use_case, mock_story_repo, mock_developer_repo
    ):
        """Should set developer_id on the story and persist."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story
        mock_developer_repo.exists.return_value = True

        result = await use_case.assign("AUTH-001", 42)

        assert story.developer_id == 42
        mock_story_repo.update.assert_called_once_with(story)
        assert result.developer_id == 42

    async def test_raises_when_story_not_found(self, use_case, mock_story_repo):
        """Should raise ValueError when story does not exist."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Historia .* nao encontrada"):
            await use_case.assign("AUTH-999", 1)

    async def test_raises_when_developer_not_found(
        self, use_case, mock_story_repo, mock_developer_repo
    ):
        """Should raise ValueError when developer does not exist."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story
        mock_developer_repo.exists.return_value = False

        with pytest.raises(ValueError, match="Desenvolvedor .* nao encontrado"):
            await use_case.assign("AUTH-001", 999)

    async def test_validates_developer_exists(
        self, use_case, mock_story_repo, mock_developer_repo
    ):
        """Should check developer existence before assigning."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story
        mock_developer_repo.exists.return_value = True

        await use_case.assign("AUTH-001", 7)

        mock_developer_repo.exists.assert_called_once_with(7)

    async def test_does_not_update_when_developer_missing(
        self, use_case, mock_story_repo, mock_developer_repo
    ):
        """Should not persist when developer validation fails."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story
        mock_developer_repo.exists.return_value = False

        with pytest.raises(ValueError):
            await use_case.assign("AUTH-001", 999)

        mock_story_repo.update.assert_not_called()

    async def test_returns_story_output_dto(
        self, use_case, mock_story_repo, mock_developer_repo
    ):
        """Should return StoryOutputDTO with all fields."""
        story = _make_story()
        mock_story_repo.get_by_id.return_value = story
        mock_developer_repo.exists.return_value = True

        result = await use_case.assign("AUTH-001", 1)

        assert result.id == "AUTH-001"
        assert result.component == "AUTH"
        assert result.status == "BACKLOG"


class TestUnassign:
    """Tests for AssignDeveloperUseCase.unassign."""

    async def test_removes_developer_from_story(self, use_case, mock_story_repo):
        """Should set developer_id to None and persist."""
        story = _make_story(developer_id=42)
        mock_story_repo.get_by_id.return_value = story

        result = await use_case.unassign("AUTH-001")

        assert story.developer_id is None
        mock_story_repo.update.assert_called_once_with(story)
        assert result.developer_id is None

    async def test_raises_when_story_not_found(self, use_case, mock_story_repo):
        """Should raise ValueError when story does not exist."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Historia .* nao encontrada"):
            await use_case.unassign("AUTH-999")

    async def test_unassign_already_unassigned(self, use_case, mock_story_repo):
        """Should succeed even if story has no developer assigned."""
        story = _make_story(developer_id=None)
        mock_story_repo.get_by_id.return_value = story

        result = await use_case.unassign("AUTH-001")

        assert result.developer_id is None
        mock_story_repo.update.assert_called_once()

    async def test_does_not_update_when_story_missing(self, use_case, mock_story_repo):
        """Should not persist when story not found."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError):
            await use_case.unassign("AUTH-999")

        mock_story_repo.update.assert_not_called()

    async def test_returns_story_output_dto(self, use_case, mock_story_repo):
        """Should return StoryOutputDTO with updated data."""
        story = _make_story(developer_id=10)
        mock_story_repo.get_by_id.return_value = story

        result = await use_case.unassign("AUTH-001")

        assert result.id == "AUTH-001"
        assert result.developer_id is None
