# UI Contract: Roadmap UX Refactor

**Feature**: 043-roadmap-ux-refactor | **Date**: 2026-04-05

## Toolbar Layout

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ [+][-][100%][Ajustar tela][Ajustar conteudo] │ [Feature▾][Comp▾][Dev▾]    │
│                                               │ [🔍 Buscar...][Limpar]     │
│ Zoom Group                                    │ Filter Group               │
├───────────────────────────────────────────────┼────────────────────────────┤
│ [🔗 Dependencias][X de Y historias]           │                   [Fechar] │
│ Dependency Group                              │ Actions Group              │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Separadores**: QFrame vertical (VLine), 1px, entre cada grupo.

## Filtros

| Controle | Widget | Placeholder | Dados | Signal |
|----------|--------|-------------|-------|--------|
| Feature | QComboBox | "Todas" | get_available_filters()["features"] | currentIndexChanged |
| Componente | QComboBox | "Todos" | get_available_filters()["components"] | currentIndexChanged |
| Responsavel | QComboBox | "Todos" | get_available_filters()["developers"] | currentIndexChanged |
| Nome | QLineEdit | "Buscar historia..." | free text | textChanged (debounce 300ms) |
| Limpar | QPushButton | — | — | clicked |

**Filtro ativo**: `border: 2px solid #0066CC;` (FILTER_ACTIVE_STYLE)

## Roadmap Canvas

### Cabecalho de Grupo (colapsado)

```
▶ Feature Name — 12 historias | 75%    [====████████████======]
```

- Icone: ▶ (colapsado) / ▼ (expandido)
- Formato: `"{name} — {count} historias | {pct}%"`
- Cor do percentual: verde (#18794E) >75%, amarelo (#B45309) 25-75%, vermelho (#991B1B) <25%
- Barra de resumo: background #D4D4D4, progress #A3A3A3

### Cabecalho de Grupo (expandido)

```
▼ Feature Name — 12 historias | 75%
    AUTH-001 | Login com OAuth
    AUTH-002 | Refresh Token
    AUTH-003 | Logout
```

### Barra de Historia

```
┌──────────────────────────────────┐
│        AUTH-001                   │  ← codigo centralizado, monospace, fontsize 7
│  [████████░░░░░░░░░░░░░░░░░░░░]  │  ← progress bar overlay
└──────────────────────────────────┘
```

- Codigo: `story.id` (ex: "AUTH-001")
- Se barra curta: codigo a direita da barra com offset

### Label Y-axis

```
  AUTH-001 | Login com OAuth...
  AUTH-002 | Refresh Token
```

- Formato: `"  {story.id} | {story_name}"`
- Truncamento: MAX_LABEL_CHARS=60, codigo sempre visivel

## Interacoes

| Acao | Trigger | Resultado |
|------|---------|-----------|
| Expand/Collapse | Click no cabecalho do grupo | toggle_group(feature_name) |
| Zoom In | Click "+", Ctrl+Scroll Up | xlim reduz (ZOOM_FACTOR_IN=1.25) |
| Zoom Out | Click "-", Ctrl+Scroll Down | xlim aumenta (ZOOM_FACTOR_OUT=0.8) |
| Reset Zoom | Click "Ajustar tela" | xlim = full range + 2 dias margem |
| Fit Content | Click "Ajustar conteudo" | xlim = regiao mais densa |
| Toggle Deps | Click "Dependencias" | show/hide setas de dependencia |
| Hover Historia | Mouse sobre barra | Tooltip HTML + setas de dependencia |
| Filtrar | Selecionar combo ou digitar | apply_filters() + re-render |
| Limpar Filtros | Click "Limpar filtros" | clear_filters() + re-render |
| Fechar | Click "Fechar" ou Escape | dialog.close() |

## Pan/Drag Horizontal (FR-022 a FR-028)

### Cursor Visual

| Estado | Cursor | Condicao |
|--------|--------|----------|
| Idle (sobre canvas) | OpenHandCursor | Mouse sobre area do grafico |
| Arrastando | ClosedHandCursor | Botao esquerdo pressionado + movendo |
| Fora do axes | ArrowCursor | Mouse fora da area do grafico |

### Interacoes de Pan

| Acao | Trigger | Resultado |
|------|---------|-----------|
| Iniciar pan | Click esquerdo sobre grafico (sem Ctrl) | Registra posicao inicial, cursor fechado |
| Pan ativo | Arrastar horizontalmente | xlim desloca proporcionalmente ao delta |
| Finalizar pan | Soltar botao | Cursor volta para mao aberta |
| Click (nao drag) | Press+release com deslocamento < 5px | Tratado como click normal (toggle grupo) |
| Nav. teclado | Seta esquerda/direita | Desloca 10% da viewport visivel |
| Reset pan | Botao "Ajustar tela" ou "Ajustar conteudo" | xlim resetado (pan implicito) |

### Limites

- Pan limitado para que pelo menos 20% do range de dados permaneca visivel
- Pan sem efeito quando zoom = 100% (todo timeline ja visivel)
- Pan nao interfere com: zoom (Ctrl+Scroll), tooltips (hover sem drag), toggle de dependencias

### Conflitos Resolvidos

- **Click vs Drag**: Threshold de 5 pixels — deslocamento menor e click, maior e pan
- **Tooltip vs Drag**: Tooltips suprimidos durante `_is_panning = True`
- **Zoom vs Pan**: Ctrl+Scroll continua sendo zoom; scroll sem Ctrl continua sendo scroll vertical

## Estado Inicial (FR-020)

- Todos os grupos colapsados
- Zoom 100% (fit all)
- Pan na posicao inicial (sem deslocamento)
- Nenhum filtro ativo
- Dependencias desativadas
- Cursor: OpenHandCursor sobre area do grafico
