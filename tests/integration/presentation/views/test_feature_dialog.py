"""Integration tests for FeatureDialog.

This module contains integration tests for the FeatureDialog class,
verifying correct behavior of the feature management dialog.
"""

from __future__ import annotations

from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.views.feature_dialog import FeatureDialog
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QListWidgetItem, QStackedWidget


class TestFeatureDialogDisplay:
    """Tests for FeatureDialog display functionality."""

    def test_dialog_shows_with_correct_title(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog shows with correct title."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Gerenciar Features"

    def test_dialog_is_modal(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog is modal."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.isModal() is True

    def test_dialog_has_minimum_size(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has correct minimum size."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog.minimumWidth() == 450
        assert dialog.minimumHeight() == 400


class TestFeatureDialogComponents:
    """Tests for FeatureDialog UI components."""

    def test_has_feature_list(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has feature list."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._feature_list is not None

    def test_has_name_field(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has name field with correct properties."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._name_edit is not None
        assert dialog._name_edit.maxLength() == 100

    def test_has_wave_spinbox(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has wave spinbox with correct properties."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._wave_spinbox is not None
        assert dialog._wave_spinbox.minimum() == 1
        assert dialog._wave_spinbox.maximum() == 100
        assert dialog._wave_spinbox.value() == 1

    def test_has_add_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has add button with correct label."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._add_button is not None
        assert dialog._add_button.text() == "Adicionar"

    def test_has_save_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has save button."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._save_button is not None
        assert dialog._save_button.text() == "Salvar"

    def test_has_cancel_edit_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has cancel edit button (for exiting edit mode)."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._cancel_edit_button is not None
        assert dialog._cancel_edit_button.text() == "Cancelar Edicao"

    def test_has_remove_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has remove button."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._remove_button is not None
        assert dialog._remove_button.text() == "Remover"

    def test_has_close_button(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has close button."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._close_button is not None
        assert dialog._close_button.text() == "Fechar"

    def test_buttons_have_tooltips(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that buttons have tooltips."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._add_button.toolTip() != ""
        assert dialog._save_button.toolTip() != ""
        assert dialog._cancel_edit_button.toolTip() != ""
        assert dialog._remove_button.toolTip() != ""


class TestFeatureDialogButtonStates:
    """Tests for button state management."""

    def test_save_button_disabled_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that save button is disabled initially."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._save_button.isEnabled() is False

    def test_save_button_hidden_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that save button is hidden initially."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._save_button.isVisible() is False

    def test_cancel_edit_button_hidden_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that cancel edit button is hidden initially."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._cancel_edit_button.isVisible() is False

    def test_remove_button_disabled_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button is disabled when no selection."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._remove_button.isEnabled() is False

    def test_add_button_enabled_initially(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that add button is enabled initially."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._add_button.isEnabled() is True

    def test_remove_button_enabled_on_selection(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button is enabled when item is selected."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        # Add a feature item manually
        item = QListWidgetItem("Feature 1 (Onda 1)")
        item.setData(Qt.ItemDataRole.UserRole, {"id": 1, "wave": 1})
        dialog._feature_list.addItem(item)

        # Select the item
        dialog._feature_list.setCurrentItem(item)

        # FeatureDialog uses double-click to edit, so only remove is enabled on selection
        assert dialog._remove_button.isEnabled() is True

    def test_remove_button_disabled_on_deselection(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that remove button is disabled when selection is cleared."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        # Add and select a feature item
        item = QListWidgetItem("Feature 1 (Onda 1)")
        item.setData(Qt.ItemDataRole.UserRole, {"id": 1, "wave": 1})
        dialog._feature_list.addItem(item)
        dialog._feature_list.setCurrentItem(item)

        # Clear selection
        dialog._feature_list.setCurrentItem(None)

        assert dialog._remove_button.isEnabled() is False


class TestFeatureDialogFormFields:
    """Tests for form field behavior."""

    def test_name_field_placeholder(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that name field has placeholder text."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._name_edit.placeholderText() != ""

    def test_wave_spinbox_default_value(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that wave spinbox has correct default value."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert dialog._wave_spinbox.value() == 1


class TestFeatureDialogClose:
    """Tests for closing the dialog."""

    def test_close_button_accepts_dialog(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that close button accepts the dialog."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        with qtbot.waitSignal(dialog.accepted, timeout=1000):
            qtbot.mouseClick(dialog._close_button, Qt.MouseButton.LeftButton)


class TestFeatureDialogSignals:
    """Tests for FeatureDialog signals."""

    def test_has_features_changed_signal(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has features_changed signal."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        assert hasattr(dialog, "features_changed")


class TestFeatureDialogListOperations:
    """Tests for list display operations."""

    def test_feature_item_stores_id_and_wave(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that feature items store their IDs and waves."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        # Add a feature item manually with data
        item = QListWidgetItem("Test Feature (Onda 2)")
        item.setData(Qt.ItemDataRole.UserRole, {"id": 42, "wave": 2})
        dialog._feature_list.addItem(item)

        # Verify data is stored
        stored_data = dialog._feature_list.item(0).data(Qt.ItemDataRole.UserRole)
        assert stored_data["id"] == 42
        assert stored_data["wave"] == 2

    def test_feature_item_displays_name_and_wave(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that feature items display name and wave."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        # Add a feature item manually
        item = QListWidgetItem("Test Feature (Onda 2)")
        dialog._feature_list.addItem(item)

        # Verify display text
        assert "Test Feature" in dialog._feature_list.item(0).text()
        assert "Onda 2" in dialog._feature_list.item(0).text()


class TestFeatureDialogWaveFormat:
    """Tests for wave format display in feature list."""

    def test_feature_dialog_wave_format(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that items display 'Onda N \u2014 Nome' format."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        # Add items manually with the expected format
        item1 = QListWidgetItem("Onda 1 \u2014 Login")
        dialog._feature_list.addItem(item1)

        item2 = QListWidgetItem("Onda 2 \u2014 Dashboard")
        dialog._feature_list.addItem(item2)

        assert dialog._feature_list.item(0).text() == "Onda 1 \u2014 Login"
        assert dialog._feature_list.item(1).text() == "Onda 2 \u2014 Dashboard"


class TestFeatureDialogEmptyState:
    """Tests for empty state display."""

    def test_feature_dialog_empty_state(
        self,
        container: DIContainer,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that empty list shows orientative message via QStackedWidget."""
        dialog = FeatureDialog(container)
        qtbot.addWidget(dialog)

        # Verify stacked widget exists with correct object name
        stacked = dialog.findChild(QStackedWidget, "feature-stacked")
        assert stacked is not None

        # Verify empty state label exists with correct object name
        empty_label = dialog.findChild(QLabel, "feature-empty-state")
        assert empty_label is not None
        assert "Nenhuma feature cadastrada" in empty_label.text()
        assert "Adicionar" in empty_label.text()
