"""Integration tests for StoryDialog.

This module contains integration tests for the StoryDialog class,
verifying correct behavior of the story creation/edit dialog.
"""

from __future__ import annotations

import asyncio
from datetime import date
from typing import TYPE_CHECKING
from unittest.mock import AsyncMock, patch

import pytest
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialogButtonBox, QLabel

from backlog_manager.application.dto.feature import FeatureOutputDTO
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.viewmodels.story_dialog_viewmodel import (
    VALID_STORY_POINTS,
)
from backlog_manager.presentation.views.story_dialog import StoryDialog


class TestStoryDialogDisplay:
    """Tests for StoryDialog display functionality."""

    def test_dialog_shows_with_create_title(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog shows with correct title in create mode."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Nova Historia"

    def test_dialog_shows_with_edit_title(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog shows with correct title in edit mode."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        assert dialog.windowTitle() == "Editar Historia"

    def test_dialog_is_modal(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog is modal."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog.isModal() is True

    def test_dialog_has_minimum_width(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has minimum width."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog.minimumWidth() == 400


class TestStoryDialogFormFields:
    """Tests for StoryDialog form fields."""

    def test_has_component_field(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has component field."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog._component_edit is not None
        assert dialog._component_edit.maxLength() == 50

    def test_has_name_field(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has name field."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog._name_edit is not None
        assert dialog._name_edit.maxLength() == 200

    def test_has_story_points_combo(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has story points combo with valid values."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog._sp_combo is not None
        assert dialog._sp_combo.count() == len(VALID_STORY_POINTS)

        for i, sp in enumerate(VALID_STORY_POINTS):
            assert dialog._sp_combo.itemData(i) == sp

    def test_has_feature_combo(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has feature combo."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog._feature_combo is not None
        # Should have at least "Nenhuma" option
        assert dialog._feature_combo.count() >= 1

    def test_has_save_cancel_buttons(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that dialog has save and cancel buttons."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        ok_button = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
        cancel_button = dialog._button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        assert ok_button is not None
        assert ok_button.text() == "Salvar"
        assert cancel_button is not None
        assert cancel_button.text() == "Cancelar"


class TestStoryDialogEditMode:
    """Tests for StoryDialog in edit mode."""

    def test_edit_mode_populates_fields(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that edit mode populates form fields."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        assert dialog._component_edit.text() == sample_story_dto.component
        assert dialog._name_edit.text() == sample_story_dto.name

    def test_edit_mode_disables_component_field(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that component field is disabled in edit mode."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        assert dialog._component_edit.isEnabled() is False

    def test_create_mode_enables_component_field(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that component field is enabled in create mode."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog._component_edit.isEnabled() is True


class TestStoryDialogValidation:
    """Tests for StoryDialog validation."""

    def test_viewmodel_validation_for_empty_component(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that viewmodel validation fails for empty component."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        # Leave component empty, fill name
        dialog._name_edit.setText("Test Story")

        # Validate through viewmodel
        is_valid, error = dialog._viewmodel.validate()

        assert is_valid is False
        assert "Componente" in error

    def test_viewmodel_validation_for_empty_name(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that viewmodel validation fails for empty name."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        # Fill component, leave name empty
        dialog._component_edit.setText("TEST")

        # Validate through viewmodel
        is_valid, error = dialog._viewmodel.validate()

        assert is_valid is False
        assert "Nome" in error

    def test_viewmodel_validation_passes_with_valid_data(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that viewmodel validation passes with valid data."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        # Fill all required fields
        dialog._component_edit.setText("TEST")
        dialog._name_edit.setText("Test Story")

        # Validate through viewmodel
        is_valid, error = dialog._viewmodel.validate()

        assert is_valid is True
        assert error == ""


class TestStoryDialogCancel:
    """Tests for cancelling the dialog."""

    def test_cancel_rejects_dialog(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that cancel button rejects the dialog."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        # Click cancel
        cancel_button = dialog._button_box.button(
            QDialogButtonBox.StandardButton.Cancel
        )

        with qtbot.waitSignal(dialog.rejected, timeout=1000):
            qtbot.mouseClick(cancel_button, Qt.MouseButton.LeftButton)

    def test_result_story_is_none_after_cancel(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that result_story is None after cancel."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        dialog.reject()

        assert dialog.result_story is None


class TestStoryDialogFormBinding:
    """Tests for form field binding to ViewModel."""

    def test_component_change_updates_viewmodel(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that component field changes update ViewModel."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        dialog._component_edit.setText("api")

        # ViewModel should have uppercased value
        assert dialog._viewmodel.component == "API"

    def test_name_change_updates_viewmodel(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that name field changes update ViewModel."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        dialog._name_edit.setText("Test Story")

        assert dialog._viewmodel.name == "Test Story"

    def test_sp_change_updates_viewmodel(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that story points combo changes update ViewModel."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        # Select 8 story points (index 2)
        dialog._sp_combo.setCurrentIndex(2)

        assert dialog._viewmodel.story_points == 8

    def test_feature_change_updates_viewmodel(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that feature combo changes update ViewModel."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        # Add a feature to the combo
        dialog._feature_combo.addItem("Test Feature", 42)
        dialog._feature_combo.setCurrentIndex(1)

        assert dialog._viewmodel.feature_id == 42


class TestStoryDialogDeveloperField:
    """Tests for developer field in StoryDialog (US1)."""

    def test_story_dialog_developer_field_visible_edit_mode(
        self,
        container: DIContainer,
        sample_story_dto: StoryOutputDTO,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test developer field is visible in edit mode."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        assert dialog._developer_container.isHidden() is False
        assert dialog._developer_combo is not None

    def test_story_dialog_developer_field_hidden_create_mode(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test developer field is hidden in create mode."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog._developer_container.isHidden() is True


class TestStoryDialogStatusField:
    """Tests for status field in StoryDialog."""

    def test_story_dialog_status_field_visible_edit_mode(
        self,
        container: DIContainer,
        sample_story_dto: StoryOutputDTO,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test status field is visible in edit mode."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        assert dialog._status_container.isHidden() is False
        assert dialog._status_combo is not None

    def test_story_dialog_status_field_hidden_create_mode(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test status field is hidden in create mode."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        assert dialog._status_container.isHidden() is True

    def test_story_dialog_status_preselects_current(
        self,
        container: DIContainer,
        sample_story_dto: StoryOutputDTO,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test status combo pre-selects the story's current status."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        assert dialog._status_combo.currentData() == sample_story_dto.status

    def test_story_dialog_status_combo_has_all_values(
        self,
        container: DIContainer,
        sample_story_dto: StoryOutputDTO,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test status combo has all 5 status values."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        values = [
            dialog._status_combo.itemData(i)
            for i in range(dialog._status_combo.count())
        ]
        assert values == ["BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO"]

    def test_story_dialog_status_change_updates_viewmodel(
        self,
        container: DIContainer,
        sample_story_dto: StoryOutputDTO,
        qapp,
        qtbot,  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that status combo changes update ViewModel."""
        dialog = StoryDialog(container, mode="edit", story=sample_story_dto)
        qtbot.addWidget(dialog)

        # Select CONCLUIDO (index 3)
        dialog._status_combo.setCurrentIndex(3)
        assert dialog._viewmodel.status == "CONCLUIDO"


class TestStoryDialogValidationUI:
    """Tests for validation UI in StoryDialog (US2)."""

    def test_story_dialog_required_indicators(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test asterisk (*) on Componente and Nome labels."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)

        # Find required indicators by objectName
        indicators = dialog.findChildren(QLabel, "required-indicator")
        assert len(indicators) >= 2
        for indicator in indicators:
            assert indicator.text() == "*"

    def test_story_dialog_error_on_blur(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test red border and error label on focusOut."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)
        dialog.show()

        # Focus component, then leave without filling
        dialog._component_edit.setFocus()
        dialog._name_edit.setFocus()  # Triggers focusOut on component

        assert dialog._component_error_label.isHidden() is False
        assert dialog._component_edit.property("error") == "true"

    def test_story_dialog_save_button_disabled(
        self, container: DIContainer, qapp, qtbot  # type: ignore[no-untyped-def]
    ) -> None:
        """Test button disabled when fields invalid."""
        dialog = StoryDialog(container, mode="create")
        qtbot.addWidget(dialog)
        dialog.show()

        # Trigger validation on both fields
        dialog._component_edit.setFocus()
        dialog._name_edit.setFocus()
        dialog._sp_combo.setFocus()  # Leave name field

        save_button = dialog._button_box.button(QDialogButtonBox.StandardButton.Ok)
        assert save_button.isEnabled() is False
