"""Developer domain service."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from backlog_manager.domain.entities import Developer

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import (
        DeveloperRepository,
        StoryRepository,
    )


class DeveloperService:
    """Servico de dominio para logica de negocio de desenvolvedores.

    Centraliza operacoes CRUD com validacoes de negocio.
    """

    def __init__(
        self,
        developer_repo: DeveloperRepository,
        story_repo: StoryRepository,
    ) -> None:
        """Inicializa servico.

        Args:
            developer_repo: Repositorio de desenvolvedores.
            story_repo: Repositorio de historias (para contagem).
        """
        self._developer_repo = developer_repo
        self._story_repo = story_repo

    def create_developer(self, name: str) -> Developer:
        """Cria uma nova entidade Developer validada.

        Args:
            name: Nome do desenvolvedor (sera normalizado com strip).

        Returns:
            Entidade Developer (id=None, nao persistida).

        Raises:
            ValueError: Se nome vazio ou excede 100 caracteres.
        """
        normalized_name = name.strip()
        return Developer(name=normalized_name)

    async def update_developer(
        self,
        developer_id: int,
        name: str,
    ) -> Developer:
        """Busca e atualiza desenvolvedor existente.

        Args:
            developer_id: ID do desenvolvedor.
            name: Novo nome (sera normalizado com strip).

        Returns:
            Nova instancia Developer com nome atualizado.

        Raises:
            ValueError: Se desenvolvedor nao encontrado.
            ValueError: Se nome invalido.
        """
        existing = await self._developer_repo.get_by_id(developer_id)
        if existing is None:
            raise ValueError(f"Desenvolvedor nao encontrado: {developer_id}")

        normalized_name = name.strip()
        return Developer(id=developer_id, name=normalized_name)

    async def delete_developer(self, developer_id: int) -> int:
        """Deleta desenvolvedor e retorna contagem de historias desalocadas.

        Args:
            developer_id: ID do desenvolvedor.

        Returns:
            Numero de historias que foram desalocadas (via ON DELETE SET NULL).

        Raises:
            ValueError: Se desenvolvedor nao encontrado.
        """
        existing = await self._developer_repo.get_by_id(developer_id)
        if existing is None:
            raise ValueError(f"Desenvolvedor nao encontrado: {developer_id}")

        count = await self._story_repo.count_by_developer(developer_id)
        await self._developer_repo.delete(developer_id)
        return count

    async def list_developers(self) -> Sequence[Developer]:
        """Lista todos os desenvolvedores ordenados por nome.

        Returns:
            Sequencia de desenvolvedores ordenados alfabeticamente.
        """
        return await self._developer_repo.get_all()
