# Prompt: Criar Especificação Técnica do EP-003

<role>
Você é um Arquiteto de Software Sênior especializado em Domain-Driven Design (DDD) e
Clean Architecture, com profundo conhecimento em:
- Design de Domain Services com orquestração de regras de negócio
- Application Layer com Use Cases, DTOs (Pydantic) e coordenação de repositórios
- Padrões Repository e Unit of Work em Python assíncrono (async/await)
- Modelagem de operações CRUD com invariantes de domínio (priorização, geração de IDs, integridade referencial)

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

### Estado Atual do Código (Implementado em EP-001 e EP-002)

As camadas de domínio e infraestrutura já possuem implementação funcional. EP-003 constrói
**a camada de serviço e aplicação** sobre esses alicerces.

**Entidades existentes (domínio):**
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com validações de ID (COMPONENTE-NNN), component, name, story_points ∈ {3,5,8,13}, priority ≥ 0, duration, datas. Não possui campo `dependencies` (dependências são gerenciadas via tabela separada).
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com id (auto-increment), name (max 100).
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com name, wave > 0, id opcional.

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` com valores {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados do workflow

**Exceções existentes:**
- Hierarquia completa em `src/backlog_manager/domain/exceptions/` — BacklogManagerException, DependencyException, FeatureException, AllocationException e warnings

**Repository Protocols existentes (em `src/backlog_manager/domain/interfaces/repositories.py`):**
- `StoryRepository(Protocol)` — add, get_by_id, get_all, get_by_status, get_by_developer, get_by_feature, update, delete, exists
- `DeveloperRepository(Protocol)` — add, get_by_id, get_all, update, delete, exists
- `FeatureRepository(Protocol)` — add, get_by_id, get_by_wave, get_all, update, delete, exists, has_stories
- `StoryDependencyRepository(Protocol)` — add, remove, get_dependencies, get_dependents, exists, get_all_dependencies
- `UnitOfWork(Protocol)` — stories, developers, features, dependencies, commit, rollback

**Implementações SQLite dos repositórios:** em `src/backlog_manager/infrastructure/database/repositories/`

**Camadas VAZIAS que EP-003 deve preencher:**
- `src/backlog_manager/domain/services/` — StoryService (regras de negócio de backlog)
- `src/backlog_manager/application/use_cases/` — Use cases para cada operação
- `src/backlog_manager/application/dto/` — DTOs Pydantic para input/output das operações
- `src/backlog_manager/application/interfaces/` — Interfaces da camada de aplicação

### ⚠️ Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificação com decisão explícita:

1. **StoryDependencyRepository sem remoção em lote**: O protocolo atual tem `remove(story_id, depends_on_id)` para pares individuais, mas RF-STORY-003 exige "remover referências de dependências" ao deletar uma história. → A spec deve decidir se adiciona um método `remove_all_for_story(story_id)` ao protocolo ou se o serviço itera manualmente.

2. **StoryRepository sem query de próximo ID**: A geração automática de IDs (COMPONENTE-NNN) exige consultar o maior número existente para aquele componente. O protocolo atual não tem método para isso. → A spec deve decidir se adiciona `get_next_id(component: str) -> str` ao repositório ou se o serviço orquestra via `get_all()`.

3. **StoryRepository sem query por prioridade adjacente**: RF-STORY-006 (mover prioridade cima/baixo) requer encontrar a história adjacente em prioridade. → A spec deve decidir o mecanismo: método novo no repositório ou lógica no serviço.

4. **Validação de developer_id na atribuição manual**: EP-003 diz "validar existência" (RF-STORY-007), mas EP-004 (CRUD de desenvolvedores) ainda não foi implementado. Os riscos do épico mencionam que validação completa depende de EP-004. → A spec deve definir o nível de validação possível agora (ex: verificar via DeveloperRepository.exists() se disponível, ou validar apenas formato).

5. **Prioridade inicial**: Épico define "prioridade inicial = max(existentes) + 1" (§8.3). → A spec deve decidir se a lógica vive no serviço (consulta max e atribui) ou no repositório.

6. **Duplicação e campos de alocação**: RF-STORY-004 exige "copiar dados, limpar alocação (dev=NULL, start_date=NULL)". → A spec deve definir exatamente quais campos são copiados e quais são resetados na duplicação, e se a nova história recebe prioridade = max+1.

7. **Gaps de prioridade**: O épico lista como risco "Prioridades são sempre contíguas (1, 2, 3...)" com mitigação "Implementar reordenação se houver gaps". → A spec deve decidir se implementa compactação de prioridades ou se garante contiguidade por invariante.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificação:

1. **Épico fonte**: `docs/epics/EP-003_gestao-de-backlog.md` — requisitos, escopo, critérios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — seções §2.2 (capacidades), §6.1 (arquitetura), §6.4 (modelo ER), §8.2 (convenções), §8.3 (regras implícitas)
3. **Spec de referência (template)**: `specs/001-ep001-foundation-persistence/spec.md` — formato e nível de detalhe esperado
4. **Plan de referência (template)**: `specs/001-ep001-foundation-persistence/plan.md` — estrutura do plano de implementação
5. **Tasks de referência (template)**: `specs/001-ep001-foundation-persistence/tasks.md` — formato das tasks
6. **Contracts de referência**: `specs/001-ep001-foundation-persistence/contracts/` — formato dos contratos (protocols, exceções)
7. **Spec EP-002 (predecessor)**: `specs/002-ep002-domain-validations/spec.md` — para entender o que EP-002 entregou
8. **Código existente dos repositórios e interfaces**:
   - `src/backlog_manager/domain/interfaces/repositories.py` — Protocols (StoryRepository, StoryDependencyRepository, UnitOfWork)
   - `src/backlog_manager/domain/entities/story.py` — Entidade Story atual
   - `src/backlog_manager/domain/entities/developer.py` — Entidade Developer atual
   - `src/backlog_manager/domain/entities/feature.py` — Entidade Feature atual
   - `src/backlog_manager/domain/services/__init__.py` — Serviços de domínio (vazio)
   - `src/backlog_manager/application/use_cases/__init__.py` — Use cases (vazio)
   - `src/backlog_manager/application/dto/__init__.py` — DTOs (vazio)
9. **Exceções disponíveis**: `src/backlog_manager/domain/exceptions/` — hierarquia completa para reutilização
</input>

<task>
Crie a **especificação técnica completa** para o épico `EP-003 — Gestão de Backlog`.

A especificação deve cobrir **exclusivamente** o escopo do épico:
- RF-STORY-001: Criar Nova História (ID auto-gerado COMPONENTE-NNN, prioridade inicial = max+1)
- RF-STORY-002: Editar História Existente (todos os campos exceto ID)
- RF-STORY-003: Deletar História (remover referências de dependências)
- RF-STORY-004: Duplicar História (novo ID, copiar dados, limpar alocação)
- RF-STORY-005: Listar Histórias do Backlog (ordenadas por prioridade)
- RF-STORY-006: Mover Prioridade (cima/baixo, troca com adjacente)
- RF-STORY-007: Atribuir Desenvolvedor Manualmente (validar existência, permitir desalocar)

**IMPORTANTE**: Este épico **não** cria entidades nem repositórios do zero. Ele **constrói a
camada de serviço e aplicação** sobre a infraestrutura já existente (EP-001) e as entidades
já validadas (EP-002), orquestrando:
- **StoryService** (domain service): regras de negócio — geração de ID, prioridade inicial, duplicação, limpeza de dependências, troca de prioridades
- **Use Cases** (application layer): coordenação de UnitOfWork + StoryService + DTOs
- **DTOs Pydantic** (application layer): input/output para cada operação CRUD
- **Extensões aos Protocols** (se necessário): novos métodos em StoryRepository ou StoryDependencyRepository para suportar operações eficientes
</task>

<rules>
### Regras de Qualidade da Especificação

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF do épico EP-003.
   Todo RF do escopo (RF-STORY-001 a 007) deve ter pelo menos um FR correspondente.

2. **Código existente prevalece como baseline**: Não redefinir entidades, value objects ou
   repositórios já implementados. Especificar apenas **extensões** (novos métodos nos Protocols)
   e **novos artefatos** (StoryService, Use Cases, DTOs).

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na seção
   `⚠️ Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma seção
   "Decisão Arquitetural" com: Contexto, Opções, Decisão, Justificativa.

4. **Separação de responsabilidades clara**: Definir com precisão o que fica no Domain Service
   (regras de negócio puras) vs. Application Use Case (coordenação, UnitOfWork, DTOs).

5. **Mensagens de erro exatas**: Toda validação no serviço deve especificar a mensagem de erro
   literal (sem acentos, conforme §8.2 do SRS).

6. **Testabilidade**: Cada FR deve ser verificável por um teste unitário ou de integração
   específico. A spec deve tornar trivial derivar os testes.

7. **Sem sobreposição com EP-001/EP-002 ou EP-004+**: Não re-especificar o que EP-001 (schema,
   repositórios base) ou EP-002 (validações de entidade) já entregaram. Não antecipar CRUD
   de desenvolvedores/features (EP-004) nem gestão de dependências avançada (EP-005).

8. **Consistência de nomenclatura**: Usar os mesmos nomes de classe, método e campo já existentes
   no código. Se um novo método precisa ser adicionado a um Protocol existente, documentar como
   extensão retrocompatível.

9. **Operações assíncronas**: Todo método de serviço e use case deve ser `async`, consistente
   com os repositórios baseados em aiosqlite.

10. **Integridade transacional**: Operações que envolvem múltiplas escritas (ex: deletar história +
    limpar dependências, mover prioridade trocando duas histórias) devem usar UnitOfWork para
    garantir atomicidade.
</rules>
