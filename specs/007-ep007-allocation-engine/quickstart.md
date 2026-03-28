# Quickstart: EP-007 Motor de Alocacao

## Uso Basico

### 1. Via Use Case (Application Layer)

```python
from datetime import date
from backlog_manager.application.use_cases.allocation import ExecuteAllocationUseCase
from backlog_manager.application.dto.allocation import ExecuteAllocationInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

async def alocar_backlog():
    async with SQLiteUnitOfWork() as uow:
        use_case = ExecuteAllocationUseCase(uow)

        input_dto = ExecuteAllocationInputDTO(
            velocity=2.0,
            project_start_date=date(2026, 3, 2),
            max_idle_days=3,
            allocation_criteria="LOAD_BALANCING",
        )

        result = await use_case.execute(input_dto)

        if result.success:
            print(f"Historias alocadas: {result.stories_allocated}")
            print(f"Tempo total: {result.total_time_seconds:.2f}s")

            for warning in result.warnings:
                print(f"Aviso: {warning}")

        return result
```

### 2. Via Domain Service (Testes)

```python
from datetime import date
from backlog_manager.domain.services import AllocationService
from backlog_manager.domain.services.allocation_service import (
    AllocationConfig,
    AllocationCriteria,
)
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028

def test_alocacao():
    # Dados de entrada
    stories = [...]  # Lista de Story
    developers = [...]  # Lista de Developer
    dependencies = [("B", "A")]  # B depende de A
    features = [...]  # Lista de Feature

    config = AllocationConfig(
        velocity=2.0,
        project_start_date=date(2026, 3, 2),
        max_idle_days=3,
        allocation_criteria=AllocationCriteria.LOAD_BALANCING,
        random_seed=42,  # Para determinismo em testes
    )

    result = AllocationService.allocate_stories(
        stories=stories,
        developers=developers,
        dependencies=dependencies,
        features=features,
        holidays=BRAZILIAN_HOLIDAYS_2026_2028,
        config=config,
    )

    assert result.metrics.stories_allocated > 0
    assert result.metrics.deadlocks_detected == 0

    return result
```

## Exemplos de Cenarios

### Cenario 1: Alocacao Simples

```python
# 3 historias, 2 desenvolvedores, sem dependencias
stories = [
    Story(id="AUTH-001", component="AUTH", name="Login", story_points=5, ...),
    Story(id="AUTH-002", component="AUTH", name="Logout", story_points=3, ...),
    Story(id="AUTH-003", component="AUTH", name="Session", story_points=8, ...),
]
developers = [
    Developer(id=1, name="Alice"),
    Developer(id=2, name="Bob"),
]
features = []  # Sem features = wave 0
dependencies = []  # Sem dependencias

config = AllocationConfig(velocity=2.0, project_start_date=date(2026, 3, 2))
result = AllocationService.allocate_stories(stories, developers, dependencies, features, holidays, config)

# Resultado esperado: 2 historias para um dev, 1 para outro
assert result.metrics.stories_allocated == 3
```

### Cenario 2: Com Criterio DEPENDENCY_OWNER

```python
# B depende de A, criterio DEPENDENCY_OWNER
stories = [
    Story(id="A", ..., developer_id=1),  # Ja alocada para Alice
    Story(id="B", ..., developer_id=None),  # Elegivel
]
dependencies = [("B", "A")]  # B depende de A

config = AllocationConfig(
    velocity=2.0,
    project_start_date=date(2026, 3, 2),
    allocation_criteria=AllocationCriteria.DEPENDENCY_OWNER,
)

result = AllocationService.allocate_stories(...)

# B deve ser alocada para Alice (proprietaria de A)
allocated_b = next(s for s in result.allocated_stories if s.id == "B")
assert allocated_b.developer_id == 1  # Alice
```

### Cenario 3: Deadlock

```python
# 5 historias, 0 desenvolvedores
stories = [Story(...) for _ in range(5)]
developers = []  # Sem devs!

result = AllocationService.allocate_stories(stories, developers, [], [], holidays, config)

# Deadlock detectado
assert result.metrics.deadlocks_detected >= 1
assert result.metrics.stories_allocated == 0
assert any(isinstance(w, DeadlockWarning) for w in result.warnings)
```

### Cenario 4: Ociosidade

```python
# Historias com gap grande entre elas para mesmo dev
# Dev1: historia A (02-04/03), historia B (10-12/03) - gap de 3 dias

config = AllocationConfig(
    velocity=2.0,
    project_start_date=date(2026, 3, 2),
    max_idle_days=2,  # Menor que gap
)

result = AllocationService.allocate_stories(...)

# Ociosidade detectada
assert any(isinstance(w, IdlenessWarning) for w in result.warnings)
```

## Interpretando Metricas

```python
result = await use_case.execute(input_dto)
m = result.metrics

# Performance
print(f"Tempo total: {m.total_time_seconds:.2f}s")
print(f"Historias processadas: {m.stories_processed}")
print(f"Historias alocadas: {m.stories_allocated}")

# Ondas
print(f"Ondas processadas: {m.waves_processed}")
print(f"Iteracoes por onda: {m.iterations_per_wave}")

# Criterios
print(f"Por DEPENDENCY_OWNER: {m.allocations_by_dependency_owner}")
print(f"Por LOAD_BALANCING: {m.allocations_by_load_balancing}")

# Problemas
print(f"Deadlocks: {m.deadlocks_detected}")
print(f"Ajustes de data: {m.date_adjustments}")

# Validacao
print(f"Realocacoes: {m.validation_reallocations}")
print(f"Conflitos resolvidos: {m.validation_conflict_fixes}")
print(f"Violacoes de dependencia corrigidas: {m.validation_dependency_fixes}")

# Ociosidade
print(f"Violacoes de ociosidade detectadas: {m.max_idle_violations_detected}")
print(f"Violacoes corrigidas: {m.max_idle_violations_fixed}")
print(f"Realocacoes falhadas: {m.failed_reallocations}")
```

## Tratando Warnings

```python
from backlog_manager.domain.exceptions import (
    DeadlockWarning,
    IdlenessWarning,
    BetweenWavesIdlenessInfo,
)

result = await use_case.execute(input_dto)

for warning in result.warnings:
    if isinstance(warning, DeadlockWarning):
        print(f"ATENCAO: Deadlock na onda {warning.wave}")
        print(f"  Historias bloqueadas: {warning.blocked_stories}")

    elif isinstance(warning, IdlenessWarning):
        print(f"AVISO: Ociosidade de {warning.developer_name}")
        print(f"  {warning.idle_days} dias ociosos na onda {warning.wave}")

    elif isinstance(warning, BetweenWavesIdlenessInfo):
        print(f"INFO: Gap entre ondas para {warning.developer_name}")
        print(f"  {warning.idle_days} dias entre onda {warning.from_wave} e {warning.to_wave}")
```

## Configuracoes Avancadas

### Determinismo em Testes

```python
# Usando seed fixo para resultados reproduziveis
config = AllocationConfig(
    velocity=2.0,
    project_start_date=date(2026, 3, 2),
    random_seed=42,  # Seed fixo
)

# Mesma entrada + mesmo seed = mesmo resultado
result1 = AllocationService.allocate_stories(..., config=config)
result2 = AllocationService.allocate_stories(..., config=config)

assert result1.allocated_stories == result2.allocated_stories
```

### Limite de Iteracoes

```python
# Para backlogs muito grandes
config = AllocationConfig(
    velocity=2.0,
    project_start_date=date(2026, 3, 2),
    max_iterations=500,  # Reduzir se necessario
)
```

### Tolerancia de Ociosidade

```python
# Aumentar tolerancia para projetos com gaps naturais
config = AllocationConfig(
    velocity=2.0,
    project_start_date=date(2026, 3, 2),
    max_idle_days=5,  # Mais tolerante (padrao=3)
)
```
