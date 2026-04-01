"""Headless tests for ConfigDialogViewModel QSettings persistence."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock, patch

from tests.headless_mocks import MockQSettings, create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks(with_qsettings=True)

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.presentation.viewmodels.config_dialog_viewmodel import (
        ConfigDialogViewModel,
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _create_vm() -> ConfigDialogViewModel:
    """Create a ConfigDialogViewModel with mock container."""
    container = MagicMock()
    return ConfigDialogViewModel(container)


def _set_setting(key: str, value: object) -> None:
    """Pre-populate a QSettings value for the allocation group."""
    MockQSettings._store[f"allocation/{key}"] = value


# ===========================================================================
# QSettings persistence tests (T008)
# ===========================================================================


class TestConfigQSettingsPersistence:
    """Tests for QSettings load/save in ConfigDialogViewModel (T008)."""

    def setup_method(self) -> None:
        """Clear QSettings before each test."""
        MockQSettings._store = {}

    def test_save_persists_sp_per_sprint_and_workdays(self) -> None:
        """save() writes sp_per_sprint and workdays_per_sprint to QSettings."""
        vm = _create_vm()
        vm.sp_per_sprint = 30
        vm.workdays_per_sprint = 15
        vm.start_date = date(2026, 1, 15)
        vm.max_idle_days = 5
        vm.save()

        assert MockQSettings._store["allocation/sp_per_sprint"] == 30
        assert MockQSettings._store["allocation/workdays_per_sprint"] == 15
        assert MockQSettings._store["allocation/start_date"] == "2026-01-15"
        assert MockQSettings._store["allocation/max_idle_days"] == 5

    def test_save_does_not_write_legacy_velocity(self) -> None:
        """save() should NOT write legacy 'velocity' field."""
        vm = _create_vm()
        vm.save()
        assert "allocation/velocity" not in MockQSettings._store

    def test_load_restores_sp_per_sprint_and_workdays(self) -> None:
        """__init__ loads previously saved sp_per_sprint and workdays."""
        _set_setting("sp_per_sprint", 25)
        _set_setting("workdays_per_sprint", 5)
        _set_setting("start_date", "2026-06-01")
        _set_setting("max_idle_days", 10)

        vm = _create_vm()
        assert vm.sp_per_sprint == 25
        assert vm.workdays_per_sprint == 5
        assert vm.velocity_per_day == 5.0
        assert vm.start_date == date(2026, 6, 1)
        assert vm.max_idle_days == 10

    def test_sp_per_sprint_out_of_range_uses_default(self) -> None:
        """sp_per_sprint outside 1-100 falls back to default."""
        _set_setting("sp_per_sprint", 200)
        vm = _create_vm()
        assert vm.sp_per_sprint == 20  # default

    def test_workdays_out_of_range_uses_default(self) -> None:
        """workdays_per_sprint outside 1-30 falls back to default."""
        _set_setting("workdays_per_sprint", 50)
        vm = _create_vm()
        assert vm.workdays_per_sprint == 10  # default

    def test_max_idle_days_out_of_range_uses_default(self) -> None:
        """max_idle_days outside 2-30 falls back to default."""
        _set_setting("max_idle_days", 100)
        vm = _create_vm()
        assert vm.max_idle_days == 3  # default

    def test_corrupt_values_use_defaults(self) -> None:
        """Corrupt/non-parseable values use defaults."""
        _set_setting("sp_per_sprint", "not_a_number")
        _set_setting("workdays_per_sprint", "abc")
        _set_setting("start_date", "invalid-date")
        _set_setting("max_idle_days", "abc")

        vm = _create_vm()
        assert vm.sp_per_sprint == 20
        assert vm.workdays_per_sprint == 10
        assert vm.start_date == date.today()
        assert vm.max_idle_days == 3


# ===========================================================================
# QSettings migration tests (T009)
# ===========================================================================


class TestConfigQSettingsMigration:
    """Tests for QSettings migration scenarios (T009)."""

    def setup_method(self) -> None:
        """Clear QSettings before each test."""
        MockQSettings._store = {}

    def test_first_run_empty_qsettings_uses_defaults(self) -> None:
        """First run with no saved QSettings uses defaults."""
        vm = _create_vm()
        assert vm.sp_per_sprint == 20
        assert vm.workdays_per_sprint == 10
        assert vm.velocity_per_day == 2.0
        assert vm.start_date == date.today()
        assert vm.max_idle_days == 3

    def test_legacy_velocity_only_uses_defaults(self) -> None:
        """Legacy QSettings with only 'velocity' field uses defaults for new fields."""
        _set_setting("velocity", 3.5)
        vm = _create_vm()
        # Should use defaults, NOT try to convert legacy velocity
        assert vm.sp_per_sprint == 20
        assert vm.workdays_per_sprint == 10
        assert vm.velocity_per_day == 2.0

    def test_current_format_loads_values(self) -> None:
        """Current format with sp_per_sprint and workdays loads correctly."""
        _set_setting("sp_per_sprint", 40)
        _set_setting("workdays_per_sprint", 20)
        vm = _create_vm()
        assert vm.sp_per_sprint == 40
        assert vm.workdays_per_sprint == 20
        assert vm.velocity_per_day == 2.0

    def test_mixed_legacy_and_current_ignores_legacy(self) -> None:
        """When both legacy velocity and new fields exist, use new fields."""
        _set_setting("velocity", 5.0)  # legacy
        _set_setting("sp_per_sprint", 30)
        _set_setting("workdays_per_sprint", 10)
        vm = _create_vm()
        assert vm.sp_per_sprint == 30
        assert vm.workdays_per_sprint == 10
        assert vm.velocity_per_day == 3.0
