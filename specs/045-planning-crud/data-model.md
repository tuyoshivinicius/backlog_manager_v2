# Data Model: Modulo de Planejamentos (CRUD Completo)

**Feature**: 045-planning-crud | **Date**: 2026-04-08

## Entidades

### Planning (NOVA)

Representa um conjunto nomeado de historias que compoem uma visao de planejamento.

| Campo | Tipo | Restricoes | Descricao |
|-------|------|-----------|-----------|
| `id` | `int` | PK, auto-increment | Identificador unico |
| `name` | `str` | NOT NULL, UNIQUE, max 200 chars | Nome do planejamento |
| `created_at` | `datetime` | NOT NULL, auto (UTC) | Data de criacao |
| `updated_at` | `datetime` | NOT NULL, auto (UTC) | Data de ultima modificacao |

**Invariantes de dominio**:
- Nome nao pode ser vazio ou apenas espacos
- Nome nao pode exceder 200 caracteres
- Nome deve ser unico entre todos os planejamentos

**Entidade de dominio** (`domain/entities/planning.py`):

```python
@dataclass
class Planning:
    id: int | None  # None para novos (auto-generated pelo DB)
    name: str
    created_at: datetime | None = None  # Auto-set pelo repositorio
    updated_at: datetime | None = None  # Auto-set pelo repositorio

    def __post_init__(self) -> None:
        self._validate_name()

    def _validate_name(self) -> None:
        if not self.name or not self.name.strip():
            raise ValueError("Nome do planejamento nao pode ser vazio")
        if len(self.name) > 200:
            raise ValueError("Nome do planejamento nao pode exceder 200 caracteres")
```

### Story (MODIFICADA)

Adiciona referencia obrigatoria ao planejamento.

| Campo | Tipo | Restricoes | Descricao | Status |
|-------|------|-----------|-----------|--------|
| `planning_id` | `int` | NOT NULL, FK → Planning(id) | Planejamento ao qual pertence | **NOVO** |
| `id` | `str` | NOT NULL, max 20 chars | Codigo do ticket externo | Existente |
| `component` | `str` | NOT NULL, max 50 chars | Componente/modulo | Existente |
| `name` | `str` | NOT NULL, max 200 chars | Nome da historia | Existente |
| `story_points` | `StoryPoint` | NOT NULL, {3,5,8,13} | Estimativa | Existente |
| `priority` | `int` | NOT NULL, >= 0 | Prioridade | Existente |
| `status` | `StoryStatus` | NOT NULL, default BACKLOG | Estado | Existente |
| `duration` | `int \| None` | >= 0 | Duracao calculada | Existente |
| `start_date` | `date \| None` | | Data inicio calculada | Existente |
| `end_date` | `date \| None` | | Data fim calculada | Existente |
| `developer_id` | `int \| None` | FK → Developer(id) | Dev alocado | Existente |
| `feature_id` | `int \| None` | FK → Feature(id) | Feature/wave | Existente |

**Mudanca de PK**: De `PRIMARY KEY (id)` para `PRIMARY KEY (planning_id, id)`.

**Unicidade**: O `id` (ticket code) eh unico apenas dentro do escopo do planejamento — constraint composta `(planning_id, id)`.

### Story_Dependency (MODIFICADA)

Adiciona `planning_id` para composite FK references.

| Campo | Tipo | Restricoes | Descricao | Status |
|-------|------|-----------|-----------|--------|
| `planning_id` | `int` | NOT NULL | Planejamento das historias | **NOVO** |
| `story_id` | `str` | NOT NULL | Historia dependente | Existente (FK alterada) |
| `depends_on_id` | `str` | NOT NULL | Historia da qual depende | Existente (FK alterada) |

**PK**: `(planning_id, story_id, depends_on_id)`
**FKs**: Ambas referenciam `Story(planning_id, id) ON DELETE CASCADE`

## Schema SQL

### Tabela Planning (NOVA)

```sql
CREATE TABLE IF NOT EXISTS Planning (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(200) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT (datetime('now')),
    updated_at TIMESTAMP NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_planning_name ON Planning(name);
```

### Tabela Story (ALTERADA)

```sql
CREATE TABLE IF NOT EXISTS Story (
    planning_id INTEGER NOT NULL REFERENCES Planning(id) ON DELETE CASCADE,
    id VARCHAR(20) NOT NULL,
    component VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    story_points INTEGER NOT NULL CHECK (story_points IN (3, 5, 8, 13)),
    priority INTEGER NOT NULL CHECK (priority >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'BACKLOG',
    duration INTEGER,
    start_date DATE,
    end_date DATE,
    developer_id INTEGER REFERENCES Developer(id) ON DELETE SET NULL,
    feature_id INTEGER REFERENCES Feature(id) ON DELETE SET NULL,
    PRIMARY KEY (planning_id, id)
);

CREATE INDEX IF NOT EXISTS idx_story_planning ON Story(planning_id);
CREATE INDEX IF NOT EXISTS idx_story_status ON Story(planning_id, status);
CREATE INDEX IF NOT EXISTS idx_story_developer ON Story(planning_id, developer_id);
CREATE INDEX IF NOT EXISTS idx_story_feature ON Story(planning_id, feature_id);
CREATE INDEX IF NOT EXISTS idx_story_priority ON Story(planning_id, priority);
```

### Tabela Story_Dependency (ALTERADA)

```sql
CREATE TABLE IF NOT EXISTS Story_Dependency (
    planning_id INTEGER NOT NULL,
    story_id VARCHAR(20) NOT NULL,
    depends_on_id VARCHAR(20) NOT NULL,
    PRIMARY KEY (planning_id, story_id, depends_on_id),
    FOREIGN KEY (planning_id, story_id) REFERENCES Story(planning_id, id) ON DELETE CASCADE,
    FOREIGN KEY (planning_id, depends_on_id) REFERENCES Story(planning_id, id) ON DELETE CASCADE,
    CHECK (story_id != depends_on_id)
);
```

## Migracao de Dados

A migracao eh executada automaticamente no startup quando detecta schema antigo (Story sem coluna `planning_id`).

### Passos da migracao

```sql
-- 1. Criar tabela Planning
CREATE TABLE IF NOT EXISTS Planning (...);

-- 2. Inserir planejamento default
INSERT INTO Planning (name) VALUES ('Planejamento Inicial');

-- 3. Rename tabela antiga
ALTER TABLE Story RENAME TO Story_old;
ALTER TABLE Story_Dependency RENAME TO Story_Dependency_old;

-- 4. Criar tabela Story com novo schema
CREATE TABLE Story (...);  -- com planning_id e composite PK

-- 5. Copiar dados com planning_id do planejamento default
INSERT INTO Story (planning_id, id, component, name, story_points, priority, status,
                   duration, start_date, end_date, developer_id, feature_id)
SELECT (SELECT id FROM Planning WHERE name = 'Planejamento Inicial'),
       id, component, name, story_points, priority, status,
       duration, start_date, end_date, developer_id, feature_id
FROM Story_old;

-- 6. Recriar Story_Dependency com novo schema
CREATE TABLE Story_Dependency (...);

INSERT INTO Story_Dependency (planning_id, story_id, depends_on_id)
SELECT (SELECT id FROM Planning WHERE name = 'Planejamento Inicial'),
       story_id, depends_on_id
FROM Story_Dependency_old;

-- 7. Drop tabelas antigas
DROP TABLE Story_Dependency_old;
DROP TABLE Story_old;

-- 8. Recriar indices
CREATE INDEX IF NOT EXISTS idx_story_planning ON Story(planning_id);
-- ... demais indices
```

### Deteccao de schema antigo

```python
async def _needs_migration(conn: aiosqlite.Connection) -> bool:
    cursor = await conn.execute("PRAGMA table_info(Story)")
    columns = await cursor.fetchall()
    column_names = [col[1] for col in columns]
    return "planning_id" not in column_names
```

## Relacionamentos

```
Planning (1) ──── (0..*) Story
    │                      │
    │                      ├── (0..1) Developer
    │                      └── (0..1) Feature
    │
    └── Story_Dependency (via planning_id scope)
            Story (planning_id, story_id) ──depends_on──▶ Story (planning_id, depends_on_id)
```

## Transicoes de Estado

### Planning Lifecycle

```
[Criado] → [Ativo] ←→ [Inativo] → [Excluido]
```

- **Criado**: `CreatePlanningUseCase` — torna-se ativo imediatamente
- **Ativo**: O planejamento cujas historias estao exibidas na tabela principal (maximo 1 ativo por vez)
- **Inativo**: Qualquer planejamento que nao eh o ativo
- **Excluido**: `DeletePlanningUseCase` — cascade remove historias e dependencias

Notas:
- O estado "ativo" nao eh persistido no banco — eh controlado via QSettings (`planning/last_active_id`)
- Nao eh possivel excluir o planejamento ativo (FR-006)
- Ao excluir o ultimo planejamento, sistema volta ao bootstrap (solicita criacao)

## Interfaces de Repositorio

### PlanningRepository (NOVO Protocol)

```python
class PlanningRepository(Protocol):
    async def add(self, planning: Planning) -> int: ...
    async def get_by_id(self, planning_id: int) -> Planning | None: ...
    async def get_by_name(self, name: str) -> Planning | None: ...
    async def get_all(self) -> Sequence[Planning]: ...
    async def update(self, planning: Planning) -> None: ...
    async def delete(self, planning_id: int) -> None: ...
    async def exists(self, planning_id: int) -> bool: ...
    async def count_stories(self, planning_id: int) -> int: ...
    async def update_timestamp(self, planning_id: int) -> None: ...
```

### StoryRepository (MODIFICADO — assinaturas com planning_id)

Todos os metodos de query recebem `planning_id: int` como primeiro parametro. Metodos que operam sobre a entidade (add, update) extraem `planning_id` do objeto Story.

### StoryDependencyRepository (MODIFICADO — assinaturas com planning_id)

Todos os metodos recebem `planning_id: int` para scoping de dependencias intra-planejamento.

### UnitOfWork (MODIFICADO)

Adiciona propriedade `plannings: PlanningRepository`.
