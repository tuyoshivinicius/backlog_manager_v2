# Research: EP-020 — Busca, Filtros e Menu de Contexto

**Feature Branch**: `020-busca-filtros-menu-contexto`
**Date**: 2026-03-29

---

## R-001: QSortFilterProxyModel com Delegates Existentes

**Contexto**: Inserir proxy entre StoryTableModel e StoryTableView sem quebrar MonospaceDelegate (col 3) e StatusBadgeDelegate (col 6).

**Decision**: Usar QSortFilterProxyModel padrao do Qt, configurado com `setSourceModel()`. Delegates sao propriedade da view (QTableView), nao do modelo. O proxy nao reordena colunas, apenas filtra linhas — indices de coluna permanecem os mesmos.

**Rationale**: O Qt documenta que delegates sao configurados na view e operam sobre o modelo visivel (proxy). Como o proxy nao altera colunas, `setItemDelegateForColumn()` continua mapeando para os mesmos indices. A ordem de configuracao deve ser: (1) proxy.setSourceModel(table_model), (2) view.setModel(proxy), (3) view.setItemDelegateForColumn().

**Alternatives considered**:
- Subclass de QAbstractProxyModel com mapeamento customizado — desnecessario, QSortFilterProxyModel ja resolve o caso.
- Manter filtragem no ViewModel (sem proxy) — quebraria indices da tabela e exigiria recriar o modelo a cada filtro.

---

## R-002: Debounce em Campo de Busca (150ms)

**Contexto**: Filtrar a tabela enquanto o usuario digita, sem processar a cada keystroke.

**Decision**: Usar QTimer.singleShot com 150ms. A cada `textChanged` signal do QLineEdit, cancelar o timer anterior e iniciar novo. Quando o timer dispara, chamar `proxy.set_text_filter(text)`.

**Rationale**: QTimer e nativo do Qt, integrado ao event loop, sem dependencias extras. 150ms e o intervalo padrao para autocomplete responsivo sem sobrecarga. O signal `textChanged` ja emite o texto atual.

**Alternatives considered**:
- Threading com debounce manual — complexidade desnecessaria para operacao sincrona de filtragem.
- Filtrar apenas ao pressionar Enter — nao atende ao requisito de busca incremental.
- Usar QTimer persistente com restart — funcionalmente equivalente, mas `singleShot` e mais simples.

**Implementacao**:
```python
self._search_timer = QTimer()
self._search_timer.setSingleShot(True)
self._search_timer.setInterval(150)
self._search_timer.timeout.connect(self._apply_text_filter)

# No textChanged:
def _on_search_text_changed(self, text: str) -> None:
    self._pending_search_text = text
    self._search_timer.start()  # restart se ja estiver rodando
```

---

## R-003: Chips de Filtro por Status — Padrao Qt

**Contexto**: Exibir 6 chips com contagem, comportamento de radio button, destaque visual no ativo.

**Decision**: Usar QPushButton com `setCheckable(True)` e `setAutoExclusive(True)` dentro de um QButtonGroup. Cada chip recebe objectName "filterChip" e classe QSS para estilizacao. Contagens vem da lista completa do ViewModel (`_stories`), nao do proxy filtrado.

**Rationale**: QPushButton checkable com QButtonGroup implementa radio behavior nativamente. QSS permite estilizar `:checked` e `:hover:!checked` sem codigo Python. Contagens do ViewModel (source of truth) garantem que os numeros refletem o total real.

**Alternatives considered**:
- QToolButton — visualmente similar mas menos customizavel via QSS.
- QRadioButton — semantica correta mas visual inadequado para chips.
- QLabel clicavel — requer mais codigo manual para estado checked.

---

## R-004: Dropdown de Feature/Onda — Populacao Dinamica

**Contexto**: QComboBox com features agrupadas por onda no formato "Onda N - Nome".

**Decision**: QComboBox populado a partir de pares unicos (feature_id, feature_name, wave) extraidos da lista de stories do ViewModel. Primeiro item fixo: "Todas as features" (valor None). Itens ordenados por wave. Sem uso de separadores nativos do QComboBox (complexidade desnecessaria).

**Rationale**: StoryOutputDTO ja contem `feature_name` e `wave` enriquecidos. Extrair features unicas da lista evita criar um use case adicional. Ordenar por wave garante agrupamento visual natural.

**Alternatives considered**:
- ListFeaturesUseCase separado — over-engineering, dados ja disponiveis no DTO (conforme ADR-005).
- QComboBox com model customizado — desnecessario para lista simples.

**Implementacao**:
```python
def _update_feature_dropdown(self) -> None:
    features: dict[int, tuple[str, int]] = {}
    for story in self._viewmodel.stories:
        if story.feature_id and story.feature_name:
            features[story.feature_id] = (story.feature_name, story.wave)

    self._feature_combo.clear()
    self._feature_combo.addItem("Todas as features", None)
    for fid, (name, wave) in sorted(features.items(), key=lambda x: x[1][1]):
        self._feature_combo.addItem(f"Onda {wave} - {name}", fid)
```

---

## R-005: Menu de Contexto — QMenu Efemero

**Contexto**: Right-click em linha da tabela abre menu com 6 acoes + separadores.

**Decision**: Criar QMenu no handler `customContextMenuRequested`. O menu e efemero — criado, exibido com `exec()` e destruido (garbage collected). Acoes criam novas QAction locais que chamam os mesmos slots do ViewModel. A acao "Deletar" recebe propriedade customizada para estilizacao QSS.

**Rationale**: Menu efemero evita gerenciar estado de QAction compartilhadas entre toolbar e menu. Cada invocacao cria acoes frescas sem efeitos colaterais. O padrao `customContextMenuRequested` e o mecanismo Qt padrao para menus de contexto.

**Alternatives considered**:
- Reutilizar QAction da toolbar — efeitos colaterais de estado (enabled/disabled) e estilizacao (ADR-007).
- Menu persistente recriado — overhead desnecessario, menu efemero e suficiente.

**Implementacao**:
```python
self._story_table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
self._story_table.customContextMenuRequested.connect(self._on_context_menu)

def _on_context_menu(self, pos: QPoint) -> None:
    index = self._story_table.indexAt(pos)
    if not index.isValid():
        return
    # Selecionar linha clicada
    self._story_table.selectRow(index.row())
    menu = QMenu(self)
    # ... add actions ...
    menu.exec(self._story_table.viewport().mapToGlobal(pos))
```

---

## R-006: Mapeamento de Indices Proxy ↔ Source

**Contexto**: Acoes do menu de contexto e toolbar precisam do story_id correto quando proxy esta ativo.

**Decision**: Ao obter story_id de uma linha selecionada, usar `proxy.mapToSource(proxy_index)` para obter o indice no source model, e entao `source_model.get_story_at(source_row)` para obter o DTO. Alternativamente, usar `proxy.data(proxy_index, Qt.UserRole)` que ja retorna o story_id (delegado ao source model via proxy).

**Rationale**: QSortFilterProxyModel repassa chamadas `data()` ao source model automaticamente, fazendo o mapeamento de indices internamente. Usar `data(index, UserRole)` e o caminho mais simples e seguro.

**Alternatives considered**:
- Manter referencia direta ao source model para lookup — desnecessario e propenso a erros de indice.

---

## R-007: Desabilitar Mover Acima/Abaixo com Filtros Ativos

**Contexto**: Quando filtros estao ativos, a ordem visual nao corresponde a ordem real de prioridade. Mover linhas filtradas causaria confusao.

**Decision**: Expor propriedade `has_active_filters` no FilterProxyModel (ou no ViewModel). Quando True, desabilitar `_action_move_up` e `_action_move_down` na toolbar. No menu de contexto, criar as acoes ja desabilitadas. Recalcular estado a cada mudanca de filtro.

**Rationale**: E a abordagem mais segura e explicita. O usuario ve visualmente que as acoes estao indisponiveis e entende que deve limpar filtros para reordenar.

**Alternatives considered**:
- Mapear indices do proxy para source e mover no source — confuso para o usuario, a linha movida pode desaparecer do filtro.
- Mostrar tooltip explicativo — complementar, mas insuficiente sem desabilitar.

---

## R-008: Integracao DuplicateStoryUseCase no ViewModel

**Contexto**: DuplicateStoryUseCase ja existe mas nao esta integrado no MainWindowViewModel.

**Decision**: Adicionar metodo `async def duplicate_story(self, story_id: str) -> StoryOutputDTO | None` no MainWindowViewModel, seguindo o padrao identico a `create_story`, `edit_story` e `delete_story`: try/except com `_set_loading()`, `_handle_error()` e `stories_changed.emit()`.

**Rationale**: Consistencia com padrao existente. O use case ja existe e e criado pelo DIContainer. O ViewModel so precisa orquestrar a chamada async e emitir sinais.

**Alternatives considered**:
- Chamar use case diretamente da View — viola MVVM (Principio XIX).

---

## R-009: Estilos QSS para Novos Componentes

**Contexto**: Novos widgets (search field, chips, menu destructive) precisam de estilos consistentes com o design system.

**Decision**: Adicionar estilos ao `stylesheet.qss` existente, usando tokens do design system (@primary, @surface, @error-fg, etc.). Chips usam objectName "filterChip" para seletores QSS. Campo de busca usa objectName "searchField". Menu destructive usa property selector `[destructive="true"]`.

**Rationale**: Manter todos os estilos centralizados no QSS existente, usando o sistema de tokens ja implementado em `theme.py`. Nao criar arquivos QSS separados.

**Alternatives considered**:
- Estilos inline via setStyleSheet() — menos mantenivel, nao usa tokens.
- Arquivo QSS separado por feature — fragmenta a estilizacao.
