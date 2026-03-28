# Decomposição do Épico de Refatoração GUI — Backlog Manager v2

> Fonte: `docs/prompt_gui_refactor.md`
> Gerado em: 27/03/2026

---

## Visão Geral da Sequência

| Ordem | Código  | Nome                                | Domínio                  | Dependências       | Impacto Visual       |
|-------|---------|-------------------------------------|--------------------------|--------------------|-----------------------|
| 1     | GUI-001 | Design System e Fundação Visual     | Fundação Visual          | —                  | Médio (QSS global)    |
| 2     | GUI-002 | Layout Principal e Migração de Painéis | Layout Principal      | GUI-001            | Alto                  |
| 3     | GUI-003 | Tabela de Backlog                   | Tabela Core              | GUI-001, GUI-002   | Alto                  |
| 4     | GUI-004 | Busca, Filtros e Menu de Contexto   | Interação e Filtros      | GUI-003            | Alto                  |
| 5     | GUI-005 | Estilização de Dialogs              | Dialogs                  | GUI-001            | Médio                 |
| 6     | GUI-006 | Polimento e UX Avançado             | Polimento e UX Avançado  | GUI-002 a GUI-005  | Médio                 |

## Mapa de Dependências

```text
GUI-001 (Design System e Fundação Visual)
  ├── GUI-002 (Layout Principal e Migração de Painéis)
  │    └── GUI-003 (Tabela de Backlog)
  │         └── GUI-004 (Busca, Filtros e Menu de Contexto)
  │
  ├── GUI-005 (Estilização de Dialogs)
  │
  └── GUI-006 (Polimento e UX Avançado)
       ← depende de GUI-002, GUI-003, GUI-004, GUI-005
```

Notas:
- **GUI-005** depende apenas de **GUI-001** (QSS/tokens) e pode ser implementado em paralelo com GUI-003 e GUI-004.
- **GUI-006** é o sub-épico de fechamento e depende de todos os anteriores.

## Matriz de Rastreabilidade: Componente → Sub-Épico

| ID      | Componente                        | Sub-Épico |
|---------|-----------------------------------|-----------|
| DS-001  | Design Tokens (theme.py)          | GUI-001   |
| DS-002  | Stylesheet QSS (stylesheet.qss)   | GUI-001   |
| DS-003  | StatusBadgeDelegate               | GUI-001   |
| DS-004  | MonospaceDelegate                 | GUI-001   |
| DS-005  | Biblioteca de Ícones              | GUI-001   |
| MW-001  | Menu Bar                          | GUI-002   |
| MW-002  | Toolbar                           | GUI-002   |
| MW-003  | Barra de Busca/Filtros            | GUI-004   |
| MW-004  | Tabela de Backlog                 | GUI-003   |
| MW-005  | Status Bar                        | GUI-002   |
| MW-006  | Layout Vertical                   | GUI-002   |
| MW-007  | Menu de Contexto                  | GUI-004   |
| MW-008  | Estado Vazio                      | GUI-003   |
| DLG-001 | StoryDialog                       | GUI-005   |
| DLG-002 | DeveloperDialog                   | GUI-005   |
| DLG-003 | FeatureDialog                     | GUI-005   |
| DLG-004 | ConfigDialog                      | GUI-002   |
| DLG-005 | DependencyDialog                  | GUI-002   |
| DLG-006 | MetricsDialog                     | GUI-002   |
| DLG-007 | ConfirmDeleteDialog               | GUI-005   |
| DLG-008 | Progress/Result Dialogs           | GUI-005   |
| UX-001  | Duplicar História na UI           | GUI-004   |
| UX-002  | Atribuição Manual de Dev          | GUI-005   |
| UX-003  | Filtros Rápidos por Status        | GUI-004   |
| UX-004  | Filtro por Feature/Onda           | GUI-004   |
| UX-005  | Agrupamento Visual por Onda       | GUI-006   |
| UX-006  | Tooltip Rico na Tabela            | GUI-006   |
| UX-007  | Indicador de Bloqueio             | GUI-006   |
| UX-008  | SP por Status na Status Bar       | GUI-006   |
| UX-009  | Dialog Sobre                      | GUI-006   |
| UX-010  | Cancelamento de Operações         | GUI-006   |
| UX-011  | Persistência de Config            | GUI-006   |
| UX-012  | Validação em Tempo Real           | GUI-005   |
| UX-013  | Estados Vazios em Dialogs         | GUI-005   |
| ACC-001 | Contraste WCAG 4.5:1             | GUI-001   |
| ACC-002 | Indicadores não-cromáticos        | GUI-001   |
| ACC-003 | Focus ring visível                | GUI-001   |
| ACC-004 | Áreas clicáveis mínimas           | GUI-001   |
| RSP-001 | Responsividade a resize           | GUI-006   |
| RSP-002 | Resolução mínima 1024×600         | GUI-006   |

---

## GUI-001 — Design System e Fundação Visual

**Domínio:** Fundação Visual

### Problema que Resolve

A aplicação não possui sistema de design: nenhum QSS é aplicado, não há tokens de cor/tipografia/espaçamento centralizados, não há delegates customizados para renderização de células, e não há ícones SVG. Toda estilização subsequente depende desta fundação. Sem ela, cada sub-épico teria que definir seus próprios valores de cor e estilo, gerando inconsistência. Os requisitos de acessibilidade (contraste WCAG, indicadores não-cromáticos, focus ring) também devem ser embutidos nos artefatos fundacionais para que sejam herdados automaticamente por todos os componentes futuros.

### Objetivo (Valor Mensurável)

Entregar o módulo de design tokens (`theme.py`), o stylesheet centralizado (`stylesheet.qss`), os delegates de renderização customizada (`StatusBadgeDelegate`, `MonospaceDelegate`), a biblioteca de ícones SVG, e os padrões de acessibilidade embutidos. Ao final, ao iniciar a aplicação, **todos os widgets padrão Qt** receberão estilização moderna automaticamente via `app.setStyleSheet()`. Os delegates estarão prontos para integração na tabela (GUI-003).

### Escopo

**Componentes incluídos:**

| ID      | Componente                | Tipo  | Descrição do que fazer                                                                                                       |
|---------|---------------------------|-------|------------------------------------------------------------------------------------------------------------------------------|
| DS-001  | Design Tokens (theme.py)  | NOVO  | Criar módulo Python com todas as constantes de cores (30+ tokens), tipografia (famílias, tamanhos, pesos), espaçamento (7 níveis), border-radius (4 níveis), sombras (3 níveis), e função `apply_theme()` |
| DS-002  | Stylesheet QSS            | NOVO  | Criar arquivo QSS centralizado com placeholders `@var`, cobrindo todos os tipos de widget: QMainWindow, QToolBar, QToolButton, QTableView, QHeaderView, QDialog, QPushButton, QLineEdit, QComboBox, QSpinBox, QDateEdit, QGroupBox, QListWidget, QStatusBar, QMenuBar, QMenu, QScrollBar, filter chips, search bar |
| DS-003  | StatusBadgeDelegate       | NOVO  | Criar QStyledItemDelegate que renderiza badges pill (border-radius 10px, 20px altura, 11px fonte, weight 500, min-width 70px) com cores por status e prefixos não-cromáticos (● ▶ ◆ ✓ ✕) |
| DS-004  | MonospaceDelegate         | NOVO  | Criar QStyledItemDelegate que renderiza texto em fonte monospace (JetBrains Mono → Cascadia Code → Consolas fallback) |
| DS-005  | Biblioteca de Ícones      | NOVO  | Empacotar 16 SVGs (Phosphor Icons, estilo Regular/outline, 16×16px): plus, pencil-simple, trash, arrow-up, arrow-down, users, package, gear, calendar-check, shuffle, download-simple, upload-simple, copy, warning-triangle, link, x |
| ACC-001 | Contraste WCAG 4.5:1      | NOVO  | Validar e garantir contraste ≥ 4.5:1 em todas as combinações texto/fundo dos tokens definidos |
| ACC-002 | Indicadores não-cromáticos | NOVO | Implementar prefixos de símbolo nos badges de status dentro do StatusBadgeDelegate |
| ACC-003 | Focus ring visível         | NOVO | Incluir no QSS regras de `:focus` com `border: 2px solid @primary` em todos os widgets interativos |
| ACC-004 | Áreas clicáveis mínimas   | NOVO  | Definir no QSS dimensões mínimas de 32×32px para QToolButton e botões de ação |

**Fora do escopo:**
- Integração dos delegates na tabela → GUI-003
- Ícones aplicados na toolbar/menus → GUI-002
- Aplicação do QSS nos dialogs existentes (estilização automática via seletores de tipo já funciona, mas ajustes finos nos dialogs → GUI-005)

### Arquivos Impactados

| Arquivo                                                              | Ação  | Descrição                                                                                         |
|----------------------------------------------------------------------|-------|----------------------------------------------------------------------------------------------------|
| `src/backlog_manager/presentation/styles/__init__.py`                | CRIAR | Tornar `styles/` um pacote Python                                                                 |
| `src/backlog_manager/presentation/styles/theme.py`                   | CRIAR | Módulo de design tokens com 30+ constantes e `apply_theme()`                                      |
| `src/backlog_manager/presentation/styles/stylesheet.qss`             | CRIAR | Stylesheet QSS centralizado com placeholders `@var`                                               |
| `src/backlog_manager/presentation/delegates/__init__.py`             | CRIAR | Tornar `delegates/` um pacote Python                                                              |
| `src/backlog_manager/presentation/delegates/status_badge_delegate.py`| CRIAR | QStyledItemDelegate para badges de status                                                         |
| `src/backlog_manager/presentation/delegates/monospace_delegate.py`   | CRIAR | QStyledItemDelegate para IDs em fonte monospace                                                   |
| `src/backlog_manager/presentation/assets/icons/`                     | CRIAR | Diretório com 16 arquivos SVG (Phosphor Icons)                                                    |
| `src/backlog_manager/presentation/app.py`                            | EDITAR | Carregar `stylesheet.qss`, aplicar `apply_theme()`, e chamar `app.setStyleSheet()` na inicialização |

### Especificações Técnicas Relevantes

**Paleta de Cores Completa (theme.py):**

```python
# — Cores primárias —
PRIMARY = "#5B5BD6"        # indigo — ações, seleção, links
PRIMARY_HOVER = "#4C4CC4"
PRIMARY_PRESSED = "#3E3EB0"
PRIMARY_LIGHT = "#EEF2FF"  # fundo de seleção na tabela

# — Semânticas —
SUCCESS = "#30A46C"        # verde — conclusão
SUCCESS_LIGHT = "#DDF3E4"
WARNING = "#F5A623"        # âmbar — testes/atenção
WARNING_LIGHT = "#FFF7C2"
ERROR = "#E5484D"          # vermelho — impedido/destrutivo
ERROR_LIGHT = "#FFE5E5"

# — Neutras (13 tons) —
NEUTRAL_0 = "#FFFFFF"      # fundo de dialogs, inputs
NEUTRAL_50 = "#FAFAFA"     # fundo do MainWindow
NEUTRAL_100 = "#F5F5F5"    # fundo de header, menu bar, status bar
NEUTRAL_150 = "#EFEFEF"    # zebra striping
NEUTRAL_200 = "#E5E5E5"    # bordas, separadores, grid lines
NEUTRAL_300 = "#D4D4D4"    # borda de inputs em repouso
NEUTRAL_400 = "#A3A3A3"    # texto placeholder, ícones inativos
NEUTRAL_500 = "#737373"    # texto secundário, labels
NEUTRAL_600 = "#525252"    # texto de corpo
NEUTRAL_700 = "#404040"    # texto de ênfase
NEUTRAL_800 = "#262626"    # títulos, texto primário
NEUTRAL_900 = "#171717"    # texto máximo contraste

# — Badges de status (bg / text / border) —
STATUS_COLORS = {
    "BACKLOG":   {"bg": "#E5E5E5", "text": "#525252", "border": "#D4D4D4"},
    "EXECUÇÃO":  {"bg": "#EEF2FF", "text": "#5B5BD6", "border": "#C7D2FE"},
    "TESTES":    {"bg": "#FFF7C2", "text": "#946800", "border": "#F5D90A"},
    "CONCLUÍDO": {"bg": "#DDF3E4", "text": "#18794E", "border": "#8ECEAA"},
    "IMPEDIDO":  {"bg": "#FFE5E5", "text": "#CE2C31", "border": "#F9A8AB"},
}

# — Indicadores não-cromáticos por status —
STATUS_SYMBOLS = {
    "BACKLOG": "●", "EXECUÇÃO": "▶", "TESTES": "◆",
    "CONCLUÍDO": "✓", "IMPEDIDO": "✕",
}
```

**Tipografia:**
- Fonte principal: `"Inter", "Segoe UI", system-ui, sans-serif`
- Fonte monospace: `"JetBrains Mono", "Cascadia Code", "Consolas", monospace`
- Escala: xs=11px, sm=12px, base=13px, md=14px, lg=16px, xl=18px
- Pesos: normal=400, medium=500, semibold=600, bold=700
- Line-height: 1.5 corpo, 1.2 headers/badges

**Espaçamento:** 4px, 8px, 12px, 16px, 20px, 24px, 32px (múltiplos de 4)

**Border-radius:** sm=4px (badges, chips), md=6px (inputs, botões), lg=8px (dialogs), xl=12px (tooltips)

**Sombras (QGraphicsDropShadowEffect):**
- sm: offset(0,1) blur(3) rgba(0,0,0,0.08) — botões hover
- md: offset(0,4) blur(12) rgba(0,0,0,0.10) — dialogs, popups
- lg: offset(0,8) blur(24) rgba(0,0,0,0.12) — menus dropdown

**Badge de Status (StatusBadgeDelegate):**
- Formato pill: border-radius 10px (metade da altura)
- Padding: 2px vertical, 8px horizontal
- Altura: 20px, fonte 11px, weight 500, min-width 70px
- Border: 1px solid (cor varia por status)
- Texto: prefixo símbolo + espaço + nome do status (ex: "● BACKLOG", "✓ CONCLUÍDO")

**Mapeamento de Ícones SVG (16 arquivos):**
| Arquivo SVG             | Uso                        | Tamanho     |
|-------------------------|----------------------------|-------------|
| `plus.svg`              | + Nova                     | 16×16px     |
| `pencil-simple.svg`     | Editar                     | 16×16px     |
| `trash.svg`             | Deletar                    | 16×16px     |
| `arrow-up.svg`          | Mover Cima                 | 16×16px     |
| `arrow-down.svg`        | Mover Baixo                | 16×16px     |
| `users.svg`             | Desenvolvedores            | 16×16px     |
| `package.svg`           | Features                   | 16×16px     |
| `gear.svg`              | Configuração               | 16×16px     |
| `calendar-check.svg`    | Calcular Cronograma        | 16×16px     |
| `shuffle.svg`           | Alocar Devs                | 16×16px     |
| `download-simple.svg`   | Importar                   | 16×16px     |
| `upload-simple.svg`     | Exportar                   | 16×16px     |
| `copy.svg`              | Duplicar                   | 16×16px     |
| `warning-triangle.svg`  | Alerta (ConfirmDelete)     | 16×16px     |
| `link.svg`              | Dependências               | 16×16px     |
| `x.svg`                 | Fechar                     | 16×16px     |

Cor dos ícones: `@neutral-600` normal, `@neutral-800` hover, `@neutral-400` disabled.

**Exemplo de QSS Estruturado (seções obrigatórias no stylesheet.qss):**

```css
/* === Base === */
QMainWindow { background-color: @neutral-50; }

/* === Menu Bar === */
QMenuBar { background-color: @neutral-100; font-size: @font-size-base; }
QMenuBar::item:selected { background-color: @primary; color: white; border-radius: @radius-sm; }

/* === Toolbar === */
QToolBar { background-color: @neutral-50; border-bottom: 1px solid @neutral-200; spacing: 4px; padding: 4px 8px; }
QToolButton { border-radius: @radius-md; padding: 6px 10px; font-size: @font-size-base; color: @neutral-700; min-width: 32px; min-height: 32px; }
QToolButton:hover { background-color: @neutral-200; }
QToolButton:pressed { background-color: @neutral-300; }
QToolButton:disabled { opacity: 0.5; }

/* === Table === */
QTableView { alternate-background-color: @neutral-150; gridline-color: transparent; selection-background-color: @primary-light; selection-color: @neutral-800; }
QTableView::item { padding: 0px 8px; height: 36px; border-bottom: 1px solid @neutral-200; }
QTableView::item:selected { background-color: @primary-light; color: @neutral-800; }
QHeaderView::section { background-color: @neutral-100; font-weight: 600; padding: 8px; border: none; border-bottom: 2px solid @neutral-200; font-size: @font-size-sm; color: @neutral-500; }

/* === Inputs === */
QLineEdit, QComboBox, QSpinBox, QDateEdit { border: 1px solid @neutral-300; border-radius: @radius-md; padding: 8px 12px; font-size: @font-size-base; }
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QDateEdit:focus { border-color: @primary; border: 2px solid @primary; }

/* === Buttons === */
QPushButton { border-radius: @radius-md; padding: 8px 16px; font-weight: 500; font-size: @font-size-base; height: 36px; }
QPushButton#btnSave { background-color: @primary; color: white; }
QPushButton#btnSave:hover { background-color: @primary-hover; }
QPushButton#btnDelete, QPushButton#btnConfirmDelete { background-color: @error; color: white; }
QPushButton#btnCancel { background-color: @neutral-200; color: @neutral-700; }
QPushButton:focus { border: 2px solid @primary; }

/* === Status Bar === */
QStatusBar { background-color: @neutral-100; border-top: 1px solid @neutral-200; font-size: @font-size-sm; color: @neutral-600; padding: 0px 12px; min-height: 24px; }

/* === Dialogs === */
QDialog { background-color: white; border-radius: @radius-lg; }
QDialog QLabel#dialogTitle { font-size: @font-size-lg; font-weight: 600; color: @neutral-800; }

/* === Context Menu === */
QMenu { background-color: white; border: 1px solid @neutral-200; border-radius: @radius-md; padding: 4px 0px; }
QMenu::item { padding: 6px 32px 6px 12px; font-size: @font-size-base; color: @neutral-700; }
QMenu::item:selected { background-color: @neutral-100; }
QMenu::separator { height: 1px; background: @neutral-200; margin: 4px 8px; }

/* === Filter Chips === */
QPushButton.filterChip { border-radius: @radius-sm; padding: 4px 12px; font-size: @font-size-sm; background-color: @neutral-100; color: @neutral-600; border: 1px solid @neutral-200; }
QPushButton.filterChip:checked { background-color: @primary; color: white; border-color: @primary; }

/* === Search Bar === */
QLineEdit#searchField { border: 1px solid @neutral-300; border-radius: @radius-md; padding: 6px 12px 6px 32px; font-size: @font-size-base; min-width: 240px; }
QLineEdit#searchField:focus { border-color: @primary; }

/* === Scrollbar === */
QScrollBar:vertical { width: 8px; background: transparent; }
QScrollBar::handle:vertical { background: @neutral-300; border-radius: 4px; min-height: 20px; }
```

**Validação de Contraste WCAG 4.5:1 (ACC-001):**
| Combinação                                 | Ratio  | Status |
|--------------------------------------------|--------|--------|
| @neutral-800 (#262626) sobre @neutral-0 (#FFFFFF) | 16.5:1 | ✓      |
| Badge BACKLOG #525252 sobre #E5E5E5        | 4.6:1  | ✓      |
| Badge EXECUÇÃO #5B5BD6 sobre #EEF2FF       | 4.7:1  | ✓      |
| Badge CONCLUÍDO #18794E sobre #DDF3E4      | 4.5:1  | ✓      |
| Badge IMPEDIDO #CE2C31 sobre #FFE5E5       | 4.8:1  | ✓      |

### Critérios de Aceite

- [ ] `theme.py` contém todas as 30+ constantes de cor, 6 tamanhos de fonte, 4 pesos, 7 espaçamentos, 4 border-radius, 3 sombras, e dicionários `STATUS_COLORS` e `STATUS_SYMBOLS`
- [ ] `apply_theme()` substitui corretamente todos os placeholders `@var` no template QSS
- [ ] `stylesheet.qss` cobre todos os tipos de widget listados (QMainWindow, QToolBar, QToolButton, QTableView, QHeaderView, QDialog, QPushButton, QLineEdit, QComboBox, QSpinBox, QDateEdit, QGroupBox, QListWidget, QStatusBar, QMenuBar, QMenu, QScrollBar, filterChip, searchField)
- [ ] QSS inclui pseudo-states `:hover`, `:pressed`, `:disabled`, `:focus`, `:selected`, `:alternate` onde aplicável
- [ ] `StatusBadgeDelegate` renderiza pills com cores corretas para os 5 status, incluindo prefixos ● ▶ ◆ ✓ ✕
- [ ] `MonospaceDelegate` renderiza texto usando fallback chain JetBrains Mono → Cascadia Code → Consolas
- [ ] 16 ícones SVG presentes no diretório `assets/icons/` e carregáveis via `QIcon`
- [ ] `app.py` carrega e aplica o QSS na inicialização — widgets padrão são estilizados ao abrir a aplicação
- [ ] Contraste ≥ 4.5:1 validado para todas as combinações texto/fundo de badges
- [ ] Focus ring (border 2px solid @primary) visível ao navegar com Tab em widgets interativos
- [ ] QToolButton tem dimensão mínima 32×32px no QSS
- [ ] Testes existentes continuam passando sem regressão

### Plano de Validação

| Tipo             | Descrição                                                                                                |
|------------------|----------------------------------------------------------------------------------------------------------|
| Teste Manual     | Iniciar aplicação e verificar que widgets padrão (botões, inputs, tabela) recebem estilização do QSS     |
| Teste Manual     | Inspecionar visualmente que ícones SVG carregam sem distorção                                            |
| Teste Unitário   | Testar `apply_theme()`: dado template com placeholders, retorna QSS com valores substituídos             |
| Teste Unitário   | Testar `StatusBadgeDelegate.paint()`: renderiza corretamente para cada status (mock QPainter)            |
| Teste Unitário   | Testar `MonospaceDelegate`: aplica família de fonte monospace                                            |
| Revisão de Código| Verificar que nenhum valor hardcoded de cor/fonte aparece fora de `theme.py`                             |
| Revisão de Código| Confirmar que QSS usa exclusivamente placeholders `@var` (nenhum hex literal no .qss)                    |

### Dependências

*Sem dependências* — este é o sub-épico fundacional.

### Riscos

| Descrição                                                              | Mitigação                                                                                                          |
|------------------------------------------------------------------------|--------------------------------------------------------------------------------------------------------------------|
| QSS do PySide6 pode não suportar todas as propriedades CSS usadas (ex: `outline`, `opacity`) | Testar cada propriedade isoladamente em PySide6. Propriedades não suportadas: usar alternativas (ex: `border` ao invés de `outline`, alpha no `color` ao invés de `opacity`) |
| Fontes Inter/JetBrains Mono podem não estar instaladas no Windows do usuário | Usar fallback chain nativa: `"Inter", "Segoe UI", system-ui` e `"JetBrains Mono", "Cascadia Code", "Consolas"`. Segoe UI e Consolas são nativos do Windows |
| SVGs Phosphor podem ter problemas de renderização via QIcon/QPixmap em certas resoluções | Validar renderização em 100% e 125% DPI. Usar `QSvgRenderer` se `QIcon(path)` não renderizar corretamente |
| `apply_theme()` com replace sequencial pode ter conflitos de substituição (ex: `@primary` matcha antes de `@primary-hover`) | Ordenar substituições do mais longo para o mais curto (ex: `@primary-pressed` antes de `@primary-hover` antes de `@primary`) |

---

## GUI-002 — Layout Principal e Migração de Painéis

**Domínio:** Layout Principal

### Problema que Resolve

A MainWindow utiliza um QSplitter horizontal onde a tabela ocupa 70% e os painéis laterais (ConfigPanel, DependencyPanel, MetricsPanel, WarningsPanel) ocupam 30%. Não existe Menu Bar nem Status Bar. A toolbar usa apenas texto sem ícones e sem agrupamento visual. O layout desperdiça espaço lateral e não corresponde ao padrão moderno de aplicações desktop (layout vertical com zonas empilhadas). Os painéis laterais devem ser migrados para dialogs modais para liberar 100% da largura para a tabela.

### Objetivo (Valor Mensurável)

Transformar a MainWindow em layout vertical de 5 zonas (Menu Bar 28px → Toolbar 44px → Barra de Filtros 36px → Tabela 100% → Status Bar 24px). Adicionar Menu Bar com 4 menus funcionais. Refatorar toolbar com ícones SVG e 5 grupos separados. Adicionar Status Bar com contadores e área de avisos. Migrar ConfigPanel, DependencyPanel, MetricsPanel para dialogs modais acessíveis via menu/toolbar, e WarningsPanel para a Status Bar. Remover QSplitter horizontal.

### Escopo

**Componentes incluídos:**

| ID      | Componente           | Tipo          | Descrição do que fazer                                                                                                  |
|---------|----------------------|---------------|-------------------------------------------------------------------------------------------------------------------------|
| MW-001  | Menu Bar             | NOVO          | Criar QMenuBar com 4 menus: Arquivo (Importar/Exportar/Sair), Cadastros (Histórias/Features/Devs/Configuração), Ferramentas (Cronograma/Alocação), Ajuda (Sobre) |
| MW-002  | Toolbar              | REFATORAÇÃO   | Adicionar ícones SVG (QIcon), ToolButtonTextBesideIcon, 5 grupos com separadores, altura 32px, dimensões/estados via QSS |
| MW-005  | Status Bar           | NOVO          | Criar QStatusBar: contadores à esquerda (histórias, SP, último cálculo), avisos à direita (migra WarningsPanel), popup de avisos |
| MW-006  | Layout Vertical      | REFATORAÇÃO   | Remover QSplitter horizontal, converter para QVBoxLayout com 5 zonas empilhadas, tabela ocupa 100% da largura          |
| DLG-004 | ConfigDialog         | MIGRAÇÃO      | Converter ConfigPanel (QWidget inline) → QDialog modal com campos existentes (velocidade, data início, máx dias ociosos) + textos explicativos + botões Aplicar/Cancelar |
| DLG-005 | DependencyDialog     | MIGRAÇÃO      | Converter DependencyPanel (QWidget inline) → QDialog modal 500×420px com seções "Depende de" e "Dependentes", dropdown de adição, erro de ciclo estilizado |
| DLG-006 | MetricsDialog        | MIGRAÇÃO      | Converter MetricsPanel (QWidget inline) → QDialog modal 440×380px com grid label:valor, exibido automaticamente pós-alocação |

**Fora do escopo:**
- Barra de Busca/Filtros (espaço reservado mas vazio) → GUI-004
- Expansão da tabela para 13 colunas → GUI-003
- Estilização fina dos dialogs StoryDialog, DeveloperDialog, FeatureDialog → GUI-005
- Ação "Duplicar" na toolbar (botão reservado mas sem wiring) → GUI-004

### Arquivos Impactados

| Arquivo                                                               | Ação     | Descrição                                                                                           |
|-----------------------------------------------------------------------|----------|------------------------------------------------------------------------------------------------------|
| `src/backlog_manager/presentation/views/main_window.py`               | EDITAR   | Refatoração maior: adicionar QMenuBar, refatorar QToolBar com ícones, adicionar QStatusBar, remover QSplitter, layout vertical |
| `src/backlog_manager/presentation/views/config_dialog.py`             | CRIAR    | QDialog modal migrando lógica de `config_panel.py`                                                  |
| `src/backlog_manager/presentation/views/dependency_dialog.py`         | CRIAR    | QDialog modal migrando lógica de `dependency_panel.py`                                              |
| `src/backlog_manager/presentation/views/metrics_dialog.py`            | CRIAR    | QDialog modal migrando lógica de `metrics_panel.py`                                                 |
| `src/backlog_manager/presentation/views/config_panel.py`              | DEPRECAR | Manter arquivo mas remover uso em main_window.py (pode ser deletado após validação)                 |
| `src/backlog_manager/presentation/views/dependency_panel.py`          | DEPRECAR | Manter arquivo mas remover uso em main_window.py                                                    |
| `src/backlog_manager/presentation/views/metrics_panel.py`             | DEPRECAR | Manter arquivo mas remover uso em main_window.py                                                    |
| `src/backlog_manager/presentation/views/warnings_panel.py`            | DEPRECAR | Funcionalidade migra para Status Bar                                                                |
| `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`| EDITAR   | Ajustar wiring para novos dialogs e status bar (signals/slots)                                      |
| `src/backlog_manager/presentation/viewmodels/allocation_viewmodel.py` | EDITAR   | Wiring para exibir MetricsDialog automaticamente pós-alocação                                       |

### Especificações Técnicas Relevantes

**Layout Vertical de 5 Zonas (dimensões em 1280×720):**

```
┌─────────────────────────────────────────────────┐
│ MENU BAR (28px altura fixa)                     │
├─────────────────────────────────────────────────┤
│ TOOLBAR (44px altura fixa)                      │
├─────────────────────────────────────────────────┤
│ BARRA DE FILTROS (36px, reservar espaço vazio)  │
├─────────────────────────────────────────────────┤
│ TABELA DE BACKLOG (~588px, stretch)             │
├─────────────────────────────────────────────────┤
│ STATUS BAR (24px altura fixa)                   │
└─────────────────────────────────────────────────┘
```

**Menu Bar (MW-001):**

```
Arquivo
  ├─ Importar Excel (Ctrl+I)
  ├─ Exportar Excel (Ctrl+E)
  └─ Sair

Cadastros
  ├─ Histórias (Ctrl+N)
  ├─ Features
  ├─ Desenvolvedores
  └─ Configuração

Ferramentas
  ├─ Calcular Cronograma (Ctrl+Shift+C)
  └─ Alocar Desenvolvedores (Ctrl+Shift+A)

Ajuda
  └─ Sobre
```

QSS: fundo `@neutral-100`, fonte `@font-size-base`, item selecionado `@primary` bg + branco texto + `@radius-sm`.

**Toolbar (MW-002) — 5 grupos com separadores:**

| Grupo                   | Ações                                    | Ícones                                           |
|-------------------------|------------------------------------------|--------------------------------------------------|
| 1 — CRUD de Histórias   | + Nova, Editar, Deletar                  | plus.svg, pencil-simple.svg, trash.svg           |
| 2 — Priorização         | Mover Cima, Mover Baixo                  | arrow-up.svg, arrow-down.svg                     |
| 3 — Cadastros           | Desenvolvedores, Features, Configuração  | users.svg, package.svg, gear.svg                 |
| 4 — Processamento       | Calcular Cronograma, Alocar Devs         | calendar-check.svg, shuffle.svg                  |
| 5 — Excel               | Importar, Exportar                       | download-simple.svg, upload-simple.svg           |

Estilo de cada QToolButton: `ToolButtonTextBesideIcon`, ícone 16×16px + texto 13px, altura 32px, padding 6px 10px, border-radius `@radius-md`. Separadores: `QToolBar::addSeparator()` com 1px solid `@neutral-200`, margem horizontal 8px. Tooltip com shortcut: ex. "Nova História (Ctrl+N)".

**Status Bar (MW-005):**

- Altura fixa: 24px. Borda superior: 1px solid `@neutral-200`. Fundo: `@neutral-100`.
- Fonte: 12px, cor `@neutral-600`. Separador entre itens: `"  ·  "` em `@neutral-300`.
- **Área esquerda** (QLabels permanentes): "42 histórias", "284 SP", "Última alocação: 27/03/2026 14:30"
- **Área direita** (avisos, migra do WarningsPanel):
  - Exibe o aviso mais crítico como texto inline color-coded
  - Ícone de indicador: Vermelho (deadlock), Laranja (ociosidade intra-onda), Cinza (ociosidade inter-ondas)
  - Múltiplos avisos: aviso mais crítico + badge contagem ("⚠ 3 avisos"), badge: fundo `@error`, texto branco, border-radius 10px, padding 2px 6px, font 11px
  - Clique abre QFrame popup fixado acima da status bar: largura 400px, altura máxima 240px, scroll vertical se > 5 itens
  - Sem avisos: "✓ Sem avisos"

**ConfigDialog (DLG-004) — 420×340px:**

Campos existentes migrados:
- Velocidade (SP/dia): input numérico decimal (0.1 a 10.0, padrão 2.0)
- Data de início: date picker (padrão: hoje)
- Máx. dias ociosos: input numérico inteiro (2 a 30, padrão 3)

Adições: texto explicativo sutil abaixo de cada campo, botões [Aplicar] [Cancelar].

**DependencyDialog (DLG-005) — 500×420px:**

Título: "Dependências: AUTH-001 — Nome da História" (16px, weight 600).
Seção "Depende de:" com lista + dropdown [+]. Seção "Dependentes:" somente leitura.
Erro de ciclo: "Dependência cíclica detectada: A → B → C → A" com fundo `@error-light`.

**MetricsDialog (DLG-006) — 440×380px:**

Título: "Métricas da Alocação" (16px, weight 600). Grid 2 colunas (label `@neutral-500` : valor `@neutral-800` weight 600).
Métricas: Histórias Alocadas (X/Y), Tempo de Execução (X.XXs), Ondas Processadas (N), Total de Iterações (N), Deadlocks Detectados (N), Violações de Ociosidade (N/N). Botão [OK].

### Critérios de Aceite

- [ ] QSplitter horizontal removido — tabela ocupa 100% da largura
- [ ] Layout vertical com 5 zonas empilhadas: Menu Bar → Toolbar → Barra de Filtros (vazia) → Tabela → Status Bar
- [ ] Menu Bar funcional com 4 menus e todos os atalhos mapeados (Ctrl+I, Ctrl+E, Ctrl+N, Ctrl+Shift+C, Ctrl+Shift+A)
- [ ] Toolbar com ícones SVG visíveis e 5 grupos separados por separadores, ToolButtonTextBesideIcon
- [ ] Tooltips nos botões da toolbar incluem atalho de teclado (ex: "Nova História (Ctrl+N)")
- [ ] Status Bar visível com contadores atualizados (total histórias, SP total, última alocação)
- [ ] Área de avisos na Status Bar funcional: exibe aviso mais crítico, badge contagem, popup ao clicar
- [ ] ConfigPanel → ConfigDialog: campos velocidade, data início, máx dias ociosos funcionais como dialog modal
- [ ] DependencyPanel → DependencyDialog: adição/remoção de dependências funcional como dialog modal
- [ ] MetricsPanel → MetricsDialog: exibido automaticamente pós-alocação com métricas corretas
- [ ] WarningsPanel migrado para Status Bar: lista de avisos acessível via popup
- [ ] Funcionalidade completa preservada: todas as ações existentes continuam operando via menu, toolbar ou dialog
- [ ] Testes existentes continuam passando sem regressão

### Plano de Validação

| Tipo             | Descrição                                                                                              |
|------------------|--------------------------------------------------------------------------------------------------------|
| Teste Manual     | Navegar por todos os menus e verificar que cada ação abre o dialog/executa a funcionalidade correta    |
| Teste Manual     | Verificar toolbar: ícones renderizados, separadores visíveis, tooltips com shortcuts                   |
| Teste Manual     | Abrir ConfigDialog via menu Cadastros → Configuração, alterar valores, clicar Aplicar/Cancelar         |
| Teste Manual     | Abrir DependencyDialog via toolbar/menu, adicionar/remover dependência, verificar erro de ciclo        |
| Teste Manual     | Executar Alocar Desenvolvedores e verificar que MetricsDialog surge automaticamente                    |
| Teste Manual     | Verificar Status Bar: contadores, área de avisos, popup de avisos completo                             |
| Teste Unitário   | Testar que MainWindow instancia sem erro com novo layout                                               |
| Teste Unitário   | Testar ConfigDialog: valores padrão, validação de range, signals Aplicar/Cancelar                      |
| Revisão de Código| Confirmar que nenhum import de ConfigPanel/DependencyPanel/MetricsPanel/WarningsPanel resta em main_window.py |

### Dependências

| Sub-Épico | Motivo                                                                                                    |
|-----------|-----------------------------------------------------------------------------------------------------------|
| GUI-001   | QSS centralizado (estilização dos novos widgets), ícones SVG (toolbar), theme.py (cores dos avisos na Status Bar) |

### Riscos

| Descrição                                                                              | Mitigação                                                                                                        |
|----------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------|
| Migração simultânea de 4 painéis + reestruturação do layout pode gerar regressão difícil de isolar | Migrar painéis um a um: ConfigPanel → DependencyPanel → MetricsPanel → WarningsPanel. Testar funcionalidade após cada migração |
| Popup de avisos na Status Bar (QFrame fixado acima) pode ter problemas de posicionamento cross-platform | Usar `QWidget` com `setWindowFlags(Qt.Popup)` e calcular posição relativa à Status Bar. Testar em múltiplas resoluções |
| Remoção do QSplitter pode quebrar lógica de resize que dependia do splitter           | Verificar que nenhum ViewModel ou UseCase referencia diretamente o splitter ou seus widgets filhos                |
| MetricsDialog auto-show pós-alocação pode interferir com o fluxo se alocação falhar   | Exibir MetricsDialog apenas quando alocação completa com sucesso. Em caso de erro, exibir dialog de erro           |

---

## GUI-003 — Tabela de Backlog

**Domínio:** Tabela Core

### Problema que Resolve

A tabela de backlog utiliza QTableView com renderização padrão Qt, 8 colunas sem delegates customizados. O status é exibido como texto puro sem diferenciação visual. IDs não usam fonte monospace. Não há zebra striping, nem estado vazio, nem estilização de header/seleção. Faltam 5 colunas (Prioridade, Onda, Componente, Dependências, Duração) que fornecem contexto essencial ao planejamento.

### Objetivo (Valor Mensurável)

Expandir o StoryTableModel de 8 para 13 colunas. Integrar StatusBadgeDelegate (badges coloridos com indicadores não-cromáticos) e MonospaceDelegate (IDs em fonte monospace) — criados em GUI-001. Aplicar zebra striping, seleção estilizada, header estilizado, scrollbar slim. Implementar estado vazio com mensagem orientativa.

### Escopo

**Componentes incluídos:**

| ID      | Componente             | Tipo          | Descrição do que fazer                                                                                                             |
|---------|------------------------|---------------|------------------------------------------------------------------------------------------------------------------------------------|
| MW-004  | Tabela de Backlog      | REFATORAÇÃO   | Expandir StoryTableModel 8→13 colunas, integrar delegates, configurar larguras/alinhamentos, aplicar zebra striping e estilos via QSS |
| MW-008  | Estado Vazio           | NOVO          | Mostrar overlay/placeholder na tabela quando sem histórias: "Nenhuma história cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para começar." |

**Fora do escopo:**
- StatusBadgeDelegate e MonospaceDelegate (já criados em GUI-001 — aqui são apenas integrados)
- Busca e filtros sobre a tabela → GUI-004
- Tooltip rico e agrupamento por onda → GUI-006

### Arquivos Impactados

| Arquivo                                                               | Ação     | Descrição                                                                                                     |
|-----------------------------------------------------------------------|----------|----------------------------------------------------------------------------------------------------------------|
| `src/backlog_manager/presentation/viewmodels/story_table_model.py`    | EDITAR   | Expandir `columnCount()` 8→13, atualizar `headerData()` e `data()` para 13 colunas, ajustar roles e alinhamentos |
| `src/backlog_manager/presentation/views/main_window.py`               | EDITAR   | Integrar delegates nas colunas Status e ID, configurar `QHeaderView` (larguras, stretch), habilitar `alternatingRowColors`, implementar overlay de estado vazio |
| `tests/unit/test_story_table_model.py` (ou equivalente)               | EDITAR   | Atualizar testes que verificam `columnCount() == 8` para `== 13`, adicionar testes para novas colunas         |

### Especificações Técnicas Relevantes

**Ordem e Especificação das 13 Colunas:**

| #  | Coluna         | Largura  | Alinhamento | Delegate           | Detalhes                                                                         |
|----|----------------|----------|-------------|---------------------|----------------------------------------------------------------------------------|
| 0  | Prioridade     | 60px fixo| Centro      | —                   | Número inteiro (0 = mais prioritário)                                            |
| 1  | Feature        | 120px    | Esquerda    | —                   | Nome da feature ou "—", truncar com elipsis                                      |
| 2  | Onda           | 50px fixo| Centro      | —                   | Número da onda de entrega (0 = sem feature)                                      |
| 3  | ID             | 100px fixo| Esquerda   | MonospaceDelegate   | Formato "COMPONENTE-NNN" (ex: AUTH-001)                                          |
| 4  | Componente     | 80px     | Esquerda    | —                   | Texto ex: AUTH, API, UI                                                          |
| 5  | Nome           | stretch  | Esquerda    | —                   | Mínimo 200px, truncar com elipsis, `QHeaderView.Stretch`                         |
| 6  | Status         | 100px fixo| Centro     | StatusBadgeDelegate | Badge pill colorido com símbolo                                                  |
| 7  | Desenvolvedor  | 100px    | Esquerda    | —                   | Nome do dev (não ID), ou "—", truncar com elipsis                                |
| 8  | Dependências   | 120px    | Esquerda    | —                   | IDs separados por vírgula ou "—", truncar com elipsis + tooltip com lista completa|
| 9  | SP             | 40px fixo| Centro      | —                   | Story Points (3, 5, 8 ou 13)                                                    |
| 10 | Início         | 90px fixo| Centro      | —                   | Data DD/MM/YYYY ou "—"                                                           |
| 11 | Fim            | 90px fixo| Centro      | —                   | Data DD/MM/YYYY ou "—"                                                           |
| 12 | Duração        | 60px fixo| Centro      | —                   | Número de dias úteis ou "—"                                                      |

**Estilização da tabela (já definida no QSS de GUI-001, integrar aqui):**
- Zebra striping: `@neutral-0` e `@neutral-150` alternados — ativar `setAlternatingRowColors(True)`
- Seleção: fundo `@primary-light` (#EEF2FF), texto `@neutral-800` (sem inversão de cores)
- Header: fundo `@neutral-100`, texto `@neutral-500` uppercase, 12px, weight 600, border-bottom 2px solid `@neutral-200`
- Grid lines: transparent (sem grid), apenas `border-bottom: 1px solid @neutral-200` por item
- Altura das linhas: 36px, header 40px
- Scrollbar: 8px width, border-radius 4px, handle `@neutral-300`
- Focus: border 2px solid `@primary` na célula focada

**Truncação e tooltip:**
- Colunas Nome, Feature, Dependências, Desenvolvedor: `elideMode(Qt.ElideRight)`
- Tooltip automático com texto completo ao hover em células truncadas

**Estado vazio (MW-008):**
- Mensagem centralizada na área da tabela: "Nenhuma história cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para começar."
- Botões de processamento (Cronograma, Alocar) desabilitados visualmente (QSS `:disabled`)

### Critérios de Aceite

- [ ] `StoryTableModel.columnCount()` retorna 13
- [ ] `headerData()` retorna nomes corretos para as 13 colunas na ordem especificada
- [ ] `data()` retorna dados formatados para cada coluna (datas em DD/MM/YYYY, IDs em COMPONENTE-NNN, dev por nome)
- [ ] StatusBadgeDelegate integrado na coluna Status (índice 6): pills coloridos com prefixos ● ▶ ◆ ✓ ✕
- [ ] MonospaceDelegate integrado na coluna ID (índice 3): fonte monospace visível
- [ ] Zebra striping visível (linhas alternadas @neutral-0 / @neutral-150)
- [ ] Seleção com fundo @primary-light, texto não invertido
- [ ] Header estilizado: uppercase, @neutral-500, weight 600, border-bottom 2px
- [ ] Coluna Nome com stretch — expande com a janela
- [ ] Colunas com texto longo truncam com elipsis e mostram tooltip completo
- [ ] Estado vazio: mensagem centralizada quando `rowCount() == 0`, botões de processamento desabilitados
- [ ] Testes unitários atualizados: `columnCount() == 13`, `headerData()` para 13 colunas
- [ ] Testes existentes ajustados e passando sem regressão

### Plano de Validação

| Tipo             | Descrição                                                                                              |
|------------------|--------------------------------------------------------------------------------------------------------|
| Teste Manual     | Abrir aplicação com dados: verificar 13 colunas com dados corretos, badges coloridos, IDs monospace    |
| Teste Manual     | Abrir aplicação sem dados: verificar estado vazio com mensagem centralizada                            |
| Teste Manual     | Redimensionar janela: coluna Nome expande/contrai, outras mantêm largura fixa                          |
| Teste Manual     | Hover sobre célula truncada: tooltip exibe texto completo                                              |
| Teste Unitário   | `test_column_count`: `model.columnCount() == 13`                                                       |
| Teste Unitário   | `test_header_data`: nomes corretos para 13 colunas                                                     |
| Teste Unitário   | `test_data_formatting`: datas DD/MM/YYYY, IDs COMPONENTE-NNN, devs por nome                            |
| Revisão de Código| Confirmar que delegates são atribuídos via `setItemDelegateForColumn()` nos índices corretos            |

### Dependências

| Sub-Épico | Motivo                                                                                          |
|-----------|-------------------------------------------------------------------------------------------------|
| GUI-001   | StatusBadgeDelegate (DS-003), MonospaceDelegate (DS-004), QSS da tabela (DS-002), theme.py (DS-001) |
| GUI-002   | Layout vertical (MW-006): tabela deve ocupar 100% da largura após remoção do QSplitter          |

### Riscos

| Descrição                                                                   | Mitigação                                                                                                   |
|-----------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|
| Expansão 8→13 colunas pode quebrar testes existentes que verificam índices  | Mapear todos os testes que referenciam índices de coluna e atualizar sistematicamente                        |
| Coluna Dependências requer joins com dados de outras entidades (IDs → nomes)| Verificar se o ViewModel já fornece dados de dependências. Se não, ajustar `data()` para buscar via ViewModel |
| Coluna Desenvolvedor atualmente exibe `developer_id` — precisa exibir nome | Ajustar `data()` para resolver ID → nome via dados já carregados no modelo                                  |
| Delegates podem conflitar com zebra striping do QSS                         | Testar renderização do badge sobre linhas alternadas. StatusBadgeDelegate deve pintar fundo do badge sobre fundo da célula |

---

## GUI-004 — Busca, Filtros e Menu de Contexto

**Domínio:** Interação e Filtros

### Problema que Resolve

Não existe mecanismo de busca, filtro ou menu de contexto na interface. Com backlogs de 100+ histórias, localizar uma história por nome/componente/status exige scroll manual. Operações como Editar, Deletar e Gerenciar Dependências são acessíveis apenas via toolbar — não há right-click na tabela. O `DuplicateStoryUseCase` está implementado no backend mas não exposto na UI. Não há filtros por status ou feature/onda para segmentar o backlog.

### Objetivo (Valor Mensurável)

Adicionar barra de busca incremental (filtra enquanto digita, Ctrl+F) com filtros por status (chips com contagem) e por feature/onda (dropdown). Adicionar menu de contexto no right-click da tabela com 6 ações agrupadas. Expor a ação de Duplicar História na toolbar, menu de contexto e atalho Ctrl+D. Implementar via `QSortFilterProxyModel` para não afetar o modelo subjacente.

### Escopo

**Componentes incluídos:**

| ID      | Componente                 | Tipo  | Descrição do que fazer                                                                                                                |
|---------|----------------------------|-------|---------------------------------------------------------------------------------------------------------------------------------------|
| MW-003  | Barra de Busca/Filtros     | NOVO  | QLineEdit (240px, Ctrl+F) à esquerda + chips de filtro por status ao centro + dropdown feature/onda à direita, 36px de altura total    |
| MW-007  | Menu de Contexto           | NOVO  | QMenu no right-click com Editar, Duplicar, Mover Cima/Baixo, Dependências, Deletar — separadores entre categorias, Deletar em @error  |
| UX-001  | Duplicar História na UI    | NOVO  | Botão [Duplicar] na toolbar (Grupo 1), item no menu de contexto, atalho Ctrl+D, wiring ao DuplicateStoryUseCase existente              |
| UX-003  | Filtros Rápidos por Status | NOVO  | 6 chips QPushButton checkable: [Todos][Backlog][Execução][Testes][Concluído][Impedido], com contagem de histórias por status            |
| UX-004  | Filtro por Feature/Onda    | NOVO  | QComboBox dropdown com features agrupadas por onda, combinável com chips de status e busca textual                                      |

**Fora do escopo:**
- Agrupamento visual por onda na tabela → GUI-006
- Tooltip rico no hover → GUI-006
- Indicador visual de bloqueio na coluna Dependências → GUI-006

### Arquivos Impactados

| Arquivo                                                             | Ação     | Descrição                                                                                                |
|---------------------------------------------------------------------|----------|----------------------------------------------------------------------------------------------------------|
| `src/backlog_manager/presentation/views/main_window.py`             | EDITAR   | Adicionar barra de busca/filtros na zona 3, menu de contexto no right-click, botão Duplicar na toolbar   |
| `src/backlog_manager/presentation/viewmodels/filter_proxy_model.py`  | CRIAR    | QSortFilterProxyModel com filtros compostos: texto (ID/Nome/Componente), status (chips), feature/onda (dropdown) |
| `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` | EDITAR | Adicionar handler para ação Duplicar, wiring ao DuplicateStoryUseCase                                   |

### Especificações Técnicas Relevantes

**Barra de Busca/Filtros (MW-003) — 36px altura total (incluindo 8px padding vertical):**

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ [🔍 Buscar...          ] [Todos][Backlog(12)][Execução(5)][...] [Feature/Onda▼]│
└─────────────────────────────────────────────────────────────────────────────────┘
```

- **Campo de busca:** QLineEdit#searchField, 240px largura, Ctrl+F para focar, filtra enquanto digita por ID, Nome ou Componente
  - QSS: border 1px solid `@neutral-300`, border-radius `@radius-md`, padding 6px 12px 6px 32px (espaço para ícone de lupa), font-size `@font-size-base`
  - Placeholder: "Buscar por ID, nome ou componente..."
- **Chips de status:** 6 QPushButton com `setCheckable(True)`, class CSS "filterChip"
  - Ativo: bg `@primary`, cor branca, border `@primary`
  - Inativo: bg `@neutral-100`, cor `@neutral-600`, border `@neutral-200`
  - Texto com contagem: "Backlog (12)"
  - QSS: border-radius `@radius-sm`, padding 4px 12px, font-size `@font-size-sm`
- **Dropdown feature/onda:** QComboBox com opção "Todas as features" + lista de features por onda
- **Layout:** QHBoxLayout — busca à esquerda, chips centralizados, dropdown à direita
- **Filtro via QSortFilterProxyModel:** proxy sobre StoryTableModel, `filterAcceptsRow()` combina texto + status + feature

**Menu de Contexto (MW-007) — right-click na tabela:**

```
┌─────────────────────────┐
│ ✏  Editar (Enter)       │
│ 📋 Duplicar (Ctrl+D)    │
├─────────────────────────┤
│ ▲  Mover Acima (Alt+↑) │
│ ▼  Mover Abaixo (Alt+↓)│
├─────────────────────────┤
│ 🔗 Dependências...      │
├─────────────────────────┤
│ 🗑 Deletar (Delete)    │
└─────────────────────────┘
```

- Items de 32px altura
- Separadores agrupam: edição, priorização, relações, destrutiva
- "Deletar" com cor de texto `@error`; demais `@neutral-700`
- QSS: bg white, border 1px solid `@neutral-200`, border-radius `@radius-md`, sombra `@shadow-md`, padding 4px 0px
- Itens: padding 6px 32px 6px 12px, font-size `@font-size-base`

**Duplicar História (UX-001):**
- Wiring ao `DuplicateStoryUseCase` existente
- Resultado: cópia com mesmo componente, nome + sufixo " (cópia)", mesmos SP e feature
- Posições: toolbar Grupo 1 (ícone copy.svg), menu de contexto, atalho Ctrl+D
- Sem dialog intermediário — duplicação imediata com feedback "História duplicada: AUTH-001 → AUTH-004"

### Critérios de Aceite

- [ ] Campo de busca filtra a tabela incrementalmente ao digitar, por ID, Nome ou Componente
- [ ] Ctrl+F foca no campo de busca
- [ ] 6 chips de status visíveis com contagem correta de histórias por status
- [ ] Chip ativo: bg @primary + branco; inativo: bg @neutral-100 + @neutral-600
- [ ] Chips combinam com busca textual (filtro composto)
- [ ] Dropdown de feature/onda filtra tabela por entrega selecionada
- [ ] Menu de contexto aparece ao right-click na tabela com 6 ações na ordem especificada
- [ ] Menu de contexto: separadores entre categorias, "Deletar" em cor @error
- [ ] Ação "Duplicar" funcional: toolbar, menu de contexto e Ctrl+D — cria cópia com sufixo " (cópia)"
- [ ] Menu de contexto "Dependências..." abre DependencyDialog (do GUI-002) para a história selecionada
- [ ] QSortFilterProxyModel intermediário entre modelo e view (StoryTableModel não alterado)
- [ ] Testes existentes continuam passando sem regressão

### Plano de Validação

| Tipo             | Descrição                                                                                              |
|------------------|--------------------------------------------------------------------------------------------------------|
| Teste Manual     | Digitar texto no campo de busca: tabela filtra por ID, Nome, Componente em tempo real                  |
| Teste Manual     | Clicar chip "Execução": apenas histórias em execução visíveis, contagem correta no chip                |
| Teste Manual     | Combinar busca "AUTH" + chip "Backlog": apenas histórias AUTH com status Backlog                        |
| Teste Manual     | Selecionar feature no dropdown: tabela filtra por feature/onda                                         |
| Teste Manual     | Right-click em história: menu de contexto com 6 itens, separadores, Deletar em vermelho                |
| Teste Manual     | Ctrl+D: história duplicada aparece na tabela com sufixo " (cópia)"                                    |
| Teste Unitário   | Testar `FilterProxyModel.filterAcceptsRow()`: filtros combinados texto + status + feature               |
| Teste Unitário   | Testar contagem de chips: retorna números corretos por status                                          |
| Revisão de Código| Confirmar que filtros não alteram o modelo original (proxy pattern)                                     |

### Dependências

| Sub-Épico | Motivo                                                                                          |
|-----------|-------------------------------------------------------------------------------------------------|
| GUI-003   | StoryTableModel expandido (13 colunas necessárias para filtragem por ID, Componente, Feature, Onda, Status) |

### Riscos

| Descrição                                                                                | Mitigação                                                                                                      |
|------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| QSortFilterProxyModel pode introduzir latência perceptível em backlogs > 500 histórias   | Filtrar com `QTimer.singleShot(150ms)` debounce no campo de busca. Performance aceitável para uso single-user   |
| Índices de coluna no proxy podem divergir do modelo original, quebrando delegates         | Delegates são atribuídos à view (não ao proxy) — confirmar que `setItemDelegateForColumn()` funciona com proxy  |
| Duplicação pode falhar silenciosamente se UseCase retornar erro                           | Capturar exceção e exibir mensagem de erro no Status Bar ou dialog de erro padrão                               |

---

## GUI-005 — Estilização de Dialogs

**Domínio:** Dialogs

### Problema que Resolve

Todos os dialogs existentes (StoryDialog, DeveloperDialog, FeatureDialog, ConfirmDeleteDialog) usam QFormLayout nativo sem estilização: bordas quadradas, espaçamento apertado, sem ícones nos botões, sem validação visual em tempo real, sem estados vazios orientativos. O StoryDialog não permite atribuição manual de desenvolvedor. O feedback de import/export Excel é genérico. O resultado é uma experiência inconsistente entre a tela principal (refatorada nos sub-épicos anteriores) e os dialogs.

### Objetivo (Valor Mensurável)

Estilizar todos os dialogs com visual consistente via objectNames + QSS centralizado. Adicionar validação em tempo real (on-blur) com indicadores de campo obrigatório e estados de erro inline. Adicionar estados vazios orientativos em listas de dialogs. Adicionar dropdown de desenvolvedor no StoryDialog. Estilizar feedback de import/export Excel.

### Escopo

**Componentes incluídos:**

| ID      | Componente             | Tipo          | Descrição do que fazer                                                                                                             |
|---------|------------------------|---------------|------------------------------------------------------------------------------------------------------------------------------------|
| DLG-001 | StoryDialog            | REFATORAÇÃO   | Estilizar via QSS (bordas arredondadas, espaçamento 16px, padding 24px, título 16px weight 600), inputs com objectNames, botões [Salvar] @primary + [Cancelar] neutral, área de erro inline |
| DLG-002 | DeveloperDialog        | REFATORAÇÃO   | Lista com items 40px e hover @neutral-100, botões com ícones SVG ([+ Adicionar] [✏ Editar] [🗑 Remover] [✕ Fechar]), estado vazio    |
| DLG-003 | FeatureDialog          | REFATORAÇÃO   | Lista com formato "Onda N — Nome da Feature", estilização consistente, estado vazio                                                 |
| DLG-007 | ConfirmDeleteDialog    | REFATORAÇÃO   | Ícone warning-triangle.svg 32×32px cor @warning, botão [Confirmar] @error bg + branco texto + 36px, [Cancelar] @neutral-200, texto descritivo "Esta ação não pode ser desfeita." |
| DLG-008 | Progress/Result Dialogs| REFATORAÇÃO   | Progress dialog estilizado ("Importando dados...", "Exportando dados..."), dialog de resultado com contagens, estilização consistente |
| UX-002  | Atribuição Manual Dev  | NOVO          | Adicionar campo "Desenvolvedor" no StoryDialog (modo edição) com QComboBox: lista de devs cadastrados + opção "Nenhum"              |
| UX-012  | Validação em Tempo Real| NOVO          | Validação on-blur: campo obrigatório (*), erro visual inline (borda @error, mensagem em @error-light bg), contagem de caracteres restantes |
| UX-013  | Estados Vazios         | NOVO          | Em DeveloperDialog: "Nenhum desenvolvedor cadastrado. Clique em 'Adicionar' para começar." Em FeatureDialog: "Nenhuma feature cadastrada." Em DependencyDialog (GUI-002): "Nenhuma dependência definida para esta história." |

**Fora do escopo:**
- ConfigDialog, DependencyDialog, MetricsDialog (já estilizados na migração em GUI-002)
- Dialog "Sobre" → GUI-006

### Arquivos Impactados

| Arquivo                                                             | Ação     | Descrição                                                                                                |
|---------------------------------------------------------------------|----------|----------------------------------------------------------------------------------------------------------|
| `src/backlog_manager/presentation/views/story_dialog.py`             | EDITAR   | Adicionar objectNames nos widgets, campo Desenvolvedor (QComboBox), validação on-blur, indicador obrigatório (*), área de erro inline |
| `src/backlog_manager/presentation/views/developer_dialog.py`         | EDITAR   | Adicionar ícones nos botões, item height 40px, hover effect via QSS, estado vazio                        |
| `src/backlog_manager/presentation/views/feature_dialog.py`           | EDITAR   | Formato "Onda N — Nome", estilização consistente, estado vazio                                           |
| `src/backlog_manager/presentation/views/confirm_delete_dialog.py`    | EDITAR   | Ícone de alerta SVG, botão Confirmar vermelho, texto descritivo                                          |
| `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py` | EDITAR | Adicionar propriedade para lista de desenvolvedores (para dropdown), validação de campos                 |
| `src/backlog_manager/presentation/styles/stylesheet.qss`             | EDITAR   | Adicionar/ajustar seletores de objectName para botões e widgets de dialogs (se necessário)                |

### Especificações Técnicas Relevantes

**StoryDialog (DLG-001) — 480×380px (expandir para ~480×440px com campo Dev):**
- Padding interno: 24px, espaçamento entre campos: 16px
- Título: "Nova História" ou "Editar História: AUTH-001" — font-size 16px, weight 600
- Campos:
  - Componente: input texto, limite 50 chars, uppercase automático (modo edição: disabled)
  - Nome: input texto, limite 200 chars
  - Story Points: dropdown (3, 5, 8, 13)
  - Feature: dropdown carregadas + "Nenhuma"
  - **Desenvolvedor (NOVO — UX-002):** QComboBox com devs cadastrados + "Nenhum" (apenas modo edição)
- Botões: [Salvar] — `QPushButton#btnSave` bg @primary, cor branca, 36px; [Cancelar] — `QPushButton#btnCancel` bg @neutral-200, cor @neutral-700, 36px
- Inputs: border-radius `@radius-md`, border 1px solid `@neutral-300`, padding 8px 12px, focus: border @primary

**Validação em Tempo Real (UX-012):**
- Campos obrigatórios marcados com `*` vermelho no label
- Validação on-blur (focusOut): se vazio, borda muda para `@error`, mensagem de erro inline abaixo com fundo `@error-light`
- Contagem de caracteres restantes em inputs de texto (ex: "45/200")
- Botão [Salvar] desabilitado se formulário inválido

**ConfirmDeleteDialog (DLG-007) — 400×200px:**
- Layout: coluna esquerda com ícone warning-triangle.svg (32×32px, cor @warning) + coluna direita com texto
- Texto: "Excluir AUTH-001 — Nome da História? Esta ação não pode ser desfeita."
- Botão [Confirmar Exclusão] — `QPushButton#btnConfirmDelete` bg @error, cor branca, 36px
- Botão [Cancelar] — bg @neutral-200, 36px

**Estados Vazios (UX-013):**
- DeveloperDialog: "Nenhum desenvolvedor cadastrado. Clique em 'Adicionar' para começar."
- FeatureDialog: "Nenhuma feature cadastrada."
- DependencyDialog: "Nenhuma dependência definida para esta história."
- Visual: texto @neutral-400, centralizado na área de lista, font-size @font-size-base

**Progress/Result Dialogs (DLG-008):**
- Importar: "Importando dados..." com QProgressBar estilizada → resultado "Importação concluída: X histórias, Y features, Z avisos"
- Exportar: "Exportando dados..." → resultado "Exportação concluída: X histórias exportadas para [caminho]"
- Estilização consistente com demais dialogs (padding 24px, border-radius @radius-lg)

### Critérios de Aceite

- [ ] StoryDialog: bordas arredondadas, espaçamento 16px, padding 24px, título 16px weight 600
- [ ] StoryDialog modo edição: campo Desenvolvedor (QComboBox) com lista de devs + "Nenhum"
- [ ] Validação on-blur: campos obrigatórios com *, borda @error se inválido, mensagem inline
- [ ] Botão [Salvar] desabilitado se formulário inválido (pelo menos Componente e Nome obrigatórios)
- [ ] DeveloperDialog: ícones nos botões, items 40px com hover, estado vazio quando lista vazia
- [ ] FeatureDialog: formato "Onda N — Nome", estado vazio quando lista vazia
- [ ] ConfirmDeleteDialog: ícone de alerta, botão vermelho, texto descritivo com ID e nome
- [ ] Progress dialogs para import/export: estilizados com QProgressBar e dialog de resultado
- [ ] Estados vazios com mensagem orientativa em todos os dialogs com listas
- [ ] ObjectNames atribuídos a todos os widgets que requerem estilização via QSS
- [ ] Testes existentes continuam passando sem regressão

### Plano de Validação

| Tipo             | Descrição                                                                                              |
|------------------|--------------------------------------------------------------------------------------------------------|
| Teste Manual     | Abrir StoryDialog em modo edição: dropdown de Dev visível e funcional                                  |
| Teste Manual     | Deixar campo obrigatório vazio e mudar foco: borda vermelha + mensagem de erro aparece                 |
| Teste Manual     | Abrir DeveloperDialog sem devs cadastrados: mensagem de estado vazio visível                           |
| Teste Manual     | Abrir ConfirmDeleteDialog: ícone de alerta, texto com ID/nome, botão vermelho                          |
| Teste Manual     | Importar Excel: progress dialog estilizado durante importação, dialog de resultado com contagens       |
| Teste Unitário   | Testar validação de campos obrigatórios no StoryDialogViewModel                                        |
| Revisão de Código| Confirmar que objectNames estão atribuídos em todos os widgets que usam seletores QSS por #id           |

### Dependências

| Sub-Épico | Motivo                                                                                                    |
|-----------|-----------------------------------------------------------------------------------------------------------|
| GUI-001   | QSS centralizado (DS-002) com seletores para dialogs, ícones SVG (DS-005) para botões e alerta, theme.py (DS-001) para cores |

### Riscos

| Descrição                                                                                | Mitigação                                                                                                      |
|------------------------------------------------------------------------------------------|----------------------------------------------------------------------------------------------------------------|
| Validação on-blur pode conflitar com lógica de validação existente no ViewModel          | Manter validação existente no ViewModel intacta; adicionar validação visual como camada adicional na View       |
| Atribuir objectNames pode impactar seletores QSS inesperadamente                        | Testar a aplicação após cada objectName adicionado; seletores QSS por #id são mais específicos que por tipo    |
| Campo Desenvolvedor no StoryDialog pode exigir alteração na assinatura do ViewModel      | Restrição: não alterar assinatura pública existente. Adicionar novo signal/propriedade sem remover existentes   |

---

## GUI-006 — Polimento e UX Avançado

**Domínio:** Polimento e UX Avançado

### Problema que Resolve

Após os sub-épicos anteriores, a aplicação tem visual moderno e funcional, mas carece de acabamentos de UX avançado: não há agrupamento visual por onda na tabela, não há tooltip rico ao hover, não há indicador de bloqueio por dependência, a Status Bar não mostra breakdown de SP por status, não há dialog "Sobre", operações longas não oferecem cancelamento, configurações não persistem entre sessões, e o layout não se adapta a resoluções menores que 1280×720.

### Objetivo (Valor Mensurável)

Adicionar agrupamento visual por onda (separadores na tabela), tooltip rico (mini-card no hover), indicador de bloqueio na coluna Dependências, breakdown de SP na Status Bar, dialog "Sobre", cancelamento de operações longas, persistência de configuração via QSettings, e responsividade para resolução mínima 1024×600.

### Escopo

**Componentes incluídos:**

| ID      | Componente                   | Tipo          | Descrição do que fazer                                                                                                     |
|---------|------------------------------|---------------|----------------------------------------------------------------------------------------------------------------------------|
| UX-005  | Agrupamento Visual por Onda  | NOVO          | Separadores visuais na tabela entre ondas de entrega (header de grupo com fundo diferenciado informando número e nome da onda) |
| UX-006  | Tooltip Rico na Tabela       | NOVO          | Hover sobre linha exibe mini-card QFrame com: ID, Nome, Status, SP, Feature, Desenvolvedor, Dependências, Datas            |
| UX-007  | Indicador de Bloqueio        | NOVO          | Ícone na coluna Dependências: 🔴 bloqueada (deps não concluídas), 🟢 livre, — sem dependências                             |
| UX-008  | SP por Status na Status Bar  | NOVO          | Breakdown "120 SP Backlog · 80 SP Execução · 84 SP Concluído" com tooltip percentual                                       |
| UX-009  | Dialog Sobre                 | NOVO          | Menu Ajuda → Sobre: nome, versão, tecnologias (Python + PySide6), caminho BD, créditos                                    |
| UX-010  | Cancelamento de Operações    | NOVO          | Botão [Cancelar] em progress dialogs de operações >2s (cronograma, alocação, import/export)                                |
| UX-011  | Persistência de Config       | NOVO          | Salvar/restaurar velocidade, data início, máx dias ociosos via QSettings. Restaurar ao abrir a aplicação                    |
| RSP-001 | Responsividade a resize      | NOVO          | Colunas Componente, Onda, Duração ocultas se janela <1024px; toolbar overflow se botões não couberem                        |
| RSP-002 | Resolução mínima 1024×600    | NOVO          | Validar que layout vertical funciona em 1024×600 sem sobreposição ou corte, minimum sizes nos widgets                       |

**Fora do escopo:**
- Drag & Drop (baixa prioridade, versão futura)
- Seleção Múltipla + batch (baixa prioridade)
- Tema Escuro (baixa prioridade)
- Undo/Redo (baixa prioridade)

### Arquivos Impactados

| Arquivo                                                             | Ação     | Descrição                                                                                                |
|---------------------------------------------------------------------|----------|----------------------------------------------------------------------------------------------------------|
| `src/backlog_manager/presentation/views/main_window.py`             | EDITAR   | Agrupamento por onda (row painting/delegate), tooltip rico (QFrame popup), indicador bloqueio, SP breakdown na Status Bar, responsividade |
| `src/backlog_manager/presentation/viewmodels/story_table_model.py`  | EDITAR   | Suporte a agrupamento por onda (sections), dados para tooltip rico, dados de bloqueio por dependência     |
| `src/backlog_manager/presentation/views/about_dialog.py`            | CRIAR    | QDialog "Sobre" (nome, versão, tecnologias, caminho BD)                                                  |
| `src/backlog_manager/presentation/views/config_dialog.py`           | EDITAR   | Integrar QSettings para salvar/restaurar valores de configuração                                         |
| `src/backlog_manager/presentation/delegates/status_badge_delegate.py` | EDITAR | Suporte a renderização condicionada por agrupamento (se necessário)                                      |

### Especificações Técnicas Relevantes

**Agrupamento Visual por Onda (UX-005):**
- Separadores visuais entre ondas: linha de grupo com fundo diferenciado (@neutral-100), texto "Onda N — Nome da Feature" em @neutral-500, weight 600, font-size @font-size-sm
- Implementar via custom painting no QTableView ou via rows de separação no modelo
- Separadores devem ser não-selecionáveis e não-editáveis

**Tooltip Rico (UX-006):**
- QFrame popup (não QToolTip nativo — permite layout complexo)
- Conteúdo: grid 2 colunas com ID (monospace), Nome, Status (badge), SP, Feature, Desenvolvedor, Dependências, Início/Fim
- Dimensões: min 280px largura, altura automática
- Border-radius: @radius-xl (12px), sombra @shadow-md, fundo @neutral-0, border 1px solid @neutral-200
- Aparece após 300ms de hover, desaparece ao mover o mouse para outra linha

**Indicador de Bloqueio (UX-007):**
- Ícone na coluna Dependências:
  - 🔴 ou ícone vermelho: história tem dependências não concluídas (bloqueada)
  - 🟢 ou ícone verde: todas as dependências concluídas (livre para execução)
  - "—": sem dependências
- Implementar via QStyledItemDelegate ou formatação condicional no `data()` com DecorationRole

**SP por Status (UX-008):**
- Na Status Bar, expandir contadores: "120 SP Backlog · 80 SP Execução · 84 SP Concluído"
- Tooltip no label: "Backlog: 42% · Execução: 28% · Concluído: 30%"

**Dialog Sobre (UX-009):**
- Dimensões: ~400×300px
- Conteúdo: nome "Backlog Manager v2", versão, tecnologias "Python 3.11 + PySide6", caminho do banco de dados (`database.db`)
- Botão [OK]

**Cancelamento de Operações (UX-010):**
- Progress dialogs (cronograma, alocação, import/export) devem incluir botão [Cancelar] se operação > 2s
- Ao cancelar: abortar operação, restaurar estado anterior, fechar dialog

**Persistência de Configuração (UX-011):**
- Via `QSettings` (mecanismo nativo do Qt)
- Valores: velocidade (SP/dia), data de início, máx dias ociosos
- Salvar ao clicar [Aplicar] no ConfigDialog
- Restaurar ao abrir a aplicação (antes de exibir a MainWindow)

**Responsividade (RSP-001, RSP-002):**
- Se `window.width() < 1024px`: ocultar colunas Componente (4), Onda (2), Duração (12)
- Toolbar: se botões não couberem, agrupar em overflow menu (QToolBar extension)
- Resolução mínima 1024×600: `setMinimumSize(1024, 600)` na MainWindow, validar que todas as zonas ficam visíveis

### Critérios de Aceite

- [ ] Agrupamento por onda: separadores visuais entre ondas na tabela com texto "Onda N — Nome"
- [ ] Tooltip rico: hover 300ms mostra mini-card com dados completos; desaparece ao mover para outra linha
- [ ] Indicador de bloqueio: ícone vermelho/verde na coluna Dependências conforme status das deps
- [ ] Status Bar: breakdown de SP por status visível, tooltip com percentuais
- [ ] Menu Ajuda → Sobre: dialog com nome, versão, tecnologias, caminho BD
- [ ] Progress dialogs: botão [Cancelar] aparece para operações >2s, cancela efetivamente
- [ ] QSettings: configuração salva e restaurada entre sessões (velocidade, data, máx dias)
- [ ] Janela <1024px: colunas Componente, Onda, Duração ocultas automaticamente
- [ ] Resolução 1024×600: layout funcional sem sobreposição ou corte
- [ ] Testes existentes continuam passando sem regressão

### Plano de Validação

| Tipo             | Descrição                                                                                              |
|------------------|--------------------------------------------------------------------------------------------------------|
| Teste Manual     | Com múltiplas ondas: verificar separadores visuais na tabela entre ondas                               |
| Teste Manual     | Hover sobre linha: mini-card aparece após 300ms com dados corretos                                     |
| Teste Manual     | História com deps não concluídas: ícone vermelho na coluna Dependências                                |
| Teste Manual     | Status Bar: "120 SP Backlog · 80 SP Execução · 84 SP Concluído" — tooltip com percentuais              |
| Teste Manual     | Redimensionar janela para 1024×600: colunas Componente/Onda/Duração ocultas, layout funcional          |
| Teste Manual     | Alterar configuração, fechar e reabrir app: configuração restaurada                                    |
| Teste Unitário   | Testar QSettings: gravar e ler valores de configuração                                                 |
| Teste Unitário   | Testar cálculo de SP breakdown por status                                                               |
| Revisão de Código| Confirmar que QSettings não acessa domínio/infra (restrição de camada)                                  |

### Dependências

| Sub-Épico | Motivo                                                                                                    |
|-----------|-----------------------------------------------------------------------------------------------------------|
| GUI-002   | Status Bar (MW-005) necessária para SP breakdown e avisos. Layout vertical (MW-006) para responsividade   |
| GUI-003   | Tabela expandida (MW-004) para agrupamento por onda, tooltip rico, indicador de bloqueio                  |
| GUI-004   | Barra de filtros (MW-003) e proxy model para interação de filtros com agrupamento por onda                 |
| GUI-005   | Dialogs estilizados (DLG-001 a DLG-008) para cancelamento de operações e consistência visual geral        |

### Riscos

| Descrição                                                                                   | Mitigação                                                                                                              |
|---------------------------------------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------|
| Agrupamento por onda na tabela pode conflitar com QSortFilterProxyModel (filtros de GUI-004) | Implementar agrupamento na view (painting) e não no modelo, para que funcione independente do proxy                    |
| Tooltip rico (QFrame popup) pode ficar posicionado fora da tela em resoluções menores       | Calcular posição relativa à célula + ajustar para manter dentro dos bounds da janela                                   |
| Cancelamento de operações assíncronas pode deixar dados em estado inconsistente             | Usar cancellation tokens no qasync. Se cancelamento não for seguro, desabilitar o botão e exibir aviso                 |
| QSettings pode armazenar dados em local inesperado em ambientes corporativos                | Documentar local de armazenamento (Registry no Windows). Usar `QSettings.IniFormat` como alternativa se necessário      |
| Ocultar colunas ao resize pode confundir o usuário se não houver indicação visual           | Adicionar indicador sutil na tabela ("3 colunas ocultas") ou tooltip no header                                          |

---

## Apêndice — Funcionalidades de Baixa Prioridade (Fora do Escopo)

As seguintes funcionalidades estão documentadas na especificação (`docs/prompt_gui_refactor.md`) como **baixa prioridade** e **não estão incluídas** nesta decomposição. Podem ser endereçadas em um épico futuro:

| Funcionalidade                        | Justificativa da exclusão                                                                   |
|---------------------------------------|---------------------------------------------------------------------------------------------|
| Drag & Drop para Priorização          | Requer QAbstractItemModel.moveRows() + drag/drop flags — complexidade alta, botões mover são suficientes |
| Seleção Múltipla + Operações em Lote  | Requer refatoração nos UseCases para suportar batch — impacto na camada de aplicação         |
| Tema Escuro                           | O sistema de tokens (GUI-001) já suporta temas alternativos — basta criar conjunto DARK_THEME em theme.py |
| Undo/Redo                             | Requer Command Pattern na camada de apresentação — complexidade alta sem impacto visual direto |
