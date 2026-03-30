"""Unit tests for CountAffectedStoriesUseCase."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.use_cases.planning.count_affected_stories import (
    CountAffectedStoriesUseCase,
)
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


def _make_story(
    story_id: str = "TEST-001",
    *,
    duration: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    developer_id: int | None = None,
    priority: int = 1,
) -> Story:
    """Helper to create a Story with optional calculated fields."""
    return Story(
        id=story_id,
        component=story_id.split("-")[0],
        name=f"Historia {story_id}",
        story_points=StoryPoint(5),
        priority=priority,
        status=StoryStatus.BACKLOG,
        duration=duration,
        start_date=start_date,
        end_date=end_date,
        developer_id=developer_id,
    )


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
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
    return CountAffectedStoriesUseCase(mock_uow)


class TestCountAffectedStoriesUseCase:
    """Tests for CountAffectedStoriesUseCase."""

    async def test_count_affected_stories(self, use_case, mock_story_repo):
        """T014: Should return correct total, with_dates, with_developer counts."""
        stories = [
            # Has both dates and developer
            _make_story(
                "TEST-001",
                duration=5,
                start_date=date(2026, 1, 5),
                end_date=date(2026, 1, 9),
                developer_id=1,
            ),
            # Has only developer
            _make_story("TEST-002", developer_id=2, priority=2),
            # Has only dates
            _make_story(
                "TEST-003",
                duration=3,
                start_date=date(2026, 1, 10),
                end_date=date(2026, 1, 12),
                priority=3,
            ),
            # No calculated fields
            _make_story("TEST-004", priority=4),
        ]
        mock_story_repo.get_all.return_value = stories

        result = await use_case.execute()

        assert result.total == 3
        assert result.with_dates == 2
        assert result.with_developer == 2

    async def test_count_empty_backlog(self, use_case, mock_story_repo):
        """Should return all zeros for empty backlog."""
        mock_story_repo.get_all.return_value = []

        result = await use_case.execute()

        assert result.total == 0
        assert result.with_dates == 0
        assert result.with_developer == 0

    async def test_count_no_planning_data(self, use_case, mock_story_repo):
        """Should return all zeros when no stories have planning data."""
        stories = [
            _make_story("TEST-001"),
            _make_story("TEST-002", priority=2),
        ]
        mock_story_repo.get_all.return_value = stories

        result = await use_case.execute()

        assert result.total == 0
        assert result.with_dates == 0
        assert result.with_developer == 0
