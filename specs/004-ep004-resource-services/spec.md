# Feature Specification: EP-004 Gestao de Recursos - Servicos e Aplicacao

**Feature Branch**: `004-ep004-resource-services`
**Created**: 2026-03-01
**Status**: Draft
**Input**: Implementacao da camada de servico e aplicacao para gestao de recursos: DeveloperService, FeatureService (domain services), Use Cases, DTOs Pydantic para operacoes CRUD de Developer e Feature, construindo sobre a infraestrutura existente (EP-001), entidades validadas (EP-002), e seguindo os padroes arquiteturais de EP-003.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cadastrar Novo Desenvolvedor (Priority: P1)

Como Scrum Master, preciso cadastrar desenvolvedores no sistema para que eu possa aloca-los a historias durante o planejamento de sprints.

**Why this priority**: Desenvolvedores sao pre-requisito para alocacao de historias. Sem desenvolvedores cadastrados, o sistema nao pode executar alocacao automatica (EP-007).

**Independent Test**: Pode ser testado criando um desenvolvedor com nome valido e verificando que foi persistido com ID auto-gerado.

**Acceptance Scenarios**:

1. **Given** nenhum desenvolvedor cadastrado, **When** cadastro desenvolvedor com nome="Ana Silva", **Then** desenvolvedor e criado com ID auto-gerado (inteiro) e nome="Ana Silva"
2. **Given** desenvolvedor existente com nome="Ana", **When** cadastro outro desenvolvedor com nome="Ana", **Then** desenvolvedor e criado (nomes duplicados sao permitidos)
3. **Given** nome vazio ou apenas espacos, **When** tento cadastrar desenvolvedor, **Then** ValueError e lancado com mensagem "Nome do desenvolvedor nao pode ser vazio"
4. **Given** nome com mais de 100 caracteres, **When** tento cadastrar desenvolvedor, **Then** ValueError e lancado com mensagem "Nome do desenvolvedor nao pode exceder 100 caracteres"

---

### User Story 2 - Listar Desenvolvedores (Priority: P1)

Como Scrum Master, preciso visualizar todos os desenvolvedores cadastrados para ter visao do time disponivel para alocacao.

**Why this priority**: Listagem e essencial para qualquer operacao de gerenciamento. E a base para selecao em atribuicao manual de historias.

**Independent Test**: Pode ser testado cadastrando multiplos desenvolvedores e verificando que todos sao retornados ordenados por nome.

**Acceptance Scenarios**:

1. **Given** desenvolvedores "Carlos", "Ana", "Bruno" cadastrados, **When** listo desenvolvedores, **Then** retornam na ordem "Ana", "Bruno", "Carlos" (ordem alfabetica)
2. **Given** nenhum desenvolvedor cadastrado, **When** listo desenvolvedores, **Then** retorna lista vazia
3. **Given** 10 desenvolvedores cadastrados, **When** listo todos, **Then** todos os 10 sao retornados

---

### User Story 3 - Editar Nome de Desenvolvedor (Priority: P1)

Como Scrum Master, preciso alterar o nome de um desenvolvedor para corrigir erros ou atualizar informacoes.

**Why this priority**: Edicao permite manutencao de dados. E operacao basica de CRUD.

**Independent Test**: Pode ser testado editando o nome de um desenvolvedor existente e verificando que a alteracao persistiu.

**Acceptance Scenarios**:

1. **Given** desenvolvedor com id=1 e nome="Ana", **When** edito nome para "Ana Silva", **Then** desenvolvedor.name == "Ana Silva" e desenvolvedor.id == 1 (imutavel)
2. **Given** desenvolvedor inexistente com id=999, **When** tento editar, **Then** ValueError e lancado com mensagem "Desenvolvedor nao encontrado: 999"
3. **Given** novo nome vazio, **When** tento editar, **Then** ValueError e lancado com mensagem "Nome do desenvolvedor nao pode ser vazio"

---

### User Story 4 - Deletar Desenvolvedor com Desalocacao (Priority: P1)

Como Scrum Master, preciso remover desenvolvedores que deixaram o time, garantindo que as historias associadas sejam automaticamente desalocadas.

**Why this priority**: Delecao com desalocacao garante integridade referencial. Historias nao podem apontar para desenvolvedor inexistente.

**Independent Test**: Pode ser testado deletando um desenvolvedor que tem historias alocadas e verificando que as historias ficam com developer_id=NULL.

**Acceptance Scenarios**:

1. **Given** desenvolvedor id=1 sem historias alocadas, **When** deleto desenvolvedor, **Then** desenvolvedor e removido do sistema
2. **Given** desenvolvedor "Ana" com 3 historias alocadas, **When** deleto Ana, **Then** Ana e removida e as 3 historias tem developer_id=NULL
3. **Given** desenvolvedor inexistente id=999, **When** tento deletar, **Then** ValueError e lancado com mensagem "Desenvolvedor nao encontrado: 999"

---

### User Story 5 - Criar Nova Feature (Priority: P1)

Como Product Owner, preciso criar features para organizar historias em ondas de entrega, garantindo que cada onda seja unica.

**Why this priority**: Features definem a estrutura de ondas para cronograma (EP-006). Sao fundamentais para organizacao do backlog.

**Independent Test**: Pode ser testado criando uma feature com nome e wave unicos e verificando persistencia.

**Acceptance Scenarios**:

1. **Given** nenhuma feature com wave=1, **When** crio feature nome="Autenticacao", wave=1, **Then** feature e criada com ID auto-gerado, nome="Autenticacao", wave=1
2. **Given** feature existente com wave=1, **When** crio outra feature com wave=1, **Then** DuplicateWaveException e lancada com mensagem "Wave 1 ja esta em uso pela feature 'X'"
3. **Given** feature existente com nome="Auth", **When** crio outra feature com nome="Auth", **Then** ValueError e lancado com mensagem "Feature com nome 'Auth' ja existe"
4. **Given** wave=0, **When** crio feature, **Then** ValueError e lancado com mensagem "Wave deve ser > 0: 0"
5. **Given** wave=-1, **When** crio feature, **Then** ValueError e lancado com mensagem "Wave deve ser > 0: -1"
6. **Given** nome vazio, **When** crio feature, **Then** ValueError e lancado com mensagem "Nome da feature nao pode ser vazio"

---

### User Story 6 - Listar Features (Priority: P1)

Como Product Owner, preciso visualizar todas as features ordenadas por wave para entender a sequencia de entregas.

**Why this priority**: Listagem e base para qualquer gerenciamento de features e planejamento de ondas.

**Independent Test**: Pode ser testado cadastrando features com diferentes waves e verificando ordenacao.

**Acceptance Scenarios**:

1. **Given** features com waves 3, 1, 2, **When** listo features, **Then** retornam na ordem wave 1, 2, 3
2. **Given** nenhuma feature cadastrada, **When** listo features, **Then** retorna lista vazia

---

### User Story 7 - Editar Feature (Priority: P1)

Como Product Owner, preciso editar nome e wave de uma feature, respeitando unicidade de ambos.

**Why this priority**: Permite ajustes no planejamento de ondas. Essencial para flexibilidade.

**Independent Test**: Pode ser testado editando nome e wave de feature existente.

**Acceptance Scenarios**:

1. **Given** feature id=1 com nome="Auth", wave=1, **When** edito nome para "Autenticacao", **Then** feature.name == "Autenticacao" e feature.wave == 1
2. **Given** feature id=1 com wave=1, **When** edito wave para 2, **Then** feature.wave == 2
3. **Given** feature id=1 com wave=1 e feature id=2 com wave=2, **When** edito feature id=1 para wave=2, **Then** DuplicateWaveException e lancada
4. **Given** feature id=1 nome="A" e feature id=2 nome="B", **When** edito feature id=1 para nome="B", **Then** ValueError e lancado com mensagem "Feature com nome 'B' ja existe"
5. **Given** feature inexistente id=999, **When** tento editar, **Then** ValueError e lancado com mensagem "Feature nao encontrada: 999"

---

### User Story 8 - Deletar Feature (Priority: P1)

Como Product Owner, preciso deletar features obsoletas, mas apenas se nao houver historias associadas para evitar perda de dados.

**Why this priority**: Protege integridade do backlog. Features com historias nao podem ser deletadas.

**Independent Test**: Pode ser testado tentando deletar feature com e sem historias.

**Acceptance Scenarios**:

1. **Given** feature id=1 sem historias associadas, **When** deleto feature, **Then** feature e removida
2. **Given** feature "Auth" com 5 historias associadas, **When** tento deletar, **Then** FeatureHasStoriesException e lancada com mensagem "Nao e possivel deletar feature 'Auth' (ID: 1): existem 5 historia(s) associada(s)"
3. **Given** feature inexistente id=999, **When** tento deletar, **Then** ValueError e lancado com mensagem "Feature nao encontrada: 999"

---

### User Story 9 - Associar Historia a Feature (Priority: P2)

Como Scrum Master, preciso associar historias a features para organiza-las em ondas de entrega.

**Why this priority**: Associacao e meio de organizar historias. E secundaria pois a funcionalidade ja existe via StoryService.update_story (EP-003).

**Independent Test**: Pode ser testado atualizando feature_id de uma historia e verificando associacao.

**Acceptance Scenarios**:

1. **Given** historia H1 sem feature e feature F1 (wave=2) existente, **When** associo H1 a F1, **Then** H1.feature_id == F1.id
2. **Given** historia H1 ja associada a F1, **When** associo H1 a F2, **Then** H1.feature_id == F2.id (substituicao)
3. **Given** historia H1 associada a F1, **When** desassocio (feature_id=NULL), **Then** H1.feature_id == NULL
4. **Given** feature inexistente id=999, **When** tento associar historia, **Then** ValueError e lancado com mensagem "Feature nao encontrada: 999"

---

### Edge Cases

- O que acontece se dois desenvolvedores tiverem o mesmo nome? Permitido - nomes de desenvolvedores nao precisam ser unicos (apenas Feature.name e unico)
- O que acontece ao tentar editar wave para um valor ja usado por outra feature? DuplicateWaveException e lancada com o nome da feature conflitante
- O que acontece ao deletar desenvolvedor com muitas historias? Todas as historias sao desalocadas via ON DELETE SET NULL no banco
- O que acontece se wave for 0 para historia sem feature? Wave=0 e um valor computado/derivado ao consultar, nao armazenado (ver ADR-006)
- O que acontece ao editar feature para mesmo nome (case-insensitive)? Validacao de unicidade considera case-sensitive conforme schema SQLite default

## Requirements *(mandatory)*

### Functional Requirements

#### Extensoes aos Protocols de Repositorio

- **FR-001**: Protocol FeatureRepository DEVE ser estendido com metodo `async def get_by_name(name: str) -> Feature | None` que retorna feature por nome exato ou None se nao existir
- **FR-002**: Protocol StoryRepository DEVE ser estendido com metodo `async def count_by_developer(developer_id: int) -> int` que retorna o numero de historias alocadas a um desenvolvedor (para logging de desalocacao)
- **FR-003**: Protocol DeveloperRepository DEVE ter metodo `async def get_all() -> Sequence[Developer]` (herdado de EP-001) que retorna todos os desenvolvedores ordenados por nome
- **FR-004**: Protocol FeatureRepository DEVE ter metodo `async def get_all() -> Sequence[Feature]` (herdado de EP-001) que retorna todas as features ordenadas por wave

#### DeveloperService - Domain Service

- **FR-010**: Sistema DEVE implementar `DeveloperService` como domain service em `src/backlog_manager/domain/services/developer_service.py`
- **FR-011**: DeveloperService DEVE receber DeveloperRepository como dependencia via construtor
- **FR-012**: DeveloperService DEVE implementar metodo `async def create_developer(name: str) -> Developer` que cria entidade Developer e retorna (sem persistir - responsabilidade do use case)
- **FR-013**: DeveloperService.create_developer DEVE delegar validacoes de nome a entidade Developer (max 100 chars, nao vazio)
- **FR-014**: DeveloperService DEVE implementar metodo `async def update_developer(developer_id: int, name: str) -> Developer`
- **FR-015**: DeveloperService.update_developer DEVE buscar desenvolvedor existente, criar nova instancia com ID preservado e nome atualizado, e retornar (ID e imutavel conforme User Story 3 cenario 1)
- **FR-016**: DeveloperService.update_developer DEVE lancar ValueError com mensagem "Desenvolvedor nao encontrado: {developer_id}" se nao existir
- **FR-017**: DeveloperService DEVE implementar metodo `async def delete_developer(developer_id: int) -> int` que retorna contagem de historias desalocadas
- **FR-018**: DeveloperService.delete_developer NAO DEVE fazer desalocacao explicita de historias - banco faz via ON DELETE SET NULL (ver ADR-001)
- **FR-019**: DeveloperService.delete_developer DEVE consultar contagem de historias antes de deletar para retornar ao chamador (fins de logging)
- **FR-020**: DeveloperService.delete_developer DEVE lancar ValueError com mensagem "Desenvolvedor nao encontrado: {developer_id}" se nao existir
- **FR-021**: DeveloperService DEVE implementar metodo `async def list_developers() -> Sequence[Developer]` que retorna todos os desenvolvedores ordenados por nome

#### FeatureService - Domain Service

- **FR-030**: Sistema DEVE implementar `FeatureService` como domain service em `src/backlog_manager/domain/services/feature_service.py`
- **FR-031**: FeatureService DEVE receber FeatureRepository como dependencia via construtor
- **FR-032**: FeatureService DEVE implementar metodo `async def create_feature(name: str, wave: int) -> Feature` que cria entidade Feature e retorna
- **FR-033**: FeatureService.create_feature DEVE validar unicidade de wave via get_by_wave() ANTES de criar entidade
- **FR-034**: FeatureService.create_feature DEVE lancar DuplicateWaveException se wave ja existe, incluindo nome da feature existente
- **FR-035**: FeatureService.create_feature DEVE validar unicidade de nome via get_by_name() ANTES de criar entidade
- **FR-036**: FeatureService.create_feature DEVE lancar ValueError com mensagem "Feature com nome '{name}' ja existe" se nome duplicado
- **FR-037**: FeatureService.create_feature DEVE delegar validacoes de wave > 0 e nome nao vazio a entidade Feature
- **FR-038**: FeatureService DEVE implementar metodo `async def update_feature(feature_id: int, name: str | None = None, wave: int | None = None) -> Feature`
- **FR-038a**: FeatureService.update_feature DEVE preservar feature_id ao criar nova instancia com campos atualizados (ID e imutavel)
- **FR-039**: FeatureService.update_feature DEVE lancar ValueError com mensagem "Feature nao encontrada: {feature_id}" se nao existir
- **FR-040**: FeatureService.update_feature DEVE validar unicidade de wave (se alterado) excluindo a propria feature
- **FR-041**: FeatureService.update_feature DEVE validar unicidade de nome (se alterado) excluindo a propria feature
- **FR-042**: FeatureService DEVE implementar metodo `async def delete_feature(feature_id: int) -> None`
- **FR-043**: FeatureService.delete_feature DEVE verificar via has_stories() se feature tem historias ANTES de chamar repository.delete()
- **FR-044**: FeatureService.delete_feature DEVE lancar FeatureHasStoriesException com contagem se houver historias
- **FR-045**: FeatureService.delete_feature DEVE lancar ValueError com mensagem "Feature nao encontrada: {feature_id}" se nao existir
- **FR-046**: FeatureService DEVE implementar metodo `async def list_features() -> Sequence[Feature]` que retorna todas as features ordenadas por wave

#### Use Cases - Application Layer (Developer)

- **FR-050**: Sistema DEVE implementar use cases em `src/backlog_manager/application/use_cases/developer/`
- **FR-051**: Sistema DEVE implementar `CreateDeveloperUseCase` com metodo `async def execute(input_dto: CreateDeveloperInputDTO) -> DeveloperOutputDTO`
- **FR-052**: CreateDeveloperUseCase DEVE usar DeveloperService para criar entidade e persistir via repository.add()
- **FR-053**: CreateDeveloperUseCase DEVE atribuir o ID retornado pelo repository.add() a entidade antes de retornar DTO
- **FR-054**: Sistema DEVE implementar `UpdateDeveloperUseCase` com metodo `async def execute(input_dto: UpdateDeveloperInputDTO) -> DeveloperOutputDTO`
- **FR-055**: UpdateDeveloperUseCase DEVE usar DeveloperService.update_developer e persistir via repository.update()
- **FR-056**: Sistema DEVE implementar `DeleteDeveloperUseCase` com metodo `async def execute(developer_id: int) -> DeleteDeveloperOutputDTO`
- **FR-057**: DeleteDeveloperUseCase DEVE usar DeveloperService.delete_developer e retornar contagem de historias desalocadas no DTO
- **FR-058**: Sistema DEVE implementar `ListDevelopersUseCase` com metodo `async def execute() -> ListDevelopersOutputDTO`
- **FR-059**: ListDevelopersUseCase DEVE usar repository.get_all() diretamente (sem necessidade de service para listagem simples)

#### Use Cases - Application Layer (Feature)

- **FR-060**: Sistema DEVE implementar use cases em `src/backlog_manager/application/use_cases/feature/`
- **FR-061**: Sistema DEVE implementar `CreateFeatureUseCase` com metodo `async def execute(input_dto: CreateFeatureInputDTO) -> FeatureOutputDTO`
- **FR-062**: CreateFeatureUseCase DEVE usar FeatureService para criar e validar, e persistir via repository.add()
- **FR-063**: CreateFeatureUseCase DEVE atribuir o ID retornado pelo repository.add() a entidade antes de retornar DTO
- **FR-064**: Sistema DEVE implementar `UpdateFeatureUseCase` com metodo `async def execute(input_dto: UpdateFeatureInputDTO) -> FeatureOutputDTO`
- **FR-065**: UpdateFeatureUseCase DEVE usar FeatureService.update_feature e persistir via repository.update()
- **FR-066**: Sistema DEVE implementar `DeleteFeatureUseCase` com metodo `async def execute(feature_id: int) -> None`
- **FR-067**: DeleteFeatureUseCase DEVE usar FeatureService.delete_feature (que faz validacao e delecao)
- **FR-068**: Sistema DEVE implementar `ListFeaturesUseCase` com metodo `async def execute() -> ListFeaturesOutputDTO`
- **FR-069**: ListFeaturesUseCase DEVE usar repository.get_all() diretamente

#### Use Cases - Transacoes e UnitOfWork

- **FR-070**: Todos os use cases DEVEM receber UnitOfWork como dependencia no construtor
- **FR-071**: Todos os use cases DEVEM executar operacoes dentro do contexto do UnitOfWork (via `async with uow`)
- **FR-072**: Todos os use cases DEVEM fazer commit implicito via context manager ao finalizar com sucesso
- **FR-073**: Todos os use cases DEVEM fazer rollback automatico em caso de excecao (via context manager)

#### DTOs - Application Layer (Developer)

- **FR-080**: Sistema DEVE implementar DTOs Pydantic em `src/backlog_manager/application/dto/developer/`
- **FR-081**: Sistema DEVE implementar `CreateDeveloperInputDTO(BaseModel)` com campo: name (str)
- **FR-082**: CreateDeveloperInputDTO DEVE validar via Pydantic que name nao e vazio e tem max 100 chars
- **FR-083**: Sistema DEVE implementar `UpdateDeveloperInputDTO(BaseModel)` com campos: developer_id (int), name (str)
- **FR-084**: Sistema DEVE implementar `DeveloperOutputDTO(BaseModel)` com campos: id (int), name (str)
- **FR-085**: DeveloperOutputDTO DEVE incluir metodo `from_entity(entity: Developer) -> Self` para conversao
- **FR-086**: Sistema DEVE implementar `DeleteDeveloperOutputDTO(BaseModel)` com campos: developer_id (int), stories_unassigned (int)
- **FR-087**: Sistema DEVE implementar `ListDevelopersOutputDTO(BaseModel)` com campo: developers (list[DeveloperOutputDTO])

#### DTOs - Application Layer (Feature)

- **FR-090**: Sistema DEVE implementar DTOs Pydantic em `src/backlog_manager/application/dto/feature/`
- **FR-091**: Sistema DEVE implementar `CreateFeatureInputDTO(BaseModel)` com campos: name (str), wave (int)
- **FR-092**: CreateFeatureInputDTO DEVE validar via Pydantic que name nao e vazio, max 100 chars, wave > 0
- **FR-093**: Sistema DEVE implementar `UpdateFeatureInputDTO(BaseModel)` com campos: feature_id (int), name (str | None = None), wave (int | None = None)
- **FR-094**: Sistema DEVE implementar `FeatureOutputDTO(BaseModel)` com campos: id (int), name (str), wave (int)
- **FR-095**: FeatureOutputDTO DEVE incluir metodo `from_entity(entity: Feature) -> Self` para conversao
- **FR-096**: Sistema DEVE implementar `ListFeaturesOutputDTO(BaseModel)` com campo: features (list[FeatureOutputDTO])

### Key Entities

- **DeveloperService**: Domain service responsavel por regras de negocio de desenvolvedores. Recebe DeveloperRepository como dependencia. Metodos: create_developer, update_developer, delete_developer, list_developers.

- **FeatureService**: Domain service responsavel por regras de negocio de features. Recebe FeatureRepository como dependencia. Valida unicidade de wave e nome, protege contra delecao de feature com historias. Metodos: create_feature, update_feature, delete_feature, list_features.

- **Use Cases**: Application services que coordenam Services com UnitOfWork para operacoes transacionais. Um use case por operacao CRUD para Developer (Create, Update, Delete, List) e Feature (Create, Update, Delete, List).

- **DTOs**: Objetos Pydantic para transporte de dados entre camadas. Input DTOs validam entrada, Output DTOs formatam saida. Desacoplam camada de aplicacao da camada de dominio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuario consegue cadastrar desenvolvedor e o ID e gerado automaticamente
- **SC-002**: Usuario consegue listar todos os desenvolvedores ordenados alfabeticamente por nome
- **SC-003**: Usuario consegue editar nome de desenvolvedor existente com persistencia imediata
- **SC-004**: Usuario consegue deletar desenvolvedor e todas as historias associadas sao desalocadas automaticamente
- **SC-005**: Usuario consegue criar feature com nome e wave unicos, recebendo ID auto-gerado
- **SC-006**: Usuario recebe erro claro ao tentar criar feature com wave duplicada (DuplicateWaveException)
- **SC-007**: Usuario consegue editar feature mantendo validacao de unicidade de wave e nome
- **SC-008**: Usuario nao consegue deletar feature com historias (FeatureHasStoriesException)
- **SC-009**: Todas as operacoes sao transacionais - falhas resultam em rollback completo
- **SC-010**: Cobertura de testes unitarios dos Services atinge 100% das regras de negocio
- **SC-011**: Cobertura de testes de integracao dos Use Cases atinge 100% dos fluxos de sucesso e erro

## Architectural Decisions

### ADR-001: Desalocacao de Historias ao Deletar Desenvolvedor

**Contexto**: O schema SQLite define `ON DELETE SET NULL` na FK `developer_id` da tabela Story, ou seja, o banco ja faz a desalocacao automaticamente ao deletar o desenvolvedor. O epico EP-004 exige "desalocar historias antes" de deletar (RF-DEV-003), sugerindo logica explicita no servico.

**Opcoes**:
1. Confiar no `ON DELETE SET NULL` do banco - servico apenas deleta, banco desaloca
2. Servico desaloca explicitamente antes de deletar (para logging/auditoria/eventos)
3. Ambos: servico desaloca para logging, banco garante como fallback

**Decisao**: Opcao 1 - Confiar no `ON DELETE SET NULL` do banco

**Justificativa**:
- Simplicidade: menos codigo, menos pontos de falha
- Atomicidade: ON DELETE SET NULL executa na mesma transacao do DELETE, garantindo consistencia
- Performance: uma unica operacao de banco vs multiplas atualizacoes
- YAGNI: nao ha requisito de logging/auditoria no epico
- O servico apenas consulta a contagem de historias ANTES de deletar para retornar ao chamador (util para UI mostrar "X historias foram desalocadas"), mas nao executa a desalocacao explicitamente

**Trade-offs**:
- Nao ha logs detalhados de quais historias foram desalocadas (aceitavel para MVP)
- Se futuramente precisar de eventos/auditoria, sera necessario refatorar

### ADR-002: Protecao Contra Delecao de Feature - Repositorio vs Servico

**Contexto**: O protocol `FeatureRepository.delete()` ja documenta que lanca `FeatureHasStoriesException`. A implementacao SQLite verifica via `has_stories()`.

**Opcoes**:
1. Validacao exclusivamente no repositorio (como esta implementado)
2. Servico faz verificacao ANTES de chamar delete (fail-fast com mensagem controlada)
3. Dupla verificacao (servico + repositorio)

**Decisao**: Opcao 2 - Servico verifica ANTES de chamar delete

**Justificativa**:
- Fail-fast: erro detectado antes de tentar operacao de persistencia
- Mensagem controlada: servico pode construir mensagem com mais contexto se necessario
- Testabilidade: logica de negocio fica no servico (domain layer), testavel com mocks
- Consistencia: mesmo padrao usado em outros services da codebase
- O repositorio mantem a validacao como fallback de seguranca (defense in depth)

### ADR-003: Validacao de Unicidade de Wave - Servico vs Repositorio

**Contexto**: `FeatureRepository.add()` e `update()` ja lancam `DuplicateWaveException` quando wave e duplicada.

**Opcoes**:
1. Servico delega ao repositorio (validacao no add/update)
2. Servico valida antes via `get_by_wave()`, depois chama add/update
3. Servico valida antes, repositorio valida como fallback

**Decisao**: Opcao 2 - Servico valida antes via `get_by_wave()`

**Justificativa**:
- Fail-fast: valida antes de tentar criar a entidade e persistir
- Mensagem rica: servico pode incluir mais contexto (nome da feature existente)
- Separacao clara: validacao de regra de negocio fica no servico
- Testabilidade: servico pode ser testado com mocks sem depender do repositorio real
- Simplicidade: repositorio nao precisa duplicar a logica de validacao (pode remover ou manter como fallback)

### ADR-004: Validacao de Unicidade de Nome de Feature

**Contexto**: O epico menciona "nome unico" para Feature (RF-FEAT-002). O repositorio `add()` levanta `ValueError: Se nome ja existe`, mas nao ha um metodo explicito `get_by_name()` no protocol.

**Opcoes**:
1. Adicionar `get_by_name(name: str) -> Feature | None` ao protocol para validacao no servico
2. Delegar ao repositorio/banco (UNIQUE constraint)

**Decisao**: Opcao 1 - Adicionar `get_by_name()` ao protocol

**Justificativa**:
- Fail-fast: valida antes de tentar persistir
- Mensagem amigavel: servico pode criar mensagem descritiva
- Consistencia: mesmo padrao de `get_by_wave()`
- Reutilizavel: metodo pode ser util para futuras funcionalidades (buscar feature por nome)

### ADR-005: Associacao de Historias a Features

**Contexto**: O epico exige "Associar Historias a Features" (RF-FEAT-004). EP-003 ja implementou `StoryService.update_story(..., feature_id=...)` que permite alterar o feature_id de uma historia via EditStoryUseCase.

**Opcoes**:
1. Reutilizar funcionalidade existente de EP-003 (EditStoryUseCase com feature_id)
2. Criar metodo dedicado no FeatureService: `associate_story(feature_id, story_id)`
3. Apenas documentar como cenario de uso sem novo codigo

**Decisao**: Opcao 1 - Reutilizar funcionalidade existente de EP-003

**Justificativa**:
- DRY: funcionalidade ja existe e funciona
- Simplicidade: nao duplica codigo
- Consistencia: usuario usa o mesmo fluxo (editar historia) para qualquer alteracao
- EP-004 NAO precisa implementar novo codigo para associacao - apenas documenta que a funcionalidade existe via EditStoryUseCase

### ADR-006: Wave=0 para Historia sem Feature

**Contexto**: A regra paragrafo 8.3 do SRS diz "historia sem feature -> wave=0". Isso e um valor computado (read-time) ou armazenado?

**Opcoes**:
1. Propriedade derivada ao consultar (Feature.wave ou 0 se feature_id=None)
2. Persistir wave=0 na tabela Story quando feature_id=NULL

**Decisao**: Opcao 1 - Propriedade derivada (computada em read-time)

**Justificativa**:
- Normalizacao: wave e atributo da Feature, nao da Story; evita redundancia
- Consistencia: se feature muda de wave, nao precisa atualizar todas as historias
- Simplicidade: menos campos para manter sincronizados
- Implementacao: Camada de apresentacao ou DTO pode derivar wave=0 quando feature_id=NULL
- EP-004 NAO precisa de logica adicional no FeatureService para isso

### ADR-007: Contagem de Historias ao Deletar Feature

**Contexto**: RF-FEAT-003 exige "Deletar Feature somente se sem historias". A informacao "quantas historias tem esta feature" e util para a mensagem de erro.

**Opcoes**:
1. `FeatureHasStoriesException` inclui contagem (ja implementado!)
2. Apenas ID/nome da feature no erro

**Decisao**: Usar implementacao existente - `FeatureHasStoriesException` ja inclui story_count

**Justificativa**:
- Ja implementado: excecao ja tem atributo `story_count`
- Mensagem informativa: usuario sabe exatamente quantas historias impediram a delecao
- O repositorio ja implementa `_count_stories()` internamente
- Servico pode obter contagem via `len(await story_repo.get_by_feature(feature_id))` ou metodo dedicado

### ADR-008: Nomes de Desenvolvedores Nao Sao Unicos

**Contexto**: O epico NAO menciona unicidade de nomes de desenvolvedores (diferente de Feature.name que e UNIQUE).

**Decisao**: Nomes duplicados de desenvolvedores SAO PERMITIDOS

**Justificativa**:
- Requisito ausente: se fosse necessario, estaria no epico/SRS
- Realidade: podem existir dois "Carlos Silva" no mesmo time
- Simplicidade: evita validacao e excecao adicionais
- ID unico: desenvolvedores sao identificados por ID, nao por nome

## Traceability Matrix

### Requisitos do Epico -> Requisitos Funcionais

| Requisito Epico | Requisitos Funcionais |
|-----------------|----------------------|
| RF-DEV-001: Cadastrar Novo Desenvolvedor | FR-010, FR-011, FR-012, FR-013, FR-051, FR-052, FR-053, FR-081, FR-082, FR-084, FR-085 |
| RF-DEV-002: Editar Desenvolvedor | FR-014, FR-015, FR-016, FR-054, FR-055, FR-083 |
| RF-DEV-003: Deletar Desenvolvedor | FR-017, FR-018, FR-019, FR-020, FR-056, FR-057, FR-086, FR-002 |
| RF-DEV-004: Listar Desenvolvedores | FR-021, FR-058, FR-059, FR-087 |
| RF-FEAT-001: Criar Nova Feature | FR-030, FR-031, FR-032, FR-033, FR-034, FR-035, FR-036, FR-037, FR-061, FR-062, FR-063, FR-091, FR-092, FR-094, FR-095, FR-001 |
| RF-FEAT-002: Editar Feature | FR-038, FR-039, FR-040, FR-041, FR-064, FR-065, FR-093 |
| RF-FEAT-003: Deletar Feature | FR-042, FR-043, FR-044, FR-045, FR-066, FR-067 |
| RF-FEAT-004: Associar Historias a Features | Reutiliza EP-003 EditStoryUseCase (ver ADR-005) |
| RF-FEAT-005: Validar Onda Unica | FR-033, FR-034, FR-040 |

## Assumptions

- DeveloperRepository e FeatureRepository estao implementados e funcionais (EP-001)
- Schema SQLite com ON DELETE SET NULL na FK developer_id da tabela Story (EP-001)
- UnitOfWork gerencia transacoes corretamente com commit/rollback automatico (EP-001)
- Entidades Developer e Feature validam invariantes no construtor (EP-002)
- StoryRepository.get_by_feature() e get_by_developer() existem e funcionam (EP-001)
- FeatureHasStoriesException ja inclui story_count no construtor (EP-001)
- Associacao de historia a feature e feita via EditStoryUseCase existente (EP-003)
- Wave=0 para historia sem feature e derivado em tempo de leitura, nao armazenado
- Nomes de desenvolvedores podem ser duplicados (sem constraint UNIQUE)
