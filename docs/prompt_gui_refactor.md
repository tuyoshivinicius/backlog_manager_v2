Crie uma especificação de épico completa para refatorar a interface visual da aplicação desktop "Backlog Manager" — uma ferramenta PySide6/Qt de planejamento inteligente de backlog de software para Scrum Masters, Tech Leads e Project Managers.

A aplicação já está funcional (MVP concluído). A interface atual utiliza widgets PySide6 padrão sem customização visual: QToolBar com QActions texto-only, QTableView sem estilização, painéis laterais (ConfigPanel, DependencyPanel, MetricsPanel, WarningsPanel) em QSplitter, e diálogos modais com QFormLayout básico. O objetivo deste épico é refatorar a camada de apresentação para alcançar uma aparência moderna, clean e profissional, sem alterar a lógica de negócio existente.

A aplicação gerencia histórias de usuário (user stories), features organizadas por ondas de entrega, desenvolvedores, dependências entre histórias, cálculo automático de cronograma e alocação inteligente de desenvolvedores.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTEXTO TÉCNICO ATUAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tecnologias:
- Python 3.11 + PySide6 (Qt 6)
- Arquitetura MVVM (Views ↔ ViewModels ↔ UseCases)
- qasync para integração asyncio/Qt

Arquivos da camada de apresentação (src/backlog_manager/presentation/):
- views/main_window.py — MainWindow com QToolBar + QSplitter (tabela 70% / painéis 30%)
- views/story_dialog.py — QDialog para criar/editar histórias
- views/developer_dialog.py — QDialog para CRUD de desenvolvedores
- views/feature_dialog.py — QDialog para CRUD de features
- views/config_panel.py — QWidget com QFormLayout para configuração
- views/dependency_panel.py — QWidget com QGroupBox para dependências
- views/metrics_panel.py — QWidget com QFormLayout para métricas
- views/warnings_panel.py — QWidget com QListWidget para avisos
- views/confirm_delete_dialog.py — QDialog de confirmação de exclusão
- viewmodels/story_table_model.py — QAbstractTableModel com 8 colunas (ID, Nome, SP, Status, Feature, Dev, Inicio, Fim)

Estado atual dos problemas visuais:
- Toolbar usa apenas texto sem ícones, sem agrupamento visual
- Tabela de backlog com visual padrão Qt (sem badges de status, sem fonte monospace para IDs)
- Painéis laterais ocupam espaço fixo — não há layout vertical puro
- Não existe Menu Bar nem Status Bar
- Diálogos usam QFormLayout nativo sem estilização
- Não há stylesheet customizado (nenhum QSS aplicado)
- Não há design tokens ou sistema de cores centralizado

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESPECIFICAÇÕES DE DESIGN ALVO
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

- Plataforma: Desktop Windows (aplicação standalone)
- Resolução inicial: 1280×720
- Resolução mínima suportada: 1024×600
- Idioma da interface: Português (Brasil)
- Estilo: clean e moderno, com gradientes sutis, bordas arredondadas (border-radius generoso), sombras suaves e bastante espaço em branco. Transmitir profissionalismo e produtividade (referências visuais: Linear, Notion, Vercel Dashboard)
- Implementação: Qt StyleSheets (QSS) centralizados + QStyledItemDelegate para células customizadas

── PALETA DE CORES (baseada em Linear/Vercel) ──

Primária (ações, seleção, links):
  @primary:         #5B5BD6   (indigo — inspirado no accent do Linear)
  @primary-hover:   #4C4CC4
  @primary-pressed:  #3E3EB0
  @primary-light:   #EEF2FF   (fundo de seleção na tabela)

Semânticas (feedback):
  @success:         #30A46C   (verde — conclusão)
  @success-light:   #DDF3E4
  @warning:         #F5A623   (âmbar — testes/atenção)
  @warning-light:   #FFF7C2
  @error:           #E5484D   (vermelho — impedido/destrutivo)
  @error-light:     #FFE5E5

Neutras (superfícies, bordas, texto):
  @neutral-0:       #FFFFFF   (fundo de dialogs, inputs)
  @neutral-50:      #FAFAFA   (fundo do MainWindow)
  @neutral-100:     #F5F5F5   (fundo de header, menu bar, status bar)
  @neutral-150:     #EFEFEF   (zebra striping — linhas alternadas)
  @neutral-200:     #E5E5E5   (bordas, separadores, grid lines)
  @neutral-300:     #D4D4D4   (borda de inputs em repouso)
  @neutral-400:     #A3A3A3   (texto placeholder, ícones inativos)
  @neutral-500:     #737373   (texto secundário, labels)
  @neutral-600:     #525252   (texto de corpo)
  @neutral-700:     #404040   (texto de ênfase)
  @neutral-800:     #262626   (títulos, texto primário)
  @neutral-900:     #171717   (texto máximo contraste)

Badges de Status (bg / texto):
  BACKLOG:     bg #E5E5E5, text #525252, border #D4D4D4
  EXECUÇÃO:    bg #EEF2FF, text #5B5BD6, border #C7D2FE
  TESTES:      bg #FFF7C2, text #946800, border #F5D90A
  CONCLUÍDO:   bg #DDF3E4, text #18794E, border #8ECEAA
  IMPEDIDO:    bg #FFE5E5, text #CE2C31, border #F9A8AB

── TIPOGRAFIA ──

Fonte principal: "Inter", "Segoe UI", system-ui, sans-serif
  (Inter é a fonte do Linear e Vercel — instalar via bundled .ttf no pacote
   ou usar Segoe UI como fallback nativo no Windows)

Fonte monospace (IDs, código): "JetBrains Mono", "Cascadia Code", "Consolas", monospace

Escala de tamanhos:
  @font-size-xs:    11px   (badges de status, metadados mínimos)
  @font-size-sm:    12px   (labels, texto secundário, status bar)
  @font-size-base:  13px   (corpo principal, inputs, tabela)
  @font-size-md:    14px   (títulos de seção em dialogs)
  @font-size-lg:    16px   (títulos de dialogs)
  @font-size-xl:    18px   (título da janela se aplicável)

Pesos:
  @font-weight-normal:  400  (corpo)
  @font-weight-medium:  500  (labels de campo, botões)
  @font-weight-semibold: 600  (headers da tabela, títulos de dialog)
  @font-weight-bold:    700  (contadores da status bar)

Line-height: 1.5 para corpo, 1.2 para headers e badges

── ÍCONES ──

Biblioteca: Phosphor Icons (MIT license) — estilo "Regular" (outline)
  → Alternativa aceitável: Lucide Icons (também MIT)
  → Formato: SVG (QIcon com QPixmap ou via QSvgRenderer)
  → Tamanho padrão: 16×16px na toolbar, 14×14px em menus, 12×12px inline na tabela
  → Cor: @neutral-600 no estado normal, @neutral-800 no hover, @neutral-400 no disabled

Mapeamento de ícones da toolbar:
  + Nova:               plus.svg
  Editar:               pencil-simple.svg
  Deletar:              trash.svg
  Mover Cima:           arrow-up.svg
  Mover Baixo:          arrow-down.svg
  Desenvolvedores:      users.svg
  Features:             package.svg
  Configuração:         gear.svg
  Calcular Cronograma:  calendar-check.svg
  Alocar Devs:          shuffle.svg
  Importar:             download-simple.svg
  Exportar:             upload-simple.svg
  Duplicar:             copy.svg

── ESPAÇAMENTO (SPACING SCALE — múltiplos de 4px) ──

  @spacing-2:    2px    (micro — gap entre ícone e badge count)
  @spacing-4:    4px    (gap entre ícones inline, padding mínimo)
  @spacing-6:    6px    (padding vertical de badges)
  @spacing-8:    8px    (padding de células, gap entre campos)
  @spacing-12:   12px   (padding horizontal de inputs e botões)
  @spacing-16:   16px   (margem entre seções, padding de dialogs)
  @spacing-20:   20px   (margem entre grupos da toolbar)
  @spacing-24:   24px   (padding externo de dialogs)
  @spacing-32:   32px   (espaçamento entre seções de dialog)

Border-radius:
  @radius-sm:    4px    (badges, chips de filtro)
  @radius-md:    6px    (inputs, botões, cards)
  @radius-lg:    8px    (dialogs, containers maiores)
  @radius-xl:    12px   (tooltips ricos, popups de avisos)

Sombras (via QGraphicsDropShadowEffect):
  @shadow-sm:    offset(0,1) blur(3)  color(rgba(0,0,0,0.08))  — botões hover
  @shadow-md:    offset(0,4) blur(12) color(rgba(0,0,0,0.10))  — dialogs, popups
  @shadow-lg:    offset(0,8) blur(24) color(rgba(0,0,0,0.12))  — menus dropdown

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REFATORAÇÃO: TELA PRINCIPAL (MainWindow)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Alterar o layout atual (QSplitter horizontal: tabela + painéis laterais) para layout vertical com 5 zonas:

┌─────────────────────────────────────────────────┐
│ MENU BAR (28px altura)                          │
├─────────────────────────────────────────────────┤
│ TOOLBAR (44px altura, ícones 16px + texto 13px) │
├─────────────────────────────────────────────────┤
│ BARRA DE BUSCA + FILTROS (36px altura)          │
│ [🔍 Buscar...          ] [Todos][Backlog][...]  │
├─────────────────────────────────────────────────┤
│                                                 │
│            TABELA DE BACKLOG                    │
│          (ocupa 100% do espaço restante)        │
│          Linhas de 36px altura                  │
│          Header de 40px altura                  │
│                                                 │
├─────────────────────────────────────────────────┤
│ STATUS BAR (24px altura)                        │
└─────────────────────────────────────────────────┘

Dimensões de referência em 1280×720:
  Menu Bar:      28px fixo
  Toolbar:       44px fixo
  Barra Filtros: 36px fixo (incluindo 8px padding vertical)
  Status Bar:    24px fixo
  Tabela:        ~588px (espaço restante, expansível)

── MENU BAR (NOVO — não existe atualmente) ──

Adicionar QMenuBar com a seguinte estrutura:

Arquivo
  ├─ Importar Excel (Ctrl+I)
  ├─ Exportar Excel (Ctrl+E)
  └─ Sair

Cadastros (cada item abre um dialog modal)
  ├─ Histórias (Ctrl+N)
  ├─ Features
  ├─ Desenvolvedores
  └─ Configuração

Ferramentas
  ├─ Calcular Cronograma (Ctrl+Shift+C)
  └─ Alocar Desenvolvedores (Ctrl+Shift+A)

Ajuda
  └─ Sobre

── TOOLBAR (REFATORAÇÃO — atual: QActions texto-only sem agrupamento) ──

Refatorar QToolBar existente para incluir ícones e agrupamento visual com separadores:

  Grupo 1 — CRUD de Histórias:
    [+ Nova] [✏ Editar] [🗑 Deletar]

  Grupo 2 — Priorização:
    [▲ Mover Cima] [▼ Mover Baixo]

  Grupo 3 — Cadastros (atalhos rápidos):
    [👥 Desenvolvedores] [📦 Features] [⚙ Configuração]

  Grupo 4 — Processamento:
    [📅 Calcular Cronograma] [🔄 Alocar Desenvolvedores]

  Grupo 5 — Excel:
    [📥 Importar] [📤 Exportar]

Cada botão deve ser QToolButton com ToolButtonTextBesideIcon, ícone 16×16px (QIcon/SVG) + texto 13px.
Dimensões: altura 32px, padding 6px 10px, border-radius @radius-md.
Tooltip com shortcut: ex. "Nova História (Ctrl+N)".
Estados: normal (@neutral-50 bg), hover (@neutral-200 bg + @shadow-sm), pressed (@neutral-300 bg),
disabled (opacity 0.5, cursor not-allowed).
Separadores entre grupos: QToolBar::addSeparator() com 1px solid @neutral-200, margem horizontal 8px.
Transição de hover: animação não nativa — usar QSS :hover direto (instantâneo, sem animação).

── TABELA DE BACKLOG (REFATORAÇÃO — atual: 8 colunas, sem delegates customizados) ──

Expandir StoryTableModel de 8 para 13 colunas:

  | Prioridade | Feature | Onda | ID | Componente | Nome | Status | Desenvolvedor | Dependências | SP | Início | Fim | Duração |

Colunas novas a adicionar: Prioridade, Onda, Componente, Dependências, Duração
Colunas existentes a manter: ID, Nome, SP, Status, Feature, Dev, Início, Fim

Detalhes de cada coluna:
  - Prioridade: número inteiro (0 = mais prioritário), alinhado ao centro, largura fixa 60px
  - Feature: nome da feature associada ou "—" se nenhuma, alinhado à esquerda, largura 120px, truncar com elipsis
  - Onda: número inteiro da onda de entrega (0 = sem feature), alinhado ao centro, largura fixa 50px
  - ID: formato "COMPONENTE-NNN" (ex: AUTH-001, API-003), alinhado à esquerda, fonte monospace via QStyledItemDelegate, largura fixa 100px
  - Componente: texto (ex: AUTH, API, UI), alinhado à esquerda, largura 80px
  - Nome: texto descritivo da história, alinhado à esquerda, coluna com stretch (ocupa espaço restante, mínimo 200px), truncar com elipsis
  - Status: badge colorido com texto via QStyledItemDelegate (atualmente exibe texto puro), alinhado ao centro, largura fixa 100px
  - Desenvolvedor: nome do dev alocado ou "—", alinhado à esquerda, largura 100px, truncar com elipsis (atualmente exibe developer_id — alterar para nome)
  - Dependências: lista de IDs separados por vírgula ou "—", alinhado à esquerda, largura 120px, truncar com elipsis + tooltip com lista completa
  - SP: story points (apenas 3, 5, 8 ou 13), alinhado ao centro, largura fixa 40px
  - Início: data no formato DD/MM/YYYY ou "—", alinhado ao centro, largura fixa 90px
  - Fim: data no formato DD/MM/YYYY ou "—", alinhado ao centro, largura fixa 90px
  - Duração: número de dias úteis ou "—", alinhado ao centro, largura fixa 60px

Comportamento de truncação:
  - Colunas com texto longo (Nome, Feature, Dependências, Desenvolvedor): usar
    QSS text-overflow ou elideMode(Qt.ElideRight) no delegate
  - Tooltip automático com texto completo ao hover em células truncadas

Redimensionamento responsivo:
  - Coluna Nome tem QHeaderView.Stretch — expande com a janela
  - Colunas fixas mantêm largura mínima
  - Se janela < 1024px: ocultar colunas Componente, Onda, Duração; ativar scroll horizontal

Cores dos badges de status (implementar via QStyledItemDelegate):
  - BACKLOG → bg #E5E5E5, text #525252, border 1px solid #D4D4D4
  - EXECUÇÃO → bg #EEF2FF, text #5B5BD6, border 1px solid #C7D2FE
  - TESTES → bg #FFF7C2, text #946800, border 1px solid #F5D90A
  - CONCLUÍDO → bg #DDF3E4, text #18794E, border 1px solid #8ECEAA
  - IMPEDIDO → bg #FFE5E5, text #CE2C31, border 1px solid #F9A8AB

Geometria dos badges:
  - Formato pill: border-radius 10px (metade da altura)
  - Padding: 2px 8px (vertical, horizontal)
  - Altura: 20px, fonte @font-size-xs (11px), weight 500
  - Largura mínima: 70px (garante alinhamento visual entre status diferentes)
  - Indicador não-cromático (acessibilidade): prefixo de símbolo antes do texto:
    ● BACKLOG, ▶ EXECUÇÃO, ◆ TESTES, ✓ CONCLUÍDO, ✕ IMPEDIDO

Estilização da tabela via QSS:
  - Linhas alternadas (zebra striping): @neutral-0 e @neutral-150 alternados
  - Linha selecionada: fundo @primary-light (#EEF2FF), texto @neutral-800 (não inverter cores)
  - Header: fundo @neutral-100, texto @neutral-500 uppercase, font-size 12px, weight 600,
    borda inferior 2px solid @neutral-200, sem bordas verticais entre colunas
  - Grid lines: transparent (sem grid visível entre células), separador apenas via
    border-bottom 1px solid @neutral-200 em cada item
  - Altura das linhas: 36px, header 40px
  - Scroll vertical: scrollbar slim (8px width, border-radius 4px, fundo @neutral-300)
  - Focus na célula: borda 2px solid @primary (focus ring visível para acessibilidade)

── PAINÉIS LATERAIS (REFATORAÇÃO — mover para dialogs modais) ──

Os painéis atuais no QSplitter lateral devem ser convertidos:
  - ConfigPanel → Dialog modal "Configuração" (acessível via menu e toolbar)
  - DependencyPanel → Dialog modal "Dependências" (acessível via menu de contexto na história selecionada)
  - MetricsPanel → Dialog modal "Métricas da Alocação" (exibido automaticamente pós-alocação)
  - WarningsPanel → Integrado à Status Bar (área de avisos inline)

Remover o QSplitter horizontal. A tabela passa a ocupar 100% da largura.

── STATUS BAR (NOVO — não existe atualmente) ──

Adicionar QStatusBar com layout em duas áreas, separadas por QWidget spacer:

Altura fixa: 24px. Borda superior: 1px solid @neutral-200. Fundo: @neutral-100.
Fonte: @font-size-sm (12px). Cor do texto: @neutral-600.
Separador entre itens da área esquerda: "  ·  " (espaço, middle dot, espaço) em @neutral-300.

Área esquerda — Contadores (QLabel permanentes via addPermanentWidget):
  - Total de histórias: "42 histórias"
  - SP total: "284 SP"
  - Último cálculo/alocação: "Última alocação: 27/03/2026 14:30"

Área direita — Avisos (migra do WarningsPanel lateral):
  - Exibe o último aviso gerado pela alocação como texto inline color-coded
  - Ícone de indicador à esquerda do texto:
    - Vermelho: Deadlock detectado (ex: "Deadlock na onda 2: AUTH-001, AUTH-002 bloqueadas")
    - Laranja: Ociosidade dentro da onda (ex: "DEV-001 ocioso 8 dias na onda 1")
    - Cinza: Ociosidade entre ondas (informativo)
  - Se houver múltiplos avisos: exibir o mais crítico + badge com contagem total (ex: "⚠ 3 avisos")
  - Badge de contagem: fundo @error, texto branco, border-radius 10px, padding 2px 6px, font-size 11px
  - Clicar na área de avisos abre um QFrame popup (não um tooltip) fixado acima da status bar,
    listando todos os avisos com scroll vertical se > 5 itens. Fechar ao clicar fora.
    Dimensões do popup: largura 400px, altura máxima 240px.
  - Estado sem avisos: área fica oculta ou exibe "✓ Sem avisos"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REFATORAÇÃO: DIALOGS (MODAIS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

── 1. DIALOG: NOVA/EDITAR HISTÓRIA (REFATORAÇÃO — story_dialog.py) ──

Refatorar StoryDialog existente. Manter a lógica do ViewModel, estilizar os widgets:

Dimensões: 480×380px (width×height), centralizado em relação à MainWindow.
Padding interno: 24px. Espaçamento entre campos: 16px.
Título do dialog: "Nova História" ou "Editar História: AUTH-001" (font-size 16px, weight 600).
Botões de ação: altura 36px, padding 8px 20px.

Campos do formulário (existentes — adicionar QSS):
  - Componente: input texto, limite 50 chars, uppercase automático
    (no modo edição: campo somente leitura / desabilitado)
  - Nome: input texto, limite 200 chars
  - Story Points: dropdown com opções 3, 5, 8, 13
  - Feature: dropdown com opções carregadas + opção "Nenhuma"

Melhorias visuais:
  - Bordas arredondadas nos inputs (border-radius via QSS)
  - Espaçamento generoso entre campos
  - Labels com tipografia clara
  - Botões estilizados: [Salvar] com cor primária, [Cancelar] neutral
  - Área de erro inline com fundo vermelho sutil

── 2. DIALOG: GERENCIAR DESENVOLVEDORES (REFATORAÇÃO — developer_dialog.py) ──

Dimensões: 500×450px, centralizado.

Manter a lógica existente. Refatorar visual:
  - Lista estilizada com items de altura 40px e hover effect (@neutral-100 bg)
  - Botões de ação com ícones: [+ Adicionar] [✏ Editar] [🗑 Remover] [✕ Fechar]
  - Ao remover: dialog de confirmação informando que histórias serão desvinculadas

── 3. DIALOG: GERENCIAR FEATURES (REFATORAÇÃO — feature_dialog.py) ──

Dimensões: 520×480px, centralizado.

Manter a lógica existente. Refatorar visual:
  - Lista com formato: "Onda N — Nome da Feature"
  - Estilização consistente com os outros dialogs
  - Formulário inline com inputs estilizados

── 4. DIALOG: CONFIGURAÇÃO (NOVO COMO DIALOG — migra de config_panel.py) ──

Dimensões: 420×340px, centralizado.

Converter ConfigPanel (QWidget inline) para QDialog modal:

Campos (existentes):
  - Velocidade (SP/dia): input numérico decimal (0.1 a 10.0, padrão: 2.0)
  - Data de início: date picker (padrão: hoje)
  - Máx. dias ociosos: input numérico inteiro (2 a 30, padrão: 3)

Adicionar:
  - Texto explicativo sutil abaixo de cada campo
  - Botões: [Aplicar] [Cancelar]
  - Estilização consistente com demais dialogs

── 5. DIALOG: DEPENDÊNCIAS (NOVO COMO DIALOG — migra de dependency_panel.py) ──

Dimensões: 500×420px, centralizado.
Título: "Dependências: AUTH-001 — Nome da História" (font-size 16px, weight 600).

Converter DependencyPanel (QWidget inline) para QDialog modal:

Layout (lógica existente):
  - Seção "Depende de:" — lista de histórias das quais a selecionada depende
  - Dropdown para adicionar nova dependência + botão [+]
  - Botão [-] para remover dependência selecionada
  - Seção "Dependentes:" — lista de histórias que dependem da selecionada (somente leitura)

Erro de ciclo: "Dependência cíclica detectada: A → B → C → A"

── 6. DIALOG: MÉTRICAS DA ALOCAÇÃO (NOVO COMO DIALOG — migra de metrics_panel.py) ──

Dimensões: 440×380px, centralizado.
Título: "Métricas da Alocação" (font-size 16px, weight 600).
Layout: grid 2 colunas (label: valor), com labels em @neutral-500 e valores em @neutral-800 weight 600.

Converter MetricsPanel (QWidget inline) para QDialog modal exibido automaticamente pós-alocação:

Métricas exibidas (existentes):
  - Histórias Alocadas: X / Y (total)
  - Tempo de Execução: X.XXs
  - Ondas Processadas: N
  - Total de Iterações: N
  - Deadlocks Detectados: N
  - Violações de Ociosidade: N detectadas, N corrigidas

Botão [OK]

── 7. DIALOG: CONFIRMAR EXCLUSÃO (REFATORAÇÃO — confirm_delete_dialog.py) ──

Dimensões: 400×200px, centralizado.

Refatorar visual do ConfirmDeleteDialog existente:
  - Botão [Confirmar] em vermelho (@error bg, branco text, 36px altura) via QSS
  - Botão [Cancelar] neutral (@neutral-200 bg, 36px altura)
  - Layout com padding 24px e ícone de alerta (warning-triangle.svg, 32×32px, cor @warning)
  - Texto descritivo: ID, Nome, "Esta ação não pode ser desfeita."

── 8. DIALOGS: IMPORTAR/EXPORTAR EXCEL (REFATORAÇÃO — lógica existente via ExcelViewModel) ──

Melhorar feedback visual dos fluxos já existentes:

Importar:
  - Progress dialog estilizado durante processamento: "Importando dados..."
  - Dialog de resultado estilizado: "Importação concluída: X histórias, Y features, Z avisos"

Exportar:
  - Progress dialog estilizado: "Exportando dados..."
  - Dialog de resultado estilizado: "Exportação concluída: X histórias exportadas para [caminho]"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SISTEMA DE DESIGN (NOVO)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Criar módulo centralizado de design tokens e stylesheet:

Arquivo: src/backlog_manager/presentation/styles/theme.py
  Conteúdo concreto do módulo (constantes Python):

  # — Cores primárias —
  PRIMARY = "#5B5BD6"
  PRIMARY_HOVER = "#4C4CC4"
  PRIMARY_PRESSED = "#3E3EB0"
  PRIMARY_LIGHT = "#EEF2FF"

  # — Semânticas —
  SUCCESS = "#30A46C"
  SUCCESS_LIGHT = "#DDF3E4"
  WARNING = "#F5A623"
  WARNING_LIGHT = "#FFF7C2"
  ERROR = "#E5484D"
  ERROR_LIGHT = "#FFE5E5"

  # — Neutras —
  NEUTRAL_0 = "#FFFFFF"
  NEUTRAL_50 = "#FAFAFA"
  NEUTRAL_100 = "#F5F5F5"
  NEUTRAL_150 = "#EFEFEF"
  NEUTRAL_200 = "#E5E5E5"
  NEUTRAL_300 = "#D4D4D4"
  NEUTRAL_400 = "#A3A3A3"
  NEUTRAL_500 = "#737373"
  NEUTRAL_600 = "#525252"
  NEUTRAL_700 = "#404040"
  NEUTRAL_800 = "#262626"
  NEUTRAL_900 = "#171717"

  # — Badges de status —
  STATUS_COLORS = {
      "BACKLOG":   {"bg": "#E5E5E5", "text": "#525252", "border": "#D4D4D4"},
      "EXECUÇÃO":  {"bg": "#EEF2FF", "text": "#5B5BD6", "border": "#C7D2FE"},
      "TESTES":    {"bg": "#FFF7C2", "text": "#946800", "border": "#F5D90A"},
      "CONCLUÍDO": {"bg": "#DDF3E4", "text": "#18794E", "border": "#8ECEAA"},
      "IMPEDIDO":  {"bg": "#FFE5E5", "text": "#CE2C31", "border": "#F9A8AB"},
  }

  # — Tipografia —
  FONT_FAMILY = '"Inter", "Segoe UI", system-ui, sans-serif'
  FONT_MONO = '"JetBrains Mono", "Cascadia Code", "Consolas", monospace'
  FONT_SIZE_XS = "11px"
  FONT_SIZE_SM = "12px"
  FONT_SIZE_BASE = "13px"
  FONT_SIZE_MD = "14px"
  FONT_SIZE_LG = "16px"
  FONT_SIZE_XL = "18px"

  # — Espaçamento —
  SPACING_4 = "4px"
  SPACING_8 = "8px"
  SPACING_12 = "12px"
  SPACING_16 = "16px"
  SPACING_20 = "20px"
  SPACING_24 = "24px"
  SPACING_32 = "32px"

  # — Border-radius —
  RADIUS_SM = "4px"
  RADIUS_MD = "6px"
  RADIUS_LG = "8px"
  RADIUS_XL = "12px"

  # — Função de substituição —
  def apply_theme(qss_template: str) -> str:
      """Substitui todos os placeholders @var pelo valor do tema."""
      replacements = {
          "@primary-hover": PRIMARY_HOVER,
          "@primary-pressed": PRIMARY_PRESSED,
          "@primary-light": PRIMARY_LIGHT,
          "@primary": PRIMARY,
          # ... (todas as variáveis acima)
      }
      result = qss_template
      for placeholder, value in replacements.items():
          result = result.replace(placeholder, value)
      return result

Arquivo: src/backlog_manager/presentation/styles/stylesheet.qss
  - QSS centralizado aplicado na inicialização (app.setStyleSheet)
  - Estilos para: QMainWindow, QToolBar, QTableView, QDialog, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QDateEdit, QGroupBox, QListWidget,
    QStatusBar, QMenuBar, QMenu

Arquivo: src/backlog_manager/presentation/delegates/status_badge_delegate.py
  - QStyledItemDelegate para renderizar badges coloridos na coluna Status

Arquivo: src/backlog_manager/presentation/delegates/monospace_delegate.py
  - QStyledItemDelegate para renderizar IDs em fonte monospace

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIRETRIZES DE QT STYLE SHEETS (QSS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Toda a estilização visual DEVE ser feita via Qt Style Sheets (QSS). Não usar
QPalette, chamadas programáticas de setFont/setColor em widgets individuais,
nem subclasses de paintEvent para estilização — exceto onde QSS não alcança
(QStyledItemDelegate para renderização de células customizadas na tabela).

Princípios de uso do QSS:

1. ARQUIVO QSS CENTRALIZADO
   - Um único arquivo .qss (stylesheet.qss) carregado na inicialização via
     app.setStyleSheet(qss_content)
   - Valores dinâmicos (cores, espaçamentos) definidos em theme.py e injetados
     no QSS via string interpolation (template) antes de aplicar
   - Exemplo de carregamento:
       qss_template = Path("stylesheet.qss").read_text()
       qss = qss_template.replace("@primary", theme.PRIMARY_COLOR)
       app.setStyleSheet(qss)

2. SELETORES QSS A UTILIZAR
   - Seletores de tipo: QPushButton { }, QLineEdit { }, QTableView { }
   - Seletores de classe customizada via objectName:
       QPushButton#btnSave { background-color: @primary; }
       QPushButton#btnDelete { background-color: @error; }
   - Pseudo-states para interatividade:
       QPushButton:hover { background-color: @primary-hover; }
       QPushButton:pressed { background-color: @primary-pressed; }
       QPushButton:disabled { opacity: 0.5; }
       QTableView::item:selected { background-color: @accent-bg; }
       QTableView::item:alternate { background-color: @zebra-bg; }
       QMenuBar::item:selected { background-color: @menu-hover; }
   - Sub-controls para widgets compostos:
       QComboBox::drop-down { border: none; }
       QSpinBox::up-button, QSpinBox::down-button { width: 20px; }
       QScrollBar::handle:vertical { background: @neutral-300; border-radius: 4px; }

3. PROPRIEDADES QSS OBRIGATÓRIAS
   Todos os widgets interativos devem definir no mínimo:
   - background-color, color (texto)
   - border, border-radius
   - padding
   - font-family, font-size
   - Estados :hover, :pressed, :disabled, :focus

4. WIDGETS QUE NÃO ACEITAM QSS COMPLETO (usar alternativas)
   - QGraphicsDropShadowEffect para sombras (QSS não suporta box-shadow)
   - QStyledItemDelegate para renderização customizada de células (badges, monospace)
   - QProxyStyle apenas se necessário para override de painting de scrollbars/headers

5. NOMENCLATURA DE OBJECTNAMES
   Atribuir setObjectName() a todo widget que precise de estilização específica:
   - Botões: "btnNew", "btnEdit", "btnDelete", "btnSave", "btnCancel"
   - Painéis: "statusBarLeft", "statusBarRight", "warningsBadge"
   - Dialogs: "storyDialog", "developerDialog", "featureDialog", "configDialog"
   Isso permite seletores QSS granulares sem subclasses desnecessárias.

6. VARIÁVEIS DE TEMA NO QSS (via placeholder replacement)
   O arquivo QSS deve usar placeholders para todos os valores de cor, tamanho e fonte:
     @primary, @primary-hover, @primary-pressed
     @success, @warning, @error
     @neutral-50, @neutral-100, ..., @neutral-900
     @font-family, @font-size-sm, @font-size-base, @font-size-lg
     @radius-sm, @radius-md, @radius-lg
     @spacing-xs, @spacing-sm, @spacing-md, @spacing-lg
   Esses placeholders são substituídos em runtime pelos valores de theme.py.

7. EXEMPLO MÍNIMO DE ESTRUTURA DO QSS
   /* === Base === */
   QMainWindow { background-color: @neutral-50; }

   /* === Menu Bar === */
   QMenuBar { background-color: @neutral-100; font-size: @font-size-base; }
   QMenuBar::item:selected { background-color: @primary; color: white; border-radius: @radius-sm; }

   /* === Toolbar === */
   QToolBar { background-color: @neutral-50; border-bottom: 1px solid @neutral-200; spacing: 4px; padding: 4px 8px; }
   QToolButton { border-radius: @radius-md; padding: 6px 10px; font-size: @font-size-base; color: @neutral-700; }
   QToolButton:hover { background-color: @neutral-200; }
   QToolButton:pressed { background-color: @neutral-300; }
   QToolButton:disabled { opacity: 0.5; }

   /* === Table === */
   QTableView { alternate-background-color: @neutral-150; gridline-color: transparent; selection-background-color: @primary-light; selection-color: @neutral-800; }
   QTableView::item { padding: 0px 8px; height: 36px; border-bottom: 1px solid @neutral-200; }
   QTableView::item:selected { background-color: @primary-light; color: @neutral-800; }
   QHeaderView::section { background-color: @neutral-100; font-weight: 600; padding: 8px; border: none; border-bottom: 2px solid @neutral-200; font-size: @font-size-sm; color: @neutral-500; }

   /* === Inputs === */
   QLineEdit, QComboBox, QSpinBox, QDateEdit {
     border: 1px solid @neutral-300; border-radius: @radius-md;
     padding: 8px 12px; font-size: @font-size-base;
   }
   QLineEdit:focus, QComboBox:focus { border-color: @primary; }

   /* === Buttons === */
   QPushButton { border-radius: @radius-md; padding: 8px 16px; font-weight: 500; font-size: @font-size-base; height: 36px; }
   QPushButton#btnSave { background-color: @primary; color: white; }
   QPushButton#btnSave:hover { background-color: @primary-hover; }
   QPushButton#btnDelete, QPushButton#btnConfirmDelete { background-color: @error; color: white; }
   QPushButton#btnDelete:hover, QPushButton#btnConfirmDelete:hover { background-color: #D63B3F; }
   QPushButton#btnCancel { background-color: @neutral-200; color: @neutral-700; }
   QPushButton#btnCancel:hover { background-color: @neutral-300; }
   QPushButton:focus { outline: 2px solid @primary; outline-offset: 2px; }

   /* === Status Bar === */
   QStatusBar { background-color: @neutral-100; border-top: 1px solid @neutral-200; font-size: @font-size-sm; color: @neutral-600; padding: 0px 12px; min-height: 24px; }

   /* === Dialogs === */
   QDialog { background-color: white; border-radius: @radius-lg; padding: @spacing-24; }
   QDialog QLabel#dialogTitle { font-size: @font-size-lg; font-weight: 600; color: @neutral-800; }

   /* === Context Menu === */
   QMenu { background-color: white; border: 1px solid @neutral-200; border-radius: @radius-md; padding: 4px 0px; }
   QMenu::item { padding: 6px 32px 6px 12px; font-size: @font-size-base; color: @neutral-700; }
   QMenu::item:selected { background-color: @neutral-100; }
   QMenu::separator { height: 1px; background: @neutral-200; margin: 4px 8px; }
   QMenu::item:disabled { color: @neutral-400; }

   /* === Filter Chips === */
   QPushButton.filterChip { border-radius: @radius-sm; padding: 4px 12px; font-size: @font-size-sm; background-color: @neutral-100; color: @neutral-600; border: 1px solid @neutral-200; }
   QPushButton.filterChip:checked { background-color: @primary; color: white; border-color: @primary; }
   QPushButton.filterChip:hover { background-color: @neutral-200; }

   /* === Search Bar === */
   QLineEdit#searchField { border: 1px solid @neutral-300; border-radius: @radius-md; padding: 6px 12px 6px 32px; font-size: @font-size-base; min-width: 240px; }
   QLineEdit#searchField:focus { border-color: @primary; }

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTADOS DA INTERFACE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Garantir que a interface refatorada suporte visualmente os seguintes estados:

1. ESTADO VAZIO (sem histórias)
   - Tabela vazia com mensagem centralizada: "Nenhuma história cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para começar."
   - Botões de processamento desabilitados (estilo visual desabilitado via QSS)

2. ESTADO COM DADOS (backlog populado)
   - Tabela preenchida com badges de status coloridos, fontes monospace nos IDs
   - Status bar com contadores atualizados

3. ESTADO LOADING (processamento em andamento)
   - Botões de processamento desabilitados
   - Progress dialog modal estilizado

4. ESTADO ERRO
   - Dialog de erro estilizado com ícone de alerta e botão OK
   - Exemplo: "Erro ao calcular cronograma: dependência cíclica detectada entre AUTH-001 → AUTH-003 → AUTH-001"

5. ESTADO SUCESSO PÓS-ALOCAÇÃO
   - Tabela atualizada com datas e desenvolvedores preenchidos
   - Dialog de métricas modal exibido automaticamente
   - Status bar exibindo avisos (se houver)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ATALHOS DE TECLADO (MANTER — já implementados)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Todos os atalhos já estão funcionais. Apenas garantir que os tooltips da toolbar refatorada os exibam corretamente:

  Ctrl+N          → Nova história
  Enter / F2      → Editar história selecionada
  Delete          → Deletar história selecionada
  Alt+↑           → Mover prioridade acima
  Alt+↓           → Mover prioridade abaixo
  Ctrl+Shift+C    → Calcular cronograma
  Ctrl+Shift+A    → Alocar desenvolvedores
  Ctrl+I          → Importar Excel
  Ctrl+E          → Exportar Excel

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MELHORIAS NO PROMPT (LACUNAS ESTRUTURAIS)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Oportunidades identificadas que devem ser endereçadas no escopo deste épico:

1. BUSCA/FILTRO NA TABELA
   - Não há mecanismo de busca ou filtro na interface.
   - Com backlogs de 100+ histórias, localizar uma história por nome/componente/status
     é impossível sem scroll manual.
   - Adicionar campo de busca acima da tabela com filtro incremental (filtra enquanto digita)
     por ID, Nome ou Componente.
   - Atalho: Ctrl+F para focar no campo de busca.

2. MENU DE CONTEXTO (RIGHT-CLICK)
   - Não há right-click na tabela. Operações como Editar, Deletar, Duplicar e Gerenciar
     Dependências devem estar acessíveis via menu de contexto na linha selecionada.
   - Itens do menu de contexto (na ordem exata):
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
   - Estilo: QMenu com bordas arredondadas, sombra @shadow-md, items de 32px altura.
   - Separadores agrupam ações por categoria (edição, priorização, relações, destrutiva).
   - "Deletar" com cor de texto @error. Demais em @neutral-700.

3. DOUBLE-CLICK NA TABELA
   - O código atual já suporta double-click para editar, mas deve ser documentado e mantido
     na refatoração. Garantir que o comportamento persista após mudanças no layout.

4. VALIDAÇÃO EM TEMPO REAL NOS FORMULÁRIOS
   - Atualmente os erros só aparecem ao clicar Salvar. Adicionar validação on-blur e on-type:
     campo Componente mostrando erro se vazio antes de clicar Salvar, indicador visual de
     campo obrigatório (*), contagem de caracteres restantes nos inputs de texto.

5. ESTADOS VAZIOS EM TODOS OS DIALOGS
   - O prompt só menciona estado vazio da tabela principal. DeveloperDialog, FeatureDialog e
     DependencyDialog também precisam de estados vazios com mensagem orientativa:
     - "Nenhum desenvolvedor cadastrado. Clique em 'Adicionar' para começar."
     - "Nenhuma feature cadastrada."
     - "Nenhuma dependência definida para esta história."

6. MENSAGENS DE ERRO COM ORIENTAÇÃO DE RESOLUÇÃO
   - Erros devem incluir sugestão de ação corretiva, não apenas a descrição do problema.
   - Exemplos:
     - "Dependência cíclica detectada: A → B → A. Remova a dependência B → A para resolver."
     - "Não é possível remover feature: 5 histórias vinculadas. Desvincule as histórias primeiro."

7. ACESSIBILIDADE
   - Contraste mínimo WCAG 4.5:1 em todos os textos e badges.
     Validação (exemplos de contraste com a paleta definida):
       • Texto primário @neutral-800 (#262626) sobre @neutral-0 (#FFFFFF) = 16.5:1 ✓
       • Badge BACKLOG text #525252 sobre bg #E5E5E5 = 4.6:1 ✓
       • Badge EXECUÇÃO text #5B5BD6 sobre bg #EEF2FF = 4.7:1 ✓
       • Badge CONCLUÍDO text #18794E sobre bg #DDF3E4 = 4.5:1 ✓
       • Badge IMPEDIDO text #CE2C31 sobre bg #FFE5E5 = 4.8:1 ✓
   - Indicadores não-cromáticos nos badges de status (ícone ou padrão visual além da cor,
     para daltonismo): ex. ● BACKLOG, ▶ EXECUÇÃO, ◆ TESTES, ✓ CONCLUÍDO, ✕ IMPEDIDO.
   - Tamanho mínimo de áreas clicáveis: 32×32px para botões da toolbar.
   - Focus ring visível em todos os widgets interativos:
     QSS: *:focus { outline: 2px solid @primary; outline-offset: 2px; }
     Onde outline não é suportado pelo QSS, usar border: 2px solid @primary.

8. CANCELAMENTO DE OPERAÇÕES LONGAS
   - O prompt menciona progress dialog para alocação/Excel, mas não especifica botão de cancelar.
   - Progress dialogs para operações que levam >2s devem incluir botão [Cancelar].

9. RESPONSIVIDADE A RESIZE
   - Definir comportamento ao redimensionar a janela:
     - Colunas da tabela: Nome tem stretch, demais mantêm largura mínima. Se espaço insuficiente,
       colunas menos prioritárias (Duração, Componente, Onda) ficam ocultas com scroll horizontal.
     - Toolbar: manter todos os botões visíveis; se janela < MIN_WIDTH, agrupar em overflow menu.

10. PERSISTÊNCIA DE CONFIGURAÇÃO ENTRE SESSÕES
    - Atualmente os valores de ConfigPanel (velocidade, data início, max dias ociosos) são perdidos
      ao fechar a aplicação. Persistir em arquivo de configuração local (JSON ou SQLite) e restaurar
      ao abrir.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FUNCIONALIDADES NOVAS PARA MELHORAR A EXPERIÊNCIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Funcionalidades que não existem no MVP atual e devem ser incluídas no escopo deste épico:

── ALTA PRIORIDADE (impacto direto na produtividade) ──

1. DUPLICAR HISTÓRIA
   - O DuplicateStoryUseCase já está implementado no backend mas NÃO tem ação na UI.
   - Adicionar botão na toolbar (Grupo 1), atalho no menu de contexto, e shortcut Ctrl+D.
   - Ao duplicar: cria cópia com mesmo componente, nome com sufixo " (cópia)", mesmos SP e feature.

2. ATRIBUIÇÃO MANUAL DE DESENVOLVEDOR
   - O AssignDeveloperUseCase existe mas só é acessível via alocação automática.
   - Adicionar coluna "Desenvolvedor" editável na tabela (dropdown inline) ou incluir campo
     "Desenvolvedor" no StoryDialog (modo edição) com dropdown dos devs cadastrados + opção "Nenhum".

3. FILTROS RÁPIDOS POR STATUS
   - Chips/botões de filtro acima da tabela (na barra de busca/filtros, 36px de altura):
     [Todos] [Backlog] [Execução] [Testes] [Concluído] [Impedido]
   - Implementar como QPushButton com setCheckable(True), classe CSS "filterChip".
   - Chip ativo: fundo @primary, texto branco, border @primary.
   - Chip inativo: fundo @neutral-100, texto @neutral-600, border @neutral-200.
   - Chip com contagem: "Backlog (12)" — número de histórias naquele status.
   - Layout: campo de busca (240px) à esquerda, chips centralizados, dropdown feature/onda à direita.
   - Combinável com a busca por texto.
   - Filtro implementado via QSortFilterProxyModel no StoryTableModel.

4. FILTRO POR FEATURE/ONDA
   - Dropdown de filtro por feature/onda ao lado dos chips de status.
   - Permite visualizar apenas histórias de uma entrega específica.

5. AGRUPAMENTO VISUAL POR ONDA
   - Separadores visuais na tabela entre ondas de entrega (header de grupo com fundo diferenciado).
   - Torna a roadmap de entregas visível diretamente na tela principal sem sair da tabela.

── MÉDIA PRIORIDADE (melhoria de contexto e feedback) ──

6. TOOLTIP RICO NA TABELA
   - Hover sobre uma linha mostra mini-card com dados completos da história:
     ID, Nome, Status, SP, Feature, Desenvolvedor, Dependências, Datas.
   - Evita abrir dialog apenas para consultar detalhes.

7. INDICADOR VISUAL DE BLOQUEIO NA TABELA
   - Ícone na célula de Dependências indicando se a história está bloqueada
     (dependências não concluídas) vs. livre para execução.
   - Cores: 🔴 bloqueada, 🟢 livre, — sem dependências.

8. CONTAGEM DE SP POR STATUS NA STATUS BAR
   - Além de "284 SP total", mostrar breakdown por status:
     "120 SP Backlog · 80 SP Execução · 84 SP Concluído"
   - Tooltip com percentual de cada status.

9. DIALOG "SOBRE"
   - Acessível via menu Ajuda → Sobre.
   - Exibe: nome da aplicação, versão, tecnologias (Python + PySide6),
     caminho do banco de dados ativo, e créditos.

── BAIXA PRIORIDADE (polimento, considerar para versão futura) ──

10. DRAG & DROP PARA PRIORIZAÇÃO
    - Reordenar prioridades arrastando linhas na tabela, como alternativa aos botões Mover Cima/Baixo.
    - Feedback visual: linha fantasma durante arraste, indicador de posição de drop.

11. SELEÇÃO MÚLTIPLA + OPERAÇÕES EM LOTE
    - Selecionar múltiplas histórias (Ctrl+Click ou Shift+Click) para deletar em lote,
      mover para feature ou atribuir desenvolvedor em batch.

12. TEMA ESCURO
    - Alternância light/dark theme via menu ou atalho.
    - O sistema de QSS com variáveis de tema já suporta isso — basta um segundo conjunto
      de tokens em theme.py (DARK_THEME) e trocar o stylesheet em runtime.

13. UNDO/REDO
    - Ctrl+Z / Ctrl+Y para desfazer última operação (criar, deletar, mover prioridade).
    - Implementar via pilha de comandos (Command Pattern) na camada de apresentação.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESTRIÇÕES E PREMISSAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Restrições:
- NÃO alterar a camada de domínio, aplicação ou infraestrutura
- NÃO alterar a assinatura pública dos ViewModels existentes (manter contratos de signals/slots),
  EXCETO no StoryTableModel onde a expansão de 8 → 13 colunas exige alteração em columnCount(),
  headerData() e data() — estes métodos podem ser alterados. Atualizar os testes unitários
  correspondentes que verificam columnCount() == 8 para refletir as 13 colunas.
- NÃO introduzir novas dependências além de PySide6 (sem frameworks CSS externos)
  EXCETO a fonte Inter (opcional, bundle .ttf se usar; Segoe UI como fallback nativo)
  e a biblioteca de ícones Phosphor/Lucide (SVGs estáticos empacotados no projeto, não dependência pip)
- Manter compatibilidade com Python 3.11 e PySide6 existente
- Manter todos os testes unitários existentes passando (ajustar os que verificam columnCount)

Premissas:
- O QSS do PySide6 suporta as propriedades necessárias para o design alvo
- QStyledItemDelegate é suficiente para renderizar badges e fontes customizadas
- A migração de painéis laterais para dialogs modais não requer alteração nos ViewModels
- A persistência de configuração (item 10 de lacunas estruturais) será feita na camada
  de apresentação usando QSettings (nativo do Qt), sem alterar infraestrutura do backend

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ENTREGÁVEIS ESPERADOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Sistema de design centralizado (theme.py + stylesheet.qss)
2. QStyledItemDelegates para badges de status e IDs monospace
3. MainWindow refatorada: Menu Bar + Toolbar com ícones + Tabela 100% largura + Status Bar
4. Painéis laterais migrados para dialogs modais estilizados
5. StoryTableModel expandido para 13 colunas
6. Todos os dialogs existentes com visual modernizado via QSS
7. Estado vazio com placeholder visual na tabela
8. Testes existentes mantidos (sem regressão)
9. Campo de busca/filtro incremental na tabela com Ctrl+F
10. Menu de contexto (right-click) na tabela
11. Ação de Duplicar História exposta na UI (toolbar + menu + Ctrl+D)
12. Filtros rápidos por status (chips) e por feature/onda (dropdown)
13. Atribuição manual de desenvolvedor no StoryDialog
14. Estados vazios em todos os dialogs
15. Acessibilidade: contraste WCAG, indicadores não-cromáticos, focus ring
16. Tooltip rico na tabela e indicador visual de bloqueio por dependência
