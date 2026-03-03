# Prompt: Criar Especificacao Tecnica do EP-007

<role>
Voce e um Arquiteto de Software Senior especializado em Clean Architecture, Domain-Driven Design (DDD) e
algoritmos de alocacao e scheduling, com profundo conhecimento em:
- Algoritmos de balanceamento de carga e distribuicao de tarefas
- Deteccao de deadlocks e resolucao de conflitos de periodo
- Domain Services para logica complexa de alocacao de recursos
- Application Layer com Use Cases, DTOs (Pydantic) e coordenacao de repositorios
- Padroes Repository e Unit of Work em Python assincrono (async/await)
- Integracao com servicos de dominio existentes (SchedulingService, DependencyService)
- Metricas de performance e observabilidade de algoritmos

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **Persistencia**: aiosqlite (async SQLite)
- **DTOs**: Pydantic
- **Testes**: pytest + pytest-cov + pytest-asyncio
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD (entidades ricas, VOs, servicos de dominio)

### Estado Atual do Codigo (Implementado em EP-001 a EP-006)

As camadas de dominio, infraestrutura e aplicacao ja possuem implementacao funcional para
**historias, desenvolvedores, features, dependencias e calculo de cronograma**. EP-007 constroi o
**AllocationService** completo para alocacao automatica de desenvolvedores.

**Entidades existentes (dominio):**
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com id (str, formato COMPONENTE-NNN), component, name, story_points, priority, status, duration (int | None), start_date (date | None), end_date (date | None), developer_id (int | None), feature_id (int | None).
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com id (auto-increment, int | None), name (max 100, nao vazio).
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com name (max 100, unico, nao vazio), wave (int > 0), id (auto-increment, int | None).

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados do workflow
- `src/backlog_manager/domain/value_objects/brazilian_holidays.py` — `BRAZILIAN_HOLIDAYS_2026_2028` (frozenset[date])

**SchedulingService existente (EP-006):**
- `src/backlog_manager/domain/services/scheduling_service.py` — servico de dominio com metodos estaticos:
  - `calculate_duration(story_points, velocity) -> int` — calcula duracao em dias uteis
  - `is_workday(d, holidays) -> bool` — verifica se data e dia util
  - `next_workday(d, holidays) -> date` — retorna proximo dia util
  - `add_workdays(start_date, workdays, holidays) -> date` — avanca N dias uteis
  - `count_workdays_between(start_date, end_date, holidays) -> int` — conta dias uteis entre datas
  - `topological_sort(stories, dependencies) -> list[Story]` — ordenacao topologica com desempate por prioridade
  - `calculate_story_dates(story, velocity, start_date, dependency_end_dates, holidays) -> tuple[date, date, int]`

**DependencyService existente (EP-005):**
- `src/backlog_manager/domain/services/dependency_service.py` — servico de dominio com metodos estaticos:
  - `build_graph(dependencies) -> dict[str, list[str]]` — constroi grafo de adjacencia
  - `would_create_cycle(graph, source, target) -> list[str] | None` — detecta se nova aresta cria ciclo
  - `detect_cycle(graph, source, target) -> list[str] | None` — detecta ciclo no grafo
  - `validate_wave_dependency(story_wave, depends_on_wave) -> bool` — valida dependencia cross-wave

**Excecoes existentes (EP-001):**
- `src/backlog_manager/domain/exceptions/allocation.py` — `AllocationException`, `MaxIterationsExceeded`
- `src/backlog_manager/domain/exceptions/warnings.py` — `BacklogWarning`, `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo`

**Repository Protocols existentes (em `src/backlog_manager/domain/interfaces/repositories.py`):**
- `StoryRepository(Protocol)` — add, get_by_id, get_all, get_by_status, get_by_developer, get_by_feature, update, delete, exists, get_max_id_number, get_max_priority, get_by_priority, **count_by_developer**
- `StoryDependencyRepository(Protocol)` — add, remove, get_dependencies, get_dependents, exists, get_all_dependencies, remove_all_for_story
- `DeveloperRepository(Protocol)` — add, get_by_id, get_all, update, delete, exists
- `FeatureRepository(Protocol)` — add, get_by_id, get_by_wave, get_all, update, delete, exists, has_stories, get_by_name
- `UnitOfWork(Protocol)` — stories, developers, features, dependencies, commit, rollback, __aenter__, __aexit__

**Use Cases existentes (EP-003 a EP-006):**
- Story: CreateStory, EditStory, DeleteStory, DuplicateStory, ListStories, MovePriority, AssignDeveloper
- Developer: CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers
- Feature: CreateFeature, UpdateFeature, DeleteFeature, ListFeatures
- Dependency: AddDependency, RemoveDependency, GetDependencies, GetDependents
- Scheduling: CalculateDuration, CalculateStoryDates, CalculateSchedule

**Camadas que EP-007 deve criar/estender:**
- `src/backlog_manager/domain/services/allocation_service.py` — AllocationService (domain service) com algoritmo completo de alocacao
- `src/backlog_manager/application/use_cases/allocation/` — Use cases para execucao de alocacao automatica
- `src/backlog_manager/application/dto/allocation/` — DTOs Pydantic para input/output de alocacao e metricas

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **AllocationService sincrono ou assincrono**: O dominio puro deve ser sincrono (Constituicao §VIII). Entretanto, alocacao precisa consultar historias, desenvolvedores e dependencias. -> A spec deve definir se (a) AllocationService e sincrono e recebe todos os dados como parametros (recomendado), (b) AllocationService recebe UnitOfWork para buscar dados (quebra Clean Architecture), ou (c) cria-se AllocationApplicationService assincrono que coordena. Recomendar opcao (a) com AllocationService puro e Use Case assincrono.

2. **Estrutura de AllocationMetrics**: RF-ALOC-011 define 16 campos de metricas. -> A spec deve decidir se AllocationMetrics e (a) dataclass no dominio (imutavel, puro), (b) Pydantic BaseModel na Application layer (serializavel, validado), ou (c) ambos (dataclass no dominio + DTO na aplicacao). Recomendar dataclass no dominio para manter pureza.

3. **Criterio DEPENDENCY_OWNER vs LOAD_BALANCING**: RF-ALOC-003 menciona criterio configuravel. -> A spec deve definir como o criterio e passado (parametro, enum, configuracao), qual e o fallback, e como contar "proprietario" de dependencias (ultimo dev que completou vs majoritario).

4. **Loop de estabilizacao pos-alocacao**: RF-ALOC-012 descreve 3 etapas (dependencias, conflitos, ociosidade) em loop de ate 10 passadas. -> A spec deve detalhar ordem de execucao, condicao de parada, e o que acontece se nao estabilizar em 10 passadas.

5. **Deteccao de conflitos de periodo**: RF-ALOC-004 menciona `_resolve_allocation_conflicts` com ate 100 passadas. -> A spec deve especificar algoritmo: como detectar sobreposicao (start_date <= other.end_date AND end_date >= other.start_date), como resolver (ajustar start_date +1 dia util), e como garantir termino.

6. **Processamento por ondas**: RF-ALOC-006 exige processar wave 0 primeiro, depois wave 1, 2, etc. -> A spec deve definir como obter wave de uma historia (via feature_id -> Feature.wave, ou 0 se sem feature), como agrupar historias por wave, e comportamento quando wave tem deadlock.

7. **Elegibilidade para alocacao**: RF-ALOC-001 define criterios de elegibilidade. -> A spec deve especificar exatamente: (a) developer_id == None, (b) start_date != None AND end_date != None, (c) story_points definido. Historias sem datas calculadas sao puladas ou erro?

8. **Calculo de ociosidade dentro vs entre ondas**: RF-ALOC-008 distingue `IdlenessWarning` (dentro da onda) de `BetweenWavesIdlenessInfo` (entre ondas). -> A spec deve definir como determinar se gap e intra-wave ou inter-wave, considerando que um dev pode ter historias em multiplas waves.

9. **Realocacao por ociosidade**: RF-ALOC-010 menciona max 3 realocacoes por historia. -> A spec deve especificar: como rastrear contagem de realocacoes, criterio para decidir realocar, e se realocacao recalcula datas ou apenas troca developer_id.

10. **Integracao com SchedulingService**: AllocationService precisa ajustar datas (RF-ALOC-004, RF-ALOC-005). -> A spec deve definir se AllocationService chama SchedulingService diretamente (ambos domain services), ou se Use Case coordena. Recomendar AllocationService usar SchedulingService como dependencia de dominio.

11. **Desempate aleatorio no balanceamento**: RF-ALOC-002 menciona "desempate aleatorio para fairness". -> A spec deve especificar como implementar aleatoriedade (random.choice, random.shuffle) e se seed deve ser fixavel para testes deterministicos.

12. **Limite de historias com warning**: RNF-PERF-001 menciona limite suave de 500 historias com warning. -> A spec deve definir onde e quando emitir esse warning (no use case antes de alocar) e se o warning e do tipo BacklogWarning ou apenas log.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-007_motor-de-alocacao.md` — requisitos, escopo, criterios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — secoes §3.6 RF-ALOC-001 a 013, §4.1 RNF-PERF-001/003, §5 UC-002 (Alocacao Automatica), §7.1 CT-001/CT-003/CT-005, §6.2 (Fluxo de Alocacao Automatica)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios arquiteturais obrigatorios (Clean Architecture, DDD, async, §VIII Programacao Assincrona, §XVI Tratamento de Erros)
4. **Spec de referencia (predecessor)**: `specs/006-ep006-scheduling-calculation/spec.md` — formato, nivel de detalhe e padrao de User Stories/Acceptance Scenarios esperado
5. **SchedulingService existente**: `src/backlog_manager/domain/services/scheduling_service.py` — para reutilizar metodos de calculo de datas e dias uteis
6. **DependencyService existente**: `src/backlog_manager/domain/services/dependency_service.py` — para reutilizar build_graph() e validacao de waves
7. **Entidade Story**: `src/backlog_manager/domain/entities/story.py` — para entender campos de alocacao (developer_id, start_date, end_date)
8. **Entidade Developer**: `src/backlog_manager/domain/entities/developer.py` — para entender estrutura do desenvolvedor
9. **Repository Protocol existente**: `src/backlog_manager/domain/interfaces/repositories.py` — StoryRepository.count_by_developer, DeveloperRepository.get_all
10. **Excecoes de alocacao**: `src/backlog_manager/domain/exceptions/allocation.py` e `warnings.py` — AllocationException, MaxIterationsExceeded, DeadlockWarning, IdlenessWarning
11. **Use Cases de Scheduling (EP-006)**: `src/backlog_manager/application/use_cases/scheduling/` — para seguir o mesmo padrao arquitetural
12. **DTOs de Scheduling (EP-006)**: `src/backlog_manager/application/dto/scheduling/` — para seguir o mesmo padrao de DTOs Pydantic
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-007 — Motor de Alocacao`.

A especificacao deve cobrir **exclusivamente** o escopo do epico:
- RF-ALOC-001: Executar Alocacao Automatica (alocar todas as historias elegiveis)
- RF-ALOC-002: Balanceamento de Carga (distribuir por contagem de historias, desempate aleatorio)
- RF-ALOC-003: Criterio Proprietario de Dependencia (priorizar dev que fez dependencias, configuravel)
- RF-ALOC-004: Evitar Conflitos de Periodo (detectar sobreposicao, ajustar datas)
- RF-ALOC-005: Ajustar Datas por Indisponibilidade (incrementar +1 dia util)
- RF-ALOC-006: Processar por Ondas (wave 0, 1, 2... sequencialmente)
- RF-ALOC-007: Detectar Deadlocks (emitir DeadlockWarning, pular para proxima onda)
- RF-ALOC-008: Detectar Ociosidade (IdlenessWarning para gaps dentro da onda)
- RF-ALOC-009: Configurar Limite de Ociosidade (max_idle_days: 2-30, padrao 3)
- RF-ALOC-010: Realocar para Minimizar Ociosidade (max 3 realocacoes por historia)
- RF-ALOC-011: Coletar Metricas de Alocacao (AllocationMetrics completo)
- RF-ALOC-012: Validacao e Estabilizacao Pos-Alocacao (loop de 10 passadas)
- RF-ALOC-013: Limites de Seguranca do Algoritmo (constantes MAX_*)

**IMPORTANTE**: Este epico **nao** cria entidades ou repositorios do zero. Ele
**constroi a camada de servico e aplicacao** para alocacao automatica sobre a infraestrutura
ja existente (EP-001 a EP-006), orquestrando:

- **AllocationService** (domain service): regras de negocio puras — balanceamento de carga, deteccao de conflitos, processamento por ondas, deteccao de deadlock, deteccao de ociosidade, loop de estabilizacao
- **AllocationMetrics** (dataclass ou DTO): estrutura completa conforme RF-ALOC-011 com 16 campos
- **Use Cases** (application layer): coordenacao de UnitOfWork + AllocationService + SchedulingService + DependencyService + repositorios
- **DTOs Pydantic** (application layer): input/output para operacao de alocacao automatica

Os cenarios de teste CT-001 (Backlog Completo 20 Historias), CT-003 (Deadlock por Falta de Devs) e CT-005 (Balanceamento com Tamanhos Diferentes) devem ser **executaveis** apos este epico.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF do epico EP-007
   (RF-ALOC-001 a 013). Todo RF do escopo deve ter pelo menos um FR correspondente. Incluir
   matriz de rastreabilidade.

2. **Codigo existente prevalece como baseline**: Nao redefinir entidades, value objects,
   repositorios ou servicos ja implementados. Especificar apenas **extensoes** (novos metodos) e
   **novos artefatos** (AllocationService, Use Cases, DTOs, AllocationMetrics).

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Separacao de responsabilidades clara**: Definir com precisao o que fica no Domain Service
   (regras de negocio puras, algoritmos de alocacao) vs. Application Use Case (coordenacao,
   UnitOfWork, DTOs) vs. Repository (acesso a dados). O AllocationService deve ser **sincrono**
   no dominio puro (receber dados como parametros).

5. **Algoritmo de alocacao especificado**: Detalhar o algoritmo completo:
   - Processamento por ondas (wave 0 primeiro, depois 1, 2...)
   - Selecao de desenvolvedor (count_by_developer, desempate aleatorio)
   - Deteccao de conflitos de periodo (sobreposicao de datas)
   - Deteccao de deadlock (nenhum progresso na iteracao)
   - Loop de estabilizacao (3 etapas, max 10 passadas)
   - Limites de seguranca (MAX_ITERATIONS, MAX_REALLOCATIONS, etc.)

6. **Integracao com SchedulingService especificada**: Detalhar como AllocationService usa
   SchedulingService para:
   - Ajustar datas por indisponibilidade (next_workday, add_workdays)
   - Recalcular end_date apos ajuste de start_date
   - Contar dias uteis entre historias (count_workdays_between)

7. **Estrutura AllocationMetrics detalhada**: Especificar todos os 16 campos conforme RF-ALOC-011,
   com tipos exatos, valores iniciais, e como/quando cada campo e incrementado.

8. **Mensagens de erro e warning exatas**: Toda validacao deve especificar a mensagem de erro
   literal (sem acentos no codigo, conforme §8.2 do SRS). Warnings devem usar as classes ja
   existentes (DeadlockWarning, IdlenessWarning, BetweenWavesIdlenessInfo).

9. **Testabilidade**: Cada FR deve ser verificavel por um teste unitario ou de integracao
   especifico. A spec deve tornar trivial derivar os testes. Incluir exemplos de cenarios
   para testes unitarios (CT-001, CT-003, CT-005 como referencia).

10. **Sem sobreposicao com EP-001 a EP-006 ou EP-008+**: Nao re-especificar o que epicos
    anteriores ja entregaram (schema, repositorios, entidades, SchedulingService, DependencyService).
    Nao antecipar interface grafica (EP-008) ou integracao Excel (EP-009).

11. **Consistencia de nomenclatura**: Usar os mesmos nomes de classe, metodo e campo ja
    existentes no codigo. Reutilizar SchedulingService.count_workdays_between() para calculo de
    ociosidade. Reutilizar DependencyService.build_graph() para dependencias.

12. **Operacoes assincronas**: Use cases devem ser `async`, consistente com os repositorios
    baseados em aiosqlite. O dominio puro (AllocationService) deve ser sincrono.

13. **Performance**: O algoritmo de alocacao deve suportar 100 historias + 10 devs em <= 5s.
    Evitar operacoes O(n^2) desnecessarias; considerar estruturas de dados eficientes.

14. **Padrao EP-006 como referencia**: Seguir o mesmo padrao arquitetural de SchedulingService,
    Use Cases e DTOs do epico anterior para garantir consistencia na codebase.

15. **Complexidade ciclomatica**: Funcoes de alocacao podem ter complexidade ate 15 (conforme
    RNF-MANT-003). Decompor algoritmo em metodos auxiliares privados para manter legibilidade.

16. **Aleatoriedade deterministica**: O desempate aleatorio deve usar `random.Random(seed)`
    para permitir testes deterministicos com seed fixo (passado como parametro opcional).
</rules>
