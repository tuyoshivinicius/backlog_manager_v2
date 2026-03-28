# Repository Extensions Contract

**Module**: `backlog_manager.domain.interfaces.repositories`
**Type**: Protocol Extensions
**Version**: 1.0.0

## Overview

EP-003 adiciona novos metodos aos protocols de repositorio existentes. Implementacoes SQLite devem ser atualizadas para suportar estes metodos.

---

## StoryRepository Extensions

### get_max_id_number

```python
async def get_max_id_number(self, component: str) -> int
```

**Purpose**: Retorna o maior numero sequencial para um componente

**Parameters**:
- `component: str` - Nome do componente (case-insensitive na busca)

**Returns**: `int` - Maior numero NNN encontrado ou 0 se nenhum

**SQL Implementation**:
```sql
SELECT COALESCE(
    MAX(CAST(SUBSTR(id, INSTR(id, '-') + 1) AS INTEGER)),
    0
)
FROM Story
WHERE UPPER(component) = UPPER(?)
```

**Examples**:
- Nenhuma historia com "AUTH": retorna 0
- Historias AUTH-001, AUTH-002, AUTH-005: retorna 5
- Historias CORE-001, AUTH-001: get_max_id_number("auth") retorna 1

---

### get_max_priority

```python
async def get_max_priority(self) -> int
```

**Purpose**: Retorna a maior prioridade existente no backlog

**Returns**: `int` - Maior prioridade ou 0 se backlog vazio

**SQL Implementation**:
```sql
SELECT COALESCE(MAX(priority), 0) FROM Story
```

---

### get_by_priority

```python
async def get_by_priority(self, priority: int) -> Story | None
```

**Purpose**: Busca historia por prioridade exata

**Parameters**:
- `priority: int` - Prioridade a buscar

**Returns**: `Story | None` - Historia encontrada ou None

**SQL Implementation**:
```sql
SELECT * FROM Story WHERE priority = ?
```

**Notes**:
- Assume prioridades unicas (invariante do sistema)
- Usado para swap de prioridades no move_priority

---

## StoryDependencyRepository Extensions

### remove_all_for_story

```python
async def remove_all_for_story(self, story_id: str) -> None
```

**Purpose**: Remove todas as dependencias onde a historia aparece

**Parameters**:
- `story_id: str` - ID da historia

**Behavior**:
- Remove onde `story_id` e o dependente (story_id)
- Remove onde `story_id` e a dependencia (depends_on_id)

**SQL Implementation**:
```sql
DELETE FROM Story_Dependency
WHERE story_id = ? OR depends_on_id = ?
```

**Notes**:
- Deve ser chamado ANTES de deletar a historia
- Operacao e idempotente (OK se nenhuma dependencia existe)
