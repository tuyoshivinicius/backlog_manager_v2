# Prompt: Criar Especificacao Tecnica do EP-005

<role>
Voce e um Arquiteto de Software Senior especializado em Domain-Driven Design (DDD) e
Clean Architecture, com profundo conhecimento em:
- Algoritmos de grafos (DFS, deteccao de ciclos, ordenacao topologica)
- Domain Services para validacao de invariantes de grafo de dependencias
- Application Layer com Use Cases, DTOs (Pydantic) e coordenacao de repositorios
- Padroes Repository e Unit of Work em Python assincrono (async/await)
- Tratamento de excecoes de dominio com informacoes ricas (path do ciclo, waves envolvidas)

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

### Estado Atual do Codigo (Implementado em EP-001 a EP-004)

As camadas de dominio, infraestrutura e aplicacao ja possuem implementacao funcional para
**historias, desenvolvedores e features**. EP-005 constroi o **sistema de gestao de dependencias**
sobre os mesmos alicerces arquiteturais.

**Entidades existentes (dominio):**
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com id (str, formato COMPONENTE-NNN), component, name, story_points, priority, status, duration, start_date, end_date, developer_id (int | None), feature_id (int | None). **Nota**: dependencias NAO sao armazenadas na entidade; sao gerenciadas pela tabela Story_Dependency.
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com id (auto-increment, int | None), name (max 100, nao vazio).
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com name (max 100, unico, nao vazio), wave (int > 0), id (auto-increment, int | None).

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados do workflow

**Excecoes existentes (hierarquia completa):**
- `BacklogManagerException` (base) em `domain/exceptions/base.py`
- `DependencyException` -> `CyclicDependencyException(path: list[str])`, `InvalidWaveDependencyException(story_id, depends_on_id, story_wave, depends_on_wave)` em `domain/exceptions/dependency.py`
- `FeatureException` -> `DuplicateWaveException`, `FeatureHasStoriesException`
- `AllocationException` -> `MaxIterationsExceeded`
- `BacklogWarning` -> `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo`

**Repository Protocols existentes (em `src/backlog_manager/domain/interfaces/repositories.py`):**
- `StoryRepository(Protocol)` — add, get_by_id, get_all, get_by_status, get_by_developer, get_by_feature, update, delete, exists, get_max_id_number, get_max_priority, get_by_priority, count_by_developer
- `StoryDependencyRepository(Protocol)` — add, remove, get_dependencies, get_dependents, exists, get_all_dependencies, remove_all_for_story
- `DeveloperRepository(Protocol)` — add, get_by_id, get_all, update, delete, exists
- `FeatureRepository(Protocol)` — add, get_by_id, get_by_wave, get_all, update, delete, exists, has_stories, get_by_name
- `UnitOfWork(Protocol)` — stories, developers, features, dependencies, commit, rollback, __aenter__, __aexit__

**Implementacao SQLite de StoryDependencyRepository (em `infrastructure/database/repositories/story_dependency_repository.py`):**
- `add(story_id, depends_on_id)` — valida auto-dependencia, verifica duplicata, insere na tabela. **NAO valida ciclos** (apenas verifica story_id == depends_on_id).
- `remove(story_id, depends_on_id)` — remove dependencia existente ou levanta ValueError.
- `get_dependencies(story_id)` — retorna lista de IDs das quais story_id depende.
- `get_dependents(story_id)` — retorna lista de IDs que dependem de story_id.
- `exists(story_id, depends_on_id)` — verifica existencia da dependencia.
- `get_all_dependencies()` — retorna todas as tuplas (story_id, depends_on_id).
- `remove_all_for_story(story_id)` — remove todas as dependencias onde story_id aparece.

**StoryService existente (EP-003):**
- `src/backlog_manager/domain/services/story_service.py` — generate_story_id, get_next_priority, create_story, swap_priorities, validate_can_move_up, validate_can_move_down, duplicate_story. Recebe StoryRepository como dependencia.

**DeveloperService existente (EP-004):**
- `src/backlog_manager/domain/services/developer_service.py` — logica de negocio para desenvolvedores.

**FeatureService existente (EP-004):**
- `src/backlog_manager/domain/services/feature_service.py` — logica de negocio para features, incluindo validacao de unicidade de wave.

**Use Cases existentes (EP-003/EP-004):**
- Story: CreateStory, EditStory, DeleteStory, DuplicateStory, ListStories, MovePriority, AssignDeveloper
- Developer: CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers
- Feature: CreateFeature, UpdateFeature, DeleteFeature, ListFeatures

**Camadas que EP-005 deve criar/estender:**
- `src/backlog_manager/domain/services/dependency_service.py` — DependencyService (domain service) com algoritmo DFS para deteccao de ciclos, validacao cross-wave
- `src/backlog_manager/application/use_cases/dependency/` — Use cases para operacoes de dependencia
- `src/backlog_manager/application/dto/dependency/` — DTOs Pydantic para dependencias

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Deteccao de ciclos — repositorio vs. servico**: O `StoryDependencyRepository.add()` atual apenas valida auto-dependencia (`story_id == depends_on_id`), mas NAO detecta ciclos indiretos (A->B->C->A). O epic EP-005 exige deteccao de ciclos via DFS com complexidade O(V+E) antes de permitir a insercao. -> A spec deve decidir se (a) a deteccao de ciclo fica no DependencyService e o repositorio apenas persiste, (b) a deteccao fica no repositorio (requer acesso a todo o grafo), ou (c) o use case coordena a deteccao antes de chamar o repositorio. Documentar trade-offs de responsabilidade entre camadas.

2. **Validacao de existencia de historias**: O RF-DEP-001 exige que "Dependencia deve existir no backlog". O repositorio atual NAO valida se as historias existem (assume FKs do banco). -> A spec deve definir se a validacao de existencia fica no (a) DependencyService via StoryRepository.exists(), (b) use case antes de chamar o servico, ou (c) banco de dados via FK constraint (falha com IntegrityError). Considerar mensagens de erro claras vs. simplicidade.

3. **Obtencao de wave da historia para validacao cross-wave**: RF-DEP-004 exige validar se historia depende de onda posterior. A wave de uma historia e derivada da feature associada (story.feature_id -> feature.wave). Historia sem feature tem wave=0. -> A spec deve definir como o DependencyService obtem a wave: (a) receber wave como parametro do use case (pre-calculado), (b) receber FeatureRepository como dependencia do servico, (c) consultar Feature via UnitOfWork. Documentar como calcular wave=0 para historias sem feature.

4. **Comportamento do warning InvalidWaveDependencyException**: O epic diz "alertar via InvalidWaveDependencyException quando depende de onda posterior" e o RF-DEP-004 diz "warning (nao bloqueante)". Isso significa que a dependencia deve ser adicionada mesmo com o warning? -> A spec deve definir se (a) adiciona dependencia e retorna/emite warning, (b) adiciona dependencia e lanca excecao (caller decide), (c) adiciona dependencia e loga warning. Documentar o comportamento esperado pelo caller.

5. **Formato do caminho do ciclo na excecao**: O SRS (§7.3 e UC-003) mostra exemplos como ["A","B","C","A"] onde o primeiro e ultimo elementos sao o mesmo (inicio do ciclo). A `CyclicDependencyException` existente ja aceita `path: list[str]`. -> A spec deve especificar exatamente como construir o path: iniciando pelo no que fecha o ciclo, em qual direcao, e garantindo que o path seja util para o usuario entender o problema.

6. **DependencyService vs. extensao do StoryService**: O epic menciona apenas DependencyService, mas a gestao de dependencias esta relacionada a historias. -> A spec deve decidir se (a) criar DependencyService separado (recomendado, SRP), (b) estender StoryService com metodos de dependencia, ou (c) criar ambos e coordenar no use case. Considerar coesao e responsabilidade unica.

7. **Operacoes bulk de dependencias**: O epic foca em adicionar/remover dependencias individuais. O RF-STORY-003 (deletar historia) ja remove dependencias via `remove_all_for_story()`. -> A spec deve confirmar que EP-005 NAO implementa operacoes bulk (ja cobertas em EP-003) e documentar a divisao de responsabilidade.

8. **Integridade transacional em adicao de dependencia**: Adicionar uma dependencia envolve: (1) validar existencia das historias, (2) detectar ciclos (requer leitura do grafo completo), (3) validar waves, (4) persistir. -> A spec deve definir se toda a operacao usa UnitOfWork para garantir atomicidade, ou se algumas validacoes podem ocorrer fora da transacao. Considerar que deteccao de ciclo e read-only.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-005_gestao-de-dependencias.md` — requisitos, escopo, criterios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — secoes §3.4 RF-DEP-001 a 004, §5 UC-003 (Detectar e Resolver Deadlock), §6.3 (Grafo de Dependencias), §7.3 (excecoes CyclicDependencyException, InvalidWaveDependencyException), §8.2 (convencoes), §8.3 (regras implicitas)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios arquiteturais obrigatorios (Clean Architecture, DDD, async, tratamento de erros, etc.)
4. **Spec de referencia (predecessor)**: `specs/003-ep003-backlog-services/spec.md` — formato, nivel de detalhe e padrao de User Stories/Acceptance Scenarios esperado
5. **Contracts de referencia**: `specs/003-ep003-backlog-services/contracts/` ou `specs/004-ep004-resource-services/contracts/` — formato dos contratos de servico, DTOs e use cases
6. **Repository Protocol existente**: `src/backlog_manager/domain/interfaces/repositories.py` — StoryDependencyRepository, StoryRepository, FeatureRepository, UnitOfWork
7. **Excecoes de dependencia existentes**: `src/backlog_manager/domain/exceptions/dependency.py` — CyclicDependencyException, InvalidWaveDependencyException (para reutilizacao)
8. **Implementacao atual do StoryDependencyRepository**: `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py` — para entender o que ja esta implementado vs. o que falta
9. **StoryService existente**: `src/backlog_manager/domain/services/story_service.py` — para entender o padrao de domain service e nao duplicar funcionalidades
10. **Entidade Story**: `src/backlog_manager/domain/entities/story.py` — para entender campos disponiveis (feature_id para derivar wave)
11. **Entidade Feature**: `src/backlog_manager/domain/entities/feature.py` — para entender campo wave
12. **Use Cases de Story (EP-003)**: `src/backlog_manager/application/use_cases/story/` — para seguir o mesmo padrao arquitetural (ex: DeleteStory que chama remove_all_for_story)
13. **DTOs de Story (EP-003)**: `src/backlog_manager/application/dto/story/` — para seguir o mesmo padrao de DTOs
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-005 — Gestao de Dependencias`.

A especificacao deve cobrir **exclusivamente** o escopo do epico:
- RF-DEP-001: Adicionar Dependencia entre Historias (validar existencia, sem auto-dependencia, sem ciclo)
- RF-DEP-002: Remover Dependencia (simples remocao da relacao)
- RF-DEP-003: Detectar Ciclos de Dependencia (algoritmo DFS O(V+E), lancar CyclicDependencyException com path)
- RF-DEP-004: Validar Dependencias entre Ondas (alertar via InvalidWaveDependencyException quando depende de onda posterior)

**IMPORTANTE**: Este epico **nao** cria entidades, repositorios base ou excecoes do zero. Ele
**constroi a camada de servico e aplicacao** para gestao de dependencias sobre a infraestrutura
ja existente (EP-001 a EP-004), orquestrando:

- **DependencyService** (domain service): regras de negocio — deteccao de ciclos via DFS, validacao de existencia de historias, validacao cross-wave, construcao do path do ciclo
- **Use Cases** (application layer): coordenacao de UnitOfWork + DependencyService + repositorios, um use case por operacao (AddDependency, RemoveDependency, GetDependencies, GetDependents)
- **DTOs Pydantic** (application layer): input/output para cada operacao
- **Extensoes aos Protocols** (se necessario): novos metodos em StoryDependencyRepository ou StoryRepository para suportar operacoes que o servico necessite e que nao existam ainda

O cenario de teste CT-002 (Deteccao de Ciclo em Grafo Grande com 50 nos < 100ms) e o UC-003 (Detectar e Resolver Deadlock) devem ser **executaveis** apos este epico.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF do epico EP-005
   (RF-DEP-001 a 004). Todo RF do escopo deve ter pelo menos um FR correspondente. Incluir
   matriz de rastreabilidade.

2. **Codigo existente prevalece como baseline**: Nao redefinir entidades, value objects,
   excecoes ou repositorios ja implementados. Especificar apenas **extensoes** (novos metodos
   nos Protocols, se necessario) e **novos artefatos** (DependencyService, Use Cases, DTOs).

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Separacao de responsabilidades clara**: Definir com precisao o que fica no Domain Service
   (regras de negocio puras, algoritmo DFS) vs. Application Use Case (coordenacao, UnitOfWork,
   DTOs) vs. Repository (acesso a dados). O DependencyService deve ser **sincrono** no dominio
   puro (receber grafo como parametro) ou **assincrono** se precisar consultar repositorios.

5. **Algoritmo DFS especificado**: Detalhar o algoritmo de deteccao de ciclos:
   - Estados dos nos (WHITE/GRAY/BLACK ou equivalente)
   - Construcao do caminho do ciclo
   - Complexidade O(V+E) garantida
   - Implementacao iterativa vs. recursiva (considerar stack overflow para grafos profundos)

6. **Mensagens de erro exatas**: Toda validacao no servico deve especificar a mensagem de erro
   literal (sem acentos, conforme §8.2 do SRS). Reutilizar excecoes existentes
   (`CyclicDependencyException`, `InvalidWaveDependencyException`) passando os parametros corretos.

7. **Testabilidade**: Cada FR deve ser verificavel por um teste unitario ou de integracao
   especifico. A spec deve tornar trivial derivar os testes. Incluir exemplos de cenarios
   para testes unitarios do DFS.

8. **Sem sobreposicao com EP-001 a EP-004 ou EP-006+**: Nao re-especificar o que epicos
   anteriores ja entregaram (schema, repositorios base, entidades, StoryService). Nao
   antecipar ordenacao topologica para cronograma (EP-006), processamento de dependencias
   na alocacao (EP-007), ou interface grafica (EP-008).

9. **Consistencia de nomenclatura**: Usar os mesmos nomes de classe, metodo e campo ja
   existentes no codigo. Se um novo metodo precisa ser adicionado a um Protocol existente,
   documentar como extensao retrocompativel.

10. **Operacoes assincronas**: Use cases devem ser `async`, consistente com os repositorios
    baseados em aiosqlite. O dominio puro (algoritmo DFS) pode ser sincrono se receber os
    dados necessarios como parametro, ou assincrono se precisar consultar repositorios.

11. **Integridade transacional**: Operacoes que envolvem multiplas escritas (verificar ciclo
    + adicionar dependencia) devem usar UnitOfWork para garantir atomicidade. Validacoes
    read-only (deteccao de ciclo) podem ocorrer antes de iniciar a transacao.

12. **Performance CT-002**: O algoritmo de deteccao de ciclos deve suportar grafo de 50 nos
    com tempo < 100ms. Evitar recriar estruturas de dados a cada adicao; considerar se o
    servico pode receber o grafo pre-construido ou se constroi sob demanda.

13. **Padrao EP-003/EP-004 como referencia**: Seguir o mesmo padrao arquitetural de StoryService,
    DeveloperService, FeatureService, Use Cases e DTOs dos epicos anteriores para garantir
    consistencia na codebase. Os novos servicos e use cases devem ser estruturalmente analogos
    aos existentes.
</rules>
