# Data Model: EP-002 Dominio Core - Entidades e Validacoes

**Date**: 2026-02-28
**Status**: Complete

## Overview

Este documento define o modelo de dados para EP-002, detalhando entidades, value objects, regras de validacao e relacionamentos.

## Value Objects

### StoryPoint

**Arquivo**: `src/backlog_manager/domain/value_objects/story_point.py`

```python
class StoryPoint(IntEnum):
    SMALL = 3
    MEDIUM = 5
    LARGE = 8
    EXTRA_LARGE = 13
```

**Validacoes**:
- Apenas valores {3, 5, 8, 13} sao aceitos
- Conversao automatica de int para enum na entidade Story

**Status EP-002**: ✅ Sem mudancas necessarias

---

### StoryStatus

**Arquivo**: `src/backlog_manager/domain/value_objects/story_status.py`

**Estado Atual (EP-001)**:
```python
class StoryStatus(StrEnum):
    BACKLOG = "BACKLOG"
    IN_PROGRESS = "IN_PROGRESS"
    BLOCKED = "BLOCKED"
    DONE = "DONE"
```

**Estado Alvo (EP-002)**:
```python
class StoryStatus(StrEnum):
    BACKLOG = "BACKLOG"
    EXECUCAO = "EXECUCAO"
    TESTES = "TESTES"
    CONCLUIDO = "CONCLUIDO"
    IMPEDIDO = "IMPEDIDO"
```

**Transicoes**: Modelo flexivel - todas as transicoes sao permitidas conforme SRS 6.5.

**Status EP-002**: ⚠️ MUDANCA NECESSARIA - 4 para 5 estados

---

## Entities

### Story

**Arquivo**: `src/backlog_manager/domain/entities/story.py`

**Campos**:

| Campo | Tipo | Obrigatorio | Default | Validacoes |
|-------|------|-------------|---------|------------|
| id | str | Sim | - | Nao vazio, padrao `^[A-Z]+-\d{3}$` |
| component | str | Sim | - | Nao vazio, max 50 chars |
| name | str | Sim | - | Nao vazio, max 200 chars |
| story_points | StoryPoint \| int | Sim | - | Valores {3, 5, 8, 13} |
| priority | int | Sim | - | >= 0 |
| status | StoryStatus | Nao | BACKLOG | Enum valido |
| duration | int \| None | Nao | None | >= 0 quando definido |
| start_date | date \| None | Nao | None | <= end_date quando ambos definidos |
| end_date | date \| None | Nao | None | >= start_date quando ambos definidos |
| developer_id | int \| None | Nao | None | FK para Developer |
| feature_id | int \| None | Nao | None | FK para Feature |

**Validacoes no `__post_init__`**:

| Validacao | Mensagem de Erro | Status EP-002 |
|-----------|------------------|---------------|
| id vazio | "ID da historia nao pode ser vazio" | ✅ Existente |
| id formato | "ID deve seguir padrao COMPONENTE-NNN: {id}" | ✅ Existente |
| component vazio | "Componente nao pode ser vazio" | ✅ Existente |
| component > 50 | "Componente nao pode exceder 50 caracteres" | ✅ Existente |
| name vazio | "Nome da historia nao pode ser vazio" | ✅ Existente |
| name > 200 | "Nome da historia nao pode exceder 200 caracteres" | ✅ Existente |
| story_points invalido | "Story points deve ser 3, 5, 8 ou 13: {value}" | ✅ Existente |
| priority < 0 | "Prioridade deve ser >= 0: {value}" | ✅ Existente |
| start > end | "Data de inicio nao pode ser posterior a data de termino" | ✅ Existente |
| duration < 0 | "Duracao deve ser >= 0: {value}" | ⚠️ ADICIONAR |

**Status EP-002**: ⚠️ MUDANCA NECESSARIA - Adicionar validacao duration >= 0

---

### Developer

**Arquivo**: `src/backlog_manager/domain/entities/developer.py`

**Campos**:

| Campo | Tipo | Obrigatorio | Default | Validacoes |
|-------|------|-------------|---------|------------|
| name | str | Sim | - | Nao vazio, max 100 chars |
| id | int \| None | Nao | None | Auto-incrementado |

**Validacoes no `__post_init__`**:

| Validacao | Mensagem de Erro | Status EP-002 |
|-----------|------------------|---------------|
| name vazio | "Nome do desenvolvedor nao pode ser vazio" | ✅ Existente |
| name > 100 | "Nome do desenvolvedor nao pode exceder 100 caracteres" | ✅ Existente |

**Status EP-002**: ✅ Sem mudancas necessarias

---

### Feature

**Arquivo**: `src/backlog_manager/domain/entities/feature.py`

**Campos**:

| Campo | Tipo | Obrigatorio | Default | Validacoes |
|-------|------|-------------|---------|------------|
| name | str | Sim | - | Nao vazio, max 100 chars |
| wave | int | Sim | - | > 0 |
| id | int \| None | Nao | None | Auto-incrementado |

**Validacoes no `__post_init__`**:

| Validacao | Mensagem de Erro | Status EP-002 |
|-----------|------------------|---------------|
| name vazio | "Nome da feature nao pode ser vazio" | ✅ Existente |
| name > 100 | "Nome da feature nao pode exceder 100 caracteres" | ✅ Existente |
| wave <= 0 | "Wave deve ser > 0: {value}" | ✅ Existente |

**Status EP-002**: ✅ Sem mudancas necessarias

---

## Repository Validations

### StoryDependencyRepository

**Arquivo**: `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py`

**Metodo `add()`**:

| Validacao | Mensagem de Erro | Status EP-002 |
|-----------|------------------|---------------|
| Dependencia duplicada | "Dependencia {story_id} -> {depends_on_id} ja existe" | ✅ Existente |
| Auto-dependencia | "Historia nao pode depender de si mesma" | ⚠️ ADICIONAR |

**Status EP-002**: ⚠️ MUDANCA NECESSARIA - Adicionar validacao auto-dependencia

---

## Relacionamentos

```
┌─────────────┐       ┌─────────────┐       ┌─────────────┐
│  Developer  │       │   Feature   │       │  Story      │
├─────────────┤       ├─────────────┤       ├─────────────┤
│ id (PK)     │       │ id (PK)     │       │ id (PK)     │
│ name        │       │ name        │       │ component   │
│             │       │ wave        │       │ name        │
└──────┬──────┘       └──────┬──────┘       │ story_points│
       │                     │              │ priority    │
       │  1                  │  1           │ status      │
       └──────────┬──────────┘              │ duration    │
                  │                         │ start_date  │
                  │  *                      │ end_date    │
                  └─────────────────────────│ developer_id│
                                            │ feature_id  │
                                            └──────┬──────┘
                                                   │
                                            ┌──────┴──────┐
                                            │             │
                                            ▼             ▼
                                    ┌───────────────────────────┐
                                    │   Story_Dependency        │
                                    ├───────────────────────────┤
                                    │ story_id (FK)             │
                                    │ depends_on_id (FK)        │
                                    │ PK(story_id, depends_on_id)│
                                    └───────────────────────────┘
```

---

## Resumo de Mudancas EP-002

| Arquivo | Mudanca | Prioridade |
|---------|---------|------------|
| story_status.py | 4 estados -> 5 estados (PT-BR) | P1 |
| story.py | Adicionar validacao duration >= 0 | P2 |
| story_dependency_repository.py | Adicionar validacao auto-dependencia | P2 |

---

## Migracao de Dados

### StoryStatus Migration

```sql
-- Migracao de status existentes
UPDATE Story SET status = 'EXECUCAO' WHERE status = 'IN_PROGRESS';
UPDATE Story SET status = 'IMPEDIDO' WHERE status = 'BLOCKED';
UPDATE Story SET status = 'CONCLUIDO' WHERE status = 'DONE';
-- BACKLOG permanece BACKLOG
-- TESTES e novo estado, sem dados existentes para migrar
```

**Nota**: Esta migracao deve ser executada como parte do script de inicializacao ou como migration versionada.
