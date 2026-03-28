"""DTOs for duration calculation."""

from __future__ import annotations

from pydantic import BaseModel, Field, field_validator


class CalculateDurationInputDTO(BaseModel):
    """Input DTO for duration calculation.

    Attributes:
        story_points: Story points of the story (3, 5, 8, or 13).
        velocity: Team velocity in story points per day.
    """

    story_points: int = Field(description="Story points")
    velocity: float = Field(gt=0, description="Velocidade em SP/dia")

    @field_validator("story_points")
    @classmethod
    def validate_story_points(cls, v: int) -> int:
        """Validate story points are in valid Fibonacci sequence."""
        if v not in {3, 5, 8, 13}:
            raise ValueError("Story points deve ser 3, 5, 8 ou 13")
        return v


class CalculateDurationOutputDTO(BaseModel):
    """Output DTO for duration calculation.

    Attributes:
        duration: Calculated duration in workdays.
        formula: Formula used for calculation.
    """

    duration: int = Field(description="Duracao calculada em dias uteis")
    formula: str = Field(description="Formula usada para o calculo")
