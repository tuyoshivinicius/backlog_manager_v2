# Feature Specification: Roadmap UX Refactor

**Feature Branch**: `043-roadmap-ux-refactor`
**Created**: 2026-04-05
**Status**: Draft
**Input**: User description: "Refatorar a funcionalidade de roadmap com toolbar organizada e agrupada com icones e tooltips, zoom in/out/reset, controle visual de dependencias, filtros por feature/componente/responsavel/nome, agrupamento por feature com expand/collapse, codigo da historia nas barras e legenda lateral, quantidade de historias e percentual de conclusao na coluna lateral."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Toolbar Organizada e Minimalista (Priority: P1)

O usuario abre o roadmap e encontra uma toolbar limpa, com ferramentas agrupadas logicamente por funcao. Cada botao possui um icone reconhecivel e um tooltip descritivo que aparece ao passar o mouse. Os grupos sao separados visualmente e facilmente identificaveis: controles de zoom, filtros, controle de dependencias e acoes gerais.

**Why this priority**: A toolbar e o ponto de entrada para todas as interacoes do roadmap. Uma toolbar confusa impede o usuario de descobrir e usar as funcionalidades disponiveis.

**Independent Test**: Pode ser testado abrindo o roadmap e verificando que todos os botoes possuem icones visiveis e tooltips descritivos, e que os grupos estao visualmente separados.

**Acceptance Scenarios**:

1. **Given** o usuario abre o roadmap, **When** visualiza a toolbar, **Then** ve os controles organizados em grupos logicos (Zoom, Filtros, Dependencias, Acoes) com separadores visuais entre eles
2. **Given** o usuario passa o mouse sobre qualquer botao da toolbar, **When** aguarda brevemente, **Then** um tooltip descritivo aparece explicando a funcao do botao
3. **Given** o usuario visualiza a toolbar, **When** observa os botoes, **Then** todos possuem icones claros e reconheciveis sem necessidade de texto auxiliar

---

### User Story 2 - Agrupamento por Feature com Expand/Collapse (Priority: P1)

O usuario visualiza o roadmap com historias agrupadas por feature em vez de por wave. Cada feature aparece como um grupo colapsavel que mostra um resumo (nome da feature, quantidade de historias e percentual de conclusao). O usuario pode expandir uma ou mais features simultaneamente para ver as historias individuais no timeline. Com multiplas features expandidas, uma barra de scroll vertical permite navegar por todo o conteudo.

**Why this priority**: O agrupamento por feature e a mudanca estrutural mais significativa e impacta diretamente como o usuario interpreta e navega pelo roadmap.

**Independent Test**: Pode ser testado carregando o roadmap com dados que contenham multiplas features, expandindo/colapsando features e verificando a navegacao via scroll.

**Acceptance Scenarios**:

1. **Given** o roadmap esta carregado com historias de multiplas features, **When** o usuario visualiza o roadmap, **Then** as historias estao agrupadas por feature com cada grupo inicialmente colapsado
2. **Given** uma feature esta colapsada, **When** o usuario clica no cabecalho do grupo, **Then** a feature expande mostrando todas as historias individuais no timeline
3. **Given** uma feature esta expandida, **When** o usuario clica no cabecalho do grupo, **Then** a feature colapsa voltando a exibir apenas o resumo
4. **Given** multiplas features estao expandidas, **When** o conteudo excede a area visivel, **Then** uma barra de scroll vertical permite navegar por todo o roadmap
5. **Given** uma feature nao possui historias agendadas, **When** o usuario visualiza o grupo, **Then** a feature aparece com indicacao visual de que nao ha dados no timeline

---

### User Story 3 - Codigo da Historia nas Barras e Legenda Lateral (Priority: P1)

O usuario ve o codigo da historia (ex: AUTH-001) diretamente na barra do timeline do roadmap, permitindo identificacao rapida sem hover. Na coluna lateral (eixo Y / legenda), o codigo tambem aparece junto ao nome da historia, facilitando a referencia cruzada.

**Why this priority**: A identificacao rapida das historias e essencial para que o usuario navegue eficientemente pelo roadmap sem depender de tooltips.

**Independent Test**: Pode ser testado verificando visualmente que o codigo aparece nas barras do timeline e na legenda lateral para cada historia.

**Acceptance Scenarios**:

1. **Given** uma feature esta expandida mostrando historias, **When** o usuario observa as barras do timeline, **Then** cada barra exibe o codigo da historia (ex: AUTH-001) de forma legivel
2. **Given** uma feature esta expandida, **When** o usuario observa a coluna lateral, **Then** cada historia mostra seu codigo seguido do nome
3. **Given** o nome da historia e longo, **When** exibido na barra ou legenda, **Then** o codigo permanece sempre visivel e o nome e truncado conforme necessario

---

### User Story 4 - Quantidade de Historias e Percentual de Conclusao na Coluna Lateral (Priority: P2)

Na coluna lateral, cada grupo de feature exibe a quantidade total de historias e o percentual de conclusao. Isso permite ao usuario avaliar rapidamente o progresso de cada feature sem precisar expandir o grupo.

**Why this priority**: Informacao de progresso na lateral complementa a visualizacao e da contexto imediato sem interacao adicional.

**Independent Test**: Pode ser testado verificando que cada cabecalho de feature na legenda lateral exibe contagem e percentual corretos.

**Acceptance Scenarios**:

1. **Given** o roadmap esta carregado, **When** o usuario observa a coluna lateral, **Then** cada feature exibe a quantidade de historias (ex: "12 historias")
2. **Given** uma feature tem historias com status CONCLUIDO, **When** o usuario observa o cabecalho da feature, **Then** o percentual de conclusao esta visivel (ex: "75%")
3. **Given** uma feature nao tem historias concluidas, **When** o usuario observa o cabecalho, **Then** o percentual exibe "0%"
4. **Given** filtros estao ativos, **When** o usuario observa a contagem, **Then** os numeros refletem apenas as historias filtradas

---

### User Story 5 - Controles de Zoom (Priority: P2)

O usuario pode aumentar o zoom (zoom in), diminuir o zoom (zoom out) e restaurar a visualizacao padrao (fit/reset) usando botoes na toolbar. O nivel de zoom atual e indicado visualmente.

**Why this priority**: Controles de zoom sao essenciais para navegacao em roadmaps com muitas historias ou periodos longos, mas a estrutura base (agrupamento, codigos) tem prioridade.

**Independent Test**: Pode ser testado clicando nos botoes de zoom e verificando que a visualizacao muda proporcionalmente.

**Acceptance Scenarios**:

1. **Given** o roadmap esta visivel, **When** o usuario clica no botao de zoom in, **Then** o range de datas no eixo X diminui (menos dias visiveis, mais detalhe temporal)
2. **Given** o roadmap esta com zoom aplicado, **When** o usuario clica no botao de zoom out, **Then** o range de datas no eixo X aumenta (mais dias visiveis, visao mais ampla)
3. **Given** o roadmap esta com qualquer nivel de zoom, **When** o usuario clica no botao de reset/fit, **Then** o eixo X retorna ao range completo mostrando todas as datas do roadmap e a posicao de pan e resetada para o inicio
4. **Given** o usuario altera o zoom, **When** observa a toolbar, **Then** o indicador de nivel de zoom reflete o estado atual (ex: "100%", "125%")

---

### User Story 5b - Pan/Navegacao por Arrasto no Grafico (Priority: P2)

O usuario pode clicar e arrastar o grafico do roadmap para mover a visualizacao horizontalmente, usando um cursor de mao que indica claramente que a area e arrastavel. Isso e essencial quando o zoom esta aplicado e partes do diagrama ficam fora da area visivel. A navegacao vertical continua sendo feita pela scroll bar existente.

**Why this priority**: Complementa diretamente os controles de zoom — sem pan horizontal, ao dar zoom o usuario perde acesso a partes do timeline que ficam fora da viewport, tornando o zoom praticamente inutil para exploracao detalhada.

**Independent Test**: Pode ser testado abrindo o roadmap, aplicando zoom com Ctrl+Scroll ou botoes, e verificando que e possivel clicar e arrastar o grafico para revelar areas fora da viewport.

**Acceptance Scenarios**:

1. **Given** o roadmap esta aberto com zoom aplicado (>100%), **When** o usuario pressiona o botao esquerdo do mouse sobre o grafico e arrasta horizontalmente, **Then** o grafico se move na direcao horizontal do arrasto, revelando conteudo do timeline anteriormente fora da tela
2. **Given** o roadmap esta aberto, **When** o usuario passa o mouse sobre a area do grafico, **Then** o cursor muda para um icone de mao aberta (open hand), indicando que a area e arrastavel
3. **Given** o usuario esta arrastando o grafico, **When** o cursor esta em movimento de drag, **Then** o cursor muda para mao fechada (closed hand/grabbing), indicando que o arrasto esta ativo
4. **Given** o usuario esta arrastando o grafico, **When** solta o botao do mouse, **Then** o grafico permanece na nova posicao e o cursor volta para mao aberta
5. **Given** o usuario tenta arrastar alem dos limites do grafico, **When** o conteudo atinge o limite, **Then** o pan e limitado para que pelo menos uma porcao do grafico permaneca visivel
6. **Given** o roadmap esta com zoom >100% e o grafico tem foco, **When** o usuario pressiona teclas de seta esquerda/direita, **Then** o viewport se move horizontalmente como alternativa ao arrasto

---

### User Story 6 - Filtros por Feature, Componente, Responsavel e Nome (Priority: P2)

O usuario pode filtrar as historias do roadmap por feature, componente, responsavel e nome da historia. Os filtros funcionam em conjunto (AND) e o usuario pode limpar todos os filtros de uma vez. Filtros ativos sao indicados visualmente.

**Why this priority**: Filtros permitem foco em subconjuntos relevantes do roadmap, mas dependem da estrutura base estar implementada.

**Independent Test**: Pode ser testado aplicando cada filtro individualmente e em combinacao, verificando que o roadmap exibe apenas historias correspondentes.

**Acceptance Scenarios**:

1. **Given** o roadmap esta carregado, **When** o usuario seleciona uma feature no filtro, **Then** apenas historias dessa feature sao exibidas
2. **Given** o roadmap esta carregado, **When** o usuario seleciona um componente no filtro, **Then** apenas historias desse componente sao exibidas
3. **Given** o roadmap esta carregado, **When** o usuario seleciona um responsavel no filtro, **Then** apenas historias atribuidas a esse responsavel sao exibidas
4. **Given** o roadmap esta carregado, **When** o usuario digita um texto no campo de busca, **Then** apenas historias cujo nome contem o texto sao exibidas
5. **Given** filtros estao ativos, **When** o usuario clica em limpar filtros, **Then** todos os filtros sao resetados e o roadmap exibe todas as historias
6. **Given** um filtro esta ativo, **When** o usuario observa o controle do filtro, **Then** ha indicacao visual de que o filtro esta aplicado

---

### User Story 7 - Controle Visual de Dependencias (Priority: P3)

O usuario pode habilitar/desabilitar a visualizacao de setas de dependencia entre historias usando um botao toggle na toolbar. As dependencias sao exibidas como linhas conectando historias relacionadas.

**Why this priority**: Dependencias adicionam uma camada de informacao importante mas secundaria; a visualizacao base e filtros tem prioridade.

**Independent Test**: Pode ser testado ativando o toggle de dependencias e verificando que setas aparecem conectando historias com dependencias registradas.

**Acceptance Scenarios**:

1. **Given** o roadmap esta visivel, **When** o usuario ativa o toggle de dependencias, **Then** setas de conexao aparecem entre historias que possuem dependencias
2. **Given** dependencias estao visiveis, **When** o usuario desativa o toggle, **Then** as setas de dependencia desaparecem
3. **Given** dependencias estao ativas e uma historia depende de outra em feature diferente, **When** ambas features estao expandidas, **Then** a seta de dependencia conecta as duas historias visualmente
4. **Given** dependencias estao ativas e uma historia dependente esta em feature colapsada ou filtrada, **When** o usuario observa, **Then** a dependencia nao e renderizada (setas so aparecem quando ambas historias estao visiveis)

---

### Edge Cases

- O que acontece quando uma feature tem apenas uma historia? O grupo funciona normalmente com expand/collapse, exibindo "1 historia" e percentual correto.
- Como o sistema lida com historias sem feature atribuida? Historias sem feature sao agrupadas em um grupo especial "Sem feature" com o mesmo comportamento de expand/collapse.
- O que acontece quando o codigo da historia e muito longo para a barra? O codigo e sempre exibido integralmente; se a barra for muito curta, o codigo pode transbordar visualmente com truncamento.
- Como o sistema se comporta com filtro ativo e todas historias filtradas? O roadmap exibe mensagem indicando que nenhuma historia corresponde aos filtros aplicados.
- O que acontece quando o usuario redimensiona a janela? O roadmap se ajusta dinamicamente mantendo a proporcionalidade e legibilidade dos elementos.
- O que acontece quando o usuario reabre o dialogo do roadmap? Todos os grupos iniciam colapsados, o zoom reseta para 100% e a posicao de pan reseta para o inicio (sem persistencia de estado entre sessoes).
- O que acontece com setas de dependencia quando um filtro oculta uma das historias? A seta e ocultada; so sao renderizadas dependencias onde ambas historias estao visiveis.
- O que acontece quando o usuario tenta arrastar alem dos limites do grafico? O pan e limitado para que o conteudo nao desapareca completamente da tela (pelo menos uma porcao do grafico permanece visivel).
- Como o pan interage com tooltips? Tooltips continuam funcionando normalmente no hover; um clique+arrasto (drag) nao dispara tooltip.
- O que acontece ao fazer pan quando o zoom esta em 100%? O pan horizontal nao tem efeito visual pois todo o timeline ja esta visivel. A navegacao vertical continua via scroll bar existente.

## Clarifications

### Session 2026-04-05

- Q: Como o zoom deve operar com matplotlib? → A: Zoom ajusta o range de datas no eixo X (zoom in = menos dias visíveis, mais detalhe; zoom out = mais dias visíveis)
- Q: Como os grupos de feature devem ser ordenados na coluna lateral? → A: Pela data de início mais cedo entre as histórias do grupo (features que começam antes aparecem no topo)
- Q: O estado de expand/collapse e zoom deve persistir entre sessões? → A: Resetar sempre ao abrir o diálogo (todos colapsados, zoom 100%)
- Q: Qual widget usar para os filtros na toolbar? → A: QComboBox para feature/componente/responsável + QLineEdit para busca por nome (consistente com UI atual)
- Q: Como setas de dependência se comportam com filtros ativos? → A: Ocultar setas quando uma das histórias da dependência não está visível (só mostrar onde ambas estão visíveis)
- Q: Como o pan deve funcionar no gráfico? → A: Click+drag com botão esquerdo move o gráfico apenas horizontalmente (eixo X/timeline). Navegação vertical permanece via scroll bar existente. Cursor muda para mão aberta (hover) e mão fechada (arrastando). Teclas de seta esquerda/direita como alternativa. Reset de zoom também reseta posição de pan.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE agrupar historias por feature na visualizacao do roadmap, substituindo o agrupamento atual por wave
- **FR-002**: O sistema DEVE permitir expandir e colapsar cada grupo de feature individualmente, clicando no cabecalho do grupo
- **FR-003**: O sistema DEVE suportar multiplas features expandidas simultaneamente com barra de scroll vertical para navegacao
- **FR-004**: O sistema DEVE exibir o codigo da historia (ex: AUTH-001) diretamente na barra do timeline de cada historia
- **FR-005**: O sistema DEVE exibir o codigo da historia na coluna lateral (legenda/eixo Y) junto ao nome da historia
- **FR-006**: O sistema DEVE exibir a quantidade total de historias para cada feature na coluna lateral
- **FR-007**: O sistema DEVE exibir o percentual de conclusao (historias com status CONCLUIDO / total) para cada feature na coluna lateral
- **FR-008**: A toolbar DEVE organizar os controles em grupos logicos separados visualmente: Zoom, Filtros, Dependencias, Acoes
- **FR-009**: Todos os botoes da toolbar DEVEM possuir icones reconheciveis e tooltips descritivos
- **FR-010**: O sistema DEVE fornecer botoes de zoom in, zoom out e reset (visualizacao padrao) na toolbar; zoom opera sobre o range de datas do eixo X
- **FR-011**: O sistema DEVE exibir o nivel de zoom atual na toolbar
- **FR-012**: O sistema DEVE permitir filtrar historias por feature (QComboBox), componente (QComboBox), responsavel (QComboBox) e nome da historia (QLineEdit com busca textual)
- **FR-013**: Os filtros DEVEM operar em conjunto com logica AND
- **FR-014**: O sistema DEVE fornecer botao para limpar todos os filtros ativos
- **FR-015**: O sistema DEVE indicar visualmente quais filtros estao ativos
- **FR-016**: O sistema DEVE fornecer toggle para habilitar/desabilitar visualizacao de dependencias entre historias
- **FR-017**: Historias sem feature atribuida DEVEM ser agrupadas em grupo especial "Sem feature"
- **FR-018**: Quando filtros estao ativos, a contagem de historias e percentual DEVEM refletir apenas historias filtradas
- **FR-019**: Os grupos de feature DEVEM ser ordenados pela data de inicio mais cedo entre as historias do grupo (features que comecam antes aparecem no topo)
- **FR-020**: Ao abrir o dialogo do roadmap, todos os grupos DEVEM iniciar colapsados e o zoom DEVE iniciar em 100% (sem persistencia de estado entre sessoes)
- **FR-021**: Setas de dependencia so DEVEM ser renderizadas quando ambas historias (origem e destino) estao visiveis (nao filtradas e em grupos expandidos)
- **FR-022**: O sistema DEVE permitir que o usuario clique e arraste o grafico do roadmap para mover a visualizacao horizontalmente (pan/drag). A navegacao vertical permanece via scroll bar existente
- **FR-023**: O cursor DEVE mudar para mao aberta (open hand) ao passar sobre a area do grafico, indicando que e arrastavel
- **FR-024**: O cursor DEVE mudar para mao fechada (closed hand/grabbing) durante o arrasto ativo
- **FR-025**: O pan DEVE ser limitado aos limites do conteudo do grafico, impedindo que o conteudo desapareca completamente da viewport
- **FR-026**: O sistema DEVE suportar navegacao horizontal via teclas de seta esquerda/direita quando o grafico tem foco, como alternativa ao arrasto
- **FR-027**: O pan NAO DEVE interferir com funcionalidades existentes: zoom (Ctrl+Scroll), tooltips (hover), clique em barras e toggle de dependencias
- **FR-028**: O botao de reset/fit (FR-010) DEVE tambem resetar a posicao de pan para o estado inicial

### Key Entities

- **Feature Group**: Representa um agrupamento de historias por feature no roadmap, com estado de expand/collapse, contagem de historias e percentual de conclusao. Ordenado pela data de inicio mais cedo entre suas historias
- **Story Bar**: Representacao visual de uma historia no timeline, contendo codigo identificador, cor por status e indicacao de progresso
- **Toolbar Group**: Agrupamento logico de controles na toolbar (Zoom, Filtros, Dependencias, Acoes) com separadores visuais
- **Zoom State**: Nivel de zoom atual que controla o range de datas visivel no eixo X. Sempre inicia em 100% (range completo) ao abrir o dialogo

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuario consegue identificar qualquer historia no roadmap pelo codigo sem precisar de hover em menos de 3 segundos
- **SC-002**: O usuario consegue expandir/colapsar uma feature com um unico clique
- **SC-003**: O usuario consegue avaliar o progresso de cada feature (percentual e contagem) sem expandir o grupo
- **SC-004**: Todos os botoes da toolbar exibem tooltip ao hover em ate 500ms
- **SC-005**: O usuario consegue aplicar qualquer combinacao de filtros e limpar todos em ate 2 cliques
- **SC-006**: O roadmap com 50+ historias e 5+ features expandidas simultaneamente permanece navegavel com scroll fluido
- **SC-007**: O usuario consegue alternar entre zoom in, zoom out e reset sem perder a orientacao no timeline
- **SC-008**: O usuario consegue visualizar qualquer area horizontal do timeline em qualquer nivel de zoom atraves de pan (arrasto), sem perda de acesso a conteudo
- **SC-009**: A navegacao por arrasto responde em tempo real ao movimento do mouse, sem atraso perceptivel
- **SC-010**: O cursor visual muda corretamente entre mao aberta e mao fechada em 100% das interacoes de pan

## Assumptions

- O sistema ja possui dados de features, historias e dependencias carregados via use cases existentes (sem alteracoes de banco de dados)
- O codigo da historia segue o formato COMPONENTE-NNN (ex: AUTH-001) e e unico
- O percentual de conclusao e calculado como: (historias com status CONCLUIDO / total de historias) * 100
- A mudanca de agrupamento de wave para feature e permanente nesta refatoracao
- Os filtros existentes de wave e status sao substituidos pelo novo conjunto de filtros (feature, componente, responsavel, nome)
- O design segue o design system existente (DESIGN_TOKENS, STATUS_PALETTE) sem introducao de novos tokens visuais
- O cursor de mao aberta/fechada usa cursores padrao do sistema operacional (OpenHandCursor e ClosedHandCursor)
- O pan por arrasto usa o botao esquerdo do mouse; botao do meio e direito mantem comportamento atual
- O incremento de scroll horizontal via teclas de seta e proporcional a largura visivel da viewport (ex: 10% da largura visivel por pressionamento)
