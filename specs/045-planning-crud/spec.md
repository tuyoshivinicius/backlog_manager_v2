# Feature Specification: Modulo de Planejamentos (CRUD Completo)

**Feature Branch**: `045-planning-crud`
**Created**: 2026-04-08
**Status**: Draft
**Input**: User description: "Crie um novo modulo chamado planejamentos, crie um crud inteiro de um planejamento, o sistema deve permitir eu manter uma lista de planejamentos salvos, cada planejamento tera um conjunto de historias, pra que eu possa compor varios visoes de planejamento e conseguir restaura-las a qualquer momento, algo como arquivo -> abrir -> planejamento. o planejamento nao eh um arquivo ele eh cadastrado no banco de dados sqlite, substitua a funcionalidade de novo planejamento atual por reiniciar planejamento pra nao conflitar com o novo modulo, no final da spec eu tenho que ser capaz de acessar a aplicacao, criar um novo planejamento cadastrar historias, abrir outro planejamento e cadastrar historias com outras estrategias, tal como restaurar um planejamento pra continuar, o planejamento deve ter um nome e um id, as historias devem relacionar o planejamento em que elas estao."

## Clarifications

### Session 2026-04-08

- Q: Estratégia de migração para histórias existentes sem planejamento? → A: Migração automática no startup da app (detecta schema antigo e migra, criando "Planejamento Inicial").
- Q: Onde ficam as operações de editar/excluir planejamentos? → A: Dentro do diálogo "Abrir Planejamento", com botões de ação por item na lista.
- Q: O story_id é digitado pelo usuário ou auto-gerado? → A: Digitado pelo usuário (código do ticket externo, ex: Jira/Azure DevOps).
- Q: Como tratar alterações pendentes ao trocar de planejamento? → A: Tudo já é auto-salvo — troca imediata sem prompt de confirmação.
- Q: Quais informações exibir por planejamento no diálogo "Abrir"? → A: Nome + quantidade de histórias + data de última modificação.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Criar um Novo Planejamento (Priority: P1)

O usuario acessa o menu "Arquivo > Novo Planejamento" e informa um nome para o planejamento. O sistema cria o planejamento no banco de dados e o define como planejamento ativo. A partir desse momento, todas as historias cadastradas serao associadas a esse planejamento. O titulo da janela principal exibe o nome do planejamento ativo.

**Why this priority**: Sem a capacidade de criar planejamentos, nenhuma outra funcionalidade do modulo funciona. Eh o ponto de entrada de todo o fluxo.

**Independent Test**: Pode ser testado criando um planejamento, verificando que ele aparece na lista de planejamentos e que o titulo da janela reflete o planejamento ativo.

**Acceptance Scenarios**:

1. **Given** o usuario esta na tela principal sem planejamento ativo, **When** acessa "Arquivo > Novo Planejamento" e informa o nome "Sprint 45", **Then** o planejamento "Sprint 45" eh criado no banco de dados, definido como ativo e o titulo da janela exibe "Sprint 45".
2. **Given** o usuario ja tem um planejamento ativo "Sprint 45", **When** cria um novo planejamento "Sprint 46", **Then** o planejamento "Sprint 46" se torna o ativo, as historias existentes permanecem associadas ao "Sprint 45" e a tabela de historias exibe apenas as historias do "Sprint 46" (inicialmente vazia).
3. **Given** o usuario tenta criar um planejamento sem nome, **When** confirma a criacao, **Then** o sistema exibe mensagem de erro informando que o nome eh obrigatorio.
4. **Given** o usuario tenta criar um planejamento com nome duplicado, **When** confirma a criacao, **Then** o sistema exibe mensagem de erro informando que ja existe um planejamento com esse nome.

---

### User Story 2 - Abrir/Restaurar um Planejamento Existente (Priority: P1)

O usuario acessa o menu "Arquivo > Abrir Planejamento" e visualiza um dialogo com a lista de todos os planejamentos salvos, exibindo para cada um: nome, quantidade de historias e data de ultima modificacao. O dialogo tambem disponibiliza botoes de acao por item para renomear e excluir planejamentos. Ao selecionar um planejamento e confirmar, o sistema o define como ativo e carrega todas as historias associadas a ele na tabela principal. A troca eh imediata pois todas as alteracoes ja sao auto-salvas.

**Why this priority**: A capacidade de alternar entre planejamentos eh o valor central da feature - permite manter multiplas visoes de planejamento e restaura-las a qualquer momento.

**Independent Test**: Pode ser testado criando dois planejamentos com historias diferentes, alternando entre eles e verificando que a tabela exibe as historias corretas de cada planejamento.

**Acceptance Scenarios**:

1. **Given** existem planejamentos "Sprint 45" e "Sprint 46" salvos, **When** o usuario acessa "Arquivo > Abrir Planejamento" e seleciona "Sprint 45", **Then** o sistema carrega as historias do "Sprint 45" na tabela, o titulo da janela atualiza para "Sprint 45".
2. **Given** o usuario esta trabalhando no "Sprint 46" com historias modificadas e salvas, **When** abre o "Sprint 45", **Then** as historias do "Sprint 45" sao exibidas integralmente com todas as suas alocacoes e cronogramas.
3. **Given** nenhum planejamento existe no sistema, **When** o usuario acessa "Arquivo > Abrir Planejamento", **Then** o sistema exibe uma lista vazia com mensagem informativa.

---

### User Story 3 - Associacao de Historias ao Planejamento Ativo (Priority: P1)

Ao cadastrar, importar ou duplicar historias, elas sao automaticamente associadas ao planejamento ativo. A tabela principal exibe apenas as historias do planejamento ativo. Operacoes de alocacao, agendamento e dependencias operam somente sobre as historias do planejamento ativo.

**Why this priority**: Eh o mecanismo fundamental que conecta historias a planejamentos, sem o qual a separacao entre planejamentos nao funciona.

**Independent Test**: Pode ser testado criando historias em planejamentos diferentes e verificando que cada planejamento so exibe suas proprias historias.

**Acceptance Scenarios**:

1. **Given** o planejamento "Sprint 45" esta ativo, **When** o usuario cadastra a historia "AUTH-001", **Then** a historia "AUTH-001" eh salva com referencia ao planejamento "Sprint 45".
2. **Given** o planejamento "Sprint 45" esta ativo e possui as historias "AUTH-001" e "AUTH-002", **When** o usuario troca para o planejamento "Sprint 46", **Then** a tabela nao exibe "AUTH-001" nem "AUTH-002".
3. **Given** o planejamento "Sprint 46" esta ativo, **When** o usuario importa historias via Excel, **Then** todas as historias importadas sao associadas ao "Sprint 46".

---

### User Story 4 - Editar Planejamento (Priority: P2)

O usuario pode renomear um planejamento existente atraves do dialogo "Abrir Planejamento", que exibe botoes de acao (editar/excluir) ao lado de cada item na lista. O sistema permite editar o nome de qualquer planejamento diretamente nesse dialogo.

**Why this priority**: Editar nomes eh uma necessidade secundaria que nao bloqueia o uso principal, mas melhora a organizacao.

**Independent Test**: Pode ser testado renomeando um planejamento e verificando que o novo nome aparece no titulo da janela e na lista de planejamentos.

**Acceptance Scenarios**:

1. **Given** o planejamento ativo eh "Sprint 45", **When** o usuario renomeia para "Sprint 45 - Revisado", **Then** o titulo da janela e a lista de planejamentos refletem o novo nome.
2. **Given** o usuario tenta renomear para um nome ja existente, **When** confirma a edicao, **Then** o sistema exibe mensagem de erro de nome duplicado.

---

### User Story 5 - Excluir Planejamento (Priority: P2)

O usuario pode excluir um planejamento que nao esteja ativo atraves do dialogo "Abrir Planejamento", usando o botao de exclusao ao lado do item. Ao excluir um planejamento, todas as historias associadas a ele tambem sao removidas. O sistema solicita confirmacao antes da exclusao, informando a quantidade de historias que serao perdidas.

**Why this priority**: Exclusao eh importante para manter a organizacao, mas nao bloqueia o uso principal.

**Independent Test**: Pode ser testado excluindo um planejamento com historias e verificando que tanto o planejamento quanto suas historias foram removidos do banco.

**Acceptance Scenarios**:

1. **Given** existem planejamentos "Sprint 45" (ativo) e "Sprint 44" (inativo, com 15 historias), **When** o usuario exclui "Sprint 44", **Then** o sistema solicita confirmacao mostrando que 15 historias serao removidas, e apos confirmacao remove o planejamento e suas historias.
2. **Given** o planejamento ativo eh "Sprint 45", **When** o usuario tenta excluir "Sprint 45", **Then** o sistema impede a exclusao informando que nao eh possivel excluir o planejamento ativo.
3. **Given** o planejamento "Sprint 44" nao possui historias, **When** o usuario exclui "Sprint 44", **Then** o sistema solicita confirmacao simples e remove o planejamento.

---

### User Story 6 - Renomear "Novo Planejamento" para "Reiniciar Planejamento" (Priority: P2)

A funcionalidade existente de "Novo Planejamento" no menu "Ferramentas" eh renomeada para "Reiniciar Planejamento". O comportamento permanece identico (limpa campos calculados das historias do planejamento ativo). A mudanca evita confusao com o novo "Arquivo > Novo Planejamento" que cria um planejamento.

**Why this priority**: Necessario para evitar confusao de nomenclatura com o novo modulo, mas nao bloqueia funcionalidades.

**Independent Test**: Pode ser testado verificando que o menu "Ferramentas" exibe "Reiniciar Planejamento" e que a funcionalidade de reset continua operando corretamente sobre as historias do planejamento ativo.

**Acceptance Scenarios**:

1. **Given** o menu "Ferramentas" esta visivel, **When** o usuario abre o menu, **Then** a opcao exibe "Reiniciar Planejamento" em vez de "Novo Planejamento".
2. **Given** o planejamento ativo "Sprint 45" possui historias com datas e alocacoes calculadas, **When** o usuario executa "Reiniciar Planejamento", **Then** os campos calculados (duration, start_date, end_date, developer_id) das historias do planejamento ativo sao limpos, mantendo os dados basicos das historias.

---

### User Story 7 - Comportamento Inicial sem Planejamento (Priority: P1)

Quando o usuario abre a aplicacao pela primeira vez (sem nenhum planejamento cadastrado), o sistema exige a criacao de um planejamento antes de permitir qualquer operacao com historias. Ao abrir a aplicacao com planejamentos existentes, o sistema carrega automaticamente o ultimo planejamento utilizado.

**Why this priority**: Define o comportamento de bootstrap da aplicacao - sem isso o usuario nao consegue comecar a usar o sistema.

**Independent Test**: Pode ser testado iniciando a aplicacao com banco vazio e verificando que o sistema solicita a criacao de um planejamento antes de habilitar outras funcionalidades.

**Acceptance Scenarios**:

1. **Given** o banco de dados nao possui nenhum planejamento, **When** o usuario inicia a aplicacao, **Then** o sistema apresenta automaticamente o dialogo de criacao de planejamento.
2. **Given** o usuario tinha o planejamento "Sprint 46" ativo na ultima sessao, **When** abre a aplicacao novamente, **Then** o "Sprint 46" eh carregado automaticamente com suas historias.
3. **Given** o ultimo planejamento utilizado foi excluido por outra via, **When** o usuario abre a aplicacao, **Then** o sistema apresenta o dialogo de criacao de planejamento.

---

### Edge Cases

- O que acontece quando o usuario tenta cadastrar uma historia sem planejamento ativo? O sistema impede a operacao e solicita a criacao ou selecao de um planejamento.
- O que acontece quando o usuario exclui todos os planejamentos? O sistema volta ao estado inicial e solicita a criacao de um novo planejamento.
- O que acontece com historias duplicadas entre planejamentos? Cada planejamento tem suas proprias historias independentes - IDs de historias podem se repetir entre planejamentos diferentes.
- O que acontece com a funcionalidade de "Reiniciar Planejamento" se nao ha planejamento ativo? A opcao fica desabilitada no menu.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir criar planejamentos com nome unico e identificador automatico.
- **FR-002**: O sistema DEVE permitir listar todos os planejamentos salvos com seus nomes e quantidade de historias associadas.
- **FR-003**: O sistema DEVE permitir selecionar e ativar um planejamento da lista, carregando suas historias na tabela principal.
- **FR-004**: O sistema DEVE permitir renomear planejamentos existentes, validando unicidade do nome.
- **FR-005**: O sistema DEVE permitir excluir planejamentos inativos, com confirmacao e remocao em cascata das historias associadas.
- **FR-006**: O sistema DEVE impedir a exclusao do planejamento ativo.
- **FR-007**: O sistema DEVE associar automaticamente toda historia criada, importada ou duplicada ao planejamento ativo.
- **FR-008**: O sistema DEVE exibir na tabela principal somente as historias do planejamento ativo.
- **FR-009**: O sistema DEVE persistir o identificador do ultimo planejamento ativo para restauracao automatica ao reabrir a aplicacao.
- **FR-010**: O sistema DEVE exibir o nome do planejamento ativo no titulo da janela principal.
- **FR-011**: O sistema DEVE renomear a opcao "Novo Planejamento" no menu "Ferramentas" para "Reiniciar Planejamento", mantendo o comportamento existente de limpar campos calculados.
- **FR-012**: O sistema DEVE restringir as operacoes de alocacao, agendamento, reinicio de planejamento e gerenciamento de dependencias ao escopo do planejamento ativo.
- **FR-013**: O sistema DEVE solicitar a criacao de um planejamento ao iniciar pela primeira vez com banco vazio.
- **FR-014**: O sistema DEVE permitir que IDs de historias (digitados pelo usuario, ex: codigos de tickets externos como Jira/Azure DevOps) se repitam entre planejamentos diferentes, garantindo unicidade apenas dentro de cada planejamento.
- **FR-015**: O sistema DEVE executar migracao automatica no startup quando detectar historias sem planejamento associado, criando um "Planejamento Inicial" e vinculando todas as historias orfas a ele.
- **FR-016**: O dialogo "Abrir Planejamento" DEVE exibir para cada planejamento: nome, quantidade de historias e data de ultima modificacao, alem de botoes de acao para renomear e excluir.
- **FR-017**: A troca de planejamento ativo DEVE ser imediata, sem prompt de confirmacao, pois todas as alteracoes sao persistidas automaticamente (auto-save).

### Key Entities

- **Planejamento (Planning)**: Representa um conjunto nomeado de historias que compoem uma visao de planejamento. Atributos: identificador unico (auto-incremento), nome (unico, obrigatorio), data de criacao (auto), data de ultima modificacao (auto, atualizada ao modificar planejamento ou suas historias). Relacionamento: um planejamento contem zero ou mais historias.
- **Historia (Story)** (entidade existente, modificada): Passa a ter uma referencia obrigatoria ao planejamento ao qual pertence. O story_id eh digitado pelo usuario (codigo de ticket externo). A unicidade do ID da historia eh validada dentro do escopo do planejamento (constraint composta: planning_id + story_id).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuario consegue criar um novo planejamento, cadastrar historias e alternar para outro planejamento em menos de 1 minuto.
- **SC-002**: Ao restaurar um planejamento salvo, 100% das historias e seus dados (alocacoes, cronogramas, dependencias) sao exibidos corretamente.
- **SC-003**: O usuario consegue manter e alternar entre pelo menos 50 planejamentos sem degradacao perceptivel de desempenho.
- **SC-004**: A transicao entre planejamentos (abrir planejamento) ocorre de forma instantanea para o usuario (sem tela de carregamento visivel para ate 500 historias por planejamento).
- **SC-005**: 100% das operacoes de criacao, edicao e exclusao de planejamentos sao persistidas corretamente no banco de dados.
- **SC-006**: A funcionalidade de "Reiniciar Planejamento" continua operando corretamente, afetando apenas as historias do planejamento ativo.

## Assumptions

- O identificador do planejamento sera um inteiro auto-incremento gerenciado pelo banco de dados.
- O nome do planejamento sera limitado a 200 caracteres.
- A persistencia do ultimo planejamento ativo sera feita via QSettings (INI format), consistente com o padrao do projeto.
- A migracao de dados existentes sera executada automaticamente no startup da aplicacao: ao detectar historias sem planning_id, o sistema cria o planejamento padrao ("Planejamento Inicial") e associa todas as historias orfas a ele, garantindo retrocompatibilidade.
- A constraint de unicidade do ID da historia sera alterada de global para composta (planning_id + story_id), permitindo que o mesmo ID de historia exista em planejamentos diferentes.
- Todas as alteracoes em historias e planejamentos sao persistidas imediatamente (auto-save), nao havendo necessidade de acao explicita de "salvar" antes de trocar de planejamento.
- A entidade Planejamento incluira campos created_at e updated_at para suportar a exibicao de data de ultima modificacao no dialogo "Abrir Planejamento".
