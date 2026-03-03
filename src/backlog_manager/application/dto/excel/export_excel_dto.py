"""DTOs for Excel export operations."""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from pydantic import BaseModel, field_validator


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
