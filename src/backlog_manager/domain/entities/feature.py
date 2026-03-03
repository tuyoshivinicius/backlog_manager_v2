"""Feature entity."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Feature:
    """Entidade representando uma feature (agrupamento de historias em wave).

    Attributes:
        id: Identificador unico auto-incrementado.
        name: Nome da feature (max 100 chars, UNIQUE).
        wave: Numero da onda de entrega (> 0, UNIQUE).
    """

    name: str
    wave: int
    id: int | None = None

    def __post_init__(self) -> None:
        """Valida invariantes da entidade Feature."""
        if not self.name or not self.name.strip():
            raise ValueError("Nome da feature nao pode ser vazio")

        if len(self.name) > 100:
            raise ValueError("Nome da feature nao pode exceder 100 caracteres")

        if self.wave <= 0:
            raise ValueError(f"Wave deve ser > 0: {self.wave}")
