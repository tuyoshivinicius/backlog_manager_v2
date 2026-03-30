"""Unit tests for EditStoryUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.story.edit_story_dto import EditStoryInputDTO
from backlog_manager.application.use_cases.story.edit_story import EditStoryUseCase
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


@pytest.fixture
def mock_story():
    """Create a mock Story entity."""
    story = MagicMock(spec=Story)
    story.id = "TEST-001"
    story.component = "TEST"
    story.name = "Test Story"
    story.story_points = StoryPoint(5)
    story.priority = 1
    story.status = StoryStatus.BACKLOG
    story.duration = 3
    story.start_date = None
    story.end_date = None
    story.developer_id = None
    story.feature_id = None
    return story


@pytest.fixture
def mock_story_repo(mock_story):
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=mock_story)
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=True)
    return repo


@pytest.fixture
def mock_uow(mock_story_repo, mock_feature_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    type(uow).features = PropertyMock(return_value=mock_feature_repo)
    return uow


class TestEditStoryDeveloperId:
    """Tests for developer_id propagation in EditStoryUseCase."""

    @pytest.mark.asyncio
    async def test_edit_story_propagates_developer_id(
        self, mock_uow, mock_story
    ) -> None:
        """Verify execute() sets developer_id on entity when provided."""
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(
            story_id="TEST-001",
            name="Test Story",
            developer_id=42,
        )

        await use_case.execute(dto)

        assert mock_story.developer_id == 42

    @pytest.mark.asyncio
    async def test_edit_story_clears_developer_id(self, mock_uow, mock_story) -> None:
        """Verify execute() clears developer_id when None is provided (desatribuicao)."""
        mock_story.developer_id = 42  # Pre-assign
        use_case = EditStoryUseCase(mock_uow)
        dto = EditStoryInputDTO(
            story_id="TEST-001",
            name="Test Story",
            developer_id=None,
        )

        await use_case.execute(dto)

        assert mock_story.developer_id is None
