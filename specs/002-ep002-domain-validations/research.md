# Research: EP-002 Dominio Core - Entidades e Validacoes

**Date**: 2026-02-28
**Status**: Complete

## Overview

Este documento consolida as decisoes de pesquisa para EP-002, focando na analise do codigo existente (EP-001) e nas mudancas necessarias para alinhar com o SRS.

## Research Tasks

### 1. StoryStatus: Mudanca de 4 para 5 Estados

**Contexto**: O codigo atual usa 4 estados em ingles (BACKLOG, IN_PROGRESS, BLOCKED, DONE). O SRS 6.5 especifica 5 estados em portugues (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO).

**Decision**: Alterar StoryStatus para os 5 estados do SRS 6.5.

**Rationale**:
- SRS e a especificacao oficial do sistema
- Interface sera em portugues brasileiro
- Valores em maiusculas sem acentos para compatibilidade com banco de dados
- Novo estado TESTES representa fase importante do workflow

**Alternatives Considered**:
- Manter estados em ingles: Rejeitado - inconsistente com SRS e interface PT-BR
- Usar acentos (EXECUÇÃO): Rejeitado - problemas de encoding em SQLite

**Migration Strategy**:
| Estado Atual | Novo Estado |
|--------------|-------------|
| BACKLOG | BACKLOG |
| IN_PROGRESS | EXECUCAO |
| BLOCKED | IMPEDIDO |
| DONE | CONCLUIDO |
| (novo) | TESTES |

### 2. Story.duration: Validacao de Valores Negativos

**Contexto**: O campo `duration` atual nao tem validacao de valores negativos. O SRS 8.3 implica duracao minima de 1 dia para historias executadas.

**Decision**: Adicionar validacao `duration >= 0` no `__post_init__` da entidade Story.

**Rationale**:
- duration = None: historia nao calculada (valido)
- duration = 0: estado intermediario ou historia sem duracao definida (valido)
- duration < 0: valor invalido (reject)
- Regra de duracao minima 1 dia aplica-se no CALCULO de cronograma, nao na entidade

**Alternatives Considered**:
- Validar duration >= 1: Rejeitado - impediria representar historias nao calculadas
- Sem validacao: Rejeitado - permite dados inconsistentes

### 3. Auto-dependencia no Repositorio

**Contexto**: A spec FR-020/FR-021 exige que auto-dependencia (story_id == depends_on_id) seja rejeitada.

**Decision**: Adicionar validacao no metodo `add()` do `SQLiteStoryDependencyRepository`.

**Rationale**:
- Entidade Story NAO possui campo `dependencies` (gerenciado na tabela Story_Dependency)
- Validacao deve ocorrer no momento de adicionar dependencia
- Repositorio ja e responsavel por operacoes na tabela Story_Dependency
- Mantem entidade Story focada em seus proprios invariantes

**Alternatives Considered**:
- Validar na entidade Story: Rejeitado - Story nao tem campo dependencies
- Validar em Use Case: Rejeitado - duplicaria logica ja presente no repositorio

### 4. Validacoes Existentes vs Novas

**Contexto**: Analise do codigo EP-001 para identificar quais validacoes ja existem.

**Decision**: Documentar estado atual e gaps.

#### Story Entity - Estado Atual (EP-001):
| Validacao | Status | Acao EP-002 |
|-----------|--------|-------------|
| id vazio | ✅ Implementado | Nenhuma |
| id padrao COMPONENTE-NNN | ✅ Implementado | Nenhuma |
| component vazio | ✅ Implementado | Nenhuma |
| component > 50 chars | ✅ Implementado | Nenhuma |
| name vazio | ✅ Implementado | Nenhuma |
| name > 200 chars | ✅ Implementado | Nenhuma |
| story_points Fibonacci | ✅ Implementado | Nenhuma |
| priority >= 0 | ✅ Implementado | Nenhuma |
| start_date <= end_date | ✅ Implementado | Nenhuma |
| duration >= 0 | ❌ Faltando | Adicionar |

#### Developer Entity - Estado Atual (EP-001):
| Validacao | Status | Acao EP-002 |
|-----------|--------|-------------|
| name vazio | ✅ Implementado | Nenhuma |
| name > 100 chars | ✅ Implementado | Nenhuma |

#### Feature Entity - Estado Atual (EP-001):
| Validacao | Status | Acao EP-002 |
|-----------|--------|-------------|
| name vazio | ✅ Implementado | Nenhuma |
| name > 100 chars | ✅ Implementado | Nenhuma |
| wave > 0 | ✅ Implementado | Nenhuma |

#### StoryDependencyRepository - Estado Atual (EP-001):
| Validacao | Status | Acao EP-002 |
|-----------|--------|-------------|
| auto-dependencia | ❌ Faltando | Adicionar |

### 5. Padrao de Mensagens de Erro

**Decision**: Manter padrao existente de mensagens em portugues sem acentos.

**Rationale**:
- Consistente com Constitution Principio XV (Idioma)
- Evita problemas de encoding
- Mensagens ja usam este padrao em EP-001

**Formato padrao**:
```python
raise ValueError("Descricao do problema: valor_invalido")
# Exemplo: "Duracao deve ser >= 0: -1"
```

## Gaps Identificados

| Gap | Arquivo | Mudanca Necessaria |
|-----|---------|-------------------|
| StoryStatus 4->5 estados | story_status.py | Alterar enum |
| duration >= 0 | story.py | Adicionar validacao |
| auto-dependencia | story_dependency_repository.py | Adicionar validacao |

## Testes Necessarios

### Unit Tests (domain/):
- test_story_status.py: Verificar 5 estados
- test_story.py: Adicionar teste duration negativo
- test_developer.py: Testes existentes suficientes
- test_feature.py: Testes existentes suficientes

### Integration Tests (infrastructure/):
- test_story_dependency_repository.py: Adicionar teste auto-dependencia

## Conclusao

A maior parte das validacoes especificadas em EP-002 ja foi implementada em EP-001. As mudancas necessarias sao:

1. **StoryStatus**: Mudanca de 4 para 5 estados (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)
2. **Story.duration**: Adicionar validacao `duration >= 0`
3. **StoryDependencyRepository**: Adicionar validacao de auto-dependencia

Todas as outras validacoes especificadas (ID, component, name, story_points, priority, dates, developer name, feature name/wave) ja estao implementadas e testadas.
