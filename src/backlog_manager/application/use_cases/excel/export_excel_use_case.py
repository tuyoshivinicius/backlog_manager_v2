"""Export Excel use case."""

from __future__ import annotations

import logging
from collections.abc import Sequence
from typing import TYPE_CHECKING, Any

from backlog_manager.application.dto.excel.export_excel_dto import (
    ExcelExportData,
    ExportExcelInputDTO,
    ExportExcelOutputDTO,
)
from backlog_manager.application.interfaces.excel_service import ExcelServiceProtocol

if TYPE_CHECKING:
    from backlog_manager.domain.entities import Developer, Feature, Story
    from backlog_manager.domain.interfaces.repositories import UnitOfWork

logger = logging.getLogger(__name__)


class ExportExcelUseCase:
    """Caso de uso para exportacao de backlog para arquivo Excel.

    Exporta todas as stories, developers e features em um unico
    arquivo Excel com tres planilhas.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        excel_service: ExcelServiceProtocol,
    ) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
            excel_service: Servico para escrita de arquivos Excel.
        """
        self._uow = uow
        self._excel_service = excel_service

    async def execute(
        self, planning_id: int, input_dto: ExportExcelInputDTO
    ) -> ExportExcelOutputDTO:
        """Executa exportacao de backlog para arquivo Excel.

        Fluxo:
        1. Busca todas as stories com seus relacionamentos
        2. Busca todos os developers
        3. Busca todas as features
        4. Constroi ExcelExportData
        5. Escreve arquivo via ExcelService

        Args:
            planning_id: ID do planejamento.
            input_dto: DTO com caminho do arquivo de destino.

        Returns:
            DTO com caminho e contagens.

        Raises:
            ExcelPermissionException: Sem permissao de escrita.
            ExcelFileCorruptedException: Erro ao escrever arquivo.
        """
        logger.info("Iniciando export para arquivo: %s", input_dto.file_path)

        # Fetch all data
        stories = await self._uow.stories.get_all(planning_id)
        developers = await self._uow.developers.get_all()
        features = await self._uow.features.get_all()

        # Build lookup maps for names
        developer_map = {d.id: d.name for d in developers if d.id is not None}
        feature_map = {f.id: f.name for f in features if f.id is not None}

        # Build stories data
        stories_data = await self._build_stories_data(
            stories, developer_map, feature_map
        )

        # Build developers data
        developers_data = self._build_developers_data(developers)

        # Build features data
        features_data = self._build_features_data(features)

        # Create export data
        export_data = ExcelExportData(
            stories=stories_data,
            developers=developers_data,
            features=features_data,
        )

        # Write file
        await self._excel_service.write_workbook(input_dto.file_path, export_data)

        logger.info(
            "Export concluido: %d historias, %d desenvolvedores, %d features em %s",
            len(stories_data),
            len(developers_data),
            len(features_data),
            input_dto.file_path,
        )

        return ExportExcelOutputDTO(
            file_path=input_dto.file_path,
            stories_exported=len(stories_data),
            developers_exported=len(developers_data),
            features_exported=len(features_data),
        )

    async def _build_stories_data(
        self,
        stories: Sequence[Story],
        developer_map: dict[int, str],
        feature_map: dict[int, str],
    ) -> list[dict[str, Any]]:
        """Constroi dados das stories para exportacao.

        Args:
            stories: Lista de entidades Story.
            developer_map: Mapa de developer_id -> nome.
            feature_map: Mapa de feature_id -> nome.

        Returns:
            Lista de dicionarios com dados formatados.
        """
        result = []

        for story in stories:
            # Get dependencies for this story
            deps = await self._uow.dependencies.get_dependencies(
                story.planning_id, story.id
            )
            deps_str = self._format_dependencies(list(deps))

            # Get developer name
            dev_name = ""
            if story.developer_id is not None:
                dev_name = developer_map.get(story.developer_id, "")

            # Get feature name
            feature_name = ""
            if story.feature_id is not None:
                feature_name = feature_map.get(story.feature_id, "")

            row = {
                "ID": story.id,
                "Componente": story.component,
                "Nome": story.name,
                "SP": int(story.story_points),
                "Status": (
                    story.status.value
                    if hasattr(story.status, "value")
                    else str(story.status)
                ),
                "Feature": feature_name,
                "Dependencias": deps_str,
                "Desenvolvedor": dev_name,
                "Data Inicio": story.start_date,
                "Data Fim": story.end_date,
            }
            result.append(row)

        return result

    def _build_developers_data(
        self, developers: Sequence[Developer]
    ) -> list[dict[str, Any]]:
        """Constroi dados dos desenvolvedores para exportacao.

        Args:
            developers: Lista de entidades Developer.

        Returns:
            Lista de dicionarios com dados formatados.
        """
        return [{"ID": d.id, "Nome": d.name} for d in developers]

    def _build_features_data(self, features: Sequence[Feature]) -> list[dict[str, Any]]:
        """Constroi dados das features para exportacao.

        Args:
            features: Lista de entidades Feature.

        Returns:
            Lista de dicionarios com dados formatados.
        """
        return [{"ID": f.id, "Nome": f.name, "Wave": f.wave} for f in features]

    def _format_dependencies(self, dep_ids: list[str]) -> str:
        """Formata lista de IDs de dependencias para string.

        Args:
            dep_ids: Lista de IDs de dependencias.

        Returns:
            String com IDs separados por ponto-e-virgula.
        """
        return ";".join(dep_ids) if dep_ids else ""
