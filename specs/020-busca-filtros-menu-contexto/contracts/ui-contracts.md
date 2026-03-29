# UI Contracts: EP-020 — Busca, Filtros e Menu de Contexto

**Feature Branch**: `020-busca-filtros-menu-contexto`
**Date**: 2026-03-29

---

## C-001: FilterProxyModel API

**Tipo**: Presentation ViewModel (QSortFilterProxyModel)
**Modulo**: `backlog_manager.presentation.viewmodels.filter_proxy_model`

### Interface

```python
class FilterProxyModel(QSortFilterProxyModel):
    """Proxy model que filtra StoryTableModel por texto, status e feature.

    Aplica filtros com AND logico sem alterar o modelo original.
    """

    def __init__(self, parent: QObject | None = None) -> None: ...

    def set_text_filter(self, text: str) -> None:
        """Define filtro de texto (case-insensitive). Busca em ID, Nome, Componente."""

    def set_status_filter(self, status: str | None) -> None:
        """Define filtro de status. None = todos os status."""

    def set_feature_filter(self, feature_id: int | None) -> None:
        """Define filtro de feature. None = todas as features."""

    @property
    def has_active_filters(self) -> bool:
        """Retorna True se qualquer filtro esta ativo (texto, status ou feature)."""

    # Override
    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Aplica AND logico dos 3 filtros na linha do source model."""
```

### Pre-condicoes

- `sourceModel()` deve ser uma instancia de `StoryTableModel`
- Colunas ID, Nome, Componente, Status, Feature devem existir no source model

### Pos-condicoes

- Apos `set_*_filter()`, `invalidateFilter()` e chamado automaticamente
- `filterAcceptsRow()` retorna True apenas se a linha passa em TODOS os filtros ativos
- `has_active_filters` retorna True se text != "" OR status != None OR feature != None

### Invariantes

- O source model (StoryTableModel) NUNCA e modificado pelo proxy
- Delegates continuam funcionando (indices de coluna inalterados)

---

## C-002: Barra de Filtros (Zona 3)

**Tipo**: Widget composto dentro de MainWindow
**Localizacao**: Zona 3 do layout (_filter_bar, 36px de altura)

### Layout

```
┌──────────────────────────────────────────────────────────────────────┐
│ [🔍 Buscar por ID, nome ou componente...] │ Todos(10) Backlog(5) ... │ [▼ Todas as features] │
│          SearchField (240px)               │     FilterChips (6)      │   FeatureCombo        │
└──────────────────────────────────────────────────────────────────────┘
```

### SearchField Contract

| Propriedade | Valor |
|-------------|-------|
| Tipo | QLineEdit |
| objectName | "searchField" |
| Largura | 240px (fixo) |
| Placeholder | "Buscar por ID, nome ou componente..." |
| Clear button | Habilitado |
| Signal | textChanged → debounce 150ms → proxy.set_text_filter() |
| Atalho | Ctrl+F foca no campo |

### FilterChips Contract

| Chip | Valor do Filtro | Contagem |
|------|-----------------|----------|
| Todos | None (sem filtro) | Total geral |
| Backlog | "BACKLOG" | Count por status |
| Execucao | "EXECUCAO" | Count por status |
| Testes | "TESTES" | Count por status |
| Concluido | "CONCLUIDO" | Count por status |
| Impedido | "IMPEDIDO" | Count por status |

**Comportamento**:
- Apenas 1 chip ativo por vez (QButtonGroup exclusive)
- "Todos" e o chip ativo por padrao
- Clique em chip → proxy.set_status_filter(valor)
- Contagem atualiza via ViewModel.stories_changed signal
- Contagem reflete total geral (nao filtrado)

### FeatureCombo Contract

| Propriedade | Valor |
|-------------|-------|
| Tipo | QComboBox |
| Primeiro item | "Todas as features" (data=None) |
| Itens | "Onda N - Nome" (data=feature_id) |
| Ordenacao | Por wave crescente |
| Signal | currentIndexChanged → proxy.set_feature_filter(data) |
| Atualizacao | Recarrega quando ViewModel.stories_changed |

---

## C-003: Menu de Contexto

**Tipo**: QMenu efemero
**Trigger**: Right-click em linha da tabela (customContextMenuRequested)

### Estrutura

```
┌─────────────────────────┐
│ Editar          Enter   │
│ Duplicar        Ctrl+D  │
│─────────────────────────│
│ Mover Acima     Alt+↑   │  (disabled se filtros ativos)
│ Mover Abaixo    Alt+↓   │  (disabled se filtros ativos)
│─────────────────────────│
│ Dependencias...         │
│─────────────────────────│
│ Deletar         Delete  │  (cor @error)
└─────────────────────────┘
```

### Pre-condicoes

- Menu so aparece se right-click em linha valida (index.isValid())
- Linha clicada e selecionada antes de abrir o menu

### Acoes e Slots

| Acao | Slot | Condicao |
|------|------|----------|
| Editar | _on_edit_story() | Sempre habilitada |
| Duplicar | _on_duplicate_story() | Sempre habilitada |
| Mover Acima | _on_move_up() | Desabilitada se has_active_filters |
| Mover Abaixo | _on_move_down() | Desabilitada se has_active_filters |
| Dependencias... | _open_dependency_dialog() | Sempre habilitada |
| Deletar | _on_delete_story() | Sempre habilitada, dialog confirmacao |

---

## C-004: Acao Duplicar Historia

**Tipo**: QAction na toolbar + atalho + menu de contexto

### Trigger Points

| Origem | Mecanismo |
|--------|-----------|
| Toolbar (Grupo 1) | QAction "Duplicar" com icone |
| Atalho | Ctrl+D (via QAction.shortcut) |
| Menu de contexto | QAction local "Duplicar (Ctrl+D)" |

### Fluxo

```
1. Usuario aciona Duplicar (qualquer trigger)
2. View verifica se ha historia selecionada
   - Se nao: ignora (noop)
3. View chama asyncio.create_task(viewmodel.duplicate_story(story_id))
4. ViewModel:
   a. _set_loading(True)
   b. Cria UoW
   c. Chama DuplicateStoryUseCase.execute(story_id)
   d. Recarrega stories (load_stories)
   e. Emite stories_changed
   f. _set_loading(False)
   g. Retorna StoryOutputDTO da copia
5. View recebe stories_changed:
   a. Atualiza tabela (via proxy/model)
   b. Atualiza contagens dos chips
   c. Atualiza dropdown de features
6. View exibe na Status Bar: "Historia duplicada: {id_original} -> {id_copia}"
```

### Pos-condicoes

- Nova historia criada com: mesmo componente, nome + " (copia)", mesmos SP/status/feature
- Sem developer, datas, duracao ou dependencias na copia
- Prioridade = ultima (max + 1)
- Status Bar exibe feedback

---

## C-005: Toolbar — Desabilitar Mover com Filtros Ativos

### Contrato de Estado

| Condicao | move_up.enabled | move_down.enabled |
|----------|-----------------|-------------------|
| Sem filtros, historia selecionada | True | True |
| Sem filtros, nada selecionado | False | False |
| Com filtros ativos | False | False |

### Signal Flow

```
FilterProxyModel.set_*_filter()
    → View._update_move_actions_state()
        → _action_move_up.setEnabled(not proxy.has_active_filters and has_selection)
        → _action_move_down.setEnabled(not proxy.has_active_filters and has_selection)
```

---

## C-006: Confirmacao de Delete

### Contrato

Todas as origens de delete (toolbar, tecla Delete, menu de contexto) DEVEM exibir dialog de confirmacao antes de executar.

```
QMessageBox.question(
    parent=self,
    title="Confirmar exclusao",
    text=f"Deseja realmente excluir a historia {story_id}?",
    buttons=QMessageBox.Yes | QMessageBox.No,
    defaultButton=QMessageBox.No
)
```

Se resposta == Yes → proceder com ViewModel.delete_story(story_id)
Se resposta == No → cancelar (noop)
