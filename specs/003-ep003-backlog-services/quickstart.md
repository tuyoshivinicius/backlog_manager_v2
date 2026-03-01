# Quickstart: EP-003 Gestao de Backlog - Servicos e Aplicacao

**Date**: 2026-02-28

## Overview

Este documento fornece exemplos de uso dos Use Cases e StoryService implementados no EP-003.

## Prerequisites

- Python 3.11+
- Dependencias instaladas via `poetry install`
- Banco de dados inicializado (EP-001)

## Basic Usage

### Creating a Story

```python
from backlog_manager.application.use_cases.story import CreateStoryUseCase
from backlog_manager.application.dto.story import CreateStoryInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

# Setup use case with UnitOfWork factory
create_use_case = CreateStoryUseCase(lambda: SQLiteUnitOfWork())

# Create input DTO
input_dto = CreateStoryInputDTO(
    component="AUTH",
    name="Implementar login com OAuth",
    story_points=8,
    feature_id=1  # Optional
)

# Execute
async def main():
    result = await create_use_case.execute(input_dto)
    print(f"Historia criada: {result.id}")  # AUTH-001
    print(f"Prioridade: {result.priority}")  # 1 (primeira historia)
```

### Listing Stories

```python
from backlog_manager.application.use_cases.story import ListStoriesUseCase
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

list_use_case = ListStoriesUseCase(lambda: SQLiteUnitOfWork())

async def main():
    result = await list_use_case.execute()
    for story in result.stories:
        print(f"{story.id}: {story.name} (P{story.priority})")
```

### Updating a Story

```python
from backlog_manager.application.use_cases.story import UpdateStoryUseCase
from backlog_manager.application.dto.story import UpdateStoryInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

update_use_case = UpdateStoryUseCase(lambda: SQLiteUnitOfWork())

input_dto = UpdateStoryInputDTO(
    story_id="AUTH-001",
    name="Implementar login com OAuth 2.0",
    story_points=13,
    status="IN_PROGRESS"
)

async def main():
    result = await update_use_case.execute(input_dto)
    print(f"Nome: {result.name}")
    print(f"Story Points: {result.story_points}")
    print(f"Status: {result.status}")
```

### Moving Priority

```python
from backlog_manager.application.use_cases.story import MovePriorityUseCase
from backlog_manager.application.dto.story import MovePriorityInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

move_use_case = MovePriorityUseCase(lambda: SQLiteUnitOfWork())

# Move story up in priority (lower number = higher priority)
input_dto = MovePriorityInputDTO(
    story_id="AUTH-002",
    direction="up"
)

async def main():
    result = await move_use_case.execute(input_dto)
    if result.moved:
        print(f"Historia movida para prioridade {result.story.priority}")
    else:
        print("Historia ja esta no topo do backlog")
```

### Duplicating a Story

```python
from backlog_manager.application.use_cases.story import DuplicateStoryUseCase
from backlog_manager.application.dto.story import DuplicateStoryInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

duplicate_use_case = DuplicateStoryUseCase(lambda: SQLiteUnitOfWork())

input_dto = DuplicateStoryInputDTO(story_id="AUTH-001")

async def main():
    result = await duplicate_use_case.execute(input_dto)
    print(f"Copia criada: {result.id}")  # AUTH-002
    print(f"Status: {result.status}")     # BACKLOG (sempre)
    print(f"Developer: {result.developer_id}")  # None (resetado)
```

### Assigning a Developer

```python
from backlog_manager.application.use_cases.story import AssignDeveloperUseCase
from backlog_manager.application.dto.story import AssignDeveloperInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

assign_use_case = AssignDeveloperUseCase(lambda: SQLiteUnitOfWork())

# Assign developer
input_dto = AssignDeveloperInputDTO(
    story_id="AUTH-001",
    developer_id=1
)

async def main():
    result = await assign_use_case.execute(input_dto)
    print(f"Desenvolvedor alocado: {result.developer_id}")

# Unassign developer
input_dto = AssignDeveloperInputDTO(
    story_id="AUTH-001",
    developer_id=None
)

async def main():
    result = await assign_use_case.execute(input_dto)
    print(f"Desenvolvedor desalocado: {result.developer_id}")  # None
```

### Deleting a Story

```python
from backlog_manager.application.use_cases.story import DeleteStoryUseCase
from backlog_manager.application.dto.story import DeleteStoryInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

delete_use_case = DeleteStoryUseCase(lambda: SQLiteUnitOfWork())

input_dto = DeleteStoryInputDTO(story_id="AUTH-002")

async def main():
    await delete_use_case.execute(input_dto)
    print("Historia deletada")
    # Dependencias tambem foram removidas automaticamente
```

## Using StoryService Directly

Para operacoes mais baixo nivel ou composicao customizada:

```python
from backlog_manager.domain.services.story_service import StoryService
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

service = StoryService()

async def main():
    async with SQLiteUnitOfWork() as uow:
        # Generate ID
        story_id = await service.generate_story_id(uow, "CORE")
        print(f"Proximo ID: {story_id}")  # CORE-001

        # Get initial priority
        priority = await service.calculate_initial_priority(uow)
        print(f"Proxima prioridade: {priority}")  # 1 (se backlog vazio)

        # Create story
        story = await service.create_story(
            uow,
            component="CORE",
            name="Setup inicial",
            story_points=3
        )

        # Commit is automatic on exit
```

## Error Handling

```python
from backlog_manager.application.use_cases.story import UpdateStoryUseCase
from backlog_manager.application.dto.story import UpdateStoryInputDTO
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork

update_use_case = UpdateStoryUseCase(lambda: SQLiteUnitOfWork())

async def main():
    try:
        input_dto = UpdateStoryInputDTO(
            story_id="INVALID-999",  # Nao existe
            name="Novo nome"
        )
        await update_use_case.execute(input_dto)
    except ValueError as e:
        print(f"Erro: {e}")  # "Historia nao encontrada: INVALID-999"

    try:
        input_dto = CreateStoryInputDTO(
            component="X" * 100,  # Excede 50 chars
            name="Test",
            story_points=5
        )
    except ValidationError as e:
        print(f"Validacao falhou: {e}")
```

## Testing

```python
import pytest
from unittest.mock import AsyncMock, MagicMock

from backlog_manager.application.use_cases.story import CreateStoryUseCase
from backlog_manager.application.dto.story import CreateStoryInputDTO
from backlog_manager.domain.entities import Story

@pytest.mark.asyncio
async def test_create_story():
    # Mock UnitOfWork
    mock_uow = MagicMock()
    mock_uow.__aenter__ = AsyncMock(return_value=mock_uow)
    mock_uow.__aexit__ = AsyncMock(return_value=None)
    mock_uow.stories = MagicMock()
    mock_uow.stories.get_max_id_number = AsyncMock(return_value=0)
    mock_uow.stories.get_max_priority = AsyncMock(return_value=0)
    mock_uow.stories.add = AsyncMock()

    # Create use case with mock factory
    use_case = CreateStoryUseCase(lambda: mock_uow)

    # Execute
    input_dto = CreateStoryInputDTO(
        component="TEST",
        name="Test Story",
        story_points=5
    )
    result = await use_case.execute(input_dto)

    # Assert
    assert result.id == "TEST-001"
    assert result.priority == 1
    assert result.status == "BACKLOG"
    mock_uow.stories.add.assert_called_once()
```
