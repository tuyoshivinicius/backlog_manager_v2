# Prompt: Criar Especificacao Tecnica do EP-020 — Busca, Filtros e Menu de Contexto

<role>
Voce e um Especialista em UI/UX com PySide6/Qt, com profundo conhecimento em:
- QSortFilterProxyModel para filtragem composta sem alterar modelo original
- QLineEdit com debounce (QTimer.singleShot) para busca incremental
- QPushButton checkable para chips de filtro com contagem dinamica
- QComboBox com itens agrupados (separadores, headers de grupo)
- QMenu de contexto (customContextMenuRequested, QAction, separadores, estilizacao)
- QShortcut e QKeySequence para atalhos de teclado (Ctrl+F, Ctrl+D, Delete, Alt+setas)
- Padrao MVVM aplicado a camada de apresentacao (proxy model como filtro sobre ViewModel)
- Estilizacao de widgets via QSS (chips, campo de busca, menu de contexto)
- Testes de GUI com pytest-qt (QSortFilterProxyModel, signals, filtragem)
- Wiring de Use Cases existentes (DuplicateStoryUseCase) via ViewModel

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001, expandida em EP-008, EP-017, EP-019)
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

### Estado Atual do Codigo (Implementado em EP-001 a EP-019)

**StoryTableModel (EP-019):**
- 13 colunas: Prioridade(0), Feature(1), Onda(2), ID(3), Componente(4), Nome(5), Status(6), Desenvolvedor(7), Dependencias(8), SP(9), Inicio(10), Fim(11), Duracao(12)
- `COLUMNS`, `COLUMN_WIDTHS`, `CENTER_COLUMNS`, `TOOLTIP_COLUMNS` como ClassVar
- Delegates integrados: MonospaceDelegate na coluna 3 (ID), StatusBadgeDelegate na coluna 6 (Status)
- Dados recebidos via `list[StoryOutputDTO]`

**MainWindow (EP-018):**
- Layout vertical de 5 zonas: Menu Bar → Toolbar → Barra Filtros (**placeholder vazio**) → Tabela → Status Bar
- StoryTableView customizado com selecao por linha, zebra striping, estado vazio
- Toolbar com 5 grupos: (1) Nova Historia, (2) Editar/Deletar, (3) Features/Devs, (4) Cronograma/Alocar, (5) Import/Export
- `_setup_central_widget()` cria a tabela com delegates configurados via `setItemDelegateForColumn()`
- DependencyDialog acessivel via botao dedicado — **nao** via right-click (ainda nao implementado)

**MainWindowViewModel:**
- Signals: `stories_changed`, `story_selected(str)`, `loading(bool)`, `error_occurred(str)`
- Gerencia `_stories: list[StoryOutputDTO]`, `_selected_story_id`, `_table_model: StoryTableModel`
- Metodos existentes: `load_stories()`, `create_story()`, `edit_story()`, `delete_story()`, `move_story_up()`, `move_story_down()`
- **Nao possui** metodo `duplicate_story()` — deve ser adicionado

**DuplicateStoryUseCase (EP-008, Application layer):**
- `async def execute(self, story_id: str) -> StoryOutputDTO`
- Usa `UnitOfWork` e `StoryService.duplicate_story()`
- Cria copia com novo ID, prioridade no fim da fila
- Raise `ValueError` se historia nao encontrada

**DependencyDialog (EP-018):**
- `DependencyDialog(container: DIContainer, story_id: str, story_name: str, all_stories: list[StoryOutputDTO], parent: QWidget | None)`
- Dialog modal para gestao de dependencias com deteccao de ciclos
- Ja funcional e testado

**Design system (EP-017):**
- `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS (cores, fontes, espacamento), STATUS_PALETTE com 5 status
- `src/backlog_manager/presentation/theme/stylesheet.qss` — stylesheet centralizado (17KB)
- STATUS_PALETTE: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO — cada um com bg, text, border, symbol

**O que NAO existe (EP-020 deve criar/modificar):**
- Barra de busca/filtros na zona 3 (atualmente placeholder vazio)
- QSortFilterProxyModel (FilterProxyModel) para filtragem composta
- Chips de status com contagem
- Dropdown de feature/onda
- Menu de contexto (right-click na tabela)
- Botao Duplicar na toolbar e atalho Ctrl+D
- Handler `duplicate_story()` no MainWindowViewModel

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **QTableView com proxy model pode quebrar delegates**: Delegates sao atribuidos a `QTableView` via `setItemDelegateForColumn()`. Ao inserir um `QSortFilterProxyModel` entre o `StoryTableModel` e a view, os indices de coluna nao mudam (proxy nao reordena colunas), mas e necessario confirmar que delegates continuam funcionando — `setModel()` deve receber o proxy, nao o modelo original. A spec deve definir a ordem exata de configuracao: (1) criar proxy, (2) setSourceModel, (3) view.setModel(proxy), (4) setItemDelegateForColumn na view.

2. **Contagem de chips requer acesso ao modelo original, nao ao filtrado**: Os chips de status exibem contagem total por status (ex: "Backlog (12)"), nao a contagem filtrada. Isso significa que a contagem deve vir do `StoryTableModel` (source model), nao do proxy. A spec deve definir se a contagem usa signal do source model ou metodo direto no ViewModel.

3. **Combinacao de filtros (texto + status + feature) no filterAcceptsRow**: O metodo `filterAcceptsRow` precisa acessar dados de colunas especificas do source model. Os indices de coluna para acesso no filtro sao: ID(3), Componente(4), Nome(5), Status(6), Feature(1). A spec deve usar as constantes `StoryTableModel.COLUMNS` ou indices nomeados para evitar hardcoding.

4. **DuplicateStoryUseCase e async — chamada no ViewModel**: O ViewModel precisa chamar `await duplicate_story_use_case.execute(story_id)`. O padrao existente no ViewModel usa `asyncio.ensure_future()` com qasync. A spec deve seguir o mesmo padrao dos metodos `create_story()`, `edit_story()`, etc.

5. **Dropdown de feature/onda depende de dados de features**: O dropdown precisa listar features agrupadas por onda. O ViewModel ja carrega stories, mas pode nao ter acesso a lista de features separadamente. A spec deve definir de onde vem a lista de features: do DTO das stories (extraindo feature_name + wave), ou de um use case separado (ListFeaturesUseCase).

6. **Barra de filtros ocupa 36px reservados em EP-018**: A zona 3 do layout ja tem espaco reservado mas esta vazia. A spec deve definir como popular essa zona com o layout QHBoxLayout contendo busca, chips e dropdown, sem alterar a estrutura de zonas do EP-018.

7. **Menu de contexto precisa de acoes ja existentes no ViewModel**: As acoes Editar, Deletar, Mover Cima, Mover Baixo ja existem como metodos no ViewModel e botoes na toolbar. O menu de contexto deve reusar essas mesmas acoes/signals, nao duplicar logica. A spec deve definir se usa as mesmas QAction da toolbar ou cria novas QAction que chamam os mesmos slots.

8. **Atalho Ctrl+D pode conflitar com atalhos existentes**: A MainWindow ja possui atalhos configurados em `_setup_shortcuts()`. A spec deve verificar que Ctrl+D nao conflita com nenhum atalho existente e definir onde registra-lo (QShortcut no MainWindow ou QAction na toolbar).

### Alinhamento com Constituicao do Projeto

- **§I Clean Architecture**: FilterProxyModel e ViewModel (Presentation layer). DuplicateStoryUseCase ja esta na Application layer — apenas wiring no ViewModel.
- **§II DDD**: Nenhuma logica de dominio no proxy ou na view — apenas filtragem de apresentacao.
- **§IV Dependency Injection**: DuplicateStoryUseCase injetado via DIContainer, mesmo padrao dos demais use cases.
- **§VIII Async**: Chamada ao DuplicateStoryUseCase segue padrao async existente no ViewModel.
- **§IX Simplicidade**: Expandir MainWindow e ViewModel existentes, nao criar novos widgets desnecessarios.
- **§X Type Hints**: Todos os metodos com type hints completas.
- **§XIV Estrategia de Testes**: Testes unitarios para FilterProxyModel, testes de integracao para menu de contexto.
- **§XIX Padroes UI/UX (MVVM)**: FilterProxyModel atua entre ViewModel (StoryTableModel) e View (StoryTableView). Logica de filtragem no proxy, nao na view.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-020_busca-filtros-menu-contexto.md` — requisitos, escopo, criterios de aceite, especificacao dos componentes MW-003, MW-007, UX-001, UX-003, UX-004
2. **SRS completo**: `srs.md` — secoes §3.1 RF-STORY-004 (duplicar historia), §3.1 RF-STORY-005 (listar historias com filtragem), §3.1 RF-STORY-006 (alterar prioridade), §3.1 RF-STORY-009 (gerenciar status), §3.4 RF-DEP-001 (adicionar dependencia), §4.2 RNF-USAB-003 (acessibilidade, atalhos), §4.2 RNF-USAB-004 (curva de aprendizado), §4.1 RNF-PERF-002 (responsividade UI <= 100ms), §4.5 RNF-MANT-001 (cobertura de testes), §8.2 (convencoes de nomenclatura)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §IV Dependency Injection, §VIII Async, §IX Simplicidade, §X Type Hints, §XIV Estrategia de Testes, §XIX Padroes de UI/UX (MVVM)
4. **StoryTableModel atual**: `src/backlog_manager/presentation/viewmodels/story_table_model.py` — modelo com 13 colunas, COLUMNS, CENTER_COLUMNS, TOOLTIP_COLUMNS, data(), indices de colunas
5. **MainWindow atual**: `src/backlog_manager/presentation/views/main_window.py` — layout de 5 zonas, toolbar com grupos, _setup_central_widget(), _setup_shortcuts(), delegates integrados, zona 3 placeholder
6. **MainWindowViewModel atual**: `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` — signals, metodos existentes (load_stories, create, edit, delete, move_up, move_down), padrao async com qasync
7. **DuplicateStoryUseCase**: `src/backlog_manager/application/use_cases/story/duplicate_story.py` — assinatura execute(story_id) -> StoryOutputDTO, tratamento de erro
8. **DependencyDialog**: `src/backlog_manager/presentation/views/dependency_dialog.py` — assinatura do construtor (container, story_id, story_name, all_stories, parent)
9. **Design system**:
   - `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS, STATUS_PALETTE (5 status com cores)
   - `src/backlog_manager/presentation/theme/stylesheet.qss` — QSS centralizado
10. **DTOs da Application layer**: `src/backlog_manager/application/dto/story.py` — verificar campos disponiveis em StoryOutputDTO (feature_name, wave, status, etc.)
11. **DIContainer**: `src/backlog_manager/presentation/container.py` — verificar se DuplicateStoryUseCase ja esta registrado no container
12. **Testes existentes**:
    - `tests/unit/presentation/viewmodels/test_story_table_model.py` — testes do modelo de tabela
    - `tests/integration/presentation/views/test_main_window.py` — testes de integracao da janela principal
13. **Spec EP-018 e EP-019**: Specs anteriores para entender baseline de layout e tabela — consultar `specs/018-*/spec.md` e `specs/019-*/spec.md`
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-020 — Busca, Filtros e Menu de Contexto (GUI-004)`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: criar FilterProxyModel para filtragem composta, implementar barra de busca/filtros com campo de texto + chips de status + dropdown de feature/onda, adicionar menu de contexto no right-click da tabela, expor DuplicateStoryUseCase na UI (toolbar, menu contexto, Ctrl+D), e criar testes unitarios para o FilterProxyModel. Este epico **nao cria entidades, value objects, repositorios, services ou delegates** — trabalha exclusivamente na camada Presentation, com wiring ao DuplicateStoryUseCase existente na Application layer.

**Componentes a especificar:**

| ID | Componente | Tipo | Descricao |
|----|------------|------|-----------|
| MW-003 | Barra de Busca/Filtros | NOVO | QLineEdit (240px, Ctrl+F) + 6 chips de status + dropdown feature/onda, 36px altura total, na zona 3 do layout |
| MW-007 | Menu de Contexto | NOVO | QMenu no right-click com 6 acoes agrupadas: Editar, Duplicar, Mover Cima, Mover Abaixo, Dependencias, Deletar |
| UX-001 | Duplicar Historia na UI | NOVO | Botao na toolbar (Grupo 1), item no menu contexto, atalho Ctrl+D, wiring ao DuplicateStoryUseCase |
| UX-003 | Filtros Rapidos por Status | NOVO | 6 QPushButton checkable com contagem de historias por status (Todos, Backlog, Execucao, Testes, Concluido, Impedido) |
| UX-004 | Filtro por Feature/Onda | NOVO | QComboBox dropdown com "Todas as features" + features agrupadas por onda |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| FilterProxyModel | QSortFilterProxyModel com filtragem composta: texto (ID/Nome/Componente), status (chips), feature/onda (dropdown). Metodos: set_text_filter(), set_status_filter(), set_feature_filter(). filterAcceptsRow() combina filtros com AND. |
| Barra de busca/filtros | QHBoxLayout na zona 3: QLineEdit a esquerda (240px, icone lupa, placeholder), chips centralizados, QComboBox a direita |
| Menu de contexto | QMenu com 6 QActions agrupadas por separadores (edicao, priorizacao, relacoes, destrutiva). "Deletar" estilizado com cor @error. |
| Duplicar na toolbar | QAction com icone copy, adicionada ao Grupo 1 da toolbar existente |
| Handler duplicate_story no ViewModel | Metodo async no MainWindowViewModel seguindo padrao existente, com feedback na Status Bar |
| Testes unitarios | Suite para FilterProxyModel: filterAcceptsRow com filtros individuais e compostos, contagem por status, set/clear de filtros |

**Criterios de aceite do epico que devem ser cobertos:**
- Campo de busca filtra por ID, Nome ou Componente enquanto digita (debounce 150ms)
- Ctrl+F foca no campo de busca
- 6 chips de status exibem contagem correta (ex: "Backlog (12)")
- Chip clicado filtra tabela pelo status correspondente (bg @primary quando ativo)
- Dropdown exibe features agrupadas por onda, formato "Onda N - Nome"
- Filtros combinam com AND: busca + status + feature
- Right-click em linha da tabela abre QMenu com 6 acoes e separadores
- "Deletar" no menu tem texto com cor @error
- Ctrl+D duplica historia selecionada com sufixo " (copia)"
- Duplicacao exibe feedback na Status Bar: "Historia duplicada: XXX -> YYY"
- DependencyDialog abre ao clicar "Dependencias..." no menu contexto
- FilterProxyModel nao altera StoryTableModel original
- Delegates continuam funcionando com proxy ativo
- Testes existentes passam sem regressao

**IMPORTANTE**: Este epico **nao** cria StatusBadgeDelegate nem MonospaceDelegate (ja existem do EP-017). **Nao** cria StoryTableModel (ja existe do EP-019). **Nao** cria tooltip rico ao hover, agrupamento visual por onda, nem indicador de bloqueio (EP-022). **Nao** cria estilizacao fina de dialogs (EP-021).
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo componente deve mapear para requisitos do SRS.
   Incluir matriz: Componente ↔ RF/RNF ↔ Criterio de Aceite do Epico.
   RF-STORY-004 → DuplicateStoryUseCase wiring. RF-STORY-005 → FilterProxyModel + barra de busca.
   RF-STORY-006 → Mover Cima/Baixo no menu contexto. RF-STORY-009 → chips de status.
   RF-DEP-001 → "Dependencias..." no menu contexto.

2. **Codigo existente como baseline**: Nao redefinir StoryTableModel, delegates, theme.py,
   stylesheet.qss, DuplicateStoryUseCase, DependencyDialog, entities, services ou repositorios.
   Especificar apenas **FilterProxyModel novo**, **barra de busca/filtros nova**,
   **menu de contexto novo**, **wiring de DuplicateStoryUseCase no ViewModel**, e **testes**.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Proxy model transparente para delegates**: A spec deve garantir que a configuracao
   do proxy model nao quebre delegates existentes (MonospaceDelegate coluna 3, StatusBadgeDelegate
   coluna 6). Definir ordem exata: criar proxy → setSourceModel → view.setModel(proxy) →
   setItemDelegateForColumn na view. Proxy nao reordena colunas.

5. **Contagem de chips via source model**: A spec deve definir que contagem nos chips
   ("Backlog (12)") vem do StoryTableModel (modelo original com todas as historias),
   nao do proxy filtrado. Definir mecanismo de atualizacao quando stories mudam.

6. **Filtragem por indices nomeados**: A spec deve usar constantes de coluna do StoryTableModel
   (ex: `StoryTableModel.COLUMNS.index("ID")`) ou constantes nomeadas no FilterProxyModel
   para acessar dados no filterAcceptsRow. Nao usar indices hardcoded.

7. **Reuso de acoes no menu de contexto**: As acoes Editar, Deletar, Mover Cima, Mover Abaixo
   ja existem como metodos no ViewModel. O menu de contexto deve reusar os mesmos slots/metodos,
   nao duplicar logica. A spec deve definir se cria novas QAction (com mesmos slots) ou reutiliza
   as QAction da toolbar.

8. **Padrao async para DuplicateStoryUseCase**: O metodo `duplicate_story()` no ViewModel
   deve seguir o mesmo padrao async dos metodos existentes (`create_story`, `edit_story`).
   A spec deve definir tratamento de erro (ValueError → mensagem de erro na Status Bar ou dialog).

9. **Debounce no campo de busca**: A spec deve especificar implementacao do debounce de 150ms
   usando QTimer.singleShot, cancelando timer anterior a cada keystroke. Definir se usa
   `textChanged` signal direto ou wrapper com timer.

10. **Dropdown de features populado dinamicamente**: A spec deve definir como obter a lista
    de features para o dropdown: extraindo de StoryOutputDTO (feature_name + wave) ao carregar
    stories, ou via use case separado. Definir formato dos itens e comportamento quando
    nao ha features cadastradas.

11. **Estilizacao via QSS existente + novas classes**: A spec deve listar quais estilos ja
    existem no stylesheet.qss do EP-017 e quais precisam ser adicionados:
    - Campo de busca (#searchField): border, border-radius, padding, placeholder
    - Chips (.filterChip): ativo/inativo, cores, border-radius, padding
    - Menu de contexto (QMenu): bg, border, border-radius, sombra, item hover, item destrutivo

12. **Testes unitarios completos para FilterProxyModel**: A spec deve especificar suite de testes:
    - `test_filter_text_by_id`: filtra por ID parcial
    - `test_filter_text_by_name`: filtra por nome parcial
    - `test_filter_text_by_component`: filtra por componente
    - `test_filter_by_status`: filtra por status unico
    - `test_filter_combined_text_and_status`: filtros compostos AND
    - `test_filter_by_feature`: filtra por feature/onda
    - `test_filter_combined_all`: texto + status + feature
    - `test_clear_filters`: limpar filtros restaura todas as linhas
    - `test_status_count`: contagem correta por status no source model
    - `test_source_model_unchanged`: filtros nao alteram modelo original

13. **Sem sobreposicao com outros epicos**: Nao especificar:
    - Tooltip rico ao hover (EP-022)
    - Agrupamento visual por onda na tabela (EP-022)
    - Indicador de bloqueio na coluna Dependencias (EP-022)
    - Estilizacao fina de dialogs (EP-021)
    - Criacao de StoryTableModel ou delegates (EP-017, EP-019)

14. **Consistencia de nomenclatura**: Usar os mesmos nomes de componentes definidos no epico
    (MW-003, MW-007, UX-001, UX-003, UX-004). Nomes de classes e metodos em ingles.
    Textos de interface em PT-BR. Status em MAIUSCULAS sem acento conforme SRS §8.2.

15. **Idioma**: Todos os textos de interface (placeholder de busca, nomes de chips, itens do
    menu contexto, mensagem de feedback da duplicacao) DEVEM ser em portugues brasileiro.
    Codigo (classes, metodos, variaveis) DEVE ser em ingles, conforme Constituicao §XV.

16. **Compatibilidade com selecao simples**: Menu de contexto implementado para selecao simples
    (SingleSelection ja configurado no StoryTableView). Selecao multipla esta fora do escopo.
    A spec deve definir comportamento quando nenhuma linha esta selecionada (menu nao aparece
    ou itens desabilitados).
</rules>
