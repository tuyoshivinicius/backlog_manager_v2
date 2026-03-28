# Feature Specification: EP-017 Design System e Fundacao Visual

**Feature Branch**: `017-ep017-design-system`
**Created**: 2026-03-27
**Status**: Draft
**Input**: Prompt de especificacao tecnica `docs/prompts/specs/prompt_017.md`

## Clarifications

### Session 2026-03-27

- Q: O que esta explicitamente fora de escopo deste epic? → A: Dark mode, animations, and custom component creation are out of scope.
- Q: Como erros de tema/styling devem ser tratados? → A: Log error to stderr/console and proceed with fallback styling.
- Q: Os valores de status sao exatamente os enum values do banco? → A: Sim, sao valores enum exatos (sem mapeamento).
- Q: Icones devem ser carregados eager ou lazy? → A: Eager loading at startup (all 16 icons pre-loaded).
- Q: Onde deve ficar o arquivo stylesheet.qss? → A: Same directory as theme.py (e.g., src/ui/theme/).

## Out of Scope

- **Dark Mode / Tema Alternativo**: Este epic estabelece apenas o tema light padrao. Suporte a dark mode sera considerado em epic futuro.
- **Animacoes e Transicoes**: Efeitos de hover animados, transicoes de estado, ou micro-interacoes nao fazem parte deste escopo.
- **Criacao de Componentes Custom**: Este epic utiliza widgets Qt nativos estilizados. Componentes custom (ex: QWidget subclasses com paint personalizado) estao fora de escopo.

## User Scenarios & Testing

### User Story 1 - Aplicacao Visual Automatica (Priority: P1)

O desenvolvedor inicia a aplicacao e todos os widgets (toolbar, tabela, dialogs, botoes, campos de entrada) recebem estilizacao visual moderna e consistente automaticamente, sem necessidade de configuracao manual.

**Why this priority**: Esta e a fundacao visual de toda a aplicacao. Sem esta story, nenhuma outra estilizacao pode ser aplicada. E o prerequisito para todas as demais funcionalidades visuais.

**Independent Test**: Pode ser testada iniciando a aplicacao e verificando visualmente que todos os widgets possuem estilizacao diferente do padrao Qt nativo (cores, bordas, fontes).

**Acceptance Scenarios**:

1. **Given** a aplicacao nao foi iniciada, **When** o usuario inicia o Backlog Manager, **Then** todos os widgets exibem estilizacao definida no design system (cores, fontes, espacamentos consistentes).
2. **Given** stylesheet.qss esta carregado, **When** inspeciono qualquer widget visivel, **Then** nenhum widget exibe estilo padrao Qt (cinza nativo do Windows).
3. **Given** theme.py contem 30+ tokens de cor, **When** executo apply_theme() com um template QSS, **Then** todos os placeholders @var sao substituidos por valores hex correspondentes.

---

### User Story 2 - Badges de Status com Acessibilidade (Priority: P2)

O usuario visualiza na tabela de backlog o status de cada historia com badges coloridos em formato pill, contendo indicadores nao-cromaticos (simbolos) que permitem identificacao mesmo para usuarios daltonicos.

**Why this priority**: Os badges de status sao o elemento visual mais frequentemente consultado na tabela de backlog. A acessibilidade e mandatoria conforme RNF-USAB-003.

**Independent Test**: Pode ser testada verificando que o StatusBadgeDelegate renderiza badges com cores e simbolos corretos para cada status.

**Acceptance Scenarios**:

1. **Given** uma historia com status BACKLOG, **When** a celula de status e renderizada, **Then** exibe badge pill com prefixo "●", fundo cinza (#E5E5E5), texto escuro (#525252).
2. **Given** uma historia com status CONCLUIDO, **When** a celula de status e renderizada, **Then** exibe badge pill com prefixo "✓", fundo verde claro (#DDF3E4), texto verde escuro (#18794E).
3. **Given** todas as combinacoes de cor texto/fundo de badges, **When** calculo o ratio de contraste, **Then** todas as combinacoes possuem contraste >= 4.5:1 (WCAG AA).

---

### User Story 3 - IDs em Fonte Monospace (Priority: P3)

O usuario visualiza os IDs das historias (ex: CORE-001, UI-042) em fonte monospace para facilitar a leitura e alinhamento visual na tabela.

**Why this priority**: IDs em monospace melhoram a legibilidade e sao uma convencao comum em ferramentas de desenvolvimento.

**Independent Test**: Pode ser testada verificando que o MonospaceDelegate aplica familia de fonte monospace correta.

**Acceptance Scenarios**:

1. **Given** uma historia com ID "CORE-001", **When** a celula de ID e renderizada, **Then** o texto e exibido em fonte JetBrains Mono ou fallback Consolas.
2. **Given** MonospaceDelegate configurado, **When** verifico a familia de fonte, **Then** utiliza fallback chain "JetBrains Mono", "Cascadia Code", "Consolas".

---

### User Story 4 - Focus Ring e Navegacao por Teclado (Priority: P3)

O usuario navega pela interface usando Tab/Shift+Tab e visualiza um indicador de foco claro (border 2px solid) em cada widget interativo.

**Why this priority**: Navegacao por teclado e requisito de acessibilidade (RNF-USAB-003).

**Independent Test**: Pode ser testada navegando por Tab entre widgets e verificando visualmente o focus ring.

**Acceptance Scenarios**:

1. **Given** foco em um QPushButton, **When** pressiono Tab, **Then** o proximo widget recebe foco e exibe focus ring visivel (border 2px solid @primary).
2. **Given** foco em QLineEdit, **When** observo o widget, **Then** exibe borda destacada diferenciada do estado normal.

---

### User Story 5 - Biblioteca de Icones SVG (Priority: P2)

O sistema disponibiliza 16 icones SVG Phosphor Icons em 16x16px, carregaveis via QIcon para uso em toolbar e menus.

**Why this priority**: Icones sao essenciais para identificacao rapida de acoes na toolbar.

**Independent Test**: Pode ser testada carregando cada arquivo SVG via QIcon e verificando renderizacao em 16x16px.

**Acceptance Scenarios**:

1. **Given** arquivo plus.svg em assets/icons/, **When** carrego via QIcon, **Then** icone renderiza corretamente em 16x16px sem distorcao.
2. **Given** todos os 16 arquivos SVG no diretorio assets/icons/, **When** listo o conteudo, **Then** encontro: plus.svg, pencil-simple.svg, trash.svg, arrow-up.svg, arrow-down.svg, users.svg, package.svg, gear.svg, calendar-check.svg, shuffle.svg, download-simple.svg, upload-simple.svg, copy.svg, warning-triangle.svg, link.svg, x.svg.

---

### Edge Cases

- **Fonte nao instalada**: Se Inter ou JetBrains Mono nao estiverem instaladas, o sistema deve usar fallback chain nativo (Segoe UI, Consolas).
- **Alto DPI (125%, 150%)**: SVGs devem renderizar sem distorcao em diferentes escalas de DPI.
- **Placeholder nao encontrado (desenvolvimento)**: Se apply_theme() encontrar placeholder @var nao definido em theme.py durante testes, o teste deve falhar indicando qual placeholder esta faltando. Em producao, o placeholder e mantido literal e um WARNING e logado.
- **QSS com valores hardcoded**: Se stylesheet.qss contiver valores hex literais (nao placeholders), validacao em testes deve falhar.
- **Erro de tema/styling (producao)**: Se apply_theme() falhar por qualquer razao (arquivo QSS ausente, erro de leitura), o sistema deve logar o erro em stderr/console e prosseguir com styling nativo do Qt (sem stylesheet), sem interromper a inicializacao da aplicacao.

## Requirements

### Functional Requirements

- **FR-DS-001**: Sistema DEVE centralizar todos os tokens de design (cores, fontes, espacamentos) em um unico modulo Python (theme.py).
- **FR-DS-002**: Sistema DEVE aplicar stylesheet QSS via app.setStyleSheet() no entry point, antes de exibir a MainWindow.
- **FR-DS-003**: Sistema DEVE fornecer funcao apply_theme(qss_template) que substitui placeholders @var por valores de theme.py.
- **FR-DS-004**: Sistema DEVE ordenar substituicoes de placeholders do mais longo para o mais curto (ex: @primary-pressed antes de @primary).
- **FR-DS-005**: Sistema DEVE renderizar status de historias com StatusBadgeDelegate, exibindo badges pill com cores e simbolos nao-cromaticos.
- **FR-DS-006**: Sistema DEVE renderizar IDs de historias com MonospaceDelegate, aplicando fonte monospace.
- **FR-DS-007**: Sistema DEVE disponibilizar 16 icones SVG Phosphor Icons em diretorio assets/icons/.
- **FR-DS-011**: Sistema DEVE pre-carregar todos os 16 icones SVG no startup da aplicacao (eager loading) para garantir renderizacao instantanea na toolbar.
- **FR-DS-008**: Sistema DEVE aplicar regras QSS de :focus em widgets interativos (QPushButton, QLineEdit, QComboBox, QSpinBox, QDateEdit, QTableView).
- **FR-DS-009**: Sistema DEVE garantir areas clicaveis minimas de 32x32px para QToolButton.
- **FR-DS-010**: StatusBadgeDelegate DEVE exibir prefixos simbolicos para cada status: "●" BACKLOG, "▶" EXECUCAO, "◆" TESTES, "✓" CONCLUIDO, "✕" IMPEDIDO.

### Non-Functional Requirements

- **NFR-DS-001 (Contraste WCAG)**: Todas as combinacoes texto/fundo de badges DEVEM ter ratio de contraste >= 4.5:1 (conforme RNF-USAB-003).
- **NFR-DS-002 (Zero Hardcoded)**: Nenhum valor de cor, fonte ou espacamento DEVE estar hardcoded fora de theme.py (conforme RNF-MANT-001).
- **NFR-DS-003 (Performance)**: Delegates DEVEM renderizar em <= 16ms por celula para manter 60fps (conforme RNF-PERF-002).
- **NFR-DS-004 (Fallback de Fontes)**: Sistema DEVE usar fallback chains: "Inter", "Segoe UI", system-ui para texto; "JetBrains Mono", "Cascadia Code", "Consolas" para monospace.

### Key Entities

- **DesignTokens (theme.py)**: Modulo contendo 57 tokens de design: 28 cores (primary, neutral, semantic, status), 12 tipografia (font-family, font-size, font-weight), 8 espacamentos, 4 border-radius, 3 sombras, 2 estados interativos. Inclui STATUS_PALETTE com 5 configuracoes de status (simbolo, cores fg/bg).
- **StatusBadgeDelegate**: QStyledItemDelegate que renderiza badges pill para coluna de status. Recebe valores enum exatos (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) sem necessidade de mapeamento.
- **MonospaceDelegate**: QStyledItemDelegate que renderiza IDs em fonte monospace.
- **Stylesheet (stylesheet.qss)**: Arquivo QSS co-localizado com theme.py no mesmo diretorio (e.g., src/ui/theme/), contendo regras para 15+ tipos de widget, usando apenas placeholders @var.

## Success Criteria

### Measurable Outcomes

- **SC-001**: 100% dos widgets visiveis na aplicacao recebem estilizacao do design system (verificado por inspecao visual).
- **SC-002**: Todas as 5 combinacoes de status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) exibem badges com contraste >= 4.5:1 (verificado por calculadora WCAG).
- **SC-003**: 0 valores de cor/fonte hardcoded existem fora de theme.py (verificado por grep no codigo).
- **SC-004**: 16 arquivos SVG estao disponiveis e carregaveis via QIcon (verificado por teste unitario).
- **SC-005**: Delegates renderizam em <= 16ms por celula (verificado por profiling).
- **SC-006**: Navegacao por teclado (Tab/Shift+Tab) funciona em todos os widgets interativos com focus ring visivel.
