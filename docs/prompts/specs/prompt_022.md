# Prompt: Criar Especificacao Tecnica do EP-022 — Polimento e UX Avancado

<role>
Voce e um Especialista em UI/UX com PySide6/Qt, com profundo conhecimento em:
- QTableView com custom painting (separadores de grupo, agrupamento visual por secao)
- QFrame popup para tooltips ricos (layout complexo com grid, posicionamento dinamico, sombras)
- QStyledItemDelegate para renderizacao customizada de celulas (icones condicionais, badges)
- QSettings para persistencia de configuracao entre sessoes (INI ou Registry)
- Status Bar (QStatusBar) com widgets customizados e breakdown de metricas
- QDialog modal com layout responsivo e informacoes de aplicacao
- Cancelamento de operacoes assincronas via cancellation tokens/flags com qasync
- Responsividade de layout Qt para resolucoes variadas (ocultar/mostrar colunas, overflow de toolbar)
- Padrao MVVM aplicado a camada de apresentacao (Views renderizam, ViewModels fornecem dados e logica)
- Testes de GUI com pytest-qt (widgets, signals, delegates, resize events)
- Design system com DESIGN_TOKENS e QSS centralizado

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001, expandida em EP-008, EP-017 a EP-021)
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

### Estado Atual do Codigo (Implementado em EP-001 a EP-021)

**MainWindow (EP-018, expandida em EP-019 a EP-021):**
- Layout vertical com 5 zonas: Menu bar, Toolbar, Filter bar (36px), StoryTableView (stretch), Status bar
- Status bar: `_stats_label` (esquerda: "X historias · Y SP · alocacao info") + `_warnings_badge` (direita, oculto)
- `_update_status_bar_stats()` calcula story count, total SP, ultima alocacao
- **NAO possui** breakdown de SP por status (Backlog/Execucao/Concluido)
- **NAO possui** tratamento de resize para ocultar colunas
- Minimo: `setMinimumSize(1024, 600)` ja configurado (MIN_WIDTH=1024, MIN_HEIGHT=600)
- Menu Ajuda → "Sobre" existe mas esta desabilitado (`about_action.setEnabled(False)  # Placeholder EP-022`)
- Dialogs abertos via padrao modal: `dialog = SomeDialog(container, self, ...)` + `dialog.exec()`

**StoryTableModel (EP-019):**
- 13 colunas: Prioridade, Feature, Onda, ID, Componente, Nome, Status, Desenvolvedor, Dependencias, SP, Inicio, Fim, Duracao
- CENTER_COLUMNS = {0, 2, 6, 9, 10, 11, 12}, TOOLTIP_COLUMNS = {1, 5, 7, 8}
- Onda (coluna 2): `story.wave` — exibe int ou "—"
- Dependencias (coluna 8): `story.dependency_ids` — lista separada por virgula ou "—"
- data() suporta DisplayRole, TextAlignmentRole, ToolTipRole, UserRole (story.id)
- **NAO possui** agrupamento visual por onda (separadores entre ondas)
- **NAO possui** dados de bloqueio por dependencia (status das dependencias)
- **NAO possui** suporte a tooltip rico (dados completos para mini-card)

**Delegates existentes (EP-019):**
- `monospace_delegate.py` — coluna ID (fonte monospace)
- `status_badge_delegate.py` — coluna Status (badge colorido com simbolo)
- **NAO existe** blocking_indicator_delegate.py para coluna Dependencias

**ConfigDialog (EP-018, estilizado em EP-021):**
- Campos: velocity (QDoubleSpinBox 0.1-10.0), start_date (QDateEdit), max_idle_days (QSpinBox 2-30)
- Valores em memoria via ConfigDialogViewModel — ADR-007 mantem in-memory
- **NAO possui** QSettings para persistencia entre sessoes
- Tamanho fixo: 420x340px

**Design system (EP-017):**
- `theme.py`: DESIGN_TOKENS (~70 tokens) incluindo:
  - Cores primarias: primary, primary-light, primary-dark, primary-pressed
  - Neutros: neutral-50 a neutral-900 (10 tons)
  - Semanticas: background, surface, border, text, text-secondary, text-muted
  - Status: success-{bg,fg}, warning-{bg,fg}, error-{bg,fg}, info-{bg,fg}
  - Tipografia: font-family, font-family-mono, font-size-{xs,sm,base,md,lg,xl,2xl}, font-weight-{normal,medium,semibold,bold}
  - Espacamento: spacing-0 a spacing-8 (0px a 32px)
  - Bordas: radius-sm(2px), radius-md(4px), radius-lg(8px), radius-full(9999px)
  - Sombras: shadow-sm, shadow-md, shadow-lg
  - Interacao: focus-ring, hover-opacity
- `stylesheet.qss`: stylesheet centralizado (~17KB)
- STATUS_PALETTE: 5 status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) com symbol, bg, fg
- `apply_theme(qss_template, tokens)`: substitui @token-name no QSS
- Icones SVG em `assets/icons/`: plus.svg, pencil-simple.svg, trash.svg, x.svg, warning-triangle.svg, users.svg, etc.

**Progress/Result Dialogs (EP-021):**
- ProgressDialog e ResultDialog criados como componentes estilizados separados
- ProgressDialog: QProgressBar + QLabel de mensagem + objectNames para QSS
- Ja possuem estilizacao basica via QSS

**StoryOutputDTO:**
- Campos relevantes: `wave: int = 0`, `dependency_ids: list[str]`, `developer_id: int | None`, `developer_name: str | None`, `feature_id: int | None`, `feature_name: str | None`

**O que NAO existe (EP-022 deve criar/modificar):**
- Agrupamento visual por onda na tabela (separadores entre ondas com texto "Onda N — Nome")
- Tooltip rico na tabela (QFrame popup com mini-card de dados completos da historia)
- Indicador de bloqueio na coluna Dependencias (icone vermelho/verde/"-")
- Breakdown de SP por status na Status Bar ("120 SP Backlog · 80 SP Execucao · 84 SP Concluido")
- Dialog "Sobre" (menu Ajuda → Sobre: nome, versao, tecnologias, caminho BD)
- Cancelamento de operacoes longas (botao [Cancelar] em progress dialogs >2s)
- Persistencia de configuracao via QSettings (velocidade, data inicio, max_idle_days)
- Responsividade a resize: ocultar colunas se janela <1024px, overflow de toolbar
- blocking_indicator_delegate.py para coluna Dependencias
- about_dialog.py para dialog "Sobre"

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Agrupamento por onda pode conflitar com QSortFilterProxyModel (EP-020)**: O filtro de EP-020 usa QSortFilterProxyModel. Agrupamento visual via separadores no modelo pode ser filtrado/reordenado pelo proxy. A spec deve definir: (a) se implementa agrupamento via custom painting no QTableView (independente do modelo), (b) se implementa via rows de separacao no modelo (risco de conflito com proxy), (c) como garantir que separadores aparecem corretamente apos filtragem/ordenacao.

2. **Tooltip rico (QFrame popup) vs tooltip nativo do Qt**: O tooltip rico requer layout complexo (grid 2 colunas, badges de status, icones). QToolTip nativo nao suporta layout complexo. A spec deve definir: (a) criacao de QFrame customizado posicionado manualmente, (b) gerenciamento de lifecycle (criar/destruir a cada hover vs reutilizar instancia), (c) posicionamento relativo a celula com ajuste para manter dentro dos bounds da janela.

3. **Indicador de bloqueio requer status das dependencias**: O StoryTableModel atual expoe `dependency_ids` (lista de IDs), mas NAO indica se as dependencias estao concluidas ou pendentes. Para mostrar icone vermelho (bloqueada) vs verde (livre), o delegate precisa saber o status de cada dependencia. A spec deve definir: (a) se StoryOutputDTO ganha campo `is_blocked: bool`, (b) se o ViewModel calcula bloqueio localmente comparando dependency_ids com status das historias no modelo, (c) como o delegate acessa essa informacao (via UserRole customizado?).

4. **Breakdown de SP por status na Status Bar — fonte dos dados**: A Status Bar atual recebe dados agregados. Para breakdown por status, precisa de SP agrupados por status. A spec deve definir: (a) se calcula no MainWindow a partir das stories do modelo, (b) se cria metodo no StoryTableModel para calcular breakdown, (c) se cria ViewModel dedicado para Status Bar.

5. **Cancelamento de operacoes assincronas pode deixar dados inconsistentes**: Operacoes de alocacao e import/export modificam dados. Cancelamento no meio pode corromper estado. A spec deve definir: (a) uso de cancellation flags/tokens no qasync, (b) pontos seguros de cancelamento (entre operacoes atomicas, nao no meio), (c) se rollback e necessario apos cancelamento, (d) quais operacoes sao cancelaveis e quais nao (alocacao vs import vs export).

6. **QSettings — escopo e formato de armazenamento**: QSettings usa Registry no Windows por default. A spec deve definir: (a) se usa QSettings.IniFormat para portabilidade, (b) quais chaves salvar (organization/application), (c) quando salvar (ao clicar Aplicar no ConfigDialog), (d) quando restaurar (antes de exibir MainWindow), (e) interacao com ADR-007 que mantem config in-memory — a spec deve conciliar persistencia via QSettings com o padrao existente.

7. **Responsividade: ocultar colunas pode perder informacao sem indicacao**: Se colunas Componente, Onda, Duracao sao ocultas ao resize para <1024px, o usuario pode nao perceber que ha informacao oculta. A spec deve definir: (a) indicador visual de colunas ocultas ("3 colunas ocultas"), (b) se tooltip no header indica colunas ocultas, (c) threshold exato de largura para ocultar (1024px total da janela ou da tabela?).

8. **Dialog "Sobre" — leitura de versao de pyproject.toml**: O dialog "Sobre" deve exibir versao da aplicacao. A spec deve definir: (a) como ler versao em runtime (importlib.metadata.version? leitura direta do pyproject.toml?), (b) se caminho do BD vem do DIContainer ou de configuracao centralizada, (c) se lista tecnologias e estaticamente definida ou dinamica.

### Alinhamento com Constituicao do Projeto

- **§I Clean Architecture**: Todos os componentes na Presentation layer. QSettings na Presentation (nao acessa dominio/infra). Delegates na Presentation.
- **§IV Dependency Injection**: Novos componentes recebem dependencias via construtor. AboutDialog recebe info do container. BlockingIndicatorDelegate recebe dados via model roles.
- **§VIII Async**: Cancelamento de operacoes usa cancellation flags com qasync. Tooltip rico nao bloqueia UI thread.
- **§IX Simplicidade**: Reusar DESIGN_TOKENS existentes. Nao criar abstraces desnecessarias. Delegates simples e focados.
- **§X Type Hints**: Todos os metodos novos com type hints completas.
- **§XIV Estrategia de Testes**: Testes unitarios para calculo de breakdown SP, logica de bloqueio, QSettings read/write. Testes de delegate com pytest-qt.
- **§XIX Padroes UI/UX (MVVM)**: Views renderizam, ViewModels fornecem dados. Tooltip rico: View gerencia QFrame, ViewModel/Model fornece dados. Delegate: renderiza com dados do model.
- **§XX Validacao e Sanitizacao**: QSettings valida valores restaurados (range check em velocity, max_idle_days).
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-022_polimento-ux-avancado.md` — requisitos, escopo, criterios de aceite, especificacao dos componentes UX-005 a UX-011, RSP-001, RSP-002
2. **SRS completo**: `srs.md` — secoes §4.1 RNF-PERF-002 (responsividade UI <= 100ms, <= 500ms com recalculo), §4.2 RNF-USAB-002 (resolucao minima 1366x768), §4.2 RNF-USAB-003 (acessibilidade: contraste 4.5:1, navegacao teclado, tooltips descritivos), §4.2 RNF-USAB-004 (curva de aprendizado <= 15min), §4.3 RNF-CONF-002 (recuperacao de erros: sem crash, mensagens claras, operacoes atomicas), §8.2 (convencoes de nomenclatura: status sem acentos MAIUSCULAS)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §IV Dependency Injection, §VIII Async, §IX Simplicidade, §X Type Hints, §XIV Estrategia de Testes, §XIX Padroes de UI/UX (MVVM), §XX Validacao e Sanitizacao
4. **MainWindow atual**: `src/backlog_manager/presentation/views/main_window.py` — layout 5 zonas, Status Bar (_stats_label, _warnings_badge, _update_status_bar_stats), menu Ajuda com "Sobre" desabilitado, MIN_WIDTH/MIN_HEIGHT, como dialogs sao abertos, resizeEvent
5. **StoryTableModel atual**: `src/backlog_manager/presentation/viewmodels/story_table_model.py` — 13 colunas, COLUMNS, CENTER_COLUMNS, TOOLTIP_COLUMNS, data() com roles, _get_display_value(), wave/dependency exposure
6. **StoryTableView**: `src/backlog_manager/presentation/views/main_window.py` (classe StoryTableView) — resizeEvent, empty state, delegate assignments
7. **ConfigDialog atual**: `src/backlog_manager/presentation/views/config_dialog.py` — campos velocity/start_date/max_idle_days, _load_values(), _on_apply(), viewmodel integration
8. **ConfigDialogViewModel**: `src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py` — propriedades, save(), load(), padrao async
9. **Delegates existentes**:
   - `src/backlog_manager/presentation/delegates/monospace_delegate.py` — padrao de delegate existente
   - `src/backlog_manager/presentation/delegates/status_badge_delegate.py` — padrao de delegate com renderizacao customizada
10. **Design system**:
    - `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS, STATUS_PALETTE, apply_theme()
    - `src/backlog_manager/presentation/theme/stylesheet.qss` — seletores QSS existentes
11. **Progress/Result Dialogs (EP-021)**:
    - Verificar se ProgressDialog ja possui suporte a cancelamento ou se precisa ser estendido
12. **DTOs**:
    - `src/backlog_manager/application/dto/story/story_output_dto.py` — StoryOutputDTO (wave, dependency_ids, developer_id)
13. **DIContainer**: `src/backlog_manager/presentation/container.py` — factory methods disponiveis
14. **Icones SVG disponiveis**: `src/backlog_manager/assets/icons/` — listar icones existentes
15. **pyproject.toml**: Verificar campo version para Dialog "Sobre"
16. **Spec EP-021**: `specs/021-*/spec.md` — verificar ProgressDialog criado, como e usado, se tem cancelamento
17. **Spec EP-019**: `specs/019-*/spec.md` — verificar delegate pattern, StoryTableModel, como columns sao configurados
18. **Spec EP-020**: `specs/020-*/spec.md` — verificar FilterProxyModel, como interage com modelo, se afeta agrupamento visual
19. **Testes existentes**:
    - `tests/unit/presentation/` — testes de viewmodels e delegates
    - `tests/integration/presentation/views/` — testes de views
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-022 — Polimento e UX Avancado (GUI-006)`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: polimento de UX avancado na camada Presentation que completa a experiencia visual e interativa da aplicacao. Este epico **nao cria entidades, value objects, repositorios, services na camada Domain/Application** — trabalha exclusivamente na camada Presentation (Views, ViewModels, Delegates), com wiring a dados ja existentes nos DTOs e modelos.

**Componentes a especificar:**

| ID | Componente | Tipo | Descricao |
|----|------------|------|-----------|
| UX-005 | Agrupamento Visual por Onda | NOVO | Separadores visuais na tabela entre ondas (header de grupo com fundo @neutral-100, texto "Onda N — Nome") |
| UX-006 | Tooltip Rico na Tabela | NOVO | QFrame popup com mini-card: ID, Nome, Status, SP, Feature, Desenvolvedor, Dependencias, Datas. Min 280px largura, radius-xl, shadow-md, aparece apos 300ms hover |
| UX-007 | Indicador de Bloqueio | NOVO | QStyledItemDelegate na coluna Dependencias: icone vermelho (bloqueada), verde (livre), "-" (sem deps) |
| UX-008 | SP por Status na Status Bar | NOVO | Breakdown "120 SP Backlog · 80 SP Execucao · 84 SP Concluido" com tooltip de percentuais |
| UX-009 | Dialog Sobre | NOVO | Menu Ajuda → Sobre: nome, versao (pyproject.toml), tecnologias, caminho BD. ~400x300px |
| UX-010 | Cancelamento de Operacoes | NOVO | Botao [Cancelar] em progress dialogs de operacoes >2s. Abortar, restaurar estado, fechar dialog |
| UX-011 | Persistencia de Config | NOVO | QSettings para salvar/restaurar velocidade, data inicio, max_idle_days. Salvar ao Aplicar, restaurar ao iniciar |
| RSP-001 | Responsividade a Resize | NOVO | Ocultar colunas Componente(4), Onda(2), Duracao(12) se janela <1024px. Overflow de toolbar |
| RSP-002 | Resolucao Minima 1024x600 | NOVO | setMinimumSize ja existe (1024, 600). Validar layout sem sobreposicao em todas as 5 zonas |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| Wave group painting/delegate | Implementacao de separadores visuais entre ondas na tabela (custom painting ou rows de separacao) |
| RichTooltipWidget | QFrame popup com layout grid 2 colunas para tooltip rico, gerenciamento de posicao e lifecycle |
| BlockingIndicatorDelegate | QStyledItemDelegate para coluna Dependencias com icones condicionais |
| StatusBarBreakdown | Widget ou logica para exibir SP por status na Status Bar |
| AboutDialog | QDialog "Sobre" com informacoes da aplicacao |
| ProgressDialog estendido | Botao [Cancelar] e integracao com cancellation flags |
| ConfigDialog + QSettings | Integracao de QSettings para persistencia entre sessoes |
| Responsive column manager | Logica para ocultar/mostrar colunas baseado em largura da janela |
| StoryTableModel estendido | Suporte a dados de bloqueio, agrupamento por onda, dados completos para tooltip |
| Seletores QSS novos | Novos seletores para separadores, tooltip rico, indicador bloqueio, breakdown SP |
| Testes unitarios | Suite para calculo de breakdown SP, logica de bloqueio, QSettings, delegates |

**Criterios de aceite do epico que devem ser cobertos:**
- Separadores visuais entre ondas com texto "Onda N — Nome"
- Tooltip rico aparece apos 300ms de hover com mini-card completo
- Indicadores de bloqueio (vermelho/verde/"-") na coluna Dependencias
- SP por status na Status Bar com tooltip de percentuais
- Dialog "Sobre" acessivel via menu Ajuda
- Cancelamento funcional em operacoes >2s
- Configuracao persistida e restaurada entre sessoes via QSettings
- Layout funcional em 1024x600 sem sobreposicao
- Colunas Componente, Onda, Duracao ocultas se janela <1024px
- Testes existentes continuam passando sem regressao

**IMPORTANTE**: Este epico **nao** cria FilterProxyModel, menu de contexto, barra de busca/filtros (EP-020). **Nao** cria StoryDialog, DeveloperDialog, FeatureDialog, ConfirmDeleteDialog (estilizados em EP-021). **Nao** cria design system base, layout principal, toolbar, menu bar (EP-017/EP-018). **Nao** cria StoryTableModel base, delegates monospace/status badge (EP-019). **Nao** altera logica de dominio, entidades, services ou repositorios. Trabalha exclusivamente em **extensao** de componentes existentes na Presentation layer e **criacao** de novos widgets de UX avancado.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo componente deve mapear para requisitos do SRS.
   Incluir matriz: Componente <-> RNF <-> Criterio de Aceite do Epico.
   RNF-USAB-002 -> RSP-001/RSP-002 (responsividade, resolucao minima).
   RNF-USAB-003 -> UX-006 (tooltips descritivos), UX-007 (indicadores visuais claros).
   RNF-USAB-004 -> UX-011 (configuracao persistida), UX-009 (dialog Sobre).
   RNF-PERF-002 -> UX-006 (tooltip renderiza em <300ms), UX-008 (status bar responsiva).
   RNF-CONF-002 -> UX-010 (cancelamento previne espera infinita).

2. **Codigo existente como baseline**: Nao redefinir theme.py (estrutura base), stylesheet.qss (base),
   StoryDialog, DeveloperDialog, FeatureDialog, ConfirmDeleteDialog (EP-021),
   FilterProxyModel, menu de contexto (EP-020), StoryTableModel base, delegates base (EP-019),
   layout principal, toolbar, menu bar (EP-018), entities, services, repositorios.
   Especificar apenas **extensao de componentes existentes** e **criacao de novos widgets de UX**.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Agrupamento por onda independente do proxy**: A spec deve definir implementacao que
   funcione independente do QSortFilterProxyModel de EP-020. Preferencia: custom painting
   no QTableView (paintEvent ou delegate) que detecta mudancas de onda entre linhas,
   em vez de rows de separacao no modelo. Definir: (a) como detectar mudanca de onda,
   (b) como pintar separador, (c) como funciona com filtros ativos.

5. **Tooltip rico com lifecycle gerenciado**: A spec deve definir:
   (a) QFrame criado como filho da tabela (nao toplevel),
   (b) timer de 300ms no hover antes de exibir,
   (c) destruicao/ocultacao ao mover mouse para outra linha ou fora da tabela,
   (d) posicionamento relativo a celula com ajuste para bounds da janela,
   (e) dados obtidos do modelo via index (nao consulta adicional ao banco).

6. **Indicador de bloqueio com dados do modelo**: A spec deve definir:
   (a) como o StoryTableModel fornece informacao de bloqueio ao delegate,
   (b) se usa UserRole customizado ou se calcula no delegate,
   (c) se StoryOutputDTO precisa de campo adicional (is_blocked) ou se calcula a partir de dependency_ids + status das historias no modelo.

7. **Cancelamento seguro de operacoes**: A spec deve definir:
   (a) quais operacoes sao cancelaveis (alocacao, import, export),
   (b) uso de asyncio.Event ou flag booleana como cancellation token,
   (c) pontos seguros de cancelamento (entre iteracoes atomicas),
   (d) comportamento apos cancelamento (rollback parcial? manter estado anterior?),
   (e) como integrar com ProgressDialog existente (EP-021).

8. **QSettings conciliado com padrao existente**: A spec deve conciliar:
   (a) ADR-007 que mantem config in-memory no ConfigDialogViewModel,
   (b) persistencia via QSettings como camada adicional (salvar ao Aplicar, restaurar ao iniciar),
   (c) quem e responsavel: ConfigDialog salva no QSettings ao Aplicar, MainWindow restaura ao iniciar,
   (d) validacao de valores restaurados (range check para evitar valores corrompidos).

9. **Responsividade com indicacao visual**: A spec deve definir:
   (a) threshold de largura (1024px da janela? da tabela?),
   (b) indicador de colunas ocultas (tooltip ou label sutil),
   (c) como restaurar colunas quando janela volta a ser grande,
   (d) overflow de toolbar quando botoes nao cabem.

10. **Dialog "Sobre" com leitura de versao**: A spec deve definir:
    (a) uso de `importlib.metadata.version("backlog-manager")` para leitura em runtime,
    (b) fallback se metadata nao disponivel (ex: dev mode),
    (c) caminho do BD obtido do DIContainer ou configuracao centralizada,
    (d) layout do dialog (~400x300px) com informacoes estaticas e dinamicas.

11. **Seletores QSS adicionados ao stylesheet existente**: A spec deve listar **todos** os novos
    seletores QSS a adicionar ao stylesheet.qss:
    - Separadores de onda: .wave-separator (fundo @neutral-100, texto @neutral-500)
    - Tooltip rico: #richTooltip (fundo @neutral-0, border @neutral-200, radius-xl, shadow-md)
    - Indicador de bloqueio: estilos no delegate (nao QSS — painting direto)
    - Status bar breakdown: .sp-breakdown (fonte @font-size-sm)
    - Dialog Sobre: QDialog#aboutDialog
    - Progresso cancelavel: QPushButton#btnCancel no ProgressDialog
    A spec deve garantir que novos seletores nao conflitam com existentes.

12. **Testes unitarios para novos componentes**: A spec deve especificar:
    - `test_sp_breakdown_by_status`: calculo correto de SP por status
    - `test_sp_breakdown_empty`: breakdown com 0 historias
    - `test_is_blocked_with_pending_deps`: historia com deps nao concluidas
    - `test_is_blocked_all_deps_done`: historia com todas deps concluidas
    - `test_is_blocked_no_deps`: historia sem dependencias
    - `test_qsettings_save_restore`: salvar e restaurar configuracao
    - `test_qsettings_invalid_values`: valores fora de range restaurados com default
    - `test_column_visibility_on_resize`: colunas ocultas/visiveis baseado em largura
    - `test_about_dialog_version`: versao exibida corretamente
    - `test_tooltip_data_completeness`: todos os campos presentes no tooltip

13. **Sem sobreposicao com outros epicos**: Nao especificar:
    - StoryDialog, DeveloperDialog, FeatureDialog, ConfirmDeleteDialog (EP-021)
    - FilterProxyModel, barra de busca, menu de contexto, atalhos (EP-020)
    - StoryTableModel base, delegates monospace/status badge (EP-019)
    - Layout principal, toolbar, menu bar, design system base (EP-017/EP-018)
    - Logica de dominio, entidades, services, repositorios

14. **Consistencia de nomenclatura**: Usar os mesmos nomes de componentes definidos no epico
    (UX-005 a UX-011, RSP-001, RSP-002). Nomes de classes e metodos em ingles.
    Textos de interface em PT-BR. Status sem acentos em MAIUSCULAS conforme SRS §8.2.

15. **Idioma**: Todos os textos de interface (labels, tooltips, mensagens, textos de botoes)
    DEVEM ser em portugues brasileiro sem acentos (conforme SRS §8.2 para valores internos).
    Codigo (classes, metodos, variaveis) DEVE ser em ingles, conforme Constituicao §XV.

16. **Padrao async para operacoes cancelaveis**: Operacoes cancelaveis devem seguir padrao
    async existente com qasync. Usar `asyncio.CancelledError` ou flag booleana para
    sinalizar cancelamento. Emitir signal ao cancelar. Nao bloquear UI thread.
</rules>
