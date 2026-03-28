"""Developer entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Developer:
    """Entidade representando um desenvolvedor.

    Attributes:
        id: Identificador unico auto-incrementado.
        name: Nome do desenvolvedor (max 100 chars).
    """

    name: str
    id: int | None = None

    def __post_init__(self) -> None:
        """Valida invariantes da entidade Developer."""
        if not self.name or not self.name.strip():
            raise ValueError("Nome do desenvolvedor nao pode ser vazio")

        if len(self.name) > 100:
            raise ValueError("Nome do desenvolvedor nao pode exceder 100 caracteres")
