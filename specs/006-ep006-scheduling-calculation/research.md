# Research: EP-006 Calculo de Cronograma

**Feature Branch**: `006-ep006-scheduling-calculation`
**Date**: 2026-03-02

## Pesquisa e Decisoes

### 1. Kahn's Algorithm para Ordenacao Topologica

**Decisao**: Usar Kahn's algorithm com min-heap (heapq) para desempate por prioridade

**Justificativa**:
- Complexidade O(V log V + E) - eficiente para backlogs de ate 500 historias
- heapq do Python fornece min-heap nativo, ideal para prioridade (menor = mais prioritario)
- Algoritmo iterativo evita stack overflow (vs DFS recursivo)
- Detecta ciclos naturalmente: se resultado tem menos vertices que entrada, ha ciclo

**Alternativas consideradas**:
1. DFS com ordenacao pos-visita - Requer stack recursivo, risco de overflow para grafos grandes
2. Kahn's com sort posterior - Menos eficiente, O(V log V) adicional no final
3. Biblioteca externa (NetworkX) - Dependencia adicional desnecessaria para algoritmo simples

**Implementacao**:
```python
import heapq
from typing import Sequence

def topological_sort(stories: Sequence[Story], graph: dict[str, list[str]]) -> list[Story]:
    # story_id -> [depends_on_ids] (grafo de adjacencia)
    in_degree: dict[str, int] = {s.id: 0 for s in stories}
    story_map: dict[str, Story] = {s.id: s for s in stories}

    # Construir grafo reverso (dependente -> dependencias)
    for story_id, deps in graph.items():
        for dep_id in deps:
            if dep_id in in_degree:
                in_degree[story_id] += 1

    # Heap: (priority, story_id) - menor prioridade primeiro
    heap = [(s.priority, s.id) for s in stories if in_degree[s.id] == 0]
    heapq.heapify(heap)

    result: list[Story] = []
    while heap:
        _, story_id = heapq.heappop(heap)
        result.append(story_map[story_id])

        # Decrementar in_degree de dependentes
        for s in stories:
            if story_id in graph.get(s.id, []):
                in_degree[s.id] -= 1
                if in_degree[s.id] == 0:
                    heapq.heappush(heap, (s.priority, s.id))

    if len(result) != len(stories):
        raise CyclicDependencyException(...)

    return result
```

---

### 2. Calculo de Dias Uteis

**Decisao**: Algoritmo iterativo simples contando dias um a um

**Justificativa**:
- Para duracoes tipicas (1-20 dias uteis), performance e mais que suficiente
- Codigo claro e facil de entender/manter
- Evita complexidade de formulas de calendario

**Alternativas consideradas**:
1. Biblioteca workalendar - Dependencia adicional, feriados podem diferir da lista hardcoded
2. Formula matematica direta - Complexa, propensa a erros com feriados
3. Pre-calcular lookup table de dias uteis - Over-engineering para o caso de uso

**Implementacao**:
```python
from datetime import date, timedelta

def add_workdays(start_date: date, workdays: int, holidays: frozenset[date]) -> date:
    if workdays < 1:
        return start_date

    current = start_date
    days_counted = 1  # start_date conta como dia 1

    while days_counted < workdays:
        current += timedelta(days=1)
        if is_workday(current, holidays):
            days_counted += 1

    return current

def is_workday(d: date, holidays: frozenset[date]) -> bool:
    return d.weekday() < 5 and d not in holidays
```

---

### 3. Estrutura de Feriados Brasileiros

**Decisao**: frozenset[date] com todas as datas de 2026-2028 hardcoded

**Justificativa**:
- frozenset permite lookup O(1)
- Imutavel, thread-safe
- Lista estatica conforme SRS Apendice A - evita calculo de feriados moveis
- 3 anos de dados sao suficientes para o escopo da aplicacao

**Alternativas consideradas**:
1. Calcular feriados moveis (Pascoa, Carnaval, Corpus Christi) via formula - Complexidade desnecessaria
2. Usar biblioteca holidays - Dependencia externa, pode ter datas diferentes
3. Banco de dados de feriados - Over-engineering para dados estaticos

**Dados**:
- 2026: 13 feriados nacionais
- 2027: 13 feriados nacionais
- 2028: 13 feriados nacionais
- Total: 39 datas em frozenset

---

### 4. Formula de Duracao

**Decisao**: `ceil(story_points / velocity)` com minimo de 1 dia

**Justificativa**:
- Formula simples e intuitiva
- ceil() garante que fracao de dia seja arredondada para cima
- Minimo de 1 dia evita duracao zero para SP < velocity

**Implementacao**:
```python
import math

def calculate_duration(story_points: int, velocity: float) -> int:
    if velocity <= 0:
        raise ValueError("Velocidade deve ser maior que zero")
    return max(1, math.ceil(story_points / velocity))
```

---

### 5. Integracao com DependencyService (EP-005)

**Decisao**: Reutilizar DependencyService.build_graph() do EP-005

**Justificativa**:
- DRY: nao duplicar logica de construcao de grafo
- Grafo ja testado e funcionando
- Consistencia de formato de dados

**Integracao**:
```python
# No CalculateScheduleUseCase
dependencies = await uow.dependencies.get_all_dependencies()
graph = DependencyService.build_graph(dependencies)
# graph: dict[str, list[str]] - story_id -> [depends_on_ids]
```

---

### 6. Tratamento de Erros e Warnings

**Decisao**: Usar CyclicDependencyException existente + warnings no OutputDTO

**Justificativa**:
- Ciclos sao erros fatais que impedem calculo - usar excecao
- Situacoes nao-fatais (historia sem SP, dependencia sem data) - usar warnings
- Consistente com padrao de tratamento de erros da aplicacao

**Warnings identificados**:
1. Historia com story_points invalido/ausente - "Historia {id} ignorada: story_points invalido"
2. Dependencia sem end_date - "Dependencia {id} sem data: usando project_start_date"
3. Backlog vazio - "Nenhuma historia elegivel encontrada no backlog"

---

### 7. Transacionalidade

**Decisao**: UnitOfWork garante atomicidade via context manager

**Justificativa**:
- Multiplas historias atualizadas em uma operacao
- Falha deve reverter todas as alteracoes
- UnitOfWork existente ja implementa commit/rollback

**Implementacao**:
```python
async with uow:
    # Calcular datas para todas as historias
    for story in sorted_stories:
        story.start_date = calculated_start
        story.end_date = calculated_end
        story.duration = calculated_duration
        await uow.stories.update(story)
    # Auto-commit no exit do context manager
```

---

## Decisoes Arquiteturais Confirmadas

| Aspecto | Decisao | Referencia |
|---------|---------|------------|
| Domain Service | SchedulingService stateless, metodos estaticos | ADR-001 (spec.md) |
| Feriados | frozenset hardcoded 2026-2028 | ADR-002 (spec.md) |
| Velocity | Recebido como parametro do use case | ADR-003 (spec.md) |
| Contagem de dias | start_date conta como dia 1 | ADR-004 (spec.md) |
| Ordenacao | Kahn's algorithm com heap | ADR-005 (spec.md) |
| Persistencia | Use case retorna datas, persiste via UnitOfWork | ADR-006 (spec.md) |
| Ajuste start_date projeto | Automatico para proximo dia util | ADR-007 (spec.md) |
| Recalculo | Parametro recalculate_all controla comportamento | ADR-008 (spec.md) |
| Grafo de dependencias | Reutiliza DependencyService.build_graph() | ADR-009 (spec.md) |

## Proximos Passos

1. **data-model.md**: Documentar entidades e value objects
2. **contracts/**: Definir interfaces publicas (se aplicavel)
3. **quickstart.md**: Exemplo de uso do SchedulingService
