# Feature Specification: EP-008 Interface Grafica

**Feature Branch**: `008-ep008-graphical-interface`
**Created**: 2026-03-03
**Status**: Draft
**Input**: Implementacao da camada de apresentacao (Presentation Layer) completa em PySide6 que integra todas as capacidades ja implementadas (EP-001 a EP-007) em uma interface grafica funcional. Este epico implementa o padrao MVVM com Views, ViewModels, DI Container, Entry Point, e testes de GUI usando pytest-qt e qasync.

## Out of Scope

- **Integracao Excel**: Import/export de dados Excel NAO e parte deste epico (EP-009) - atalhos Ctrl+I e Ctrl+E NAO serao implementados
- **Logica de Negocio**: Use Cases, Services, Entities, Value Objects, Repositories ja implementados em EP-001 a EP-007
- **Novos Requisitos Funcionais**: Este epico NAO cria novos RFs - e um epico de INTEGRACAO de UI para RFs existentes
- **Configuration Entity**: Se necessaria, sera criada minimamente apenas para suportar o ConfigPanel (decisao ADR-007)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Visualizar e Gerenciar Backlog (Priority: P1)

Como Scrum Master, preciso visualizar todas as historias do backlog em uma tabela ordenada por prioridade, para ter visibilidade completa do trabalho planejado.

**Why this priority**: Funcionalidade core - sem a visualizacao do backlog, nenhuma outra operacao faz sentido. MainWindow e StoryTable sao o coracao da aplicacao.

**Independent Test**: Pode ser testado abrindo a aplicacao com um banco de dados contendo historias e verificando que a tabela exibe todas as colunas (ID, Nome, SP, Status, Feature, Dev, Datas) ordenadas por prioridade.

**Acceptance Scenarios**:

1. **Given** backlog com 10 historias cadastradas, **When** abro a aplicacao, **Then** vejo tabela com todas as 10 historias ordenadas por prioridade (menor = mais prioritario)
2. **Given** resolucao de tela 1366x768, **When** visualizo a MainWindow, **Then** interface e utilizavel sem cortes ou scrolls horizontais excessivos
3. **Given** tabela de backlog visivel, **When** observo as colunas, **Then** vejo: ID, Nome, SP, Status, Feature, Desenvolvedor, Data Inicio, Data Fim
4. **Given** aplicacao em cold start, **When** meco o tempo de inicializacao, **Then** interface esta pronta em <= 3 segundos (RNF-PERF-004)

---

### User Story 2 - Criar e Editar Historias via Dialogo (Priority: P1)

Como Scrum Master, preciso criar novas historias e editar existentes atraves de dialogos modais, para manter o backlog atualizado.

**Why this priority**: CRUD de historias e a funcionalidade mais usada diariamente. Sem ela, backlog nao pode ser gerenciado.

**Independent Test**: Pode ser testado clicando em "Nova Historia", preenchendo campos, salvando e verificando que historia aparece na tabela.

**Acceptance Scenarios**:

1. **Given** MainWindow aberta, **When** clico no botao "Nova Historia" ou pressiono Ctrl+N, **Then** dialogo StoryDialog abre com campos para Componente, Nome, SP e Feature
2. **Given** StoryDialog aberto com dados validos (Componente="CORE", Nome="Login", SP=5), **When** clico "Salvar", **Then** historia e criada e aparece na tabela instantaneamente
3. **Given** historia selecionada na tabela, **When** pressiono Enter ou F2, **Then** StoryDialog abre em modo edicao com dados preenchidos
4. **Given** StoryDialog em modo edicao, **When** altero o nome e clico "Salvar", **Then** historia e atualizada e tabela reflete a mudanca
5. **Given** StoryDialog com SP invalido (ex: 7), **When** tento salvar, **Then** sistema exibe mensagem de erro em PT-BR e NAO fecha o dialogo

---

### User Story 3 - Alterar Prioridade de Historias (Priority: P1)

Como Scrum Master, preciso mover historias para cima ou para baixo na prioridade, para refletir mudancas no planejamento.

**Why this priority**: Priorizacao e atividade central do planejamento agil.

**Independent Test**: Pode ser testado selecionando uma historia e pressionando Alt+Up ou Alt+Down para verificar a troca de prioridade.

**Acceptance Scenarios**:

1. **Given** historia com prioridade 3 selecionada, **When** pressiono Alt+Up, **Then** historia passa a ter prioridade 2 e a anterior passa a ter 3
2. **Given** historia com prioridade 3 selecionada, **When** clico no botao "Mover para Cima" na toolbar, **Then** historia passa a ter prioridade 2
3. **Given** historia com prioridade 1 (primeira), **When** pressiono Alt+Up, **Then** nada acontece (ja e a mais prioritaria)
4. **Given** historia com ultima prioridade, **When** pressiono Alt+Down, **Then** nada acontece (ja e a menos prioritaria)

---

### User Story 4 - Deletar Historia com Confirmacao (Priority: P1)

Como Scrum Master, preciso deletar historias do backlog com confirmacao previa, para evitar exclusoes acidentais.

**Why this priority**: Operacao destrutiva requer confirmacao - essencial para integridade dos dados.

**Independent Test**: Pode ser testado selecionando uma historia, pressionando Delete, confirmando no dialogo e verificando que historia foi removida.

**Acceptance Scenarios**:

1. **Given** historia selecionada na tabela, **When** pressiono Delete, **Then** dialogo de confirmacao aparece com nome da historia
2. **Given** dialogo de confirmacao aberto, **When** clico "Confirmar", **Then** historia e removida e tabela atualiza
3. **Given** dialogo de confirmacao aberto, **When** clico "Cancelar", **Then** historia NAO e removida e dialogo fecha
4. **Given** historia A com dependencias de outras historias, **When** deleto A e confirmo, **Then** dependencias sao removidas automaticamente

---

### User Story 5 - Gerenciar Desenvolvedores (Priority: P1)

Como Scrum Master, preciso cadastrar, editar e remover desenvolvedores do time, para manter a equipe atualizada.

**Why this priority**: Sem desenvolvedores cadastrados, alocacao automatica nao funciona.

**Independent Test**: Pode ser testado abrindo DeveloperDialog, adicionando um desenvolvedor, editando seu nome e deletando-o.

**Acceptance Scenarios**:

1. **Given** MainWindow aberta, **When** acesso o menu/botao "Desenvolvedores", **Then** DeveloperDialog abre com lista de desenvolvedores cadastrados
2. **Given** DeveloperDialog aberto, **When** clico "Adicionar" e informo nome "Ana", **Then** desenvolvedor "Ana" aparece na lista
3. **Given** desenvolvedor selecionado na lista, **When** clico "Editar" e altero nome para "Ana Silva", **Then** nome e atualizado na lista
4. **Given** desenvolvedor selecionado, **When** clico "Remover" e confirmo, **Then** desenvolvedor e removido e historias alocadas a ele ficam sem desenvolvedor
5. **Given** campo nome vazio, **When** tento salvar, **Then** sistema exibe erro "Nome e obrigatorio"

---

### User Story 6 - Gerenciar Features e Ondas (Priority: P1)

Como Product Owner, preciso criar features com ondas de entrega e associar historias a elas, para organizar o roadmap.

**Why this priority**: Features e ondas organizam o backlog e determinam ordem de processamento na alocacao.

**Independent Test**: Pode ser testado criando uma feature com onda 1, outra com onda 2, e verificando que ondas sao unicas.

**Acceptance Scenarios**:

1. **Given** MainWindow aberta, **When** acesso o menu/botao "Features", **Then** FeatureDialog abre com lista de features cadastradas
2. **Given** FeatureDialog aberto, **When** clico "Adicionar" e informo Nome="Auth" e Onda=1, **Then** feature "Auth" aparece na lista
3. **Given** Feature "Auth" com onda 1 existente, **When** tento criar feature "Login" com onda 1, **Then** sistema exibe erro "Onda ja existe"
4. **Given** Feature com historias associadas, **When** tento deletar, **Then** sistema exibe erro "Feature possui historias associadas"
5. **Given** StoryDialog aberto, **When** seleciono Feature no dropdown, **Then** historia e associada a feature selecionada

---

### User Story 7 - Gerenciar Dependencias entre Historias (Priority: P1)

Como Scrum Master, preciso definir que uma historia depende de outra, para garantir sequenciamento correto.

**Why this priority**: Dependencias determinam ordem de execucao e sao validadas no cronograma.

**Independent Test**: Pode ser testado selecionando uma historia, abrindo o painel de dependencias, adicionando uma dependencia e verificando que ciclos sao rejeitados.

**Acceptance Scenarios**:

1. **Given** historia selecionada na tabela, **When** visualizo o painel de dependencias, **Then** vejo lista de dependencias (historias das quais depende) e dependentes (historias que dependem dela)
2. **Given** painel de dependencias aberto para historia B, **When** adiciono historia A como dependencia, **Then** B passa a depender de A
3. **Given** A depende de B e B depende de C, **When** tento adicionar C depende de A, **Then** sistema exibe erro "Ciclo de dependencia detectado"
4. **Given** dependencia existente, **When** clico em remover, **Then** dependencia e removida
5. **Given** historia sem feature em onda 1 depende de historia em onda 2, **When** adiciono dependencia, **Then** sistema exibe warning (nao bloqueia, mas alerta)

---

### User Story 8 - Executar Alocacao Automatica (Priority: P1)

Como Scrum Master, preciso executar alocacao automatica de desenvolvedores com um clique, para distribuir trabalho eficientemente.

**Why this priority**: Alocacao automatica e o diferencial do produto - integra todas as capacidades anteriores.

**Independent Test**: Pode ser testado configurando velocidade/data inicio, clicando "Alocar Automaticamente" e verificando que historias recebem desenvolvedores.

**Acceptance Scenarios**:

1. **Given** backlog com historias elegiveis (datas calculadas, sem dev) e desenvolvedores cadastrados, **When** clico "Alocar Automaticamente" ou pressiono Ctrl+Shift+A, **Then** alocacao e executada e historias recebem desenvolvedores
2. **Given** alocacao em execucao (pode levar ate 5s), **When** observo a interface, **Then** feedback visual e mostrado (progress, cursor de espera) e interface permanece responsiva
3. **Given** alocacao completa, **When** visualizo o painel de metricas, **Then** vejo estatisticas: historias alocadas, tempo de execucao, deadlocks detectados
4. **Given** deadlock detectado durante alocacao, **When** visualizo o painel de warnings, **Then** vejo DeadlockWarning com detalhes da onda e historias bloqueadas
5. **Given** ociosidade excessiva detectada, **When** visualizo warnings, **Then** vejo IdlenessWarning ou BetweenWavesIdlenessInfo conforme o caso

---

### User Story 9 - Configurar Parametros de Alocacao (Priority: P2)

Como Scrum Master, preciso configurar velocidade do time, data de inicio e limite de ociosidade, para personalizar a alocacao.

**Why this priority**: Configuracao e necessaria antes da alocacao, mas valores default permitem uso inicial.

**Independent Test**: Pode ser testado alterando os valores no ConfigPanel e executando alocacao para verificar que os novos valores sao usados.

**Acceptance Scenarios**:

1. **Given** ConfigPanel visivel, **When** visualizo os campos, **Then** vejo: Velocidade (SP/dia), Data de Inicio, Dias Maximos de Ociosidade
2. **Given** ConfigPanel com valores default (velocity=2.0, max_idle_days=3), **When** altero velocidade para 3.0, **Then** proxima alocacao usa velocidade 3.0
3. **Given** data de inicio informada, **When** executo alocacao, **Then** cronograma comeca na data informada
4. **Given** max_idle_days=5, **When** alocacao detecta gap de 4 dias, **Then** NAO emite IdlenessWarning (dentro do limite)
5. **Given** max_idle_days invalido (ex: 1 ou 50), **When** tento salvar, **Then** sistema exibe erro de validacao

---

### User Story 10 - Navegar pela Interface com Atalhos de Teclado (Priority: P2)

Como usuario avancado, preciso usar atalhos de teclado para operacoes frequentes, para aumentar produtividade.

**Why this priority**: Atalhos melhoram UX mas nao sao essenciais para funcionalidade basica.

**Independent Test**: Pode ser testado pressionando cada atalho e verificando que a acao correspondente e executada.

**Acceptance Scenarios**:

1. **Given** foco na MainWindow, **When** pressiono Ctrl+N, **Then** StoryDialog abre para nova historia
2. **Given** historia selecionada, **When** pressiono Enter ou F2, **Then** StoryDialog abre para editar historia
3. **Given** historia selecionada, **When** pressiono Delete, **Then** dialogo de confirmacao de exclusao aparece
4. **Given** historia selecionada, **When** pressiono Alt+Up, **Then** prioridade da historia aumenta
5. **Given** historia selecionada, **When** pressiono Alt+Down, **Then** prioridade da historia diminui
6. **Given** foco na MainWindow, **When** pressiono Ctrl+Shift+A, **Then** alocacao automatica e executada

---

### User Story 11 - Navegar por Tab e Acessibilidade Basica (Priority: P3)

Como usuario, preciso navegar pela interface usando Tab/Shift+Tab e ter contraste adequado, para acessibilidade basica.

**Why this priority**: Acessibilidade e importante mas nao bloqueia funcionalidade principal.

**Independent Test**: Pode ser testado navegando pela interface apenas com teclado e verificando contraste visual.

**Acceptance Scenarios**:

1. **Given** foco inicial na MainWindow, **When** pressiono Tab repetidamente, **Then** foco move entre elementos interativos em ordem logica
2. **Given** foco em um botao, **When** pressiono Shift+Tab, **Then** foco volta para elemento anterior
3. **Given** botao com icone sem texto, **When** passo mouse sobre ele, **Then** tooltip descritivo aparece em PT-BR
4. **Given** interface renderizada, **When** analiso contraste de texto/fundo, **Then** ratio e >= 4.5:1 (WCAG AA)

---

### Edge Cases

- O que acontece quando nenhum desenvolvedor esta cadastrado? Alocacao retorna com 0 historias alocadas e DeadlockWarning para cada onda.
- O que acontece quando backlog esta vazio? Tabela exibe uma linha com mensagem "Nenhuma historia cadastrada. Pressione Ctrl+N para criar." centralizada.
- O que acontece quando banco de dados nao existe? Sistema cria banco vazio na inicializacao. Ver FR-152: "main() DEVE inicializar banco de dados (SQLiteConnection) e executar migrations se necessario".
- O que acontece quando usuario tenta criar historia com nome vazio? Erro de validacao com mensagem em PT-BR.
- O que acontece quando usuario redimensiona janela abaixo de 1366x768? Layout adapta-se ou mostra scrollbar horizontal.
- O que acontece quando operacao de banco falha? Erro e capturado, transacao e revertida, mensagem e exibida ao usuario, aplicacao NAO crasha.
- O que acontece durante alocacao se usuario tenta outra operacao? Botao de alocacao fica desabilitado durante execucao.

## Requirements *(mandatory)*

### Functional Requirements

#### MainWindow - Janela Principal

- **FR-001**: Sistema DEVE implementar `MainWindow(QMainWindow)` em `src/backlog_manager/presentation/views/main_window.py`
- **FR-002**: MainWindow DEVE conter toolbar com botoes: Nova Historia, Editar, Deletar, Mover Cima, Mover Baixo, Desenvolvedores, Features, Alocar Automaticamente
- **FR-003**: MainWindow DEVE conter tabela de backlog como widget central ocupando maior parte do espaco
- **FR-004**: MainWindow DEVE conter painel lateral direito com: DependencyPanel, MetricsPanel, WarningsPanel, ConfigPanel
- **FR-005**: MainWindow DEVE usar QSplitter para permitir redimensionamento entre tabela e paineis laterais
- **FR-006**: MainWindow DEVE ter titulo "Backlog Manager" em portugues
- **FR-007**: MainWindow DEVE ter tamanho inicial de 1280x720 e minimo de 1024x600
- **FR-008**: MainWindow DEVE ser funcional em resolucao 1366x768 (RNF-USAB-002)

#### StoryTableModel - Modelo da Tabela de Backlog

- **FR-010**: Sistema DEVE implementar `StoryTableModel(QAbstractTableModel)` em `src/backlog_manager/presentation/viewmodels/story_table_model.py`
- **FR-011**: StoryTableModel DEVE expor colunas: ID, Nome, SP, Status, Feature, Desenvolvedor, Data Inicio, Data Fim
- **FR-012**: StoryTableModel DEVE ordenar dados por prioridade (menor = mais prioritario)
- **FR-013**: StoryTableModel DEVE emitir signal `dataChanged` quando dados sao atualizados
- **FR-014**: StoryTableModel DEVE usar StoryOutputDTO como fonte de dados

#### StoryTableView - Visualizacao da Tabela

- **FR-020**: Sistema DEVE implementar `StoryTableView(QTableView)` em `src/backlog_manager/presentation/views/story_table_view.py`
- **FR-021**: StoryTableView DEVE conectar ao StoryTableModel
- **FR-022**: StoryTableView DEVE permitir selecao de linha unica
- **FR-023**: StoryTableView DEVE emitir signals para acoes: `story_selected(str)`, `story_double_clicked(str)`
- **FR-024**: StoryTableView DEVE redimensionar colunas proporcionalmente ao espaco disponivel

#### StoryDialog - Dialogo de Historia

- **FR-030**: Sistema DEVE implementar `StoryDialog(QDialog)` em `src/backlog_manager/presentation/views/story_dialog.py`
- **FR-031**: StoryDialog DEVE conter campos: Componente (QLineEdit), Nome (QLineEdit), Story Points (QComboBox com 3,5,8,13), Feature (QComboBox opcional)
- **FR-032**: StoryDialog DEVE operar em dois modos: criacao e edicao
- **FR-033**: Em modo edicao, StoryDialog DEVE preencher campos com dados existentes
- **FR-034**: StoryDialog DEVE validar campos antes de salvar (Componente/Nome nao vazios, SP valido)
- **FR-035**: StoryDialog DEVE exibir mensagens de erro inline ou via QMessageBox em PT-BR
- **FR-036**: StoryDialog DEVE ter botoes "Salvar" e "Cancelar"
- **FR-037**: StoryDialog DEVE ter titulo "Nova Historia" ou "Editar Historia" conforme modo

#### DeveloperDialog - Dialogo de Desenvolvedores

- **FR-040**: Sistema DEVE implementar `DeveloperDialog(QDialog)` em `src/backlog_manager/presentation/views/developer_dialog.py`
- **FR-041**: DeveloperDialog DEVE exibir lista de desenvolvedores cadastrados
- **FR-042**: DeveloperDialog DEVE ter botoes: Adicionar, Editar, Remover
- **FR-043**: DeveloperDialog DEVE pedir confirmacao antes de remover desenvolvedor
- **FR-044**: DeveloperDialog DEVE validar nome nao vazio ao adicionar/editar
- **FR-045**: DeveloperDialog DEVE usar DeveloperOutputDTO como fonte de dados

#### FeatureDialog - Dialogo de Features

- **FR-050**: Sistema DEVE implementar `FeatureDialog(QDialog)` em `src/backlog_manager/presentation/views/feature_dialog.py`
- **FR-051**: FeatureDialog DEVE exibir lista de features cadastradas (Nome e Onda)
- **FR-052**: FeatureDialog DEVE ter botoes: Adicionar, Editar, Remover
- **FR-053**: FeatureDialog DEVE validar nome nao vazio e onda > 0 e onda unica
- **FR-054**: FeatureDialog DEVE exibir erro DuplicateWaveException em PT-BR
- **FR-055**: FeatureDialog DEVE exibir erro FeatureHasStoriesException em PT-BR se tentar deletar feature com historias

#### DependencyPanel - Painel de Dependencias

- **FR-060**: Sistema DEVE implementar `DependencyPanel(QWidget)` em `src/backlog_manager/presentation/views/dependency_panel.py`
- **FR-061**: DependencyPanel DEVE exibir duas listas: "Depende de" e "Dependentes"
- **FR-062**: DependencyPanel DEVE ter botao "Adicionar Dependencia" que abre seletor de historia
- **FR-063**: DependencyPanel DEVE ter botao "Remover Dependencia" para dependencia selecionada
- **FR-064**: DependencyPanel DEVE exibir erro CyclicDependencyException com caminho do ciclo em PT-BR
- **FR-065**: DependencyPanel DEVE atualizar quando historia selecionada na tabela muda

#### MetricsPanel - Painel de Metricas

- **FR-070**: Sistema DEVE implementar `MetricsPanel(QWidget)` em `src/backlog_manager/presentation/views/metrics_panel.py`
- **FR-071**: MetricsPanel DEVE exibir metricas da ultima alocacao: tempo total, historias alocadas, ondas processadas
- **FR-072**: MetricsPanel DEVE exibir metricas detalhadas: deadlocks detectados, ajustes de data, conflitos resolvidos
- **FR-073**: MetricsPanel DEVE atualizar apos cada execucao de alocacao
- **FR-074**: MetricsPanel DEVE consumir AllocationMetricsDTO

#### WarningsPanel - Painel de Avisos

- **FR-080**: Sistema DEVE implementar `WarningsPanel(QWidget)` em `src/backlog_manager/presentation/views/warnings_panel.py`
- **FR-081**: WarningsPanel DEVE exibir lista de warnings da ultima alocacao
- **FR-082**: WarningsPanel DEVE diferenciar visualmente DeadlockWarning (vermelho/warning) de BetweenWavesIdlenessInfo (cinza/info)
- **FR-083**: WarningsPanel DEVE exibir detalhes do warning ao clicar

#### ConfigPanel - Painel de Configuracao

- **FR-090**: Sistema DEVE implementar `ConfigPanel(QWidget)` em `src/backlog_manager/presentation/views/config_panel.py`
- **FR-091**: ConfigPanel DEVE ter campos: Velocidade (QDoubleSpinBox, min=0.1, default=2.0), Data Inicio (QDateEdit), Max Dias Ociosos (QSpinBox, min=2, max=30, default=3)
- **FR-092**: ConfigPanel DEVE validar valores antes de usar na alocacao
- **FR-093**: ConfigPanel DEVE fornecer valores via propriedades para uso em ExecuteAllocationInputDTO (sem persistencia no MVP conforme ADR-007)

#### ConfirmDeleteDialog - Dialogo de Confirmacao

- **FR-100**: Sistema DEVE implementar `ConfirmDeleteDialog(QDialog)` em `src/backlog_manager/presentation/views/confirm_delete_dialog.py`
- **FR-101**: ConfirmDeleteDialog DEVE exibir mensagem clara do que sera deletado (nome do item)
- **FR-102**: ConfirmDeleteDialog DEVE ter botoes "Confirmar" e "Cancelar"
- **FR-103**: ConfirmDeleteDialog DEVE ser reutilizado para historias, desenvolvedores e features

#### ViewModels - Logica de Apresentacao

- **FR-110**: Sistema DEVE implementar `MainWindowViewModel(QObject)` em `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`
- **FR-111**: MainWindowViewModel DEVE receber use cases no construtor (ListStories, CreateStory, EditStory, DeleteStory, etc)
- **FR-112**: MainWindowViewModel DEVE expor metodos async para todas as operacoes
- **FR-113**: MainWindowViewModel DEVE emitir signals para: stories_changed, error_occurred(str), loading(bool)
- **FR-114**: Sistema DEVE implementar `StoryDialogViewModel(QObject)` para logica do dialogo de historia
- **FR-115**: Sistema DEVE implementar `AllocationViewModel(QObject)` para logica de alocacao com signals: allocation_started, allocation_completed(metrics), allocation_error(str)
- **FR-116**: ViewModels DEVEM capturar excecoes e emitir signal de erro em vez de propagar

#### Atalhos de Teclado

- **FR-120**: Sistema DEVE implementar atalho Ctrl+N para abrir StoryDialog em modo criacao
- **FR-121**: Sistema DEVE implementar atalho Enter ou F2 para editar historia selecionada
- **FR-122**: Sistema DEVE implementar atalho Delete para deletar historia selecionada (com confirmacao)
- **FR-123**: Sistema DEVE implementar atalho Alt+Up para mover prioridade para cima
- **FR-124**: Sistema DEVE implementar atalho Alt+Down para mover prioridade para baixo
- **FR-125**: Sistema DEVE implementar atalho Ctrl+Shift+A para executar alocacao automatica
- **FR-126**: Atalhos DEVEM usar QShortcut ou QAction.setShortcut conforme contexto

#### Integracao asyncio com Qt (qasync)

- **FR-130**: Sistema DEVE usar qasync para integrar asyncio event loop com Qt event loop
- **FR-131**: ViewModels DEVEM chamar use cases async usando `asyncio.ensure_future()` ou `asyncio.create_task()`
- **FR-132**: Thread principal NUNCA DEVE ser bloqueada por operacoes I/O
- **FR-133**: Durante alocacao (ate 5s), sistema DEVE mostrar feedback visual (cursor de espera, botao desabilitado)
- **FR-134**: Sistema DEVE usar decorador ou pattern consistente para metodos async nos ViewModels

#### DI Container e Composicao

- **FR-140**: Sistema DEVE implementar `DIContainer` em `src/backlog_manager/presentation/container.py`
- **FR-141**: DIContainer DEVE instanciar: SQLiteConnection -> SQLiteUnitOfWork -> Use Cases (23) -> ViewModels -> Views
- **FR-142**: DIContainer DEVE ser configurado na funcao main() antes de criar MainWindow
- **FR-143**: DIContainer DEVE ser singleton para garantir instancia unica de UnitOfWork/Connection

#### Entry Point

- **FR-150**: Sistema DEVE implementar `main()` em `src/backlog_manager/presentation/app.py`
- **FR-151**: main() DEVE inicializar QApplication com qasync event loop
- **FR-152**: main() DEVE inicializar banco de dados (SQLiteConnection) e executar migrations se necessario
- **FR-153**: main() DEVE configurar DIContainer
- **FR-154**: main() DEVE criar e mostrar MainWindow
- **FR-155**: main() DEVE ter try/except global para capturar e logar crashes (RNF-CONF-002)
- **FR-156**: Sistema DEVE declarar entry point em pyproject.toml: `backlog-manager = "backlog_manager.presentation.app:main"`
- **FR-157**: Sistema DEVE suportar execucao via `python -m backlog_manager` (criar `__main__.py`)

#### Tratamento de Erros na UI

- **FR-160**: ValueError (validacao de entidade) DEVE exibir QMessageBox.warning com mensagem da excecao em PT-BR
- **FR-161**: BacklogManagerException e subclasses DEVEM exibir QMessageBox.warning com mensagem em PT-BR
- **FR-162**: Excecoes de infraestrutura (I/O, SQLite) DEVEM exibir QMessageBox.critical com mensagem generica + log ERROR
- **FR-163**: Nenhuma excecao DEVE crashar a aplicacao (RNF-CONF-002)
- **FR-164**: Pattern: ViewModel captura excecao -> emite signal de erro -> View conecta signal e exibe dialogo

#### Atualizacao de pyproject.toml

- **FR-170**: Sistema DEVE adicionar `PySide6 = "^6.6.1"` em `[tool.poetry.dependencies]`
- **FR-171**: Sistema DEVE adicionar `qasync = "^0.27.1"` em `[tool.poetry.dependencies]`
- **FR-172**: Sistema DEVE adicionar `pytest-qt = "^4.4"` em `[tool.poetry.group.dev.dependencies]`
- **FR-173**: Sistema DEVE adicionar entry point em `[project.scripts]` ou `[tool.poetry.scripts]`

#### Textos da Interface em PT-BR

- **FR-180**: Todos os titulos de janela DEVEM ser em portugues: "Backlog Manager", "Nova Historia", "Editar Historia", "Desenvolvedores", "Features", "Confirmar Exclusao"
- **FR-181**: Todos os labels de formulario DEVEM ser em portugues: "Componente:", "Nome:", "Story Points:", "Feature:", "Velocidade (SP/dia):", "Data de Inicio:", "Dias Max. Ociosos:"
- **FR-182**: Todos os botoes DEVEM ser em portugues: "Salvar", "Cancelar", "Adicionar", "Editar", "Remover", "Confirmar", "Alocar Automaticamente", "Mover para Cima", "Mover para Baixo"
- **FR-183**: Todos os tooltips DEVEM ser descritivos em portugues
- **FR-184**: Todas as mensagens de erro DEVEM ser em portugues conforme Constituicao §XVI

### Key Entities

- **MainWindow**: Janela principal da aplicacao contendo toolbar, tabela de backlog e paineis laterais. Coordena interacao entre componentes via MainWindowViewModel.
- **StoryTableModel**: Modelo MVC para tabela de backlog. Recebe lista de StoryOutputDTO e expoe dados para QTableView.
- **MainWindowViewModel**: ViewModel principal que contem toda a logica de apresentacao. Recebe use cases no construtor, expoe metodos async e emite signals Qt.
- **StoryDialogViewModel**: ViewModel para dialogo de historia. Valida entrada, chama CreateStory ou EditStory use case.
- **AllocationViewModel**: ViewModel para alocacao. Chama ExecuteAllocation use case, emite signals de progresso e resultado.
- **DIContainer**: Container de injecao de dependencias. Centraliza instanciacao de todo o grafo de objetos.
- **ConfigPanel**: Widget de configuracao. Armazena valores de velocity, start_date, max_idle_days (persistencia conforme ADR-007).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuario consegue visualizar todas as historias do backlog na tabela ordenadas por prioridade ao abrir a aplicacao
- **SC-002**: Usuario consegue criar uma nova historia via dialogo em menos de 30 segundos (tempo de preenchimento + feedback)
- **SC-003**: Usuario consegue editar uma historia existente via dialogo e ver a atualizacao refletida na tabela imediatamente
- **SC-004**: Usuario consegue alterar prioridade de historia via atalhos ou botoes e ver reordenacao na tabela
- **SC-005**: Usuario consegue executar alocacao automatica via botao ou Ctrl+Shift+A e ver desenvolvedores atribuidos as historias
- **SC-006**: Aplicacao inicia em menos de 3 segundos em cold start (RNF-PERF-004)
- **SC-007**: Operacoes CRUD respondem em menos de 100ms (RNF-PERF-002)
- **SC-008**: Alocacao de ate 100 historias completa em menos de 5 segundos com feedback visual (RNF-PERF-001)
- **SC-009**: Interface permanece responsiva durante alocacao (nao congela)
- **SC-010**: Erros sao exibidos ao usuario via dialogo em vez de crashar a aplicacao (RNF-CONF-002)
- **SC-011**: Cenarios de teste CT-001 a CT-005 sao executaveis pela interface grafica
- **SC-012**: Cobertura de testes: ViewModels >= 80%, Views >= 50% (conforme Constituicao §XIV)

## Architectural Decisions

### ADR-001: Integracao asyncio <-> Qt Event Loop via qasync

**Contexto**: PySide6 tem seu proprio event loop (QApplication.exec()). O codigo existente usa async/await em todos os use cases e repositorios. Precisamos integrar os dois loops.

**Opcoes**:
1. qasync (substitui exec() por loop asyncio) - recomendado
2. QThread para operacoes async (mais complexo)
3. asyncio.run() em thread separada com signal/slot

**Decisao**: Opcao 1 - qasync para integracao de event loops

**Justificativa**:
- qasync e biblioteca madura e testada para integracao asyncio/Qt
- Permite usar async/await diretamente nos ViewModels
- Simplifica codigo - nao requer gerenciamento manual de threads
- Compativel com pytest-qt via fixture qeventloop
- Mantem arquitetura consistente com use cases async existentes

### ADR-002: DIContainer Centralizado vs Composicao Manual

**Contexto**: Nao existe container de DI no projeto. Use cases recebem UnitOfWork no construtor. Precisamos decidir como instanciar o grafo de objetos.

**Opcoes**:
1. DIContainer centralizado que instancia UnitOfWork -> Use Cases -> ViewModels (recomendado)
2. Composicao manual na MainWindow
3. Library de DI (dependency-injector, inject)

**Decisao**: Opcao 1 - DIContainer centralizado implementado manualmente

**Justificativa**:
- Grafo de dependencias e conhecido e estatico - nao precisa de framework complexo
- Container proprio permite controle total sobre ciclo de vida
- Mantem projeto sem dependencias externas de DI
- Centraliza composicao na raiz (main) conforme Constituicao §IV
- Facil de testar - pode mockar container inteiro ou componentes individuais

### ADR-003: StoryTable com QTableView + QAbstractTableModel

**Contexto**: Tabela principal de backlog precisa exibir ate 500+ historias com performance adequada.

**Opcoes**:
1. QTableView + QAbstractTableModel customizado (MVC nativo, performante) - recomendado
2. QTableWidget (mais simples, menos performante)
3. QTreeView para agrupamento por feature/wave

**Decisao**: Opcao 1 - QTableView + QAbstractTableModel

**Justificativa**:
- QAbstractTableModel permite renderizacao lazy e melhor performance
- Separacao clara Model-View alinha com MVVM
- Suporta ordenacao e filtragem nativas
- Performance adequada para 500+ linhas
- QTreeView adiciona complexidade desnecessaria para MVP

### ADR-004: ViewModels para Dialogos

**Contexto**: Constituicao §XIX exige MVVM, mas dialogos simples podem ser over-engineering com ViewModel separado.

**Opcoes**:
1. ViewModel separado para todos os componentes
2. ViewModel apenas para MainWindow e StoryTable, logica inline para dialogos simples
3. ViewModel apenas para componentes complexos (MainWindow, Allocation)

**Decisao**: Opcao 1 (parcialmente) - ViewModels para todos os componentes significativos

**Justificativa**:
- MainWindowViewModel, StoryDialogViewModel, AllocationViewModel sao obrigatorios
- DeveloperDialog e FeatureDialog podem ter logica minima inline (validacao basica)
- Dialogos de confirmacao sao puramente visuais - nao precisam de ViewModel
- Mantem testabilidade dos componentes principais
- Pragmatismo sem violar arquitetura

### ADR-005: Tratamento de Erros Padronizado

**Contexto**: RNF-CONF-002 exige que erros NAO crashem a aplicacao e exibam mensagem clara.

**Opcoes**:
1. try/except no ViewModel com signal de erro para View exibir QMessageBox (recomendado)
2. Decorador @error_handler nos metodos de ViewModel
3. Middleware de erros no event loop

**Decisao**: Opcao 1 - try/except no ViewModel com signal de erro

**Justificativa**:
- Pattern simples e explicito
- ViewModel controla logica de apresentacao de erro
- View apenas conecta signal e exibe dialogo
- Decorador pode esconder logica importante
- Middleware adiciona complexidade desnecessaria

### ADR-006: Refresh da Tabela apos Operacoes

**Contexto**: Quando usuario cria/edita/deleta historia, tabela deve atualizar.

**Opcoes**:
1. ViewModel emite signal `stories_changed` e View reconstroi dados (recomendado)
2. View observa UnitOfWork diretamente (viola MVVM)
3. Polling periodico

**Decisao**: Opcao 1 - Signal `stories_changed` do ViewModel

**Justificativa**:
- Mantem separacao View/ViewModel
- Fluxo claro: usuario Salvar -> ViewModel chama use case -> use case persiste -> ViewModel busca lista atualizada -> ViewModel emite signal -> View atualiza
- Reativo e eficiente
- Alinha com padrao Qt de signals/slots

### ADR-007: Persistencia de Configuracao

**Contexto**: RNF-USAB / RF-SCHED-001 / RF-ALOC-009 exigem configuracao de velocity, start_date e max_idle_days. NAO existe entidade Configuration no codigo atual. Constituicao §XVIII define Configuration como entidade persistida em SQLite.

**Opcoes**:
1. Criar Configuration entity + ConfigurationRepository (mudanca de dominio)
2. ConfigPanel armazena valores em arquivo JSON local
3. Valores passados como parametros sem persistencia (usuario reconfigura cada sessao)

**Decisao**: Opcao 3 para MVP, com interface preparada para Opcao 1

**Justificativa**:
- MVP nao requer persistencia de configuracao - usuario pode informar antes de cada alocacao
- ConfigPanel tera campos editaveis que alimentam ExecuteAllocationInputDTO
- Evita criar entidade de dominio fora do escopo do epico
- Constituicao §XVIII pode ser implementada em epico futuro se necessario
- Interface ja esta preparada - so precisa adicionar persistencia depois

### ADR-008: Layout da MainWindow

**Contexto**: SRS §6.1 mostra MainWindow com StoryTable central. Precisamos definir layout detalhado.

**Opcoes**:
1. QSplitter com tabela a esquerda e paineis empilhados a direita
2. Abas (QTabWidget) para diferentes visoes
3. Layout fixo com toolbar + tabela central + statusbar

**Decisao**: Opcao 1 - QSplitter horizontal com tabela e paineis

**Justificativa**:
- QSplitter permite usuario ajustar proporcao conforme preferencia
- Tabela ocupa ~70% do espaco, paineis ~30%
- Paineis laterais empilhados verticalmente: Dependencies, Config, Metrics, Warnings
- Funciona bem em 1366x768
- Mais flexivel que layout fixo

## Traceability Matrix

### Componentes UI -> RFs do SRS -> Use Cases Consumidos

| Componente UI       | RFs Relacionados           | Use Cases Consumidos                              |
|---------------------|----------------------------|---------------------------------------------------|
| MainWindow          | RF-STORY-005               | ListStories, CalculateSchedule                    |
| StoryDialog         | RF-STORY-001, RF-STORY-002 | CreateStory, EditStory                            |
| StoryTableModel     | RF-STORY-005               | ListStories                                       |
| PriorityButtons     | RF-STORY-006               | MovePriority                                      |
| DeveloperDialog     | RF-DEV-001/002/003/004     | CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers |
| FeatureDialog       | RF-FEAT-001/002/003        | CreateFeature, UpdateFeature, DeleteFeature, ListFeatures |
| DependencyPanel     | RF-DEP-001, RF-DEP-002     | AddDependency, RemoveDependency, GetDependencies, GetDependents |
| AllocationButton    | RF-ALOC-001                | ExecuteAllocation                                 |
| MetricsPanel        | RF-ALOC-011                | ExecuteAllocation (output DTO)                    |
| WarningsPanel       | RF-ALOC-007, RF-ALOC-008   | ExecuteAllocation (output DTO)                    |
| ConfigPanel         | RF-SCHED-001, RF-ALOC-009  | (parametros para ExecuteAllocation)               |
| ConfirmDeleteDialog | RF-STORY-003               | DeleteStory, DeleteDeveloper, DeleteFeature       |

### User Stories -> Requisitos Funcionais

| User Story                          | Requisitos Funcionais                                      |
|-------------------------------------|-----------------------------------------------------------|
| US-1: Visualizar Backlog            | FR-001 a FR-008, FR-010 a FR-014, FR-020 a FR-024        |
| US-2: Criar/Editar Historias        | FR-030 a FR-037, FR-114                                   |
| US-3: Alterar Prioridade            | FR-002 (botoes), FR-123, FR-124                          |
| US-4: Deletar Historia              | FR-100 a FR-103, FR-122                                   |
| US-5: Gerenciar Desenvolvedores     | FR-040 a FR-045                                           |
| US-6: Gerenciar Features            | FR-050 a FR-055                                           |
| US-7: Gerenciar Dependencias        | FR-060 a FR-065                                           |
| US-8: Executar Alocacao             | FR-070 a FR-074, FR-080 a FR-083, FR-115, FR-125         |
| US-9: Configurar Parametros         | FR-090 a FR-093                                           |
| US-10: Atalhos de Teclado           | FR-120 a FR-126                                           |
| US-11: Acessibilidade               | RNF-USAB-003, tooltips em FR-183                          |

## Assumptions

- Todos os Use Cases (23) estao implementados e funcionais conforme EP-001 a EP-007
- Todos os DTOs Pydantic estao implementados e prontos para consumo (22 DTOs)
- SQLiteUnitOfWork gerencia transacoes corretamente com commit/rollback automatico
- Excecoes de dominio estao definidas: BacklogManagerException, CyclicDependencyException, DuplicateWaveException, FeatureHasStoriesException, DeadlockWarning, IdlenessWarning, BetweenWavesIdlenessInfo
- PySide6 6.6.1+ funciona corretamente em Windows 10/11
- qasync 0.27.1+ funciona corretamente com PySide6 6.6.1+
- pytest-qt funciona corretamente com qasync para testes de GUI
- Banco de dados SQLite ja tem schema definido e migrations funcionais
- Logger esta configurado conforme Constituicao §XVII

## Test Scenarios

### Testes Unitarios - ViewModels

1. **test_main_window_viewmodel_load_stories**: ViewModel carrega historias via use case e emite signal
2. **test_main_window_viewmodel_create_story**: ViewModel chama CreateStory e emite stories_changed
3. **test_main_window_viewmodel_edit_story**: ViewModel chama EditStory e emite stories_changed
4. **test_main_window_viewmodel_delete_story**: ViewModel chama DeleteStory e emite stories_changed
5. **test_main_window_viewmodel_move_priority**: ViewModel chama MovePriority e emite stories_changed
6. **test_main_window_viewmodel_error_handling**: ViewModel captura excecao e emite error_occurred
7. **test_story_dialog_viewmodel_validate_empty_name**: ViewModel rejeita nome vazio
8. **test_story_dialog_viewmodel_validate_invalid_sp**: ViewModel rejeita SP invalido
9. **test_allocation_viewmodel_execute**: ViewModel chama ExecuteAllocation e emite allocation_completed
10. **test_allocation_viewmodel_loading_state**: ViewModel emite allocation_started antes e allocation_completed depois
11. **test_story_table_model_column_count**: Model retorna 8 colunas
12. **test_story_table_model_data_display**: Model retorna dados corretos para cada celula

### Testes de Integracao - Views (pytest-qt)

1. **test_main_window_shows_stories**: MainWindow exibe historias na tabela
2. **test_main_window_story_dialog_opens**: Ctrl+N abre StoryDialog
3. **test_main_window_edit_story_on_enter**: Enter abre StoryDialog em modo edicao
4. **test_main_window_delete_story_on_delete**: Delete abre dialogo de confirmacao
5. **test_main_window_move_priority_up**: Alt+Up move prioridade para cima
6. **test_main_window_move_priority_down**: Alt+Down move prioridade para baixo
7. **test_main_window_allocation_button**: Ctrl+Shift+A executa alocacao
8. **test_story_dialog_save_valid**: Salvar com dados validos fecha dialogo
9. **test_story_dialog_cancel**: Cancelar fecha dialogo sem salvar
10. **test_story_dialog_validation_error**: Dados invalidos mostram erro
11. **test_developer_dialog_crud**: CRUD completo de desenvolvedores funciona
12. **test_feature_dialog_crud**: CRUD completo de features funciona
13. **test_dependency_panel_add_remove**: Adicionar e remover dependencias funciona
14. **test_startup_time**: Aplicacao inicia em menos de 3 segundos
15. **test_crud_response_time**: Operacoes CRUD respondem em menos de 100ms

### Cenarios de Teste do SRS (Executaveis pela UI)

#### CT-001: Backlog Completo 20 Historias (via UI)

```
Dado:
  - 20 historias criadas via StoryDialog em 3 features/ondas
  - 3 desenvolvedores cadastrados via DeveloperDialog
  - Dependencias definidas via DependencyPanel
  - velocity = 2 SP/dia, start_date = 2026-03-02 configurados no ConfigPanel

Quando:
  - Usuario clica "Alocar Automaticamente" ou pressiona Ctrl+Shift+A

Entao:
  - Todas 20 historias tem desenvolvedor na tabela
  - MetricsPanel mostra: stories_allocated=20, deadlocks_detected=0
  - WarningsPanel pode mostrar IdlenessWarning conforme gaps
```

#### CT-003: Deadlock por Falta de Desenvolvedores (via UI)

```
Dado:
  - 5 historias criadas via StoryDialog
  - 0 desenvolvedores cadastrados

Quando:
  - Usuario clica "Alocar Automaticamente"

Entao:
  - Tabela mostra historias sem desenvolvedor
  - WarningsPanel mostra DeadlockWarning para cada onda
  - MetricsPanel mostra: stories_allocated=0, deadlocks_detected >= 1
```

#### CT-005: Balanceamento com Tamanhos Diferentes (via UI)

```
Dado:
  - 4 historias: A (SP=13), B (SP=3), C (SP=3), D (SP=3)
  - 2 desenvolvedores: Dev1, Dev2

Quando:
  - Usuario executa alocacao automatica

Entao:
  - Cada desenvolvedor recebe 2 historias (balanceamento por contagem)
  - Tabela mostra distribucao equilibrada
```
