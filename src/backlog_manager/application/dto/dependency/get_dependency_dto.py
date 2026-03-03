"""DTOs for GetDependencies and GetDependents use cases."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class GetDependenciesInputDTO(BaseModel):
    """Input DTO para consulta de dependencias.

    Attributes:
        story_id: ID da historia para consultar dependencias.
    """

    story_id: str

    @field_validator("story_id", mode="before")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Valida que ID nao e vazio."""
        if not value or not value.strip():
            raise ValueError("ID nao pode ser vazio")
        return value.strip()


class GetDependenciesOutputDTO(BaseModel):
    """Output DTO para consulta de dependencias.

    Attributes:
        story_id: ID da historia consultada.
        dependencies: Lista de IDs das historias das quais depende.
    """

    story_id: str
    dependencies: list[str]


class GetDependentsInputDTO(BaseModel):
    """Input DTO para consulta de dependentes.

    Attributes:
        story_id: ID da historia para consultar dependentes.
    """

    story_id: str

    @field_validator("story_id", mode="before")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Valida que ID nao e vazio."""
        if not value or not value.strip():
            raise ValueError("ID nao pode ser vazio")
        return value.strip()


class GetDependentsOutputDTO(BaseModel):
    """Output DTO para consulta de dependentes.

    Attributes:
        story_id: ID da historia consultada.
        dependents: Lista de IDs das historias que dependem desta.
    """

    story_id: str
    dependents: list[str]
