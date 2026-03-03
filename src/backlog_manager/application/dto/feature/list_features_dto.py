"""List Features DTOs."""

from __future__ import annotations

from pydantic import BaseModel

from backlog_manager.application.dto.feature.feature_output_dto import FeatureOutputDTO


class ListFeaturesOutputDTO(BaseModel):
    """DTO de saida para listagem de features.

    Contem lista de features ordenadas por wave.
    """

    features: list[FeatureOutputDTO]
