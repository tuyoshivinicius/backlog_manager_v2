"""Headless tests for ExcelViewModel."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from tests.headless_mocks import create_pyside6_mocks

_mock_qt_core, _pyside6_mocks = create_pyside6_mocks()

with patch.dict("sys.modules", _pyside6_mocks):
    import backlog_manager.presentation.viewmodels.excel_viewmodel as _evm
    from backlog_manager.presentation.viewmodels.excel_viewmodel import (
        ExcelViewModel,
    )

from backlog_manager.application.exceptions.excel_exceptions import (  # noqa: E402
    ExcelCycleDetectedException,
    ExcelException,
    ExcelFileCorruptedException,
    ExcelFileNotFoundException,
    ExcelMissingHeaderException,
    ExcelPermissionException,
)
from backlog_manager.domain.exceptions import BacklogManagerException  # noqa: E402


@pytest.fixture(autouse=True)
def _patch_dtos(monkeypatch):
    """Patch DTOs to bypass Pydantic file-path validation."""
    mock_import_dto_cls = MagicMock(side_effect=lambda **kw: MagicMock(**kw))
    mock_export_dto_cls = MagicMock(side_effect=lambda **kw: MagicMock(**kw))
    monkeypatch.setattr(_evm, "ImportExcelInputDTO", mock_import_dto_cls)
    monkeypatch.setattr(_evm, "ExportExcelInputDTO", mock_export_dto_cls)


@pytest.fixture
def mock_container():
    """Create a mock DIContainer."""
    container = MagicMock()
    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=False)
    container.create_unit_of_work.return_value = mock_uow
    return container


@pytest.fixture
def viewmodel(mock_container):
    """Create an ExcelViewModel."""
    return ExcelViewModel(mock_container)


def _make_import_result(stories=5, features=2, warnings=None):
    result = MagicMock()
    result.stories_imported = stories
    result.features_created = features
    result.warnings = warnings or []
    return result


def _make_export_result(stories=10, developers=3, features=4):
    result = MagicMock()
    result.stories_exported = stories
    result.developers_exported = developers
    result.features_exported = features
    return result


class TestExcelViewModelInitialization:  # noqa: D101
    def test_initial_state(self, viewmodel) -> None:
        assert viewmodel.is_importing is False
        assert viewmodel.is_exporting is False
        assert viewmodel.is_busy is False

    def test_stores_container(self, viewmodel, mock_container) -> None:
        assert viewmodel._container is mock_container


class TestExcelViewModelProperties:  # noqa: D101
    def test_is_busy_when_importing(self, viewmodel) -> None:
        viewmodel._is_importing = True
        assert viewmodel.is_busy is True

    def test_is_busy_when_exporting(self, viewmodel) -> None:
        viewmodel._is_exporting = True
        assert viewmodel.is_busy is True

    def test_is_busy_when_both(self, viewmodel) -> None:
        viewmodel._is_importing = True
        viewmodel._is_exporting = True
        assert viewmodel.is_busy is True

    def test_not_busy_when_idle(self, viewmodel) -> None:
        assert viewmodel.is_busy is False


class TestProgressCallback:  # noqa: D101
    def test_emits_progress_signal(self, viewmodel) -> None:
        viewmodel._progress_callback(50)
        assert (50,) in viewmodel.progress_updated.emissions


class TestGetErrorMessage:  # noqa: D101
    def test_file_not_found_with_msg(self, viewmodel) -> None:
        err = ExcelFileNotFoundException("Custom not found")
        assert viewmodel._get_error_message(err) == "Custom not found"

    def test_file_not_found_no_msg(self, viewmodel) -> None:
        err = ExcelFileNotFoundException()
        assert viewmodel._get_error_message(err) == "Arquivo nao encontrado"

    def test_file_corrupted_with_msg(self, viewmodel) -> None:
        err = ExcelFileCorruptedException("Bad file")
        assert viewmodel._get_error_message(err) == "Bad file"

    def test_file_corrupted_no_msg(self, viewmodel) -> None:
        err = ExcelFileCorruptedException()
        assert viewmodel._get_error_message(err) == "Arquivo invalido ou corrompido"

    def test_missing_header_with_msg(self, viewmodel) -> None:
        err = ExcelMissingHeaderException("Missing col X")
        assert viewmodel._get_error_message(err) == "Missing col X"

    def test_missing_header_no_msg(self, viewmodel) -> None:
        err = ExcelMissingHeaderException()
        assert (
            viewmodel._get_error_message(err)
            == "Colunas obrigatorias ausentes no arquivo"
        )

    def test_cycle_detected_with_msg(self, viewmodel) -> None:
        err = ExcelCycleDetectedException("Cycle found")
        assert viewmodel._get_error_message(err) == "Cycle found"

    def test_cycle_detected_no_msg(self, viewmodel) -> None:
        err = ExcelCycleDetectedException()
        assert (
            viewmodel._get_error_message(err)
            == "Ciclo de dependencia detectado no arquivo"
        )

    def test_permission_with_msg(self, viewmodel) -> None:
        err = ExcelPermissionException("No access")
        assert viewmodel._get_error_message(err) == "No access"

    def test_permission_no_msg(self, viewmodel) -> None:
        err = ExcelPermissionException()
        assert viewmodel._get_error_message(err) == "Sem permissao para acessar arquivo"

    def test_generic_excel_with_msg(self, viewmodel) -> None:
        err = ExcelException("Generic excel error")
        assert viewmodel._get_error_message(err) == "Generic excel error"

    def test_generic_excel_no_msg(self, viewmodel) -> None:
        err = ExcelException()
        assert viewmodel._get_error_message(err) == "Erro na operacao Excel"

    def test_backlog_exception_with_msg(self, viewmodel) -> None:
        err = BacklogManagerException("Domain error")
        assert viewmodel._get_error_message(err) == "Domain error"

    def test_backlog_exception_no_msg(self, viewmodel) -> None:
        err = BacklogManagerException()
        assert viewmodel._get_error_message(err) == "Erro na operacao"

    def test_unexpected_exception(self, viewmodel) -> None:
        err = RuntimeError("Something broke")
        assert viewmodel._get_error_message(err) == "Erro inesperado"


class TestImportFromFile:  # noqa: D101
    @pytest.fixture(autouse=True)
    def _mock_import_dto(self):
        with patch(
            "backlog_manager.presentation.viewmodels.excel_viewmodel.ImportExcelInputDTO",
            return_value=MagicMock(),
        ):
            yield

    @pytest.mark.asyncio
    async def test_successful_import(self, viewmodel, mock_container) -> None:
        mock_result = _make_import_result(stories=5, features=2, warnings=["warn1"])
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = mock_result
        mock_container.create_import_excel_use_case.return_value = mock_uc

        result = await viewmodel.import_from_file(Path("/tmp/test.xlsx"))

        assert result is mock_result
        assert viewmodel.is_importing is False
        assert viewmodel.import_started.emissions[0] == ()
        assert (0,) in viewmodel.progress_updated.emissions
        assert (100,) in viewmodel.progress_updated.emissions
        assert (mock_result,) in viewmodel.import_completed.emissions

    @pytest.mark.asyncio
    async def test_import_none_when_busy_importing(self, viewmodel) -> None:
        viewmodel._is_importing = True
        result = await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert result is None

    @pytest.mark.asyncio
    async def test_import_none_when_busy_exporting(self, viewmodel) -> None:
        viewmodel._is_exporting = True
        result = await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert result is None

    @pytest.mark.asyncio
    async def test_import_error_file_not_found(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ExcelFileNotFoundException("Not found")
        mock_container.create_import_excel_use_case.return_value = mock_uc
        result = await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert result is None
        assert viewmodel.is_importing is False
        assert viewmodel.import_error.emissions[0] == ("Not found",)

    @pytest.mark.asyncio
    async def test_import_error_missing_header(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ExcelMissingHeaderException("Missing col A")
        mock_container.create_import_excel_use_case.return_value = mock_uc
        result = await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert result is None
        assert viewmodel.import_error.emissions[0] == ("Missing col A",)

    @pytest.mark.asyncio
    async def test_import_unexpected_error(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = RuntimeError("boom")
        mock_container.create_import_excel_use_case.return_value = mock_uc
        result = await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert result is None
        assert viewmodel.import_error.emissions[0] == ("Erro inesperado",)

    @pytest.mark.asyncio
    async def test_import_cancelled(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = asyncio.CancelledError()
        mock_container.create_import_excel_use_case.return_value = mock_uc
        result = await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert result is None
        assert viewmodel.is_importing is False
        assert len(viewmodel.import_cancelled.emissions) == 1

    @pytest.mark.asyncio
    async def test_import_resets_flag_on_error(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ExcelException("fail")
        mock_container.create_import_excel_use_case.return_value = mock_uc
        await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert viewmodel.is_importing is False

    @pytest.mark.asyncio
    async def test_import_flag_during_execution(
        self, viewmodel, mock_container
    ) -> None:
        captured = {}

        async def capture(*args, **kwargs):
            captured["v"] = viewmodel.is_importing
            return _make_import_result()

        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = capture
        mock_container.create_import_excel_use_case.return_value = mock_uc
        await viewmodel.import_from_file(Path("/tmp/test.xlsx"))
        assert captured["v"] is True
        assert viewmodel.is_importing is False


class TestExportToFile:  # noqa: D101
    @pytest.fixture(autouse=True)
    def _mock_export_dto(self):
        with patch(
            "backlog_manager.presentation.viewmodels.excel_viewmodel.ExportExcelInputDTO",
            return_value=MagicMock(),
        ):
            yield

    @pytest.mark.asyncio
    async def test_successful_export(self, viewmodel, mock_container) -> None:
        mock_result = _make_export_result(stories=10, developers=3, features=4)
        mock_uc = AsyncMock()
        mock_uc.execute.return_value = mock_result
        mock_container.create_export_excel_use_case.return_value = mock_uc
        result = await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert result is mock_result
        assert viewmodel.is_exporting is False
        assert viewmodel.export_started.emissions[0] == ()
        assert (0,) in viewmodel.progress_updated.emissions
        assert (100,) in viewmodel.progress_updated.emissions
        assert (mock_result,) in viewmodel.export_completed.emissions

    @pytest.mark.asyncio
    async def test_export_none_when_busy_importing(self, viewmodel) -> None:
        viewmodel._is_importing = True
        result = await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert result is None

    @pytest.mark.asyncio
    async def test_export_none_when_busy_exporting(self, viewmodel) -> None:
        viewmodel._is_exporting = True
        result = await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert result is None

    @pytest.mark.asyncio
    async def test_export_error_permission(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ExcelPermissionException("No write access")
        mock_container.create_export_excel_use_case.return_value = mock_uc
        result = await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert result is None
        assert viewmodel.is_exporting is False
        assert viewmodel.export_error.emissions[0] == ("No write access",)

    @pytest.mark.asyncio
    async def test_export_unexpected_error(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ValueError("unexpected")
        mock_container.create_export_excel_use_case.return_value = mock_uc
        result = await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert result is None
        assert viewmodel.export_error.emissions[0] == ("Erro inesperado",)

    @pytest.mark.asyncio
    async def test_export_cancelled_deletes_partial(
        self, viewmodel, mock_container
    ) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = asyncio.CancelledError()
        mock_container.create_export_excel_use_case.return_value = mock_uc
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        result = await viewmodel.export_to_file(mock_path)
        assert result is None
        assert viewmodel.is_exporting is False
        assert len(viewmodel.export_cancelled.emissions) == 1
        mock_path.unlink.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_cancelled_no_partial(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = asyncio.CancelledError()
        mock_container.create_export_excel_use_case.return_value = mock_uc
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = False
        result = await viewmodel.export_to_file(mock_path)
        assert result is None
        assert len(viewmodel.export_cancelled.emissions) == 1
        mock_path.unlink.assert_not_called()

    @pytest.mark.asyncio
    async def test_export_cancelled_unlink_oserror(
        self, viewmodel, mock_container
    ) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = asyncio.CancelledError()
        mock_container.create_export_excel_use_case.return_value = mock_uc
        mock_path = MagicMock(spec=Path)
        mock_path.exists.return_value = True
        mock_path.unlink.side_effect = OSError("locked")
        result = await viewmodel.export_to_file(mock_path)
        assert result is None
        assert len(viewmodel.export_cancelled.emissions) == 1

    @pytest.mark.asyncio
    async def test_export_resets_flag_on_error(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = ExcelException("fail")
        mock_container.create_export_excel_use_case.return_value = mock_uc
        await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert viewmodel.is_exporting is False

    @pytest.mark.asyncio
    async def test_export_flag_during_execution(
        self, viewmodel, mock_container
    ) -> None:
        captured = {}

        async def capture(*args, **kwargs):
            captured["v"] = viewmodel.is_exporting
            return _make_export_result()

        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = capture
        mock_container.create_export_excel_use_case.return_value = mock_uc
        await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert captured["v"] is True
        assert viewmodel.is_exporting is False

    @pytest.mark.asyncio
    async def test_export_backlog_exception(self, viewmodel, mock_container) -> None:
        mock_uc = AsyncMock()
        mock_uc.execute.side_effect = BacklogManagerException("Domain error")
        mock_container.create_export_excel_use_case.return_value = mock_uc
        result = await viewmodel.export_to_file(Path("/tmp/export.xlsx"))
        assert result is None
        assert viewmodel.export_error.emissions[0] == ("Domain error",)
