"""Integration tests for ConfigDialog."""

from __future__ import annotations

import pytest
from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import QDialogButtonBox

from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.views.config_dialog import ConfigDialog


@pytest.fixture(autouse=True)
def clear_qsettings():
    """Clear allocation QSettings before each test."""
    settings = QSettings(
        QSettings.Format.IniFormat,
        QSettings.Scope.UserScope,
        "BacklogManager",
        "Backlog Manager",
    )
    settings.remove("allocation")
    yield


class TestConfigDialogDisplay:
    """Tests for ConfigDialog display."""

    def test_dialog_opens_with_correct_title(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has correct title."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Configuracao de Alocacao"

    def test_dialog_has_fixed_size(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has fixed size 420x340."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.width() == 420
        assert dialog.height() == 340

    def test_dialog_is_modal(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog is modal."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.isModal()


class TestConfigDialogValues:
    """Tests for ConfigDialog value handling."""

    def test_default_sp_per_sprint(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test default SP/Sprint and workdays values."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._sp_per_sprint_spin.value() == 20
        assert dialog._workdays_per_sprint_spin.value() == 10

    def test_default_max_idle_days(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test default max idle days value."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._max_idle_spin.value() == 3

    def test_apply_valid_values(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test applying valid values."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        dialog._sp_per_sprint_spin.setValue(30)
        dialog._workdays_per_sprint_spin.setValue(10)
        dialog._max_idle_spin.setValue(5)

        # Click apply
        dialog._on_apply()

        # Verify viewmodel was updated
        vm = container.config_dialog_viewmodel
        assert vm.sp_per_sprint == 30
        assert vm.workdays_per_sprint == 10
        assert vm.velocity == 3.0
        assert vm.max_idle_days == 5

    def test_velocity_label_updates_dynamically(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that derived velocity label updates when spinboxes change."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        dialog._sp_per_sprint_spin.setValue(15)
        dialog._workdays_per_sprint_spin.setValue(5)

        assert "3.0" in dialog._velocity_label.text()
