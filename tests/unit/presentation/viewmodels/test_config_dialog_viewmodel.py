"""Unit tests for ConfigDialogViewModel."""

from __future__ import annotations

from datetime import date
from unittest.mock import MagicMock

from backlog_manager.presentation.viewmodels.config_dialog_viewmodel import (
    ConfigDialogViewModel,
)


def _make_vm(qapp) -> ConfigDialogViewModel:  # type: ignore[no-untyped-def]
    """Create a ConfigDialogViewModel with mock container."""
    container = MagicMock()
    return ConfigDialogViewModel(container)


class TestConfigDialogViewModelValidate:
    """Tests for validate() boundaries."""

    def test_validate_default_values(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        is_valid, msg = vm.validate()
        assert is_valid
        assert msg == ""

    def test_validate_velocity_too_low(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.velocity = 0.0
        is_valid, msg = vm.validate()
        assert not is_valid
        assert "velocidade" in msg.lower()

    def test_validate_velocity_too_high(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.velocity = 11.0
        is_valid, msg = vm.validate()
        assert not is_valid

    def test_validate_velocity_at_min(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.velocity = 0.1
        is_valid, _ = vm.validate()
        assert is_valid

    def test_validate_velocity_at_max(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        vm.velocity = 10.0
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
        vm.velocity = 0.0
        with qtbot.waitSignal(vm.error_occurred, timeout=1000):
            vm.save()


class TestConfigDialogViewModelProperties:
    """Tests for property getters and setters."""

    def test_velocity_property(self, qapp) -> None:  # type: ignore[no-untyped-def]
        vm = _make_vm(qapp)
        assert vm.velocity == 2.0
        vm.velocity = 5.0
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
