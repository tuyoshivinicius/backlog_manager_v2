"""Unit tests for ConfigDialogViewModel QSettings persistence."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from PySide6.QtCore import QSettings

from backlog_manager.presentation.viewmodels.config_dialog_viewmodel import (
    ConfigDialogViewModel,
)


def _create_vm() -> ConfigDialogViewModel:
    """Create a ConfigDialogViewModel with mock container."""
    container = MagicMock()
    return ConfigDialogViewModel(container)


class TestConfigQSettingsPersistence:
    """Tests for QSettings load/save in ConfigDialogViewModel."""

    def setup_method(self) -> None:
        """Clear QSettings before each test."""
        settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "BacklogManager",
            "Backlog Manager",
        )
        settings.remove("allocation")

    def test_save_persists_to_qsettings(self) -> None:
        """save() writes values to QSettings."""
        vm = _create_vm()
        vm.velocity = 3.5
        vm.start_date = date(2026, 1, 15)
        vm.max_idle_days = 5
        vm.save()

        settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "BacklogManager",
            "Backlog Manager",
        )
        settings.beginGroup("allocation")
        assert float(settings.value("velocity")) == 3.5
        assert settings.value("start_date") == "2026-01-15"
        assert int(settings.value("max_idle_days")) == 5
        settings.endGroup()

    def test_load_restores_from_qsettings(self) -> None:
        """__init__ loads previously saved values from QSettings."""
        # Save values first
        settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "BacklogManager",
            "Backlog Manager",
        )
        settings.beginGroup("allocation")
        settings.setValue("velocity", 4.0)
        settings.setValue("start_date", "2026-06-01")
        settings.setValue("max_idle_days", 10)
        settings.endGroup()
        settings.sync()

        # Create new VM — should load values
        vm = _create_vm()
        assert vm.velocity == 4.0
        assert vm.start_date == date(2026, 6, 1)
        assert vm.max_idle_days == 10

    def test_velocity_out_of_range_uses_default(self) -> None:
        """Velocity outside 0.1-10.0 falls back to default."""
        settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "BacklogManager",
            "Backlog Manager",
        )
        settings.beginGroup("allocation")
        settings.setValue("velocity", 99.0)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.velocity == 2.0  # default

    def test_max_idle_days_out_of_range_uses_default(self) -> None:
        """max_idle_days outside 2-30 falls back to default."""
        settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "BacklogManager",
            "Backlog Manager",
        )
        settings.beginGroup("allocation")
        settings.setValue("max_idle_days", 100)
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.max_idle_days == 3  # default

    def test_corrupt_values_use_defaults(self) -> None:
        """Corrupt/non-parseable values use defaults."""
        settings = QSettings(
            QSettings.Format.IniFormat,
            QSettings.Scope.UserScope,
            "BacklogManager",
            "Backlog Manager",
        )
        settings.beginGroup("allocation")
        settings.setValue("velocity", "not_a_number")
        settings.setValue("start_date", "invalid-date")
        settings.setValue("max_idle_days", "abc")
        settings.endGroup()
        settings.sync()

        vm = _create_vm()
        assert vm.velocity == 2.0
        assert vm.start_date == date.today()
        assert vm.max_idle_days == 3

    def test_first_run_uses_defaults(self) -> None:
        """First run with no saved QSettings uses defaults."""
        vm = _create_vm()
        assert vm.velocity == 2.0
        assert vm.start_date == date.today()
        assert vm.max_idle_days == 3
