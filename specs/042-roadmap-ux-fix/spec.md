# Feature Specification: Correção de Problemas de Interface do Roadmap

**Feature Branch**: `042-roadmap-ux-fix`
**Created**: 2026-04-04
**Status**: Draft
**Input**: Epic "Correção de Problemas de Interface do Roadmap" — 17 problemas críticos de usabilidade no módulo de visualização de roadmap (timeline Gantt)

## Clarifications

### Session 2026-04-04

- Q: "Ajustar à tela" (US5) e "Ajustar ao conteúdo" (US11) são o mesmo botão ou dois botões separados? → A: Dois botões separados na toolbar — "Ajustar à tela" mostra o período completo, "Ajustar ao conteúdo" foca na região de maior densidade.
- Q: Qual nível de acessibilidade por teclado deve ser implementado? → A: Parcial — toolbar, filtros e expand/collapse de waves navegáveis por teclado (Tab/Enter). Navegação granular nas barras individuais fica para iteração futura.
- Q: Qual cor exata para a linha "hoje"? → A: Laranja (#ED8936), evitando conflito semântico com o vermelho de IMPEDIDO no STATUS_PALETTE.

## User Scenarios & Testing *(mandatory)*


### User Story 1 - Visualização legível de barras com cores de status (Priority: P1)

O gerente de projeto abre o roadmap e precisa identificar rapidamente o status de cada história pela cor da barra. Atualmente todas as barras aparecem na mesma cor cinza, impossibilitando a identificação visual de progresso. Após a correção, cada barra exibe a cor correspondente ao seu status real (BACKLOG cinza, EXECUÇÃO azul, TESTES amarelo, CONCLUÍDO verde, IMPEDIDO vermelho tracejado) com preenchimento parcial indicando progresso.

**Why this priority**: Sem cores de status, o roadmap perde sua função principal como ferramenta de acompanhamento — o gerente não consegue distinguir o progresso de nenhuma história.

**Independent Test**: Pode ser testado carregando um backlog com histórias em diferentes status e verificando visualmente que cada barra exibe a cor e preenchimento corretos conforme o STATUS_PALETTE.

**Acceptance Scenarios**:

1. **Given** um backlog com histórias em status BACKLOG, EXECUÇÃO, TESTES, CONCLUÍDO e IMPEDIDO, **When** o usuário abre o roadmap, **Then** cada barra exibe a cor correspondente ao seu status conforme o STATUS_PALETTE definido no design system
2. **Given** uma história em status EXECUÇÃO, **When** renderizada no roadmap, **Then** a barra exibe preenchimento parcial de 33% em tom mais escuro da cor azul
3. **Given** uma história em status IMPEDIDO, **When** renderizada no roadmap, **Then** a barra exibe cor vermelha com borda tracejada

---

### User Story 2 - Expandir e colapsar waves funcionalmente (Priority: P1)

O desenvolvedor precisa expandir uma wave para ver as histórias individuais e depois colapsar para ter visão geral. Atualmente o toggle não funciona bidirecionalmente. Após a correção, clicar no cabeçalho de uma wave alterna entre expandido (mostra histórias individuais com altura mínima legível) e colapsado (mostra apenas barra de resumo). O scroll vertical funciona fluidamente quando o conteúdo excede a área visível.

**Why this priority**: Sem expandir/colapsar funcional, o usuário não consegue navegar entre visão geral e detalhada, tornando o roadmap inutilizável para backlogs grandes.

**Independent Test**: Pode ser testado clicando em cabeçalhos de waves e verificando que o toggle alterna corretamente, as histórias são exibidas com altura mínima, e o scroll funciona.

**Acceptance Scenarios**:

1. **Given** o roadmap com waves colapsadas, **When** o usuário clica no cabeçalho de uma wave, **Then** a wave expande mostrando cada história como barra individual
2. **Given** uma wave expandida, **When** o usuário clica novamente no cabeçalho, **Then** a wave colapsa voltando a exibir apenas a barra de resumo
3. **Given** múltiplas waves expandidas cujo conteúdo excede a área visível, **When** o conteúdo total ultrapassa o viewport, **Then** o scroll vertical funciona de forma fluida
4. **Given** uma história com rótulo longo, **When** expandida, **Then** o rótulo é truncado com reticências sem sobrepor rótulos adjacentes e a barra mantém altura mínima legível
5. **Given** o container do gráfico, **When** o usuário expande ou colapsa uma wave, **Then** a altura total é recalculada sem comprimir linhas existentes

---

### User Story 3 - Controles de janela e espaço útil (Priority: P1)

O gerente de projeto abre o roadmap e a janela não possui controles padrão de maximizar/minimizar, limitando o espaço útil para visualização. Após a correção, a janela abre maximizada por padrão com botões de minimizar, maximizar e redimensionar funcionais, permitindo ao usuário ajustar o espaço conforme necessário.

**Why this priority**: Sem maximizar, o roadmap fica confinado a um diálogo pequeno, inviabilizando a visualização de backlogs com muitas histórias.

**Independent Test**: Pode ser testado abrindo o roadmap e verificando que a janela abre maximizada com botões de controle funcionais.

**Acceptance Scenarios**:

1. **Given** o usuário aciona a abertura do roadmap, **When** o diálogo é exibido, **Then** a janela abre maximizada com botões de minimizar, maximizar e fechar visíveis
2. **Given** a janela do roadmap aberta, **When** o usuário redimensiona a janela, **Then** o conteúdo se adapta ao novo tamanho sem distorção

---

### User Story 4 - Eixo temporal adaptativo e legível (Priority: P2)

O gerente visualiza o roadmap em diferentes níveis de zoom e os marcadores de data ficam sobrepostos ou ilegíveis. Após a correção, os marcadores se adaptam automaticamente à largura disponível, com granularidade variável (dias/semanas/meses) conforme o zoom, mantendo sempre contexto suficiente nos rótulos.

**Why this priority**: Marcadores ilegíveis removem o contexto temporal, mas o roadmap ainda é parcialmente utilizável com referência às barras.

**Independent Test**: Pode ser testado variando o zoom e verificando que os marcadores permanecem legíveis, sem sobreposição, e com granularidade adequada.

**Acceptance Scenarios**:

1. **Given** o roadmap em zoom próximo, **When** o eixo temporal é renderizado, **Then** os marcadores exibem datas diárias na horizontal com espaçamento adequado
2. **Given** o roadmap em zoom distante, **When** o eixo temporal é renderizado, **Then** os marcadores exibem meses com contexto suficiente (ex: "Abr 2026")
3. **Given** espaço insuficiente para marcadores horizontais, **When** renderizados, **Then** os marcadores são rotacionados no máximo 45 graus
4. **Given** qualquer nível de zoom, **When** o eixo temporal é renderizado, **Then** há no mínimo 5 marcadores visíveis com contexto suficiente

---

### User Story 5 - Controles de zoom com feedback visual (Priority: P2)

O usuário utiliza os botões de zoom ou Ctrl+Scroll para ajustar a visualização. Os ícones atuais são confusos (setas direcionais) e não há indicação do nível atual. Após a correção, os botões usam ícones de lupa com +/-, há indicador de nível de zoom, botão "Ajustar à tela" e todos os botões possuem tooltips descritivos.

**Why this priority**: Controles confusos dificultam a navegação, mas o zoom via Ctrl+Scroll ainda funciona como alternativa.

**Independent Test**: Pode ser testado interagindo com os controles de zoom e verificando ícones, indicador de nível, tooltips e botão "Ajustar à tela".

**Acceptance Scenarios**:

1. **Given** a toolbar do roadmap, **When** o usuário visualiza os controles de zoom, **Then** os botões exibem ícones de lupa com + e - (não setas direcionais)
2. **Given** o usuário altera o zoom, **When** o nível muda, **Then** um indicador numérico (ex: "100%", "150%") é atualizado próximo aos controles
3. **Given** o zoom no nível máximo, **When** o usuário tenta ampliar mais, **Then** o zoom é limitado a mostrar no máximo 7 dias na viewport
4. **Given** qualquer nível de zoom, **When** o usuário clica em "Ajustar à tela", **Then** o zoom é redimensionado para mostrar todo o período do roadmap
5. **Given** qualquer botão da toolbar, **When** o usuário passa o mouse sobre ele, **Then** um tooltip descritivo é exibido

---

### User Story 6 - Legenda padronizada e consistente (Priority: P2)

O usuário consulta a legenda para entender o mapeamento de cores e encontra uma mistura confusa de símbolos diferentes. Após a correção, a legenda usa exclusivamente quadrados coloridos padronizados para todos os status, com tipografia e espaçamento do design system.

**Why this priority**: A legenda confusa dificulta a interpretação das cores, mas com a codificação correta nas barras (P1) o impacto é amenizado.

**Independent Test**: Pode ser testado verificando visualmente que a legenda usa apenas quadrados coloridos e segue a tipografia do design system.

**Acceptance Scenarios**:

1. **Given** o roadmap aberto, **When** o usuário visualiza a legenda, **Then** todos os status são representados por quadrados coloridos de no mínimo 12x12px seguidos do nome do status
2. **Given** a legenda renderizada, **When** comparada com outros componentes da aplicação, **Then** a tipografia e espaçamento são consistentes com o design system

---

### User Story 7 - Rótulos de grupo com nome da feature (Priority: P2)

O usuário visualiza as waves e vê apenas "Wave N" sem saber o escopo funcional. Após a correção, os rótulos exibem "Wave N — [Nome da Feature] - X% [Y histórias]", facilitando a identificação do conteúdo de cada wave.

**Why this priority**: Melhora significativa de contexto, mas o número da wave ainda permite navegação básica.

**Independent Test**: Pode ser testado verificando que os rótulos das waves exibem o formato completo com nome da feature quando disponível.

**Acceptance Scenarios**:

1. **Given** uma wave associada a uma feature, **When** renderizada no roadmap, **Then** o rótulo exibe "Wave N — [Nome da Feature] - X% [Y histórias]"
2. **Given** uma wave com histórias de múltiplas features, **When** renderizada, **Then** o rótulo lista as features separadas por vírgula, truncando se necessário
3. **Given** uma wave sem informação de feature disponível, **When** renderizada, **Then** o rótulo exibe "Wave N" como fallback

---

### User Story 8 - Consistência visual com design system (Priority: P2)

O usuário navega entre o roadmap e outras telas e percebe descontinuidade visual nos dropdowns, tooltips, campo de busca e botões. Após a correção, todos os widgets do roadmap seguem o stylesheet global da aplicação.

**Why this priority**: Afeta a percepção de qualidade da ferramenta, mas não bloqueia funcionalidade.

**Independent Test**: Pode ser testado comparando visualmente os componentes do roadmap com componentes equivalentes em outras telas da aplicação.

**Acceptance Scenarios**:

1. **Given** os dropdowns de filtro no roadmap, **When** comparados com dropdowns em outras telas, **Then** usam o mesmo estilo de padding, fonte e bordas
2. **Given** o campo de busca no roadmap, **When** renderizado, **Then** inclui ícone de lupa e segue o estilo visual dos inputs da aplicação
3. **Given** os botões da toolbar no roadmap, **When** comparados com botões de outras telas, **Then** seguem o mesmo tamanho, padding e estilo

---

### User Story 9 - Linha "hoje" destacada (Priority: P2)

O usuário precisa identificar visualmente a data atual no roadmap para contextualizar o progresso. A linha atual é pouco visível. Após a correção, a linha "hoje" é espessa, em cor destacada, com label "Hoje" e em camada superior para não ser ocultada por barras.

**Why this priority**: Referência temporal importante para contextualizar progresso, mas não bloqueia navegação.

**Independent Test**: Pode ser testado verificando visualmente que a linha "hoje" é claramente distinta das linhas de grade e possui label identificativo.

**Acceptance Scenarios**:

1. **Given** o roadmap aberto, **When** a data atual está no período visível, **Then** uma linha vertical destacada (mínimo 2px, cor laranja #ED8936, opacidade >= 0.8) marca a data de hoje
2. **Given** a linha "hoje" renderizada, **When** há barras na mesma posição, **Then** a linha permanece visível acima das barras
3. **Given** a linha "hoje" renderizada, **When** o usuário a visualiza, **Then** um label "Hoje" é exibido próximo ao topo da linha

---

### User Story 10 - Correção do dropdown fantasma (Priority: P3)

O usuário interage com o dropdown de Status e um retângulo vazio ou popup fantasma aparece. Após a correção, o dropdown funciona normalmente sem artefatos visuais.

**Why this priority**: Bug visual pontual que afeta apenas a interação com filtro de status.

**Independent Test**: Pode ser testado interagindo repetidamente com o dropdown de Status e verificando ausência de artefatos visuais.

**Acceptance Scenarios**:

1. **Given** o dropdown de Status no roadmap, **When** o usuário clica para abrir, **Then** apenas as opções disponíveis são exibidas sem retângulos vazios ou popups fantasma
2. **Given** o dropdown de Status aberto, **When** o usuário seleciona uma opção ou clica fora, **Then** o dropdown fecha normalmente sem artefatos residuais

---

### User Story 11 - Escala temporal adaptativa à distribuição (Priority: P3)

O usuário visualiza histórias distribuídas de forma desigual no tempo e a viewport inicial mostra grandes áreas vazias. Após a correção, o zoom inicial foca na região com maior densidade de tarefas e há opção de "Ajustar ao conteúdo".

**Why this priority**: Melhora a experiência inicial mas o usuário pode ajustar manualmente via zoom.

**Independent Test**: Pode ser testado com dados desigualmente distribuídos e verificando que o zoom inicial foca na região densa.

**Acceptance Scenarios**:

1. **Given** um backlog onde 90% das tarefas estão concentradas em 20% do período, **When** o roadmap abre, **Then** o zoom inicial foca na região de maior densidade
2. **Given** o roadmap aberto, **When** o usuário clica em "Ajustar ao conteúdo", **Then** a viewport redimensiona para a região com maior densidade de tarefas

---

### User Story 12 - Setas de dependência melhoradas (Priority: P3)

O usuário visualiza dependências entre histórias e as setas vermelhas sugerem erro. Após a correção, as setas usam cor neutra, curvatura variável para reduzir sobreposição e há opção de mostrar todas simultaneamente.

**Why this priority**: Melhora visual e funcional, mas dependências já são visíveis via hover (comportamento mantido).

**Independent Test**: Pode ser testado passando o mouse sobre histórias com dependências e verificando cor, curvatura e opção de exibir todas.

**Acceptance Scenarios**:

1. **Given** histórias com dependências no roadmap, **When** o usuário passa o mouse sobre uma história, **Then** as setas de dependência são exibidas em cor neutra (azul escuro ou cinza escuro)
2. **Given** múltiplas setas se sobrepondo a barras, **When** renderizadas, **Then** usam curvatura variável para reduzir sobreposição
3. **Given** a toolbar do roadmap, **When** o usuário clica em "Mostrar todas as dependências", **Then** todas as setas de dependência são renderizadas simultaneamente

---

### User Story 13 - Barra de status enriquecida no rodapé (Priority: P3)

O usuário consulta o resumo de status no rodapé e vê apenas contagens textuais. Após a correção, há mini-barra de progresso visual ao lado das contagens e indicação de filtros ativos.

**Why this priority**: Enriquecimento informacional que melhora a experiência mas não bloqueia funcionalidade existente.

**Independent Test**: Pode ser testado verificando que o rodapé exibe contagens com mini-barra de progresso e indica filtros ativos quando aplicados.

**Acceptance Scenarios**:

1. **Given** o roadmap aberto, **When** o usuário visualiza o rodapé, **Then** contagens por status são exibidas com mini-barra de progresso horizontal nas cores do STATUS_PALETTE
2. **Given** filtros ativos no roadmap, **When** o usuário visualiza o rodapé, **Then** a mensagem exibe "X de Y histórias (filtro ativo)"

---

### User Story 14 - Navegação eficiente para alto volume (Priority: P3)

O usuário navega por um backlog de 190+ histórias e precisa localizar histórias específicas. A busca atual não mostra contador de resultados e não oculta não-correspondentes. Após a correção, a busca exibe contador, oculta não-correspondentes, e o scroll é sincronizado entre painéis.

**Why this priority**: Melhora significativa para backlogs grandes, mas filtros existentes já permitem reduzir o volume visível.

**Independent Test**: Pode ser testado buscando uma história em backlog grande e verificando contador, ocultação e sincronização de scroll.

**Acceptance Scenarios**:

1. **Given** um backlog com 190 histórias, **When** o usuário digita no campo de busca, **Then** um contador exibe "X de Y histórias" com os resultados encontrados
2. **Given** uma busca ativa, **When** os resultados são exibidos, **Then** histórias que não correspondem são ocultadas (filtro efetivo)
3. **Given** o roadmap com scroll, **When** o usuário rola verticalmente, **Then** o painel de rótulos e a área de barras rolam sincronizados
4. **Given** uma wave com muitas histórias, **When** o usuário a expande, **Then** o sistema faz auto-scroll para que o conteúdo expandido fique visível

---

### User Story 15 - Correção da Wave 7 ausente (Priority: P3)

O usuário visualiza todas as waves e percebe lacuna na numeração (Wave 7 ausente). Após a correção, todas as waves são exibidas sem lacunas, ou waves vazias são exibidas com indicação "(vazia)".

**Why this priority**: Bug específico que afeta completude dos dados exibidos, mas não impede uso das demais waves.

**Independent Test**: Pode ser testado verificando que todas as waves são renderizadas sem lacunas na numeração.

**Acceptance Scenarios**:

1. **Given** dados que incluem Wave 7, **When** o roadmap é renderizado, **Then** a Wave 7 é exibida corretamente na sequência
2. **Given** uma wave sem histórias associadas, **When** renderizada, **Then** a wave é exibida com indicação "(vazia)" ou "(0 histórias)"
3. **Given** todas as waves renderizadas, **When** o usuário verifica a sequência, **Then** não há lacunas na numeração

---

### Edge Cases

- O que acontece quando o backlog tem 0 histórias? O roadmap deve exibir estado vazio com mensagem informativa.
- O que acontece quando todas as histórias estão no mesmo status? As barras devem exibir a cor correspondente e a legenda deve mostrar todos os status (não apenas o ativo).
- O que acontece quando uma história não tem datas definidas? A história deve ser excluída do roadmap com indicação no rodapé de quantas histórias foram omitidas por falta de datas.
- O que acontece quando o período de uma história é de 0 dias (início = fim)? A barra deve ser renderizada com largura mínima visível (ex: 1 dia de largura).
- O que acontece quando o usuário redimensiona a janela enquanto waves estão expandidas? O gráfico deve se reajustar mantendo o estado de expansão.
- O que acontece quando não há dependências no backlog? O botão "Mostrar todas as dependências" deve ficar desabilitado com tooltip explicativo.
- O que acontece quando o usuário busca um termo sem resultados? O roadmap exibe mensagem "Nenhuma história encontrada" e o contador mostra "0 de Y histórias".

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir a janela do roadmap com botões de minimizar, maximizar e fechar, abrindo maximizada por padrão
- **FR-002**: O sistema DEVE permitir redimensionamento livre da janela do roadmap
- **FR-003**: O sistema DEVE implementar toggle bidirecional de expandir/colapsar ao clicar no cabeçalho de uma wave
- **FR-004**: O sistema DEVE renderizar cada história expandida com altura mínima de 20px
- **FR-005**: O sistema DEVE oferecer scroll vertical fluido quando o conteúdo total excede a área visível
- **FR-006**: O sistema DEVE truncar rótulos longos com reticências sem sobrepor rótulos adjacentes
- **FR-007**: O sistema DEVE recalcular a altura total do gráfico ao expandir/colapsar waves sem comprimir linhas existentes
- **FR-008**: O sistema DEVE adaptar automaticamente os marcadores de data conforme o nível de zoom e largura disponível
- **FR-009**: O sistema DEVE variar a granularidade temporal: dias (zoom próximo), semanas (zoom médio), meses (zoom distante)
- **FR-010**: O sistema DEVE manter no mínimo 5 marcadores de data visíveis em qualquer nível de zoom
- **FR-011**: O sistema DEVE exibir marcadores de data na horizontal quando há espaço, rotacionando no máximo 45 graus quando necessário
- **FR-012**: O sistema DEVE exibir ícones de lupa com + e - nos botões de zoom (não setas direcionais)
- **FR-013**: O sistema DEVE exibir indicador numérico do nível de zoom atual (ex: "100%", "150%")
- **FR-014**: O sistema DEVE limitar o zoom inferior para que nomes de waves sejam legíveis e o superior para mostrar no máximo 7 dias na viewport
- **FR-015**: O sistema DEVE oferecer botão "Ajustar à tela" que redimensiona o zoom para mostrar todo o período (botão separado de "Ajustar ao conteúdo")
- **FR-016**: O sistema DEVE exibir tooltips descritivos em todos os botões da toolbar
- **FR-017**: O sistema DEVE colorir cada barra conforme o STATUS_PALETTE do design system baseado no status real da história
- **FR-018**: O sistema DEVE exibir preenchimento parcial nas barras indicando progresso (0% BACKLOG, 33% EXECUÇÃO, 66% TESTES, 100% CONCLUÍDO)
- **FR-019**: O sistema DEVE renderizar barras de histórias IMPEDIDO com cor vermelha e borda tracejada
- **FR-020**: O sistema DEVE exibir a legenda usando exclusivamente quadrados coloridos de no mínimo 12x12px para todos os status
- **FR-021**: O sistema DEVE exibir rótulos de wave no formato "Wave N — [Nome da Feature] - X% [Y histórias]" quando a informação de feature está disponível
- **FR-022**: O sistema DEVE aplicar o stylesheet global da aplicação a todos os widgets do diálogo de roadmap
- **FR-023**: O sistema DEVE eliminar artefatos visuais (retângulos vazios, popups fantasma) ao interagir com dropdowns
- **FR-024**: O sistema DEVE focar o zoom inicial na região de maior densidade de tarefas quando a distribuição é desigual (via botão dedicado "Ajustar ao conteúdo", separado de "Ajustar à tela")
- **FR-025**: O sistema DEVE renderizar a linha "hoje" com espessura mínima de 2px, cor laranja (#ED8936) com opacidade >= 0.8, label "Hoje" e em camada superior
- **FR-026**: O sistema DEVE exibir setas de dependência em cor neutra (azul escuro ou cinza escuro) ao invés de vermelho
- **FR-027**: O sistema DEVE oferecer opção "Mostrar todas as dependências" na toolbar
- **FR-028**: O sistema DEVE exibir mini-barra de progresso horizontal no rodapé ao lado das contagens por status
- **FR-029**: O sistema DEVE indicar "X de Y histórias (filtro ativo)" no rodapé quando filtros estiverem ativos
- **FR-030**: O sistema DEVE exibir contador de resultados na busca (ex: "3 de 190 histórias")
- **FR-031**: O sistema DEVE ocultar histórias que não correspondem à busca (filtro efetivo)
- **FR-032**: O sistema DEVE sincronizar o scroll vertical entre o painel de rótulos e a área de barras
- **FR-033**: O sistema DEVE fazer auto-scroll ao expandir uma wave para que o conteúdo expandido fique visível
- **FR-034**: O sistema DEVE renderizar todas as waves sem lacunas na numeração, exibindo waves vazias com indicação "(vazia)"
- **FR-035**: O sistema DEVE renderizar o gráfico completo com 190 histórias em no máximo 2 segundos
- **FR-036**: O sistema DEVE permitir navegação por teclado (Tab/Enter) nos controles da toolbar, filtros e expand/collapse de waves

### Key Entities

- **Wave**: Agrupamento de histórias por ciclo de entrega. Atributos: número, nome da feature (quando disponível), percentual de progresso, contagem de histórias
- **História**: Unidade de trabalho com prazo e responsável. Atributos: nome, status (BACKLOG/EXECUÇÃO/TESTES/CONCLUÍDO/IMPEDIDO), desenvolvedor, pontos, datas de início e fim, componente, dependências
- **Dependência**: Relação entre duas histórias indicando que uma depende da conclusão de outra

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Todas as 17 issues do relatório de auditoria são resolvidas e verificáveis em teste manual
- **SC-002**: O roadmap exibe corretamente 190 histórias com todas as waves expandidas sem sobreposição de rótulos
- **SC-003**: O toggle expandir/colapsar funciona bidirecionalmente em todas as waves sem falhas
- **SC-004**: 100% das barras exibem cores correspondentes ao status real de cada história
- **SC-005**: Os marcadores do eixo temporal são legíveis em todos os níveis de zoom, sem sobreposição
- **SC-006**: A janela pode ser maximizada, minimizada e redimensionada sem distorção do conteúdo
- **SC-007**: Nenhum artefato visual (dropdown fantasma) aparece durante a interação com filtros
- **SC-008**: 100% dos botões da toolbar possuem tooltips descritivos
- **SC-009**: A linha "hoje" é visualmente distinta das linhas de grade em todos os cenários
- **SC-010**: O tempo de renderização completa não excede 2 segundos com 190 histórias
- **SC-011**: A interface do roadmap é visualmente consistente com o restante da aplicação (mesmos estilos de componentes)

## Assumptions

- O STATUS_PALETTE já está definido e disponível no design system da aplicação
- A informação de feature/módulo está disponível nos dados das histórias para composição dos rótulos de wave (caso contrário, fallback para "Wave N")
- O bug de cores cinzas nas barras é um problema de renderização (o código de mapeamento de cores existe mas não está sendo aplicado corretamente)
- O problema do dropdown fantasma é causado por um widget não-populado ou órfão, não por limitação do framework
- A Wave 7 existe nos dados mas não está sendo renderizada (bug de renderização, não de dados)
- Filtros operam com lógica AND (comportamento existente mantido)
- O estado de expandir/colapsar não precisa persistir entre sessões
- Tooltips de barras individuais continuam funcionando normalmente (nome, status, desenvolvedor, pontos, datas, duração, componente, dependências)
