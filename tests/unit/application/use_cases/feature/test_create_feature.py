"""Unit tests for CreateFeatureUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.feature import CreateFeatureInputDTO
from backlog_manager.application.use_cases.feature import CreateFeatureUseCase
from backlog_manager.domain.entities import Feature
from backlog_manager.domain.exceptions import DuplicateWaveException


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.add = AsyncMock(return_value=1)
    repo.get_by_wave = AsyncMock(return_value=None)
    repo.get_by_name = AsyncMock(return_value=None)
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
    return CreateFeatureUseCase(mock_uow)


class TestCreateFeatureUseCase:
    """Tests for CreateFeatureUseCase."""

    async def test_creates_feature_with_generated_id(self, use_case, mock_feature_repo):
        """Should create feature with auto-generated ID."""
        mock_feature_repo.add.return_value = 42

        input_dto = CreateFeatureInputDTO(name="Autenticacao", wave=1)

        result = await use_case.execute(input_dto)

        assert result.id == 42
        assert result.name == "Autenticacao"
        assert result.wave == 1

    async def test_normalizes_name_with_strip(self, use_case, mock_feature_repo):
        """Should strip whitespace from name."""
        mock_feature_repo.add.return_value = 1

        input_dto = CreateFeatureInputDTO(name="  Dashboard  ", wave=2)

        result = await use_case.execute(input_dto)

        assert result.name == "Dashboard"

    async def test_raises_error_for_duplicate_wave(self, use_case, mock_feature_repo):
        """Should raise DuplicateWaveException for existing wave."""
        mock_feature_repo.get_by_wave.return_value = Feature(
            id=1, name="Existing", wave=1
        )

        input_dto = CreateFeatureInputDTO(name="New", wave=1)

        with pytest.raises(DuplicateWaveException) as exc_info:
            await use_case.execute(input_dto)

        assert exc_info.value.wave == 1
        assert exc_info.value.existing_feature_name == "Existing"

    async def test_raises_error_for_duplicate_name(self, use_case, mock_feature_repo):
        """Should raise ValueError for existing name."""
        mock_feature_repo.get_by_name.return_value = Feature(id=1, name="Auth", wave=2)

        input_dto = CreateFeatureInputDTO(name="Auth", wave=1)

        with pytest.raises(ValueError, match="Feature com nome 'Auth' ja existe"):
            await use_case.execute(input_dto)

    async def test_persists_feature(self, use_case, mock_feature_repo):
        """Should call repository add."""
        mock_feature_repo.add.return_value = 1

        input_dto = CreateFeatureInputDTO(name="Auth", wave=1)

        await use_case.execute(input_dto)

        mock_feature_repo.add.assert_called_once()


class TestCreateFeatureInputDTOValidation:
    """Tests for CreateFeatureInputDTO validation."""

    def test_validates_empty_name(self):
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="vazio"):
            CreateFeatureInputDTO(name="   ", wave=1)

    def test_validates_name_length(self):
        """Should raise ValueError for name exceeding 100 chars."""
        long_name = "A" * 101
        with pytest.raises(ValueError, match="100 caracteres"):
            CreateFeatureInputDTO(name=long_name, wave=1)

    def test_validates_wave_zero(self):
        """Should raise ValueError for wave = 0."""
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            CreateFeatureInputDTO(name="Auth", wave=0)

    def test_validates_negative_wave(self):
        """Should raise ValueError for negative wave."""
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            CreateFeatureInputDTO(name="Auth", wave=-1)
