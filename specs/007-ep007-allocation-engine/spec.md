# Feature Specification: EP-007 Motor de Alocacao

**Feature Branch**: `007-ep007-allocation-engine`
**Created**: 2026-03-02
**Status**: Draft
**Input**: Implementacao do AllocationService (domain service) completo para alocacao automatica de desenvolvedores com balanceamento de carga por contagem de historias, processamento sequencial por ondas (wave 0, 1, 2...), deteccao e resolucao de conflitos de periodo, deteccao de deadlocks com emissao de warnings, monitoramento de ociosidade, e loop de estabilizacao pos-alocacao.

## Out of Scope

- **Interface Grafica**: Telas e dialogs para alocacao automatica NAO sao parte deste epico (EP-008)
- **Integracao Excel**: Import/export de dados Excel NAO e parte deste epico (EP-009)
- **Calculo de Cronograma**: Calculo de datas ja implementado em EP-006; este epico CONSOME datas calculadas
- **Gestao de Dependencias**: Dependencias ja implementadas em EP-005; este epico CONSOME o grafo de dependencias
- **Balanceamento por Story Points**: Balanceamento e por contagem de historias (decisao de design documentada)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Executar Alocacao Automatica do Backlog (Priority: P1)

Como Scrum Master, preciso executar alocacao automatica de desenvolvedores para todas as historias elegiveis do backlog, para distribuir o trabalho de forma eficiente e equilibrada.

**Why this priority**: Funcionalidade core do epico - sem ela, nenhum outro requisito de alocacao faz sentido.

**Independent Test**: Pode ser testado com um backlog de historias com datas calculadas e desenvolvedores cadastrados, verificando que todas as historias elegiveis recebem developer_id.

**Acceptance Scenarios**:

1. **Given** 3 historias elegiveis (dev=NULL, datas definidas, SP definido) e 2 devs, **When** executo alocacao automatica, **Then** todas as 3 historias tem developer_id != NULL
2. **Given** historia sem datas calculadas, **When** executo alocacao automatica, **Then** historia NAO e alocada (permanece sem dev)
3. **Given** historia ja com desenvolvedor alocado, **When** executo alocacao automatica, **Then** alocacao existente e mantida (nao realocada)
4. **Given** nenhuma historia elegivel no backlog, **When** executo alocacao automatica, **Then** retorna success com stories_allocated=0
5. **Given** nenhum desenvolvedor cadastrado, **When** executo alocacao automatica, **Then** nenhuma historia e alocada e DeadlockWarning e emitido

---

### User Story 2 - Balanceamento de Carga entre Desenvolvedores (Priority: P1)

Como Scrum Master, preciso que as historias sejam distribuidas equilibradamente entre desenvolvedores baseado na contagem de historias, para evitar sobrecarga de qualquer membro do time.

**Why this priority**: Fundamento do algoritmo de alocacao - garante distribuicao justa.

**Independent Test**: Pode ser testado criando historias independentes e verificando que desenvolvedores recebem quantidades equilibradas.

**Acceptance Scenarios**:

1. **Given** Dev1 com 2 historias e Dev2 com 1 historia, **When** aloco nova historia, **Then** historia e atribuida a Dev2 (menos historias)
2. **Given** Dev1 e Dev2 ambos com 1 historia, **When** aloco nova historia, **Then** historia e atribuida aleatoriamente (desempate aleatorio)
3. **Given** 4 historias independentes e 2 devs, **When** executo alocacao, **Then** cada dev recebe 2 historias
4. **Given** seed aleatorio fixo para testes, **When** executo alocacao com empates, **Then** resultado e deterministico e reproduzivel

---

### User Story 3 - Processar Historias por Ondas Sequencialmente (Priority: P1)

Como Scrum Master, preciso que historias sejam processadas onda por onda (wave 0, 1, 2...), para garantir que features de ondas anteriores sejam priorizadas.

**Why this priority**: Fundamental para respeitar a priorizacao de features/ondas definida pelo PO.

**Independent Test**: Pode ser testado criando historias em diferentes ondas e verificando ordem de processamento.

**Acceptance Scenarios**:

1. **Given** Feature "Auth" (onda 1) com 3 historias e Feature "API" (onda 2) com 2 historias, **When** executo alocacao, **Then** todas as 3 de onda 1 sao alocadas antes das 2 de onda 2
2. **Given** 2 historias sem feature (wave=0) e 2 em onda 1, **When** executo alocacao, **Then** wave=0 sao alocadas primeiro
3. **Given** deadlock na onda 1, **When** sistema detecta deadlock, **Then** emite DeadlockWarning e prossegue para onda 2
4. **Given** historias em ondas 0, 1, 2, 3, **When** executo alocacao, **Then** ordem de processamento e 0, 1, 2, 3

---

### User Story 4 - Evitar Conflitos de Periodo (Priority: P1)

Como Scrum Master, preciso que o sistema detecte e resolva conflitos de periodo automaticamente, para garantir que um desenvolvedor nao tenha duas historias sobrepostas no mesmo periodo.

**Why this priority**: Sem resolucao de conflitos, cronograma seria invalido.

**Independent Test**: Pode ser testado criando historias com periodos sobrepostos para mesmo dev e verificando ajuste de datas.

**Acceptance Scenarios**:

1. **Given** Dev1 com historia A (02/03-04/03) e historia B (03/03-05/03) sobrepostas, **When** sistema resolve conflitos, **Then** B.start_date = 05/03 (proximo dia util apos A.end_date)
2. **Given** Dev1 com historias sem sobreposicao, **When** sistema verifica conflitos, **Then** nenhum ajuste e feito
3. **Given** conflito que requer ajuste no fim de semana, **When** sistema resolve conflito, **Then** nova start_date e ajustada para proximo dia util (segunda)
4. **Given** multiplas historias com conflitos em cascata, **When** sistema resolve, **Then** todas sao ajustadas ate MAX_CONFLICT_PASSES (100) ou estabilizacao

---

### User Story 5 - Detectar Deadlocks na Alocacao (Priority: P2)

Como Scrum Master, preciso que o sistema detecte situacoes de deadlock onde nenhuma historia pode ser alocada, para identificar problemas de planejamento.

**Why this priority**: Importante para diagnostico, mas alocacao pode funcionar parcialmente sem deteccao perfeita.

**Independent Test**: Pode ser testado criando cenarios onde nenhum progresso e possivel e verificando emissao de warning.

**Acceptance Scenarios**:

1. **Given** onda 2 com 3 historias pendentes e nenhum dev disponivel, **When** sistema detecta que nao houve progresso na iteracao, **Then** emite DeadlockWarning e processa onda 3
2. **Given** deadlock detectado, **When** verifico metricas, **Then** deadlocks_detected >= 1
3. **Given** onda com deadlock, **When** alocacao termina, **Then** historias bloqueadas estao listadas no DeadlockWarning
4. **Given** MAX_ITERATIONS atingido sem progresso, **When** sistema verifica, **Then** DeadlockWarning e emitido com flag `max_iterations_reached=True` e alocacao parcial e retornada (MaxIterationsExceeded NAO e lancada)

---

### User Story 6 - Detectar e Alertar Ociosidade (Priority: P2)

Como Scrum Master, preciso que o sistema detecte periodos de ociosidade excessiva entre historias de um desenvolvedor, para identificar gaps no planejamento.

**Why this priority**: Otimizacao do planejamento, mas alocacao basica funciona sem.

**Independent Test**: Pode ser testado criando historias com gaps entre elas para mesmo dev e verificando warnings.

**Acceptance Scenarios**:

1. **Given** Dev1 com historia A (02-04/03) e historia B (10-12/03) na mesma onda, **When** sistema verifica ociosidade (gap=3 dias), **Then** se gap > max_idle_days emite IdlenessWarning
2. **Given** gap de ociosidade entre ondas diferentes, **When** sistema verifica, **Then** emite BetweenWavesIdlenessInfo (informativo, nao problema)
3. **Given** max_idle_days=3 configurado, **When** gap=4 dias dentro da onda, **Then** IdlenessWarning e emitido
4. **Given** max_idle_days=5 configurado, **When** gap=4 dias dentro da onda, **Then** nenhum warning e emitido

---

### User Story 7 - Criterio Proprietario de Dependencia (Priority: P3)

Como Scrum Master, posso configurar criterio de alocacao por proprietario de dependencia, para priorizar continuidade de contexto.

**Why this priority**: Otimizacao avancada, balanceamento de carga e suficiente para MVP.

**Independent Test**: Pode ser testado configurando criterio DEPENDENCY_OWNER e verificando alocacao preferencial.

**Acceptance Scenarios**:

1. **Given** historia B depende de A, A foi feita por Dev1, criterio=DEPENDENCY_OWNER, **When** aloco B, **Then** B e alocada para Dev1 se disponivel
2. **Given** criterio=DEPENDENCY_OWNER mas Dev1 nao disponivel, **When** aloco B, **Then** fallback para balanceamento de carga
3. **Given** criterio=LOAD_BALANCING (padrao), **When** aloco historia com dependencias, **Then** ignora proprietario e usa contagem
4. **Given** historia sem dependencias e criterio=DEPENDENCY_OWNER, **When** aloco historia, **Then** usa balanceamento de carga como fallback

---

### User Story 8 - Realocar para Minimizar Ociosidade (Priority: P3)

Como Scrum Master, preciso que o sistema tente realocar historias quando detecta ociosidade excessiva, para otimizar o cronograma automaticamente.

**Why this priority**: Otimizacao avancada; sistema funciona com deteccao sem realocacao automatica.

**Independent Test**: Pode ser testado criando cenarios com ociosidade e verificando tentativas de realocacao.

**Acceptance Scenarios**:

1. **Given** Dev1 com gap excessivo e Dev2 com disponibilidade no periodo, **When** sistema tenta realocar, **Then** historia pode ser movida para Dev2
2. **Given** historia ja realocada 3 vezes (MAX_REALLOCATIONS_PER_STORY), **When** sistema tenta realocar novamente, **Then** realocacao e bloqueada (evita ping-pong)
3. **Given** realocacao bem-sucedida, **When** verifico metricas, **Then** validation_reallocations >= 1
4. **Given** realocacao impossivel, **When** verifico metricas, **Then** failed_reallocations >= 1

---

### User Story 9 - Coletar Metricas de Alocacao (Priority: P2)

Como Scrum Master, preciso visualizar metricas detalhadas apos a alocacao, para analisar performance e identificar problemas.

**Why this priority**: Essencial para diagnostico e melhoria continua do planejamento.

**Independent Test**: Pode ser testado executando alocacao e verificando estrutura AllocationMetrics completa.

**Acceptance Scenarios**:

1. **Given** alocacao completa, **When** consulto metricas, **Then** tenho: total_time_seconds, stories_allocated, waves_processed
2. **Given** deadlocks ocorreram, **When** consulto metricas, **Then** deadlocks_detected > 0
3. **Given** conflitos resolvidos, **When** consulto metricas, **Then** validation_conflict_fixes >= 1
4. **Given** nenhum problema na alocacao, **When** consulto metricas, **Then** todos campos de warning/fix = 0

---

### User Story 10 - Loop de Estabilizacao Pos-Alocacao (Priority: P1)

Como Scrum Master, preciso que o sistema execute validacao e estabilizacao apos a alocacao principal, para garantir consistencia final do cronograma.

**Why this priority**: Garante resultado valido mesmo apos alocacao inicial.

**Independent Test**: Pode ser testado executando alocacao e verificando que loop de estabilizacao corrige inconsistencias.

**Acceptance Scenarios**:

1. **Given** alocacao inicial com violacoes de dependencia, **When** loop de estabilizacao executa, **Then** violacoes sao corrigidas
2. **Given** conflitos de periodo remanescentes, **When** loop de estabilizacao executa, **Then** conflitos sao resolvidos
3. **Given** violacoes de max_idle_days, **When** loop de estabilizacao executa, **Then** tentativa de realocacao e feita
4. **Given** loop executa MAX_STABILIZATION_PASSES (10) sem estabilizar, **When** limite atingido, **Then** loop para e resultado parcial e retornado

---

### Edge Cases

- O que acontece quando nao ha desenvolvedores cadastrados? Todas as historias permanecem sem alocacao; DeadlockWarning emitido para cada onda.
- O que acontece quando todas as historias ja estao alocadas? Retorna success com stories_allocated=0 (nenhuma elegivel).
- O que acontece com historia sem feature? wave=0, processada antes de todas as ondas.
- O que acontece quando historia tem dependencia sem end_date? Usa project_start_date como fallback (conforme EP-006).
- O que acontece quando dev e deletado durante alocacao? Use case opera em transacao; rollback garante consistencia.
- O que acontece com empate de contagem entre multiplos devs? Desempate aleatorio com seed opcional para determinismo em testes.
- O que acontece quando MAX_ITERATIONS (1000) e atingido? DeadlockWarning e emitido com max_iterations_reached=True; alocacao parcial mantida.
- O que acontece quando historia tem story_points invalido? Historia ignorada (nao elegivel); warning emitido.

## Requirements *(mandatory)*

### Functional Requirements

#### AllocationService - Domain Service

- **FR-001**: Sistema DEVE implementar `AllocationService` como domain service em `src/backlog_manager/domain/services/allocation_service.py`
- **FR-002**: AllocationService DEVE ser uma classe com metodos estaticos ou metodos de instancia que recebem dados como parametros (stateless ou com estado injetado)
- **FR-003**: AllocationService DEVE ser SINCRONO no dominio puro, recebendo todos os dados como parametros (nao acessar repositorios ou UnitOfWork)
- **FR-004**: AllocationService DEVE implementar metodo `allocate_stories(stories, developers, dependencies, features, holidays, config) -> AllocationResult` que executa alocacao completa
- **FR-005**: AllocationService DEVE processar historias agrupadas por onda (wave 0, 1, 2...) em ordem crescente
- **FR-006**: AllocationService DEVE obter wave de historia via feature_id -> Feature.wave, retornando 0 se historia nao tem feature

#### Criterios de Elegibilidade (RF-ALOC-001)

- **FR-010**: Historia e elegivel para alocacao se: (a) developer_id == None, (b) start_date != None AND end_date != None, (c) story_points definido
- **FR-011**: Historias nao elegiveis DEVEM ser ignoradas na alocacao (nao lancar erro, apenas pular)
- **FR-012**: Historias ja alocadas (developer_id != None) DEVEM manter alocacao existente

#### Balanceamento de Carga (RF-ALOC-002)

- **FR-020**: Sistema DEVE alocar historias para desenvolvedor com MENOR contagem de historias alocadas
- **FR-021**: Contagem DEVE usar count_by_developer() ou calculo local baseado nos dados recebidos
- **FR-022**: Desempate entre desenvolvedores com mesma contagem DEVE ser aleatorio
- **FR-023**: Aleatoriedade DEVE usar `random.Random(seed)` com seed opcional para testes deterministicos
- **FR-024**: Se seed nao fornecido, usar aleatoriedade padrao do sistema

#### Criterio Proprietario de Dependencia (RF-ALOC-003)

- **FR-030**: Sistema DEVE suportar criterio configuravel de alocacao: LOAD_BALANCING (padrao) ou DEPENDENCY_OWNER
- **FR-031**: Com DEPENDENCY_OWNER, sistema DEVE priorizar desenvolvedor que completou dependencias da historia
- **FR-032**: Proprietario e determinado pelo developer_id da historia de dependencia (ultimo que completou)
- **FR-033**: Se multiplas dependencias com diferentes devs, usar o dev da dependencia com maior end_date (mais recente)
- **FR-034**: Se proprietario nao disponivel ou criterio LOAD_BALANCING, usar balanceamento de carga

#### Conflitos de Periodo (RF-ALOC-004)

- **FR-040**: Sistema DEVE detectar sobreposicao de periodo: story_a.start_date <= story_b.end_date AND story_a.end_date >= story_b.start_date
- **FR-041**: Sistema DEVE resolver conflitos ajustando start_date da historia conflitante para proximo dia util apos end_date da anterior
- **FR-042**: Sistema DEVE recalcular end_date usando SchedulingService.add_workdays apos ajuste de start_date
- **FR-043**: Sistema DEVE executar resolucao de conflitos em loop ate estabilizar ou atingir MAX_CONFLICT_PASSES (100)
- **FR-044**: Metodo `_resolve_allocation_conflicts` DEVE ser implementado conforme especificado no SRS

#### Ajuste de Datas (RF-ALOC-005)

- **FR-050**: Sistema DEVE incrementar start_date +1 dia util quando nenhum dev disponivel no periodo original
- **FR-051**: Sistema DEVE usar SchedulingService.next_workday para ajuste de datas
- **FR-052**: Sistema DEVE usar SchedulingService.add_workdays para recalcular end_date

#### Processamento por Ondas (RF-ALOC-006)

- **FR-060**: Sistema DEVE agrupar historias por wave antes de processar
- **FR-061**: Sistema DEVE processar ondas em ordem crescente (0, 1, 2, 3...)
- **FR-062**: Sistema DEVE completar processamento de uma onda antes de iniciar proxima
- **FR-063**: Deadlock em uma onda NAO DEVE bloquear processamento de ondas subsequentes

#### Deteccao de Deadlock (RF-ALOC-007)

- **FR-070**: Sistema DEVE detectar deadlock quando: nenhuma alocacao E nenhum ajuste de data na iteracao
- **FR-071**: Sistema DEVE emitir DeadlockWarning com wave e lista de historias bloqueadas
- **FR-072**: Sistema DEVE prosseguir para proxima onda apos detectar deadlock
- **FR-073**: Sistema DEVE incrementar metricas.deadlocks_detected a cada deadlock

#### Deteccao de Ociosidade (RF-ALOC-008)

- **FR-080**: Sistema DEVE calcular gap de ociosidade usando SchedulingService.count_workdays_between
- **FR-081**: Sistema DEVE emitir IdlenessWarning para gaps dentro da MESMA onda que excedam max_idle_days
- **FR-082**: Sistema DEVE emitir BetweenWavesIdlenessInfo para gaps ENTRE ondas (informativo, nao problema)
- **FR-083**: Gap intra-wave e determinado por: ambas historias do mesmo dev tem feature na mesma wave (ou ambas sem feature)

#### Configuracao de Ociosidade (RF-ALOC-009)

- **FR-090**: Sistema DEVE aceitar parametro max_idle_days com padrao 3
- **FR-091**: Sistema DEVE validar max_idle_days no range [2, 30]
- **FR-092**: Validacao de limite DEVE lancar ValueError se fora do range

#### Realocacao por Ociosidade (RF-ALOC-010)

- **FR-100**: Sistema DEVE rastrear contagem de realocacoes por historia (reallocation_count)
- **FR-101**: Sistema NAO DEVE realocar historia mais de MAX_REALLOCATIONS_PER_STORY (3) vezes
- **FR-102**: Realocacao DEVE recalcular datas apos trocar developer_id
- **FR-103**: Sistema DEVE tentar realocacao quando IdlenessWarning e detectado e limite nao atingido

#### AllocationMetrics (RF-ALOC-011)

- **FR-110**: Sistema DEVE implementar `AllocationMetrics` como dataclass em `src/backlog_manager/domain/services/allocation_service.py`
- **FR-111**: AllocationMetrics DEVE conter os 16 campos especificados no SRS:
  - total_time_seconds: float (tempo total de execucao)
  - stories_processed: int (total de historias processadas)
  - stories_allocated: int (historias alocadas com sucesso)
  - waves_processed: int (numero de ondas processadas)
  - total_iterations: int (total de iteracoes do algoritmo)
  - iterations_per_wave: dict[int, int] (iteracoes por onda)
  - allocations_by_dependency_owner: int (alocacoes por criterio DEPENDENCY_OWNER)
  - allocations_by_load_balancing: int (alocacoes por criterio LOAD_BALANCING)
  - deadlocks_detected: int (deadlocks detectados)
  - date_adjustments: int (ajustes de data realizados)
  - validation_reallocations: int (realocacoes bem-sucedidas na validacao)
  - validation_dependency_fixes: int (violacoes de dependencia corrigidas)
  - validation_conflict_fixes: int (conflitos de periodo resolvidos)
  - max_idle_violations_detected: int (violacoes de max_idle_days detectadas)
  - max_idle_violations_fixed: int (violacoes corrigidas por realocacao)
  - failed_reallocations: int (tentativas de realocacao que falharam)
- **FR-112**: Todos os campos de metricas DEVEM ter valor inicial 0 (exceto iterations_per_wave = {})

#### Loop de Estabilizacao (RF-ALOC-012)

- **FR-120**: Sistema DEVE executar loop de estabilizacao apos alocacao principal
- **FR-121**: Loop DEVE executar 3 etapas em ordem: (1) _final_dependency_check, (2) _resolve_allocation_conflicts, (3) _check_and_fix_idle_violations
- **FR-122**: Loop DEVE repetir ate nao haver mais ajustes ou atingir MAX_STABILIZATION_PASSES (10)
- **FR-123**: Cada passada DEVE incrementar contadores apropriados em metricas

#### Limites de Seguranca (RF-ALOC-013)

- **FR-130**: Sistema DEVE definir constante DEFAULT_MAX_ITERATIONS = 1000
- **FR-131**: Sistema DEVE definir constante MAX_REALLOCATIONS_PER_STORY = 3
- **FR-132**: Sistema DEVE definir constante MAX_STABILIZATION_PASSES = 10
- **FR-133**: Sistema DEVE definir constante MAX_CONFLICT_PASSES = 100
- **FR-134**: Sistema DEVE respeitar todos os limites para garantir termino do algoritmo

#### AllocationCriteria - Enum

- **FR-140**: Sistema DEVE implementar enum `AllocationCriteria` com valores LOAD_BALANCING e DEPENDENCY_OWNER
- **FR-141**: LOAD_BALANCING DEVE ser o valor padrao

#### AllocationConfig - Dataclass

- **FR-150**: Sistema DEVE implementar `AllocationConfig` dataclass para parametros de configuracao
- **FR-151**: AllocationConfig DEVE conter: velocity (float), project_start_date (date), max_idle_days (int), allocation_criteria (AllocationCriteria), max_iterations (int), random_seed (int | None)
- **FR-152**: AllocationConfig DEVE ter valores default: max_idle_days=3, allocation_criteria=LOAD_BALANCING, max_iterations=DEFAULT_MAX_ITERATIONS, random_seed=None

#### AllocationResult - Dataclass

- **FR-160**: Sistema DEVE implementar `AllocationResult` dataclass para resultado da alocacao
- **FR-161**: AllocationResult DEVE conter: allocated_stories (list[Story]), metrics (AllocationMetrics), warnings (list[BacklogWarning])
- **FR-162**: allocated_stories DEVE conter apenas historias que foram alocadas (com mudancas)

#### Use Cases - Application Layer

- **FR-200**: Sistema DEVE implementar use cases em `src/backlog_manager/application/use_cases/allocation/`
- **FR-201**: Sistema DEVE implementar `ExecuteAllocationUseCase` que coordena alocacao automatica
- **FR-202**: ExecuteAllocationUseCase DEVE ser classe async com metodo `async def execute(input_dto) -> OutputDTO`
- **FR-203**: ExecuteAllocationUseCase DEVE receber UnitOfWork no construtor
- **FR-204**: ExecuteAllocationUseCase DEVE buscar dados (stories, developers, dependencies, features) via UnitOfWork
- **FR-205**: ExecuteAllocationUseCase DEVE passar dados para AllocationService.allocate_stories()
- **FR-206**: ExecuteAllocationUseCase DEVE persistir historias atualizadas via StoryRepository.update()
- **FR-207**: ExecuteAllocationUseCase DEVE usar context manager do UnitOfWork para garantir transacao atomica
- **FR-208**: ExecuteAllocationUseCase DEVE emitir warning se backlog > 500 historias (RNF-PERF-001 limite suave)

#### DTOs - Application Layer

- **FR-220**: Sistema DEVE implementar DTOs Pydantic em `src/backlog_manager/application/dto/allocation/`
- **FR-221**: Sistema DEVE implementar `ExecuteAllocationInputDTO(BaseModel)` com campos: velocity (float), project_start_date (date), max_idle_days (int, default=3), allocation_criteria (str, default="LOAD_BALANCING"), random_seed (int | None, default=None)
- **FR-222**: Sistema DEVE implementar `ExecuteAllocationOutputDTO(BaseModel)` com campos: success (bool), stories_allocated (int), total_time_seconds (float), warnings (list[str]), metrics (AllocationMetricsDTO)
- **FR-223**: Sistema DEVE implementar `AllocationMetricsDTO(BaseModel)` espelhando AllocationMetrics para serializacao
- **FR-224**: DTOs DEVEM usar validacao Pydantic (velocity > 0, max_idle_days in [2, 30])

### Key Entities

- **AllocationService**: Domain service que implementa algoritmo completo de alocacao automatica. Recebe todos os dados como parametros (sincrono, puro). Responsavel por: agrupar por ondas, balancear carga, detectar conflitos, detectar deadlocks, loop de estabilizacao.
- **AllocationMetrics**: Dataclass imutavel no dominio contendo 16 campos de metricas de performance e diagnostico. Permite analise pos-alocacao.
- **AllocationConfig**: Dataclass de configuracao contendo parametros de alocacao (velocity, max_idle_days, criteria, seed).
- **AllocationResult**: Dataclass de resultado contendo historias alocadas, metricas e warnings.
- **AllocationCriteria**: Enum com criterios de selecao de desenvolvedor (LOAD_BALANCING, DEPENDENCY_OWNER).
- **ExecuteAllocationUseCase**: Application service async que coordena alocacao. Busca dados, invoca AllocationService, persiste resultados.
- **DTOs**: Objetos Pydantic para input/output da aplicacao. Validam parametros e formatam resultados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Todas as historias elegiveis do backlog recebem developer_id apos alocacao automatica
- **SC-002**: Balanceamento de carga distribui historias com diferenca maxima de 1 entre desenvolvedores
- **SC-003**: Historias de onda N sao completamente processadas antes de onda N+1
- **SC-004**: Conflitos de periodo sao 100% resolvidos (sem sobreposicao de datas por dev)
- **SC-005**: Deadlocks sao detectados e reportados via DeadlockWarning sem travar o sistema
- **SC-006**: Ociosidade excessiva e detectada e reportada via IdlenessWarning
- **SC-007**: Cenario CT-001 (Backlog Completo 20 Historias) executa corretamente apos este epico
- **SC-008**: Cenario CT-003 (Deadlock por Falta de Devs) detecta deadlock corretamente
- **SC-009**: Cenario CT-005 (Balanceamento com Tamanhos Diferentes) distribui equilibradamente
- **SC-010**: Alocacao de 100 historias com 10 devs completa em tempo inferior a 5 segundos
- **SC-011**: Cobertura de testes unitarios do AllocationService atinge 100% das regras de negocio

## Architectural Decisions

### ADR-001: AllocationService Sincrono Recebendo Dados como Parametros

**Contexto**: A Constituicao VIII define que o dominio deve ser sincrono. Entretanto, alocacao precisa de historias, desenvolvedores, dependencias e features que estao no banco.

**Opcoes**:
1. AllocationService sincrono recebe todos os dados como parametros (use case busca dados)
2. AllocationService recebe UnitOfWork para buscar dados (quebra Clean Architecture)
3. Criar AllocationApplicationService assincrono que coordena

**Decisao**: Opcao 1 - AllocationService sincrono recebe todos os dados como parametros

**Justificativa**:
- Mantem dominio puro e testavel sem mocks
- Use case (application layer) e responsavel por buscar dados e passar para servico
- Consistente com SchedulingService e DependencyService (EP-005, EP-006) que tambem recebem dados como parametros
- Permite testar algoritmo em isolamento com dados in-memory

### ADR-002: AllocationMetrics como Dataclass no Dominio

**Contexto**: RF-ALOC-011 define 16 campos de metricas. Precisa decidir onde colocar a estrutura.

**Opcoes**:
1. Dataclass no dominio (imutavel, puro)
2. Pydantic BaseModel na Application layer (serializavel, validado)
3. Ambos (dataclass no dominio + DTO na aplicacao)

**Decisao**: Opcao 3 - Dataclass no dominio + DTO na aplicacao

**Justificativa**:
- Dominio permanece puro com dataclass simples
- DTO Pydantic na aplicacao permite serializacao e validacao
- Separacao clara de responsabilidades entre camadas
- Consistente com padrao de DTOs do EP-006

### ADR-003: Desempate Aleatorio com Seed Opcional

**Contexto**: RF-ALOC-002 menciona "desempate aleatorio para fairness". Testes precisam ser deterministicos.

**Opcoes**:
1. Sempre aleatorio (testes nao deterministicos)
2. Sempre deterministico (seed fixo)
3. Seed opcional - aleatorio por padrao, fixo para testes

**Decisao**: Opcao 3 - Seed opcional via parametro random_seed em AllocationConfig

**Justificativa**:
- Producao usa aleatoriedade real para fairness
- Testes podem fixar seed para reprodutibilidade
- Consistente com boas praticas de testes deterministicos

### ADR-004: Criterio de Proprietario de Dependencia

**Contexto**: RF-ALOC-003 menciona criterio configuravel. Precisa definir como determinar "proprietario".

**Opcoes**:
1. Dev que completou a ULTIMA dependencia (maior end_date)
2. Dev que completou MAIS dependencias (majoritario)
3. Dev que completou QUALQUER dependencia (primeiro encontrado)

**Decisao**: Opcao 1 - Dev que completou a dependencia com maior end_date

**Justificativa**:
- Mais recente = contexto mais fresco na memoria
- Simples de implementar (um lookup)
- Evita complexidade de contagem de proprietarios

### ADR-005: Deteccao de Ociosidade Intra vs Inter-Wave

**Contexto**: RF-ALOC-008 distingue IdlenessWarning (dentro da onda) de BetweenWavesIdlenessInfo (entre ondas).

**Opcoes**:
1. Determinar wave de cada historia via feature_id -> Feature.wave
2. Manter wave cacheado na historia durante processamento
3. Verificar apenas se historias consecutivas do dev estao na mesma wave

**Decisao**: Opcao 1 - Determinar wave via feature_id usando mapa de features passado

**Justificativa**:
- Consistente com processamento por ondas
- Mapa de features ja esta disponivel como parametro
- Permite verificacao correta mesmo quando dev tem historias em multiplas waves

### ADR-006: Integracao com SchedulingService

**Contexto**: AllocationService precisa ajustar datas (RF-ALOC-004, RF-ALOC-005). Ambos sao domain services.

**Opcoes**:
1. AllocationService importa e chama SchedulingService diretamente
2. Use case coordena ambos os servicos
3. AllocationService recebe funcoes de calculo como parametros (injecao)

**Decisao**: Opcao 1 - AllocationService chama SchedulingService diretamente

**Justificativa**:
- Ambos sao domain services, podem se conhecer
- SchedulingService e stateless, sem efeitos colaterais
- Simplifica API do AllocationService (menos parametros)
- Consistente com DDD onde domain services podem colaborar

### ADR-007: Warning de Limite de Historias

**Contexto**: RNF-PERF-001 menciona limite suave de 500 historias com warning.

**Opcoes**:
1. Warning no use case antes de alocar
2. Warning no AllocationService
3. Warning em ambos

**Decisao**: Opcao 1 - Warning no ExecuteAllocationUseCase

**Justificativa**:
- Logica de negocio de "limite de sistema" pertence a aplicacao
- Dominio nao deve conhecer restricoes de deployment
- Use case pode logar warning antes de iniciar alocacao

## Traceability Matrix

### Requisitos do Epico -> Requisitos Funcionais

| Requisito Epico                              | Requisitos Funcionais                       |
|----------------------------------------------|---------------------------------------------|
| RF-ALOC-001: Executar Alocacao Automatica    | FR-001 a FR-012, FR-200 a FR-208            |
| RF-ALOC-002: Balanceamento de Carga          | FR-020 a FR-024                             |
| RF-ALOC-003: Criterio Proprietario           | FR-030 a FR-034, FR-140, FR-141             |
| RF-ALOC-004: Evitar Conflitos de Periodo     | FR-040 a FR-044                             |
| RF-ALOC-005: Ajustar Datas                   | FR-050 a FR-052                             |
| RF-ALOC-006: Processar por Ondas             | FR-060 a FR-063                             |
| RF-ALOC-007: Detectar Deadlocks              | FR-070 a FR-073                             |
| RF-ALOC-008: Detectar Ociosidade             | FR-080 a FR-083                             |
| RF-ALOC-009: Configurar Limite Ociosidade    | FR-090 a FR-092                             |
| RF-ALOC-010: Realocar por Ociosidade         | FR-100 a FR-103                             |
| RF-ALOC-011: Coletar Metricas                | FR-110 a FR-112                             |
| RF-ALOC-012: Loop de Estabilizacao           | FR-120 a FR-123                             |
| RF-ALOC-013: Limites de Seguranca            | FR-130 a FR-134                             |

### User Stories -> Requisitos Epico

| User Story                                   | Requisitos Epico                            |
|----------------------------------------------|---------------------------------------------|
| US-1: Executar Alocacao Automatica           | RF-ALOC-001                                 |
| US-2: Balanceamento de Carga                 | RF-ALOC-002                                 |
| US-3: Processar por Ondas                    | RF-ALOC-006                                 |
| US-4: Evitar Conflitos de Periodo            | RF-ALOC-004, RF-ALOC-005                    |
| US-5: Detectar Deadlocks                     | RF-ALOC-007                                 |
| US-6: Detectar Ociosidade                    | RF-ALOC-008, RF-ALOC-009                    |
| US-7: Criterio Proprietario de Dependencia   | RF-ALOC-003                                 |
| US-8: Realocar por Ociosidade                | RF-ALOC-010                                 |
| US-9: Coletar Metricas                       | RF-ALOC-011                                 |
| US-10: Loop de Estabilizacao                 | RF-ALOC-012, RF-ALOC-013                    |

## Assumptions

- SchedulingService esta implementado e funcional (EP-006) com metodos: calculate_duration, is_workday, next_workday, add_workdays, count_workdays_between, topological_sort, calculate_story_dates
- DependencyService esta implementado e funcional (EP-005) com metodos: build_graph, validate_wave_dependency
- StoryRepository.count_by_developer() esta implementado e funcional (EP-003)
- UnitOfWork gerencia transacoes corretamente com commit/rollback automatico
- Excecoes AllocationException, MaxIterationsExceeded, DeadlockWarning, IdlenessWarning, BetweenWavesIdlenessInfo estao definidas (EP-001)
- Story entity possui campos: developer_id, start_date, end_date, duration, feature_id (EP-002)
- Feature entity possui campo wave (EP-004)
- Historias elegiveis ja tem datas calculadas (EP-006) antes da alocacao
- Grafo de dependencias cabe em memoria para backlogs de ate 500 historias
- BRAZILIAN_HOLIDAYS_2026_2028 esta disponivel como frozenset[date]

## Algorithm Specifications

### Algoritmo Principal de Alocacao

```
Entrada:
  - stories: Sequence[Story] (todas as historias)
  - developers: Sequence[Developer] (todos os desenvolvedores)
  - dependencies: Sequence[tuple[str, str]] (grafo de dependencias)
  - features: Sequence[Feature] (todas as features)
  - holidays: frozenset[date] (feriados)
  - config: AllocationConfig (configuracao)

Saida:
  - AllocationResult com historias alocadas, metricas, warnings

Algoritmo:
  1. Inicializar metricas e random com seed
  2. Filtrar historias elegiveis (dev=NULL, datas definidas, SP definido)
  3. Construir mapa feature_id -> wave para lookup rapido
  4. Agrupar historias elegiveis por wave
  5. Ordenar waves em ordem crescente
  6. Para cada wave:
     a. iteration = 0
     b. Enquanto existir historia elegivel E iteration < max_iterations:
        i.   Para cada historia elegivel na wave:
             - _ensure_dependencies_finished (ajusta datas)
             - Selecionar desenvolvedor disponivel
             - Se dev encontrado: alocar, incrementar metricas
             - Se nao: ajustar data +1 dia util
        ii.  Verificar progresso (alocacao ou ajuste)
        iii. Se sem progresso: deadlock, emitir warning, break
        iv.  iteration += 1
  7. Loop de estabilizacao (max 10 passadas):
     a. _final_dependency_check
     b. _resolve_allocation_conflicts
     c. _check_and_fix_idle_violations
     d. Se nenhum ajuste: break
  8. Coletar tempo total
  9. Retornar AllocationResult
```

### Algoritmo de Selecao de Desenvolvedor

```
Entrada:
  - developers: Sequence[Developer]
  - story: Story
  - allocated_stories: dict[int, list[Story]] (dev_id -> historias)
  - config: AllocationConfig

Saida:
  - Developer | None

Algoritmo:
  1. Se criteria == DEPENDENCY_OWNER:
     a. Buscar dependencias da historia
     b. Se tem dependencias alocadas:
        - Encontrar dev da dependencia com maior end_date
        - Se dev disponivel no periodo: return dev
  2. Fallback para LOAD_BALANCING:
     a. Calcular contagem de historias por dev
     b. Filtrar devs disponiveis no periodo
     c. Ordenar por contagem (menor primeiro)
     d. Se empate: shuffle com random.Random(seed)
     e. Retornar primeiro dev ou None se nenhum disponivel

Disponibilidade = nao ha conflito de periodo com historias ja alocadas do dev
```

### Algoritmo de Resolucao de Conflitos

```
Entrada:
  - stories: list[Story] (historias alocadas)
  - holidays: frozenset[date]

Saida:
  - int (numero de conflitos resolvidos)

Algoritmo:
  1. fixes = 0
  2. Para pass em range(MAX_CONFLICT_PASSES):
     a. conflict_found = False
     b. Agrupar historias por developer_id
     c. Para cada grupo:
        - Ordenar por start_date
        - Para cada par consecutivo (a, b):
          Se overlap(a, b):
            - b.start_date = next_workday(a.end_date + 1)
            - b.end_date = add_workdays(b.start_date, b.duration)
            - conflict_found = True
            - fixes += 1
     d. Se not conflict_found: break
  3. return fixes
```

## Test Scenarios

### Testes Unitarios - AllocationService

1. **test_allocate_empty_backlog**: Sem historias -> success com 0 alocadas
2. **test_allocate_no_developers**: Sem devs -> deadlock warning para cada onda
3. **test_allocate_single_story_single_dev**: 1 historia, 1 dev -> historia alocada
4. **test_allocate_balanced_distribution**: 4 historias, 2 devs -> 2 cada
5. **test_allocate_uneven_distribution**: 5 historias, 2 devs -> 3 e 2 (ou 2 e 3)
6. **test_allocate_by_wave_order**: Ondas 0, 1, 2 -> processadas em ordem
7. **test_allocate_wave_0_first**: Historias sem feature processadas primeiro
8. **test_resolve_conflict_simple**: 2 historias sobrepostas -> ajustadas
9. **test_resolve_conflict_cascade**: Conflitos em cascata -> todos resolvidos
10. **test_detect_deadlock**: Sem progresso -> DeadlockWarning emitido
11. **test_detect_idleness_intra_wave**: Gap dentro da onda -> IdlenessWarning
12. **test_detect_idleness_inter_wave**: Gap entre ondas -> BetweenWavesIdlenessInfo
13. **test_dependency_owner_allocation**: Criterio DEPENDENCY_OWNER funciona
14. **test_load_balancing_tiebreak**: Desempate aleatorio com seed fixo
15. **test_max_iterations_respected**: Limite de iteracoes respeitado
16. **test_max_reallocations_respected**: Limite de realocacoes por historia
17. **test_stabilization_loop**: Loop de estabilizacao corrige inconsistencias
18. **test_metrics_collected**: Todos os 16 campos de metricas preenchidos

### Testes de Integracao - Use Cases

1. **test_execute_allocation_success**: Alocacao completa funciona
2. **test_execute_allocation_rollback_on_error**: Erro -> rollback de transacao
3. **test_execute_allocation_with_dependencies**: Dependencias respeitadas
4. **test_execute_allocation_ct001**: Cenario CT-001 (20 historias, 3 devs)
5. **test_execute_allocation_ct003**: Cenario CT-003 (deadlock por falta de devs)
6. **test_execute_allocation_ct005**: Cenario CT-005 (balanceamento)
7. **test_allocation_performance**: 100 historias, 10 devs em < 5s
8. **test_allocation_large_backlog_warning**: > 500 historias emite warning

### Cenarios de Teste do SRS

#### CT-001: Backlog Completo 20 Historias

```
Dado:
  - 20 historias em 3 ondas (wave 1: 8, wave 2: 7, wave 3: 5)
  - 3 desenvolvedores
  - Dependencias entre historias
  - velocity = 2 SP/dia, start_date = 2026-03-02

Quando:
  - Executo alocacao automatica

Entao:
  - Todas 20 historias alocadas
  - Balanceamento ~7, 7, 6 (ou similar)
  - Ondas processadas em ordem 1, 2, 3
  - Nenhum conflito de periodo
  - Metricas completas coletadas
```

#### CT-003: Deadlock por Falta de Desenvolvedores

```
Dado:
  - 5 historias em onda 1
  - 0 desenvolvedores

Quando:
  - Executo alocacao automatica

Entao:
  - DeadlockWarning emitido para onda 1
  - Nenhuma historia alocada
  - metrics.deadlocks_detected >= 1
```

#### CT-005: Balanceamento com Tamanhos Diferentes

```
Dado:
  - Historia A (SP=13, 7 dias)
  - Historia B (SP=3, 2 dias)
  - Historia C (SP=3, 2 dias)
  - Historia D (SP=3, 2 dias)
  - 2 desenvolvedores

Quando:
  - Executo alocacao automatica

Entao:
  - Dev1: 2 historias, Dev2: 2 historias
  - OU Dev1: 3 historias, Dev2: 1 historia (se A vai para um dev)
  - Balanceamento por CONTAGEM, nao por SP
```
