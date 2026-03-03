# Data Model: EP-009 Excel Integration

**Feature**: EP-009 Excel Integration
**Date**: 2026-03-03
**Status**: Complete

## Overview

EP-009 does not introduce new domain entities. Excel integration is an I/O concern handled at the Infrastructure and Application layers. This document defines the DTOs and data structures used for Excel import/export operations.

## Existing Entities (No Changes)

The following domain entities are used by Excel operations but remain unchanged:

| Entity | Location | Used By |
|--------|----------|---------|
| Story | `domain/entities/story.py` | Import creates, Export reads |
| Developer | `domain/entities/developer.py` | Export reads |
| Feature | `domain/entities/feature.py` | Import creates/reads, Export reads |

## New Data Transfer Objects

### 1. ExcelReadResult

**Location**: `application/dto/excel/import_excel_dto.py`

Data structure returned by ExcelService.read_stories_from_file().

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ExcelReadResult:
    """Resultado da leitura de arquivo Excel.

    Attributes:
        rows: Lista de dicionarios com dados de cada linha.
            Chaves sao os headers da primeira linha.
        warnings: Lista de avisos gerados durante leitura.
    """
    rows: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| rows | list[dict[str, Any]] | Each dict represents a row with header names as keys |
| warnings | list[str] | Non-critical issues found during reading |

---

### 2. ExcelExportData

**Location**: `application/dto/excel/export_excel_dto.py`

Data structure passed to ExcelService.write_workbook().

```python
from dataclasses import dataclass, field
from typing import Any

@dataclass
class ExcelExportData:
    """Dados para exportacao em arquivo Excel.

    Attributes:
        stories: Lista de dicionarios com dados das historias.
        developers: Lista de dicionarios com dados dos desenvolvedores.
        features: Lista de dicionarios com dados das features.
    """
    stories: list[dict[str, Any]] = field(default_factory=list)
    developers: list[dict[str, Any]] = field(default_factory=list)
    features: list[dict[str, Any]] = field(default_factory=list)
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| stories | list[dict[str, Any]] | Story data for "Stories" worksheet |
| developers | list[dict[str, Any]] | Developer data for "Developers" worksheet |
| features | list[dict[str, Any]] | Feature data for "Features" worksheet |

---

### 3. ImportExcelInputDTO

**Location**: `application/dto/excel/import_excel_dto.py`

Input for ImportExcelUseCase.execute().

```python
from pathlib import Path
from pydantic import BaseModel, field_validator

class ImportExcelInputDTO(BaseModel):
    """DTO de entrada para importacao de arquivo Excel.

    Attributes:
        file_path: Caminho absoluto para o arquivo .xlsx.
    """
    file_path: Path

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: Path) -> Path:
        """Valida que o caminho existe e tem extensao .xlsx."""
        if not v.exists():
            raise ValueError(f"Arquivo nao encontrado: {v}")
        if v.suffix.lower() != ".xlsx":
            raise ValueError("Formato de arquivo nao suportado. Use .xlsx")
        return v
```

**Fields**:
| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| file_path | Path | Must exist, must be .xlsx | Absolute path to Excel file |

---

### 4. ImportExcelOutputDTO

**Location**: `application/dto/excel/import_excel_dto.py`

Output from ImportExcelUseCase.execute().

```python
from pydantic import BaseModel

class ImportExcelOutputDTO(BaseModel):
    """DTO de saida para importacao de arquivo Excel.

    Attributes:
        stories_imported: Numero de historias importadas com sucesso.
        features_created: Numero de features criadas automaticamente.
        warnings: Lista de avisos nao-criticos (linhas puladas, etc).
        errors: Lista de erros criticos (vazio se sucesso).
    """
    stories_imported: int = 0
    features_created: int = 0
    warnings: list[str] = []
    errors: list[str] = []

    @property
    def success(self) -> bool:
        """Retorna True se import foi bem-sucedido (sem erros criticos)."""
        return len(self.errors) == 0
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| stories_imported | int | Count of successfully imported stories |
| features_created | int | Count of features auto-created during import |
| warnings | list[str] | Non-critical warnings (skipped rows, missing deps) |
| errors | list[str] | Critical errors (empty if successful) |

---

### 5. ExportExcelInputDTO

**Location**: `application/dto/excel/export_excel_dto.py`

Input for ExportExcelUseCase.execute().

```python
from pathlib import Path
from pydantic import BaseModel, field_validator

class ExportExcelInputDTO(BaseModel):
    """DTO de entrada para exportacao de arquivo Excel.

    Attributes:
        file_path: Caminho absoluto para o arquivo .xlsx de destino.
    """
    file_path: Path

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: Path) -> Path:
        """Valida que o caminho tem extensao .xlsx."""
        if v.suffix.lower() != ".xlsx":
            raise ValueError("Formato de arquivo nao suportado. Use .xlsx")
        return v
```

**Fields**:
| Field | Type | Validation | Description |
|-------|------|------------|-------------|
| file_path | Path | Must be .xlsx extension | Absolute path for output file |

---

### 6. ExportExcelOutputDTO

**Location**: `application/dto/excel/export_excel_dto.py`

Output from ExportExcelUseCase.execute().

```python
from pathlib import Path
from pydantic import BaseModel

class ExportExcelOutputDTO(BaseModel):
    """DTO de saida para exportacao de arquivo Excel.

    Attributes:
        file_path: Caminho do arquivo criado.
        stories_exported: Numero de historias exportadas.
        developers_exported: Numero de desenvolvedores exportados.
        features_exported: Numero de features exportadas.
    """
    file_path: Path
    stories_exported: int = 0
    developers_exported: int = 0
    features_exported: int = 0
```

**Fields**:
| Field | Type | Description |
|-------|------|-------------|
| file_path | Path | Path to the created Excel file |
| stories_exported | int | Count of exported stories |
| developers_exported | int | Count of exported developers |
| features_exported | int | Count of exported features |

---

## Excel File Format Schemas

### Import Schema (Stories Sheet)

Headers expected on row 1 (case-sensitive, per FR-110):

| Column | Required | Type | Validation |
|--------|----------|------|------------|
| ID | No | String | If empty, auto-generated from Componente |
| Componente | Conditional | String | Required if ID is empty |
| Nome | Yes | String | Non-empty |
| SP | Yes | Integer | Must be 3, 5, 8, or 13 |
| Feature | No | String | Created if not exists (wave=1) |
| Dependencias | No | String | IDs separated by semicolon (;) |
n**Note**: Desenvolvedor column in export is informational only; allocations are recalculated by AllocationEngine, not imported directly.

### Export Schema (Stories Sheet)

Headers on row 1 (per FR-117):

| Column | Type | Source |
|--------|------|--------|
| ID | String | story.id |
| Componente | String | story.component |
| Nome | String | story.name |
| SP | Integer | story.story_points |
| Status | String | story.status.value |
| Feature | String | feature.name or empty |
| Dependencias | String | IDs joined with ";" |
| Desenvolvedor | String | developer.name or empty |
| Data Inicio | Date/None | story.start_date |
| Data Fim | Date/None | story.end_date |

### Export Schema (Developers Sheet)

Headers on row 1 (per FR-118):

| Column | Type | Source |
|--------|------|--------|
| ID | Integer | developer.id |
| Nome | String | developer.name |

### Export Schema (Features Sheet)

Headers on row 1 (per FR-119):

| Column | Type | Source |
|--------|------|--------|
| ID | Integer | feature.id |
| Nome | String | feature.name |
| Wave | Integer | feature.wave |

---

## State Transitions

### Import State Machine

```
START
  |
  v
[Validate Headers] --missing--> ERROR: "Coluna obrigatoria ausente"
  |
  ok
  v
[Pass 1: Create Stories/Features] --row invalid--> WARNING (skip row)
  |
  all rows processed
  v
[Validate Dependency Graph] --cycle detected--> ROLLBACK + ERROR
  |
  no cycles
  v
[Pass 2: Create Dependencies] --dep not found--> WARNING (skip dep)
  |
  v
[Commit] --> SUCCESS with ImportExcelOutputDTO
```

### Export State Machine

```
START
  |
  v
[Fetch Stories] --> [Fetch Developers] --> [Fetch Features]
  |
  v
[Build ExcelExportData]
  |
  v
[Write to File] --permission error--> ERROR: "Sem permissao"
  |
  ok
  v
SUCCESS with ExportExcelOutputDTO
```

---

## Validation Rules
n### Header Validation Rules (ExcelService)

| Rule | Specification |
|------|---------------|
| Case-sensitivity | Headers MUST match exactly: "ID", "Componente", "Nome", "SP", "Feature", "Dependencias" |
| Order | Headers MUST appear in columns A-F in the specified order |
| Row | Headers MUST be in row 1 |


### Row-Level Validation (ImportExcelUseCase)

| Field | Rule | On Failure |
|-------|------|------------|
| ID | If empty, Componente must be non-empty | Warning, skip row |
| ID | Must not already exist in database | Warning, skip row |
| Componente | Max 50 chars, alphanumeric + dash | Warning, skip row |
| Nome | Non-empty, max 200 chars | Warning, skip row |
| SP | Integer in {3, 5, 8, 13} | Warning, skip row |
| Feature | Max 100 chars | Warning, skip row |
| Dependencias | Valid ID format, semicolon-separated | Warning per invalid ID |

### File-Level Validation (ExcelService)

| Check | On Failure |
|-------|------------|
| Extension is .xlsx | Reject: "Formato nao suportado" |
| File is readable | Reject: "Arquivo invalido ou corrompido. Verifique o formato" |
| Required headers present | Reject: "Coluna obrigatoria ausente" |

---

## Relationships

```
+-------------------+      reads      +------------------+
|  ImportExcelDTO   | <-------------- | ImportExcelUC    |
+-------------------+                 +------------------+
                                             |
                                             | uses
                                             v
+-------------------+      returns    +------------------+
|  ExcelReadResult  | <-------------- | ExcelService     |
+-------------------+                 +------------------+
                                             ^
                                             | writes
+-------------------+      passes     +------------------+
|  ExcelExportData  | --------------> | ExcelService     |
+-------------------+                 +------------------+
        ^
        | builds
+-------------------+
|  ExportExcelUC    |
+-------------------+
```

## File Locations Summary

| DTO | File Path |
|-----|-----------|
| ExcelReadResult | src/backlog_manager/application/dto/excel/import_excel_dto.py |
| ImportExcelInputDTO | src/backlog_manager/application/dto/excel/import_excel_dto.py |
| ImportExcelOutputDTO | src/backlog_manager/application/dto/excel/import_excel_dto.py |
| ExcelExportData | src/backlog_manager/application/dto/excel/export_excel_dto.py |
| ExportExcelInputDTO | src/backlog_manager/application/dto/excel/export_excel_dto.py |
| ExportExcelOutputDTO | src/backlog_manager/application/dto/excel/export_excel_dto.py |
