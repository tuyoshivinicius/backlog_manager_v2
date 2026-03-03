# Data Model: EP-007 Motor de Alocacao

## Entidades do Dominio

### AllocationCriteria (Enum)

Criterio de selecao de desenvolvedor para alocacao.

| Valor | Descricao |
|-------|-----------|
| LOAD_BALANCING | Alocar para dev com menor contagem de historias (padrao) |
| DEPENDENCY_OWNER | Priorizar dev que completou dependencias da historia |

```python
class AllocationCriteria(Enum):
    LOAD_BALANCING = "load_balancing"
    DEPENDENCY_OWNER = "dependency_owner"
```

### AllocationConfig (Dataclass)

Configuracao para execucao da alocacao automatica.

| Campo | Tipo | Default | Validacao | Descricao |
|-------|------|---------|-----------|-----------|
| velocity | float | - | > 0 | Velocidade do time em SP/dia |
| project_start_date | date | - | not null | Data de inicio do projeto |
| max_idle_days | int | 3 | [2, 30] | Dias maximos de ociosidade aceitavel |
| allocation_criteria | AllocationCriteria | LOAD_BALANCING | enum | Criterio de selecao de dev |
| max_iterations | int | 1000 | > 0 | Limite de iteracoes por onda |
| random_seed | int | None | None | None | Seed para aleatoriedade (testes) |

```python
@dataclass
class AllocationConfig:
    velocity: float
    project_start_date: date
    max_idle_days: int = 3
    allocation_criteria: AllocationCriteria = AllocationCriteria.LOAD_BALANCING
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    random_seed: int | None = None

    def __post_init__(self) -> None:
        if self.velocity <= 0:
            raise ValueError("Velocidade deve ser maior que zero")
        if not 2 <= self.max_idle_days <= 30:
            raise ValueError("max_idle_days deve estar entre 2 e 30")
```

### AllocationMetrics (Dataclass)

Metricas coletadas durante a execucao da alocacao.

| Campo | Tipo | Default | Descricao |
|-------|------|---------|-----------|
| total_time_seconds | float | 0.0 | Tempo total de execucao |
| stories_processed | int | 0 | Total de historias processadas |
| stories_allocated | int | 0 | Historias alocadas com sucesso |
| waves_processed | int | 0 | Numero de ondas processadas |
| total_iterations | int | 0 | Total de iteracoes do algoritmo |
| iterations_per_wave | dict[int, int] | {} | Iteracoes por onda |
| allocations_by_dependency_owner | int | 0 | Alocacoes por criterio DEPENDENCY_OWNER |
| allocations_by_load_balancing | int | 0 | Alocacoes por criterio LOAD_BALANCING |
| deadlocks_detected | int | 0 | Deadlocks detectados |
| date_adjustments | int | 0 | Ajustes de data realizados |
| validation_reallocations | int | 0 | Realocacoes bem-sucedidas na validacao |
| validation_dependency_fixes | int | 0 | Violacoes de dependencia corrigidas |
| validation_conflict_fixes | int | 0 | Conflitos de periodo resolvidos |
| max_idle_violations_detected | int | 0 | Violacoes de max_idle_days detectadas |
| max_idle_violations_fixed | int | 0 | Violacoes corrigidas por realocacao |
| failed_reallocations | int | 0 | Tentativas de realocacao que falharam |

```python
@dataclass
class AllocationMetrics:
    total_time_seconds: float = 0.0
    stories_processed: int = 0
    stories_allocated: int = 0
    waves_processed: int = 0
    total_iterations: int = 0
    iterations_per_wave: dict[int, int] = field(default_factory=dict)
    allocations_by_dependency_owner: int = 0
    allocations_by_load_balancing: int = 0
    deadlocks_detected: int = 0
    date_adjustments: int = 0
    validation_reallocations: int = 0
    validation_dependency_fixes: int = 0
    validation_conflict_fixes: int = 0
    max_idle_violations_detected: int = 0
    max_idle_violations_fixed: int = 0
    failed_reallocations: int = 0
```

### AllocationResult (Dataclass)

Resultado da execucao da alocacao automatica.

| Campo | Tipo | Descricao |
|-------|------|-----------|
| allocated_stories | list[Story] | Historias que foram alocadas (com mudancas) |
| metrics | AllocationMetrics | Metricas de execucao |
| warnings | list[BacklogWarning] | Warnings emitidos durante execucao |

```python
@dataclass
class AllocationResult:
    allocated_stories: list[Story]
    metrics: AllocationMetrics
    warnings: list[BacklogWarning]
```

## Entidades Existentes (Referencia)

### Story (Existente - EP-002)

Campos relevantes para alocacao:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | str | Identificador unico (COMPONENT-NNN) |
| story_points | StoryPoint | int | Story points (3, 5, 8, 13) |
| duration | int | None | Duracao em dias uteis |
| start_date | date | None | Data de inicio |
| end_date | date | None | Data de termino |
| developer_id | int | None | ID do desenvolvedor alocado |
| feature_id | int | None | ID da feature (para wave) |

**Criterio de Elegibilidade**:
- developer_id == None (nao alocada)
- start_date != None AND end_date != None (datas calculadas)
- story_points definido (valor valido)

### Developer (Existente - EP-002)

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | int | None | ID auto-gerado |
| name | str | Nome do desenvolvedor |

### Feature (Existente - EP-004)

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | int | None | ID auto-gerado |
| name | str | Nome da feature |
| wave | int | Numero da onda (> 0) |

## Constantes de Seguranca

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| DEFAULT_MAX_ITERATIONS | 1000 | Limite de iteracoes por onda |
| MAX_REALLOCATIONS_PER_STORY | 3 | Limite de realocacoes por historia |
| MAX_STABILIZATION_PASSES | 10 | Limite de passadas de estabilizacao |
| MAX_CONFLICT_PASSES | 100 | Limite de passadas de resolucao de conflitos |

## Relacoes

```
AllocationService
    |
    +-- recebe --> AllocationConfig
    +-- recebe --> Sequence[Story] (todas as historias)
    +-- recebe --> Sequence[Developer] (todos os desenvolvedores)
    +-- recebe --> Sequence[tuple[str, str]] (grafo de dependencias)
    +-- recebe --> Sequence[Feature] (todas as features)
    +-- recebe --> frozenset[date] (feriados)
    |
    +-- retorna --> AllocationResult
                        |
                        +-- allocated_stories: list[Story]
                        +-- metrics: AllocationMetrics
                        +-- warnings: list[BacklogWarning]
                                          |
                                          +-- DeadlockWarning
                                          +-- IdlenessWarning
                                          +-- BetweenWavesIdlenessInfo
```

## Fluxo de Estados

### Historia no Processo de Alocacao

```
[Nao Elegivel] --> [Elegivel] --> [Alocada]
     |                  |              |
     v                  v              v
  - sem datas     - dev=NULL      - dev != NULL
  - sem SP        - datas ok      - datas ok
  - ja alocada    - SP ok         - SP ok
```

### Estados de Onda

```
[Pendente] --> [Em Processamento] --> [Concluida]
                      |                    |
                      v                    v
                 [Deadlock]          todas historias
                      |              alocadas ou
                      v              deadlock
                 proxima onda
```

## Mapas Auxiliares (Runtime)

Construidos no inicio da alocacao para lookup eficiente:

| Mapa | Tipo | Descricao |
|------|------|-----------|
| feature_map | dict[int, int] | feature_id -> wave |
| story_map | dict[str, Story] | story_id -> Story |
| dev_count | dict[int, int] | dev_id -> count de historias |
| reallocation_count | dict[str, int] | story_id -> count de realocacoes |
