"""DTOs for full schedule calculation."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class CalculateScheduleInputDTO(BaseModel):
    """Input DTO for full schedule calculation.

    Attributes:
        velocity: Team velocity in story points per day.
        start_date: Project start date.
        recalculate_all: Whether to recalculate all stories (default: True).
    """

    velocity: float = Field(gt=0, description="Velocidade em SP/dia")
    start_date: date = Field(description="Data de inicio do projeto")
    recalculate_all: bool = Field(
        default=True, description="Recalcular todas as historias"
    )


class CalculateScheduleOutputDTO(BaseModel):
    """Output DTO for full schedule calculation.

    Attributes:
        success: Whether calculation completed successfully.
        stories_processed: Number of stories processed.
        stories_updated: Number of stories updated.
        warnings: List of warnings (e.g., skipped stories).
    """

    success: bool = Field(description="Calculo completou com sucesso")
    stories_processed: int = Field(description="Numero de historias processadas")
    stories_updated: int = Field(description="Numero de historias atualizadas")
    warnings: list[str] = Field(default_factory=list, description="Lista de avisos")
