# Research: Roadmap UX Refactor

**Feature**: 043-roadmap-ux-refactor | **Date**: 2026-04-05

## R1: Formato do Codigo da Historia

**Decision**: Usar `story.id` diretamente (ja no formato "COMPONENTE-NNN", ex: "AUTH-001").

**Rationale**: O campo `StoryOutputDTO.id` (tipo `str`) ja contem o identificador no formato desejado. Nao e necessario construir o codigo a partir de `story.component + story.id.zfill(3)` — o ID ja e a concatenacao.

**Alternatives considered**:
- Construir dinamicamente a partir de `component` + sequencial: rejeitado porque `story.id` ja contem essa informacao de forma canonica.

## R2: Agrupamento por Feature — Estrategia de Grouping Key

**Decision**: Usar `story.feature_name` (str | None) como chave de agrupamento. Stories com `feature_name is None` vao para grupo "Sem feature".

**Rationale**: `feature_name` ja esta populado no DTO via enrichment nos use cases. E o campo natural para agrupar pois ja contem o nome legivel da feature.

**Alternatives considered**:
- Agrupar por `feature_id` e fazer lookup do nome: mais complexo, requer mapeamento extra. Rejeitado pela simplicidade.
- Manter `_cached_features` para criacao de grupos vazios (como fazia com waves): rejeitado porque nao ha requisito para mostrar features sem historias agendadas.

## R3: Ordenacao de Grupos (FR-019)

**Decision**: Ordenar por `min_date` (data inicio mais cedo) ascendente, com "Sem feature" sempre por ultimo.

**Rationale**: Conforme spec FR-019 — "features que comecam antes aparecem no topo". Usar `(feature_id is None, min_date or date.max)` como sort key garante "Sem feature" por ultimo e ordenacao temporal para os demais.

**Alternatives considered**:
- Ordenar alfabeticamente por feature name: rejeitado, spec e explicita sobre ordenacao temporal.
- Ordenar por wave da feature: rejeitado, conceito de wave nao mais relevante no agrupamento.

## R4: Toolbar — Reorganizacao de Grupos

**Decision**: 4 grupos semanticos: Zoom | Filtros | Dependencias | Acoes. Extrair `_create_toolbar` em 4 sub-metodos para respeitar limite de 40 linhas.

**Rationale**: Constitution IX (simplicidade, funcoes <=40 linhas). A toolbar atual tem 131 linhas em um unico metodo. Separar em sub-metodos melhora legibilidade e facilita manutencao.

**Alternatives considered**:
- Manter metodo unico com comentarios de secao: rejeitado, viola Constitution IX.
- Criar classe separada ToolbarWidget: over-engineering para o escopo atual.

## R5: Codigo na Barra — Posicionamento

**Decision**: Texto `ax.text()` centralizado dentro da barra se couber (estimativa de largura em pixels). Caso contrario, texto a direita com offset.

**Rationale**: Garante legibilidade do codigo em todos os cenarios. Estimativa de largura usa `len(code) * 6` pixels como heuristica para fonte monospace tamanho 7.

**Alternatives considered**:
- Sempre dentro da barra com fonte auto-scaling: complexo e pode ficar ilegivel em barras muito curtas.
- Sempre fora da barra: desperdica espaco em barras largas.

## R6: Filtros — Substituicao wave/status por feature

**Decision**: Remover campos `wave` e `status` de `RoadmapFilters`. Adicionar campo `feature: str | None`. Manter `developer`, `component`, `search_text`.

**Rationale**: Spec FR-012 explicita: "filtros por feature/componente/responsavel/nome". Wave e status nao fazem parte do novo conjunto de filtros.

**Alternatives considered**:
- Manter status como filtro adicional: rejeitado, spec e explicita sobre quais filtros incluir.
- Adicionar feature sem remover wave: rejeitado, wave nao mais relevante no agrupamento.

## R7: Debounce na Busca por Nome

**Decision**: QTimer instance (singleShot, 300ms). `_on_search_changed` reinicia o timer. `_apply_search_filter` aplica o filtro apos debounce.

**Rationale**: `QTimer.singleShot` (metodo estatico) nao pode ser cancelado. Um QTimer instance com `setSingleShot(True)` permite chamar `start()` repetidamente, reiniciando a contagem.

**Alternatives considered**:
- Sem debounce (aplicar imediatamente): funciona para poucos dados mas pode causar lag com 50+ historias.
- Usar threading.Timer: nao se integra com Qt event loop.

## R8: Dependencias — Setas Somente quando Ambas Visiveis (FR-021)

**Decision**: Quando `target_pos is None` em `_draw_dependency_arrows`, simplesmente `continue` (nao renderizar nada). Remover logica de seta tracejada para historias ocultas.

**Rationale**: FR-021 explicito: "Setas de dependencia so DEVEM ser renderizadas quando ambas historias estao visiveis". Setas tracejadas para destinos ocultos adicionam ruido visual.

**Alternatives considered**:
- Manter setas tracejadas para indicar dependencias parcialmente visiveis: rejeitado, spec e explicita.

## R9: Metricas de Progresso — Coloracao

**Decision**: Aplicar cor no texto do percentual no cabecalho do grupo via `ax.get_yticklabels()` pos-render. Verde (#18794E) para >75%, amarelo (#B45309) para 25-75%, vermelho (#991B1B) para <25%.

**Rationale**: Cores do STATUS_PALETTE existente (CONCLUIDO, TESTES, IMPEDIDO) para consistencia visual. Aplicar pos-render evita complexidade de labels customizados.

**Alternatives considered**:
- Mini progress bar com matplotlib Rectangle: adiciona complexidade significativa para ganho visual marginal. Pode ser adicionado futuramente.
- Texto plano sem cor: perde informacao visual rapida sobre progresso.

## R10: Pan/Drag Horizontal com Matplotlib + PySide6

**Decision**: Implementar pan horizontal via eventos nativos do matplotlib (`button_press_event`, `button_release_event`, `motion_notify_event`) no FigureCanvasQTAgg existente. O pan opera exclusivamente no eixo X (horizontal), alterando `ax.set_xlim()` com base no delta do arrasto.

**Rationale**: O matplotlib ja expoe `mpl_connect()` para os tres eventos necessarios — a implementacao atual ja usa `button_press_event` (para toggle de grupos) e `motion_notify_event` (para tooltips). Basta estender esses handlers. Nao e necessario usar `NavigationToolbar2QT` do matplotlib (toolbar nativa) pois a toolbar customizada ja existe e o pan nativo do matplotlib inclui funcionalidades indesejadas (zoom retangulo, home, etc.). O pan e puramente visual (altera xlim do axes) — nao altera dados do ViewModel, mantendo a separacao View/ViewModel.

**Alternatives considered**:
- matplotlib NavigationToolbar2QT: descartado — toolbar nativa conflita com toolbar customizada; inclui controles de zoom por retangulo indesejados; nao permite cursor customizado facilmente.
- QGraphicsView com pan nativo: descartado — requer reescrever toda a renderizacao; matplotlib FigureCanvas nao e QGraphicsItem.
- QScrollBar horizontal: descartado — nao oferece sensacao de "drag" direto no grafico; requer mapeamento complexo entre posicao do scrollbar e xlim.

**Detalhes de implementacao**:

Estado necessario no View:
- `_is_panning: bool = False`
- `_pan_start_x: float | None = None` (xdata no inicio do drag)
- `_pan_start_xlim: tuple[float, float] | None = None` (xlim no inicio do drag)

Fluxo:
1. `button_press_event` (botao esquerdo, sem Ctrl): registra start_x e start_xlim, seta `_is_panning = True`
2. `motion_notify_event` (se `_is_panning`): calcula dx, aplica `ax.set_xlim(start - dx, end - dx)` com clamping
3. `button_release_event`: seta `_is_panning = False`

Conflito com click existente: distinguir click de drag por threshold de deslocamento — se deslocamento < 5px, tratar como click; senao, foi pan.

Limites do pan (FR-025): clampar xlim para que pelo menos 20% do range de dados permaneca visivel na viewport.

## R11: Cursor de Mao Aberta/Fechada

**Decision**: Usar `Qt.CursorShape.OpenHandCursor` e `Qt.CursorShape.ClosedHandCursor` via `self._canvas.setCursor()` para feedback visual de pan.

**Rationale**: PySide6/Qt ja fornece cursores nativos de mao aberta e fechada — sao cursores padrao do sistema operacional, nao requerem assets customizados. O FigureCanvasQTAgg herda de QWidget, suportando `setCursor()` nativamente. Conforme spec, o cursor deve mudar ao passar sobre area do grafico (FR-023) e durante arrasto (FR-024).

**Alternatives considered**:
- Cursores customizados via QPixmap: descartado — complexidade desnecessaria; cursores nativos sao reconheciveis e consistentes cross-platform.
- CSS cursor property: descartado — nao aplicavel a FigureCanvas do matplotlib.

**Transicoes de cursor**:
- Default (sobre canvas): `OpenHandCursor` — indica area arrastavel
- Durante drag: `ClosedHandCursor` — indica arrasto ativo
- Fora do axes ou sobre toolbar: `ArrowCursor` — cursor padrao

**Integracao com hover**: quando `_is_panning` e True, tooltips sao suprimidos (FR-027: drag nao dispara tooltip).

## R12: Navegacao por Teclas de Seta

**Decision**: Estender `keyPressEvent()` no RoadmapDialog para capturar `Qt.Key.Key_Left` e `Qt.Key.Key_Right`, deslocando o viewport horizontal em 10% da largura visivel por pressionamento.

**Rationale**: O `keyPressEvent` atual ja trata `Escape` para fechar o dialogo — basta adicionar cases para setas. 10% da viewport por tecla e consistente com convencoes de scroll em editores e viewers. Teclas de seta so tem efeito quando zoom > 100% (quando ha conteudo fora da viewport).

**Alternatives considered**:
- Shortcuts via QShortcut: descartado — `keyPressEvent` ja existe e e mais simples para teclas de navegacao.
- Page Up/Page Down: considerado como complemento, mas a spec nao menciona — YAGNI.

**Incremento**: `shift = (xlim[1] - xlim[0]) * 0.10` — 10% da viewport visivel. Negativo para esquerda, positivo para direita. Clampar aos mesmos limites do pan por arrasto.

## R13: Estado Atual da Implementacao vs Spec

**Decision**: A implementacao atual ja contem a maioria das funcionalidades da spec. O delta real e pequeno e concentrado em pan/drag.

**Funcionalidades ja implementadas**:

| Funcionalidade | Status | Referencia |
|----------------|--------|------------|
| Toolbar organizada em 4 grupos com separadores | ✅ | `_create_toolbar()` |
| Icones e tooltips em botoes | ✅ | `_create_zoom_group()`, etc. |
| Zoom in/out/reset via botoes | ✅ | `_apply_zoom()`, `_on_fit_view()`, `_on_fit_content()` |
| Zoom via Ctrl+Scroll | ✅ | `_on_scroll()` |
| Indicador de nivel de zoom | ✅ | `_update_zoom_label()` |
| Filtros: feature/componente/responsavel/nome | ✅ | `_create_filter_group()`, `_build_current_filters()` |
| Filtros AND com indicador visual | ✅ | `RoadmapFilters.matches()`, `_update_filter_styles()` |
| Botao limpar filtros | ✅ | `_on_clear_filters()` |
| Agrupamento por feature com expand/collapse | ✅ | `_render_chart()`, `toggle_group()` |
| Codigo da historia nas barras | ✅ | `_render_story_code()` |
| Codigo na legenda lateral | ✅ | `_build_story_label()` |
| Quantidade de historias no header | ✅ | `_build_group_label()` |
| Percentual de conclusao no header | ✅ | `_build_group_label()`, `completion_percent` |
| Toggle de dependencias | ✅ | `_on_toggle_dependencies()` |
| Grupo "Sem feature" | ✅ | `_build_roadmap_data()` |
| Ordenacao por data de inicio | ✅ | `_create_sorted_groups()` |
| Contagem reflete filtros ativos | ✅ | `apply_filters()` |

**Funcionalidades a implementar**:

| Funcionalidade | FR | Complexidade |
|----------------|-----|--------------|
| Pan horizontal via click+drag | FR-022 | Media |
| Cursor mao aberta/fechada | FR-023, FR-024 | Baixa |
| Navegacao via teclas de seta | FR-026 | Baixa |
| Distincao click vs drag | FR-022/FR-027 | Baixa |
| Reset de pan no fit/reset | FR-028 | Baixa (ja implicito — set_xlim reseta) |
| Limites do pan | FR-025 | Baixa |
