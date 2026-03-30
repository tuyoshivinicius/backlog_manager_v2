# Quickstart: Table Selection Highlight

**Feature**: 025-table-selection-highlight
**Date**: 2026-03-30

## Resumo

Adicionar destaque visual persistente à linha selecionada na tabela de backlog, com restauração automática após operações de move/edit/delete.

## Arquivos a Modificar

### Produção

1. **`src/backlog_manager/presentation/theme/theme.py`**
   - Adicionar tokens: `selection-bg`, `selection-fg`, `selection-border`, `hover-bg`
   - Adicionar QSS para `QTableView::item:selected` e `QTableView::item:hover`

2. **`src/backlog_manager/presentation/views/main_window.py`**
   - Aplicar QSS de seleção ao `StoryTableView`
   - Implementar `_restore_selection(story_id)` — busca row por story_id e chama `setCurrentIndex`
   - Conectar `stories_changed` → restauração de seleção
   - Atualizar `_on_delete_story()` — selecionar linha adjacente após exclusão
   - Desabilitar Edit/Delete quando nenhuma história selecionada

3. **`src/backlog_manager/presentation/delegates/status_badge_delegate.py`**
   - Verificar `option.state & State_Selected` no `paint()`
   - Usar `selection-bg` como background da célula quando selecionada

4. **`src/backlog_manager/presentation/delegates/dependency_indicator_delegate.py`**
   - Verificar estado de seleção e ajustar background

5. **`src/backlog_manager/presentation/delegates/monospace_delegate.py`**
   - Verificar estado de seleção e ajustar foreground

6. **`src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py`**
   - Garantir que `selected_story_id` é preservado após `load_stories()`
   - Adicionar lógica de seleção adjacente após delete

### Testes

7. **`tests/unit/presentation/viewmodels/test_main_window_viewmodel.py`**
   - Testes de preservação de `selected_story_id` após refresh
   - Testes de seleção adjacente após delete

8. **`tests/integration/presentation/views/test_main_window.py`**
   - Testes de seleção visual (click → highlight)
   - Testes de persistência de seleção após move up/down
   - Testes de desabilitação de botões sem seleção

## Ordem de Implementação

1. Tokens de design (theme.py) — base para tudo
2. QSS de seleção (main_window.py) — visual básico
3. Delegates — consistência visual
4. Restauração de seleção (main_window.py + viewmodel) — comportamento
5. Desabilitação de ações — safety
6. Testes

## Comandos Úteis

```bash
# Rodar testes da feature
pytest tests/unit/presentation/viewmodels/test_main_window_viewmodel.py -v
pytest tests/integration/presentation/views/test_main_window.py -v

# Rodar aplicação para teste visual
poetry run python -m backlog_manager

# Verificar formatação
black src/backlog_manager/presentation/ tests/
isort src/backlog_manager/presentation/ tests/

# Type check
mypy src/backlog_manager/presentation/
```
