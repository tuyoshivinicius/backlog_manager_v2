"""Roadmap ViewModel.

This module provides the ViewModel for the roadmap visualization,
handling data loading, grouping by feature, filtering, and collapse state.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import TYPE_CHECKING

from PySide6.QtCore import QObject

if TYPE_CHECKING:
    from backlog_manager.application.dto.story.story_output_dto import StoryOutputDTO
    from backlog_manager.presentation.container import DIContainer

logger = logging.getLogger(__name__)


@dataclass
class RoadmapFilters:
    """Filtros aplicaveis ao roadmap."""

    feature: str | None = None
    developer: str | None = None
    component: str | None = None
    search_text: str | None = None

    @property
    def is_active(self) -> bool:
        """Verifica se algum filtro esta ativo."""
        return any(
            [
                self.feature is not None,
                self.developer is not None,
                self.component is not None,
                self.search_text is not None and self.search_text.strip() != "",
            ]
        )

    def matches(self, story: StoryOutputDTO) -> bool:
        """Verifica se uma historia atende a todos os filtros ativos (logica AND)."""
        if self.feature is not None and story.feature_name != self.feature:
            return False
        if self.developer is not None and story.developer_name != self.developer:
            return False
        if self.component is not None and story.component != self.component:
            return False
        if (
            self.search_text
            and self.search_text.strip()
            and self.search_text.strip().lower() not in story.name.lower()
        ):
            return False
        return True


@dataclass
class RoadmapGroup:
    """Um grupo de historias no roadmap, correspondente a uma feature."""

    name: str
    feature_id: int | None = None
    stories: list[StoryOutputDTO] = field(default_factory=list)
    expanded: bool = False

    @property
    def completion_percent(self) -> float:
        """Percentual de historias com status CONCLUIDO."""
        if not self.stories:
            return 0.0
        done = sum(1 for s in self.stories if s.status == "CONCLUIDO")
        return (done / len(self.stories)) * 100.0

    @property
    def has_scheduled_stories(self) -> bool:
        """Indica se o grupo tem historias com datas calculadas."""
        return any(s.start_date and s.end_date for s in self.stories)

    @property
    def min_date(self) -> date | None:
        """Data de inicio mais antiga do grupo."""
        dates = [s.start_date for s in self.stories if s.start_date]
        return min(dates) if dates else None

    @property
    def max_date(self) -> date | None:
        """Data de fim mais recente do grupo."""
        dates = [s.end_date for s in self.stories if s.end_date]
        return max(dates) if dates else None

    @property
    def status_counts(self) -> dict[str, int]:
        """Contagem de historias por status."""
        counts: dict[str, int] = {}
        for s in self.stories:
            counts[s.status] = counts.get(s.status, 0) + 1
        return counts


@dataclass
class RoadmapData:
    """Dados consolidados para renderizacao do roadmap."""

    groups: list[RoadmapGroup]
    min_date: date
    max_date: date
    total_stories: int
    scheduled_stories: int

    @property
    def status_counts(self) -> dict[str, int]:
        """Contagem agregada de historias por status."""
        counts: dict[str, int] = {}
        for group in self.groups:
            for status, count in group.status_counts.items():
                counts[status] = counts.get(status, 0) + count
        return counts


class RoadmapViewModel(QObject):
    """ViewModel para visualizacao de roadmap.

    Coordena carregamento de dados, agrupamento por feature, filtragem e colapso.
    """

    def __init__(
        self,
        container: DIContainer,
    ) -> None:
        """Inicializa o ViewModel.

        Args:
            container: Container de dependencias da camada de apresentacao.
        """
        super().__init__()
        self._container = container
        self._cached_stories: list[StoryOutputDTO] = []
        self._cached_features: dict[int, str] = {}
        self._group_states: dict[str, bool] = {}
        self._current_filters: RoadmapFilters = RoadmapFilters()
        self._show_all_dependencies: bool = False

        logger.debug("RoadmapViewModel initialized")

    async def load_data(self) -> RoadmapData | None:
        """Carrega historias e features, agrupa por feature.

        Returns:
            RoadmapData com grupos colapsados por padrao, ou None se nenhuma
            historia tem datas calculadas.
        """
        async with self._container.create_unit_of_work() as uow:
            list_stories_uc = self._container.create_list_stories_use_case(uow)
            list_features_uc = self._container.create_list_features_use_case(uow)
            stories = list(await list_stories_uc.execute())
            features_output = await list_features_uc.execute()

        self._cached_features = {f.id: f.name for f in features_output.features}
        self._cached_stories = stories
        self._group_states = {}
        self._current_filters = RoadmapFilters()

        scheduled = [s for s in stories if s.start_date and s.end_date]
        if not scheduled:
            return None

        return self._build_roadmap_data(stories)

    def toggle_group(self, group_name: str) -> RoadmapData:
        """Alterna estado de expansao/colapso de um grupo.

        Args:
            group_name: Nome do grupo (feature) a alternar.

        Returns:
            RoadmapData atualizado com estado de expansao alterado.
        """
        self._group_states[group_name] = not self._group_states.get(group_name, False)
        stories = self._get_filtered_stories()
        return self._build_roadmap_data(stories)

    def apply_filters(self, filters: RoadmapFilters) -> RoadmapData:
        """Aplica filtros sobre historias cacheadas e reconstroi grupos.

        Args:
            filters: Criterios de filtragem (AND logico).

        Returns:
            RoadmapData filtrado. Grupos sem historias apos filtro sao omitidos.
        """
        self._current_filters = filters
        stories = self._get_filtered_stories()
        return self._build_roadmap_data(stories)

    def clear_filters(self) -> RoadmapData:
        """Remove todos os filtros e retorna dados completos.

        Returns:
            RoadmapData sem filtros aplicados.
        """
        self._current_filters = RoadmapFilters()
        return self._build_roadmap_data(self._cached_stories)

    def toggle_show_all_dependencies(self) -> bool:
        """Alterna exibicao global de setas de dependencia.

        Returns:
            Novo estado do toggle (True = exibir todas).
        """
        self._show_all_dependencies = not self._show_all_dependencies
        return self._show_all_dependencies

    def get_available_filters(self) -> dict[str, list[str]]:
        """Retorna opcoes disponiveis para cada filtro.

        Returns:
            Dict com chaves: features, developers, components.
        """
        features: set[str] = set()
        developers: set[str] = set()
        components: set[str] = set()

        for story in self._cached_stories:
            if story.feature_name:
                features.add(story.feature_name)
            if story.developer_name:
                developers.add(story.developer_name)
            else:
                developers.add("Nao atribuido")
            if story.component:
                components.add(story.component)

        return {
            "features": sorted(features),
            "developers": sorted(developers),
            "components": sorted(components),
        }

    def _get_filtered_stories(self) -> list[StoryOutputDTO]:
        """Retorna historias filtradas conforme filtros atuais."""
        if not self._current_filters.is_active:
            return self._cached_stories
        return [s for s in self._cached_stories if self._current_filters.matches(s)]

    def get_density_region(self) -> tuple[date, date]:
        """Retorna janela temporal com maior concentracao de historias.

        Usa algoritmo de sliding window de 30% do periodo total.

        Returns:
            Tupla (start, end) da regiao de maior densidade.
        """
        scheduled = [s for s in self._cached_stories if s.start_date and s.end_date]
        if not scheduled:
            today = date.today()
            return (today, today)

        all_starts: list[date] = [
            s.start_date for s in scheduled if s.start_date is not None
        ]
        all_ends: list[date] = [s.end_date for s in scheduled if s.end_date is not None]
        global_min = min(all_starts)
        global_max = max(all_ends)

        total_days = (global_max - global_min).days
        if total_days <= 0:
            return (global_min, global_max)

        window_days = max(int(total_days * 0.3), 7)
        best_start = global_min
        best_count = 0

        current = global_min
        while current + timedelta(days=window_days) <= global_max:
            window_end = current + timedelta(days=window_days)
            count = sum(
                1
                for s in scheduled
                if s.start_date is not None
                and s.end_date is not None
                and s.start_date <= window_end
                and s.end_date >= current
            )
            if count > best_count:
                best_count = count
                best_start = current
            current += timedelta(days=1)

        return (best_start, best_start + timedelta(days=window_days))

    def _build_roadmap_data(
        self,
        all_stories: list[StoryOutputDTO],
    ) -> RoadmapData:
        """Constroi RoadmapData agrupando por feature."""
        groups_dict: dict[str, list[StoryOutputDTO]] = {}
        feature_id_map: dict[str, int | None] = {}

        for story in all_stories:
            group_name = story.feature_name if story.feature_name else "Sem feature"
            feature_id_map.setdefault(group_name, story.feature_id)
            groups_dict.setdefault(group_name, []).append(story)

        groups = self._create_sorted_groups(groups_dict, feature_id_map)

        scheduled = [s for s in all_stories if s.start_date and s.end_date]
        start_dates = [s.start_date for s in scheduled if s.start_date]
        end_dates = [s.end_date for s in scheduled if s.end_date]

        return RoadmapData(
            groups=groups,
            min_date=min(start_dates) if start_dates else date.today(),
            max_date=max(end_dates) if end_dates else date.today(),
            total_stories=len(all_stories),
            scheduled_stories=len(scheduled),
        )

    def _create_sorted_groups(
        self,
        groups_dict: dict[str, list[StoryOutputDTO]],
        feature_id_map: dict[str, int | None],
    ) -> list[RoadmapGroup]:
        """Cria grupos ordenados por data de inicio mais cedo (FR-019).

        Args:
            groups_dict: Mapeamento nome do grupo -> lista de historias.
            feature_id_map: Mapeamento nome do grupo -> feature_id.

        Returns:
            Lista de RoadmapGroup ordenados por min_date.
        """
        groups = [
            RoadmapGroup(
                name=name,
                feature_id=feature_id_map.get(name),
                stories=stories,
                expanded=self._group_states.get(name, False),
            )
            for name, stories in groups_dict.items()
        ]
        groups.sort(
            key=lambda g: (
                g.feature_id is None,
                g.min_date or date.max,
            )
        )
        return groups
