# Data Model: EP-018 — Layout Principal e Migração de Painéis

**Date**: 2026-03-28
**Status**: Complete

---

## Overview

Esta feature é primariamente de **Presentation Layer** e não introduz novas entidades de domínio. Os "entities" aqui documentados são componentes de UI (Views e ViewModels) que seguem o padrão MVVM da constituição.

---

## 1. Views (Presentation Layer)

### 1.1 MainWindow (Refatoração)

**Arquivo**: `src/backlog_manager/presentation/views/main_window.py`

**Mudanças**:
- Remoção de QSplitter horizontal
- Adição de QMenuBar com 4 menus
- Refatoração de QToolBar com ícones
- Adição de QStatusBar com contadores e warnings badge
- Remoção de painéis laterais (ConfigPanel, DependencyPanel, MetricsPanel, WarningsPanel)
- Adição de filter bar placeholder (36px)
- Implementação de context menu na tabela

**Layout Structure**:
```
QMainWindow
├── QMenuBar (28px) - 4 menus
├── QToolBar (44px) - 5 grupos com ícones
└── CentralWidget (QWidget)
    └── QVBoxLayout
        ├── FilterBar (36px) - placeholder
        └── StoryTableView (stretch)
└── QStatusBar (24px) - contadores + warnings badge
```

**Validações**:
- Layout funcional em 1366x768 mínimo
- Atalhos de teclado não conflitam

---

### 1.2 ConfigDialog (Novo)

**Arquivo**: `src/backlog_manager/presentation/views/config_dialog.py`

**Campos**:
| Campo | Tipo | Validação | Default |
|-------|------|-----------|---------|
| velocity | QDoubleSpinBox | 0.1-10.0 | 2.0 |
| start_date | QDateEdit | não nulo | hoje |
| max_idle_days | QSpinBox | 2-30 | 3 |

**Dimensões**: 420x340px (fixo, per FR-015)

**Botões**: Aplicar, Cancelar

**Transições de Estado**:
```
[Aberto] --Aplicar(válido)--> [Fechado, valores salvos]
[Aberto] --Aplicar(inválido)--> [Aberto, erro exibido]
[Aberto] --Cancelar--> [Fechado, valores descartados]
```

---

### 1.3 DependencyDialog (Novo)

**Arquivo**: `src/backlog_manager/presentation/views/dependency_dialog.py`

**Campos**:
| Campo | Tipo | Modo |
|-------|------|------|
| story_id | str (readonly) | Header do dialog |
| story_name | str (readonly) | Header do dialog |
| depends_on | QListWidget | Editável (add/remove) |
| dependents | QListWidget | Somente leitura |
| available_stories | QComboBox | Seleção para adicionar |

**Dimensões**: 500x420px (fixo, per FR-017)

**Estados de Erro**:
- Ciclo detectado: Fundo vermelho claro (#FFEEEE), mensagem explicativa

**Transições de Estado**:
```
[Aberto] --Adicionar(válido)--> [Dependência adicionada, lista atualizada]
[Aberto] --Adicionar(ciclo)--> [Erro ciclo exibido, fundo vermelho]
[Aberto] --Remover--> [Dependência removida, lista atualizada]
[Aberto] --Fechar--> [Fechado]
```

---

### 1.4 MetricsDialog (Novo)

**Arquivo**: `src/backlog_manager/presentation/views/metrics_dialog.py`

**Campos** (somente leitura):
| Campo | Tipo | Formato |
|-------|------|---------|
| stories_allocated | int | "X histórias" |
| execution_time | float | "X.XXs" |
| waves_processed | int | "X ondas" |
| total_iterations | int | "X iterações" |
| deadlocks_detected | int | "X deadlocks" |
| idle_violations | tuple(int,int) | "X detectados, Y corrigidos" |

**Dimensões**: 440x380px (fixo, per FR-020)

**Comportamento**:
- Auto-show após allocation_completed (FR-021)
- NÃO abre se allocation falhou ou stories_allocated == 0 (FR-022)

---

### 1.5 StatusBar Components

**Arquivo**: `src/backlog_manager/presentation/views/status_bar.py`

#### StatsLabel

**Formato**: `"X histórias · Y SP · Última alocação: DD/MM/YYYY HH:MM"`

**Campos**:
| Campo | Tipo | Formato |
|-------|------|---------|
| story_count | int | "X histórias" |
| total_sp | int | "Y SP" |
| last_allocation | datetime | None | "DD/MM/YYYY HH:MM" ou "Sem alocação" |

#### WarningsBadge

**Campos**:
| Campo | Tipo | Comportamento |
|-------|------|---------------|
| warning_count | int | Exibe "⚠ X avisos" |
| warnings_list | list[str] | Conteúdo do popup |

**Visibilidade**: Oculto quando count == 0 (per clarification)

**Popup**: QMenu ou QDialog com scroll para lista de warnings

---

## 2. ViewModels (Presentation Layer)

### 2.1 ConfigDialogViewModel

**Arquivo**: `src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py`

**Properties**:
```python
@dataclass
class ConfigDialogViewModel(QObject):
    velocity: float = 2.0
    start_date: date = field(default_factory=date.today)
    max_idle_days: int = 3
```

**Signals**:
- `saved: Signal()`
- `error_occurred: Signal(str)`

**Methods**:
- `validate() -> tuple[bool, str]`
- `save() -> None`

**Validação**:
- velocity: 0.1 <= v <= 10.0
- max_idle_days: 2 <= d <= 30
- start_date: não nulo

---

### 2.2 DependencyDialogViewModel

**Arquivo**: `src/backlog_manager/presentation/viewmodels/dependency_dialog_viewmodel.py`

**Properties**:
```python
@dataclass
class DependencyDialogViewModel(QObject):
    story_id: str
    story_name: str
    depends_on: list[StoryOutputDTO]
    dependents: list[StoryOutputDTO]
    available_stories: list[StoryOutputDTO]
    has_cycle_error: bool = False
    cycle_error_message: str = ""
```

**Signals**:
- `dependencies_changed: Signal()`
- `error_occurred: Signal(str)`
- `cycle_detected: Signal(str)`

**Methods**:
- `async load_dependencies() -> None`
- `async add_dependency(target_id: str) -> None`
- `async remove_dependency(target_id: str) -> None`

---

### 2.3 StatusBarViewModel

**Arquivo**: `src/backlog_manager/presentation/viewmodels/status_bar_viewmodel.py`

**Properties**:
```python
@dataclass
class StatusBarViewModel(QObject):
    story_count: int = 0
    total_sp: int = 0
    last_allocation: datetime | None = None
    warning_count: int = 0
    warnings: list[str] = field(default_factory=list)
```

**Signals**:
- `stats_changed: Signal()`
- `warnings_changed: Signal()`

**Methods**:
- `update_stats(stories: list[StoryOutputDTO]) -> None`
- `set_last_allocation(timestamp: datetime) -> None`
- `set_warnings(warnings: list[str]) -> None`

---

## 3. Menu Structure

### 3.1 Menu Arquivo

| Item | Atalho | Action |
|------|--------|--------|
| Importar Excel | Ctrl+I | _import_action |
| Exportar Excel | Ctrl+E | _export_action |
| --- | | separator |
| Sair | | _exit_action |

### 3.2 Menu Cadastros

| Item | Atalho | Action |
|------|--------|--------|
| Histórias | Ctrl+N | _new_story_action |
| Features | | _features_action |
| Desenvolvedores | | _developers_action |
| Configuração | | _config_action |

### 3.3 Menu Ferramentas

| Item | Atalho | Action |
|------|--------|--------|
| Calcular Cronograma | Ctrl+Shift+C | _schedule_action |
| Alocar Desenvolvedores | Ctrl+Shift+A | _allocate_action |

### 3.4 Menu Ajuda

| Item | Atalho | Action |
|------|--------|--------|
| Sobre | | _about_action (placeholder) |

---

## 4. Toolbar Groups

### 4.1 Grupo CRUD
| Botão | Ícone | Atalho | Tooltip |
|-------|-------|--------|---------|
| Nova | plus.svg | Ctrl+N | Nova História (Ctrl+N) |
| Editar | pencil-simple.svg | F2 | Editar História (F2) |
| Deletar | trash.svg | Delete | Deletar História (Delete) |

### 4.2 Grupo Priorização
| Botão | Ícone | Atalho | Tooltip |
|-------|-------|--------|---------|
| Mover Cima | arrow-up.svg | Alt+Up | Mover Prioridade Acima (Alt+Up) |
| Mover Baixo | arrow-down.svg | Alt+Down | Mover Prioridade Abaixo (Alt+Down) |

### 4.3 Grupo Cadastros
| Botão | Ícone | Atalho | Tooltip |
|-------|-------|--------|---------|
| Desenvolvedores | users.svg | | Gerenciar Desenvolvedores |
| Features | package.svg | | Gerenciar Features |
| Configuração | gear.svg | | Configuração |

### 4.4 Grupo Processamento
| Botão | Ícone | Atalho | Tooltip |
|-------|-------|--------|---------|
| Calcular | calendar-check.svg | Ctrl+Shift+C | Calcular Cronograma (Ctrl+Shift+C) |
| Alocar | shuffle.svg | Ctrl+Shift+A | Alocar Desenvolvedores (Ctrl+Shift+A) |

### 4.5 Grupo Excel
| Botão | Ícone | Atalho | Tooltip |
|-------|-------|--------|---------|
| Importar | download-simple.svg | Ctrl+I | Importar Excel (Ctrl+I) |
| Exportar | upload-simple.svg | Ctrl+E | Exportar Excel (Ctrl+E) |

---

## 5. Signal Connections (MainWindow)

### 5.1 Novas Conexões

```python
# Config Dialog
self._config_action.triggered.connect(self._open_config_dialog)

# Dependency Dialog (via context menu)
# Conexão feita dinamicamente no contextMenuEvent

# Metrics Dialog auto-show
self._container.allocation_viewmodel.allocation_completed.connect(
    self._on_allocation_completed_show_metrics
)

# Status Bar updates
self._viewmodel.stories_changed.connect(self._update_status_bar_stats)
self._container.allocation_viewmodel.warnings_updated.connect(
    self._update_status_bar_warnings
)
```

### 5.2 Conexões Mantidas

Todas as conexões existentes de:
- StoryDialog
- DeveloperDialog
- FeatureDialog
- ExcelViewModel
- ScheduleViewModel
- AllocationViewModel (exceto novo handler para MetricsDialog)

---

## 6. Delegates Integration

### 6.1 Aplicação de Delegates

```python
# Em _setup_central_widget()
from backlog_manager.presentation.delegates import (
    StatusBadgeDelegate,
    MonospaceDelegate,
)

# Coluna ID (índice 0)
self._story_table.setItemDelegateForColumn(0, MonospaceDelegate(self._story_table))

# Coluna Status (índice depende do modelo, assumindo 5)
self._story_table.setItemDelegateForColumn(5, StatusBadgeDelegate(self._story_table))
```

---

## 7. Arquivos Legados (Não Removidos)

Conforme FR-025, os seguintes arquivos são mantidos mas removidos de main_window.py:

| Arquivo | Status |
|---------|--------|
| config_panel.py | Mantido, não importado |
| dependency_panel.py | Mantido, não importado |
| metrics_panel.py | Mantido, não importado |
| warnings_panel.py | Mantido, não importado |

**Razão**: Preservar histórico e permitir rollback se necessário. Podem ser removidos em EP futuro.
