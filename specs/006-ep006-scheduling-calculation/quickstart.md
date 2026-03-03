# Quickstart: EP-006 Calculo de Cronograma

**Feature Branch**: `006-ep006-scheduling-calculation`
**Date**: 2026-03-02

## Uso Rapido

### 1. Calcular Cronograma Completo

```python
from datetime import date
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork
from backlog_manager.application.use_cases.scheduling import CalculateScheduleUseCase
from backlog_manager.application.dto.scheduling import CalculateScheduleInputDTO

async def calculate_full_schedule():
    async with SQLiteUnitOfWork() as uow:
        use_case = CalculateScheduleUseCase(uow)

        result = await use_case.execute(
            CalculateScheduleInputDTO(
                velocity=2.0,  # 2 story points por dia
                start_date=date(2026, 3, 2)  # Data de inicio do projeto
            )
        )

        print(f"Sucesso: {result.success}")
        print(f"Historias processadas: {result.stories_processed}")
        print(f"Historias atualizadas: {result.stories_updated}")

        if result.warnings:
            print("Avisos:")
            for warning in result.warnings:
                print(f"  - {warning}")
```

### 2. Calcular Duracao de Uma Historia

```python
from backlog_manager.application.use_cases.scheduling import CalculateDurationUseCase
from backlog_manager.application.dto.scheduling import CalculateDurationInputDTO

async def calculate_story_duration():
    use_case = CalculateDurationUseCase()

    result = await use_case.execute(
        CalculateDurationInputDTO(
            story_points=5,
            velocity=2.0
        )
    )

    print(f"Duracao: {result.duration} dias uteis")
    print(f"Formula: {result.formula}")
    # Output:
    # Duracao: 3 dias uteis
    # Formula: ceil(5 / 2.0) = 3
```

### 3. Calcular Datas de Uma Historia Especifica

```python
from datetime import date
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork
from backlog_manager.application.use_cases.scheduling import CalculateStoryDatesUseCase
from backlog_manager.application.dto.scheduling import CalculateStoryDatesInputDTO

async def calculate_story_dates():
    async with SQLiteUnitOfWork() as uow:
        use_case = CalculateStoryDatesUseCase(uow)

        result = await use_case.execute(
            CalculateStoryDatesInputDTO(
                story_id="FEAT-001",
                velocity=2.0,
                project_start_date=date(2026, 3, 2)
            )
        )

        print(f"Historia: {result.story_id}")
        print(f"Inicio: {result.start_date}")
        print(f"Fim: {result.end_date}")
        print(f"Duracao: {result.duration} dias")
```

### 4. Usar SchedulingService Diretamente (Testes)

```python
from datetime import date
from backlog_manager.domain.services import SchedulingService
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028

# Calcular duracao
duration = SchedulingService.calculate_duration(story_points=5, velocity=2.0)
print(f"Duracao: {duration} dias")  # 3 dias

# Verificar se e dia util
is_workday = SchedulingService.is_workday(
    date(2026, 3, 2),  # Segunda-feira
    BRAZILIAN_HOLIDAYS_2026_2028
)
print(f"E dia util: {is_workday}")  # True

# Avancar dias uteis
end_date = SchedulingService.add_workdays(
    start_date=date(2026, 3, 2),
    workdays=3,
    holidays=BRAZILIAN_HOLIDAYS_2026_2028
)
print(f"Data final: {end_date}")  # 2026-03-04

# Ajustar para proximo dia util
next_work = SchedulingService.next_workday(
    date(2026, 3, 7),  # Sabado
    BRAZILIAN_HOLIDAYS_2026_2028
)
print(f"Proximo dia util: {next_work}")  # 2026-03-09 (Segunda)
```

---

## Cenarios de Teste

### Cenario 1: Cronograma Simples sem Dependencias

```python
# Configuracao:
# - 3 historias: A (5 SP), B (8 SP), C (3 SP)
# - Sem dependencias
# - velocity = 2.0 SP/dia
# - start_date = 2026-03-02 (segunda)

# Resultado esperado:
# Todas iniciam em 2026-03-02
# A: 02/03 - 04/03 (3 dias)
# B: 02/03 - 05/03 (4 dias)
# C: 02/03 - 02/03 (1 dia - minimo)
```

### Cenario 2: Cadeia de Dependencias

```python
# Configuracao:
# - A (5 SP) -> B (8 SP) -> C (5 SP)
# - B depende de A, C depende de B
# - velocity = 2.0 SP/dia
# - start_date = 2026-03-02 (segunda)

# Resultado esperado:
# A: 02/03 - 04/03 (3 dias)
# B: 05/03 - 12/03 (4 dias, pula fim de semana)
# C: 13/03 - 17/03 (3 dias)
```

### Cenario 3: Feriados (CT-004)

```python
# Configuracao:
# - Historia com 4 dias de duracao
# - start_date = 2026-04-01 (quarta)
# - Feriado: 2026-04-03 (Sexta-Santa)

# Resultado esperado:
# Dias uteis: 01/04 (1), 02/04 (2), 06/04 (3), 07/04 (4)
# Pulou: 03/04 (feriado), 04-05/04 (fim de semana)
# end_date = 2026-04-07
```

### Cenario 4: Desempate por Prioridade

```python
# Configuracao:
# - A (priority=2), B (priority=1), ambos independentes
# - velocity = 2.0 SP/dia

# Resultado da ordenacao topologica:
# [B, A] - B primeiro por ter menor prioridade
```

---

## Tratamento de Erros

### Ciclo Detectado

```python
from backlog_manager.domain.exceptions import CyclicDependencyException

try:
    result = await use_case.execute(input_dto)
except CyclicDependencyException as e:
    print(f"Ciclo detectado: {' -> '.join(e.path)}")
    # Ciclo detectado: FEAT-001 -> FEAT-002 -> FEAT-003 -> FEAT-001
```

### Velocity Invalida

```python
try:
    duration = SchedulingService.calculate_duration(5, 0)
except ValueError as e:
    print(f"Erro: {e}")
    # Erro: Velocidade deve ser maior que zero
```

### Historia com SP Invalido

```python
# Historias com story_points None ou fora de {3, 5, 8, 13}
# sao ignoradas e geram warning no OutputDTO

result = await use_case.execute(input_dto)
for warning in result.warnings:
    print(warning)
# Historia FEAT-005 ignorada: story_points invalido ou ausente
```

---

## Imports

```python
# Domain Services
from backlog_manager.domain.services import SchedulingService

# Value Objects
from backlog_manager.domain.value_objects import BRAZILIAN_HOLIDAYS_2026_2028
from backlog_manager.domain.value_objects import get_holidays_for_year

# Use Cases
from backlog_manager.application.use_cases.scheduling import (
    CalculateScheduleUseCase,
    CalculateDurationUseCase,
    CalculateStoryDatesUseCase,
)

# DTOs
from backlog_manager.application.dto.scheduling import (
    CalculateScheduleInputDTO,
    CalculateScheduleOutputDTO,
    CalculateDurationInputDTO,
    CalculateDurationOutputDTO,
    CalculateStoryDatesInputDTO,
    CalculateStoryDatesOutputDTO,
)

# Exceptions
from backlog_manager.domain.exceptions import CyclicDependencyException

# Infrastructure
from backlog_manager.infrastructure.database.unit_of_work import SQLiteUnitOfWork
```
