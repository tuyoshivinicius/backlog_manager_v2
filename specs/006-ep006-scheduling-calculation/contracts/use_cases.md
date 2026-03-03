# Contract: Scheduling Use Cases

**Module**: `backlog_manager.application.use_cases.scheduling`
**Type**: Application Use Cases (async)

## Overview

Use cases para operacoes de cronograma. Todos os use cases sao assincronos e utilizam UnitOfWork para transacoes.

---

## CalculateScheduleUseCase

Calcula cronograma completo para todas as historias elegiveis do backlog.

### Constructor

```python
def __init__(self, uow: UnitOfWork) -> None
```

### execute

**Signature**:
```python
async def execute(self, input_dto: CalculateScheduleInputDTO) -> CalculateScheduleOutputDTO
```

### Input DTO

```python
class CalculateScheduleInputDTO(BaseModel):
    velocity: float = Field(gt=0, description="Velocidade em SP/dia")
    start_date: date = Field(description="Data de inicio do projeto")
    recalculate_all: bool = Field(default=True, description="Recalcular todas as historias")
```

### Output DTO

```python
class CalculateScheduleOutputDTO(BaseModel):
    success: bool
    stories_processed: int
    stories_updated: int
    warnings: list[str]
```

### Behavior

1. Busca todas as historias via `uow.stories.get_all()`
2. Filtra historias elegiveis:
   - status == BACKLOG
   - story_points valido (3, 5, 8, 13)
3. Se nenhuma elegivel: retorna success=True, stories_processed=0, warning
4. Busca dependencias via `uow.dependencies.get_all_dependencies()`
5. Constroi grafo via `DependencyService.build_graph()`
6. Ordena topologicamente via `SchedulingService.topological_sort()`
7. Para cada historia em ordem:
   - Busca end_dates das dependencias
   - Se dependencia sem end_date: usa project_start_date, adiciona warning
   - Calcula datas via `SchedulingService.calculate_story_dates()`
   - Atualiza story.duration, story.start_date, story.end_date
   - Persiste via `uow.stories.update()`
8. Commit automatico via UnitOfWork context manager
9. Retorna OutputDTO

### Warnings

| Condicao | Warning Message |
|----------|-----------------|
| Backlog vazio | "Nenhuma historia elegivel encontrada no backlog" |
| SP invalido | "Historia {id} ignorada: story_points invalido ou ausente" |
| Dep sem end_date | "Dependencia {dep_id} sem data: usando project_start_date como fallback" |

### Raises

- `CyclicDependencyException`: Se ciclo detectado no grafo de dependencias

### Example

```python
async with SQLiteUnitOfWork() as uow:
    use_case = CalculateScheduleUseCase(uow)
    result = await use_case.execute(
        CalculateScheduleInputDTO(
            velocity=2.0,
            start_date=date(2026, 3, 2)
        )
    )
    print(f"Processadas: {result.stories_processed}")
    print(f"Atualizadas: {result.stories_updated}")
    for warning in result.warnings:
        print(f"Warning: {warning}")
```

---

## CalculateDurationUseCase

Calcula duracao de uma historia individual (operacao pura, sem persistencia).

### Constructor

```python
def __init__(self) -> None
```

### execute

**Signature**:
```python
async def execute(self, input_dto: CalculateDurationInputDTO) -> CalculateDurationOutputDTO
```

### Input DTO

```python
class CalculateDurationInputDTO(BaseModel):
    story_points: int = Field(description="Story points")
    velocity: float = Field(gt=0, description="Velocidade em SP/dia")

    @field_validator("story_points")
    @classmethod
    def validate_story_points(cls, v: int) -> int:
        if v not in {3, 5, 8, 13}:
            raise ValueError("Story points deve ser 3, 5, 8 ou 13")
        return v
```

### Output DTO

```python
class CalculateDurationOutputDTO(BaseModel):
    duration: int
    formula: str
```

### Behavior

1. Valida input via Pydantic
2. Calcula duracao via `SchedulingService.calculate_duration()`
3. Constroi string da formula
4. Retorna OutputDTO

### Example

```python
use_case = CalculateDurationUseCase()
result = await use_case.execute(
    CalculateDurationInputDTO(story_points=5, velocity=2.0)
)
# result.duration = 3
# result.formula = "ceil(5 / 2.0) = 3"
```

---

## CalculateStoryDatesUseCase

Calcula e persiste datas para uma historia individual.

### Constructor

```python
def __init__(self, uow: UnitOfWork) -> None
```

### execute

**Signature**:
```python
async def execute(self, input_dto: CalculateStoryDatesInputDTO) -> CalculateStoryDatesOutputDTO
```

### Input DTO

```python
class CalculateStoryDatesInputDTO(BaseModel):
    story_id: str = Field(pattern=r"^[A-Z]{2,10}-\d{3}$", description="ID da historia")
    velocity: float = Field(gt=0, description="Velocidade em SP/dia")
    project_start_date: date = Field(description="Data de inicio do projeto")
```

### Output DTO

```python
class CalculateStoryDatesOutputDTO(BaseModel):
    story_id: str
    start_date: date
    end_date: date
    duration: int
```

### Behavior

1. Busca historia via `uow.stories.get_by_id()`
2. Se nao encontrada: ValueError
3. Busca dependencias via `uow.dependencies.get_dependencies()`
4. Para cada dependencia:
   - Busca historia da dependencia
   - Se end_date None: usa project_start_date como fallback
   - Coleta end_date
5. Calcula datas via `SchedulingService.calculate_story_dates()`
6. Atualiza story.duration, story.start_date, story.end_date
7. Persiste via `uow.stories.update()`
8. Retorna OutputDTO

### Raises

- `ValueError`: Se historia nao encontrada

### Example

```python
async with SQLiteUnitOfWork() as uow:
    use_case = CalculateStoryDatesUseCase(uow)
    result = await use_case.execute(
        CalculateStoryDatesInputDTO(
            story_id="FEAT-001",
            velocity=2.0,
            project_start_date=date(2026, 3, 2)
        )
    )
    print(f"Start: {result.start_date}")
    print(f"End: {result.end_date}")
    print(f"Duration: {result.duration} dias")
```
