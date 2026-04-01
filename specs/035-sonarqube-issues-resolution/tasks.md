# Tasks: Resolucao de Issues SonarQube para Quality Gate

**Input**: Design documents from `/specs/035-sonarqube-issues-resolution/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: Nao solicitados. Apenas garantir que testes existentes continuam passando.

**Organization**: Tasks agrupadas por user story para implementacao e teste independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependencias)
- **[Story]**: User story associada (US1, US2, US3)
- Caminhos exatos incluidos nas descricoes

---

## Phase 1: Setup

**Purpose**: Nenhuma inicializacao de projeto necessaria — codebase existente, sem novos arquivos de configuracao.

- [ ] T001 Verificar estado atual do branch `035-sonarqube-issues-resolution` e garantir que esta atualizado com `001-ep001-foundation-persistence`

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Validar que o ambiente esta funcional antes de qualquer modificacao.

- [ ] T002 Executar `poetry run pytest tests/ -v` para confirmar que todos os testes passam no estado atual (baseline)

**Checkpoint**: Baseline de testes confirmada — implementacao pode comecar.

---

## Phase 3: User Story 1 - Resolver Issue Critica de Complexidade Cognitiva (Priority: P1) MVP

**Goal**: Reduzir a complexidade cognitiva de `_generate_inter_wave_deps()` de 16 para <=15 extraindo funcao auxiliar `_try_create_inter_wave_dep()`.

**Independent Test**: Executar `poetry run pytest tests/ -v` — todos os testes devem passar. Apos re-analiskk/e no SonarQube, issue S3776 (key: `AZ1H3y5IMsoPwz0FZVip`) nao deve mais aparecer.

### Implementation for User Story 1

- [ ] T003 [US1] Criar funcao auxiliar `_try_create_inter_wave_dep(story_id, earlier_waves, dependencies, story_dep_count) -> bool` imediatamente antes de `_generate_inter_wave_deps()` em `scripts/seed_test_backlog.py` — deve encapsular a logica do inner loop (check de `earlier_waves`, `random.random() < 0.3`, `random.choice()`, e chamada a `_try_add_dependency()`), com type hints completos e docstring
- [ ] T004 [US1] Refatorar `_generate_inter_wave_deps()` em `scripts/seed_test_backlog.py` para chamar `_try_create_inter_wave_dep()` no lugar do bloco inline, reduzindo complexidade cognitiva de 16 para ~11
- [ ] T005 [US1] Executar `poetry run pytest tests/ -v` para validar que todos os testes passam apos a refatoracao

**Checkpoint**: User Story 1 completa — funcao refatorada, comportamento preservado, testes passando.

---

## Phase 4: User Story 2 - Revisar Security Hotspot de Gerador Pseudoaleatorio (Priority: P1)

**Goal**: Marcar o security hotspot S2245 (key: `AZ1I5XNA3OXD0TCP-O9_`) como SAFE no SonarQube para que `new_security_hotspots_reviewed` atinja 100% e o quality gate passe.

**Independent Test**: Verificar no SonarQube que o hotspot mudou para status REVIEWED com resolucao SAFE e que a metrica `new_security_hotspots_reviewed` subiu para 100%.

### Implementation for User Story 2

- [ ] T006 [US2] Marcar security hotspot `AZ1I5XNA3OXD0TCP-O9_` como SAFE no SonarQube via MCP tool `change_security_hotspot_status` com justificativa: "Uso de random.choice() em script de geracao de dados de teste com seed fixo (random.seed(RANDOM_SEED)). Nao ha contexto criptografico ou de seguranca. Mesmo tipo de hotspot (S2245) ja revisado e marcado SAFE em 7 outras ocorrencias no mesmo arquivo."
- [ ] T007 [US2] Verificar via MCP tool `search_security_hotspots` que nao ha mais hotspots TO_REVIEW no projeto

**Checkpoint**: User Story 2 completa — hotspot revisado, metrica de security hotspots deve atingir 100%.

---

## Phase 5: User Story 3 - Tratar Issues de Convencao de Nomes em Mocks Qt (Priority: P2)

**Goal**: Marcar as 11 issues MINOR de naming convention (S100/S116) em `tests/headless_mocks.py` como ACCEPTED no SonarQube.

**Independent Test**: Verificar no SonarQube que as 11 issues mudaram de OPEN para ACCEPTED e que o total de issues abertas caiu para 0 (apos correcao de S3776 via US1).

### Implementation for User Story 3

- [ ] T008 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQEw` (beginResetModel) como ACCEPTED via MCP tool `change_sonar_issue_status` com justificativa: "Metodo camelCase obrigatorio para compatibilidade com API Qt/PySide6. Mock deve replicar interface do framework."
- [ ] T009 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQEx` (endResetModel) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T010 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQEz` (beginInsertRows) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T011 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQE1` (endInsertRows) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T012 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQE3` (beginRemoveRows) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T013 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQE5` (endRemoveRows) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T014 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQE8` (beginGroup) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T015 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQE9` (endGroup) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T016 [P] [US3] Marcar issue S100 `AZ1HXJJBhkGAnEFrWQE-` (setValue) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T017 [P] [US3] Marcar issue S116 `AZ1HXJJBhkGAnEFrWQFA` (IniFormat) como ACCEPTED via MCP tool `change_sonar_issue_status` com justificativa: "Campo PascalCase obrigatorio para compatibilidade com enum Qt/PySide6. Mock deve replicar interface do framework."
- [ ] T018 [P] [US3] Marcar issue S116 `AZ1HXJJBhkGAnEFrWQFB` (UserScope) como ACCEPTED via MCP tool `change_sonar_issue_status` com mesma justificativa
- [ ] T019 [US3] Verificar via MCP tool `search_sonar_issues_in_projects` que nao ha mais issues OPEN no projeto

**Checkpoint**: User Story 3 completa — todas as 11 issues de naming convention tratadas.

---

## Phase 6: Polish & Verificacao Final

**Purpose**: Validacao cruzada de que todas as acoes atingiram o resultado esperado.

- [ ] T020 Executar `poetry run pytest tests/ -v` para confirmar que todos os testes continuam passando
- [ ] T021 Verificar via MCP tool `get_project_quality_gate_status` que o quality gate esta OK
- [ ] T022 Verificar via MCP tool `search_sonar_issues_in_projects(issueStatuses=["OPEN"])` que ha 0 issues abertas
- [ ] T023 Verificar via MCP tool `search_security_hotspots(status=["TO_REVIEW"])` que ha 0 hotspots pendentes

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependencias — pode comecar imediatamente
- **Foundational (Phase 2)**: Depende de Phase 1 — BLOQUEIA user stories
- **US1 (Phase 3)**: Depende de Phase 2 — unica story com alteracao de codigo
- **US2 (Phase 4)**: Depende de Phase 2 — pode rodar em paralelo com US1 e US3 (apenas API)
- **US3 (Phase 5)**: Depende de Phase 2 — pode rodar em paralelo com US1 e US2 (apenas API)
- **Polish (Phase 6)**: Depende de US1, US2, e US3 estarem completas

### User Story Dependencies

- **US1 (P1)**: Independente — alteracao de codigo em `scripts/seed_test_backlog.py`
- **US2 (P1)**: Independente — acao via API SonarQube (hotspot)
- **US3 (P2)**: Independente — acoes via API SonarQube (11 issues)

### Within Each User Story

- US1: T003 → T004 → T005 (sequencial — criar funcao, refatorar chamador, testar)
- US2: T006 → T007 (sequencial — marcar, verificar)
- US3: T008-T018 em paralelo [P] → T019 (verificacao apos todas marcacoes)

### Parallel Opportunities

- US1, US2, e US3 podem rodar em paralelo apos Phase 2
- Dentro de US3, todas as 11 marcacoes de issues (T008-T018) podem rodar em paralelo
- T020-T023 (verificacao final) podem rodar em paralelo entre si

---

## Parallel Example: User Story 3

```bash
# Todas as marcacoes de issues podem rodar em paralelo:
Task T008: "Marcar issue beginResetModel como ACCEPTED"
Task T009: "Marcar issue endResetModel como ACCEPTED"
Task T010: "Marcar issue beginInsertRows como ACCEPTED"
Task T011: "Marcar issue endInsertRows como ACCEPTED"
Task T012: "Marcar issue beginRemoveRows como ACCEPTED"
Task T013: "Marcar issue endRemoveRows como ACCEPTED"
Task T014: "Marcar issue beginGroup como ACCEPTED"
Task T015: "Marcar issue endGroup como ACCEPTED"
Task T016: "Marcar issue setValue como ACCEPTED"
Task T017: "Marcar issue IniFormat como ACCEPTED"
Task T018: "Marcar issue UserScope como ACCEPTED"

# Apos todas completarem:
Task T019: "Verificar 0 issues OPEN no projeto"
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2)

1. Complete Phase 1: Setup (verificar branch)
2. Complete Phase 2: Foundational (baseline de testes)
3. Complete Phase 3: US1 — refatorar complexidade cognitiva
4. Complete Phase 4: US2 — marcar hotspot como SAFE
5. **STOP and VALIDATE**: Quality gate deve passar (hotspot era a unica causa de falha)

### Incremental Delivery

1. Setup + Foundational → ambiente validado
2. US1 (refatoracao) → issue CRITICAL resolvida
3. US2 (hotspot SAFE) → quality gate passa (OK)
4. US3 (naming issues ACCEPTED) → painel limpo, 0 issues abertas
5. Verificacao final → confirmacao completa

### Parallel Strategy

Com capacidade paralela:
1. Completar Setup + Foundational juntos
2. Apos Foundational:
   - Stream A: US1 (codigo)
   - Stream B: US2 (hotspot API)
   - Stream C: US3 (issues API — 11 chamadas paralelas)
3. Verificacao final apos todos os streams

---

## Notes

- [P] tasks = arquivos/recursos diferentes, sem dependencias
- [Story] label mapeia task para user story especifica
- US2 e US3 nao envolvem alteracao de codigo — apenas acoes via API SonarQube (MCP tools)
- US1 e a unica story que modifica codigo (`scripts/seed_test_backlog.py`)
- Testes novos NAO foram solicitados — apenas garantir que existentes passam
