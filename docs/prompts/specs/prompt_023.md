# Prompt: Criar Especificacao Tecnica do EP-023 — Novo Planejamento (Reset de Cronograma e Alocacao)

<role>
Voce e um Especialista em Arquitetura de Software com profundo conhecimento em:
- Clean Architecture com 4 camadas (Presentation -> Infrastructure -> Application -> Domain)
- Domain-Driven Design (DDD) com entidades ricas, servicos de dominio e Unit of Work
- Padrao MVVM aplicado a camada de apresentacao (Views renderizam, ViewModels fornecem dados e logica)
- PySide6/Qt para aplicacoes desktop (QMainWindow, QAction, QToolBar, QMessageBox, dialogs modais)
- Use Cases assincronos com qasync para integracao asyncio <-> Qt event loop
- Repository Pattern com Protocol interfaces no dominio e implementacoes concretas na infraestrutura
- Dependency Injection via DIContainer centralizado com constructor injection
- SQLite como banco de dados com operacoes atomicas via Unit of Work
- Testes de GUI com pytest-qt (widgets, signals, dialogs)
- Design system com DESIGN_TOKENS e QSS centralizado

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001, expandida ate EP-022)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **UI**: PySide6 6.6.1+ com padrao MVVM
- **Async/Qt**: qasync para integracao asyncio <-> Qt event loop
- **Persistencia**: aiosqlite (async SQLite)
- **DTOs**: Pydantic
- **Testes**: pytest + pytest-cov + pytest-asyncio + pytest-qt
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD, MVVM (na Presentation)

### Estado Atual do Codigo (Implementado em EP-001 a EP-022)

**Fluxo de Planejamento Atual (2 etapas manuais):**
1. **Calcular Cronograma** (Ctrl+Shift+C): Chama `CalculateScheduleUseCase` que:
   - Filtra historias elegiveis (status=BACKLOG, story_points validos, sem datas ou recalculate_all=True)
   - Ordena topologicamente (dependencias + prioridade)
   - Para cada historia: calcula `duration = ceil(SP/velocity)`, `start_date`, `end_date`
   - Persiste `duration`, `start_date`, `end_date` no banco via `story_repository.update(story)`

2. **Alocar Desenvolvedores** (Ctrl+Shift+A): Chama `ExecuteAllocationUseCase` que:
   - Busca stories, developers, features, dependencies
   - Filtra historias elegiveis (developer_id=None, start_date!=None, end_date!=None, story_points definido)
   - Agrupa por wave, aloca developers via AllocationService (criterio: LOAD_BALANCING ou DEPENDENCY_OWNER)
   - Persiste `developer_id` no banco via `story_repository.update(story)`

**Dados de Planejamento na Story (campos calculados — NAO inseridos pelo usuario):**
- `duration: int | None` — dias uteis calculados pelo cronograma
- `start_date: date | None` — data de inicio calculada pelo cronograma
- `end_date: date | None` — data de fim calculada pelo cronograma
- `developer_id: int | None` — desenvolvedor alocado pela alocacao automatica

**Dados de Backlog na Story (campos do usuario — NAO devem ser resetados):**
- `id`, `component`, `name`, `story_points`, `priority`, `status`, `feature_id`

**NAO existe funcionalidade de "Novo Planejamento" / Reset:**
- Atualmente, para recomecar o planejamento, o usuario teria que editar cada historia manualmente
- Nao existe use case para limpar dados calculados em lote
- Nao existe botao ou acao para reset de planejamento na UI

**MainWindow (EP-018, expandida ate EP-022):**
- Layout vertical com 5 zonas: Menu Bar, Toolbar, Filter Bar, StoryTableView, Status Bar
- Menu Ferramentas: "Calcular Cronograma" (Ctrl+Shift+C) + "Alocar" (Ctrl+Shift+A)
- Toolbar Grupo 4: botao "Cronograma" (icone schedule) + botao "Alocar" (icone shuffle)
- `_on_calculate_schedule()`: valida config, chama `_execute_schedule_calculation()` async
- `_on_allocate()`: valida config, chama `_execute_allocation()` async com ProgressDialog
- Apos cada operacao, chama `await self._viewmodel.load_stories()` para atualizar tabela
- Status bar exibe: "{N} historias · {SP} SP · Ultima alocacao: {datetime}"
- `_last_allocation_time` rastreia timestamp da ultima alocacao

**DIContainer (container.py):**
- Factory methods existentes: `create_calculate_schedule_use_case(uow)`, `create_execute_allocation_use_case(uow)`, etc.
- Padrao de registro: `def create_X_use_case(self, uow: SQLiteUnitOfWork) -> XUseCase: return XUseCase(uow)`
- ViewModels singleton: `schedule_viewmodel`, `allocation_viewmodel`, `config_dialog_viewmodel`

**ScheduleViewModel:**
- Signals: `started`, `completed(CalculateScheduleOutputDTO)`, `error_occurred(str)`
- Metodo `execute(velocity, start_date)` async

**AllocationViewModel:**
- Signals: `started`, `completed(AllocationMetricsDTO)`, `warnings_updated(list)`, `cancelled`
- Metodo `execute(velocity, start_date, max_idle_days)` async

**StoryRepository (story_repository.py):**
- `async def update(story: Story) -> None` — atualiza todos os campos da story no banco
- `async def get_all() -> Sequence[Story]` — retorna todas as stories
- Story entity usa `object.__setattr__()` para modificar campos (frozen dataclass)

**ConfigDialogViewModel:**
- Propriedades: `velocity`, `start_date`, `max_idle_days`
- Metodo `validate() -> tuple[bool, str]`
- Valores persistidos via QSettings entre sessoes

**Icones SVG disponiveis em `assets/icons/`:**
- plus.svg, pencil-simple.svg, trash.svg, x.svg, warning-triangle.svg, users.svg, shuffle.svg, schedule.svg, gear.svg, import.svg, export.svg, arrows-down-up.svg, copy.svg, funnel.svg, magnifying-glass.svg, list.svg

**Design system (EP-017):**
- `theme.py`: DESIGN_TOKENS (~70 tokens), STATUS_PALETTE, `apply_theme()`, `get_icon_manager()`
- `stylesheet.qss`: stylesheet centralizado (~17KB)
- Cores semanticas: primary, error-{bg,fg}, warning-{bg,fg}, success-{bg,fg}, info-{bg,fg}

**StoryOutputDTO:**
- Campos: `id`, `component`, `name`, `story_points`, `priority`, `status`, `duration`, `start_date`, `end_date`, `developer_id`, `feature_id`, `developer_name`, `feature_name`, `wave`, `dependency_ids`

**Testes existentes para cronograma/alocacao:**
- `tests/unit/application/use_cases/scheduling/` — testes do CalculateScheduleUseCase
- `tests/unit/application/use_cases/allocation/` — testes do ExecuteAllocationUseCase
- `tests/unit/presentation/viewmodels/` — testes de schedule_viewmodel, allocation_viewmodel

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Escopo do reset — apenas campos calculados ou tambem status?**: O reset deve limpar `duration`, `start_date`, `end_date`, `developer_id` (campos calculados). A questao e se `status` tambem deve ser resetado para BACKLOG. Stories com status EXECUCAO, TESTES ou CONCLUIDO podem indicar trabalho real ja iniciado. A spec deve definir: (a) se reseta apenas campos calculados (duration, start_date, end_date, developer_id), (b) se tambem reseta status para BACKLOG, (c) se oferece opcao ao usuario (checkbox "Resetar status para Backlog"), (d) como tratar stories com status CONCLUIDO (ignorar? incluir no reset?).

2. **Atomicidade da operacao de reset**: O reset modifica multiplas stories no banco. Se falhar no meio, pode deixar o backlog inconsistente (algumas stories resetadas, outras nao). A spec deve definir: (a) se usa transacao atomica (todas ou nenhuma), (b) como lidar com falhas parciais, (c) se Unit of Work ja garante atomicidade.

3. **Confirmacao do usuario antes do reset**: Reset e uma operacao destrutiva (perde dados calculados). A spec deve definir: (a) dialog de confirmacao com descricao clara do que sera resetado, (b) se mostra preview (ex: "X historias terao datas removidas, Y historias terao desenvolvedores desalocados"), (c) se e reversivel (pode desfazer?) — provavelmente nao, entao o aviso deve ser claro.

4. **Posicao do botao "Novo Planejamento" na UI**: A spec deve definir: (a) se fica no Menu Ferramentas (junto com Cronograma e Alocar), (b) se fica na Toolbar (grupo 4 com Cronograma e Alocar), (c) se tem atalho de teclado, (d) qual icone usar.

5. **Impacto no status bar e estado da UI apos reset**: Apos reset, a status bar deve ser atualizada. A spec deve definir: (a) se `_last_allocation_time` e resetado para None, (b) como a status bar reflete o novo estado, (c) se o SP breakdown e atualizado, (d) se mostra mensagem temporaria de confirmacao.

6. **Interacao com stories nao-elegiveis**: Stories com status != BACKLOG podem ter dados calculados (ex: EXECUCAO com datas). A spec deve definir: (a) se reset afeta TODAS as stories (independente de status), (b) se afeta apenas stories com status BACKLOG, (c) se oferece opcao ao usuario.

7. **Relacao com operacoes em andamento**: Se cronograma ou alocacao estiver em execucao, o reset nao deve ser permitido. A spec deve definir: (a) desabilitar botao durante operacoes, (b) como detectar operacao em andamento (via loading state do ViewModel).

### Alinhamento com Constituicao do Projeto

- **§I Clean Architecture**: Use case na Application layer, repository na Infrastructure, botao/dialog na Presentation. Sem logica de negocio na View.
- **§II DDD**: Reset e uma operacao de dominio sobre entidades Story. Usa repository pattern para persistencia.
- **§IV Dependency Injection**: Novo use case registrado no DIContainer. ViewModel recebe dependencias via construtor.
- **§V SQLite**: Operacao atomica via Unit of Work (transacao). Rollback automatico em caso de falha.
- **§VIII Async**: Use case async (aiosqlite). Integracao com Qt via qasync.
- **§IX Simplicidade**: KISS — um use case, um metodo no ViewModel, um botao na UI. Sem over-engineering.
- **§X Type Hints**: Todos os metodos novos com type hints completas.
- **§XIV Estrategia de Testes**: Testes unitarios para use case (mock repository), testes para ViewModel (signals), testes de integracao (banco real).
- **§XVI Error Handling**: Hierarquia de excecoes existente. Usar BacklogManagerException para erros de dominio.
- **§XIX Padroes UI/UX (MVVM)**: View renderiza botao e dialog, ViewModel executa logica, Use Case opera sobre dados.
- **§XX Validacao e Sanitizacao**: Validar que ha stories para resetar. Confirmacao do usuario antes de executar.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **SRS completo**: `srs.md` — secoes §3.5 RF-SCHED (cronograma), §3.6 RF-ALOC (alocacao), §4.1 RNF-PERF-002 (responsividade UI <= 100ms), §4.3 RNF-CONF-002 (recuperacao de erros: sem crash, mensagens claras, operacoes atomicas), §8.2 (convencoes de nomenclatura)
2. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §II DDD, §IV Dependency Injection, §V SQLite, §VIII Async, §IX Simplicidade, §X Type Hints, §XIV Estrategia de Testes, §XVI Error Handling, §XIX Padroes de UI/UX (MVVM), §XX Validacao e Sanitizacao
3. **CalculateScheduleUseCase**: `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py` — entender o que e calculado e persiste (duration, start_date, end_date)
4. **ExecuteAllocationUseCase**: `src/backlog_manager/application/use_cases/allocation/execute_allocation.py` — entender o que e alocado e persiste (developer_id)
5. **MainWindow atual**: `src/backlog_manager/presentation/views/main_window.py` — verificar menu Ferramentas (acao Cronograma + Alocar), toolbar grupo 4, como handlers sao conectados (_on_calculate_schedule, _on_allocate), padrao async com QTimer.singleShot + asyncio.create_task, atualizacao de status bar
6. **MainWindowViewModel**: `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` — padrao de use case call (create_unit_of_work, factory, execute, load_stories), signals (stories_changed, loading, error_occurred)
7. **ScheduleViewModel**: `src/backlog_manager/presentation/viewmodels/schedule_viewmodel.py` — padrao de signals (started, completed, error_occurred), metodo execute()
8. **AllocationViewModel**: `src/backlog_manager/presentation/viewmodels/allocation_viewmodel.py` — padrao de signals, metodo execute(), cancellation support
9. **StoryRepository**: `src/backlog_manager/infrastructure/database/repositories/story_repository.py` — metodo update(), get_all(), schema da tabela Story (campos duration, start_date, end_date, developer_id)
10. **Story entity**: `src/backlog_manager/domain/entities/story.py` — campos, frozen dataclass, uso de object.__setattr__()
11. **StoryOutputDTO**: `src/backlog_manager/application/dto/story/story_output_dto.py` — campos duration, start_date, end_date, developer_id
12. **DIContainer**: `src/backlog_manager/presentation/container.py` — factory methods para use cases, padrao de registro, viewmodels singleton
13. **Unit of Work**: `src/backlog_manager/infrastructure/database/unit_of_work.py` — padrao async context manager, transacao atomica
14. **Domain exceptions**: `src/backlog_manager/domain/exceptions.py` — hierarquia de excecoes existente
15. **Design system**: `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS, get_icon_manager(), icones disponiveis
16. **Progress Dialog**: `src/backlog_manager/presentation/views/progress_dialog.py` — padrao de dialog de progresso (se necessario para operacao longa)
17. **Confirm Delete Dialog**: `src/backlog_manager/presentation/views/confirm_delete_dialog.py` — padrao de dialog de confirmacao existente (reusar estrutura similar)
18. **Testes existentes**:
    - `tests/unit/application/use_cases/scheduling/` — padrao de testes de use case
    - `tests/unit/application/use_cases/allocation/` — padrao de testes de use case
    - `tests/unit/presentation/viewmodels/` — padrao de testes de viewmodel
    - `tests/integration/presentation/views/` — padrao de testes de view
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-023 — Novo Planejamento (Reset de Cronograma e Alocacao)`.

A especificacao deve cobrir o **ciclo completo** da funcionalidade: desde o botao na UI ate a limpeza dos dados no banco, seguindo Clean Architecture de ponta a ponta.

**Funcionalidade principal:**
O usuario clica em "Novo Planejamento" e o sistema limpa todos os dados de planejamento calculados (duration, start_date, end_date, developer_id) de todas as historias elegiveis, permitindo recomecar o planejamento do zero.

**Componentes a especificar:**

| ID | Componente | Tipo | Camada | Descricao |
|----|------------|------|--------|-----------|
| NP-001 | Botao "Novo Planejamento" | NOVO | Presentation | QAction no menu Ferramentas + Toolbar (grupo 4), com icone, tooltip e atalho de teclado |
| NP-002 | Dialog de Confirmacao | NOVO | Presentation | Dialog modal com aviso claro do que sera resetado, contagem de stories afetadas, botoes [Confirmar] e [Cancelar] |
| NP-003 | ResetPlanningViewModel | NOVO | Presentation | ViewModel com signals (started, completed, error_occurred), metodo execute() async, metodo preview() para contar stories afetadas |
| NP-004 | ResetPlanningUseCase | NOVO | Application | Use case que limpa campos calculados (duration, start_date, end_date, developer_id) de stories elegiveis, em transacao atomica |
| NP-005 | ResetPlanningInputDTO/OutputDTO | NOVO | Application | DTOs com opcoes de reset e resultado (stories_reset, warnings) |
| NP-006 | CountAffectedStoriesUseCase | NOVO | Application | Use case auxiliar para contar stories que serao afetadas (para preview no dialog) |
| NP-007 | Integracao MainWindow | MODIFICACAO | Presentation | Adicionar action, handler, conexao de signals no MainWindow existente |
| NP-008 | Integracao DIContainer | MODIFICACAO | Presentation | Registrar factory methods para novos use cases e ViewModel |
| NP-009 | Atualizacao Status Bar | MODIFICACAO | Presentation | Resetar _last_allocation_time, atualizar SP breakdown, mensagem temporaria |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| ResetPlanningUseCase | Use case na Application layer: busca stories, filtra elegiveis, limpa campos, persiste via repository, retorna contagem |
| CountAffectedStoriesUseCase | Use case auxiliar: conta stories que serao afetadas sem modificar dados (para preview) |
| ResetPlanningInputDTO | DTO de entrada: opcoes de filtro (ex: resetar apenas BACKLOG ou todas) |
| ResetPlanningOutputDTO | DTO de saida: stories_reset (int), warnings (list[str]) |
| ResetPlanningViewModel | ViewModel: signals started/completed/error_occurred, metodos preview() e execute() |
| ConfirmResetDialog | QDialog modal: aviso, contagem de stories afetadas, botoes Confirmar/Cancelar |
| MainWindow handler | _on_new_planning(): valida estado, mostra dialog, executa reset, atualiza UI |
| DIContainer registros | Factory methods: create_reset_planning_use_case(uow), create_count_affected_stories_use_case(uow) |
| Testes unitarios | Suite para use case (mock repo), ViewModel (signals), dialog (pytest-qt) |

**Criterios de aceite que devem ser cobertos:**
- Botao "Novo Planejamento" visivel no menu Ferramentas e na Toolbar
- Clicar no botao exibe dialog de confirmacao com contagem de stories afetadas
- Confirmar executa limpeza atomica de duration, start_date, end_date, developer_id
- Dados do usuario (id, component, name, story_points, priority, feature_id) NAO sao alterados
- Status bar e tabela sao atualizados apos o reset
- Botao desabilitado durante operacoes em andamento (cronograma, alocacao)
- Botao desabilitado quando nao ha stories com dados de planejamento
- Operacao concluida exibe mensagem de sucesso com contagem
- Erro na operacao exibe mensagem de erro sem crash
- Dependencias entre stories NAO sao alteradas
- Operacao e atomica (todas ou nenhuma story resetada)
- Testes existentes continuam passando sem regressao

**IMPORTANTE**: Este epico **nao** modifica logica de calculo de cronograma (CalculateScheduleUseCase), logica de alocacao (ExecuteAllocationUseCase), entidades de dominio (Story, Developer, Feature), servicos de dominio (SchedulingService, AllocationService), configuracao (ConfigDialogViewModel), dependencias entre stories, ou qualquer componente de UI existente alem do que e necessario para adicionar o novo botao. Trabalha com **criacao de novo use case** na Application layer, **novo ViewModel** na Presentation layer, **novo dialog de confirmacao**, e **modificacao minima** do MainWindow e DIContainer para wiring.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo componente deve mapear para requisitos do SRS.
   Incluir matriz: Componente <-> RF/RNF <-> Criterio de Aceite.
   RF-SCHED-001 a RF-SCHED-006 -> NP-004 (campos de cronograma a resetar).
   RF-ALOC-001 -> NP-004 (campo de alocacao a resetar).
   RNF-CONF-002 -> NP-002 (confirmacao), NP-004 (atomicidade), NP-007 (tratamento de erro).
   RNF-PERF-002 -> NP-004 (operacao de reset <= 500ms para backlogs < 500 stories).

2. **Codigo existente como baseline**: Nao redefinir CalculateScheduleUseCase, ExecuteAllocationUseCase,
   AllocationService, SchedulingService, Story entity, StoryRepository, DIContainer (estrutura).
   Especificar apenas **criacao de novos artefatos** e **modificacao minima** para wiring.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Clean Architecture end-to-end**: A spec deve especificar a travessia completa das 4 camadas:
   Presentation (View -> ViewModel) -> Application (Use Case + DTOs) -> Infrastructure (Repository via UoW).
   Nenhuma camada pode pular outra. View NAO chama Use Case diretamente.

5. **Atomicidade via Unit of Work**: O reset deve ocorrer dentro de uma unica transacao.
   Se qualquer update falhar, nenhuma story e resetada. A spec deve definir:
   (a) uso de `async with container.create_unit_of_work() as uow` no ViewModel,
   (b) todas as operacoes dentro do mesmo UoW,
   (c) commit automatico no final (padrao existente do UoW).

6. **Confirmacao antes de operacao destrutiva**: O dialog de confirmacao DEVE:
   (a) mostrar quantas stories serao afetadas (chamando CountAffectedStoriesUseCase),
   (b) descrever claramente o que sera resetado ("Datas, duracoes e alocacoes de X historias serao removidas"),
   (c) ter botao de cancelamento como opcao padrao (foco inicial),
   (d) seguir padrao visual do ConfirmDeleteDialog existente (icone warning, botao destrutivo com cor @error).

7. **Padrao async existente**: O handler deve seguir o padrao ja usado em _on_calculate_schedule:
   (a) QTimer.singleShot(0, lambda: asyncio.create_task(self._execute_X())),
   (b) async def _execute_X() com await no ViewModel,
   (c) signals de started/completed/error para feedback na UI.

8. **Icone e posicao na toolbar**: A spec deve definir:
   (a) posicao no menu Ferramentas (antes de "Calcular Cronograma"),
   (b) posicao na toolbar grupo 4 (antes do botao Cronograma),
   (c) icone a utilizar (avaliar icones existentes ou sugerir novo: ex: arrows-down-up.svg rotacionado, ou novo icone),
   (d) atalho de teclado (sugestao: Ctrl+Shift+N).

9. **Desabilitacao inteligente do botao**: O botao deve ser desabilitado quando:
   (a) nao ha stories carregadas (has_stories == False),
   (b) operacao em andamento (loading == True),
   (c) nenhuma story tem dados de planejamento (nenhuma com duration, start_date, end_date ou developer_id nao-null).
   A spec deve definir como verificar condicao (c) eficientemente.

10. **Atualizacao de estado apos reset**: A spec deve definir:
    (a) chamar `await self._viewmodel.load_stories()` para atualizar tabela,
    (b) resetar `_last_allocation_time = None`,
    (c) atualizar SP breakdown via `_update_sp_breakdown()`,
    (d) mostrar mensagem na status bar ("Planejamento resetado: X historias", timeout 5s),
    (e) emitir `stories_changed` signal.

11. **Testes unitarios para novos componentes**: A spec deve especificar:
    - `test_reset_planning_clears_calculated_fields`: verifica que duration, start_date, end_date, developer_id sao None apos reset
    - `test_reset_planning_preserves_user_data`: verifica que id, component, name, story_points, priority, feature_id NAO sao alterados
    - `test_reset_planning_preserves_dependencies`: verifica que dependencias entre stories NAO sao alteradas
    - `test_reset_planning_atomic_on_failure`: verifica rollback se update falhar
    - `test_reset_planning_empty_backlog`: verifica comportamento com 0 stories
    - `test_reset_planning_no_planning_data`: verifica comportamento quando nenhuma story tem dados calculados
    - `test_count_affected_stories`: verifica contagem correta de stories com dados de planejamento
    - `test_reset_planning_viewmodel_signals`: verifica emissao de started/completed signals
    - `test_confirm_dialog_shows_count`: verifica que dialog exibe contagem correta
    - `test_button_disabled_during_operation`: verifica desabilitacao durante loading

12. **Sem sobreposicao com outros epicos**: Nao especificar:
    - Logica de calculo de cronograma (EP-006)
    - Logica de alocacao (EP-007)
    - Servicos de dominio SchedulingService, AllocationService (EP-006/EP-007)
    - ConfigDialog, configuracao (EP-018/EP-022)
    - Design system, theme, stylesheet base (EP-017)
    - StoryTableModel, delegates, tooltip rico (EP-019/EP-022)
    - FilterProxyModel, busca, filtros (EP-020)
    - Dialogs de CRUD (EP-021)
    - Entidades de dominio, value objects (EP-002)

13. **Consistencia de nomenclatura**: Usar os mesmos nomes de componentes definidos nesta spec
    (NP-001 a NP-009). Nomes de classes e metodos em ingles (ResetPlanningUseCase, not LimparPlanejamentoUseCase).
    Textos de interface em PT-BR sem acentos conforme SRS §8.2.

14. **Idioma**: Todos os textos de interface (labels, tooltips, mensagens de botoes, textos de dialog)
    DEVEM ser em portugues brasileiro sem acentos (conforme SRS §8.2).
    Codigo (classes, metodos, variaveis) DEVE ser em ingles, conforme Constituicao §XV.

15. **Status das stories e o reset**: A spec deve definir claramente quais stories sao afetadas
    pelo reset. Decisao recomendada: resetar campos calculados de TODAS as stories que possuem
    esses campos preenchidos, independente do status. O campo `status` NAO deve ser alterado
    (se a story estava em EXECUCAO, permanece em EXECUCAO — apenas perde datas e alocacao).
    Justificativa: o usuario pode querer replanejar com os mesmos status de progresso.
</rules>
