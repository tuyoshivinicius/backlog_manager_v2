# Feature Specification: EP-003 Gestao de Backlog - Servicos e Aplicacao

**Feature Branch**: `003-ep003-backlog-services`
**Created**: 2026-02-28
**Status**: Draft
**Input**: Implementacao da camada de servico e aplicacao para gestao de backlog: StoryService (domain service), Use Cases, DTOs Pydantic, e extensoes aos protocols de repositorio para suportar operacoes CRUD completas de historias

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Criar Nova Historia com ID Auto-gerado (Priority: P1)

Como Scrum Master, preciso criar novas historias no backlog com ID automaticamente gerado no formato COMPONENTE-NNN para que eu possa adicionar trabalho ao backlog sem me preocupar com a geracao manual de identificadores unicos.

**Why this priority**: Criacao de historias e a operacao fundamental que habilita todo o backlog. Sem ela, nao ha dados para priorizar, editar ou alocar.

**Independent Test**: Pode ser testado criando uma historia com componente "CORE" e verificando que o ID gerado segue o padrao CORE-001, CORE-002, etc.

**Acceptance Scenarios**:

1. **Given** que nao existe historia com componente "CORE", **When** crio historia com Componente="CORE", Nome="Login", SP=5, **Then** historia e criada com ID="CORE-001" e priority=1
2. **Given** que existe historia CORE-001, **When** crio nova historia com Componente="CORE", **Then** historia e criada com ID="CORE-002"
3. **Given** que existem 3 historias com prioridades 1, 2, 3, **When** crio nova historia, **Then** nova historia recebe priority=4
4. **Given** dados invalidos (nome vazio), **When** tento criar historia, **Then** ValueError e lancado com mensagem descritiva

---

### User Story 2 - Listar Historias Ordenadas por Prioridade (Priority: P1)

Como Scrum Master, preciso visualizar todas as historias do backlog ordenadas por prioridade para que eu possa planejar sprints e identificar o trabalho mais importante.

**Why this priority**: Listagem e essencial para visualizacao e planejamento. E a base para todas as operacoes de gerenciamento.

**Independent Test**: Pode ser testado criando multiplas historias com diferentes prioridades e verificando a ordenacao.

**Acceptance Scenarios**:

1. **Given** historias com prioridades 3, 1, 2, **When** listo todas as historias, **Then** retornam na ordem 1, 2, 3
2. **Given** backlog vazio, **When** listo todas as historias, **Then** retorna lista vazia
3. **Given** historias com diferentes status, **When** listo todas, **Then** todas sao retornadas independente do status

---

### User Story 3 - Editar Historia Existente (Priority: P1)

Como Scrum Master, preciso editar historias existentes para atualizar estimativas, nomes ou status conforme o projeto evolui, mantendo o ID original imutavel.

**Why this priority**: Edicao permite ajustes ao longo do tempo. E essencial para manter o backlog atualizado.

**Independent Test**: Pode ser testado editando campos de uma historia e verificando que as mudancas persistem enquanto o ID permanece inalterado.

**Acceptance Scenarios**:

1. **Given** historia CORE-001 com Nome="Login", **When** altero Nome para "Autenticacao", **Then** historia.name == "Autenticacao" e historia.id == "CORE-001"
2. **Given** historia existente, **When** tento alterar ID, **Then** ID permanece inalterado (imutavel)
3. **Given** historia existente com SP=5, **When** altero SP para 8, **Then** historia.story_points == 8
4. **Given** historia existente, **When** altero status para "EXECUCAO", **Then** historia.status == "EXECUCAO"
5. **Given** historia inexistente, **When** tento editar, **Then** ValueError e lancado

---

### User Story 4 - Deletar Historia com Limpeza de Dependencias (Priority: P1)

Como Scrum Master, preciso deletar historias do backlog quando elas se tornam obsoletas, garantindo que todas as referencias de dependencia sejam removidas automaticamente.

**Why this priority**: Delecao e necessaria para manter o backlog limpo. A limpeza de dependencias garante integridade referencial.

**Independent Test**: Pode ser testado deletando uma historia que e dependencia de outra e verificando que a referencia foi removida.

**Acceptance Scenarios**:

1. **Given** historia A sem dependentes, **When** deleto A, **Then** A e removida do backlog
2. **Given** historia B que depende de A, **When** deleto A, **Then** A e removida e B.dependencies nao contem mais "A"
3. **Given** historia A com multiplos dependentes (B, C, D), **When** deleto A, **Then** todas as referencias sao removidas
4. **Given** historia inexistente, **When** tento deletar, **Then** ValueError e lancado

---

### User Story 5 - Mover Prioridade para Cima/Baixo (Priority: P1)

Como Scrum Master, preciso reordenar historias no backlog movendo-as para cima ou baixo na prioridade para refletir mudancas nas prioridades de negocio.

**Why this priority**: Priorizacao e uma das funcoes principais do Scrum Master. Permite ajuste dinamico do backlog.

**Independent Test**: Pode ser testado movendo uma historia e verificando que as prioridades adjacentes sao trocadas.

**Acceptance Scenarios**:

1. **Given** historias A(p=1), B(p=2), C(p=3), **When** movo C para cima, **Then** C.priority=2 e B.priority=3
2. **Given** historias A(p=1), B(p=2), **When** movo A para cima, **Then** nada muda (ja e o mais prioritario)
3. **Given** historias A(p=1), B(p=2), **When** movo B para baixo, **Then** nada muda (ja e o menos prioritario)
4. **Given** historia com priority=5 e outra com priority=6, **When** movo p=5 para baixo, **Then** p=5 vira p=6 e p=6 vira p=5
5. **Given** historia inexistente, **When** tento mover, **Then** ValueError e lancado

---

### User Story 6 - Duplicar Historia (Priority: P2)

Como Scrum Master, preciso duplicar uma historia existente para criar historias similares rapidamente, recebendo novo ID e sem dados de alocacao copiados.

**Why this priority**: Duplicacao acelera a criacao de historias similares. E uma funcionalidade de conveniencia.

**Independent Test**: Pode ser testado duplicando uma historia alocada e verificando que a copia tem novo ID, mesmos dados base, mas sem alocacao.

**Acceptance Scenarios**:

1. **Given** historia CORE-001 com SP=5, feature_id=10, developer_id=1, start_date="2026-03-02", **When** duplico CORE-001, **Then** nova historia CORE-002 tem SP=5, feature_id=10, developer_id=NULL, start_date=NULL, end_date=NULL
2. **Given** historia duplicada, **When** verifico prioridade, **Then** prioridade = max(existentes) + 1
3. **Given** historia com status CONCLUIDO, **When** duplico, **Then** nova historia tem status BACKLOG
4. **Given** historia inexistente, **When** tento duplicar, **Then** ValueError e lancado
n> **Nota**: Os cenarios de aceitacao mostram o estado da historia ORIGINAL (input) vs DUPLICADA (output). Campos de alocacao (developer_id, start_date, end_date, duration) sao sempre resetados na copia, independente do valor original.

---

### User Story 7 - Atribuir/Desatribuir Desenvolvedor (Priority: P2)

Como Scrum Master, preciso atribuir manualmente um desenvolvedor a uma historia ou remover a atribuicao para controle direto sobre a alocacao.

**Why this priority**: Atribuicao manual complementa a alocacao automatica. Permite ajustes finos.

**Independent Test**: Pode ser testado atribuindo um desenvolvedor existente a uma historia e verificando a associacao.

**Acceptance Scenarios**:

1. **Given** desenvolvedor "Dev1" com id=1 cadastrado, **When** atribuo Dev1 a uma historia, **Then** historia.developer_id == 1
2. **Given** historia com developer_id=1, **When** desaloco (developer_id=NULL), **Then** historia.developer_id == NULL
3. **Given** developer_id de desenvolvedor inexistente, **When** tento atribuir, **Then** ValueError e lancado com mensagem "Desenvolvedor nao encontrado: {id}"
4. **Given** historia inexistente, **When** tento atribuir desenvolvedor, **Then** ValueError e lancado

---

### Edge Cases

- O que acontece quando componente tem caracteres especiais? Componente e validado na entidade (max 50 chars, nao vazio); caracteres especiais sao aceitos mas ID usa apenas MAIUSCULAS
- O que acontece quando todas as prioridades sao iguais? Sistema assume prioridades unicas e contiguas; gaps nao devem ocorrer por invariante
- O que acontece quando developer_id e 0? 0 e tratado como ID valido; apenas NULL indica desalocacao
- O que acontece quando historia tem feature_id invalido ao duplicar? Feature_id e copiado como esta; validacao de FK e no banco
- O que acontece ao mover prioridade em backlog com uma unica historia? Operacao retorna sem efeito (nao ha adjacente)

## Requirements *(mandatory)*

### Functional Requirements

#### Extensoes aos Protocols de Repositorio

- **FR-001**: Protocol StoryRepository DEVE ser estendido com metodo `async def get_max_id_number(component: str) -> int` que retorna o maior numero NNN para um componente ou 0 se nao existir
- **FR-002**: Protocol StoryRepository DEVE ser estendido com metodo `async def get_max_priority() -> int` que retorna a maior prioridade existente ou 0 se backlog vazio
- **FR-003**: Protocol StoryRepository DEVE ser estendido com metodo `async def get_by_priority(priority: int) -> Story | None` para buscar historia por prioridade exata
- **FR-004**: Protocol StoryDependencyRepository DEVE ser estendido com metodo `async def remove_all_for_story(story_id: str) -> None` para remover todas as dependencias onde story_id aparece em QUALQUER direcao: (1) onde story_id e o dependente (story_id depende de X), e (2) onde story_id e a dependencia (Y depende de story_id). Isso garante integridade referencial ao deletar historia.

#### StoryService - Domain Service

- **FR-010**: Sistema DEVE implementar `StoryService` como domain service em `src/backlog_manager/domain/services/story_service.py`
- **FR-011**: StoryService DEVE ser uma classe que recebe UnitOfWork como dependencia via construtor
- **FR-012**: StoryService DEVE implementar metodo `async def generate_story_id(component: str) -> str` que gera ID no formato COMPONENTE-NNN onde NNN = max(existentes)+1 ou 001 se primeiro
- **FR-013**: StoryService DEVE implementar metodo `async def calculate_initial_priority() -> int` que retorna max(prioridades)+1 ou 1 se backlog vazio
- **FR-014**: StoryService DEVE implementar metodo `async def create_story(component: str, name: str, story_points: int, feature_id: int | None = None) -> Story`
- **FR-015**: StoryService.create_story DEVE gerar ID automaticamente usando generate_story_id
- **FR-016**: StoryService.create_story DEVE atribuir prioridade inicial usando calculate_initial_priority
- **FR-017**: StoryService.create_story DEVE criar instancia Story com status=BACKLOG e persistir via repositorio
- **FR-018**: StoryService DEVE implementar metodo `async def update_story(story_id: str, name: str | None = None, story_points: int | None = None, status: str | None = None, feature_id: int | None | UNSET = UNSET) -> Story` onde UNSET (sentinel object) indica "nao alterar" e None indica "remover associacao"
- **FR-019**: StoryService.update_story DEVE lancar ValueError se historia nao existe com mensagem "Historia nao encontrada: {story_id}"
- **FR-020**: StoryService.update_story NAO DEVE permitir alteracao do ID ou component (imutaveis)
- **FR-021**: StoryService DEVE implementar metodo `async def delete_story(story_id: str) -> None`
- **FR-022**: StoryService.delete_story DEVE remover todas as dependencias usando remove_all_for_story ANTES de deletar a historia
- **FR-023**: StoryService.delete_story DEVE lancar ValueError se historia nao existe com mensagem "Historia nao encontrada: {story_id}"
- **FR-024**: StoryService DEVE implementar metodo `async def duplicate_story(story_id: str) -> Story`
- **FR-025**: StoryService.duplicate_story DEVE copiar: component, name, story_points, feature_id
- **FR-026**: StoryService.duplicate_story DEVE resetar: developer_id=NULL, start_date=NULL, end_date=NULL, duration=NULL
- **FR-027**: StoryService.duplicate_story DEVE atribuir status=BACKLOG independente do status original
- **FR-028**: StoryService.duplicate_story DEVE gerar novo ID e atribuir prioridade = max+1
- **FR-029**: StoryService DEVE implementar metodo `async def move_priority(story_id: str, direction: Literal["up", "down"]) -> bool` retornando True se moveu, False se na borda
- **FR-030**: StoryService.move_priority "up" DEVE trocar prioridade com historia de prioridade imediatamente menor (priority - 1)
- **FR-031**: StoryService.move_priority "down" DEVE trocar prioridade com historia de prioridade imediatamente maior (priority + 1)
- **FR-032**: StoryService.move_priority DEVE executar swap de prioridades atomicamente usando UnitOfWork
- **FR-033**: StoryService DEVE implementar metodo `async def assign_developer(story_id: str, developer_id: int | None) -> Story`
- **FR-034**: StoryService.assign_developer DEVE validar que desenvolvedor existe via DeveloperRepository.exists() quando developer_id nao e None
- **FR-035**: StoryService.assign_developer DEVE lancar ValueError com mensagem "Desenvolvedor nao encontrado: {developer_id}" se desenvolvedor nao existe
- **FR-036**: StoryService.assign_developer DEVE permitir developer_id=None para desalocar
- **FR-037**: StoryService DEVE implementar metodo `async def list_stories() -> Sequence[Story]` retornando todas as historias ordenadas por prioridade

#### Use Cases - Application Layer

- **FR-040**: Sistema DEVE implementar use cases em `src/backlog_manager/application/use_cases/story/`
- **FR-041**: Sistema DEVE implementar `CreateStoryUseCase` que coordena StoryService.create_story com UnitOfWork
- **FR-042**: Sistema DEVE implementar `UpdateStoryUseCase` que coordena StoryService.update_story com UnitOfWork
- **FR-043**: Sistema DEVE implementar `DeleteStoryUseCase` que coordena StoryService.delete_story com UnitOfWork
- **FR-044**: Sistema DEVE implementar `DuplicateStoryUseCase` que coordena StoryService.duplicate_story com UnitOfWork
- **FR-045**: Sistema DEVE implementar `ListStoriesUseCase` que coordena StoryService.list_stories com UnitOfWork
- **FR-046**: Sistema DEVE implementar `MovePriorityUseCase` que coordena StoryService.move_priority com UnitOfWork
- **FR-047**: Sistema DEVE implementar `AssignDeveloperUseCase` que coordena StoryService.assign_developer com UnitOfWork
- **FR-048**: Todos os use cases DEVEM ser classes async com metodo `async def execute(input_dto: InputDTO) -> OutputDTO`
- **FR-049**: Todos os use cases DEVEM receber UnitOfWork factory como dependencia no construtor
- **FR-050**: Todos os use cases DEVEM usar context manager do UnitOfWork para garantir transacoes atomicas
- **FR-051**: Todos os use cases DEVEM fazer commit no final de operacoes bem-sucedidas
- **FR-052**: Todos os use cases DEVEM fazer rollback automatico em caso de excecao

#### DTOs - Application Layer

- **FR-060**: Sistema DEVE implementar DTOs Pydantic em `src/backlog_manager/application/dto/story/`
- **FR-061**: Sistema DEVE implementar `CreateStoryInputDTO(BaseModel)` com campos: component (str), name (str), story_points (int), feature_id (int | None = None)
- **FR-062**: Sistema DEVE implementar `CreateStoryOutputDTO(BaseModel)` com campos: id (str), component (str), name (str), story_points (int), priority (int), status (str), feature_id (int | None)
- **FR-063**: Sistema DEVE implementar `UpdateStoryInputDTO(BaseModel)` com campos: story_id (str), name (str | None = None), story_points (int | None = None), status (str | None = None), feature_id (int | None = None), clear_feature (bool = False). Quando clear_feature=True, feature_id e explicitamente removido (set to NULL) independente do valor de feature_id no DTO.
- **FR-064**: Sistema DEVE implementar `StoryOutputDTO(BaseModel)` com todos os campos da entidade Story para retorno padronizado
- **FR-065**: Sistema DEVE implementar `ListStoriesOutputDTO(BaseModel)` com campo: stories (list[StoryOutputDTO])
- **FR-066**: Sistema DEVE implementar `MovePriorityInputDTO(BaseModel)` com campos: story_id (str), direction (Literal["up", "down"])
- **FR-067**: Sistema DEVE implementar `MovePriorityOutputDTO(BaseModel)` com campos: moved (bool), story (StoryOutputDTO)
- **FR-068**: Sistema DEVE implementar `AssignDeveloperInputDTO(BaseModel)` com campos: story_id (str), developer_id (int | None)
- **FR-069**: Todos os DTOs DEVEM usar validacao Pydantic para garantir tipos corretos
- **FR-070**: DTOs de output DEVEM incluir metodo `from_entity(entity: Story) -> Self` para conversao

### Key Entities

- **StoryService**: Domain service responsavel por regras de negocio de historias - geracao de ID, calculo de prioridade inicial, duplicacao, limpeza de dependencias, troca de prioridades. Recebe UnitOfWork como dependencia.
- **Use Cases**: Application services que coordenam StoryService com UnitOfWork para operacoes transacionais. Um use case por operacao (Create, Update, Delete, Duplicate, List, MovePriority, AssignDeveloper).
- **DTOs**: Objetos Pydantic para transporte de dados entre camadas. Input DTOs validam entrada, Output DTOs formatam saida. Desacoplam camada de aplicacao da camada de dominio.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuario consegue criar uma historia e o ID e gerado automaticamente no formato correto (COMPONENTE-NNN)
- **SC-002**: Usuario consegue listar todas as historias ordenadas por prioridade em tempo constante relativo ao tamanho do backlog
- **SC-003**: Usuario consegue editar qualquer campo de uma historia exceto ID/component, com persistencia imediata
- **SC-004**: Usuario consegue deletar uma historia e todas as dependencias relacionadas sao removidas automaticamente
- **SC-005**: Usuario consegue mover prioridade de historia para cima/baixo com troca atomica de posicoes
- **SC-006**: Usuario consegue duplicar historia recebendo copia com novo ID, sem dados de alocacao
- **SC-007**: Usuario consegue atribuir/desatribuir desenvolvedor a historia com validacao de existencia
- **SC-008**: Todas as operacoes sao transacionais - falhas resultam em rollback completo
- **SC-009**: Cobertura de testes unitarios do StoryService atinge 100% das regras de negocio
- **SC-010**: Cobertura de testes de integracao dos use cases atinge 100% dos fluxos de sucesso e erro

## Architectural Decisions

### ADR-001: Remocao em Lote de Dependencias

**Contexto**: RF-STORY-003 exige "remover referencias de dependencias" ao deletar historia. O protocolo atual tem apenas `remove(story_id, depends_on_id)` para pares individuais.

**Opcoes**:
1. Adicionar metodo `remove_all_for_story(story_id)` ao protocolo StoryDependencyRepository
2. Servico itera manualmente chamando `remove()` para cada dependencia

**Decisao**: Opcao 1 - Adicionar `remove_all_for_story(story_id: str) -> None` ao protocolo

**Justificativa**:
- Performance: Uma unica query SQL vs multiplas
- Atomicidade: Operacao unica e mais facil de garantir atomicidade
- Simplicidade: Menos codigo no servico
- Consistencia: Remove tanto dependencias onde story_id e dependente quanto onde e dependencia

### ADR-002: Geracao de Proximo ID

**Contexto**: Geracao automatica de IDs (COMPONENTE-NNN) exige consultar o maior numero existente para o componente. O protocolo atual nao tem metodo para isso.

**Opcoes**:
1. Adicionar `get_max_id_number(component: str) -> int` ao StoryRepository
2. Servico orquestra via `get_all()` e filtra/calcula
3. Adicionar `get_next_id(component: str) -> str` que retorna ID completo

**Decisao**: Opcao 1 - Adicionar `get_max_id_number(component: str) -> int`

**Justificativa**:
- Performance: Query especifica vs carregar todas as historias
- Separacao de responsabilidades: Repositorio fornece dados, servico gera ID
- Flexibilidade: Servico controla formato do ID
- Simplicidade: Retorna 0 se nao existir historia para o componente

### ADR-003: Mecanismo de Troca de Prioridade

**Contexto**: RF-STORY-006 (mover prioridade cima/baixo) requer encontrar historia adjacente em prioridade.

**Opcoes**:
1. Adicionar `get_by_priority_adjacent(priority, direction)` ao repositorio
2. Adicionar `get_by_priority(priority)` ao repositorio e logica de busca no servico
3. Servico busca via `get_all()` e encontra adjacente

**Decisao**: Opcao 2 - Adicionar `get_by_priority(priority: int) -> Story | None` e logica no servico

**Justificativa**:
- Query simples e reutilizavel
- Servico calcula prioridade adjacente (p-1 ou p+1)
- Permite detectar bordas facilmente (retorna None se nao existe)
- Swap de prioridades e simples: atualiza ambas historias

### ADR-004: Validacao de developer_id na Atribuicao

**Contexto**: RF-STORY-007 exige "validar existencia" do desenvolvedor. EP-004 (CRUD de desenvolvedores) nao foi implementado ainda, mas DeveloperRepository.exists() ja existe no protocolo.

**Opcoes**:
1. Validar via DeveloperRepository.exists() (se disponivel)
2. Validar apenas formato (inteiro positivo)
3. Nao validar (deixar FK do banco falhar)

**Decisao**: Opcao 1 - Validar via DeveloperRepository.exists()

**Justificativa**:
- Protocolo DeveloperRepository ja define `exists(developer_id)` - ja implementado em EP-001
- Mensagem de erro mais clara que violacao de FK
- Fail-fast: erro antes de tentar persistir
- Se desenvolvedor nao existir, lancar ValueError explicativo

### ADR-005: Localizacao da Logica de Prioridade Inicial

**Contexto**: Epico define "prioridade inicial = max(existentes) + 1".

**Opcoes**:
1. Logica no StoryService (consulta max e atribui)
2. Logica no StoryRepository (calcula durante add)
3. Trigger no banco de dados

**Decisao**: Opcao 1 - Logica no StoryService

**Justificativa**:
- Regra de negocio pertence ao dominio, nao a infraestrutura
- Testavel em isolamento com mocks
- Precisa de `get_max_priority()` no repositorio
- Servico tem controle total sobre a atribuicao

### ADR-006: Campos Copiados/Resetados na Duplicacao

**Contexto**: RF-STORY-004 exige "copiar dados, limpar alocacao (dev=NULL, start_date=NULL)".

**Opcoes**:
1. Copiar todos os campos exceto alocacao
2. Copiar apenas campos essenciais, resetar resto

**Decisao**: Definicao explicita dos campos:

**Campos COPIADOS**:
- component (extraido do ID original para gerar novo ID)
- name
- story_points
- feature_id

**Campos RESETADOS/CALCULADOS**:
- id: Novo ID gerado (COMPONENTE-NNN)
- priority: max(existentes) + 1
- status: BACKLOG (sempre, independente do original)
- developer_id: NULL
- start_date: NULL
- end_date: NULL
- duration: NULL

**Justificativa**:
- Historia duplicada e uma nova historia independente
- Dados de alocacao/cronograma nao fazem sentido copiar
- Status BACKLOG garante que historia entra no fluxo normal
- Feature_id mantido pois representa agrupamento logico

### ADR-007: Tratamento de Gaps de Prioridade

**Contexto**: Epico lista "Prioridades sao sempre contiguas (1, 2, 3...)" como premissa com mitigacao "Implementar reordenacao se houver gaps".

**Opcoes**:
1. Garantir contiguidade por invariante (swap nunca cria gaps)
2. Permitir gaps e compactar sob demanda
3. Permitir gaps sem compactacao

**Decisao**: Opcao 1 - Garantir contiguidade por invariante

**Justificativa**:
- Operacao de criar sempre usa max+1 (sem gaps)
- Operacao de mover faz swap de prioridades (sem gaps)
- Operacao de deletar: Gaps podem surgir. Decisao: Nao compactar automaticamente
- Trade-off: Aceitar gaps temporarios apos delecao, prioridades continuam funcionais
- Complexidade de compactacao nao justifica o beneficio para v1
- Futuro: Se necessario, adicionar operacao explicita de compactacao

**Nota**: Mesmo com gaps, ordenacao por prioridade funciona corretamente. Gaps sao apenas esteticos.

## Traceability Matrix

### Requisitos do Epico -> Requisitos Funcionais

| Requisito Epico | Requisitos Funcionais |
|-----------------|----------------------|
| RF-STORY-001: Criar Nova Historia | FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-041, FR-061, FR-062 |
| RF-STORY-002: Editar Historia | FR-018, FR-019, FR-020, FR-042, FR-063 |
| RF-STORY-003: Deletar Historia | FR-004, FR-021, FR-022, FR-023, FR-043 |
| RF-STORY-004: Duplicar Historia | FR-024, FR-025, FR-026, FR-027, FR-028, FR-044 |
| RF-STORY-005: Listar Historias | FR-037, FR-045, FR-064, FR-065 |
| RF-STORY-006: Mover Prioridade | FR-003, FR-029, FR-030, FR-031, FR-032, FR-046, FR-066, FR-067 |
| RF-STORY-007: Atribuir Desenvolvedor | FR-033, FR-034, FR-035, FR-036, FR-047, FR-068 |

## Assumptions

- DeveloperRepository.exists() esta implementado e funcional (EP-001)
- UnitOfWork gerencia transacoes corretamente com commit/rollback automatico
- Entidade Story valida todos os invariantes no construtor (EP-002)
- Banco de dados SQLite com foreign keys habilitadas (EP-001)
- Historias existentes tem prioridades unicas e positivas
- Componente de uma historia e imutavel apos criacao
- Status padrao para novas historias e historias duplicadas e sempre BACKLOG
