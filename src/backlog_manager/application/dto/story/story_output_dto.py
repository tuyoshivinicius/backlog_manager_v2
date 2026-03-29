"""Story output DTO."""

from __future__ import annotations

from datetime import date
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Story


class StoryOutputDTO(BaseModel):
    """DTO para saida de historia.

    Representa uma historia completa para retorno em use cases.
    """

    id: str
    component: str
    name: str
    story_points: int
    priority: int
    status: str
    duration: int | None
    start_date: date | None
    end_date: date | None
    developer_id: int | None
    feature_id: int | None
    developer_name: str | None = None
    feature_name: str | None = None
    wave: int = 0
    dependency_ids: list[str] = Field(default_factory=list)

    @classmethod
    def from_entity(cls, story: Story) -> StoryOutputDTO:
        """Converte entidade Story para DTO.

        Args:
            story: Entidade Story.

        Returns:
            DTO com dados da historia.
        """
        return cls(
            id=story.id,
            component=story.component,
            name=story.name,
            story_points=int(story.story_points),
            priority=story.priority,
            status=str(story.status),
            duration=story.duration,
            start_date=story.start_date,
            end_date=story.end_date,
            developer_id=story.developer_id,
            feature_id=story.feature_id,
        )
