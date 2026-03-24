# Data Model: EP-015 Melhoria Iterativa dos Algoritmos de Alocacao

**Date**: 2026-03-12

## Entidades Existentes (Sem Modificacao)

### AllocationMetrics

Estrutura existente em `domain/services/allocation_service.py` com 16 campos.

```python
@dataclass
class AllocationMetrics:
    """Metricas coletadas durante a execucao da alocacao."""

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

**Campos para logging INFO (FR-001)**:
- Todos os 16 campos serao logados ao final da execucao

### AllocationConfig

Estrutura existente em `domain/services/allocation_service.py`.

```python
@dataclass
class AllocationConfig:
    """Configuracao para execucao da alocacao automatica."""

    velocity: float
    project_start_date: date
    max_idle_days: int = 3
    allocation_criteria: AllocationCriteria = AllocationCriteria.LOAD_BALANCING
    max_iterations: int = DEFAULT_MAX_ITERATIONS
    random_seed: int | None = None
```

### BacklogWarning (Hierarquia)

Estrutura existente em `domain/exceptions/warnings.py`.

```python
# Warnings emitidos durante alocacao
class BacklogWarning(Warning):
    """Base para warnings de negocio."""

class DeadlockWarning(BacklogWarning):
    """Emitido quando nenhum progresso na onda."""
    wave: int
    blocked_stories: list[str]
    max_iterations_reached: bool = False

class IdlenessWarning(BacklogWarning):
    """Emitido quando ociosidade intra-wave excede max_idle_days."""
    developer_id: int
    developer_name: str
    idle_days: int
    wave: int

class BetweenWavesIdlenessInfo(BacklogWarning):
    """Informativo - ociosidade inter-wave (esperada)."""
    developer_id: int
    developer_name: str
    idle_days: int
    from_wave: int
    to_wave: int
```

**Logging para warnings (FR-003, FR-004)**:
- `DeadlockWarning`: Logar em nivel WARNING
- `IdlenessWarning`: Logar em nivel WARNING
- `BetweenWavesIdlenessInfo`: Logar em nivel INFO

## Novas Estruturas (Nao Persistidas)

### Log de Correcao (Conceitual)

Nao e uma entidade de dominio - e documentacao gerada durante ciclos de melhoria.

```markdown
## Correcao [numero]

**Data**: [timestamp]
**Problema identificado**: [descricao do problema observado]
**Diagnostico**: [causa raiz identificada via logs]
**Mudanca aplicada**: [arquivos modificados, linhas alteradas]
**Resultado**: [metricas antes/depois, status dos testes]
```

**Armazenamento**: Arquivo markdown no diretorio da feature (`specs/015-improve-allocation-scheduling/corrections/`).

## Relacionamentos

```
AllocationService
├── AllocationConfig (parametro de entrada)
├── AllocationMetrics (saida - logado em INFO)
└── AllocationResult
    ├── allocated_stories: list[Story]
    ├── metrics: AllocationMetrics
    └── warnings: list[BacklogWarning]  (logado em WARNING/INFO)
```

## Validacoes

| Entidade | Campo | Regra | Origem |
|----------|-------|-------|--------|
| AllocationConfig | velocity | > 0 | Existente |
| AllocationConfig | max_idle_days | 2 <= x <= 30 | Existente |
| AllocationConfig | max_iterations | > 0 | Existente |

## Estados de Log

O algoritmo de alocacao nao possui maquina de estados explicita, mas o logging segue o fluxo:

```
[INFO] Alocacao iniciada
    │
    ├── [INFO] Onda N iniciada
    │   ├── [DEBUG] Processando historia X
    │   ├── [DEBUG] Desenvolvedor selecionado (motivo)
    │   ├── [DEBUG] Data ajustada
    │   └── [WARNING] Deadlock detectado (se ocorrer)
    ├── [INFO] Onda N completa
    │
    ├── [INFO] Estabilizacao iniciada
    │   ├── [DEBUG] Dependencias verificadas
    │   ├── [DEBUG] Conflitos resolvidos
    │   └── [WARNING] Violacao de ociosidade (se ocorrer)
    │
    └── [INFO] Alocacao completa (metricas)
```
