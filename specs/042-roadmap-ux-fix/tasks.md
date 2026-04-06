# Tasks: Correção de Problemas de Interface do Roadmap

**Input**: Design documents from `/specs/042-roadmap-ux-fix/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/roadmap-ui-contract.md

**Tests**: Não solicitados explicitamente — testes omitidos. Expandir testes existentes se necessário durante implementação.

**Organization**: Tasks agrupadas por user story para implementação e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode executar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: User story associada (US1–US15)
- Caminhos exatos incluídos nas descrições

---

## Phase 1: Setup (Constantes e Infraestrutura Compartilhada)

**Purpose**: Adicionar constantes e estruturas de dados necessárias para múltiplas user stories

- [X] T001 Adicionar constantes TODAY_LINE_COLOR, TODAY_LINE_WIDTH, TODAY_LINE_ALPHA, TODAY_LINE_ZORDER, DEPENDENCY_COLOR, DEPENDENCY_HIDDEN_COLOR, ZOOM_MAX_DAYS, LEGEND_PATCH_SIZE, MAX_LABEL_CHARS em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T002 [P] Adicionar campo `feature_names: list[str]` ao dataclass `RoadmapGroup` em `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`
- [X] T003 [P] Adicionar campo `_show_all_dependencies: bool` e método `toggle_show_all_dependencies()` ao `RoadmapViewModel` em `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

---

## Phase 2: Foundational (Pré-requisitos Bloqueantes)

**Purpose**: Alterações no ViewModel que servem múltiplas user stories — DEVEM ser concluídas antes das fases de user story

**CRITICAL**: Nenhuma user story pode iniciar antes desta fase estar completa

- [X] T004 Modificar `_build_roadmap_data()` para popular `feature_names` no `RoadmapGroup` a partir de `story.feature_name` e criar grupos para waves vazias via `_cached_feature_waves` em `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`
- [X] T005 Implementar método `get_density_region() -> tuple[date, date]` com algoritmo sliding window no `RoadmapViewModel` em `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

**Checkpoint**: Fundação pronta — implementação de user stories pode iniciar

---

## Phase 3: User Story 1 — Cores de Status nas Barras (Priority: P1) MVP

**Goal**: Cada barra exibe cor correspondente ao status real (BACKLOG cinza, EXECUÇÃO azul, TESTES amarelo, CONCLUÍDO verde, IMPEDIDO vermelho tracejado) com preenchimento parcial indicando progresso

**Independent Test**: Carregar backlog com histórias em diferentes status e verificar visualmente que cada barra exibe a cor e preenchimento corretos conforme STATUS_PALETTE

**Nota**: Conforme research R1, a implementação de cores já está correta em `_render_story_bar()`. Esta fase é de verificação e eventual correção.

- [X] T006 [US1] Verificar e validar que `_render_story_bar()` aplica corretamente STATUS_PALETTE para todos os 5 status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T007 [US1] Verificar que STATUS_PROGRESS mapping (0% BACKLOG, 33% EXECUCAO, 66% TESTES, 100% CONCLUIDO) gera preenchimento parcial correto em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T008 [US1] Verificar que IMPEDIDO renderiza com `edgecolor="#991B1B"`, `linewidth=2.5`, `linestyle="--"` em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US1 verificada — barras com cores de status corretas

---

## Phase 4: User Story 2 — Expandir e Colapsar Waves (Priority: P1)

**Goal**: Toggle bidirecional funcional, altura mínima legível, truncamento de rótulos, scroll vertical fluido

**Independent Test**: Clicar em cabeçalhos de waves verificando toggle, altura mínima das barras, truncamento de labels e scroll

- [X] T009 [US2] Implementar truncamento de rótulos longos com reticências (MAX_LABEL_CHARS=60) na renderização de labels de histórias expandidas em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T010 [US2] Garantir altura mínima de 20px por história expandida (ajustar `y_pos` increment e coordenadas matplotlib) em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T011 [US2] Implementar recálculo correto de altura total do gráfico ao expandir/colapsar sem comprimir linhas existentes em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T012 [US2] Implementar auto-scroll ao expandir wave para que conteúdo expandido fique visível (ajustar `ylim` do axes) em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US2 completa — expand/collapse funcional com labels legíveis

---

## Phase 5: User Story 3 — Controles de Janela (Priority: P1)

**Goal**: Janela abre maximizada com botões de minimizar, maximizar e fechar funcionais

**Independent Test**: Abrir roadmap e verificar que janela abre maximizada com botões de controle

- [X] T013 [US3] Definir `self.setWindowFlags(Qt.WindowType.Window)` no construtor do `RoadmapDialog` para habilitar botões minimize/maximize/close em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T014 [US3] Garantir que `showMaximized()` continua sendo chamado após definição de WindowFlags e que redimensionamento adapta conteúdo sem distorção em `src/backlog_manager/presentation/views/main_window.py`

**Checkpoint**: US3 completa — janela com controles padrão

---

## Phase 6: User Story 4 — Eixo Temporal Adaptativo (Priority: P2)

**Goal**: Marcadores de data se adaptam ao zoom com granularidade variável (dias/semanas/meses), sem sobreposição

**Independent Test**: Variar zoom e verificar que marcadores permanecem legíveis com granularidade adequada

- [X] T015 [US4] Substituir `WeekdayLocator(interval=1)` por `AutoDateLocator(minticks=5)` e `DateFormatter` por `ConciseDateFormatter(locator)` em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T016 [US4] Ajustar rotação de marcadores para no máximo 45 graus (quando necessário) e garantir mínimo 5 marcadores visíveis em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US4 completa — eixo temporal adaptativo e legível

---

## Phase 7: User Story 5 — Controles de Zoom (Priority: P2)

**Goal**: Ícones de lupa +/-, indicador de nível %, botão "Ajustar à tela", limite de 7 dias, tooltips

**Independent Test**: Interagir com controles verificando ícones, indicador, tooltips e botão fit

- [X] T017 [US5] Substituir ícones SP_ArrowUp/Down por texto "+" e "-" com fallback de `QIcon.fromTheme("zoom-in"/"zoom-out")` nos botões de zoom em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T018 [US5] Adicionar QLabel indicador de zoom level ("100%") na toolbar, atualizado a cada mudança de zoom em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T019 [US5] Adicionar botão "Ajustar à tela" na toolbar que redimensiona zoom para mostrar todo o período do roadmap em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T020 [US5] Implementar limite de zoom máximo para mostrar no máximo 7 dias (ZOOM_MAX_DAYS) na viewport em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T021 [US5] Garantir tooltips descritivos em todos os botões da toolbar (zoom in, zoom out, ajustar à tela, limpar filtros, etc.) em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US5 completa — controles de zoom intuitivos com feedback

---

## Phase 8: User Story 6 — Legenda Padronizada (Priority: P2)

**Goal**: Legenda com quadrados coloridos padronizados sem símbolos, tipografia do design system

**Independent Test**: Verificar visualmente que legenda usa apenas quadrados coloridos e segue design system

- [X] T022 [US6] Refatorar legenda para usar `mpatches.Patch` sem símbolos no label (remover "●" dos labels), fontsize=8, quadrados mínimo 12x12px em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US6 completa — legenda padronizada

---

## Phase 9: User Story 7 — Rótulos de Wave com Feature (Priority: P2)

**Goal**: Rótulos exibem "Wave N — [Feature] - X% [Y histórias]" com fallback

**Independent Test**: Verificar que rótulos das waves exibem formato completo com nome da feature

- [X] T023 [US7] Modificar renderização de labels de wave para usar formato "Wave N — FeatureName - X% [Y histórias]" usando `feature_names` do `RoadmapGroup`, com fallback para "Wave N - X% [Y histórias]" em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T024 [US7] Implementar truncamento de rótulos de wave com múltiplas features (separadas por vírgula, truncar em MAX_LABEL_CHARS com "...") em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US7 completa — rótulos de wave informativos

---

## Phase 10: User Story 8 — Consistência Visual (Priority: P2)

**Goal**: Widgets do roadmap seguem stylesheet global da aplicação

**Independent Test**: Comparar visualmente componentes do roadmap com componentes equivalentes em outras telas

- [X] T025 [US8] Remover ou consolidar estilos inline (`setStyleSheet`) do `RoadmapDialog` para herdar stylesheet global via parent, usando tokens do DESIGN_TOKENS quando customização é necessária em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T026 [US8] Garantir que campo de busca inclui ícone de lupa e segue estilo visual dos inputs da aplicação em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US8 completa — consistência visual com design system

---

## Phase 11: User Story 9 — Linha "Hoje" Destacada (Priority: P2)

**Goal**: Linha "hoje" espessa, laranja, com label "Hoje", em camada superior

**Independent Test**: Verificar que linha "hoje" é claramente distinta das linhas de grade e possui label

- [X] T027 [US9] Modificar renderização da linha "hoje" para usar TODAY_LINE_COLOR (#ED8936), TODAY_LINE_WIDTH (2.0), TODAY_LINE_ALPHA (0.8), estilo sólido, TODAY_LINE_ZORDER (10) em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T028 [US9] Adicionar label "Hoje" com `ax.text()` posicionado no topo da linha "hoje" em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US9 completa — linha "hoje" visualmente destacada

---

## Phase 12: User Story 10 — Dropdown Fantasma (Priority: P3)

**Goal**: Dropdown de Status funciona sem artefatos visuais

**Independent Test**: Interagir repetidamente com dropdown de Status verificando ausência de artefatos

- [X] T029 [US10] Adicionar `hidePopup()` antes de repopular combos em `_populate_filter_combos()` para eliminar artefatos visuais de popup fantasma em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US10 completa — dropdown sem artefatos

---

## Phase 13: User Story 11 — Escala Temporal Adaptativa (Priority: P3)

**Goal**: Zoom inicial foca na região de maior densidade; botão "Ajustar ao conteúdo"

**Independent Test**: Abrir roadmap com dados desigualmente distribuídos e verificar foco na região densa

- [X] T030 [US11] Adicionar botão "Ajustar ao conteúdo" na toolbar que chama `get_density_region()` do ViewModel e aplica zoom na região retornada em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US11 completa — escala adaptativa à distribuição

---

## Phase 14: User Story 12 — Setas de Dependência (Priority: P3)

**Goal**: Setas em cor neutra, curvatura variável, toggle global "Mostrar todas"

**Independent Test**: Hover sobre histórias com dependências verificando cor, curvatura e toggle global

- [X] T031 [US12] Modificar cor das setas de dependência de `#991B1B` para DEPENDENCY_COLOR (`#4A5568`) e implementar curvatura variável `rad=0.1 + 0.05*i` em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T032 [US12] Adicionar botão toggle "Dependências" na toolbar que chama `toggle_show_all_dependencies()` e renderiza todas as setas permanentemente quando ativo em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US12 completa — setas de dependência melhoradas

---

## Phase 15: User Story 13 — Barra de Status Enriquecida (Priority: P3)

**Goal**: Mini-barra de progresso colorida no rodapé com indicação de filtros ativos

**Independent Test**: Verificar que rodapé exibe contagens com mini-barra e indica filtros ativos

- [X] T033 [US13] Implementar widget de mini-barra de progresso horizontal com segmentos coloridos usando STATUS_PALETTE no status bar em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T034 [US13] Modificar texto do rodapé para exibir "X de Y histórias (filtro ativo)" quando filtros estiverem ativos em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: US13 completa — barra de status enriquecida

---

## Phase 16: User Story 14 — Navegação para Alto Volume (Priority: P3)

**Goal**: Busca com contador, ocultação de não-correspondentes, auto-scroll sincronizado

**Independent Test**: Buscar história em backlog grande verificando contador, ocultação e scroll

- [X] T035 [US14] Adicionar QLabel contador de resultados "X de Y histórias" na toolbar, atualizado a cada mudança de filtro/busca em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T036 [US14] Garantir que busca efetiva oculta histórias não-correspondentes (verificar que `apply_filters()` remove histórias dos grupos renderizados) em `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

**Checkpoint**: US14 completa — navegação eficiente para alto volume

---

## Phase 17: User Story 15 — Wave 7 Ausente (Priority: P3)

**Goal**: Todas as waves renderizadas sem lacunas, waves vazias com indicação "(vazia)"

**Independent Test**: Verificar que todas as waves são exibidas sem lacunas na numeração

- [X] T037 [US15] Garantir que `_build_roadmap_data()` cria grupos para todas as waves (inclusive vazias) iterando `_cached_feature_waves`, exibindo waves sem histórias com indicação "(vazia)" ou "(0 histórias)" em `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py`

**Checkpoint**: US15 completa — todas as waves visíveis

---

## Phase 18: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias que afetam múltiplas user stories

- [X] T038 [P] Garantir navegação por teclado (Tab/Enter) nos controles da toolbar e filtros com `setFocusPolicy(Qt.StrongFocus)` nos botões em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T039 [P] Verificar performance de renderização com 190 histórias ≤ 2s — otimizar `_count_business_days()` com `np.busday_count()` se necessário em `src/backlog_manager/presentation/views/roadmap_dialog.py`
- [X] T040 Executar validação do quickstart.md — rodar testes existentes e verificar que todos passam
- [X] T041 Verificar contraste WCAG AA (4.5:1) para todas as cores de barras e rótulos usando `calculate_contrast_ratio` do design system em `src/backlog_manager/presentation/theme/theme.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup (T002, T003) — BLOQUEIA todas as user stories
- **US1 (Phase 3)**: Depende de Phase 2 — verificação, pode iniciar independentemente
- **US2 (Phase 4)**: Depende de Phase 2
- **US3 (Phase 5)**: Depende de Phase 2
- **US4–US9 (Phases 6–11)**: Dependem de Phase 2 — podem executar em paralelo entre si
- **US10–US15 (Phases 12–17)**: Dependem de Phase 2 — podem executar em paralelo entre si
- **US5 (Phase 7)** deve ser concluída antes de **US11 (Phase 13)** (botão "Ajustar ao conteúdo" na mesma toolbar)
- **US7 (Phase 9)** depende de T004 (feature_names populados no ViewModel)
- **US15 (Phase 17)** depende de T004 (waves vazias criadas no ViewModel)
- **Polish (Phase 18)**: Depende de todas as user stories desejadas completas

### User Story Dependencies

- **US1 (P1)**: Independente — verificação de implementação existente
- **US2 (P1)**: Independente — refatoração na View
- **US3 (P1)**: Independente — WindowFlags no construtor
- **US4 (P2)**: Independente — substituição de locator/formatter
- **US5 (P2)**: Independente — novos botões na toolbar
- **US6 (P2)**: Independente — refatoração da legenda
- **US7 (P2)**: Depende de T004 (feature_names no RoadmapGroup)
- **US8 (P2)**: Independente — consolidação de estilos
- **US9 (P2)**: Independente — parâmetros da linha "hoje"
- **US10 (P3)**: Independente — hidePopup no combo
- **US11 (P3)**: Depende de T005 (get_density_region) e US5 (toolbar com zoom)
- **US12 (P3)**: Depende de T003 (toggle_show_all_dependencies)
- **US13 (P3)**: Independente — widget no status bar
- **US14 (P3)**: Independente — contador e filtro efetivo
- **US15 (P3)**: Depende de T004 (waves vazias no _build_roadmap_data)

### Within Each User Story

- Core implementation antes de integração
- Story completa antes de mover para próxima prioridade

### Parallel Opportunities

- T002 e T003 podem executar em paralelo (campos diferentes no ViewModel)
- T001, T002, T003 podem executar em paralelo (arquivos diferentes)
- US1, US2, US3 (P1) podem executar em paralelo após Phase 2
- US4, US5, US6, US8, US9 (P2) podem executar em paralelo após Phase 2
- US10, US12, US13, US14 (P3) podem executar em paralelo após Phase 2
- T038 e T039 (Polish) podem executar em paralelo

---

## Parallel Example: P1 User Stories

```bash
# Após Phase 2, iniciar as 3 user stories P1 em paralelo:
Task: "T006-T008 — US1: Verificar cores de status em roadmap_dialog.py"
Task: "T009-T012 — US2: Expand/collapse em roadmap_dialog.py"
Task: "T013-T014 — US3: Window flags em roadmap_dialog.py + main_window.py"
```

## Parallel Example: P2 User Stories (arquivos independentes)

```bash
# US4, US6, US9 operam em seções diferentes do mesmo arquivo — sequenciais
# US5 e US8 podem ser paralelos se tocam seções distintas
Task: "T015-T016 — US4: Eixo temporal em roadmap_dialog.py"
Task: "T022 — US6: Legenda em roadmap_dialog.py"
Task: "T027-T028 — US9: Linha hoje em roadmap_dialog.py"
```

---

## Implementation Strategy

### MVP First (US1 + US2 + US3 — P1 Only)

1. Complete Phase 1: Setup (constantes e campos)
2. Complete Phase 2: Foundational (ViewModel changes)
3. Complete Phase 3–5: US1, US2, US3 (P1)
4. **STOP and VALIDATE**: Testar as 3 user stories P1 independentemente
5. Deploy/demo se pronto

### Incremental Delivery

1. Setup + Foundational -> Fundação pronta
2. US1 + US2 + US3 (P1) -> MVP funcional com cores, expand/collapse e janela
3. US4–US9 (P2) -> Polimento visual e UX
4. US10–US15 (P3) -> Melhorias avançadas e edge cases
5. Polish -> Performance, acessibilidade, validação

### Single Developer Strategy

1. Complete Setup + Foundational
2. P1 sequencial: US3 (mais simples) -> US1 (verificação) -> US2 (mais complexo)
3. P2 sequencial: US4 -> US9 -> US5 -> US6 -> US7 -> US8
4. P3 sequencial: US10 -> US15 -> US11 -> US12 -> US13 -> US14
5. Polish

---

## Notes

- [P] tasks = arquivos diferentes, sem dependências
- [Story] label mapeia task à user story para rastreabilidade
- Cada user story pode ser completada e testada independentemente
- Commit após cada task ou grupo lógico
- Parar em qualquer checkpoint para validar story independentemente
- Evitar: tasks vagas, conflitos no mesmo arquivo, dependências cross-story que quebrem independência
- **Atenção**: Maioria das tasks modifica `roadmap_dialog.py` — serializar tasks que tocam o mesmo método/seção
