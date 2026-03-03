"""Unit tests for FeatureService."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backlog_manager.domain.entities import Feature
from backlog_manager.domain.exceptions import DuplicateWaveException
from backlog_manager.domain.services.feature_service import FeatureService


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.get_by_id = AsyncMock(return_value=None)
    repo.get_by_wave = AsyncMock(return_value=None)
    repo.get_by_name = AsyncMock(return_value=None)
    repo.get_all = AsyncMock(return_value=[])
    repo.delete = AsyncMock()
    return repo


@pytest.fixture
def feature_service(mock_feature_repo):
    """Create feature service with mock repository."""
    return FeatureService(mock_feature_repo)


class TestCreateFeature:
    """Tests for create_feature method."""

    async def test_creates_feature_with_normalized_name(
        self, feature_service, mock_feature_repo
    ):
        """Should create feature with stripped name."""
        result = await feature_service.create_feature("  Autenticacao  ", wave=1)

        assert result.name == "Autenticacao"
        assert result.wave == 1
        assert result.id is None

    async def test_raises_error_for_wave_zero(self, feature_service, mock_feature_repo):
        """Should raise ValueError for wave = 0."""
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            await feature_service.create_feature("Auth", wave=0)

    async def test_raises_error_for_negative_wave(
        self, feature_service, mock_feature_repo
    ):
        """Should raise ValueError for negative wave."""
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            await feature_service.create_feature("Auth", wave=-1)

    async def test_raises_error_for_duplicate_wave(
        self, feature_service, mock_feature_repo
    ):
        """Should raise DuplicateWaveException for existing wave."""
        mock_feature_repo.get_by_wave.return_value = Feature(
            id=1, name="Dashboard", wave=1
        )

        with pytest.raises(DuplicateWaveException) as exc_info:
            await feature_service.create_feature("Auth", wave=1)

        assert exc_info.value.wave == 1
        assert exc_info.value.existing_feature_name == "Dashboard"

    async def test_raises_error_for_duplicate_name(
        self, feature_service, mock_feature_repo
    ):
        """Should raise ValueError for existing name."""
        mock_feature_repo.get_by_wave.return_value = None
        mock_feature_repo.get_by_name.return_value = Feature(id=1, name="Auth", wave=2)

        with pytest.raises(ValueError, match="Feature com nome 'Auth' ja existe"):
            await feature_service.create_feature("Auth", wave=1)

    async def test_raises_error_for_empty_name(
        self, feature_service, mock_feature_repo
    ):
        """Should raise ValueError for empty name."""
        with pytest.raises(ValueError, match="vazio"):
            await feature_service.create_feature("   ", wave=1)


class TestUpdateFeature:
    """Tests for update_feature method."""

    async def test_updates_existing_feature_name(
        self, feature_service, mock_feature_repo
    ):
        """Should return new Feature with updated name."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        result = await feature_service.update_feature(1, name="  Autenticacao  ")

        assert result.id == 1
        assert result.name == "Autenticacao"
        assert result.wave == 1

    async def test_updates_existing_feature_wave(
        self, feature_service, mock_feature_repo
    ):
        """Should return new Feature with updated wave."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        result = await feature_service.update_feature(1, wave=2)

        assert result.id == 1
        assert result.name == "Auth"
        assert result.wave == 2

    async def test_updates_both_name_and_wave(self, feature_service, mock_feature_repo):
        """Should update both name and wave."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        result = await feature_service.update_feature(1, name="Dashboard", wave=3)

        assert result.name == "Dashboard"
        assert result.wave == 3

    async def test_raises_error_for_nonexistent_feature(
        self, feature_service, mock_feature_repo
    ):
        """Should raise ValueError for nonexistent feature."""
        mock_feature_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Feature nao encontrada: 999"):
            await feature_service.update_feature(999, name="New")

    async def test_raises_error_for_duplicate_wave_in_other_feature(
        self, feature_service, mock_feature_repo
    ):
        """Should raise DuplicateWaveException for existing wave in another feature."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)
        mock_feature_repo.get_by_wave.return_value = Feature(
            id=2, name="Dashboard", wave=2
        )

        with pytest.raises(DuplicateWaveException) as exc_info:
            await feature_service.update_feature(1, wave=2)

        assert exc_info.value.wave == 2
        assert exc_info.value.existing_feature_name == "Dashboard"

    async def test_allows_same_wave_for_same_feature(
        self, feature_service, mock_feature_repo
    ):
        """Should allow keeping same wave for the feature."""
        existing = Feature(id=1, name="Auth", wave=1)
        mock_feature_repo.get_by_id.return_value = existing
        mock_feature_repo.get_by_wave.return_value = existing

        result = await feature_service.update_feature(1, wave=1)

        assert result.wave == 1

    async def test_raises_error_for_duplicate_name_in_other_feature(
        self, feature_service, mock_feature_repo
    ):
        """Should raise ValueError for existing name in different feature."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)
        mock_feature_repo.get_by_name.return_value = Feature(
            id=2, name="Dashboard", wave=2
        )

        with pytest.raises(ValueError, match="Feature com nome 'Dashboard' ja existe"):
            await feature_service.update_feature(1, name="Dashboard")

    async def test_allows_same_name_for_same_feature(
        self, feature_service, mock_feature_repo
    ):
        """Should allow keeping same name for the feature."""
        existing = Feature(id=1, name="Auth", wave=1)
        mock_feature_repo.get_by_id.return_value = existing
        mock_feature_repo.get_by_name.return_value = existing

        result = await feature_service.update_feature(1, name="Auth")

        assert result.name == "Auth"


class TestDeleteFeature:
    """Tests for delete_feature method."""

    async def test_deletes_feature_when_no_stories(
        self, feature_service, mock_feature_repo
    ):
        """Should delete feature when it has no stories."""
        mock_feature_repo.get_by_id.return_value = Feature(id=1, name="Auth", wave=1)

        await feature_service.delete_feature(1)

        mock_feature_repo.delete.assert_called_once_with(1)

    async def test_raises_error_for_nonexistent_feature(
        self, feature_service, mock_feature_repo
    ):
        """Should raise ValueError for nonexistent feature."""
        mock_feature_repo.get_by_id.return_value = None

        with pytest.raises(ValueError, match="Feature nao encontrada: 999"):
            await feature_service.delete_feature(999)

        mock_feature_repo.delete.assert_not_called()


class TestListFeatures:
    """Tests for list_features method."""

    async def test_returns_all_features_from_repo(
        self, feature_service, mock_feature_repo
    ):
        """Should return all features from repository."""
        features = [
            Feature(id=1, name="Auth", wave=1),
            Feature(id=2, name="Dashboard", wave=2),
        ]
        mock_feature_repo.get_all.return_value = features

        result = await feature_service.list_features()

        assert list(result) == features
        mock_feature_repo.get_all.assert_called_once()

    async def test_returns_empty_list_when_no_features(
        self, feature_service, mock_feature_repo
    ):
        """Should return empty list when no features exist."""
        mock_feature_repo.get_all.return_value = []

        result = await feature_service.list_features()

        assert list(result) == []
