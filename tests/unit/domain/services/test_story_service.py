"""Unit tests for StoryService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backlog_manager.domain.entities import Story
from backlog_manager.domain.services.story_service import StoryService
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_max_id_number = AsyncMock(return_value=0)
    repo.get_max_priority = AsyncMock(return_value=0)
    repo.get_by_priority = AsyncMock(return_value=None)
    return repo


@pytest.fixture
def story_service(mock_story_repo):
    """Create story service with mock repository."""
    return StoryService(mock_story_repo)


class TestGenerateStoryId:
    """Tests for generate_story_id method."""

    async def test_generates_first_id_for_new_component(
        self, story_service, mock_story_repo
    ):
        """Should generate 001 for component with no stories."""
        mock_story_repo.get_max_id_number.return_value = 0

        result = await story_service.generate_story_id("AUTH")

        assert result == "AUTH-001"
        mock_story_repo.get_max_id_number.assert_called_once_with("AUTH")

    async def test_increments_existing_number(self, story_service, mock_story_repo):
        """Should increment from max existing number."""
        mock_story_repo.get_max_id_number.return_value = 5

        result = await story_service.generate_story_id("CORE")

        assert result == "CORE-006"

    async def test_converts_component_to_uppercase(
        self, story_service, mock_story_repo
    ):
        """Should uppercase component in generated ID."""
        mock_story_repo.get_max_id_number.return_value = 0

        result = await story_service.generate_story_id("auth")

        assert result == "AUTH-001"

    async def test_pads_number_with_zeros(self, story_service, mock_story_repo):
        """Should pad number to 3 digits."""
        mock_story_repo.get_max_id_number.return_value = 99

        result = await story_service.generate_story_id("AUTH")

        assert result == "AUTH-100"


class TestGetNextPriority:
    """Tests for get_next_priority method."""

    async def test_returns_one_for_empty_backlog(self, story_service, mock_story_repo):
        """Should return 1 when backlog is empty."""
        mock_story_repo.get_max_priority.return_value = 0

        result = await story_service.get_next_priority()

        assert result == 1

    async def test_increments_max_priority(self, story_service, mock_story_repo):
        """Should return max + 1."""
        mock_story_repo.get_max_priority.return_value = 10

        result = await story_service.get_next_priority()

        assert result == 11


class TestCreateStory:
    """Tests for create_story method."""

    async def test_creates_story_with_generated_id(
        self, story_service, mock_story_repo
    ):
        """Should create story with auto-generated ID."""
        mock_story_repo.get_max_id_number.return_value = 5
        mock_story_repo.get_max_priority.return_value = 3

        story = await story_service.create_story(
            component="AUTH",
            name="Implement login",
            story_points=5,
        )

        assert story.id == "AUTH-006"
        assert story.name == "Implement login"
        assert int(story.story_points) == 5
        assert story.priority == 4
        assert story.status == StoryStatus.BACKLOG

    async def test_creates_story_with_feature_id(self, story_service, mock_story_repo):
        """Should create story with optional feature ID."""
        mock_story_repo.get_max_id_number.return_value = 0
        mock_story_repo.get_max_priority.return_value = 0

        story = await story_service.create_story(
            component="CORE",
            name="Test story",
            story_points=3,
            feature_id=42,
        )

        assert story.feature_id == 42


class TestSwapPriorities:
    """Tests for swap_priorities method."""

    async def test_swaps_priorities_between_stories(self, story_service):
        """Should swap priority values."""
        story1 = Story(
            id="AUTH-001",
            component="AUTH",
            name="Story 1",
            story_points=StoryPoint.SMALL,
            priority=1,
        )
        story2 = Story(
            id="AUTH-002",
            component="AUTH",
            name="Story 2",
            story_points=StoryPoint.MEDIUM,
            priority=5,
        )

        await story_service.swap_priorities(story1, story2)

        assert story1.priority == 5
        assert story2.priority == 1


class TestValidateCanMoveUp:
    """Tests for validate_can_move_up method."""

    async def test_returns_false_at_top(self, story_service, mock_story_repo):
        """Should return False when already at top (priority 0)."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Story",
            story_points=StoryPoint.SMALL,
            priority=0,
        )

        result = await story_service.validate_can_move_up(story)

        assert result is False

    async def test_returns_true_when_previous_exists(
        self, story_service, mock_story_repo
    ):
        """Should return True when story with previous priority exists."""
        story = Story(
            id="AUTH-002",
            component="AUTH",
            name="Story",
            story_points=StoryPoint.SMALL,
            priority=2,
        )
        mock_story_repo.get_by_priority.return_value = Story(
            id="AUTH-001",
            component="AUTH",
            name="Previous",
            story_points=StoryPoint.SMALL,
            priority=1,
        )

        result = await story_service.validate_can_move_up(story)

        assert result is True
        mock_story_repo.get_by_priority.assert_called_once_with(1)


class TestValidateCanMoveDown:
    """Tests for validate_can_move_down method."""

    async def test_returns_false_at_bottom(self, story_service, mock_story_repo):
        """Should return False when no story below."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Story",
            story_points=StoryPoint.SMALL,
            priority=5,
        )
        mock_story_repo.get_by_priority.return_value = None

        result = await story_service.validate_can_move_down(story)

        assert result is False

    async def test_returns_true_when_next_exists(self, story_service, mock_story_repo):
        """Should return True when story with next priority exists."""
        story = Story(
            id="AUTH-001",
            component="AUTH",
            name="Story",
            story_points=StoryPoint.SMALL,
            priority=2,
        )
        mock_story_repo.get_by_priority.return_value = Story(
            id="AUTH-002",
            component="AUTH",
            name="Next",
            story_points=StoryPoint.SMALL,
            priority=3,
        )

        result = await story_service.validate_can_move_down(story)

        assert result is True


class TestDuplicateStory:
    """Tests for duplicate_story method."""

    async def test_creates_copy_with_new_id(self, story_service, mock_story_repo):
        """Should create copy with new auto-generated ID."""
        mock_story_repo.get_max_id_number.return_value = 10
        mock_story_repo.get_max_priority.return_value = 5

        original = Story(
            id="AUTH-001",
            component="AUTH",
            name="Original Story",
            story_points=StoryPoint.MEDIUM,
            priority=1,
            feature_id=42,
        )

        duplicate = await story_service.duplicate_story(original)

        assert duplicate.id == "AUTH-011"
        assert duplicate.name == "Original Story (copia)"
        assert int(duplicate.story_points) == int(original.story_points)
        assert duplicate.priority == 6
        assert duplicate.status == StoryStatus.BACKLOG
        assert duplicate.feature_id == 42
