"""Headless tests for ScheduleViewModel."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.schedule_viewmodel import (
        ScheduleViewModel,
    )

from backlog_manager.application.dto.scheduling.calculate_schedule_dto import (
    CalculateScheduleOutputDTO,
)
from backlog_manager.domain.exceptions import (  # noqa: E402
    BacklogManagerException,
    CyclicDependencyException,
)


@pytest.fixture
def mock_container():
    """Create a mock DIContainer."""
    container = MagicMock()
    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    container.create_unit_of_work.return_value = mock_uow
    return container


@pytest.fixture
def viewmodel(mock_container):
    """Create a ScheduleViewModel."""
    return ScheduleViewModel(mock_container)


def _make_schedule_result(stories_processed=10, stories_updated=8, warnings=None):
    return CalculateScheduleOutputDTO(
        success=True,
        stories_processed=stories_processed,
        stories_updated=stories_updated,
        warnings=warnings or [],
    )


# noqa: D101
class TestScheduleViewModelInitialization:
    def test_initial_state(self, viewmodel) -> None:
        assert viewmodel.is_running is False

    def test_stores_container(self, viewmodel, mock_container) -> None:
        assert viewmodel._container is mock_container


# noqa: D101
class TestScheduleExecuteSuccess:
    @pytest.mark.asyncio
    async def test_successful_execution(self, viewmodel, mock_container) -> None:
        expected = _make_schedule_result(stories_processed=10, stories_updated=8)
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = expected
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        result = await viewmodel.execute(velocity=2.5, start_date=date(2026, 1, 1))
        assert result is expected
        assert viewmodel.is_running is False
        assert len(viewmodel.schedule_started.emissions) == 1
        assert (expected,) in viewmodel.schedule_completed.emissions

    @pytest.mark.asyncio
    async def test_creates_correct_input_dto(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = _make_schedule_result()
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        await viewmodel.execute(velocity=3.0, start_date=date(2026, 6, 15))
        call_args = mock_uc.execute.call_args[0][0]
        assert call_args.velocity == 3.0
        assert call_args.start_date == date(2026, 6, 15)
        assert call_args.recalculate_all is True

    @pytest.mark.asyncio
    async def test_uses_uow_context(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = _make_schedule_result()
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        mock_container.create_unit_of_work.assert_called_once()


# noqa: D101
class TestScheduleExecuteGuard:
    @pytest.mark.asyncio
    async def test_returns_none_when_already_running(self, viewmodel) -> None:
        viewmodel._is_running = True
        result = await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert result is None
        assert len(viewmodel.schedule_started.emissions) == 0

    @pytest.mark.asyncio
    async def test_sets_flag_during_execution(self, viewmodel, mock_container) -> None:
        captured = {}

        async def capture(*args, **kwargs):
            captured["v"] = viewmodel.is_running
            return _make_schedule_result()

        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = capture
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert captured["v"] is True
        assert viewmodel.is_running is False


# noqa: D101
class TestScheduleExecuteErrors:
    @pytest.mark.asyncio
    async def test_cyclic_dependency_error(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = CyclicDependencyException(
            path=["A-001", "A-002", "A-001"]
        )
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        result = await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert result is None
        assert viewmodel.is_running is False
        assert len(viewmodel.schedule_error.emissions) == 1
        error_msg = viewmodel.schedule_error.emissions[0][0]
        assert "Dependencia ciclica detectada" in error_msg
        assert "A-001 -> A-002 -> A-001" in error_msg

    @pytest.mark.asyncio
    async def test_backlog_manager_exception(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = BacklogManagerException("Domain problem")
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        result = await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert result is None
        assert viewmodel.is_running is False
        error_msg = viewmodel.schedule_error.emissions[0][0]
        assert "Erro ao calcular cronograma" in error_msg
        assert "Domain problem" in error_msg

    @pytest.mark.asyncio
    async def test_unexpected_exception(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = RuntimeError("kaboom")
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        result = await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert result is None
        assert viewmodel.is_running is False
        error_msg = viewmodel.schedule_error.emissions[0][0]
        assert "Erro inesperado ao calcular cronograma" in error_msg
        assert "kaboom" in error_msg

    @pytest.mark.asyncio
    async def test_resets_flag_on_cyclic_error(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = CyclicDependencyException(path=["X", "Y", "X"])
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert viewmodel.is_running is False

    @pytest.mark.asyncio
    async def test_resets_flag_on_unexpected_error(
        self, viewmodel, mock_container
    ) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ValueError("bad")
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert viewmodel.is_running is False


# noqa: D101
class TestScheduleSignals:
    @pytest.mark.asyncio
    async def test_no_completed_signal_on_error(
        self, viewmodel, mock_container
    ) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = RuntimeError("fail")
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert len(viewmodel.schedule_completed.emissions) == 0
        assert len(viewmodel.schedule_error.emissions) == 1

    @pytest.mark.asyncio
    async def test_started_signal_emitted_even_on_error(
        self, viewmodel, mock_container
    ) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = BacklogManagerException("err")
        mock_container.create_calculate_schedule_use_case.return_value = mock_uc
        await viewmodel.execute(velocity=1.0, start_date=date(2026, 1, 1))
        assert len(viewmodel.schedule_started.emissions) == 1
