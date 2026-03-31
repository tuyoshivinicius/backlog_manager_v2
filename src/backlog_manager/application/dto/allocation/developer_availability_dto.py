"""DTOs for developer availability in manual allocation."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel


class BlockingStoryDTO(BaseModel):
    """Historia que bloqueia a disponibilidade de um desenvolvedor."""

    story_id: str
    story_name: str
    start_date: date
    end_date: date


class DeveloperAvailabilityDTO(BaseModel):
    """Disponibilidade de um desenvolvedor para alocacao manual."""

    developer_id: int
    developer_name: str
    is_available: bool
    is_recommended: bool
    blocking_stories: list[BlockingStoryDTO]
    story_count: int
