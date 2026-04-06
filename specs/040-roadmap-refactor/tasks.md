# Tasks: Refatoracao do Roadmap Visualization

**Input**: Design documents from `/specs/040-roadmap-refactor/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Testes incluidos — arquivos de teste existentes serao atualizados para refletir a nova implementacao.

**Organization**: Tasks agrupadas por user story para implementacao e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story associada (US1, US2, etc.)
- Caminhos exatos de arquivos nas descricoes

---

## Phase 1: Setup

**Purpose**: Adicionar dependencia matplotlib e preparar estrutura

- [x] T001 Adicionar matplotlib ^3.10.0 ao pyproject.toml via `poetry add matplotlib@^3.10.0`
- [x] T002 [P] Adicionar matplotlib ao mypy overrides em pyproject.toml (ignore_missing_imports)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Refatorar ViewModel removendo indicadores e QSettings — necessario antes de qualquer user story

**CRITICAL**: Nenhuma user story pode iniciar antes desta fase estar completa

- [x] T003 Remover dataclass RoadmapIndicators, metodos load_indicators(), save_indicators(), is_overdue(), is_critical_blocker() e import QSettings em `src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py` (FR-013, FR-014)
- [x] T004 Remover testes de indicadores (TestIsOverdue, TestIsCriticalBlocker, TestQSettingsRoundTrip) e imports associados em `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py`
- [x] T005 Atualizar `src/backlog_manager/presentation/views/main_window.py` linhas 1456-1477: remover chamada a `vm.load_indicators()`, remover parametro `indicators` ao instanciar RoadmapDialog, ajustar para nova assinatura da dialog

**Checkpoint**: ViewModel simplificado, sem indicadores. Testes do viewmodel passam.

---

## Phase 3: User Story 1 - Visualizar todas as historias no roadmap (Priority: P1) MVP

**Goal**: Garantir que 100% das historias com datas calculadas aparecem no grafico, agrupadas por Feature, com cores do STATUS_PALETTE.

**Independent Test**: Criar conjunto de historias com datas e verificar que todas aparecem no grafico renderizado.

### Tests for User Story 1

- [x] T006 [US1] Atualizar testes existentes em `tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py`: remover import de RoadmapIndicators, garantir que TestLoadData e TestRoadmapGroup continuam passando com ViewModel simplificado

### Implementation for User Story 1

- [x] T007 [US1] Reescrever `src/backlog_manager/presentation/views/roadmap_dialog.py`: remover todas as classes QGraphicsView (StoryBarItem, RoadmapGraphicsView, GroupLabelPanel), remover imports de QGraphicsView/QGraphicsScene/QGraphicsRectItem, remover constantes antigas (PIXELS_PER_DAY, BAR_SPACING, etc.), criar nova classe RoadmapDialog com matplotlib FigureCanvas embarcado — renderizar barras horizontais (ax.barh) para cada historia agrupada por Feature com cores do STATUS_PALETTE, labels de grupo com percentual de conclusao, eixo X com datas (mdates), mensagem informativa quando nao ha dados (FR-015)
- [x] T008 [US1] Adicionar constantes de layout matplotlib (BAR_HEIGHT, GROUP_SPACING, LABEL_FONT_SIZE, GROUP_FONT_SIZE, MIN_BAR_WIDTH_DAYS) em `src/backlog_manager/presentation/views/roadmap_dialog.py` conforme data-model.md
- [x] T009 [US1] Atualizar mocks e testes em `tests/unit/presentation/views/test_roadmap_dialog.py`: substituir mocks de QGraphicsView por mocks de matplotlib (FigureCanvas, Figure, Axes), adaptar TestBuildTooltipHtml para nova funcao de tooltip, adicionar teste verificando que todas as historias aparecem no chart

**Checkpoint**: Roadmap renderiza todas as historias com matplotlib. Agrupamento por Feature funciona com percentual.

---

## Phase 4: User Story 2 - Carregamento assincrono sem travamento (Priority: P1)

**Goal**: Interface nunca congela durante carregamento de dados, indicador de progresso visivel.

**Independent Test**: Verificar que loading indicator aparece e interface permanece responsiva durante carregamento.

### Implementation for User Story 2

- [x] T010 [US2] Implementar indicador de progresso (QLabel ou QProgressBar) na RoadmapDialog em `src/backlog_manager/presentation/views/roadmap_dialog.py`: exibir durante load_data(), ocultar apos renderizacao, exibir mensagem de erro amigavel em caso de falha de I/O (FR-007, FR-008)
- [x] T011 [US2] Atualizar `src/backlog_manager/presentation/views/main_window.py` _execute_roadmap(): instanciar RoadmapDialog com nova assinatura (sem indicators), abrir dialog maximizada e modal, carregar dados async dentro da dialog (nao antes de abrir)
- [x] T012 [US2] Adicionar teste de loading state em `tests/unit/presentation/views/test_roadmap_dialog.py`: verificar que loading indicator e configurado corretamente na inicializacao

**Checkpoint**: Dialog abre imediatamente, mostra loading, carrega dados async, renderiza sem travar.

---

## Phase 5: User Story 3 - Renderizacao profissional com matplotlib (Priority: P2)

**Goal**: Visual profissional estilo Gantt adequado para apresentacoes.

**Independent Test**: Verificar que grafico matplotlib renderiza com barras de Gantt, labels legiveis e visual limpo.

### Implementation for User Story 3

- [x] T013 [US3] Refinar renderizacao em `src/backlog_manager/presentation/views/roadmap_dialog.py`: ajustar fig.tight_layout(), cores de fundo, grid sutil, formatacao de datas no eixo X (mdates.DateFormatter), labels legiveis com tamanho de fonte adequado, barra com largura minima de MIN_BAR_WIDTH_DAYS para historias com start==end
- [x] T014 [US3] Implementar status bar na RoadmapDialog em `src/backlog_manager/presentation/views/roadmap_dialog.py`: exibir total de historias, historias agendadas, intervalo de datas (min_date a max_date)

**Checkpoint**: Roadmap com visual profissional, pronto para apresentacoes.

---

## Phase 6: User Story 4 - Alternar agrupamento Feature/Componente (Priority: P2)

**Goal**: Permitir alternar agrupamento via toolbar.

**Independent Test**: Alternar controle e verificar que historias se reorganizam corretamente.

### Implementation for User Story 4

- [x] T015 [US4] Implementar toolbar com QComboBox para agrupamento (Feature/Componente) em `src/backlog_manager/presentation/views/roadmap_dialog.py`: conectar a viewmodel.regroup(), re-renderizar grafico ao trocar agrupamento (FR-004)
- [x] T016 [US4] Adicionar teste de regroup na dialog em `tests/unit/presentation/views/test_roadmap_dialog.py`: verificar que troca de agrupamento chama viewmodel.regroup() e atualiza chart

**Checkpoint**: Agrupamento Feature/Componente funciona com percentuais recalculados.

---

## Phase 7: User Story 5 - Navegacao no grafico (scroll e zoom) (Priority: P3)

**Goal**: Scroll horizontal/vertical e zoom via Ctrl+scroll e botoes +/-.

**Independent Test**: Verificar que scroll e zoom funcionam no grafico renderizado.

### Implementation for User Story 5

- [x] T017 [US5] Implementar zoom via Ctrl+scroll (mpl_connect scroll_event) e botoes +/- na toolbar em `src/backlog_manager/presentation/views/roadmap_dialog.py`: zoom horizontal centrado no mouse, limites min/max de escala (FR-009, FR-010)
- [x] T018 [US5] Implementar scroll horizontal/vertical via ajuste de xlim/ylim do matplotlib em `src/backlog_manager/presentation/views/roadmap_dialog.py`

**Checkpoint**: Navegacao completa no grafico com scroll e zoom.

---

## Phase 8: User Story 6 - Tooltip com detalhes da historia (Priority: P3)

**Goal**: Tooltip ao passar o mouse sobre barras com nome, status, datas.

**Independent Test**: Verificar que tooltip exibe informacoes corretas ao hover.

### Implementation for User Story 6

- [x] T019 [US6] Implementar tooltip via mpl_connect('motion_notify_event') + QToolTip.showText() em `src/backlog_manager/presentation/views/roadmap_dialog.py`: detectar barra sob cursor, exibir nome, status, start_date, end_date, ocultar ao sair da barra (FR-011)
- [x] T020 [US6] Adaptar testes de tooltip em `tests/unit/presentation/views/test_roadmap_dialog.py`: atualizar TestBuildTooltipHtml para nova funcao de tooltip (nome, status, datas)

**Checkpoint**: Tooltips funcionam com informacoes corretas.

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Validacao final, limpeza e qualidade

- [x] T021 [P] Atualizar mocks em `tests/headless_mocks.py` se necessario para suportar matplotlib mocks
- [x] T022 Executar suite completa de testes: `poetry run pytest tests/ -v --cov=src/backlog_manager --cov-report=term-missing`
- [x] T023 [P] Executar formatacao e linting: `poetry run black` + `poetry run isort` nos arquivos modificados
- [x] T024 [P] Executar type checking: `poetry run mypy` nos arquivos modificados
- [x] T025 Executar validacao funcional conforme quickstart.md: abrir app, menu Roadmap, verificar todas as historias, agrupamento, zoom, scroll, tooltips

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEIA todas as user stories
- **US1 (Phase 3)**: Depende de Foundational — MVP
- **US2 (Phase 4)**: Depende de US1 (dialog precisa existir para adicionar loading)
- **US3 (Phase 5)**: Depende de US1 (refinamento visual da renderizacao existente)
- **US4 (Phase 6)**: Depende de US1 (toolbar precisa de chart para re-renderizar)
- **US5 (Phase 7)**: Depende de US1 (navegacao no chart existente)
- **US6 (Phase 8)**: Depende de US1 (tooltips nas barras existentes)
- **Polish (Phase 9)**: Depende de todas as user stories desejadas

### User Story Dependencies

- **US1 (P1)**: Apos Foundational — nenhuma dependencia de outras stories
- **US2 (P1)**: Apos US1 — precisa da dialog com chart
- **US3 (P2)**: Apos US1 — pode rodar em paralelo com US2
- **US4 (P2)**: Apos US1 — pode rodar em paralelo com US2/US3
- **US5 (P3)**: Apos US1 — pode rodar em paralelo com US2/US3/US4
- **US6 (P3)**: Apos US1 — pode rodar em paralelo com US2/US3/US4/US5

### Within Each User Story

- Testes atualizados antes ou junto com implementacao
- Core rendering antes de refinamentos
- Dialog completa antes de integracao com main_window

### Parallel Opportunities

- T001 e T002 (Setup) podem rodar em paralelo
- Apos US1, as stories US2-US6 podem rodar em paralelo (arquivos diferentes ou secoes independentes do mesmo arquivo)
- T021, T023, T024 (Polish) podem rodar em paralelo

---

## Parallel Example: User Story 1

```bash
# Apos Foundational completa, lancar US1:
Task: "Reescrever roadmap_dialog.py com matplotlib (T007)"
Task: "Adicionar constantes de layout matplotlib (T008)"
# Apos T007+T008:
Task: "Atualizar testes da dialog (T009)"
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Completar Phase 1: Setup (matplotlib)
2. Completar Phase 2: Foundational (remover indicadores)
3. Completar Phase 3: User Story 1 (renderizacao basica)
4. **STOP and VALIDATE**: Testar que todas as historias aparecem, agrupadas por Feature
5. Deploy/demo se pronto

### Incremental Delivery

1. Setup + Foundational → Base pronta
2. US1 → Roadmap funcional basico (MVP!)
3. US2 → Loading async sem travamento
4. US3 → Visual profissional
5. US4 → Agrupamento Feature/Componente
6. US5 → Scroll e zoom
7. US6 → Tooltips
8. Cada story adiciona valor sem quebrar as anteriores

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica
- Apenas 2 arquivos fonte (roadmap_viewmodel.py, roadmap_dialog.py) + 2 arquivos de teste + main_window.py
- matplotlib NAO e thread-safe — todo rendering no main thread
- Usar draw_idle() para performance
- Commit apos cada task ou grupo logico
- Parar em qualquer checkpoint para validar story independentemente
