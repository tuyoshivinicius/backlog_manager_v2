# UI Contract: Roadmap Dialog

**Date**: 2026-04-04 | **Branch**: `042-roadmap-ux-fix`

## Visão geral

O Roadmap Dialog é um QDialog que exibe visualização Gantt de histórias agrupadas por wave usando matplotlib embarcado em PySide6. Este contrato define a interface visual e comportamental do componente.

---

## Toolbar (barra superior)

### Filtros (existentes — sem alteração de contrato)

| Componente | Tipo | Placeholder | Comportamento |
|------------|------|-------------|---------------|
| Wave | QComboBox | "Todas" | Filtra por número da wave |
| Status | QComboBox | "Todos" | Filtra por status da história |
| Responsável | QComboBox | "Todos" | Filtra por desenvolvedor |
| Componente | QComboBox | "Todos" | Filtra por componente funcional |
| Busca | QLineEdit | "Buscar história..." | Filtro substring case-insensitive |
| Limpar filtros | QPushButton | — | Reset de todos os filtros |

**Indicador visual**: Filtros ativos recebem `border: 2px solid #0066CC`

### Controles de zoom (MODIFICADO)

| Componente | Tipo | Texto/Ícone | Tooltip | Comportamento |
|------------|------|-------------|---------|---------------|
| Zoom In | QPushButton | "+" com ícone lupa+ | "Ampliar (Ctrl+Scroll Up)" | Zoom in com fator 1.25 |
| Zoom Out | QPushButton | "-" com ícone lupa- | "Reduzir (Ctrl+Scroll Down)" | Zoom out com fator 0.8 |
| **Zoom Level** | **QLabel** | **"100%"** | — | **Indicador % do zoom atual** |
| **Ajustar à tela** | **QPushButton** | **"Ajustar à tela"** | **"Mostrar todo o período do roadmap"** | **Zoom para período completo** |
| **Ajustar ao conteúdo** | **QPushButton** | **"Ajustar ao conteúdo"** | **"Focar na região de maior densidade"** | **Zoom na região densa** |

### Controles de dependência (NOVO)

| Componente | Tipo | Texto | Tooltip | Comportamento |
|------------|------|-------|---------|---------------|
| **Mostrar dependências** | **QPushButton (toggle)** | **"Dependências"** | **"Mostrar/ocultar todas as dependências"** | **Toggle renderização permanente de setas** |

### Contador de resultados (NOVO)

| Componente | Tipo | Formato | Visibilidade |
|------------|------|---------|--------------|
| **Contador** | **QLabel** | **"X de Y histórias"** | **Sempre visível; atualiza com filtros** |

---

## Área de gráfico (matplotlib canvas)

### Barras de história (existente — sem alteração)

| Propriedade | Valor |
|-------------|-------|
| Altura | `BAR_HEIGHT = 0.6` |
| Background | STATUS_PALETTE[status].background, alpha=0.4 |
| Progress overlay | STATUS_PALETTE[status].background, largura = width × STATUS_PROGRESS[status] |
| IMPEDIDO | Borda tracejada `#991B1B`, linewidth=2.5 |
| Largura mínima | 1 dia |

### Barras de grupo colapsado (existente — sem alteração)

| Propriedade | Valor |
|-------------|-------|
| Altura | `SUMMARY_BAR_HEIGHT = 1.0` |
| Cor base | `#D4D4D4`, alpha=0.5 |
| Overlay de conclusão | `#A3A3A3`, largura proporcional ao % concluído |

### Rótulos de wave (MODIFICADO)

| Estado | Formato antigo | Formato novo |
|--------|---------------|--------------|
| Colapsado | `"Wave N - X% [Y histórias]"` | `"Wave N — FeatureName - X% [Y histórias]"` |
| Expandido | `"▼ Wave N - X%"` | `"▼ Wave N — FeatureName - X% [Y histórias]"` |
| Sem feature | `"Wave N"` | `"Wave N - X% [Y histórias]"` (fallback) |
| Wave vazia | (não renderizado) | `"Wave N (vazia)"` |
| Múltiplas features | — | `"Wave N — Feat1, Feat2 - X% [Y histórias]"` (truncar em 60 chars) |

### Rótulos de história (MODIFICADO)

| Propriedade | Valor antigo | Valor novo |
|-------------|-------------|------------|
| Texto | `"  {name}"` sem truncamento | `"  {name}"` truncado em 60 chars com "..." |

### Eixo temporal (MODIFICADO)

| Propriedade | Valor antigo | Valor novo |
|-------------|-------------|------------|
| Locator | `WeekdayLocator(interval=1)` | `AutoDateLocator(minticks=5)` |
| Formatter | `DateFormatter("%d/%m/%Y")` | `ConciseDateFormatter(locator)` |
| Rotação | 45° fixo | 45° máximo (quando necessário) |

### Linha "hoje" (MODIFICADO)

| Propriedade | Valor antigo | Valor novo |
|-------------|-------------|------------|
| Cor | `#991B1B` (vermelho) | `#ED8936` (laranja) |
| Espessura | `lw=1` | `lw=2` |
| Alpha | 0.5 | 0.8 |
| Estilo | `--` (tracejado) | Sólido |
| Label | Nenhum | "Hoje" no topo |
| zorder | Padrão | 10 (acima das barras) |

### Setas de dependência (MODIFICADO)

| Propriedade | Valor antigo | Valor novo |
|-------------|-------------|------------|
| Cor (visível) | `#991B1B` (vermelho) | `#4A5568` (cinza escuro) |
| Cor (oculta) | `#991B1B` | `#A0AEC0` (cinza claro) |
| Curvatura | `rad=0.1` fixo | `rad=0.1 + 0.05*i` (variável) |
| Modo | Apenas on-hover | On-hover + toggle global |

### Legenda (MODIFICADO)

| Propriedade | Valor antigo | Valor novo |
|-------------|-------------|------------|
| Ícone | Patch + símbolo no label | Patch quadrado (mín 12×12px) sem símbolo |
| Label | `"● BACKLOG"` | `"BACKLOG"` |
| Posição | upper right | upper right |
| Font size | 7 | 8 (design system `font-size-xs`) |

---

## Status bar (rodapé) — MODIFICADO

| Componente | Formato antigo | Formato novo |
|------------|---------------|--------------|
| Contagens | `"BACKLOG: N \| EXECUCAO: N \| ..."` | Contagens + mini-barra de progresso colorida |
| Total | `"Total: N histórias"` | `"X de Y histórias"` quando filtro ativo |
| Indicação de filtro | Nenhuma | `"(filtro ativo)"` quando filtros ativos |
| Período | `"min_date a max_date"` | Mantido |

---

## Janela (MODIFICADO)

| Propriedade | Valor antigo | Valor novo |
|-------------|-------------|------------|
| WindowFlags | QDialog padrão | `Qt.WindowType.Window` (botões min/max/close) |
| Abertura | `showMaximized()` | `showMaximized()` (mantido) |
| Redimensionamento | `setSizeGripEnabled(True)` | Mantido (implícito com WindowType.Window) |

---

## Interações

### Teclado (NOVO)

| Tecla | Contexto | Ação |
|-------|----------|------|
| Tab | Toolbar | Navega entre widgets |
| Enter | Botão com foco | Ativa o botão |
| Ctrl+Scroll | Canvas | Zoom in/out |
| Escape | Dialog | Fecha o dialog |

### Mouse (existente — sem alteração exceto dependências)

| Ação | Alvo | Comportamento |
|------|------|---------------|
| Click | Cabeçalho de wave | Toggle expand/collapse |
| Hover | Barra de história | Tooltip + setas de dependência (modo hover) |
| Ctrl+Scroll | Canvas | Zoom horizontal |
