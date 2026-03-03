# StoryService Contract

**Module**: `backlog_manager.domain.services.story_service`
**Type**: Domain Service
**Version**: 1.0.0

## Overview

StoryService e o domain service responsavel por todas as regras de negocio relacionadas a gestao de historias no backlog. Fornece operacoes CRUD completas com geracao automatica de ID e prioridade.

## Dependencies

- `UnitOfWork` - Injetado via construtor, fornece acesso aos repositorios

## Methods

### generate_story_id

```python
async def generate_story_id(self, component: str) -> str
```

**Purpose**: Gera ID unico no formato COMPONENTE-NNN

**Parameters**:
- `component: str` - Nome do componente (sera convertido para MAIUSCULAS)

**Returns**: `str` - ID no formato COMPONENTE-NNN (ex: "AUTH-001")

**Behavior**:
- Busca maior numero existente para o componente via repositorio
- Se nenhuma historia existe: retorna COMPONENTE-001
- Caso contrario: retorna COMPONENTE-(max+1) com padding de zeros

**Example**:
```python
id1 = await service.generate_story_id("auth")  # "AUTH-001"
id2 = await service.generate_story_id("auth")  # "AUTH-002"
id3 = await service.generate_story_id("core")  # "CORE-001"
```

---

### calculate_initial_priority

```python
async def calculate_initial_priority(self) -> int
```

**Purpose**: Calcula prioridade inicial para nova historia

**Returns**: `int` - Proxima prioridade disponivel

**Behavior**:
- Se backlog vazio: retorna 1
- Caso contrario: retorna max(prioridades) + 1

---

### create_story

```python
async def create_story(
    self,
    component: str,
    name: str,
    story_points: int,
    feature_id: int | None = None
) -> Story
```

**Purpose**: Cria nova historia com ID e prioridade automaticos

**Parameters**:
- `component: str` - Componente (1-50 chars)
- `name: str` - Nome da historia (1-200 chars)
- `story_points: int` - Pontos (3, 5, 8, ou 13)
- `feature_id: int | None` - ID da feature associada (opcional)

**Returns**: `Story` - Historia criada e persistida

**Behavior**:
1. Gera ID via `generate_story_id(component)`
2. Calcula prioridade via `calculate_initial_priority()`
3. Cria Story com status=BACKLOG
4. Persiste via repositorio

**Errors**:
- `ValueError` - Parametros invalidos (nome vazio, SP invalido, etc.)

---

### update_story

```python
async def update_story(
    self,
    story_id: str,
    name: str | None = None,
    story_points: int | None = None,
    status: str | None = None,
    feature_id: int | None = ...,
) -> Story
```

**Purpose**: Atualiza campos de historia existente

**Parameters**:
- `story_id: str` - ID da historia a atualizar
- `name: str | None` - Novo nome (opcional)
- `story_points: int | None` - Novos pontos (opcional)
- `status: str | None` - Novo status (opcional)
- `feature_id` - `...` = nao alterar, `int` = novo valor, `None` = remover

**Returns**: `Story` - Historia atualizada

**Behavior**:
- ID e component sao imutaveis (ignorados se passados)
- Apenas campos nao-None sao atualizados
- Persiste alteracoes via repositorio

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")` - Historia nao existe

---

### delete_story

```python
async def delete_story(self, story_id: str) -> None
```

**Purpose**: Remove historia e suas dependencias

**Parameters**:
- `story_id: str` - ID da historia a deletar

**Behavior**:
1. Remove todas as dependencias via `remove_all_for_story(story_id)`
2. Remove a historia via repositorio

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")` - Historia nao existe

---

### duplicate_story

```python
async def duplicate_story(self, story_id: str) -> Story
```

**Purpose**: Duplica historia existente

**Parameters**:
- `story_id: str` - ID da historia a duplicar

**Returns**: `Story` - Nova historia (copia)

**Behavior**:
- **Copiados**: component, name, story_points, feature_id
- **Resetados**: id (novo), priority (max+1), status (BACKLOG)
- **Nulos**: developer_id, start_date, end_date, duration

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")` - Historia nao existe

---

### move_priority

```python
async def move_priority(
    self,
    story_id: str,
    direction: Literal["up", "down"]
) -> bool
```

**Purpose**: Move historia na fila de prioridade

**Parameters**:
- `story_id: str` - ID da historia
- `direction: Literal["up", "down"]` - Direcao ("up" = menor numero, "down" = maior numero)

**Returns**: `bool` - True se moveu, False se na borda

**Behavior**:
- "up": troca com historia de prioridade p-1
- "down": troca com historia de prioridade p+1
- Se nao ha adjacente: retorna False (borda)
- Swap e atomico (ambas atualizadas na mesma transacao)

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")` - Historia nao existe

---

### assign_developer

```python
async def assign_developer(
    self,
    story_id: str,
    developer_id: int | None
) -> Story
```

**Purpose**: Atribui ou remove desenvolvedor de historia

**Parameters**:
- `story_id: str` - ID da historia
- `developer_id: int | None` - ID do desenvolvedor ou None para desalocar

**Returns**: `Story` - Historia atualizada

**Behavior**:
- Se `developer_id` nao e None: valida existencia
- Atualiza `developer_id` da historia

**Errors**:
- `ValueError("Historia nao encontrada: {story_id}")` - Historia nao existe
- `ValueError("Desenvolvedor nao encontrado: {developer_id}")` - Desenvolvedor nao existe

---

### list_stories

```python
async def list_stories(self) -> Sequence[Story]
```

**Purpose**: Lista todas as historias ordenadas por prioridade

**Returns**: `Sequence[Story]` - Lista ordenada (prioridade crescente)

**Behavior**:
- Retorna todas as historias independente de status
- Ordenacao por priority ASC (menor = mais prioritario)
- Lista vazia se backlog vazio
