# Research: Table Selection Highlight

**Feature**: 025-table-selection-highlight
**Date**: 2026-03-30

## R-001: Abordagem para Estilização de Seleção em QTableView

**Decision**: Utilizar QSS (Qt Style Sheets) para estilizar o pseudo-estado `::item:selected` da `QTableView`, combinado com pintura custom nos delegates existentes para respeitar o estado de seleção.

**Rationale**: QSS é a abordagem nativa e mais simples do Qt para estilizar estados visuais (hover, selected, focus). Permite definir cores de background e foreground diretamente, sem necessidade de custom painting complexo. Os delegates existentes (StatusBadgeDelegate, DependencyIndicatorDelegate, MonospaceDelegate) já fazem custom painting — precisam apenas verificar `option.state & QStyle.StateFlag.State_Selected` para ajustar cores quando a linha está selecionada.

**Alternatives considered**:
- **Custom delegate painting para todas as colunas**: Rejeitado — excesso de complexidade; QSS resolve para colunas padrão, delegates existentes precisam de ajuste pontual.
- **Override de `QStyledItemDelegate.paint()` global**: Rejeitado — interferiria com os delegates especializados já implementados.
- **QProxyStyle**: Rejeitado — muito mais complexo que QSS para o mesmo resultado visual.

## R-002: Restauração de Seleção Após Refresh do Modelo

**Decision**: Após operações que chamam `load_stories()` (move up, move down, delete, status change), restaurar a seleção usando o `story_id` armazenado no ViewModel (`selected_story_id`). A View busca o índice do story_id no modelo e chama `setCurrentIndex()`.

**Rationale**: O `StoryTableModel` já expõe story_id via `Qt.ItemDataRole.UserRole`. Após `beginResetModel`/`endResetModel`, a seleção é perdida. Restaurar via `setCurrentIndex()` após o signal `stories_changed` é a abordagem mais direta. O ViewModel já mantém `selected_story_id`, então basta a View reconectar a seleção ao índice correto.

**Alternatives considered**:
- **Persistir `QModelIndex` e restaurar**: Rejeitado — `QModelIndex` é invalidado após reset do modelo.
- **Usar `QPersistentModelIndex`**: Rejeitado — também invalidado em `beginResetModel`.
- **Não chamar `beginResetModel` (atualizar in-place)**: Rejeitado — exigiria refatoração significativa do modelo para suportar move operations incrementais; não está no escopo.

## R-003: Diferenciação Visual entre Hover e Seleção

**Decision**: Utilizar cores distintas para hover (`::item:hover`) e seleção (`::item:selected`). Hover usa tonalidade mais sutil (neutral-100 como background), seleção usa primary-light como background com primary como borda lateral (ou primary-dark como foreground). Quando ambos hover + selected, usar cor levemente mais intensa.

**Rationale**: A spec exige (FR-008) que "selection highlight MUST be clearly distinguishable from hover effects and from the normal row state". Usando o design system existente: hover = neutral-100 (#F5F5F5), selected = primary-light (#E6F0FA) com borda left primary (#0066CC). Contraste calculado: foreground #171717 sobre background #E6F0FA = ratio ~15.5:1 (WCAG AAA).

**Alternatives considered**:
- **Usar mesma cor com opacidade diferente**: Rejeitado — Qt QSS não suporta RGBA de forma confiável em todas as plataformas.
- **Apenas mudança de borda sem background**: Rejeitado — muito sutil para percepção rápida (SC-001: identificar em <1s).

## R-004: Comportamento de Seleção Após Exclusão

**Decision**: Quando a história selecionada é deletada, mover seleção para a história adjacente (próxima, ou anterior se era a última). Se a tabela ficar vazia, limpar seleção. Implementar no callback `_on_delete_story()` da View, usando o índice anterior como referência.

**Rationale**: Edge case da spec: "What happens when the selected story is deleted? The selection should move to the nearest remaining story, or clear if the table becomes empty." A lógica é: salvar o row index antes do delete, após refresh, selecionar `min(old_row, new_row_count - 1)`.

**Alternatives considered**:
- **Sempre limpar seleção após delete**: Rejeitado — experiência inferior; usuário perde contexto de posição na lista.
- **Selecionar a primeira história**: Rejeitado — comportamento inesperado se o usuário estava no meio da lista.

## R-005: Interação de Seleção com Delegates Existentes

**Decision**: Os delegates existentes (StatusBadgeDelegate, DependencyIndicatorDelegate, MonospaceDelegate) devem verificar `option.state & QStyle.StateFlag.State_Selected` no método `paint()` e:
1. **StatusBadgeDelegate**: Manter o badge pill com cores próprias, mas desenhar o background da célula com a cor de seleção (em vez do wave background).
2. **DependencyIndicatorDelegate**: Usar background de seleção quando a linha estiver selecionada.
3. **MonospaceDelegate**: O texto monospace deve usar a cor de foreground de seleção quando selecionado.

**Rationale**: Se os delegates não respeitarem o estado de seleção, a linha terá aparência inconsistente — algumas colunas com highlight, outras sem. O StatusBadgeDelegate já faz `fillRect` para o background da célula; basta trocar a cor quando selecionado.

**Alternatives considered**:
- **Não alterar delegates**: Rejeitado — criaria inconsistência visual (colunas com delegate sem highlight).
- **Substituir delegates por QSS**: Rejeitado — perderíamos os badges estilizados e indicadores de dependência.

## R-006: Desabilitar Ações Quando Nenhuma História Selecionada

**Decision**: Avaliar estado atual — o MainWindow já tem `_update_move_actions_state()` que habilita/desabilita botões de move. Estender para Edit e Delete: desabilitar quando `selected_story_id is None`. Usar `setEnabled(False)` nas ações do toolbar/menu.

**Rationale**: FR-006 exige "disable or provide feedback for Edit/Delete/Move actions when no story is selected." A abordagem mais simples é desabilitar as ações via `QAction.setEnabled(False)`, o que já deixa o botão visualmente esmaecido — feedback visual claro sem necessidade de mensagem extra.

**Alternatives considered**:
- **Mostrar dialog "Selecione uma história primeiro"**: Rejeitado como abordagem primária — interruptivo. Pode ser mantido como fallback se alguém chamar a ação programaticamente, mas o botão desabilitado previne o caso do usuário.
