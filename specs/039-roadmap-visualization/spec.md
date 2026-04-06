# Feature Specification: Visualizacao de Roadmap

**Feature Branch**: `039-roadmap-visualization`
**Created**: 2026-04-02
**Status**: Draft
**Input**: User description: "Visualizacao de Roadmap — tela fullscreen com timeline Gantt-like para acompanhar progresso do backlog apos planejamento"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar Roadmap com Timeline (Priority: P1)

O gestor de projeto finaliza o planejamento (scheduling + alocacao) e deseja ter uma visao panoramica do cronograma. Ele aciona o botao/menu de roadmap na tela principal e o sistema abre uma tela fullscreen exibindo um grafico de timeline (Gantt-like) com barras horizontais representando cada historia posicionada no eixo temporal (start_date a end_date). As historias sao agrupadas por feature, e o gestor consegue identificar rapidamente a distribuicao temporal de todo o backlog.

**Why this priority**: Esta e a funcionalidade core da feature — sem a timeline com as barras posicionadas corretamente, nenhuma outra funcionalidade tem valor. E o MVP minimo que ja entrega visibilidade do cronograma.

**Independent Test**: Pode ser testado abrindo a tela de roadmap com um backlog que tenha historias com datas calculadas e verificando que todas as barras aparecem posicionadas corretamente no eixo temporal.

**Acceptance Scenarios**:

1. **Given** um backlog com historias que possuem start_date e end_date calculados, **When** o gestor aciona a visualizacao de roadmap, **Then** o sistema abre uma tela fullscreen com um grafico de timeline exibindo barras horizontais para cada historia posicionada corretamente no tempo
2. **Given** um backlog sem historias com datas calculadas (start_date/end_date vazios), **When** o gestor tenta abrir o roadmap, **Then** o sistema exibe mensagem orientando a executar o planejamento primeiro
3. **Given** a tela de roadmap aberta, **When** o gestor fecha a tela, **Then** o sistema retorna a tela principal

---

### User Story 2 - Agrupamento e Progresso por Feature/Componente (Priority: P2)

O gestor visualiza o roadmap e deseja alternar o modo de agrupamento das historias entre "por Feature" e "por Componente". Ao alternar, as historias sao reorganizadas nos respectivos grupos, e cada grupo exibe um indicador de percentual de conclusao no cabecalho (proporcao de historias CONCLUIDO sobre o total).

**Why this priority**: O agrupamento e o indicador de progresso transformam uma simples timeline em uma ferramenta de gestao — permitem ao gestor entender rapidamente o status de cada area do projeto.

**Independent Test**: Pode ser testado alternando entre os modos de agrupamento e verificando que os grupos mudam corretamente e que o percentual de conclusao reflete a proporcao real de historias concluidas.

**Acceptance Scenarios**:

1. **Given** o roadmap aberto com historias pertencentes a multiplas features, **When** o gestor seleciona agrupamento "por Feature", **Then** as historias sao organizadas em grupos por feature com cabecalho exibindo o nome da feature e percentual de conclusao
2. **Given** o roadmap aberto com agrupamento por feature, **When** o gestor alterna para "por Componente", **Then** as historias sao reorganizadas em grupos por componente com percentual de conclusao atualizado
3. **Given** uma feature com 4 historias (2 CONCLUIDO, 2 em outros status), **When** o gestor visualiza o grupo, **Then** o indicador exibe 50% de conclusao

---

### User Story 3 - Tooltip Rico com Detalhes da Historia (Priority: P3)

O gestor passa o mouse sobre uma barra de historia na timeline e visualiza um tooltip rico contendo: desenvolvedor alocado, story points, status, dependencias, datas (inicio/fim), duracao e componente. Isso permite obter detalhes sem sair da visao panoramica.

**Why this priority**: O tooltip e essencial para a usabilidade — permite consultar detalhes sem mudar de contexto. Porem, o roadmap ja funciona sem ele (gestor pode consultar detalhes na tela principal).

**Independent Test**: Pode ser testado passando o mouse sobre diferentes barras de historia e verificando que todas as informacoes esperadas sao exibidas corretamente no tooltip.

**Acceptance Scenarios**:

1. **Given** o roadmap aberto com historias exibidas, **When** o gestor passa o mouse sobre uma barra de historia, **Then** um tooltip aparece exibindo: desenvolvedor alocado, story points, status, dependencias, datas de inicio e fim, duracao em dias e componente
2. **Given** uma historia sem desenvolvedor alocado, **When** o gestor passa o mouse sobre a barra, **Then** o tooltip exibe "Nao alocado" no campo de desenvolvedor
3. **Given** uma historia sem dependencias, **When** o gestor passa o mouse sobre a barra, **Then** o tooltip exibe "Sem dependencias" no campo correspondente

---

### User Story 4 - Indicadores Visuais Opcionais (Priority: P4)

O gestor ativa/desativa indicadores visuais opcionais na timeline: itens em atraso (historias cuja end_date e anterior a data atual e status diferente de CONCLUIDO), criticidade de dependencias (historias bloqueadoras em status IMPEDIDO ou em atraso) e datas/deadlines. Os toggles de cada indicador sao independentes e as preferencias sao persistidas entre sessoes.

**Why this priority**: Os indicadores enriquecem a visualizacao mas sao aditivos — o roadmap base ja funciona sem eles. A persistencia de preferencias e um diferencial de usabilidade.

**Independent Test**: Pode ser testado ativando/desativando cada indicador e verificando que a representacao visual muda conforme esperado, e que ao reabrir o roadmap as preferencias sao mantidas.

**Acceptance Scenarios**:

1. **Given** o roadmap aberto com historias em atraso, **When** o gestor ativa o indicador de "atraso", **Then** as historias em atraso sao destacadas visualmente (cor/icone diferenciado)
2. **Given** o indicador de "criticidade de dependencias" ativado, **When** existem historias bloqueadoras com status IMPEDIDO, **Then** essas historias sao destacadas visualmente
3. **Given** o gestor desativa o indicador de "deadlines", **When** a tela e atualizada, **Then** as marcacoes de deadline desaparecem da timeline
4. **Given** o gestor ativa indicadores de atraso e dependencias, **When** fecha e reabre o roadmap, **Then** os indicadores permanecem ativados conforme a ultima configuracao

---

### Edge Cases

- O que acontece quando nao existem historias com datas calculadas? O sistema exibe mensagem orientando a executar o planejamento primeiro e nao abre a tela de roadmap.
- O que acontece quando todas as historias de um grupo estao concluidas? O indicador de progresso exibe 100% e o grupo pode ser visualmente diferenciado como completo.
- O que acontece quando um grupo tem zero historias? O grupo nao e exibido na timeline.
- Como o sistema se comporta com backlogs muito grandes (200+ historias)? O layout deve permanecer legivel e a renderizacao deve ocorrer em tempo aceitavel (menos de 3 segundos).
- O que acontece quando uma historia nao tem feature ou componente associado? A historia e agrupada em um grupo "Sem classificacao".
- O que acontece quando a janela e redimensionada? O grafico se ajusta responsivamente ao tamanho disponivel.

## Clarifications

### Session 2026-04-02

- Q: Como o usuário navega a timeline quando o backlog é extenso? → A: Scroll horizontal + zoom via Ctrl+scroll wheel (mudança de granularidade temporal)
- Q: Como as barras de história são coloridas na timeline? → A: Cor por status (verde=concluído, azul=em andamento, vermelho=impedido, cinza=pendente)
- Q: Qual abordagem de renderização para o gráfico Gantt? → A: QGraphicsView + QGraphicsScene (itens gráficos gerenciados pelo Qt)
- Q: As dependências entre histórias devem ser visualizadas como linhas/setas na timeline? → A: Apenas no tooltip (sem linhas/setas na timeline)
- Q: O que significa "tela fullscreen" para o roadmap? → A: QDialog maximizado (janela modal separada sobre a principal)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE exibir um botao/menu na tela principal para abrir a visualizacao de roadmap
- **FR-002**: Sistema DEVE validar que existem historias com start_date e end_date preenchidos antes de abrir o roadmap; caso contrario, exibir mensagem informativa
- **FR-003**: Sistema DEVE abrir a tela de roadmap como QDialog maximizado (janela modal separada sobre a principal)
- **FR-004**: Sistema DEVE renderizar um grafico de timeline (Gantt-like) com eixo horizontal representando o tempo, utilizando QGraphicsView + QGraphicsScene
- **FR-005**: Sistema DEVE exibir cada historia como uma barra horizontal posicionada entre start_date e end_date, colorida por status (verde=concluído, azul=em andamento, vermelho=impedido, cinza=pendente)
- **FR-006**: Sistema DEVE agrupar historias por feature (modo padrao) com opcao de alternar para agrupamento por componente
- **FR-007**: Sistema DEVE exibir no cabecalho de cada grupo o nome e o percentual de conclusao (historias CONCLUIDO / total de historias do grupo)
- **FR-008**: Sistema DEVE exibir tooltip rico ao hover sobre uma barra de historia contendo: desenvolvedor alocado, story points, status, dependencias, datas inicio/fim, duracao e componente
- **FR-009**: Sistema DEVE oferecer toggles independentes para indicadores visuais: atraso, criticidade de dependencias, datas/deadlines
- **FR-010**: Sistema DEVE destacar visualmente historias em atraso (end_date anterior a data atual E status diferente de CONCLUIDO) quando o indicador estiver ativo
- **FR-011**: Sistema DEVE destacar visualmente historias bloqueadoras (que possuem dependentes) com status IMPEDIDO ou em atraso quando o indicador de criticidade estiver ativo
- **FR-012**: Sistema DEVE persistir as preferencias de indicadores visuais entre sessoes
- **FR-013**: Sistema DEVE permitir ao gestor fechar a tela de roadmap e retornar a tela principal
- **FR-014**: Sistema DEVE respeitar o design system existente (cores, tipografia, tokens de tema)
- **FR-015**: Sistema DEVE manter o layout legivel com backlogs de ate 200 historias
- **FR-016**: Sistema DEVE suportar scroll horizontal na timeline e zoom via Ctrl+scroll wheel para mudanca de granularidade temporal
- **FR-017**: Sistema DEVE exibir dependencias entre historias apenas no tooltip (sem linhas/setas visuais na timeline)

### Key Entities

- **Historia (Story)**: Unidade de trabalho com atributos relevantes para o roadmap: titulo, start_date, end_date, status, story_points, desenvolvedor alocado, feature, componente, dependencias
- **Feature**: Agrupamento logico de historias por funcionalidade; possui nome e conjunto de historias associadas
- **Componente**: Agrupamento logico de historias por area tecnica/modulo; possui nome e conjunto de historias associadas
- **Grupo de Roadmap**: Representacao visual de um agrupamento (feature ou componente) com nome, lista de historias e percentual de conclusao calculado

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Gestor consegue abrir o roadmap e visualizar todas as historias com datas em menos de 3 segundos
- **SC-002**: 100% das historias com datas calculadas aparecem posicionadas corretamente na timeline
- **SC-003**: Percentual de conclusao exibido corresponde exatamente a proporcao de historias CONCLUIDO por grupo
- **SC-004**: Indicadores visuais de atraso e dependencia sao visiveis sem necessidade de interacao adicional (quando ativados)
- **SC-005**: Tooltip exibe todas as 7 informacoes relevantes da historia (desenvolvedor, SP, status, dependencias, datas, duracao, componente) ao hover
- **SC-006**: Preferencias de indicadores visuais persistem entre sessoes (fechar e reabrir o roadmap mantem os toggles no estado anterior)
- **SC-007**: O layout permanece legivel e navegavel com backlogs de ate 200 historias

## Assumptions

- O planejamento (scheduling + alocacao) ja esta implementado e preenche start_date e end_date nas historias
- Cada historia pertence a pelo menos uma feature ou componente (historias sem classificacao serao agrupadas em "Sem classificacao")
- O status CONCLUIDO e o unico status que indica conclusao para fins do calculo de progresso
- O status IMPEDIDO e um status valido existente no sistema
- O design system do projeto (cores, tipografia, tokens) ja esta definido e disponivel para uso
- A tela de roadmap e somente leitura — nenhuma edicao de dados ocorre nela
