# Feature Specification: Refatoracao do Roadmap Visualization

**Feature Branch**: `040-roadmap-refactor`
**Created**: 2026-04-02
**Status**: Draft
**Input**: User description: "Refatoracao completa do roadmap de visualizacao para resolver problemas de performance, completude e design, adotando matplotlib como engine de renderizacao"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar todas as historias no roadmap (Priority: P1)

Como Gerente de Projeto, quero abrir o roadmap e ver TODAS as historias que possuem datas calculadas (start_date e end_date), agrupadas por Feature, para ter uma visao completa do cronograma do projeto sem historias faltantes.

**Why this priority**: Esta e a funcionalidade central do roadmap. O bug atual que omite historias invalida completamente a utilidade da visualizacao. Sem isso, o roadmap nao cumpre seu proposito basico.

**Independent Test**: Pode ser testado criando um conjunto de historias com datas calculadas e verificando que 100% delas aparecem no grafico renderizado.

**Acceptance Scenarios**:

1. **Given** existem 50 historias com start_date e end_date calculados no backlog, **When** o Gerente de Projeto abre o roadmap, **Then** todas as 50 historias aparecem no grafico de timeline agrupadas por Feature com barras coloridas por status.
2. **Given** existem historias sem feature atribuida, **When** o roadmap e renderizado, **Then** essas historias aparecem sob o grupo "Sem classificacao".
3. **Given** existem historias com diferentes status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO), **When** o roadmap e renderizado, **Then** cada barra usa a cor correspondente do STATUS_PALETTE do design system.
4. **Given** nao existem historias com datas calculadas, **When** o Gerente de Projeto abre o roadmap, **Then** o sistema exibe uma mensagem informativa indicando que nao ha dados para visualizar.

---

### User Story 2 - Carregamento assincrono sem travamento da interface (Priority: P1)

Como Gerente de Projeto, quero que o carregamento de dados do roadmap seja totalmente assincrono para que a interface nunca congele ou trave durante o carregamento.

**Why this priority**: O travamento da interface e um problema critico de usabilidade que impede o uso produtivo da ferramenta. E co-prioritario com a completude dos dados.

**Independent Test**: Pode ser testado verificando que a interface permanece responsiva durante o carregamento de dados e que um indicador de progresso e exibido.

**Acceptance Scenarios**:

1. **Given** o roadmap esta sendo aberto, **When** os dados estao sendo carregados, **Then** um indicador de progresso e exibido e a interface permanece responsiva (nao congela).
2. **Given** o carregamento esta em andamento, **When** o usuario interage com a dialog (mover, redimensionar), **Then** a interface responde normalmente sem travamento.
3. **Given** o carregamento de dados falha (erro de I/O), **When** o erro ocorre, **Then** o sistema exibe uma mensagem de erro amigavel sem travar.

---

### User Story 3 - Renderizacao profissional com matplotlib (Priority: P2)

Como Gerente de Projeto, quero que o roadmap tenha um visual profissional e agradavel, renderizado com matplotlib, para que eu possa usar a visualizacao em apresentacoes e reunioes de acompanhamento.

**Why this priority**: O redesign visual e importante para a adocao da ferramenta, mas depende da completude dos dados (P1) para ter valor.

**Independent Test**: Pode ser testado verificando que o grafico matplotlib e renderizado corretamente dentro da dialog, com barras de Gantt, labels legiveis e visual limpo.

**Acceptance Scenarios**:

1. **Given** os dados foram carregados com sucesso, **When** o roadmap e renderizado, **Then** o grafico exibe um timeline estilo Gantt com barras horizontais para cada historia.
2. **Given** historias estao agrupadas por Feature, **When** o roadmap e exibido, **Then** cada grupo mostra o nome da Feature e o percentual de conclusao (ex: "Feature X - 75%").
3. **Given** o roadmap e renderizado, **When** o Gerente de Projeto visualiza o grafico, **Then** as labels sao legiveis, as cores sao distintas e o layout e limpo e profissional.

---

### User Story 4 - Alternar agrupamento entre Feature e Componente (Priority: P2)

Como Gerente de Projeto, quero alternar o agrupamento das historias entre Feature e Componente para analisar o roadmap sob diferentes perspectivas.

**Why this priority**: O agrupamento e o unico controle de filtragem necessario, complementando a visualizacao principal.

**Independent Test**: Pode ser testado alternando o controle de agrupamento e verificando que as historias se reorganizam corretamente.

**Acceptance Scenarios**:

1. **Given** o roadmap esta exibindo historias agrupadas por Feature, **When** o Gerente de Projeto seleciona "Componente" na toolbar, **Then** as historias se reorganizam por Componente com percentuais recalculados.
2. **Given** o agrupamento esta em "Componente", **When** o Gerente de Projeto seleciona "Feature", **Then** as historias voltam ao agrupamento por Feature.
3. **Given** existem historias sem componente atribuido, **When** o agrupamento por Componente esta ativo, **Then** essas historias aparecem sob "Sem classificacao".

---

### User Story 5 - Navegacao no grafico (scroll e zoom) (Priority: P3)

Como Gerente de Projeto, quero navegar pelo grafico usando scroll horizontal/vertical e zoom para explorar diferentes partes do roadmap em detalhe.

**Why this priority**: Navegacao melhora a usabilidade mas nao e essencial para a funcionalidade basica do roadmap.

**Independent Test**: Pode ser testado verificando que scroll e zoom funcionam corretamente no grafico renderizado.

**Acceptance Scenarios**:

1. **Given** o roadmap tem mais historias do que cabem na tela, **When** o Gerente de Projeto faz scroll vertical, **Then** o grafico rola para revelar historias adicionais.
2. **Given** o timeline e mais longo que a area visivel, **When** o Gerente de Projeto faz scroll horizontal, **Then** o grafico rola para revelar periodos anteriores ou futuros.
3. **Given** o roadmap esta exibido, **When** o Gerente de Projeto faz zoom in/out, **Then** o grafico ajusta a escala mantendo a legibilidade.

---

### User Story 6 - Tooltip com detalhes da historia (Priority: P3)

Como Gerente de Projeto, quero ver detalhes de uma historia ao passar o mouse sobre sua barra no grafico para obter informacoes rapidas sem sair da visualizacao.

**Why this priority**: Tooltips sao uma funcionalidade de conveniencia que agrega valor mas nao e critica para o uso basico.

**Independent Test**: Pode ser testado passando o mouse sobre barras e verificando que o tooltip exibe as informacoes corretas.

**Acceptance Scenarios**:

1. **Given** o roadmap esta renderizado, **When** o Gerente de Projeto passa o mouse sobre uma barra de historia, **Then** um tooltip exibe o nome da historia, status, data de inicio e data de fim.
2. **Given** o tooltip esta visivel, **When** o mouse sai da barra, **Then** o tooltip desaparece.

---

### Edge Cases

- O que acontece quando existem centenas de historias (200+)? O grafico deve renderizar em menos de 3 segundos sem comprometer a usabilidade.
- O que acontece quando todas as historias pertencem a uma unica Feature? O roadmap exibe um unico grupo com todas as barras.
- O que acontece quando uma historia tem start_date igual a end_date? A barra deve ter uma largura minima visivel para nao desaparecer.
- O que acontece quando historias tem periodos muito distantes no tempo? O scroll horizontal permite navegar entre os periodos.
- O que acontece quando o usuario redimensiona a janela? O grafico se ajusta ao novo tamanho mantendo proporcoes.

## Clarifications

### Session 2026-04-02

- Q: Qual criterio define "conclusao" para o percentual de conclusao dos grupos? → A: Apenas status CONCLUIDO conta como completo.
- Q: A dialog do roadmap deve ser modal ou modeless? → A: Modal — bloqueia a janela principal.
- Q: Qual mecanismo de interacao para zoom no grafico? → A: Ctrl+scroll do mouse + botoes (+/-) na toolbar.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE exibir TODAS as historias que possuem start_date e end_date calculados no roadmap, sem omitir nenhuma.
- **FR-002**: O sistema DEVE renderizar o roadmap como um grafico de timeline estilo Gantt usando matplotlib embarcado na dialog.
- **FR-003**: O sistema DEVE agrupar historias por Feature como padrao, exibindo o nome do grupo e percentual de conclusao. O percentual e calculado como (historias com status CONCLUIDO / total de historias do grupo) * 100.
- **FR-004**: O sistema DEVE permitir alternar o agrupamento entre Feature e Componente via controle na toolbar.
- **FR-005**: Historias sem feature ou componente atribuido DEVEM ser agrupadas sob "Sem classificacao".
- **FR-006**: As barras DEVEM usar cores do STATUS_PALETTE do design system (BACKLOG=cinza, EXECUCAO=azul, TESTES=amarelo, CONCLUIDO=verde, IMPEDIDO=vermelho).
- **FR-007**: O carregamento de dados DEVE ser 100% assincrono, sem bloquear a interface em nenhum momento.
- **FR-008**: O sistema DEVE exibir um indicador de progresso durante o carregamento de dados.
- **FR-009**: O sistema DEVE suportar scroll horizontal e vertical para navegacao no grafico.
- **FR-010**: O sistema DEVE suportar zoom in/out no grafico via Ctrl+scroll do mouse e botoes (+/-) na toolbar.
- **FR-011**: O sistema DEVE exibir tooltip com nome, status, data de inicio e data de fim ao passar o mouse sobre uma barra.
- **FR-012**: A dialog DEVE abrir maximizada e ser modal (bloqueia interacao com a janela principal).
- **FR-013**: O sistema DEVE remover todos os filtros de indicadores visuais (overdue, critical deps, deadlines) da implementacao anterior.
- **FR-014**: O sistema DEVE remover a persistencia de preferencias de indicadores via QSettings.
- **FR-015**: O sistema DEVE exibir uma mensagem informativa quando nao existem historias com datas calculadas.

### Key Entities

- **Historia (Story)**: Unidade de trabalho com nome, status, start_date, end_date, feature associada e componente associado. Representada como barra horizontal no grafico.
- **Feature**: Agrupamento logico de historias por funcionalidade. Exibido como grupo com nome e percentual de conclusao.
- **Componente**: Agrupamento logico de historias por area tecnica. Alternativa de agrupamento a Feature.
- **Grupo de Visualizacao**: Agrupamento dinamico (Feature ou Componente) que organiza as barras no grafico, exibindo nome e percentual de conclusao.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das historias com datas calculadas aparecem no roadmap — zero historias omitidas em qualquer cenario.
- **SC-002**: A interface permanece responsiva durante o carregamento de dados — nenhum congelamento ou travamento perceptivel pelo usuario.
- **SC-003**: O roadmap renderiza 200+ historias em menos de 3 segundos.
- **SC-004**: O agrupamento por Feature e Componente funciona corretamente com percentual de conclusao calculado para cada grupo.
- **SC-005**: Todos os testes unitarios existentes sao atualizados e passam com sucesso.
- **SC-006**: A quantidade de classes e estados na implementacao e menor que a versao anterior, resultando em codigo mais simples e manutenivel.
- **SC-007**: O visual do roadmap e profissional e adequado para apresentacoes, conforme avaliacao do usuario.

## Assumptions

- O STATUS_PALETTE com as cores por status ja existe no design system do projeto e sera reutilizado.
- Os use cases existentes (ListStoriesUseCase, ListFeaturesUseCase) fornecem todos os dados necessarios sem modificacao.
- matplotlib e uma dependencia aceitavel para o projeto e sera adicionada ao pyproject.toml.
- A dialog do roadmap sera acessivel via menu e atalho Ctrl+Shift+R, mantendo o ponto de entrada existente.
- A refatoracao substitui completamente a implementacao atual baseada em QGraphicsView.

## Dependencies

- ListStoriesUseCase e ListFeaturesUseCase existentes (sem alteracoes).
- STATUS_PALETTE do design system existente.
- Biblioteca matplotlib (nova dependencia).
- PySide6 e qasync (dependencias existentes).

## Out of Scope

- Adicao de novos filtros (por developer, status, sprint, etc.).
- Exportacao do roadmap como imagem ou PDF.
- Drag-and-drop ou edicao de historias diretamente no roadmap.
- Linhas de dependencia entre historias.
- Novos indicadores visuais (overdue, critical deps, deadlines).
- Alteracoes no schema do banco de dados.
- Alteracoes nos use cases existentes.
