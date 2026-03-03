"""DTOs for AddDependency use case."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class AddDependencyInputDTO(BaseModel):
    """Input DTO para adicao de dependencia.

    Attributes:
        story_id: ID da historia que vai depender.
        depends_on_id: ID da historia da qual vai depender.
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


class InvalidWaveDependencyWarningDTO(BaseModel):
    """DTO de warning para dependencia entre waves.

    Retornado quando uma historia depende de outra
    em wave posterior (nao bloqueia, apenas avisa).

    Attributes:
        story_id: ID da historia que depende.
        depends_on_id: ID da historia da qual depende.
        story_wave: Wave da historia que depende.
        depends_on_wave: Wave da historia da qual depende.
        message: Mensagem de warning para exibicao.
    """

    story_id: str
    depends_on_id: str
    story_wave: int
    depends_on_wave: int
    message: str


class AddDependencyOutputDTO(BaseModel):
    """Output DTO para adicao de dependencia.

    Attributes:
        success: Indica se a operacao foi bem sucedida.
        story_id: ID da historia que depende.
        depends_on_id: ID da historia da qual depende.
        warning: Warning opcional para dependencia entre waves.
    """

    success: bool
    story_id: str
    depends_on_id: str
    warning: InvalidWaveDependencyWarningDTO | None = None
