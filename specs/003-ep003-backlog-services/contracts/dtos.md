# DTO Contracts: EP-003 Gestao de Backlog

**Date**: 2026-02-28
**Type**: Pydantic Models

## Overview

Este documento define os contratos dos Data Transfer Objects (DTOs) Pydantic utilizados pelos Use Cases.

## Input DTOs

### CreateStoryInputDTO

```python
class CreateStoryInputDTO(BaseModel):
    component: str           # Obrigatorio, 1-50 chars, auto-uppercase
    name: str                # Obrigatorio, 1-200 chars
    story_points: int        # Obrigatorio, valores: 3, 5, 8, 13
    feature_id: int | None   # Opcional, referencia Feature
```

**Validation Rules**:
- `component`: strip, not empty, max 50, converted to uppercase
- `name`: strip, not empty, max 200
- `story_points`: must be in {3, 5, 8, 13}
- `feature_id`: positive integer if provided

### UpdateStoryInputDTO

```python
class UpdateStoryInputDTO(BaseModel):
    story_id: str                 # Obrigatorio, pattern COMPONENTE-NNN
    name: str | None = None       # Opcional, novo nome
    story_points: int | None = None  # Opcional, nova estimativa
    status: str | None = None     # Opcional, novo status
    feature_id: int | None = None # Opcional, nova feature
    clear_feature: bool = False   # Se True, remove feature (feature_id=None)
```

**Validation Rules**:
- `story_id`: pattern ^[A-Z]+-\d{3}$
- `name`: max 200 if provided
- `story_points`: must be in {3, 5, 8, 13} if provided
- `status`: must be valid StoryStatus value
- `clear_feature`: precedence over feature_id when True

### DeleteStoryInputDTO

```python
class DeleteStoryInputDTO(BaseModel):
    story_id: str  # Obrigatorio, pattern COMPONENTE-NNN
```

### DuplicateStoryInputDTO

```python
class DuplicateStoryInputDTO(BaseModel):
    story_id: str  # Obrigatorio, pattern COMPONENTE-NNN
```

### MovePriorityInputDTO

```python
class MovePriorityInputDTO(BaseModel):
    story_id: str                          # Obrigatorio, pattern COMPONENTE-NNN
    direction: Literal["up", "down"]       # Obrigatorio
```

### AssignDeveloperInputDTO

```python
class AssignDeveloperInputDTO(BaseModel):
    story_id: str          # Obrigatorio, pattern COMPONENTE-NNN
    developer_id: int | None  # None para desalocar, int para alocar
```

## Output DTOs

### StoryOutputDTO

DTO padrao para representacao de historia.

```python
class StoryOutputDTO(BaseModel):
    id: str
    component: str
    name: str
    story_points: int
    priority: int
    status: str
    duration: int | None
    start_date: date | None
    end_date: date | None
    developer_id: int | None
    feature_id: int | None

    @classmethod
    def from_entity(cls, story: Story) -> "StoryOutputDTO": ...
```

### CreateStoryOutputDTO

Alias para StoryOutputDTO (semantica).

```python
CreateStoryOutputDTO = StoryOutputDTO
```

### ListStoriesOutputDTO

```python
class ListStoriesOutputDTO(BaseModel):
    stories: list[StoryOutputDTO]

    @classmethod
    def from_entities(cls, stories: Sequence[Story]) -> "ListStoriesOutputDTO": ...
```

### MovePriorityOutputDTO

```python
class MovePriorityOutputDTO(BaseModel):
    moved: bool
    story: StoryOutputDTO
```

## Serialization Format

Todos os DTOs sao serializaveis para JSON via Pydantic:

```python
dto = CreateStoryInputDTO(component="AUTH", name="Login", story_points=5)
json_str = dto.model_dump_json()
# {"component": "AUTH", "name": "Login", "story_points": 5, "feature_id": null}
```

Datas sao serializadas em formato ISO 8601:
```python
# start_date: "2026-03-01"
```
