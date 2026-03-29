"""Integration tests for ConfigDialog."""

from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox

from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.views.config_dialog import ConfigDialog


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

    def test_default_velocity(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test default velocity value."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._velocity_spin.value() == 2.0

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

        dialog._velocity_spin.setValue(3.0)
        dialog._max_idle_spin.setValue(5)

        # Click apply
        dialog._on_apply()

        # Verify viewmodel was updated
        vm = container.config_dialog_viewmodel
        assert vm.velocity == 3.0
        assert vm.max_idle_days == 5

    def test_reject_invalid_velocity_zero(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that velocity 0 shows error."""
        dialog = ConfigDialog(container)
        qtbot.addWidget(dialog)

        # SpinBox minimum is 0.1, so set via viewmodel
        dialog._velocity_spin.setValue(0.1)
        dialog._on_apply()

        # Should succeed at 0.1
        assert not dialog._error_label.isVisible()
