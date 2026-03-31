"""Unit tests for ResetPlanningViewModel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from backlog_manager.application.dto.planning.reset_planning_dto import (
    CountAffectedStoriesOutputDTO,
    ResetPlanningOutputDTO,
)
from backlog_manager.presentation.viewmodels.reset_planning_viewmodel import (
    ResetPlanningViewModel,
)


@pytest.fixture
def mock_container():
    """Create mock DIContainer."""
    container = MagicMock()

    # Mock UoW context manager
    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    container.create_unit_of_work.return_value = mock_uow

    # Mock use case factories
    mock_reset_uc = MagicMock()
    mock_reset_uc.execute = AsyncMock(
        return_value=ResetPlanningOutputDTO(
            success=True,
            stories_reset=5,
            stories_with_dates_cleared=5,
            stories_with_developer_cleared=3,
        )
    )
    container.create_reset_planning_use_case.return_value = mock_reset_uc

    mock_count_uc = MagicMock()
    mock_count_uc.execute = AsyncMock(
        return_value=CountAffectedStoriesOutputDTO(
            total=5,
            with_dates=5,
            with_developer=3,
        )
    )
    container.create_count_affected_stories_use_case.return_value = mock_count_uc

    return container


@pytest.fixture
def viewmodel(mock_container):
    """Create ResetPlanningViewModel with mocks."""
    return ResetPlanningViewModel(mock_container)


class TestResetPlanningViewModel:
    """Tests for ResetPlanningViewModel."""

    async def test_reset_planning_viewmodel_signals(self, viewmodel, qtbot):
        """T019: Should emit reset_started and reset_completed signals."""
        started_signals = []
        completed_signals = []

        viewmodel.reset_started.connect(lambda: started_signals.append(True))
        viewmodel.reset_completed.connect(lambda r: completed_signals.append(r))

        result = await viewmodel.execute()

        assert len(started_signals) == 1
        assert len(completed_signals) == 1
        assert result is not None
        assert result.success is True
        assert result.stories_reset == 5

    async def test_reset_planning_viewmodel_error_signal(
        self, viewmodel, mock_container, qtbot
    ):
        """T020: Should emit reset_error on failure."""
        error_signals = []
        viewmodel.reset_error.connect(lambda msg: error_signals.append(msg))

        # Make use case raise an exception
        mock_uc = mock_container.create_reset_planning_use_case.return_value
        mock_uc.execute.side_effect = RuntimeError("DB connection lost")

        result = await viewmodel.execute()

        assert result is None
        assert len(error_signals) == 1
        assert "DB connection lost" in error_signals[0]

    async def test_status_bar_updated_after_reset(self, viewmodel, qtbot):
        """T021: Should emit reset_completed with output DTO for status bar update."""
        completed_results = []
        viewmodel.reset_completed.connect(lambda r: completed_results.append(r))

        await viewmodel.execute()

        assert len(completed_results) == 1
        result = completed_results[0]
        assert result.stories_reset == 5
        assert result.stories_with_dates_cleared == 5
        assert result.stories_with_developer_cleared == 3

    async def test_preview_returns_counts(self, viewmodel):
        """Should return count DTO from preview method."""
        result = await viewmodel.preview()

        assert result is not None
        assert result.total == 5
        assert result.with_dates == 5
        assert result.with_developer == 3

    async def test_is_running_prevents_concurrent_execution(self, viewmodel):
        """Should return None if already running."""
        viewmodel._is_running = True
        result = await viewmodel.execute()
        assert result is None
