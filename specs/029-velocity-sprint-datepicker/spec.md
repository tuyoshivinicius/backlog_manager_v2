# Feature Specification: Velocidade em SP/Sprint e DatePicker Reutilizavel

**Feature Branch**: `029-velocity-sprint-datepicker`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Alterar a unidade de medida de velocidade na Configuracao de Alocacao de SP/dia para SP/Sprint, e adicionar campo de dias uteis por sprint, com impacto em dominio, aplicacao e apresentacao. Adicionalmente, criar componente DatePicker reutilizavel para campos de data."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Configurar Velocidade em SP/Sprint (Priority: P1)

O usuario abre a configuracao de alocacao (ConfigDialog ou ConfigPanel) e configura a velocidade do time em story points por sprint (ex: 20 SP/Sprint) em vez de story points por dia. O usuario tambem informa quantos dias uteis tem uma sprint (ex: 10 dias). O sistema deriva internamente a velocidade por dia (velocity_per_day = sp_per_sprint / workdays_per_sprint) para uso nos calculos de duracao.

**Why this priority**: Esta e a mudanca principal da feature. SP/Sprint e a unidade mais natural para times ageis, alinhada com como equipes realmente medem velocidade. Sem isso, o usuario precisa fazer a conversao mental de SP/Sprint para SP/dia.

**Independent Test**: Pode ser testado abrindo o ConfigDialog, preenchendo SP/Sprint e dias uteis por sprint, aplicando, e verificando que a alocacao automatica calcula duracoes corretamente com a velocidade derivada.

**Acceptance Scenarios**:

1. **Given** o ConfigDialog esta aberto, **When** o usuario insere 20 no campo "Velocidade (SP/Sprint)" e 10 no campo "Dias Uteis por Sprint", **Then** o sistema aceita os valores e persiste ambos os campos.
2. **Given** o usuario configurou 20 SP/Sprint e 10 dias/sprint, **When** a alocacao automatica e executada, **Then** o SchedulingService recebe velocity_per_day = 2.0 (20/10) e calcula duracoes corretamente.
3. **Given** o ConfigPanel esta visivel no painel lateral, **When** o usuario altera a velocidade para 15 SP/Sprint e dias uteis para 5, **Then** os valores sao refletidos e a velocidade derivada e 3.0 SP/dia.
4. **Given** o campo SP/Sprint esta vazio ou com valor invalido, **When** o usuario tenta aplicar, **Then** o sistema exibe mensagem de validacao e impede a aplicacao.

---

### User Story 2 - Persistencia e Migracao de Velocidade (Priority: P2)

Os novos campos (SP/Sprint e dias uteis por sprint) sao persistidos via QSettings. Quando o usuario reabre a aplicacao, os valores configurados anteriormente sao restaurados. Se existir um valor antigo de velocidade em SP/dia (de versao anterior), o sistema trata com defaults seguros sem erro.

**Why this priority**: Sem persistencia, o usuario teria que reconfigurar a cada abertura. A migracao garante compatibilidade retroativa com configuracoes existentes.

**Independent Test**: Pode ser testado configurando valores, fechando e reabrindo o dialog, verificando que os valores foram restaurados. Para migracao, simular QSettings com velocity antigo em SP/dia e verificar que o sistema carrega com defaults seguros.

**Acceptance Scenarios**:

1. **Given** o usuario configurou 25 SP/Sprint e 10 dias/sprint e aplicou, **When** ele reabre o ConfigDialog, **Then** os campos mostram 25 SP/Sprint e 10 dias/sprint.
2. **Given** o QSettings contem apenas "velocity" (formato antigo em SP/dia) sem "sp_per_sprint", **When** o ConfigDialog e aberto, **Then** o sistema carrega defaults seguros (sp_per_sprint=20, workdays_per_sprint=10) sem erro ou crash.
3. **Given** o QSettings esta completamente vazio (primeira execucao), **When** o ConfigDialog e aberto, **Then** os campos exibem os valores padrao (sp_per_sprint=20, workdays_per_sprint=10).

---

### User Story 3 - DatePicker Reutilizavel (Priority: P3)

O usuario interage com campos de data (data de inicio do projeto, data de inicio de alocacao manual) atraves de um componente DatePicker reutilizavel com estilizacao consistente com o Design System. O componente substitui os QDateEdit inline existentes, oferecendo calendar popup, formato dd/MM/yyyy e suporte a min/max date.

**Why this priority**: Embora melhore a consistencia visual e a manutencao do codigo, e uma refatoracao de componente que nao altera funcionalidade. Os QDateEdit existentes ja funcionam corretamente.

**Independent Test**: Pode ser testado abrindo o ConfigDialog e o ManualAllocationDialog, interagindo com os campos de data e verificando que o comportamento e identico ao anterior (calendar popup, formato, restricoes de data) com estilizacao consistente.

**Acceptance Scenarios**:

1. **Given** o ConfigDialog esta aberto, **When** o usuario clica no campo de data de inicio, **Then** um calendar popup e exibido com formato dd/MM/yyyy e estilizacao consistente com o Design System.
2. **Given** o ManualAllocationDialog esta aberto, **When** o usuario interage com o campo de data de inicio, **Then** o DatePicker exibe calendar popup com data minima configurada (proximo dia util).
3. **Given** o DatePicker tem min_date configurado, **When** o usuario tenta selecionar uma data anterior ao minimo, **Then** a data nao e aceita e o campo permanece com o valor anterior.

---

### Edge Cases

- O que acontece quando o usuario insere 0 ou valor negativo em SP/Sprint? O sistema deve validar e impedir (range minimo > 0).
- O que acontece quando dias uteis por sprint e 0? O sistema deve validar (range minimo >= 1) para evitar divisao por zero na derivacao velocity_per_day.
- Como o sistema se comporta com valores extremos (ex: 1 SP/Sprint e 15 dias/sprint resultando em 0.067 SP/dia)? Deve funcionar corretamente com a formula existente.
- O que acontece se o QSettings contem dados corrompidos nos novos campos? Defaults seguros devem ser usados.
- O que acontece quando o DatePicker recebe min_date posterior a max_date? O componente deve tratar graciosamente.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O campo "Velocidade" no ConfigDialog e ConfigPanel DEVE usar a unidade SP/Sprint (inteiro, range 1-100, default 20).
- **FR-002**: O ConfigDialog e ConfigPanel DEVEM exibir um novo campo "Dias Uteis por Sprint" (inteiro, range 1-30, default 10).
- **FR-003**: O sistema DEVE derivar velocity_per_day internamente como sp_per_sprint / workdays_per_sprint antes de passar ao dominio.
- **FR-004**: O SchedulingService e AllocationConfig DEVEM continuar recebendo velocity_per_day (float em SP/dia) sem alteracao na formula interna.
- **FR-005**: Os valores de SP/Sprint e dias uteis por sprint DEVEM ser persistidos via QSettings no grupo "allocation".
- **FR-006**: O sistema DEVE tratar migracao de QSettings antigo (velocity em SP/dia) com defaults seguros quando os novos campos nao existirem.
- **FR-007**: O sistema DEVE disponibilizar um componente DatePicker reutilizavel com calendar popup, formato dd/MM/yyyy e suporte a min/max date.
- **FR-008**: O DatePicker DEVE seguir a estilizacao do Design System existente (DESIGN_TOKENS).
- **FR-009**: O DatePicker DEVE substituir os QDateEdit inline no ConfigDialog/ConfigPanel e ManualAllocationDialog.
- **FR-010**: A validacao DEVE impedir divisao por zero: dias uteis por sprint deve ser >= 1.
- **FR-011**: A validacao DEVE impedir SP/Sprint <= 0.
- **FR-012**: O ConfigDialog e ConfigPanel DEVEM exibir um label read-only com o valor derivado de velocity_per_day (ex: "= 2.0 SP/dia") atualizado dinamicamente quando o usuario altera SP/Sprint ou dias uteis por sprint.

### Key Entities

- **AllocationConfig**: Entidade de dominio que armazena configuracao de alocacao. Continua recebendo velocity como float em SP/dia (derivada). Sem alteracao na entidade de dominio.
- **ExecuteAllocationInputDTO**: DTO de aplicacao que trafega parametros de alocacao. Continua recebendo velocity como float em SP/dia. A conversao SP/Sprint -> SP/dia ocorre na camada de apresentacao/viewmodel.
- **DatePicker**: Novo componente de apresentacao reutilizavel para campos de data com estilizacao consistente e configuracao de formato/restricoes.

## Clarifications

### Session 2026-03-31

- Q: O usuario deve ver o valor derivado de velocity_per_day como feedback visual? → A: Sim, exibir label read-only com velocity_per_day derivada (ex: "= 2.0 SP/dia").
- Q: O campo SP/Sprint deve ser inteiro ou decimal? → A: Inteiro apenas (range 1-100).

## Assumptions

- **Dominio inalterado**: A decisao e manter AllocationConfig e SchedulingService recebendo velocity_per_day (SP/dia). Justificativa: o dominio opera em "dias uteis" como unidade atomica de planejamento. SP/Sprint e uma conveniencia de UX que nao deveria vazar para o dominio. A conversao e responsabilidade da camada de apresentacao/viewmodel, mantendo o dominio desacoplado de conceitos de sprint.
- **Range de SP/Sprint**: O range 1-100 cobre cenarios comuns (times pequenos com 5 SP/sprint ate times grandes com 80+ SP/sprint).
- **Range de dias uteis por sprint**: O range 1-30 permite sprints de 1 dia (kanban-like) ate sprints de 6 semanas. Default de 10 dias (2 semanas) e o mais comum em Scrum.
- **Migracao**: Ao encontrar QSettings antigo sem os novos campos, o sistema usa defaults (20 SP/Sprint, 10 dias/sprint). O campo antigo "velocity" (SP/dia) e ignorado apos migracao, pois os novos campos sao a fonte de verdade.
- **DatePicker**: O componente nao implementa validacao de dias uteis (business days) internamente. A logica de dias uteis permanece no SchedulingService. O DatePicker apenas oferece min/max date e formato.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuario consegue configurar velocidade em SP/Sprint e dias uteis por sprint em menos de 30 segundos, sem necessidade de calcular manualmente SP/dia.
- **SC-002**: 100% das alocacoes automaticas produzem resultados identicos quando a velocidade derivada (SP/Sprint / dias) e equivalente a velocidade anterior em SP/dia.
- **SC-003**: Ao reabrir a aplicacao, os valores de SP/Sprint e dias uteis por sprint sao restaurados corretamente em 100% dos casos.
- **SC-004**: Todos os campos de data na aplicacao utilizam o componente DatePicker reutilizavel com aparencia visual consistente.
- **SC-005**: A migracao de configuracoes antigas ocorre sem erros ou perda de dados, com defaults seguros aplicados automaticamente.
