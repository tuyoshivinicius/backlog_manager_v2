# Quickstart: EP-009 Excel Integration

**Feature**: EP-009 Excel Integration
**Date**: 2026-03-03

## Prerequisites

1. Python 3.11+ installed
2. Poetry installed
3. Backlog Manager v2 repository cloned
4. EP-001 through EP-008 implemented (existing codebase)

## Setup

### 1. Install New Dependency

```bash
cd backlog_manager_v2
poetry add openpyxl@^3.1.0
```

### 2. Verify Installation

```bash
poetry run python -c "import openpyxl; print(openpyxl.__version__)"
# Expected: 3.1.x
```

## Implementation Order

Follow this order to maintain dependencies between components:

### Phase 1: DTOs (No Dependencies)

1. Create `src/backlog_manager/application/dto/excel/__init__.py`
2. Create `src/backlog_manager/application/dto/excel/import_excel_dto.py`
3. Create `src/backlog_manager/application/dto/excel/export_excel_dto.py`

### Phase 2: Protocol Interface (Depends on DTOs)

1. Create `src/backlog_manager/application/interfaces/excel_service.py`

### Phase 3: Infrastructure Implementation (Depends on Protocol, DTOs)

1. Create `src/backlog_manager/infrastructure/excel/__init__.py`
2. Create `src/backlog_manager/infrastructure/excel/excel_service.py`

### Phase 4: Domain Exceptions (No Dependencies)

1. Add Excel exceptions to `src/backlog_manager/domain/exceptions/`

### Phase 5: Use Cases (Depends on Protocol, DTOs, Repositories)

1. Create `src/backlog_manager/application/use_cases/excel/__init__.py`
2. Create `src/backlog_manager/application/use_cases/excel/import_excel_use_case.py`
3. Create `src/backlog_manager/application/use_cases/excel/export_excel_use_case.py`

### Phase 6: ViewModel (Depends on Use Cases)

1. Create `src/backlog_manager/presentation/viewmodels/excel_viewmodel.py`

### Phase 7: UI Integration (Depends on ViewModel)

1. Modify `src/backlog_manager/presentation/views/main_window.py`
2. Add import/export buttons and shortcuts

### Phase 8: DI Container (Depends on All Above)

1. Modify `src/backlog_manager/presentation/container.py`
2. Register ExcelService and factories

## Key Code Snippets

### ExcelService (Infrastructure)

```python
# src/backlog_manager/infrastructure/excel/excel_service.py
import asyncio
import logging
from pathlib import Path

from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

from backlog_manager.application.dto.excel.import_excel_dto import ExcelReadResult
from backlog_manager.application.dto.excel.export_excel_dto import ExcelExportData
from backlog_manager.domain.exceptions.excel import (
    ExcelFileCorruptedException,
    ExcelFileNotFoundException,
    ExcelMissingHeaderException,
    ExcelPermissionException,
)

logger = logging.getLogger(__name__)

REQUIRED_HEADERS = ["ID", "Componente", "Nome", "SP", "Feature", "Dependencias"]


class ExcelService:
    """Servico de infraestrutura para operacoes Excel via openpyxl."""

    async def read_stories_from_file(self, file_path: Path) -> ExcelReadResult:
        """Le arquivo Excel de forma assincrona."""
        return await asyncio.to_thread(self._read_stories_sync, file_path)

    def _read_stories_sync(self, file_path: Path) -> ExcelReadResult:
        """Operacao sincrona de leitura."""
        logger.info("Lendo arquivo Excel: %s", file_path)

        if not file_path.exists():
            raise ExcelFileNotFoundException(f"Arquivo nao encontrado: {file_path}")

        if file_path.suffix.lower() != ".xlsx":
            raise ExcelFileCorruptedException("Formato nao suportado. Use .xlsx")

        try:
            wb = load_workbook(file_path, read_only=True, data_only=True)
        except PermissionError as e:
            raise ExcelPermissionException(f"Sem permissao para ler: {file_path}") from e
        except InvalidFileException as e:
            raise ExcelFileCorruptedException("Arquivo invalido ou corrompido") from e

        try:
            ws = wb.active
            headers = [cell.value for cell in ws[1]]

            # Validate required headers
            for required in REQUIRED_HEADERS:
                if required not in headers:
                    raise ExcelMissingHeaderException(
                        f"Coluna obrigatoria '{required}' nao encontrada na linha 1"
                    )

            rows = []
            warnings = []
            for row in ws.iter_rows(min_row=2, values_only=True):
                row_dict = dict(zip(headers, row))
                rows.append(row_dict)

            return ExcelReadResult(rows=rows, warnings=warnings)
        finally:
            wb.close()

    async def write_workbook(self, file_path: Path, data: ExcelExportData) -> None:
        """Escreve arquivo Excel de forma assincrona."""
        await asyncio.to_thread(self._write_workbook_sync, file_path, data)

    def _write_workbook_sync(self, file_path: Path, data: ExcelExportData) -> None:
        """Operacao sincrona de escrita."""
        logger.info("Escrevendo arquivo Excel: %s", file_path)

        try:
            wb = Workbook()
            wb.remove(wb.active)

            # Stories sheet
            self._write_sheet(wb, "Stories", data.stories)

            # Developers sheet
            self._write_sheet(wb, "Developers", data.developers)

            # Features sheet
            self._write_sheet(wb, "Features", data.features)

            wb.save(file_path)
            logger.info("Export concluido: %s", file_path)
        except PermissionError as e:
            raise ExcelPermissionException(f"Sem permissao para escrever: {file_path}") from e

    def _write_sheet(
        self, wb: Workbook, name: str, data: list[dict]
    ) -> None:
        """Cria worksheet com dados."""
        ws = wb.create_sheet(name)
        if data:
            headers = list(data[0].keys())
            ws.append(headers)
            for row_dict in data:
                ws.append([row_dict.get(h) for h in headers])
```

### ImportExcelUseCase (Application)

```python
# src/backlog_manager/application/use_cases/excel/import_excel_use_case.py
import logging
from typing import Callable

from backlog_manager.application.dto.excel.import_excel_dto import (
    ImportExcelInputDTO,
    ImportExcelOutputDTO,
)
from backlog_manager.application.interfaces.excel_service import ExcelServiceProtocol
from backlog_manager.domain.services.dependency_service import DependencyService
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

logger = logging.getLogger(__name__)


class ImportExcelUseCase:
    """Caso de uso para importacao de arquivo Excel."""

    def __init__(
        self,
        uow: SQLiteUnitOfWork,
        excel_service: ExcelServiceProtocol,
        progress_callback: Callable[[int], None] | None = None,
    ) -> None:
        self._uow = uow
        self._excel_service = excel_service
        self._progress_callback = progress_callback

    async def execute(self, input_dto: ImportExcelInputDTO) -> ImportExcelOutputDTO:
        """Executa importacao de arquivo Excel."""
        logger.info("Iniciando import de arquivo: %s", input_dto.file_path)

        result = await self._excel_service.read_stories_from_file(input_dto.file_path)

        stories_imported = 0
        features_created = 0
        warnings = list(result.warnings)

        # Pass 1: Create stories and features
        # ... implementation details ...

        # Pass 2: Create dependencies after cycle validation
        # ... implementation details ...

        logger.info(
            "Import concluido: %d historias importadas, %d warnings",
            stories_imported,
            len(warnings),
        )

        return ImportExcelOutputDTO(
            stories_imported=stories_imported,
            features_created=features_created,
            warnings=warnings,
        )
```

### ExcelViewModel (Presentation)

```python
# src/backlog_manager/presentation/viewmodels/excel_viewmodel.py
import logging
from pathlib import Path

from PySide6.QtCore import QObject, Signal

from backlog_manager.application.dto.excel.import_excel_dto import ImportExcelOutputDTO
from backlog_manager.application.dto.excel.export_excel_dto import ExportExcelOutputDTO

logger = logging.getLogger(__name__)


class ExcelViewModel(QObject):
    """ViewModel para operacoes de import/export Excel."""

    import_started = Signal()
    import_completed = Signal(object)
    import_error = Signal(str)
    export_started = Signal()
    export_completed = Signal(object)
    export_error = Signal(str)
    progress_updated = Signal(int)

    def __init__(self, container: "DIContainer") -> None:
        super().__init__()
        self._container = container

    async def import_from_file(self, file_path: Path) -> None:
        """Importa dados de arquivo Excel."""
        self.import_started.emit()
        self.progress_updated.emit(0)

        try:
            async with self._container.create_unit_of_work() as uow:
                use_case = self._container.create_import_excel_use_case(
                    uow, progress_callback=self.progress_updated.emit
                )
                result = await use_case.execute(
                    ImportExcelInputDTO(file_path=file_path)
                )

            self.progress_updated.emit(100)
            self.import_completed.emit(result)
        except Exception as e:
            logger.error("Erro no import: %s", str(e), exc_info=True)
            self.import_error.emit(str(e))
```

## Testing

### Run Unit Tests

```bash
poetry run pytest tests/unit/application/use_cases/excel/ -v
```

### Run Integration Tests

```bash
poetry run pytest tests/integration/infrastructure/excel/ -v
```

### Run All Tests with Coverage

```bash
poetry run pytest --cov=src/backlog_manager --cov-report=term-missing
```

## Manual Testing

### Create Test Excel File

Create a file `test_import.xlsx` with:

**Row 1 (Headers)**:
| ID | Componente | Nome | SP | Feature | Dependencias |

**Row 2+**:
| AUTH-001 | AUTH | Login de usuario | 5 | Autenticacao | |
| AUTH-002 | AUTH | Logout de usuario | 3 | Autenticacao | AUTH-001 |
| | API | Endpoint de health | 3 | Infraestrutura | |

### Test Import

1. Launch application: `poetry run python -m backlog_manager`
2. Press `Ctrl+I` or click "Importar Excel"
3. Select `test_import.xlsx`
4. Verify:
   - 3 stories imported
   - 2 features created (Autenticacao, Infraestrutura)
   - 1 dependency created (AUTH-002 -> AUTH-001)
   - API-001 auto-generated for row without ID

### Test Export

1. Click "Exportar Excel" or press `Ctrl+E`
2. Choose destination file
3. Open in Excel/LibreOffice
4. Verify 3 worksheets: Stories, Developers, Features

### Test Roundtrip

1. Export to `backup.xlsx`
2. Clear database (delete backlog.db)
3. Import `backup.xlsx`
4. Verify all data restored identically

## Troubleshooting

### "openpyxl not found"
```bash
poetry install
poetry run python -c "import openpyxl"
```

### "Permission denied" on Windows
Close Excel if the file is open.

### Progress dialog freezes
Ensure asyncio.to_thread() is used in ExcelService.

### Cycle detection fails
Check DependencyService.build_graph() and detect_cycle() are called correctly.
