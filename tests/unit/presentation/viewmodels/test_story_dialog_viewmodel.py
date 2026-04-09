"""Headless tests for StoryDialogViewModel."""

from __future__ import annotations

from datetime import date
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    from backlog_manager.application.dto.developer import DeveloperOutputDTO
    from backlog_manager.application.dto.feature import FeatureOutputDTO
    from backlog_manager.application.dto.story import StoryOutputDTO
    from backlog_manager.domain.exceptions import BacklogManagerException
    from backlog_manager.presentation.viewmodels.story_dialog_viewmodel import (
        VALID_STORY_POINTS,
        StoryDialogViewModel,
    )


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def container() -> MagicMock:
    """Return a mock DI container."""
    mock = MagicMock()
    # create_unit_of_work returns an async context manager
    mock_uow = AsyncMock()
    mock.create_unit_of_work.return_value = mock_uow
    mock.main_window_viewmodel.active_planning_id = 1
    return mock


@pytest.fixture()
def sample_story_dto() -> StoryOutputDTO:
    """Return a sample StoryOutputDTO for edit-mode tests."""
    return StoryOutputDTO(
        planning_id=1,
        id="COMP-001",
        component="COMP",
        name="Sample Story",
        story_points=5,
        priority=1,
        status="BACKLOG",
        duration=3,
        start_date=date(2026, 1, 15),
        end_date=date(2026, 1, 17),
        developer_id=1,
        feature_id=1,
    )


def _make_vm(container: MagicMock) -> StoryDialogViewModel:
    return StoryDialogViewModel(container)


# ===========================================================================
# Initialization
# ===========================================================================


class TestStoryDialogViewModelInitialization:
    """Tests for StoryDialogViewModel initialization."""

    def test_initial_state(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        assert viewmodel.mode == "create"
        assert viewmodel.story_id is None
        assert viewmodel.component == ""
        assert viewmodel.name == ""
        assert viewmodel.story_points == 5
        assert viewmodel.feature_id is None
        assert viewmodel.features == []

    def test_has_required_signals(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        assert hasattr(viewmodel, "saved")
        assert hasattr(viewmodel, "error_occurred")
        assert hasattr(viewmodel, "features_loaded")


# ===========================================================================
# Properties
# ===========================================================================


class TestStoryDialogViewModelProperties:
    """Tests for StoryDialogViewModel properties."""

    def test_component_setter_strips_and_uppercases(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "  api  "
        assert viewmodel.component == "API"

    def test_name_setter_strips_whitespace(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.name = "  Test Story  "
        assert viewmodel.name == "Test Story"

    def test_story_points_setter_valid(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        for sp in VALID_STORY_POINTS:
            viewmodel.story_points = sp
            assert viewmodel.story_points == sp

    def test_story_points_setter_invalid_ignored(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.story_points = 5
        viewmodel.story_points = 7  # Invalid
        assert viewmodel.story_points == 5

    def test_feature_id_setter(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.feature_id = 42
        assert viewmodel.feature_id == 42

    def test_feature_id_can_be_none(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.feature_id = 42
        viewmodel.feature_id = None
        assert viewmodel.feature_id is None

    def test_features_returns_copy(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        features1 = viewmodel.features
        features2 = viewmodel.features
        assert features1 is not features2


# ===========================================================================
# Mode management
# ===========================================================================


class TestStoryDialogViewModelMode:
    """Tests for mode management."""

    def test_set_mode_to_create(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel.set_mode("create")
        assert viewmodel.mode == "create"
        assert viewmodel.component == ""
        assert viewmodel.name == ""

    def test_set_mode_to_edit(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_mode("edit")
        assert viewmodel.mode == "edit"

    def test_set_story_populates_form(
        self, container: MagicMock, sample_story_dto: StoryOutputDTO
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_story(sample_story_dto)
        assert viewmodel.mode == "edit"
        assert viewmodel.story_id == sample_story_dto.id
        assert viewmodel.component == sample_story_dto.component
        assert viewmodel.name == sample_story_dto.name
        assert viewmodel.story_points == sample_story_dto.story_points
        assert viewmodel.feature_id == sample_story_dto.feature_id


# ===========================================================================
# Validation
# ===========================================================================


class TestStoryDialogViewModelValidation:
    """Tests for form validation."""

    def test_validate_empty_component(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.name = "Test Story"
        is_valid, error = viewmodel.validate()
        assert is_valid is False
        assert "Componente" in error

    def test_validate_component_too_long(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "A" * 51
        viewmodel.name = "Test Story"
        is_valid, error = viewmodel.validate()
        assert is_valid is False
        assert "50" in error

    def test_validate_empty_name(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        is_valid, error = viewmodel.validate()
        assert is_valid is False
        assert "Nome" in error

    def test_validate_name_too_long(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "A" * 201
        is_valid, error = viewmodel.validate()
        assert is_valid is False
        assert "200" in error

    def test_validate_invalid_story_points(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel._story_points = 7  # Force invalid value
        is_valid, error = viewmodel.validate()
        assert is_valid is False
        assert "Story Points" in error

    def test_validate_success(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel.story_points = 5
        is_valid, error = viewmodel.validate()
        assert is_valid is True
        assert error == ""


# ===========================================================================
# Load features
# ===========================================================================


class TestStoryDialogViewModelLoadFeatures:
    """Tests for loading features."""

    @pytest.mark.asyncio
    async def test_load_features_success(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)

        mock_features = [
            FeatureOutputDTO(id=1, name="Feature 1", wave=1),
            FeatureOutputDTO(id=2, name="Feature 2", wave=2),
        ]

        mock_use_case = AsyncMock()
        mock_result = MagicMock()
        mock_result.features = mock_features
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container, "create_list_features_use_case", return_value=mock_use_case
        ):
            await viewmodel.load_features()

        assert len(viewmodel.features) == 2
        assert len(viewmodel.features_loaded.emissions) == 1

    @pytest.mark.asyncio
    async def test_load_features_error_emits_signal(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)

        with patch.object(
            container,
            "create_unit_of_work",
            side_effect=Exception("Connection failed"),
        ):
            await viewmodel.load_features()

        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Erro" in viewmodel.error_occurred.emissions[0][0]


# ===========================================================================
# Save
# ===========================================================================


class TestStoryDialogViewModelSave:
    """Tests for saving stories."""

    @pytest.mark.asyncio
    async def test_save_validation_error_emits_signal(
        self, container: MagicMock
    ) -> None:
        viewmodel = _make_vm(container)
        # Empty component -> invalid
        result = await viewmodel.save()
        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Componente" in viewmodel.error_occurred.emissions[0][0]

    @pytest.mark.asyncio
    async def test_save_create_success(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        viewmodel.story_points = 5

        mock_story = StoryOutputDTO(
            planning_id=1,
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
        assert len(viewmodel.saved.emissions) == 1

    @pytest.mark.asyncio
    async def test_save_edit_success(
        self, container: MagicMock, sample_story_dto: StoryOutputDTO
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_story(sample_story_dto)
        viewmodel.name = "Updated Story"

        mock_story = StoryOutputDTO(
            planning_id=1,
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
        assert len(viewmodel.saved.emissions) == 1

    @pytest.mark.asyncio
    async def test_save_backlog_manager_exception_emits_error(
        self, container: MagicMock
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = BacklogManagerException(
            "Historia duplicada"
        )

        with patch.object(
            container, "create_story_use_case_factory", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Historia duplicada" in viewmodel.error_occurred.emissions[0][0]

    @pytest.mark.asyncio
    async def test_save_unexpected_exception_emits_error(
        self, container: MagicMock
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"

        mock_use_case = AsyncMock()
        mock_use_case.execute.side_effect = RuntimeError("Unexpected error")

        with patch.object(
            container, "create_story_use_case_factory", return_value=mock_use_case
        ):
            result = await viewmodel.save()

        assert result is None
        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Erro inesperado" in viewmodel.error_occurred.emissions[0][0]


# ===========================================================================
# Developer ID
# ===========================================================================


class TestStoryDialogViewModelDeveloperId:
    """Tests for developer_id property and load_developers (US1)."""

    def test_developer_id_property_get_set(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.developer_id = 42
        assert viewmodel.developer_id == 42
        viewmodel.developer_id = None
        assert viewmodel.developer_id is None

    def test_developer_id_initial_none(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        assert viewmodel.developer_id is None

    def test_set_story_loads_developer_id(
        self, container: MagicMock, sample_story_dto: StoryOutputDTO
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_story(sample_story_dto)
        assert viewmodel.developer_id == sample_story_dto.developer_id

    @pytest.mark.asyncio
    async def test_load_developers_returns_list(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)

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
        assert len(viewmodel.developers_loaded.emissions) == 1

    @pytest.mark.asyncio
    async def test_load_developers_includes_none_option(
        self, container: MagicMock
    ) -> None:
        viewmodel = _make_vm(container)

        mock_developers = [DeveloperOutputDTO(id=1, name="Dev 1")]

        mock_use_case = AsyncMock()
        mock_result = MagicMock()
        mock_result.developers = mock_developers
        mock_use_case.execute.return_value = mock_result

        with patch.object(
            container, "create_list_developers_use_case", return_value=mock_use_case
        ):
            await viewmodel.load_developers()

        assert len(viewmodel.developers) == 1
        assert viewmodel.developer_id is None

    @pytest.mark.asyncio
    async def test_load_developers_error_emits_signal(
        self, container: MagicMock
    ) -> None:
        viewmodel = _make_vm(container)

        with patch.object(
            container,
            "create_unit_of_work",
            side_effect=Exception("Connection failed"),
        ):
            await viewmodel.load_developers()

        assert len(viewmodel.error_occurred.emissions) == 1
        assert "Erro" in viewmodel.error_occurred.emissions[0][0]

    @pytest.mark.asyncio
    async def test_save_with_developer_id(
        self, container: MagicMock, sample_story_dto: StoryOutputDTO
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_story(sample_story_dto)
        viewmodel.developer_id = 42

        mock_story = StoryOutputDTO(
            planning_id=1,
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
        call_dto = mock_use_case.execute.call_args[0][1]
        assert call_dto.developer_id == 42

    @pytest.mark.asyncio
    async def test_save_without_developer(
        self, container: MagicMock, sample_story_dto: StoryOutputDTO
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_story(sample_story_dto)
        viewmodel.developer_id = None

        mock_story = StoryOutputDTO(
            planning_id=1,
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
        call_dto = mock_use_case.execute.call_args[0][1]
        assert call_dto.developer_id is None


# ===========================================================================
# Status
# ===========================================================================


class TestStoryDialogViewModelStatus:
    """Tests for status property and edit flow."""

    def test_status_property_get_set(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.status = "CONCLUIDO"
        assert viewmodel.status == "CONCLUIDO"

    def test_status_initial_backlog(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        assert viewmodel.status == "BACKLOG"

    def test_set_story_loads_status(
        self, container: MagicMock, sample_story_dto: StoryOutputDTO
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_story(sample_story_dto)
        assert viewmodel.status == sample_story_dto.status

    def test_reset_form_resets_status(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.status = "CONCLUIDO"
        viewmodel.set_mode("create")
        assert viewmodel.status == "BACKLOG"

    @pytest.mark.asyncio
    async def test_save_with_status(
        self, container: MagicMock, sample_story_dto: StoryOutputDTO
    ) -> None:
        viewmodel = _make_vm(container)
        viewmodel.set_story(sample_story_dto)
        viewmodel.status = "CONCLUIDO"

        mock_story = StoryOutputDTO(
            planning_id=1,
            id=sample_story_dto.id,
            component=sample_story_dto.component,
            name=sample_story_dto.name,
            story_points=sample_story_dto.story_points,
            priority=sample_story_dto.priority,
            status="CONCLUIDO",
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
        call_dto = mock_use_case.execute.call_args[0][1]
        assert call_dto.status == "CONCLUIDO"


# ===========================================================================
# validate_field
# ===========================================================================


class TestStoryDialogViewModelValidateField:
    """Tests for validate_field method (US2)."""

    def test_validate_field_component_empty(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        is_valid, msg = viewmodel.validate_field("component")
        assert is_valid is False
        assert msg == "Campo obrigatorio"

    def test_validate_field_component_too_long(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "A" * 51
        is_valid, msg = viewmodel.validate_field("component")
        assert is_valid is False
        assert msg == "Maximo de 50 caracteres"

    def test_validate_field_component_valid(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "API"
        is_valid, msg = viewmodel.validate_field("component")
        assert is_valid is True
        assert msg == ""

    def test_validate_field_name_empty(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        is_valid, msg = viewmodel.validate_field("name")
        assert is_valid is False
        assert msg == "Campo obrigatorio"

    def test_validate_field_name_too_long(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.name = "A" * 201
        is_valid, msg = viewmodel.validate_field("name")
        assert is_valid is False
        assert msg == "Maximo de 200 caracteres"

    def test_validate_field_name_valid(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.name = "Test Story"
        is_valid, msg = viewmodel.validate_field("name")
        assert is_valid is True
        assert msg == ""

    def test_validate_field_unknown(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        is_valid, msg = viewmodel.validate_field("unknown_field")
        assert is_valid is True
        assert msg == ""

    def test_validate_global_still_works(self, container: MagicMock) -> None:
        viewmodel = _make_vm(container)
        viewmodel.component = "TEST"
        viewmodel.name = "Test Story"
        is_valid, error = viewmodel.validate()
        assert is_valid is True
        assert error == ""
