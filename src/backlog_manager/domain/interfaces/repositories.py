"""Repository protocols (interfaces)."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING, Protocol

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Developer, Feature, Story


class StoryRepository(Protocol):
    """Interface para persistencia de historias."""

    async def add(self, story: Story) -> None:
        """Adiciona uma nova historia ao repositorio.

        Args:
            story: Historia a ser adicionada.

        Raises:
            ValueError: Se historia com mesmo ID ja existe.
        """
        ...

    async def get_by_id(self, story_id: str) -> Story | None:
        """Busca historia por ID.

        Args:
            story_id: Identificador da historia.

        Returns:
            Historia encontrada ou None se nao existir.
        """
        ...

    async def get_all(self) -> Sequence[Story]:
        """Retorna todas as historias.

        Returns:
            Lista de todas as historias ordenadas por prioridade.
        """
        ...

    async def get_by_status(self, status: str) -> Sequence[Story]:
        """Busca historias por status.

        Args:
            status: Status a filtrar (BACKLOG, IN_PROGRESS, DONE, BLOCKED).

        Returns:
            Lista de historias com o status especificado.
        """
        ...

    async def get_by_developer(self, developer_id: int) -> Sequence[Story]:
        """Busca historias alocadas a um desenvolvedor.

        Args:
            developer_id: ID do desenvolvedor.

        Returns:
            Lista de historias alocadas ao desenvolvedor.
        """
        ...

    async def get_by_feature(self, feature_id: int) -> Sequence[Story]:
        """Busca historias de uma feature.

        Args:
            feature_id: ID da feature.

        Returns:
            Lista de historias da feature.
        """
        ...

    async def update(self, story: Story) -> None:
        """Atualiza uma historia existente.

        Args:
            story: Historia com dados atualizados.

        Raises:
            ValueError: Se historia nao existe.
        """
        ...

    async def delete(self, story_id: str) -> None:
        """Remove uma historia.

        Args:
            story_id: ID da historia a remover.

        Raises:
            ValueError: Se historia nao existe.
        """
        ...

    async def exists(self, story_id: str) -> bool:
        """Verifica se historia existe.

        Args:
            story_id: ID da historia.

        Returns:
            True se existe, False caso contrario.
        """
        ...

    async def get_max_id_number(self, component: str) -> int:
        """Retorna o maior numero sequencial para um componente.

        Args:
            component: Nome do componente (case-insensitive).

        Returns:
            Maior numero NNN encontrado ou 0 se nenhum.
        """
        ...

    async def get_max_priority(self) -> int:
        """Retorna a maior prioridade existente no backlog.

        Returns:
            Maior prioridade ou 0 se backlog vazio.
        """
        ...

    async def get_by_priority(self, priority: int) -> Story | None:
        """Busca historia por prioridade exata.

        Args:
            priority: Prioridade a buscar.

        Returns:
            Historia encontrada ou None.
        """
        ...


class DeveloperRepository(Protocol):
    """Interface para persistencia de desenvolvedores."""

    async def add(self, developer: Developer) -> int:
        """Adiciona um novo desenvolvedor.

        Args:
            developer: Desenvolvedor a ser adicionado.

        Returns:
            ID gerado para o desenvolvedor.
        """
        ...

    async def get_by_id(self, developer_id: int) -> Developer | None:
        """Busca desenvolvedor por ID.

        Args:
            developer_id: Identificador do desenvolvedor.

        Returns:
            Desenvolvedor encontrado ou None se nao existir.
        """
        ...

    async def get_all(self) -> Sequence[Developer]:
        """Retorna todos os desenvolvedores.

        Returns:
            Lista de todos os desenvolvedores ordenados por nome.
        """
        ...

    async def update(self, developer: Developer) -> None:
        """Atualiza um desenvolvedor existente.

        Args:
            developer: Desenvolvedor com dados atualizados.

        Raises:
            ValueError: Se desenvolvedor nao existe.
        """
        ...

    async def delete(self, developer_id: int) -> None:
        """Remove um desenvolvedor.

        Args:
            developer_id: ID do desenvolvedor a remover.

        Raises:
            ValueError: Se desenvolvedor nao existe.

        Note:
            Historias alocadas terao developer_id = NULL (ON DELETE SET NULL).
        """
        ...

    async def exists(self, developer_id: int) -> bool:
        """Verifica se desenvolvedor existe.

        Args:
            developer_id: ID do desenvolvedor.

        Returns:
            True se existe, False caso contrario.
        """
        ...


class FeatureRepository(Protocol):
    """Interface para persistencia de features."""

    async def add(self, feature: Feature) -> int:
        """Adiciona uma nova feature.

        Args:
            feature: Feature a ser adicionada.

        Returns:
            ID gerado para a feature.

        Raises:
            DuplicateWaveException: Se wave ja existe.
            ValueError: Se nome ja existe.
        """
        ...

    async def get_by_id(self, feature_id: int) -> Feature | None:
        """Busca feature por ID.

        Args:
            feature_id: Identificador da feature.

        Returns:
            Feature encontrada ou None se nao existir.
        """
        ...

    async def get_by_wave(self, wave: int) -> Feature | None:
        """Busca feature por numero de wave.

        Args:
            wave: Numero da wave.

        Returns:
            Feature encontrada ou None se nao existir.
        """
        ...

    async def get_all(self) -> Sequence[Feature]:
        """Retorna todas as features.

        Returns:
            Lista de todas as features ordenadas por wave.
        """
        ...

    async def update(self, feature: Feature) -> None:
        """Atualiza uma feature existente.

        Args:
            feature: Feature com dados atualizados.

        Raises:
            ValueError: Se feature nao existe.
            DuplicateWaveException: Se nova wave ja existe.
        """
        ...

    async def delete(self, feature_id: int) -> None:
        """Remove uma feature.

        Args:
            feature_id: ID da feature a remover.

        Raises:
            ValueError: Se feature nao existe.
            FeatureHasStoriesException: Se feature tem historias associadas.
        """
        ...

    async def exists(self, feature_id: int) -> bool:
        """Verifica se feature existe.

        Args:
            feature_id: ID da feature.

        Returns:
            True se existe, False caso contrario.
        """
        ...

    async def has_stories(self, feature_id: int) -> bool:
        """Verifica se feature tem historias associadas.

        Args:
            feature_id: ID da feature.

        Returns:
            True se tem historias, False caso contrario.
        """
        ...


class StoryDependencyRepository(Protocol):
    """Interface para persistencia de dependencias entre historias."""

    async def add(self, story_id: str, depends_on_id: str) -> None:
        """Adiciona uma dependencia entre historias.

        Args:
            story_id: ID da historia que depende.
            depends_on_id: ID da historia da qual depende.

        Raises:
            ValueError: Se dependencia ja existe ou historias nao existem.
            CyclicDependencyException: Se criaria ciclo.
        """
        ...

    async def remove(self, story_id: str, depends_on_id: str) -> None:
        """Remove uma dependencia entre historias.

        Args:
            story_id: ID da historia que depende.
            depends_on_id: ID da historia da qual depende.

        Raises:
            ValueError: Se dependencia nao existe.
        """
        ...

    async def get_dependencies(self, story_id: str) -> Sequence[str]:
        """Retorna IDs das historias das quais uma historia depende.

        Args:
            story_id: ID da historia.

        Returns:
            Lista de IDs das dependencias.
        """
        ...

    async def get_dependents(self, story_id: str) -> Sequence[str]:
        """Retorna IDs das historias que dependem de uma historia.

        Args:
            story_id: ID da historia.

        Returns:
            Lista de IDs das historias dependentes.
        """
        ...

    async def exists(self, story_id: str, depends_on_id: str) -> bool:
        """Verifica se dependencia existe.

        Args:
            story_id: ID da historia que depende.
            depends_on_id: ID da historia da qual depende.

        Returns:
            True se existe, False caso contrario.
        """
        ...

    async def get_all_dependencies(self) -> Sequence[tuple[str, str]]:
        """Retorna todas as dependencias.

        Returns:
            Lista de tuplas (story_id, depends_on_id).
        """
        ...

    async def remove_all_for_story(self, story_id: str) -> None:
        """Remove todas as dependencias onde a historia aparece.

        Args:
            story_id: ID da historia.

        Note:
            Remove onde story_id e o dependente E onde e a dependencia.
        """
        ...


class UnitOfWork(Protocol):
    """Interface para gerenciamento de transacoes."""

    stories: StoryRepository
    developers: DeveloperRepository
    features: FeatureRepository
    dependencies: StoryDependencyRepository

    async def __aenter__(self) -> UnitOfWork:
        """Inicia transacao."""
        ...

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Finaliza transacao (commit ou rollback)."""
        ...

    async def commit(self) -> None:
        """Confirma transacao."""
        ...

    async def rollback(self) -> None:
        """Reverte transacao."""
        ...
