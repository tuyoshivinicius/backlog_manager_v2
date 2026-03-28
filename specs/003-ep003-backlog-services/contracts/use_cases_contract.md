# Use Cases Contract

**Module**: `backlog_manager.application.use_cases.story`
**Type**: Application Services
**Version**: 1.0.0

## Overview

Use cases coordenam StoryService com UnitOfWork para operacoes transacionais. Cada use case representa uma operacao de negocio completa.

## Common Pattern

Todos os use cases seguem o padrao:

```python
class XxxUseCase:
    def __init__(self, uow_factory: Callable[[], AsyncContextManager[UnitOfWork]]):
        self._uow_factory = uow_factory

    async def execute(self, input_dto: InputDTO) -> OutputDTO:
        async with self._uow_factory() as uow:
            service = StoryService(uow)
            result = await service.xxx(...)
            await uow.commit()
            return OutputDTO.from_entity(result)
```

---

## CreateStoryUseCase

```python
async def execute(self, input_dto: CreateStoryInputDTO) -> CreateStoryOutputDTO
```

**Input**: CreateStoryInputDTO
- `component: str` - Componente (1-50 chars)
- `name: str` - Nome (1-200 chars)
- `story_points: int` - Pontos (3, 5, 8, 13)
- `feature_id: int | None` - Feature opcional

**Output**: CreateStoryOutputDTO
- `id, component, name, story_points, priority, status, feature_id`

**Errors**: Propagados do StoryService e validacao Pydantic

---

## UpdateStoryUseCase

```python
async def execute(self, input_dto: UpdateStoryInputDTO) -> StoryOutputDTO
```

**Input**: UpdateStoryInputDTO
- `story_id: str` - ID da historia
- `name: str | None` - Novo nome (opcional)
- `story_points: int | None` - Novos pontos (opcional)
- `status: str | None` - Novo status (opcional)
- `feature_id: int | None` - Nova feature (opcional)
- `clear_feature: bool` - True para remover feature

**Output**: StoryOutputDTO (todos os campos da Story)

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")`

---

## DeleteStoryUseCase

```python
async def execute(self, story_id: str) -> None
```

**Input**: `story_id: str`

**Output**: None

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")`

---

## DuplicateStoryUseCase

```python
async def execute(self, story_id: str) -> StoryOutputDTO
```

**Input**: `story_id: str`

**Output**: StoryOutputDTO (nova historia)

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")`

---

## ListStoriesUseCase

```python
async def execute(self) -> ListStoriesOutputDTO
```

**Input**: None

**Output**: ListStoriesOutputDTO
- `stories: list[StoryOutputDTO]` - Lista ordenada por prioridade

---

## MovePriorityUseCase

```python
async def execute(self, input_dto: MovePriorityInputDTO) -> MovePriorityOutputDTO
```

**Input**: MovePriorityInputDTO
- `story_id: str` - ID da historia
- `direction: Literal["up", "down"]` - Direcao

**Output**: MovePriorityOutputDTO
- `moved: bool` - True se moveu
- `story: StoryOutputDTO` - Historia atualizada

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")`

---

## AssignDeveloperUseCase

```python
async def execute(self, input_dto: AssignDeveloperInputDTO) -> StoryOutputDTO
```

**Input**: AssignDeveloperInputDTO
- `story_id: str` - ID da historia
- `developer_id: int | None` - ID do desenvolvedor ou None

**Output**: StoryOutputDTO (historia atualizada)

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")`
- `ValueError("Desenvolvedor nao encontrado: {developer_id}")`
