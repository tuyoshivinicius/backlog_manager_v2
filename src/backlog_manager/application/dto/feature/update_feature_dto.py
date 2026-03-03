"""Update Feature DTOs."""

from __future__ import annotations

from pydantic import BaseModel, field_validator


class UpdateFeatureInputDTO(BaseModel):
    """DTO para atualizacao de feature.

    Suporta atualizacao parcial (nome e/ou wave).
    """

    feature_id: int
    name: str | None = None
    wave: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Valida nome nao vazio e tamanho maximo se fornecido."""
        if v is None:
            return None
        if not v or not v.strip():
            raise ValueError("Nome da feature nao pode ser vazio")
        if len(v) > 100:
            raise ValueError("Nome da feature nao pode exceder 100 caracteres")
        return v.strip()

    @field_validator("wave")
    @classmethod
    def validate_wave(cls, v: int | None) -> int | None:
        """Valida wave > 0 se fornecida."""
        if v is None:
            return None
        if v <= 0:
            raise ValueError(f"Wave deve ser > 0: {v}")
        return v
