"""Story entity."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import date

from backlog_manager.domain.value_objects import StoryPoint, StoryStatus


@dataclass
class Story:
    """Entidade representando uma User Story no backlog.

    Attributes:
        id: Identificador unico no formato COMPONENTE-NNN (ex: AUTH-001).
        component: Componente/modulo ao qual pertence (max 50 chars).
        name: Nome/titulo da historia (max 200 chars).
        story_points: Estimativa em pontos Fibonacci (3, 5, 8, 13).
        priority: Prioridade numerica (>= 0, menor = mais prioritario).
        status: Estado atual do workflow (default: BACKLOG).
        duration: Duracao em dias uteis (calculado).
        start_date: Data de inicio (calculado).
        end_date: Data de termino (calculado).
        developer_id: Referencia ao desenvolvedor alocado.
        feature_id: Referencia a feature/wave.
    """

    id: str
    component: str
    name: str
    story_points: StoryPoint | int
    priority: int
    status: StoryStatus = StoryStatus.BACKLOG
    duration: int | None = None
    start_date: date | None = None
    end_date: date | None = None
    developer_id: int | None = None
    feature_id: int | None = None

    _ID_PATTERN: re.Pattern[str] = re.compile(r"^[A-Z]+-\d{3}$")

    def __post_init__(self) -> None:
        """Valida invariantes da entidade Story."""
        self._validate_id()
        self._validate_component()
        self._validate_name()
        self._validate_story_points()
        self._validate_numeric_fields()
        self._validate_date_range()

    def _validate_id(self) -> None:
        if not self.id or not self.id.strip():
            raise ValueError("ID da historia nao pode ser vazio")
        if not self._ID_PATTERN.match(self.id):
            raise ValueError(f"ID deve seguir padrao COMPONENTE-NNN: {self.id}")

    def _validate_component(self) -> None:
        if not self.component or not self.component.strip():
            raise ValueError("Componente nao pode ser vazio")
        if len(self.component) > 50:
            raise ValueError("Componente nao pode exceder 50 caracteres")

    def _validate_name(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome da historia nao pode ser vazio")
        if len(self.name) > 200:
            raise ValueError("Nome da historia nao pode exceder 200 caracteres")

    def _validate_story_points(self) -> None:
        if not isinstance(self.story_points, StoryPoint):
            if self.story_points in (3, 5, 8, 13):
                object.__setattr__(self, "story_points", StoryPoint(self.story_points))
            else:
                raise ValueError(
                    f"Story points deve ser 3, 5, 8 ou 13: {self.story_points}"
                )

    def _validate_numeric_fields(self) -> None:
        if self.priority < 0:
            raise ValueError(f"Prioridade deve ser >= 0: {self.priority}")
        if self.duration is not None and self.duration < 0:
            raise ValueError(f"Duracao deve ser >= 0: {self.duration}")

    def _validate_date_range(self) -> None:
        if (
            self.start_date is not None
            and self.end_date is not None
            and self.start_date > self.end_date
        ):
            raise ValueError("Data de inicio nao pode ser posterior a data de termino")
