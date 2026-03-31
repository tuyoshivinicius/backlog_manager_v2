"""Unit tests for ConfigDialogViewModel QSettings persistence."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from backlog_manager.presentation.viewmodels.config_dialog_viewmodel import (
    ConfigDialogViewModel,
)
from PySide6.QtCore import QSettings


def _create_vm() -> ConfigDialogViewModel:
    """Create a ConfigDialogViewModel with mock container."""
    container = MagicMock()
    return ConfigDialogViewModel(container)


def _get_settings() -> QSettings:
    return QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "BacklogManager",
        "Backlog Manager",
    )


class TestConfigQSettingsPersistence:
    """Tests for QSettings load/save in ConfigDialogViewModel (T008)."""

    def setup_method(self) -> None:
        """Clear QSettings before each test."""
        settings = _get_settings()
        settings.remove("allocation")

    def test_save_persists_sp_per_sprint_and_workdays(self) -> None:
        """save() writes sp_per_sprint and workdays_per_sprint to QSettings."""
        vm = _create_vm()
        vm.sp_per_sprint = 30
        vm.workdays_per_sprint = 15
        vm.start_date = date(2026, 1, 15)
        vm.max_idle_days = 5
        vm.save()

        settings = _get_settings()
        settings.beginGroup("allocation")
        assert int(settings.value("sp_per_sprint")) == 30
        assert int(settings.value("workdays_per_sprint")) == 15
        assert settings.value("start_date") == "2026-01-15"
        assert int(settings.value("max_idle_days")) == 5
        settings.endGroup()

    def test_save_does_not_write_legacy_velocity(self) -> None:
        """save() should NOT write legacy 'velocity' field."""
        vm = _create_vm()
        vm.save()

        settings = _get_settings()
        settings.beginGroup("allocation")
        assert settings.value("velocity") is None
        settings.endGroup()

    def test_load_restores_sp_per_sprint_and_workdays(self) -> None:
        """__init__ loads previously saved sp_per_sprint and workdays."""
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("sp_per_sprint", 25)
        settings.setValue("workdays_per_sprint", 5)
        settings.setValue("start_date", "2026-06-01")
        settings.setValue("max_idle_days", 10)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.sp_per_sprint == 25
        assert vm.workdays_per_sprint == 5
        assert vm.velocity_per_day == 5.0
        assert vm.start_date == date(2026, 6, 1)
        assert vm.max_idle_days == 10

    def test_sp_per_sprint_out_of_range_uses_default(self) -> None:
        """sp_per_sprint outside 1-100 falls back to default."""
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("sp_per_sprint", 200)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.sp_per_sprint == 20  # default

    def test_workdays_out_of_range_uses_default(self) -> None:
        """workdays_per_sprint outside 1-30 falls back to default."""
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("workdays_per_sprint", 50)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.workdays_per_sprint == 10  # default

    def test_max_idle_days_out_of_range_uses_default(self) -> None:
        """max_idle_days outside 2-30 falls back to default."""
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("max_idle_days", 100)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.max_idle_days == 3  # default

    def test_corrupt_values_use_defaults(self) -> None:
        """Corrupt/non-parseable values use defaults."""
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("sp_per_sprint", "not_a_number")
        settings.setValue("workdays_per_sprint", "abc")
        settings.setValue("start_date", "invalid-date")
        settings.setValue("max_idle_days", "abc")
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.sp_per_sprint == 20
        assert vm.workdays_per_sprint == 10
        assert vm.start_date == date.today()
        assert vm.max_idle_days == 3


class TestConfigQSettingsMigration:
    """Tests for QSettings migration scenarios (T009)."""

    def setup_method(self) -> None:
        """Clear QSettings before each test."""
        settings = _get_settings()
        settings.remove("allocation")

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
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("velocity", 3.5)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        # Should use defaults, NOT try to convert legacy velocity
        assert vm.sp_per_sprint == 20
        assert vm.workdays_per_sprint == 10
        assert vm.velocity_per_day == 2.0

    def test_current_format_loads_values(self) -> None:
        """Current format with sp_per_sprint and workdays loads correctly."""
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("sp_per_sprint", 40)
        settings.setValue("workdays_per_sprint", 20)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.sp_per_sprint == 40
        assert vm.workdays_per_sprint == 20
        assert vm.velocity_per_day == 2.0

    def test_mixed_legacy_and_current_ignores_legacy(self) -> None:
        """When both legacy velocity and new fields exist, use new fields."""
        settings = _get_settings()
        settings.beginGroup("allocation")
        settings.setValue("velocity", 5.0)  # legacy
        settings.setValue("sp_per_sprint", 30)
        settings.setValue("workdays_per_sprint", 10)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.sp_per_sprint == 30
        assert vm.workdays_per_sprint == 10
        assert vm.velocity_per_day == 3.0
