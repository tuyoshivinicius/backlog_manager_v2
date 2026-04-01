"""Headless tests for ManualAllocationDialogViewModel.

Tests business logic (data transformation, state management, signal emissions)
without any PySide6 dependency. Uses unittest.mock to mock PySide6 modules.
"""

from __future__ import annotations

# ---------------------------------------------------------------------------
# PySide6 mock setup — must happen before importing the module under test
# ---------------------------------------------------------------------------
import sys
from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

# Remove cached presentation modules so they get re-imported with mocked PySide6
_modules_to_purge = [
    key
    for key in sys.modules
    if key.startswith("backlog_manager.presentation.viewmodels.manual_allocation")
]
for _key in _modules_to_purge:
    del sys.modules[_key]

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.application.dto.allocation.developer_availability_dto import (
        DeveloperAvailabilityDTO,
    )
    from backlog_manager.application.dto.allocation.get_developer_availability_dto import (
        GetDeveloperAvailabilityOutputDTO,
    )
    from backlog_manager.presentation.viewmodels.manual_allocation_dialog_viewmodel import (
        ManualAllocationDialogViewModel,
    )

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_container() -> MagicMock:
    """Create a mock container with async UoW context manager."""
    container = MagicMock()
    container.config_dialog_viewmodel.velocity = 2.0

    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    mock_uow.commit = AsyncMock()
    container.create_unit_of_work.return_value = mock_uow
    return container


def _make_availability_output(
    dev_count: int = 2,
    recommended_id: int | None = 1,
) -> GetDeveloperAvailabilityOutputDTO:
    """Create a sample availability output DTO."""
    devs = []
    for i in range(1, dev_count + 1):
        devs.append(
            DeveloperAvailabilityDTO(
                developer_id=i,
                developer_name=f"Dev {i}",
                is_available=True,
                is_recommended=(i == recommended_id),
                blocking_stories=[],
                story_count=0,
            )
        )
    return GetDeveloperAvailabilityOutputDTO(
        developers=devs,
        recommended_developer_id=recommended_id,
        story_start_date=date(2026, 4, 1),
        story_end_date=date(2026, 4, 3),
    )


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestManualAllocationDialogViewModel:
    """Tests for ManualAllocationDialogViewModel."""

    def test_initial_state(self) -> None:
        """Test ViewModel initializes with correct default state."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)

        assert vm.selected_developer_id is None
        assert vm.new_start_date is None
        assert vm.new_end_date is None

    def test_selected_developer_setter(self) -> None:
        """Test setting the selected developer ID."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)

        vm.selected_developer_id = 5
        assert vm.selected_developer_id == 5

    def test_new_dates_none_when_not_changed(self) -> None:
        """Test that new dates return None when date was not changed."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)

        # Even if internal dates are set, new_start_date returns None
        # when date was not changed
        vm._new_start_date = date(2026, 4, 1)
        vm._new_end_date = date(2026, 4, 3)
        assert vm.new_start_date is None
        assert vm.new_end_date is None

    def test_new_dates_returned_when_changed(self) -> None:
        """Test that new dates are returned when date was changed."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)

        vm._date_was_changed = True
        vm._new_start_date = date(2026, 4, 2)
        vm._new_end_date = date(2026, 4, 4)
        assert vm.new_start_date == date(2026, 4, 2)
        assert vm.new_end_date == date(2026, 4, 4)

    def test_reset_clears_state(self) -> None:
        """Test that reset clears all internal state."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)

        vm._story_id = "TEST-001"
        vm._selected_developer_id = 1
        vm._date_was_changed = True
        vm._new_start_date = date(2026, 4, 1)

        vm.reset()

        assert vm._story_id == ""
        assert vm.selected_developer_id is None
        assert vm.new_start_date is None
        assert vm._date_was_changed is False

    @pytest.mark.asyncio
    async def test_load_developers_emits_signal(self) -> None:
        """Test that loading developers emits developers_loaded signal."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)

        output = _make_availability_output()
        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(return_value=output)

        container.create_get_developer_availability_use_case.return_value = (
            mock_use_case
        )

        await vm._load_developers_async("TEST-001", date(2026, 4, 1))

        assert len(vm.developers_loaded.emissions) == 1
        assert vm.developers_loaded.emissions[0][0].recommended_developer_id == 1

    @pytest.mark.asyncio
    async def test_load_developers_error_emits_signal(self) -> None:
        """Test that error during loading emits error_occurred signal."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock(side_effect=ValueError("not found"))
        container.create_get_developer_availability_use_case.return_value = (
            mock_use_case
        )

        await vm._load_developers_async("MISSING-001", date(2026, 4, 1))

        assert len(vm.error_occurred.emissions) == 1
        assert "not found" in vm.error_occurred.emissions[0][0]

    @pytest.mark.asyncio
    async def test_confirm_allocation_persists_developer_id(self) -> None:
        """Test that confirming allocation persists the developer ID."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)
        vm._story_id = "TEST-001"
        vm._selected_developer_id = 3

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock()
        container.create_edit_story_use_case.return_value = mock_use_case

        await vm._confirm_allocation_async()

        assert len(vm.allocation_confirmed.emissions) == 1
        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.story_id == "TEST-001"
        assert call_args.developer_id == 3

    @pytest.mark.asyncio
    async def test_confirm_with_changed_date_persists_all_fields(self) -> None:
        """Test that confirming with changed date persists all fields."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)
        vm._story_id = "TEST-001"
        vm._selected_developer_id = 2
        vm._date_was_changed = True
        vm._new_start_date = date(2026, 4, 6)
        vm._new_end_date = date(2026, 4, 8)

        mock_use_case = MagicMock()
        mock_use_case.execute = AsyncMock()
        container.create_edit_story_use_case.return_value = mock_use_case

        await vm._confirm_allocation_async()

        call_args = mock_use_case.execute.call_args[0][0]
        assert call_args.story_id == "TEST-001"
        assert call_args.developer_id == 2
        assert call_args.start_date == date(2026, 4, 6)
        assert call_args.end_date == date(2026, 4, 8)

    def test_on_date_changed_same_date_skips(self) -> None:
        """Test that on_date_changed skips when date is the same."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)
        vm._new_start_date = date(2026, 4, 1)

        with patch.object(vm, "load_developers") as mock_load:
            vm.on_date_changed(date(2026, 4, 1))
            mock_load.assert_not_called()

    def test_on_date_changed_different_date_loads(self) -> None:
        """Test that on_date_changed triggers load when date differs."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)
        vm._story_id = "TEST-001"
        vm._original_start_date = date(2026, 4, 1)
        vm._new_start_date = date(2026, 4, 1)

        with patch.object(vm, "load_developers") as mock_load:
            vm.on_date_changed(date(2026, 4, 6))
            mock_load.assert_called_once_with("TEST-001", date(2026, 4, 6))
            assert vm._date_was_changed is True

    def test_confirm_allocation_does_nothing_without_selection(self) -> None:
        """Test that confirm_allocation is a no-op without a selected developer."""
        container = _make_container()
        vm = ManualAllocationDialogViewModel(container)
        vm._selected_developer_id = None

        # Should not crash or create any task
        vm.confirm_allocation()
