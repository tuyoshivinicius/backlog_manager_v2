# Research: Roadmap UX Overhaul

**Feature**: 041-roadmap-ux-overhaul
**Date**: 2026-04-03

## R-001: Colapso/Expansao de Grupos em matplotlib

**Decision**: Implementar colapso/expansao no ViewModel (estado logico) e re-renderizar o chart completo ao alternar. Nao usar animacoes matplotlib — redesenhar o chart com grupos filtrados.

**Rationale**: matplotlib nao suporta nativamente colapso/expansao de elementos. A abordagem mais simples e manter um `dict[str, bool]` de estados de expansao no ViewModel e, ao renderizar, desenhar apenas a barra-resumo para grupos colapsados ou as barras individuais para grupos expandidos. Re-renderizar o chart completo e rapido o suficiente (<500ms para 200 historias, conforme benchmarks do matplotlib barh).

**Alternatives considered**:
- Animacao com `FuncAnimation`: Complexidade excessiva, sem beneficio real para UX. Rejeitada por KISS.
- QGraphicsView customizado: Substituiria toda a infraestrutura matplotlib existente. Rejeitada por escopo excessivo.
- Ocultar/mostrar patches individuais: matplotlib nao suporta bem ocultar subconjuntos de barras sem re-render. Rejeitada por fragilidade.

## R-002: Filtragem e Busca no ViewModel

**Decision**: Filtros aplicados no ViewModel sobre dados cacheados (`_cached_stories`). O ViewModel expoe metodos `apply_filters()` e `clear_filters()` que retornam `RoadmapData` filtrado. A View chama `_render_chart()` com os dados filtrados.

**Rationale**: Os dados ja estao completamente em memoria apos `load_data()`. Filtrar in-memory sobre ~200 historias e instantaneo. Nao ha necessidade de consultar o banco novamente. O ViewModel ja tem o padrao de cache com `_cached_stories`.

**Alternatives considered**:
- Filtrar na View (matplotlib): Viola MVVM — logica de filtragem pertence ao ViewModel. Rejeitada.
- Novos use cases com filtros: Adicionaria complexidade desnecessaria — dados ja estao em memoria. Viola YAGNI. Rejeitada.

## R-003: Barra-Resumo para Grupos Colapsados

**Decision**: Para grupos colapsados, renderizar uma unica barra horizontal cobrindo o intervalo `[min(start_date), max(end_date)]` do grupo, com cor baseada no status predominante e texto mostrando `"{nome} - {completion}%"`. A barra-resumo usa altura maior que barras individuais (1.2 vs 0.6).

**Rationale**: A barra-resumo funciona como um "preview" compacto do grupo, transmitindo intervalo temporal e progresso de forma visual. O texto com percentual de conclusao da informacao imediata sem expandir. A cor predominante e um bonus visual mas nao essencial — pode usar cor neutra com overlay de progresso.

**Alternatives considered**:
- Apenas texto sem barra: Perde a informacao temporal (posicao na timeline). Rejeitada.
- Barra com gradiente multi-status: Complexidade visual excessiva para beneficio marginal. Rejeitada.

## R-004: Tooltip Enriquecido com Dependencias

**Decision**: Estender `_build_tooltip_text()` para incluir todos os campos da spec (nome, status, responsavel, story points, datas, duracao em dias uteis, componente, dependencias). Dependencias formatadas como lista de IDs. O tooltip existente (matplotlib annotation) e suficiente — nao precisa de widget Qt customizado.

**Rationale**: O mecanismo de tooltip ja existe (`_on_hover` + annotation). Basta enriquecer o conteudo. Calcular dias uteis pode ser feito inline: `sum(1 for d in date_range if d.weekday() < 5)`. As dependencias ja estao disponíveis no DTO (`dependency_ids`).

**Alternatives considered**:
- Tooltip com QWidget popup: Adicionaria complexidade de posicionamento Qt vs matplotlib. Rejeitada por simplicidade.
- Panel lateral de detalhes: Escopo excessivo, nao solicitado na spec. Rejeitada.

## R-005: Setas de Dependencias no Hover

**Decision**: Ao detectar hover sobre uma historia, desenhar setas (matplotlib `annotate` com `arrowprops`) conectando a historia as suas dependencias diretas. Setas desenhadas como overlay temporario que e removido ao sair do hover. Usar `FancyArrowPatch` com estilo `arc3,rad=0.1` para evitar sobreposicao com barras.

**Rationale**: matplotlib `annotate` com `arrowprops` e a forma mais simples de desenhar setas entre pontos. O overlay temporario evita poluicao visual permanente. A especificacao exige apenas dependencias diretas (1 nivel), limitando a complexidade.

**Alternatives considered**:
- Setas permanentes (sempre visiveis): Poluicao visual com 200+ historias. Rejeitada.
- Linhas retas simples: Podem se sobrepor a barras. `arc3` e preferivel. Rejeitada.

## R-006: Scroll Sincronizado (Labels vs Barras)

**Decision**: Usar o mecanismo nativo do matplotlib: labels como ytick labels no axes principal. Como labels e barras compartilham o mesmo axes, o scroll vertical ja e sincronizado nativamente. O problema atual de desalinhamento (se existir) e resolvido por usar um unico axes para ambos.

**Rationale**: A implementacao atual ja usa ytick labels no mesmo axes das barras, entao labels e barras ja estao naturalmente sincronizados. O requisito FR-019 e atendido pela arquitetura existente. Se necessario scroll horizontal independente, o matplotlib `NavigationToolbar` ja suporta pan/zoom.

**Alternatives considered**:
- Dois paineis separados com scroll sincronizado: Complexidade desnecessaria se o axes unico resolve. Rejeitada.
- QSplitter com dois canvas: Duplicaria a infraestrutura de rendering. Rejeitada.

## R-007: Progresso Visual nas Barras

**Decision**: Implementar progresso como uma barra interna de preenchimento parcial. Cada barra de historia e renderizada em duas camadas: (1) barra completa com cor de fundo (status color, alpha reduzido), (2) barra parcial sobreposta (mesma cor, alpha total) cobrindo a porcentagem de progresso (0/33/66/100%). O mapeamento status->progresso e fixo conforme spec.

**Rationale**: Duas camadas de barh sobrepostas e o padrao mais simples em matplotlib para indicar preenchimento parcial. O alpha diferenciado cria contraste visual claro entre "completado" e "restante".

**Alternatives considered**:
- Hatch patterns: Menos intuitivos que preenchimento parcial. Rejeitada.
- Icone/badge de progresso: Ocupa espaco extra e menos intuitivo que preenchimento na propria barra. Rejeitada.

## R-008: Legenda de Cores e Rodape Estatistico

**Decision**: Legenda implementada como `ax.legend()` do matplotlib com patches coloridos para cada status. Rodape atualizado para exibir contagem por status em vez de contagem total. Ambos refletem filtros ativos.

**Rationale**: `ax.legend()` e nativo do matplotlib e se posiciona automaticamente. Para o rodape, o QLabel de status bar existente e suficiente — basta formatar o texto com contagens por status.

**Alternatives considered**:
- Legenda como widgets Qt separados: Perderia sincronizacao com o chart. Rejeitada.
- Rodape como QTableWidget: Overengineering para dados tabulares simples. Rejeitada.

## R-009: Performance com 200+ Historias

**Decision**: Manter matplotlib barh como mecanismo de rendering. Para 200+ historias, o gargalo nao e a renderizacao (matplotlib e eficiente com barh) mas sim o redraw completo. Estrategias: (1) grupos colapsados por padrao reduzem itens visiveis drasticamente, (2) blitting para updates parciais se necessario, (3) cache de figure para regrouping.

**Rationale**: Com grupos colapsados por padrao (~20 waves = ~20 barras-resumo em vez de 200 barras individuais), a renderizacao inicial e rapida (<1s). Ao expandir um grupo individual, re-render com ~20-30 barras adicionais e negligivel. O requisito de <3s para 200+ historias com todos expandidos e atendido por matplotlib barh nativo (benchmarks indicam ~0.5s para 500 barras).

**Alternatives considered**:
- Substituir matplotlib por QGraphicsView: Reescrita completa. Rejeitada por escopo.
- Virtualização (renderizar apenas visiveis): Complexidade excessiva para matplotlib. Rejeitada.

## R-010: Agrupamento Fixo por Wave

**Decision**: Alterar o agrupamento padrao de FEATURE para WAVE. Cada grupo corresponde a uma wave (Feature.wave). Historias sem wave ficam em grupo "Sem wave". O ComboBox de agrupamento existente sera substituido por controles de filtro.

**Rationale**: A spec especifica que o agrupamento e "sempre por wave" — sem opcao de mudar criterio. O ViewModel atual agrupa por feature ou component; precisa ser adaptado para agrupar por wave. O campo `wave` ja esta disponivel no StoryOutputDTO.

**Alternatives considered**:
- Manter agrupamento dual (wave + feature/component): Spec exige apenas wave. Viola YAGNI. Rejeitada.

## R-011: Toolbar com Icones

**Decision**: Substituir o ComboBox de agrupamento por controles de filtro (ComboBoxes para wave, status, responsavel, componente + QLineEdit para busca). Cada botao da toolbar recebe icone via `QIcon.fromTheme()` ou icones embutidos (PySide6 built-in icons). Todos com tooltips descritivos.

**Rationale**: A toolbar atual tem apenas agrupamento e zoom. A spec exige filtros e busca na toolbar. PySide6 tem icones built-in via `QStyle.StandardPixmap` que sao suficientes para botoes de zoom, limpar filtros, etc.

**Alternatives considered**:
- Icones SVG customizados: Dependencia externa desnecessaria. PySide6 built-in e suficiente. Rejeitada.
- Toolbar como panel lateral: Ocupa espaco excessivo. Rejeitada.
