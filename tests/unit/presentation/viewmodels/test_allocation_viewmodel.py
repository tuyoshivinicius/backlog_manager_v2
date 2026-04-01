"""Headless tests for AllocationViewModel."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.allocation_viewmodel import (
        AllocationViewModel,
    )

from backlog_manager.application.dto.allocation import (  # noqa: E402
    AllocationMetricsDTO,
    ExecuteAllocationOutputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException  # noqa: E402

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def mock_container():
    """Create a mock DIContainer with UoW context manager."""
    container = MagicMock()
    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    container.create_unit_of_work.return_value = mock_uow
    return container


@pytest.fixture
def viewmodel(mock_container):
    """Create an AllocationViewModel with mock container."""
    return AllocationViewModel(mock_container)


def _make_success_result(
    stories: int = 10,
    waves: int = 2,
    deadlocks: int = 0,
    warnings: list[str] | None = None,
) -> tuple[MagicMock, ExecuteAllocationOutputDTO]:
    """Build a mock use-case that returns a successful allocation result."""
    mock_metrics = AllocationMetricsDTO(
        stories_processed=stories,
        stories_allocated=stories,
        waves_processed=waves,
        deadlocks_detected=deadlocks,
    )
    mock_result = ExecuteAllocationOutputDTO(
        success=True,
        stories_allocated=stories,
        total_time_seconds=1.5,
        metrics=mock_metrics,
        warnings=warnings or [],
    )
    mock_uc = AsyncMock()
    mock_uc.execute.return_value = mock_result
    return mock_uc, mock_result


# ---------------------------------------------------------------------------
# Tests — Initialization
# ---------------------------------------------------------------------------


class TestAllocationViewModelInitialization:
    """Tests for AllocationViewModel initialization."""

    def test_initial_state(self, viewmodel) -> None:
        """Test that ViewModel initializes with correct state."""
        assert viewmodel.is_running is False
        assert viewmodel.last_metrics is None
        assert viewmodel.last_warnings == []

    def test_has_required_signals(self, viewmodel) -> None:
        """Test that ViewModel has required signals."""
        assert hasattr(viewmodel, "allocation_started")
        assert hasattr(viewmodel, "allocation_completed")
        assert hasattr(viewmodel, "allocation_error")
        assert hasattr(viewmodel, "warnings_updated")


# ---------------------------------------------------------------------------
# Tests — Properties
# ---------------------------------------------------------------------------


class TestAllocationViewModelProperties:
    """Tests for AllocationViewModel properties."""

    def test_is_running_property(self, viewmodel) -> None:
        """Test is_running property."""
        assert viewmodel.is_running is False
        viewmodel._is_running = True
        assert viewmodel.is_running is True

    def test_last_warnings_returns_copy(self, viewmodel) -> None:
        """Test that last_warnings property returns a copy."""
        viewmodel._last_warnings = ["Warning 1", "Warning 2"]
        warnings1 = viewmodel.last_warnings
        warnings2 = viewmodel.last_warnings
        assert warnings1 is not warnings2
        assert warnings1 == warnings2

    def test_can_execute_when_not_running(self, viewmodel) -> None:
        """Test can_execute returns True when not running."""
        assert viewmodel.can_execute() is True

    def test_can_execute_when_running(self, viewmodel) -> None:
        """Test can_execute returns False when running."""
        viewmodel._is_running = True
        assert viewmodel.can_execute() is False


# ---------------------------------------------------------------------------
# Tests — Execution
# ---------------------------------------------------------------------------


class TestAllocationViewModelExecution:
    """Tests for allocation execution."""

    @pytest.mark.asyncio
    async def test_execute_returns_none_if_already_running(self, viewmodel) -> None:
        """Test that execute returns None if allocation is already running."""
        viewmodel._is_running = True
        result = await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))
        assert result is None

    @pytest.mark.asyncio
    async def test_execute_emits_started_signal(
        self, viewmodel, mock_container
    ) -> None:
        """Test that execute emits allocation_started signal."""
        mock_uc, _ = _make_success_result()
        mock_container.create_execute_allocation_use_case.return_value = mock_uc

        await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert len(viewmodel.allocation_started.emissions) == 1

    @pytest.mark.asyncio
    async def test_execute_success_emits_completed_signal(
        self, viewmodel, mock_container
    ) -> None:
        """Test successful execution emits allocation_completed signal."""
        mock_uc, _ = _make_success_result()
        mock_container.create_execute_allocation_use_case.return_value = mock_uc

        result = await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert result is not None
        assert result.stories_allocated == 10
        assert len(viewmodel.allocation_completed.emissions) == 1
        emitted_metrics = viewmodel.allocation_completed.emissions[0][0]
        assert emitted_metrics.stories_processed == 10

    @pytest.mark.asyncio
    async def test_execute_success_updates_state(
        self, viewmodel, mock_container
    ) -> None:
        """Test successful execution updates internal state."""
        mock_uc, _ = _make_success_result(deadlocks=1, warnings=["Deadlock na onda 1"])
        mock_container.create_execute_allocation_use_case.return_value = mock_uc

        await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert viewmodel.last_metrics is not None
        assert viewmodel.last_metrics.stories_processed == 10
        assert len(viewmodel.last_warnings) == 1
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_execute_emits_warnings_updated_signal(
        self, viewmodel, mock_container
    ) -> None:
        """Test that execute emits warnings_updated signal."""
        mock_uc, _ = _make_success_result(
            stories=8, deadlocks=1, warnings=["Deadlock detectado"]
        )
        mock_container.create_execute_allocation_use_case.return_value = mock_uc

        await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert len(viewmodel.warnings_updated.emissions) == 1
        emitted_warnings = viewmodel.warnings_updated.emissions[0][0]
        assert len(emitted_warnings) == 1

    @pytest.mark.asyncio
    async def test_execute_backlog_manager_exception_emits_error(
        self, viewmodel, mock_container
    ) -> None:
        """Test that BacklogManagerException emits error signal."""
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = BacklogManagerException(
            "Nenhum desenvolvedor disponivel"
        )
        mock_container.create_execute_allocation_use_case.return_value = mock_uc

        result = await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert result is None
        assert len(viewmodel.allocation_error.emissions) == 1
        assert "desenvolvedor" in viewmodel.allocation_error.emissions[0][0]
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_execute_unexpected_exception_emits_error(
        self, viewmodel, mock_container
    ) -> None:
        """Test that unexpected exceptions emit error signal."""
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = RuntimeError("Unexpected error")
        mock_container.create_execute_allocation_use_case.return_value = mock_uc

        result = await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert result is None
        assert len(viewmodel.allocation_error.emissions) == 1
        assert "Erro inesperado" in viewmodel.allocation_error.emissions[0][0]
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_execute_resets_running_state_after_exception(
        self, viewmodel, mock_container
    ) -> None:
        """Test that is_running is reset even after exception."""
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = Exception("Test error")
        mock_container.create_execute_allocation_use_case.return_value = mock_uc

        await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert viewmodel.is_running is False


# ---------------------------------------------------------------------------
# Tests — Clear Results
# ---------------------------------------------------------------------------


class TestAllocationViewModelClearResults:
    """Tests for clearing allocation results."""

    def test_clear_results_clears_metrics(self, viewmodel) -> None:
        """Test that clear_results clears the metrics."""
        viewmodel._last_metrics = AllocationMetricsDTO(
            stories_processed=10,
            stories_allocated=10,
            waves_processed=2,
            deadlocks_detected=0,
        )
        viewmodel.clear_results()
        assert viewmodel.last_metrics is None

    def test_clear_results_clears_warnings(self, viewmodel) -> None:
        """Test that clear_results clears the warnings."""
        viewmodel._last_warnings = ["Warning 1", "Warning 2"]
        viewmodel.clear_results()
        assert viewmodel.last_warnings == []

    def test_clear_results_emits_warnings_updated(self, viewmodel) -> None:
        """Test that clear_results emits warnings_updated signal."""
        viewmodel._last_warnings = ["Warning 1"]
        viewmodel.clear_results()

        assert len(viewmodel.warnings_updated.emissions) >= 1
        last_emission = viewmodel.warnings_updated.emissions[-1][0]
        assert last_emission == []
