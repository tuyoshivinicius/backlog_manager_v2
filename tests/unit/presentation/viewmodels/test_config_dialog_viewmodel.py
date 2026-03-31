"""Unit tests for ConfigDialogViewModel."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from PySide6.QtCore import QSettings

from backlog_manager.presentation.viewmodels.config_dialog_viewmodel import (
    ConfigDialogViewModel,
)


def _clear_qsettings() -> None:
    """Clear allocation QSettings to ensure clean test state."""
    settings = QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "BacklogManager",
        "Backlog Manager",
    )
    settings.remove("allocation")


def _make_vm(qapp) -> ConfigDialogViewModel:  # type: ignore[no-untyped-def]
    """Create a ConfigDialogViewModel with mock container."""
    _clear_qsettings()
    container = MagicMock()
    return ConfigDialogViewModel(container)


class TestConfigDialogViewModelValidate:
    """Tests for validate() boundaries."""

    def test_validate_default_values(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        is_valid, msg = vm.validate()
        assert is_valid
        assert msg == ""

    def test_validate_sp_per_sprint_too_low(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 0
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "sp/sprint" in msg.lower()

    def test_validate_sp_per_sprint_too_high(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 101
        is_valid, msg = vm.validate()
        assert not is_valid

    def test_validate_sp_per_sprint_at_min(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 1
        is_valid, _ = vm.validate()
        assert is_valid

    def test_validate_sp_per_sprint_at_max(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 100
        is_valid, _ = vm.validate()
        assert is_valid

    def test_validate_max_idle_too_low(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.max_idle_days = 1
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "dias" in msg.lower() or "ociosos" in msg.lower()

    def test_validate_max_idle_too_high(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.max_idle_days = 31
        is_valid, msg = vm.validate()
        assert not is_valid

    def test_validate_max_idle_at_min(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.max_idle_days = 2
        is_valid, _ = vm.validate()
        assert is_valid

    def test_validate_max_idle_at_max(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.max_idle_days = 30
        is_valid, _ = vm.validate()
        assert is_valid


class TestConfigDialogViewModelSave:
    """Tests for save()."""

    def test_save_emits_saved_on_valid(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        with qtbot.waitSignal(vm.saved, timeout=1000):
            vm.save()

    def test_save_emits_error_on_invalid(self, qapp, qtbot) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 0
        with qtbot.waitSignal(vm.error_occurred, timeout=1000):
            vm.save()


class TestConfigDialogViewModelProperties:
    """Tests for property getters and setters."""

    def test_velocity_property_derived(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        assert vm.velocity == 2.0  # 20/10
        vm.sp_per_sprint = 50
        vm.workdays_per_sprint = 10
        assert vm.velocity == 5.0

    def test_start_date_property(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        assert vm.start_date == date.today()
        new_date = date(2026, 6, 1)
        vm.start_date = new_date
        assert vm.start_date == new_date

    def test_max_idle_days_property(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        assert vm.max_idle_days == 3
        vm.max_idle_days = 10
        assert vm.max_idle_days == 10


class TestSpPerSprintAndWorkdays:
    """Tests for sp_per_sprint, workdays_per_sprint properties and velocity_per_day derivation (T001)."""

    def test_sp_per_sprint_default(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        assert vm.sp_per_sprint == 20

    def test_sp_per_sprint_setter(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 30
        assert vm.sp_per_sprint == 30

    def test_workdays_per_sprint_default(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        assert vm.workdays_per_sprint == 10

    def test_workdays_per_sprint_setter(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.workdays_per_sprint = 5
        assert vm.workdays_per_sprint == 5

    def test_velocity_per_day_derived(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        # Default: 20 / 10 = 2.0
        assert vm.velocity_per_day == 2.0

    def test_velocity_per_day_after_change(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 15
        vm.workdays_per_sprint = 5
        assert vm.velocity_per_day == 3.0

    def test_velocity_per_day_fractional(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 10
        vm.workdays_per_sprint = 3
        assert abs(vm.velocity_per_day - 10 / 3) < 0.001

    def test_velocity_property_returns_velocity_per_day(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """velocity property should return derived velocity_per_day for retrocompatibility."""
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 30
        vm.workdays_per_sprint = 10
        assert vm.velocity == 3.0


class TestSpPerSprintValidation:
    """Tests for validation rules on sp_per_sprint and workdays_per_sprint (T002)."""

    def test_sp_per_sprint_below_min_invalid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 0
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "sp/sprint" in msg.lower() or "sp" in msg.lower()

    def test_sp_per_sprint_above_max_invalid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 101
        is_valid, msg = vm.validate()
        assert not is_valid

    def test_sp_per_sprint_at_min_valid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 1
        is_valid, _ = vm.validate()
        assert is_valid

    def test_sp_per_sprint_at_max_valid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.sp_per_sprint = 100
        is_valid, _ = vm.validate()
        assert is_valid

    def test_workdays_below_min_invalid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.workdays_per_sprint = 0
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "dias" in msg.lower() or "workdays" in msg.lower()

    def test_workdays_above_max_invalid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.workdays_per_sprint = 31
        is_valid, msg = vm.validate()
        assert not is_valid

    def test_workdays_at_min_valid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.workdays_per_sprint = 1
        is_valid, _ = vm.validate()
        assert is_valid

    def test_workdays_at_max_valid(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.workdays_per_sprint = 30
        is_valid, _ = vm.validate()
        assert is_valid

    def test_division_by_zero_protected(self, qapp) -> None:  # type: ignore[no-untyped-def]
        """workdays_per_sprint=0 should be caught by validation before velocity_per_day is computed."""
        vm = _make_vm(qapp)
        vm.workdays_per_sprint = 0
        is_valid, _ = vm.validate()
        assert not is_valid
