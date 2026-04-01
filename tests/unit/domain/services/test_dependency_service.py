"""Unit tests for DependencyService."""

from __future__ import annotations

import time

from backlog_manager.domain.services.dependency_service import DependencyService


class TestBuildGraph:
    """Tests for build_graph method."""

    def test_build_graph_empty(self) -> None:
        """Empty dependencies returns empty graph."""
        graph = DependencyService.build_graph([])
        assert graph == {}

    def test_build_graph_single_dependency(self) -> None:
        """Single dependency creates correct graph."""
        deps = [("A", "B")]
        graph = DependencyService.build_graph(deps)
        assert graph == {"A": ["B"], "B": []}

    def test_build_graph_chain(self) -> None:
        """Chain of dependencies A->B->C."""
        deps = [("A", "B"), ("B", "C")]
        graph = DependencyService.build_graph(deps)
        assert graph == {"A": ["B"], "B": ["C"], "C": []}

    def test_build_graph_multiple_dependencies(self) -> None:
        """Story with multiple dependencies."""
        deps = [("A", "B"), ("A", "C")]
        graph = DependencyService.build_graph(deps)
        assert graph == {"A": ["B", "C"], "B": [], "C": []}

    def test_build_graph_diamond(self) -> None:
        """Diamond pattern: A->B,C; B,C->D."""
        deps = [("A", "B"), ("A", "C"), ("B", "D"), ("C", "D")]
        graph = DependencyService.build_graph(deps)
        assert graph == {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}


class TestDetectCycleDirect:
    """Tests for direct cycle detection (A->B, B->A)."""

    def test_direct_cycle_simple(self) -> None:
        """Direct cycle A->B, B->A is detected."""
        graph = {"A": ["B"], "B": ["A"]}
        cycle = DependencyService.detect_cycle(graph, "B", "A")
        assert cycle is not None
        assert len(cycle) >= 2
        # Cycle should start and end with same node
        assert cycle[0] == cycle[-1]

    def test_would_create_direct_cycle(self) -> None:
        """Adding B->A to A->B would create cycle."""
        graph = {"A": ["B"], "B": []}
        cycle = DependencyService.would_create_cycle(graph, "B", "A")
        assert cycle is not None
        assert cycle[0] == cycle[-1]
        # Should contain A and B
        assert "A" in cycle
        assert "B" in cycle


class TestDetectCycleIndirect:
    """Tests for indirect cycle detection (A->B->C->A)."""

    def test_indirect_cycle_three_nodes(self) -> None:
        """Indirect cycle A->B->C->A is detected."""
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        cycle = DependencyService.detect_cycle(graph, "C", "A")
        assert cycle is not None
        assert cycle[0] == cycle[-1]
        # Should contain all three nodes
        cycle_nodes = set(cycle)
        assert "A" in cycle_nodes
        assert "B" in cycle_nodes
        assert "C" in cycle_nodes

    def test_would_create_indirect_cycle(self) -> None:
        """Adding C->A to A->B->C would create cycle."""
        graph = {"A": ["B"], "B": ["C"], "C": []}
        cycle = DependencyService.would_create_cycle(graph, "C", "A")
        assert cycle is not None
        assert cycle[0] == cycle[-1]

    def test_indirect_cycle_four_nodes(self) -> None:
        """Indirect cycle A->B->C->D->A is detected."""
        graph = {"A": ["B"], "B": ["C"], "C": ["D"], "D": ["A"]}
        cycle = DependencyService.detect_cycle(graph, "D", "A")
        assert cycle is not None
        assert cycle[0] == cycle[-1]


class TestNoCycleDAG:
    """Tests confirming no cycle in valid DAGs."""

    def test_no_cycle_simple_dag(self) -> None:
        """Simple DAG A->B->C has no cycle."""
        graph = {"A": ["B"], "B": ["C"], "C": []}
        _ = DependencyService.detect_cycle(graph, "A", "B")
        # Since this is existing graph, we test from A
        # Actually detect_cycle checks from target
        result = DependencyService.would_create_cycle(graph, "D", "C")
        assert result is None

    def test_no_cycle_diamond(self) -> None:
        """Diamond DAG has no cycle."""
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        # Adding E->A should not create cycle
        cycle = DependencyService.would_create_cycle(graph, "E", "A")
        assert cycle is None

    def test_no_cycle_adding_leaf(self) -> None:
        """Adding dependency to leaf node doesn't create cycle."""
        graph = {"A": ["B"], "B": ["C"], "C": []}
        # D depending on C is fine
        cycle = DependencyService.would_create_cycle(graph, "D", "C")
        assert cycle is None

    def test_no_cycle_parallel_paths(self) -> None:
        """Multiple paths to same node without cycle."""
        graph = {"A": ["B", "C"], "B": ["D"], "C": ["D"], "D": []}
        # E depending on D is fine
        cycle = DependencyService.would_create_cycle(graph, "E", "D")
        assert cycle is None


class TestPerformance50Nodes:
    """Performance test for 50-node graph (<100ms as per CT-002)."""

    def test_performance_50_nodes_chain(self) -> None:
        """Cycle detection in 50-node chain completes in <100ms."""
        # Build chain: 0->1->2->...->49
        deps = [(str(i), str(i + 1)) for i in range(49)]
        graph = DependencyService.build_graph(deps)

        start = time.perf_counter()
        # Try to add 49->0 which would create cycle
        cycle = DependencyService.would_create_cycle(graph, "49", "0")
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert cycle is not None, "Should detect cycle"
        assert elapsed < 100, f"Cycle detection took {elapsed:.2f}ms, expected <100ms"

    def test_performance_50_nodes_no_cycle(self) -> None:
        """No-cycle verification in 50-node chain completes in <100ms."""
        # Build chain: 0->1->2->...->49
        deps = [(str(i), str(i + 1)) for i in range(49)]
        graph = DependencyService.build_graph(deps)

        start = time.perf_counter()
        # Adding 50->49 should not create cycle
        cycle = DependencyService.would_create_cycle(graph, "50", "49")
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert cycle is None, "Should not detect cycle"
        assert elapsed < 100, f"Verification took {elapsed:.2f}ms, expected <100ms"

    def test_performance_50_nodes_dense(self) -> None:
        """Performance with 50 nodes and more edges."""
        # Build more complex graph with ~100 edges
        # Direction: i -> i-1 (i depends on i-1, meaning edge goes from i to i-1)
        deps = []
        for i in range(1, 50):
            # Each node depends on previous node
            deps.append((str(i), str(i - 1)))
            if i > 5:
                deps.append((str(i), str(i - 5)))

        graph = DependencyService.build_graph(deps)

        start = time.perf_counter()
        # Try to add 0->49 which would create a cycle
        # (since path exists from 49 to 0 via chain)
        cycle = DependencyService.would_create_cycle(graph, "0", "49")
        elapsed = (time.perf_counter() - start) * 1000  # ms

        assert cycle is not None, "Should detect cycle"
        assert elapsed < 100, f"Cycle detection took {elapsed:.2f}ms, expected <100ms"


class TestValidateWave:
    """Tests for validate_wave_dependency method."""

    def test_valid_same_wave(self) -> None:
        """Same wave dependency is valid."""
        assert DependencyService.validate_wave_dependency(1, 1) is True

    def test_valid_earlier_wave(self) -> None:
        """Depending on earlier wave is valid."""
        assert DependencyService.validate_wave_dependency(2, 1) is True
        assert DependencyService.validate_wave_dependency(5, 1) is True

    def test_invalid_later_wave(self) -> None:
        """Depending on later wave is invalid."""
        assert DependencyService.validate_wave_dependency(1, 2) is False
        assert DependencyService.validate_wave_dependency(1, 5) is False

    def test_valid_wave_zero(self) -> None:
        """Wave 0 (no feature) can depend on wave 0."""
        assert DependencyService.validate_wave_dependency(0, 0) is True

    def test_invalid_wave_zero_depends_later(self) -> None:
        """Wave 0 depending on wave 1+ is invalid."""
        assert DependencyService.validate_wave_dependency(0, 1) is False
        assert DependencyService.validate_wave_dependency(0, 2) is False

    def test_valid_wave_depends_on_zero(self) -> None:
        """Any wave can depend on wave 0."""
        assert DependencyService.validate_wave_dependency(1, 0) is True
        assert DependencyService.validate_wave_dependency(2, 0) is True


class TestCyclePath:
    """Tests for cycle path format."""

    def test_cycle_path_starts_ends_same(self) -> None:
        """Cycle path starts and ends with same node."""
        graph = {"A": ["B"], "B": ["A"]}
        cycle = DependencyService.detect_cycle(graph, "B", "A")
        assert cycle is not None
        assert cycle[0] == cycle[-1]

    def test_cycle_path_contains_all_cycle_nodes(self) -> None:
        """Cycle path contains all nodes in cycle."""
        graph = {"A": ["B"], "B": ["C"], "C": ["A"]}
        cycle = DependencyService.detect_cycle(graph, "C", "A")
        assert cycle is not None
        # All cycle nodes should be present
        nodes_in_cycle = set(cycle[:-1])  # Exclude duplicate end node
        assert "A" in nodes_in_cycle
        assert "B" in nodes_in_cycle
        assert "C" in nodes_in_cycle
