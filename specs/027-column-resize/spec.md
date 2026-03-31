# Feature Specification: Column Resize

**Feature Branch**: `027-column-resize`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Eu quero poder redimensionar as colunas para alterar o tamanho e melhorar a visualização igual eu faço no excel."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Redimensionar colunas arrastando a borda (Priority: P1)

Como usuario do backlog manager, quero arrastar a borda entre os cabecalhos das colunas para ajustar a largura de cada coluna, permitindo visualizar melhor o conteudo que esta truncado ou reduzir colunas que ocupam espaco desnecessario.

**Why this priority**: Esta e a funcionalidade principal solicitada. Sem ela, o usuario nao consegue personalizar a visualizacao da tabela conforme suas necessidades.

**Independent Test**: Pode ser testado abrindo a tabela do backlog e arrastando a borda direita de qualquer cabecalho de coluna para alterar sua largura.

**Acceptance Scenarios**:

1. **Given** a tabela do backlog esta visivel com dados, **When** o usuario posiciona o cursor sobre a borda direita de um cabecalho de coluna, **Then** o cursor muda para o indicador de redimensionamento (seta dupla horizontal)
2. **Given** o cursor esta sobre a borda de um cabecalho, **When** o usuario clica e arrasta para a direita, **Then** a coluna aumenta de largura proporcionalmente ao arraste
3. **Given** o cursor esta sobre a borda de um cabecalho, **When** o usuario clica e arrasta para a esquerda, **Then** a coluna diminui de largura proporcionalmente ao arraste
4. **Given** uma coluna esta sendo redimensionada, **When** o usuario solta o botao do mouse, **Then** a coluna mantem a nova largura definida

---

### User Story 2 - Persistir larguras personalizadas entre sessoes (Priority: P2)

Como usuario, quero que as larguras que defini para as colunas sejam salvas automaticamente, para que ao reabrir o aplicativo eu encontre a tabela do jeito que personalizei.

**Why this priority**: Complementa a experiencia de redimensionamento. Sem persistencia, o usuario precisaria reajustar as colunas toda vez que abrisse o aplicativo, tornando a funcionalidade frustrante.

**Independent Test**: Pode ser testado redimensionando colunas, fechando o aplicativo e reabrindo para verificar que as larguras foram preservadas.

**Acceptance Scenarios**:

1. **Given** o usuario redimensionou uma ou mais colunas, **When** o usuario fecha e reabre o aplicativo, **Then** as colunas aparecem com as larguras personalizadas salvas anteriormente
2. **Given** o usuario nunca redimensionou colunas (primeira execucao), **When** o aplicativo e aberto, **Then** as colunas usam as larguras padrao definidas pelo sistema

---

### User Story 3 - Restaurar larguras padrao (Priority: P3)

Como usuario, quero poder restaurar rapidamente todas as colunas para as larguras padrao originais, caso tenha feito ajustes que nao ficaram bons.

**Why this priority**: Funcionalidade de conveniencia que da seguranca ao usuario para experimentar sem medo de "estragar" o layout.

**Independent Test**: Pode ser testado redimensionando varias colunas para tamanhos diferentes e usando a opcao de restaurar padrao para verificar que todas voltam aos tamanhos originais.

**Acceptance Scenarios**:

1. **Given** o usuario personalizou larguras de colunas, **When** o usuario aciona a opcao de restaurar larguras padrao (via menu de contexto do cabecalho), **Then** todas as colunas voltam as larguras originais definidas pelo sistema
2. **Given** o usuario restaurou as larguras padrao, **When** o usuario fecha e reabre o aplicativo, **Then** as colunas aparecem com as larguras padrao (a restauracao tambem e persistida)

---

### Edge Cases

- O que acontece quando o usuario tenta reduzir uma coluna abaixo de uma largura minima? A coluna deve respeitar uma largura minima para que o cabecalho permaneca legivel.
- O que acontece quando a janela e redimensionada apos o usuario ter personalizado larguras? A coluna flexivel ("Nome") deve continuar absorvendo o espaco restante.
- O que acontece com duplo-clique na borda do cabecalho? A coluna deve ajustar automaticamente ao conteudo visivel (auto-fit), seguindo o comportamento padrao de planilhas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir que o usuario redimensione qualquer coluna da tabela arrastando a borda direita do cabecalho
- **FR-002**: O sistema DEVE exibir um cursor de redimensionamento (seta dupla horizontal) ao posicionar o mouse sobre a borda entre cabecalhos
- **FR-003**: O sistema DEVE manter a coluna "Nome" com comportamento flexivel (stretch), absorvendo o espaco restante quando outras colunas sao redimensionadas
- **FR-004**: O sistema DEVE definir uma largura minima de 30 pixels para qualquer coluna, impedindo que fique invisivel ou ilegivel
- **FR-005**: O sistema DEVE salvar automaticamente as larguras personalizadas das colunas quando o usuario altera qualquer largura
- **FR-006**: O sistema DEVE restaurar as larguras salvas ao iniciar o aplicativo
- **FR-007**: O sistema DEVE oferecer uma opcao "Restaurar larguras padrao" acessivel via menu de contexto do cabecalho da tabela
- **FR-008**: O sistema DEVE ajustar automaticamente a largura de uma coluna ao conteudo visivel quando o usuario fizer duplo-clique na borda do cabecalho (auto-fit)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuario consegue redimensionar qualquer coluna em menos de 2 segundos (arrastar e soltar)
- **SC-002**: As larguras personalizadas sao preservadas entre sessoes com 100% de fidelidade
- **SC-003**: A restauracao para larguras padrao ocorre instantaneamente (menos de 1 segundo)
- **SC-004**: O duplo-clique para auto-fit ajusta a coluna ao conteudo visivel em menos de 1 segundo
- **SC-005**: A coluna "Nome" continua preenchendo o espaco restante apos redimensionamento de outras colunas

## Assumptions

- O aplicativo ja utiliza QSettings para persistencia de preferencias de UI, portanto as larguras de colunas seguirao o mesmo mecanismo
- A largura minima de 30 pixels e suficiente para exibir pelo menos um caractere e a borda de arraste
- O comportamento de duplo-clique para auto-fit segue o padrao amplamente conhecido de planilhas (Excel, Google Sheets)
- A coluna "Nome" sempre permanece como stretch, mesmo apos personalizacao das demais colunas
