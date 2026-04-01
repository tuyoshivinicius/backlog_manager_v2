"""Excel ViewModel for import/export operations.

This module provides the ViewModel for Excel import/export operations,
coordinating between use cases and UI, emitting signals for progress and status.
"""

from __future__ import annotations

import asyncio
import logging
from pathlib import Path
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.excel.export_excel_dto import ExportExcelInputDTO
from backlog_manager.application.dto.excel.import_excel_dto import ImportExcelInputDTO
from backlog_manager.application.exceptions.excel_exceptions import (
    ExcelCycleDetectedException,
    ExcelException,
    ExcelFileCorruptedException,
    ExcelFileNotFoundException,
    ExcelMissingHeaderException,
    ExcelPermissionException,
)
from backlog_manager.domain.exceptions import BacklogManagerException

if TYPE_CHECKING:
    from backlog_manager.application.dto.excel.export_excel_dto import (
        ExportExcelOutputDTO,
    )
    from backlog_manager.application.dto.excel.import_excel_dto import (
        ImportExcelOutputDTO,
    )
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


class ExcelViewModel(QObject):
    """ViewModel para operacoes de import/export Excel.

    Gerencia operacoes assincronas de Excel e emite signals para
    a View atualizar a UI com progresso e resultados.

    Signals:
        import_started: Emitido quando import inicia.
        import_completed: Emitido quando import termina com sucesso.
        import_error: Emitido quando import falha.
        export_started: Emitido quando export inicia.
        export_completed: Emitido quando export termina com sucesso.
        export_error: Emitido quando export falha.
        progress_updated: Emitido durante operacao com percentual (0-100).
    """

    # Import signals
    import_started = Signal()
    import_completed = Signal(object)  # ImportExcelOutputDTO
    import_error = Signal(str)
    import_cancelled = Signal()

    # Export signals
    export_started = Signal()
    export_completed = Signal(object)  # ExportExcelOutputDTO
    export_error = Signal(str)
    export_cancelled = Signal()

    # Progress signal
    progress_updated = Signal(int)  # 0-100 percentage

    def __init__(self, container: DIContainer) -> None:
        """Initialize the ViewModel.

        Args:
            container: Dependency injection container.
        """
        super().__init__()
        self._container = container
        self._is_importing = False
        self._is_exporting = False

        logger.debug("ExcelViewModel initialized")

    @property
    def is_importing(self) -> bool:
        """Check if import operation is in progress.

        Returns:
            True if importing, False otherwise.
        """
        return self._is_importing

    @property
    def is_exporting(self) -> bool:
        """Check if export operation is in progress.

        Returns:
            True if exporting, False otherwise.
        """
        return self._is_exporting

    @property
    def is_busy(self) -> bool:
        """Check if any operation is in progress.

        Returns:
            True if any operation is running.
        """
        return self._is_importing or self._is_exporting

    def _progress_callback(self, percent: int) -> None:
        """Handle progress updates from use case.

        Args:
            percent: Progress percentage (0-100).
        """
        self.progress_updated.emit(percent)

    def _get_error_message(self, error: Exception) -> str:
        """Convert exception to user-friendly error message.

        Args:
            error: The exception that occurred.

        Returns:
            Error message in Portuguese.
        """
        if isinstance(error, ExcelFileNotFoundException):
            return str(error) or "Arquivo nao encontrado"
        if isinstance(error, ExcelFileCorruptedException):
            return str(error) or "Arquivo invalido ou corrompido"
        if isinstance(error, ExcelMissingHeaderException):
            return str(error) or "Colunas obrigatorias ausentes no arquivo"
        if isinstance(error, ExcelCycleDetectedException):
            return str(error) or "Ciclo de dependencia detectado no arquivo"
        if isinstance(error, ExcelPermissionException):
            return str(error) or "Sem permissao para acessar arquivo"
        if isinstance(error, ExcelException):
            return str(error) or "Erro na operacao Excel"
        if isinstance(error, BacklogManagerException):
            return str(error) or "Erro na operacao"
        return "Erro inesperado"

    async def import_from_file(self, file_path: Path) -> ImportExcelOutputDTO | None:
        """Importa dados de arquivo Excel.

        Emite signals durante operacao:
        1. import_started
        2. progress_updated (0-100%)
        3. import_completed OR import_error

        Args:
            file_path: Caminho para arquivo .xlsx.

        Returns:
            DTO com resultados ou None se erro.
        """
        if self.is_busy:
            logger.warning("Operacao ja em andamento, ignorando import")
            return None

        self._is_importing = True
        self.import_started.emit()
        self.progress_updated.emit(0)

        logger.info("Iniciando import de: %s", file_path)

        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_import_excel_use_case(
                    uow, self._progress_callback
                )
                input_dto = ImportExcelInputDTO(file_path=file_path)
                result = await use_case.execute(input_dto)

                self.progress_updated.emit(100)
                self.import_completed.emit(result)

                logger.info(
                    "Import concluido: %d historias, %d features, %d avisos",
                    result.stories_imported,
                    result.features_created,
                    len(result.warnings),
                )
                return result

        except asyncio.CancelledError:
            logger.info("Import cancelled by user")
            self.import_cancelled.emit()
            raise

        except Exception as e:
            error_msg = self._get_error_message(e)
            logger.error("Erro no import: %s", error_msg)
            self.import_error.emit(error_msg)
            return None

        finally:
            self._is_importing = False

    async def export_to_file(self, file_path: Path) -> ExportExcelOutputDTO | None:
        """Exporta dados para arquivo Excel.

        Emite signals durante operacao:
        1. export_started
        2. progress_updated (0, 100)
        3. export_completed OR export_error

        Args:
            file_path: Caminho de destino .xlsx.

        Returns:
            DTO com resultados ou None se erro.
        """
        if self.is_busy:
            logger.warning("Operacao ja em andamento, ignorando export")
            return None

        self._is_exporting = True
        self.export_started.emit()
        self.progress_updated.emit(0)

        logger.info("Iniciando export para: %s", file_path)

        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_export_excel_use_case(uow)
                input_dto = ExportExcelInputDTO(file_path=file_path)
                result = await use_case.execute(input_dto)

                self.progress_updated.emit(100)
                self.export_completed.emit(result)

                logger.info(
                    "Export concluido: %d historias, %d desenvolvedores, %d features",
                    result.stories_exported,
                    result.developers_exported,
                    result.features_exported,
                )
                return result

        except asyncio.CancelledError:
            logger.info("Export cancelled by user")
            # Delete partial file if it exists
            if file_path.exists():
                try:
                    file_path.unlink()
                    logger.info("Partial export file deleted: %s", file_path)
                except OSError:
                    logger.warning("Could not delete partial file: %s", file_path)
            self.export_cancelled.emit()
            raise

        except Exception as e:
            error_msg = self._get_error_message(e)
            logger.error("Erro no export: %s", error_msg)
            self.export_error.emit(error_msg)
            return None

        finally:
            self._is_exporting = False
