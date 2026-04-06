# Data Model: Roadmap UX Refactor

**Feature**: 043-roadmap-ux-refactor | **Date**: 2026-04-05

## Entidades Modificadas

### RoadmapFilters (dataclass — Presentation layer)

**Localizacao**: `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

| Campo | Tipo | Default | Acao | Notas |
|-------|------|---------|------|-------|
| ~~wave~~ | ~~int \| None~~ | ~~None~~ | REMOVER | Substituido por feature |
| ~~status~~ | ~~str \| None~~ | ~~None~~ | REMOVER | Nao mais necessario |
| feature | str \| None | None | ADICIONAR | Filtro por nome da feature |
| developer | str \| None | None | MANTER | Filtro por responsavel |
| component | str \| None | None | MANTER | Filtro por componente |
| search_text | str \| None | None | MANTER | Busca por nome da historia |

**Propriedade `is_active`**: Retorna True se `feature`, `developer`, `component` ou `search_text` (stripped, nao vazio) estiver definido.

**Metodo `matches(story)`**: Logica AND — todas as condicoes ativas devem ser satisfeitas:
- `feature`: `story.feature_name == self.feature`
- `developer`: `story.developer_name == self.developer`
- `component`: `story.component == self.component`
- `search_text`: `self.search_text.lower() in story.name.lower()`

---

### RoadmapGroup (dataclass — Presentation layer)

**Localizacao**: `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

| Campo | Tipo | Default | Acao | Notas |
|-------|------|---------|------|-------|
| name | str | (required) | MANTER | Agora contem o feature name |
| ~~wave~~ | ~~int~~ | ~~0~~ | REMOVER | Nao mais relevante |
| ~~feature_names~~ | ~~list[str]~~ | ~~[]~~ | REMOVER | Grupo JA E a feature |
| feature_id | int \| None | None | ADICIONAR | ID da feature (None = "Sem feature") |
| stories | list[StoryOutputDTO] | [] | MANTER | Historias do grupo |
| expanded | bool | False | MANTER | Estado expand/collapse |

**Properties mantidas (sem alteracao):**
- `completion_percent: float` — % de historias com status "CONCLUIDO"
- `has_scheduled_stories: bool` — True se alguma historia tem start_date e end_date
- `min_date: date | None` — Menor start_date do grupo
- `max_date: date | None` — Maior end_date do grupo
- `status_counts: dict[str, int]` — Contagem por status

---

### RoadmapData (dataclass — Presentation layer)

**Localizacao**: `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

Sem alteracoes estruturais. Os grupos agora sao ordenados por min_date em vez de wave number.

---

### RoadmapViewModel (classe — Presentation layer)

**Localizacao**: `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

| Atributo | Tipo | Acao | Notas |
|----------|------|------|-------|
| _cached_stories | list[StoryOutputDTO] | MANTER | |
| _cached_features | dict[int, str] | MANTER | Pode ser util para lookups futuros |
| ~~_cached_feature_waves~~ | ~~dict[int, int]~~ | REMOVER | Nao mais necessario |
| _group_states | dict[str, bool] | MANTER | Keys agora sao feature names |
| _current_filters | RoadmapFilters | MANTER | Tipo refatorado |
| _show_all_dependencies | bool | MANTER | |

---

## Entidades NAO Modificadas

### StoryOutputDTO (Application layer)

Sem alteracoes. Campos relevantes para o roadmap:
- `id: str` — Codigo da historia (ex: "AUTH-001")
- `feature_id: int | None` — ID da feature pai
- `feature_name: str | None` — Nome da feature pai
- `component: str` — Componente
- `developer_name: str | None` — Responsavel
- `status: str` — Status atual
- `start_date: date | None` — Data inicio
- `end_date: date | None` — Data fim
- `dependency_ids: list[str]` — Dependencias

### FeatureOutputDTO (Application layer)

Sem alteracoes. Ainda carregado em `load_data` para popular `_cached_features`.

---

## Fluxo de Dados

```
StoryOutputDTO (Application)
    → RoadmapViewModel._build_roadmap_data()
        → Agrupa por story.feature_name
        → Cria RoadmapGroup (name=feature_name, feature_id=story.feature_id)
        → Ordena por min_date (FR-019)
    → RoadmapData (groups, min/max dates, counts)
        → RoadmapDialog._render_chart()
            → Toolbar: feature/componente/responsavel/busca
            → Barras: story.id como codigo, progress bar
            → Cabecalho: "Feature Name — N historias | X%"
            → Dependencias: setas entre historias visiveis
```

## Regras de Validacao

- `RoadmapFilters.matches()`: Logica AND — todos os filtros ativos devem corresponder
- `RoadmapGroup` ordenacao: `(feature_id is None, min_date or date.max)` — "Sem feature" por ultimo
- Story code: Sempre visivel (dentro ou fora da barra)
- Metricas: Recalculadas com dados filtrados quando filtros ativos (FR-018)
- Dependencias: Setas somente quando ambas historias visiveis (FR-021)

## Transicoes de Estado

### Expand/Collapse

```
Todos colapsados (FR-020)
    → click cabecalho grupo → toggle_group(feature_name) → grupo expandido
    → click novamente → grupo colapsado
```

### Filtros

```
Nenhum filtro ativo
    → usuario seleciona feature → apply_filters(feature="X")
    → usuario adiciona componente → apply_filters(feature="X", component="Y")
    → usuario clica "Limpar" → clear_filters() → nenhum filtro
```

### Zoom

```
100% (fit all) — FR-020
    → zoom in → range X reduz (ZOOM_FACTOR_IN=1.25)
    → zoom out → range X aumenta (ZOOM_FACTOR_OUT=0.8)
    → reset → 100% (fit all) + reset pan position
    Limite: minimo ZOOM_MAX_DAYS=7 dias visiveis
```

### Pan/Drag (FR-022 a FR-028)

```
Idle (cursor: OpenHandCursor)
    → button_press (botao esquerdo, sem Ctrl, sobre axes)
        → Panning (cursor: ClosedHandCursor)
            → motion_notify → atualiza xlim (delta horizontal)
            → button_release
                → se deslocamento < PAN_CLICK_THRESHOLD (5px) → click (toggle grupo)
                → senao → finaliza pan → Idle
    → key_press (Left/Right, zoom > 100%)
        → desloca xlim 10% da viewport → Idle
    → fit_view/fit_content/reset
        → xlim resetado (pan position implicito) → Idle
```

## Entidades Adicionais (Pan State — View layer)

### Pan State (atributos internos do RoadmapDialog)

**Localizacao**: `src/backlog_manager/presentation/views/roadmap_dialog.py`

| Atributo | Tipo | Default | Descricao |
|----------|------|---------|-----------|
| _is_panning | bool | False | Indica se arrasto esta ativo |
| _pan_start_x | float \| None | None | Posicao xdata no inicio do drag |
| _pan_start_xlim | tuple[float, float] \| None | None | Limites xlim no inicio do drag |

**Nota**: Estes atributos sao estado visual local do View — nao fazem parte do ViewModel pois nao afetam dados de negocio.

### Constantes Adicionais

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| PAN_CLICK_THRESHOLD | 5.0 | Pixels minimos para distinguir click de drag |
| PAN_VISIBLE_RATIO | 0.2 | Fracao minima do range visivel ao clampar pan |
| KEYBOARD_PAN_RATIO | 0.10 | Fracao da viewport por tecla de seta |
