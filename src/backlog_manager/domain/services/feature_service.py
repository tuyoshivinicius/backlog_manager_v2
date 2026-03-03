"""Feature domain service."""

from __future__ import annotations

from collections.abc import Sequence
from typing import TYPE_CHECKING

from backlog_manager.domain.entities import Feature
from backlog_manager.domain.exceptions import DuplicateWaveException

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import FeatureRepository


class FeatureService:
    """Servico de dominio para logica de negocio de features.

    Centraliza operacoes CRUD com validacoes de unicidade de wave e nome,
    e protecao contra delecao de features com historias.
    """

    def __init__(self, feature_repo: FeatureRepository) -> None:
        """Inicializa servico.

        Args:
            feature_repo: Repositorio de features.
        """
        self._feature_repo = feature_repo

    async def create_feature(self, name: str, wave: int) -> Feature:
        """Cria uma nova entidade Feature com validacao de unicidade.

        Args:
            name: Nome da feature (sera normalizado com strip).
            wave: Numero da onda (deve ser > 0).

        Returns:
            Entidade Feature (id=None, nao persistida).

        Raises:
            ValueError: Se nome vazio ou excede 100 caracteres.
            ValueError: Se wave <= 0.
            DuplicateWaveException: Se wave ja existe.
            ValueError: Se nome ja existe.
        """
        normalized_name = name.strip()

        # Fail-fast: validate wave > 0 before queries
        if wave <= 0:
            raise ValueError(f"Wave deve ser > 0: {wave}")

        # Check wave uniqueness
        existing_by_wave = await self._feature_repo.get_by_wave(wave)
        if existing_by_wave is not None:
            raise DuplicateWaveException(
                wave=wave,
                existing_feature_name=existing_by_wave.name,
            )

        # Check name uniqueness
        existing_by_name = await self._feature_repo.get_by_name(normalized_name)
        if existing_by_name is not None:
            raise ValueError(f"Feature com nome '{normalized_name}' ja existe")

        return Feature(name=normalized_name, wave=wave)

    async def update_feature(
        self,
        feature_id: int,
        name: str | None = None,
        wave: int | None = None,
    ) -> Feature:
        """Busca e atualiza feature existente (parcial).

        Args:
            feature_id: ID da feature.
            name: Novo nome (opcional, sera normalizado se fornecido).
            wave: Nova wave (opcional).

        Returns:
            Nova instancia Feature com campos atualizados.

        Raises:
            ValueError: Se feature nao encontrada.
            ValueError: Se nome invalido ou duplicado.
            DuplicateWaveException: Se wave ja existe em OUTRA feature.
        """
        existing = await self._feature_repo.get_by_id(feature_id)
        if existing is None:
            raise ValueError(f"Feature nao encontrada: {feature_id}")

        new_name = existing.name
        new_wave = existing.wave

        # Validate and update wave if provided
        if wave is not None and wave != existing.wave:
            if wave <= 0:
                raise ValueError(f"Wave deve ser > 0: {wave}")
            existing_by_wave = await self._feature_repo.get_by_wave(wave)
            if existing_by_wave is not None and existing_by_wave.id != feature_id:
                raise DuplicateWaveException(
                    wave=wave,
                    existing_feature_name=existing_by_wave.name,
                )
            new_wave = wave

        # Validate and update name if provided
        if name is not None:
            normalized_name = name.strip()
            if normalized_name != existing.name:
                existing_by_name = await self._feature_repo.get_by_name(normalized_name)
                if existing_by_name is not None and existing_by_name.id != feature_id:
                    raise ValueError(f"Feature com nome '{normalized_name}' ja existe")
                new_name = normalized_name

        return Feature(id=feature_id, name=new_name, wave=new_wave)

    async def delete_feature(self, feature_id: int) -> None:
        """Deleta feature somente se nao houver historias associadas.

        Args:
            feature_id: ID da feature.

        Raises:
            ValueError: Se feature nao encontrada.
            FeatureHasStoriesException: Se feature tem historias associadas.
        """
        existing = await self._feature_repo.get_by_id(feature_id)
        if existing is None:
            raise ValueError(f"Feature nao encontrada: {feature_id}")

        # Repository delete will check for stories and raise FeatureHasStoriesException
        await self._feature_repo.delete(feature_id)

    async def list_features(self) -> Sequence[Feature]:
        """Lista todas as features ordenadas por wave.

        Returns:
            Sequencia de features ordenadas por wave crescente.
        """
        return await self._feature_repo.get_all()
