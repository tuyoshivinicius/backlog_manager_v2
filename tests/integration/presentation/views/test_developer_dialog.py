"""Integration tests for DeveloperDialog.

This module contains integration tests for the DeveloperDialog class,
verifying correct behavior of the developer management dialog.
"""

from __future__ import annotations

from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.views.developer_dialog import DeveloperDialog
from PySide6.QtCore import Qt


class TestDeveloperDialogDisplay:
    """Tests for DeveloperDialog display functionality."""

    def test_dialog_shows_with_correct_title(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog shows with correct title."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Gerenciar Desenvolvedores"

    def test_dialog_is_modal(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog is modal."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.isModal() is True

    def test_dialog_has_minimum_size(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has correct minimum size."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.minimumWidth() == 400
        assert dialog.minimumHeight() == 300


class TestDeveloperDialogComponents:
    """Tests for DeveloperDialog UI components."""

    def test_has_developer_list(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has developer list."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._developer_list is not None

    def test_has_add_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has add button with correct label."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._add_button is not None
        assert dialog._add_button.text() == "Adicionar"

    def test_has_edit_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has edit button with correct label."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._edit_button is not None
        assert dialog._edit_button.text() == "Editar"

    def test_has_remove_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has remove button with correct label."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._remove_button is not None
        assert dialog._remove_button.text() == "Remover"

    def test_has_close_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has close button with correct label."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._close_button is not None
        assert dialog._close_button.text() == "Fechar"

    def test_add_button_has_tooltip(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that add button has tooltip."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._add_button.toolTip() != ""

    def test_edit_button_has_tooltip(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that edit button has tooltip."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._edit_button.toolTip() != ""

    def test_remove_button_has_tooltip(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button has tooltip."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._remove_button.toolTip() != ""


class TestDeveloperDialogButtonStates:
    """Tests for button state management."""

    def test_edit_button_disabled_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that edit button is disabled when no selection."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._edit_button.isEnabled() is False

    def test_remove_button_disabled_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button is disabled when no selection."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._remove_button.isEnabled() is False

    def test_add_button_always_enabled(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that add button is always enabled."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._add_button.isEnabled() is True

    def test_buttons_enabled_on_selection(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that buttons are enabled when item is selected."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        # Add a developer item manually
        from PySide6.QtWidgets import QListWidgetItem

        item = QListWidgetItem("Test Developer")
        item.setData(Qt.ItemDataRole.UserRole, 1)
        dialog._developer_list.addItem(item)

        # Select the item
        dialog._developer_list.setCurrentItem(item)

        assert dialog._edit_button.isEnabled() is True
        assert dialog._remove_button.isEnabled() is True

    def test_buttons_disabled_on_deselection(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that buttons are disabled when selection is cleared."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        # Add and select a developer item
        from PySide6.QtWidgets import QListWidgetItem

        item = QListWidgetItem("Test Developer")
        item.setData(Qt.ItemDataRole.UserRole, 1)
        dialog._developer_list.addItem(item)
        dialog._developer_list.setCurrentItem(item)

        # Clear selection
        dialog._developer_list.setCurrentItem(None)

        assert dialog._edit_button.isEnabled() is False
        assert dialog._remove_button.isEnabled() is False


class TestDeveloperDialogClose:
    """Tests for closing the dialog."""

    def test_close_button_accepts_dialog(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that close button accepts the dialog."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        with qtbot.waitSignal(dialog.accepted, timeout=1000):
            qtbot.mouseClick(dialog._close_button, Qt.MouseButton.LeftButton)


class TestDeveloperDialogSignals:
    """Tests for DeveloperDialog signals."""

    def test_has_developers_changed_signal(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has developers_changed signal."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert hasattr(dialog, "developers_changed")


class TestDeveloperDialogListOperations:
    """Tests for list display operations."""

    def test_developer_item_stores_id(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that developer items store their IDs."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        # Add a developer item manually
        from PySide6.QtWidgets import QListWidgetItem

        item = QListWidgetItem("Test Developer")
        item.setData(Qt.ItemDataRole.UserRole, 42)
        dialog._developer_list.addItem(item)

        # Verify ID is stored
        stored_id = dialog._developer_list.item(0).data(Qt.ItemDataRole.UserRole)
        assert stored_id == 42

    def test_developer_item_displays_name(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that developer items display their names."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        # Add a developer item manually
        from PySide6.QtWidgets import QListWidgetItem

        item = QListWidgetItem("Test Developer")
        dialog._developer_list.addItem(item)

        # Verify name is displayed
        assert dialog._developer_list.item(0).text() == "Test Developer"


class TestDeveloperDialogIcons:
    """Tests for DeveloperDialog button icons."""

    def test_developer_dialog_icons(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that all action buttons have non-null icons."""
        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        assert not dialog._add_button.icon().isNull()
        assert not dialog._edit_button.icon().isNull()
        assert not dialog._remove_button.icon().isNull()
        assert not dialog._close_button.icon().isNull()


class TestDeveloperDialogEmptyState:
    """Tests for DeveloperDialog empty state."""

    def test_developer_dialog_empty_state(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that empty list shows orientative message via QStackedWidget."""
        from PySide6.QtWidgets import QStackedWidget

        dialog = DeveloperDialog(container)
        qtbot.addWidget(dialog)

        # Verify stacked widget exists
        stacked = dialog.findChild(QStackedWidget, "developer-stacked")
        assert stacked is not None

        # With no items, empty state should be shown (index 1)
        dialog._developer_list.clear()
        dialog._update_empty_state()
        assert stacked.currentIndex() == 1

        # Verify the empty state label exists and has the correct text
        from PySide6.QtWidgets import QLabel

        empty_label = dialog.findChild(QLabel, "developer-empty-state")
        assert empty_label is not None
        assert "Nenhum desenvolvedor cadastrado" in empty_label.text()
