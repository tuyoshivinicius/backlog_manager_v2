"""Feature output DTOs."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pydantic import BaseModel

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Feature


class FeatureOutputDTO(BaseModel):
    """DTO de saida para feature.

    Representa dados de uma feature para resposta.
    """

    id: int
    name: str
    wave: int

    @classmethod
    def from_entity(cls, feature: Feature) -> FeatureOutputDTO:
        """Cria DTO a partir de entidade Feature.

        Args:
            feature: Entidade Feature com ID preenchido.

        Returns:
            DTO com dados da feature.
        """
        if feature.id is None:
            raise ValueError("Feature must have an ID to create output DTO")
        return cls(id=feature.id, name=feature.name, wave=feature.wave)
