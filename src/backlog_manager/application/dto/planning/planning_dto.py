"""DTOs for planning CRUD operations."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, field_validator


class CreatePlanningInput(BaseModel):
    """Input DTO for creating a new planning."""

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate planning name."""
        if not v or not v.strip():
            raise ValueError("Nome do planejamento nao pode ser vazio")
        if len(v) > 200:
            raise ValueError("Nome do planejamento nao pode exceder 200 caracteres")
        return v.strip()


class UpdatePlanningInput(BaseModel):
    """Input DTO for updating a planning."""

    planning_id: int
    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate planning name."""
        if not v or not v.strip():
            raise ValueError("Nome do planejamento nao pode ser vazio")
        if len(v) > 200:
            raise ValueError("Nome do planejamento nao pode exceder 200 caracteres")
        return v.strip()


class PlanningOutput(BaseModel):
    """Output DTO for a single planning."""

    id: int
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None


class PlanningListItem(BaseModel):
    """Output DTO for planning list with story count."""

    id: int
    name: str
    story_count: int = 0
    updated_at: datetime | None = None
