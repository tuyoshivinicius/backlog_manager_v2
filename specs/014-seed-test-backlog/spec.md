# Feature Specification: Script de Seed para Teste de Alocacao

**Feature Branch**: `014-seed-test-backlog`
**Created**: 2026-03-12
**Status**: Draft
**Input**: User description: "Criar Script de Seed para popular banco de dados com dados de teste volumosos para validar motor de alocacao (EP-007) e calculo de cronograma (EP-006)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Gerar Backlog de Teste Completo (Priority: P1)

Como desenvolvedor ou QA, quero executar um script que popula o banco de dados com um backlog realista de 150-200 historias, para validar o comportamento do sistema com volume de dados proximo ao de producao.

**Why this priority**: Esta e a funcionalidade principal do script - sem ela, nao ha como testar os motores de alocacao e cronograma com dados volumosos.

**Independent Test**: Pode ser testado executando o script e verificando contagens no banco de dados.

**Acceptance Scenarios**:

1. **Given** banco de dados vazio, **When** executo `python scripts/seed_test_backlog.py`, **Then** sao criados exatamente 7 desenvolvedores com nomes: Ana, Bruno, Carlos, Diana, Eduardo, Fernanda, Gabriel
2. **Given** banco de dados vazio, **When** executo o script de seed, **Then** sao criadas aproximadamente 30 features distribuidas em 7 ondas (4-5 features por onda)
3. **Given** banco de dados vazio, **When** executo o script de seed, **Then** sao criadas entre 150 e 200 historias com story points variados (3, 5, 8, 13)
4. **Given** banco de dados vazio, **When** executo o script de seed, **Then** sao criadas entre 80 e 120 dependencias entre historias

---

### User Story 2 - Garantir Integridade de Dependencias (Priority: P1)

Como desenvolvedor, quero que o script gere dependencias sem ciclos e respeitando regras de onda, para garantir que os dados de teste sejam validos para o motor de alocacao.

**Why this priority**: Dependencias invalidas (ciclos, ondas invertidas) impediriam o uso dos dados de teste pelo motor de alocacao.

**Independent Test**: Pode ser testado executando validacao de ciclos apos seed e verificando regras de onda.

**Acceptance Scenarios**:

1. **Given** script de seed executado, **When** executo deteccao de ciclos no grafo de dependencias, **Then** nenhum ciclo e encontrado
2. **Given** historia em onda N, **When** verifico suas dependencias, **Then** todas as dependencias estao em ondas <= N
3. **Given** dependencias criadas, **When** verifico distribuicao, **Then** aproximadamente 60% sao intra-onda e 40% sao inter-ondas

---

### User Story 3 - Limpar Dados Existentes (Priority: P2)

Como desenvolvedor, quero poder limpar dados existentes antes de popular novamente, para resetar o ambiente de teste quando necessario.

**Why this priority**: Util para reexecucao, mas nao essencial para o primeiro uso.

**Independent Test**: Pode ser testado executando seed com flag --clean em banco com dados.

**Acceptance Scenarios**:

1. **Given** banco com dados existentes, **When** executo `python scripts/seed_test_backlog.py --clean`, **Then** dados anteriores sao removidos e novos dados sao inseridos
2. **Given** banco com dados existentes, **When** executo script sem flag --clean, **Then** script falha com mensagem informativa sobre conflito

---

### User Story 4 - Especificar Banco de Dados Customizado (Priority: P2)

Como desenvolvedor, quero especificar um caminho de banco de dados alternativo, para gerar dados em arquivos de teste isolados.

**Why this priority**: Permite isolamento de testes sem afetar banco principal.

**Independent Test**: Pode ser testado executando com --db-path apontando para arquivo temporario.

**Acceptance Scenarios**:

1. **Given** caminho de banco customizado, **When** executo `python scripts/seed_test_backlog.py --db-path ./test.db`, **Then** dados sao inseridos no arquivo especificado
2. **Given** script executado sem --db-path, **When** verifico onde dados foram salvos, **Then** dados estao no banco padrao da aplicacao

---

### User Story 5 - Acompanhar Progresso da Geracao (Priority: P3)

Como desenvolvedor, quero ver o progresso da geracao de dados durante execucao, para saber que o script esta funcionando e acompanhar cada etapa.

**Why this priority**: Melhora experiencia do usuario mas nao afeta funcionalidade core.

**Independent Test**: Pode ser testado observando saida do terminal durante execucao.

**Acceptance Scenarios**:

1. **Given** script em execucao, **When** observo saida do terminal, **Then** vejo mensagens de progresso para cada etapa (desenvolvedores, features, historias, dependencias)
2. **Given** script finalizado com sucesso, **When** observo saida final, **Then** vejo resumo com contagens totais de entidades criadas

---

### User Story 6 - Garantir Reproducibilidade (Priority: P2)

Como desenvolvedor, quero que execucoes repetidas do script gerem exatamente os mesmos dados, para garantir reproducibilidade em testes.

**Why this priority**: Essencial para testes deterministicos e debugging.

**Independent Test**: Pode ser testado executando script duas vezes e comparando dados.

**Acceptance Scenarios**:

1. **Given** banco vazio, **When** executo script duas vezes em bancos diferentes, **Then** os dados gerados sao identicos (mesmos IDs, nomes, dependencias)
2. **Given** random seed fixo (42), **When** executo script, **Then** sequencia de geracao e deterministica

---

### Edge Cases

- O que acontece quando o banco de dados nao existe? O script cria o arquivo e inicializa o schema reutilizando o modulo de inicializacao existente da aplicacao.
- O que acontece quando o script e interrompido durante execucao? Transacao atomica faz rollback, banco permanece no estado anterior.
- O que acontece quando --db-path aponta para diretorio inexistente? Script falha com mensagem de erro clara.
- O que acontece quando banco tem FKs invalidas pre-existentes? Script com --clean remove todos os dados respeitando ordem de FKs.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE inserir exatamente 7 desenvolvedores com nomes predefinidos (Ana, Bruno, Carlos, Diana, Eduardo, Fernanda, Gabriel)
- **FR-002**: Sistema DEVE criar aproximadamente 30 features distribuidas em 7 ondas (4-5 features por onda), cada onda com dominio especifico (Auth, User, Products, etc.)
- **FR-003**: Sistema DEVE gerar entre 150 e 200 historias com story points variados (3, 5, 8, 13) distribuidos de forma realista
- **FR-004**: Sistema DEVE criar entre 80 e 120 dependencias entre historias, com aproximadamente 60% intra-onda e 40% inter-ondas
- **FR-005**: Sistema DEVE garantir ausencia de ciclos em todas as dependencias geradas, validando antes de cada insercao
- **FR-006**: Sistema DEVE garantir que dependencias inter-ondas sempre apontem para ondas anteriores (historia de onda N so depende de ondas < N)
- **FR-007**: Sistema DEVE permitir limpeza de dados existentes via flag --clean antes de popular
- **FR-008**: Sistema DEVE permitir especificacao de caminho de banco customizado via --db-path
- **FR-009**: Sistema DEVE exibir log de progresso durante execucao com contagens por etapa
- **FR-010**: Sistema DEVE usar random seed fixo (42) para garantir reproducibilidade
- **FR-011**: Sistema DEVE usar transacao atomica (BEGIN/COMMIT/ROLLBACK) para garantir consistencia
- **FR-012**: Sistema DEVE gerar IDs de historia no formato COMPONENTE-NNN (ex: AUTH-001, USER-042)
- **FR-013**: Sistema DEVE criar historias com status inicial BACKLOG e sem alocacao (developer_id = NULL, datas = NULL)
- **FR-014**: Sistema DEVE incluir cenarios criticos: cadeia longa de dependencias cruzando ondas, historias com multiplas dependencias, ondas com densidades variadas
- **FR-015**: Sistema DEVE reutilizar o modulo de inicializacao de schema existente da aplicacao quando o banco de dados nao existir

### Key Entities *(include if feature involves data)*

- **Developer**: Representa membro da equipe de desenvolvimento (id auto-increment, nome)
- **Feature**: Agrupa historias em dominio especifico, associada a uma onda (id auto-increment, nome unico, wave unica)
- **Story**: Unidade de trabalho do backlog (id formato COMPONENTE-NNN, componente, nome, story_points, prioridade, status, feature_id)
- **Story_Dependency**: Relacionamento entre historias indicando prerequisito (story_id, depends_on_id, ambos FK para Story)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Script popula banco de dados completo em menos de 5 segundos
- **SC-002**: 100% das dependencias geradas sao validas (sem ciclos, respeitando regras de onda)
- **SC-003**: Dados gerados permitem execucao bem-sucedida do motor de alocacao e calculo de cronograma
- **SC-004**: Execucoes repetidas geram dados identicos (100% reproducibilidade)
- **SC-005**: Desenvolvedor consegue gerar ambiente de teste completo com um unico comando
- **SC-006**: Todas as 7 ondas possuem features e historias associadas
- **SC-007**: Distribuicao de story points e realista (mix de 3, 5, 8, 13)

## Clarifications

### Session 2026-03-12

- Q: When the database file doesn't exist, how should the script initialize the schema? → A: Reuse existing schema init (call existing app module)
- Q: Should the seed script validate that the generated data works with the allocation engine, or only generate data? → A: Script generates data only; allocation/scheduling engines run separately

## Out of Scope

- Execucao ou validacao do motor de alocacao (EP-007) - deve ser executado separadamente apos seed
- Execucao ou validacao do calculo de cronograma (EP-006) - deve ser executado separadamente apos seed
- Testes de integracao automatizados com os motores - responsabilidade dos respectivos epics
- Geracao de dados de alocacao (developer_id, start_date, end_date preenchidos) - script gera apenas backlog nao alocado

## Assumptions

- O schema do banco de dados SQLite esta estavel e nao mudara durante desenvolvimento deste script
- 7 ondas sao suficientes para testar cenarios criticos de alocacao
- Os componentes listados (AUTH, USER, PROD, CART, PAY, REPORT, NOTIF, API) cobrem dominios tipicos de projetos
- O script sera executado em ambiente de desenvolvimento/teste, nao em producao
- O usuario que executa o script tem permissao de escrita no diretorio do banco
- O Python e dependencias do projeto ja estao instalados no ambiente

## Traceability Matrix

| Epic RF       | Spec FR              | Description                       |
|---------------|----------------------|-----------------------------------|
| RF-SEED-001   | FR-001               | Inserir 7 Desenvolvedores         |
| RF-SEED-002   | FR-002               | Inserir Features por Onda         |
| RF-SEED-003   | FR-003               | Gerar Historias com SP Variados   |
| RF-SEED-004   | FR-004 (60%)         | Criar Dependencias Intra-Onda     |
| RF-SEED-005   | FR-004 (40%), FR-006 | Criar Dependencias Inter-Ondas    |
| RF-SEED-006   | FR-005               | Validar Ausencia de Ciclos        |
| RF-SEED-007   | FR-007               | Limpar Dados Existentes           |
| RF-SEED-008   | FR-009               | Log de Progresso                  |
