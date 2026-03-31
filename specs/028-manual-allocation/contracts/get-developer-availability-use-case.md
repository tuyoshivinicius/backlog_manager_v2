# Application Contract: GetDeveloperAvailabilityUseCase

**Layer**: Application | **Type**: Query Use Case

## Assinatura

```python
class GetDeveloperAvailabilityUseCase:
    def __init__(self, uow: UnitOfWork) -> None: ...

    async def execute(
        self, input_dto: GetDeveloperAvailabilityInputDTO
    ) -> GetDeveloperAvailabilityOutputDTO: ...
```

## Input DTO

```python
class GetDeveloperAvailabilityInputDTO(BaseModel):
    story_id: str                          # ID da historia alvo
    candidate_start_date: date             # Data de inicio candidata
    velocity: float = Field(gt=0)          # SP/dia para recalculo
    allocation_criteria: str = "LOAD_BALANCING"  # Estrategia de alocacao
```

## Output DTO

```python
class GetDeveloperAvailabilityOutputDTO(BaseModel):
    developers: list[DeveloperAvailabilityDTO]  # Ordenados: livres primeiro
    recommended_developer_id: int | None         # ID do dev recomendado (ou None)
    story_start_date: date                       # Data de inicio usada
    story_end_date: date                         # Data de fim recalculada

class DeveloperAvailabilityDTO(BaseModel):
    developer_id: int
    developer_name: str
    is_available: bool
    is_recommended: bool
    blocking_stories: list[BlockingStoryDTO]
    story_count: int

class BlockingStoryDTO(BaseModel):
    story_id: str
    story_name: str
    start_date: date
    end_date: date
```

## Fluxo Interno

1. `story = await uow.stories.get_by_id(story_id)` — ValueError se nao existe
2. `developers = await uow.developers.get_all()`
3. `all_stories = await uow.stories.get_all()`
4. `dependencies = await uow.dependencies.get_all_dependencies()`
5. Recalcular `(start_date, end_date, duration)` via `SchedulingService.calculate_story_dates()`
6. Para cada developer:
   - Filtrar historias alocadas ao dev (excluindo a propria historia alvo)
   - Testar overlap com periodo recalculado via `AllocationService._has_period_overlap()`
   - Coletar blocking stories (nome, datas)
7. Identificar recomendacao via `AllocationService._select_developer()` entre devs livres
8. Retornar DTO ordenado (livres primeiro, depois ocupados)

## Erros

| Condicao | Excecao |
|----------|---------|
| Historia nao encontrada | `ValueError("Historia {story_id} nao encontrada")` |
| Historia sem story_points | `ValueError("Historia sem story points definidos")` |
| Nenhum desenvolvedor cadastrado | Retorna lista vazia (nao e erro) |
