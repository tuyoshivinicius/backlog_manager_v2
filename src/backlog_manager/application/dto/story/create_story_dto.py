"""Create Story DTOs."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class CreateStoryInputDTO(BaseModel):
    """DTO para criacao de historia.

    Apenas campos obrigatorios para criacao.
    ID e prioridade sao gerados automaticamente.
    """

    component: str
    name: str
    story_points: int
    feature_id: int | None = None

    @field_validator("component")
    @classmethod
    def validate_component(cls, v: str) -> str:
        """Valida componente nao vazio e tamanho maximo."""
        if not v or not v.strip():
            raise ValueError("Componente nao pode ser vazio")
        if len(v) > 50:
            raise ValueError("Componente nao pode exceder 50 caracteres")
        return v.strip().upper()

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida nome nao vazio e tamanho maximo."""
        if not v or not v.strip():
            raise ValueError("Nome nao pode ser vazio")
        if len(v) > 200:
            raise ValueError("Nome nao pode exceder 200 caracteres")
        return v.strip()

    @field_validator("story_points")
    @classmethod
    def validate_story_points(cls, v: int) -> int:
        """Valida story points no conjunto Fibonacci permitido."""
        allowed = (3, 5, 8, 13)
        if v not in allowed:
            raise ValueError(f"Story points deve ser um de {allowed}")
        return v
