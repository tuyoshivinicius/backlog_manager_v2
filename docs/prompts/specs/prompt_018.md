# Prompt: Criar Especificacao Tecnica do EP-018 — Layout Principal e Migracao de Paineis

<role>
Voce e um Especialista em UI/UX com PySide6/Qt, com profundo conhecimento em:
- Arquitetura de layout Qt (QVBoxLayout, QHBoxLayout, QMenuBar, QToolBar, QStatusBar)
- Refatoracao de interfaces existentes sem quebrar funcionalidade
- QDialog modal para formularios e configuracoes
- Padroes de navegacao desktop (menus com atalhos, toolbar com icones + texto, status bar informativa)
- Integracao de delegates customizados com QTableView
- Padrao MVVM aplicado a camada de apresentacao
- Migracao incremental de paineis para dialogs modais
- Responsividade de layout em diferentes resolucoes (1366x768+)
- Acessibilidade: atalhos de teclado, tooltips com shortcuts, navegacao por Tab
- Testes de GUI com pytest-qt (views refatoradas, novos dialogs)

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001, expandida em EP-008 e EP-017)
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

### Estado Atual do Codigo (Implementado em EP-001 a EP-017)

A camada de apresentacao possui **UI funcional completa** (EP-008) e **design system** (EP-017). A MainWindow atual usa layout horizontal com QSplitter (70% tabela, 30% paineis laterais). **Nao existe** Menu Bar nem Status Bar. A toolbar exibe apenas texto, sem icones e sem agrupamento visual. O design system (theme.py, stylesheet.qss, delegates, icones SVG) foi entregue em EP-017 mas **icones e delegates ainda nao foram integrados** nos componentes.

**Estrutura atual da MainWindow (EP-008):**
- `src/backlog_manager/presentation/views/main_window.py` — QMainWindow com:
  - QToolBar horizontal: botoes de texto (Nova Historia, Editar, Deletar, Mover Cima/Baixo, Desenvolvedores, Features, Calcular Cronograma, Alocar Automaticamente, Importar/Exportar Excel)
  - QSplitter horizontal: StoryTableView (70%) + side panel (30%)
  - Side panel contem: ConfigPanel, DependencyPanel, MetricsPanel, WarningsPanel empilhados
  - Atalhos de teclado implementados via QShortcut e QAction.setShortcut

**Paineis laterais existentes (a migrar para dialogs):**
- `src/backlog_manager/presentation/views/config_panel.py` — ConfigPanel: QGroupBox com inputs de velocity, start_date, max_idle_days
- `src/backlog_manager/presentation/views/dependency_panel.py` — DependencyPanel: secoes "Depende de" e "Dependentes" com listas e botoes
- `src/backlog_manager/presentation/views/metrics_panel.py` — MetricsPanel: grid de metricas de alocacao (16 campos)
- `src/backlog_manager/presentation/views/warnings_panel.py` — WarningsPanel: lista de DeadlockWarning e IdlenessWarning

**Design system implementado (EP-017, pronto para integracao):**
- `src/backlog_manager/presentation/styles/` ou `theme/` — design tokens, apply_theme()
- `src/backlog_manager/presentation/styles/stylesheet.qss` — stylesheet centralizado
- `src/backlog_manager/presentation/delegates/status_badge_delegate.py` — StatusBadgeDelegate
- `src/backlog_manager/presentation/delegates/monospace_delegate.py` — MonospaceDelegate
- `presentation/assets/icons/*.svg` — 16 icones Phosphor Icons (plus, pencil-simple, trash, arrow-up, arrow-down, users, package, gear, calendar-check, shuffle, download-simple, upload-simple, etc.)

**O que NAO existe (EP-018 deve criar):**
- QMenuBar com 4 menus funcionais
- QStatusBar com contadores e area de avisos
- Toolbar com icones SVG + texto + separadores visuais
- Layout vertical de 5 zonas (Menu Bar -> Toolbar -> Barra Filtros -> Tabela -> Status Bar)
- ConfigDialog (migracao de ConfigPanel)
- DependencyDialog (migracao de DependencyPanel)
- MetricsDialog (migracao de MetricsPanel, auto-show pos-alocacao)

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Remocao do QSplitter sem quebrar funcionalidade**: O QSplitter atual conecta tabela e side panel. Ao remover, a logica de resize pode estar acoplada. -> A spec deve verificar que nenhum ViewModel ou UseCase referencia o splitter diretamente. Detalhar o novo layout QVBoxLayout com 5 zonas.

2. **Migracao incremental vs big-bang**: 4 paineis para migrar simultaneamente pode gerar regressao dificil de isolar. -> A spec deve definir ordem de migracao: ConfigPanel -> DependencyPanel -> MetricsPanel -> WarningsPanel (este ultimo migra para Status Bar, nao para dialog). Detalhar testes de regressao apos cada migracao.

3. **MetricsDialog auto-show**: MetricsDialog deve surgir automaticamente apos alocacao bem-sucedida. Se alocacao falhar, nao exibir. -> A spec deve detalhar como o AllocationViewModel sinaliza sucesso vs erro e como MainWindow conecta o signal para abrir MetricsDialog.

4. **Popup de avisos na Status Bar**: Avisos (WarningsPanel atual) devem migrar para area direita da Status Bar com badge de contagem e popup ao clicar. -> A spec deve definir widget QFrame com setWindowFlags(Qt.Popup) ou QMenu, calcular posicao relativa a Status Bar, testar cross-platform e em multiplas resolucoes.

5. **Integracao de icones SVG na toolbar**: Icones do EP-017 estao prontos mas nao integrados. -> A spec deve especificar: carregamento de icones via QIcon com caminho relativo ao pacote, aplicacao em cada QAction da toolbar, tamanho 16x16 ou 24x24px, fallback se icone nao existir.

6. **Toolbar ToolButtonTextBesideIcon**: Botoes devem exibir icone + texto ao lado, nao abaixo. -> A spec deve configurar `toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)` e validar altura de 44px.

7. **5 grupos de toolbar com separadores**: Epico define 5 grupos (CRUD, Priorizacao, Cadastros, Processamento, Excel). -> A spec deve detalhar quais acoes pertencem a cada grupo e onde adicionar `toolbar.addSeparator()`.

8. **Menu Bar com 4 menus e atalhos**: Menus Arquivo, Cadastros, Ferramentas, Ajuda. -> A spec deve listar cada menu, cada acao, atalho de teclado, e como conectar a acoes ja existentes na toolbar (sem duplicar logica).

9. **Status Bar com 3 contadores + area de avisos**: "42 historias . 284 SP . Ultima alocacao: DD/MM/YYYY HH:MM" a esquerda. Avisos a direita. -> A spec deve definir mecanismo de atualizacao dos contadores (signal do ViewModel ou polling?), formato de timestamp, e como sincronizar com warnings.

10. **Barra de Filtros reservada mas vazia**: Layout inclui espaco de 36px para barra de filtros, mas implementacao e EP-020. -> A spec deve criar QWidget placeholder com altura fixa 36px, sem funcionalidade.

11. **ConfigDialog dimensoes e layout**: 420x340px, campos de velocity, start_date, max_idle_days, botoes [Aplicar][Cancelar]. -> A spec deve detalhar validacao de range (velocity 0.1-10.0, max_idle_days 2-30), como valores sao persistidos (Application layer? Local state?), e se herda valores do config_panel.py.

12. **DependencyDialog para historia selecionada**: Titulo dinamico "Dependencias: AUTH-001 — Nome da Historia". Secoes "Depende de" e "Dependentes". -> A spec deve detalhar como DependencyDialog recebe a historia atual, como atualiza apos adicao/remocao, e tratamento de erro de ciclo (fundo @error-light com mensagem).

13. **Deprecacao de paineis antigos**: config_panel.py, dependency_panel.py, metrics_panel.py, warnings_panel.py devem ser mantidos como arquivos mas removidos de main_window.py. -> A spec deve listar imports a remover e garantir que nenhum outro modulo depende deles.

14. **Integracao de delegates na tabela**: StatusBadgeDelegate e MonospaceDelegate do EP-017 devem ser aplicados a StoryTableView. -> A spec deve especificar `table.setItemDelegateForColumn(col_index, delegate)` para colunas ID (monospace) e Status (badge).

15. **Atalhos de teclado em menus**: Todos os atalhos do Apendice B devem estar mapeados nos menus com exibicao do shortcut (ex: "Ctrl+N" ao lado de "Nova Historia"). -> A spec deve usar QAction.setShortcut() e confirmar que atalhos nao conflitam com sistema Windows.

### Alinhamento com Constituicao do Projeto

- **§I Clean Architecture**: Views importam apenas ViewModels e DTOs, dialogs sao Views
- **§IV Dependency Injection**: Dialogs recebem container ou viewmodels via construtor
- **§VIII Programacao Assincrona**: Operacoes de persistencia continuam async, dialogs podem chamar use cases via ViewModel
- **§XIV Estrategia de Testes**: Testes de regressao para MainWindow refatorada, testes unitarios para novos dialogs
- **§XIX Padroes UI/UX (MVVM)**: ConfigDialog, DependencyDialog, MetricsDialog seguem MVVM (ViewModel opcional para dialogs simples)
- **§XXI CI/CD**: Cobertura de testes para novos componentes
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-018_layout-principal-migracao-paineis.md` — requisitos, escopo, criterios de aceite, especificacoes tecnicas detalhadas (layout de 5 zonas, estrutura de menus, grupos de toolbar, Status Bar, dialogs)
2. **SRS completo**: `srs.md` — secoes §4.2 RNF-USAB-002 (resolucao minima 1366x768), §4.2 RNF-USAB-003 (acessibilidade, atalhos), §4.2 RNF-USAB-004 (curva de aprendizado), §4.1 RNF-PERF-002 (responsividade UI <= 100ms), §4.1 RNF-PERF-004 (startup <= 3s), §4.3 RNF-CONF-002 (dialogs nao crasham aplicacao), Apendice B (atalhos de teclado)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §IV Dependency Injection, §VIII Programacao Assincrona, §XIV Estrategia de Testes, §XIX Padroes de UI/UX (MVVM)
4. **Spec de referencia (EP-008)**: `specs/008-ep008-interface-grafica/spec.md` ou consultar implementacao atual — formato, nivel de detalhe esperado
5. **MainWindow atual**: `src/backlog_manager/presentation/views/main_window.py` — estrutura atual com QSplitter, toolbar, conexao de signals, metodos de handler
6. **Paineis a migrar**:
   - `src/backlog_manager/presentation/views/config_panel.py` — ConfigPanel
   - `src/backlog_manager/presentation/views/dependency_panel.py` — DependencyPanel
   - `src/backlog_manager/presentation/views/metrics_panel.py` — MetricsPanel
   - `src/backlog_manager/presentation/views/warnings_panel.py` — WarningsPanel
7. **ViewModels relacionados**:
   - `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` — ViewModel principal
   - `src/backlog_manager/presentation/viewmodels/allocation_viewmodel.py` — signals de alocacao (para MetricsDialog auto-show)
8. **Design system (EP-017)**:
   - `src/backlog_manager/presentation/styles/theme.py` ou `theme/theme.py` — design tokens
   - `src/backlog_manager/presentation/styles/stylesheet.qss` — stylesheet centralizado
   - `src/backlog_manager/presentation/delegates/status_badge_delegate.py` — StatusBadgeDelegate
   - `src/backlog_manager/presentation/delegates/monospace_delegate.py` — MonospaceDelegate
9. **Assets de icones**: `src/backlog_manager/presentation/assets/icons/*.svg` — verificar quais icones existem
10. **Container DI**: `src/backlog_manager/presentation/container.py` — DIContainer para injecao em novos dialogs
11. **Entry point**: `src/backlog_manager/presentation/app.py` — inicializacao e aplicacao de stylesheet
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-018 — Layout Principal e Migracao de Paineis`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: refatorar a MainWindow para layout vertical de 5 zonas, adicionar Menu Bar e Status Bar, migrar paineis laterais para dialogs modais, integrar icones SVG na toolbar, e integrar delegates na tabela. Este epico **nao cria RFs novos** — e um epico de **refatoracao de UI** para RFs ja implementados em EP-008.

**Componentes de UI a especificar:**

| Componente | Descricao | Dependencia | RNFs Relacionados |
|------------|-----------|-------------|-------------------|
| MW-001 Menu Bar | QMenuBar com 4 menus: Arquivo, Cadastros, Ferramentas, Ajuda | QAction existentes | RNF-USAB-003 |
| MW-002 Toolbar Refatorada | Icones SVG + texto, 5 grupos com separadores, altura 32px | Icones EP-017 | RNF-USAB-003 |
| MW-005 Status Bar | Contadores a esquerda, avisos a direita com popup | WarningsPanel migrado | RNF-USAB-003, RNF-PERF-002 |
| MW-006 Layout Vertical | Remocao QSplitter, QVBoxLayout com 5 zonas | MainWindow atual | RNF-USAB-002 |
| DLG-004 ConfigDialog | QDialog modal 420x340px, migracao de ConfigPanel | ConfigPanel | RNF-CONF-002 |
| DLG-005 DependencyDialog | QDialog modal 500x420px, migracao de DependencyPanel | DependencyPanel | RNF-CONF-002 |
| DLG-006 MetricsDialog | QDialog modal 440x380px, auto-show pos-alocacao | MetricsPanel | RNF-CONF-002 |
| INT-001 Delegates | Integracao StatusBadgeDelegate e MonospaceDelegate na tabela | Delegates EP-017 | RNF-PERF-002 |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| Layout de 5 zonas | Menu Bar (28px) -> Toolbar (44px) -> Barra Filtros (36px, vazia) -> Tabela (stretch) -> Status Bar (24px) |
| Estrutura de menus | Arquivo (Importar/Exportar/Sair), Cadastros (Historias/Features/Devs/Config), Ferramentas (Cronograma/Alocacao), Ajuda (Sobre) |
| Grupos de toolbar | 5 grupos: CRUD, Priorizacao, Cadastros, Processamento, Excel |
| Migracao de paineis | ConfigPanel -> ConfigDialog, DependencyPanel -> DependencyDialog, MetricsPanel -> MetricsDialog, WarningsPanel -> Status Bar |
| Integracao de icones | Mapeamento icone SVG -> QAction para cada botao da toolbar |
| Deprecacao de arquivos | config_panel.py, dependency_panel.py, metrics_panel.py, warnings_panel.py marcados como deprecados |

**Criterios de aceite do epico que devem ser cobertos:**
- Layout de 5 zonas empilhadas (Menu Bar, Toolbar, Barra Filtros, Tabela, Status Bar)
- QSplitter horizontal removido — tabela ocupa 100% da largura
- Menu Bar com 4 menus funcionais e atalhos de teclado
- Toolbar com icones SVG + texto, 5 grupos separados, tooltips com shortcuts
- Status Bar com contadores e area de avisos com popup
- ConfigDialog, DependencyDialog, MetricsDialog como modais funcionais
- MetricsDialog auto-show apos alocacao bem-sucedida
- Testes existentes do EP-008 continuam passando
- Tempo de inicializacao <= 3s

**Cenarios de teste que devem ser especificados:**
- MainWindow instancia com novo layout sem erro
- Menu Bar: cada acao dos 4 menus funciona corretamente
- Toolbar: cada botao com icone renderizado e acao conectada
- Status Bar: contadores atualizados, popup de avisos funcional
- ConfigDialog: validacao de campos, aplicar/cancelar
- DependencyDialog: adicionar/remover dependencia, erro de ciclo
- MetricsDialog: exibe metricas, fecha com OK
- Delegates: StatusBadgeDelegate e MonospaceDelegate renderizam corretamente

**IMPORTANTE**: Este epico **nao** cria logica de negocio, entidades, value objects, repositorios ou use cases. EP-018 cria **exclusivamente** refatoracao de layout e migracao de componentes de UI.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade para RNFs**: Todo componente deve mapear para um ou mais RNFs do SRS.
   Incluir matriz de rastreabilidade: Componente UI <-> RNF <-> Criterio de Aceite do Epico.

2. **Codigo existente como baseline**: Nao redefinir ViewModels, Use Cases, DTOs, Services ou
   delegates ja implementados. Especificar apenas **refatoracao de MainWindow**, **novos dialogs**,
   e **integracao de componentes existentes** (icones, delegates).

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Migracao incremental documentada**: Para cada painel migrado (ConfigPanel -> ConfigDialog,
   etc.), detalhar: (a) logica a copiar, (b) logica a remover do painel antigo, (c) como conectar
   o novo dialog a MainWindow, (d) teste de regressao para validar que funcionalidade nao quebrou.

5. **Layout especificado com precisao**: Para o novo layout de 5 zonas, incluir:
   - Altura fixa de cada zona (Menu Bar 28px, Toolbar 44px, Barra Filtros 36px, Status Bar 24px)
   - Comportamento da zona Tabela (stretch para ocupar espaco restante)
   - Margens e espacamentos (QVBoxLayout.setContentsMargins, setSpacing)
   - Comportamento em resolucao minima 1366x768

6. **Menus detalhados com atalhos**: Para cada menu e acao, especificar:
   - Texto do menu e da acao em PT-BR
   - Atalho de teclado (QKeySequence)
   - Conexao com metodo existente ou novo slot
   - Separadores entre grupos de acoes

7. **Toolbar com icones e grupos**: Para cada grupo da toolbar, especificar:
   - Acoes pertencentes ao grupo
   - Icone SVG correspondente (nome do arquivo)
   - `toolbar.addSeparator()` entre grupos
   - `toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)`

8. **Status Bar com atualizacao reativa**: Especificar:
   - Quais signals do ViewModel atualizam os contadores
   - Formato exato dos textos ("42 historias . 284 SP . Ultima alocacao: DD/MM/YYYY HH:MM")
   - Widget de avisos com badge de contagem
   - Popup de avisos: tipo de widget (QFrame? QMenu?), posicionamento relativo, conteudo

9. **Dialogs com ViewModels opcionais**: Para cada dialog migrado, decidir:
   - Se usa ViewModel separado (recomendado para DependencyDialog que tem logica complexa)
   - Se tem logica inline (aceitavel para ConfigDialog e MetricsDialog que sao simples)
   - Pattern de comunicacao: signal/slot ou retorno sincrono

10. **MetricsDialog auto-show**: Detalhar:
    - Qual signal do AllocationViewModel indica sucesso
    - Como MainWindow conecta o signal para instanciar e exibir MetricsDialog
    - Condicoes para NAO exibir (erro de alocacao, 0 historias alocadas)

11. **Integracao de delegates**: Especificar:
    - Quais colunas recebem quais delegates (ID -> MonospaceDelegate, Status -> StatusBadgeDelegate)
    - Onde no codigo chamar `setItemDelegateForColumn`
    - Teste para validar renderizacao correta

12. **Deprecacao de arquivos**: Para cada painel deprecado, especificar:
    - Que o arquivo permanece no repositorio (nao deletar)
    - Que imports sao removidos de main_window.py
    - Comentario no topo do arquivo indicando deprecacao e alternativa

13. **Testes de regressao**: Especificar:
    - Quais testes existentes devem continuar passando
    - Novos testes para MainWindow refatorada (instanciacao, layout, menus, toolbar, status bar)
    - Novos testes para cada dialog migrado
    - Testes de integracao de delegates

14. **Performance**: Especificar:
    - Tempo de abertura de cada dialog <= 100ms (RNF-PERF-002)
    - Tempo de startup com novo layout <= 3s (RNF-PERF-004)
    - Renderizacao de delegates sem impacto perceptivel

15. **Sem sobreposicao com EP-019 a EP-022**: Nao especificar:
    - Expansao da tabela para 13 colunas (EP-019)
    - Barra de busca/filtros funcional (EP-020)
    - Ajustes finos de dialogs existentes (EP-021)
    - Dialog "Sobre" (EP-022)
    - Acao "Duplicar" wiring completo (EP-020)

16. **Consistencia de nomenclatura**: Usar os mesmos nomes de componentes definidos no epico
    (ConfigDialog, DependencyDialog, MetricsDialog). Nao renomear sem justificativa.

17. **Idioma**: Todos os textos de interface (titulos, labels, botoes, tooltips, mensagens)
    DEVEM ser em portugues brasileiro. Codigo (nomes de classes, metodos, variaveis) DEVE
    ser em ingles, conforme Constituicao §XV.

18. **Barra de Filtros placeholder**: Especificar QWidget com altura fixa 36px, sem conteudo
    funcional, apenas reservando espaco para EP-020.
</rules>
