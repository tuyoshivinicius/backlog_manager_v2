"""Unit tests for DeveloperService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest
from backlog_manager.domain.entities import Developer
from backlog_manager.domain.services.developer_service import DeveloperService


@pytest.fixture
def mock_developer_repo():
    """Create mock developer repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_all = AsyncMock(return_value=[])
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.count_all_by_developer = AsyncMock(return_value=0)
    return repo


@pytest.fixture
def developer_service(mock_developer_repo, mock_story_repo):
    """Create developer service with mock repositories."""
    return DeveloperService(mock_developer_repo, mock_story_repo)


class TestCreateDeveloper:
    """Tests for create_developer method."""

    def test_creates_developer_with_normalized_name(
        self, developer_service, mock_developer_repo
    ):
        """Should create developer with stripped name."""
        result = developer_service.create_developer("  Ana Silva  ")

        assert result.name == "Ana Silva"
        assert result.id is None

    async def test_raises_error_for_empty_name(
        self, developer_service, mock_developer_repo
    ):
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="vazio"):
            await developer_service.create_developer("   ")

    async def test_raises_error_for_name_exceeding_100_chars(
        self, developer_service, mock_developer_repo
    ):
        """Should raise ValueError for name exceeding 100 characters."""
        long_name = "A" * 101
        with pytest.raises(ValueError, match="100 caracteres"):
            await developer_service.create_developer(long_name)


class TestUpdateDeveloper:
    """Tests for update_developer method."""

    async def test_updates_existing_developer(
        self, developer_service, mock_developer_repo
    ):
        """Should return new Developer with updated name."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")

        result = await developer_service.update_developer(1, "  Ana Maria  ")

        assert result.id == 1
        assert result.name == "Ana Maria"

    async def test_raises_error_for_nonexistent_developer(
        self, developer_service, mock_developer_repo
    ):
        """Should raise ValueError for nonexistent developer."""
        mock_developer_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Desenvolvedor nao encontrado: 999"):
            await developer_service.update_developer(999, "Ana")

    async def test_raises_error_for_empty_name(
        self, developer_service, mock_developer_repo
    ):
        """Should raise ValueError for empty name."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")

        with pytest.raises(ValueError, match="vazio"):
            await developer_service.update_developer(1, "   ")


class TestDeleteDeveloper:
    """Tests for delete_developer method."""

    async def test_deletes_developer_and_returns_story_count(
        self, developer_service, mock_developer_repo, mock_story_repo
    ):
        """Should delete developer and return count of unassigned stories."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")
        mock_story_repo.count_all_by_developer.return_value = 5

        result = await developer_service.delete_developer(1)

        assert result == 5
        mock_developer_repo.delete.assert_called_once_with(1)

    async def test_returns_zero_when_no_stories_assigned(
        self, developer_service, mock_developer_repo, mock_story_repo
    ):
        """Should return 0 when developer has no stories."""
        mock_developer_repo.get_by_id.return_value = Developer(id=1, name="Ana")
        mock_story_repo.count_all_by_developer.return_value = 0

        result = await developer_service.delete_developer(1)

        assert result == 0

    async def test_raises_error_for_nonexistent_developer(
        self, developer_service, mock_developer_repo, mock_story_repo
    ):
        """Should raise ValueError for nonexistent developer."""
        mock_developer_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Desenvolvedor nao encontrado: 999"):
            await developer_service.delete_developer(999)

        mock_developer_repo.delete.assert_not_called()


class TestListDevelopers:
    """Tests for list_developers method."""

    async def test_returns_all_developers_from_repo(
        self, developer_service, mock_developer_repo
    ):
        """Should return all developers from repository."""
        developers = [
            Developer(id=1, name="Ana"),
            Developer(id=2, name="Bruno"),
        ]
        mock_developer_repo.get_all.return_value = developers

        result = await developer_service.list_developers()

        assert list(result) == developers
        mock_developer_repo.get_all.assert_called_once()

    async def test_returns_empty_list_when_no_developers(
        self, developer_service, mock_developer_repo
    ):
        """Should return empty list when no developers exist."""
        mock_developer_repo.get_all.return_value = []

        result = await developer_service.list_developers()

        assert list(result) == []
