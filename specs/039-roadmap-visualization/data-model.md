# Data Model: Visualizacao de Roadmap

**Feature Branch**: `039-roadmap-visualization`
**Date**: 2026-04-02

## Entidades Existentes (sem alteracao)

### Story (Domain Entity)

Campos relevantes para o roadmap (ja existentes):

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | str | ID unico (formato COMPONENT-NNN) |
| component | str | Componente tecnico |
| name | str | Nome da historia |
| story_points | StoryPoint | Pontos de historia (Fibonacci) |
| priority | int | Prioridade |
| status | StoryStatus | Status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) |
| duration | int \| None | Duracao em dias (calculada) |
| start_date | date \| None | Data inicio (calculada) |
| end_date | date \| None | Data fim (calculada) |
| developer_id | int \| None | FK para Developer |
| feature_id | int \| None | FK para Feature |

### Feature (Domain Entity)

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | int | ID auto-increment |
| name | str | Nome da feature |
| wave | int | Numero da onda (> 0) |

### StoryOutputDTO (Application DTO — existente)

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | str | ID da historia |
| component | str | Componente |
| name | str | Nome |
| story_points | int | Story points |
| priority | int | Prioridade |
| status | str | Status como string |
| duration | int \| None | Duracao dias |
| start_date | date \| None | Data inicio |
| end_date | date \| None | Data fim |
| developer_id | int \| None | FK developer |
| feature_id | int \| None | FK feature |
| developer_name | str \| None | Nome do desenvolvedor (enriquecido) |
| feature_name | str \| None | Nome da feature (enriquecido) |
| wave | int | Onda da feature |
| dependency_ids | list[str] | IDs das dependencias |

### FeatureOutputDTO (Application DTO — existente)

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | int | ID da feature |
| name | str | Nome |
| wave | int | Onda |

## Novos Modelos (Presentation Layer)

### RoadmapGroupMode (Enum — presentation/viewmodels/)

Modo de agrupamento das historias na timeline.

```python
from enum import Enum

class RoadmapGroupMode(str, Enum):
    """Modo de agrupamento das historias no roadmap."""
    FEATURE = "feature"
    COMPONENT = "component"
```

### RoadmapIndicators (DataClass — presentation/viewmodels/)

Preferencias de indicadores visuais, persistidas via QSettings.

```python
from dataclasses import dataclass

@dataclass
class RoadmapIndicators:
    """Preferencias de indicadores visuais do roadmap."""
    show_overdue: bool = True
    show_critical_deps: bool = False
    show_deadlines: bool = False
```

**Persistencia QSettings**:
- Grupo: `RoadmapIndicators`
- Chaves: `show_overdue`, `show_critical_deps`, `show_deadlines`
- Tipo: bool (obrigatorio `type=bool` no read)

### RoadmapGroup (DataClass — presentation/viewmodels/)

Representacao de um grupo na timeline (feature ou componente).

```python
from dataclasses import dataclass, field

@dataclass
class RoadmapGroup:
    """Um grupo de historias no roadmap (feature ou componente)."""
    name: str
    stories: list[StoryOutputDTO] = field(default_factory=list)

    @property
    def completion_percent(self) -> float:
        """Percentual de historias com status CONCLUIDO."""
        if not self.stories:
            return 0.0
        done = sum(1 for s in self.stories if s.status == "CONCLUIDO")
        return (done / len(self.stories)) * 100.0

    @property
    def has_scheduled_stories(self) -> bool:
        """Indica se o grupo tem historias com datas calculadas."""
        return any(s.start_date and s.end_date for s in self.stories)
```

### RoadmapData (DataClass — presentation/viewmodels/)

Dados completos para renderizar o roadmap.

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class RoadmapData:
    """Dados consolidados para renderizacao do roadmap."""
    groups: list[RoadmapGroup]
    min_date: date
    max_date: date
    total_stories: int
    scheduled_stories: int
```

## Fluxo de Dados

```
┌──────────────────────┐
│  MainWindow          │  Aciona "Visualizar Roadmap"
│  (botao/menu)        │
└──────────┬───────────┘
           │
           ▼
┌──────────────────────┐
│  RoadmapViewModel    │  1. Valida: existem historias com datas?
│  (presentation)      │  2. Carrega stories via ListStoriesUseCase
│                      │  3. Carrega features via ListFeaturesUseCase
│                      │  4. Agrupa historias (por feature ou componente)
│                      │  5. Calcula min/max dates, progresso
│                      │  6. Carrega/salva preferencias (QSettings)
└──────────┬───────────┘
           │ RoadmapData
           ▼
┌──────────────────────┐
│  RoadmapDialog       │  1. Cria QGraphicsScene
│  (QDialog maximizado)│  2. Renderiza barras (QGraphicsRectItem)
│                      │  3. Posiciona no eixo temporal
│                      │  4. Configura tooltips HTML
│                      │  5. Aplica indicadores visuais
│                      │  6. Zoom/scroll interativo
└──────────────────────┘
```

## Mapeamento de Cores (Status → Barra)

Reutiliza STATUS_PALETTE do design system existente:

| Status | Cor Background | Cor Foreground (borda) | Mnemonic |
|--------|---------------|----------------------|----------|
| BACKLOG | #E5E5E5 | #525252 | cinza |
| EXECUCAO | #DBEAFE | #1E40AF | azul |
| TESTES | #FEF3C7 | #B45309 | amarelo |
| CONCLUIDO | #DDF3E4 | #18794E | verde |
| IMPEDIDO | #FECACA | #991B1B | vermelho |

**Nota**: Spec define "azul=em andamento" — EXECUCAO e TESTES sao ambos "em andamento". TESTES mantem cor propria (amarelo) para diferenciar visualmente.

## Indicadores Visuais (quando ativados)

| Indicador | Condicao | Representacao Visual |
|-----------|----------|---------------------|
| Atraso | `end_date < today AND status != CONCLUIDO` | Borda vermelha tracejada + icone ⚠ |
| Criticidade deps | Historia e bloqueadora (tem dependentes) AND (`status == IMPEDIDO` OR em atraso) | Borda laranja espessa |
| Deadlines | Sempre (quando toggle ativo) | Linhas verticais tracejadas nas end_dates |

## State Transitions

Nenhuma transicao de estado ocorre nesta feature (somente leitura). O roadmap reflete o estado atual das historias conforme retornado pelos use cases.
