# Research: EP-007 Motor de Alocacao

## 1. Padrao de Domain Service Stateless

**Decisao**: AllocationService sera implementado como classe com metodos estaticos (@staticmethod), seguindo o padrao de SchedulingService e DependencyService.

**Racional**:
- Consistente com servicos existentes no dominio (SchedulingService, DependencyService)
- Facilita testes sem necessidade de mocks
- Recebe todos os dados como parametros (sincrono, puro)
- Pode chamar SchedulingService diretamente para calculos de datas

**Alternativas Consideradas**:
1. Instancia com estado - rejeitado por violar principio stateless
2. Funcoes soltas - rejeitado por dificultar organizacao e namespace

## 2. Algoritmo de Balanceamento de Carga

**Decisao**: Balanceamento por contagem de historias (LOAD_BALANCING) com desempate aleatorio.

**Racional**:
- Simples de implementar e entender
- Garante distribuicao justa (diferenca maxima de 1 historia entre devs)
- Determinismo em testes via random.Random(seed)

**Implementacao**:
```python
def _select_developer(
    developers: Sequence[Developer],
    story: Story,
    allocated_count: dict[int, int],  # dev_id -> count
    rng: random.Random,
) -> Developer | None:
    if not developers:
        return None

    # Ordenar por contagem (menor primeiro)
    sorted_devs = sorted(developers, key=lambda d: allocated_count.get(d.id, 0))
    min_count = allocated_count.get(sorted_devs[0].id, 0)

    # Filtrar devs com mesma contagem minima
    candidates = [d for d in sorted_devs
                  if allocated_count.get(d.id, 0) == min_count]

    # Desempate aleatorio
    return rng.choice(candidates)
```

**Alternativas Consideradas**:
1. Round-robin - rejeitado por nao considerar carga atual
2. Balanceamento por Story Points - rejeitado por decisao de design na spec

## 3. Deteccao de Conflito de Periodo

**Decisao**: Formula matematica de sobreposicao com resolucao em cascata.

**Racional**:
- Formula bem definida: overlap = (a.start <= b.end) AND (a.end >= b.start)
- Resolucao em cascata garante consistencia
- MAX_CONFLICT_PASSES (100) previne loops infinitos

**Alternativas Consideradas**:
1. Erro imediato em conflito - rejeitado por ser muito restritivo
2. Nao resolver (apenas detectar) - rejeitado por deixar cronograma invalido

## 4. Deteccao de Deadlock

**Decisao**: Detectar deadlock quando nenhum progresso ocorre em uma iteracao.

**Racional**:
- Progresso = alocacao OU ajuste de data
- Se nenhum dos dois ocorre, sistema esta travado
- Emitir DeadlockWarning e prosseguir para proxima onda

**Alternativas Consideradas**:
1. Lancar excecao - rejeitado por interromper todo o processo
2. Tentar resolver automaticamente - rejeitado por adicionar complexidade desnecessaria

## 5. Deteccao de Ociosidade

**Decisao**: Distinguir ociosidade intra-wave (problema) de inter-wave (esperado).

**Racional**:
- Gap dentro da mesma onda indica problema de planejamento
- Gap entre ondas diferentes e natural (ondas sao priorizadas)
- Usar SchedulingService.count_workdays_between() para calcular gap

**Alternativas Consideradas**:
1. Nao distinguir intra/inter wave - rejeitado por gerar falsos positivos
2. Ignorar ociosidade - rejeitado por perder informacao valiosa

## 6. Loop de Estabilizacao

**Decisao**: Loop de 3 etapas com MAX_STABILIZATION_PASSES (10).

**Racional**:
- Fixed-point iteration: repetir ate nao haver mais ajustes
- Ordem das etapas garante consistencia (dependencias -> conflitos -> ociosidade)
- Limite de passadas previne loop infinito

**Alternativas Consideradas**:
1. Sem estabilizacao - rejeitado por deixar inconsistencias
2. Apenas uma passada - rejeitado por nao resolver cascatas

## 7. Criterio DEPENDENCY_OWNER

**Decisao**: Usar desenvolvedor que completou dependencia mais recente (maior end_date).

**Racional**:
- Desenvolvedor recente tem contexto mais fresco
- Simples de implementar (um lookup)
- Fallback para LOAD_BALANCING se nao disponivel

**Alternativas Consideradas**:
1. Dev que completou MAIS dependencias - rejeitado por complexidade
2. Primeiro dev encontrado - rejeitado por ser arbitrario

## 8. Integracao com SchedulingService

**Decisao**: AllocationService importa e chama SchedulingService diretamente.

**Racional**:
- Ambos sao domain services (podem se conhecer)
- SchedulingService e stateless, sem efeitos colaterais
- Simplifica API (menos parametros no AllocationService)

**Metodos Utilizados**:
- `SchedulingService.next_workday(date, holidays)` - proximo dia util
- `SchedulingService.add_workdays(start, workdays, holidays)` - avanca N dias uteis
- `SchedulingService.count_workdays_between(start, end, holidays)` - gap de dias uteis
- `SchedulingService.calculate_duration(sp, velocity)` - duracao em dias

**Alternativas Consideradas**:
1. Passar funcoes como parametros - rejeitado por adicionar complexidade
2. Use case coordena ambos - rejeitado por duplicar logica

## 9. Estrutura de DTOs

**Decisao**: Pydantic BaseModel com Field() para validacao.

**Racional**:
- Consistente com DTOs existentes (CalculateScheduleInputDTO)
- Validacao automatica de entrada
- Serializacao/deserializacao facil

**Estrutura de Campos**:

ExecuteAllocationInputDTO:
- velocity: float (Field gt=0)
- project_start_date: date
- max_idle_days: int (Field default=3, ge=2, le=30)
- allocation_criteria: str (Field default="LOAD_BALANCING")
- random_seed: int | None (Field default=None)

ExecuteAllocationOutputDTO:
- success: bool
- stories_allocated: int
- total_time_seconds: float
- warnings: list[str] (Field default_factory=list)
- metrics: AllocationMetricsDTO

AllocationMetricsDTO (16 campos):
- total_time_seconds: float = 0.0
- stories_processed: int = 0
- stories_allocated: int = 0
- waves_processed: int = 0
- total_iterations: int = 0
- iterations_per_wave: dict[int, int] = Field(default_factory=dict)
- allocations_by_dependency_owner: int = 0
- allocations_by_load_balancing: int = 0
- deadlocks_detected: int = 0
- date_adjustments: int = 0
- validation_reallocations: int = 0
- validation_dependency_fixes: int = 0
- validation_conflict_fixes: int = 0
- max_idle_violations_detected: int = 0
- max_idle_violations_fixed: int = 0
- failed_reallocations: int = 0

## 10. Constantes de Seguranca

**Decisao**: Definir constantes no modulo para limites de seguranca.

```python
DEFAULT_MAX_ITERATIONS: int = 1000
MAX_REALLOCATIONS_PER_STORY: int = 3
MAX_STABILIZATION_PASSES: int = 10
MAX_CONFLICT_PASSES: int = 100
```

**Racional**:
- Previne loops infinitos em casos extremos
- Valores baseados em analise de complexidade (O(n^2) no pior caso)
- Podem ser expostos em AllocationConfig se necessario futuramente

## 11. Padroes de Entity Update

**Decisao**: Usar object.__setattr__ para atualizar dataclasses frozen.

**Racional**:
- Story e frozen dataclass (imutavel)
- Padrao ja estabelecido em CalculateScheduleUseCase
- Permite atualizacao in-place sem criar novos objetos

**Campos Atualizados**:
- story.developer_id - ID do desenvolvedor alocado
- story.start_date - pode ser ajustado em conflitos
- story.end_date - recalculado apos ajuste de start_date

## 12. Processamento por Ondas

**Decisao**: Agrupar historias por wave e processar em ordem crescente.

**Racional**:
- Wave 0 (historias sem feature) processadas primeiro
- Ondas subsequentes em ordem (1, 2, 3...)
- Respeita priorizacao do PO
- Deadlock em onda N nao bloqueia onda N+1

**Implementacao**:
1. Construir mapa feature_id -> wave
2. Agrupar historias elegiveis por wave
3. Ordenar waves (sorted keys)
4. Para cada wave: loop de alocacao com verificacao de progresso

## 13. Rastreamento de Realocacoes

**Decisao**: Usar dicionario externo para contar realocacoes por historia.

**Racional**:
- Nao polui entidade Story com campo temporario
- Permite limite MAX_REALLOCATIONS_PER_STORY = 3
- Evita ping-pong infinito entre desenvolvedores

**Implementacao**:
```python
reallocation_count: dict[str, int] = {}  # story_id -> count

def _can_reallocate(story_id: str) -> bool:
    return reallocation_count.get(story_id, 0) < MAX_REALLOCATIONS_PER_STORY

def _register_reallocation(story_id: str) -> None:
    reallocation_count[story_id] = reallocation_count.get(story_id, 0) + 1
```
