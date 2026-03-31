"""Input/Output DTOs for GetDeveloperAvailabilityUseCase."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, Field

from backlog_manager.application.dto.allocation.developer_availability_dto import (
    DeveloperAvailabilityDTO,
)


class GetDeveloperAvailabilityInputDTO(BaseModel):
    """Input para consulta de disponibilidade de desenvolvedores."""

    story_id: str
    candidate_start_date: date
    velocity: float = Field(gt=0)
    allocation_criteria: str = "LOAD_BALANCING"


class GetDeveloperAvailabilityOutputDTO(BaseModel):
    """Resultado da consulta de disponibilidade de desenvolvedores."""

    developers: list[DeveloperAvailabilityDTO]
    recommended_developer_id: int | None
    story_start_date: date
    story_end_date: date
