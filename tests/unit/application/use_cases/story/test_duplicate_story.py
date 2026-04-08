"""Unit tests for DuplicateStoryUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.use_cases.story.duplicate_story import (
    DuplicateStoryUseCase,
)
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects.story_point import StoryPoint
from backlog_manager.domain.value_objects.story_status import StoryStatus


def _make_story(
    story_id: str = "AUTH-001",
    priority: int = 1,
    name: str = "Original story",
    component: str = "AUTH",
    story_points: StoryPoint = StoryPoint.MEDIUM,
    feature_id: int | None = None,
) -> Story:
    """Create a Story entity for testing."""
    return Story(
        planning_id=1,
        id=story_id,
        component=component,
        name=name,
        story_points=story_points,
        priority=priority,
        status=StoryStatus.BACKLOG,
        feature_id=feature_id,
    )


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock()
    repo.add = AsyncMock()
    repo.get_max_id_number = AsyncMock(return_value=1)
    repo.get_max_priority = AsyncMock(return_value=5)
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
    return DuplicateStoryUseCase(mock_uow)


class TestDuplicateStoryUseCase:
    """Tests for DuplicateStoryUseCase.execute."""

    async def test_raises_when_story_not_found(self, use_case, mock_story_repo):
        """Should raise ValueError when original story does not exist."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Historia .* nao encontrada"):
            await use_case.execute(1, "AUTH-999")

    async def test_creates_duplicate_with_new_id(self, use_case, mock_story_repo):
        """Should create a copy with a new generated ID."""
        original = _make_story()
        mock_story_repo.get_by_id.return_value = original
        mock_story_repo.get_max_id_number.return_value = 1

        result = await use_case.execute(1, "AUTH-001")

        assert result.id == "AUTH-002"
        assert result.id != original.id

    async def test_duplicate_has_copy_suffix_in_name(self, use_case, mock_story_repo):
        """Should append '(copia)' to the name."""
        original = _make_story(name="Implement login")
        mock_story_repo.get_by_id.return_value = original

        result = await use_case.execute(1, "AUTH-001")

        assert result.name == "Implement login (copia)"

    async def test_duplicate_gets_next_priority(self, use_case, mock_story_repo):
        """Should assign next available priority (end of queue)."""
        original = _make_story(priority=2)
        mock_story_repo.get_by_id.return_value = original
        mock_story_repo.get_max_priority.return_value = 10

        result = await use_case.execute(1, "AUTH-001")

        assert result.priority == 11

    async def test_duplicate_has_backlog_status(self, use_case, mock_story_repo):
        """Should set status to BACKLOG regardless of original."""
        original = _make_story()
        original.status = StoryStatus.BACKLOG
        mock_story_repo.get_by_id.return_value = original

        result = await use_case.execute(1, "AUTH-001")

        assert result.status == "BACKLOG"

    async def test_duplicate_preserves_component(self, use_case, mock_story_repo):
        """Should keep the same component as the original."""
        original = _make_story(component="CORE")
        mock_story_repo.get_by_id.return_value = original
        mock_story_repo.get_max_id_number.return_value = 3

        result = await use_case.execute(1, "AUTH-001")

        assert result.component == "CORE"

    async def test_duplicate_preserves_story_points(self, use_case, mock_story_repo):
        """Should keep the same story points as the original."""
        original = _make_story(story_points=StoryPoint.LARGE)
        mock_story_repo.get_by_id.return_value = original

        result = await use_case.execute(1, "AUTH-001")

        assert result.story_points == 8

    async def test_duplicate_preserves_feature_id(self, use_case, mock_story_repo):
        """Should keep the same feature_id as the original."""
        original = _make_story(feature_id=42)
        mock_story_repo.get_by_id.return_value = original

        result = await use_case.execute(1, "AUTH-001")

        assert result.feature_id == 42

    async def test_persists_duplicate(self, use_case, mock_story_repo):
        """Should call repository add with the duplicate story."""
        original = _make_story()
        mock_story_repo.get_by_id.return_value = original

        await use_case.execute(1, "AUTH-001")

        mock_story_repo.add.assert_called_once()
        added = mock_story_repo.add.call_args[0][0]
        assert added.id != original.id
        assert "(copia)" in added.name

    async def test_returns_story_output_dto(self, use_case, mock_story_repo):
        """Should return StoryOutputDTO with duplicate data."""
        original = _make_story()
        mock_story_repo.get_by_id.return_value = original

        result = await use_case.execute(1, "AUTH-001")

        assert hasattr(result, "id")
        assert hasattr(result, "component")
        assert hasattr(result, "name")
        assert hasattr(result, "story_points")
        assert hasattr(result, "priority")
        assert hasattr(result, "status")

    async def test_does_not_persist_when_not_found(self, use_case, mock_story_repo):
        """Should not call add when original story not found."""
        mock_story_repo.get_by_id.return_value = None

        with pytest.raises(ValueError):
            await use_case.execute(1, "AUTH-999")

        mock_story_repo.add.assert_not_called()
