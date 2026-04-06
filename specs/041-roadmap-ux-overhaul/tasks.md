# Tasks: Roadmap UX Overhaul

**Input**: Design documents from `/specs/041-roadmap-ux-overhaul/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/ui-contracts.md, quickstart.md

**Tests**: Incluidos conforme requisito da constitution (XIV: ViewModel 80%+, View 50%+).

**Organization**: Tasks agrupadas por user story para implementacao e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story a que pertence (US1..US9)
- Caminhos exatos incluidos em cada task

---

## Phase 1: Setup

**Purpose**: Preparar estruturas de dados e remover codigo obsoleto

- [x] T001 Remover enum RoadmapGroupMode e referencias em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T002 Adicionar dataclass RoadmapFilters com metodos is_active e matches em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T003 Modificar dataclass RoadmapGroup: adicionar campo expanded=False, properties completion_percent, has_scheduled_stories, min_date, max_date e status_counts em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T004 Modificar dataclass RoadmapData: adicionar property status_counts agregada em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T005 Adicionar constantes STATUS_PROGRESS e layout (SUMMARY_BAR_HEIGHT, GROUP_SPACING, MIN_LABEL_HEIGHT_PX) em src/backlog_manager/presentation/views/roadmap_dialog.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Logica core do ViewModel que DEVE estar completa antes das user stories

**CRITICAL**: Nenhuma user story pode comecar sem esta fase completa

- [x] T006 Refatorar load_data() para agrupar historias por wave (fixo) em vez de feature/component, retornando grupos colapsados por padrao em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T007 Implementar metodo toggle_group(group_name) que alterna expanded e retorna RoadmapData atualizado em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T008 Implementar metodo apply_filters(filters: RoadmapFilters) que filtra cache e reconstroi grupos em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T009 Implementar metodo clear_filters() que reseta filtros e retorna dados completos em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T010 Implementar metodo get_available_filters() retornando dict com waves, statuses, developers e components unicos em src/backlog_manager/presentation/viewmodels/roadmap_viewmodel.py
- [x] T011 Escrever testes para RoadmapFilters (is_active, matches com todos os criterios, logica AND) em tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py
- [x] T012 Escrever testes para RoadmapGroup properties (completion_percent, min_date, max_date, status_counts) em tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py
- [x] T013 Escrever testes para load_data() com agrupamento por wave em tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py
- [x] T014 Escrever testes para toggle_group(), apply_filters(), clear_filters() e get_available_filters() em tests/unit/presentation/viewmodels/test_roadmap_viewmodel.py

**Checkpoint**: ViewModel completo com agrupamento por wave, filtragem e colapso. Todos os testes passando.

---

## Phase 3: User Story 1 - Identificacao Visual por Status (Priority: P1) MVP

**Goal**: Barras coloridas por status com legenda e destaque IMPEDIDO

**Independent Test**: Abrir roadmap com historias em diferentes status e verificar cores, legenda e destaque IMPEDIDO.

### Tests for User Story 1

- [x] T015 [P] [US1] Escrever teste que verifica renderizacao de barras com cores do STATUS_PALETTE por status em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T016 [P] [US1] Escrever teste que verifica presenca da legenda de cores na figura matplotlib em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T017 [P] [US1] Escrever teste que verifica destaque visual adicional para historias com status IMPEDIDO em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 1

- [x] T018 [US1] Refatorar _render_chart() para usar STATUS_PALETTE na cor de fundo de cada barra baseado no status da historia em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T019 [US1] Adicionar legenda matplotlib (ax.legend) com patches coloridos para cada status em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T020 [US1] Implementar destaque visual adicional (borda diferenciada) para historias com status IMPEDIDO em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Roadmap exibe barras coloridas por status, legenda visivel e IMPEDIDO destacado.

---

## Phase 4: User Story 2 - Colapso e Expansao de Grupos (Priority: P1)

**Goal**: Grupos (waves) colapsados por padrao com barra-resumo; click para expandir/colapsar

**Independent Test**: Abrir roadmap, verificar grupos colapsados com barra-resumo e percentual, expandir/colapsar individualmente.

### Tests for User Story 2

- [x] T021 [P] [US2] Escrever teste que verifica renderizacao de barra-resumo para grupo colapsado com percentual e intervalo de datas em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T022 [P] [US2] Escrever teste que verifica renderizacao de historias individuais para grupo expandido em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T023 [P] [US2] Escrever teste que verifica deteccao de click em regiao de grupo e chamada a toggle_group em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 2

- [x] T024 [US2] Refatorar _render_chart() para renderizar barra-resumo (SUMMARY_BAR_HEIGHT) com texto "{nome} - {N}% [{total} historias]" para grupos colapsados em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T025 [US2] Implementar renderizacao de historias individuais com header de grupo para grupos expandidos em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T026 [US2] Implementar _group_click_regions e deteccao de click via button_press_event para toggle de grupo em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T027 [US2] Conectar _on_group_click ao ViewModel.toggle_group() e re-renderizar chart com dados atualizados em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Grupos colapsados por padrao, expandem/colapsam com click, barra-resumo com percentual visivel.

---

## Phase 5: User Story 3 - Linha de Referencia Temporal "Hoje" (Priority: P2)

**Goal**: Linha vertical tracejada indicando a data de hoje no roadmap

**Independent Test**: Abrir roadmap e verificar linha vertical tracejada na posicao da data atual.

### Tests for User Story 3

- [x] T028 [P] [US3] Escrever teste que verifica presenca de linha vertical tracejada na data atual quando dentro do intervalo em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T029 [P] [US3] Escrever teste que verifica ausencia de linha quando data atual fora do intervalo em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 3

- [x] T030 [US3] Implementar ou ajustar renderizacao da linha "hoje" como axvline tracejada em cor #991B1B, alpha=0.5, visivel no zoom padrao em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Linha "hoje" visivel sem scroll quando data atual esta no intervalo da timeline.

---

## Phase 6: User Story 4 - Correcao de Rotulos e Hierarquia Visual (Priority: P2)

**Goal**: Rotulos legiveis sem sobreposicao, hierarquia visual entre waves com separadores e indentacao

**Independent Test**: Expandir grupo com 20+ historias e verificar que nenhum rotulo se sobrepoe, todos com minimo 14px de altura.

### Tests for User Story 4

- [x] T031 [P] [US4] Escrever teste que verifica altura minima de labels (MIN_LABEL_HEIGHT_PX) em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T032 [P] [US4] Escrever teste que verifica auto-colapso de grupo quando rotulos nao cabem no espaco em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 4

- [x] T033 [US4] Configurar font size de labels (LABEL_FONT_SIZE) e group headers (GROUP_FONT_SIZE) garantindo minimo 14px de altura em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T034 [US4] Implementar resolucao de colisoes de rotulos e espacamento entre barras para evitar sobreposicao em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T035 [US4] Implementar separadores visuais e indentacao entre waves para hierarquia visual em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T036 [US4] Implementar auto-colapso de grupo quando rotulos nao cabem no espaco disponivel (FR-008) em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Rotulos legiveis, sem sobreposicao, hierarquia visual clara entre waves.

---

## Phase 7: User Story 5 - Filtragem e Busca (Priority: P2)

**Goal**: Filtros por wave/status/responsavel/componente na toolbar + campo de busca por nome

**Independent Test**: Aplicar cada filtro individualmente e combinados, verificar que apenas historias correspondentes sao exibidas.

### Tests for User Story 5

- [x] T037 [P] [US5] Escrever teste que verifica que ComboBoxes de filtro sao populados com opcoes do get_available_filters() em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T038 [P] [US5] Escrever teste que verifica que alteracao de filtro chama apply_filters e re-renderiza em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T039 [P] [US5] Escrever teste que verifica indicacao visual de filtro ativo (borda colorida) em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T040 [P] [US5] Escrever teste que verifica que botao limpar filtros chama clear_filters em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 5

- [x] T041 [US5] Substituir ComboBox de agrupamento por 4 QComboBox de filtro (wave, status, developer, component) na toolbar em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T042 [US5] Adicionar QLineEdit de busca com placeholder "Buscar historia..." na toolbar em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T043 [US5] Adicionar QPushButton "Limpar filtros" com icone na toolbar em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T044 [US5] Implementar _on_filter_changed() que constroi RoadmapFilters e chama ViewModel.apply_filters() em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T045 [US5] Implementar _on_search_changed() que constroi RoadmapFilters com search_text e chama apply_filters em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T046 [US5] Implementar _on_clear_filters() que reseta ComboBoxes/busca e chama ViewModel.clear_filters() em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T047 [US5] Implementar indicacao visual de filtros ativos (borda colorida #0066CC nos ComboBoxes/QLineEdit) em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T048 [US5] Popular ComboBoxes com opcoes do get_available_filters() apos load_data em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T049 [US5] Exibir mensagem "Nenhuma historia encontrada" quando filtros nao retornam resultados em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Filtros e busca funcionais, indicacao visual de filtros ativos, limpar filtros reseta tudo.

---

## Phase 8: User Story 6 - Tooltip Enriquecido e Dependencias (Priority: P3)

**Goal**: Tooltip detalhado com todos os campos + setas de dependencias no hover

**Independent Test**: Hover sobre historia com dependencias, verificar tooltip completo e setas conectando dependencias.

### Tests for User Story 6

- [x] T050 [P] [US6] Escrever teste que verifica conteudo do tooltip enriquecido (nome, status, responsavel, story points, datas, duracao dias uteis, componente, dependencias) em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T051 [P] [US6] Escrever teste que verifica criacao de setas de dependencias no hover e remocao ao sair em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 6

- [x] T052 [US6] Refatorar _build_tooltip_text() para incluir todos os campos: nome, status, responsavel, story points, datas, duracao em dias uteis, componente e dependencias em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T053 [US6] Implementar calculo de dias uteis entre start_date e end_date no tooltip em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T054 [US6] Implementar renderizacao de setas de dependencias (FancyArrowPatch, arc3,rad=0.1) como overlay temporario no hover em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T055 [US6] Implementar remocao de setas de dependencias ao sair do hover e tratamento de dependencias para historias ocultas (seta tracejada) em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Tooltip enriquecido com todos os campos, setas de dependencias no hover.

---

## Phase 9: User Story 7 - Toolbar com Icones e Rodape Estatistico (Priority: P3)

**Goal**: Todos os botoes com icone + tooltip; rodape com contagem por status

**Independent Test**: Inspecionar cada botao da toolbar (icone + tooltip), verificar rodape com contagem por status.

### Tests for User Story 7

- [x] T056 [P] [US7] Escrever teste que verifica que todos os botoes da toolbar possuem icone e tooltip em tests/unit/presentation/views/test_roadmap_dialog.py
- [x] T057 [P] [US7] Escrever teste que verifica formato do rodape com contagem por status em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 7

- [x] T058 [US7] Adicionar icones (QStyle.StandardPixmap) e tooltips descritivos a todos os botoes da toolbar (zoom+, zoom-, limpar filtros) em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T059 [US7] Refatorar rodape (status bar) para exibir contagem por status no formato "BACKLOG: N | EXECUCAO: N | TESTES: N | CONCLUIDO: N | IMPEDIDO: N | Total: N" usando RoadmapData.status_counts em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T060 [US7] Garantir que rodape reflete filtros ativos (contagem apenas das historias visiveis) em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: 100% dos botoes com icone e tooltip, rodape com contagem por status refletindo filtros.

---

## Phase 10: User Story 8 - Progresso Visual nas Barras (Priority: P3)

**Goal**: Barras com preenchimento parcial baseado no status (0/33/66/100%)

**Independent Test**: Verificar que historias em cada status exibem preenchimento correto dentro da barra.

### Tests for User Story 8

- [x] T061 [P] [US8] Escrever teste que verifica renderizacao de duas camadas de barra (fundo alpha reduzido + preenchimento parcial) por status em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 8

- [x] T062 [US8] Implementar renderizacao de barras em duas camadas: barra completa (alpha reduzido) + barra parcial (alpha total) conforme STATUS_PROGRESS em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Barras exibem preenchimento parcial correto por status.

---

## Phase 11: User Story 9 - Scroll Sincronizado (Priority: P3)

**Goal**: Scroll entre painel de labels e area de barras sincronizado

**Independent Test**: Expandir grupos, scroll vertical, verificar alinhamento labels/barras.

### Tests for User Story 9

- [x] T063 [P] [US9] Escrever teste que verifica que labels e barras compartilham mesmo axes (sincronizacao nativa) em tests/unit/presentation/views/test_roadmap_dialog.py

### Implementation for User Story 9

- [x] T064 [US9] Verificar e garantir que labels (ytick labels) e barras usam mesmo axes matplotlib para sincronizacao nativa de scroll em src/backlog_manager/presentation/views/roadmap_dialog.py

**Checkpoint**: Labels e barras permanecem alinhados durante scroll vertical.

---

## Phase 12: Polish & Cross-Cutting Concerns

**Purpose**: Melhorias que afetam multiplas user stories

- [x] T065 [P] Garantir tratamento de edge cases: grupo sem historias (0%, ponto unico), historias sem datas (indicacao "sem datas"), busca sem resultados em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T066 [P] Garantir tratamento de edge case: historias sem responsavel ("Sem responsavel" no tooltip, opcao "Nao atribuido" no filtro) em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T067 Validar performance: renderizacao de 200+ historias com todos os grupos expandidos em <3s em src/backlog_manager/presentation/views/roadmap_dialog.py
- [x] T068 Executar validacao do quickstart.md — rodar testes e verificar cobertura (ViewModel 80%+, View 50%+)
- [x] T069 Executar formatacao (black, isort) e type checking (mypy) em todos os arquivos modificados

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — pode iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup — BLOQUEIA todas as user stories
- **US1 (Phase 3)**: Depende de Foundational — sem dependencia de outras stories
- **US2 (Phase 4)**: Depende de Foundational — sem dependencia de outras stories
- **US3 (Phase 5)**: Depende de Foundational — sem dependencia de outras stories
- **US4 (Phase 6)**: Depende de Foundational — beneficia-se de US1+US2 (barras coloridas + colapso)
- **US5 (Phase 7)**: Depende de Foundational — sem dependencia de outras stories
- **US6 (Phase 8)**: Depende de Foundational — sem dependencia de outras stories
- **US7 (Phase 9)**: Depende de US5 (toolbar ja com filtros) — rodape independente
- **US8 (Phase 10)**: Depende de US1 (barras coloridas como base)
- **US9 (Phase 11)**: Depende de Foundational — sem dependencia de outras stories
- **Polish (Phase 12)**: Depende de todas as user stories desejadas

### User Story Dependencies

- **US1 (P1)**: Independente — pode iniciar apos Foundational
- **US2 (P1)**: Independente — pode iniciar apos Foundational
- **US3 (P2)**: Independente — pode iniciar apos Foundational
- **US4 (P2)**: Parcialmente dependente — beneficia-se de US1+US2 para testes visuais completos
- **US5 (P2)**: Independente — pode iniciar apos Foundational
- **US6 (P3)**: Independente — pode iniciar apos Foundational
- **US7 (P3)**: Parcialmente dependente de US5 (toolbar com filtros)
- **US8 (P3)**: Dependente de US1 (barras coloridas como base para preenchimento parcial)
- **US9 (P3)**: Independente — validacao da arquitetura existente

### Within Each User Story

- Testes escritos ANTES da implementacao
- Implementacao segue: rendering base → interacao → integracao
- Story completa antes de avancar para proxima prioridade

### Parallel Opportunities

- T002, T003, T004 podem rodar em paralelo (dataclasses diferentes no mesmo arquivo, mas secoes distintas)
- T011, T012 podem rodar em paralelo (testes diferentes)
- T015, T016, T017 podem rodar em paralelo (testes US1)
- T021, T022, T023 podem rodar em paralelo (testes US2)
- T028, T029 podem rodar em paralelo (testes US3)
- T031, T032 podem rodar em paralelo (testes US4)
- T037, T038, T039, T040 podem rodar em paralelo (testes US5)
- T050, T051 podem rodar em paralelo (testes US6)
- T056, T057 podem rodar em paralelo (testes US7)
- US1 e US2 podem ser implementadas em paralelo (P1 stories independentes)
- US3, US4, US5 podem ser implementadas em paralelo (P2 stories, com ressalva para US4)
- T065, T066 podem rodar em paralelo (edge cases diferentes)

---

## Parallel Example: User Story 1

```bash
# Launch all tests for US1 together:
Task: "Teste renderizacao barras com cores STATUS_PALETTE" (T015)
Task: "Teste presenca legenda de cores" (T016)
Task: "Teste destaque visual IMPEDIDO" (T017)

# Then implementation sequentially:
Task: "Refatorar _render_chart com STATUS_PALETTE" (T018)
Task: "Adicionar legenda matplotlib" (T019)
Task: "Destaque visual IMPEDIDO" (T020)
```

## Parallel Example: User Story 5

```bash
# Launch all tests for US5 together:
Task: "Teste ComboBoxes populados" (T037)
Task: "Teste filtro chama apply_filters" (T038)
Task: "Teste indicacao visual filtro ativo" (T039)
Task: "Teste botao limpar filtros" (T040)

# Then implementation sequentially:
Task: "Substituir ComboBox por filtros" (T041)
Task: "Adicionar QLineEdit busca" (T042)
Task: "Adicionar botao limpar filtros" (T043)
Task: "Implementar _on_filter_changed" (T044)
...
```

---

## Implementation Strategy

### MVP First (User Stories 1 + 2)

1. Complete Phase 1: Setup (T001-T005)
2. Complete Phase 2: Foundational (T006-T014)
3. Complete Phase 3: US1 - Cores por status (T015-T020)
4. Complete Phase 4: US2 - Colapso/Expansao (T021-T027)
5. **STOP and VALIDATE**: Roadmap funcional com cores e colapso
6. Deploy/demo se pronto

### Incremental Delivery

1. Setup + Foundational → Base pronta
2. US1 (cores) → Testar independente → MVP visual
3. US2 (colapso) → Testar independente → MVP navegacional
4. US3 (linha hoje) + US4 (rotulos) + US5 (filtros) → P2 completo
5. US6 (tooltip) + US7 (toolbar) + US8 (progresso) + US9 (scroll) → P3 completo
6. Polish → Validacao final

---

## Notes

- [P] tasks = arquivos diferentes, sem dependencias
- [Story] label mapeia task a user story especifica
- Cada user story e independentemente completavel e testavel
- Testes devem falhar antes da implementacao
- Commit apos cada task ou grupo logico
- Pare em qualquer checkpoint para validar story independente
- Todos os 4 arquivos modificados: roadmap_viewmodel.py, roadmap_dialog.py + seus testes
