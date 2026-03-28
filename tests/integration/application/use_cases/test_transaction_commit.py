"""Integration tests for use case transaction commit behavior."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backlog_manager.application.dto.developer import CreateDeveloperInputDTO
from backlog_manager.application.dto.feature import CreateFeatureInputDTO
from backlog_manager.application.use_cases.developer import CreateDeveloperUseCase
from backlog_manager.application.use_cases.feature import CreateFeatureUseCase
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactionCommit:
    """Tests verifying use case transaction commits on success."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_create_developer_commits_on_success(self, db_path: Path) -> None:
        """Verify CreateDeveloperUseCase commits transaction on success."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CreateDeveloperUseCase(uow)
            result = await use_case.execute(CreateDeveloperInputDTO(name="Ana Silva"))

        # Verify data persisted by reading in new connection
        async with SQLiteUnitOfWork(db_path) as uow:
            developer = await uow.developers.get_by_id(result.id)
            assert developer is not None
            assert developer.name == "Ana Silva"

    async def test_create_feature_commits_on_success(self, db_path: Path) -> None:
        """Verify CreateFeatureUseCase commits transaction on success."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CreateFeatureUseCase(uow)
            result = await use_case.execute(
                CreateFeatureInputDTO(name="Autenticacao", wave=1)
            )

        # Verify data persisted by reading in new connection
        async with SQLiteUnitOfWork(db_path) as uow:
            feature = await uow.features.get_by_id(result.id)
            assert feature is not None
            assert feature.name == "Autenticacao"
            assert feature.wave == 1

    async def test_multiple_operations_commit_together(self, db_path: Path) -> None:
        """Verify multiple operations in same UoW all commit together."""
        await init_database(db_path)

        async with SQLiteUnitOfWork(db_path) as uow:
            dev_uc = CreateDeveloperUseCase(uow)
            feat_uc = CreateFeatureUseCase(uow)

            dev = await dev_uc.execute(CreateDeveloperInputDTO(name="Carlos"))
            feat = await feat_uc.execute(
                CreateFeatureInputDTO(name="Dashboard", wave=2)
            )

        # Verify both persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            assert await uow.developers.get_by_id(dev.id) is not None
            assert await uow.features.get_by_id(feat.id) is not None
