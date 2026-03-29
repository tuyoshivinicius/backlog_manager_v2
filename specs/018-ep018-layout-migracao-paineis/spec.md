# Feature Specification: EP-018 — Layout Principal e Migracao de Paineis

**Feature Branch**: `018-ep018-layout-migracao-paineis`
**Created**: 2026-03-28
**Status**: Draft
**Input**: User description: "Prompt para especificacao tecnica do EP-018 - refatoracao da MainWindow para layout vertical de 5 zonas, adicao de Menu Bar e Status Bar, migracao de paineis laterais para dialogs modais"

---

## Clarifications

### Session 2026-03-28

- Q: Durante execução de alocação, como UI deve indicar progresso? → A: Preservar comportamento de progresso existente do EP-008
- Q: Com 0 avisos após alocação, como badge de warnings na Status Bar deve se comportar? → A: Ocultar badge completamente quando count é 0
- Q: Como usuário acessa DependencyDialog para história selecionada? → A: Menu de contexto (right-click) na linha da tabela
- Q: Como tratar compatibilidade de testes com refatoração panels→dialogs? → A: Testes podem ser atualizados; "sem regressão" significa funcionalidade preservada

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Navegacao por Menu Bar (Priority: P1)

O usuario deseja acessar todas as funcionalidades da aplicacao atraves de um menu profissional no topo da janela, com atalhos de teclado visiveis para acelerar o fluxo de trabalho.

**Why this priority**: Menu Bar e o componente de navegacao principal da aplicacao desktop. Permite acesso a todas as funcionalidades de forma organizada e padronizada, essencial para usabilidade e descoberta de recursos.

**Independent Test**: Pode ser testado completamente navegando pelos 4 menus (Arquivo, Cadastros, Ferramentas, Ajuda) e verificando que cada acao executa corretamente.

**Acceptance Scenarios**:

1. **Given** aplicacao iniciada, **When** visualizo a barra superior, **Then** vejo Menu Bar com 4 menus: Arquivo, Cadastros, Ferramentas, Ajuda
2. **Given** Menu Bar visivel, **When** clico em Arquivo > Importar Excel, **Then** dialog de selecao de arquivo abre
3. **Given** Menu Bar visivel, **When** pressiono Ctrl+N, **Then** dialog de nova historia abre
4. **Given** Menu Bar visivel, **When** abro menu Cadastros, **Then** vejo opcoes: Historias, Features, Desenvolvedores, Configuracao com atalhos exibidos

---

### User Story 2 - Layout Vertical com Tabela Expandida (Priority: P1)

O usuario deseja visualizar a tabela de historias em 100% da largura disponivel, sem paineis laterais ocupando espaco, para melhor visualizacao do backlog completo.

**Why this priority**: Maximizar a area util da tabela de historias e fundamental para produtividade. A refatoracao do layout de QSplitter para QVBoxLayout vertical e pre-requisito para todos os outros componentes.

**Independent Test**: Pode ser testado iniciando a aplicacao e verificando que a tabela ocupa toda a largura da area central sem divisores laterais.

**Acceptance Scenarios**:

1. **Given** aplicacao iniciada, **When** observo o layout, **Then** vejo 5 zonas empilhadas: Menu Bar, Toolbar, Barra Filtros, Tabela, Status Bar
2. **Given** layout vertical, **When** verifico a tabela, **Then** tabela ocupa 100% da largura (sem QSplitter horizontal)
3. **Given** resolucao 1366x768, **When** abro aplicacao, **Then** layout funcional sem cortes ou sobreposicoes

---

### User Story 3 - Toolbar com Icones e Grupos (Priority: P2)

O usuario deseja identificar visualmente as acoes da toolbar atraves de icones SVG, com botoes agrupados por categoria para facilitar a localizacao de funcoes.

**Why this priority**: Toolbar com icones melhora a usabilidade visual e reduz tempo de aprendizado. Agrupamento por categoria torna a interface mais profissional.

**Independent Test**: Pode ser testado verificando que cada botao da toolbar exibe icone + texto, com separadores visiveis entre os 5 grupos.

**Acceptance Scenarios**:

1. **Given** toolbar visivel, **When** inspeciono botoes, **Then** cada botao exibe icone SVG + texto ao lado (ToolButtonTextBesideIcon)
2. **Given** toolbar, **When** verifico grupos, **Then** vejo 5 grupos separados: CRUD, Priorizacao, Cadastros, Processamento, Excel
3. **Given** hover em botao da toolbar, **When** leio tooltip, **Then** inclui descricao e atalho de teclado (ex: "Nova Historia (Ctrl+N)")

---

### User Story 4 - Status Bar com Contadores e Avisos (Priority: P2)

O usuario deseja ver estatisticas do backlog e avisos de alocacao de forma permanente na parte inferior da janela, sem ocupar espaco da tabela.

**Why this priority**: Status Bar fornece feedback continuo sobre o estado do backlog sem demandar acao do usuario. Migracao de WarningsPanel para Status Bar libera espaco lateral.

**Independent Test**: Pode ser testado executando uma alocacao e verificando que contadores e avisos aparecem na Status Bar.

**Acceptance Scenarios**:

1. **Given** Status Bar visivel, **When** verifico conteudo a esquerda, **Then** vejo "X historias . Y SP . Ultima alocacao: DD/MM/YYYY HH:MM"
2. **Given** alocacao executada com avisos, **When** verifico Status Bar a direita, **Then** vejo badge com contagem de avisos
3. **Given** avisos detectados, **When** clico no badge de avisos, **Then** popup exibe lista completa de warnings

---

### User Story 5 - ConfigDialog Modal (Priority: P2)

O usuario deseja configurar parametros de alocacao (velocidade, data inicio, max dias ociosos) atraves de um dialog modal acessivel pelo menu, sem ocupar espaco permanente na interface.

**Why this priority**: Configuracao e uma acao ocasional, nao justifica painel permanente. Dialog modal permite interface mais limpa e focada.

**Independent Test**: Pode ser testado abrindo ConfigDialog via menu, alterando valores e verificando que sao aplicados.

**Acceptance Scenarios**:

1. **Given** menu Cadastros, **When** clico em Configuracao, **Then** ConfigDialog abre como modal
2. **Given** ConfigDialog aberto, **When** altero velocidade para 2.5 e clico Aplicar, **Then** valor e usado na proxima alocacao
3. **Given** ConfigDialog com velocidade invalida (0), **When** clico Aplicar, **Then** mensagem de erro exibida, dialog nao fecha

---

### User Story 6 - DependencyDialog Modal (Priority: P2)

O usuario deseja gerenciar dependencias de uma historia atraves de um dialog modal dedicado, com feedback visual para erros de ciclo.

**Why this priority**: Gestao de dependencias e acao focada em uma historia especifica. Dialog modal permite foco total na tarefa.

**Independent Test**: Pode ser testado selecionando historia, abrindo DependencyDialog, adicionando/removendo dependencias e verificando ciclos.

**Acceptance Scenarios**:

1. **Given** historia selecionada, **When** clico com botao direito e seleciono "Dependencias" no menu de contexto, **Then** DependencyDialog abre com titulo "Dependencias: AUTH-001 - Nome da Historia"
2. **Given** DependencyDialog, **When** adiciono dependencia valida, **Then** dependencia aparece na lista "Depende de"
3. **Given** tentativa de criar ciclo, **When** adiciono dependencia ciclica, **Then** fundo fica vermelho claro com mensagem explicativa

---

### User Story 7 - MetricsDialog Auto-Show Pos-Alocacao (Priority: P3)

O usuario deseja ver automaticamente as metricas da alocacao apos execucao bem-sucedida, sem precisar navegar para encontrar os resultados.

**Why this priority**: Auto-show de metricas fornece feedback imediato sobre resultado da alocacao. Nao e critico para funcionamento mas melhora experiencia.

**Independent Test**: Pode ser testado executando alocacao bem-sucedida e verificando que MetricsDialog surge automaticamente.

**Acceptance Scenarios**:

1. **Given** alocacao executada com sucesso, **When** processo completa, **Then** MetricsDialog abre automaticamente com metricas
2. **Given** MetricsDialog aberto, **When** verifico conteudo, **Then** vejo: Historias Alocadas, Tempo, Ondas, Iteracoes, Deadlocks, Violacoes
3. **Given** alocacao com erro, **When** processo falha, **Then** MetricsDialog NAO abre, apenas mensagem de erro

---

### User Story 8 - Integracao de Delegates na Tabela (Priority: P3)

O usuario deseja ver colunas da tabela formatadas de forma profissional: IDs em fonte monospace e Status como badges coloridos.

**Why this priority**: Delegates melhoram legibilidade e estetica da tabela, mas funcionalidade existe sem eles.

**Independent Test**: Pode ser testado verificando que coluna ID usa fonte monospace e coluna Status renderiza badges coloridos.

**Acceptance Scenarios**:

1. **Given** tabela de historias, **When** verifico coluna ID, **Then** texto renderizado em fonte monospace (JetBrains Mono ou fallback)
2. **Given** tabela de historias, **When** verifico coluna Status, **Then** status renderizado como badge colorido com simbolo (ex: "CONCLUIDO" com checkmark)

---

### Edge Cases

- O que acontece quando nao ha historias no backlog? Status Bar deve exibir "0 historias . 0 SP . Sem alocacao"
- O que acontece quando popup de avisos excede altura da tela? Popup deve ter scroll interno
- Como sistema trata resolucao menor que 1366x768? Interface deve degradar gracefully com scroll se necessario
- O que acontece se icone SVG nao existir? QIcon vazio usado como fallback, botao funciona sem icone
- O que acontece se MetricsDialog for fechado durante alocacao em progresso? Dialog nao deve abrir, apenas ao final
- Durante execução de alocação, indicador de progresso existente do EP-008 é preservado
- O que acontece quando há 0 avisos? Badge de warnings é ocultado completamente (exibido apenas quando existem avisos)

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE exibir Menu Bar com 4 menus: Arquivo, Cadastros, Ferramentas, Ajuda
- **FR-002**: Menu Arquivo DEVE conter: Importar Excel (Ctrl+I), Exportar Excel (Ctrl+E), Sair
- **FR-003**: Menu Cadastros DEVE conter: Nova História (Ctrl+N), Features, Desenvolvedores, Configuração
- **FR-004**: Menu Ferramentas DEVE conter: Calcular Cronograma (Ctrl+Shift+C), Alocar Desenvolvedores (Ctrl+Shift+A)
- **FR-005**: Menu Ajuda DEVE conter: Sobre (implementacao em EP-022)
- **FR-006**: Sistema DEVE exibir Toolbar com icones SVG + texto ao lado de cada botao
- **FR-007**: Toolbar DEVE ter 5 grupos com separadores visuais: CRUD (Nova, Editar, Deletar), Priorizacao (Mover Cima, Mover Baixo), Cadastros (Desenvolvedores, Features, Configuracao), Processamento (Calcular Cronograma, Alocar Devs), Excel (Importar, Exportar)
- **FR-008**: Tooltips de botoes DEVEM incluir atalho de teclado (ex: "Nova Historia (Ctrl+N)")
- **FR-009**: Sistema DEVE exibir Status Bar com contadores a esquerda e area de avisos a direita
- **FR-010**: Contadores da Status Bar DEVEM exibir: "X historias . Y SP . Ultima alocacao: DD/MM/YYYY HH:MM"
- **FR-011**: Area de avisos da Status Bar DEVE exibir badge com contagem e popup ao clicar (badge oculto quando contagem é 0)
- **FR-012**: Sistema DEVE usar layout vertical QVBoxLayout com 5 zonas empilhadas
- **FR-013**: Zonas do layout DEVEM ter alturas: Menu Bar (~28px), Toolbar (44px), Barra Filtros (36px placeholder), Tabela (stretch), Status Bar (24px)
- **FR-014**: QSplitter horizontal DEVE ser removido, tabela ocupando 100% da largura
- **FR-015**: ConfigDialog DEVE ser modal, tamanho 420x340px, com campos: Velocidade (0.1-10.0 SP/dia), Data Inicio, Max Dias Ociosos (2-30)
- **FR-016**: ConfigDialog DEVE ter botoes Aplicar e Cancelar
- **FR-017**: DependencyDialog DEVE ser modal, tamanho 500x420px, com titulo dinamico incluindo ID e nome da historia
- **FR-018**: DependencyDialog DEVE exibir secoes "Depende de" (editavel) e "Dependentes" (somente leitura)
- **FR-019**: DependencyDialog DEVE exibir erro de ciclo com fundo vermelho claro e mensagem explicativa
- **FR-020**: MetricsDialog DEVE ser modal, tamanho 440x380px, com grid de metricas da alocacao
- **FR-021**: MetricsDialog DEVE abrir automaticamente apos alocacao bem-sucedida
- **FR-022**: MetricsDialog NAO DEVE abrir se alocacao falhar ou alocar 0 historias
- **FR-023**: StatusBadgeDelegate DEVE ser aplicado na coluna Status da tabela
- **FR-024**: MonospaceDelegate DEVE ser aplicado na coluna ID da tabela
- **FR-025**: Arquivos config_panel.py, dependency_panel.py, metrics_panel.py, warnings_panel.py DEVEM ser mantidos mas removidos de main_window.py
- **FR-026**: Sistema DEVE preservar comportamento de indicação de progresso existente do EP-008 durante execução de alocação
- **FR-027**: Tabela de histórias DEVE exibir menu de contexto (right-click) com opção "Dependências" que abre DependencyDialog

### Key Entities

- **ConfigDialog**: Dialog modal para configuracao de parametros de alocacao (velocidade, data inicio, max dias ociosos)
- **DependencyDialog**: Dialog modal para gestao de dependencias de uma historia especifica
- **MetricsDialog**: Dialog modal para exibicao de metricas pos-alocacao

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das acoes existentes acessiveis via Menu Bar com atalhos de teclado funcionais
- **SC-002**: Tabela de historias ocupa 100% da largura disponivel (sem paineis laterais)
- **SC-003**: Tempo de abertura de qualquer dialog (ConfigDialog, DependencyDialog, MetricsDialog) menor que 100ms
- **SC-004**: Tempo de inicializacao da aplicacao com novo layout menor ou igual a 3 segundos (cold start)
- **SC-005**: Todas as funcionalidades testadas no EP-008 continuam funcionando sem regressão (testes podem ser adaptados para nova arquitetura dialog-based)
- **SC-006**: Layout funcional e utilizavel em resolucao minima 1366x768 sem cortes
- **SC-007**: Cada botao da toolbar exibe icone SVG renderizado corretamente (ou fallback graceful)
- **SC-008**: Status Bar atualiza contadores em tempo real apos operacoes CRUD e alocacao
- **SC-009**: MetricsDialog surge automaticamente em 100% das alocacoes bem-sucedidas
- **SC-010**: Delegates (StatusBadge e Monospace) aplicados corretamente nas colunas ID e Status

---

## Assumptions

1. **Icones SVG disponiveis**: Os icones SVG definidos em EP-017 estao disponiveis no diretorio assets/icons/ (plus.svg, pencil-simple.svg, trash.svg, arrow-up.svg, arrow-down.svg, users.svg, package.svg, gear.svg, calendar-check.svg, shuffle.svg, download-simple.svg, upload-simple.svg)
2. **Design system implementado**: theme.py com DESIGN_TOKENS e STATUS_PALETTE esta disponivel e funcional
3. **Delegates implementados**: StatusBadgeDelegate e MonospaceDelegate estao implementados e testados
4. **Ordem de migracao**: Paineis serao migrados na ordem: ConfigPanel -> DependencyPanel -> MetricsPanel -> WarningsPanel (para Status Bar)
5. **Atalhos de teclado**: Combinacoes de atalhos nao conflitam com atalhos do sistema Windows
6. **Barra de Filtros**: Espaco reservado de 36px sera um QWidget vazio placeholder, funcionalidade em EP-020
7. **Dialog Sobre**: Menu Ajuda > Sobre sera placeholder ate EP-022
