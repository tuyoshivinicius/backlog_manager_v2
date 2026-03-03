"""DTOs for Excel import operations."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_validator


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
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def __init__(self, **data: Any) -> None:
        """Initialize with default empty lists for warnings and errors."""
        if "warnings" not in data:
            data["warnings"] = []
        if "errors" not in data:
            data["errors"] = []
        super().__init__(**data)

    @property
    def success(self) -> bool:
        """Retorna True se import foi bem-sucedido (sem erros criticos)."""
        return len(self.errors) == 0
