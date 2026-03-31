"""E2E tests for CT-002: Ciclo em Grafo Grande.

Tests cycle detection in a large graph (50 nodes)
with performance requirements.
"""

from __future__ import annotations

import time

import pytest
import pytest_asyncio
from backlog_manager.application.dto.dependency import (
    AddDependencyInputDTO,
    GetDependenciesInputDTO,
)
from backlog_manager.domain.entities.story import Story
from backlog_manager.domain.exceptions import CyclicDependencyException
from backlog_manager.domain.value_objects import StoryPoint, StoryStatus

pytestmark = [pytest.mark.e2e]


class TestCT002CicloGrafoGrande:
    """CT-002: Deteccao de ciclo em grafo com 50 nos."""

    @pytest_asyncio.fixture
    async def ct002_setup(self, e2e_app, qasync_loop):
        """Setup for CT-002: Create 50 stories with linear dependencies.

        Creates a chain: S-001 -> S-002 -> ... -> S-050
        (S-002 depends on S-001, etc.)
        """
        async with e2e_app.create_unit_of_work() as uow:
            # Create 50 stories
            for i in range(1, 51):
                story = Story(
                    id=f"CTWO-{i:03d}",
                    component="CTWO",
                    name=f"Historia {i}",
                    story_points=StoryPoint(5),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)

            await uow.commit()

        # Add linear dependencies (not cyclic yet)
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            for i in range(2, 51):
                await add_dep.execute(
                    AddDependencyInputDTO(
                        story_id=f"CTWO-{i:03d}", depends_on_id=f"CTWO-{i-1:03d}"
                    )
                )
            await uow.commit()

        return e2e_app

    @pytest.mark.asyncio
    async def test_ct002_cyclic_exception_em_100ms(self, ct002_setup, qasync_loop):
        """Test that cycle detection completes in less than 100ms.

        RNF-PERF-002: Cycle detection should be fast even in large graphs.
        """
        e2e_app = ct002_setup

        # Try to close cycle: CTWO-001 depends on CTWO-050
        start_time = time.perf_counter()
        error_raised = False

        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="CTWO-001", depends_on_id="CTWO-050")
                )
                await uow.commit()
            except CyclicDependencyException:
                error_raised = True

        elapsed_ms = (time.perf_counter() - start_time) * 1000

        assert error_raised, "Cycle should have been detected"
        # Allow some tolerance for CI
        assert (
            elapsed_ms < 200
        ), f"Cycle detection took {elapsed_ms:.2f}ms (limit: 100ms + tolerance)"

    @pytest.mark.asyncio
    async def test_ct002_detects_cycle_at_any_position(self, e2e_app, qasync_loop):
        """Test cycle detection when cycle closes at different positions."""
        # Create 30 stories
        async with e2e_app.create_unit_of_work() as uow:
            for i in range(1, 31):
                story = Story(
                    id=f"CTWB-{i:03d}",
                    component="CTWB",
                    name=f"Historia B {i}",
                    story_points=StoryPoint(5),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)
            await uow.commit()

        # Add dependencies to create chain
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            for i in range(2, 31):
                await add_dep.execute(
                    AddDependencyInputDTO(
                        story_id=f"CTWB-{i:03d}", depends_on_id=f"CTWB-{i-1:03d}"
                    )
                )
            await uow.commit()

        # Try to close cycle at position 15 back to position 10
        # CTWB-010 depends on CTWB-015 would create cycle because
        # 15 -> 14 -> 13 -> 12 -> 11 -> 10 -> 15 (via new dependency)
        error_raised = False

        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="CTWB-010", depends_on_id="CTWB-015")
                )
                await uow.commit()
            except CyclicDependencyException:
                error_raised = True

        assert error_raised, "Cycle in middle of chain should be detected"

    @pytest.mark.asyncio
    async def test_ct002_no_cycle_valid_dependency(self, ct002_setup, qasync_loop):
        """Test that valid dependencies are accepted (no false positives)."""
        e2e_app = ct002_setup

        # Adding dependency from higher to lower is valid
        # CTWO-050 already depends on CTWO-049, adding CTWO-050 depends on CTWO-001 is valid
        # (CTWO-001 doesn't depend on CTWO-050)
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            # This should work - CTWO-050 depends on both CTWO-049 and CTWO-001
            await add_dep.execute(
                AddDependencyInputDTO(story_id="CTWO-050", depends_on_id="CTWO-001")
            )
            await uow.commit()

        # Verify dependency was added
        async with e2e_app.create_unit_of_work() as uow:
            get_deps = e2e_app.create_get_dependencies_use_case(uow)
            result = await get_deps.execute(
                GetDependenciesInputDTO(story_id="CTWO-050")
            )

        assert "CTWO-001" in result.dependencies
        assert "CTWO-049" in result.dependencies

    @pytest.mark.asyncio
    async def test_ct002_error_message_includes_cycle_path(
        self, ct002_setup, qasync_loop
    ):
        """Test that cycle detection error includes useful information."""
        e2e_app = ct002_setup

        error_message = None

        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="CTWO-001", depends_on_id="CTWO-050")
                )
                await uow.commit()
            except CyclicDependencyException as e:
                error_message = str(e)

        assert error_message is not None
        # Error message should mention cycle or dependency
        assert (
            "ciclo" in error_message.lower()
            or "cycle" in error_message.lower()
            or "circular" in error_message.lower()
            or "dependencia" in error_message.lower()
        )


class TestCT002GrafoDesconexo:
    """Tests for cycle detection in disconnected graphs."""

    @pytest.mark.asyncio
    async def test_ciclo_em_subgrafo_desconexo(self, e2e_app, qasync_loop):
        """Test cycle detection in disconnected subgraph."""
        # Create two disconnected chains
        async with e2e_app.create_unit_of_work() as uow:
            # Chain A: A-001 -> A-002 -> A-003
            for i in range(1, 4):
                story = Story(
                    id=f"A-{i:03d}",
                    component="A",
                    name=f"Historia A {i}",
                    story_points=StoryPoint(5),
                    priority=i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)

            # Chain B: B-001 -> B-002 -> B-003
            for i in range(1, 4):
                story = Story(
                    id=f"B-{i:03d}",
                    component="B",
                    name=f"Historia B {i}",
                    story_points=StoryPoint(5),
                    priority=10 + i,
                    status=StoryStatus.BACKLOG,
                )
                await uow.stories.add(story)

            await uow.commit()

        # Add dependencies for both chains
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            await add_dep.execute(
                AddDependencyInputDTO(story_id="A-002", depends_on_id="A-001")
            )
            await add_dep.execute(
                AddDependencyInputDTO(story_id="A-003", depends_on_id="A-002")
            )
            await add_dep.execute(
                AddDependencyInputDTO(story_id="B-002", depends_on_id="B-001")
            )
            await add_dep.execute(
                AddDependencyInputDTO(story_id="B-003", depends_on_id="B-002")
            )
            await uow.commit()

        # Try to create cycle in chain B
        error_raised = False
        async with e2e_app.create_unit_of_work() as uow:
            add_dep = e2e_app.create_add_dependency_use_case(uow)
            try:
                await add_dep.execute(
                    AddDependencyInputDTO(story_id="B-001", depends_on_id="B-003")
                )
                await uow.commit()
            except CyclicDependencyException:
                error_raised = True

        assert error_raised, "Cycle in disconnected subgraph should be detected"

        # Chain A should be unaffected
        async with e2e_app.create_unit_of_work() as uow:
            get_deps = e2e_app.create_get_dependencies_use_case(uow)
            result_a3 = await get_deps.execute(
                GetDependenciesInputDTO(story_id="A-003")
            )

        assert "A-002" in result_a3.dependencies
