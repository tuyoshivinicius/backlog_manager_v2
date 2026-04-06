# Research: Refatoracao do Roadmap Visualization

**Feature**: 040-roadmap-refactor
**Date**: 2026-04-02

## 1. Engine de Renderizacao: matplotlib embarcado em PySide6

**Decision**: Usar `matplotlib.backends.backend_qtagg.FigureCanvas` como widget Qt embarcado na dialog.

**Rationale**: FigureCanvas herda de QWidget, integra-se nativamente ao layout PySide6 sem adaptadores. O backend `QtAgg` e o recomendado pela documentacao oficial do matplotlib para PySide6.

**Alternatives considered**:
- QGraphicsView (implementacao atual): complexo, muitas classes customizadas, bug de historias omitidas, dificil de manter.
- pyqtgraph: focado em plots cientificos/real-time, nao ideal para Gantt charts.
- plotly: dependencia pesada, orientado a web, nao nativo Qt.

**Key pattern**:
```python
from matplotlib.backends.backend_qtagg import FigureCanvas
from matplotlib.figure import Figure

canvas = FigureCanvas(Figure(figsize=(10, 8), dpi=100))
ax = canvas.figure.add_subplot(111)
# canvas e um QWidget — adicionar ao layout normalmente
```

## 2. Tipo de Grafico: broken_barh para Gantt

**Decision**: Usar `ax.barh()` com datas convertidas para numeros matplotlib (`mdates.date2num`) para barras horizontais estilo Gantt.

**Rationale**: `barh()` e mais intuitivo para Gantt charts com labels no eixo Y. `broken_barh()` e melhor para multiplos segmentos por linha, mas aqui cada historia tem uma unica barra. `barh()` permite `left` + `width` posicionamento direto com datas.

**Alternatives considered**:
- `broken_barh()`: mais eficiente para multiplos segmentos por barra, mas overkill para barras simples.
- `fill_between()`: orientado a areas, nao a barras individuais.

**Performance**: 200+ barras e trivial para matplotlib. O gargalo sera draw, nao o calculo. Usar `draw_idle()` para performance.

## 3. Agrupamento Visual por Feature/Componente

**Decision**: Organizar barras no eixo Y por grupo, com separadores visuais (linhas horizontais) e labels de grupo com percentual no eixo Y.

**Rationale**: Mapear cada historia para uma posicao Y unica, agrupando por Feature/Componente. Grupos separados por espaco extra e label com percentual de conclusao.

**Pattern**:
- Y positions calculadas sequencialmente: grupo 1 (barras), espaco, grupo 2 (barras), etc.
- Labels do eixo Y: nome do grupo + percentual (ex: "Feature X - 75%")
- Barras dentro do grupo: labels individuais com nome da historia

## 4. Zoom e Navegacao

**Decision**: Implementar zoom via Ctrl+scroll do mouse customizado + botoes (+/-) na toolbar. Scroll horizontal/vertical nativo via ScrollArea ou matplotlib pan.

**Rationale**: NavigationToolbar2QT fornece zoom/pan built-in, mas Ctrl+scroll precisa de handler customizado via `mpl_connect('scroll_event')`.

**Pattern**:
```python
def on_scroll(self, event):
    if event.key == 'control':
        factor = 1.25 if event.button == 'up' else 0.8
        ax.set_xlim(...)  # Zoom horizontal centrado no mouse
        canvas.draw_idle()
```

**Alternatives considered**:
- NavigationToolbar2QT completa: inclui botoes desnecessarios (save, subplot config). Melhor criar toolbar customizada.
- QScrollArea envolvendo canvas: adiciona complexidade de layout. Melhor usar xlim/ylim do matplotlib para "scroll virtual".

## 5. Tooltips

**Decision**: Usar `QToolTip.showText()` nativo do Qt, acionado por `mpl_connect('motion_notify_event')`.

**Rationale**: QToolTip e mais rapido e integrado ao look-and-feel do sistema operacional. Annotations do matplotlib sao mais lentas e visualmente inconsistentes com o resto da UI.

**Pattern**:
```python
def on_hover(self, event):
    if event.inaxes != self.ax:
        QToolTip.hideText()
        return
    # Buscar barra sob o cursor usando coordenadas event.xdata, event.ydata
    # Mapear para indice da historia
    story = self._find_story_at(event.xdata, event.ydata)
    if story:
        pos = self.canvas.mapToGlobal(QPoint(int(event.x), int(self.canvas.height() - event.y)))
        QToolTip.showText(pos, self._build_tooltip(story))
```

## 6. Carregamento Assincrono

**Decision**: Carregar dados via `async def load_data()` usando qasync, exibir loading indicator, renderizar grafico no main thread apos dados carregados.

**Rationale**: matplotlib NAO e thread-safe. Todo rendering deve ocorrer no main thread. Com qasync, o await retorna ao main thread naturalmente — seguro para atualizar o canvas.

**Pattern**:
```python
async def _on_open_roadmap(self):
    self.loading_label.show()
    data = await self.viewmodel.load_data()  # I/O async
    self.loading_label.hide()
    if data:
        self._render_chart(data)  # Main thread — seguro
    else:
        self._show_empty_message()
```

## 7. Dependencia matplotlib

**Decision**: Adicionar `matplotlib ^3.10.0` ao pyproject.toml como dependencia de producao.

**Rationale**: Versao 3.10.x e a estavel atual com suporte completo a PySide6 via backend QtAgg. Adicionar tambem ao mypy overrides para ignore_missing_imports.

## 8. Remocao de Indicadores e QSettings

**Decision**: Remover completamente o sistema de indicadores visuais (overdue, critical deps, deadlines) e a persistencia de preferencias via QSettings do viewmodel.

**Rationale**: FR-013 e FR-014 exigem remocao. Simplifica significativamente o viewmodel (remocao de RoadmapIndicators dataclass, load_indicators, save_indicators, is_overdue, is_critical_blocker) e a dialog (remocao de checkboxes de indicadores, _apply_indicators).
