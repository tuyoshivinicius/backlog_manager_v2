# Feature Specification: Novo Planejamento (Reset de Cronograma e Alocacao)

**Feature Branch**: `023-reset-planning`
**Created**: 2026-03-30
**Status**: Draft
**Input**: User description: "EP-023 — Novo Planejamento (Reset de Cronograma e Alocacao)"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Resetar Planejamento Completo (Priority: P1)

O usuario deseja recomecar o planejamento do zero. Ele clica no botao "Novo Planejamento" no menu Ferramentas ou na Toolbar. O sistema exibe um dialog de confirmacao mostrando quantas historias serao afetadas. Ao confirmar, o sistema limpa todos os dados calculados (duration, start_date, end_date, developer_id) de todas as historias que possuem esses campos preenchidos, independente do status da historia. Apos o reset, a tabela e a status bar sao atualizados para refletir o novo estado.

**Why this priority**: Esta e a funcionalidade principal do epico. Sem ela, o usuario precisa editar cada historia manualmente para recomecar o planejamento, o que e impraticavel para backlogs grandes.

**Independent Test**: Pode ser testado criando historias com dados de planejamento preenchidos, executando o reset e verificando que os campos calculados foram limpos enquanto os dados do usuario foram preservados.

**Acceptance Scenarios**:

1. **Given** um backlog com 10 historias, 7 com dados de planejamento (duration, start_date, end_date, developer_id preenchidos), **When** o usuario clica em "Novo Planejamento" e confirma no dialog, **Then** as 7 historias tem seus campos calculados limpos (duration=None, start_date=None, end_date=None, developer_id=None), as 3 historias sem dados de planejamento permanecem inalteradas, e os dados do usuario (id, component, name, story_points, priority, status, feature_id) de todas as 10 historias permanecem intactos.

2. **Given** um backlog com historias em diferentes status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO) todas com datas calculadas, **When** o usuario executa o reset, **Then** os campos calculados de TODAS as historias sao limpos independente do status, e o campo status de cada historia permanece inalterado.

3. **Given** um backlog com historias que possuem dependencias entre si, **When** o usuario executa o reset, **Then** as dependencias entre historias NAO sao alteradas — apenas os campos calculados sao limpos.

---

### User Story 2 - Confirmacao com Preview antes do Reset (Priority: P2)

Antes de executar o reset, o sistema exibe um dialog de confirmacao que mostra ao usuario exatamente o que sera afetado. O dialog informa quantas historias terao datas removidas e quantas terao desenvolvedores desalocados, permitindo que o usuario tome uma decisao informada.

**Why this priority**: O reset e uma operacao destrutiva e irreversivel. O usuario precisa de informacao clara antes de confirmar para evitar perda acidental de dados de planejamento.

**Independent Test**: Pode ser testado verificando que o dialog exibe a contagem correta de historias afetadas e que o cancelamento nao modifica nenhum dado.

**Acceptance Scenarios**:

1. **Given** um backlog com 15 historias, 10 com datas calculadas e 8 com developer_id, **When** o usuario clica em "Novo Planejamento", **Then** o dialog exibe "10 historias terao datas e duracoes removidas" e "8 historias terao desenvolvedores desalocados", com botoes [Confirmar] e [Cancelar].

2. **Given** o dialog de confirmacao exibido, **When** o usuario clica em [Cancelar], **Then** o dialog fecha e nenhum dado e alterado.

3. **Given** o dialog de confirmacao exibido, **When** o usuario pressiona Escape, **Then** o dialog fecha sem executar o reset.

---

### User Story 3 - Feedback Visual apos Reset (Priority: P3)

Apos a execucao do reset, o sistema atualiza a interface para refletir o novo estado: a tabela de historias e recarregada mostrando os campos calculados vazios, a status bar e atualizada removendo a informacao de ultima alocacao, e uma mensagem temporaria confirma o sucesso da operacao.

**Why this priority**: Feedback visual claro e essencial para que o usuario tenha confianca de que a operacao foi concluida com sucesso e saiba o estado atual do sistema.

**Independent Test**: Pode ser testado executando o reset e verificando que a tabela, status bar e mensagem temporaria refletem corretamente o novo estado.

**Acceptance Scenarios**:

1. **Given** o reset executado com sucesso em 7 historias, **When** a operacao completa, **Then** a tabela e recarregada com campos calculados vazios, a status bar mostra "Planejamento resetado: 7 historias" por 5 segundos, e a informacao de "Ultima alocacao" e removida.

2. **Given** o reset executado com sucesso, **When** a tabela e atualizada, **Then** as colunas de duracao, data inicio, data fim e desenvolvedor mostram valores vazios para as historias resetadas.

---

### User Story 4 - Botao Desabilitado em Condicoes Invalidas (Priority: P3)

O botao "Novo Planejamento" e desabilitado automaticamente quando nao ha historias carregadas, quando uma operacao esta em andamento (cronograma ou alocacao), ou quando nenhuma historia possui dados de planejamento para resetar.

**Why this priority**: Previne que o usuario tente executar o reset em situacoes onde nao ha sentido ou onde poderia causar conflitos com operacoes em andamento.

**Independent Test**: Pode ser testado verificando o estado do botao em diferentes cenarios (backlog vazio, operacao em andamento, sem dados de planejamento).

**Acceptance Scenarios**:

1. **Given** um backlog sem nenhuma historia, **When** a tela principal carrega, **Then** o botao "Novo Planejamento" esta desabilitado.

2. **Given** o calculo de cronograma em andamento, **When** o usuario observa o botao "Novo Planejamento", **Then** o botao esta desabilitado ate a operacao concluir.

3. **Given** um backlog com 5 historias, mas nenhuma com dados de planejamento (todos os campos calculados sao None), **When** o usuario observa o botao, **Then** o botao esta desabilitado.

4. **Given** o botao desabilitado porque nao ha dados de planejamento, **When** o usuario executa o calculo de cronograma com sucesso, **Then** o botao "Novo Planejamento" passa a estar habilitado.

---

### Edge Cases

- O que acontece quando o backlog tem 0 historias? O botao permanece desabilitado e o reset nao e executavel.
- O que acontece se uma falha ocorre no meio do reset (ex: erro de disco)? A operacao e atomica via transacao — nenhuma historia e resetada e o usuario ve uma mensagem de erro clara.
- O que acontece se o usuario executa "Novo Planejamento" duas vezes consecutivas? A segunda execucao mostra o dialog com 0 historias afetadas (nenhuma tem dados de planejamento) e o botao esta desabilitado, impedindo execucao desnecessaria.
- O que acontece com historias que tem apenas developer_id preenchido (sem datas)? Sao incluidas no reset — qualquer historia com pelo menos um campo calculado preenchido e afetada.
- O que acontece com historias que tem apenas duracao e datas mas nao developer_id? Sao incluidas no reset — todos os campos calculados sao limpos.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE fornecer uma acao "Novo Planejamento" acessivel pelo menu Ferramentas e pela Toolbar, com atalho de teclado Ctrl+Shift+N.
- **FR-002**: O sistema DEVE exibir um dialog de confirmacao antes de executar o reset, mostrando a contagem de historias que serao afetadas.
- **FR-003**: O dialog de confirmacao DEVE informar separadamente quantas historias terao datas/duracoes removidas e quantas terao desenvolvedores desalocados.
- **FR-004**: O sistema DEVE limpar os campos calculados (duration, start_date, end_date, developer_id) de todas as historias que possuem pelo menos um desses campos preenchido, independente do status da historia.
- **FR-005**: O sistema NAO DEVE alterar dados do usuario: id, component, name, story_points, priority, status, feature_id.
- **FR-006**: O sistema NAO DEVE alterar dependencias entre historias.
- **FR-007**: O sistema NAO DEVE alterar o campo status das historias — se uma historia estava em EXECUCAO, permanece em EXECUCAO apos o reset.
- **FR-008**: A operacao de reset DEVE ser atomica — todas as historias sao resetadas ou nenhuma e, em caso de falha.
- **FR-009**: Apos o reset, o sistema DEVE atualizar a tabela de historias e a status bar para refletir o novo estado.
- **FR-010**: Apos o reset, o sistema DEVE exibir uma mensagem temporaria na status bar com a contagem de historias resetadas (visivel por 5 segundos).
- **FR-011**: Apos o reset, o sistema DEVE limpar a informacao de "Ultima alocacao" da status bar.
- **FR-012**: O botao "Novo Planejamento" DEVE ser desabilitado quando: (a) nao ha historias carregadas, (b) uma operacao esta em andamento, (c) nenhuma historia possui dados de planejamento.
- **FR-013**: Em caso de erro na operacao de reset, o sistema DEVE exibir uma mensagem de erro clara sem encerrar a aplicacao.
- **FR-014**: O botao "Novo Planejamento" DEVE ter um icone visual consistente com o design system da aplicacao.
- **FR-015**: O botao "Novo Planejamento" DEVE estar posicionado no menu Ferramentas antes de "Calcular Cronograma" e na Toolbar no grupo 4 antes do botao "Cronograma".
- **FR-016**: O dialog de confirmacao DEVE ter o botao [Cancelar] como opcao padrao (foco inicial), e o botao [Confirmar] com estilo destrutivo (cor de erro).
- **FR-017**: O sistema DEVE contar as historias afetadas antes de exibir o dialog, sem modificar nenhum dado nessa etapa.

### Key Entities

- **Story (campos calculados)**: Os campos duration (duracao em dias uteis), start_date (data de inicio), end_date (data de fim) e developer_id (desenvolvedor alocado) sao os dados de planejamento que serao limpos pelo reset. Esses campos sao calculados pelas operacoes de cronograma e alocacao e nao representam dados inseridos pelo usuario.
- **Story (dados do usuario)**: Os campos id, component, name, story_points, priority, status e feature_id sao dados inseridos e gerenciados pelo usuario e NUNCA devem ser afetados pelo reset.
- **Dependencias entre stories**: Relacoes de dependencia entre historias sao dados estruturais do backlog e NAO devem ser afetadas pelo reset.

## Architectural Decisions

### ADR-001: Escopo do Reset — Apenas Campos Calculados

**Contexto**: O reset precisa definir quais dados sao limpos. Os campos calculados (duration, start_date, end_date, developer_id) sao gerados pelo cronograma e alocacao. O campo status e gerenciado pelo usuario e pode indicar trabalho real ja iniciado.

**Opcoes**:
- (a) Resetar apenas campos calculados (duration, start_date, end_date, developer_id)
- (b) Resetar campos calculados + status para BACKLOG
- (c) Oferecer checkbox "Resetar status para Backlog" ao usuario
- (d) Ignorar stories com status CONCLUIDO

**Decisao**: Opcao (a) — Resetar APENAS campos calculados.

**Justificativa**: O campo status representa progresso real do trabalho (EXECUCAO, TESTES, CONCLUIDO) e nao deve ser alterado por uma operacao de replanejamento. O usuario pode querer replanejar mantendo o progresso registrado. Limpar o status seria uma perda de informacao sobre o trabalho ja realizado. A opcao (c) adicionaria complexidade desnecessaria para um caso de uso raro.

### ADR-002: Atomicidade via Unit of Work

**Contexto**: O reset modifica multiplas stories. Uma falha parcial deixaria o backlog em estado inconsistente.

**Opcoes**:
- (a) Usar transacao atomica via Unit of Work (todas ou nenhuma)
- (b) Reset individual com log de falhas parciais
- (c) Reset com mecanismo de undo

**Decisao**: Opcao (a) — Transacao atomica via Unit of Work.

**Justificativa**: O padrao Unit of Work ja existente na aplicacao garante atomicidade naturalmente. Todas as operacoes de update acontecem dentro de uma unica transacao. Se qualquer update falhar, o UoW faz rollback automatico. Nao e necessario implementar mecanismos adicionais.

### ADR-003: Confirmacao Obrigatoria com Preview

**Contexto**: O reset e uma operacao destrutiva e irreversivel (perde dados calculados que podem levar tempo para recalcular).

**Opcoes**:
- (a) Executar sem confirmacao
- (b) Dialog simples "Tem certeza?"
- (c) Dialog com preview mostrando contagem de historias afetadas

**Decisao**: Opcao (c) — Dialog com preview detalhado.

**Justificativa**: A operacao e irreversivel. O usuario precisa saber exatamente o impacto antes de confirmar. O custo de implementacao e baixo (uma consulta para contar stories afetadas) e o beneficio para a experiencia do usuario e alto. O padrao ja existe na aplicacao (ConfirmDeleteDialog).

### ADR-004: Posicao na UI — Menu e Toolbar

**Contexto**: O botao precisa de posicao logica na interface, consistente com as acoes de cronograma e alocacao.

**Opcoes**:
- (a) Apenas no menu Ferramentas
- (b) Menu Ferramentas + Toolbar
- (c) Menu Ferramentas + Toolbar + Atalho

**Decisao**: Opcao (c) — Menu Ferramentas + Toolbar + Atalho (Ctrl+Shift+N).

**Justificativa**: Consistencia com as acoes de cronograma (Ctrl+Shift+C) e alocacao (Ctrl+Shift+A) que ja possuem as tres formas de acesso. O "N" de "Novo" e intuitivo e nao conflita com atalhos existentes. Posicao antes de Cronograma/Alocar no menu e toolbar porque e logicamente a primeira etapa do fluxo (resetar -> calcular -> alocar).

### ADR-005: Status Bar e Estado apos Reset

**Contexto**: A status bar mostra "Ultima alocacao: {datetime}" e SP breakdown. Apos o reset, essa informacao fica obsoleta.

**Opcoes**:
- (a) Manter informacao de ultima alocacao
- (b) Limpar informacao de ultima alocacao
- (c) Limpar e mostrar mensagem de reset

**Decisao**: Opcao (c) — Limpar informacao de ultima alocacao e mostrar mensagem temporaria.

**Justificativa**: A informacao de ultima alocacao perde relevancia apos o reset (as alocacoes foram removidas). A mensagem temporaria ("Planejamento resetado: X historias") da feedback imediato ao usuario. Apos 5 segundos, a status bar retorna ao estado normal com SP breakdown atualizado.

### ADR-006: Stories Afetadas — Todas com Dados de Planejamento

**Contexto**: O reset precisa definir quais stories sao elegivas. Stories podem ter diferentes status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO) e diferentes combinacoes de campos calculados preenchidos.

**Opcoes**:
- (a) Resetar apenas stories com status BACKLOG
- (b) Resetar TODAS as stories com dados de planejamento, independente do status
- (c) Oferecer opcao ao usuario (checkbox por status)

**Decisao**: Opcao (b) — Resetar TODAS as stories com pelo menos um campo calculado preenchido, independente do status.

**Justificativa**: O objetivo do "Novo Planejamento" e limpar o planejamento anterior para recomecar. Se stories em EXECUCAO mantivessem suas datas, o novo planejamento seria inconsistente. O campo status e preservado (ADR-001), entao o progresso real nao e perdido. O usuario pode ver quais stories estavam em andamento pelo status e tomar decisoes informadas no novo planejamento.

### ADR-007: Relacao com Operacoes em Andamento

**Contexto**: Se o cronograma ou alocacao estiver em execucao, executar o reset simultaneamente causaria inconsistencia.

**Opcoes**:
- (a) Permitir reset durante operacoes (conflito possivel)
- (b) Desabilitar botao durante operacoes em andamento

**Decisao**: Opcao (b) — Desabilitar botao durante operacoes em andamento.

**Justificativa**: O sistema ja rastreia operacoes em andamento via is_running nos ViewModels. O botao e desabilitado quando loading==True, impedindo conflitos. Padrao consistente com a forma como outros botoes ja sao gerenciados na aplicacao.

### ADR-008: Icone do Botao

**Contexto**: O botao precisa de um icone visual. A aplicacao possui icones SVG em assets/icons/.

**Opcoes**:
- (a) Reusar arrows-down-up.svg (icone de reordenamento)
- (b) Reusar list.svg (icone de lista)
- (c) Criar novo icone (ex: refresh/reset)

**Decisao**: Opcao (a) — Usar arrows-down-up.svg como icone do botao "Novo Planejamento".

**Justificativa**: O icone de setas para cima/baixo sugere visualmente "recomecar/reordenar", que e semanticamente proximo de "novo planejamento". Evita a necessidade de criar um novo icone SVG. O tooltip e o texto do menu compensam qualquer ambiguidade visual.

## Traceability Matrix

| Componente | Requisitos SRS | Requisitos Funcionais | Criterios de Aceite |
|------------|----------------|----------------------|---------------------|
| NP-001 Botao "Novo Planejamento" | RNF-PERF-002 (responsividade UI) | FR-001, FR-012, FR-014, FR-015 | US-4 AS-1/2/3/4 |
| NP-002 Dialog de Confirmacao | RNF-CONF-002 (confirmacao) | FR-002, FR-003, FR-016, FR-017 | US-2 AS-1/2/3 |
| NP-003 ResetPlanningViewModel | RNF-PERF-002 (responsividade) | FR-009, FR-010, FR-011, FR-012 | US-3 AS-1/2 |
| NP-004 ResetPlanningUseCase | RF-SCHED-001..006, RF-ALOC-001, RNF-CONF-002 | FR-004, FR-005, FR-006, FR-007, FR-008, FR-013 | US-1 AS-1/2/3 |
| NP-005 ResetPlanningInputDTO/OutputDTO | — | FR-004, FR-008 | US-1 AS-1 |
| NP-006 CountAffectedStoriesUseCase | — | FR-017, FR-003 | US-2 AS-1 |
| NP-007 Integracao MainWindow | RNF-PERF-002, RNF-CONF-002 | FR-001, FR-009, FR-015 | US-1/3 AS-1 |
| NP-008 Integracao DIContainer | — | FR-001 | US-1 AS-1 |
| NP-009 Atualizacao Status Bar | RNF-PERF-002 | FR-009, FR-010, FR-011 | US-3 AS-1/2 |

## Component Specifications

### NP-001: Botao "Novo Planejamento"

- QAction com texto "Novo Planejamento" no menu Ferramentas, posicionado antes de "Calcular Cronograma"
- Botao na Toolbar grupo 4, posicionado antes do botao "Cronograma"
- Icone: arrows-down-up.svg
- Tooltip: "Limpar dados de planejamento e recomecar do zero (Ctrl+Shift+N)"
- Atalho: Ctrl+Shift+N
- Desabilitado quando: sem historias, operacao em andamento, ou sem dados de planejamento

### NP-002: Dialog de Confirmacao (ConfirmResetDialog)

- QDialog modal seguindo padrao visual do ConfirmDeleteDialog existente
- Icone de aviso (warning-triangle.svg)
- Titulo: "Novo Planejamento"
- Mensagem principal: "Deseja limpar todos os dados de planejamento?"
- Detalhes: "{N} historias terao datas e duracoes removidas" e "{M} historias terao desenvolvedores desalocados"
- Aviso: "Esta acao nao pode ser desfeita."
- Botao [Cancelar] com foco inicial (opcao padrao)
- Botao [Confirmar] com estilo destrutivo (cor de erro do design system)

### NP-003: ResetPlanningViewModel

- Signals: reset_started, reset_completed(object), reset_error(str)
- Propriedade: is_running (bool)
- Metodo preview(): retorna contagem de stories afetadas (stories com datas, stories com developer) sem modificar dados
- Metodo execute(): executa o reset atomico, emite signals de progresso
- Padrao async identico ao ScheduleViewModel/AllocationViewModel

### NP-004: ResetPlanningUseCase

- Recebe UnitOfWork via construtor
- Busca todas as stories via repository
- Filtra stories com pelo menos um campo calculado preenchido (duration, start_date, end_date, developer_id)
- Para cada story elegivel: limpa duration, start_date, end_date, developer_id (set para None)
- Persiste todas as alteracoes via repository.update() dentro da mesma transacao
- Retorna ResetPlanningOutputDTO com contagem e avisos
- NAO altera: id, component, name, story_points, priority, status, feature_id, dependencias

### NP-005: DTOs

- ResetPlanningInputDTO: (sem campos obrigatorios — o reset afeta todas as stories com dados de planejamento)
- ResetPlanningOutputDTO: stories_reset (int), stories_with_dates_cleared (int), stories_with_developer_cleared (int), warnings (list[str])

### NP-006: CountAffectedStoriesUseCase

- Recebe UnitOfWork via construtor
- Busca todas as stories via repository
- Conta: (a) stories com pelo menos um campo calculado preenchido (total afetadas), (b) stories com duration/start_date/end_date preenchidos, (c) stories com developer_id preenchido
- Retorna CountAffectedStoriesOutputDTO com as tres contagens
- NAO modifica nenhum dado

### NP-007: Integracao MainWindow

- Adicionar QAction _new_planning_action no menu Ferramentas (antes de "Calcular Cronograma")
- Adicionar botao na Toolbar grupo 4 (antes do botao "Cronograma")
- Handler _on_new_planning() seguindo padrao async existente (QTimer.singleShot + asyncio.create_task)
- Conectar signals do ResetPlanningViewModel para atualizar UI
- Gerenciar estado enabled/disabled do botao baseado em: has_stories, is_loading, has_planning_data

### NP-008: Integracao DIContainer

- Factory method: create_reset_planning_use_case(uow) -> ResetPlanningUseCase
- Factory method: create_count_affected_stories_use_case(uow) -> CountAffectedStoriesUseCase
- Propriedade lazy: reset_planning_viewmodel -> ResetPlanningViewModel

### NP-009: Atualizacao Status Bar

- Apos reset: chamar load_stories() para atualizar tabela
- Resetar _last_allocation_time para None
- Atualizar SP breakdown via _update_sp_breakdown()
- Exibir mensagem temporaria: "Planejamento resetado: {N} historias" por 5 segundos
- Emitir signal stories_changed

## Test Specifications

- **test_reset_planning_clears_calculated_fields**: Verifica que duration, start_date, end_date, developer_id sao None apos reset
- **test_reset_planning_preserves_user_data**: Verifica que id, component, name, story_points, priority, feature_id NAO sao alterados
- **test_reset_planning_preserves_dependencies**: Verifica que dependencias entre stories NAO sao alteradas
- **test_reset_planning_preserves_status**: Verifica que o campo status NAO e alterado (EXECUCAO permanece EXECUCAO)
- **test_reset_planning_atomic_on_failure**: Verifica rollback se update falhar no meio da operacao
- **test_reset_planning_empty_backlog**: Verifica comportamento com 0 stories (retorna 0, sem erro)
- **test_reset_planning_no_planning_data**: Verifica comportamento quando nenhuma story tem dados calculados (retorna 0, sem erro)
- **test_reset_planning_partial_data**: Verifica que stories com apenas developer_id (sem datas) ou apenas datas (sem developer) sao incluidas no reset
- **test_count_affected_stories**: Verifica contagem correta de stories com dados de planejamento (total, com datas, com developer)
- **test_reset_planning_viewmodel_signals**: Verifica emissao de reset_started e reset_completed signals
- **test_reset_planning_viewmodel_error_signal**: Verifica emissao de reset_error signal em caso de falha
- **test_confirm_dialog_shows_count**: Verifica que dialog exibe contagem correta de historias afetadas
- **test_confirm_dialog_cancel_default**: Verifica que botao Cancelar tem foco inicial
- **test_button_disabled_during_operation**: Verifica desabilitacao do botao durante loading
- **test_button_disabled_no_planning_data**: Verifica desabilitacao quando nenhuma story tem dados de planejamento
- **test_button_enabled_after_schedule**: Verifica que botao habilita apos calculo de cronograma bem-sucedido
- **test_status_bar_updated_after_reset**: Verifica que status bar mostra mensagem temporaria e limpa ultima alocacao

## Assumptions

- A operacao de reset para backlogs tipicos (< 500 historias) completa em menos de 500ms, nao necessitando de ProgressDialog com barra de progresso. O feedback visual via signals (started/completed) e suficiente.
- O icone arrows-down-up.svg (a ser criado conforme Phosphor Icons style) e visualmente adequado para representar "Novo Planejamento". Caso o time de design considere inadequado, um novo icone SVG pode ser adicionado posteriormente sem impacto na funcionalidade.
- O atalho Ctrl+Shift+N nao conflita com nenhum atalho existente na aplicacao ou no sistema operacional Windows para esta aplicacao.
- A operacao de reset nao necessita de mecanismo de undo/redo. O usuario pode recalcular o cronograma e a alocacao apos o reset para restaurar os dados.
- O dialog de confirmacao segue o padrao visual do ConfirmDeleteDialog ja existente, adaptado para o contexto de reset de planejamento.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuario consegue resetar o planejamento completo em ate 3 cliques (botao -> dialog -> confirmar) e menos de 2 segundos de tempo total de interacao.
- **SC-002**: A operacao de reset completa sem erros para backlogs de ate 500 historias, com tempo de processamento imperceptivel para o usuario.
- **SC-003**: 100% dos dados do usuario (id, component, name, story_points, priority, status, feature_id, dependencias) permanecem inalterados apos o reset.
- **SC-004**: Apos o reset, o usuario pode imediatamente recalcular cronograma e alocar desenvolvedores sem necessidade de intervencao manual adicional.
- **SC-005**: Em caso de falha, 0 historias sao parcialmente resetadas (atomicidade garantida) e o usuario recebe mensagem de erro clara.
- **SC-006**: Todos os testes existentes da aplicacao continuam passando sem regressao apos a implementacao do EP-023.
