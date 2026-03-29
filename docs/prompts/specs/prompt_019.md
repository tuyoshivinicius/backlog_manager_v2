# Prompt: Criar Especificacao Tecnica do EP-019 — Tabela de Backlog

<role>
Voce e um Especialista em UI/UX com PySide6/Qt, com profundo conhecimento em:
- QTableView, QAbstractTableModel e QStyledItemDelegate para renderizacao customizada
- Configuracao de QHeaderView (larguras fixas, stretch, resize modes)
- Integracao de delegates customizados (StatusBadgeDelegate, MonospaceDelegate) em colunas especificas
- Padrao MVVM aplicado a camada de apresentacao (StoryTableModel como ViewModel)
- Estilizacao de tabelas via QSS (zebra striping, selecao, header, scrollbar, grid lines)
- Estado vazio em tabelas (overlay, QStackedWidget, placeholder widget)
- Formatacao de dados para exibicao (datas DD/MM/YYYY, IDs COMPONENTE-NNN, truncacao com elipsis)
- Testes de GUI com pytest-qt (QAbstractTableModel, delegates, renderizacao)

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

### Estado Atual do Codigo (Implementado em EP-001 a EP-018)

O `StoryTableModel` atual (EP-008) possui **8 colunas**: ID, Nome, SP, Status, Feature, Dev, Inicio, Fim. O metodo `columnCount()` retorna `len(self.COLUMNS)` = 8. O metodo `data()` usa match/case para cada coluna com `_get_display_value()`. Alinhamento e configurado via `TextAlignmentRole`. A coluna Nome nao usa stretch.

**Delegates ja integrados na MainWindow (EP-018):**
- `MonospaceDelegate` aplicado na coluna 0 (ID) via `setItemDelegateForColumn(0, monospace_delegate)`
- `StatusBadgeDelegate` aplicado dinamicamente na coluna Status

**Design system implementado (EP-017):**
- `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS (cores, fontes, espacamento), STATUS_PALETTE com 5 status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)
- `src/backlog_manager/presentation/theme/stylesheet.qss` — stylesheet centralizado (17KB) com zebra striping, selecao, header, scrollbar
- `src/backlog_manager/presentation/delegates/status_badge_delegate.py` — StatusBadgeDelegate com pill badges, simbolos (●, ▶, ◆, ✓, ✕), cores WCAG AA
- `src/backlog_manager/presentation/delegates/monospace_delegate.py` — MonospaceDelegate com fallback chain (JetBrains Mono → Cascadia Code → Consolas → monospace)

**Layout atual (EP-018):**
- MainWindow com layout vertical de 5 zonas: Menu Bar → Toolbar → Barra Filtros (placeholder) → Tabela → Status Bar
- Tabela ocupa 100% da largura (QSplitter removido em EP-018)
- `setAlternatingRowColors(True)` ja ativo

**Testes existentes:**
- Nao ha teste unitario dedicado para `StoryTableModel` — testes de integracao cobrem via `test_main_window.py`
- Testes unitarios existem para delegates: `test_monospace_delegate.py`, `test_status_badge_delegate.py`

**O que NAO existe (EP-019 deve criar/modificar):**
- 5 colunas adicionais: Prioridade, Onda, Componente, Dependencias, Duracao
- Reordenacao das colunas (ordem atual: ID, Nome, SP, Status, Feature, Dev, Inicio, Fim → nova ordem de 13 colunas)
- Larguras fixas e stretch configuradas por coluna
- Delegates reatribuidos nos novos indices (ID muda de indice 0 para 3, Status muda para indice 6)
- Estado vazio com mensagem orientativa quando `rowCount() == 0`
- Testes unitarios dedicados para o StoryTableModel expandido

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Reordenacao de colunas quebra indices de delegates**: Os delegates MonospaceDelegate e StatusBadgeDelegate estao atualmente mapeados por indice de coluna (coluna 0 = ID com monospace, coluna dinamica = Status com badge). Ao expandir de 8 para 13 colunas e reordenar, os indices mudam: ID passa de indice 0 para indice 3, Status passa para indice 6. -> A spec deve detalhar como reatribuir `setItemDelegateForColumn()` nos novos indices e garantir que a MainWindow use constantes ou lookup por nome de coluna ao inves de indices hardcoded.

2. **Dados insuficientes no DTO para novas colunas**: O StoryTableModel atual recebe dados via DTO. As novas colunas Prioridade, Onda, Componente, Dependencias e Duracao podem nao estar disponiveis no DTO atual. -> A spec deve verificar se `StoryDTO` (ou equivalente) ja inclui os campos `priority`, `wave`, `component`, `dependencies`, `duration` e especificar como obte-los sem violar Clean Architecture (DTO deve vir da Application layer).

3. **Coluna Dependencias requer resolucao de IDs**: A coluna Dependencias deve exibir IDs separados por virgula (ex: "AUTH-001, API-003"). O modelo pode receber apenas IDs numericos internos. -> A spec deve definir se a resolucao ID numerico → ID formatado (COMPONENTE-NNN) ocorre no ViewModel, no Use Case, ou no DTO.

4. **Coluna Desenvolvedor exibe ID ao inves de nome**: Atualmente `developer_id` e armazenado. A tabela deve exibir o nome do desenvolvedor. -> A spec deve definir onde a resolucao ID → nome ocorre (DTO ja resolvido? ViewModel com cache de devs?).

5. **Estado vazio pode conflitar com QTableView**: Exibir mensagem centralizada quando `rowCount() == 0` requer uma abordagem que nao quebre o modelo. -> A spec deve definir se usa QStackedWidget, overlay transparente sobre a tabela, ou `paintEvent` customizado no QTableView.

6. **Testes existentes sem cobertura de StoryTableModel**: Nao existem testes unitarios dedicados para o modelo. A expansao de 8 para 13 colunas precisa de testes novos. -> A spec deve especificar suite completa de testes unitarios para `columnCount`, `headerData`, `data` (cada coluna), `roleAlignment`, `toolTipRole`.

7. **Truncacao com elipsis e tooltip**: Colunas Nome, Feature, Dependencias, Desenvolvedor devem truncar com elipsis e mostrar tooltip com texto completo. -> A spec deve definir se truncacao e feita via `QHeaderView.setDefaultSectionResizeMode`, `elideMode` no delegate, ou CSS, e como `data()` com `Qt.ToolTipRole` retorna o texto completo.

8. **Botoes desabilitados no estado vazio**: Botoes Cronograma e Alocar devem ser desabilitados quando nao ha historias. -> A spec deve definir o mecanismo de sincronizacao (signal do ViewModel? verificacao direta de `rowCount`? binding reativo?).

### Alinhamento com Constituicao do Projeto

- **§I Clean Architecture**: StoryTableModel e ViewModel (Presentation layer), recebe dados via DTOs da Application layer
- **§II DDD**: Nenhuma logica de dominio no modelo de tabela — apenas formatacao para exibicao
- **§IV Dependency Injection**: Delegates e dados injetados via construtor
- **§IX Simplicidade**: Expandir modelo existente, nao criar abstraçao nova
- **§X Type Hints**: Todos os metodos do modelo com type hints completas
- **§XIV Estrategia de Testes**: Testes unitarios para modelo, testes de integracao para delegates na tabela
- **§XIX Padroes UI/UX (MVVM)**: StoryTableModel e o ViewModel da tabela, Views nao importam de domain
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-019_tabela-de-backlog.md` — requisitos, escopo, criterios de aceite, especificacao das 13 colunas com larguras/alinhamentos/delegates
2. **SRS completo**: `srs.md` — secoes §3.1 RF-STORY-005 (listar historias do backlog), §3.1 RF-STORY-009 (gerenciar status), §4.2 RNF-USAB-003 (acessibilidade, zebra striping, badges nao-cromaticos), §4.2 RNF-USAB-004 (curva de aprendizado, estado vazio orientativo), §4.1 RNF-PERF-002 (responsividade UI <= 100ms, renderizacao delegates <= 16ms), §4.5 RNF-MANT-001 (cobertura de testes >= 80%), §8.2 (convencoes de nomenclatura: COMPONENTE-NNN, status MAIUSCULAS sem acento, datas)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §II DDD, §IV Dependency Injection, §IX Simplicidade, §X Type Hints, §XIV Estrategia de Testes, §XIX Padroes de UI/UX (MVVM)
4. **StoryTableModel atual**: `src/backlog_manager/presentation/viewmodels/story_table_model.py` — modelo com 8 colunas, COLUMNS, data(), headerData(), columnCount(), _get_display_value()
5. **MainWindow atual**: `src/backlog_manager/presentation/views/main_window.py` — integracao de delegates (setItemDelegateForColumn), configuracao de QHeaderView, StoryTableView
6. **Delegates existentes**:
   - `src/backlog_manager/presentation/delegates/status_badge_delegate.py` — StatusBadgeDelegate
   - `src/backlog_manager/presentation/delegates/monospace_delegate.py` — MonospaceDelegate
7. **Design system**:
   - `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS, STATUS_PALETTE
   - `src/backlog_manager/presentation/theme/stylesheet.qss` — QSS com zebra striping, selecao, header, scrollbar
8. **DTOs da Application layer**: `src/backlog_manager/application/dto/` — verificar se StoryDTO inclui campos para as 5 novas colunas (priority, wave, component, dependencies, duration)
9. **Testes existentes**:
   - `tests/integration/presentation/views/test_main_window.py` — testes que referenciam colunas/indices
   - `tests/unit/presentation/delegates/test_monospace_delegate.py`
   - `tests/unit/presentation/delegates/test_status_badge_delegate.py`
10. **Spec EP-017 e EP-018**: Specs anteriores para entender o baseline de design system e layout — consultar `specs/017-*/spec.md` e `specs/018-*/spec.md`
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-019 — Tabela de Backlog (GUI-003)`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: expandir o StoryTableModel de 8 para 13 colunas, integrar delegates nos novos indices, aplicar estilizacao QSS, implementar estado vazio orientativo, e criar testes unitarios dedicados. Este epico **nao cria entidades, value objects, repositorios, use cases ou services** — trabalha exclusivamente na camada Presentation.

**Componentes a especificar:**

| ID | Componente | Tipo | Descricao |
|----|------------|------|-----------|
| MW-004 | Tabela de Backlog | REFATORACAO | Expandir StoryTableModel de 8 para 13 colunas, reordenar, configurar larguras/alinhamentos, reatribuir delegates |
| MW-008 | Estado Vazio | NOVO | Overlay/placeholder na tabela quando sem historias, com mensagem orientativa e botoes desabilitados |

**Detalhamento das 13 colunas (ordem obrigatoria):**

| # | Coluna | Largura | Alinhamento | Delegate | Fonte de Dados |
|---|--------|---------|-------------|----------|----------------|
| 0 | Prioridade | 60px fixo | Centro | — | story.priority (inteiro) |
| 1 | Feature | 120px | Esquerda | — | feature.name ou "—" |
| 2 | Onda | 50px fixo | Centro | — | feature.wave ou 0 |
| 3 | ID | 100px fixo | Esquerda | MonospaceDelegate | story.story_id (COMPONENTE-NNN) |
| 4 | Componente | 80px | Esquerda | — | extraido do story_id (prefixo) |
| 5 | Nome | stretch | Esquerda | — | story.name (min 200px, elipsis) |
| 6 | Status | 100px fixo | Centro | StatusBadgeDelegate | story.status (badge pill) |
| 7 | Desenvolvedor | 100px | Esquerda | — | developer.name ou "—" (elipsis) |
| 8 | Dependencias | 120px | Esquerda | — | IDs separados por virgula ou "—" (elipsis) |
| 9 | SP | 40px fixo | Centro | — | story.story_points |
| 10 | Inicio | 90px fixo | Centro | — | DD/MM/YYYY ou "—" |
| 11 | Fim | 90px fixo | Centro | — | DD/MM/YYYY ou "—" |
| 12 | Duracao | 60px fixo | Centro | — | dias uteis ou "—" |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| StoryTableModel expandido | COLUMNS com 13 entradas, data() com 13 cases, headerData() atualizado, roles de alinhamento por coluna |
| Configuracao de QHeaderView | Larguras fixas por coluna, stretch na coluna Nome, resize modes |
| Reatribuicao de delegates | MonospaceDelegate no indice 3, StatusBadgeDelegate no indice 6 |
| Estado vazio (MW-008) | Widget overlay ou QStackedWidget com mensagem centralizada |
| Testes unitarios | Suite completa para StoryTableModel (columnCount, headerData, data por coluna, roles, estado vazio) |
| Estilizacao QSS | Verificar e ativar: zebra striping, selecao, header estilizado, scrollbar slim, altura de linhas |

**Criterios de aceite do epico que devem ser cobertos:**
- `StoryTableModel.columnCount()` retorna 13
- `headerData()` retorna nomes corretos na ordem especificada
- Datas formatadas como DD/MM/YYYY
- Delegates integrados e funcionais nas colunas ID (indice 3) e Status (indice 6)
- Zebra striping visivel (linhas alternadas)
- Selecao com fundo @primary-light, texto nao invertido
- Header uppercase, @neutral-500, weight 600, border-bottom 2px
- Coluna Nome expande/contrai com stretch
- Texto longo truncado com elipsis e tooltip com texto completo
- Estado vazio: mensagem centralizada quando rowCount() == 0
- Botoes Cronograma e Alocar desabilitados no estado vazio
- Testes existentes atualizados para 13 colunas, todos passando
- Renderizacao de delegate <= 16ms por celula

**IMPORTANTE**: Este epico **nao** cria StatusBadgeDelegate nem MonospaceDelegate (ja existem do EP-017). **Nao** cria busca/filtros (EP-020). **Nao** cria tooltip rico ao hover, agrupamento por onda, nem indicador de bloqueio na coluna Dependencias (EP-022).
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo componente deve mapear para requisitos do SRS.
   Incluir matriz: Coluna ↔ RF/RNF ↔ Criterio de Aceite do Epico.
   RF-STORY-005 → expansao para 13 colunas. RF-STORY-009 → integracao StatusBadgeDelegate.

2. **Codigo existente como baseline**: Nao redefinir delegates, theme.py, stylesheet.qss, Use Cases,
   DTOs, Services ou entities. Especificar apenas **expansao do StoryTableModel**, **reconfiguracao
   de QHeaderView**, **reatribuicao de delegates**, **estado vazio**, e **testes**.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Indices de coluna nao hardcoded**: A spec deve definir constantes ou enum para indices de
   coluna (ex: `COLUMN_PRIORITY = 0`, `COLUMN_ID = 3`, `COLUMN_STATUS = 6`) e usar essas
   constantes em `setItemDelegateForColumn`, `setColumnWidth`, e testes. Justificativa: reordenacao
   futura nao deve quebrar delegates nem testes.

5. **Dados via DTO**: A spec deve verificar se o DTO atual inclui todos os campos necessarios para
   as 13 colunas. Se campos estiverem faltando, a spec deve especificar o que precisa ser adicionado
   ao DTO (na Application layer), respeitando Clean Architecture — StoryTableModel nunca acessa
   repositorios diretamente.

6. **Resolucao de nomes e IDs**: A spec deve definir explicitamente onde resolver:
   - `developer_id` → nome do desenvolvedor (DTO ja resolvido? ViewModel com cache?)
   - IDs de dependencias numericos → IDs formatados COMPONENTE-NNN
   - `feature_id` → nome da feature e numero da onda

7. **Estado vazio robusto**: A spec deve definir implementacao que nao quebre o QTableView nem o
   modelo. Deve detalhar: tipo de widget, condicao de exibicao, mensagem exata, estilizacao
   (fonte, cor, alinhamento), e mecanismo de sincronizacao com botoes desabilitados.

8. **Truncacao e tooltip**: A spec deve especificar para cada coluna com truncacao:
   - Modo de truncacao (elideMode ou delegate)
   - `data()` com `Qt.ToolTipRole` retornando texto completo
   - Colunas afetadas: Nome, Feature, Dependencias, Desenvolvedor

9. **Estilizacao verificada**: A spec deve listar cada item de estilizacao QSS e confirmar se ja
   esta ativo via stylesheet.qss do EP-017 ou se precisa ser ativado/ajustado no codigo:
   - Zebra striping (setAlternatingRowColors)
   - Selecao (fundo @primary-light)
   - Header (uppercase, cor, weight, border-bottom)
   - Scrollbar slim
   - Altura de linhas (36px) e header (40px)
   - Grid lines transparent

10. **Testes unitarios completos**: A spec deve especificar suite de testes para:
    - `test_column_count`: `model.columnCount() == 13`
    - `test_header_data`: nomes corretos para as 13 colunas na ordem
    - `test_data_display_role`: valor correto para cada coluna (incluindo formatacao de datas, resolucao de nomes)
    - `test_data_alignment_role`: alinhamento correto por coluna
    - `test_data_tooltip_role`: tooltip retorna texto completo para colunas com truncacao
    - `test_empty_state`: estado vazio quando rowCount() == 0
    - `test_delegate_column_indices`: delegates atribuidos nos indices corretos

11. **Performance de renderizacao**: Delegates devem renderizar em <= 16ms por celula (60fps).
    A spec deve especificar como medir (pytest-benchmark ou time.perf_counter) e validar.

12. **Sem sobreposicao com outros epicos**: Nao especificar:
    - Busca e filtros (EP-020)
    - Tooltip rico ao hover (EP-022)
    - Agrupamento visual por onda (EP-022)
    - Indicador de bloqueio na coluna Dependencias (EP-022)
    - StatusBadgeDelegate e MonospaceDelegate internos (EP-017, apenas integrar)

13. **Consistencia de nomenclatura**: Usar os mesmos nomes de componentes definidos no epico
    (MW-004, MW-008). Nomes de classes e metodos em ingles. Textos de interface em PT-BR.
    Status em MAIUSCULAS sem acento conforme SRS §8.2.

14. **Idioma**: Todos os textos de interface (headers, estado vazio, tooltips) DEVEM ser em
    portugues brasileiro. Codigo (classes, metodos, variaveis) DEVE ser em ingles,
    conforme Constituicao §XV.

15. **Compatibilidade**: A spec deve garantir que a tabela funciona em resolucao minima 1366x768
    (RNF-USAB-002). Se a soma das larguras fixas exceder a largura disponivel, scrollbar
    horizontal deve aparecer automaticamente.
</rules>
