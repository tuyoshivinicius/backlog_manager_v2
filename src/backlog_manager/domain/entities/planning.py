"""Planning entity."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass
class Planning:
    """Entidade representando um Planejamento no backlog.

    Attributes:
        id: Identificador unico (auto-generated pelo banco).
        name: Nome do planejamento (max 200 chars, UNIQUE).
        created_at: Data de criacao (UTC).
        updated_at: Data de ultima modificacao (UTC).
    """

    id: int | None
    name: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    def __post_init__(self) -> None:
        """Valida invariantes da entidade Planning."""
        self._validate_name()

    def _validate_name(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome do planejamento nao pode ser vazio")
        if len(self.name) > 200:
            raise ValueError("Nome do planejamento nao pode exceder 200 caracteres")
