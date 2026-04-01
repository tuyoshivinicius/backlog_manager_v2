"""Unit tests for ImportExcelUseCase."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.dto.excel.import_excel_dto import (
    ExcelReadResult,
    ImportExcelInputDTO,
)
from backlog_manager.application.exceptions.excel_exceptions import (
    ExcelCycleDetectedException,
)
from backlog_manager.application.use_cases.excel.import_excel_use_case import (
    ImportExcelUseCase,
)


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_max_id_number = AsyncMock(return_value=0)
    repo.get_max_priority = AsyncMock(return_value=0)
    repo.add = AsyncMock()
    repo.exists = AsyncMock(return_value=False)
    return repo


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.exists = AsyncMock(return_value=True)
    repo.get_by_name = AsyncMock(return_value=None)
    repo.add = AsyncMock(return_value=1)
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.get_all_dependencies = AsyncMock(return_value=[])
    repo.add = AsyncMock()
    repo.exists = AsyncMock(return_value=False)
    return repo


@pytest.fixture
def mock_uow(mock_story_repo, mock_feature_repo, mock_dependency_repo):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    type(uow).features = PropertyMock(return_value=mock_feature_repo)
    type(uow).dependencies = PropertyMock(return_value=mock_dependency_repo)
    return uow


@pytest.fixture
def mock_excel_service():
    """Create mock excel service."""
    service = MagicMock()
    service.read_stories_from_file = AsyncMock()
    return service


@pytest.fixture
def use_case(mock_uow, mock_excel_service):
    """Create use case with mock dependencies."""
    return ImportExcelUseCase(mock_uow, mock_excel_service)


@pytest.fixture
def valid_excel_file(tmp_path: Path) -> Path:
    """Create a dummy valid Excel file path."""
    file_path = tmp_path / "test.xlsx"
    file_path.touch()
    return file_path


class TestImportExcelUseCase:
    """Tests for ImportExcelUseCase."""

    async def test_import_valid_file_creates_all_stories(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should import all valid rows from file creating stories."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Login de usuario",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-002",
                    "Componente": "AUTH",
                    "Nome": "Logout de usuario",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 2
        assert result.success is True
        assert mock_story_repo.add.call_count == 2

    async def test_import_auto_generate_id_from_component(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should generate ID in COMPONENTE-NNN format when ID is empty."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "",
                    "Componente": "API",
                    "Nome": "Endpoint de health",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        mock_story_repo.get_max_id_number.return_value = 0

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 1
        # Check the story was created with generated ID
        added_story = mock_story_repo.add.call_args[0][0]
        assert added_story.id == "API-001"

    async def test_import_creates_feature_when_not_exists(
        self,
        use_case,
        mock_excel_service,
        mock_feature_repo,
        valid_excel_file,
    ):
        """Should create feature with wave=1 when feature doesn't exist."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Login",
                    "SP": 5,
                    "Feature": "Autenticacao",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        mock_feature_repo.get_by_name.return_value = None
        mock_feature_repo.add.return_value = 1
        mock_feature_repo.get_all.return_value = []

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.features_created == 1
        mock_feature_repo.add.assert_called_once()
        # Check feature was created with correct wave
        added_feature = mock_feature_repo.add.call_args[0][0]
        assert added_feature.name == "Autenticacao"
        assert added_feature.wave == 1

    async def test_import_creates_dependencies_in_second_pass(
        self,
        use_case,
        mock_excel_service,
        mock_story_repo,
        mock_dependency_repo,
        valid_excel_file,
    ):
        """Should create dependencies after all stories are created."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Login",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-002",
                    "Componente": "AUTH",
                    "Nome": "Logout",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "AUTH-001",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 2
        mock_dependency_repo.add.assert_called_once_with("AUTH-002", "AUTH-001")

    async def test_import_empty_file_returns_zero_counts(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should return empty result for empty file."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 0
        assert result.features_created == 0
        assert result.success is True
        assert len(result.warnings) > 0  # Should have "empty file" warning

    async def test_import_skip_existing_id_generates_warning(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should skip row when ID already exists in database and generate warning per FR-032."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Story that already exists",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-002",
                    "Componente": "AUTH",
                    "Nome": "New story",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        # AUTH-001 already exists, AUTH-002 does not
        mock_story_repo.exists.side_effect = [True, False]

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        # Only AUTH-002 should be imported
        assert result.stories_imported == 1
        assert result.success is True
        # Should have warning for existing ID
        assert any("AUTH-001" in w and "ja existe" in w for w in result.warnings)
        # Only one story added (AUTH-002)
        assert mock_story_repo.add.call_count == 1
        added_story = mock_story_repo.add.call_args[0][0]
        assert added_story.id == "AUTH-002"


class TestImportValidation:
    """Tests for import validation scenarios."""

    async def test_import_invalid_sp_generates_warning_skips_row(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should skip row with invalid SP and add warning."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Valid story",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-002",
                    "Componente": "AUTH",
                    "Nome": "Invalid SP story",
                    "SP": 7,  # Invalid SP
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 1
        assert any("Story Points invalido" in w for w in result.warnings)

    async def test_import_cycle_detection_raises_exception(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should detect cycle and raise exception when dependencies form cycle."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "Story A",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "B-001",
                },
                {
                    "ID": "B-001",
                    "Componente": "B",
                    "Nome": "Story B",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "A-001",  # Creates cycle A -> B -> A
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelCycleDetectedException, match="Ciclo de dependencia"):
            await use_case.execute(input_dto)

    async def test_import_missing_dependency_generates_warning(
        self,
        use_case,
        mock_excel_service,
        mock_story_repo,
        mock_dependency_repo,
        valid_excel_file,
    ):
        """Should warn and skip dependency when referenced ID doesn't exist."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Story with missing dep",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "NONEXISTENT-001",
                },
            ],
            warnings=[],
        )
        mock_story_repo.exists.return_value = False

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 1
        assert any("nao encontrada" in w for w in result.warnings)
        mock_dependency_repo.add.assert_not_called()

    async def test_import_partial_success_imports_valid_lines(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should import valid lines even when some have errors."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Valid story 1",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-002",
                    "Componente": "AUTH",
                    "Nome": "",  # Empty name - invalid
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-003",
                    "Componente": "AUTH",
                    "Nome": "Valid story 3",
                    "SP": 8,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 2  # Only valid stories
        assert len(result.warnings) >= 1  # Warning for invalid row


class TestProgressCallback:
    """Tests for progress callback functionality."""

    async def test_progress_callback_is_called(
        self, mock_uow, mock_excel_service, valid_excel_file
    ):
        """Should call progress callback during import."""
        progress_values = []

        def callback(percent: int) -> None:
            progress_values.append(percent)

        use_case = ImportExcelUseCase(mock_uow, mock_excel_service, callback)

        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Story 1",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        await use_case.execute(input_dto)

        assert len(progress_values) > 0
        assert 0 in progress_values
        assert 100 in progress_values


class TestDependencyParsing:
    """Tests for dependency string parsing."""

    async def test_parse_multiple_dependencies(
        self,
        use_case,
        mock_excel_service,
        mock_story_repo,
        mock_dependency_repo,
        valid_excel_file,
    ):
        """Should parse semicolon-separated dependency IDs."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "Story A",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "B-001",
                    "Componente": "B",
                    "Nome": "Story B",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "C-001",
                    "Componente": "C",
                    "Nome": "Story C depends on A and B",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "A-001;B-001",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 3
        assert mock_dependency_repo.add.call_count == 2


class TestLargeFileAndEdgeCases:
    """Tests for large file warning, truncation, and other edge cases."""

    async def test_large_file_warning_over_500_rows(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should add performance warning when file has more than 500 rows."""
        rows = [
            {
                "ID": f"X-{i:04d}",
                "Componente": "X",
                "Nome": f"Story {i}",
                "SP": 5,
                "Feature": "",
                "Dependencias": "",
            }
            for i in range(1, 502)
        ]
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=rows,
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert any("mais de 500" in w for w in result.warnings)

    async def test_name_exceeding_200_chars_is_truncated(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should truncate name longer than 200 characters and add warning."""
        long_name = "A" * 250
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": long_name,
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 1
        assert any("200 caracteres" in w for w in result.warnings)
        added_story = mock_story_repo.add.call_args[0][0]
        assert len(added_story.name) == 200

    async def test_non_integer_sp_skips_row(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should skip row when SP cannot be converted to int."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Story with bad SP",
                    "SP": "abc",
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 0
        assert any("Story Points invalido" in w for w in result.warnings)

    async def test_component_exceeding_50_chars_skips_row(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should skip row when component exceeds 50 characters (auto-ID generation)."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "",
                    "Componente": "C" * 51,
                    "Nome": "Story with long component",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 0

    async def test_exception_in_pass_one_adds_warning(
        self, mock_uow, mock_excel_service, valid_excel_file
    ):
        """Should catch exceptions during row processing and add warning."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Valid story",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        # Force an exception during story processing
        mock_uow.stories.exists = AsyncMock(side_effect=RuntimeError("DB error"))

        use_case = ImportExcelUseCase(mock_uow, mock_excel_service)
        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 0
        assert any("DB error" in w for w in result.warnings)

    async def test_exception_in_dependency_creation_adds_warning(
        self,
        mock_uow,
        mock_excel_service,
        valid_excel_file,
    ):
        """Should catch exceptions during dependency creation and add warning."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Base story",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-002",
                    "Componente": "AUTH",
                    "Nome": "Dependent story",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "AUTH-001",
                },
            ],
            warnings=[],
        )
        # exists check succeeds but add throws
        mock_uow.dependencies.exists = AsyncMock(return_value=False)
        mock_uow.dependencies.add = AsyncMock(
            side_effect=RuntimeError("Dep creation error")
        )

        use_case = ImportExcelUseCase(mock_uow, mock_excel_service)
        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 2
        assert any("Erro ao criar dependencia" in w for w in result.warnings)


class TestFeatureHandling:
    """Tests for feature cache and wave assignment."""

    async def test_feature_found_in_cache_reuses_id(
        self, mock_uow, mock_excel_service, valid_excel_file
    ):
        """Should reuse feature_id from cache when same feature appears twice."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Story 1",
                    "SP": 5,
                    "Feature": "SharedFeature",
                    "Dependencias": "",
                },
                {
                    "ID": "AUTH-002",
                    "Componente": "AUTH",
                    "Nome": "Story 2",
                    "SP": 3,
                    "Feature": "SharedFeature",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        mock_uow.features.get_by_name = AsyncMock(return_value=None)
        mock_uow.features.add = AsyncMock(return_value=42)
        mock_uow.features.get_all = AsyncMock(return_value=[])

        use_case = ImportExcelUseCase(mock_uow, mock_excel_service)
        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 2
        assert result.features_created == 1
        # Feature add should only be called once (second time uses cache)
        mock_uow.features.add.assert_called_once()

    async def test_feature_found_in_db_not_created(
        self, mock_uow, mock_excel_service, valid_excel_file
    ):
        """Should not create feature if it already exists in database."""
        from backlog_manager.domain.entities import Feature

        existing_feature = Feature(name="ExistingFeature", wave=1)
        object.__setattr__(existing_feature, "id", 99)

        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Story 1",
                    "SP": 5,
                    "Feature": "ExistingFeature",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        mock_uow.features.get_by_name = AsyncMock(return_value=existing_feature)

        use_case = ImportExcelUseCase(mock_uow, mock_excel_service)
        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.stories_imported == 1
        assert result.features_created == 0
        mock_uow.features.add.assert_not_called()

    async def test_feature_wave_increments_when_waves_taken(
        self, mock_uow, mock_excel_service, valid_excel_file
    ):
        """Should assign next available wave when existing waves are taken."""
        from backlog_manager.domain.entities import Feature

        existing_features = [
            Feature(name="F1", wave=1),
            Feature(name="F2", wave=2),
        ]

        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Story 1",
                    "SP": 5,
                    "Feature": "NewFeature",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        mock_uow.features.get_by_name = AsyncMock(return_value=None)
        mock_uow.features.add = AsyncMock(return_value=3)
        mock_uow.features.get_all = AsyncMock(return_value=existing_features)

        use_case = ImportExcelUseCase(mock_uow, mock_excel_service)
        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        assert result.features_created == 1
        added_feature = mock_uow.features.add.call_args[0][0]
        assert added_feature.wave == 3  # Next available after 1 and 2


class TestParsingEdgeCases:
    """Tests for parsing edge cases in dependencies."""

    async def test_empty_dep_id_after_split_is_ignored(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should ignore empty dependency IDs from trailing semicolons."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "Story A",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "B-001",
                    "Componente": "B",
                    "Nome": "Story B",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "A-001;  ;",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto)

        # Only one real dependency (A-001), empty parts should be ignored
        assert result.stories_imported == 2
