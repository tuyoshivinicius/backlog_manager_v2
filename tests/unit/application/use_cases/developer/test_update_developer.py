"""Unit tests for UpdateDeveloperUseCase."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest

from backlog_manager.application.dto.developer import UpdateDeveloperInputDTO
from backlog_manager.application.use_cases.developer import UpdateDeveloperUseCase
from backlog_manager.domain.entities import Developer


@pytest.fixture
def mock_developer_repo():
    """Create mock developer repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.update = AsyncMock()
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
    return UpdateDeveloperUseCase(mock_uow)


class TestUpdateDeveloperUseCase:
    """Tests for UpdateDeveloperUseCase."""

    async def test_updates_developer_name(self, use_case, mock_developer_repo):
        """Should update developer name."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")

        input_dto = UpdateDeveloperInputDTO(developer_id=1, name="Ana Maria")

        result = await use_case.execute(input_dto)

        assert result.id == 1
        assert result.name == "Ana Maria"

    async def test_calls_repository_update(self, use_case, mock_developer_repo):
        """Should call repository update."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")

        input_dto = UpdateDeveloperInputDTO(developer_id=1, name="Ana Maria")

        await use_case.execute(input_dto)

        mock_developer_repo.update.assert_called_once()
        updated = mock_developer_repo.update.call_args[0][0]
        assert updated.id == 1
        assert updated.name == "Ana Maria"

    async def test_raises_error_for_nonexistent_developer(
        self, use_case, mock_developer_repo
    ):
        """Should raise ValueError for nonexistent developer."""
        mock_developer_repo.get_by_id.return_value = None

        input_dto = UpdateDeveloperInputDTO(developer_id=999, name="Ana")

        with pytest.raises(ValueError, match="Desenvolvedor nao encontrado: 999"):
            await use_case.execute(input_dto)

        mock_developer_repo.update.assert_not_called()

    async def test_normalizes_name_with_strip(self, use_case, mock_developer_repo):
        """Should strip whitespace from name."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")

        input_dto = UpdateDeveloperInputDTO(developer_id=1, name="  Bruno Costa  ")

        result = await use_case.execute(input_dto)

        assert result.name == "Bruno Costa"


class TestUpdateDeveloperInputDTOValidation:
    """Tests for UpdateDeveloperInputDTO validation."""

    def test_validates_empty_name(self):
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="vazio"):
            UpdateDeveloperInputDTO(developer_id=1, name="   ")

    def test_validates_name_length(self):
        """Should raise ValueError for name exceeding 100 chars."""
        long_name = "A" * 101
        with pytest.raises(ValueError, match="100 caracteres"):
            UpdateDeveloperInputDTO(developer_id=1, name=long_name)
