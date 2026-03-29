# Feature Specification: EP-020 — Busca, Filtros e Menu de Contexto

**Feature Branch**: `020-busca-filtros-menu-contexto`
**Created**: 2026-03-29
**Status**: Draft
**Input**: Implementar busca incremental, filtros por status e feature/onda, menu de contexto com right-click, e expor acao de Duplicar Historia na UI com atalho Ctrl+D.

---

## Clarifications

### Session 2026-03-29

- Q: Mover Acima/Abaixo devem ser desabilitados quando filtros estao ativos? → A: Sim, desabilitar quando qualquer filtro esta ativo.
- Q: Deve haver dialog de confirmacao antes de deletar via menu de contexto? → A: Sim, sempre exibir dialog de confirmacao.

---

## Rastreabilidade Bidirecional

| Componente | Requisitos SRS | Criterios de Aceite |
|------------|---------------|---------------------|
| MW-003 (Barra de Busca/Filtros) | RF-STORY-005, RNF-PERF-002, RNF-USAB-003, RNF-USAB-004 | Campo busca filtra por ID/Nome/Componente com debounce 150ms; Ctrl+F foca no campo |
| MW-007 (Menu de Contexto) | RF-STORY-004, RF-STORY-006, RF-DEP-001, RNF-USAB-004 | Right-click abre QMenu com 6 acoes; "Deletar" com cor @error |
| UX-001 (Duplicar Historia na UI) | RF-STORY-004, RNF-USAB-003 | Ctrl+D duplica historia; feedback na Status Bar; botao na toolbar |
| UX-003 (Filtros Rapidos por Status) | RF-STORY-009, RF-STORY-005, RNF-PERF-002 | 6 chips com contagem correta; chip ativo filtra tabela; bg @primary quando ativo |
| UX-004 (Filtro por Feature/Onda) | RF-STORY-005, RNF-USAB-004 | Dropdown com features agrupadas por onda; formato "Onda N - Nome" |
| FilterProxyModel | RF-STORY-005, RNF-PERF-002 | Filtros combinam com AND; nao altera modelo original; delegates funcionam com proxy |

---

## User Scenarios & Testing

### User Story 1 - Busca Incremental por Texto (Priority: P1)

O usuario digita texto no campo de busca para encontrar historias rapidamente pelo ID, nome ou componente. A tabela filtra em tempo real conforme digita, com debounce de 150ms para evitar processamento excessivo.

**Why this priority**: Busca por texto e a forma mais rapida e intuitiva de encontrar uma historia especifica. Com centenas de historias, navegar manualmente e impraticavel. E o filtro mais usado no dia a dia.

**Independent Test**: Pode ser testado digitando texto no campo de busca e verificando que a tabela exibe apenas historias cujo ID, nome ou componente contem o texto digitado.

**Acceptance Scenarios**:

1. **Given** a tabela exibe 50 historias, **When** o usuario digita "AUTH" no campo de busca, **Then** a tabela exibe apenas historias cujo ID, nome ou componente contem "AUTH" (case-insensitive), apos 150ms de pausa na digitacao.
2. **Given** o campo de busca contem "AUTH" e a tabela esta filtrada, **When** o usuario limpa o campo, **Then** a tabela volta a exibir todas as historias (respeitando outros filtros ativos).
3. **Given** qualquer tela esta ativa, **When** o usuario pressiona Ctrl+F, **Then** o cursor foca no campo de busca.
4. **Given** a tabela exibe historias, **When** o usuario digita um texto que nao corresponde a nenhuma historia, **Then** a tabela exibe zero linhas.

---

### User Story 2 - Filtro Rapido por Status (Priority: P1)

O usuario clica em chips de status para filtrar rapidamente historias por estado. Cada chip exibe a contagem total de historias naquele status. O chip "Todos" exibe o total geral.

**Why this priority**: Filtrar por status e a segunda operacao mais comum — o usuario quer ver apenas historias em execucao, ou impedidas, sem navegar por toda a tabela.

**Independent Test**: Pode ser testado clicando em cada chip e verificando que a tabela exibe apenas historias do status correspondente, com contagem correta.

**Acceptance Scenarios**:

1. **Given** existem 5 historias BACKLOG, 3 EXECUCAO e 2 CONCLUIDO, **When** a tela carrega, **Then** os chips exibem "Todos (10)", "Backlog (5)", "Execucao (3)", "Testes (0)", "Concluido (2)", "Impedido (0)".
2. **Given** o chip "Todos" esta ativo, **When** o usuario clica em "Backlog (5)", **Then** a tabela exibe apenas as 5 historias com status BACKLOG, e o chip "Backlog" recebe destaque visual (bg @primary, texto branco).
3. **Given** o chip "Backlog" esta ativo, **When** o usuario clica em "Todos", **Then** a tabela volta a exibir todas as historias e o chip "Todos" recebe destaque visual.
4. **Given** o chip "Testes" esta ativo e exibe contagem 0, **When** o usuario clica nele, **Then** a tabela nao exibe nenhuma historia.
5. **Given** uma historia e duplicada, **When** a tabela e atualizada, **Then** a contagem nos chips reflete a nova historia (ex: "Backlog (6)").

---

### User Story 3 - Menu de Contexto na Tabela (Priority: P2)

O usuario clica com botao direito em uma linha da tabela para acessar acoes rapidas: Editar, Duplicar, Mover Acima, Mover Abaixo, Dependencias e Deletar. As acoes reutilizam a logica existente no ViewModel.

**Why this priority**: Menu de contexto e um padrao esperado em aplicacoes desktop. Agiliza operacoes comuns sem precisar navegar pela toolbar.

**Independent Test**: Pode ser testado clicando com botao direito em uma linha e verificando que o menu aparece com as 6 acoes corretas, e que cada acao executa a operacao esperada.

**Acceptance Scenarios**:

1. **Given** a tabela exibe historias, **When** o usuario clica com botao direito em uma linha, **Then** um QMenu aparece com: "Editar (Enter)", "Duplicar (Ctrl+D)", separador, "Mover Acima (Alt+Up)", "Mover Abaixo (Alt+Down)", separador, "Dependencias...", separador, "Deletar (Delete)" com texto em cor @error.
2. **Given** o menu de contexto esta aberto, **When** o usuario clica em "Editar", **Then** o dialog de edicao abre para a historia da linha clicada.
3. **Given** o menu de contexto esta aberto, **When** o usuario clica em "Duplicar", **Then** a historia e duplicada e a Status Bar exibe "Historia duplicada: ORIG-001 -> ORIG-002".
4. **Given** o menu de contexto esta aberto, **When** o usuario clica em "Dependencias...", **Then** o DependencyDialog abre para a historia da linha clicada.
5. **Given** o menu de contexto esta aberto, **When** o usuario clica em "Deletar", **Then** um dialog de confirmacao e exibido e, se confirmado, a historia e deletada.
6. **Given** nenhuma linha esta selecionada na tabela, **When** o usuario clica com botao direito em area vazia, **Then** o menu de contexto nao aparece.

---

### User Story 4 - Duplicar Historia (Priority: P2)

O usuario duplica uma historia selecionada via botao na toolbar, item no menu de contexto ou atalho Ctrl+D. A copia recebe novo ID, sufixo " (copia)" no nome, e feedback visual na Status Bar.

**Why this priority**: Duplicar historia agiliza a criacao de historias similares, evitando retrabalho manual de preenchimento.

**Independent Test**: Pode ser testado selecionando uma historia, pressionando Ctrl+D, e verificando que uma nova historia aparece com os dados corretos e feedback na Status Bar.

**Acceptance Scenarios**:

1. **Given** a historia "CORE-001 - Implementar Login" esta selecionada, **When** o usuario pressiona Ctrl+D, **Then** uma nova historia "CORE-002 - Implementar Login (copia)" e criada com mesmos story points, status e feature, sem developer, datas, duracao ou dependencias.
2. **Given** a duplicacao foi bem-sucedida, **When** a nova historia aparece, **Then** a Status Bar exibe "Historia duplicada: CORE-001 -> CORE-002".
3. **Given** nenhuma historia esta selecionada, **When** o usuario pressiona Ctrl+D, **Then** nada acontece (acao ignorada).
4. **Given** a toolbar esta visivel, **When** o usuario observa o Grupo 1, **Then** ha um botao "Duplicar" com icone de copia ao lado de "Nova Historia".

---

### User Story 5 - Filtro por Feature/Onda (Priority: P3)

O usuario seleciona uma feature no dropdown para filtrar historias por feature e onda. O dropdown agrupa features por onda no formato "Onda N - Nome da Feature".

**Why this priority**: Filtro por feature e util para focar em um escopo funcional, mas e menos frequente que busca por texto ou status.

**Independent Test**: Pode ser testado selecionando uma feature no dropdown e verificando que a tabela exibe apenas historias daquela feature.

**Acceptance Scenarios**:

1. **Given** existem features "Autenticacao" (onda 1) e "Relatorios" (onda 2), **When** o dropdown e aberto, **Then** os itens sao: "Todas as features", separador, "Onda 1 - Autenticacao", "Onda 2 - Relatorios".
2. **Given** "Todas as features" esta selecionado, **When** o usuario seleciona "Onda 1 - Autenticacao", **Then** a tabela exibe apenas historias da feature "Autenticacao".
3. **Given** "Onda 1 - Autenticacao" esta selecionado, **When** o usuario seleciona "Todas as features", **Then** a tabela volta a exibir todas as historias.
4. **Given** nenhuma feature esta cadastrada, **When** o dropdown e exibido, **Then** apenas "Todas as features" aparece.

---

### User Story 6 - Filtros Compostos (Priority: P3)

O usuario combina multiplos filtros simultaneamente — texto, status e feature — e a tabela exibe apenas historias que atendem a todos os criterios (AND logico).

**Why this priority**: Composicao de filtros e avancada e depende das funcionalidades individuais estarem prontas.

**Independent Test**: Pode ser testado aplicando busca por texto + filtro de status + filtro de feature simultaneamente e verificando que apenas historias que atendem a todos os criterios aparecem.

**Acceptance Scenarios**:

1. **Given** o usuario digitou "Login" na busca e selecionou chip "Backlog", **When** a tabela atualiza, **Then** exibe apenas historias com status BACKLOG cujo ID, nome ou componente contem "Login".
2. **Given** busca "Login", chip "Backlog", feature "Autenticacao" estao ativos, **When** a tabela atualiza, **Then** exibe apenas historias BACKLOG da feature "Autenticacao" contendo "Login".
3. **Given** filtros compostos estao ativos resultando em zero historias, **When** o usuario limpa a busca, **Then** a tabela exibe historias que atendem aos filtros de status e feature restantes.

---

### Edge Cases

- O que acontece quando o usuario digita caracteres especiais na busca? A busca trata o texto como literal, sem regex.
- O que acontece quando historias sao adicionadas/removidas enquanto filtros estao ativos? Os filtros sao reaplicados automaticamente e as contagens dos chips atualizam.
- O que acontece quando o usuario clica com botao direito em uma linha nao selecionada? A linha e selecionada antes de abrir o menu de contexto.
- O que acontece quando o proxy model esta ativo e o usuario reordena prioridades? As acoes Mover Acima/Mover Abaixo sao desabilitadas quando qualquer filtro esta ativo (texto, status ou feature). O usuario deve limpar filtros para reordenar.

---

## Decisoes Arquiteturais (ADRs)

### ADR-001: Configuracao do Proxy Model com Delegates

**Contexto**: Delegates (MonospaceDelegate col 3, StatusBadgeDelegate col 6) sao atribuidos a QTableView via setItemDelegateForColumn(). Ao inserir QSortFilterProxyModel entre StoryTableModel e a view, e necessario garantir que delegates continuem funcionando.

**Opcoes**:
- A) Configurar delegates antes do proxy model
- B) Configurar delegates depois do proxy model, com view.setModel(proxy)

**Decisao**: Opcao B — ordem exata: (1) criar FilterProxyModel, (2) proxy.setSourceModel(table_model), (3) view.setModel(proxy), (4) view.setItemDelegateForColumn() na view. Proxy nao reordena colunas, entao indices de delegate nao mudam.

**Justificativa**: Delegates sao propriedade da view, nao do modelo. Configurar apos setModel(proxy) garante que a view renderiza via proxy sem quebrar mapeamento de colunas.

---

### ADR-002: Contagem de Chips via ViewModel

**Contexto**: Chips de status exibem contagem total por status (ex: "Backlog (12)"). A contagem deve refletir todas as historias, nao apenas as filtradas.

**Opcoes**:
- A) Contar a partir do proxy model filtrado
- B) Contar a partir do StoryTableModel (source model) via metodo direto
- C) Contar a partir do ViewModel (lista _stories)

**Decisao**: Opcao C — usar a lista completa de stories do ViewModel (propriedade stories) para calcular contagens. O ViewModel ja mantem a lista completa e emite stories_changed quando ela muda.

**Justificativa**: O ViewModel e a fonte de verdade para os dados. Acessar a lista via propriedade e simples, direto e desacoplado do modelo de tabela. A atualizacao e feita reagindo ao signal stories_changed.

---

### ADR-003: Indices de Coluna via Constantes Nomeadas

**Contexto**: O metodo filterAcceptsRow precisa acessar dados de colunas especificas (ID, Componente, Nome, Status, Feature) do source model.

**Opcoes**:
- A) Usar indices hardcoded (3, 4, 5, 6, 1)
- B) Usar StoryTableModel.COLUMNS.index("ID") para resolver indices
- C) Definir constantes nomeadas no FilterProxyModel

**Decisao**: Opcao B — resolver indices via StoryTableModel.COLUMNS.index() no __init__ do FilterProxyModel e armazenar como atributos de instancia (ex: self._col_id = StoryTableModel.COLUMNS.index("ID")).

**Justificativa**: Evita hardcoding e mantem rastreabilidade com a definicao de colunas do StoryTableModel. Se colunas forem reordenadas, os indices sao recalculados automaticamente.

---

### ADR-004: Padrao Async para DuplicateStoryUseCase no ViewModel

**Contexto**: DuplicateStoryUseCase.execute() e async. O ViewModel precisa chama-lo seguindo o padrao existente.

**Opcoes**:
- A) Chamar diretamente com await dentro de metodo async
- B) Usar asyncio.ensure_future() com qasync

**Decisao**: Opcao A — seguir o mesmo padrao dos metodos existentes (create_story, edit_story, delete_story) que sao metodos async chamados via asyncio.create_task() a partir da view.

**Justificativa**: Consistencia com o padrao ja estabelecido no ViewModel. Os metodos existentes usam try/except com emit de error_occurred em caso de falha.

---

### ADR-005: Dropdown de Features Populado via StoryOutputDTO

**Contexto**: O dropdown precisa listar features agrupadas por onda. O ViewModel carrega stories com feature_name e wave enriquecidos no DTO.

**Opcoes**:
- A) Extrair features distintas de StoryOutputDTO (feature_name + wave) ao carregar stories
- B) Usar ListFeaturesUseCase separado

**Decisao**: Opcao A — extrair features unicas da lista de stories no ViewModel, agrupando por wave. Iterar sobre stories e coletar pares (feature_id, feature_name, wave) unicos.

**Justificativa**: O StoryOutputDTO ja contem feature_name e wave enriquecidos. Criar um use case separado seria over-engineering para dados que ja estao disponiveis. Manter simplicidade conforme Principio IX.

---

### ADR-006: Populacao da Zona 3 (Barra de Filtros)

**Contexto**: A zona 3 do layout tem 36px reservados (placeholder vazio criado em EP-018).

**Opcoes**:
- A) Substituir o placeholder por um novo widget com QHBoxLayout
- B) Adicionar widgets diretamente ao placeholder existente

**Decisao**: Opcao B — configurar QHBoxLayout no widget placeholder existente (_filter_bar) e adicionar os widgets de busca, chips e dropdown sem alterar a estrutura de zonas do EP-018.

**Justificativa**: Preserva a estrutura de 5 zonas do EP-018. O placeholder ja existe como QWidget com altura fixa. Basta adicionar layout e filhos.

---

### ADR-007: Reuso de Acoes no Menu de Contexto

**Contexto**: Acoes Editar, Deletar, Mover Cima, Mover Abaixo ja existem como metodos no ViewModel e botoes na toolbar.

**Opcoes**:
- A) Reutilizar as mesmas QAction da toolbar no menu de contexto
- B) Criar novas QAction no menu que chamam os mesmos metodos do ViewModel

**Decisao**: Opcao B — criar novas QAction no menu de contexto que chamam os mesmos slots/metodos do ViewModel. O menu e criado dinamicamente a cada right-click (nao persistente).

**Justificativa**: QAction da toolbar tem estado (enabled/disabled) gerenciado pela toolbar. Criar QAction locais para o menu evita efeitos colaterais e permite estilizacao independente (ex: "Deletar" com cor @error). O menu e efemero — criado, exibido e destruido a cada invocacao.

---

### ADR-008: Atalho Ctrl+D sem Conflito

**Contexto**: A MainWindow ja possui atalhos configurados em _setup_shortcuts(). Ctrl+D nao esta em uso.

**Opcoes**:
- A) Registrar como QShortcut no MainWindow
- B) Registrar como QAction na toolbar com shortcut associado

**Decisao**: Opcao B — adicionar QAction "Duplicar" na toolbar (Grupo 1) com shortcut Ctrl+D. O atalho fica visivel na toolbar e no menu de contexto.

**Justificativa**: QAction com shortcut e o padrao ja usado para outros atalhos da toolbar (Ctrl+N, F2, Delete). Manter consistencia de implementacao.

---

## Requirements

### Functional Requirements

- **FR-001**: O sistema DEVE exibir um campo de busca com 240px de largura, icone de lupa e placeholder "Buscar por ID, nome ou componente..." na barra de filtros (zona 3).
- **FR-002**: O sistema DEVE filtrar a tabela enquanto o usuario digita, aplicando debounce de 150ms para evitar processamento excessivo.
- **FR-003**: A busca DEVE ser case-insensitive e buscar nas colunas ID, Nome e Componente do modelo original.
- **FR-004**: O atalho Ctrl+F DEVE focar o cursor no campo de busca.
- **FR-005**: O sistema DEVE exibir 6 chips de status na barra de filtros: "Todos", "Backlog", "Execucao", "Testes", "Concluido", "Impedido".
- **FR-006**: Cada chip DEVE exibir a contagem total de historias naquele status entre parenteses (ex: "Backlog (12)").
- **FR-007**: A contagem nos chips DEVE refletir o total geral de historias (nao o total filtrado por outros filtros).
- **FR-008**: Ao clicar em um chip, a tabela DEVE exibir apenas historias do status correspondente. O chip ativo DEVE receber destaque visual (fundo @primary, texto branco).
- **FR-009**: Apenas um chip de status pode estar ativo por vez (comportamento de radio button).
- **FR-010**: O sistema DEVE exibir um dropdown na barra de filtros com "Todas as features" como opcao padrao, seguido de features agrupadas por onda no formato "Onda N - Nome da Feature".
- **FR-011**: A lista de features no dropdown DEVE ser extraida dinamicamente dos dados carregados (StoryOutputDTO.feature_name e wave).
- **FR-012**: Ao selecionar uma feature no dropdown, a tabela DEVE exibir apenas historias daquela feature.
- **FR-013**: Filtros de texto, status e feature DEVEM combinar com AND logico.
- **FR-014**: O sistema DEVE exibir um QMenu ao clicar com botao direito em uma linha da tabela, contendo: "Editar (Enter)", "Duplicar (Ctrl+D)", separador, "Mover Acima (Alt+Up)", "Mover Abaixo (Alt+Down)", separador, "Dependencias...", separador, "Deletar (Delete)".
- **FR-015**: A acao "Deletar" no menu de contexto DEVE ser exibida com texto em cor @error (vermelho).
- **FR-016**: O menu de contexto NAO DEVE aparecer quando o right-click e em area vazia (sem linha).
- **FR-017**: O sistema DEVE permitir duplicar a historia selecionada via botao na toolbar (Grupo 1), item no menu de contexto, ou atalho Ctrl+D.
- **FR-018**: A duplicacao DEVE criar uma nova historia com mesmo componente, nome + sufixo " (copia)", story points, status e feature. Developer, datas, duracao e dependencias NAO sao copiados.
- **FR-019**: Apos duplicacao bem-sucedida, a Status Bar DEVE exibir "Historia duplicada: [ID_ORIGINAL] -> [ID_COPIA]".
- **FR-020**: A acao "Dependencias..." no menu de contexto DEVE abrir o DependencyDialog existente para a historia da linha clicada.
- **FR-021**: O FilterProxyModel NAO DEVE alterar o StoryTableModel original — apenas filtrar a visualizacao.
- **FR-022**: Delegates existentes (MonospaceDelegate col 3, StatusBadgeDelegate col 6) DEVEM continuar funcionando com o proxy model ativo.
- **FR-023**: As acoes Mover Acima e Mover Abaixo DEVEM ser desabilitadas (na toolbar e no menu de contexto) quando qualquer filtro esta ativo (texto, status ou feature).
- **FR-024**: A acao Deletar (via menu de contexto, toolbar ou tecla Delete) DEVE sempre exibir um dialog de confirmacao antes de executar a exclusao.

### Key Entities

- **FilterProxyModel**: Intermediario entre StoryTableModel e StoryTableView que aplica filtros de texto, status e feature sem alterar os dados originais. Expoe metodos set_text_filter(), set_status_filter() e set_feature_filter().
- **Barra de Busca/Filtros**: Widget composto na zona 3 do layout, contendo campo de busca (240px, icone lupa, placeholder PT-BR), 6 chips de status com contagem e dropdown de feature/onda.

---

## Estilos QSS

### Estilos Existentes (nao modificar)

- QLineEdit (T023): border, border-radius, padding, focus ring
- QPushButton (T022): estilos primario e secundario
- QComboBox (T024): border, border-radius, padding
- QMenu (T029): background, border, item hover, separator

### Estilos Novos a Adicionar

- Campo de busca (#searchField): padding-left para icone, min-width/max-width 240px
- Chips de filtro (QPushButton[class="filterChip"]): fundo @surface, texto @text-secondary, border-radius @radius-full, padding @spacing-1 @spacing-3, font-size @font-size-xs
- Chips de filtro ativos (QPushButton[class="filterChip"]:checked): fundo @primary, texto branco, border @primary
- Chips de filtro hover (QPushButton[class="filterChip"]:hover:!checked): fundo @neutral-100, border @neutral-300
- Menu de contexto - acao destrutiva (QMenu::item[destructive="true"]): cor @error-fg

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: O usuario consegue encontrar uma historia especifica em menos de 3 segundos usando busca por texto.
- **SC-002**: A filtragem da tabela ocorre em ate 150ms apos o usuario parar de digitar (debounce).
- **SC-003**: As contagens nos chips de status estao 100% corretas em relacao aos dados carregados.
- **SC-004**: Filtros compostos (texto + status + feature) retornam resultados corretos com AND logico.
- **SC-005**: O usuario acessa qualquer acao do menu de contexto em 2 cliques (right-click + selecao).
- **SC-006**: A duplicacao de historia e concluida com feedback visual na Status Bar em ate 500ms.
- **SC-007**: Todos os testes existentes continuam passando sem regressao.
- **SC-008**: A cobertura de testes do FilterProxyModel atinge pelo menos 80%.
- **SC-009**: Os atalhos Ctrl+F e Ctrl+D funcionam corretamente sem conflito com atalhos existentes.
- **SC-010**: Delegates (MonospaceDelegate, StatusBadgeDelegate) continuam renderizando corretamente com proxy model ativo.
