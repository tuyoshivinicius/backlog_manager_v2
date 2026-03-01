"""Unit tests for CreateStoryUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.story.create_story_dto import CreateStoryInputDTO
from backlog_manager.application.use_cases.story.create_story import CreateStoryUseCase


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_max_id_number = AsyncMock(return_value=0)
    repo.get_max_priority = AsyncMock(return_value=0)
    repo.add = AsyncMock()
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


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return CreateStoryUseCase(mock_uow)


class TestCreateStoryUseCase:
    """Tests for CreateStoryUseCase."""

    async def test_creates_story_with_generated_id(self, use_case, mock_story_repo):
        """Should create story with auto-generated ID."""
        mock_story_repo.get_max_id_number.return_value = 0
        mock_story_repo.get_max_priority.return_value = 0

        input_dto = CreateStoryInputDTO(
            component="AUTH",
            name="Implement login",
            story_points=5,
        )

        result = await use_case.execute(input_dto)

        assert result.id == "AUTH-001"
        assert result.name == "Implement login"
        assert result.story_points == 5
        assert result.priority == 1
        assert result.status == "BACKLOG"

    async def test_increments_id_for_existing_component(
        self, use_case, mock_story_repo
    ):
        """Should increment ID from existing max."""
        mock_story_repo.get_max_id_number.return_value = 5
        mock_story_repo.get_max_priority.return_value = 10

        input_dto = CreateStoryInputDTO(
            component="core",  # lowercase to test normalization
            name="Test story",
            story_points=3,
        )

        result = await use_case.execute(input_dto)

        assert result.id == "CORE-006"
        assert result.component == "CORE"
        assert result.priority == 11

    async def test_persists_story(self, use_case, mock_story_repo):
        """Should call repository add."""
        input_dto = CreateStoryInputDTO(
            component="AUTH",
            name="Test",
            story_points=3,
        )

        await use_case.execute(input_dto)

        mock_story_repo.add.assert_called_once()
        added_story = mock_story_repo.add.call_args[0][0]
        assert added_story.id == "AUTH-001"

    async def test_validates_feature_exists(self, use_case, mock_feature_repo):
        """Should validate feature exists when provided."""
        input_dto = CreateStoryInputDTO(
            component="AUTH",
            name="Test",
            story_points=3,
            feature_id=42,
        )

        await use_case.execute(input_dto)

        mock_feature_repo.exists.assert_called_once_with(42)

    async def test_raises_when_feature_not_found(self, use_case, mock_feature_repo):
        """Should raise ValueError when feature doesn't exist."""
        mock_feature_repo.exists.return_value = False

        input_dto = CreateStoryInputDTO(
            component="AUTH",
            name="Test",
            story_points=3,
            feature_id=999,
        )

        with pytest.raises(ValueError, match="Feature com ID 999 nao encontrada"):
            await use_case.execute(input_dto)

    async def test_skips_feature_validation_when_none(
        self, use_case, mock_feature_repo
    ):
        """Should not validate feature when None."""
        input_dto = CreateStoryInputDTO(
            component="AUTH",
            name="Test",
            story_points=3,
            feature_id=None,
        )

        await use_case.execute(input_dto)

        mock_feature_repo.exists.assert_not_called()

    async def test_returns_story_output_dto(self, use_case):
        """Should return StoryOutputDTO with all fields."""
        input_dto = CreateStoryInputDTO(
            component="AUTH",
            name="Full story",
            story_points=8,
            feature_id=None,
        )

        result = await use_case.execute(input_dto)

        assert hasattr(result, "id")
        assert hasattr(result, "component")
        assert hasattr(result, "name")
        assert hasattr(result, "story_points")
        assert hasattr(result, "priority")
        assert hasattr(result, "status")
        assert hasattr(result, "duration")
        assert hasattr(result, "start_date")
        assert hasattr(result, "end_date")
        assert hasattr(result, "developer_id")
        assert hasattr(result, "feature_id")
