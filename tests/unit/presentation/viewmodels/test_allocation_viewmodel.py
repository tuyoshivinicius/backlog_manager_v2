"""Tests for AllocationViewModel.

This module contains unit tests for the AllocationViewModel class,
verifying allocation execution, signal emissions, and state management.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from backlog_manager.application.dto.allocation import (
    AllocationMetricsDTO,
    ExecuteAllocationOutputDTO,
)
from backlog_manager.domain.exceptions import BacklogManagerException
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.viewmodels.allocation_viewmodel import (
    AllocationViewModel,
)


class TestAllocationViewModelInitialization:
    """Tests for AllocationViewModel initialization."""

    def test_initial_state(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that ViewModel initializes with correct state."""
        viewmodel = AllocationViewModel(container)

        assert viewmodel.is_running is False
        assert viewmodel.last_metrics is None
        assert viewmodel.last_warnings == []

    def test_has_required_signals(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that ViewModel has required signals."""
        viewmodel = AllocationViewModel(container)

        assert hasattr(viewmodel, "allocation_started")
        assert hasattr(viewmodel, "allocation_completed")
        assert hasattr(viewmodel, "allocation_error")
        assert hasattr(viewmodel, "warnings_updated")


class TestAllocationViewModelProperties:
    """Tests for AllocationViewModel properties."""

    def test_is_running_property(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test is_running property."""
        viewmodel = AllocationViewModel(container)

        assert viewmodel.is_running is False

        # Set internal state
        viewmodel._is_running = True
        assert viewmodel.is_running is True

    def test_last_warnings_returns_copy(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that last_warnings property returns a copy."""
        viewmodel = AllocationViewModel(container)
        viewmodel._last_warnings = ["Warning 1", "Warning 2"]

        warnings1 = viewmodel.last_warnings
        warnings2 = viewmodel.last_warnings

        assert warnings1 is not warnings2
        assert warnings1 == warnings2

    def test_can_execute_when_not_running(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test can_execute returns True when not running."""
        viewmodel = AllocationViewModel(container)

        assert viewmodel.can_execute() is True

    def test_can_execute_when_running(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test can_execute returns False when running."""
        viewmodel = AllocationViewModel(container)
        viewmodel._is_running = True

        assert viewmodel.can_execute() is False


class TestAllocationViewModelExecution:
    """Tests for allocation execution."""

    @pytest.mark.asyncio
    async def test_execute_returns_none_if_already_running(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that execute returns None if allocation is already running."""
        viewmodel = AllocationViewModel(container)
        viewmodel._is_running = True

        result = await viewmodel.execute(
            velocity=2.0,
            start_date=date(2026, 1, 1),
        )

        assert result is None

    @pytest.mark.asyncio
    async def test_execute_emits_started_signal(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that execute emits allocation_started signal."""
        viewmodel = AllocationViewModel(container)

        started_emitted = []

        def on_started() -> None:
            started_emitted.append(True)

        viewmodel.allocation_started.connect(on_started)

        # Mock the execute allocation use case
        mock_metrics = AllocationMetricsDTO(
            stories_processed=10,
            stories_allocated=10,
            waves_processed=2,
            deadlocks_detected=0,
        )
        mock_result = ExecuteAllocationOutputDTO(
            success=True,
            stories_allocated=10,
            total_time_seconds=1.5,
            metrics=mock_metrics,
            warnings=[],
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container,
            "create_execute_allocation_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert len(started_emitted) == 1

    @pytest.mark.asyncio
    async def test_execute_success_emits_completed_signal(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful execution emits allocation_completed signal."""
        viewmodel = AllocationViewModel(container)

        completed_metrics = []

        def on_completed(metrics: AllocationMetricsDTO) -> None:
            completed_metrics.append(metrics)

        viewmodel.allocation_completed.connect(on_completed)

        # Mock the execute allocation use case
        mock_metrics = AllocationMetricsDTO(
            stories_processed=10,
            stories_allocated=10,
            waves_processed=2,
            deadlocks_detected=0,
        )
        mock_result = ExecuteAllocationOutputDTO(
            success=True,
            stories_allocated=10,
            total_time_seconds=1.5,
            metrics=mock_metrics,
            warnings=[],
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container,
            "create_execute_allocation_use_case",
            return_value=mock_use_case,
        ):
            result = await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert result is not None
        assert result.stories_allocated == 10
        assert len(completed_metrics) == 1
        assert completed_metrics[0].stories_processed == 10

    @pytest.mark.asyncio
    async def test_execute_success_updates_state(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful execution updates internal state."""
        viewmodel = AllocationViewModel(container)

        # Mock the execute allocation use case
        mock_metrics = AllocationMetricsDTO(
            stories_processed=10,
            stories_allocated=10,
            waves_processed=2,
            deadlocks_detected=1,
        )
        mock_result = ExecuteAllocationOutputDTO(
            success=True,
            stories_allocated=10,
            total_time_seconds=1.5,
            metrics=mock_metrics,
            warnings=["Deadlock na onda 1"],
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container,
            "create_execute_allocation_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert viewmodel.last_metrics is not None
        assert viewmodel.last_metrics.stories_processed == 10
        assert len(viewmodel.last_warnings) == 1
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_execute_emits_warnings_updated_signal(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that execute emits warnings_updated signal."""
        viewmodel = AllocationViewModel(container)

        warnings_received = []

        def on_warnings(warnings: list) -> None:
            warnings_received.extend(warnings)

        viewmodel.warnings_updated.connect(on_warnings)

        # Mock the execute allocation use case with warnings
        mock_metrics = AllocationMetricsDTO(
            stories_processed=10,
            stories_allocated=8,
            waves_processed=2,
            deadlocks_detected=1,
        )
        mock_result = ExecuteAllocationOutputDTO(
            success=True,
            stories_allocated=8,
            total_time_seconds=1.5,
            metrics=mock_metrics,
            warnings=["Deadlock detectado"],
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container,
            "create_execute_allocation_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert len(warnings_received) == 1

    @pytest.mark.asyncio
    async def test_execute_backlog_manager_exception_emits_error(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that BacklogManagerException emits error signal."""
        viewmodel = AllocationViewModel(container)

        errors_received = []

        def on_error(message: str) -> None:
            errors_received.append(message)

        viewmodel.allocation_error.connect(on_error)

        # Mock to raise BacklogManagerException
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = BacklogManagerException(
            "Nenhum desenvolvedor disponivel"
        )

        with patch.object(
            container,
            "create_execute_allocation_use_case",
            return_value=mock_use_case,
        ):
            result = await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert result is None
        assert len(errors_received) == 1
        assert "desenvolvedor" in errors_received[0]
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_execute_unexpected_exception_emits_error(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that unexpected exceptions emit error signal."""
        viewmodel = AllocationViewModel(container)

        errors_received = []

        def on_error(message: str) -> None:
            errors_received.append(message)

        viewmodel.allocation_error.connect(on_error)

        # Mock to raise generic exception
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = RuntimeError("Unexpected error")

        with patch.object(
            container,
            "create_execute_allocation_use_case",
            return_value=mock_use_case,
        ):
            result = await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        assert result is None
        assert len(errors_received) == 1
        assert "Erro inesperado" in errors_received[0]
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_execute_resets_running_state_after_exception(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that is_running is reset even after exception."""
        viewmodel = AllocationViewModel(container)

        # Mock to raise exception
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = Exception("Test error")

        with patch.object(
            container,
            "create_execute_allocation_use_case",
            return_value=mock_use_case,
        ):
            await viewmodel.execute(velocity=2.0, start_date=date(2026, 1, 1))

        # Should be False even after error (reset in finally block)
        assert viewmodel.is_running is False


class TestAllocationViewModelClearResults:
    """Tests for clearing allocation results."""

    def test_clear_results_clears_metrics(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that clear_results clears the metrics."""
        viewmodel = AllocationViewModel(container)
        viewmodel._last_metrics = AllocationMetricsDTO(
            stories_processed=10,
            stories_allocated=10,
            waves_processed=2,
            deadlocks_detected=0,
        )

        viewmodel.clear_results()

        assert viewmodel.last_metrics is None

    def test_clear_results_clears_warnings(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that clear_results clears the warnings."""
        viewmodel = AllocationViewModel(container)
        viewmodel._last_warnings = ["Warning 1", "Warning 2"]

        viewmodel.clear_results()

        assert viewmodel.last_warnings == []

    def test_clear_results_emits_warnings_updated(
        self,
        container: DIContainer,
        qapp,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that clear_results emits warnings_updated signal."""
        viewmodel = AllocationViewModel(container)
        viewmodel._last_warnings = ["Warning 1"]

        warnings_received = []

        def on_warnings(warnings: list) -> None:
            warnings_received.append(warnings)

        viewmodel.warnings_updated.connect(on_warnings)

        viewmodel.clear_results()

        assert len(warnings_received) == 1
        assert warnings_received[0] == []
