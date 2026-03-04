# Data Model: Corrigir Bugs de Inicialização

**Feature**: 011-fix-startup-bugs
**Date**: 2026-03-04

## Resumo

Esta feature é uma correção de bugs que não introduz novas entidades ou modificações no modelo de dados. O schema existente permanece inalterado.

## Entidades Existentes (Sem Mudanças)

As seguintes entidades já existem e são utilizadas pela feature:

| Entidade | Tabela | Descrição |
|----------|--------|-----------|
| Story | `Story` | Histórias do backlog |
| Developer | `Developer` | Desenvolvedores |
| Feature | `Feature` | Features/ondas |
| Story_Dependency | `Story_Dependency` | Dependências entre histórias |

## Schema Existente

O schema está definido em `src/backlog_manager/infrastructure/database/schema.sql`:

```sql
CREATE TABLE IF NOT EXISTS Developer (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Feature (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    wave INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Story (
    id TEXT PRIMARY KEY,
    component TEXT NOT NULL,
    name TEXT NOT NULL,
    story_points INTEGER NOT NULL,
    priority INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'not_started',
    duration REAL,
    start_date TEXT,
    end_date TEXT,
    developer_id TEXT REFERENCES Developer(id),
    feature_id TEXT REFERENCES Feature(id)
);

CREATE TABLE IF NOT EXISTS Story_Dependency (
    story_id TEXT NOT NULL REFERENCES Story(id),
    depends_on_id TEXT NOT NULL REFERENCES Story(id),
    PRIMARY KEY (story_id, depends_on_id)
);
```

## Função init_database()

A função que inicializa o banco já existe em `sqlite_connection.py`:

```python
async def init_database(db_path: str | Path | None = None) -> None:
    """Initialize database with schema.

    Creates all tables if they don't exist.
    """
    schema = _SCHEMA_PATH.read_text(encoding="utf-8")

    conn = await create_connection(db_path)
    try:
        await conn.executescript(schema)
        await conn.commit()
    finally:
        await conn.close()
```

## Impacto no Modelo de Dados

| Aspecto | Impacto |
|---------|---------|
| Novas tabelas | Nenhuma |
| Alteração de schema | Nenhuma |
| Migrações | Nenhuma necessária |
| Compatibilidade | 100% compatível com dados existentes |

## Conclusão

Esta feature não requer mudanças no modelo de dados. A correção envolve apenas garantir que o schema existente seja executado na inicialização da aplicação.
