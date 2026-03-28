"""Unit tests for UpdateFeatureUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.feature import UpdateFeatureInputDTO
from backlog_manager.application.use_cases.feature import UpdateFeatureUseCase
from backlog_manager.domain.entities import Feature
from backlog_manager.domain.exceptions import DuplicateWaveException


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_wave = AsyncMock(return_value=None)
    repo.get_by_name = AsyncMock(return_value=None)
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_uow(mock_feature_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).features = PropertyMock(return_value=mock_feature_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return UpdateFeatureUseCase(mock_uow)


class TestUpdateFeatureUseCase:
    """Tests for UpdateFeatureUseCase."""

    async def test_updates_feature_name(self, use_case, mock_feature_repo):
        """Should update feature name."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        input_dto = UpdateFeatureInputDTO(feature_id=1, name="Authentication")

        result = await use_case.execute(input_dto)

        assert result.id == 1
        assert result.name == "Authentication"
        assert result.wave == 1

    async def test_updates_feature_wave(self, use_case, mock_feature_repo):
        """Should update feature wave."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        input_dto = UpdateFeatureInputDTO(feature_id=1, wave=2)

        result = await use_case.execute(input_dto)

        assert result.wave == 2

    async def test_updates_both_name_and_wave(self, use_case, mock_feature_repo):
        """Should update both name and wave."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        input_dto = UpdateFeatureInputDTO(feature_id=1, name="Dashboard", wave=3)

        result = await use_case.execute(input_dto)

        assert result.name == "Dashboard"
        assert result.wave == 3

    async def test_calls_repository_update(self, use_case, mock_feature_repo):
        """Should call repository update."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        input_dto = UpdateFeatureInputDTO(feature_id=1, name="New Name")

        await use_case.execute(input_dto)

        mock_feature_repo.update.assert_called_once()

    async def test_raises_error_for_nonexistent_feature(
        self, use_case, mock_feature_repo
    ):
        """Should raise ValueError for nonexistent feature."""
        mock_feature_repo.get_by_id.return_value = None

        input_dto = UpdateFeatureInputDTO(feature_id=999, name="Auth")

        with pytest.raises(ValueError, match="Feature nao encontrada: 999"):
            await use_case.execute(input_dto)

    async def test_raises_error_for_duplicate_wave(self, use_case, mock_feature_repo):
        """Should raise DuplicateWaveException for existing wave in other feature."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)
        mock_feature_repo.get_by_wave.return_value = Feature(
            id=2, name="Dashboard", wave=2
        )

        input_dto = UpdateFeatureInputDTO(feature_id=1, wave=2)

        with pytest.raises(DuplicateWaveException):
            await use_case.execute(input_dto)


class TestUpdateFeatureInputDTOValidation:
    """Tests for UpdateFeatureInputDTO validation."""

    def test_validates_empty_name(self):
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="vazio"):
            UpdateFeatureInputDTO(feature_id=1, name="   ")

    def test_allows_none_name(self):
        """Should allow None name for partial update."""
        dto = UpdateFeatureInputDTO(feature_id=1, name=None, wave=2)
        assert dto.name is None

    def test_validates_wave_zero(self):
        """Should raise ValueError for wave = 0."""
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            UpdateFeatureInputDTO(feature_id=1, wave=0)

    def test_allows_none_wave(self):
        """Should allow None wave for partial update."""
        dto = UpdateFeatureInputDTO(feature_id=1, name="Auth", wave=None)
        assert dto.wave is None
