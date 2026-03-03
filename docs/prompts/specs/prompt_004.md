# Prompt: Criar Especificação Técnica do EP-004

<role>
Você é um Arquiteto de Software Sênior especializado em Domain-Driven Design (DDD) e
Clean Architecture, com profundo conhecimento em:
- Design de Domain Services com orquestração de regras de negócio e invariantes de integridade referencial
- Application Layer com Use Cases, DTOs (Pydantic) e coordenação de repositórios
- Padrões Repository e Unit of Work em Python assíncrono (async/await)
- Modelagem de operações CRUD com proteção contra deleção em cascata e validação de unicidade cross-entidade

Você produz especificações técnicas prescritivas, rastreáveis a requisitos, e implementáveis
de forma incremental sem decisões ambíguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicação desktop standalone em Python (PySide6 + SQLite) para gestão de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Técnica (Definida em EP-001)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **Persistência**: aiosqlite (async SQLite)
- **DTOs**: Pydantic
- **Testes**: pytest + pytest-cov + pytest-asyncio
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation → Infrastructure → Application → Domain
- **Padrões**: Repository Pattern (Protocol), Unit of Work, DDD (entidades ricas, VOs, serviços de domínio)

### Estado Atual do Código (Implementado em EP-001, EP-002 e EP-003)

As camadas de domínio, infraestrutura e aplicação já possuem implementação funcional para
**histórias**. EP-004 constrói a **camada de serviço e aplicação para desenvolvedores e features**
sobre os mesmos alicerces arquiteturais.

**Entidades existentes (domínio):**
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com id (auto-increment, int | None), name (max 100, não vazio). Validações no `__post_init__`.
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com name (max 100, único, não vazio), wave (int > 0), id (auto-increment, int | None). Validações no `__post_init__`.
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com developer_id (int | None) e feature_id (int | None) como FKs.

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados do workflow

**Exceções existentes (hierarquia completa):**
- `BacklogManagerException` (base) em `domain/exceptions/base.py`
- `FeatureException` → `DuplicateWaveException`, `FeatureHasStoriesException` em `domain/exceptions/feature.py`
- `DependencyException` → `CyclicDependencyException`, `InvalidWaveDependencyException`
- `AllocationException` → `MaxIterationsExceeded`
- `BacklogWarning` → `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo`

**Repository Protocols existentes (em `src/backlog_manager/domain/interfaces/repositories.py`):**
- `DeveloperRepository(Protocol)` — add (retorna int), get_by_id, get_all, update, delete (note: ON DELETE SET NULL no schema), exists
- `FeatureRepository(Protocol)` — add (retorna int, raises DuplicateWaveException), get_by_id, get_by_wave, get_all, update (raises DuplicateWaveException), delete (raises FeatureHasStoriesException), exists, has_stories
- `StoryRepository(Protocol)` — add, get_by_id, get_all, get_by_status, get_by_developer, get_by_feature, update, delete, exists, get_max_id_number, get_max_priority, get_by_priority
- `StoryDependencyRepository(Protocol)` — add, remove, get_dependencies, get_dependents, exists, get_all_dependencies, remove_all_for_story
- `UnitOfWork(Protocol)` — stories, developers, features, dependencies, commit, rollback, __aenter__, __aexit__

**Implementações SQLite dos repositórios:** em `src/backlog_manager/infrastructure/database/repositories/`
- `developer_repository.py`, `feature_repository.py`, `story_repository.py`, `story_dependency_repository.py`

**StoryService existente (EP-003):**
- `src/backlog_manager/domain/services/story_service.py` — generate_story_id, calculate_initial_priority, create_story, update_story, delete_story, duplicate_story, move_priority, assign_developer, list_stories. Recebe StoryRepository como dependência.

**Use Cases existentes (EP-003) para Story:**
- `src/backlog_manager/application/use_cases/story/` — CreateStory, EditStory, DeleteStory, DuplicateStory, ListStories, MovePriority, AssignDeveloper. Cada um recebe UnitOfWork factory.

**DTOs existentes (EP-003) para Story:**
- `src/backlog_manager/application/dto/story/` — CreateStoryDTO, EditStoryDTO, StoryOutputDTO

**Camadas VAZIAS que EP-004 deve preencher:**
- `src/backlog_manager/domain/services/` — DeveloperService e/ou FeatureService (regras de negócio de recursos)
- `src/backlog_manager/application/use_cases/` — Use cases para Developer e Feature
- `src/backlog_manager/application/dto/` — DTOs Pydantic para Developer e Feature

### ⚠️ Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificação com decisão explícita:

1. **Desalocação de histórias ao deletar desenvolvedor — banco vs. serviço**: O schema SQLite define `ON DELETE SET NULL` na FK `developer_id` da tabela Story, ou seja, o banco já faz a desalocação automaticamente ao deletar o desenvolvedor. O épico EP-004 exige "desalocar histórias antes" de deletar (RF-DEV-003), sugerindo lógica explícita no serviço. → A spec deve decidir se (a) confia no `ON DELETE SET NULL` do banco e o serviço apenas deleta, (b) o serviço desaloca explicitamente antes de deletar (para fins de logging/auditoria/eventos), ou (c) ambos (serviço desaloca para logging, banco garante como fallback). Documentar trade-offs.

2. **Proteção contra deleção de feature — repositório vs. serviço**: O protocol `FeatureRepository.delete()` já documenta que lança `FeatureHasStoriesException`. A implementação SQLite provavelmente verifica via `has_stories()`. → A spec deve definir se a validação fica exclusivamente no repositório (como está), se o serviço faz a verificação ANTES de chamar delete (fail-fast com mensagem controlada), ou se há dupla verificação. Documentar a decisão.

3. **Validação de unicidade de wave — repositório vs. serviço**: `FeatureRepository.add()` e `update()` já lançam `DuplicateWaveException`. → A spec deve decidir se o serviço valida unicidade antes (via `get_by_wave()`) ou delega ao repositório. Considerar que validar no serviço permite mensagens de erro mais ricas e fail-fast antes de tentativa de persistência.

4. **Validação de unicidade de nome de feature**: O épico menciona "nome único" para Feature (RF-FEAT-002). O repositório `add()` levanta `ValueError: Se nome ja existe`, mas não há um método explícito `get_by_name()` no protocol. → A spec deve decidir se adiciona `get_by_name(name: str) -> Feature | None` ao protocol para validação no serviço, ou se delega ao repositório/banco.

5. **Associação de histórias a features (RF-FEAT-004)**: O épico exige "Associar Histórias a Features". EP-003 já implementou `StoryService.update_story(..., feature_id=...)` que permite alterar o feature_id de uma história. → A spec deve decidir se EP-004 reutiliza essa funcionalidade existente (delegando ao StoryService via use case), se cria um método no FeatureService que coordena a associação (ex: `associate_story(feature_id, story_id)`), ou se é apenas um cenário de uso documentado sem novo código.

6. **Wave=0 para história sem feature**: A regra §8.3 do SRS diz "história sem feature → wave=0". Isso é um valor computado (read-time) ou armazenado? → A spec deve definir se wave=0 é uma propriedade derivada ao consultar (Feature.wave ou 0 se feature_id=None), ou se é persistido na tabela Story. Isso impacta se o FeatureService precisa de lógica adicional ou se fica na camada de apresentação.

7. **Contagem de histórias ao deletar feature**: RF-FEAT-003 exige "Deletar Feature somente se sem histórias". A informação "quantas histórias tem esta feature" é útil para a mensagem de erro. → A spec deve decidir se `FeatureHasStoriesException` inclui a contagem ou apenas o ID da feature, e se é necessário um método `count_stories(feature_id)` no `StoryRepository` ou `FeatureRepository`.

8. **Desenvolvedor sem validação de nome único**: O épico não menciona unicidade de nomes de desenvolvedores (diferente de Feature.name que é UNIQUE). → Confirmar que nomes duplicados são permitidos para desenvolvedores. Se sim, documentar explicitamente.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificação:

1. **Épico fonte**: `docs/epics/EP-004_gestao-de-recursos.md` — requisitos, escopo, critérios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — seções §2.2 (capacidades 2 e 3), §6.1 (arquitetura), §6.4 (modelo ER — tabelas Developer e Feature), §7.3 (exceções DuplicateWaveException, FeatureHasStoriesException), §8.2 (convenções), §8.3 (regras implícitas — wave=0 para história sem feature, onda mínima=1)
3. **Constituição do projeto**: `.specify/memory/constitution.md` — princípios arquiteturais obrigatórios (Clean Architecture, DDD, async, etc.)
4. **Spec de referência (predecessor)**: `specs/003-ep003-backlog-services/spec.md` — formato, nível de detalhe e padrão de ADRs esperado
5. **Plan de referência**: `specs/001-ep001-foundation-persistence/plan.md` — estrutura do plano de implementação
6. **Tasks de referência**: `specs/001-ep001-foundation-persistence/tasks.md` — formato das tasks
7. **Contracts de referência (EP-003)**: `specs/003-ep003-backlog-services/contracts/` — formato dos contratos de serviço, DTOs e use cases
8. **Repository Protocols existentes**: `src/backlog_manager/domain/interfaces/repositories.py` — DeveloperRepository, FeatureRepository, StoryRepository, UnitOfWork (para entender o que já existe e decidir extensões)
9. **Entidades existentes**:
   - `src/backlog_manager/domain/entities/developer.py` — Developer com validações atuais
   - `src/backlog_manager/domain/entities/feature.py` — Feature com validações atuais
   - `src/backlog_manager/domain/entities/story.py` — Story com campos developer_id e feature_id
10. **StoryService existente**: `src/backlog_manager/domain/services/story_service.py` — para entender o padrão de domain service e não duplicar funcionalidades
11. **Use Cases de Story (EP-003)**: `src/backlog_manager/application/use_cases/story/` — para seguir o mesmo padrão arquitetural
12. **DTOs de Story (EP-003)**: `src/backlog_manager/application/dto/story/` — para seguir o mesmo padrão de DTOs
13. **Exceções de Feature**: `src/backlog_manager/domain/exceptions/feature.py` — DuplicateWaveException, FeatureHasStoriesException (para reutilização)
14. **Implementações SQLite dos repositórios**: `src/backlog_manager/infrastructure/database/repositories/developer_repository.py` e `feature_repository.py` — para entender o que já está implementado vs. o que falta
</input>

<task>
Crie a **especificação técnica completa** para o épico `EP-004 — Gestão de Recursos: Desenvolvedores e Features`.

A especificação deve cobrir **exclusivamente** o escopo do épico:
- RF-DEV-001: Cadastrar Novo Desenvolvedor (nome obrigatório, ID auto-gerado)
- RF-DEV-002: Editar Desenvolvedor (alterar nome)
- RF-DEV-003: Deletar Desenvolvedor (desalocar histórias associadas)
- RF-DEV-004: Listar Desenvolvedores
- RF-FEAT-001: Criar Nova Feature (nome único, onda > 0, onda única)
- RF-FEAT-002: Editar Feature (validar unicidade de nome e onda)
- RF-FEAT-003: Deletar Feature (somente se sem histórias associadas)
- RF-FEAT-004: Associar Histórias a Features (1 história : 1 feature, sem feature → wave=0)
- RF-FEAT-005: Validar Onda Única (rejeitar duplicata com DuplicateWaveException)

**IMPORTANTE**: Este épico **não** cria entidades, repositórios ou exceções do zero. Ele
**constrói a camada de serviço e aplicação** para Developer e Feature sobre a infraestrutura
já existente (EP-001), as entidades validadas (EP-002), e seguindo os mesmos padrões
arquiteturais de EP-003 (StoryService/Use Cases/DTOs), orquestrando:

- **DeveloperService** (domain service): regras de negócio — desalocação de histórias ao deletar desenvolvedor, validações de domínio
- **FeatureService** (domain service): regras de negócio — validação de unicidade de onda/nome, proteção contra deleção com histórias, associação de história a feature, cálculo/derivação de wave=0
- **Use Cases** (application layer): coordenação de UnitOfWork + Services + DTOs, um use case por operação CRUD
- **DTOs Pydantic** (application layer): input/output para cada operação CRUD de Developer e Feature
- **Extensões aos Protocols** (se necessário): novos métodos em DeveloperRepository, FeatureRepository ou StoryRepository para suportar operações que o serviço necessite e que não existam ainda
</task>

<rules>
### Regras de Qualidade da Especificação

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF do épico EP-004
   (RF-DEV-001 a 004, RF-FEAT-001 a 005). Todo RF do escopo deve ter pelo menos um FR
   correspondente. Incluir matriz de rastreabilidade.

2. **Código existente prevalece como baseline**: Não redefinir entidades, value objects,
   exceções ou repositórios já implementados. Especificar apenas **extensões** (novos métodos
   nos Protocols, se necessário) e **novos artefatos** (DeveloperService, FeatureService,
   Use Cases, DTOs).

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na seção
   `⚠️ Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma seção
   "Decisão Arquitetural" (ADR) com: Contexto, Opções, Decisão, Justificativa.

4. **Separação de responsabilidades clara**: Definir com precisão o que fica no Domain Service
   (regras de negócio puras) vs. Application Use Case (coordenação, UnitOfWork, DTOs) vs.
   Repository (acesso a dados). Em particular, clarificar o que o serviço valida vs. o que
   já é validado pelo repositório existente.

5. **Mensagens de erro exatas**: Toda validação no serviço deve especificar a mensagem de erro
   literal (sem acentos, conforme §8.2 do SRS). Reutilizar exceções existentes
   (`DuplicateWaveException`, `FeatureHasStoriesException`) quando aplicável.

6. **Testabilidade**: Cada FR deve ser verificável por um teste unitário ou de integração
   específico. A spec deve tornar trivial derivar os testes.

7. **Sem sobreposição com EP-001/EP-002/EP-003 ou EP-005+**: Não re-especificar o que épicos
   anteriores já entregaram (schema, repositórios base, entidades, StoryService). Não
   antecipar gestão de dependências (EP-005), cálculo de cronograma (EP-006) ou alocação
   automática (EP-007).

8. **Consistência de nomenclatura**: Usar os mesmos nomes de classe, método e campo já
   existentes no código. Se um novo método precisa ser adicionado a um Protocol existente,
   documentar como extensão retrocompatível.

9. **Operações assíncronas**: Todo método de serviço e use case deve ser `async`, consistente
   com os repositórios baseados em aiosqlite. O domínio puro (entidades, VOs) permanece
   síncrono conforme Princípio VIII da Constituição.

10. **Integridade transacional**: Operações que envolvem múltiplas escritas (ex: desalocar
    histórias + deletar desenvolvedor, verificar histórias + deletar feature) devem usar
    UnitOfWork para garantir atomicidade.

11. **Padrão EP-003 como referência**: Seguir o mesmo padrão arquitetural de StoryService,
    Use Cases e DTOs de EP-003 para garantir consistência na codebase. Os novos serviços
    e use cases devem ser estruturalmente análogos aos existentes.
</rules>
