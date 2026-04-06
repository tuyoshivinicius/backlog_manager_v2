# Data Model: Refatoracao do Roadmap Visualization

**Feature**: 040-roadmap-refactor
**Date**: 2026-04-02

## Entidades Existentes (sem alteracao)

### StoryOutputDTO (application/dto)
Usado como input — nenhuma modificacao necessaria.

Campos relevantes para o roadmap:
- `id: str` — Identificador unico
- `name: str` — Nome da historia
- `status: str` — Status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)
- `story_points: int` — Pontos da historia
- `start_date: date | None` — Data de inicio calculada
- `end_date: date | None` — Data de fim calculada
- `feature_id: str | None` — ID da feature associada
- `feature_name: str | None` — Nome da feature
- `component: str | None` — Componente tecnico
- `developer_name: str | None` — Nome do desenvolvedor alocado
- `dependency_ids: list[str]` — IDs de dependencias

### FeatureOutputDTO (application/dto)
Usado para mapear feature_id -> feature_name. Nenhuma modificacao necessaria.

## Entidades do ViewModel (refatoradas)

### RoadmapGroupMode (Enum — mantido)
```python
class RoadmapGroupMode(str, Enum):
    FEATURE = "feature"
    COMPONENT = "component"
```

### RoadmapGroup (dataclass — simplificado)
```python
@dataclass
class RoadmapGroup:
    name: str
    stories: list[StoryOutputDTO]

    @property
    def completion_percent(self) -> float:
        """Percentual de historias com status CONCLUIDO."""
        if not self.stories:
            return 0.0
        completed = sum(1 for s in self.stories if s.status == "CONCLUIDO")
        return (completed / len(self.stories)) * 100

    @property
    def has_scheduled_stories(self) -> bool:
        """Verifica se o grupo possui historias com datas calculadas."""
        return any(s.start_date and s.end_date for s in self.stories)
```

### RoadmapData (dataclass — simplificado)
```python
@dataclass
class RoadmapData:
    groups: list[RoadmapGroup]
    min_date: date
    max_date: date
    total_stories: int
    scheduled_stories: int
```

### Removidos (FR-013, FR-014)
- ~~RoadmapIndicators~~ — removido (nao ha mais indicadores visuais)
- ~~load_indicators()~~ — removido (nao ha mais persistencia QSettings)
- ~~save_indicators()~~ — removido
- ~~is_overdue()~~ — removido
- ~~is_critical_blocker()~~ — removido

## Constantes da View (refatoradas)

### Constantes de Layout (novas)
```python
BAR_HEIGHT: float = 0.6          # Altura da barra no eixo Y (unidades matplotlib)
GROUP_SPACING: float = 1.5        # Espaco extra entre grupos
LABEL_FONT_SIZE: int = 8          # Tamanho da fonte dos labels
GROUP_FONT_SIZE: int = 9          # Tamanho da fonte dos nomes de grupo
MIN_BAR_WIDTH_DAYS: int = 1       # Largura minima da barra (1 dia) para historias com start == end
```

### Constantes Removidas
- ~~PIXELS_PER_DAY~~ — nao aplicavel (matplotlib usa coordenadas de dados)
- ~~BAR_SPACING~~ — substituido por BAR_HEIGHT
- ~~GROUP_HEADER_HEIGHT~~ — substituido por GROUP_SPACING
- ~~GROUP_PADDING~~ — nao necessario
- ~~LABEL_PANEL_WIDTH~~ — nao necessario (labels no eixo Y)
- ~~TIME_HEADER_HEIGHT~~ — nao necessario (eixo X nativo)

## Fluxo de Dados

```
ListStoriesUseCase.execute() -> list[StoryOutputDTO]
ListFeaturesUseCase.execute() -> ListFeaturesOutputDTO
                    |
                    v
        RoadmapViewModel.load_data()
          - Filtra historias com start_date e end_date
          - Agrupa por Feature (padrao) ou Componente
          - Calcula min_date, max_date
          - Retorna RoadmapData | None
                    |
                    v
        RoadmapDialog._render_chart(data: RoadmapData)
          - Limpa axes
          - Para cada grupo: desenha barras com ax.barh()
          - Configura eixo X com datas (mdates)
          - Configura eixo Y com labels de grupo
          - canvas.draw_idle()
```

## State Transitions

O roadmap nao tem estados persistentes. Os estados transitorios da dialog sao:

```
LOADING -> DATA_LOADED -> RENDERED
LOADING -> NO_DATA -> EMPTY_MESSAGE
LOADING -> ERROR -> ERROR_MESSAGE
```

Nao ha transicoes de estado nas entidades — feature read-only.
