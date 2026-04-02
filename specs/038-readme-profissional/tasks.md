# Tasks: README Profissional do Projeto

**Input**: Design documents from `/specs/038-readme-profissional/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, quickstart.md ✅

**Tests**: Não solicitados — feature puramente documental. Validação manual via renderização no GitHub.

**Organization**: Tasks agrupadas por user story para permitir implementação e validação independentes.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Pode rodar em paralelo (arquivos diferentes, sem dependências)
- **[Story]**: User story associada (US1, US2, US3)
- Paths absolutos a partir da raiz do repositório

## Path Conventions

```text
README.md                    # Artefato principal (reescrita completa)
docs/images/screenshot.png   # Screenshot da interface (captura manual)
```

---

## Phase 1: Setup (Preparação)

**Purpose**: Levantar informações do projeto e preparar estrutura de diretórios

- [x] T001 Criar diretório `docs/images/` na raiz do repositório (se não existir)
- [x] T002 [P] Coletar informações do `pyproject.toml`: nome do pacote, versão Python, dependências principais, comando de execução (`[tool.poetry.scripts]`), licença
- [x] T003 [P] Coletar informações da `constitution.md`: diagrama de camadas (Domain, Application, Infrastructure, Presentation), princípios arquiteturais

**Checkpoint**: Informações coletadas, diretório de imagens criado

---

## Phase 2: Foundational (Seções Base do README)

**Purpose**: Criar a estrutura do README.md com as seções que são pré-requisito para todas as user stories

**⚠️ CRITICAL**: O README.md será reescrito por completo. Todas as seções serão criadas nesta fase e refinadas nas fases seguintes.

- [x] T004 Escrever seção de **Badges** no topo de `README.md` — manter os 10 badges existentes (CI, Codecov, SonarCloud Quality Gate/Maintainability/Reliability/Security, PyPI version/downloads/Python versions, License) organizados visualmente em linhas por categoria
- [x] T005 Escrever **Título** e **descrição curta** (1 linha) do projeto logo após os badges em `README.md`
- [x] T006 Escrever **Índice (TOC)** com âncoras para todas as seções do `README.md` conforme estrutura definida em `data-model.md`

**Checkpoint**: README.md criado com badges, título e índice navegável

---

## Phase 3: User Story 1 — Visitante Entende o Projeto (Priority: P1) 🎯 MVP

**Goal**: Um visitante que abre o repositório pela primeira vez consegue entender em até 30 segundos o que o projeto faz, para quem é destinado, qual problema resolve e sua filosofia arquitetural.

**Independent Test**: Apresentar o README a um desenvolvedor que nunca viu o projeto e verificar se ele consegue explicar o propósito em menos de 1 minuto.

### Implementation for User Story 1

- [x] T007 [P] [US1] Escrever seção **Sobre o Projeto** (introdução 1-2 parágrafos) em `README.md` — explicar o que é o Zion Backlog Manager, para quem é destinado e qual problema resolve (FR-003)
- [x] T008 [P] [US1] Escrever seção **Conceito e Filosofia** em `README.md` — explicar Clean Architecture, async-first, injeção de dependências, type safety e motivação por trás das decisões técnicas (FR-004)
- [x] T009 [P] [US1] Escrever seção **Funcionalidades** em `README.md` — listar capacidades principais: gestão de backlog, alocação automática de desenvolvedores, planejamento de sprints, gestão de dependências, integração Excel, design system (FR-005)
- [x] T010 [P] [US1] Escrever seção **Aplicabilidade** em `README.md` — descrever cenários de uso reais: equipes ágeis, gestores de projeto, squads de desenvolvimento (FR-006)
- [x] T011 [P] [US1] Escrever seção **Screenshot** em `README.md` — placeholder referenciando `docs/images/screenshot.png` com tag de imagem markdown (FR-015). Nota: captura manual será feita separadamente (R-004)

**Checkpoint**: Visitante consegue entender o projeto lendo apenas as seções acima

---

## Phase 4: User Story 2 — Usuário Instala e Executa o Projeto (Priority: P2)

**Goal**: Um desenvolvedor consegue instalar e executar o Zion Backlog Manager seguindo apenas as instruções do README, sem consultar outros arquivos, em menos de 10 minutos.

**Independent Test**: Seguir as instruções do README em uma máquina limpa com Python 3.13+ e verificar que a aplicação inicia corretamente.

### Implementation for User Story 2

- [x] T012 [P] [US2] Escrever seção **Instalação** em `README.md` com dois caminhos: (1) Via pip (`pip install zion-backlog-manager`) para usuário final; (2) Via código-fonte com Poetry (`git clone`, `poetry install`, `poetry run`) para desenvolvedor. Incluir pré-requisitos: Python >=3.13,<3.15 (FR-007, R-006, R-007)
- [x] T013 [P] [US2] Escrever seção **Uso** em `README.md` — comando para iniciar a aplicação (`zion-backlog-manager`), primeiros passos após instalação (FR-008)
- [x] T014 [US2] Escrever seção **Solução de Problemas** em `README.md` — orientações para erros mais comuns: versão Python incompatível, dependências faltantes, problemas com PySide6/Qt

**Checkpoint**: Usuário consegue instalar e executar seguindo apenas o README

---

## Phase 5: User Story 3 — Desenvolvedor Avalia Qualidade e Segurança (Priority: P3)

**Goal**: Um líder técnico ou arquiteto consegue avaliar a maturidade do projeto (coverage, quality gate, CI, arquitetura) sem precisar navegar além do README.

**Independent Test**: Verificar se um avaliador técnico consegue identificar todos os indicadores de qualidade sem sair do README.

### Implementation for User Story 3

- [x] T015 [P] [US3] Escrever seção **Stack Tecnológica** em `README.md` — listar tecnologias principais e suas funções: PySide6 (UI), aiosqlite (persistência), Pydantic (DTOs), qasync (async/Qt), Poetry (build), pytest (testes) (FR-014)
- [x] T016 [P] [US3] Escrever seção **Arquitetura** em `README.md` — diagrama ASCII box-drawing com 4 camadas (Presentation → Infrastructure → Application → Domain) e tecnologias associadas, baseado na constitution.md (FR-009, FR-016, R-003)
- [x] T017 [P] [US3] Escrever seção **Contribuição** em `README.md` — link para `CONTRIBUTING.md`, diretrizes gerais do projeto (FR-010)
- [x] T018 [US3] Escrever seção **Licença** em `README.md` — informar licença MIT conforme pyproject.toml, notar que arquivo LICENSE será criado em issue separada (FR-011, R-005)

**Checkpoint**: Avaliador técnico encontra todos os indicadores de qualidade no README

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Validação final, ajustes de formatação e consistência

- [x] T019 Revisar TOC (T006) e adicionar âncoras para todas as seções criadas em `README.md` — garantir que todos os links internos funcionam (SC-006)
- [x] T020 [P] Revisar consistência de emojis nos títulos de seção em `README.md` — garantir padrão visual uniforme (FR-001)
- [x] T021 [P] Validar que todos os 10 badges renderizam corretamente e apontam para os serviços correspondentes em `README.md` (SC-002)
- [ ] T022 Validar renderização completa do `README.md` no GitHub — push para branch e verificar visualmente (quickstart.md passo 2-4)
- [x] T023 Executar validação do `quickstart.md` — verificar todos os critérios de aceitação

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Sem dependências — pode iniciar imediatamente
- **Foundational (Phase 2)**: Depende de Setup (T002, T003 fornecem informações para o conteúdo)
- **User Story 1 (Phase 3)**: Depende de Phase 2 (README.md deve existir com badges/título/TOC)
- **User Story 2 (Phase 4)**: Depende de Phase 2 — independente de US1
- **User Story 3 (Phase 5)**: Depende de Phase 2 — independente de US1 e US2
- **Polish (Phase 6)**: Depende de todas as user stories completas

### User Story Dependencies

- **User Story 1 (P1)**: Independente — seções de entendimento do projeto
- **User Story 2 (P2)**: Independente — seções de instalação e uso
- **User Story 3 (P3)**: Independente — seções de qualidade e arquitetura

### Within Each User Story

- Todas as seções marcadas [P] podem ser escritas em paralelo (são seções independentes do README)
- Seções sem [P] dependem de contexto das anteriores

### Parallel Opportunities

- T002 e T003 (coleta de informações) podem rodar em paralelo
- T007, T008, T009, T010, T011 (todas as seções da US1) podem rodar em paralelo
- T012, T013 (instalação e uso) podem rodar em paralelo
- T015, T016, T017 (stack, arquitetura, contribuição) podem rodar em paralelo
- T020, T021 (revisões) podem rodar em paralelo
- **User Stories 1, 2 e 3 podem ser implementadas em paralelo** após Phase 2

---

## Parallel Example: User Story 1

```bash
# Todas as seções da US1 podem ser escritas em paralelo (seções independentes):
Task: "Escrever seção Sobre o Projeto em README.md" (T007)
Task: "Escrever seção Conceito e Filosofia em README.md" (T008)
Task: "Escrever seção Funcionalidades em README.md" (T009)
Task: "Escrever seção Aplicabilidade em README.md" (T010)
Task: "Escrever seção Screenshot em README.md" (T011)
```

## Parallel Example: User Story 3

```bash
# Seções de avaliação técnica podem ser escritas em paralelo:
Task: "Escrever seção Stack Tecnológica em README.md" (T015)
Task: "Escrever seção Arquitetura em README.md" (T016)
Task: "Escrever seção Contribuição em README.md" (T017)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T003)
2. Complete Phase 2: Foundational (T004-T006) — README com badges, título e TOC
3. Complete Phase 3: User Story 1 (T007-T011) — seções de entendimento
4. **STOP and VALIDATE**: Visitante consegue entender o projeto?
5. Push para branch e verificar renderização

### Incremental Delivery

1. Setup + Foundational → README com estrutura base
2. Add US1 → Visitante entende o projeto → Validar (MVP!)
3. Add US2 → Usuário instala e executa → Validar
4. Add US3 → Avaliador técnico encontra indicadores → Validar
5. Polish → Revisão final e validação completa
6. Cada incremento agrega valor sem quebrar os anteriores

### Single Developer Strategy (Recomendado)

Como feature puramente documental com 1 arquivo principal:

1. Escrever README.md completo de uma vez (Phases 1-5 sequencialmente)
2. Revisar e validar (Phase 6)
3. Total estimado: 23 tasks, todas no mesmo arquivo `README.md`

---

## Notes

- Feature puramente documental — sem código, sem testes automatizados
- Todas as tasks modificam o mesmo arquivo (`README.md`), mas seções são independentes
- Screenshot (`docs/images/screenshot.png`) requer captura manual em ambiente gráfico — placeholder será usado
- Arquivo LICENSE não será criado nesta feature (R-005) — escopo separado
- Conteúdo 100% em português brasileiro (FR-001)
- Validação final requer push para branch e verificação visual no GitHub
