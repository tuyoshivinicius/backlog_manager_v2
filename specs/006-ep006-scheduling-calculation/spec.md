# Feature Specification: EP-006 Calculo de Cronograma

**Feature Branch**: `006-ep006-scheduling-calculation`
**Created**: 2026-03-01
**Status**: Draft
**Input**: Implementacao do SchedulingService (domain service) para calculo de cronogramas com duracao baseada em story points e velocidade, considerando apenas dias uteis (segunda a sexta), excluindo feriados brasileiros (2026-2028), respeitando dependencias entre historias, e ordenacao topologica via Kahn's algorithm com desempate por prioridade.

## Clarifications

### Session 2026-03-02

- Q: Which story statuses are eligible for scheduling calculation? → A: Only BACKLOG stories are scheduled; other statuses keep existing dates but participate in dependency graph.
- Q: What happens when backlog is empty or no eligible stories exist? → A: Return success with stories_processed=0, stories_updated=0, and informational warning in warnings list.
- Q: What is explicitly out of scope for this epic? → A: Date calculation only; resource allocation (assigning developers) and sprint planning (grouping into sprints) are out of scope (EP-007).
- Q: What happens when a dependency has no end_date set? → A: Fallback to project_start_date when dependency lacks end_date; emit warning in output.
- Q: What happens when a story has invalid/missing story_points? → A: Skip stories with invalid/missing story_points; emit warning listing skipped stories; continue with valid stories.

## Out of Scope

- **Resource Allocation**: Assigning developers/team members to stories is NOT part of this epic (deferred to EP-007)
- **Sprint Planning**: Grouping stories into sprint boundaries or 2-week cycles is NOT part of this epic (deferred to EP-007)
- **Capacity Planning**: Considering team capacity or availability constraints is NOT part of this epic
- **Parallel Execution**: Stories are scheduled sequentially based on dependencies; parallel work streams are not modeled

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Calcular Duracao de Historia Baseada em Story Points (Priority: P1)

Como Scrum Master, preciso que o sistema calcule automaticamente a duracao de cada historia em dias uteis baseado nos story points e na velocidade configurada, para que eu possa planejar entregas com precisao.

**Why this priority**: O calculo de duracao e a base para todos os outros calculos de cronograma. Sem ele, nao e possivel determinar datas de inicio e fim das historias.

**Independent Test**: Pode ser testado calculando duracao para diferentes combinacoes de SP e velocidade, verificando que a formula `ceil(SP / velocity)` e aplicada corretamente com minimo de 1 dia util.

**Acceptance Scenarios**:

1. **Given** SP=5 e velocity=2 SP/dia, **When** calculo duracao, **Then** duration = ceil(5/2) = 3 dias uteis
2. **Given** SP=3 e velocity=5 SP/dia, **When** calculo duracao, **Then** duration = 1 (minimo garantido)
3. **Given** SP=8 e velocity=2 SP/dia, **When** calculo duracao, **Then** duration = ceil(8/2) = 4 dias uteis
4. **Given** SP=13 e velocity=2 SP/dia, **When** calculo duracao, **Then** duration = ceil(13/2) = 7 dias uteis
5. **Given** velocity=0 ou negativo, **When** tento calcular duracao, **Then** ValueError e lancado com mensagem "Velocidade deve ser maior que zero"

---

### User Story 2 - Avancar N Dias Uteis a Partir de Uma Data (Priority: P1)

Como Scrum Master, preciso que o sistema calcule a data de termino avancando N dias uteis a partir da data de inicio, considerando apenas segunda a sexta e excluindo feriados brasileiros.

**Why this priority**: O calculo de end_date e essencial para o cronograma. Sem ele, nao ha como determinar quando uma historia termina.

**Independent Test**: Pode ser testado avancando dias uteis a partir de datas especificas e verificando que fins de semana e feriados sao pulados.

**Acceptance Scenarios**:

1. **Given** start_date=2026-03-02 (segunda) e duration=2, **When** calculo end_date, **Then** end_date=2026-03-03 (terca) - contando inicio como dia 1
2. **Given** start_date=2026-03-05 (quinta) e duration=2, **When** calculo end_date, **Then** end_date=2026-03-06 (sexta)
3. **Given** start_date=2026-03-06 (sexta) e duration=2, **When** calculo end_date, **Then** end_date=2026-03-09 (segunda) - pula fim de semana
4. **Given** start_date=2026-04-20 (segunda antes de Tiradentes) e duration=2, **When** calculo end_date, **Then** end_date=2026-04-22 (quarta) - pula 21/04
5. **Given** start_date=2026-04-01 (quarta) e duration=4, **When** calculo end_date, **Then** end_date=2026-04-07 (terca) - pula Sexta-Santa (03/04) e fim de semana (CT-004)

---

### User Story 3 - Ajustar Data de Inicio para Proximo Dia Util (Priority: P1)

Como Scrum Master, preciso que datas de inicio que caiam em fins de semana ou feriados sejam automaticamente ajustadas para o proximo dia util.

**Why this priority**: Garantir que todas as datas de inicio sejam dias uteis e pre-requisito para calculos corretos de cronograma.

**Independent Test**: Pode ser testado passando datas em fins de semana e feriados e verificando o ajuste automatico.

**Acceptance Scenarios**:

1. **Given** start_date=2026-03-07 (sabado), **When** ajusto para dia util, **Then** start_date=2026-03-09 (segunda)
2. **Given** start_date=2026-03-08 (domingo), **When** ajusto para dia util, **Then** start_date=2026-03-09 (segunda)
3. **Given** start_date=2026-04-21 (Tiradentes), **When** ajusto para dia util, **Then** start_date=2026-04-22 (quarta)
4. **Given** start_date=2026-04-03 (Sexta-Santa), **When** ajusto para dia util, **Then** start_date=2026-04-06 (segunda)
5. **Given** start_date=2026-03-02 (segunda, dia util), **When** ajusto para dia util, **Then** start_date=2026-03-02 (inalterado)

---

### User Story 4 - Calcular Datas Respeitando Dependencias (Priority: P1)

Como Scrum Master, preciso que o sistema calcule a data de inicio de uma historia como o proximo dia util apos o termino de todas as suas dependencias, para garantir a ordem correta de execucao.

**Why this priority**: Respeitar dependencias e fundamental para um cronograma valido. Historias nao podem iniciar antes de suas dependencias terminarem.

**Independent Test**: Pode ser testado criando historias com dependencias e verificando que start_date >= max(end_date_deps) + 1 dia util.

**Acceptance Scenarios**:

1. **Given** B depende de A e A.end_date=2026-03-04 (quarta), **When** calculo B.start_date, **Then** B.start_date=2026-03-05 (quinta)
2. **Given** C depende de A e B, A.end_date=2026-03-03 e B.end_date=2026-03-05, **When** calculo C.start_date, **Then** C.start_date=2026-03-06 (max + 1 dia util)
3. **Given** B depende de A e A.end_date=2026-03-06 (sexta), **When** calculo B.start_date, **Then** B.start_date=2026-03-09 (segunda, pula fim de semana)
4. **Given** B depende de A e A.end_date=2026-04-20 (segunda antes de Tiradentes), **When** calculo B.start_date, **Then** B.start_date=2026-04-22 (pula Tiradentes)
5. **Given** historia sem dependencias e project_start_date=2026-03-02, **When** calculo start_date, **Then** start_date=project_start_date ajustado para dia util

---

### User Story 5 - Ordenar Historias Topologicamente com Desempate por Prioridade (Priority: P2)

Como Scrum Master, preciso que o sistema ordene as historias respeitando dependencias (dependencias antes de dependentes) e desempate por prioridade quando duas historias sao independentes.

**Why this priority**: Ordenacao topologica determina a sequencia de processamento do cronograma. E necessaria para calcular datas em cascata.

**Independent Test**: Pode ser testado criando um grafo de dependencias e verificando que a ordem retornada respeita dependencias e prioridades.

**Acceptance Scenarios**:

1. **Given** A->B->C (C depende de B, B depende de A), **When** ordeno topologicamente, **Then** ordem = [A, B, C]
2. **Given** A (prio=1) e B (prio=2) independentes, **When** ordeno topologicamente, **Then** ordem = [A, B] (menor prioridade primeiro)
3. **Given** A->C, B->C, A.prio=2, B.prio=1, **When** ordeno topologicamente, **Then** ordem = [B, A, C] (B antes de A por prioridade, ambos antes de C por dependencia)
4. **Given** grafo com ciclo detectado, **When** tento ordenar topologicamente, **Then** CyclicDependencyException e lancada (reutiliza deteccao do EP-005)
5. **Given** 100 historias com dependencias complexas, **When** ordeno topologicamente, **Then** tempo de execucao e O(V+E), menor que 100ms

---

### User Story 6 - Calcular Cronograma Completo do Backlog (Priority: P2)

Como Scrum Master, preciso calcular as datas de inicio e fim de todas as historias do backlog em uma unica operacao, respeitando dependencias, dias uteis e feriados.

**Why this priority**: Operacao agregada que orquestra todos os calculos individuais. E o ponto de integracao para a alocacao automatica (EP-007).

**Independent Test**: Pode ser testado com um conjunto de historias e verificando que todas recebem datas corretas em ordem topologica.

**Acceptance Scenarios**:

1. **Given** historias A (SP=5), B (SP=8, depende de A), C (SP=5, depende de B), velocity=2, start_date=2026-03-02, **When** calculo cronograma, **Then** A: 02-04/03, B: 05-12/03, C: 13-17/03
2. **Given** historias sem dependencias com prioridades 1, 2, 3, **When** calculo cronograma, **Then** todas iniciam em start_date, processadas em ordem de prioridade
3. **Given** cronograma calculado e historias ja com datas, **When** recalculo cronograma, **Then** datas sao atualizadas em cascata
4. **Given** historias com dependencias entre waves, **When** calculo cronograma, **Then** datas respeitam dependencias independente de wave
5. **Given** historias sem feature (wave=0), **When** calculo cronograma, **Then** sao processadas antes das historias de wave 1+

---

### Edge Cases

- O que acontece quando a configuracao nao tem velocity definida? Use case usa velocity default (2.0 SP/dia) da Configuration.
- O que acontece com historias ja com datas manuais? Ver FR-041a - apenas historias com status=BACKLOG sao recalculadas; outras participam do grafo mas mantem datas existentes.
- O que acontece se todas as historias tem ciclos? CyclicDependencyException e lancada na primeira deteccao de ciclo, nenhuma data e calculada.
- O que acontece se start_date do projeto cai em feriado? Ajustado automaticamente para proximo dia util.
- O que acontece com historias de anos fora de 2026-2028? Apenas feriados de 2026-2028 sao considerados; outros anos usam apenas validacao de fim de semana.
- O que acontece quando backlog esta vazio ou nao ha historias elegiveis? Retorna success=true com stories_processed=0, stories_updated=0, e warning informativo na lista warnings.
- O que acontece quando uma dependencia nao tem end_date definido? Usa project_start_date como fallback e emite warning no output informando qual dependencia estava sem data.
- O que acontece quando uma historia tem story_points invalido ou ausente? Historia e ignorada no calculo; warning e emitido listando historias ignoradas; calculo continua com historias validas.

## Requirements *(mandatory)*

### Functional Requirements

#### SchedulingService - Domain Service

- **FR-001**: Sistema DEVE implementar `SchedulingService` como domain service em `src/backlog_manager/domain/services/scheduling_service.py`
- **FR-002**: SchedulingService DEVE ser uma classe com metodos estaticos (stateless), sem dependencias de repositorios ou I/O
- **FR-003**: SchedulingService DEVE implementar metodo `calculate_duration(story_points: int, velocity: float) -> int` que retorna duracao em dias uteis
- **FR-004**: SchedulingService.calculate_duration DEVE usar formula `ceil(story_points / velocity)` com minimo de 1 dia util
- **FR-005**: SchedulingService.calculate_duration DEVE lancar ValueError se velocity <= 0 com mensagem "Velocidade deve ser maior que zero"
- **FR-006**: SchedulingService DEVE implementar metodo `is_workday(date: date, holidays: frozenset[date]) -> bool` que verifica se data e dia util
- **FR-007**: SchedulingService.is_workday DEVE retornar False para sabados (weekday=5), domingos (weekday=6) e datas em holidays
- **FR-008**: SchedulingService DEVE implementar metodo `next_workday(date: date, holidays: frozenset[date]) -> date` que retorna proximo dia util
- **FR-009**: SchedulingService.next_workday DEVE avancar ate encontrar dia util (segunda-sexta, nao feriado)
- **FR-010**: SchedulingService DEVE implementar metodo `add_workdays(start_date: date, workdays: int, holidays: frozenset[date]) -> date` que avanca N dias uteis
- **FR-011**: SchedulingService.add_workdays DEVE contar start_date como dia 1 (ex: start=segunda, workdays=2 -> terca)
- **FR-012**: SchedulingService.add_workdays DEVE pular fins de semana e feriados durante a contagem
- **FR-013**: SchedulingService DEVE implementar metodo `count_workdays_between(start_date: date, end_date: date, holidays: frozenset[date]) -> int` que conta dias uteis entre duas datas (exclusivo). *Nota: Metodo utilitario para validacao e debugging; nao usado diretamente nos calculos de cronograma.*
- **FR-014**: SchedulingService DEVE implementar metodo `topological_sort(stories: Sequence[Story], dependencies: dict[str, list[str]]) -> list[Story]` que ordena historias topologicamente
- **FR-015**: SchedulingService.topological_sort DEVE usar Kahn's algorithm com heap/priority queue para desempate por prioridade
- **FR-016**: SchedulingService.topological_sort DEVE ter complexidade O(V+E) onde V=numero de historias, E=numero de dependencias
- **FR-017**: SchedulingService.topological_sort DEVE lancar CyclicDependencyException se ciclo for detectado (reutilizar DependencyService.detect_cycle)
- **FR-018**: SchedulingService DEVE implementar metodo `calculate_story_dates(story: Story, velocity: float, start_date: date, dependency_end_dates: Sequence[date], holidays: frozenset[date]) -> tuple[date, date, int]` que retorna (start_date, end_date, duration) calculados
- **FR-019**: SchedulingService.calculate_story_dates DEVE calcular start_date como max(dependency_end_dates) + 1 dia util, ou start_date parametro se sem dependencias
- **FR-019a**: CalculateScheduleUseCase DEVE usar project_start_date como fallback quando uma dependencia nao possui end_date definido, e adicionar warning ao output identificando a dependencia sem data
- **FR-020**: SchedulingService.calculate_story_dates DEVE ajustar start_date para dia util via next_workday

#### BrazilianHolidays - Value Object

- **FR-030**: Sistema DEVE implementar `BRAZILIAN_HOLIDAYS_2026_2028` como constante frozenset[date] em `src/backlog_manager/domain/value_objects/brazilian_holidays.py`
- **FR-031**: BRAZILIAN_HOLIDAYS_2026_2028 DEVE conter todos os feriados nacionais de 2026, 2027 e 2028 conforme Apendice A do SRS
- **FR-032**: Feriados de 2026 DEVEM incluir: 01/01, 16/02, 17/02, 03/04, 21/04, 01/05, 04/06, 07/09, 12/10, 02/11, 15/11, 20/11, 25/12
- **FR-033**: Feriados de 2027 DEVEM incluir: 01/01, 08/02, 09/02, 26/03, 21/04, 01/05, 27/05, 07/09, 12/10, 02/11, 15/11, 20/11, 25/12
- **FR-034**: Feriados de 2028 DEVEM incluir: 01/01, 28/02, 29/02, 14/04, 21/04, 01/05, 15/06, 07/09, 12/10, 02/11, 15/11, 20/11, 25/12
- **FR-035**: Sistema DEVE implementar funcao `get_holidays_for_year(year: int) -> frozenset[date]` que retorna feriados de um ano especifico
- **FR-036**: get_holidays_for_year DEVE retornar frozenset vazio para anos fora de 2026-2028

#### Use Cases - Application Layer

- **FR-040**: Sistema DEVE implementar use cases em `src/backlog_manager/application/use_cases/scheduling/`
- **FR-041**: Sistema DEVE implementar `CalculateScheduleUseCase` que calcula datas para todas as historias elegiveis
- **FR-041a**: CalculateScheduleUseCase DEVE considerar elegiveis apenas historias com status=BACKLOG; historias com outros statuses (IN_PROGRESS, DONE, etc.) mantem datas existentes mas participam do grafo de dependencias
- **FR-041b**: CalculateScheduleUseCase DEVE ignorar historias com story_points invalido ou ausente (None ou fora de {3,5,8,13}), adicionando warning ao output listando as historias ignoradas
- **FR-042**: CalculateScheduleUseCase DEVE receber velocity e start_date como parametros (nao acessar Configuration diretamente)
- **FR-043**: CalculateScheduleUseCase DEVE buscar todas as dependencias via get_all_dependencies() e construir grafo via DependencyService.build_graph()
- **FR-044**: CalculateScheduleUseCase DEVE ordenar historias topologicamente via SchedulingService.topological_sort()
- **FR-045**: CalculateScheduleUseCase DEVE calcular datas em ordem topologica, passando end_dates de dependencias para cada historia
- **FR-046**: CalculateScheduleUseCase DEVE atualizar entidades Story com duration, start_date, end_date calculados
- **FR-047**: CalculateScheduleUseCase DEVE persistir historias atualizadas via StoryRepository.update() dentro do UnitOfWork
- **FR-048**: CalculateScheduleUseCase DEVE retornar DTO com lista de historias processadas, count de atualizacoes, e warnings
- **FR-048a**: CalculateScheduleUseCase DEVE retornar success=true com stories_processed=0, stories_updated=0, e warning informativo quando backlog estiver vazio ou nao houver historias elegiveis (status=BACKLOG)
- **FR-049**: Sistema DEVE implementar `CalculateDurationUseCase` que calcula duracao de uma historia individual
- **FR-050**: Sistema DEVE implementar `CalculateStoryDatesUseCase` que calcula datas de uma historia individual respeitando dependencias
- **FR-051**: Todos os use cases DEVEM ser classes async com metodo `async def execute(input_dto: InputDTO) -> OutputDTO`
- **FR-052**: Todos os use cases DEVEM receber UnitOfWork como dependencia no construtor
- **FR-053**: Todos os use cases DEVEM usar context manager do UnitOfWork para garantir transacoes atomicas

#### DTOs - Application Layer

- **FR-060**: Sistema DEVE implementar DTOs Pydantic em `src/backlog_manager/application/dto/scheduling/`
- **FR-061**: Sistema DEVE implementar `CalculateScheduleInputDTO(BaseModel)` com campos: velocity (float), project_start_date (date), recalculate_all (bool, default=True)
- **FR-062**: Sistema DEVE implementar `CalculateScheduleOutputDTO(BaseModel)` com campos: success (bool), stories_processed (int), stories_updated (int), warnings (list[str])
- **FR-063**: Sistema DEVE implementar `CalculateDurationInputDTO(BaseModel)` com campos: story_points (int), velocity (float)
- **FR-064**: Sistema DEVE implementar `CalculateDurationOutputDTO(BaseModel)` com campos: duration (int), formula (str)
- **FR-065**: Sistema DEVE implementar `CalculateStoryDatesInputDTO(BaseModel)` com campos: story_id (str), velocity (float), project_start_date (date)
- **FR-066**: Sistema DEVE implementar `CalculateStoryDatesOutputDTO(BaseModel)` com campos: story_id (str), start_date (date), end_date (date), duration (int)
- **FR-067**: Todos os DTOs DEVEM usar validacao Pydantic para garantir valores validos (velocity > 0, story_points in {3, 5, 8, 13})

### Key Entities

- **SchedulingService**: Domain service stateless responsavel por regras de negocio de cronograma - calculo de duracao, verificacao de dias uteis, avanco de dias uteis, ordenacao topologica. Recebe todos os dados via parametros, mantendo dominio sincrono.
- **BRAZILIAN_HOLIDAYS_2026_2028**: Value object (frozenset imutavel) contendo todas as datas de feriados nacionais brasileiros para 2026-2028. Permite verificacao O(1) se uma data e feriado.
- **CalculateScheduleUseCase**: Application service que coordena calculo de cronograma completo. Busca dependencias, ordena topologicamente, calcula datas em cascata, persiste atualizacoes.
- **DTOs**: Objetos Pydantic para transporte de dados entre camadas. Input DTOs validam parametros, Output DTOs formatam resultados.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuario pode calcular duracao de qualquer historia com formula correta ceil(SP/velocity), minimo 1 dia
- **SC-002**: Sistema calcula end_date corretamente avancando N dias uteis, pulando fins de semana e feriados
- **SC-003**: Cenario CT-004 (Feriados em Sequencia) executa corretamente: start=01/04/2026, duration=4 dias -> end=07/04/2026
- **SC-004**: Sistema ajusta automaticamente datas de inicio que caem em dias nao uteis
- **SC-005**: Historias dependentes sempre iniciam apos o termino de todas as suas dependencias
- **SC-006**: Ordenacao topologica de 100 historias executa em menos de 100ms com complexidade O(V+E)
- **SC-007**: Desempate por prioridade funciona corretamente na ordenacao topologica
- **SC-008**: Calculo de cronograma completo atualiza todas as historias em ordem correta
- **SC-009**: Todas as operacoes sao transacionais - falhas resultam em rollback completo
- **SC-010**: Cobertura de testes unitarios do SchedulingService atinge 100% das regras de negocio
- **SC-011**: UC-002 (Alocacao Automatica) recebe datas pre-calculadas corretamente apos este epico

## Architectural Decisions

### ADR-001: SchedulingService Sincrono Recebendo Dados como Parametros

**Contexto**: A Constituicao §VIII define que o dominio deve ser sincrono. Entretanto, calcular ordenacao topologica requer acesso ao grafo de dependencias que esta no banco.

**Opcoes**:
1. SchedulingService sincrono recebe grafo como parametro (use case busca dados)
2. SchedulingService recebe UnitOfWork para buscar dependencias (quebra Clean Architecture)
3. Criar SchedulingApplicationService assincrono que coordena

**Decisao**: Opcao 1 - SchedulingService sincrono recebe todos os dados como parametros

**Justificativa**:
- Mantem dominio puro e testavel sem mocks
- Use case (application layer) e responsavel por buscar dados e passar para servico
- Consistente com DependencyService (EP-005) que tambem recebe grafo como parametro
- Permite testar algoritmos em isolamento com dados in-memory

### ADR-002: Feriados como Lista Estatica Hardcoded

**Contexto**: RF-SCHED-003 menciona feriados 2026-2028 hardcoded. Alguns feriados sao moveis (Carnaval, Pascoa, Corpus Christi).

**Opcoes**:
1. Lista estatica de todas as datas fixas para 2026-2028 (simples, requer atualizacao manual)
2. Calcular datas moveis via formula de Pascoa (complexo, mas escalavel)
3. Combinar: fixos + formula para moveis

**Decisao**: Opcao 1 - Lista estatica completa de todas as datas para 2026-2028

**Justificativa**:
- SRS Apendice A ja fornece todas as datas (incluindo moveis) para o periodo
- Aplicacao e single-user sem atualizacoes automaticas
- Complexidade de calculo de Pascoa nao justifica para 3 anos fixos
- Para anos alem de 2028, nova versao pode incluir datas atualizadas
- frozenset permite verificacao O(1) e imutabilidade

### ADR-003: Velocity Recebido como Parametro do Use Case

**Contexto**: RF-SCHED-001 usa velocity para calcular duracao. Constitution §XVIII define Configuration.velocity com default 2.0.

**Opcoes**:
1. Use case recebe velocity como parametro de input
2. Use case busca velocity de ConfigurationRepository
3. SchedulingService recebe ConfigurationRepository como dependencia

**Decisao**: Opcao 1 - Use case recebe velocity como parametro de input

**Justificativa**:
- Desacopla SchedulingService de ConfigurationRepository
- Permite usar velocidades diferentes em cenarios de simulacao
- Caller (UI ou teste) decide de onde obter velocity
- Consistente com principio de inversao de dependencia

### ADR-004: Calculo de end_date Contando start_date como Dia 1

**Contexto**: RF-SCHED-002 e exemplos do SRS mostram que duracao=2 dias resulta em start e end diferentes (ex: segunda -> terca).

**Opcoes**:
1. start_date conta como dia 1 (duration=2, segunda -> terca)
2. start_date conta como dia 0 (duration=2, segunda -> quarta)

**Decisao**: Opcao 1 - start_date conta como dia 1

**Justificativa**:
- Consistente com exemplos do SRS e CT-004
- Intuitivo: "2 dias de trabalho" significa trabalha segunda e terca
- end_date = add_workdays(start_date, duration - 1) + ajustes
- Alinhado com pratica comum de cronogramas

### ADR-005: Ordenacao Topologica com Heap para Desempate

**Contexto**: RF-SCHED-006 exige Kahn's algorithm com desempate por prioridade.

**Opcoes**:
1. Kahn's com heap/priority queue para ordenar candidatos por prioridade
2. Kahn's padrao + sort posterior (menos eficiente)
3. DFS com ordenacao por prioridade (mais complexo)

**Decisao**: Opcao 1 - Kahn's algorithm com heap para desempate

**Justificativa**:
- Heap garante O(log n) para cada insercao/extracao
- Prioridade menor = mais prioritario (heap min)
- Complexidade total O(V log V + E) que ainda e eficiente
- Codigo mais limpo que alternativas

### ADR-006: Atualizacao de Datas em Cascata via Use Case

**Contexto**: Ao recalcular cronograma, historias dependentes precisam ter datas recalculadas em ordem topologica.

**Opcoes**:
1. SchedulingService retorna datas calculadas, use case persiste todas de uma vez
2. SchedulingService opera sobre entidades diretamente (modifica in-place)
3. Use case coordena update story-by-story

**Decisao**: Opcao 1 - SchedulingService retorna tuplas (story_id, start, end, duration), use case persiste

**Justificativa**:
- SchedulingService permanece puro (sem side effects)
- Use case controla transacao e persistencia
- Permite batch update para performance
- Entidades sao modificadas apenas na camada de aplicacao

### ADR-007: Ajuste de Data Inicial do Projeto

**Contexto**: RF-SCHED-005 ajusta datas que caem em dias nao uteis. Aplica-se tambem a start_date global do projeto?

**Opcoes**:
1. start_date do projeto e ajustado automaticamente se cair em dia nao util
2. start_date do projeto e validado e rejeitado se invalido
3. start_date do projeto e aceito como esta (caller responsavel)

**Decisao**: Opcao 1 - start_date do projeto e ajustado automaticamente

**Justificativa**:
- Consistente com RF-SCHED-005 que ajusta todas as datas
- Experiencia do usuario melhor (nao precisa saber calendario)
- Historias sem dependencias usam start_date ajustado
- Warning pode ser emitido se ajuste ocorrer

### ADR-008: Historias sem Datas nao Participam do Recalculo por Default

**Contexto**: Historias podem existir sem datas calculadas (recen criadas, status != BACKLOG).

**Opcoes**:
1. Use case calcula datas para todas as historias elegiveis (status=BACKLOG, sem datas)
2. Use case recalcula apenas historias ja com datas
3. Parametro recalculate_all controla comportamento

**Decisao**: Opcao 3 - Parametro recalculate_all controla comportamento

**Justificativa**:
- Flexibilidade: caller decide se quer calcular todas ou apenas recalcular existentes
- Default recalculate_all=True para comportamento mais comum
- recalculate_all=False util para recalculo apos mudanca de dependencia especifica
- Consistente com RF-ALOC que assume datas ja calculadas

### ADR-009: Reutilizar DependencyService.build_graph para Construcao de Grafo

**Contexto**: DependencyService (EP-005) ja possui build_graph() que retorna adjacencia list.

**Opcoes**:
1. SchedulingService reutiliza DependencyService.build_graph()
2. SchedulingService implementa propria construcao de grafo

**Decisao**: Opcao 1 - Reutilizar DependencyService.build_graph()

**Justificativa**:
- DRY: nao duplicar logica de construcao de grafo
- DependencyService ja esta testado e funcionando
- Use case busca dependencias e passa para ambos os servicos
- Grafo e construido uma vez e usado para ordenacao e calculo de datas

## Traceability Matrix

### Requisitos do Epico -> Requisitos Funcionais

| Requisito Epico | Requisitos Funcionais |
|-----------------|----------------------|
| RF-SCHED-001: Calcular Duracao | FR-003, FR-004, FR-005, FR-049, FR-063, FR-064 |
| RF-SCHED-002: Dias Uteis | FR-006, FR-007, FR-010, FR-011, FR-012 |
| RF-SCHED-003: Feriados | FR-030 a FR-036 |
| RF-SCHED-004: Dependencias | FR-018, FR-019, FR-043, FR-045, FR-050 |
| RF-SCHED-005: Ajustar Data | FR-008, FR-009, FR-020 |
| RF-SCHED-006: Ordenacao Topologica | FR-014 a FR-017 |

### User Stories -> Requisitos Epico

| User Story | Requisitos Epico |
|------------|-----------------|
| US-1: Calcular Duracao | RF-SCHED-001 |
| US-2: Avancar Dias Uteis | RF-SCHED-002, RF-SCHED-003 |
| US-3: Ajustar Data Inicio | RF-SCHED-005 |
| US-4: Respeitar Dependencias | RF-SCHED-004 |
| US-5: Ordenacao Topologica | RF-SCHED-006 |
| US-6: Cronograma Completo | RF-SCHED-001 a RF-SCHED-006 |

## Assumptions

- DependencyService.build_graph() esta implementado e funcional (EP-005)
- StoryRepository.get_all() e update() estao implementados (EP-003)
- UnitOfWork gerencia transacoes corretamente com commit/rollback automatico
- CyclicDependencyException esta definida (EP-005)
- Story entity possui campos duration, start_date, end_date como date | None (EP-002)
- Grafo de dependencias cabe em memoria para backlogs de ate 500 historias
- Feriados de 2026-2028 sao suficientes para o periodo de uso da aplicacao
- Configuration.velocity existe com default 2.0 SP/dia (Constituicao §XVIII)

## Algorithm Specifications

### Kahn's Algorithm para Ordenacao Topologica com Desempate

```
Entrada:
  - stories: Sequencia de Story
  - graph: dict[str, list[str]] (story_id -> [depends_on_ids])

Saida:
  - Lista de Story em ordem topologica

Algoritmo:
  1. Construir in_degree map: para cada historia, contar quantas dependencias ela tem
  2. Inicializar heap min com historias de in_degree=0, ordenadas por priority
  3. result = []
  4. Enquanto heap nao vazio:
     a. Extrair historia com menor priority do heap
     b. Adicionar ao result
     c. Para cada historia que depende desta (dependentes):
        - Decrementar in_degree do dependente
        - Se in_degree == 0, inserir no heap
  5. Se len(result) != len(stories): ciclo detectado
  6. Retornar result

Complexidade: O(V log V + E)
- V operacoes de heap (insercao/extracao): O(V log V)
- E atualizacoes de in_degree: O(E)
```

### Calculo de end_date Avancando N Dias Uteis

```
Entrada:
  - start_date: date (ja ajustado para dia util)
  - workdays: int (duracao em dias uteis)
  - holidays: frozenset[date]

Saida:
  - end_date: date

Algoritmo:
  1. current = start_date
  2. days_counted = 1  # start_date conta como dia 1
  3. Enquanto days_counted < workdays:
     a. current = current + 1 dia
     b. Se is_workday(current, holidays):
        days_counted += 1
  4. Retornar current

Nota: Se workdays == 1, retorna start_date
```

### Verificacao de Dia Util

```
Entrada:
  - date: date
  - holidays: frozenset[date]

Saida:
  - bool

Algoritmo:
  1. weekday = date.weekday()
  2. Se weekday >= 5: return False  # Sabado ou domingo
  3. Se date in holidays: return False
  4. return True
```

## Brazilian Holidays Data

### 2026

| Data | Feriado |
|------|---------|
| 2026-01-01 | Ano Novo |
| 2026-02-16 | Carnaval (segunda) |
| 2026-02-17 | Carnaval (terca) |
| 2026-04-03 | Sexta-feira Santa |
| 2026-04-21 | Tiradentes |
| 2026-05-01 | Dia do Trabalho |
| 2026-06-04 | Corpus Christi |
| 2026-09-07 | Independencia |
| 2026-10-12 | Nossa Senhora Aparecida |
| 2026-11-02 | Finados |
| 2026-11-15 | Proclamacao da Republica |
| 2026-11-20 | Consciencia Negra |
| 2026-12-25 | Natal |

### 2027

| Data | Feriado |
|------|---------|
| 2027-01-01 | Ano Novo |
| 2027-02-08 | Carnaval (segunda) |
| 2027-02-09 | Carnaval (terca) |
| 2027-03-26 | Sexta-feira Santa |
| 2027-04-21 | Tiradentes |
| 2027-05-01 | Dia do Trabalho |
| 2027-05-27 | Corpus Christi |
| 2027-09-07 | Independencia |
| 2027-10-12 | Nossa Senhora Aparecida |
| 2027-11-02 | Finados |
| 2027-11-15 | Proclamacao da Republica |
| 2027-11-20 | Consciencia Negra |
| 2027-12-25 | Natal |

### 2028

| Data | Feriado |
|------|---------|
| 2028-01-01 | Ano Novo |
| 2028-02-28 | Carnaval (segunda) |
| 2028-02-29 | Carnaval (terca) |
| 2028-04-14 | Sexta-feira Santa |
| 2028-04-21 | Tiradentes |
| 2028-05-01 | Dia do Trabalho |
| 2028-06-15 | Corpus Christi |
| 2028-09-07 | Independencia |
| 2028-10-12 | Nossa Senhora Aparecida |
| 2028-11-02 | Finados |
| 2028-11-15 | Proclamacao da Republica |
| 2028-11-20 | Consciencia Negra |
| 2028-12-25 | Natal |

## Test Scenarios

### Testes Unitarios - SchedulingService

1. **test_calculate_duration_normal**: SP=5, velocity=2 -> duration=3
2. **test_calculate_duration_minimum**: SP=3, velocity=5 -> duration=1 (minimo)
3. **test_calculate_duration_exact**: SP=8, velocity=4 -> duration=2
4. **test_calculate_duration_invalid_velocity**: velocity=0 -> ValueError
5. **test_is_workday_monday**: 2026-03-02 -> True
6. **test_is_workday_saturday**: 2026-03-07 -> False
7. **test_is_workday_holiday**: 2026-04-21 -> False
8. **test_next_workday_already_workday**: 2026-03-02 -> 2026-03-02
9. **test_next_workday_from_saturday**: 2026-03-07 -> 2026-03-09
10. **test_next_workday_from_holiday**: 2026-04-21 -> 2026-04-22
11. **test_add_workdays_same_week**: 2026-03-02, 2 dias -> 2026-03-03
12. **test_add_workdays_across_weekend**: 2026-03-06, 2 dias -> 2026-03-09
13. **test_add_workdays_with_holiday**: 2026-04-20, 2 dias -> 2026-04-22 (pula Tiradentes)
14. **test_add_workdays_ct004**: 2026-04-01, 4 dias -> 2026-04-07 (Sexta-Santa + fim de semana)
15. **test_topological_sort_linear**: A->B->C -> [A, B, C]
16. **test_topological_sort_priority_tiebreak**: A(prio=2), B(prio=1) independentes -> [B, A]
17. **test_topological_sort_complex**: grafo com multiplos caminhos
18. **test_topological_sort_cycle**: ciclo -> CyclicDependencyException
19. **test_count_workdays_between**: 2026-03-02 a 2026-03-06 -> 3 dias

### Testes de Integracao - Use Cases

1. **test_calculate_schedule_success**: Cronograma completo calculado corretamente
2. **test_calculate_schedule_with_dependencies**: Datas respeitam dependencias
3. **test_calculate_schedule_with_holidays**: Feriados sao pulados
4. **test_calculate_schedule_cycle_detected**: Ciclo -> CyclicDependencyException
5. **test_calculate_schedule_empty_backlog**: Sem historias -> success com 0 processadas
6. **test_calculate_duration_use_case**: Calcula duracao individual
7. **test_calculate_story_dates_use_case**: Calcula datas de historia individual
8. **test_schedule_rollback_on_error**: Erro -> rollback de todas as alteracoes
