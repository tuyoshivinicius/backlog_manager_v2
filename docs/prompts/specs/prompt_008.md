# Prompt: Criar Especificacao Tecnica do EP-008

<role>
Voce e um Especialista em UI/UX com PySide6/Qt e padrao MVVM, com profundo conhecimento em:
- Arquitetura MVVM (Model-View-ViewModel) para aplicacoes desktop Qt
- PySide6 widgets (QMainWindow, QDialog, QTableView, QAbstractTableModel, layouts, sinais/slots)
- Integracao de asyncio com Qt event loop via qasync
- Clean Architecture aplicada a camada de apresentacao (Views importam apenas ViewModels e DTOs)
- Testes de GUI com pytest-qt e qasync (fixtures qtbot, qeventloop, waitSignal)
- Acessibilidade basica (WCAG AA, contraste 4.5:1, navegacao por teclado, tooltips)
- Injecao de dependencias e composicao de root na camada de apresentacao
- Responsividade e performance de UI (operacoes assincronas sem bloquear thread principal)
- Design de formularios e dialogos para CRUD com validacao inline

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **UI**: PySide6 6.6.1+ com padrao MVVM
- **Async/Qt**: qasync para integracao asyncio <-> Qt event loop
- **Persistencia**: aiosqlite (async SQLite)
- **DTOs**: Pydantic
- **Testes**: pytest + pytest-cov + pytest-asyncio + pytest-qt
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD (entidades ricas, VOs, servicos de dominio), MVVM (na Presentation)

### Estado Atual do Codigo (Implementado em EP-001 a EP-007)

As camadas de dominio, infraestrutura e aplicacao estao **completamente implementadas**. Todas as 6 capacidades core do produto (Backlog, Features, Desenvolvedores, Dependencias, Cronograma, Alocacao) possuem Use Cases, DTOs e Services funcionais. EP-008 constroi a **camada de apresentacao (UI)** que integra todas estas capacidades em uma interface grafica PySide6.

**Entidades existentes (dominio):**
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com id (str, formato COMPONENTE-NNN), component, name, story_points, priority, status, duration (int | None), start_date (date | None), end_date (date | None), developer_id (int | None), feature_id (int | None).
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com id (auto-increment, int | None), name (max 100, nao vazio).
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com name (max 100, unico, nao vazio), wave (int > 0), id (auto-increment, int | None).

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados do workflow (BACKLOG, PLANEJAMENTO, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)
- `src/backlog_manager/domain/value_objects/brazilian_holidays.py` — `BRAZILIAN_HOLIDAYS_2026_2028` (frozenset[date])

**Domain Services existentes:**
- `src/backlog_manager/domain/services/allocation_service.py` — `AllocationService` com `allocate_stories()` (sincrono, recebe dados como parametros, retorna `AllocationResult`)
- `src/backlog_manager/domain/services/scheduling_service.py` — `SchedulingService` com `calculate_duration()`, `topological_sort()`, `calculate_story_dates()`, etc. (sincrono)
- `src/backlog_manager/domain/services/dependency_service.py` — `DependencyService` com `build_graph()`, `would_create_cycle()`, `validate_wave_dependency()` (sincrono)
- `src/backlog_manager/domain/services/story_service.py` — `StoryService` com `create_story()` (geracao de ID)
- `src/backlog_manager/domain/services/developer_service.py` — `DeveloperService` com `create_developer()`
- `src/backlog_manager/domain/services/feature_service.py` — `FeatureService` com `create_feature()`

**Excecoes existentes:**
- `src/backlog_manager/domain/exceptions/base.py` — `BacklogManagerException`
- `src/backlog_manager/domain/exceptions/allocation.py` — `AllocationException`, `MaxIterationsExceeded`
- `src/backlog_manager/domain/exceptions/dependency.py` — `CyclicDependencyException`, `InvalidWaveDependencyException`
- `src/backlog_manager/domain/exceptions/feature.py` — `DuplicateWaveException`, `FeatureHasStoriesException`
- `src/backlog_manager/domain/exceptions/warnings.py` — `BacklogWarning`, `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo`

**Repository Protocols existentes (em `src/backlog_manager/domain/interfaces/repositories.py`):**
- `StoryRepository(Protocol)` — add, get_by_id, get_all, get_by_status, get_by_developer, get_by_feature, update, delete, exists, get_max_id_number, get_max_priority, get_by_priority, count_by_developer
- `StoryDependencyRepository(Protocol)` — add, remove, get_dependencies, get_dependents, exists, get_all_dependencies, remove_all_for_story
- `DeveloperRepository(Protocol)` — add, get_by_id, get_all, update, delete, exists
- `FeatureRepository(Protocol)` — add, get_by_id, get_by_wave, get_all, update, delete, exists, has_stories, get_by_name
- `UnitOfWork(Protocol)` — stories, developers, features, dependencies, commit, rollback, __aenter__, __aexit__

**Implementacoes SQLite existentes (infrastructure):**
- `src/backlog_manager/infrastructure/database/repositories/story_repository.py`
- `src/backlog_manager/infrastructure/database/repositories/developer_repository.py`
- `src/backlog_manager/infrastructure/database/repositories/feature_repository.py`
- `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py`
- `src/backlog_manager/infrastructure/database/unit_of_work.py` — `SQLiteUnitOfWork`
- `src/backlog_manager/infrastructure/database/sqlite_connection.py`
- `src/backlog_manager/infrastructure/logging/logger_config.py`

**Use Cases existentes (23 use cases em application/use_cases/):**
- Story: CreateStory, EditStory, DeleteStory, DuplicateStory, ListStories, MovePriority, AssignDeveloper
- Developer: CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers
- Feature: CreateFeature, UpdateFeature, DeleteFeature, ListFeatures
- Dependency: AddDependency, RemoveDependency, GetDependencies, GetDependents
- Scheduling: CalculateDuration, CalculateStoryDates, CalculateSchedule
- Allocation: ExecuteAllocation

**DTOs Pydantic existentes (22 DTOs em application/dto/):**
- Story: CreateStoryDTO, EditStoryDTO, StoryOutputDTO
- Developer: CreateDeveloperDTO, UpdateDeveloperDTO, DeleteDeveloperDTO, DeveloperOutputDTO, ListDevelopersDTO
- Feature: CreateFeatureDTO, FeatureOutputDTO, ListFeaturesDTO, UpdateFeatureDTO
- Dependency: AddDependencyDTO, GetDependencyDTO, RemoveDependencyDTO
- Scheduling: CalculateDurationDTO, CalculateScheduleDTO, CalculateStoryDatesDTO
- Allocation: ExecuteAllocationInputDTO, ExecuteAllocationOutputDTO, AllocationMetricsDTO

**Estado da camada Presentation (VAZIA — diretorio existente, sem implementacao):**
- `src/backlog_manager/presentation/__init__.py` — apenas "Presentation layer - Views e ViewModels."
- `src/backlog_manager/presentation/viewmodels/__init__.py` — vazio
- `src/backlog_manager/presentation/views/__init__.py` — vazio

**Estado do DI Container:** NAO EXISTE. Use cases sao instanciados manualmente com UnitOfWork nos use cases.

**Dependencias faltando no pyproject.toml:** PySide6 e qasync NAO estao declarados como dependencias. Apenas pydantic, aiosqlite e aiofiles estao presentes.

**Camadas que EP-008 deve criar:**
- `src/backlog_manager/presentation/views/` — MainWindow, StoryDialog, DeveloperDialog, FeatureDialog, DependencyPanel
- `src/backlog_manager/presentation/viewmodels/` — ViewModels para cada componente de UI (MVVM)
- `src/backlog_manager/presentation/app.py` (ou main.py) — ponto de entrada da aplicacao com composicao de dependencias e event loop qasync
- DI Container ou composicao manual de dependencias na raiz de composicao

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Integracao asyncio <-> Qt event loop**: PySide6 tem seu proprio event loop (QApplication.exec()). O codigo existente usa async/await em todos os use cases e repositorios. -> A spec deve definir como integrar: (a) qasync (recomendado, substitui exec() por loop asyncio), (b) QThread para operacoes async (mais complexo), ou (c) asyncio.run() em thread separada com signal/slot para comunicacao. Detalhar como ViewModels chamam use cases async.

2. **DI Container ou composicao manual**: Nao existe container de DI no projeto. Use cases recebem UnitOfWork no construtor. -> A spec deve definir se (a) cria DIContainer centralizado que instancia UnitOfWork + Use Cases + ViewModels (recomendado), (b) composicao manual na MainWindow, ou (c) usa library de DI (dependency-injector, inject). Detalhar o grafo de dependencias completo.

3. **PySide6 e qasync como dependencias**: Nao estao no pyproject.toml. -> A spec deve incluir adição de `PySide6>=6.6.1` e `qasync>=0.27.1` em `[tool.poetry.dependencies]`, e `pytest-qt` em `[tool.poetry.group.dev.dependencies]`.

4. **StoryTable: QTableView + QAbstractTableModel vs QTableWidget**: Para a tabela principal de backlog com colunas (ID, Nome, SP, Status, Feature, Dev, Datas). -> A spec deve decidir se (a) QTableView + QAbstractTableModel customizado (mais performante, MVC nativo, recomendado), (b) QTableWidget (mais simples, menos performante), ou (c) QTreeView para agrupamento por feature/wave. Considerar performance com 500+ historias.

5. **Separacao View/ViewModel para dialogos**: A Constituicao (§XIX) exige MVVM, mas dialogos simples (StoryDialog, DeveloperDialog) podem ser over-engineering com ViewModel separado. -> A spec deve definir quais componentes TEM ViewModel separado (MainWindow, StoryTable obrigatoriamente) vs quais podem ter logica inline (dialogos simples com validacao basica). Manter pragmatismo sem violar a constituicao.

6. **Tratamento de erros na UI**: RNF-CONF-002 exige que erros NAO crashem a aplicacao e exibam mensagem clara. -> A spec deve definir padrao de tratamento: (a) try/except no ViewModel com signal de erro para View exibir QMessageBox, (b) decorador @error_handler nos metodos de ViewModel, ou (c) middleware de erros no event loop. Detalhar como cada tipo de excecao (ValueError, BacklogManagerException, excecos de infra) e apresentado ao usuario.

7. **ConfigPanel e entidade Configuration**: RNF-USAB / RF-SCHED-001 / RF-ALOC-009 exigem configuracao de velocity, start_date e max_idle_days. Entretanto, NAO existe entidade Configuration nem ConfigurationRepository no codigo. -> A spec deve definir se (a) cria Configuration entity + repository (mudanca de dominio, pode ser escopo de EP-008), (b) ConfigPanel armazena valores em arquivo JSON local (simples, fora do banco), ou (c) valores sao passados como parametros ao executar alocacao (sem persistencia, usuario reconfigura a cada sessao). Considerar que a Constituicao §XVIII define Configuration como entidade persistida em SQLite.

8. **Ponto de entrada da aplicacao (main.py / entry point)**: Nao existe entry point definido em pyproject.toml. -> A spec deve definir: (a) script entry point em `[project.scripts]` (ex: `backlog-manager = "backlog_manager.presentation.app:main"`), (b) `__main__.py` para `python -m backlog_manager`, ou (c) ambos. Detalhar a funcao main() com inicializacao de QApplication, qasync loop, DI container, e MainWindow.

9. **Dialogo de confirmacao para delete**: RF-STORY-003 exige "Confirmar antes de deletar". -> A spec deve definir se (a) QMessageBox.question padrao (simples), (b) dialogo customizado com detalhes do item, ou (c) soft delete com undo. Aplicar para stories, developers e features.

10. **Refresh da tabela apos operacoes**: Quando usuario cria/edita/deleta historia via dialogo, a tabela deve atualizar. -> A spec deve definir mecanismo de refresh: (a) ViewModel emite signal `stories_changed` e View reconstroi dados (recomendado), (b) View observa UnitOfWork diretamente (viola MVVM), ou (c) polling periodico. Detalhar fluxo completo: usuario clica Salvar -> ViewModel chama use case -> use case persiste -> ViewModel emite signal -> View atualiza tabela.

11. **Layout da MainWindow**: SRS §6.1 mostra MainWindow com StoryTable central. -> A spec deve definir layout detalhado: (a) QSplitter com tabela a esquerda e paineis a direita (dependencias, metricas, config), (b) abas (QTabWidget) para diferentes visoes, ou (c) layout fixo com toolbar + tabela central + statusbar. Considerar resolucao 1366x768.

12. **Atalhos de teclado (Apendice B)**: 8 atalhos definidos. -> A spec deve especificar implementacao: QShortcut vs QAction.setShortcut, escopo de cada atalho (global vs widget), e tratamento de conflitos com atalhos do sistema. Nota: Ctrl+I e Ctrl+E sao EP-009 (Import/Export Excel) — nao implementar neste epico.

13. **Operacoes longas e feedback visual**: Alocacao pode levar ate 5s (RNF-PERF-001). -> A spec deve definir como mostrar progresso: (a) QProgressDialog com mensagem, (b) statusbar com spinner, ou (c) botao desabilitado + cursor de espera. Detalhar como a thread principal permanece responsiva durante operacao async.

14. **Idioma da interface**: Toda a interface deve ser em PT-BR (SRS §2.4). -> A spec deve listar todos os textos de UI (titulos de janela, labels de formulario, botoes, tooltips, mensagens de erro) literais em portugues.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-008_interface-grafica.md` — requisitos, escopo, criterios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — secoes §2.4 (Restricoes, idioma PT-BR), §3.1-§3.7 (todos os RFs que a UI deve expor), §4.1 RNF-PERF-002/004, §4.2 RNF-USAB-001 a 004, §4.3 RNF-CONF-001/002, §5 UC-001 a UC-005 (fluxos de usuario na UI), §6.1 (Arquitetura de Camadas — camada de Apresentacao), Apendice B (Atalhos de Teclado)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §IV Dependency Injection, §VIII Programacao Assincrona, §XIV Estrategia de Testes (pytest-qt, qasync), §XIX Padroes de UI/UX (MVVM), §XX Validacao e Sanitizacao de Entrada
4. **Spec de referencia (predecessor)**: `specs/007-ep007-allocation-engine/spec.md` — formato, nivel de detalhe e padrao de User Stories/Acceptance Scenarios esperado
5. **Use Case ExecuteAllocation**: `src/backlog_manager/application/use_cases/allocation/execute_allocation.py` — padrao arquitetural de use case async com UnitOfWork
6. **DTO ExecuteAllocation**: `src/backlog_manager/application/dto/allocation/execute_allocation_dto.py` — padrao de DTOs Pydantic (input/output) que ViewModels consomem
7. **StoryOutputDTO**: `src/backlog_manager/application/dto/story/story_output_dto.py` — DTO que a tabela de backlog deve exibir
8. **DeveloperOutputDTO**: `src/backlog_manager/application/dto/developer/developer_output_dto.py` — DTO para dialogo de desenvolvedores
9. **FeatureOutputDTO**: `src/backlog_manager/application/dto/feature/feature_output_dto.py` — DTO para dialogo de features
10. **AllocationService**: `src/backlog_manager/domain/services/allocation_service.py` — AllocationConfig, AllocationCriteria, AllocationMetrics (estrutura de metricas para painel)
11. **Repository Protocols**: `src/backlog_manager/domain/interfaces/repositories.py` — todas as interfaces que ViewModels/Use Cases consomem
12. **UnitOfWork SQLite**: `src/backlog_manager/infrastructure/database/unit_of_work.py` — implementacao concreta de UnitOfWork para composicao na raiz
13. **SQLiteConnection**: `src/backlog_manager/infrastructure/database/sqlite_connection.py` — para inicializacao do banco na startup
14. **Logger config**: `src/backlog_manager/infrastructure/logging/logger_config.py` — para configuracao de logging na startup
15. **Todos os Use Cases em application/use_cases/**: para mapear quais ViewModels consomem quais use cases
16. **Todos os DTOs em application/dto/**: para mapear quais dados cada componente de UI precisa
17. **pyproject.toml**: para verificar dependencias atuais e adicionar PySide6, qasync, pytest-qt
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-008 — Interface Grafica`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: implementar a camada de apresentacao (Presentation Layer) completa em PySide6 que integra todas as capacidades ja implementadas (EP-001 a EP-007) em uma interface grafica funcional. Este epico nao cria nenhum RF novo — e um epico de **integracao de UI** para RFs ja existentes.

**Componentes de UI a especificar:**

| Componente | Descricao | Use Cases Consumidos | RFs Relacionados |
|------------|-----------|---------------------|------------------|
| MainWindow | Janela principal com toolbar, tabela de backlog, paineis laterais | ListStories, CalculateSchedule, ExecuteAllocation | RF-STORY-005 |
| StoryDialog | Dialogo modal para criar/editar historia | CreateStory, EditStory | RF-STORY-001/002 |
| StoryTableModel | QAbstractTableModel para tabela de backlog | ListStories | RF-STORY-005 |
| PriorityButtons | Botoes mover cima/baixo na toolbar | MovePriority | RF-STORY-006 |
| DeveloperDialog | Dialogo modal para CRUD de desenvolvedores | CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers | RF-DEV-001/002/003/004 |
| FeatureDialog | Dialogo modal para CRUD de features | CreateFeature, UpdateFeature, DeleteFeature, ListFeatures | RF-FEAT-001/002/003 |
| DependencyPanel | Painel para adicionar/remover dependencias | AddDependency, RemoveDependency, GetDependencies, GetDependents | RF-DEP-001/002 |
| AllocationButton | Botao "Alocar Automaticamente" com feedback visual | ExecuteAllocation | RF-ALOC-001 |
| MetricsPanel | Painel com metricas de alocacao (16 campos) | ExecuteAllocation (output DTO) | RF-ALOC-011 |
| WarningsPanel | Painel com DeadlockWarning, IdlenessWarning | ExecuteAllocation (output DTO) | RF-ALOC-007/008 |
| ConfigPanel | Configuracao de velocity, data inicio, max_idle_days | (parametros para ExecuteAllocation e CalculateSchedule) | RF-SCHED-001, RF-ALOC-009 |
| ConfirmDeleteDialog | Dialogo de confirmacao para operacoes destrutivas | DeleteStory, DeleteDeveloper, DeleteFeature | RF-STORY-003 |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| DIContainer / Composicao | Grafo de dependencias: SQLiteConnection -> UnitOfWork -> Use Cases -> ViewModels -> Views |
| Entry Point (main/app.py) | QApplication + qasync event loop + inicializacao de banco + DI + MainWindow.show() |
| pyproject.toml updates | Adicao de PySide6, qasync, pytest-qt como dependencias |
| Atalhos de teclado | 6 atalhos (Apendice B excluindo Ctrl+I e Ctrl+E que sao EP-009) |
| Error handling pattern | Padrao de tratamento de erros na UI: excecao -> ViewModel signal -> View QMessageBox |

**Casos de uso do SRS que ficam completos (executaveis via UI) apos este epico:**
- UC-001: Criar e Priorizar Backlog — fluxo principal inteiro na UI
- UC-002: Executar Alocacao Automatica com Dependencias — fluxo principal inteiro na UI
- UC-003: Detectar e Resolver Deadlock — visualizacao de warnings na UI
- UC-005: Gerenciar Ondas de Entrega — fluxo principal inteiro na UI

**Cenarios de teste que devem ser executaveis via interface:**
- CT-001 a CT-005 — todos executaveis pela UI (manualmente)

**IMPORTANTE**: Este epico **nao** cria logica de negocio, entidades, value objects, repositorios ou use cases. A unica excecao possivel e a criacao de Configuration entity + ConfigurationRepository se a spec decidir que configuracoes devem ser persistidas (conflito #7). Fora isso, EP-008 cria **exclusivamente** a camada de apresentacao: Views, ViewModels, DI container, entry point, e testes de GUI.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo componente de UI deve mapear para um ou mais RFs do SRS.
   Toda funcionalidade RF ja implementada nos Use Cases deve ter representacao na UI. Incluir
   matriz de rastreabilidade: Componente UI <-> RF <-> Use Case <-> DTO.

2. **Codigo existente prevalece como baseline**: Nao redefinir Use Cases, DTOs, Services, Entities
   ou Repositories ja implementados em EP-001 a EP-007. Especificar apenas **novos artefatos**
   da camada de apresentacao (Views, ViewModels, DI Container, Entry Point) e eventuais
   extensoes necessarias.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Padrao MVVM estrito**: Views (QWidget, QDialog, QMainWindow) contem APENAS codigo de UI
   (layout, widgets, conexao de sinais). Logica de apresentacao (formatacao, validacao,
   estado de UI, chamadas a use cases) DEVE ficar em ViewModels. Views NAO DEVEM importar
   de domain ou infrastructure. Views DEVEM importar apenas de viewmodels e application/dto.

5. **Integracao async especificada**: Detalhar como ViewModels chamam Use Cases async:
   - Mecanismo qasync para integrar asyncio com Qt event loop
   - Pattern: ViewModel.method() -> asyncio.ensure_future(coro) via qasync
   - Thread principal NUNCA bloqueada por operacoes I/O
   - Feedback visual durante operacoes longas (alocacao)

6. **Composicao de dependencias completa**: Detalhar o grafo completo de instanciacao:
   SQLiteConnection -> SQLiteUnitOfWork -> Use Cases (todos 23) -> ViewModels -> Views -> MainWindow.
   Especificar se usa DIContainer, factory functions, ou composicao manual no entry point.

7. **Layout e wireframes**: Para cada componente de UI, especificar:
   - Hierarquia de widgets (QVBoxLayout, QHBoxLayout, QSplitter, etc.)
   - Posicao e tamanho relativo dos elementos
   - Comportamento em resolucao 1366x768 (sem cortes, sem scrolls excessivos)
   - Textos literais em PT-BR para todos os labels, botoes, tooltips e titulos

8. **Atalhos de teclado especificados**: Detalhar implementacao dos 6 atalhos (excluindo Ctrl+I e Ctrl+E):
   - Ctrl+N: Nova Historia
   - Enter/F2: Editar Selecionado
   - Delete: Deletar Selecionado
   - Alt+Up: Mover Prioridade Cima
   - Alt+Down: Mover Prioridade Baixo
   - Ctrl+Shift+A: Executar Alocacao
   Especificar QShortcut vs QAction, escopo, e interacao com foco/selecao da tabela.

9. **Tratamento de erros padronizado**: Para cada tipo de excecao que pode ocorrer na UI:
   - `ValueError` (validacao de entidade) -> QMessageBox.warning com mensagem da excecao
   - `BacklogManagerException` e subclasses -> QMessageBox.warning com mensagem em PT-BR
   - Excecoes de infraestrutura (I/O, SQLite) -> QMessageBox.critical com mensagem generica + log ERROR
   - Nenhuma excecao deve crashar a aplicacao (RNF-CONF-002)
   Detalhar pattern de captura: try/except no ViewModel, emissao de signal de erro, View exibe dialogo.

10. **Testabilidade de GUI**: Cada ViewModel deve ser testavel unitariamente sem Qt (mock de use cases).
    Testes de integracao de Views devem usar pytest-qt com qtbot. Especificar:
    - Fixtures de teste (qtbot, qasync event loop, mock UnitOfWork)
    - Exemplo de teste unitario para cada ViewModel principal
    - Exemplo de teste de integracao para cada View principal
    - Views (codigo visual) podem ter cobertura menor (minimo 50% conforme Constituicao §XIV)

11. **Performance e responsividade**: Especificar:
    - Startup ≤ 3s (RNF-PERF-004): o que acontece na inicializacao (QApplication, DB init, DI, MainWindow)
    - CRUD ≤ 100ms (RNF-PERF-002): operacoes simples nao devem ter delay perceptivel
    - Recalculo ≤ 500ms (RNF-PERF-002): adicionar dependencia pode recalcular cronograma
    - Alocacao ≤ 5s (RNF-PERF-001): mostrar feedback visual, thread principal responsiva

12. **Acessibilidade basica**: Especificar:
    - Contraste minimo 4.5:1 (WCAG AA) — definir paleta de cores ou usar tema padrao Qt
    - Navegacao por Tab/Shift+Tab — ordem logica de foco entre widgets
    - Tooltips descritivos em todos os botoes e icones
    - Texts legíveis em resolucao 1366x768

13. **Sem sobreposicao com EP-001 a EP-007 ou EP-009**: Nao re-especificar o que epicos anteriores
    ja entregaram (servicos, use cases, DTOs, repositorios). Nao antecipar integracao Excel
    (EP-009) — atalhos Ctrl+I e Ctrl+E nao devem ser implementados.

14. **Consistencia de nomenclatura**: Usar os mesmos nomes de Use Cases, DTOs e Services ja existentes
    no codigo. ViewModels devem consumir exatamente os DTOs ja definidos. Nao criar DTOs duplicados.

15. **Idioma**: Todos os textos de interface (titulos, labels, botoes, tooltips, mensagens de erro
    exibidas ao usuario) DEVEM ser em portugues brasileiro. Codigo (nomes de classes, metodos,
    variaveis) DEVE ser em ingles, conforme Constituicao §XV.

16. **Entry point e empacotamento**: Especificar entry point em pyproject.toml para que
    `poetry run backlog-manager` ou `python -m backlog_manager` inicie a aplicacao.
    Detalhar funcao main() com try/except global para logging de crashes.
</rules>
