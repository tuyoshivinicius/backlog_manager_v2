"""Delete Developer DTOs."""

from __future__ import annotations

from pydantic import BaseModel


class DeleteDeveloperOutputDTO(BaseModel):
    """DTO de saida para delecao de desenvolvedor.

    Retorna ID deletado e quantidade de historias desalocadas.
    """

    developer_id: int
    stories_unassigned: int
