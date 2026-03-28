# Contract: SchedulingService

**Module**: `backlog_manager.domain.services.scheduling_service`
**Type**: Domain Service (stateless, static methods)

## Overview

Domain service responsavel por calculos de cronograma. Todos os metodos sao estaticos e nao possuem efeitos colaterais (side effects). Dados sao passados como parametros.

---

## Methods

### calculate_duration

Calcula a duracao de uma historia em dias uteis baseado em story points e velocidade.

**Signature**:
```python
@staticmethod
def calculate_duration(story_points: int, velocity: float) -> int
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| story_points | int | Yes | Story points da historia (3, 5, 8 ou 13) |
| velocity | float | Yes | Velocidade da equipe em SP/dia |

**Returns**: `int` - Duracao em dias uteis (minimo 1)

**Raises**:
- `ValueError`: Se velocity <= 0 com mensagem "Velocidade deve ser maior que zero"

**Formula**: `max(1, ceil(story_points / velocity))`

**Examples**:
```python
# Caso normal
SchedulingService.calculate_duration(5, 2.0)  # Returns: 3

# Duracao minima
SchedulingService.calculate_duration(3, 5.0)  # Returns: 1

# Divisao exata
SchedulingService.calculate_duration(8, 4.0)  # Returns: 2

# Velocity invalida
SchedulingService.calculate_duration(5, 0)    # Raises: ValueError
```

---

### is_workday

Verifica se uma data e dia util (segunda a sexta, nao feriado).

**Signature**:
```python
@staticmethod
def is_workday(d: date, holidays: frozenset[date]) -> bool
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| d | date | Yes | Data a verificar |
| holidays | frozenset[date] | Yes | Conjunto de feriados |

**Returns**: `bool` - True se dia util, False caso contrario

**Logic**:
1. Se weekday >= 5 (sabado ou domingo): False
2. Se d in holidays: False
3. Caso contrario: True

**Examples**:
```python
holidays = BRAZILIAN_HOLIDAYS_2026_2028

# Segunda-feira
SchedulingService.is_workday(date(2026, 3, 2), holidays)   # Returns: True

# Sabado
SchedulingService.is_workday(date(2026, 3, 7), holidays)   # Returns: False

# Feriado (Tiradentes)
SchedulingService.is_workday(date(2026, 4, 21), holidays)  # Returns: False
```

---

### next_workday

Retorna o proximo dia util a partir de uma data (inclusive).

**Signature**:
```python
@staticmethod
def next_workday(d: date, holidays: frozenset[date]) -> date
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| d | date | Yes | Data de inicio |
| holidays | frozenset[date] | Yes | Conjunto de feriados |

**Returns**: `date` - Proximo dia util (d se ja for dia util)

**Logic**:
1. Se is_workday(d): retorna d
2. Avanca d += 1 dia ate encontrar dia util

**Examples**:
```python
holidays = BRAZILIAN_HOLIDAYS_2026_2028

# Ja e dia util
SchedulingService.next_workday(date(2026, 3, 2), holidays)   # Returns: 2026-03-02

# Sabado -> Segunda
SchedulingService.next_workday(date(2026, 3, 7), holidays)   # Returns: 2026-03-09

# Feriado -> Proximo dia util
SchedulingService.next_workday(date(2026, 4, 21), holidays)  # Returns: 2026-04-22
```

---

### add_workdays

Avanca N dias uteis a partir de uma data. A data de inicio conta como dia 1.

**Signature**:
```python
@staticmethod
def add_workdays(start_date: date, workdays: int, holidays: frozenset[date]) -> date
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| start_date | date | Yes | Data de inicio (deve ser dia util) |
| workdays | int | Yes | Numero de dias uteis a avancar (>= 1) |
| holidays | frozenset[date] | Yes | Conjunto de feriados |

**Returns**: `date` - Data apos avancar N dias uteis

**Logic**:
1. Se workdays <= 1: retorna start_date
2. current = start_date, days_counted = 1
3. Enquanto days_counted < workdays:
   - current += 1 dia
   - Se is_workday(current): days_counted += 1
4. Retorna current

**Examples**:
```python
holidays = BRAZILIAN_HOLIDAYS_2026_2028

# 2 dias na mesma semana
SchedulingService.add_workdays(date(2026, 3, 2), 2, holidays)   # Returns: 2026-03-03

# 2 dias pulando fim de semana
SchedulingService.add_workdays(date(2026, 3, 6), 2, holidays)   # Returns: 2026-03-09

# 2 dias pulando feriado (Tiradentes 21/04)
SchedulingService.add_workdays(date(2026, 4, 20), 2, holidays)  # Returns: 2026-04-22

# CT-004: 4 dias pulando Sexta-Santa + fim de semana
SchedulingService.add_workdays(date(2026, 4, 1), 4, holidays)   # Returns: 2026-04-07
```

---

### count_workdays_between

Conta o numero de dias uteis entre duas datas (exclusivo em ambos os extremos).

**Signature**:
```python
@staticmethod
def count_workdays_between(start_date: date, end_date: date, holidays: frozenset[date]) -> int
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| start_date | date | Yes | Data inicial (exclusiva) |
| end_date | date | Yes | Data final (exclusiva) |
| holidays | frozenset[date] | Yes | Conjunto de feriados |

**Returns**: `int` - Numero de dias uteis entre as datas

**Examples**:
```python
holidays = BRAZILIAN_HOLIDAYS_2026_2028

# 3 dias uteis entre 02/03 e 06/03
SchedulingService.count_workdays_between(date(2026, 3, 2), date(2026, 3, 6), holidays)  # Returns: 3
```

---

### topological_sort

Ordena historias topologicamente usando Kahn's algorithm com desempate por prioridade.

**Signature**:
```python
@staticmethod
def topological_sort(
    stories: Sequence[Story],
    dependencies: dict[str, list[str]]
) -> list[Story]
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| stories | Sequence[Story] | Yes | Lista de historias a ordenar |
| dependencies | dict[str, list[str]] | Yes | Grafo: story_id -> [depends_on_ids] |

**Returns**: `list[Story]` - Historias ordenadas topologicamente

**Raises**:
- `CyclicDependencyException`: Se ciclo detectado no grafo

**Logic**:
1. Construir in_degree para cada historia
2. Inicializar min-heap com historias de in_degree=0
3. Extrair historia com menor prioridade do heap
4. Decrementar in_degree de dependentes
5. Inserir dependentes com in_degree=0 no heap
6. Se resultado incompleto: ciclo detectado

**Complexity**: O(V log V + E)

**Examples**:
```python
# Cadeia linear: A -> B -> C
stories = [story_a, story_b, story_c]
deps = {"FEAT-002": ["FEAT-001"], "FEAT-003": ["FEAT-002"]}
result = SchedulingService.topological_sort(stories, deps)
# Returns: [story_a, story_b, story_c]

# Desempate por prioridade
stories = [story_a_prio_2, story_b_prio_1]  # Independentes
deps = {}
result = SchedulingService.topological_sort(stories, deps)
# Returns: [story_b, story_a]  # B primeiro (menor prioridade)
```

---

### calculate_story_dates

Calcula datas de inicio, fim e duracao para uma historia.

**Signature**:
```python
@staticmethod
def calculate_story_dates(
    story: Story,
    velocity: float,
    start_date: date,
    dependency_end_dates: Sequence[date],
    holidays: frozenset[date]
) -> tuple[date, date, int]
```

**Parameters**:
| Name | Type | Required | Description |
|------|------|----------|-------------|
| story | Story | Yes | Historia a calcular |
| velocity | float | Yes | Velocidade em SP/dia |
| start_date | date | Yes | Data de inicio do projeto |
| dependency_end_dates | Sequence[date] | Yes | Datas de fim das dependencias |
| holidays | frozenset[date] | Yes | Conjunto de feriados |

**Returns**: `tuple[date, date, int]` - (start_date, end_date, duration)

**Logic**:
1. Se dependency_end_dates nao vazio: base_date = max(dependency_end_dates) + 1 dia
2. Se vazio: base_date = start_date
3. Ajustar base_date para proximo dia util
4. Calcular duracao via calculate_duration
5. Calcular end_date via add_workdays
6. Retornar (base_date, end_date, duration)

**Examples**:
```python
holidays = BRAZILIAN_HOLIDAYS_2026_2028

# Historia sem dependencias
result = SchedulingService.calculate_story_dates(
    story=story_5sp,
    velocity=2.0,
    start_date=date(2026, 3, 2),
    dependency_end_dates=[],
    holidays=holidays
)
# Returns: (date(2026, 3, 2), date(2026, 3, 4), 3)

# Historia com dependencia terminando na sexta
result = SchedulingService.calculate_story_dates(
    story=story_5sp,
    velocity=2.0,
    start_date=date(2026, 3, 2),
    dependency_end_dates=[date(2026, 3, 6)],  # Sexta
    holidays=holidays
)
# Returns: (date(2026, 3, 9), date(2026, 3, 11), 3)  # Comeca segunda
```
