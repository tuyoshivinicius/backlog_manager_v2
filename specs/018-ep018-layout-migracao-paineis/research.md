# Research: EP-018 — Layout Principal e Migracao de Paineis

**Date**: 2026-03-28
**Status**: Complete

## Research Tasks

### 1. PySide6 QMainWindow Layout Architecture

**Decision**: Utilizar QMainWindow com QMenuBar nativa, QToolBar com icones, QStatusBar, e QVBoxLayout no central widget.

**Rationale**:
- QMainWindow ja fornece slots dedicados para menuBar(), addToolBar(), e statusBar()
- Menu Bar aparece automaticamente no topo da janela (integracao com sistema Windows)
- QStatusBar tem metodos addWidget() e addPermanentWidget() para posicionar elementos a esquerda/direita
- Central widget deve usar QVBoxLayout para empilhar Barra de Filtros e Tabela

**Alternatives Considered**:
- Usar QVBoxLayout puro com QWidget para menu: Rejeitado - perde integracao nativa com sistema operacional
- Manter QSplitter horizontal: Rejeitado - nao atende requisito de tabela em 100% da largura

**Implementation Pattern**:


### 2. QMenuBar Best Practices

**Decision**: Criar menus via addMenu() e actions via addAction() com QKeySequence para atalhos.

**Rationale**:
- QMenuBar.addMenu(title) cria QMenu hierarquico
- QAction suporta triggered signal, shortcut, tooltip, icon
- Atalhos de teclado devem usar QKeySequence para compatibilidade cross-platform

**Menu Structure** (per FR-001 to FR-005):
- Arquivo: Importar Excel (Ctrl+I), Exportar Excel (Ctrl+E), Sair
- Cadastros: Historias (Ctrl+N), Features, Desenvolvedores, Configuracao
- Ferramentas: Calcular Cronograma (Ctrl+Shift+C), Alocar Desenvolvedores (Ctrl+Shift+A)
- Ajuda: Sobre (placeholder)

### 3. QToolBar with Icons

**Decision**: Usar QToolBar.setToolButtonStyle(ToolButtonTextBesideIcon) e QAction com QIcon do IconManager.

**Rationale**:
- ToolButtonTextBesideIcon atende FR-006 (icone + texto ao lado)
- IconManager ja carrega SVGs de assets/icons/ (implementado em EP-017)
- addSeparator() cria separadores visuais entre grupos

**Toolbar Groups** (per FR-007):
1. CRUD: Nova (+), Editar (pencil), Deletar (trash)
2. Priorizacao: Mover Cima (arrow-up), Mover Baixo (arrow-down)
3. Cadastros: Desenvolvedores (users), Features (package), Configuracao (gear)
4. Processamento: Calcular Cronograma (calendar-check), Alocar (shuffle)
5. Excel: Importar (download-simple), Exportar (upload-simple)

### 4. QStatusBar Layout

**Decision**: Usar addWidget() para labels a esquerda e addPermanentWidget() para badge de warnings a direita.

**Rationale**:
- addWidget() posiciona widgets que sao empurrados por mensagens temporarias
- addPermanentWidget() posiciona widgets que permanecem fixos a direita
- Badge de warnings pode ser QPushButton estilizado que exibe popup ao clicar

### 5. Modal Dialog Pattern

**Decision**: Criar QDialog subclasses com setModal(True), fixed sizes, e botoes Aplicar/Cancelar.

**Rationale**:
- QDialog.exec() bloqueia ate fechamento, retornando Accepted/Rejected
- setWindowModality(WindowModal) permite que dialog bloqueie apenas parent
- Tamanhos fixos por FR-015/FR-017/FR-020

### 6. Context Menu for Table

**Decision**: Implementar contextMenuEvent() na StoryTableView para exibir menu com opcao "Dependencias".

**Rationale**:
- Per FR-027, DependencyDialog e acessado via right-click na linha da tabela
- contextMenuEvent recebe QContextMenuEvent com globalPos() para posicionamento
- QMenu.exec() exibe menu popup e retorna action selecionada

### 7. MetricsDialog Auto-Show Pattern

**Decision**: Conectar signal allocation_completed ao metodo que abre MetricsDialog com metricas.

**Rationale**:
- Per FR-021/FR-022, dialog abre automaticamente apos alocacao bem-sucedida
- Nao abre se stories_allocated == 0 ou se houve erro
- Dialog deve ser modal para focar atencao do usuario

### 8. Delegate Integration

**Decision**: Aplicar StatusBadgeDelegate e MonospaceDelegate as colunas apropriadas durante _setup_central_widget().

**Rationale**:
- Per FR-023/FR-024, delegates ja estao implementados em EP-017
- setItemDelegateForColumn() aplica delegate a coluna especifica
- Requer conhecer indices de coluna (ID=0, Status=dependendo do modelo)

## Dependencies Identified

1. **IconManager** (theme.py): Ja implementado, fornece get_icon_manager().get(name)
2. **StatusBadgeDelegate**: Ja implementado em delegates/status_badge_delegate.py
3. **MonospaceDelegate**: Ja implementado em delegates/monospace_delegate.py
4. **DESIGN_TOKENS**: Ja definidos em theme.py para cores e espacamentos
5. **AllocationMetricsDTO**: Ja existe em application/dto/allocation.py

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Atalhos conflitam com sistema | Low | Medium | Testar em Windows; usar QKeySequence.StandardKey quando possivel |
| Popup de warnings excede tela | Low | Low | Implementar scroll interno com QScrollArea |
| Delegates nao encontram coluna | Medium | High | Validar indices via table_model.column_index() |
| Testes de panels quebram | High | Medium | Adaptar testes para nova arquitetura de dialogs |

## Recommendations

1. **Ordem de implementacao**:
   - Layout base (QVBoxLayout) -> Menu Bar -> Toolbar com icones -> Status Bar -> Dialogs
2. **Reusar logica existente**: ConfigPanel, DependencyPanel, MetricsPanel tem logica que pode ser copiada para dialogs
3. **Testar resolucao minima**: Validar layout em 1366x768 antes de finalizar
4. **Preservar atalhos existentes**: Manter Ctrl+N, Ctrl+Shift+A, etc. que ja funcionam
