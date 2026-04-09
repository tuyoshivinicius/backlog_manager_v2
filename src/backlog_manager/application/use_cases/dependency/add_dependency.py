"""AddDependency use case."""

from __future__ import annotations

from typing import TYPE_CHECKING

from backlog_manager.application.dto.dependency import (
    AddDependencyInputDTO,
    AddDependencyOutputDTO,
    InvalidWaveDependencyWarningDTO,
)
from backlog_manager.domain.exceptions.dependency import CyclicDependencyException
from backlog_manager.domain.services.dependency_service import DependencyService

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork


class AddDependencyUseCase:
    """Use case para adicionar dependencia entre historias.

    Valida existencia das historias, verifica ciclos via
    DependencyService, e emite warning para dependencias
    entre waves invalidas.

    Attributes:
        _uow: Unit of Work para acesso aos repositorios.
    """

    def __init__(self, uow: UnitOfWork) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
        """
        self._uow = uow

    async def execute(
        self, input_dto: AddDependencyInputDTO, planning_id: int
    ) -> AddDependencyOutputDTO:
        """Executa adicao de dependencia.

        Fluxo:
        1. Valida que story_id != depends_on_id
        2. Valida existencia de ambas historias
        3. Verifica se dependencia ja existe
        4. Constroi grafo e verifica ciclos
        5. Valida waves e gera warning se necessario
        6. Persiste dependencia

        Args:
            input_dto: DTO com dados da dependencia.
            planning_id: ID do planejamento.

        Args:
            input_dto: DTO com story_id e depends_on_id.

        Returns:
            DTO com resultado da operacao e warning opcional.

        Raises:
            ValueError: Se historias nao existem, IDs iguais, ou duplicata.
            CyclicDependencyException: Se criaria ciclo no grafo.
        """
        story_id = input_dto.story_id
        depends_on_id = input_dto.depends_on_id

        # 1. Self-dependency check
        if story_id == depends_on_id:
            raise ValueError("Historia nao pode depender de si mesma")

        # 2. Story existence validation
        story_exists = await self._uow.stories.exists(planning_id, story_id)
        if not story_exists:
            raise ValueError(f"Historia {story_id} nao encontrada")

        depends_on_exists = await self._uow.stories.exists(planning_id, depends_on_id)
        if not depends_on_exists:
            raise ValueError(f"Historia {depends_on_id} nao encontrada")

        # 3. Duplicate dependency check
        dependency_exists = await self._uow.dependencies.exists(
            planning_id, story_id, depends_on_id
        )
        if dependency_exists:
            raise ValueError(
                f"Dependencia de {story_id} para {depends_on_id} ja existe"
            )

        # 4. Cycle detection
        all_dependencies = await self._uow.dependencies.get_all_dependencies(
            planning_id
        )
        graph = DependencyService.build_graph(all_dependencies)
        cycle = DependencyService.would_create_cycle(graph, story_id, depends_on_id)
        if cycle:
            raise CyclicDependencyException(cycle)

        # 5. Wave validation
        warning = await self._get_wave_warning(planning_id, story_id, depends_on_id)

        # 6. Persist dependency
        await self._uow.dependencies.add(planning_id, story_id, depends_on_id)

        return AddDependencyOutputDTO(
            success=True,
            story_id=story_id,
            depends_on_id=depends_on_id,
            warning=warning,
        )

    async def _get_wave_warning(
        self, planning_id: int, story_id: str, depends_on_id: str
    ) -> InvalidWaveDependencyWarningDTO | None:
        """Verifica e gera warning para dependencias entre waves.

        Args:
            planning_id: ID do planning ativo.
            story_id: ID da historia que depende.
            depends_on_id: ID da historia da qual depende.

        Returns:
            WarningDTO se dependencia for entre waves invalidas, None otherwise.
        """
        # Get stories to access feature_id
        story = await self._uow.stories.get_by_id(planning_id, story_id)
        depends_on = await self._uow.stories.get_by_id(planning_id, depends_on_id)

        if story is None or depends_on is None:
            return None  # Should not happen, already validated

        # Get waves from features
        story_wave = 0
        depends_on_wave = 0

        if story.feature_id is not None:
            feature = await self._uow.features.get_by_id(story.feature_id)
            if feature is not None:
                story_wave = feature.wave

        if depends_on.feature_id is not None:
            feature = await self._uow.features.get_by_id(depends_on.feature_id)
            if feature is not None:
                depends_on_wave = feature.wave

        # Validate wave dependency
        is_valid = DependencyService.validate_wave_dependency(
            story_wave, depends_on_wave
        )
        if not is_valid:
            return InvalidWaveDependencyWarningDTO(
                story_id=story_id,
                depends_on_id=depends_on_id,
                story_wave=story_wave,
                depends_on_wave=depends_on_wave,
                message=(
                    f"Historia {story_id} (wave {story_wave}) depende de "
                    f"{depends_on_id} (wave {depends_on_wave}): "
                    f"dependencia de wave posterior"
                ),
            )

        return None
