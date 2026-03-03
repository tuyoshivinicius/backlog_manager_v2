"""Protocol for Excel file I/O operations."""

from pathlib import Path
from typing import Protocol

from backlog_manager.application.dto.excel.export_excel_dto import ExcelExportData
from backlog_manager.application.dto.excel.import_excel_dto import ExcelReadResult


class ExcelServiceProtocol(Protocol):
    """Protocolo para operacoes de leitura/escrita de arquivos Excel.

    Define a interface para o servico de Excel, permitindo inversao
    de dependencia entre Application e Infrastructure layers.

    Todas as operacoes sao assincronas para nao bloquear o event loop.
    """

    async def read_stories_from_file(self, file_path: Path) -> ExcelReadResult:
        """Le dados do arquivo Excel para importacao.

        Args:
            file_path: Caminho absoluto para arquivo .xlsx.

        Returns:
            ExcelReadResult com lista de dicionarios (linhas) e warnings.

        Raises:
            ExcelFileNotFoundException: Arquivo nao encontrado.
            ExcelFileCorruptedException: Arquivo invalido ou corrompido.
            ExcelMissingHeaderException: Coluna obrigatoria ausente.
            ExcelPermissionException: Sem permissao de leitura.
        """
        ...

    async def write_workbook(self, file_path: Path, data: ExcelExportData) -> None:
        """Escreve dados em arquivo Excel para exportacao.

        Args:
            file_path: Caminho absoluto para arquivo .xlsx de destino.
            data: Dados a serem escritos (stories, developers, features).

        Raises:
            ExcelPermissionException: Sem permissao de escrita.
            ExcelFileCorruptedException: Erro ao escrever arquivo.
        """
        ...
