"""E2E tests for UC-003: Detectar e Resolver Deadlock.

Tests the cyclic dependency detection flow including direct
and indirect cycle detection.
"""

from __future__ import annotations

import pytest

from backlog_manager.application.dto.dependency import (
    AddDependencyInputDTO,
    GetDependenciesInputDTO,
    RemoveDependencyInputDTO,
)
from backlog_manager.application.dto.story import CreateStoryInputDTO
from backlog_manager.domain.exceptions import CyclicDependencyException
from tests.e2e.factories import (
    create_cyclic_graph,
    create_stories,
    get_dependency_pairs,
)

pytestmark = [pytest.mark.e2e]


class TestUC003DetectarCicloDireto:
    """Tests for direct cycle detection (FR-036)."""

    @pytest.mark.asyncio
    async def test_detectar_ciclo_direto_a_depende_de_b_depende_de_a(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test detection of direct cycle: A -> B -> A.

        FR-036: Direct cycles should be detected and rejected.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create two stories
        dto1 = CreateStoryInputDTO(
            component="CYC",
            name="Historia A",
            story_points=5,
        )
        dto2 = CreateStoryInputDTO(
            component="CYC",
            name="Historia B",
            story_points=5,
        )
        await viewmodel.create_story(dto1)
        await viewmodel.create_story(dto2)

        # Add dependency: CYC-002 depends on CYC-001
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="CYC-002", depends_on_id="CYC-001")
            )
            await uow.commit()

        # Try to add cycle: CYC-001 depends on CYC-002 (should fail)
        error_raised = False
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="CYC-001", depends_on_id="CYC-002")
                )
                await uow.commit()
            except CyclicDependencyException:
                error_raised = True

        assert error_raised, "Cyclic dependency should have been rejected"

    @pytest.mark.asyncio
    async def test_detectar_auto_dependencia(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test detection of self-dependency: A -> A.

        FR-036: Self-dependencies should be rejected.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create story
        dto = CreateStoryInputDTO(
            component="SELF",
            name="Historia Auto",
            story_points=5,
        )
        await viewmodel.create_story(dto)

        # Try to add self-dependency
        error_raised = False
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="SELF-001", depends_on_id="SELF-001")
                )
                await uow.commit()
            except Exception:
                error_raised = True

        assert error_raised, "Self-dependency should have been rejected"


class TestUC003DetectarCicloIndireto:
    """Tests for indirect cycle detection (FR-037)."""

    @pytest.mark.asyncio
    async def test_detectar_ciclo_indireto_a_b_c_a(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test detection of indirect cycle: A -> B -> C -> A.

        FR-037: Indirect cycles should be detected and rejected.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create three stories
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="IND",
                name=f"Historia {chr(64 + i)}",  # A, B, C
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Create chain: IND-002 depends on IND-001, IND-003 depends on IND-002
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="IND-002", depends_on_id="IND-001")
            )  # B -> A
            await add_dep.execute(
                AddDependencyInputDTO(story_id="IND-003", depends_on_id="IND-002")
            )  # C -> B
            await uow.commit()

        # Try to close cycle: IND-001 depends on IND-003 (A -> C, creating A->B->C->A)
        error_raised = False
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="IND-001", depends_on_id="IND-003")
                )
                await uow.commit()
            except CyclicDependencyException:
                error_raised = True

        assert error_raised, "Indirect cyclic dependency should have been rejected"

    @pytest.mark.asyncio
    async def test_detectar_ciclo_cadeia_longa(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test detection of cycle in long chain.

        FR-037: Cycles in chains of any length should be detected.
        """
        viewmodel = e2e_main_window.viewmodel

        # Create 5 stories
        for i in range(1, 6):
            dto = CreateStoryInputDTO(
                component="LONG",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Create chain: 2->1, 3->2, 4->3, 5->4
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            for i in range(2, 6):
                await add_dep.execute(
                    AddDependencyInputDTO(
                        story_id=f"LONG-{i:03d}", depends_on_id=f"LONG-{i-1:03d}"
                    )
                )
            await uow.commit()

        # Try to close cycle: 1 depends on 5
        error_raised = False
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="LONG-001", depends_on_id="LONG-005")
                )
                await uow.commit()
            except CyclicDependencyException:
                error_raised = True

        assert error_raised, "Long chain cycle should have been rejected"


class TestUC003ValidDependencies:
    """Tests for valid (non-cyclic) dependencies."""

    @pytest.mark.asyncio
    async def test_permitir_dependencia_valida(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that valid dependencies are accepted."""
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        for i in range(1, 4):
            dto = CreateStoryInputDTO(
                component="VAL",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Add valid dependencies (no cycles)
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="VAL-002", depends_on_id="VAL-001")
            )  # 2 -> 1
            await add_dep.execute(
                AddDependencyInputDTO(story_id="VAL-003", depends_on_id="VAL-001")
            )  # 3 -> 1 (parallel to 2)
            await uow.commit()

        # Verify dependencies were added
        async with e2e_app.create_unit_of_work() as uow:
            get_deps = e2e_app.create_get_dependencies_use_case(uow)
            result_2 = await get_deps.execute(
                GetDependenciesInputDTO(story_id="VAL-002")
            )
            result_3 = await get_deps.execute(
                GetDependenciesInputDTO(story_id="VAL-003")
            )

        assert "VAL-001" in result_2.dependencies
        assert "VAL-001" in result_3.dependencies

    @pytest.mark.asyncio
    async def test_permitir_multiplas_dependencias(
        self, e2e_main_window, e2e_app, qasync_loop
    ):
        """Test that a story can have multiple dependencies."""
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        for i in range(1, 5):
            dto = CreateStoryInputDTO(
                component="MULT",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Story 4 depends on 1, 2, and 3
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="MULT-004", depends_on_id="MULT-001")
            )
            await add_dep.execute(
                AddDependencyInputDTO(story_id="MULT-004", depends_on_id="MULT-002")
            )
            await add_dep.execute(
                AddDependencyInputDTO(story_id="MULT-004", depends_on_id="MULT-003")
            )
            await uow.commit()

        # Verify all dependencies
        async with e2e_app.create_unit_of_work() as uow:
            get_deps = e2e_app.create_get_dependencies_use_case(uow)
            result = await get_deps.execute(
                GetDependenciesInputDTO(story_id="MULT-004")
            )

        assert len(result.dependencies) == 3
        assert "MULT-001" in result.dependencies
        assert "MULT-002" in result.dependencies
        assert "MULT-003" in result.dependencies


class TestUC003RemoveDependency:
    """Tests for dependency removal."""

    @pytest.mark.asyncio
    async def test_remover_dependencia(self, e2e_main_window, e2e_app, qasync_loop):
        """Test that dependencies can be removed."""
        viewmodel = e2e_main_window.viewmodel

        # Create stories
        for i in range(1, 3):
            dto = CreateStoryInputDTO(
                component="REM",
                name=f"Historia {i}",
                story_points=5,
            )
            await viewmodel.create_story(dto)

        # Add dependency
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="REM-002", depends_on_id="REM-001")
            )
            await uow.commit()

        # Remove dependency
        async with e2e_app.create_unit_of_work() as uow:
            remove_dep = e2e_app.create_remove_dependency_use_case(uow)
            await remove_dep.execute(
                RemoveDependencyInputDTO(story_id="REM-002", depends_on_id="REM-001")
            )
            await uow.commit()

        # Verify removal
        async with e2e_app.create_unit_of_work() as uow:
            get_deps = e2e_app.create_get_dependencies_use_case(uow)
            result = await get_deps.execute(GetDependenciesInputDTO(story_id="REM-002"))

        assert len(result.dependencies) == 0
