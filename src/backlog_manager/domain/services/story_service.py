"""Story domain service."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.domain.entities import Story
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import StoryRepository


class StoryService:
    """Servico de dominio para operacoes complexas com historias.

    Centraliza logica de negocio que envolve:
    - Geracao de IDs unicos
    - Calculo e ajuste de prioridades
    - Validacoes de dominio
    """

    def __init__(self, story_repository: StoryRepository) -> None:
        """Inicializa servico.

        Args:
            story_repository: Repositorio de historias.
        """
        self._story_repo = story_repository

    async def generate_story_id(self, planning_id: int, component: str) -> str:
        """Gera ID unico para nova historia.

        Formato: COMPONENTE-NNN (ex: AUTH-001, AUTH-002).

        Args:
            planning_id: ID do planejamento.
            component: Nome do componente.

        Returns:
            ID unico no formato padrao.
        """
        component_upper = component.upper()
        max_number = await self._story_repo.get_max_id_number(
            planning_id, component_upper
        )
        next_number = max_number + 1
        return f"{component_upper}-{next_number:03d}"

    async def get_next_priority(self, planning_id: int) -> int:
        """Retorna proxima prioridade disponivel (fim da fila).

        Args:
            planning_id: ID do planejamento.

        Returns:
            Proxima prioridade (max + 1).
        """
        max_priority = await self._story_repo.get_max_priority(planning_id)
        return max_priority + 1

    async def create_story(
        self,
        planning_id: int,
        component: str,
        name: str,
        story_points: int,
        feature_id: int | None = None,
    ) -> Story:
        """Cria nova historia com ID e prioridade gerados automaticamente.

        Args:
            planning_id: ID do planejamento.
            component: Componente da historia.
            name: Nome/titulo da historia.
            story_points: Estimativa em pontos (3, 5, 8, 13).
            feature_id: ID da feature opcional.

        Returns:
            Nova entidade Story criada.
        """
        story_id = await self.generate_story_id(planning_id, component)
        priority = await self.get_next_priority(planning_id)

        return Story(
            planning_id=planning_id,
            id=story_id,
            component=component.upper(),
            name=name,
            story_points=StoryPoint(story_points),
            priority=priority,
            status=StoryStatus.BACKLOG,
            feature_id=feature_id,
        )

    def swap_priorities(self, story1: Story, story2: Story) -> None:
        """Troca prioridades entre duas historias.

        Args:
            story1: Primeira historia.
            story2: Segunda historia.
        """
        story1.priority, story2.priority = story2.priority, story1.priority

    def validate_can_move_up(self, story: Story) -> bool:
        """Valida se historia pode mover para cima (menor prioridade).

        Args:
            story: Historia a validar.

        Returns:
            True se pode mover, False caso contrario.
        """
        return story.priority > 0

    async def validate_can_move_down(self, story: Story) -> bool:
        """Valida se historia pode mover para baixo (maior prioridade).

        Args:
            story: Historia a validar.

        Returns:
            True se pode mover, False caso contrario.
        """
        next_story = await self._story_repo.get_by_priority(
            story.planning_id, story.priority + 1
        )
        return next_story is not None

    async def duplicate_story(self, planning_id: int, original: Story) -> Story:
        """Cria copia de historia existente com novo ID e prioridade.

        Args:
            planning_id: ID do planejamento destino.
            original: Historia a duplicar.

        Returns:
            Nova historia duplicada.
        """
        new_id = await self.generate_story_id(planning_id, original.component)
        priority = await self.get_next_priority(planning_id)

        return Story(
            planning_id=planning_id,
            id=new_id,
            component=original.component,
            name=f"{original.name} (copia)",
            story_points=original.story_points,
            priority=priority,
            status=StoryStatus.BACKLOG,
            feature_id=original.feature_id,
        )
