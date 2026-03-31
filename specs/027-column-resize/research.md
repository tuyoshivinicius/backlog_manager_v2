# Research: Column Resize

**Feature Branch**: `027-column-resize`
**Date**: 2026-03-31

## Research Tasks

### R1: Como QHeaderView lida com redimensionamento interativo

**Decision**: Usar `QHeaderView.ResizeMode.Interactive` para todas as colunas exceto "Nome" (que permanece `Stretch`).

**Rationale**: O `StoryTableView.__init__` já configura `header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)`, porém o método `_setup_table_columns` em `main_window.py:508-520` sobrescreve cada coluna para `Fixed`. A mudança consiste em trocar `Fixed` por `Interactive`, mantendo larguras mínimas via `setMinimumSectionSize(30)`.

**Alternatives considered**:
- `ResizeToContents`: automático mas impede arraste manual — rejeitado
- `Fixed` (atual): impede totalmente o redimensionamento — é o problema atual
- `Interactive` + `Stretch` para Nome: permite arraste manual + coluna flexível — escolhido

### R2: Persistência de larguras de colunas via QSettings

**Decision**: Usar `QHeaderView.saveState()` / `restoreState()` com QSettings, grupo `"column_widths"`.

**Rationale**: O projeto já usa QSettings (IniFormat, UserScope, "BacklogManager") no `ConfigDialogViewModel`. `saveState()` serializa todas as larguras, ordem e modos de redimensionamento em um `QByteArray`, que pode ser armazenado diretamente no QSettings. Isso é mais robusto que salvar cada largura individualmente.

**Alternatives considered**:
- Salvar larguras individuais por nome de coluna: mais granular mas frágil se colunas mudam — rejeitado
- Usar arquivo JSON separado: inconsistente com padrão existente (QSettings) — rejeitado
- `saveState()`/`restoreState()`: padrão Qt, robusto, uma linha para salvar/restaurar — escolhido

### R3: Duplo-clique para auto-fit ao conteúdo

**Decision**: Implementar handler de `sectionDoubleClicked` no `QHeaderView` que chama `resizeSectionToContents(logicalIndex)` seguido de persistência.

**Rationale**: `QHeaderView.resizeSectionToContents()` é o método nativo do Qt para auto-fit. Calcula a largura com base no conteúdo visível das células + cabeçalho, comportamento idêntico ao Excel.

**Alternatives considered**:
- Calcular manualmente iterando rows: desnecessário, Qt já faz isso — rejeitado
- Usar `ResizeToContents` mode permanente: impede redimensionamento manual — rejeitado

### R4: Menu de contexto para restaurar larguras padrão

**Decision**: Adicionar item "Restaurar larguras padrão" ao menu de contexto do `QHeaderView` via `customContextMenuRequested`.

**Rationale**: O spec FR-007 exige acesso via menu de contexto do cabeçalho. O `QHeaderView` suporta `setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)` nativamente. A restauração aplica os valores de `StoryTableModel.COLUMN_WIDTHS` e remove o estado salvo do QSettings.

**Alternatives considered**:
- Botão separado na toolbar: não solicitado no spec, adiciona complexidade visual — rejeitado
- Atalho de teclado: pode complementar mas não substitui o menu de contexto — não implementado nesta iteração

### R5: Integração com colunas ocultas (responsividade)

**Decision**: Preservar o mecanismo existente de ocultação de colunas (Onda, Componente, Duração) em janelas < 1024px. Larguras salvas só se aplicam a colunas visíveis.

**Rationale**: O `main_window.py:256-311` já tem lógica de responsividade que oculta/exibe colunas baseado na largura da janela. O `saveState()`/`restoreState()` do QHeaderView preserva automaticamente o estado de visibilidade, então os dois mecanismos coexistem sem conflito.

**Alternatives considered**:
- Desabilitar redimensionamento em modo narrow: limita funcionalidade sem necessidade — rejeitado
- Salvar estados separados para narrow/wide: complexidade desnecessária — rejeitado
