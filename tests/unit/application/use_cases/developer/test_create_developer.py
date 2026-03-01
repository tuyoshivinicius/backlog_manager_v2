"""Unit tests for CreateDeveloperUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.developer import CreateDeveloperInputDTO
from backlog_manager.application.use_cases.developer import CreateDeveloperUseCase


@pytest.fixture
def mock_developer_repo():
    """Create mock developer repository."""
    repo = MagicMock()
    repo.add = AsyncMock(return_value=1)
    return repo


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.count_by_developer = AsyncMock(return_value=0)
    return repo


@pytest.fixture
def mock_uow(mock_developer_repo, mock_story_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).developers = PropertyMock(return_value=mock_developer_repo)
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    return uow


@pytest.fixture
def use_case(mock_uow):
    """Create use case with mock dependencies."""
    return CreateDeveloperUseCase(mock_uow)


class TestCreateDeveloperUseCase:
    """Tests for CreateDeveloperUseCase."""

    async def test_creates_developer_with_generated_id(
        self, use_case, mock_developer_repo
    ):
        """Should create developer with auto-generated ID."""
        mock_developer_repo.add.return_value = 42

        input_dto = CreateDeveloperInputDTO(name="Ana Silva")

        result = await use_case.execute(input_dto)

        assert result.id == 42
        assert result.name == "Ana Silva"

    async def test_normalizes_name_with_strip(self, use_case, mock_developer_repo):
        """Should strip whitespace from name."""
        mock_developer_repo.add.return_value = 1

        input_dto = CreateDeveloperInputDTO(name="  Bruno Costa  ")

        result = await use_case.execute(input_dto)

        assert result.name == "Bruno Costa"

    async def test_persists_developer(self, use_case, mock_developer_repo):
        """Should call repository add."""
        mock_developer_repo.add.return_value = 1

        input_dto = CreateDeveloperInputDTO(name="Ana")

        await use_case.execute(input_dto)

        mock_developer_repo.add.assert_called_once()
        added_developer = mock_developer_repo.add.call_args[0][0]
        assert added_developer.name == "Ana"

    async def test_returns_developer_output_dto(self, use_case, mock_developer_repo):
        """Should return DeveloperOutputDTO with all fields."""
        mock_developer_repo.add.return_value = 1

        input_dto = CreateDeveloperInputDTO(name="Ana Silva")

        result = await use_case.execute(input_dto)

        assert hasattr(result, "id")
        assert hasattr(result, "name")
        assert result.id == 1
        assert result.name == "Ana Silva"


class TestCreateDeveloperInputDTOValidation:
    """Tests for CreateDeveloperInputDTO validation."""

    def test_validates_empty_name(self):
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="vazio"):
            CreateDeveloperInputDTO(name="   ")

    def test_validates_name_length(self):
        """Should raise ValueError for name exceeding 100 chars."""
        long_name = "A" * 101
        with pytest.raises(ValueError, match="100 caracteres"):
            CreateDeveloperInputDTO(name=long_name)

    def test_accepts_valid_name(self):
        """Should accept valid name."""
        dto = CreateDeveloperInputDTO(name="Ana Silva")
        assert dto.name == "Ana Silva"

    def test_strips_whitespace(self):
        """Should strip whitespace from name."""
        dto = CreateDeveloperInputDTO(name="  Ana Silva  ")
        assert dto.name == "Ana Silva"
