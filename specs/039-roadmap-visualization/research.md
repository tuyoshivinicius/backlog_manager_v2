# Research: Visualizacao de Roadmap

**Feature Branch**: `039-roadmap-visualization`
**Date**: 2026-04-02

## R1: Abordagem de Renderizacao (QGraphicsView + QGraphicsScene)

**Decision**: Utilizar QGraphicsView + QGraphicsScene com subclasses de QGraphicsRectItem para as barras de historia.

**Rationale**:
- QGraphicsView e a solucao nativa do Qt para graficos 2D interativos — sem dependencias externas.
- QGraphicsRectItem ja fornece `rect()`, `boundingRect()`, `paint()` com brush/pen, evitando reimplementar geometria.
- Override de `paint()` apenas para adicionar texto (nome da historia) dentro das barras.
- Coordenadas da scene: X = eixo temporal (dias desde data de referencia * pixels_per_day), Y = agrupamento vertical (grupos empilhados com banda fixa de altura).

**Alternatives Considered**:
- QGraphicsItem puro: boilerplate excessivo para barras retangulares.
- QGraphicsWidget: overhead de layout desnecessario.
- Bibliotecas externas (matplotlib, pyqtgraph): dependencia adicional, menos controle de interacao, nao alinha com principio IX (simplicidade).

## R2: Performance para 200+ Historias

**Decision**: Combinar BSP tree indexing + device coordinate cache + smart viewport update.

**Rationale**:
- `scene.setItemIndexMethod(QGraphicsScene.BspTreeIndex)` — padrao, eficiente para buscas espaciais ate milhares de itens.
- `setCacheMode(QGraphicsItem.DeviceCoordinateCache)` em cada barra — cacheia resultado de paint() como pixmap, ganho significativo para itens estaticos.
- `setViewportUpdateMode(QGraphicsView.SmartViewportUpdate)` — repinta apenas regioes alteradas.
- `setOptimizationFlag(QGraphicsView.DontAdjustForAntialiasing)` se anti-aliasing habilitado.

**Alternatives Considered**:
- OpenGL viewport: overengineering para 200 itens.
- Culling manual: desnecessario com BSP tree para esta escala.

## R3: Zoom Horizontal (Ctrl+Scroll)

**Decision**: Override `wheelEvent` no QGraphicsView, escalar apenas eixo X via `setTransform()`. Anchor sob o mouse.

**Rationale**:
- Escalar apenas X mantem espacamento vertical estavel (grupos nao esticam).
- `setTransformationAnchor(QGraphicsView.AnchorUnderMouse)` centraliza zoom na posicao do cursor — intuitivo para navegacao temporal.
- Fator de zoom: 1.25x (zoom in) / 0.8x (zoom out) por step.
- Limitar escala X entre min/max para evitar zoom excessivo.

**Alternatives Considered**:
- Redesenhar scene com pixel_per_day diferente a cada zoom: mais lento, perda de estado de scroll.
- Zoom em ambos os eixos: distorce layout vertical.

## R4: Labels de Grupo Fixos (Eixo Vertical)

**Decision**: Painel lateral esquerdo (QWidget) separado do QGraphicsView, sincronizado via scrollbar vertical.

**Rationale**:
- Labels de grupo (feature/componente) devem permanecer visiveis durante scroll horizontal.
- Painel separado sincronizado via `verticalScrollBar().valueChanged` signal e mais simples que um segundo QGraphicsView.
- Layout: QHBoxLayout com [LabelPanel | QGraphicsView].

**Alternatives Considered**:
- Segundo QGraphicsView compartilhando scene: renderizacao duplicada, complexidade desnecessaria.
- Labels overlay dentro da scene: movem com scroll horizontal, inutil.

## R5: Tooltips Ricos

**Decision**: Utilizar `item.setToolTip(html_string)` diretamente nos QGraphicsRectItem.

**Rationale**:
- Qt suporta HTML subset em tooltips nativamente (bold, line breaks, tables, cores).
- Zero codigo de evento customizado — framework scene/view despacha tooltip events automaticamente.
- Formato: tabela HTML com desenvolvedor, SP, status, dependencias, datas, duracao, componente.

**Alternatives Considered**:
- `QToolTip.showText()` em hoverMoveEvent: requer event handling manual, tracking de posicao, hide logic explicito. So justificado para tooltips dinamicos/interativos.

## R6: Persistencia de Preferencias (QSettings)

**Decision**: QSettings com grupo `RoadmapIndicators` e booleans nomeados `show_<indicador>`.

**Rationale**:
- Consistente com uso existente de QSettings no projeto (column widths, velocity preferences).
- `type=bool` obrigatorio no read — sem ele, QSettings retorna strings do INI ("true"/"false"), nao Python bools.
- Defaults explicitos em cada leitura.

**Pattern**:
```python
settings.beginGroup("RoadmapIndicators")
settings.setValue("show_overdue", True)
settings.setValue("show_critical_deps", False)
settings.setValue("show_deadlines", False)
settings.endGroup()
```

**Alternatives Considered**:
- Int 0/1: menos legivel no INI, propenso a erros.
- JSON blob: overengineering para toggles simples.

## R7: QDialog Maximizado

**Decision**: QDialog com QVBoxLayout, `showMaximized()`, e Escape nativo para fechar.

**Rationale**:
- QDialog ja fornece comportamento modal, Escape handling (via `reject()`), e semantica de return code.
- `showMaximized()` (nao `showFullScreen()`) mantem taskbar/title bar visiveis — menos desorientador.
- `setSizeGripEnabled(True)` para flexibilidade de redimensionamento.

**Alternatives Considered**:
- QMainWindow separada: sem modal blocking, lifecycle mais complexo.
- `showFullScreen()`: esconde chrome do OS, confuso para sub-dialog.

## R8: Coloracao por Status

**Decision**: Reutilizar STATUS_PALETTE existente do design system para cores de barras.

**Rationale**:
- O projeto ja define cores por status em `presentation/theme/theme.py`:
  - BACKLOG: cinza (#E5E5E5 bg)
  - EXECUCAO: azul (#DBEAFE bg)
  - TESTES: amarelo (#FEF3C7 bg — mapeado como "em andamento")
  - CONCLUIDO: verde (#DDF3E4 bg)
  - IMPEDIDO: vermelho (#FECACA bg)
- Spec define: verde=concluido, azul=em andamento, vermelho=impedido, cinza=pendente.
- Mapeamento: BACKLOG→cinza, EXECUCAO→azul, TESTES→azul (variante), CONCLUIDO→verde, IMPEDIDO→vermelho.
- Usar cores de foreground do STATUS_PALETTE para bordas das barras (contraste).

**Alternatives Considered**:
- Cores customizadas: inconsistencia com design system, viola principio IX.
