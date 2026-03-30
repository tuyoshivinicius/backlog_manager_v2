"""Tests for StoryDialogViewModel.

This module contains unit tests for the StoryDialogViewModel class,
verifying validation, signal emissions, and proper operation handling.
"""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
import pytest_asyncio
from PySide6.QtCore import SignalInstance

from backlog_manager.application.dto.developer import DeveloperOutputDTO
from backlog_manager.application.dto.feature import FeatureOutputDTO
from backlog_manager.application.dto.story import StoryOutputDTO
from backlog_manager.domain.exceptions import BacklogManagerException
from backlog_manager.presentation.container import DIContainer
from backlog_manager.presentation.viewmodels.story_dialog_viewmodel import (
    VALID_STORY_POINTS,
    StoryDialogViewModel,
)


class TestStoryDialogViewModelInitialization:
    """Tests for StoryDialogViewModel initialization."""

    def test_initial_state(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that ViewModel initializes with correct state."""
        viewmodel = StoryDialogViewModel(container)

        assert viewmodel.mode == "create"
        assert viewmodel.story_id is None
        assert viewmodel.component == ""
        assert viewmodel.name == ""
        assert viewmodel.story_points == 5
        assert viewmodel.feature_id is None
        assert viewmodel.features == []

    def test_has_required_signals(self, container: DIContainer, qapp) -> None:  # type: ignore[no-untyped-def]
        """Test that ViewModel has required signals."""
        viewmodel = StoryDialogViewModel(container)

        assert hasattr(viewmodel, "saved")
        assert hasattr(viewmodel, "error_occurred")
        assert hasattr(viewmodel, "features_loaded")


class TestStoryDialogViewModelProperties:
    """Tests for StoryDialogViewModel properties."""

    def test_component_setter_strips_and_uppercases(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that component setter strips whitespace and uppercases."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "  api  "

        assert viewmodel.component == "API"

    def test_name_setter_strips_whitespace(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that name setter strips whitespace."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.name = "  Test Story  "

        assert viewmodel.name == "Test Story"

    def test_story_points_setter_valid(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test setting valid story points."""
        viewmodel = StoryDialogViewModel(container)

        for sp in VALID_STORY_POINTS:
            viewmodel.story_points = sp
            assert viewmodel.story_points == sp

    def test_story_points_setter_invalid_ignored(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that invalid story points are ignored."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.story_points = 5  # Set valid first
        viewmodel.story_points = 7  # Invalid

        assert viewmodel.story_points == 5  # Unchanged

    def test_feature_id_setter(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test setting feature ID."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.feature_id = 42

        assert viewmodel.feature_id == 42

    def test_feature_id_can_be_none(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that feature ID can be set to None."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.feature_id = 42
        viewmodel.feature_id = None

        assert viewmodel.feature_id is None

    def test_features_returns_copy(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that features property returns a copy."""
        viewmodel = StoryDialogViewModel(container)
        features1 = viewmodel.features
        features2 = viewmodel.features

        assert features1 is not features2


class TestStoryDialogViewModelMode:
    """Tests for mode management."""

    def test_set_mode_to_create(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test setting mode to create."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel.set_mode("create")

        assert viewmodel.mode == "create"
        # Should reset form
        assert viewmodel.component == ""
        assert viewmodel.name == ""

    def test_set_mode_to_edit(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test setting mode to edit."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.set_mode("edit")

        assert viewmodel.mode == "edit"

    def test_set_story_populates_form(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that set_story populates the form."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.set_story(sample_story_dto)

        assert viewmodel.mode == "edit"
        assert viewmodel.story_id == sample_story_dto.id
        assert viewmodel.component == sample_story_dto.component
        assert viewmodel.name == sample_story_dto.name
        assert viewmodel.story_points == sample_story_dto.story_points
        assert viewmodel.feature_id == sample_story_dto.feature_id


class TestStoryDialogViewModelValidation:
    """Tests for form validation."""

    def test_validate_empty_component(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validation fails with empty component."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.name = "Test Story"

        is_valid, error = viewmodel.validate()

        assert is_valid is False
        assert "Componente" in error

    def test_validate_component_too_long(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validation fails with component > 50 chars."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "A" * 51
        viewmodel.name = "Test Story"

        is_valid, error = viewmodel.validate()

        assert is_valid is False
        assert "50" in error

    def test_validate_empty_name(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validation fails with empty name."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"

        is_valid, error = viewmodel.validate()

        assert is_valid is False
        assert "Nome" in error

    def test_validate_name_too_long(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validation fails with name > 200 chars."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "A" * 201

        is_valid, error = viewmodel.validate()

        assert is_valid is False
        assert "200" in error

    def test_validate_invalid_story_points(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validation fails with invalid story points."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel._story_points = 7  # Force invalid value

        is_valid, error = viewmodel.validate()

        assert is_valid is False
        assert "Story Points" in error

    def test_validate_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validation succeeds with valid data."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel.story_points = 5

        is_valid, error = viewmodel.validate()

        assert is_valid is True
        assert error == ""


class TestStoryDialogViewModelLoadFeatures:
    """Tests for loading features."""

    @pytest.mark.asyncio
    async def test_load_features_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful feature loading."""
        viewmodel = StoryDialogViewModel(container)

        features_received = []

        def on_features_loaded(features: list) -> None:
            features_received.extend(features)

        viewmodel.features_loaded.connect(on_features_loaded)

        # Create mock features
        mock_features = [
            FeatureOutputDTO(id=1, name="Feature 1", wave=1),
            FeatureOutputDTO(id=2, name="Feature 2", wave=2),
        ]

        # Mock the list features use case
        mock_use_case = AsyncMock()
        mock_result = MagicMock()
        mock_result.features = mock_features
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container, "create_list_features_use_case", return_value=mock_use_case
        ):
            await viewmodel.load_features()

        assert len(viewmodel.features) == 2
        assert len(features_received) == 2

    @pytest.mark.asyncio
    async def test_load_features_error_emits_signal(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that feature loading errors emit error signal."""
        viewmodel = StoryDialogViewModel(container)

        errors_received = []

        def on_error(message: str) -> None:
            errors_received.append(message)

        viewmodel.error_occurred.connect(on_error)

        # Mock to raise exception
        with patch.object(
            container,
            "create_unit_of_work",
            side_effect=Exception("Connection failed"),
        ):
            await viewmodel.load_features()

        assert len(errors_received) == 1
        assert "Erro" in errors_received[0]


class TestStoryDialogViewModelSave:
    """Tests for saving stories."""

    @pytest.mark.asyncio
    async def test_save_validation_error_emits_signal(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that validation errors emit error signal."""
        viewmodel = StoryDialogViewModel(container)
        # Empty component - invalid

        errors_received = []

        def on_error(message: str) -> None:
            errors_received.append(message)

        viewmodel.error_occurred.connect(on_error)

        result = await viewmodel.save()

        assert result is None
        assert len(errors_received) == 1
        assert "Componente" in errors_received[0]

    @pytest.mark.asyncio
    async def test_save_create_success(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful story creation."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel.story_points = 5

        saved_emitted = []

        def on_saved() -> None:
            saved_emitted.append(True)

        viewmodel.saved.connect(on_saved)

        # Mock the create story use case
        mock_story = StoryOutputDTO(
            id="TEST-001",
            component="TEST",
            name="Test Story",
            story_points=5,
            priority=1,
            status="BACKLOG",
            duration=3,
            start_date=None,
            end_date=None,
            developer_id=None,
            feature_id=None,
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_story

        with patch.object(
            container, "create_story_use_case_factory", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is not None
        assert result.id == "TEST-001"
        assert len(saved_emitted) == 1

    @pytest.mark.asyncio
    async def test_save_edit_success(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test successful story editing."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.set_story(sample_story_dto)
        viewmodel.name = "Updated Story"

        saved_emitted = []

        def on_saved() -> None:
            saved_emitted.append(True)

        viewmodel.saved.connect(on_saved)

        # Mock the edit story use case
        mock_story = StoryOutputDTO(
            id=sample_story_dto.id,
            component=sample_story_dto.component,
            name="Updated Story",
            story_points=sample_story_dto.story_points,
            priority=sample_story_dto.priority,
            status=sample_story_dto.status,
            duration=sample_story_dto.duration,
            start_date=sample_story_dto.start_date,
            end_date=sample_story_dto.end_date,
            developer_id=sample_story_dto.developer_id,
            feature_id=sample_story_dto.feature_id,
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_story

        with patch.object(
            container, "create_edit_story_use_case", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is not None
        assert result.name == "Updated Story"
        assert len(saved_emitted) == 1

    @pytest.mark.asyncio
    async def test_save_backlog_manager_exception_emits_error(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that BacklogManagerException emits error signal."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"

        errors_received = []

        def on_error(message: str) -> None:
            errors_received.append(message)

        viewmodel.error_occurred.connect(on_error)

        # Mock to raise BacklogManagerException
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = BacklogManagerException(
            "Historia duplicada"
        )

        with patch.object(
            container, "create_story_use_case_factory", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is None
        assert len(errors_received) == 1
        assert "Historia duplicada" in errors_received[0]

    @pytest.mark.asyncio
    async def test_save_unexpected_exception_emits_error(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that unexpected exceptions emit error signal."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"

        errors_received = []

        def on_error(message: str) -> None:
            errors_received.append(message)

        viewmodel.error_occurred.connect(on_error)

        # Mock to raise generic exception
        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = RuntimeError("Unexpected error")

        with patch.object(
            container, "create_story_use_case_factory", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is None
        assert len(errors_received) == 1
        assert "Erro inesperado" in errors_received[0]


class TestStoryDialogViewModelDeveloperId:
    """Tests for developer_id property and load_developers (US1)."""

    def test_developer_id_property_get_set(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test developer_id property accepts int and None."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.developer_id = 42
        assert viewmodel.developer_id == 42

        viewmodel.developer_id = None
        assert viewmodel.developer_id is None

    def test_developer_id_initial_none(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test initial developer_id is None."""
        viewmodel = StoryDialogViewModel(container)
        assert viewmodel.developer_id is None

    def test_set_story_loads_developer_id(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test that set_story recovers developer_id."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.set_story(sample_story_dto)
        assert viewmodel.developer_id == sample_story_dto.developer_id

    @pytest.mark.asyncio
    async def test_load_developers_returns_list(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test load_developers populates list via ListDevelopersUseCase."""
        viewmodel = StoryDialogViewModel(container)

        developers_received = []

        def on_developers_loaded(devs: list) -> None:
            developers_received.extend(devs)

        viewmodel.developers_loaded.connect(on_developers_loaded)

        mock_developers = [
            DeveloperOutputDTO(id=1, name="Dev 1"),
            DeveloperOutputDTO(id=2, name="Dev 2"),
        ]

        mock_use_case = AsyncMock()
        mock_result = MagicMock()
        mock_result.developers = mock_developers
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container, "create_list_developers_use_case", return_value=mock_use_case
        ):
            await viewmodel.load_developers()

        assert len(viewmodel.developers) == 2
        assert len(developers_received) == 2

    @pytest.mark.asyncio
    async def test_load_developers_includes_none_option(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test loaded list allows 'Nenhum' (no developer) as first dropdown option."""
        viewmodel = StoryDialogViewModel(container)

        developers_received = []

        def on_developers_loaded(devs: list) -> None:
            developers_received.extend(devs)

        viewmodel.developers_loaded.connect(on_developers_loaded)

        mock_developers = [DeveloperOutputDTO(id=1, name="Dev 1")]

        mock_use_case = AsyncMock()
        mock_result = MagicMock()
        mock_result.developers = mock_developers
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container, "create_list_developers_use_case", return_value=mock_use_case
        ):
            await viewmodel.load_developers()

        # ViewModel stores developers; View is responsible for adding "Nenhum" option
        assert len(viewmodel.developers) == 1
        # developer_id can be None to represent "Nenhum"
        assert viewmodel.developer_id is None

    @pytest.mark.asyncio
    async def test_load_developers_error_emits_signal(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test load failure emits error_occurred."""
        viewmodel = StoryDialogViewModel(container)

        errors_received = []

        def on_error(message: str) -> None:
            errors_received.append(message)

        viewmodel.error_occurred.connect(on_error)

        with patch.object(
            container,
            "create_unit_of_work",
            side_effect=Exception("Connection failed"),
        ):
            await viewmodel.load_developers()

        assert len(errors_received) == 1
        assert "Erro" in errors_received[0]

    @pytest.mark.asyncio
    async def test_save_with_developer_id(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test save in edit mode includes developer_id."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.set_story(sample_story_dto)
        viewmodel.developer_id = 42

        mock_story = StoryOutputDTO(
            id=sample_story_dto.id,
            component=sample_story_dto.component,
            name=sample_story_dto.name,
            story_points=sample_story_dto.story_points,
            priority=sample_story_dto.priority,
            status=sample_story_dto.status,
            duration=sample_story_dto.duration,
            start_date=sample_story_dto.start_date,
            end_date=sample_story_dto.end_date,
            developer_id=42,
            feature_id=sample_story_dto.feature_id,
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_story

        with patch.object(
            container, "create_edit_story_use_case", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is not None
        # Verify developer_id was passed in the DTO
        call_dto = mock_use_case.execute.call_args[0][0]
        assert call_dto.developer_id == 42

    @pytest.mark.asyncio
    async def test_save_without_developer(
        self, container: DIContainer, sample_story_dto: StoryOutputDTO, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test save in edit mode without developer."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.set_story(sample_story_dto)
        viewmodel.developer_id = None

        mock_story = StoryOutputDTO(
            id=sample_story_dto.id,
            component=sample_story_dto.component,
            name=sample_story_dto.name,
            story_points=sample_story_dto.story_points,
            priority=sample_story_dto.priority,
            status=sample_story_dto.status,
            duration=sample_story_dto.duration,
            start_date=sample_story_dto.start_date,
            end_date=sample_story_dto.end_date,
            developer_id=None,
            feature_id=sample_story_dto.feature_id,
        )
        mock_use_case = AsyncMock()
        mock_use_case.execute.return_value = mock_story

        with patch.object(
            container, "create_edit_story_use_case", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is not None
        call_dto = mock_use_case.execute.call_args[0][0]
        assert call_dto.developer_id is None


class TestStoryDialogViewModelValidateField:
    """Tests for validate_field method (US2)."""

    def test_validate_field_component_empty(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validate_field returns (False, 'Campo obrigatorio') for empty component."""
        viewmodel = StoryDialogViewModel(container)
        is_valid, msg = viewmodel.validate_field("component")
        assert is_valid is False
        assert msg == "Campo obrigatorio"

    def test_validate_field_component_too_long(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validate_field returns error for component > 50 chars."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "A" * 51
        is_valid, msg = viewmodel.validate_field("component")
        assert is_valid is False
        assert msg == "Maximo de 50 caracteres"

    def test_validate_field_component_valid(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validate_field returns (True, '') for valid component."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "API"
        is_valid, msg = viewmodel.validate_field("component")
        assert is_valid is True
        assert msg == ""

    def test_validate_field_name_empty(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validate_field returns (False, 'Campo obrigatorio') for empty name."""
        viewmodel = StoryDialogViewModel(container)
        is_valid, msg = viewmodel.validate_field("name")
        assert is_valid is False
        assert msg == "Campo obrigatorio"

    def test_validate_field_name_too_long(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validate_field returns error for name > 200 chars."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.name = "A" * 201
        is_valid, msg = viewmodel.validate_field("name")
        assert is_valid is False
        assert msg == "Maximo de 200 caracteres"

    def test_validate_field_name_valid(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validate_field returns (True, '') for valid name."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.name = "Test Story"
        is_valid, msg = viewmodel.validate_field("name")
        assert is_valid is True
        assert msg == ""

    def test_validate_field_unknown(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test validate_field returns (True, '') for unknown fields."""
        viewmodel = StoryDialogViewModel(container)
        is_valid, msg = viewmodel.validate_field("unknown_field")
        assert is_valid is True
        assert msg == ""

    def test_validate_global_still_works(
        self, container: DIContainer, qapp  # type: ignore[no-untyped-def]
    ) -> None:
        """Test existing validate() unchanged."""
        viewmodel = StoryDialogViewModel(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        is_valid, error = viewmodel.validate()
        assert is_valid is True
        assert error == ""
