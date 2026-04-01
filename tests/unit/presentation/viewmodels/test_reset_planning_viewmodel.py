"""Headless tests for ResetPlanningViewModel."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.reset_planning_viewmodel import (
        ResetPlanningViewModel,
    )

from backlog_manager.application.dto.planning.reset_planning_dto import (  # noqa: E402
    CountAffectedStoriesOutputDTO,
    ResetPlanningOutputDTO,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


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


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestResetPlanningViewModel:
    """Tests for ResetPlanningViewModel."""

    @pytest.mark.asyncio
    async def test_reset_planning_viewmodel_signals(self, viewmodel):
        """T019: Should emit reset_started and reset_completed signals."""
        result = await viewmodel.execute()

        assert len(viewmodel.reset_started.emissions) == 1
        assert len(viewmodel.reset_completed.emissions) == 1
        assert result is not None
        assert result.success is True
        assert result.stories_reset == 5

    @pytest.mark.asyncio
    async def test_reset_planning_viewmodel_error_signal(
        self, viewmodel, mock_container
    ):
        """T020: Should emit reset_error on failure."""
        mock_uc = mock_container.create_reset_planning_use_case.return_value
        mock_uc.execute.side_effect = RuntimeError("DB connection lost")

        result = await viewmodel.execute()

        assert result is None
        assert len(viewmodel.reset_error.emissions) == 1
        assert "DB connection lost" in viewmodel.reset_error.emissions[0][0]

    @pytest.mark.asyncio
    async def test_status_bar_updated_after_reset(self, viewmodel):
        """T021: Should emit reset_completed with output DTO for status bar update."""
        await viewmodel.execute()

        assert len(viewmodel.reset_completed.emissions) == 1
        emitted_result = viewmodel.reset_completed.emissions[0][0]
        assert emitted_result.stories_reset == 5
        assert emitted_result.stories_with_dates_cleared == 5
        assert emitted_result.stories_with_developer_cleared == 3

    @pytest.mark.asyncio
    async def test_preview_returns_counts(self, viewmodel):
        """Should return count DTO from preview method."""
        result = await viewmodel.preview()

        assert result is not None
        assert result.total == 5
        assert result.with_dates == 5
        assert result.with_developer == 3

    @pytest.mark.asyncio
    async def test_is_running_prevents_concurrent_execution(self, viewmodel):
        """Should return None if already running."""
        viewmodel._is_running = True
        result = await viewmodel.execute()
        assert result is None

    @pytest.mark.asyncio
    async def test_is_running_reset_after_success(self, viewmodel):
        """Should reset is_running after successful execution."""
        await viewmodel.execute()
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_is_running_reset_after_error(self, viewmodel, mock_container):
        """Should reset is_running after error."""
        mock_uc = mock_container.create_reset_planning_use_case.return_value
        mock_uc.execute.side_effect = RuntimeError("fail")

        await viewmodel.execute()
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_preview_returns_none_on_error(self, viewmodel, mock_container):
        """Should return None when preview fails."""
        mock_uc = mock_container.create_count_affected_stories_use_case.return_value
        mock_uc.execute.side_effect = RuntimeError("DB error")

        result = await viewmodel.preview()
        assert result is None
