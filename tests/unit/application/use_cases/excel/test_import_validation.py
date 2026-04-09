"""Unit tests for Excel import validation scenarios (US2)."""

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
    ExcelFileCorruptedException,
    ExcelFileNotFoundException,
    ExcelMissingHeaderException,
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


class TestHeaderValidation:
    """Tests for Excel header validation (AC-US2-01)."""

    async def test_missing_required_header_raises_exception(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should raise ExcelMissingHeaderException when required header missing."""
        mock_excel_service.read_stories_from_file.side_effect = (
            ExcelMissingHeaderException("Coluna obrigatoria 'Nome' nao encontrada")
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelMissingHeaderException, match="Nome"):
            await use_case.execute(input_dto, 1)

    async def test_all_required_headers_present_succeeds(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should succeed when all required headers are present."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Test",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                }
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto, 1)

        assert result.success is True
        assert result.stories_imported == 1


class TestStoryPointValidation:
    """Tests for Story Point validation (AC-US2-02)."""

    async def test_invalid_sp_value_warns_and_skips(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should warn and skip row with invalid SP value (not 3, 5, 8, 13)."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "AUTH-001",
                    "Componente": "AUTH",
                    "Nome": "Invalid SP",
                    "SP": 7,  # Invalid
                    "Feature": "",
                    "Dependencias": "",
                }
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto, 1)

        assert result.stories_imported == 0
        assert any("Story Points invalido" in w for w in result.warnings)

    async def test_valid_sp_values_3_5_8_13_accepted(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should accept SP values 3, 5, 8, and 13."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "SP 3",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "B-001",
                    "Componente": "B",
                    "Nome": "SP 5",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "C-001",
                    "Componente": "C",
                    "Nome": "SP 8",
                    "SP": 8,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "D-001",
                    "Componente": "D",
                    "Nome": "SP 13",
                    "SP": 13,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto, 1)

        assert result.stories_imported == 4


class TestCycleDetection:
    """Tests for dependency cycle detection (AC-US2-03)."""

    async def test_direct_cycle_a_depends_on_b_depends_on_a(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should detect direct cycle: A -> B -> A."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "A",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "B-001",
                },
                {
                    "ID": "B-001",
                    "Componente": "B",
                    "Nome": "B",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "A-001",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelCycleDetectedException, match="Ciclo de dependencia"):
            await use_case.execute(input_dto, 1)

    async def test_indirect_cycle_a_b_c_a(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should detect indirect cycle: A -> B -> C -> A."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "A",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "B-001",
                },
                {
                    "ID": "B-001",
                    "Componente": "B",
                    "Nome": "B",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "C-001",
                },
                {
                    "ID": "C-001",
                    "Componente": "C",
                    "Nome": "C",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "A-001",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelCycleDetectedException):
            await use_case.execute(input_dto, 1)

    async def test_self_dependency_detected_as_cycle(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should detect self-dependency as cycle: A -> A."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "Self",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "A-001",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelCycleDetectedException):
            await use_case.execute(input_dto, 1)


class TestEmptyFieldsValidation:
    """Tests for empty/missing field validation (AC-US2-04)."""

    async def test_empty_nome_skips_row_with_warning(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should skip row with empty Nome field."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto, 1)

        assert result.stories_imported == 0
        assert any("Nome vazio" in w for w in result.warnings)

    async def test_empty_id_and_componente_skips_row(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should skip row when both ID and Componente are empty."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "",
                    "Componente": "",
                    "Nome": "Test",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto, 1)

        assert result.stories_imported == 0

    async def test_empty_id_with_valid_componente_generates_id(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should generate ID from Componente when ID is empty."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "",
                    "Componente": "AUTH",
                    "Nome": "Test",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )
        mock_story_repo.get_max_id_number.return_value = 0

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto, 1)

        assert result.stories_imported == 1
        # Verify ID was generated
        added_story = mock_story_repo.add.call_args[0][0]
        assert added_story.id == "AUTH-001"


class TestPartialSuccessImport:
    """Tests for partial success scenarios (AC-US2-05)."""

    async def test_valid_rows_imported_invalid_rows_warned(
        self, use_case, mock_excel_service, mock_story_repo, valid_excel_file
    ):
        """Should import valid rows and generate warnings for invalid ones."""
        mock_excel_service.read_stories_from_file.return_value = ExcelReadResult(
            rows=[
                {
                    "ID": "A-001",
                    "Componente": "A",
                    "Nome": "Valid 1",
                    "SP": 5,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "B-001",
                    "Componente": "B",
                    "Nome": "Invalid SP",
                    "SP": 7,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "C-001",
                    "Componente": "C",
                    "Nome": "",
                    "SP": 3,
                    "Feature": "",
                    "Dependencias": "",
                },
                {
                    "ID": "D-001",
                    "Componente": "D",
                    "Nome": "Valid 2",
                    "SP": 8,
                    "Feature": "",
                    "Dependencias": "",
                },
            ],
            warnings=[],
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)
        result = await use_case.execute(input_dto, 1)

        assert result.stories_imported == 2  # A-001 and D-001
        assert len(result.warnings) >= 2  # Warnings for B-001 and C-001
        assert result.success is True

    async def test_complete_failure_on_file_error(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should fail completely on file-level errors."""
        mock_excel_service.read_stories_from_file.side_effect = (
            ExcelFileCorruptedException("Arquivo invalido")
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelFileCorruptedException):
            await use_case.execute(input_dto, 1)


class TestFileValidation:
    """Tests for file-level validation."""

    async def test_nonexistent_file_raises_exception(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should raise ExcelFileNotFoundException for missing file."""
        mock_excel_service.read_stories_from_file.side_effect = (
            ExcelFileNotFoundException("Arquivo nao encontrado")
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelFileNotFoundException):
            await use_case.execute(input_dto, 1)

    async def test_corrupted_file_raises_exception(
        self, use_case, mock_excel_service, valid_excel_file
    ):
        """Should raise ExcelFileCorruptedException for corrupted file."""
        mock_excel_service.read_stories_from_file.side_effect = (
            ExcelFileCorruptedException("Arquivo corrompido")
        )

        input_dto = ImportExcelInputDTO(file_path=valid_excel_file)

        with pytest.raises(ExcelFileCorruptedException):
            await use_case.execute(input_dto, 1)
