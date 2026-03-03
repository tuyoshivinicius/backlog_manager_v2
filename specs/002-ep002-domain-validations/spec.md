# Feature Specification: EP-002 Dominio Core - Entidades e Validacoes

**Feature Branch**: `002-ep002-domain-validations`
**Created**: 2026-02-28
**Status**: Draft
**Input**: Aprimoramento das entidades Story, Developer e Feature com validacoes completas de invariantes, maquina de estados corrigida conforme SRS 6.5, e regras de negocio implicitas do SRS 8.3

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validacao de Story Points (Priority: P1)

Como desenvolvedor do sistema, preciso que a entidade Story valide rigorosamente os valores de Story Points para garantir que apenas valores Fibonacci validos sejam aceitos, mantendo a consistencia das estimativas no backlog.

**Why this priority**: Story Points e o campo mais fundamental para calculo de duracao e planejamento. Valores invalidos comprometem todo o algoritmo de alocacao e cronograma.

**Independent Test**: Pode ser testado criando instancias de Story com diferentes valores de story_points e verificando que apenas {3, 5, 8, 13} sao aceitos.

**Acceptance Scenarios**:

1. **Given** um valor de Story Points = 5, **When** crio uma Story com esse valor, **Then** a Story e criada com sucesso e story_points = StoryPoint.MEDIUM
2. **Given** um valor de Story Points = 7 (invalido), **When** tento criar uma Story com esse valor, **Then** ValueError e lancado com mensagem "Story points deve ser 3, 5, 8 ou 13: 7"
3. **Given** valores de Story Points = 1, 2, 4, 10, 20 (invalidos), **When** tento criar Stories com esses valores, **Then** ValueError e lancado para cada tentativa

---

### User Story 2 - Maquina de Estados do Status (Priority: P1)

Como desenvolvedor do sistema, preciso que a entidade Story utilize os 5 estados corretos conforme SRS 6.5 (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) para representar adequadamente o fluxo de trabalho das historias.

**Why this priority**: O status controla o workflow das historias. Usar estados incorretos (como os atuais em ingles) gera inconsistencia com o SRS e com a interface em PT-BR.

**Independent Test**: Pode ser testado verificando que StoryStatus possui exatamente os 5 valores especificados e que Story aceita qualquer um deles.

**Acceptance Scenarios**:

1. **Given** StoryStatus enum, **When** verifico os valores disponiveis, **Then** existem exatamente 5 valores: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO
2. **Given** uma Story existente com status BACKLOG, **When** altero para EXECUCAO, **Then** a mudanca e aceita sem erros
3. **Given** uma Story existente, **When** altero status de IMPEDIDO para CONCLUIDO diretamente, **Then** a mudanca e aceita (transicoes livres conforme SRS)
4. **Given** uma nova Story criada sem status explicito, **When** verifico seu status, **Then** status = BACKLOG (estado inicial padrao)

---

### User Story 3 - Validacao de Invariantes da Entidade Story (Priority: P1)

Como desenvolvedor do sistema, preciso que a entidade Story valide todos os seus invariantes no construtor para garantir que nenhuma instancia invalida possa ser criada, protegendo a integridade dos dados.

**Why this priority**: Validacoes no construtor sao a primeira linha de defesa contra dados invalidos. Sem elas, dados corrompidos podem propagar por todo o sistema.

**Independent Test**: Pode ser testado criando Stories com diferentes combinacoes de campos invalidos e verificando as excecoes correspondentes.

**Acceptance Scenarios**:

1. **Given** ID vazio ou None, **When** crio uma Story, **Then** ValueError e lancado com mensagem "ID da historia nao pode ser vazio"
2. **Given** ID que nao segue padrao COMPONENTE-NNN (ex: "invalid"), **When** crio uma Story, **Then** ValueError e lancado com mensagem "ID deve seguir padrao COMPONENTE-NNN: invalid"
3. **Given** component vazio ou apenas espacos, **When** crio uma Story, **Then** ValueError e lancado com mensagem "Componente nao pode ser vazio"
4. **Given** component com mais de 50 caracteres, **When** crio uma Story, **Then** ValueError e lancado com mensagem "Componente nao pode exceder 50 caracteres"
5. **Given** name vazio ou apenas espacos, **When** crio uma Story, **Then** ValueError e lancado com mensagem "Nome da historia nao pode ser vazio"
6. **Given** name com mais de 200 caracteres, **When** crio uma Story, **Then** ValueError e lancado com mensagem "Nome da historia nao pode exceder 200 caracteres"
7. **Given** priority negativa (ex: -1), **When** crio uma Story, **Then** ValueError e lancado com mensagem "Prioridade deve ser >= 0: -1"
8. **Given** duration negativa (ex: -1), **When** crio uma Story, **Then** ValueError e lancado com mensagem "Duracao deve ser >= 0: -1"
9. **Given** start_date posterior a end_date, **When** crio uma Story, **Then** ValueError e lancado com mensagem "Data de inicio nao pode ser posterior a data de termino"

---

### User Story 4 - Validacao de Duracao (Priority: P2)

Como desenvolvedor do sistema, preciso que a entidade Story valide o campo duration para aceitar apenas valores nao-negativos, conforme regra implicita do SRS 8.3 que estabelece duracao minima de 1 dia para historias executadas.

**Why this priority**: Duration e usado no calculo de cronograma. Valores negativos ou zero em historias alocadas causariam erros de calculo.

**Independent Test**: Pode ser testado criando Stories com diferentes valores de duration e verificando a validacao.

**Acceptance Scenarios**:

1. **Given** duration = None, **When** crio uma Story, **Then** a Story e criada com sucesso (duration e opcional antes do calculo)
2. **Given** duration = 0, **When** crio uma Story, **Then** a Story e criada com sucesso (0 indica historia nao calculada)
3. **Given** duration = 3, **When** crio uma Story, **Then** a Story e criada com sucesso
4. **Given** duration = -1, **When** crio uma Story, **Then** ValueError e lancado com mensagem "Duracao deve ser >= 0: -1"

---

### User Story 5 - Validacao de Auto-dependencia no Repositorio (Priority: P2)

Como desenvolvedor do sistema, preciso que o repositorio de dependencias valide que uma historia nao pode depender de si mesma, prevenindo ciclos triviais no grafo de dependencias.

**Why this priority**: Auto-dependencia e o caso mais basico de ciclo invalido. Deve ser rejeitado imediatamente ao adicionar dependencia.

**Independent Test**: Pode ser testado tentando adicionar uma dependencia de uma historia para ela mesma via repositorio.

**Acceptance Scenarios**:

1. **Given** historia com ID "AUTH-001", **When** tento adicionar dependencia "AUTH-001" -> "AUTH-001", **Then** ValueError e lancado com mensagem "Historia nao pode depender de si mesma"
2. **Given** historia A e historia B diferentes, **When** adiciono dependencia A -> B, **Then** a dependencia e adicionada com sucesso

---

### User Story 6 - Validacao de Entidade Developer (Priority: P2)

Como desenvolvedor do sistema, preciso que a entidade Developer valide seus invariantes no construtor para garantir integridade dos dados de desenvolvedores.

**Why this priority**: Desenvolvedores sao alocados a historias. Nomes invalidos comprometem a identificacao e rastreabilidade.

**Independent Test**: Pode ser testado criando Developers com diferentes valores de nome e verificando validacoes.

**Acceptance Scenarios**:

1. **Given** name valido "Ana Silva", **When** crio um Developer, **Then** o Developer e criado com sucesso
2. **Given** name vazio ou None, **When** crio um Developer, **Then** ValueError e lancado com mensagem "Nome do desenvolvedor nao pode ser vazio"
3. **Given** name apenas com espacos "   ", **When** crio um Developer, **Then** ValueError e lancado com mensagem "Nome do desenvolvedor nao pode ser vazio"
4. **Given** name com mais de 100 caracteres, **When** crio um Developer, **Then** ValueError e lancado com mensagem "Nome do desenvolvedor nao pode exceder 100 caracteres"

---

### User Story 7 - Validacao de Entidade Feature (Priority: P2)

Como desenvolvedor do sistema, preciso que a entidade Feature valide seus invariantes (name e wave) no construtor conforme regras do SRS 8.3.

**Why this priority**: Features organizam historias em ondas de entrega. Waves invalidas comprometem a ordenacao de processamento.

**Independent Test**: Pode ser testado criando Features com diferentes valores de name e wave e verificando validacoes.

**Acceptance Scenarios**:

1. **Given** name valido "Autenticacao" e wave = 1, **When** crio uma Feature, **Then** a Feature e criada com sucesso
2. **Given** name vazio ou None, **When** crio uma Feature, **Then** ValueError e lancado com mensagem "Nome da feature nao pode ser vazio"
3. **Given** name com mais de 100 caracteres, **When** crio uma Feature, **Then** ValueError e lancado com mensagem "Nome da feature nao pode exceder 100 caracteres"
4. **Given** wave = 0, **When** crio uma Feature, **Then** ValueError e lancado com mensagem "Wave deve ser > 0: 0"
5. **Given** wave = -1, **When** crio uma Feature, **Then** ValueError e lancado com mensagem "Wave deve ser > 0: -1"

---

### Edge Cases

- O que acontece quando ID tem formato correto mas componente nao corresponde? Sistema aceita (ID e validado apenas por regex, nao por consistencia com campo component)
- O que acontece quando story_points e passado como int em vez de StoryPoint enum? Sistema converte automaticamente se valor valido, ou lanca ValueError se invalido
- O que acontece quando status string e passado em vez de StoryStatus enum? Sistema deve usar o enum; strings devem ser convertidas na camada de servico/repositorio
- O que acontece quando duration e 0 mas historia esta alocada? 0 e aceito na entidade; regra de duracao minima 1 e aplicada no calculo de cronograma (RF-SCHED-001)

## Requirements *(mandatory)*

### Functional Requirements

#### Validacao de Story Points (RF-STORY-008)

- **FR-001**: Entidade Story DEVE aceitar apenas valores de story_points pertencentes ao conjunto {3, 5, 8, 13}
- **FR-002**: Entidade Story DEVE converter automaticamente inteiros validos {3, 5, 8, 13} para o enum StoryPoint correspondente
- **FR-003**: Entidade Story DEVE lancar ValueError com mensagem descritiva quando story_points nao pertence ao conjunto valido
- **FR-004**: Value Object StoryPoint DEVE definir exatamente 4 valores: SMALL(3), MEDIUM(5), LARGE(8), EXTRA_LARGE(13)

#### Maquina de Estados - Status (RF-STORY-009)

- **FR-005**: Value Object StoryStatus DEVE definir exatamente 5 estados: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO (valores em maiusculas, sem acento)
- **FR-006**: Entidade Story DEVE usar StoryStatus.BACKLOG como valor padrao quando status nao for especificado
- **FR-007**: Entidade Story DEVE permitir transicao livre entre quaisquer estados (modelo flexivel conforme SRS 6.5)
- **FR-008**: Migracao de dados existentes DEVE mapear: BACKLOG -> BACKLOG, IN_PROGRESS -> EXECUCAO, BLOCKED -> IMPEDIDO, DONE -> CONCLUIDO

#### Validacao de Invariantes da Historia (RF-STORY-010)

- **FR-009**: Entidade Story DEVE validar que id nao e None, vazio ou apenas espacos em branco
- **FR-010**: Entidade Story DEVE validar que id segue padrao regex `^[A-Z]+-\d{3}$` (ex: AUTH-001, CORE-042)
- **FR-011**: Entidade Story DEVE validar que component nao e None, vazio ou apenas espacos em branco
- **FR-012**: Entidade Story DEVE validar que component tem no maximo 50 caracteres
- **FR-013**: Entidade Story DEVE validar que name nao e None, vazio ou apenas espacos em branco
- **FR-014**: Entidade Story DEVE validar que name tem no maximo 200 caracteres
- **FR-015**: Entidade Story DEVE validar que priority >= 0
- **FR-016**: Entidade Story DEVE validar que duration >= 0 quando duration nao for None
- **FR-017**: Entidade Story DEVE validar que start_date <= end_date quando ambas as datas estao definidas
- **FR-018**: Todas as validacoes DEVEM ser executadas no `__post_init__` da dataclass
- **FR-019**: Todas as validacoes DEVEM lancar ValueError com mensagem descritiva em portugues (sem acentos)

#### Validacao de Auto-dependencia

- **FR-020**: Repositorio de dependencias DEVE rejeitar adicao de dependencia onde story_id == depends_on_id
- **FR-021**: Rejeicao de auto-dependencia DEVE lancar ValueError com mensagem "Historia nao pode depender de si mesma"

#### Validacao de Entidade Developer

- **FR-022**: Entidade Developer DEVE validar que name nao e None, vazio ou apenas espacos em branco
- **FR-023**: Entidade Developer DEVE validar que name tem no maximo 100 caracteres
- **FR-024**: Validacoes DEVEM ser executadas no `__post_init__` da dataclass

#### Validacao de Entidade Feature

- **FR-025**: Entidade Feature DEVE validar que name nao e None, vazio ou apenas espacos em branco
- **FR-026**: Entidade Feature DEVE validar que name tem no maximo 100 caracteres
- **FR-027**: Entidade Feature DEVE validar que wave > 0
- **FR-028**: Validacoes DEVEM ser executadas no `__post_init__` da dataclass

### Key Entities

- **Story**: Unidade de trabalho com ID (COMPONENTE-NNN), component, name, story_points (Fibonacci), priority, status (5 estados), duration, datas e relacionamentos. Valida todos os invariantes no construtor.
- **StoryPoint**: Value Object enum com valores Fibonacci {3, 5, 8, 13} representando complexidade da historia.
- **StoryStatus**: Value Object enum com 5 estados do workflow: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO.
- **Developer**: Pessoa que executa historias, com name validado (max 100 chars).
- **Feature**: Agrupamento de historias em ondas de entrega, com name (max 100 chars) e wave (> 0).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das tentativas de criar Story com story_points fora de {3, 5, 8, 13} resultam em ValueError
- **SC-002**: 100% das tentativas de criar Story com ID, component ou name vazios resultam em ValueError
- **SC-003**: 100% das tentativas de criar Story com priority ou duration negativos resultam em ValueError
- **SC-004**: StoryStatus enum possui exatamente 5 valores: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO
- **SC-005**: 100% das transicoes de status sao aceitas (modelo flexivel)
- **SC-006**: 100% das tentativas de adicionar auto-dependencia resultam em ValueError
- **SC-007**: 100% das tentativas de criar Developer com name vazio ou > 100 chars resultam em ValueError
- **SC-008**: 100% das tentativas de criar Feature com name vazio, wave <= 0 resultam em ValueError
- **SC-009**: Cobertura de testes unitarios das validacoes atinge 100%
- **SC-010**: Todos os testes de boundary (limites) passam: 50 chars para component, 200 chars para name, 100 chars para dev/feature name

## Conflict Resolution Decisions

Esta secao documenta as decisoes tomadas para resolver os conflitos identificados entre o codigo atual (EP-001) e o SRS/Epico EP-002:

### Conflito 1: StoryStatus (4 estados em ingles vs 5 estados em portugues)

**Decisao**: Adotar os 5 estados do SRS 6.5 (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)

**Justificativa**: O SRS e a especificacao oficial. A interface sera em PT-BR. Os valores internos devem ser sem acento para compatibilidade com banco de dados.

**Migracao**: Mapear valores existentes: BACKLOG -> BACKLOG, IN_PROGRESS -> EXECUCAO, BLOCKED -> IMPEDIDO, DONE -> CONCLUIDO. O novo estado TESTES nao tem correspondente no codigo atual.

### Conflito 2: Story.dependencies e validacao de auto-dependencia

**Decisao**: Validacao de auto-dependencia fica no REPOSITORIO de dependencias, nao na entidade Story

**Justificativa**:
- Entidade Story NAO possui campo `dependencies` (dependencias sao gerenciadas na tabela Story_Dependency)
- A validacao deve ocorrer no momento de adicionar a dependencia, nao na criacao da Story
- Repositorio ja e responsavel por operacoes na tabela Story_Dependency
- Manter entidade Story focada em seus proprios invariantes

### Conflito 3: Story.duration (None vs 0 vs valor minimo 1)

**Decisao**: Entidade aceita duration = None (nao calculado) ou duration >= 0. Regra de duracao minima 1 e aplicada no CALCULO de cronograma (RF-SCHED-001), nao na entidade.

**Justificativa**:
- duration = None indica historia ainda nao calculada
- duration = 0 pode indicar estado intermediario ou historia sem duracao definida
- A regra "duracao minima = 1 dia util" do SRS 8.3 refere-se ao RESULTADO do calculo, nao a validacao da entidade
- Calculo de cronograma aplica `max(1, ceil(sp/velocity))` conforme RF-SCHED-001

### Conflito 4: Story.developer_id (string vazia vs INTEGER NULL)

**Decisao**: developer_id e INTEGER NULL no schema. Validacao de "string vazia" NAO se aplica.

**Justificativa**:
- Schema define developer_id como INTEGER NULL (FK para Developer.id)
- A mencao no SRS RF-STORY-007 sobre "string vazia" parece ser de versao anterior onde developer_id era string
- Com tipo INTEGER, valores validos sao: NULL (nao alocado) ou inteiro positivo (ID do desenvolvedor)
- Validacao de developer_id existente fica no servico de alocacao, nao na entidade

## Assumptions

- Validacoes sao sincronas e executadas no construtor (`__post_init__`)
- Entidades sao sempre validas apos criacao bem-sucedida (fail-fast)
- Mensagens de erro em portugues sem acentos para compatibilidade
- Migracao de dados de status existentes sera tratada em script separado ou automaticamente no repositorio
- Testes unitarios devem cobrir 100% das validacoes com casos de sucesso e falha
