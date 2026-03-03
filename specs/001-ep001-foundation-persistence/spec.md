# Feature Specification: EP-001 Fundacao e Persistencia

**Feature Branch**: `001-ep001-foundation-persistence`
**Created**: 2026-02-28
**Status**: Draft
**Input**: Especificacao tecnica de implementacao do epico EP-001 (Fundacao e Persistencia): estrutura de projeto 4 camadas, banco SQLite com schema das 4 tabelas, hierarquia de excecoes, sistema de logging, pipeline de qualidade de codigo

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configuracao do Ambiente de Desenvolvimento (Priority: P1)

Como desenvolvedor do projeto, preciso de um ambiente Python configurado corretamente para que eu possa comecar a implementar funcionalidades do Backlog Manager sem configuracao adicional.

**Why this priority**: Esta e a fundacao absoluta — sem estrutura de projeto e dependencias configuradas, nenhum outro trabalho pode comecar. Todos os 8 epicos subsequentes dependem deste setup inicial.

**Independent Test**: Pode ser testado executando `pip install -e .` em um ambiente limpo e verificando que o pacote e importavel.

**Acceptance Scenarios**:

1. **Given** um ambiente Python 3.11+ limpo, **When** executo `pip install -e .` na raiz do projeto, **Then** todas as dependencias sao instaladas sem erros e o modulo `backlog_manager` e importavel
2. **Given** o projeto instalado, **When** executo `python -c "import backlog_manager"`, **Then** nenhum erro de importacao ocorre
3. **Given** o projeto instalado, **When** executo `pytest --collect-only`, **Then** a estrutura de testes e reconhecida e coletavel

---

### User Story 2 - Banco de Dados SQLite Operacional (Priority: P1)

Como sistema Backlog Manager, preciso de um banco de dados SQLite com schema completo para que eu possa persistir e recuperar dados de historias, desenvolvedores, features e dependencias.

**Why this priority**: Sem persistencia, os dados seriam perdidos entre sessoes. Este e o segundo pilar fundamental, habilitando todas as operacoes CRUD dos epicos posteriores.

**Independent Test**: Pode ser testado criando uma conexao com o banco, executando operacoes CRUD basicas e verificando constraints.

**Acceptance Scenarios**:

1. **Given** o modulo de banco de dados, **When** inicializo o banco pela primeira vez, **Then** as 4 tabelas (Story, Story_Dependency, Developer, Feature) sao criadas com todas as constraints
2. **Given** uma tabela Story vazia, **When** insiro uma historia valida, **Then** a historia e persistida com todos os campos
3. **Given** uma historia existente, **When** tento inserir story_points=7 (invalido), **Then** a operacao falha com violacao de CHECK constraint
4. **Given** uma historia com developer_id apontando para Developer inexistente, **When** tento inserir, **Then** a operacao falha com violacao de FK
5. **Given** uma transacao em andamento, **When** ocorre um erro, **Then** rollback e executado e dados permanecem consistentes

---

### User Story 3 - Hierarquia de Excecoes Customizadas (Priority: P2)

Como desenvolvedor dos servicos de negocio, preciso de excecoes customizadas bem definidas para que eu possa tratar erros de forma especifica e fornecer mensagens claras ao usuario.

**Why this priority**: Excecoes sao necessarias para tratamento de erros em todos os epicos subsequentes, especialmente EP-005 (dependencias) e EP-007 (alocacao).

**Independent Test**: Pode ser testado importando o modulo de excecoes e verificando a hierarquia de heranca.

**Acceptance Scenarios**:

1. **Given** o modulo de excecoes, **When** importo `BacklogManagerException`, **Then** ela herda de `Exception`
2. **Given** a hierarquia de excecoes, **When** capturo `BacklogManagerException`, **Then** todas as excecoes filhas (DependencyException, FeatureException, AllocationException) sao capturadas
3. **Given** a excecao `CyclicDependencyException`, **When** instancio com `path=["A", "B", "C", "A"]`, **Then** a mensagem inclui o caminho do ciclo
4. **Given** o warning `DeadlockWarning`, **When** emito via `warnings.warn()`, **Then** ele pode ser capturado e filtrado separadamente

---

### User Story 4 - Sistema de Logging Configurado (Priority: P2)

Como operador do sistema, preciso de logs persistentes em local padronizado para que eu possa diagnosticar problemas e auditar operacoes criticas.

**Why this priority**: Logging e essencial para diagnostico de problemas em producao, mas nao bloqueia o desenvolvimento inicial das funcionalidades.

**Independent Test**: Pode ser testado executando uma operacao logavel e verificando a criacao do arquivo em AppData.

**Acceptance Scenarios**:

1. **Given** o sistema de logging configurado, **When** registro uma mensagem de INFO, **Then** a mensagem e gravada em `%APPDATA%/BacklogManager/logs/`
2. **Given** um arquivo de log com 10MB, **When** registro uma nova mensagem, **Then** rotacao ocorre e arquivo anterior e mantido (maximo 3 arquivos)
3. **Given** o logger, **When** registro mensagens de diferentes niveis (DEBUG, INFO, WARNING, ERROR), **Then** o formato inclui timestamp, nivel e mensagem
4. **Given** o diretorio AppData nao existente, **When** inicializo o logger, **Then** o diretorio e criado automaticamente

---

### User Story 5 - Pipeline de Qualidade de Codigo (Priority: P3)

Como desenvolvedor contribuindo com o projeto, preciso de ferramentas de qualidade de codigo configuradas para que eu mantenha padroes consistentes e detecte problemas antes do commit.

**Why this priority**: Qualidade de codigo e importante para manutenibilidade a longo prazo, mas nao bloqueia a implementacao de funcionalidades basicas.

**Independent Test**: Pode ser testado executando `pre-commit run --all-files` e verificando que todos os hooks passam.

**Acceptance Scenarios**:

1. **Given** pre-commit instalado, **When** faco commit com codigo mal formatado, **Then** black/isort reformatam automaticamente
2. **Given** pytest configurado, **When** executo `pytest --cov`, **Then** relatorio de cobertura e gerado
3. **Given** codigo fonte, **When** executo `pydocstyle src/`, **Then** docstrings faltantes em classes/metodos publicos sao reportadas
4. **Given** codigo com complexidade ciclomatica > 10, **When** executo verificacao, **Then** warning e emitido

---

### Edge Cases

- O que acontece quando AppData nao e acessivel (permissoes negadas)? Sistema deve falhar graciosamente com mensagem clara
- O que acontece quando banco de dados esta corrompido? Sistema deve detectar e sugerir recriacao
- O que acontece quando multiplas instancias tentam acessar o banco? SQLite gerencia locks; operacoes devem aguardar ou falhar com timeout
- O que acontece quando FK referencia registro que foi deletado? ON DELETE SET NULL para developer_id, ON DELETE CASCADE para story_dependency

## Requirements *(mandatory)*

### Functional Requirements

#### Estrutura de Projeto

- **FR-001**: Sistema DEVE organizar codigo em 4 camadas distintas: UI (Apresentacao), Services (Servicos), Domain (Entidades), Repository (Persistencia)
- **FR-002**: Sistema DEVE expor pacote instalavel via `pip install -e .` com entry point configurado
- **FR-003**: Sistema DEVE incluir estrutura de testes espelhando a estrutura de codigo fonte

#### Banco de Dados SQLite

- **FR-004**: Sistema DEVE criar banco de dados SQLite em `%APPDATA%/BacklogManager/data/backlog.db`
- **FR-005**: Sistema DEVE criar tabela `Story` com colunas: id (PK VARCHAR(20)), component (VARCHAR(50) NOT NULL), name (VARCHAR(200) NOT NULL), story_points (INTEGER NOT NULL CHECK IN (3,5,8,13)), priority (INTEGER NOT NULL CHECK >= 0), status (VARCHAR(20) NOT NULL DEFAULT 'BACKLOG'), duration (INTEGER NULL), start_date (DATE NULL), end_date (DATE NULL), developer_id (FK INTEGER NULL), feature_id (FK INTEGER NULL)
- **FR-006**: Sistema DEVE criar tabela `Story_Dependency` com colunas: story_id (FK VARCHAR(20) NOT NULL), depends_on_id (FK VARCHAR(20) NOT NULL), com UNIQUE(story_id, depends_on_id) e CHECK(story_id != depends_on_id)
- **FR-007**: Sistema DEVE criar tabela `Developer` com colunas: id (PK INTEGER AUTOINCREMENT), name (VARCHAR(100) NOT NULL)
- **FR-008**: Sistema DEVE criar tabela `Feature` com colunas: id (PK INTEGER AUTOINCREMENT), name (VARCHAR(100) NOT NULL UNIQUE), wave (INTEGER NOT NULL UNIQUE CHECK > 0)
- **FR-009**: Sistema DEVE habilitar `PRAGMA foreign_keys = ON` para enforcement de FKs
- **FR-010**: Sistema DEVE usar prepared statements (parametrizados) em 100% das queries SQL
- **FR-011**: Sistema DEVE executar commit imediato apos cada operacao de escrita (auto-save)
- **FR-012**: Sistema DEVE implementar ON DELETE SET NULL para Story.developer_id quando Developer e deletado
- **FR-013**: Sistema DEVE implementar ON DELETE CASCADE para Story_Dependency quando Story e deletada

#### Hierarquia de Excecoes

- **FR-014**: Sistema DEVE definir `BacklogManagerException` como excecao base customizada herdando de `Exception`
- **FR-015**: Sistema DEVE definir `DependencyException` herdando de `BacklogManagerException`
- **FR-016**: Sistema DEVE definir `CyclicDependencyException` herdando de `DependencyException` com atributo `path: list[str]`
- **FR-017**: Sistema DEVE definir `InvalidWaveDependencyException` herdando de `DependencyException`
- **FR-018**: Sistema DEVE definir `FeatureException` herdando de `BacklogManagerException`
- **FR-019**: Sistema DEVE definir `DuplicateWaveException` herdando de `FeatureException`
- **FR-020**: Sistema DEVE definir `FeatureHasStoriesException` herdando de `FeatureException`
- **FR-021**: Sistema DEVE definir `AllocationException` herdando de `BacklogManagerException`
- **FR-022**: Sistema DEVE definir `MaxIterationsExceeded` herdando de `AllocationException`
- **FR-023**: Sistema DEVE definir `BacklogWarning` herdando de `Warning`
- **FR-024**: Sistema DEVE definir `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo` herdando de `BacklogWarning`

#### Sistema de Logging

- **FR-025**: Sistema DEVE criar logs em `%APPDATA%/BacklogManager/logs/backlog_manager.log`
- **FR-026**: Sistema DEVE configurar rotacao de logs: maximo 10MB por arquivo, retencao de 3 arquivos
- **FR-027**: Sistema DEVE incluir no formato de log: timestamp ISO 8601, nivel (DEBUG/INFO/WARNING/ERROR/CRITICAL), nome do logger, mensagem
- **FR-028**: Sistema DEVE criar diretorio de logs automaticamente se nao existir

#### Pipeline de Qualidade

- **FR-029**: Sistema DEVE configurar pytest com plugin pytest-cov para medicao de cobertura
- **FR-030**: Sistema DEVE configurar black com line-length=88 como formatador
- **FR-031**: Sistema DEVE configurar isort compativel com black para ordenacao de imports
- **FR-032**: Sistema DEVE configurar pydocstyle para validacao de docstrings Google Style
- **FR-033**: Sistema DEVE configurar pre-commit com hooks: black, isort, flake8
- **FR-034**: Sistema DEVE configurar pyproject.toml com metadados do projeto e dependencias

### Key Entities

- **Story**: Unidade de trabalho (User Story) com identificador unico no formato COMPONENTE-NNN, pontos fibonacci (3,5,8,13), status de workflow, e relacionamentos opcionais com Developer e Feature
- **Story_Dependency**: Relacao N:M auto-referenciada entre Stories, representando que uma historia so pode iniciar apos outra terminar
- **Developer**: Pessoa que executa historias, com identificador unico auto-incrementado e nome
- **Feature**: Agrupamento de historias em ondas de entrega sequenciais (wave 1 entrega antes de wave 2)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Desenvolvedores conseguem clonar repositorio e executar `pip install -e .` seguido de `pytest` em menos de 5 minutos
- **SC-002**: Sistema persiste dados entre sessoes com zero perda de dados em operacoes normais
- **SC-003**: 100% das operacoes de banco de dados usam prepared statements (auditavel por inspecao de codigo)
- **SC-004**: Todas as 4 tabelas sao criadas com constraints corretas na primeira inicializacao
- **SC-005**: Logs sao criados automaticamente em AppData sem intervencao manual
- **SC-006**: Pre-commit hooks executam sem erros em codigo formatado corretamente
- **SC-007**: Cobertura de testes do codigo de infraestrutura atinge minimo de 80%
- **SC-008**: Todas as excecoes customizadas sao capturaveis por sua excecao base
- **SC-009**: Sistema inicia corretamente em Windows 10 e Windows 11
- **SC-010**: Banco de dados suporta ate 500 historias sem degradacao perceptivel de performance
