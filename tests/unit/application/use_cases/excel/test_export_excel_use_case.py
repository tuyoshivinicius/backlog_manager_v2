"""Unit tests for ExportExcelUseCase."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, PropertyMock

import pytest
from backlog_manager.application.dto.excel.export_excel_dto import ExportExcelInputDTO
from backlog_manager.application.use_cases.excel.export_excel_use_case import (
    ExportExcelUseCase,
)
from backlog_manager.domain.entities import Developer, Feature, Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


@pytest.fixture
def mock_story_repo():
    """Create mock story repository."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_developer_repo():
    """Create mock developer repository."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_feature_repo():
    """Create mock feature repository."""
    repo = MagicMock()
    repo.get_all = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_dependency_repo():
    """Create mock dependency repository."""
    repo = MagicMock()
    repo.get_dependencies = AsyncMock(return_value=[])
    return repo


@pytest.fixture
def mock_uow(
    mock_story_repo, mock_developer_repo, mock_feature_repo, mock_dependency_repo
):
    """Create mock unit of work."""
    uow = MagicMock()
    type(uow).stories = PropertyMock(return_value=mock_story_repo)
    type(uow).developers = PropertyMock(return_value=mock_developer_repo)
    type(uow).features = PropertyMock(return_value=mock_feature_repo)
    type(uow).dependencies = PropertyMock(return_value=mock_dependency_repo)
    return uow


@pytest.fixture
def mock_excel_service():
    """Create mock excel service."""
    service = MagicMock()
    service.write_workbook = AsyncMock()
    return service


@pytest.fixture
def use_case(mock_uow, mock_excel_service):
    """Create use case with mock dependencies."""
    return ExportExcelUseCase(mock_uow, mock_excel_service)


@pytest.fixture
def sample_stories():
    """Create sample stories for testing."""
    return [
        Story(
            id="AUTH-001",
            component="AUTH",
            name="Login de usuario",
            story_points=StoryPoint(5),
            priority=1,
            status=StoryStatus.BACKLOG,
            developer_id=1,
            feature_id=1,
        ),
        Story(
            id="AUTH-002",
            component="AUTH",
            name="Logout de usuario",
            story_points=StoryPoint(3),
            priority=2,
            status=StoryStatus.EXECUCAO,
            developer_id=None,
            feature_id=1,
        ),
    ]


@pytest.fixture
def sample_developers():
    """Create sample developers for testing."""
    return [
        Developer(id=1, name="Joao"),
        Developer(id=2, name="Maria"),
    ]


@pytest.fixture
def sample_features():
    """Create sample features for testing."""
    return [
        Feature(id=1, name="Autenticacao", wave=1),
        Feature(id=2, name="API", wave=2),
    ]


class TestExportExcelUseCase:
    """Tests for ExportExcelUseCase."""

    async def test_export_creates_file_with_all_data(
        self,
        use_case,
        mock_story_repo,
        mock_developer_repo,
        mock_feature_repo,
        mock_excel_service,
        sample_stories,
        sample_developers,
        sample_features,
        tmp_path: Path,
    ):
        """Should export all stories, developers, and features to file."""
        mock_story_repo.get_all.return_value = sample_stories
        mock_developer_repo.get_all.return_value = sample_developers
        mock_feature_repo.get_all.return_value = sample_features

        file_path = tmp_path / "export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        result = await use_case.execute(input_dto)

        assert result.stories_exported == 2
        assert result.developers_exported == 2
        assert result.features_exported == 2
        assert result.file_path == file_path
        mock_excel_service.write_workbook.assert_called_once()

    async def test_export_empty_database_creates_empty_file(
        self,
        use_case,
        mock_excel_service,
        tmp_path: Path,
    ):
        """Should create file with empty data when database is empty."""
        file_path = tmp_path / "empty_export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        result = await use_case.execute(input_dto)

        assert result.stories_exported == 0
        assert result.developers_exported == 0
        assert result.features_exported == 0
        mock_excel_service.write_workbook.assert_called_once()

    async def test_export_includes_dependencies_in_stories(
        self,
        use_case,
        mock_story_repo,
        mock_dependency_repo,
        mock_excel_service,
        sample_stories,
        tmp_path: Path,
    ):
        """Should include dependency IDs separated by semicolon."""
        mock_story_repo.get_all.return_value = sample_stories
        mock_dependency_repo.get_dependencies.side_effect = [
            ["DB-001", "API-001"],  # AUTH-001 depends on these
            [],  # AUTH-002 has no dependencies
        ]

        file_path = tmp_path / "deps_export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        await use_case.execute(input_dto)

        # Check the data passed to write_workbook
        call_args = mock_excel_service.write_workbook.call_args
        export_data = call_args[0][1]

        # First story should have dependencies
        assert export_data.stories[0]["Dependencias"] == "DB-001;API-001"
        # Second story should have empty dependencies
        assert export_data.stories[1]["Dependencias"] == ""

    async def test_export_includes_developer_names(
        self,
        use_case,
        mock_story_repo,
        mock_developer_repo,
        mock_excel_service,
        sample_stories,
        sample_developers,
        tmp_path: Path,
    ):
        """Should include developer name for each story."""
        mock_story_repo.get_all.return_value = sample_stories
        mock_developer_repo.get_all.return_value = sample_developers

        file_path = tmp_path / "devs_export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        await use_case.execute(input_dto)

        call_args = mock_excel_service.write_workbook.call_args
        export_data = call_args[0][1]

        # First story has developer_id=1 (Joao)
        assert export_data.stories[0]["Desenvolvedor"] == "Joao"
        # Second story has no developer
        assert export_data.stories[1]["Desenvolvedor"] == ""

    async def test_export_includes_feature_names(
        self,
        use_case,
        mock_story_repo,
        mock_feature_repo,
        mock_excel_service,
        sample_stories,
        sample_features,
        tmp_path: Path,
    ):
        """Should include feature name for each story."""
        mock_story_repo.get_all.return_value = sample_stories
        mock_feature_repo.get_all.return_value = sample_features

        file_path = tmp_path / "features_export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        await use_case.execute(input_dto)

        call_args = mock_excel_service.write_workbook.call_args
        export_data = call_args[0][1]

        # Both stories have feature_id=1 (Autenticacao)
        assert export_data.stories[0]["Feature"] == "Autenticacao"
        assert export_data.stories[1]["Feature"] == "Autenticacao"


class TestExportDataFormat:
    """Tests for export data format compliance."""

    async def test_stories_have_all_required_columns(
        self,
        use_case,
        mock_story_repo,
        mock_excel_service,
        sample_stories,
        tmp_path: Path,
    ):
        """Should include all required columns for stories."""
        mock_story_repo.get_all.return_value = sample_stories[:1]

        file_path = tmp_path / "columns_export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        await use_case.execute(input_dto)

        call_args = mock_excel_service.write_workbook.call_args
        export_data = call_args[0][1]
        story_row = export_data.stories[0]

        # Check required columns exist
        assert "ID" in story_row
        assert "Componente" in story_row
        assert "Nome" in story_row
        assert "SP" in story_row
        assert "Status" in story_row
        assert "Feature" in story_row
        assert "Dependencias" in story_row
        assert "Desenvolvedor" in story_row
        assert "Data Inicio" in story_row
        assert "Data Fim" in story_row

    async def test_sp_exported_as_integer(
        self,
        use_case,
        mock_story_repo,
        mock_excel_service,
        sample_stories,
        tmp_path: Path,
    ):
        """Should export SP as integer value."""
        mock_story_repo.get_all.return_value = sample_stories[:1]

        file_path = tmp_path / "sp_export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        await use_case.execute(input_dto)

        call_args = mock_excel_service.write_workbook.call_args
        export_data = call_args[0][1]

        assert isinstance(export_data.stories[0]["SP"], int)
        assert export_data.stories[0]["SP"] == 5

    async def test_status_exported_as_string(
        self,
        use_case,
        mock_story_repo,
        mock_excel_service,
        sample_stories,
        tmp_path: Path,
    ):
        """Should export Status as string value."""
        mock_story_repo.get_all.return_value = sample_stories[:1]

        file_path = tmp_path / "status_export.xlsx"
        input_dto = ExportExcelInputDTO(file_path=file_path)
        await use_case.execute(input_dto)

        call_args = mock_excel_service.write_workbook.call_args
        export_data = call_args[0][1]

        assert isinstance(export_data.stories[0]["Status"], str)
        assert export_data.stories[0]["Status"] == "BACKLOG"
