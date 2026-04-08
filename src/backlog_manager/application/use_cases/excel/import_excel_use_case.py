"""Import Excel use case."""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from backlog_manager.application.dto.excel.import_excel_dto import (
    ImportExcelInputDTO,
    ImportExcelOutputDTO,
)
from backlog_manager.application.exceptions.excel_exceptions import (
    ExcelCycleDetectedException,
)
from backlog_manager.application.interfaces.excel_service import ExcelServiceProtocol
from backlog_manager.domain.entities import Feature, Story
from backlog_manager.domain.services.dependency_service import DependencyService
from backlog_manager.domain.services.story_service import StoryService
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

if TYPE_CHECKING:
    from backlog_manager.domain.interfaces.repositories import UnitOfWork

logger = logging.getLogger(__name__)

VALID_SP_VALUES = {3, 5, 8, 13}


class ImportExcelUseCase:
    """Caso de uso para importacao de arquivo Excel.

    Implementa importacao em dois passes:
    1. Cria stories e features (sem dependencias)
    2. Valida ciclos e cria dependencias

    Utiliza rollback via UoW se ciclo for detectado.
    """

    def __init__(
        self,
        uow: UnitOfWork,
        excel_service: ExcelServiceProtocol,
        progress_callback: Callable[[int], None] | None = None,
    ) -> None:
        """Inicializa use case.

        Args:
            uow: Unit of Work para acesso aos repositorios.
            excel_service: Servico para leitura de arquivos Excel.
            progress_callback: Callback opcional para progresso (0-100).
        """
        self._uow = uow
        self._excel_service = excel_service
        self._progress_callback = progress_callback

    async def execute(
        self, input_dto: ImportExcelInputDTO, planning_id: int
    ) -> ImportExcelOutputDTO:
        """Executa importacao de arquivo Excel.

        Fluxo:
        1. Le arquivo Excel via ExcelService
        2. Pass 1: Cria stories e features
        3. Valida grafo de dependencias (ciclos)
        4. Pass 2: Cria dependencias
        5. Commit ou rollback

        Args:
            input_dto: DTO com caminho do arquivo.
            planning_id: ID do planejamento.

        Returns:
            DTO com contagens e avisos.

        Raises:
            ExcelFileNotFoundException: Arquivo nao encontrado.
            ExcelFileCorruptedException: Arquivo invalido.
            ExcelMissingHeaderException: Headers faltando.
            ExcelCycleDetectedException: Ciclo de dependencia detectado.
        """
        logger.info("Iniciando import de arquivo: %s", input_dto.file_path)
        self._report_progress(0)

        read_result = await self._excel_service.read_stories_from_file(
            input_dto.file_path
        )
        rows = read_result.rows
        warnings = list(read_result.warnings)

        if not rows:
            logger.info("Arquivo vazio, nenhuma historia para importar")
            return ImportExcelOutputDTO(
                stories_imported=0,
                features_created=0,
                warnings=["Arquivo vazio, nenhuma historia importada"],
            )

        if len(rows) > 500:
            warnings.append(
                f"Arquivo contem {len(rows)} linhas. "
                "Arquivos com mais de 500 historias podem afetar performance."
            )

        (
            stories_imported,
            features_created,
            pending_dependencies,
            created_story_ids,
        ) = await self._execute_pass_one(planning_id, rows, warnings)

        await self._validate_cycles(planning_id, pending_dependencies)

        deps_created = await self._execute_pass_two(
            planning_id, pending_dependencies, created_story_ids, warnings
        )

        self._report_progress(100)

        logger.info(
            "Import concluido: %d historias importadas, %d features criadas, "
            "%d dependencias criadas, %d avisos",
            stories_imported,
            features_created,
            deps_created,
            len(warnings),
        )

        return ImportExcelOutputDTO(
            stories_imported=stories_imported,
            features_created=features_created,
            warnings=warnings,
        )

    async def _execute_pass_one(
        self,
        planning_id: int,
        rows: list[dict[str, Any]],
        warnings: list[str],
    ) -> tuple[int, int, list[tuple[str, list[str]]], set[str]]:
        """Pass 1: Create stories and features from rows.

        Args:
            planning_id: ID do planejamento.
            rows: List of row dicts from Excel.
            warnings: List to accumulate warnings.

        Returns:
            Tuple of (stories_imported, features_created,
            pending_dependencies, created_story_ids).
        """
        stories_imported = 0
        features_created = 0
        story_service = StoryService(self._uow.stories)
        feature_cache: dict[str, int] = {}
        pending_dependencies: list[tuple[str, list[str]]] = []
        created_story_ids: set[str] = set()
        total_rows = len(rows)

        for idx, row in enumerate(rows, start=1):
            try:
                story, feature_was_created = await self._process_row_pass_one(
                    planning_id=planning_id,
                    row=row,
                    row_number=idx + 1,
                    story_service=story_service,
                    feature_cache=feature_cache,
                    warnings=warnings,
                )

                if story is not None:
                    created_story_ids.add(story.id)
                    stories_imported += 1
                    if feature_was_created:
                        features_created += 1

                    self._collect_row_dependencies(row, story.id, pending_dependencies)

            except Exception as e:
                logger.warning("Linha %d ignorada: %s", idx + 1, str(e))
                warnings.append(f"Linha {idx + 1}: {e}")

            self._report_progress(int((idx / total_rows) * 50))

        return (
            stories_imported,
            features_created,
            pending_dependencies,
            created_story_ids,
        )

    def _collect_row_dependencies(
        self,
        row: dict[str, Any],
        story_id: str,
        pending_dependencies: list[tuple[str, list[str]]],
    ) -> None:
        """Collect dependencies from a row for pass 2.

        Args:
            row: Row dict from Excel.
            story_id: ID of the created story.
            pending_dependencies: List to append dependencies to.
        """
        deps_str = row.get("Dependencias")
        if not deps_str or not str(deps_str).strip():
            return
        dep_ids = self._parse_dependencies(str(deps_str))
        if dep_ids:
            pending_dependencies.append((story_id, dep_ids))

    async def _validate_cycles(
        self,
        planning_id: int,
        pending_dependencies: list[tuple[str, list[str]]],
    ) -> None:
        """Validate that pending dependencies do not create cycles.

        Args:
            planning_id: ID do planning ativo.
            pending_dependencies: List of (story_id, dep_ids) tuples.

        Raises:
            ExcelCycleDetectedException: If a cycle is detected.
        """
        if not pending_dependencies:
            return

        existing_deps = await self._uow.dependencies.get_all_dependencies(planning_id)
        all_deps = list(existing_deps)

        for story_id, dep_ids in pending_dependencies:
            for dep_id in dep_ids:
                all_deps.append((story_id, dep_id))

        graph = DependencyService.build_graph(all_deps)
        cycle = self._detect_any_cycle(graph)
        if cycle:
            cycle_path = " -> ".join(cycle)
            logger.error("Ciclo de dependencia detectado: %s", cycle_path)
            raise ExcelCycleDetectedException(
                f"Ciclo de dependencia detectado: {cycle_path}. "
                "Nenhum dado foi importado."
            )

    async def _execute_pass_two(
        self,
        planning_id: int,
        pending_dependencies: list[tuple[str, list[str]]],
        created_story_ids: set[str],
        warnings: list[str],
    ) -> int:
        """Pass 2: Create dependencies between stories.

        Args:
            planning_id: ID do planning ativo.
            pending_dependencies: List of (story_id, dep_ids) tuples.
            created_story_ids: Set of story IDs created in pass 1.
            warnings: List to accumulate warnings.

        Returns:
            Number of dependencies created.
        """
        deps_created = 0
        total = len(pending_dependencies)

        for dep_idx, (story_id, dep_ids) in enumerate(pending_dependencies):
            deps_created += await self._create_dependencies_for_story(
                planning_id, story_id, dep_ids, created_story_ids, warnings
            )

            self._report_progress(50 + int((dep_idx + 1) / total * 50))

        return deps_created

    async def _create_dependencies_for_story(
        self,
        planning_id: int,
        story_id: str,
        dep_ids: list[str],
        created_story_ids: set[str],
        warnings: list[str],
    ) -> int:
        """Create dependencies for a single story.

        Args:
            planning_id: ID do planning ativo.
            story_id: Story that depends on others.
            dep_ids: IDs of stories it depends on.
            created_story_ids: Set of story IDs created in pass 1.
            warnings: List to accumulate warnings.

        Returns:
            Number of dependencies created.
        """
        deps_created = 0
        for dep_id in dep_ids:
            try:
                dep_exists = (
                    dep_id in created_story_ids
                    or await self._uow.stories.exists(planning_id, dep_id)
                )
                if not dep_exists:
                    warnings.append(
                        f"Dependencia {story_id} -> {dep_id}: "
                        f"historia {dep_id} nao encontrada, ignorada"
                    )
                    continue

                already_exists = await self._uow.dependencies.exists(
                    planning_id, story_id, dep_id
                )
                if not already_exists:
                    await self._uow.dependencies.add(planning_id, story_id, dep_id)
                    deps_created += 1

            except Exception as e:
                warnings.append(
                    f"Erro ao criar dependencia {story_id} -> {dep_id}: {e}"
                )
        return deps_created

    async def _process_row_pass_one(
        self,
        planning_id: int,
        row: dict[str, Any],
        row_number: int,
        story_service: StoryService,
        feature_cache: dict[str, int],
        warnings: list[str],
    ) -> tuple[Story | None, bool]:
        """Processa uma linha do Excel no pass 1 (cria story e feature).

        Args:
            planning_id: ID do planning ativo.
            row: Dicionario com dados da linha.
            row_number: Numero da linha no Excel (para mensagens).
            story_service: Servico para geracao de ID.
            feature_cache: Cache de features por nome.
            warnings: Lista para acumular avisos.

        Returns:
            Tupla (story criada ou None, feature foi criada).
        """
        feature_created = False

        # Get and validate ID/Component
        story_id = await self._generate_id_if_needed(
            planning_id, row, row_number, story_service
        )
        if story_id is None:
            return None, False

        # Check if story already exists
        if await self._uow.stories.exists(planning_id, story_id):
            warnings.append(
                f"Linha {row_number}: Historia {story_id} ja existe, ignorada"
            )
            return None, False

        # Validate Name
        name = row.get("Nome")
        if not name or not str(name).strip():
            warnings.append(f"Linha {row_number}: Nome vazio, linha ignorada")
            return None, False
        name = str(name).strip()

        if len(name) > 200:
            warnings.append(f"Linha {row_number}: Nome excede 200 caracteres, truncado")
            name = name[:200]

        # Validate SP
        sp_raw = row.get("SP")
        try:
            sp_value = int(sp_raw) if sp_raw is not None else None
        except (ValueError, TypeError):
            sp_value = None

        if sp_value not in VALID_SP_VALUES:
            warnings.append(
                f"Linha {row_number}: Story Points invalido ({sp_raw}), "
                "deve ser 3, 5, 8 ou 13. Linha ignorada"
            )
            return None, False

        # Get component from ID
        component = story_id.rsplit("-", 1)[0]

        # Handle Feature
        feature_id: int | None = None
        feature_name = row.get("Feature")
        if feature_name and str(feature_name).strip():
            feature_name = str(feature_name).strip()
            feature_id, was_created = await self._create_feature_if_needed(
                feature_name, feature_cache
            )
            if was_created:
                feature_created = True

        # Get next priority
        priority = await story_service.get_next_priority(planning_id)

        # Create story entity
        story = Story(
            planning_id=planning_id,
            id=story_id,
            component=component,
            name=name,
            story_points=StoryPoint(sp_value),
            priority=priority,
            status=StoryStatus.BACKLOG,
            feature_id=feature_id,
        )

        # Persist story
        await self._uow.stories.add(story)

        return story, feature_created

    async def _generate_id_if_needed(
        self,
        planning_id: int,
        row: dict[str, Any],
        row_number: int,
        story_service: StoryService,
    ) -> str | None:
        """Gera ID automatico se coluna ID estiver vazia.

        Args:
            planning_id: ID do planning ativo.
            row: Dicionario com dados da linha.
            row_number: Numero da linha no Excel.
            story_service: Servico para geracao de ID.

        Returns:
            ID da historia ou None se invalido.
        """
        story_id = row.get("ID")
        if story_id and str(story_id).strip():
            return str(story_id).strip().upper()

        # ID vazio, usar Componente para gerar
        component = row.get("Componente")
        if not component or not str(component).strip():
            logger.warning(
                "Linha %d: ID e Componente vazios, linha ignorada", row_number
            )
            return None

        component = str(component).strip().upper()

        if len(component) > 50:
            logger.warning("Linha %d: Componente excede 50 caracteres", row_number)
            return None

        # Generate ID
        return await story_service.generate_story_id(planning_id, component)

    async def _create_feature_if_needed(
        self, feature_name: str, feature_cache: dict[str, int]
    ) -> tuple[int, bool]:
        """Cria feature se nao existir.

        Args:
            feature_name: Nome da feature.
            feature_cache: Cache de features por nome.

        Returns:
            Tupla (feature_id, foi_criada).
        """
        # Check cache first
        if feature_name in feature_cache:
            return feature_cache[feature_name], False

        # Check database
        existing = await self._uow.features.get_by_name(feature_name)
        if existing is not None and existing.id is not None:
            feature_cache[feature_name] = existing.id
            return existing.id, False

        # Create new feature with wave=1 per ADR-005
        # Find next available wave
        all_features = await self._uow.features.get_all()
        used_waves = {f.wave for f in all_features}
        next_wave = 1
        while next_wave in used_waves:
            next_wave += 1

        feature = Feature(name=feature_name, wave=next_wave)
        feature_id = await self._uow.features.add(feature)
        feature_cache[feature_name] = feature_id

        logger.info("Feature criada: %s (wave=%d)", feature_name, next_wave)
        return feature_id, True

    def _parse_dependencies(self, deps_str: str) -> list[str]:
        """Parse string de dependencias separadas por ponto-e-virgula.

        Args:
            deps_str: String com IDs separados por ";".

        Returns:
            Lista de IDs de dependencias.
        """
        if not deps_str or not deps_str.strip():
            return []

        deps = []
        for part in deps_str.split(";"):
            dep_id = part.strip().upper()
            if dep_id:
                deps.append(dep_id)

        return deps

    def _detect_any_cycle(self, graph: dict[str, list[str]]) -> list[str] | None:
        """Detecta qualquer ciclo no grafo.

        Args:
            graph: Grafo de adjacencia.

        Returns:
            Caminho do ciclo se encontrado, None caso contrario.
        """
        for node in graph:
            for target in graph.get(node, []):
                cycle = DependencyService.detect_cycle(graph, node, target)
                if cycle:
                    return cycle
        return None

    def _report_progress(self, percent: int) -> None:
        """Reporta progresso via callback.

        Args:
            percent: Percentual de progresso (0-100).
        """
        if self._progress_callback is not None:
            self._progress_callback(min(100, max(0, percent)))
