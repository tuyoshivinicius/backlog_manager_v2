# Data Model: EP-003 Gestao de Backlog - Servicos e Aplicacao

**Date**: 2026-02-28
**Status**: Complete

## Overview

Este documento define as estruturas de dados introduzidas no EP-003. O foco sao os DTOs da camada de aplicacao e as extensoes aos repositorios existentes. A entidade Story ja existe (EP-001/EP-002) e nao e modificada.

## Entities (Existing - No Changes)

### Story Entity

A entidade Story foi definida em EP-001 e validada em EP-002. Nao ha alteracoes na estrutura.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| id | str | PK, Pattern COMPONENTE-NNN | Imutavel apos criacao |
| component | str | Max 50 chars, not empty | Imutavel, uppercase |
| name | str | Max 200 chars, not empty | Editavel |
| story_points | StoryPoint | Enum: 3, 5, 8, 13 | Editavel |
| priority | int | >= 0 | Gerenciado pelo StoryService |
| status | StoryStatus | Enum: BACKLOG, IN_PROGRESS, DONE, BLOCKED | Editavel |
| duration | int or None | >= 0 | Calculado pelo sistema |
| start_date | date or None | - | Calculado pelo sistema |
| end_date | date or None | >= start_date | Calculado pelo sistema |
| developer_id | int or None | FK Developer | Editavel via assign |
| feature_id | int or None | FK Feature | Editavel |

## DTOs (New)

### Input DTOs

#### CreateStoryInputDTO

DTO para entrada de criacao de historia.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| component | str | Yes | Not empty, max 50 chars, uppercase |
| name | str | Yes | Not empty, max 200 chars |
| story_points | int | Yes | Must be 3, 5, 8, or 13 |
| feature_id | int or None | No | Positive integer if provided |

#### UpdateStoryInputDTO

DTO para entrada de atualizacao de historia.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| story_id | str | Yes | Pattern COMPONENTE-NNN |
| name | str or None | No | Max 200 chars if provided |
| story_points | int or None | No | Must be 3, 5, 8, or 13 if provided |
| status | str or None | No | Valid StoryStatus value |
| feature_id | int or None | No | Positive integer if provided |
| clear_feature | bool | No (default False) | If True, sets feature_id to None |

#### DeleteStoryInputDTO

DTO para entrada de delecao de historia.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| story_id | str | Yes | Pattern COMPONENTE-NNN |

#### DuplicateStoryInputDTO

DTO para entrada de duplicacao de historia.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| story_id | str | Yes | Pattern COMPONENTE-NNN |

#### MovePriorityInputDTO

DTO para entrada de movimentacao de prioridade.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| story_id | str | Yes | Pattern COMPONENTE-NNN |
| direction | Literal["up", "down"] | Yes | Must be "up" or "down" |

#### AssignDeveloperInputDTO

DTO para entrada de atribuicao de desenvolvedor.

| Field | Type | Required | Validation |
|-------|------|----------|------------|
| story_id | str | Yes | Pattern COMPONENTE-NNN |
| developer_id | int or None | Yes | None to unassign, positive int to assign |

### Output DTOs

#### StoryOutputDTO

DTO padrao para saida de historia (usado por todos os use cases).

| Field | Type | Source |
|-------|------|--------|
| id | str | story.id |
| component | str | story.component |
| name | str | story.name |
| story_points | int | int(story.story_points) |
| priority | int | story.priority |
| status | str | str(story.status) |
| duration | int or None | story.duration |
| start_date | date or None | story.start_date |
| end_date | date or None | story.end_date |
| developer_id | int or None | story.developer_id |
| feature_id | int or None | story.feature_id |

**Methods**:
- `from_entity(story: Story) -> StoryOutputDTO`: Classmethod para conversao

#### CreateStoryOutputDTO

Alias para StoryOutputDTO (clareza semantica no use case).

#### ListStoriesOutputDTO

DTO para saida de listagem de historias.

| Field | Type | Source |
|-------|------|--------|
| stories | list[StoryOutputDTO] | Lista de stories convertidas |

#### MovePriorityOutputDTO

DTO para saida de movimentacao de prioridade.

| Field | Type | Source |
|-------|------|--------|
| moved | bool | True se movimento ocorreu |
| story | StoryOutputDTO | Historia apos operacao |

## Repository Extensions

### StoryRepository (Existing Protocol - Extended)

Novos metodos adicionados ao protocol existente:

| Method | Signature | Return | Description |
|--------|-----------|--------|-------------|
| get_max_id_number | (component: str) -> int | int | Maior numero NNN do componente, 0 se nenhum |
| get_max_priority | () -> int | int | Maior prioridade existente, 0 se vazio |
| get_by_priority | (priority: int) -> Story or None | Story or None | Historia com prioridade exata |

### StoryDependencyRepository (Existing Protocol - Extended)

Novo metodo adicionado ao protocol existente:

| Method | Signature | Return | Description |
|--------|-----------|--------|-------------|
| remove_all_for_story | (story_id: str) -> None | None | Remove todas as dependencias onde story_id aparece |

## Domain Service

### StoryService

Servico de dominio stateless para operacoes de negocio de historias.

| Method | Signature | Description |
|--------|-----------|-------------|
| generate_story_id | (uow: UnitOfWork, component: str) -> str | Gera ID no formato COMPONENTE-NNN |
| calculate_initial_priority | (uow: UnitOfWork) -> int | Retorna max(prioridades) + 1 |
| create_story | (uow, component, name, story_points, feature_id) -> Story | Cria historia com ID e prioridade auto |
| update_story | (uow, story_id, name, story_points, status, feature_id, clear_feature) -> Story | Atualiza campos editaveis |
| delete_story | (uow, story_id) -> None | Remove historia e dependencias |
| duplicate_story | (uow, story_id) -> Story | Duplica com novo ID e campos resetados |
| move_priority | (uow, story_id, direction) -> bool | Move prioridade cima/baixo |
| assign_developer | (uow, story_id, developer_id) -> Story | Atribui/desatribui desenvolvedor |
| list_stories | (uow) -> Sequence[Story] | Lista historias por prioridade |

## State Transitions

### Story Status

Nao ha restricoes de transicao de status neste EP. Qualquer status pode ser alterado para qualquer outro via UpdateStoryUseCase.

```
BACKLOG <--> IN_PROGRESS <--> DONE
    ^            ^             ^
    |            |             |
    +--------- BLOCKED --------+
```

### Story Priority

Prioridades sao gerenciadas pelo StoryService:
- Create: priority = max(existentes) + 1
- Move Up: swap com priority - 1
- Move Down: swap com priority + 1
- Delete: gap pode ser criado (aceito por ADR-007)

## Relationships

```
Story *--1 Developer (optional via developer_id)
Story *--1 Feature (optional via feature_id)
Story *--* Story (dependencies via StoryDependency table)
```

## Validation Rules Summary

| Entity/DTO | Field | Rule | Error Message |
|------------|-------|------|---------------|
| CreateStoryInputDTO | component | not empty, max 50 | "Componente nao pode ser vazio" |
| CreateStoryInputDTO | name | not empty, max 200 | "Nome nao pode ser vazio" |
| CreateStoryInputDTO | story_points | in (3,5,8,13) | "Story points deve ser 3, 5, 8 ou 13" |
| UpdateStoryInputDTO | story_id | exists | "Historia nao encontrada: {id}" |
| AssignDeveloperInputDTO | developer_id | exists if not None | "Desenvolvedor nao encontrado: {id}" |
| MovePriorityInputDTO | direction | "up" or "down" | Pydantic validation |
