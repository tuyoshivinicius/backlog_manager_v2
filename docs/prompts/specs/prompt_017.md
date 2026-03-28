# Prompt: Criar Especificacao Tecnica do EP-017 — Design System e Fundacao Visual

<role>
Voce e um Especialista em UI/UX com PySide6/Qt, com profundo conhecimento em:
- Sistema de design (design tokens, paletas de cores, tipografia, espacamento)
- QSS (Qt Style Sheets) com substituicao de variaveis via Python
- QStyledItemDelegate para renderizacao customizada de celulas em QTableView
- Acessibilidade WCAG AA (contraste 4.5:1, indicadores nao-cromaticos, focus ring, areas clicaveis minimas)
- Icones SVG e integracao com QIcon em PySide6
- Arquitetura limpa aplicada a camada de apresentacao (styles, delegates como modulos independentes)
- Testes unitarios de delegates com mock de QPainter e QStyleOptionViewItem
- Otimizacao de performance de renderizacao (60fps = 16ms por celula)

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos nao-funcionais,
e implementaveis de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001, expandida em EP-008)
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

### Estado Atual do Codigo (Implementado em EP-001 a EP-008)

A camada de apresentacao (Presentation) ja existe com Views, ViewModels, DI Container e Entry Point funcionais. EP-008 implementou a **estrutura funcional completa da UI**, mas **sem sistema de design**. Todos os widgets usam estilizacao padrao do Qt/Windows, sem tokens de design centralizados.

**Componentes de UI existentes (sem estilizacao):**
- `src/backlog_manager/presentation/app.py` — Entry point com QApplication e qasync
- `src/backlog_manager/presentation/container.py` — DIContainer com todos os ViewModels
- `src/backlog_manager/presentation/views/main_window.py` — QMainWindow com toolbar e tabela
- `src/backlog_manager/presentation/views/story_dialog.py` — QDialog para criar/editar historia
- `src/backlog_manager/presentation/views/developer_dialog.py` — QDialog para CRUD de devs
- `src/backlog_manager/presentation/views/feature_dialog.py` — QDialog para CRUD de features
- `src/backlog_manager/presentation/views/dependency_panel.py` — Painel de dependencias
- `src/backlog_manager/presentation/views/config_panel.py` — Painel de configuracao
- `src/backlog_manager/presentation/views/metrics_panel.py` — Painel de metricas
- `src/backlog_manager/presentation/views/warnings_panel.py` — Painel de warnings
- `src/backlog_manager/presentation/views/confirm_delete_dialog.py` — Dialogo de confirmacao
- `src/backlog_manager/presentation/viewmodels/story_table_model.py` — QAbstractTableModel para backlog
- `src/backlog_manager/presentation/viewmodels/*.py` — ViewModels para cada componente

**Value Objects relevantes para estilizacao:**
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO

**O que NAO existe (EP-017 deve criar):**
- `src/backlog_manager/presentation/styles/` — Nao existe diretorio
- `src/backlog_manager/presentation/delegates/` — Nao existe diretorio
- `src/backlog_manager/presentation/assets/icons/` — Nao existe diretorio
- Nenhum arquivo QSS
- Nenhum modulo de design tokens
- Nenhum delegate customizado
- Nenhum icone SVG

**Estado do app.py (sem chamada a stylesheet):**
```python
app = QApplication(sys.argv)
app.setApplicationName("Backlog Manager")
# NAO existe: app.setStyleSheet(...)
```

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Ordem de substituicao de placeholders**: `apply_theme()` precisa substituir `@primary-pressed` antes de `@primary`, senao havera conflito parcial de substituicao (ex: `@primary-pressed` vira `#5B5BD6-pressed`). -> A spec deve definir ordem de substituicao (mais longo primeiro) e implementacao correta.

2. **Suporte a propriedades QSS**: PySide6 QSS nao suporta todas as propriedades CSS (ex: `outline`, `opacity`, `box-shadow`). -> A spec deve listar quais propriedades serao usadas e alternativas para propriedades nao suportadas (ex: `border` ao inves de `outline`, `rgba()` ao inves de `opacity`).

3. **Fontes Inter e JetBrains Mono**: Nao estao instaladas por padrao no Windows. -> A spec deve definir fallback chain: `"Inter", "Segoe UI", system-ui` para texto normal e `"JetBrains Mono", "Cascadia Code", "Consolas"` para monospace. Especificar que fontes sao preferencias, nao obrigatorias.

4. **Renderizacao de SVG em diferentes DPIs**: QIcon pode ter problemas de renderizacao em DPIs altos (125%, 150%). -> A spec deve validar renderizacao em 100%, 125% e 150% DPI. Se necessario, usar QSvgRenderer com escalonamento manual.

5. **Contraste WCAG 4.5:1 para badges de status**: Cada combinacao texto/fundo dos badges deve ter contraste >= 4.5:1. -> A spec deve incluir tabela de validacao de contraste para cada status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) com valores calculados.

6. **Indicadores nao-cromaticos**: Para acessibilidade de daltonicos, badges de status precisam de prefixos simbolicos alem de cores. -> A spec deve definir simbolos Unicode para cada status (ex: "●" BACKLOG, "▶" EXECUCAO, "◆" TESTES, "✓" CONCLUIDO, "✕" IMPEDIDO).

7. **Focus ring visivel**: Navegacao por teclado exige focus ring visivel em widgets interativos. -> A spec deve definir regras QSS de `:focus` com `border: 2px solid @primary` ou similar. Especificar quais widgets recebem focus ring.

8. **Areas clicaveis minimas**: QToolButton deve ter area minima de 32x32px para clique confortavel. -> A spec deve incluir regras de `min-width`, `min-height` para botoes de toolbar.

9. **Integracao com StoryTableModel existente**: StatusBadgeDelegate e MonospaceDelegate precisam ser integrados ao QTableView existente em main_window.py. -> A spec deve especificar que a **integracao** (chamar setItemDelegateForColumn) sera feita em EP-018, mas os delegates devem estar prontos e testaveis isoladamente.

10. **Integracao do stylesheet no app.py**: `app.setStyleSheet()` precisa ser chamado no entry point. -> A spec deve especificar a edicao de `app.py` para carregar e aplicar o stylesheet. Detalhar em qual ponto da inicializacao (antes ou depois de criar MainWindow).

11. **Localizacao de arquivos de assets**: Icones SVG precisam ser acessados em runtime. -> A spec deve definir estrutura de diretorios (`presentation/assets/icons/`) e como carregar icones via `pkg_resources` ou `pathlib` relativo ao pacote.

12. **Testabilidade de delegates**: StatusBadgeDelegate.paint() recebe QPainter e QStyleOptionViewItem que sao objetos complexos. -> A spec deve definir estrategia de teste: (a) mock de QPainter com verificacao de chamadas, (b) integracao com QPixmap para captura visual, ou (c) testes de unidade limitados a logica (cor, simbolo) com paint() testado visualmente.

13. **Performance de renderizacao**: RNF-PERF-002 exige renderizacao <= 16ms por celula para 60fps. -> A spec deve especificar que delegates nao devem fazer I/O ou calculos pesados em paint(). Cores e simbolos devem ser pre-calculados.

### Alinhamento com Constituicao do Projeto

- **§I Clean Architecture**: Styles e delegates ficam na camada Presentation, sem dependencias de Domain/Infrastructure (exceto import de StoryStatus para mapeamento de cores)
- **§IX Simplicidade**: Design tokens em modulo Python simples, sem framework de temas
- **§XIV Estrategia de Testes**: Delegates e apply_theme() devem ter testes unitarios
- **§XIX Padroes UI/UX (MVVM)**: Delegates sao parte da View layer, renderizam dados do Model
- **§XXI CI/CD**: Cobertura de testes para novos modulos (styles, delegates)
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-017_design-system-fundacao-visual.md` — requisitos, escopo, criterios de aceite, paleta de cores, lista de icones
2. **SRS completo**: `srs.md` — secoes §4.2 RNF-USAB-003 (Acessibilidade Basica: contraste 4.5:1, navegacao por teclado, tooltips), §4.5 RNF-MANT-001 (Manutenibilidade: zero valores hardcoded), §4.1 RNF-PERF-002 (Responsividade UI: renderizacao rapida)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §IX Simplicidade e Legibilidade, §XIV Estrategia de Testes, §XIX Padroes de UI/UX, §XXI CI/CD
4. **Spec de referencia (predecessor)**: `specs/008-ep008-interface-grafica/spec.md` — formato, nivel de detalhe e padrao esperado
5. **Entry point existente**: `src/backlog_manager/presentation/app.py` — onde aplicar stylesheet via app.setStyleSheet()
6. **StoryStatus VO**: `src/backlog_manager/domain/value_objects/story_status.py` — enum de status para mapeamento de cores nos badges
7. **StoryTableModel existente**: `src/backlog_manager/presentation/viewmodels/story_table_model.py` — model que os delegates vao renderizar
8. **MainWindow existente**: `src/backlog_manager/presentation/views/main_window.py` — onde os delegates serao integrados (EP-018)
9. **pyproject.toml**: para verificar dependencias atuais (PySide6 ja esta presente desde EP-008)
10. **Todos os dialogs em views/**: para verificar quais widgets precisam de estilizacao QSS
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-017 — Design System e Fundacao Visual`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: implementar o sistema de design centralizado (tokens, stylesheet, delegates, icones) que sera a fundacao visual para toda a UI do Backlog Manager. Este epico **nao cria RFs novos** — e um epico de **implementacao tecnica de RNFs de usabilidade e manutenibilidade**.

**Componentes a especificar:**

| ID | Componente | Arquivo | Descricao |
|----|------------|---------|-----------|
| DS-001 | Design Tokens | `styles/theme.py` | Modulo Python com 30+ constantes de cores, 6 tamanhos de fonte, 7 espacamentos, 4 border-radius, 3 sombras, paleta de status, simbolos nao-cromaticos |
| DS-002 | Apply Theme | `styles/theme.py` | Funcao `apply_theme(qss_template: str) -> str` que substitui placeholders `@var` por valores reais |
| DS-003 | Stylesheet QSS | `styles/stylesheet.qss` | Arquivo QSS centralizado cobrindo 15+ tipos de widget, usando apenas placeholders |
| DS-004 | StatusBadgeDelegate | `delegates/status_badge_delegate.py` | QStyledItemDelegate para badges pill de status com cores e simbolos nao-cromaticos |
| DS-005 | MonospaceDelegate | `delegates/monospace_delegate.py` | QStyledItemDelegate para IDs em fonte monospace |
| DS-006 | Biblioteca de Icones | `assets/icons/*.svg` | 16 arquivos SVG Phosphor Icons (16x16px) |
| ACC-001 | Validacao de Contraste | (documentacao) | Tabela de contraste WCAG para todas as combinacoes texto/fundo |
| ACC-002 | Focus Ring | `stylesheet.qss` | Regras `:focus` para widgets interativos |
| ACC-003 | Areas Clicaveis | `stylesheet.qss` | Dimensoes minimas 32x32px para QToolButton |
| INT-001 | Integracao app.py | `app.py` | Editar entry point para carregar e aplicar stylesheet |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| Estrutura de diretorios | `presentation/styles/`, `presentation/delegates/`, `presentation/assets/icons/` |
| Paleta de cores completa | 30+ tokens incluindo primarias, semanticas, neutras (13 tons), badges de status |
| Regras QSS detalhadas | Seletores para QMainWindow, QToolBar, QToolButton, QTableView, QHeaderView, QDialog, QPushButton, QLineEdit, QComboBox, QSpinBox, QDateEdit, QStatusBar, QMenuBar, QMenu, QScrollBar |
| Tabela de contraste WCAG | Validacao >= 4.5:1 para cada combinacao texto/fundo dos badges |
| Lista de icones SVG | 16 icones com nome de arquivo, uso pretendido e fonte (Phosphor Icons) |

**RNFs que ficam implementados apos este epico:**
- RNF-USAB-003: Acessibilidade basica (contraste 4.5:1, focus ring, areas clicaveis minimas)
- RNF-MANT-001: Manutenibilidade (zero valores hardcoded de cor/fonte fora de theme.py)

**O que NAO faz parte deste epico (sera feito em EP-018 a EP-022):**
- Integracao dos delegates na tabela (EP-018)
- Aplicacao de icones em toolbar/menus (EP-018)
- Ajustes finos em dialogs (EP-021)
- Migracoes para novos componentes (EP-018, EP-019)
- Logica de negocio, entidades, value objects novos, repositorios, use cases

**IMPORTANTE**: Este epico cria **infraestrutura de estilizacao** reutilizavel. Os delegates devem estar prontos e testaveis, mas sua integracao com QTableView sera EP-018. O stylesheet deve estar completo e aplicado via `app.setStyleSheet()`, mas ajustes finos de layout serao epicos posteriores.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade para RNFs**: Todo componente deve mapear para um ou mais RNFs do SRS.
   Incluir matriz de rastreabilidade: Componente <-> RNF <-> Criterio de Aceite do Epico.

2. **Codigo existente como baseline**: Nao redefinir Views, ViewModels, Container ou Entry Point
   ja implementados em EP-008. Especificar apenas **novos artefatos** (styles/, delegates/, assets/)
   e **edicoes minimas** necessarias (app.py para carregar stylesheet).

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Paleta de cores completa e validada**: Incluir todas as 30+ cores definidas no epico
   com seus valores hex. Para badges de status, incluir `bg`, `text`, `border` para cada status.
   Validar contraste WCAG 4.5:1 para cada combinacao texto/fundo.

5. **Indicadores nao-cromaticos especificados**: Definir simbolo Unicode para cada status
   (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) conforme epico. Simbolos devem ser
   renderizados como prefixo no badge pelo StatusBadgeDelegate.

6. **apply_theme() com ordem correta**: Especificar implementacao que ordena substituicoes
   do placeholder mais longo para o mais curto, evitando conflitos parciais
   (ex: `@primary-pressed` antes de `@primary`).

7. **QSS com placeholders exclusivamente**: O arquivo stylesheet.qss NAO DEVE conter
   valores hex literais. Todos os valores de cor, fonte e espacamento devem usar
   placeholders `@var` que serao substituidos por apply_theme().

8. **Lista de widgets cobertos pelo QSS**: Especificar seletores para no minimo:
   QMainWindow, QToolBar, QToolButton, QTableView, QHeaderView::section,
   QDialog, QPushButton, QLineEdit, QComboBox, QSpinBox, QDateEdit,
   QStatusBar, QMenuBar, QMenu, QMenu::item, QScrollBar.

9. **Delegates com paint() otimizado**: StatusBadgeDelegate e MonospaceDelegate devem
   pre-calcular cores e fontes. Metodo paint() NAO deve fazer lookup de dicionario
   ou I/O durante renderizacao. Manter tempo de paint() <= 16ms.

10. **Testes unitarios para theme.py**: Testar apply_theme() com template contendo
    placeholders, verificar que todos sao substituidos corretamente, nenhum placeholder
    restante no output.

11. **Testes unitarios para delegates**: Testar que StatusBadgeDelegate retorna cor/simbolo
    correto para cada StoryStatus. Testar que MonospaceDelegate aplica familia de fonte
    correta. NAO testar paint() diretamente (muito complexo), apenas logica de mapeamento.

12. **Icones SVG listados individualmente**: Para cada um dos 16 icones, especificar:
    nome do arquivo, icone Phosphor correspondente, uso pretendido na UI, tamanho (16x16px).

13. **Integracao em app.py especificada**: Detalhar exatamente onde no app.py inserir
    codigo para carregar stylesheet.qss, chamar apply_theme(), e app.setStyleSheet().
    Incluir tratamento de erro se arquivo nao existir.

14. **Fallback de fontes documentado**: Especificar font-family com fallback chain
    completa para Inter e JetBrains Mono. Documentar que fontes preferidas nao sao
    obrigatorias.

15. **Focus ring e areas clicaveis**: Incluir regras QSS para `:focus` em QPushButton,
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QTableView. Incluir `min-width: 32px`
    e `min-height: 32px` para QToolButton.

16. **Performance documentada**: Especificar que delegates nao devem fazer operacoes
    lentas em paint(). Incluir nota sobre pre-calculo de cores no __init__ ou como
    constantes de classe.

17. **Sem sobreposicao com EP-018 a EP-022**: Nao especificar integracao de delegates
    na tabela (EP-018), aplicacao de icones em toolbar (EP-018), migracoes de layout
    (EP-018), ajustes de dialogs (EP-021). EP-017 cria fundacao, epicos seguintes integram.

18. **Consistencia de nomenclatura**: Usar nomes do epico (theme.py, stylesheet.qss,
    status_badge_delegate.py, monospace_delegate.py). Nao criar arquivos com nomes diferentes.

19. **Idioma**: Todos os comentarios em codigo devem ser em ingles. Documentacao da spec
    e textos de UI (tooltips, mensagens) devem ser em portugues brasileiro, conforme
    Constituicao §XV.

20. **Estrutura de diretorios criada**: Especificar criacao de __init__.py para
    `presentation/styles/` e `presentation/delegates/` tornando-os pacotes Python.
    Especificar criacao de `presentation/assets/icons/` com os 16 arquivos SVG.
</rules>
