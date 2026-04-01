"""Unit tests for CalculateScheduleUseCase."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from backlog_manager.application.dto.scheduling.calculate_schedule_dto import (
    CalculateScheduleInputDTO,
)
from backlog_manager.application.use_cases.scheduling.calculate_schedule import (
    CalculateScheduleUseCase,
)
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


def _make_story(
    story_id: str = "TEST-001",
    *,
    priority: int = 1,
    sp: int = 5,
    status: StoryStatus = StoryStatus.BACKLOG,
    start_date: date | None = None,
    end_date: date | None = None,
) -> Story:
    return Story(
        id=story_id,
        component=story_id.rsplit("-", 1)[0],
        name=f"Story {story_id}",
        story_points=StoryPoint(sp),
        priority=priority,
        status=status,
        start_date=start_date,
        end_date=end_date,
    )


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.stories = MagicMock()
    uow.dependencies = MagicMock()
    uow.stories.get_all = AsyncMock(return_value=[])
    uow.stories.get_by_id = AsyncMock(return_value=None)
    uow.stories.update = AsyncMock()
    uow.dependencies.get_all_dependencies = AsyncMock(return_value=[])
    return uow


def _make_input(**kwargs) -> CalculateScheduleInputDTO:
    defaults = {
        "velocity": 2.0,
        "start_date": date(2026, 4, 1),
        "recalculate_all": False,
    }
    defaults.update(kwargs)
    return CalculateScheduleInputDTO(**defaults)


@pytest.mark.unit
class TestFilterEligibleStories:
    """Tests for _filter_eligible_stories edge cases."""

    @pytest.mark.asyncio
    async def test_story_with_invalid_sp_is_skipped(self, mock_uow):
        """Story with invalid story_points should be filtered out with warning."""
        story = _make_story("A-001", sp=5)
        # Set SP to an invalid value (not in {3, 5, 8, 13})
        # Use raw int to bypass StoryPoint enum validation
        object.__setattr__(story, "story_points", 1)
        mock_uow.stories.get_all.return_value = [story]

        use_case = CalculateScheduleUseCase(mock_uow)
        result = await use_case.execute(_make_input())

        assert any("story_points invalido" in w for w in result.warnings)
        assert result.stories_updated == 0

    @pytest.mark.asyncio
    async def test_story_with_dates_skipped_when_not_recalculate_all(self, mock_uow):
        """Story that already has dates should be skipped when recalculate_all=False."""
        story = _make_story(
            "A-001",
            start_date=date(2026, 4, 1),
            end_date=date(2026, 4, 3),
        )
        mock_uow.stories.get_all.return_value = [story]

        use_case = CalculateScheduleUseCase(mock_uow)
        result = await use_case.execute(_make_input(recalculate_all=False))

        # Story should be skipped (already has dates)
        assert result.stories_updated == 0
        assert result.stories_processed == 0


@pytest.mark.unit
class TestResolveDependencyEndDates:
    """Tests for _resolve_dependency_end_dates edge cases."""

    @pytest.mark.asyncio
    async def test_dependency_from_db_without_end_date_uses_fallback(self, mock_uow):
        """Dependency found in DB but without end_date should use fallback."""
        story_a = _make_story("A-001")
        story_b = _make_story("B-001")  # dependency, no end_date

        mock_uow.stories.get_all.return_value = [story_a]
        mock_uow.stories.get_by_id.return_value = story_b
        mock_uow.dependencies.get_all_dependencies.return_value = [("A-001", "B-001")]

        use_case = CalculateScheduleUseCase(mock_uow)
        result = await use_case.execute(_make_input())

        # Should have processed and generated a fallback warning
        assert any("sem data" in w for w in result.warnings)

    @pytest.mark.asyncio
    async def test_dependency_from_db_with_end_date(self, mock_uow):
        """Dependency found in DB with end_date should use that date."""
        story_a = _make_story("A-001")
        story_b = _make_story(
            "B-001",
            start_date=date(2026, 3, 25),
            end_date=date(2026, 3, 28),
        )

        mock_uow.stories.get_all.return_value = [story_a]
        mock_uow.stories.get_by_id.return_value = story_b
        mock_uow.dependencies.get_all_dependencies.return_value = [("A-001", "B-001")]

        use_case = CalculateScheduleUseCase(mock_uow)
        result = await use_case.execute(_make_input())

        assert result.stories_updated == 1
        # No fallback warning because B-001 has an end_date
        assert not any("sem data" in w for w in result.warnings)
