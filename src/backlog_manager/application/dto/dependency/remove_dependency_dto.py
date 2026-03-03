"""DTOs for RemoveDependency use case."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class RemoveDependencyInputDTO(BaseModel):
    """Input DTO para remocao de dependencia.

    Attributes:
        story_id: ID da historia que depende.
        depends_on_id: ID da historia da qual depende.
    """

    story_id: str
    depends_on_id: str

    @field_validator("story_id", "depends_on_id", mode="before")
    @classmethod
    def validate_not_empty(cls, value: str) -> str:
        """Valida que IDs nao sao vazios."""
        if not value or not value.strip():
            raise ValueError("ID nao pode ser vazio")
        return value.strip()


class RemoveDependencyOutputDTO(BaseModel):
    """Output DTO para remocao de dependencia.

    Attributes:
        success: Indica se a operacao foi bem sucedida.
    """

    success: bool
