# Data Model: Roadmap UX Overhaul

**Feature**: 041-roadmap-ux-overhaul
**Date**: 2026-04-03

## Entidades Existentes (Inalteradas)

### StoryOutputDTO (application/dto/story/story_output_dto.py)

```python
class StoryOutputDTO(BaseModel):
    id: str                          # Ex: "AUTH-001"
    component: str                   # Modulo/componente
    name: str                        # Nome da historia
    story_points: int                # Fibonacci: 3, 5, 8, 13
    priority: int                    # >= 0
    status: str                      # BACKLOG | EXECUCAO | TESTES | CONCLUIDO | IMPEDIDO
    duration: int | None             # Dias calculados
    start_date: date | None          # Data inicio calculada
    end_date: date | None            # Data fim calculada
    developer_id: int | None
    feature_id: int | None
    developer_name: str | None = None
    feature_name: str | None = None
    wave: int = 0                    # Wave da feature associada
    dependency_ids: list[str] = []   # IDs das dependencias diretas
```

### FeatureOutputDTO (application/dto/feature/feature_output_dto.py)

```python
class FeatureOutputDTO(BaseModel):
    id: int
    name: str
    wave: int
```

### StatusConfig (presentation/theme/theme.py)

```python
@dataclass(frozen=True)
class StatusConfig:
    symbol: str       # Simbolo nao-cromatico para acessibilidade
    background: str   # Cor de fundo hex
    foreground: str   # Cor de texto hex (WCAG AA)
```

## Entidades Modificadas (ViewModel)

### RoadmapGroupMode (REMOVIDO)

O enum `RoadmapGroupMode` e removido. O agrupamento e fixo por wave conforme spec.

### RoadmapGroup (MODIFICADO)

```python
@dataclass
class RoadmapGroup:
    """Grupo de historias no roadmap, correspondente a uma wave."""

    name: str                                           # Nome da wave/feature
    wave: int                                           # Numero da wave (0 = sem wave)
    stories: list[StoryOutputDTO] = field(default_factory=list)
    expanded: bool = False                              # NOVO: estado de expansao (colapsado por padrao)

    @property
    def completion_percent(self) -> float:
        """Percentual de historias CONCLUIDO no grupo."""
        if not self.stories:
            return 0.0
        done = sum(1 for s in self.stories if s.status == "CONCLUIDO")
        return (done / len(self.stories)) * 100.0

    @property
    def has_scheduled_stories(self) -> bool:
        """Verifica se ha historias com datas atribuidas."""
        return any(s.start_date and s.end_date for s in self.stories)

    @property
    def min_date(self) -> date | None:                  # NOVO
        """Data de inicio mais antiga do grupo."""
        dates = [s.start_date for s in self.stories if s.start_date]
        return min(dates) if dates else None

    @property
    def max_date(self) -> date | None:                  # NOVO
        """Data de fim mais recente do grupo."""
        dates = [s.end_date for s in self.stories if s.end_date]
        return max(dates) if dates else None

    @property
    def status_counts(self) -> dict[str, int]:          # NOVO
        """Contagem de historias por status."""
        counts: dict[str, int] = {}
        for s in self.stories:
            counts[s.status] = counts.get(s.status, 0) + 1
        return counts
```

### RoadmapData (MODIFICADO)

```python
@dataclass
class RoadmapData:
    """Dados completos do roadmap para renderizacao."""

    groups: list[RoadmapGroup]
    min_date: date
    max_date: date
    total_stories: int
    scheduled_stories: int

    @property
    def status_counts(self) -> dict[str, int]:          # NOVO
        """Contagem agregada de historias por status (respeitando filtros)."""
        counts: dict[str, int] = {}
        for group in self.groups:
            for status, count in group.status_counts.items():
                counts[status] = counts.get(status, 0) + count
        return counts
```

## Entidades Novas (ViewModel)

### RoadmapFilters

```python
@dataclass
class RoadmapFilters:
    """Filtros aplicaveis ao roadmap."""

    wave: int | None = None                 # Filtrar por wave especifica
    status: str | None = None               # Filtrar por status
    developer: str | None = None            # Filtrar por responsavel (nome)
    component: str | None = None            # Filtrar por componente
    search_text: str | None = None          # Busca por nome de historia

    @property
    def is_active(self) -> bool:
        """Verifica se algum filtro esta ativo."""
        return any([
            self.wave is not None,
            self.status is not None,
            self.developer is not None,
            self.component is not None,
            self.search_text is not None and self.search_text.strip() != "",
        ])

    def matches(self, story: StoryOutputDTO) -> bool:
        """Verifica se uma historia atende a todos os filtros ativos (logica AND)."""
        if self.wave is not None and story.wave != self.wave:
            return False
        if self.status is not None and story.status != self.status:
            return False
        if self.developer is not None:
            if story.developer_name != self.developer:
                return False
        if self.component is not None and story.component != self.component:
            return False
        if self.search_text and self.search_text.strip():
            if self.search_text.strip().lower() not in story.name.lower():
                return False
        return True
```

## Mapeamentos e Constantes

### STATUS_PROGRESS (NOVO - roadmap_dialog.py)

```python
STATUS_PROGRESS: dict[str, float] = {
    "BACKLOG": 0.0,
    "EXECUCAO": 0.33,
    "TESTES": 0.66,
    "CONCLUIDO": 1.0,
    "IMPEDIDO": 0.0,   # Sem progresso — status bloqueado
}
```

### Constantes de Layout (MODIFICADAS - roadmap_dialog.py)

```python
BAR_HEIGHT: float = 0.6                # Barra individual
SUMMARY_BAR_HEIGHT: float = 1.0        # NOVO: barra-resumo de grupo colapsado
GROUP_SPACING: float = 1.5             # Espacamento entre grupos
LABEL_FONT_SIZE: int = 8               # Fonte de rotulos (minimo 14px = ~10pt)
GROUP_FONT_SIZE: int = 9               # Fonte de cabecalhos de grupo
MIN_BAR_WIDTH_DAYS: int = 1            # Largura minima
MIN_LABEL_HEIGHT_PX: int = 14          # NOVO: altura minima de rotulos (FR-008)
```

## Fluxo de Dados

```
User Action → View (signal) → ViewModel (process) → RoadmapData → View (render)

1. Dialog open:
   View.load_and_render()
   → ViewModel.load_data()
   → ListStoriesUseCase + ListFeaturesUseCase
   → Cache stories + features
   → Group by wave (all collapsed)
   → Return RoadmapData
   → View._render_chart(data)

2. Toggle group:
   View._on_group_toggle(group_name)
   → ViewModel.toggle_group(group_name)
   → Flip expanded flag in cached group
   → Return updated RoadmapData
   → View._render_chart(data)

3. Apply filter:
   View._on_filter_changed()
   → ViewModel.apply_filters(RoadmapFilters)
   → Filter cached stories
   → Regroup filtered stories by wave
   → Return filtered RoadmapData
   → View._render_chart(data)

4. Search:
   View._on_search(text)
   → ViewModel.apply_filters(RoadmapFilters(search_text=text))
   → Same as filter flow

5. Hover story:
   View._on_hover(event)
   → Find story at coordinates
   → Show enriched tooltip
   → Draw dependency arrows (temporary overlay)

6. Hover exit:
   View._on_hover(event) — no story found
   → Remove dependency arrows
   → Hide tooltip
```

## Transicoes de Estado

### Grupo (Wave)

```
COLLAPSED (padrao) ←→ EXPANDED (click)
```

- Estado inicial: todos COLLAPSED
- Transicao: click no grupo alterna estado
- Preservacao: durante a sessao (em memoria no ViewModel)
- Auto-colapso: se rotulos nao cabem no espaco (FR-008)

### Filtros

```
INACTIVE (padrao) → ACTIVE (filtro aplicado) → INACTIVE (filtro removido)
```

- Estado inicial: todos INACTIVE
- Multiplos filtros: combinacao AND
- Limpeza: botao "limpar filtros" reseta todos
- Indicacao visual: badge na toolbar quando ativo
```
