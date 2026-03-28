# Data Model: EP-001 Fundacao e Persistencia

**Feature**: EP-001 Fundacao e Persistencia
**Date**: 2026-02-28
**Status**: Completo

## Visao Geral

Este documento define o modelo de dados para o Backlog Manager, incluindo entidades de dominio, value objects, e o schema de persistencia SQLite.

---

## Entidades de Dominio

### 1. Story (Historia)

Unidade de trabalho representando uma User Story no backlog.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | str | Sim | Identificador unico no formato COMPONENTE-NNN (ex: AUTH-001) |
| component | str | Sim | Componente/modulo ao qual pertence (max 50 chars) |
| name | str | Sim | Nome/titulo da historia (max 200 chars) |
| story_points | StoryPoint | Sim | Estimativa em pontos Fibonacci (3, 5, 8, 13) |
| priority | int | Sim | Prioridade numerica (>= 0, menor = mais prioritario) |
| status | StoryStatus | Sim | Estado atual do workflow (default: BACKLOG) |
| duration | int | Nao | Duracao em dias uteis (calculado) |
| start_date | date | Nao | Data de inicio (calculado) |
| end_date | date | Nao | Data de termino (calculado) |
| developer_id | int | Nao | Referencia ao desenvolvedor alocado |
| feature_id | int | Nao | Referencia a feature/wave |

**Invariantes**:
- `id` deve seguir padrao COMPONENTE-NNN (regex: `^[A-Z]+-\d{3}$`)
- `component` e `name` nao podem ser vazios ou apenas espacos
- `story_points` deve ser 3, 5, 8 ou 13
- `priority` deve ser >= 0
- Se `start_date` e `end_date` definidos, `start_date <= end_date`

**Transicoes de Status**:
```
BACKLOG -> IN_PROGRESS -> DONE
             |
             v
         BLOCKED -> IN_PROGRESS
```

---

### 2. Developer (Desenvolvedor)

Pessoa que executa historias.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | int | Sim (auto) | Identificador unico auto-incrementado |
| name | str | Sim | Nome do desenvolvedor (max 100 chars) |

**Invariantes**:
- `name` nao pode ser vazio ou apenas espacos
- `name` deve ter no maximo 100 caracteres

---

### 3. Feature (Funcionalidade)

Agrupamento de historias em ondas de entrega.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| id | int | Sim (auto) | Identificador unico auto-incrementado |
| name | str | Sim | Nome da feature (max 100 chars, UNIQUE) |
| wave | int | Sim | Numero da onda de entrega (> 0, UNIQUE) |

**Invariantes**:
- `name` nao pode ser vazio ou apenas espacos
- `name` deve ser unico no sistema
- `wave` deve ser > 0
- `wave` deve ser unico no sistema (uma wave por feature)

---

### 4. Story_Dependency (Dependencia entre Historias)

Relacao N:M auto-referenciada entre Stories.

| Campo | Tipo | Obrigatorio | Descricao |
|-------|------|-------------|-----------|
| story_id | str | Sim | Historia que depende de outra |
| depends_on_id | str | Sim | Historia da qual depende |

**Invariantes**:
- `story_id != depends_on_id` (historia nao pode depender de si mesma)
- Par (story_id, depends_on_id) deve ser unico
- Nao pode formar ciclos no grafo de dependencias

---

## Value Objects

### StoryPoint

Representa pontos de historia na escala Fibonacci restrita.

```python
from enum import IntEnum

class StoryPoint(IntEnum):
    """Escala Fibonacci para estimativa de historias."""
    SMALL = 3
    MEDIUM = 5
    LARGE = 8
    EXTRA_LARGE = 13
```

### StoryStatus

Estados possiveis no workflow de uma historia.

```python
from enum import StrEnum

class StoryStatus(StrEnum):
    """Estados do workflow de uma historia."""
    BACKLOG = "BACKLOG"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
```

---

## Relacionamentos

```
┌─────────────┐       ┌─────────────┐
│  Developer  │       │   Feature   │
│─────────────│       │─────────────│
│ id (PK)     │       │ id (PK)     │
│ name        │       │ name (UQ)   │
└──────┬──────┘       │ wave (UQ)   │
       │              └──────┬──────┘
       │ 0..1                │ 0..1
       │                     │
       ▼                     ▼
┌─────────────────────────────────────┐
│              Story                  │
│─────────────────────────────────────│
│ id (PK)                             │
│ component                           │
│ name                                │
│ story_points                        │
│ priority                            │
│ status                              │
│ duration                            │
│ start_date                          │
│ end_date                            │
│ developer_id (FK) ──────────────────┘
│ feature_id (FK) ────────────────────┘
└───────────────┬─────────────────────┘
                │
                │ N:M (auto-referencia)
                │
                ▼
┌─────────────────────────────────────┐
│         Story_Dependency            │
│─────────────────────────────────────│
│ story_id (FK, PK)                   │
│ depends_on_id (FK, PK)              │
└─────────────────────────────────────┘
```

---

## Schema SQLite

```sql
-- Schema: EP-001 Fundacao e Persistencia
-- Versao: 001
-- Data: 2026-02-28

PRAGMA foreign_keys = ON;

-- Tabela Developer
CREATE TABLE IF NOT EXISTS Developer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL
);

-- Tabela Feature
CREATE TABLE IF NOT EXISTS Feature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    wave INTEGER NOT NULL UNIQUE CHECK (wave > 0)
);

-- Tabela Story
CREATE TABLE IF NOT EXISTS Story (
    id VARCHAR(20) PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    story_points INTEGER NOT NULL CHECK (story_points IN (3, 5, 8, 13)),
    priority INTEGER NOT NULL CHECK (priority >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'BACKLOG',
    duration INTEGER,
    start_date DATE,
    end_date DATE,
    developer_id INTEGER REFERENCES Developer(id) ON DELETE SET NULL,
    feature_id INTEGER REFERENCES Feature(id) ON DELETE SET NULL
);

-- Tabela Story_Dependency
CREATE TABLE IF NOT EXISTS Story_Dependency (
    story_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    depends_on_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    PRIMARY KEY (story_id, depends_on_id),
    CHECK (story_id != depends_on_id)
);

-- Indices para performance
CREATE INDEX IF NOT EXISTS idx_story_status ON Story(status);
CREATE INDEX IF NOT EXISTS idx_story_developer ON Story(developer_id);
CREATE INDEX IF NOT EXISTS idx_story_feature ON Story(feature_id);
CREATE INDEX IF NOT EXISTS idx_story_priority ON Story(priority);
```

---

## Regras de Integridade Referencial

| Relacionamento | ON DELETE | ON UPDATE |
|----------------|-----------|-----------|
| Story.developer_id -> Developer.id | SET NULL | CASCADE |
| Story.feature_id -> Feature.id | SET NULL | CASCADE |
| Story_Dependency.story_id -> Story.id | CASCADE | CASCADE |
| Story_Dependency.depends_on_id -> Story.id | CASCADE | CASCADE |

---

## Validacoes de Negocio (Domain Layer)

### Story

```python
def __post_init__(self) -> None:
    """Valida invariantes da entidade Story."""
    if not self.id or not self.id.strip():
        raise ValueError("ID da historia nao pode ser vazio")

    if not re.match(r"^[A-Z]+-\d{3}$", self.id):
        raise ValueError(f"ID deve seguir padrao COMPONENTE-NNN: {self.id}")

    if not self.component or not self.component.strip():
        raise ValueError("Componente nao pode ser vazio")

    if not self.name or not self.name.strip():
        raise ValueError("Nome da historia nao pode ser vazio")

    if self.story_points not in (3, 5, 8, 13):
        raise ValueError(f"Story points deve ser 3, 5, 8 ou 13: {self.story_points}")

    if self.priority < 0:
        raise ValueError(f"Prioridade deve ser >= 0: {self.priority}")

    if self.start_date and self.end_date and self.start_date > self.end_date:
        raise ValueError("Data de inicio nao pode ser posterior a data de termino")
```

### Developer

```python
def __post_init__(self) -> None:
    """Valida invariantes da entidade Developer."""
    if not self.name or not self.name.strip():
        raise ValueError("Nome do desenvolvedor nao pode ser vazio")

    if len(self.name) > 100:
        raise ValueError("Nome do desenvolvedor nao pode exceder 100 caracteres")
```

### Feature

```python
def __post_init__(self) -> None:
    """Valida invariantes da entidade Feature."""
    if not self.name or not self.name.strip():
        raise ValueError("Nome da feature nao pode ser vazio")

    if len(self.name) > 100:
        raise ValueError("Nome da feature nao pode exceder 100 caracteres")

    if self.wave <= 0:
        raise ValueError(f"Wave deve ser > 0: {self.wave}")
```

---

## Indices de Performance

| Indice | Colunas | Justificativa |
|--------|---------|---------------|
| idx_story_status | Story.status | Filtragem frequente por status (BACKLOG, IN_PROGRESS) |
| idx_story_developer | Story.developer_id | Join com Developer, filtragem por desenvolvedor |
| idx_story_feature | Story.feature_id | Join com Feature, filtragem por wave |
| idx_story_priority | Story.priority | Ordenacao por prioridade no backlog |

---

## Consideracoes de Migracao

1. **Versionamento**: Cada alteracao de schema gera novo arquivo em `migrations/`
2. **Nomenclatura**: `VXX_descricao.sql` onde XX e numero sequencial
3. **Rollback**: Cada migracao deve ter script de rollback correspondente
4. **Automatica**: Migracoes executam automaticamente na inicializacao
