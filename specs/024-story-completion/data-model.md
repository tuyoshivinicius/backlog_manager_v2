# Data Model: Story Completion Status

**Feature**: 024-story-completion
**Date**: 2026-03-30

## Entidades Existentes (sem alteração de schema)

### Story

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | VARCHAR(20) PK | Identificador único |
| name | VARCHAR(200) | Nome da história |
| status | VARCHAR(20) | Estado: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO |
| story_points | INTEGER | Pontos de esforço |
| developer_id | VARCHAR(20) FK | Desenvolvedor alocado (nullable) |
| start_date | DATE | Data início calculada (nullable) |
| end_date | DATE | Data fim calculada (nullable) |
| feature_id | INTEGER FK | Feature associada (nullable) |
| duration | INTEGER | Duração em dias (nullable) |
| priority | INTEGER | Ordem de prioridade |

**Regras de validação para esta feature**:
- Transição para `CONCLUIDO`: todas as dependências diretas devem estar em `CONCLUIDO`
- Transição de `CONCLUIDO` para qualquer outro status: sem restrições
- Ao ser marcada como `CONCLUIDO`: preserva developer_id, start_date, end_date (FR-005)

### Story_Dependency

| Campo | Tipo | Descrição |
|-------|------|-----------|
| story_id | VARCHAR(20) PK, FK | História que depende |
| depends_on_id | VARCHAR(20) PK, FK | História da qual depende |

**Constraint**: `CHECK (story_id != depends_on_id)` — sem auto-dependência.

**Uso nesta feature**: Para validar conclusão, busca-se `get_dependencies(story_id)` → retorna lista de `depends_on_id`. Para cada dependência, verifica-se `story.status == CONCLUIDO`.

## Nova Exceção de Domínio

### IncompleteDependencyException

```python
class IncompleteDependencyException(DependencyException):
    """Dependências incompletas impedem conclusão da história."""

    story_id: str                                    # História que tentou ser concluída
    incomplete_dependencies: list[tuple[str, str, str]]  # [(id, name, status), ...]
```

**Transições de estado relevantes**:

```
Qualquer Status ──→ CONCLUIDO
    GATE: todas dependências diretas em CONCLUIDO
    REJECT: IncompleteDependencyException com lista de bloqueadoras

CONCLUIDO ──→ Qualquer Status
    GATE: nenhum (livre)
    SIDE EFFECT: nenhum cascateamento
```

## Impacto em Processos Existentes

### CalculateScheduleUseCase
- **Filtro existente**: `if story.status != StoryStatus.BACKLOG: continue`
- **Impacto**: Nenhum — CONCLUIDO já é excluído pelo filtro existente

### AllocationService._is_eligible()
- **Filtro atual**: developer_id == None AND start_date != None AND end_date != None AND story_points != None
- **Alteração**: Adicionar `AND story.status != StoryStatus.CONCLUIDO`
- **Impacto**: Histórias concluídas não serão re-alocadas
