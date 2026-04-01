"""Allocation Service for automatic developer allocation.

Domain service that implements the automatic allocation algorithm.
All public methods are static and have no side effects.
"""

from __future__ import annotations

import logging
import random
import time
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import TYPE_CHECKING

from backlog_manager.domain.exceptions.warnings import (
    BacklogWarning,
    BetweenWavesIdlenessInfo,
    DeadlockWarning,
    IdlenessWarning,
)
from backlog_manager.domain.services.scheduling_service import SchedulingService
from backlog_manager.domain.value_objects import StoryStatus
from backlog_manager.infrastructure.logging import get_logger

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Developer, Feature, Story

# Module-level logger for allocation service (T011: FR-001 a FR-005)
logger = get_logger("domain.services.allocation_service")

# Security constants - prevent infinite loops in edge cases
DEFAULT_MAX_ITERATIONS: int = 1000
MAX_REALLOCATIONS_PER_STORY: int = 3
MAX_STABILIZATION_PASSES: int = 10
MAX_CONFLICT_PASSES: int = 100


class AllocationCriteria(Enum):
    """Criterio de selecao de desenvolvedor para alocacao.

    LOAD_BALANCING: Alocar para dev com menor contagem de historias (padrao).
    DEPENDENCY_OWNER: Priorizar dev que completou dependencias da historia.
    """

    LOAD_BALANCING = "load_balancing"
    DEPENDENCY_OWNER = "dependency_owner"


@dataclass
class AllocationConfig:
    """Configuracao para execucao da alocacao automatica.

    Attributes:
        velocity: Velocidade do time em SP/dia.
        project_start_date: Data de inicio do projeto.
        max_idle_days: Dias maximos de ociosidade aceitavel (default=3, range [2,30]).
        allocation_criteria: Criterio de selecao de dev (default=LOAD_BALANCING).
        max_iterations: Limite de iteracoes por onda (default=1000).
        random_seed: Seed para aleatoriedade (None = aleatorio).
    """

    velocity: float
    project_start_date: date
    max_idle_days: int = 3
    allocation_criteria: AllocationCriteria = AllocationCriteria.LOAD_BALANCING
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    random_seed: int | None = None

    def __post_init__(self) -> None:
        """Valida invariantes da configuracao."""
        if self.velocity <= 0:
            raise ValueError("Velocidade deve ser maior que zero")
        if not 2 <= self.max_idle_days <= 30:
            raise ValueError("max_idle_days deve estar entre 2 e 30")
        if self.max_iterations <= 0:
            raise ValueError("max_iterations deve ser maior que zero")


@dataclass
class AllocationMetrics:
    """Metricas coletadas durante a execucao da alocacao.

    Attributes:
        total_time_seconds: Tempo total de execucao.
        stories_processed: Total de historias processadas.
        stories_allocated: Historias alocadas com sucesso.
        waves_processed: Numero de ondas processadas.
        total_iterations: Total de iteracoes do algoritmo.
        iterations_per_wave: Iteracoes por onda.
        allocations_by_dependency_owner: Alocacoes por criterio DEPENDENCY_OWNER.
        allocations_by_load_balancing: Alocacoes por criterio LOAD_BALANCING.
        deadlocks_detected: Deadlocks detectados.
        date_adjustments: Ajustes de data realizados.
        validation_reallocations: Realocacoes bem-sucedidas na validacao.
        validation_dependency_fixes: Violacoes de dependencia corrigidas.
        validation_conflict_fixes: Conflitos de periodo resolvidos.
        max_idle_violations_detected: Violacoes de max_idle_days detectadas.
        max_idle_violations_fixed: Violacoes corrigidas por realocacao.
        failed_reallocations: Tentativas de realocacao que falharam.
    """

    total_time_seconds: float = 0.0
    stories_processed: int = 0
    stories_allocated: int = 0
    waves_processed: int = 0
    total_iterations: int = 0
    iterations_per_wave: dict[int, int] = field(default_factory=dict)
    allocations_by_dependency_owner: int = 0
    allocations_by_load_balancing: int = 0
    deadlocks_detected: int = 0
    date_adjustments: int = 0
    validation_reallocations: int = 0
    validation_dependency_fixes: int = 0
    validation_conflict_fixes: int = 0
    max_idle_violations_detected: int = 0
    max_idle_violations_fixed: int = 0
    failed_reallocations: int = 0


@dataclass
class AllocationResult:
    """Resultado da execucao da alocacao automatica.

    Attributes:
        allocated_stories: Historias que foram alocadas (com mudancas).
        metrics: Metricas de execucao.
        warnings: Warnings emitidos durante execucao.
    """

    allocated_stories: list[Story]
    metrics: AllocationMetrics
    warnings: list[BacklogWarning]


class AllocationService:
    """Domain service for automatic developer allocation.

    Servico stateless que implementa o algoritmo de alocacao automatica
    de desenvolvedores para historias do backlog. Recebe todos os dados
    via parametros, nao acessa repositorios ou faz I/O.

    O algoritmo funciona em fases:
    1. Filtra historias elegiveis (dev=NULL, datas ok, SP ok)
    2. Agrupa historias por wave (feature -> wave, sem feature = wave 0)
    3. Para cada wave em ordem crescente: loop de alocacao
    4. Loop de estabilizacao para garantir consistencia final

    Example:
        >>> from datetime import date
        >>> from backlog_manager.domain.value_objects import (
        ...     BRAZILIAN_HOLIDAYS_2026_2028,
        ... )
        >>> config = AllocationConfig(velocity=2.0, project_start_date=date(2026, 3, 2))
        >>> result = AllocationService.allocate_stories(
        ...     stories=stories,
        ...     developers=developers,
        ...     dependencies=[("B", "A")],
        ...     features=features,
        ...     holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        ...     config=config,
        ... )
    """

    @staticmethod
    def _recalculate_end_date(
        story: Story,
        new_start: date,
        holidays: frozenset[date],
        config: AllocationConfig,
    ) -> date:
        """Calcula nova end_date a partir de start_date usando duracao ou SP."""
        if story.duration:
            return SchedulingService.add_workdays(new_start, story.duration, holidays)
        sp = (
            story.story_points.value
            if hasattr(story.story_points, "value")
            else story.story_points
        )
        duration = SchedulingService.calculate_duration(sp, config.velocity)
        return SchedulingService.add_workdays(new_start, duration, holidays)

    @staticmethod
    def _move_story_dates(
        story: Story,
        new_start: date,
        holidays: frozenset[date],
        config: AllocationConfig,
    ) -> None:
        """Atualiza start_date e end_date de uma historia."""
        new_end = AllocationService._recalculate_end_date(
            story, new_start, holidays, config
        )
        object.__setattr__(story, "start_date", new_start)
        object.__setattr__(story, "end_date", new_end)

    @staticmethod
    def _group_stories_by_developer(stories: Sequence[Story]) -> dict[int, list[Story]]:
        """Agrupa historias por developer_id."""
        dev_stories: dict[int, list[Story]] = {}
        for story in stories:
            if story.developer_id is not None:
                if story.developer_id not in dev_stories:
                    dev_stories[story.developer_id] = []
                dev_stories[story.developer_id].append(story)
        return dev_stories

    @staticmethod
    def _find_max_dependency_end_date(
        story_id: str,
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
    ) -> date | None:
        """Encontra a maior end_date entre as dependencias de uma historia."""
        deps = dependency_graph.get(story_id, [])
        if not deps:
            return None
        max_dep_end: date | None = None
        for dep_id in deps:
            dep_story = story_map.get(dep_id)
            if (
                dep_story
                and dep_story.end_date
                and (max_dep_end is None or dep_story.end_date > max_dep_end)
            ):
                max_dep_end = dep_story.end_date
        return max_dep_end

    @staticmethod
    def _is_eligible(story: Story) -> bool:
        """Verifica se historia e elegivel para alocacao.

        Uma historia e elegivel se:
        - Nao esta alocada (developer_id == None)
        - Tem datas calculadas (start_date != None AND end_date != None)
        - Tem story points definidos

        Args:
            story: Historia a verificar.

        Returns:
            True se elegivel, False caso contrario.
        """
        return (
            story.status != StoryStatus.CONCLUIDO
            and story.developer_id is None
            and story.start_date is not None
            and story.end_date is not None
            and story.story_points is not None
        )

    @staticmethod
    def _get_story_wave(story: Story, feature_map: dict[int, int]) -> int:
        """Retorna wave da historia.

        Historias sem feature (feature_id=None) pertencem a wave 0.
        Historias com feature retornam wave da feature.

        Args:
            story: Historia a verificar.
            feature_map: Mapa feature_id -> wave.

        Returns:
            Numero da wave (0 se sem feature).
        """
        if story.feature_id is None:
            return 0
        return feature_map.get(story.feature_id, 0)

    @staticmethod
    def _build_feature_map(features: Sequence[Feature]) -> dict[int, int]:
        """Constroi mapa feature_id -> wave.

        Args:
            features: Lista de features.

        Returns:
            Dicionario feature_id -> wave.
        """
        return {f.id: f.wave for f in features if f.id is not None}

    @staticmethod
    def _group_stories_by_wave(
        stories: Sequence[Story], feature_map: dict[int, int]
    ) -> dict[int, list[Story]]:
        """Agrupa historias por wave.

        Args:
            stories: Lista de historias.
            feature_map: Mapa feature_id -> wave.

        Returns:
            Dicionario wave -> lista de historias.
        """
        grouped: dict[int, list[Story]] = {}
        for story in stories:
            wave = AllocationService._get_story_wave(story, feature_map)
            if wave not in grouped:
                grouped[wave] = []
            grouped[wave].append(story)
        return grouped

    @staticmethod
    def _has_period_overlap(story_a: Story, story_b: Story) -> bool:
        """Verifica se dois periodos se sobrepoe.

        Formula: overlap = (a.start <= b.end) AND (a.end >= b.start)

        Args:
            story_a: Primeira historia.
            story_b: Segunda historia.

        Returns:
            True se ha sobreposicao, False caso contrario.
        """
        if (
            story_a.start_date is None
            or story_a.end_date is None
            or story_b.start_date is None
            or story_b.end_date is None
        ):
            return False
        return (
            story_a.start_date <= story_b.end_date
            and story_a.end_date >= story_b.start_date
        )

    @staticmethod
    def _select_developer(
        developers: Sequence[Developer],
        story: Story,
        dev_count: dict[int, int],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        config: AllocationConfig,
        rng: random.Random,
    ) -> Developer | None:
        """Seleciona desenvolvedor para alocar historia.

        Se criterio=DEPENDENCY_OWNER e ha dependencias, prioriza dev
        que completou dependencia mais recente (maior end_date).
        Se nao disponivel ou criterio=LOAD_BALANCING, usa balanceamento.

        Args:
            developers: Lista de desenvolvedores disponiveis.
            story: Historia a alocar.
            dev_count: Contagem de historias por dev.
            dependency_graph: Grafo de dependencias (story_id -> [depends_on_ids]).
            story_map: Mapa story_id -> Story.
            config: Configuracao de alocacao.
            rng: Gerador de numeros aleatorios.

        Returns:
            Developer selecionado ou None se nenhum disponivel.
        """
        if not developers:
            return None

        # Filter developers with valid id
        valid_devs = [d for d in developers if d.id is not None]
        if not valid_devs:
            return None

        # Try DEPENDENCY_OWNER if configured
        if config.allocation_criteria == AllocationCriteria.DEPENDENCY_OWNER:
            owner = AllocationService._get_dependency_owner(
                story, dependency_graph, story_map, valid_devs
            )
            if owner is not None:
                return owner

        # Fallback to LOAD_BALANCING
        return AllocationService._select_by_load_balancing(valid_devs, dev_count, rng)

    @staticmethod
    def _select_by_load_balancing(
        developers: Sequence[Developer],
        dev_count: dict[int, int],
        rng: random.Random,
    ) -> Developer | None:
        """Seleciona dev com menor carga (contagem de historias).

        Em caso de empate, usa desempate aleatorio.

        Args:
            developers: Lista de desenvolvedores.
            dev_count: Contagem de historias por dev.
            rng: Gerador de numeros aleatorios.

        Returns:
            Developer com menor carga ou None se lista vazia.
        """
        if not developers:
            return None

        # Sort by count (ascending)
        sorted_devs = sorted(
            developers, key=lambda d: dev_count.get(d.id, 0) if d.id else 0
        )

        # Get minimum count
        min_count = dev_count.get(sorted_devs[0].id, 0) if sorted_devs[0].id else 0

        # Filter candidates with same min count
        candidates = [
            d
            for d in sorted_devs
            if d.id is not None and dev_count.get(d.id, 0) == min_count
        ]

        # Random tiebreak
        return rng.choice(candidates) if candidates else sorted_devs[0]

    @staticmethod
    def _get_dependency_owner(
        story: Story,
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        developers: Sequence[Developer],
    ) -> Developer | None:
        """Retorna dev que completou dependencia mais recente.

        Busca entre todas as dependencias da historia, o desenvolvedor
        alocado para a que tem maior end_date.

        Args:
            story: Historia a verificar.
            dependency_graph: Grafo de dependencias.
            story_map: Mapa story_id -> Story.
            developers: Lista de desenvolvedores validos.

        Returns:
            Developer proprietario ou None se nao encontrado.
        """
        deps = dependency_graph.get(story.id, [])
        if not deps:
            return None

        # Build dev_id -> Developer map
        dev_map = {d.id: d for d in developers if d.id is not None}

        # Find dependency with latest end_date that has a developer
        latest_dep: Story | None = None
        for dep_id in deps:
            dep_story = story_map.get(dep_id)
            has_dev_and_end = (
                dep_story
                and dep_story.developer_id is not None
                and dep_story.end_date is not None
            )
            is_later = latest_dep is None or (
                latest_dep.end_date is not None
                and dep_story
                and dep_story.end_date
                and dep_story.end_date > latest_dep.end_date
            )
            if has_dev_and_end and is_later:
                latest_dep = dep_story

        if latest_dep and latest_dep.developer_id in dev_map:
            return dev_map[latest_dep.developer_id]

        return None

    @staticmethod
    def _fix_single_overlap(
        current: Story,
        next_story: Story,
        holidays: frozenset[date],
        config: AllocationConfig,
    ) -> bool:
        """Corrige sobreposicao entre duas historias consecutivas do mesmo dev."""
        if not AllocationService._has_period_overlap(current, next_story):
            return False
        if current.end_date is None:
            return False

        from datetime import timedelta

        new_start = SchedulingService.next_workday(
            current.end_date + timedelta(days=1), holidays
        )
        AllocationService._move_story_dates(next_story, new_start, holidays, config)
        return True

    @staticmethod
    def _resolve_allocation_conflicts(
        stories: list[Story],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
    ) -> None:
        """Resolve conflitos de periodo entre historias do mesmo dev."""
        dev_stories = AllocationService._group_stories_by_developer(stories)

        for _pass_num in range(MAX_CONFLICT_PASSES):
            conflicts_fixed = 0

            for _dev_id, dev_story_list in dev_stories.items():
                sorted_stories = sorted(
                    dev_story_list,
                    key=lambda s: s.start_date if s.start_date else date.min,
                )
                for i in range(len(sorted_stories) - 1):
                    if AllocationService._fix_single_overlap(
                        sorted_stories[i], sorted_stories[i + 1], holidays, config
                    ):
                        metrics.validation_conflict_fixes += 1
                        metrics.date_adjustments += 1
                        conflicts_fixed += 1

            if conflicts_fixed == 0:
                break

    @staticmethod
    def _ensure_dependencies_finished(
        story: Story,
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
    ) -> bool:
        """Ajusta start_date da historia para depois das dependencias.

        Verifica se a historia comeca antes de suas dependencias
        terminarem e, se necessario, ajusta start_date e end_date.

        Args:
            story: Historia a verificar.
            dependency_graph: Grafo de dependencias.
            story_map: Mapa story_id -> Story.
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.
            metrics: Metricas a atualizar.

        Returns:
            True se ajuste foi feito, False se nenhum ajuste necessario.
        """
        from datetime import timedelta

        max_dep_end = AllocationService._find_max_dependency_end_date(
            story.id, dependency_graph, story_map
        )
        if max_dep_end is None or not story.start_date:
            return False

        if story.start_date <= max_dep_end:
            new_start = SchedulingService.next_workday(
                max_dep_end + timedelta(days=1), holidays
            )
            AllocationService._move_story_dates(story, new_start, holidays, config)
            metrics.date_adjustments += 1
            return True

        return False

    @staticmethod
    def _final_dependency_check(
        stories: list[Story],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
    ) -> bool:
        """Verifica e corrige violacoes de dependencia.

        Uma violacao ocorre quando uma historia comeca antes de suas
        dependencias terminarem.

        Args:
            stories: Lista de historias.
            dependency_graph: Grafo de dependencias.
            story_map: Mapa story_id -> Story.
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.
            metrics: Metricas a atualizar.

        Returns:
            True se houve correcoes, False se nenhuma violacao.
        """
        from datetime import timedelta

        any_fixed = False

        for story in stories:
            max_dep_end = AllocationService._find_max_dependency_end_date(
                story.id, dependency_graph, story_map
            )
            if max_dep_end is None:
                continue

            if story.start_date and story.start_date <= max_dep_end:
                new_start = SchedulingService.next_workday(
                    max_dep_end + timedelta(days=1), holidays
                )
                AllocationService._move_story_dates(story, new_start, holidays, config)
                metrics.validation_dependency_fixes += 1
                metrics.date_adjustments += 1
                any_fixed = True

        return any_fixed

    @staticmethod
    def _emit_idleness_if_excessive(
        current: Story,
        next_story: Story,
        dev_id: int,
        dev: Developer,
        feature_map: dict[int, int],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
        warnings: list[BacklogWarning],
    ) -> None:
        """Emite warning de ociosidade se gap entre historias excede max_idle_days."""
        if current.end_date is None or next_story.start_date is None:
            return

        idle_days = SchedulingService.count_workdays_between(
            current.end_date, next_story.start_date, holidays
        )
        if idle_days <= config.max_idle_days:
            return

        current_wave = AllocationService._get_story_wave(current, feature_map)
        next_wave = AllocationService._get_story_wave(next_story, feature_map)

        if current_wave == next_wave:
            metrics.max_idle_violations_detected += 1
            warnings.append(
                IdlenessWarning(
                    developer_id=dev_id,
                    developer_name=dev.name,
                    idle_days=idle_days,
                    wave=current_wave,
                )
            )
            logger.warning(
                "Ociosidade detectada: dev %s (%d) - %d dias na onda %d",
                dev.name,
                dev_id,
                idle_days,
                current_wave,
            )
        else:
            warnings.append(
                BetweenWavesIdlenessInfo(
                    developer_id=dev_id,
                    developer_name=dev.name,
                    idle_days=idle_days,
                    from_wave=current_wave,
                    to_wave=next_wave,
                )
            )
            logger.info(
                "Ociosidade inter-wave: dev %s (%d) - %d dias entre ondas %d e %d",
                dev.name,
                dev_id,
                idle_days,
                current_wave,
                next_wave,
            )

    @staticmethod
    def _check_idleness(
        stories: list[Story],
        developers: Sequence[Developer],
        feature_map: dict[int, int],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
        warnings: list[BacklogWarning],
    ) -> None:
        """Detecta ociosidade excessiva entre historias do mesmo dev.

        Distingue entre ociosidade intra-wave (problema - emite IdlenessWarning)
        e inter-wave (esperado - emite BetweenWavesIdlenessInfo).

        Args:
            stories: Lista de historias alocadas.
            developers: Lista de desenvolvedores.
            feature_map: Mapa feature_id -> wave.
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.
            metrics: Metricas a atualizar.
            warnings: Lista de warnings a adicionar.
        """
        dev_map = {d.id: d for d in developers if d.id is not None}
        dev_stories = AllocationService._group_stories_by_developer(stories)

        for dev_id, dev_story_list in dev_stories.items():
            dev = dev_map.get(dev_id)
            if not dev:
                continue

            sorted_stories = sorted(
                dev_story_list,
                key=lambda s: s.end_date if s.end_date else date.min,
            )

            for i in range(len(sorted_stories) - 1):
                AllocationService._emit_idleness_if_excessive(
                    sorted_stories[i],
                    sorted_stories[i + 1],
                    dev_id,
                    dev,
                    feature_map,
                    holidays,
                    config,
                    metrics,
                    warnings,
                )

    @staticmethod
    def _try_reallocate_idle_story(
        current: Story,
        next_story: Story,
        dev_id: int,
        developers: Sequence[Developer],
        dev_count: dict[int, int],
        feature_map: dict[int, int],
        reallocation_count: dict[str, int],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
        rng: random.Random,
    ) -> bool:
        """Tenta realocar uma historia ociosa para outro desenvolvedor."""
        if current.end_date is None or next_story.start_date is None:
            return False

        idle_days = SchedulingService.count_workdays_between(
            current.end_date, next_story.start_date, holidays
        )
        if idle_days <= config.max_idle_days:
            return False

        current_wave = AllocationService._get_story_wave(current, feature_map)
        next_wave = AllocationService._get_story_wave(next_story, feature_map)
        if current_wave != next_wave:
            return False

        if reallocation_count.get(next_story.id, 0) >= MAX_REALLOCATIONS_PER_STORY:
            metrics.failed_reallocations += 1
            return False

        other_devs = [d for d in developers if d.id != dev_id]
        if not other_devs:
            metrics.failed_reallocations += 1
            return False

        new_dev = AllocationService._select_by_load_balancing(
            other_devs, dev_count, rng
        )
        if not new_dev or new_dev.id is None:
            metrics.failed_reallocations += 1
            return False

        dev_count[dev_id] = dev_count.get(dev_id, 1) - 1
        dev_count[new_dev.id] = dev_count.get(new_dev.id, 0) + 1
        object.__setattr__(next_story, "developer_id", new_dev.id)
        reallocation_count[next_story.id] = reallocation_count.get(next_story.id, 0) + 1
        metrics.validation_reallocations += 1
        metrics.max_idle_violations_fixed += 1
        return True

    @staticmethod
    def _check_and_fix_idle_violations(
        stories: list[Story],
        developers: Sequence[Developer],
        dev_count: dict[int, int],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        feature_map: dict[int, int],
        reallocation_count: dict[str, int],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
        rng: random.Random,
    ) -> bool:
        """Tenta realocar historias para reduzir ociosidade.

        Args:
            stories: Lista de historias.
            developers: Lista de desenvolvedores.
            dev_count: Contagem de historias por dev.
            dependency_graph: Grafo de dependencias.
            story_map: Mapa story_id -> Story.
            feature_map: Mapa feature_id -> wave.
            reallocation_count: Contador de realocacoes por historia.
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.
            metrics: Metricas a atualizar.
            rng: Gerador de numeros aleatorios.

        Returns:
            True se houve realocacao, False caso contrario.
        """
        any_reallocation = False
        dev_stories = AllocationService._group_stories_by_developer(stories)

        for dev_id, dev_story_list in dev_stories.items():
            sorted_stories = sorted(
                dev_story_list,
                key=lambda s: s.end_date if s.end_date else date.min,
            )

            for i in range(len(sorted_stories) - 1):
                result = AllocationService._try_reallocate_idle_story(
                    sorted_stories[i],
                    sorted_stories[i + 1],
                    dev_id,
                    developers,
                    dev_count,
                    feature_map,
                    reallocation_count,
                    holidays,
                    config,
                    metrics,
                    rng,
                )
                if result:
                    any_reallocation = True

        return any_reallocation

    @staticmethod
    def _adjust_date_for_availability(
        story: Story,
        developers: Sequence[Developer],
        dev_count: dict[int, int],
        dev_stories: dict[int, list[Story]],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
    ) -> bool:
        """Ajusta data da historia quando nenhum dev esta disponivel.

        Implementa FR-050 a FR-052: quando nenhum desenvolvedor pode
        iniciar a historia na data atual, avanca start_date em +1 dia util.

        Args:
            story: Historia a ajustar.
            developers: Lista de desenvolvedores.
            dev_count: Contagem de historias por dev.
            dev_stories: Historias por desenvolvedor.
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.
            metrics: Metricas a atualizar.

        Returns:
            True se data foi ajustada, False caso contrario.
        """
        from datetime import timedelta

        if story.start_date is None:
            return False

        valid_devs = [d for d in developers if d.id is not None]
        if not valid_devs:
            return False

        if AllocationService._any_dev_available(story, valid_devs, dev_stories):
            return False

        new_start = SchedulingService.next_workday(
            story.start_date + timedelta(days=1), holidays
        )
        AllocationService._move_story_dates(story, new_start, holidays, config)
        metrics.date_adjustments += 1
        return True

    @staticmethod
    def _any_dev_available(
        story: Story,
        valid_devs: list[Developer],
        dev_stories: dict[int, list[Story]],
    ) -> bool:
        """Verifica se algum dev pode assumir a historia sem conflito."""
        for dev in valid_devs:
            assert dev.id is not None
            dev_story_list = dev_stories.get(dev.id, [])
            has_conflict = any(
                AllocationService._has_period_overlap(story, ds)
                for ds in dev_story_list
                if ds.id != story.id
            )
            if not has_conflict:
                return True
        return False

    @staticmethod
    def _allocate_by_wave(
        wave: int,
        wave_stories: list[Story],
        developers: Sequence[Developer],
        dev_count: dict[int, int],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
        warnings: list[BacklogWarning],
        rng: random.Random,
    ) -> list[Story]:
        """Processa alocacao de uma wave.

        Loop de alocacao ate estabilizar ou atingir limite de iteracoes.
        Detecta deadlock quando nenhum progresso ocorre.

        Args:
            wave: Numero da wave.
            wave_stories: Historias da wave.
            developers: Lista de desenvolvedores.
            dev_count: Contagem de historias por dev.
            dependency_graph: Grafo de dependencias.
            story_map: Mapa story_id -> Story.
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.
            metrics: Metricas a atualizar.
            warnings: Lista de warnings.
            rng: Gerador de numeros aleatorios.

        Returns:
            Lista de historias alocadas nesta wave.
        """
        allocated_in_wave: list[Story] = []
        wave_start_time = time.perf_counter()

        dev_stories = AllocationService._group_stories_by_developer(
            list(story_map.values())
        )

        eligible = [s for s in wave_stories if AllocationService._is_eligible(s)]
        metrics.stories_processed += len(eligible)

        logger.info("Onda %d: iniciando alocacao de %d historias", wave, len(eligible))

        iteration = AllocationService._run_allocation_loop(
            eligible,
            allocated_in_wave,
            developers,
            dev_count,
            dev_stories,
            dependency_graph,
            story_map,
            holidays,
            config,
            metrics,
            rng,
        )

        AllocationService._handle_remaining_eligible(
            eligible,
            iteration,
            wave,
            config,
            metrics,
            warnings,
        )

        wave_time = time.perf_counter() - wave_start_time
        logger.info(
            "Onda %d: completa - %d/%d historias em %.2fs (%d iteracoes)",
            wave,
            len(allocated_in_wave),
            len(wave_stories),
            wave_time,
            iteration,
        )

        metrics.total_iterations += iteration
        metrics.iterations_per_wave[wave] = iteration

        return allocated_in_wave

    @staticmethod
    def _find_available_developers(
        story: Story,
        developers: Sequence[Developer],
        dev_stories: dict[int, list[Story]],
    ) -> list[Developer]:
        """Filtra desenvolvedores sem conflito de periodo com a historia."""
        available: list[Developer] = []
        for candidate in developers:
            if candidate.id is None:
                continue
            has_conflict = any(
                AllocationService._has_period_overlap(story, ds)
                for ds in dev_stories.get(candidate.id, [])
            )
            if not has_conflict:
                available.append(candidate)
        return available

    @staticmethod
    def _perform_allocation(
        story: Story,
        dev: Developer,
        dev_count: dict[int, int],
        dev_stories: dict[int, list[Story]],
        allocated_in_wave: list[Story],
        eligible: list[Story],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        developers: Sequence[Developer],
        config: AllocationConfig,
        metrics: AllocationMetrics,
    ) -> None:
        """Executa a alocacao de uma historia para um desenvolvedor."""
        assert dev.id is not None
        object.__setattr__(story, "developer_id", dev.id)
        dev_count[dev.id] = dev_count.get(dev.id, 0) + 1

        if dev.id not in dev_stories:
            dev_stories[dev.id] = []
        dev_stories[dev.id].append(story)

        allocated_in_wave.append(story)
        eligible.remove(story)
        metrics.stories_allocated += 1

        AllocationService._log_allocation_reason(
            story,
            dev,
            dependency_graph,
            story_map,
            developers,
            config,
            metrics,
        )

    @staticmethod
    def _log_allocation_reason(
        story: Story,
        dev: Developer,
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        developers: Sequence[Developer],
        config: AllocationConfig,
        metrics: AllocationMetrics,
    ) -> None:
        """Determina e loga o motivo da alocacao."""
        allocation_reason = "LOAD_BALANCING"
        if config.allocation_criteria == AllocationCriteria.DEPENDENCY_OWNER:
            owner = AllocationService._get_dependency_owner(
                story, dependency_graph, story_map, developers
            )
            if owner and owner.id == dev.id:
                metrics.allocations_by_dependency_owner += 1
                allocation_reason = "DEPENDENCY_OWNER"
            else:
                metrics.allocations_by_load_balancing += 1
                allocation_reason = "FALLBACK_LOAD_BALANCING"
        else:
            metrics.allocations_by_load_balancing += 1

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Historia %s: alocada para dev %d (%s)",
                story.id,
                dev.id,
                allocation_reason,
            )

    @staticmethod
    def _run_allocation_loop(
        eligible: list[Story],
        allocated_in_wave: list[Story],
        developers: Sequence[Developer],
        dev_count: dict[int, int],
        dev_stories: dict[int, list[Story]],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
        rng: random.Random,
    ) -> int:
        """Loop principal de alocacao. Retorna numero de iteracoes."""
        iteration = 0
        while eligible and iteration < config.max_iterations:
            iteration += 1
            progress_made = False

            for story in eligible[:]:
                dep_adjusted = AllocationService._ensure_dependencies_finished(
                    story,
                    dependency_graph,
                    story_map,
                    holidays,
                    config,
                    metrics,
                )
                if dep_adjusted:
                    progress_made = True

                available_devs = AllocationService._find_available_developers(
                    story,
                    developers,
                    dev_stories,
                )

                if available_devs:
                    dev = AllocationService._select_developer(
                        available_devs,
                        story,
                        dev_count,
                        dependency_graph,
                        story_map,
                        config,
                        rng,
                    )
                    if dev is not None and dev.id is not None:
                        AllocationService._perform_allocation(
                            story,
                            dev,
                            dev_count,
                            dev_stories,
                            allocated_in_wave,
                            eligible,
                            dependency_graph,
                            story_map,
                            developers,
                            config,
                            metrics,
                        )
                        progress_made = True
                else:
                    adjusted = AllocationService._adjust_date_for_availability(
                        story,
                        developers,
                        dev_count,
                        dev_stories,
                        holidays,
                        config,
                        metrics,
                    )
                    if adjusted:
                        progress_made = True

            if not progress_made:
                break

        return iteration

    @staticmethod
    def _handle_remaining_eligible(
        eligible: list[Story],
        iteration: int,
        wave: int,
        config: AllocationConfig,
        metrics: AllocationMetrics,
        warnings: list[BacklogWarning],
    ) -> None:
        """Registra deadlock se ainda ha historias nao alocadas."""
        if not eligible:
            return

        max_iterations_reached = iteration >= config.max_iterations
        metrics.deadlocks_detected += 1
        blocked_ids = [s.id for s in eligible]
        warnings.append(
            DeadlockWarning(
                wave=wave,
                blocked_stories=blocked_ids,
                max_iterations_reached=max_iterations_reached,
            )
        )
        logger.warning(
            "Onda %d: deadlock detectado - %d historias bloqueadas: %s",
            wave,
            len(blocked_ids),
            ", ".join(blocked_ids[:5]) + ("..." if len(blocked_ids) > 5 else ""),
            extra={
                "deadlock": {
                    "wave": wave,
                    "blocked_count": len(blocked_ids),
                    "blocked_stories": blocked_ids,
                    "max_iterations_reached": max_iterations_reached,
                }
            },
        )

    @staticmethod
    def _stabilization_loop(
        allocated_stories: list[Story],
        developers: Sequence[Developer],
        dev_count: dict[int, int],
        dependency_graph: dict[str, list[str]],
        story_map: dict[str, Story],
        feature_map: dict[int, int],
        holidays: frozenset[date],
        config: AllocationConfig,
        metrics: AllocationMetrics,
        warnings: list[BacklogWarning],
        rng: random.Random,
    ) -> None:
        """Loop de estabilizacao pos-alocacao.

        Executa 3 etapas em loop ate estabilizar:
        1. Verifica dependencias
        2. Resolve conflitos de periodo
        3. Verifica e corrige ociosidade

        Args:
            allocated_stories: Historias alocadas.
            developers: Lista de desenvolvedores.
            dev_count: Contagem de historias por dev.
            dependency_graph: Grafo de dependencias.
            story_map: Mapa story_id -> Story.
            feature_map: Mapa feature_id -> wave.
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.
            metrics: Metricas a atualizar.
            warnings: Lista de warnings.
            rng: Gerador de numeros aleatorios.
        """
        reallocation_count: dict[str, int] = {}

        for _ in range(MAX_STABILIZATION_PASSES):
            any_changes = False

            # Step 1: Check dependencies
            dep_fixed = AllocationService._final_dependency_check(
                allocated_stories,
                dependency_graph,
                story_map,
                holidays,
                config,
                metrics,
            )
            if dep_fixed:
                any_changes = True

            # Step 2: Resolve conflicts
            initial_conflict_fixes = metrics.validation_conflict_fixes
            AllocationService._resolve_allocation_conflicts(
                allocated_stories, holidays, config, metrics
            )
            if metrics.validation_conflict_fixes > initial_conflict_fixes:
                any_changes = True

            # Step 3: Check and fix idleness
            idle_fixed = AllocationService._check_and_fix_idle_violations(
                allocated_stories,
                developers,
                dev_count,
                dependency_graph,
                story_map,
                feature_map,
                reallocation_count,
                holidays,
                config,
                metrics,
                rng,
            )
            if idle_fixed:
                any_changes = True

            if not any_changes:
                break

        # Final idleness check for warnings (after stabilization)
        AllocationService._check_idleness(
            allocated_stories,
            developers,
            feature_map,
            holidays,
            config,
            metrics,
            warnings,
        )

    @staticmethod
    def allocate_stories(
        stories: Sequence[Story],
        developers: Sequence[Developer],
        dependencies: Sequence[tuple[str, str]],
        features: Sequence[Feature],
        holidays: frozenset[date],
        config: AllocationConfig,
    ) -> AllocationResult:
        """Executa alocacao automatica de desenvolvedores para historias.

        Algoritmo principal:
        1. Filtra historias elegiveis (dev=NULL, datas ok, SP ok)
        2. Constroi mapas auxiliares (feature_id->wave, story_id->Story)
        3. Agrupa historias por wave
        4. Para cada wave em ordem crescente:
           - Loop de alocacao ate estabilizar ou limite
           - Deteccao de deadlock se sem progresso
        5. Loop de estabilizacao:
           - Verifica dependencias
           - Resolve conflitos de periodo
           - Verifica ociosidade
        6. Coleta metricas e retorna resultado

        Args:
            stories: Todas as historias do backlog.
            developers: Todos os desenvolvedores disponiveis.
            dependencies: Grafo de dependencias [(story_id, depends_on_id), ...].
            features: Todas as features (para obter wave).
            holidays: Conjunto de feriados.
            config: Configuracao de alocacao.

        Returns:
            AllocationResult com historias alocadas, metricas e warnings.

        Raises:
            ValueError: Se config.velocity <= 0 ou
                config.max_idle_days fora de [2, 30].

        Example:
            >>> result = AllocationService.allocate_stories(
            ...     stories=stories,
            ...     developers=developers,
            ...     dependencies=[("B", "A")],
            ...     features=features,
            ...     holidays=BRAZILIAN_HOLIDAYS_2026_2028,
            ...     config=AllocationConfig(
            ...         velocity=2.0, project_start_date=date(2026, 3, 2)
            ...     ),
            ... )
            >>> print(result.metrics.stories_allocated)
        """
        start_time = time.perf_counter()

        # Initialize metrics and warnings
        metrics = AllocationMetrics()
        warnings: list[BacklogWarning] = []

        # Initialize RNG
        rng = random.Random(config.random_seed)

        # Build auxiliary maps
        feature_map = AllocationService._build_feature_map(features)
        story_map: dict[str, Story] = {s.id: s for s in stories}

        # Build dependency graph
        from backlog_manager.domain.services.dependency_service import DependencyService

        dependency_graph = DependencyService.build_graph(dependencies)

        # Initialize dev_count with existing allocations
        dev_count: dict[int, int] = {}
        for story in stories:
            if story.developer_id is not None:
                dev_count[story.developer_id] = dev_count.get(story.developer_id, 0) + 1

        # Group eligible stories by wave
        eligible_stories = [s for s in stories if AllocationService._is_eligible(s)]
        grouped = AllocationService._group_stories_by_wave(
            eligible_stories, feature_map
        )

        # Process waves in order
        all_allocated: list[Story] = []
        for wave in sorted(grouped.keys()):
            wave_stories = grouped[wave]
            allocated = AllocationService._allocate_by_wave(
                wave,
                wave_stories,
                developers,
                dev_count,
                dependency_graph,
                story_map,
                holidays,
                config,
                metrics,
                warnings,
                rng,
            )
            all_allocated.extend(allocated)
            metrics.waves_processed += 1

        # Stabilization loop
        AllocationService._stabilization_loop(
            all_allocated,
            developers,
            dev_count,
            dependency_graph,
            story_map,
            feature_map,
            holidays,
            config,
            metrics,
            warnings,
            rng,
        )

        # Record total time
        metrics.total_time_seconds = time.perf_counter() - start_time

        # T013: FR-001 - Log allocation summary with all 16 metrics
        logger.info(
            "Alocacao completa: %d/%d historias (%.2fs, %d ondas, %d iteracoes)",
            metrics.stories_allocated,
            metrics.stories_processed,
            metrics.total_time_seconds,
            metrics.waves_processed,
            metrics.total_iterations,
        )

        # T013: FR-001 - Log detailed metrics at DEBUG level
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "Metricas detalhadas: "
                "allocations_by_dependency_owner=%d, "
                "allocations_by_load_balancing=%d, "
                "deadlocks_detected=%d, "
                "date_adjustments=%d, "
                "validation_reallocations=%d, "
                "validation_dependency_fixes=%d, "
                "validation_conflict_fixes=%d, "
                "max_idle_violations_detected=%d, "
                "max_idle_violations_fixed=%d, "
                "failed_reallocations=%d",
                metrics.allocations_by_dependency_owner,
                metrics.allocations_by_load_balancing,
                metrics.deadlocks_detected,
                metrics.date_adjustments,
                metrics.validation_reallocations,
                metrics.validation_dependency_fixes,
                metrics.validation_conflict_fixes,
                metrics.max_idle_violations_detected,
                metrics.max_idle_violations_fixed,
                metrics.failed_reallocations,
            )

        return AllocationResult(
            allocated_stories=all_allocated,
            metrics=metrics,
            warnings=warnings,
        )
