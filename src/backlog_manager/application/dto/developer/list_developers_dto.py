"""List Developers DTOs."""

from __future__ import annotations

from pydantic import BaseModel

from backlog_manager.application.dto.developer.developer_output_dto import (
    DeveloperOutputDTO,
)


class ListDevelopersOutputDTO(BaseModel):
    """DTO de saida para listagem de desenvolvedores.

    Contem lista de desenvolvedores ordenados por nome.
    """

    developers: list[DeveloperOutputDTO]
