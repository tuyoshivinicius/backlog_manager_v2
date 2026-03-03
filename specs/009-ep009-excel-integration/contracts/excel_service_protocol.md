# Contract: ExcelServiceProtocol

**Location**: `src/backlog_manager/application/interfaces/excel_service.py`
**Type**: Protocol (Interface)
**Layer**: Application (interfaces)

## Overview

Protocol defining the contract for Excel file I/O operations. Implemented by `ExcelService` in Infrastructure layer, enabling dependency inversion per Clean Architecture principles.

## Protocol Definition

```python
from pathlib import Path
from typing import Protocol

from backlog_manager.application.dto.excel.import_excel_dto import ExcelReadResult
from backlog_manager.application.dto.excel.export_excel_dto import ExcelExportData


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
```

## Method Contracts

### read_stories_from_file

| Aspect | Specification |
|--------|---------------|
| **Input** | `file_path: Path` - Absolute path to .xlsx file |
| **Output** | `ExcelReadResult` - Rows as list of dicts + warnings |
| **Preconditions** | File exists, is readable, has .xlsx extension |
| **Postconditions** | Returns all data rows with headers as keys |
| **Side Effects** | None (read-only operation) |

**Validation Performed**:
1. File extension must be `.xlsx`
2. File must exist and be readable
3. Required headers present: ID, Componente, Nome, SP, Feature, Dependencias
4. Row 1 treated as headers, row 2+ as data

**Error Scenarios**:
| Exception | Condition |
|-----------|-----------|
| `ExcelFileNotFoundException` | File does not exist |
| `ExcelFileCorruptedException` | File is malformed or unreadable |
| `ExcelMissingHeaderException` | Required column missing from row 1 |
| `ExcelPermissionException` | No read permission on file |

### write_workbook

| Aspect | Specification |
|--------|---------------|
| **Input** | `file_path: Path` - Output path, `data: ExcelExportData` - Data to write |
| **Output** | `None` |
| **Preconditions** | Directory exists, write permission available |
| **Postconditions** | File created with 3 worksheets |
| **Side Effects** | Creates/overwrites file at `file_path` |

**Worksheet Creation**:
1. "Stories" sheet with columns from `data.stories`
2. "Developers" sheet with columns from `data.developers`
3. "Features" sheet with columns from `data.features`

**Error Scenarios**:
| Exception | Condition |
|-----------|-----------|
| `ExcelPermissionException` | No write permission on directory/file |
| `ExcelFileCorruptedException` | I/O error during write |

## Implementation Requirements

1. **Async Execution**: Both methods must be async, using `asyncio.to_thread()` for openpyxl operations
2. **Thread Safety**: Each call creates its own Workbook instance
3. **Resource Cleanup**: Workbook must be closed after read operations
4. **Logging**: Log INFO at start/end, ERROR on exceptions (per FR-124-126)

## Usage Example

```python
from backlog_manager.application.interfaces.excel_service import ExcelServiceProtocol
from backlog_manager.infrastructure.excel.excel_service import ExcelService

class ImportExcelUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        excel_service: ExcelServiceProtocol  # Injected via protocol
    ) -> None:
        self._uow = uow
        self._excel_service = excel_service

    async def execute(self, input_dto: ImportExcelInputDTO) -> ImportExcelOutputDTO:
        result = await self._excel_service.read_stories_from_file(input_dto.file_path)
        # Process result.rows...
```

## Dependency Direction

```
Application Layer              Infrastructure Layer
+----------------------+       +----------------------+
| ImportExcelUseCase   |       | ExcelService         |
|   depends on         |       |   implements         |
|   ExcelServiceProtocol|<-----|   ExcelServiceProtocol|
+----------------------+       +----------------------+
        ^                              |
        |                              |
   Protocol defined             Implementation uses
   in Application               openpyxl library
```
