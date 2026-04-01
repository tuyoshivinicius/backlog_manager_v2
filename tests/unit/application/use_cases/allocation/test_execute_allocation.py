"""Unit tests for ExecuteAllocationUseCase."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from backlog_manager.application.dto.allocation.execute_allocation_dto import (
    ExecuteAllocationInputDTO,
)
from backlog_manager.application.use_cases.allocation.execute_allocation import (
    LARGE_BACKLOG_THRESHOLD,
    ExecuteAllocationUseCase,
)
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


def _make_story(story_id: str = "TEST-001", **kwargs) -> Story:
    defaults = {
        "id": story_id,
        "component": story_id.rsplit("-", 1)[0],
        "name": f"Story {story_id}",
        "story_points": StoryPoint(5),
        "priority": 1,
        "status": StoryStatus.BACKLOG,
    }
    defaults.update(kwargs)
    return Story(**defaults)


@dataclass
class FakeMetrics:
    """Minimal stand-in for AllocationMetrics."""

    total_time_seconds: float = 0.1
    stories_processed: int = 1
    stories_allocated: int = 1
    waves_processed: int = 1
    total_iterations: int = 1
    iterations_per_wave: dict = field(default_factory=lambda: {1: 1})
    allocations_by_dependency_owner: int = 0
    allocations_by_load_balancing: int = 1
    deadlocks_detected: int = 0
    date_adjustments: int = 0
    validation_reallocations: int = 0
    validation_dependency_fixes: int = 0
    validation_conflict_fixes: int = 0
    max_idle_violations_detected: int = 0
    max_idle_violations_fixed: int = 0
    failed_reallocations: int = 0


@dataclass
class FakeAllocationResult:
    """Minimal stand-in for AllocationResult."""

    allocated_stories: list = field(default_factory=list)
    metrics: FakeMetrics = field(default_factory=FakeMetrics)
    warnings: list = field(default_factory=list)


@pytest.fixture
def mock_uow():
    uow = MagicMock()
    uow.stories = MagicMock()
    uow.developers = MagicMock()
    uow.features = MagicMock()
    uow.dependencies = MagicMock()
    uow.stories.get_all = AsyncMock(return_value=[])
    uow.developers.get_all = AsyncMock(return_value=[])
    uow.features.get_all = AsyncMock(return_value=[])
    uow.dependencies.get_all_dependencies = AsyncMock(return_value=[])
    uow.stories.update = AsyncMock()
    return uow


def _make_input(**kwargs) -> ExecuteAllocationInputDTO:
    defaults = {
        "velocity": 2.0,
        "project_start_date": date(2026, 4, 1),
    }
    defaults.update(kwargs)
    return ExecuteAllocationInputDTO(**defaults)


@pytest.mark.unit
class TestExecuteAllocationUseCase:
    """Tests for ExecuteAllocationUseCase."""

    @pytest.mark.asyncio
    async def test_large_backlog_warning(self, mock_uow):
        """Should emit warning when backlog exceeds threshold."""
        stories = [
            _make_story(f"COMP-{i:03d}") for i in range(1, LARGE_BACKLOG_THRESHOLD + 2)
        ]
        mock_uow.stories.get_all.return_value = stories

        fake_result = FakeAllocationResult(allocated_stories=[], warnings=[])
        with patch(
            "backlog_manager.application.use_cases.allocation.execute_allocation.AllocationService.allocate_stories",
            return_value=fake_result,
        ):
            use_case = ExecuteAllocationUseCase(mock_uow)
            result = await use_case.execute(_make_input())

        assert any("Backlog muito grande" in w for w in result.warnings)
        assert any(str(LARGE_BACKLOG_THRESHOLD) in w for w in result.warnings)

    @pytest.mark.asyncio
    async def test_invalid_allocation_criteria_falls_back(self, mock_uow):
        """Should fall back to LOAD_BALANCING on invalid criteria string."""
        mock_uow.stories.get_all.return_value = [_make_story()]

        fake_result = FakeAllocationResult(allocated_stories=[], warnings=[])
        with patch(
            "backlog_manager.application.use_cases.allocation.execute_allocation.AllocationService.allocate_stories",
            return_value=fake_result,
        ) as mock_alloc:
            use_case = ExecuteAllocationUseCase(mock_uow)
            result = await use_case.execute(
                _make_input(allocation_criteria="INVALID_CRITERIA")
            )

        assert any("Criterio invalido" in w for w in result.warnings)
        assert any("LOAD_BALANCING" in w for w in result.warnings)
        # Verify LOAD_BALANCING was actually used
        call_kwargs = mock_alloc.call_args
        config = call_kwargs.kwargs.get("config") or call_kwargs[1].get("config")
        assert config.allocation_criteria.value == "load_balancing"

    @pytest.mark.asyncio
    async def test_allocated_stories_are_persisted(self, mock_uow):
        """Should call update for each allocated story."""
        story = _make_story("COMP-001")
        mock_uow.stories.get_all.return_value = [story]

        fake_result = FakeAllocationResult(
            allocated_stories=[story],
            warnings=[],
        )
        with patch(
            "backlog_manager.application.use_cases.allocation.execute_allocation.AllocationService.allocate_stories",
            return_value=fake_result,
        ):
            use_case = ExecuteAllocationUseCase(mock_uow)
            result = await use_case.execute(_make_input())

        mock_uow.stories.update.assert_called_once_with(story)
        assert result.success is True

    @pytest.mark.asyncio
    async def test_allocation_warnings_are_collected(self, mock_uow):
        """Should collect warnings emitted by AllocationService."""
        mock_uow.stories.get_all.return_value = [_make_story()]

        from backlog_manager.domain.exceptions.warnings import BacklogWarning

        fake_result = FakeAllocationResult(
            allocated_stories=[],
            warnings=[BacklogWarning("Dev sem historias disponiveis")],
        )
        with patch(
            "backlog_manager.application.use_cases.allocation.execute_allocation.AllocationService.allocate_stories",
            return_value=fake_result,
        ):
            use_case = ExecuteAllocationUseCase(mock_uow)
            result = await use_case.execute(_make_input())

        assert any("Dev sem historias" in w for w in result.warnings)

    @pytest.mark.asyncio
    async def test_deadlock_warning_logged(self, mock_uow):
        """Should log warning when deadlocks are detected."""
        mock_uow.stories.get_all.return_value = [_make_story()]

        fake_metrics = FakeMetrics(deadlocks_detected=2)
        fake_result = FakeAllocationResult(
            allocated_stories=[],
            metrics=fake_metrics,
            warnings=[],
        )
        with patch(
            "backlog_manager.application.use_cases.allocation.execute_allocation.AllocationService.allocate_stories",
            return_value=fake_result,
        ):
            use_case = ExecuteAllocationUseCase(mock_uow)
            result = await use_case.execute(_make_input())

        assert result.success is True
        # Deadlock count should be reflected in metrics
        assert result.metrics.deadlocks_detected == 2
