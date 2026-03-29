# Feature Specification: EP-019 — Tabela de Backlog (GUI-003)

**Feature Branch**: `019-backlog-table`
**Created**: 2026-03-29
**Status**: Draft
**Input**: Expandir StoryTableModel de 8 para 13 colunas, reordenar colunas, integrar delegates nos novos indices, aplicar estilizacao QSS, implementar estado vazio orientativo, e criar testes unitarios dedicados. Escopo exclusivo na camada Presentation.
**Out of scope**: Sorting de colunas (epico futuro), redimensionamento manual de colunas pelo usuario, selecao multipla de linhas.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizacao completa do backlog em 13 colunas (Priority: P1)

Como gestor de backlog, quero ver todas as 13 colunas de informacao de cada historia (Prioridade, Feature, Onda, ID, Componente, Nome, Status, Desenvolvedor, Dependencias, SP, Inicio, Fim, Duracao) em uma unica tabela, para ter visibilidade completa sem precisar abrir cada historia individualmente.

**Why this priority**: Esta e a funcionalidade central do epico — sem a expansao das colunas, nenhuma outra funcionalidade (estado vazio, delegates reposicionados) faz sentido. A tabela e o ponto focal da aplicacao.

**Independent Test**: Pode ser testado carregando historias no modelo e verificando que todas as 13 colunas exibem dados corretos, com formatacao adequada (datas DD/MM/YYYY, IDs COMPONENTE-NNN, nomes resolvidos).

**Acceptance Scenarios**:

1. **Given** o backlog contem historias cadastradas, **When** o usuario abre a aplicacao, **Then** a tabela exibe 13 colunas na ordem: Prioridade, Feature, Onda, ID, Componente, Nome, Status, Desenvolvedor, Dependencias, SP, Inicio, Fim, Duracao.
2. **Given** uma historia com start_date e end_date preenchidos, **When** a tabela e renderizada, **Then** as datas aparecem no formato DD/MM/YYYY.
3. **Given** uma historia com developer_id associado, **When** a tabela e renderizada, **Then** a coluna Desenvolvedor exibe o nome do desenvolvedor (nao o ID numerico).
4. **Given** uma historia com feature_id associada, **When** a tabela e renderizada, **Then** a coluna Feature exibe o nome da feature e a coluna Onda exibe o numero da onda. Quando nao ha feature, ambas exibem "—".
5. **Given** uma historia sem feature, desenvolvedor ou datas, **When** a tabela e renderizada, **Then** as colunas correspondentes exibem "—".
6. **Given** uma historia com dependencias, **When** a tabela e renderizada, **Then** a coluna Dependencias exibe os IDs formatados separados por virgula (ex: "AUTH-001, API-003").

---

### User Story 2 - Larguras, alinhamentos e delegates corretos por coluna (Priority: P1)

Como usuario, quero que cada coluna tenha largura e alinhamento adequados ao seu conteudo, com o ID em fonte monospacada e o Status como badge colorido, para facilitar a leitura rapida e a identificacao visual.

**Why this priority**: Sem configuracao de larguras e delegates, a tabela expandida seria ilegivel — colunas se sobreporiam e informacoes visuais (badges, monospace) ficariam perdidas.

**Independent Test**: Pode ser testado verificando que MonospaceDelegate esta na coluna ID (indice 3), StatusBadgeDelegate na coluna Status (indice 6), larguras fixas aplicadas, e coluna Nome com stretch.

**Acceptance Scenarios**:

1. **Given** a tabela e exibida, **When** o usuario observa a coluna ID, **Then** o texto aparece em fonte monospacada (JetBrains Mono, Cascadia Code, Consolas ou monospace).
2. **Given** a tabela e exibida, **When** o usuario observa a coluna Status, **Then** o status aparece como badge pill colorido com simbolo (ex: "● BACKLOG", "▶ EXECUCAO").
3. **Given** a janela e redimensionada, **When** a largura aumenta, **Then** apenas a coluna Nome expande (stretch), as demais mantem largura fixa.
4. **Given** texto longo nas colunas Nome, Feature, Desenvolvedor ou Dependencias, **When** o texto excede a largura da coluna, **Then** o texto e truncado com elipsis (...) e um tooltip exibe o texto completo ao passar o mouse.

---

### User Story 3 - Estado vazio orientativo (Priority: P2)

Como usuario novo, quero ver uma mensagem orientativa quando o backlog esta vazio, para saber como comecar a usar a aplicacao.

**Why this priority**: Importante para a experiencia do primeiro uso (RNF-USAB-004), mas secundario em relacao a visualizacao de dados que e o uso principal.

**Independent Test**: Pode ser testado abrindo a aplicacao sem historias cadastradas e verificando que a mensagem aparece e os botoes estao desabilitados.

**Acceptance Scenarios**:

1. **Given** nao ha historias cadastradas, **When** o usuario abre a aplicacao, **Then** a tabela exibe uma mensagem centralizada: "Nenhuma historia cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para comecar."
2. **Given** nao ha historias cadastradas, **When** o usuario observa a toolbar, **Then** os botoes "Calcular Cronograma" e "Alocar" estao visualmente desabilitados.
3. **Given** o estado vazio esta sendo exibido, **When** o usuario cadastra a primeira historia, **Then** a mensagem desaparece e a tabela exibe a historia normalmente.
4. **Given** o usuario deleta a ultima historia, **When** a tabela fica vazia, **Then** a mensagem orientativa reaparece e os botoes sao desabilitados.

---

### User Story 4 - Estilizacao visual consistente (Priority: P2)

Como usuario, quero que a tabela tenha zebra striping, selecao com destaque suave, e header estilizado, para uma experiencia visual profissional e confortavel.

**Why this priority**: A estilizacao complementa a funcionalidade principal e garante conformidade com o design system (EP-017).

**Independent Test**: Pode ser testado por inspecao visual e verificacao de que as propriedades QSS estao sendo aplicadas corretamente.

**Acceptance Scenarios**:

1. **Given** a tabela contem historias, **When** o usuario observa as linhas, **Then** linhas alternadas tem cores de fundo diferentes (zebra striping).
2. **Given** o usuario seleciona uma linha, **When** a selecao e aplicada, **Then** o fundo muda para azul claro (#E6F0FA) e o texto permanece escuro (sem inversao de cor).
3. **Given** a tabela e exibida, **When** o usuario observa o header, **Then** os nomes das colunas aparecem em texto secundario, peso 600, com borda inferior.

---

### User Story 5 - Testes unitarios para o modelo expandido (Priority: P2)

Como desenvolvedor, quero testes unitarios dedicados cobrindo o StoryTableModel expandido, para garantir que mudancas futuras nao quebrem a tabela.

**Why this priority**: Essencial para manutencao (RNF-MANT-001, cobertura >= 80%), mas nao visivel ao usuario final.

**Independent Test**: Pode ser testado executando a suite de testes e verificando cobertura >= 80% para o modelo.

**Acceptance Scenarios**:

1. **Given** a suite de testes e executada, **When** todos os testes rodam, **Then** `columnCount()` retorna 13 e `headerData()` retorna nomes corretos para todas as colunas.
2. **Given** a suite de testes e executada, **When** `data()` e chamado para cada coluna, **Then** os valores retornados estao formatados corretamente (datas, IDs, nomes resolvidos, "—" para ausentes).
3. **Given** a suite de testes e executada, **When** testes de alinhamento rodam, **Then** cada coluna tem o alinhamento correto (Centro ou Esquerda conforme especificado).
4. **Given** a suite de testes e executada, **When** testes de integracao existentes rodam, **Then** todos passam sem regressao.

---

### Edge Cases

- O que acontece quando uma historia tem `developer_id` que nao corresponde a nenhum desenvolvedor cadastrado? A coluna Desenvolvedor deve exibir "—".
- O que acontece quando uma historia tem `feature_id` que nao corresponde a nenhuma feature cadastrada? As colunas Feature e Onda devem exibir "—".
- O que acontece quando uma historia tem dependencias cujos IDs nao existem mais? Os IDs devem ser exibidos conforme armazenados, sem validacao na camada de apresentacao.
- O que acontece quando o texto de Nome e extremamente longo (>500 caracteres)? Deve truncar com elipsis e o tooltip completo deve funcionar.
- O que acontece quando a resolucao e menor que a soma das larguras fixas (ex: 1024px)? A scrollbar horizontal deve aparecer automaticamente.
- O que acontece quando `story.component` esta vazio? A coluna Componente deve exibir "—".
- O que acontece quando `story.duration` e None? A coluna Duracao deve exibir "—".

## Clarifications

### Session 2026-03-29

- Q: As colunas da tabela devem ser ordenaveis ao clicar no header? → A: Nao neste epico; sorting sera um epico futuro.
- Q: Como o ViewModel recebe nomes resolvidos (developer_name, feature_name, wave)? → A: DTO enriquecido — Application layer entrega nomes ja resolvidos no DTO.
- Q: O usuario pode redimensionar colunas manualmente arrastando o header? → A: Nao, larguras fixas conforme FR-015 (exceto Nome que faz stretch).
- Q: Qual o modo de selecao de linhas na tabela? → A: Selecao unica — apenas uma linha por vez.
- Q: Qual o numero maximo esperado de historias no backlog? → A: Ate 500 historias, sem necessidade de virtualizacao.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A tabela DEVE exibir exatamente 13 colunas na seguinte ordem: Prioridade, Feature, Onda, ID, Componente, Nome, Status, Desenvolvedor, Dependencias, SP, Inicio, Fim, Duracao.
- **FR-002**: A coluna Prioridade DEVE exibir o valor inteiro de prioridade da historia.
- **FR-003**: A coluna Feature DEVE exibir o nome da feature associada, ou "—" quando nao ha feature.
- **FR-004**: A coluna Onda DEVE exibir o numero da onda da feature associada, ou "—" quando nao ha feature associada. **Nota**: Ondas validas comecam em 1; "—" indica ausencia de feature (consistente com FR-003).
- **FR-005**: A coluna ID DEVE exibir o identificador no formato COMPONENTE-NNN (ex: AUTH-001) com fonte monospacada.
- **FR-006**: A coluna Componente DEVE exibir o prefixo de componente extraido do story_id.
- **FR-007**: A coluna Nome DEVE expandir com a janela (stretch), ter largura minima de 200px, e truncar texto longo com elipsis.
- **FR-008**: A coluna Status DEVE exibir o status como badge pill colorido com simbolo, usando o delegate existente.
- **FR-009**: A coluna Desenvolvedor DEVE exibir o nome do desenvolvedor, ou "—" quando nao atribuido. Texto longo deve truncar com elipsis.
- **FR-010**: A coluna Dependencias DEVE exibir IDs formatados (COMPONENTE-NNN) separados por virgula, ou "—" quando nao ha dependencias. Texto longo deve truncar com elipsis.
- **FR-011**: A coluna SP DEVE exibir o valor inteiro de story points.
- **FR-012**: As colunas Inicio e Fim DEVEM exibir datas no formato DD/MM/YYYY, ou "—" quando nao preenchidas.
- **FR-013**: A coluna Duracao DEVE exibir o numero de dias uteis, ou "—" quando nao calculado.
- **FR-014**: Colunas com texto truncado (Nome, Feature, Desenvolvedor, Dependencias) DEVEM exibir tooltip com o texto completo ao passar o mouse.
- **FR-015**: Cada coluna DEVE ter largura fixa ou stretch conforme especificado: Prioridade (60px), Feature (120px), Onda (50px), ID (100px), Componente (80px), Nome (stretch, min 200px), Status (100px), Desenvolvedor (100px), Dependencias (120px), SP (40px), Inicio (90px), Fim (90px), Duracao (60px). Larguras sao fixas e NAO redimensionaveis pelo usuario.
- **FR-016**: Cada coluna DEVE ter alinhamento conforme especificado: Centro (Prioridade, Onda, Status, SP, Inicio, Fim, Duracao), Esquerda (Feature, ID, Componente, Nome, Desenvolvedor, Dependencias).
- **FR-017**: Quando nao ha historias cadastradas, a tabela DEVE exibir uma mensagem centralizada: "Nenhuma historia cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para comecar."
- **FR-018**: Quando nao ha historias cadastradas, os botoes "Calcular Cronograma" e "Alocar" DEVEM estar desabilitados.
- **FR-019**: Quando a primeira historia e cadastrada, a mensagem de estado vazio DEVE desaparecer e a tabela DEVE exibir a historia.
- **FR-020**: Quando a ultima historia e removida, a mensagem de estado vazio DEVE reaparecer e os botoes DEVEM ser desabilitados.
- **FR-021**: A tabela DEVE manter zebra striping (linhas alternadas com cores diferentes).
- **FR-022**: A selecao de linha DEVE usar fundo azul claro com texto escuro (sem inversao de cor). Modo de selecao: unica (apenas uma linha por vez).
- **FR-023**: O header da tabela DEVE exibir nomes de coluna em texto secundario, peso 600, com borda inferior.
- **FR-024**: Testes unitarios DEVEM cobrir: contagem de colunas, nomes de headers, dados por coluna com formatacao, alinhamentos, tooltips, e estado vazio.
- **FR-025**: Testes de integracao existentes DEVEM ser atualizados para refletir 13 colunas sem regressao.

### Key Entities

- **StoryTableModel (ViewModel)**: Modelo de dados da tabela que formata e expoe 13 colunas de informacao de historias para a View. Recebe dados via DTOs da camada Application. Responsavel por formatacao de exibicao (datas, IDs, nomes resolvidos), alinhamentos por coluna, e tooltips.
- **Estado Vazio (MW-008)**: Componente visual que exibe mensagem orientativa quando a tabela nao contem historias. Sincroniza com botoes da toolbar para desabilita-los.

## Assumptions

- O `StoryOutputDTO` ja contem os campos `id`, `component`, `name`, `story_points`, `priority`, `status`, `duration`, `start_date`, `end_date`, `developer_id`, `feature_id`. Campos adicionais necessarios para resolucao de nomes (developer_name, feature_name, wave, dependencies) serao providos via DTO enriquecido pela camada Application (nao via dados auxiliares no ViewModel).
- Os delegates `StatusBadgeDelegate` e `MonospaceDelegate` ja existem e estao funcionais (EP-017). Este epico apenas os reposiciona nos novos indices de coluna.
- O design system (theme.py, stylesheet.qss) ja esta implementado (EP-017) e o layout vertical com 5 zonas ja esta implementado (EP-018).
- A resolucao de `developer_id` para nome e `feature_id` para nome/onda ocorre na camada Application (DTO enriquecido) ou via dados auxiliares injetados no ViewModel, nunca acessando repositorios diretamente da Presentation.
- A resolucao de IDs de dependencias para formato COMPONENTE-NNN ocorre na camada Application ao construir o DTO.
- Textos de interface sao em portugues brasileiro. Codigo (classes, metodos, variaveis) em ingles.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A tabela exibe 13 colunas completas e na ordem correta, verificavel por inspecao visual e testes automatizados.
- **SC-002**: Usuarios identificam o status de cada historia em menos de 2 segundos gracas ao badge visual com simbolo e cor.
- **SC-003**: Todas as informacoes relevantes de uma historia sao visiveis sem necessidade de abrir um formulario de edicao.
- **SC-004**: O estado vazio orienta o usuario novo a criar ou importar historias na primeira interacao.
- **SC-005**: Cobertura de testes unitarios do StoryTableModel >= 80%.
- **SC-006**: Zero regressoes nos testes de integracao existentes apos a expansao de 8 para 13 colunas.
- **SC-007**: Cada celula e renderizada em tempo imperceptivel ao usuario (fluido a 60fps). Volume maximo esperado: ate 500 historias, sem necessidade de virtualizacao.
- **SC-008**: A tabela e funcional em resolucao 1366x768 sem perda de informacao critica.
