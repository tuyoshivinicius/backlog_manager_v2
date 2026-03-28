"""Integration tests for use case transaction rollback behavior."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest

from backlog_manager.application.dto.feature import CreateFeatureInputDTO
from backlog_manager.application.use_cases.feature import CreateFeatureUseCase
from backlog_manager.domain.exceptions import DuplicateWaveException
from backlog_manager.infrastructure.database import SQLiteUnitOfWork, init_database


@pytest.mark.integration
@pytest.mark.asyncio
class TestTransactionRollback:
    """Tests verifying use case transaction rollback on errors."""

    @pytest.fixture
    def db_path(self):
        """Create a temporary database path."""
        with tempfile.TemporaryDirectory() as tmp_dir:
            yield Path(tmp_dir) / "test.db"

    async def test_create_feature_rollback_on_duplicate_wave(
        self, db_path: Path
    ) -> None:
        """Verify CreateFeatureUseCase rollback on DuplicateWaveException."""
        await init_database(db_path)

        # Create first feature successfully
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CreateFeatureUseCase(uow)
            await use_case.execute(CreateFeatureInputDTO(name="Auth", wave=1))

        # Attempt to create feature with duplicate wave - should rollback
        with pytest.raises(DuplicateWaveException):
            async with SQLiteUnitOfWork(db_path) as uow:
                use_case = CreateFeatureUseCase(uow)
                await use_case.execute(CreateFeatureInputDTO(name="Dashboard", wave=1))

        # Verify no partial data committed (only original feature exists)
        async with SQLiteUnitOfWork(db_path) as uow:
            features = await uow.features.get_all()
            assert len(features) == 1
            assert features[0].name == "Auth"

    async def test_create_feature_rollback_on_duplicate_name(
        self, db_path: Path
    ) -> None:
        """Verify CreateFeatureUseCase rollback on duplicate name ValueError."""
        await init_database(db_path)

        # Create first feature successfully
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CreateFeatureUseCase(uow)
            await use_case.execute(CreateFeatureInputDTO(name="Auth", wave=1))

        # Attempt to create feature with duplicate name - should rollback
        with pytest.raises(ValueError, match="ja existe"):
            async with SQLiteUnitOfWork(db_path) as uow:
                use_case = CreateFeatureUseCase(uow)
                await use_case.execute(CreateFeatureInputDTO(name="Auth", wave=2))

        # Verify only original feature exists
        async with SQLiteUnitOfWork(db_path) as uow:
            features = await uow.features.get_all()
            assert len(features) == 1
            assert features[0].wave == 1

    async def test_validation_error_does_not_affect_database(
        self, db_path: Path
    ) -> None:
        """Verify validation errors before DB operation don't corrupt state."""
        await init_database(db_path)

        # Create a valid feature first
        async with SQLiteUnitOfWork(db_path) as uow:
            use_case = CreateFeatureUseCase(uow)
            await use_case.execute(CreateFeatureInputDTO(name="Auth", wave=1))

        # DTO validation error (wave=0 is invalid) should not affect DB
        with pytest.raises(ValueError, match="Wave deve ser > 0"):
            CreateFeatureInputDTO(name="Dashboard", wave=0)

        # Verify original data intact
        async with SQLiteUnitOfWork(db_path) as uow:
            features = await uow.features.get_all()
            assert len(features) == 1
            assert features[0].name == "Auth"

    async def test_exception_in_use_case_rolls_back_context_manager(
        self, db_path: Path
    ) -> None:
        """Verify context manager properly rolls back on exception."""
        await init_database(db_path)

        # Count features before
        async with SQLiteUnitOfWork(db_path) as uow:
            initial_count = len(await uow.features.get_all())
            assert initial_count == 0

        # Create with duplicate - UoW context should rollback
        with pytest.raises(DuplicateWaveException):
            async with SQLiteUnitOfWork(db_path) as uow:
                # First add succeeds
                await uow.features.add(
                    __import__(
                        "backlog_manager.domain.entities", fromlist=["Feature"]
                    ).Feature(name="F1", wave=1)
                )
                # Second add fails - whole transaction should rollback
                await uow.features.add(
                    __import__(
                        "backlog_manager.domain.entities", fromlist=["Feature"]
                    ).Feature(name="F2", wave=1)
                )

        # Verify nothing persisted
        async with SQLiteUnitOfWork(db_path) as uow:
            features = await uow.features.get_all()
            assert len(features) == 0
