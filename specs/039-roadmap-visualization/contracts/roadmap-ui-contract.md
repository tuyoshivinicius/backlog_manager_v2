# UI Contract: Roadmap Dialog

**Feature Branch**: `039-roadmap-visualization`
**Date**: 2026-04-02

## RoadmapDialog (QDialog)

### Entry Point

A MainWindow expoe um botao/acao de menu "Roadmap" que:
1. Instancia `RoadmapViewModel` via DIContainer
2. Chama `viewmodel.load_data()` (async)
3. Se nao ha historias com datas → exibe `QMessageBox.information()` com orientacao
4. Se ha dados → instancia `RoadmapDialog(roadmap_data, indicators, parent)` e chama `dialog.showMaximized()`

### Constructor Contract

```python
class RoadmapDialog(QDialog):
    def __init__(
        self,
        data: RoadmapData,
        indicators: RoadmapIndicators,
        parent: QWidget | None = None,
    ) -> None: ...
```

### Signals Emitidos

| Signal | Payload | Quando |
|--------|---------|--------|
| `group_mode_changed` | `RoadmapGroupMode` | Usuario alterna agrupamento |
| `indicators_changed` | `RoadmapIndicators` | Usuario altera toggle de indicador |

### Slots Esperados

| Slot | Parametro | Efeito |
|------|-----------|--------|
| `update_data` | `RoadmapData` | Re-renderiza scene com novos dados/agrupamento |
| `update_indicators` | `RoadmapIndicators` | Aplica/remove indicadores visuais |

### Layout

```
┌─────────────────────────────────────────────────────────┐
│  Toolbar: [Agrupar: Feature ▾ | Componente ▾]          │
│           [☐ Atraso] [☐ Criticidade] [☐ Deadlines]     │
├────────┬────────────────────────────────────────────────┤
│ Group  │  Timeline (QGraphicsView)                      │
│ Labels │  ┌─ Feature A (75%) ────────────────────┐      │
│ Panel  │  │ ██████░░░░  Story-001                │      │
│ (fixed)│  │ ████████████  Story-002              │      │
│        │  ├─ Feature B (50%) ────────────────────┤      │
│        │  │ ████░░░░░░  Story-003                │      │
│        │  └──────────────────────────────────────┘      │
│        │  ← scroll horizontal →                         │
├────────┴────────────────────────────────────────────────┤
│  Status: 15 historias | 2026-01-15 a 2026-06-30        │
└─────────────────────────────────────────────────────────┘
```

### Interacoes

| Acao do Usuario | Comportamento |
|----------------|---------------|
| Hover sobre barra | Tooltip HTML com detalhes da historia |
| Ctrl + scroll wheel | Zoom horizontal (escala X, Y fixo) |
| Scroll horizontal | Navega na timeline |
| Scroll vertical | Navega entre grupos |
| Alternar agrupamento | Emite `group_mode_changed`, ViewModel reagrupa, dialog re-renderiza |
| Toggle indicador | Emite `indicators_changed`, aplica/remove destaques visuais |
| Escape / fechar | `dialog.reject()` retorna a MainWindow |

### Tooltip HTML Format

```html
<table style="font-family: Inter, sans-serif;">
  <tr><td><b>{story.name}</b></td></tr>
  <tr><td>Desenvolvedor:</td><td>{story.developer_name or "Nao alocado"}</td></tr>
  <tr><td>Story Points:</td><td>{story.story_points}</td></tr>
  <tr><td>Status:</td><td>{story.status}</td></tr>
  <tr><td>Dependencias:</td><td>{deps or "Sem dependencias"}</td></tr>
  <tr><td>Inicio:</td><td>{story.start_date}</td></tr>
  <tr><td>Fim:</td><td>{story.end_date}</td></tr>
  <tr><td>Duracao:</td><td>{story.duration} dias</td></tr>
  <tr><td>Componente:</td><td>{story.component}</td></tr>
</table>
```

---

## RoadmapViewModel

### Constructor Contract

```python
class RoadmapViewModel:
    def __init__(
        self,
        list_stories_use_case: ListStoriesUseCase,
        list_features_use_case: ListFeaturesUseCase,
    ) -> None: ...
```

### Public API

| Metodo | Retorno | Descricao |
|--------|---------|-----------|
| `async load_data()` | `RoadmapData \| None` | Carrega historias e features. Retorna None se nenhuma historia tem datas. |
| `regroup(mode: RoadmapGroupMode)` | `RoadmapData` | Reagrupa historias no modo especificado (usa dados ja carregados). |
| `load_indicators()` | `RoadmapIndicators` | Carrega preferencias de QSettings. |
| `save_indicators(indicators: RoadmapIndicators)` | `None` | Persiste preferencias em QSettings. |
| `is_overdue(story: StoryOutputDTO, today: date)` | `bool` | Verifica se historia esta em atraso. |
| `is_critical_blocker(story: StoryOutputDTO, all_stories: list[StoryOutputDTO])` | `bool` | Verifica se historia e bloqueadora critica. |
