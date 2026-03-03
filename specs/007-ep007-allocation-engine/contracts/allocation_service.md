# Contract: AllocationService

## Visao Geral

AllocationService e um domain service stateless que implementa o algoritmo de alocacao automatica de desenvolvedores para historias do backlog.

## Interface Publica

### allocate_stories

```python
@staticmethod
def allocate_stories(
    stories: Sequence[Story],
    developers: Sequence[Developer],
    dependencies: Sequence[tuple[str, str]],
    features: Sequence[Feature],
    holidays: frozenset[date],
    config: AllocationConfig,
) -> AllocationResult:
    """Executa alocacao automatica de desenvolvedores para historias.

    Algoritmo principal:
    1. Filtra historias elegiveis (dev=NULL, datas ok, SP ok)
    2. Constroi mapas auxiliares (feature_id->wave, story_id->Story)
    3. Agrupa historias por wave
    4. Para cada wave em ordem crescente:
       - Loop de alocacao ate estabilizar ou limite
       - Deteccao de deadlock se sem progresso
    5. Loop de estabilizacao:
       - Verifica dependencias
       - Resolve conflitos de periodo
       - Verifica ociosidade
    6. Coleta metricas e retorna resultado

    Args:
        stories: Todas as historias do backlog.
        developers: Todos os desenvolvedores disponiveis.
        dependencies: Grafo de dependencias [(story_id, depends_on_id), ...].
        features: Todas as features (para obter wave).
        holidays: Conjunto de feriados.
        config: Configuracao de alocacao.

    Returns:
        AllocationResult com historias alocadas, metricas e warnings.

    Raises:
        ValueError: Se config.velocity <= 0 ou config.max_idle_days fora de [2, 30].
        MaxIterationsExceeded: Se max_iterations atingido sem convergencia (opcional).

    Example:
        >>> result = AllocationService.allocate_stories(
        ...     stories=stories,
        ...     developers=developers,
        ...     dependencies=[("B", "A")],
        ...     features=features,
        ...     holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        ...     config=AllocationConfig(velocity=2.0, project_start_date=date(2026, 3, 2)),
        ... )
        >>> print(result.metrics.stories_allocated)
    """
```

## Pre-condicoes

| Condicao | Descricao |
|----------|-----------|
| stories validas | Todas as historias tem id unico |
| developers validos | Todos os devs tem id != None |
| dependencias validas | Todos os story_ids existem em stories |
| features validas | Todas as features tem wave > 0 |
| config valido | velocity > 0, max_idle_days in [2, 30] |

## Pos-condicoes

| Condicao | Descricao |
|----------|-----------|
| historias alocadas | Todas as elegiveis tem developer_id ou estao em deadlock |
| sem conflitos | Nenhum dev tem historias com periodos sobrepostos |
| metricas completas | Todos os 16 campos de metricas preenchidos |
| warnings coletados | DeadlockWarning, IdlenessWarning conforme necessario |

## Invariantes

1. **Imutabilidade de entrada**: stories, developers, features originais nao sao modificados; copias sao feitas
2. **Ordem de waves**: wave N processada completamente antes de N+1
3. **Balanceamento**: diferenca maxima de 1 historia entre devs (se todos disponiveis)
4. **Terminacao**: sempre termina devido a MAX_ITERATIONS e MAX_STABILIZATION_PASSES
5. **Determinismo**: com random_seed fixo, mesmo resultado para mesma entrada

## Comportamento por Cenario

### Cenario: Backlog Vazio

- **Entrada**: stories = []
- **Saida**: AllocationResult(allocated_stories=[], metrics(stories_allocated=0), warnings=[])

### Cenario: Sem Desenvolvedores

- **Entrada**: developers = []
- **Saida**: DeadlockWarning para cada wave com historias elegiveis
- **Metricas**: deadlocks_detected >= 1, stories_allocated = 0

### Cenario: Todas Ja Alocadas

- **Entrada**: todas as historias com developer_id != None
- **Saida**: AllocationResult(allocated_stories=[], metrics(stories_allocated=0), warnings=[])

### Cenario: Conflito de Periodo

- **Entrada**: historias com periodos sobrepostos apos alocacao
- **Comportamento**: resolve ajustando start_date da historia posterior
- **Metricas**: validation_conflict_fixes >= 1

### Cenario: Ociosidade Detectada

- **Entrada**: gap > max_idle_days entre historias do mesmo dev na mesma wave
- **Comportamento**: emite IdlenessWarning, tenta realocacao se possivel
- **Metricas**: max_idle_violations_detected >= 1

## Metodos Auxiliares (Privados)

| Metodo | Responsabilidade |
|--------|------------------|
| _is_eligible | Verifica se historia e elegivel para alocacao |
| _select_developer | Seleciona dev por criterio (LOAD_BALANCING ou DEPENDENCY_OWNER) |
| _allocate_by_wave | Processa todas as historias de uma wave |
| _resolve_allocation_conflicts | Resolve sobreposicoes de periodo |
| _final_dependency_check | Verifica e corrige violacoes de dependencia |
| _check_and_fix_idle_violations | Detecta e corrige ociosidade |
| _get_story_wave | Retorna wave da historia (0 se sem feature) |
| _get_dependency_owner | Retorna dev_id do proprietario de dependencia |

## Integracao com Outros Servicos

### SchedulingService

Metodos utilizados:
- `next_workday(date, holidays) -> date`
- `add_workdays(start, workdays, holidays) -> date`
- `count_workdays_between(start, end, holidays) -> int`
- `calculate_duration(sp, velocity) -> int`

### DependencyService

Metodos utilizados:
- `build_graph(dependencies) -> dict[str, list[str]]`

## Limites de Seguranca

| Constante | Valor | Proposito |
|-----------|-------|-----------|
| DEFAULT_MAX_ITERATIONS | 1000 | Previne loop infinito por wave |
| MAX_REALLOCATIONS_PER_STORY | 3 | Evita ping-pong de realocacoes |
| MAX_STABILIZATION_PASSES | 10 | Limita loop de estabilizacao |
| MAX_CONFLICT_PASSES | 100 | Limita resolucao de conflitos |
