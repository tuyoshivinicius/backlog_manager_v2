# Data Model: Correção de Problemas de Interface do Roadmap

**Date**: 2026-04-04 | **Branch**: `042-roadmap-ux-fix`

## Nota sobre escopo

Esta feature é 100% camada Presentation. Não há criação de novas entidades de domínio, DTOs, ou alterações de schema SQLite. Os modelos abaixo descrevem **estruturas de dados internas** da camada de apresentação (dataclasses no ViewModel e constantes na View).

---

## Entidades existentes (sem alterações)

### StoryOutputDTO (Application layer — somente leitura)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | str | Identificador único da história |
| component | str | Componente funcional |
| name | str | Nome da história |
| story_points | int | Pontos de esforço |
| priority | int | Prioridade numérica |
| status | str | BACKLOG \| EXECUCAO \| TESTES \| CONCLUIDO \| IMPEDIDO |
| duration | int \| None | Duração em dias úteis |
| start_date | date \| None | Data de início calculada |
| end_date | date \| None | Data de fim calculada |
| developer_id | int \| None | ID do desenvolvedor atribuído |
| feature_id | int \| None | ID da feature associada |
| developer_name | str \| None | Nome do desenvolvedor (enriquecido) |
| feature_name | str \| None | Nome da feature (enriquecido) |
| wave | int | Número da wave (0 = sem wave) |
| dependency_ids | list[str] | IDs das dependências |

### FeatureOutputDTO (Application layer — somente leitura)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | int | Identificador da feature |
| name | str | Nome da feature |
| wave | int | Número da wave atribuída |

---

## Estruturas de dados do ViewModel (modificações)

### RoadmapGroup (dataclass — modificado)

| Campo | Tipo | Descrição | Novo? |
|-------|------|-----------|-------|
| name | str | Nome do grupo (ex: "Wave 1") | Existente |
| wave | int | Número da wave | Existente |
| stories | list[StoryOutputDTO] | Histórias do grupo | Existente |
| expanded | bool | Estado de expansão | Existente |
| **feature_names** | **list[str]** | **Nomes das features neste grupo** | **NOVO** |

**Propriedades existentes (sem alterações)**: `completion_percent`, `has_scheduled_stories`, `min_date`, `max_date`, `status_counts`

**Label renderizado**:
- Com feature: `"Wave N — FeatureName - X% [Y histórias]"`
- Múltiplas features: `"Wave N — Feature1, Feature2 - X% [Y histórias]"`
- Sem feature: `"Wave N - X% [Y histórias]"` (fallback)

### RoadmapData (dataclass — sem alterações estruturais)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| groups | list[RoadmapGroup] | Grupos de waves |
| min_date | date | Data de início global |
| max_date | date | Data de fim global |
| total_stories | int | Total de histórias |
| scheduled_stories | int | Histórias com datas |

### RoadmapFilters (dataclass — sem alterações)

| Campo | Tipo | Descrição |
|-------|------|-----------|
| wave | int \| None | Filtro por wave |
| status | str \| None | Filtro por status |
| developer | str \| None | Filtro por desenvolvedor |
| component | str \| None | Filtro por componente |
| search_text | str \| None | Busca por nome |

### RoadmapViewModel (QObject — modificações)

**Novos campos de instância**:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| _show_all_dependencies | bool | Toggle para exibir todas as setas de dependência |

**Novos métodos**:

| Método | Retorno | Descrição |
|--------|---------|-----------|
| toggle_show_all_dependencies() | bool | Alterna exibição global de dependências |
| get_density_region() | tuple[date, date] | Retorna janela temporal de maior densidade |

**Modificações em métodos existentes**:

| Método | Alteração |
|--------|-----------|
| _build_roadmap_data() | Popula `feature_names` no RoadmapGroup a partir de `story.feature_name`; cria grupos para waves vazias via `_cached_feature_waves` |

---

## Constantes da View (modificações)

### Constantes existentes (valores atualizados)

| Constante | Valor atual | Novo valor | Motivo |
|-----------|-------------|------------|--------|
| — | — | — | Nenhuma constante existente precisa de alteração de valor |

### Novas constantes

| Constante | Tipo | Valor | Descrição |
|-----------|------|-------|-----------|
| TODAY_LINE_COLOR | str | "#ED8936" | Cor da linha "hoje" (laranja) |
| TODAY_LINE_WIDTH | float | 2.0 | Espessura mínima da linha "hoje" |
| TODAY_LINE_ALPHA | float | 0.8 | Opacidade da linha "hoje" |
| TODAY_LINE_ZORDER | int | 10 | Camada superior para linha "hoje" |
| DEPENDENCY_COLOR | str | "#4A5568" | Cor neutra para setas de dependência |
| DEPENDENCY_HIDDEN_COLOR | str | "#A0AEC0" | Cor para dependências ocultas/filtradas |
| ZOOM_MAX_DAYS | int | 7 | Zoom máximo: 7 dias na viewport |
| LEGEND_PATCH_SIZE | int | 12 | Tamanho mínimo dos quadrados da legenda (px) |
| MAX_LABEL_CHARS | int | 60 | Truncamento de rótulos longos |

---

## Transições de estado

### Estado de expansão de wave (existente — sem alteração)

```
[COLLAPSED] ←→ [EXPANDED]
    Click no cabeçalho alterna estado
    ViewModel._group_states[name] = True/False
```

### Estado de zoom (existente — refinado)

```
[ZOOM_MIN] ← zoom out ← [CURRENT] → zoom in → [ZOOM_MAX]
    ZOOM_MIN: todo o período visível (names legíveis)
    ZOOM_MAX: ≤ 7 dias na viewport
    Novo: indicador % atualizado na toolbar
```

### Estado de dependências (NOVO)

```
[HOVER_ONLY] ←→ [SHOW_ALL]
    Toggle via botão "Mostrar todas as dependências"
    ViewModel._show_all_dependencies = True/False
    HOVER_ONLY: setas aparecem apenas on-hover (comportamento atual)
    SHOW_ALL: todas as setas renderizadas permanentemente
```

---

## Validações

Nenhuma validação nova é necessária na camada de apresentação. Os dados chegam validados dos use cases (camada Application). As únicas verificações são:

1. `story.start_date and story.end_date` — filtro de histórias agendadas (já existente)
2. `STATUS_PALETTE.get(story.status)` — fallback para DEFAULT_COLOR (já existente)
3. `story.feature_name` — fallback para None quando não disponível (já existente)
