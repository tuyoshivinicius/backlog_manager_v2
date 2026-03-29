# Quickstart: EP-018 — Layout Principal e Migração de Painéis

**Date**: 2026-03-28
**Status**: Ready for Implementation

---

## Prerequisites

1. **EP-017 Completo**: Design system com tokens, IconManager, delegates implementados
2. **Dependências Python**: PySide6, qasync, pydantic (já instalados)
3. **Branch**: `018-ep018-layout-migracao-paineis`

---

## Development Setup

```bash
# Ativar ambiente
cd C:/Users/tvini/projects/personal/backlog_manager_v2
poetry shell

# Verificar dependências
poetry install

# Executar aplicação atual (para comparar antes/depois)
poetry run python -m backlog_manager

# Executar testes existentes
poetry run pytest tests/integration/presentation/views/test_main_window.py -v
```

---

## Implementation Order

### Fase 1: Layout Base

1. **Refatorar _setup_central_widget()** em `main_window.py`:
   - Remover QSplitter e painéis laterais
   - Criar QVBoxLayout com filter bar placeholder e tabela

2. **Adicionar _setup_menu_bar()**:
   - Criar menus: Arquivo, Cadastros, Ferramentas, Ajuda
   - Adicionar ações com atalhos

3. **Refatorar _setup_toolbar()**:
   - Adicionar ícones via IconManager
   - Definir estilo ToolButtonTextBesideIcon
   - Agrupar com separadores

4. **Adicionar _setup_status_bar()**:
   - Criar label de estatísticas
   - Criar badge de warnings

### Fase 2: Dialogs

5. **Criar ConfigDialog**:
   - View: `views/config_dialog.py`
   - ViewModel: `viewmodels/config_dialog_viewmodel.py`

6. **Criar DependencyDialog**:
   - View: `views/dependency_dialog.py`
   - ViewModel: `viewmodels/dependency_dialog_viewmodel.py`
   - Migrar lógica de `dependency_panel.py`

7. **Criar MetricsDialog**:
   - View: `views/metrics_dialog.py`
   - Migrar lógica de `metrics_panel.py`
   - Conectar auto-show

### Fase 3: Integrações

8. **Implementar context menu** na tabela
9. **Integrar delegates** (StatusBadge, Monospace)
10. **Criar StatusBarViewModel** e conectar signals

---

## Key Code Patterns

### Menu Bar Setup

```python
def _setup_menu_bar(self) -> None:
    """Configura menu bar com 4 menus."""
    menu_bar = self.menuBar()

    # Menu Arquivo
    file_menu = menu_bar.addMenu("&Arquivo")
    file_menu.addAction(self._import_action)
    file_menu.addAction(self._export_action)
    file_menu.addSeparator()
    exit_action = QAction("Sair", self)
    exit_action.triggered.connect(self.close)
    file_menu.addAction(exit_action)

    # Menu Cadastros
    cadastros_menu = menu_bar.addMenu("&Cadastros")
    cadastros_menu.addAction(self._new_story_action)
    cadastros_menu.addAction(self._features_action)
    cadastros_menu.addAction(self._developers_action)
    cadastros_menu.addSeparator()
    cadastros_menu.addAction(self._config_action)

    # Menu Ferramentas
    tools_menu = menu_bar.addMenu("&Ferramentas")
    tools_menu.addAction(self._schedule_action)
    tools_menu.addAction(self._allocate_action)

    # Menu Ajuda
    help_menu = menu_bar.addMenu("A&juda")
    about_action = QAction("Sobre", self)
    about_action.setEnabled(False)  # Placeholder EP-022
    help_menu.addAction(about_action)
```

### Toolbar with Icons

```python
def _setup_toolbar(self) -> None:
    """Configura toolbar com ícones e grupos."""
    from backlog_manager.presentation.theme.theme import get_icon_manager

    toolbar = QToolBar("Principal")
    toolbar.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
    toolbar.setIconSize(QSize(20, 20))
    toolbar.setMovable(False)
    self.addToolBar(toolbar)

    icon = get_icon_manager()

    # Grupo CRUD
    self._new_story_action = QAction(icon.get("plus"), "Nova", self)
    self._new_story_action.setShortcut(QKeySequence("Ctrl+N"))
    self._new_story_action.setToolTip("Nova História (Ctrl+N)")
    toolbar.addAction(self._new_story_action)

    # ... mais ações ...

    toolbar.addSeparator()

    # Grupo Priorização
    # ...
```

### Status Bar

```python
def _setup_status_bar(self) -> None:
    """Configura status bar com estatísticas e warnings."""
    status = self.statusBar()

    # Estatísticas à esquerda
    self._stats_label = QLabel("0 histórias · 0 SP · Sem alocação")
    status.addWidget(self._stats_label, stretch=1)

    # Badge de warnings à direita
    self._warnings_badge = QPushButton()
    self._warnings_badge.setFlat(True)
    self._warnings_badge.setObjectName("warnings-badge")
    self._warnings_badge.setVisible(False)
    self._warnings_badge.clicked.connect(self._show_warnings_popup)
    status.addPermanentWidget(self._warnings_badge)
```

### Context Menu

```python
def _on_table_context_menu(self, position: QPoint) -> None:
    """Exibe menu de contexto na tabela."""
    index = self._story_table.indexAt(position)
    if not index.isValid():
        return

    story_id = self._get_story_id_from_index(index)
    if not story_id:
        return

    menu = QMenu(self)
    deps_action = menu.addAction("Dependências")
    deps_action.triggered.connect(lambda: self._open_dependency_dialog(story_id))
    menu.exec(self._story_table.viewport().mapToGlobal(position))
```

### MetricsDialog Auto-Show

```python
def _on_allocation_completed(self, result: AllocationResultDTO) -> None:
    """Handler para alocação completa."""
    # ... atualização existente ...

    # Auto-show MetricsDialog se bem-sucedido (FR-021)
    if result.stories_allocated > 0:
        dialog = MetricsDialog(result.metrics, parent=self)
        dialog.exec()
```

---

## Testing Strategy

### Testes Unitários (ViewModels)

```python
# tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py
def test_validate_velocity_invalid():
    vm = ConfigDialogViewModel()
    vm.velocity = 0.0
    is_valid, msg = vm.validate()
    assert not is_valid
    assert "velocidade" in msg.lower()
```

### Testes de Integração (Views)

```python
# tests/integration/presentation/views/test_config_dialog.py
async def test_config_dialog_apply_valid(qtbot, container):
    dialog = ConfigDialog(container)
    qtbot.addWidget(dialog)

    # Set values
    dialog._velocity_spin.setValue(3.0)
    dialog._max_idle_spin.setValue(5)

    # Click apply
    qtbot.mouseClick(dialog._button_box.button(QDialogButtonBox.Ok), Qt.LeftButton)

    assert dialog.result() == QDialog.Accepted
```

---

## Validation Checklist

### Layout (SC-002, SC-006)

- [ ] Tabela ocupa 100% da largura (sem painéis laterais)
- [ ] Layout funcional em 1366x768
- [ ] 5 zonas visíveis: Menu, Toolbar, Filtros, Tabela, Status

### Menu Bar (SC-001)

- [ ] 4 menus presentes: Arquivo, Cadastros, Ferramentas, Ajuda
- [ ] Todos os atalhos funcionando (Ctrl+N, Ctrl+I, etc.)
- [ ] Ações executam corretamente

### Toolbar (SC-007)

- [ ] Ícones SVG renderizados
- [ ] 5 grupos com separadores
- [ ] Tooltips com atalhos

### Dialogs (SC-003, SC-009)

- [ ] ConfigDialog abre em < 100ms
- [ ] MetricsDialog abre automaticamente após alocação
- [ ] DependencyDialog acessível via right-click

### Status Bar (SC-008)

- [ ] Contadores atualizados após CRUD
- [ ] Badge de warnings funcional
- [ ] Popup de warnings com scroll

---

## Common Issues & Solutions

### Ícone não aparece

```python
# Verificar se IconManager foi inicializado
from backlog_manager.presentation.theme.theme import get_icon_manager
icon_mgr = get_icon_manager()
assert icon_mgr.get("plus").isNull() == False
```

### Atalho não funciona

```python
# Usar QKeySequence para compatibilidade
action.setShortcut(QKeySequence("Ctrl+N"))  # ✓
action.setShortcut("Ctrl+N")  # Pode falhar em alguns sistemas
```

### Context menu não aparece

```python
# Habilitar context menu na tabela
self._story_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
self._story_table.customContextMenuRequested.connect(self._on_table_context_menu)
```

---

## Files to Create

| Arquivo | Tipo | Prioridade |
|---------|------|------------|
| `views/config_dialog.py` | View | P2 |
| `views/dependency_dialog.py` | View | P2 |
| `views/metrics_dialog.py` | View | P3 |
| `viewmodels/config_dialog_viewmodel.py` | ViewModel | P2 |
| `viewmodels/dependency_dialog_viewmodel.py` | ViewModel | P2 |
| `viewmodels/status_bar_viewmodel.py` | ViewModel | P2 |

## Files to Modify

| Arquivo | Mudança | Prioridade |
|---------|---------|------------|
| `views/main_window.py` | Refatoração layout completo | P1 |
| `theme/stylesheet.qss` | Novos estilos QMenuBar, QStatusBar | P2 |
| `container.py` | Novos ViewModels | P2 |

## Files to Keep (Legacy)

| Arquivo | Razão |
|---------|-------|
| `views/config_panel.py` | Backup, não importado |
| `views/dependency_panel.py` | Backup, não importado |
| `views/metrics_panel.py` | Backup, não importado |
| `views/warnings_panel.py` | Backup, não importado |
