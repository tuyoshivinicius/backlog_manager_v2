"""Edit Story DTOs."""

from __future__ import annotations

from datetime import date

from pydantic import BaseModel, field_validator


class EditStoryInputDTO(BaseModel):
    """DTO para edicao de historia.

    Todos os campos sao opcionais - apenas os fornecidos serao atualizados.
    """

    story_id: str
    name: str | None = None
    story_points: int | None = None
    status: str | None = None
    duration: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    feature_id: int | None = None
    developer_id: int | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str | None) -> str | None:
        """Valida nome nao vazio e tamanho maximo."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError("Nome nao pode ser vazio")
        if len(v) > 200:
            raise ValueError("Nome nao pode exceder 200 caracteres")
        return v.strip()

    @field_validator("story_points")
    @classmethod
    def validate_story_points(cls, v: int | None) -> int | None:
        """Valida story points no conjunto Fibonacci permitido."""
        if v is None:
            return v
        allowed = (3, 5, 8, 13)
        if v not in allowed:
            raise ValueError(f"Story points deve ser um de {allowed}")
        return v

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """Valida status valido."""
        if v is None:
            return v
        allowed = ("BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO")
        if v.upper() not in allowed:
            raise ValueError(f"Status deve ser um de {allowed}")
        return v.upper()

    @field_validator("duration")
    @classmethod
    def validate_duration(cls, v: int | None) -> int | None:
        """Valida duracao nao negativa."""
        if v is not None and v < 0:
            raise ValueError("Duracao deve ser >= 0")
        return v
