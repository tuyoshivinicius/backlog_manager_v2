"""Create Feature DTOs."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class CreateFeatureInputDTO(BaseModel):
    """DTO para criacao de feature.

    Campos obrigatorios para criacao.
    ID e gerado automaticamente pelo repositorio.
    """

    name: str
    wave: int

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Valida nome nao vazio e tamanho maximo."""
        if not v or not v.strip():
            raise ValueError("Nome da feature nao pode ser vazio")
        if len(v) > 100:
            raise ValueError("Nome da feature nao pode exceder 100 caracteres")
        return v.strip()

    @field_validator("wave")
    @classmethod
    def validate_wave(cls, v: int) -> int:
        """Valida wave > 0."""
        if v <= 0:
            raise ValueError(f"Wave deve ser > 0: {v}")
        return v
