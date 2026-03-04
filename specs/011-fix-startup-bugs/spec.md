# Feature Specification: Corrigir Bugs de Inicialização da Aplicação

**Feature Branch**: `011-fix-startup-bugs`
**Created**: 2026-03-04
**Status**: Draft
**Input**: User description: "Corrigir inicialização do banco de dados e conflitos de event loop asyncio/qasync na aplicação"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Inicialização Automática do Banco de Dados (Priority: P1)

Como usuário do Backlog Manager, ao abrir a aplicação pela primeira vez, o sistema deve criar automaticamente todas as tabelas necessárias no banco de dados para que eu possa começar a usar imediatamente sem erros.

**Why this priority**: Este é o bug mais crítico - a aplicação não funciona de forma alguma sem as tabelas do banco de dados. Bloqueia 100% das funcionalidades.

**Independent Test**: Pode ser testado deletando o arquivo de banco de dados e iniciando a aplicação. O sistema deve iniciar sem erros e estar pronto para uso.

**Acceptance Scenarios**:

1. **Given** o usuário não possui arquivo de banco de dados, **When** a aplicação é iniciada, **Then** todas as tabelas são criadas automaticamente e a aplicação exibe a tela principal sem erros
2. **Given** o usuário possui um banco de dados existente com todas as tabelas, **When** a aplicação é iniciada, **Then** a aplicação carrega normalmente sem recriar as tabelas
3. **Given** o usuário possui um banco de dados corrompido ou parcial, **When** a aplicação é iniciada, **Then** as tabelas faltantes são criadas (usando IF NOT EXISTS) e a aplicação inicia

---

### User Story 2 - Diálogos Funcionam Sem Travamentos (Priority: P1)

Como usuário do Backlog Manager, ao abrir e fechar diálogos (criar história, editar história, gerenciar desenvolvedores, etc.), a aplicação deve permanecer estável e responsiva.

**Why this priority**: Este bug causa crash da aplicação ao usar funcionalidades básicas do CRUD, tornando a aplicação inutilizável após qualquer interação com diálogos.

**Independent Test**: Pode ser testado abrindo qualquer diálogo, realizando uma operação e fechando. A aplicação deve continuar funcionando normalmente.

**Acceptance Scenarios**:

1. **Given** a aplicação está rodando, **When** o usuário abre o diálogo de nova história e salva, **Then** o diálogo fecha e a lista de histórias é atualizada sem erros
2. **Given** a aplicação está rodando, **When** o usuário abre o diálogo de desenvolvedores e fecha, **Then** a aplicação permanece responsiva
3. **Given** a aplicação está rodando, **When** o usuário executa a alocação automática, **Then** a alocação é executada e os resultados são exibidos sem crash
4. **Given** a aplicação está rodando, **When** o usuário abre múltiplos diálogos em sequência, **Then** cada operação completa corretamente sem conflitos

---

### User Story 3 - Encerramento Limpo da Aplicação (Priority: P2)

Como usuário do Backlog Manager, ao fechar a aplicação, o sistema deve encerrar corretamente sem deixar processos pendentes ou exibir erros.

**Why this priority**: Importante para experiência do usuário, mas não bloqueia o uso da aplicação durante a sessão.

**Independent Test**: Pode ser testado fechando a aplicação após realizar operações. Não devem aparecer erros no console ou logs.

**Acceptance Scenarios**:

1. **Given** a aplicação está rodando com operações pendentes, **When** o usuário fecha a janela, **Then** a aplicação encerra sem erros de "Task was destroyed but it is pending"
2. **Given** a aplicação está rodando, **When** o usuário fecha a janela, **Then** não há mensagens de erro no log sobre event loop

---

### Edge Cases

- O que acontece se o diretório do banco de dados não tiver permissões de escrita?
- O que acontece se o usuário fechar a aplicação durante uma operação de banco de dados?
- O que acontece se múltiplas instâncias da aplicação tentarem acessar o mesmo banco?
- O que acontece se uma operação assíncrona falhar durante um diálogo modal?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE inicializar o banco de dados (criar tabelas) automaticamente ao iniciar a aplicação
- **FR-002**: Sistema DEVE utilizar padrão "IF NOT EXISTS" para criação de tabelas, permitindo execução idempotente
- **FR-003**: Sistema DEVE agendar operações assíncronas para o próximo ciclo do event loop após diálogos modais
- **FR-004**: Sistema DEVE garantir que tasks assíncronas não sejam criadas enquanto outra task está em execução
- **FR-005**: Sistema DEVE permitir abertura e fechamento de diálogos sem causar conflitos de event loop
- **FR-006**: Sistema DEVE manter o event loop principal ativo enquanto a janela estiver visível
- **FR-007**: Sistema DEVE encerrar todas as tasks pendentes de forma limpa ao fechar a aplicação

### Key Entities

- **Database Schema**: Conjunto de tabelas (Story, Feature, Developer, Story_Dependency) que armazenam os dados da aplicação
- **Event Loop**: Loop de eventos asyncio integrado com Qt via qasync que gerencia operações assíncronas
- **Modal Dialog**: Janelas de diálogo que bloqueiam a interação com a janela principal durante sua exibição

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Aplicação inicia com sucesso em 100% das vezes, mesmo sem banco de dados pré-existente
- **SC-002**: Usuários conseguem criar, editar e deletar histórias sem encontrar erros de crash
- **SC-003**: Diálogos abrem e fecham sem gerar exceções de RuntimeError no event loop
- **SC-004**: Aplicação encerra sem mensagens de erro sobre tasks pendentes no log
- **SC-005**: Todos os testes automatizados existentes continuam passando após as correções
- **SC-006**: Alocação automática executa completamente sem interrupção

## Assumptions

- O schema do banco de dados já está definido corretamente em `schema.sql`
- A função `init_database()` já existe e funciona corretamente (confirmado pelos testes)
- O padrão de uso de `QTimer.singleShot(0, ...)` é compatível com PySide6 ^6.10.0 (verificado: método existe desde Qt 4.0, suportado em todas as versões PySide6)
- A aplicação é executada em ambiente single-user (sem acesso concorrente ao banco)

## Scope Boundaries

### In Scope
- Correção da inicialização do banco de dados na startup
- Correção dos conflitos de event loop em todos os diálogos
- Garantir encerramento limpo da aplicação

### Out of Scope
- Mudanças no schema do banco de dados
- Novas funcionalidades
- Otimizações de performance além das correções de bugs
- Tratamento de acesso concorrente ao banco de dados
