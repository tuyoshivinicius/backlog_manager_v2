# Prompt: Criar Especificacao Tecnica do EP-006

<role>
Voce e um Arquiteto de Software Senior especializado em Clean Architecture, Domain-Driven Design (DDD) e
algoritmos de scheduling, com profundo conhecimento em:
- Algoritmos de grafos (ordenacao topologica via Kahn's algorithm, DFS)
- Calculo de dias uteis com exclusao de fins de semana e feriados
- Domain Services para calculo de cronogramas e duracao de tarefas
- Application Layer com Use Cases, DTOs (Pydantic) e coordenacao de repositorios
- Padroes Repository e Unit of Work em Python assincrono (async/await)
- Integracao com servicos de dominio existentes (DependencyService)

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

### Estado Atual do Codigo (Implementado em EP-001 a EP-005)

As camadas de dominio, infraestrutura e aplicacao ja possuem implementacao funcional para
**historias, desenvolvedores, features e dependencias**. EP-006 constroi o **SchedulingService**
para calculo de cronogramas sobre os alicerces arquiteturais existentes.

**Entidades existentes (dominio):**
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com id (str, formato COMPONENTE-NNN), component, name, story_points, priority, status, **duration** (int | None, dias uteis calculados), **start_date** (date | None), **end_date** (date | None), developer_id (int | None), feature_id (int | None).
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com id (auto-increment, int | None), name (max 100, nao vazio).
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com name (max 100, unico, nao vazio), wave (int > 0), id (auto-increment, int | None).

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados do workflow

**DependencyService existente (EP-005):**
- `src/backlog_manager/domain/services/dependency_service.py` — servico de dominio com metodos estaticos:
  - `build_graph(dependencies: list[tuple[str, str]]) -> dict[str, list[str]]` — constroi grafo de adjacencia
  - `would_create_cycle(graph, source, target) -> bool` — detecta se nova aresta cria ciclo
  - `detect_cycle(graph) -> list[str] | None` — detecta ciclo no grafo
  - `validate_wave_dependency(story_wave, depends_on_wave) -> bool` — valida se dependencia cross-wave e valida

**Repository Protocols existentes (em `src/backlog_manager/domain/interfaces/repositories.py`):**
- `StoryRepository(Protocol)` — add, get_by_id, get_all, get_by_status, get_by_developer, get_by_feature, update, delete, exists, get_max_id_number, get_max_priority, get_by_priority, count_by_developer
- `StoryDependencyRepository(Protocol)` — add, remove, get_dependencies, get_dependents, exists, get_all_dependencies, remove_all_for_story
- `FeatureRepository(Protocol)` — add, get_by_id, get_by_wave, get_all, update, delete, exists, has_stories, get_by_name
- `UnitOfWork(Protocol)` — stories, developers, features, dependencies, commit, rollback, __aenter__, __aexit__

**Use Cases existentes (EP-003/EP-004/EP-005):**
- Story: CreateStory, EditStory, DeleteStory, DuplicateStory, ListStories, MovePriority, AssignDeveloper
- Developer: CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers
- Feature: CreateFeature, UpdateFeature, DeleteFeature, ListFeatures
- Dependency: AddDependency, RemoveDependency, GetDependencies, GetDependents

**Camadas que EP-006 deve criar/estender:**
- `src/backlog_manager/domain/services/scheduling_service.py` — SchedulingService (domain service) com algoritmos de calculo de duracao, dias uteis, feriados, ordenacao topologica
- `src/backlog_manager/domain/value_objects/brazilian_holidays.py` — Value Object com feriados brasileiros 2026-2028 (se nao existir)
- `src/backlog_manager/application/use_cases/scheduling/` — Use cases para operacoes de cronograma
- `src/backlog_manager/application/dto/scheduling/` — DTOs Pydantic para cronograma
- Extensoes ao StoryService ou StoryRepository (se necessario) para atualizar datas calculadas

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Feriados moveis (Carnaval, Corpus Christi, Pascoa)**: O SRS menciona que feriados sao "hardcoded" para 2026-2028. -> A spec deve decidir se (a) utiliza lista estatica de datas fixas (simples, mas requer atualizacao manual), (b) calcula datas moveis via formula de Pascoa (complexo, mas escalavel), ou (c) combina ambos (fixos para conhecidos + formula para moveis). Documentar trade-offs.

2. **Onde persistir velocidade (velocity)**: RF-SCHED-001 usa `velocity` (SP/dia) para calcular duracao. A Constituicao (§XVIII) define `Configuration.velocity` com padrao 2.0. -> A spec deve confirmar que SchedulingService recebe velocity como parametro (injecao de dependencia) ou se acessa Configuration diretamente. Recomendar parametro para desacoplar.

3. **Atualizacao de datas em cascata**: Ao recalcular cronograma, historias dependentes precisam ter suas datas recalculadas em ordem topologica. -> A spec deve definir se (a) SchedulingService atualiza todas as datas em memoria e retorna (use case persiste), (b) SchedulingService opera sobre entities diretamente, ou (c) use case coordena update story-by-story. Considerar performance com muitas historias.

4. **SchedulingService sincrono ou assincrono**: O dominio puro deve ser sincrono (Constituicao §VIII). Entretanto, calcular ordenacao topologica requer acesso ao grafo de dependencias. -> A spec deve definir se (a) SchedulingService e sincrono e recebe grafo como parametro (recomendado), (b) SchedulingService recebe UnitOfWork para buscar dependencias (quebra Clean Architecture), ou (c) cria-se um SchedulingApplicationService assincrono que coordena.

5. **Ordenacao topologica com desempate**: RF-SCHED-006 exige desempate por prioridade quando duas historias nao tem dependencia entre si. -> A spec deve especificar como Kahn's algorithm utiliza heap/priority queue para desempate, e como o codigo obtem prioridade de cada historia.

6. **Ajuste de data inicial do projeto**: RF-SCHED-005 ajusta datas que caem em dias nao uteis. Isso se aplica tambem a `start_date` global do projeto ou apenas a datas derivadas de dependencias? -> A spec deve definir comportamento para a primeira historia (sem dependencias) e se `Configuration.start_date` pode cair em fim de semana.

7. **Integracao com DependencyService.build_graph**: O DependencyService ja possui `build_graph()` que retorna adjacencia list. -> A spec deve confirmar se SchedulingService reutiliza esse metodo ou se implementa sua propria construcao de grafo. Recomendar reutilizacao.

8. **Tratamento de historias sem datas**: Historias sem `start_date`/`end_date` nao participam de calculo de cronograma automaticamente. -> A spec deve definir se (a) o use case calcula datas para todas as historias elegiveis (sem developer, status=BACKLOG), (b) apenas recalcula historias ja com datas, ou (c) oferece ambas as opcoes via parametro.

9. **Calculo de end_date incluindo ou excluindo dias**: RF-SCHED-002 e CT-004 mostram exemplos onde duracao=2 dias resulta em start_date e end_date diferentes. -> A spec deve especificar a formula exata: se duracao=2 e start=segunda, end_date=terca (contando start como dia 1) ou end_date=quarta (contando start como dia 0). Analisar exemplos do SRS para consistencia.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-006_calculo-de-cronograma.md` — requisitos, escopo, criterios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — secoes §3.5 RF-SCHED-001 a 006, §5 UC-002 (Alocacao Automatica com cronograma), §7.1 CT-004 (Feriados em Sequencia), §8.3 (regras implicitas, duracao minima = 1 dia util), Apendice A (feriados 2026-2028)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios arquiteturais obrigatorios (Clean Architecture, DDD, async, §VIII Programacao Assincrona, §XVIII Gestao de Configuracao)
4. **Spec de referencia (predecessor)**: `specs/005-ep005-dependency-services/spec.md` — formato, nivel de detalhe e padrao de User Stories/Acceptance Scenarios esperado
5. **DependencyService existente**: `src/backlog_manager/domain/services/dependency_service.py` — para reutilizar build_graph() e entender padrao de domain service estatico
6. **Entidade Story**: `src/backlog_manager/domain/entities/story.py` — para entender campos duration, start_date, end_date, feature_id
7. **Entidade Feature**: `src/backlog_manager/domain/entities/feature.py` — para entender campo wave
8. **Repository Protocol existente**: `src/backlog_manager/domain/interfaces/repositories.py` — StoryRepository, StoryDependencyRepository, FeatureRepository, UnitOfWork
9. **Use Cases de Dependency (EP-005)**: `src/backlog_manager/application/use_cases/dependency/` — para seguir o mesmo padrao arquitetural
10. **DTOs de Dependency (EP-005)**: `src/backlog_manager/application/dto/dependency/` — para seguir o mesmo padrao de DTOs Pydantic
11. **Configuration (se existir)**: para entender como velocity e start_date sao armazenados
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-006 — Calculo de Cronograma`.

A especificacao deve cobrir **exclusivamente** o escopo do epico:
- RF-SCHED-001: Calcular Duracao da Historia (`duration = ceil(SP / velocity)`, minimo 1 dia util)
- RF-SCHED-002: Considerar Apenas Dias Uteis (segunda a sexta, ajustar inicio em fim de semana)
- RF-SCHED-003: Excluir Feriados Brasileiros (12 feriados/ano, 2026-2028 hardcoded)
- RF-SCHED-004: Respeitar Dependencias no Cronograma (start >= max(end_deps) + 1 dia util)
- RF-SCHED-005: Ajustar Data de Inicio (avancar para proximo dia util se necessario)
- RF-SCHED-006: Ordenacao Topologica (Kahn's algorithm, O(V+E), desempate por prioridade)

**IMPORTANTE**: Este epico **nao** cria entidades ou repositorios do zero. Ele
**constroi a camada de servico e aplicacao** para calculo de cronogramas sobre a infraestrutura
ja existente (EP-001 a EP-005), orquestrando:

- **SchedulingService** (domain service): regras de negocio puras — calculo de duracao, verificacao de dia util, ajuste de datas, ordenacao topologica com Kahn's algorithm
- **BrazilianHolidays** (value object ou constante): lista de feriados nacionais 2026-2028
- **Use Cases** (application layer): coordenacao de UnitOfWork + SchedulingService + DependencyService + repositorios
- **DTOs Pydantic** (application layer): input/output para cada operacao

O cenario de teste CT-004 (Feriados em Sequencia) e parte do UC-002 (calculo de datas na alocacao) devem ser **executaveis** apos este epico.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF do epico EP-006
   (RF-SCHED-001 a 006). Todo RF do escopo deve ter pelo menos um FR correspondente. Incluir
   matriz de rastreabilidade.

2. **Codigo existente prevalece como baseline**: Nao redefinir entidades, value objects ou
   repositorios ja implementados. Especificar apenas **extensoes** (novos metodos) e
   **novos artefatos** (SchedulingService, Use Cases, DTOs, BrazilianHolidays).

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Separacao de responsabilidades clara**: Definir com precisao o que fica no Domain Service
   (regras de negocio puras, algoritmos de calculo) vs. Application Use Case (coordenacao,
   UnitOfWork, DTOs) vs. Repository (acesso a dados). O SchedulingService deve ser **sincrono**
   no dominio puro (receber dados como parametros).

5. **Algoritmo Kahn especificado**: Detalhar o algoritmo de ordenacao topologica:
   - Construcao de in-degree map
   - Uso de heap/priority queue para desempate por prioridade
   - Complexidade O(V+E) garantida
   - Tratamento de ciclos (deve retornar erro se ciclo encontrado)

6. **Calculo de dias uteis especificado**: Detalhar algoritmo para:
   - Verificar se data e dia util (nao fim de semana, nao feriado)
   - Avancar N dias uteis a partir de uma data
   - Contar dias uteis entre duas datas
   - Ajustar data para proximo dia util

7. **Feriados brasileiros detalhados**: Especificar lista completa de feriados 2026-2028
   conforme Apendice A do SRS. Definir estrutura de dados (frozenset de dates, constantes,
   ou classe).

8. **Mensagens de erro exatas**: Toda validacao deve especificar a mensagem de erro
   literal (sem acentos, conforme §8.2 do SRS).

9. **Testabilidade**: Cada FR deve ser verificavel por um teste unitario ou de integracao
   especifico. A spec deve tornar trivial derivar os testes. Incluir exemplos de cenarios
   para testes unitarios (CT-004 como referencia).

10. **Sem sobreposicao com EP-001 a EP-005 ou EP-007+**: Nao re-especificar o que epicos
    anteriores ja entregaram (schema, repositorios, entidades, DependencyService). Nao
    antecipar alocacao de desenvolvedores (EP-007) ou interface grafica (EP-008).

11. **Consistencia de nomenclatura**: Usar os mesmos nomes de classe, metodo e campo ja
    existentes no codigo. Reutilizar DependencyService.build_graph() para construcao do grafo.

12. **Operacoes assincronas**: Use cases devem ser `async`, consistente com os repositorios
    baseados em aiosqlite. O dominio puro (SchedulingService) deve ser sincrono.

13. **Performance**: O algoritmo de ordenacao topologica deve suportar 500 historias com
    tempo aceitavel. Evitar reconstruir grafo a cada operacao; considerar cache se necessario.

14. **Padrao EP-005 como referencia**: Seguir o mesmo padrao arquitetural de DependencyService,
    Use Cases e DTOs do epico anterior para garantir consistencia na codebase.
</rules>
