"""DTOs for story dates calculation."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field


class CalculateStoryDatesInputDTO(BaseModel):
    """Input DTO for story dates calculation.

    Attributes:
        story_id: ID of the story (format: COMPONENT-NNN).
        velocity: Team velocity in story points per day.
        project_start_date: Project start date.
    """

    story_id: str = Field(pattern=r"^[A-Z]+-\d{3}$", description="ID da historia")
    velocity: float = Field(gt=0, description="Velocidade em SP/dia")
    project_start_date: date = Field(description="Data de inicio do projeto")


class CalculateStoryDatesOutputDTO(BaseModel):
    """Output DTO for story dates calculation.

    Attributes:
        story_id: ID of the story.
        start_date: Calculated start date.
        end_date: Calculated end date.
        duration: Duration in workdays.
    """

    story_id: str = Field(description="ID da historia")
    start_date: date = Field(description="Data de inicio calculada")
    end_date: date = Field(description="Data de termino calculada")
    duration: int = Field(description="Duracao em dias uteis")
