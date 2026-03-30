"""DTOs for planning reset operations."""

from __future__ import annotations

from pydantic import BaseModel


class ResetPlanningInputDTO(BaseModel):
    """Input DTO for reset planning use case. No parameters needed."""

    pass


class ResetPlanningOutputDTO(BaseModel):
    """Output DTO with reset operation results."""

    success: bool
    stories_reset: int
    stories_with_dates_cleared: int
    stories_with_developer_cleared: int
    warnings: list[str] = []


class CountAffectedStoriesOutputDTO(BaseModel):
    """Output DTO with counts of stories that would be affected."""

    total: int
    with_dates: int
    with_developer: int
