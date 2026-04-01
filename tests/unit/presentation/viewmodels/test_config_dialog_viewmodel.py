"""Headless tests for ConfigDialogViewModel."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks(with_qsettings=True)

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.config_dialog_viewmodel import (
        ConfigDialogViewModel,
    )


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


def _make_vm() -> ConfigDialogViewModel:
    """Create a ConfigDialogViewModel with mock container and mocked QSettings."""
    container = MagicMock()
    mock_settings = MagicMock()
    mock_settings.value.return_value = None
    with patch.object(
        ConfigDialogViewModel, "_get_qsettings", return_value=mock_settings
    ):
        vm = ConfigDialogViewModel(container)
    return vm


# ===========================================================================
# Validation tests
# ===========================================================================


class TestConfigDialogViewModelValidate:
    """Tests for validate() boundaries."""

    def test_validate_default_values(self) -> None:
        vm = _make_vm()
        is_valid, msg = vm.validate()
        assert is_valid
        assert msg == ""

    def test_validate_sp_per_sprint_too_low(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 0
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "sp/sprint" in msg.lower()

    def test_validate_sp_per_sprint_too_high(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 101
        is_valid, _ = vm.validate()
        assert not is_valid

    def test_validate_sp_per_sprint_at_min(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 1
        is_valid, _ = vm.validate()
        assert is_valid

    def test_validate_sp_per_sprint_at_max(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 100
        is_valid, _ = vm.validate()
        assert is_valid

    def test_validate_max_idle_too_low(self) -> None:
        vm = _make_vm()
        vm.max_idle_days = 1
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "dias" in msg.lower() or "ociosos" in msg.lower()

    def test_validate_max_idle_too_high(self) -> None:
        vm = _make_vm()
        vm.max_idle_days = 31
        is_valid, _ = vm.validate()
        assert not is_valid

    def test_validate_max_idle_at_min(self) -> None:
        vm = _make_vm()
        vm.max_idle_days = 2
        is_valid, _ = vm.validate()
        assert is_valid

    def test_validate_max_idle_at_max(self) -> None:
        vm = _make_vm()
        vm.max_idle_days = 30
        is_valid, _ = vm.validate()
        assert is_valid


# ===========================================================================
# Save tests
# ===========================================================================


class TestConfigDialogViewModelSave:
    """Tests for save()."""

    def test_save_emits_saved_on_valid(self) -> None:
        vm = _make_vm()
        mock_settings = MagicMock()
        with patch.object(
            ConfigDialogViewModel, "_get_qsettings", return_value=mock_settings
        ):
            vm.save()
        assert len(vm.saved.emissions) == 1

    def test_save_emits_error_on_invalid(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 0
        vm.save()
        assert len(vm.error_occurred.emissions) == 1


# ===========================================================================
# Property tests
# ===========================================================================


class TestConfigDialogViewModelProperties:
    """Tests for property getters and setters."""

    def test_velocity_property_derived(self) -> None:
        vm = _make_vm()
        assert vm.velocity == pytest.approx(2.0)  # 20/10
        vm.sp_per_sprint = 50
        vm.workdays_per_sprint = 10
        assert vm.velocity == pytest.approx(5.0)

    def test_start_date_property(self) -> None:
        vm = _make_vm()
        assert vm.start_date == date.today()
        new_date = date(2026, 6, 1)
        vm.start_date = new_date
        assert vm.start_date == new_date

    def test_max_idle_days_property(self) -> None:
        vm = _make_vm()
        assert vm.max_idle_days == 3
        vm.max_idle_days = 10
        assert vm.max_idle_days == 10


# ===========================================================================
# SP / Workdays / Velocity tests
# ===========================================================================


class TestSpPerSprintAndWorkdays:
    """Tests for sp_per_sprint, workdays_per_sprint properties and velocity_per_day derivation (T001)."""

    def test_sp_per_sprint_default(self) -> None:
        vm = _make_vm()
        assert vm.sp_per_sprint == 20

    def test_sp_per_sprint_setter(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 30
        assert vm.sp_per_sprint == 30

    def test_workdays_per_sprint_default(self) -> None:
        vm = _make_vm()
        assert vm.workdays_per_sprint == 10

    def test_workdays_per_sprint_setter(self) -> None:
        vm = _make_vm()
        vm.workdays_per_sprint = 5
        assert vm.workdays_per_sprint == 5

    def test_velocity_per_day_derived(self) -> None:
        vm = _make_vm()
        assert vm.velocity_per_day == pytest.approx(2.0)

    def test_velocity_per_day_after_change(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 15
        vm.workdays_per_sprint = 5
        assert vm.velocity_per_day == pytest.approx(3.0)

    def test_velocity_per_day_fractional(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 10
        vm.workdays_per_sprint = 3
        assert abs(vm.velocity_per_day - 10 / 3) < 0.001

    def test_velocity_property_returns_velocity_per_day(self) -> None:
        """velocity property should return derived velocity_per_day for retrocompatibility."""
        vm = _make_vm()
        vm.sp_per_sprint = 30
        vm.workdays_per_sprint = 10
        assert vm.velocity == pytest.approx(3.0)


# ===========================================================================
# Validation boundary tests (T002)
# ===========================================================================


class TestSpPerSprintValidation:
    """Tests for validation rules on sp_per_sprint and workdays_per_sprint (T002)."""

    def test_sp_per_sprint_below_min_invalid(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 0
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "sp/sprint" in msg.lower() or "sp" in msg.lower()

    def test_sp_per_sprint_above_max_invalid(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 101
        is_valid, _ = vm.validate()
        assert not is_valid

    def test_sp_per_sprint_at_min_valid(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 1
        is_valid, _ = vm.validate()
        assert is_valid

    def test_sp_per_sprint_at_max_valid(self) -> None:
        vm = _make_vm()
        vm.sp_per_sprint = 100
        is_valid, _ = vm.validate()
        assert is_valid

    def test_workdays_below_min_invalid(self) -> None:
        vm = _make_vm()
        vm.workdays_per_sprint = 0
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "dias" in msg.lower() or "workdays" in msg.lower()

    def test_workdays_above_max_invalid(self) -> None:
        vm = _make_vm()
        vm.workdays_per_sprint = 31
        is_valid, _ = vm.validate()
        assert not is_valid

    def test_workdays_at_min_valid(self) -> None:
        vm = _make_vm()
        vm.workdays_per_sprint = 1
        is_valid, _ = vm.validate()
        assert is_valid

    def test_workdays_at_max_valid(self) -> None:
        vm = _make_vm()
        vm.workdays_per_sprint = 30
        is_valid, _ = vm.validate()
        assert is_valid

    def test_division_by_zero_protected(self) -> None:
        """workdays_per_sprint=0 should be caught by validation before velocity_per_day is computed."""
        vm = _make_vm()
        vm.workdays_per_sprint = 0
        is_valid, _ = vm.validate()
        assert not is_valid
