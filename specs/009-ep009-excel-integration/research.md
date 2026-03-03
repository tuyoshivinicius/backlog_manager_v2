# Research: EP-009 Excel Integration

**Feature**: EP-009 Excel Integration
**Date**: 2026-03-03
**Status**: Complete

## Research Tasks

This document consolidates research findings for implementing Excel integration in Backlog Manager.

---

## 1. openpyxl Library Best Practices

### Decision
Use openpyxl ^3.1.0 for Excel (.xlsx) file operations, wrapped with asyncio.to_thread() for non-blocking I/O.

### Rationale
- **openpyxl** is the de-facto standard for .xlsx manipulation in Python
- Native support for reading/writing multiple worksheets
- Mature library with extensive documentation
- Supports cell formatting, validation rules, and data types
- Already listed in Constitution VI as required dependency

### Alternatives Considered
1. **xlsxwriter**: Write-only (no read support) - rejected because we need both import and export
2. **pandas + openpyxl**: Adds unnecessary dependency, pandas overkill for structured row data
3. **xlrd/xlwt**: Legacy .xls format only, not .xlsx - rejected per spec (RF-005 requires .xlsx)

### Key openpyxl Patterns

```python
from openpyxl import Workbook, load_workbook
from openpyxl.utils.exceptions import InvalidFileException

# Reading
def read_excel_sync(file_path: Path) -> list[dict[str, Any]]:
    try:
        wb = load_workbook(file_path, read_only=True, data_only=True)
        ws = wb.active
        headers = [cell.value for cell in ws[1]]
        rows = []
        for row in ws.iter_rows(min_row=2, values_only=True):
            rows.append(dict(zip(headers, row)))
        wb.close()
        return rows
    except InvalidFileException:
        raise ExcelFileCorruptedException("Arquivo invalido ou corrompido")

# Writing
def write_excel_sync(file_path: Path, sheets: dict[str, list[dict]]) -> None:
    wb = Workbook()
    wb.remove(wb.active)  # Remove default sheet
    for sheet_name, data in sheets.items():
        ws = wb.create_sheet(sheet_name)
        if data:
            headers = list(data[0].keys())
            ws.append(headers)
            for row_dict in data:
                ws.append([row_dict.get(h) for h in headers])
    wb.save(file_path)
```

---

## 2. asyncio.to_thread() Integration Pattern

### Decision
Wrap all openpyxl operations in asyncio.to_thread() at the ExcelService level.

### Rationale
- openpyxl is synchronous (no native async support)
- asyncio.to_thread() moves blocking I/O to a thread pool without blocking event loop
- Maintains async contract required by Constitution VIII
- Keeps UI responsive during large file operations

### Implementation Pattern

```python
import asyncio
from pathlib import Path

class ExcelService:
    async def read_stories_from_file(self, file_path: Path) -> ExcelReadResult:
        """Le arquivo Excel de forma assincrona."""
        return await asyncio.to_thread(self._read_stories_sync, file_path)

    def _read_stories_sync(self, file_path: Path) -> ExcelReadResult:
        """Operacao sincrona de leitura - executada em thread separada."""
        # openpyxl operations here
        ...

    async def write_workbook(self, file_path: Path, data: ExcelExportData) -> None:
        """Escreve arquivo Excel de forma assincrona."""
        await asyncio.to_thread(self._write_workbook_sync, file_path, data)

    def _write_workbook_sync(self, file_path: Path, data: ExcelExportData) -> None:
        """Operacao sincrona de escrita - executada em thread separada."""
        # openpyxl operations here
        ...
```

### Thread Safety Considerations
- Each operation creates its own Workbook instance (no shared state)
- File path passed as parameter, no instance-level file handles
- Safe for concurrent import/export operations (different files)

---

## 3. Excel File Validation Strategy

### Decision
Two-level validation: (1) structural validation in ExcelService, (2) business validation in ImportExcelUseCase.

### Rationale
Separates concerns per Clean Architecture:
- ExcelService (Infrastructure): file format, headers presence, basic types
- ImportExcelUseCase (Application): SP values, dependency cycles, ID formats

### Validation Layers

#### Layer 1: ExcelService (Structural)
| Check | Error Type | Message |
|-------|------------|---------|
| File extension | Reject | "Formato de arquivo nao suportado. Use .xlsx" |
| File corrupt/invalid | Reject | "Arquivo invalido ou corrompido" |
| Empty file (no rows) | Warning | "Arquivo vazio" |
| Missing required column | Reject | "Coluna obrigatoria [NOME] nao encontrada na linha 1" |

#### Layer 2: ImportExcelUseCase (Business)
| Check | Error Type | Message |
|-------|------------|---------|
| SP not in {3,5,8,13} | Warning (skip row) | "Linha [N]: Story Points invalido ([VALOR]), linha ignorada" |
| Empty Nome | Warning (skip row) | "Linha [N]: Nome vazio, linha ignorada" |
| Dependency cycle | Reject all | "Ciclo de dependencia detectado: [CAMINHO]. Nenhum dado foi importado" |
| Dependency not found | Warning | "Linha [N]: Dependencia [ID] nao encontrada, ignorada" |
| ID empty + Componente empty | Warning (skip row) | "Linha [N]: ID e Componente vazios, linha ignorada" |

### Header Validation

Required headers (case-sensitive, exact order per FR-110):
```
ID | Componente | Nome | SP | Feature | Dependencias
```

Additional columns on export (FR-117):
```
ID | Componente | Nome | SP | Status | Feature | Dependencias | Desenvolvedor | Data Inicio | Data Fim
```

---

## 4. Two-Pass Import Algorithm

### Decision
Process import in two passes: (1) create stories/features, (2) create dependencies.

### Rationale
Per ADR-003 in spec:
- Dependencies reference IDs that may not exist during first row read
- Two passes ensure all IDs exist before validating dependency graph
- Allows cycle detection on complete graph before persisting dependencies
- Facilitates clean rollback if cycle detected

### Algorithm

```
PASS 1: Create Entities
+-------------------------------------------------------------+
| For each row in Excel:                                      |
|   1. Validate required fields (Nome, Componente if no ID)   |
|   2. Validate SP in {3,5,8,13}                              |
|   3. If ID empty: generate ID = COMPONENTE-NNN              |
|   4. If Feature exists: lookup feature_id                   |
|   5. If Feature not exists: create Feature(wave=1)          |
|   6. Create Story with all fields except dependencies       |
|   7. Collect (row_number, story_id, dependency_ids_string)  |
|   8. Track warnings for skipped rows                        |
+-------------------------------------------------------------+

BETWEEN PASSES: Build Dependency Graph
+-------------------------------------------------------------+
| 1. Get existing dependencies from database                  |
| 2. Parse collected dependency_ids strings                   |
| 3. Build temporary graph: existing + new dependencies       |
| 4. Run DependencyService.detect_cycle() on full graph       |
| 5. If cycle found: ROLLBACK all, return error               |
+-------------------------------------------------------------+

PASS 2: Create Dependencies
+-------------------------------------------------------------+
| For each (story_id, depends_on_id) in new dependencies:     |
|   1. Check if depends_on_id exists (in DB or created)       |
|   2. If not exists: add warning, skip this dependency       |
|   3. If exists: add dependency via StoryDependencyRepo      |
+-------------------------------------------------------------+

COMMIT: Persist all changes
+-------------------------------------------------------------+
| 1. UnitOfWork.commit()                                      |
| 2. Return ImportExcelOutputDTO with counts and warnings     |
+-------------------------------------------------------------+
```

### Rollback Scenarios
| Scenario | Action |
|----------|--------|
| Missing required header | Reject before any write |
| Cycle detected | Rollback all (UoW rollback) |
| IO error during write | Rollback all (UoW rollback) |
| Invalid SP / missing dependency | Warning only, continue |

---

## 5. ID Generation Strategy

### Decision
Reuse existing StoryService.generate_story_id(component) for auto-generating IDs during import.

### Rationale
Per ADR-002:
- Maintains consistency with system-wide ID format (COMPONENT-NNN)
- Reuses existing tested logic
- Uses Componente column from Excel when ID is empty

### Implementation

```python
async def _generate_id_if_needed(
    self,
    row: dict,
    story_service: StoryService
) -> str:
    """Gera ID automatico se coluna ID estiver vazia."""
    if row.get("ID"):
        return str(row["ID"]).strip()

    component = row.get("Componente", "").strip()
    if not component:
        raise ValueError("ID e Componente vazios - impossivel gerar ID")

    return await story_service.generate_story_id(component)
```

---

## 6. Export Format Specification

### Decision
Export creates single .xlsx file with three worksheets: Stories, Developers, Features.

### Rationale
Per ADR-008:
- Single file = single backup unit
- Clear separation by entity type
- Native openpyxl multi-sheet support
- Roundtrip compatible with import format

### Worksheet Schemas

#### Stories Sheet (FR-117)
| Column | Type | Source |
|--------|------|--------|
| ID | String | story.id |
| Componente | String | story.component |
| Nome | String | story.name |
| SP | Integer | story.story_points |
| Status | String | story.status.value |
| Feature | String | feature.name (lookup) |
| Dependencias | String | "ID1;ID2;ID3" (join) |
| Desenvolvedor | String | developer.name (lookup) |
| Data Inicio | Date | story.start_date |
| Data Fim | Date | story.end_date |

#### Developers Sheet (FR-118)
| Column | Type | Source |
|--------|------|--------|
| ID | Integer | developer.id |
| Nome | String | developer.name |

#### Features Sheet (FR-119)
| Column | Type | Source |
|--------|------|--------|
| ID | Integer | feature.id |
| Nome | String | feature.name |
| Wave | Integer | feature.wave |

---

## 7. Error Handling Strategy

### Decision
Use dedicated exceptions for Excel operations, following existing exception hierarchy.

### Rationale
Per Constitution XVI:
- Clear exception hierarchy for different error types
- Messages in Portuguese for end users
- Infrastructure errors converted to application exceptions

### Exception Hierarchy

```python
# New exceptions for Excel operations
class ExcelException(BacklogManagerException):
    """Base exception for Excel operations."""
    pass

class ExcelFileNotFoundException(ExcelException):
    """Arquivo Excel nao encontrado."""
    pass

class ExcelFileCorruptedException(ExcelException):
    """Arquivo Excel corrompido ou formato invalido."""
    pass

class ExcelMissingHeaderException(ExcelException):
    """Coluna obrigatoria ausente no arquivo Excel."""
    pass

class ExcelCycleDetectedException(ExcelException):
    """Ciclo de dependencia detectado no arquivo importado."""
    pass

class ExcelPermissionException(ExcelException):
    """Sem permissao para ler/escrever arquivo Excel."""
    pass
```

### Error Handling Flow

```
openpyxl Exception -> ExcelService catches -> Converts to ExcelException
                                           |
                          ImportExcelUseCase catches -> Logs error
                                                     |
                                    Returns ImportExcelOutputDTO with errors
                                                     |
                              ExcelViewModel catches -> Emits error signal
                                                     |
                                        MainWindow shows QMessageBox
```

---

## 8. Progress Reporting Strategy

### Decision
Report progress via ViewModel signal at row-level granularity during import.

### Rationale
Per FR-061:
- Users need feedback for large files (100+ rows)
- Row-level progress is meaningful and measurable
- QProgressDialog integration via signals

### Implementation

```python
class ExcelViewModel(QObject):
    progress_updated = Signal(int)  # 0-100 percentage

class ImportExcelUseCase:
    def __init__(
        self,
        uow: UnitOfWork,
        excel_service: ExcelServiceProtocol,
        progress_callback: Callable[[int], None] | None = None
    ):
        self._progress_callback = progress_callback

    async def execute(self, input_dto: ImportExcelInputDTO) -> ImportExcelOutputDTO:
        rows = await self._excel_service.read_stories_from_file(input_dto.file_path)
        total = len(rows)

        for i, row in enumerate(rows, 1):
            # Process row...
            if self._progress_callback:
                self._progress_callback(int(i * 100 / total))
```

---

## Summary

All research items have been resolved. Key decisions:

1. **openpyxl ^3.1.0** as Excel library
2. **asyncio.to_thread()** for non-blocking I/O
3. **Two-level validation** (structural + business)
4. **Two-pass import** (entities then dependencies)
5. **StoryService.generate_story_id()** for auto ID generation
6. **Multi-sheet export** (Stories, Developers, Features)
7. **ExcelException hierarchy** for error handling
8. **Row-level progress** via ViewModel signals

No NEEDS CLARIFICATION items remaining.
