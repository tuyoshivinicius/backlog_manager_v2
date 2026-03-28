"""Dependency Service for cycle detection and wave validation.

Domain service that implements graph algorithms for dependency management.
Uses iterative DFS to avoid stack overflow in deep graphs.
"""

from __future__ import annotations

from collections.abc import Sequence

# DFS node states
WHITE = 0  # Not visited
GRAY = 1  # In processing (on current path)
BLACK = 2  # Finished processing


class DependencyService:
    """Servico de dominio para operacoes com dependencias.

    Servico stateless que implementa algoritmos de grafo para
    deteccao de ciclos e validacao de waves. Recebe todos os
    dados via parametros, nao acessa repositorios ou faz I/O.

    Example:
        >>> deps = [("A", "B"), ("B", "C")]
        >>> graph = DependencyService.build_graph(deps)
        >>> cycle = DependencyService.would_create_cycle(graph, "C", "A")
        >>> if cycle:
        ...     print(f"Cycle: {' -> '.join(cycle)}")
        Cycle: A -> B -> C -> A
    """

    @staticmethod
    def build_graph(dependencies: Sequence[tuple[str, str]]) -> dict[str, list[str]]:
        """Constroi grafo de adjacencia a partir das dependencias.

        O grafo representa: story_id -> [depends_on_ids]
        Ou seja, arestas vao de quem depende para quem e dependencia.

        Args:
            dependencies: Lista de tuplas (story_id, depends_on_id).

        Returns:
            Dicionario de adjacencia onde chave e story_id e
            valor e lista de IDs dos quais depende.

        Example:
            >>> deps = [("A", "B"), ("B", "C")]
            >>> graph = DependencyService.build_graph(deps)
            >>> graph == {"A": ["B"], "B": ["C"], "C": []}
            True
        """
        graph: dict[str, list[str]] = {}

        for story_id, depends_on_id in dependencies:
            # Ensure both nodes exist in graph
            if story_id not in graph:
                graph[story_id] = []
            if depends_on_id not in graph:
                graph[depends_on_id] = []

            # Add edge: story_id depends on depends_on_id
            graph[story_id].append(depends_on_id)

        return graph

    @staticmethod
    def would_create_cycle(
        graph: dict[str, list[str]], source: str, target: str
    ) -> list[str] | None:
        """Verifica se adicionar aresta source->target criaria ciclo.

        Simula adicao da aresta e verifica se existe caminho
        de target de volta para source (o que formaria ciclo).

        Args:
            graph: Grafo de adjacencia atual.
            source: ID da historia que vai depender (origem).
            target: ID da historia da qual vai depender (destino).

        Returns:
            Lista de IDs formando o ciclo se detectado,
            None se nao criaria ciclo.
            Formato: ["A", "B", "C", "A"] (comeca e termina no mesmo no).

        Example:
            >>> graph = {"A": ["B"], "B": [], "C": []}
            >>> # Adding B->A would create cycle A->B->A
            >>> cycle = DependencyService.would_create_cycle(graph, "B", "A")
            >>> cycle == ["A", "B", "A"]
            True
        """
        # Create temporary graph with the new edge
        temp_graph = {node: list(edges) for node, edges in graph.items()}

        # Ensure both nodes exist
        if source not in temp_graph:
            temp_graph[source] = []
        if target not in temp_graph:
            temp_graph[target] = []

        # Add the new edge
        temp_graph[source].append(target)

        return DependencyService.detect_cycle(temp_graph, source, target)

    @staticmethod
    def detect_cycle(
        graph: dict[str, list[str]], source: str, target: str
    ) -> list[str] | None:
        """Detecta ciclo no grafo usando DFS iterativo.

        Usa coloracao de nos (WHITE/GRAY/BLACK) para detectar back edges.
        Implementacao iterativa com pilha explicita para evitar
        stack overflow em grafos profundos.

        Args:
            graph: Grafo de adjacencia.
            source: No de origem da aresta recem adicionada.
            target: No de destino da aresta recem adicionada.

        Returns:
            Lista de IDs formando o ciclo se detectado,
            None se grafo e aciclico.

        Note:
            O ciclo retornado comeca e termina no mesmo no.
            Ex: ["A", "B", "C", "A"]
        """
        # Initialize colors and parent tracking
        color: dict[str, int] = {node: WHITE for node in graph}
        parent: dict[str, str | None] = {node: None for node in graph}

        # Stack for iterative DFS: (node, iterator_index)
        # We track index to resume iteration after returning from children
        stack: list[tuple[str, int]] = [(target, 0)]
        color[target] = GRAY

        while stack:
            node, idx = stack.pop()

            neighbors = graph.get(node, [])

            if idx < len(neighbors):
                # Still have neighbors to process
                neighbor = neighbors[idx]

                # Push current node back with incremented index
                stack.append((node, idx + 1))

                if color.get(neighbor, WHITE) == WHITE:
                    # Unvisited: explore it
                    color[neighbor] = GRAY
                    parent[neighbor] = node
                    stack.append((neighbor, 0))
                elif color.get(neighbor, WHITE) == GRAY:
                    # Back edge found - cycle detected!
                    # Build cycle path from neighbor back to neighbor
                    cycle_path = DependencyService._build_cycle_path(
                        parent, neighbor, node
                    )
                    return cycle_path
            else:
                # All neighbors processed, mark as finished
                color[node] = BLACK

        return None

    @staticmethod
    def _build_cycle_path(
        parent: dict[str, str | None], cycle_start: str, last_node: str
    ) -> list[str]:
        """Constroi caminho do ciclo a partir do mapa de pais.

        Args:
            parent: Dicionario de pais (node -> parent).
            cycle_start: No onde o ciclo comeca (e termina).
            last_node: Ultimo no visitado antes de encontrar back edge.

        Returns:
            Lista de IDs formando o ciclo.
            Ex: ["A", "B", "C", "A"]
        """
        path = [cycle_start]
        current: str | None = last_node

        while current is not None and current != cycle_start:
            path.append(current)
            current = parent.get(current)

        path.append(cycle_start)
        path.reverse()
        return path

    @staticmethod
    def validate_wave_dependency(story_wave: int, depends_on_wave: int) -> bool:
        """Valida se dependencia entre waves e valida.

        Uma historia so deve depender de historias de waves
        anteriores ou iguais, nao posteriores.

        Args:
            story_wave: Wave da historia que depende.
            depends_on_wave: Wave da historia da qual depende.

        Returns:
            True se dependencia e valida (depends_on_wave <= story_wave),
            False se invalida (story depende de wave posterior).

        Example:
            >>> DependencyService.validate_wave_dependency(2, 1)  # OK
            True
            >>> DependencyService.validate_wave_dependency(1, 2)  # Invalid
            False
            >>> DependencyService.validate_wave_dependency(1, 1)  # Same wave OK
            True
        """
        return depends_on_wave <= story_wave
