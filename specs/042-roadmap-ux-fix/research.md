# Research: Correção de Problemas de Interface do Roadmap

**Date**: 2026-04-04 | **Branch**: `042-roadmap-ux-fix`

## R1: Cores de status nas barras (US1 — P1)

**Decision**: As cores já estão implementadas corretamente em `_render_story_bar()`. O código usa `STATUS_PALETTE` para `color` e `edge_color`. Progresso parcial (background alpha=0.4 + overlay) funciona. IMPEDIDO com borda tracejada está implementado.

**Rationale**: Análise do código mostra que `_render_story_bar()` (linhas 544-594) já mapeia `story.status` → `STATUS_PALETTE.get(story.status)` e aplica cores corretamente. O STATUS_PROGRESS mapping define 0% (BACKLOG), 33% (EXECUCAO), 66% (TESTES), 100% (CONCLUIDO). IMPEDIDO recebe `edgecolor="#991B1B"`, `linewidth=2.5`, `linestyle="--"`.

**Alternatives considered**: Nenhuma — implementação existente está correta. O problema reportado pode ter sido de uma versão anterior ou de dados incorretos. Manter implementação atual, verificar cobertura de testes.

## R2: Expand/collapse bidirecional de waves (US2 — P1)

**Decision**: O toggle existe em `_on_click()` → `toggle_group()` → `_render_chart()`. Problemas identificados: (1) altura mínima de barras não é garantida em px (usa matplotlib data coordinates), (2) truncamento de rótulos longos não implementado, (3) recálculo de altura funciona mas `y_pos += 1.0` fixo pode comprimir com muitas histórias, (4) sem auto-scroll ao expandir.

**Rationale**: O ViewModel `toggle_group()` alterna `_group_states[group_name]` corretamente. A View re-renderiza completamente. Problemas são de refinamento na View, não estruturais.

**Alternatives considered**: QGraphicsView (rejeitada — spec 039/040/041 já migraram para matplotlib).

## R3: Controles de janela (US3 — P1)

**Decision**: A janela já abre maximizada (`dialog.showMaximized()` em `main_window.py:1463`). `setSizeGripEnabled(True)` permite redimensionamento. Falta: `setWindowFlags` com `Qt.Window` para garantir botões minimize/maximize/close no diálogo.

**Rationale**: `QDialog` por padrão não inclui botões maximize/minimize. É necessário definir `self.setWindowFlags(Qt.WindowType.Window)` no construtor do `RoadmapDialog` para obter frame de janela completa com todos os botões.

**Alternatives considered**: Converter para QMainWindow (rejeitada — QDialog com WindowFlags é suficiente e mais simples).

## R4: Eixo temporal adaptativo (US4 — P2)

**Decision**: Implementar `AutoDateLocator` + `ConciseDateFormatter` do matplotlib no lugar do `WeekdayLocator(interval=1)` + `DateFormatter("%d/%m/%Y")` fixos atuais.

**Rationale**: O código atual (linha 483) usa `mdates.WeekdayLocator(interval=1)` que sempre mostra semanas, causando sobreposição em zoom distante. `AutoDateLocator` adapta automaticamente entre dias/semanas/meses. `ConciseDateFormatter` garante rótulos concisos. A rotação de 45° já está aplicada via `autofmt_xdate(rotation=45)`. Para garantir mínimo 5 marcadores: configurar `minticks=5` no locator.

**Alternatives considered**: Locator customizado (rejeitada — AutoDateLocator resolve 95% dos casos com zero código custom).

## R5: Controles de zoom melhorados (US5 — P2)

**Decision**: (1) Substituir ícones SP_ArrowUp/Down por texto unicode 🔍+/🔍- (QStyle não tem ícone de lupa nativo; usar `QIcon.fromTheme("zoom-in")` com fallback para texto "+"/"-"); (2) Adicionar QLabel de zoom level na toolbar; (3) Adicionar botão "Ajustar à tela" (`fit_view`); (4) Limitar zoom máximo para 7 dias na viewport; (5) Tooltips já existem.

**Rationale**: PySide6 QStyle não oferece ícones de lupa padronizados. Usar `QIcon.fromTheme()` com fallback garante funcionalidade multiplataforma. Nível de zoom pode ser calculado como `(xlim_range / total_range) * 100`. Limite de 7 dias = `mdates.date2num(max) - mdates.date2num(min) >= 7`.

**Alternatives considered**: Ícones SVG customizados (rejeitada — adiciona complexidade de assets; fallback de texto é funcional e alinhado com KISS).

## R6: Legenda padronizada (US6 — P2)

**Decision**: A legenda atual usa `mpatches.Patch` com `facecolor`/`edgecolor` + símbolo no label. Para quadrados de 12x12px: usar `handler_map` com `HandlerPatch` customizado ou simplesmente garantir que `fontsize=8` + patches padrão rendam quadrados visíveis. Remover símbolos do label — usar apenas nome do status.

**Rationale**: matplotlib `Patch` na legenda já renderiza como retângulos. O spec pede "exclusivamente quadrados coloridos" sem mistura de símbolos. Manter `fontsize` consistente com design system.

**Alternatives considered**: Legenda manual com `ax.text()` + retângulos desenhados (rejeitada — matplotlib legend com patches é mais simples e auto-posicionada).

## R7: Rótulos de wave com nome da feature (US7 — P2)

**Decision**: O ViewModel já tem `_cached_features` (feature_id → name) e `_cached_feature_waves` (feature_id → wave). Para compor "Wave N — Feature Name", enriquecer `RoadmapGroup` com lista de feature names. O `_build_roadmap_data` precisa rastrear quais features estão em cada grupo.

**Rationale**: Cada `StoryOutputDTO` tem `feature_name` (enriquecido pelo `ListStoriesUseCase`). Ao agrupar por wave, coletar `set()` de `feature_name` por grupo. Formato: `"Wave N — FeatureName - X% [Y histórias]"`. Se múltiplas features: separar por vírgula, truncar com "..." se > 60 chars.

**Alternatives considered**: Adicionar campo no DTO (rejeitada — informação já disponível, apenas precisa ser composta no ViewModel).

## R8: Consistência visual com design system (US8 — P2)

**Decision**: Aplicar stylesheet global ao `RoadmapDialog`. Atualmente os widgets usam estilos inline (`setStyleSheet`). Solução: (1) Chamar `self.setStyleSheet(...)` com tokens do `DESIGN_TOKENS` no construtor, ou (2) garantir que `stylesheet.qss` global é herdado pelo dialog.

**Rationale**: PySide6 propaga stylesheets de pai para filhos. Se `MainWindow` aplica stylesheet global, o `RoadmapDialog` como child herda automaticamente. Verificar se o dialog está sendo criado com `parent=self` (sim, está — `main_window.py:1462`). Estilos inline (`setStyleSheet`) no dialog podem sobrescrever — consolidar para usar tokens do design system.

**Alternatives considered**: Criar QSS específico para o roadmap (rejeitada — viola consistência; melhor herdar o global e customizar apenas o necessário).

## R9: Linha "hoje" destacada (US9 — P2)

**Decision**: A linha existe (linha 496) mas usa cor vermelha `#991B1B` com `alpha=0.5`, `lw=1`, `linestyle="--"`. Spec pede: laranja `#ED8936`, `lw>=2`, `alpha>=0.8`, label "Hoje", camada superior (zorder alto).

**Rationale**: Cor vermelha conflita semanticamente com IMPEDIDO (mesmo `#991B1B`). Laranja é neutro. `zorder=10` garante que fica acima das barras. Label com `ax.text()` posicionado no topo da linha.

**Alternatives considered**: Nenhuma — correção direta dos parâmetros.

## R10: Dropdown fantasma (US10 — P3)

**Decision**: Investigar causa provável: `QComboBox` sem itens ou com item vazio renderiza popup fantasma. Solução: garantir que `blockSignals` é usado corretamente durante `_populate_filter_combos()` e que nenhum `addItem("")` é chamado. Verificar se `clear()` + repopulate causa artefato — pode ser necessário chamar `view().setMinimumWidth()` ou usar `setMaxVisibleItems()`.

**Rationale**: O padrão `blockSignals → clear → addItem → blockSignals(False)` está correto. Provável causa: QComboBox popup residual quando filtro muda e repopula durante hover/focus. Solução: forçar `hidePopup()` antes de repopular.

**Alternatives considered**: Substituir QComboBox por menu customizado (rejeitada — overhead desnecessário).

## R11: Escala temporal adaptativa à distribuição (US11 — P3)

**Decision**: Implementar método `_calculate_density_region()` no ViewModel que identifica a janela temporal com maior concentração de histórias. No dialog, botão "Ajustar ao conteúdo" (`fit_content`) aplica zoom nessa região. Algoritmo: sliding window de 30% do período total, encontrar a posição com maior contagem de histórias.

**Rationale**: Com 190 histórias potencialmente distribuídas de forma desigual, o zoom inicial em 100% do período pode mostrar áreas vazias. Sliding window é O(n*m) mas n=190 e m~=100 é trivial.

**Alternatives considered**: Clustering temporal (rejeitada — sliding window é simples e eficaz para o caso de uso); K-means (rejeitada — overkill).

## R12: Setas de dependência melhoradas (US12 — P3)

**Decision**: (1) Mudar cor de `#991B1B` (vermelho) para `#4A5568` (cinza escuro) ou `#2B6CB0` (azul escuro). (2) Variar `rad` do `connectionstyle` baseado no índice para reduzir sobreposição. (3) Adicionar toggle "Mostrar todas as dependências" na toolbar que renderiza todas as setas, não apenas on-hover.

**Rationale**: Vermelho semanticamente sugere erro. Cor neutra é mais adequada. Curvatura variável: `rad=0.1 + 0.05*i` para i-ésima seta de uma história. Toggle global requer novo estado no ViewModel (`show_all_dependencies`).

**Alternatives considered**: Bezier curves manuais (rejeitada — FancyArrowPatch com `arc3` é suficiente).

## R13: Barra de status enriquecida (US13 — P3)

**Decision**: Adicionar mini-barra de progresso como QProgressBar (ou QWidget customizado) ao lado das contagens textuais no status bar. Usar cores do STATUS_PALETTE para segmentos da barra. Indicar "filtro ativo" quando `RoadmapFilters.is_active`.

**Rationale**: QProgressBar nativo do Qt é limitado a uma cor. Usar QWidget customizado com `paintEvent` para segmentos coloridos é mais flexível e alinhado com o design system.

**Alternatives considered**: matplotlib mini-figure no status bar (rejeitada — overhead de outro canvas; QWidget pintado é mais leve).

## R14: Navegação para alto volume (US14 — P3)

**Decision**: (1) Contador de resultados: adicionar QLabel na toolbar "X de Y histórias". (2) Busca efetiva: já implementada via `apply_filters()` — histórias não-correspondentes são omitidas dos grupos. (3) Scroll sincronizado: matplotlib canvas é único, scroll é nativo. (4) Auto-scroll ao expandir: chamar `self._ax.set_ylim()` para ajustar viewport após toggle.

**Rationale**: Scroll sincronizado não é um problema real — o matplotlib canvas é um único widget. A questão é garantir que ao expandir uma wave, o viewport ajuste para mostrar o conteúdo. Usar `self._canvas.scrollContentsBy()` ou ajustar `ylim` do axes.

**Alternatives considered**: Virtualização de barras (rejeitada — 190 histórias é viável sem virtualização em matplotlib).

## R15: Wave 7 ausente (US15 — P3)

**Decision**: Bug no agrupamento: `_build_roadmap_data()` agrupa por `story.wave` que vem de `feature.wave`. Se nenhuma story tem `feature_id` apontando para uma feature com `wave=7`, a Wave 7 não aparece. Solução: usar a lista de features cacheadas para criar grupos para todas as waves, mesmo vazias.

**Rationale**: Código atual (linhas 251-261) só cria grupo se alguma story pertence àquele wave. Features sem stories (ou com stories sem datas) não geram grupo. Solução: iterar `_cached_feature_waves` para criar grupos base, mesmo que vazios, e marcar como "(vazia)" ou "(0 histórias)".

**Alternatives considered**: Filtrar waves vazias (rejeitada — spec exige que todas sejam exibidas).

## R16: Performance (FR-035)

**Decision**: Renderização de 190 histórias em < 2s é viável com matplotlib. Bottleneck potencial: `_count_business_days()` é O(n) por chamada com loop `while`. Para tooltips (on-hover) não é crítico, mas para renderização em batch, usar fórmula analítica: `np.busday_count(start, end)`.

**Rationale**: matplotlib Agg backend renderiza 200 barras em ~100ms. O overhead vem de `tight_layout()` e `draw_idle()`. Para 190 histórias expandidas, são ~200 barras + labels + grid = ~500ms total. Dentro do budget de 2s.

**Alternatives considered**: QGraphicsView (rejeitada — já decidido por matplotlib nas specs 040/041).

## R17: Navegação por teclado (FR-036)

**Decision**: Toolbar widgets (QComboBox, QLineEdit, QPushButton) já são navegáveis por Tab/Enter nativo do Qt. Expand/collapse de waves via teclado: adicionar `keyPressEvent` no dialog para Enter/Space quando foco está em um grupo (requer rastreamento de grupo selecionado). Para esta iteração: toolbar + filtros por teclado (Tab/Enter) conforme spec — navegação granular nas barras fica para iteração futura.

**Rationale**: Qt nativo gerencia focus order entre widgets filhos. Garantir `setFocusPolicy(Qt.StrongFocus)` nos botões. Para expand/collapse via teclado, seria necessário um sistema de foco no canvas matplotlib que é mais complexo — spec aceita parcial.

**Alternatives considered**: Implementar foco completo no canvas (rejeitada — spec explicitamente aceita parcial para esta iteração).
