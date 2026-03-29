# Quickstart: EP-020 — Busca, Filtros e Menu de Contexto

**Feature Branch**: `020-busca-filtros-menu-contexto`
**Date**: 2026-03-29

---

## Visao Geral

Este EP adiciona busca incremental, filtros por status/feature, menu de contexto e acao de duplicar historia a UI existente. Todo o escopo esta na camada Presentation — nenhuma alteracao em Domain, Application ou Infrastructure.

## Pre-requisitos

- Branch `020-busca-filtros-menu-contexto` baseada em `001-ep001-foundation-persistence`
- EP-018 (layout com 5 zonas) e EP-019 (StoryTableModel + delegates) completos
- DuplicateStoryUseCase ja disponivel em Application layer
- Ambiente com Python 3.11+, PySide6, pytest, pytest-qt

## Ordem de Implementacao Recomendada

### Fase 1: FilterProxyModel (base para tudo)

1. **Criar `filter_proxy_model.py`** em `presentation/viewmodels/`
   - Subclass de QSortFilterProxyModel
   - Resolver indices de coluna via StoryTableModel.COLUMNS.index()
   - Implementar `filterAcceptsRow()` com AND logico
   - Expor `set_text_filter()`, `set_status_filter()`, `set_feature_filter()`
   - Property `has_active_filters`

2. **Testes unitarios** do FilterProxyModel
   - Criar StoryTableModel com dados mock
   - Testar cada filtro individualmente
   - Testar combinacoes (AND)
   - Testar has_active_filters

### Fase 2: Integrar Proxy na MainWindow

3. **Modificar `main_window.py`** — `_setup_central_widget()`
   - Criar FilterProxyModel
   - `proxy.setSourceModel(viewmodel.table_model)`
   - `view.setModel(proxy)`
   - Reconfigurar delegates APOS setModel(proxy)

4. **Verificar** que delegates continuam funcionando

### Fase 3: Barra de Filtros (Zona 3)

5. **Populadr zona 3** — `_setup_filter_bar()`
   - QHBoxLayout no _filter_bar existente
   - Adicionar SearchField (QLineEdit, 240px)
   - Adicionar 6 FilterChips (QPushButton checkable + QButtonGroup)
   - Adicionar FeatureCombo (QComboBox)
   - Spacer entre grupos

6. **Conectar signals**
   - SearchField.textChanged → debounce timer → proxy.set_text_filter()
   - QButtonGroup.buttonClicked → proxy.set_status_filter()
   - FeatureCombo.currentIndexChanged → proxy.set_feature_filter()
   - ViewModel.stories_changed → atualizar contagens chips + dropdown

7. **Atalho Ctrl+F** → focar SearchField

### Fase 4: Duplicar Historia

8. **Adicionar `duplicate_story()`** no MainWindowViewModel
   - Padrao async identico a create/edit/delete
   - Retornar StoryOutputDTO da copia

9. **Adicionar QAction Duplicar** na toolbar (Grupo 1)
   - Icone de copia, shortcut Ctrl+D
   - Slot `_on_duplicate_story()` → asyncio.create_task()

10. **Feedback na Status Bar** apos duplicacao

### Fase 5: Menu de Contexto

11. **Configurar** `customContextMenuRequested` na StoryTableView
12. **Criar** `_on_context_menu()` com QMenu efemero e 6 acoes
13. **Desabilitar** Mover Acima/Abaixo quando has_active_filters

### Fase 6: Estilos e Polish

14. **Adicionar estilos QSS** para searchField, filterChip, menu destructive
15. **Confirmacao de delete** via QMessageBox em todas as origens
16. **Testes de integracao** com pytest-qt

## Arquivos a Modificar

| Arquivo | Tipo | Descricao |
|---------|------|-----------|
| `presentation/viewmodels/filter_proxy_model.py` | NOVO | QSortFilterProxyModel customizado |
| `presentation/viewmodels/main_window_viewmodel.py` | MODIFICAR | +duplicate_story() |
| `presentation/views/main_window.py` | MODIFICAR | +zona 3, +menu contexto, +Ctrl+D/F |
| `presentation/theme/stylesheet.qss` | MODIFICAR | +estilos novos componentes |
| `tests/unit/presentation/test_filter_proxy_model.py` | NOVO | Testes do proxy model |
| `tests/unit/presentation/test_main_window_viewmodel.py` | MODIFICAR | +testes duplicate |
| `tests/integration/presentation/test_main_window_filters.py` | NOVO | Testes integrados |

## Comandos Uteis

```bash
# Rodar testes do EP-020
pytest tests/unit/presentation/test_filter_proxy_model.py -v

# Rodar todos os testes
pytest tests/ -v

# Verificar formatacao
black src/backlog_manager/presentation/viewmodels/filter_proxy_model.py
isort src/backlog_manager/presentation/viewmodels/filter_proxy_model.py

# Verificar tipos
mypy src/backlog_manager/presentation/viewmodels/filter_proxy_model.py --strict
```

## Riscos e Mitigacoes

| Risco | Mitigacao |
|-------|-----------|
| Delegates quebram com proxy | Configurar delegates APOS setModel(proxy) — testar visualmente |
| Debounce nao cancela timer anterior | QTimer.start() ja reinicia automaticamente |
| Contagens de chips desincronizam | Reagir a stories_changed para recalcular sempre |
| Indices proxy vs source confundem | Usar data(index, UserRole) que delega ao source automaticamente |
| Ctrl+D conflita com outro atalho | Verificado: Ctrl+D nao esta em uso (R-008) |
