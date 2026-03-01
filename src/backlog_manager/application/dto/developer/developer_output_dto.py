"""Developer output DTOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Developer


class DeveloperOutputDTO(BaseModel):
    """DTO de saida para desenvolvedor.

    Representa dados de um desenvolvedor para resposta.
    """

    id: int
    name: str

    @classmethod
    def from_entity(cls, developer: Developer) -> DeveloperOutputDTO:
        """Cria DTO a partir de entidade Developer.

        Args:
            developer: Entidade Developer com ID preenchido.

        Returns:
            DTO com dados do desenvolvedor.
        """
        if developer.id is None:
            raise ValueError("Developer must have an ID to create output DTO")
        return cls(id=developer.id, name=developer.name)
