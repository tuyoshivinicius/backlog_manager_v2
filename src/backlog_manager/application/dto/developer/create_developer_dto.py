"""Create Developer DTOs."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class CreateDeveloperInputDTO(BaseModel):
    """DTO para criacao de desenvolvedor.

    Apenas campo nome obrigatorio para criacao.
    ID e gerado automaticamente pelo repositorio.
    """

    name: str

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida nome nao vazio e tamanho maximo."""
        if not v or not v.strip():
            raise ValueError("Nome do desenvolvedor nao pode ser vazio")
        if len(v) > 100:
            raise ValueError("Nome do desenvolvedor nao pode exceder 100 caracteres")
        return v.strip()
