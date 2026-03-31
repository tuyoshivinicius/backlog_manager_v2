# Feature Specification: Alocacao Manual de Desenvolvedores

**Feature Branch**: `028-manual-allocation`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Alocar desenvolvedores manualmente selecionando inline na tabela de backlog via dialog de selecao com visibilidade de disponibilidade, recomendacao automatica e flexibilidade de data de inicio."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Abrir Dialog de Alocacao Manual (Priority: P1)

O usuario visualiza a tabela de backlog e deseja alocar manualmente um desenvolvedor a uma historia. Ao fazer double-click na celula da coluna "Desenvolvedor" de uma historia, uma dialog e aberta exibindo a lista de todos os desenvolvedores, classificados entre livres e ocupados, com uma recomendacao visual do desenvolvedor mais adequado segundo os criterios da alocacao automatica.

**Why this priority**: Este e o fluxo principal da funcionalidade. Sem a dialog de alocacao, nenhuma outra historia de usuario funciona. Entrega valor imediato ao permitir visibilidade completa sobre a disponibilidade da equipe.

**Independent Test**: Pode ser testado clicando na celula "Desenvolvedor" de qualquer historia na tabela e verificando que a dialog abre com a lista correta de desenvolvedores, seus estados e a recomendacao.

**Acceptance Scenarios**:

1. **Given** uma historia sem desenvolvedor alocado na tabela, **When** o usuario faz double-click na celula "Desenvolvedor", **Then** uma dialog e aberta exibindo todos os desenvolvedores separados em "Livres" e "Ocupados".
2. **Given** a dialog de alocacao aberta, **When** existem desenvolvedores ocupados, **Then** cada desenvolvedor ocupado exibe a lista de historias que o mantem ocupado (nome, datas de inicio/fim).
3. **Given** a dialog de alocacao aberta, **When** o algoritmo de alocacao automatica identifica um desenvolvedor recomendado, **Then** esse desenvolvedor e destacado visualmente como "Recomendado".
4. **Given** uma historia que ja possui desenvolvedor alocado, **When** o usuario faz double-click na celula "Desenvolvedor", **Then** a dialog abre com o desenvolvedor atual pre-selecionado, permitindo troca.

---

### User Story 2 - Selecionar Desenvolvedor e Confirmar Alocacao (Priority: P1)

O usuario visualiza a lista de desenvolvedores na dialog e seleciona um desenvolvedor livre para alocar a historia. A selecao e confirmada e a tabela de backlog e atualizada com o desenvolvedor escolhido.

**Why this priority**: Complementa a US1 — e o ato de alocar em si. Sem confirmar a selecao, a dialog nao tem efeito pratico.

**Independent Test**: Pode ser testado selecionando um desenvolvedor livre na dialog, confirmando, e verificando que a tabela reflete a alocacao.

**Acceptance Scenarios**:

1. **Given** a dialog de alocacao aberta com desenvolvedores livres, **When** o usuario seleciona um desenvolvedor livre e confirma, **Then** a historia e atualizada com o desenvolvedor selecionado e a tabela reflete a mudanca.
2. **Given** a dialog de alocacao aberta, **When** existem desenvolvedores ocupados, **Then** suas linhas aparecem greyed out/desabilitadas e nao sao clicaveis (visiveis para informacao mas nao selecionaveis).
3. **Given** a dialog de alocacao aberta, **When** o usuario cancela a dialog, **Then** nenhuma alteracao e feita na historia.

---

### User Story 3 - Alterar Data de Inicio para Recalcular Disponibilidade (Priority: P2)

O usuario deseja alocar um desenvolvedor que esta atualmente ocupado, mas que estara livre em uma data futura. Na dialog, o usuario altera a data de inicio da historia, o que dispara um recalculo de disponibilidade dos desenvolvedores, atualizando a lista de livres/ocupados.

**Why this priority**: Adiciona flexibilidade ao fluxo principal. Sem essa funcionalidade, o usuario estaria limitado a alocar apenas desenvolvedores livres na data atual da historia, restringindo o capacity planning.

**Independent Test**: Pode ser testado alterando a data de inicio na dialog e verificando que a lista de desenvolvedores livres/ocupados e atualizada conforme a nova data.

**Acceptance Scenarios**:

1. **Given** a dialog de alocacao aberta com uma data de inicio exibida, **When** o usuario altera a data de inicio para uma data futura, **Then** a disponibilidade dos desenvolvedores e recalculada e a lista e atualizada.
2. **Given** um desenvolvedor ocupado ate 15/04, **When** o usuario altera a data de inicio para 16/04, **Then** o desenvolvedor passa a aparecer como livre e se torna selecionavel.
3. **Given** o usuario alterou a data de inicio e selecionou um desenvolvedor, **When** confirma a alocacao, **Then** a historia e atualizada com o desenvolvedor selecionado E com a nova data de inicio.
4. **Given** a dialog de alocacao aberta, **When** o usuario altera a data de inicio, **Then** a recomendacao do algoritmo e recalculada para a nova data.

---

### Edge Cases

- O que acontece quando nao ha desenvolvedores cadastrados? A dialog exibe uma mensagem informativa e nao permite selecao.
- O que acontece quando todos os desenvolvedores estao ocupados na data da historia? A lista de "Livres" fica vazia; o usuario pode alterar a data de inicio para encontrar disponibilidade.
- O que acontece quando a historia nao possui datas calculadas (start_date/end_date nulos)? A dialog informa que o agendamento deve ser executado antes da alocacao manual.
- O que acontece quando a historia ja esta concluida (status CONCLUIDO)? A celula "Desenvolvedor" nao abre a dialog de alocacao para historias concluidas.
- O que acontece quando o usuario seleciona a mesma data de inicio que ja existia? Nenhum recalculo ocorre; a lista permanece inalterada.
- O que acontece quando a historia nao possui story points definidos? A dialog exibe mensagem informativa orientando o usuario a definir os story points antes da alocacao manual.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE abrir uma dialog de alocacao manual quando o usuario fizer double-click na celula "Desenvolvedor" de uma historia na tabela de backlog (nao usar droplist/combobox inline como o campo Status). Single-click mantem o comportamento padrao de selecao de linha.
- **FR-002**: A dialog DEVE exibir todos os desenvolvedores cadastrados, separados visualmente em duas secoes: "Livres" e "Ocupados".
- **FR-003**: Para cada desenvolvedor ocupado, a dialog DEVE exibir as historias que o mantem ocupado, incluindo nome da historia, data de inicio e data de fim.
- **FR-004**: O sistema DEVE utilizar a estrategia de alocacao atualmente configurada no projeto (LOAD_BALANCING ou DEPENDENCY_OWNER, conforme configuracao ativa) para identificar e destacar visualmente um desenvolvedor como "Recomendado".
- **FR-005**: O usuario DEVE poder selecionar qualquer desenvolvedor que esteja livre para alocacao.
- **FR-006**: O sistema DEVE impedir a selecao de desenvolvedores que estao ocupados no periodo da historia — linhas de desenvolvedores ocupados ficam greyed out/desabilitadas (visiveis mas nao clicaveis). Nao ha mecanismo de override — o usuario deve alterar a data de inicio (FR-007) para encontrar disponibilidade.
- **FR-007**: A dialog DEVE oferecer um campo para alterar a data de inicio da historia, disparando recalculo automatico de disponibilidade. O date picker DEVE restringir a selecao apenas a dias uteis futuros (bloqueando datas passadas, finais de semana e feriados conforme constante BRAZILIAN_HOLIDAYS existente no SchedulingService).
- **FR-008**: Ao alterar a data de inicio, o sistema DEVE recalcular a data de fim da historia (baseado em story points e velocidade) e atualizar a classificacao livres/ocupados dos desenvolvedores, movendo-os dinamicamente entre as secoes "Livres" e "Ocupados" de forma instantanea.
- **FR-009**: Ao confirmar a alocacao, o sistema DEVE persistir o desenvolvedor selecionado, a data de inicio (se alterada) e a data de fim recalculada (se a data de inicio foi alterada) na historia.
- **FR-010**: A funcionalidade de alocacao manual DEVE reutilizar os servicos de dominio existentes (AllocationService, SchedulingService) sem modifica-los.
- **FR-011**: A dialog NAO DEVE abrir para historias com status CONCLUIDO. Historias com status IMPEDIDO permitem alocacao normalmente.
- **FR-012**: Quando a historia ja possui um desenvolvedor alocado, a dialog DEVE exibir o desenvolvedor atual como pre-selecionado. Se o desenvolvedor atual estiver na secao "Ocupados", ele DEVE ser visualmente destacado (indicando que e o atual) mas permanece nao-selecionavel conforme FR-006.
- **FR-013**: A dialog DEVE exibir uma mensagem informativa quando a historia nao possui datas calculadas, orientando o usuario a executar o agendamento primeiro.

### Key Entities

- **Developer**: Representacao de um membro da equipe com id e nome. Classificado como "Livre" ou "Ocupado" com base na sobreposicao de periodos com a historia alvo.
- **Story**: Item do backlog com id, nome, datas (inicio/fim), story points, developer_id. E o alvo da alocacao manual.
- **AllocationRecommendation**: Conceito derivado — resultado da aplicacao dos criterios de alocacao automatica a um unico developer-story pair, indicando qual desenvolvedor e o mais adequado.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuario consegue alocar manualmente um desenvolvedor a uma historia em menos de 30 segundos (abertura da dialog, selecao e confirmacao).
- **SC-002**: 100% das alocacoes manuais respeitam a regra de nao permitir selecao de desenvolvedores ocupados no periodo da historia.
- **SC-003**: A alteracao de data de inicio atualiza a lista de disponibilidade em tempo real (perceptivelmente instantaneo para o usuario).
- **SC-004**: A recomendacao do algoritmo coincide com o resultado que a alocacao automatica produziria para a mesma historia nas mesmas condicoes.
- **SC-005**: Nenhum servico de dominio existente e modificado para suportar a alocacao manual — toda a logica nova e implementada de forma desacoplada.

## Clarifications

### Session 2026-03-31

- Q: Qual estrategia de alocacao usar para a recomendacao na dialog (LOAD_BALANCING ou DEPENDENCY_OWNER)? → A: Usar a estrategia atualmente configurada no projeto (a mesma usada pela alocacao automatica).
- Q: Ao confirmar alocacao com data de inicio alterada, a end_date recalculada tambem deve ser persistida? → A: Sim, persistir start_date, end_date e developer_id juntos.
- Q: O sistema deve permitir force-override para alocar desenvolvedor ocupado? → A: Nao, bloqueio estrito sem override. Usuario deve alterar data de inicio para encontrar disponibilidade.
- Q: Como a dialog de alocacao deve ser acionada (single-click, double-click, botao)? → A: Double-click na celula "Desenvolvedor" abre a dialog (single-click ja e usado para selecao de linha).
- Q: A dialog deve ser bloqueada para historias com status IMPEDIDO? → A: Nao, apenas CONCLUIDO bloqueia. IMPEDIDO permite alocacao (o impedimento pode ser justamente a falta de desenvolvedor).
- Q: Desenvolvedores ocupados devem ser selecionaveis na dialog? → A: Nao, linhas de desenvolvedores ocupados ficam greyed out/desabilitadas (visiveis mas nao clicaveis).
- Q: Quais restricoes aplicam ao date picker de data de inicio? → A: Apenas dias uteis futuros (bloquear datas passadas, finais de semana e feriados).
- Q: Ao alterar a data de inicio, desenvolvedores devem mover dinamicamente entre secoes Livres/Ocupados? → A: Sim, movimentacao dinamica instantanea entre secoes conforme recalculo de disponibilidade.

## Assumptions

- A velocidade (velocity) e a data de inicio do projeto utilizadas para o recalculo de disponibilidade serao obtidas das configuracoes existentes do sistema (mesmas usadas pela alocacao automatica).
- O conceito de "ocupado" e definido como sobreposicao de periodo: um desenvolvedor esta ocupado se possui pelo menos uma historia cujo periodo (start_date a end_date) se sobrepoem com o periodo da historia sendo alocada.
- Feriados sao considerados no recalculo de datas, reutilizando o servico de agendamento existente.
- A dialog segue o design system existente do projeto (cores, fontes, espacamentos definidos no theme).
- A coluna "Desenvolvedor" na tabela ja existe e exibe o nome do desenvolvedor alocado; a mudanca e no comportamento ao fazer double-click (dialog ao inves de edicao direta).
