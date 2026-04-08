"""Unit tests for ResetPlanningUseCase."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.dto.planning.reset_planning_dto import (
    ResetPlanningInputDTO,
)
from backlog_manager.application.use_cases.planning.reset_planning import (
    ResetPlanningUseCase,
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
    status: StoryStatus = StoryStatus.BACKLOG,
    priority: int = 1,
    feature_id: int | None = None,
) -> Story:
    """Helper to create a Story with optional calculated fields."""
    return Story(
        planning_id=1,
        id=story_id,
        component=story_id.split("-")[0],
        name=f"Historia {story_id}",
        story_points=StoryPoint(5),
        priority=priority,
        status=status,
        duration=duration,
        start_date=start_date,
        end_date=end_date,
        developer_id=developer_id,
        feature_id=feature_id,
    )


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
    repo.update = AsyncMock()
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
    return ResetPlanningUseCase(mock_uow)


class TestResetPlanningUseCase:
    """Tests for ResetPlanningUseCase."""

    async def test_reset_planning_clears_calculated_fields(
        self, use_case, mock_story_repo
    ):
        """T005: Should clear duration, start_date, end_date, developer_id."""
        story = _make_story(
            "TEST-001",
            duration=5,
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 9),
            developer_id=1,
        )
        mock_story_repo.get_all.return_value = [story]

        result = await use_case.execute(ResetPlanningInputDTO(planning_id=1))

        assert result.success is True
        assert result.stories_reset == 1
        assert story.duration is None
        assert story.start_date is None
        assert story.end_date is None
        assert story.developer_id is None
        mock_story_repo.update.assert_awaited_once_with(story)

    async def test_reset_planning_preserves_user_data(self, use_case, mock_story_repo):
        """T006: Should preserve id, component, name, story_points, priority, feature_id."""
        story = _make_story(
            "AUTH-001",
            duration=5,
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 9),
            developer_id=1,
            feature_id=42,
        )
        mock_story_repo.get_all.return_value = [story]

        await use_case.execute(ResetPlanningInputDTO(planning_id=1))

        assert story.id == "AUTH-001"
        assert story.component == "AUTH"
        assert story.name == "Historia AUTH-001"
        assert story.story_points == StoryPoint(5)
        assert story.priority == 1
        assert story.feature_id == 42

    async def test_reset_planning_preserves_dependencies(
        self, use_case, mock_story_repo
    ):
        """T007: Dependencies are structural data and should not be affected."""
        story = _make_story(
            "TEST-001",
            duration=5,
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 9),
            developer_id=1,
        )
        mock_story_repo.get_all.return_value = [story]

        result = await use_case.execute(ResetPlanningInputDTO(planning_id=1))

        # Dependencies are stored separately in Story_Dependency table,
        # not on the Story entity. The use case only clears story fields.
        assert result.success is True
        assert result.stories_reset == 1

    async def test_reset_planning_preserves_status(self, use_case, mock_story_repo):
        """T008: Should preserve status field (e.g. EXECUCAO stays EXECUCAO)."""
        story = _make_story(
            "TEST-001",
            duration=5,
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 9),
            developer_id=1,
            status=StoryStatus.EXECUCAO,
        )
        mock_story_repo.get_all.return_value = [story]

        await use_case.execute(ResetPlanningInputDTO(planning_id=1))

        assert story.status == StoryStatus.EXECUCAO

    async def test_reset_planning_atomic_on_failure(self, use_case, mock_story_repo):
        """T009: Should raise exception if update fails (UoW handles rollback)."""
        stories = [
            _make_story("TEST-001", duration=5, developer_id=1),
            _make_story("TEST-002", duration=3, developer_id=2, priority=2),
        ]
        mock_story_repo.get_all.return_value = stories
        mock_story_repo.update.side_effect = [None, RuntimeError("DB error")]

        with pytest.raises(RuntimeError, match="DB error"):
            await use_case.execute(ResetPlanningInputDTO(planning_id=1))

    async def test_reset_planning_empty_backlog(self, use_case, mock_story_repo):
        """T010: Should succeed with 0 stories reset when backlog is empty."""
        mock_story_repo.get_all.return_value = []

        result = await use_case.execute(ResetPlanningInputDTO(planning_id=1))

        assert result.success is True
        assert result.stories_reset == 0
        assert result.stories_with_dates_cleared == 0
        assert result.stories_with_developer_cleared == 0
        mock_story_repo.update.assert_not_awaited()

    async def test_reset_planning_no_planning_data(self, use_case, mock_story_repo):
        """T011: Should succeed with 0 reset when no story has calculated fields."""
        stories = [
            _make_story("TEST-001"),
            _make_story("TEST-002", priority=2),
        ]
        mock_story_repo.get_all.return_value = stories

        result = await use_case.execute(ResetPlanningInputDTO(planning_id=1))

        assert result.success is True
        assert result.stories_reset == 0
        mock_story_repo.update.assert_not_awaited()

    async def test_reset_planning_partial_data(self, use_case, mock_story_repo):
        """T012: Should handle stories with only developer_id or only dates."""
        story_dev_only = _make_story("TEST-001", developer_id=3)
        story_dates_only = _make_story(
            "TEST-002",
            duration=5,
            start_date=date(2026, 1, 5),
            end_date=date(2026, 1, 9),
            priority=2,
        )
        mock_story_repo.get_all.return_value = [story_dev_only, story_dates_only]

        result = await use_case.execute(ResetPlanningInputDTO(planning_id=1))

        assert result.success is True
        assert result.stories_reset == 2
        assert result.stories_with_dates_cleared == 1
        assert result.stories_with_developer_cleared == 1

        assert story_dev_only.developer_id is None
        assert story_dates_only.duration is None
        assert story_dates_only.start_date is None
        assert story_dates_only.end_date is None
