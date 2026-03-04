# Prompt: Criar Especificacao Tecnica do EP-010

<role>
Voce e um Engenheiro de Qualidade Senior especializado em testes de integracao e E2E,
com profundo conhecimento em:
- Estrategias de teste para sistemas desktop Python (pytest, pytest-qt, pytest-cov)
- Integracao de testes com Qt/PySide6 via pytest-qt e qasync
- Arquitetura de testes em Clean Architecture (testes unitarios vs integracao vs E2E)
- Cobertura de codigo e metricas de qualidade (RNF-MANT-001: >= 80%)
- Validacao de casos de uso completos (UC-001 a UC-005)
- Implementacao de cenarios de teste do SRS (CT-001 a CT-005)
- Deteccao e tratamento de regressoes em aplicacoes com GUI
- Correcao de bugs revelados por testes seguindo politica de criticidade

Voce produz especificacoes tecnicas de qualidade prescritivas, rastreaveis a requisitos,
que garantem integridade do sistema como um todo.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **UI**: PySide6 6.10.0+ com padrao MVVM (implementado em EP-008)
- **Async/Qt**: qasync para integracao asyncio <-> Qt event loop
- **Persistencia**: aiosqlite (async SQLite)
- **DTOs**: Pydantic ^2.0
- **Excel**: openpyxl (implementado em EP-009)
- **Testes**: pytest + pytest-cov + pytest-asyncio + pytest-qt
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD (entidades ricas, VOs, servicos de dominio), MVVM (na Presentation)

### Estado Atual do Codigo (Implementado em EP-001 a EP-009)

O produto atingiu **funcionalidade completa** apos EP-009. Todas as 7 capacidades do SRS estao implementadas:
1. **Gestao de Backlog**: EP-003 + EP-008
2. **Gestao de Features**: EP-004 + EP-008
3. **Gestao de Desenvolvedores**: EP-004 + EP-008
4. **Gestao de Dependencias**: EP-005 + EP-008
5. **Calculo de Cronograma**: EP-006 + EP-008
6. **Alocacao Automatica**: EP-007 + EP-008
7. **Integracao Excel**: EP-009

**Entidades de dominio implementadas:**
- `Story`, `Developer`, `Feature` (em `src/backlog_manager/domain/entities/`)
- Dependencias via tabela `Story_Dependency`

**Value Objects implementados:**
- `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `StoryStatus(StrEnum)` {BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO}
- `BRAZILIAN_HOLIDAYS_2026_2028` (frozenset[date])

**Domain Services implementados:**
- `StoryService` — geracao de IDs, prioridades
- `DeveloperService` — criacao de desenvolvedores
- `FeatureService` — criacao de features, validacao de wave
- `DependencyService` — build_graph(), would_create_cycle(), validate_wave_dependency()
- `SchedulingService` — calculate_duration(), topological_sort(), calculate_story_dates()
- `AllocationService` — allocate_stories(), processamento por ondas

**Excecoes implementadas:**
- `BacklogManagerException` (base)
- `CyclicDependencyException`, `InvalidWaveDependencyException`
- `DuplicateWaveException`, `FeatureHasStoriesException`
- `MaxIterationsExceeded`
- `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo`

**Repository Protocols implementados:**
- `StoryRepository`, `DeveloperRepository`, `FeatureRepository`, `StoryDependencyRepository`
- `UnitOfWork` com commit/rollback transacional

**Use Cases implementados (23+):**
- Story: CreateStory, EditStory, DeleteStory, DuplicateStory, ListStories, MovePriority, AssignDeveloper
- Developer: CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers
- Feature: CreateFeature, UpdateFeature, DeleteFeature, ListFeatures
- Dependency: AddDependency, RemoveDependency, GetDependencies, GetDependents
- Scheduling: CalculateDuration, CalculateStoryDates, CalculateSchedule
- Allocation: ExecuteAllocation
- Excel: ImportExcel, ExportExcel (EP-009)

**Camada de Presentation implementada (EP-008):**
- `MainWindow` com toolbar, menu, tabela de backlog
- Dialogos: StoryDialog, DeveloperDialog, FeatureDialog, DependencyPanel
- ViewModels: BacklogViewModel, AllocationViewModel, etc.
- Atalhos: Ctrl+N, Ctrl+E, Ctrl+I, Ctrl+D, etc.

**Infraestrutura de Testes existente (EP-001):**
- `tests/unit/` — testes unitarios rapidos, sem I/O
- `tests/integration/` — testes com SQLite real
- `conftest.py` com fixtures comuns (db_path, event_loop, etc.)
- pytest-qt configurado com qasync para testes de GUI

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Localizacao dos testes E2E**: A estrutura atual tem `tests/unit/` e `tests/integration/`. -> A spec deve decidir se (a) criar `tests/e2e/` como diretorio separado para testes E2E com GUI, (b) adicionar testes E2E em `tests/integration/` com marcador pytest `@pytest.mark.e2e`, ou (c) criar subpasta `tests/integration/e2e/`. Considerar que testes E2E sao mais lentos e podem precisar de xvfb em CI.

2. **Sincronizacao pytest-qt + qasync**: Constitution XIV diz "Testes de GUI DEVEM rodar sobre o loop qasync, aguardando corrotinas via `await` ou `qtbot.waitSignal`". -> A spec deve detalhar como combinar `qtbot` do pytest-qt com `qeventloop` do qasync para aguardar operacoes assincronas sem `time.sleep()`. Incluir exemplo de fixture.

3. **Fixtures compartilhadas vs. isoladas**: Testes E2E precisam de banco populado (historias, devs, features, dependencias). -> A spec deve decidir se (a) criar fixtures especificas para E2E com dados de teste padronizados, (b) usar factory functions para gerar dados dinamicamente, ou (c) carregar dados de arquivo Excel de teste via ImportExcel. Considerar reproducibilidade e isolamento entre testes.

4. **Cobertura de Views vs. ViewModels**: Constitution XIV diz "Views (UI visual) PODEM ter cobertura menor (minimo 50%), ViewModels DEVEM ter 80%". -> A spec deve detalhar como medir cobertura de UI (linhas executadas via pytest-qt) vs. cobertura de logica (ViewModels, Use Cases). Incluir configuracao de pytest-cov.

5. **Cenarios de teste CT do SRS**: O SRS define CT-001 a CT-005 com setups especificos. -> A spec deve mapear cada CT para testes automatizados, especificando: (a) como criar o setup programaticamente, (b) quais assercoes validam o resultado, (c) se o teste usa GUI ou apenas backend.

6. **Casos de uso UC via GUI**: UC-001 a UC-005 sao fluxos de usuario via interface. -> A spec deve decidir se testes E2E de UC (a) simulam cliques e inputs via qtbot, (b) chamam ViewModels diretamente (sem simular cliques), ou (c) combinam ambos. Considerar trade-off entre fidelidade e estabilidade.

7. **Tratamento de bugs revelados**: O epico define politica de criticidade (Simples, Media, Critica). -> A spec deve definir como bugs sao documentados durante execucao de testes: (a) issues criadas automaticamente, (b) comentarios em codigo, ou (c) lista de TODOs em arquivo separado. Considerar que bugs simples sao corrigidos no mesmo PR.

8. **Performance dos testes**: Testes E2E com GUI sao lentos. -> A spec deve definir: (a) timeout maximo por teste (ex: 30s), (b) estrategia de paralelizacao (pytest-xdist), (c) quando pular testes lentos (ex: em pre-commit hooks). Considerar meta de suite completa < 5 minutos.

9. **Testes de performance RNF-PERF**: Os RNFs definem metricas quantitativas (ex: alocacao <= 5s para 100 historias). -> A spec deve decidir se testes de performance ficam (a) juntos com E2E, (b) em diretorio separado `tests/performance/`, ou (c) como subconjunto opcional executado sob demanda. Incluir como medir tempo e memoria.

10. **CI/CD com display virtual**: Testes com GUI precisam de display. -> A spec deve definir configuracao de CI (GitHub Actions) com xvfb ou similar. Incluir exemplo de workflow.

11. **Estabilidade de testes de GUI (flakiness)**: Testes E2E com Qt podem ser flakey. -> A spec deve definir boas praticas para evitar instabilidade: (a) sempre usar qtbot.waitSignal, (b) evitar timeouts fixos, (c) garantir estado limpo entre testes. Incluir padroes de implementacao.

12. **Bugs criticos e refatoracao**: Se testes E2E revelarem bugs criticos que exigem refatoracao, podem impactar escopo/tempo. -> A spec deve definir procedimento: (a) criar branch separada para correcao, (b) registrar issue com causa raiz, (c) ajustar plano se necessario. Definir limites de atuacao dentro do escopo do epico.

13. **Validacao de cobertura final**: RNF-MANT-001 exige >= 80% de cobertura. -> A spec deve definir como validar a cobertura apos implementacao dos testes E2E: (a) comando pytest-cov com fail-under, (b) relatorio de cobertura por modulo, (c) acoes corretivas se meta nao atingida (adicionar testes unitarios).

14. **Roundtrip Excel como teste E2E**: UC-004 + RF-EXCEL valida import/export. -> A spec deve incluir teste E2E de roundtrip: export todos os dados, limpar banco, reimportar, validar igualdade. Especificar como comparar dados antes/depois.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-010_testes-de-integracao-e2e.md` — requisitos, escopo, criterios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — secoes:
   - §2.2 (7 capacidades do produto)
   - §5 UC-001 a UC-005 (casos de uso completos)
   - §7.1 CT-001 a CT-005 (cenarios de teste praticos)
   - §7.2 Catalogo de Excecoes
   - §7.4 Matriz de Rastreabilidade
   - §4.1 RNF-PERF (metricas de performance)
   - §4.3 RNF-CONF (confiabilidade)
   - §4.5 RNF-MANT-001 (cobertura de testes)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios:
   - §XIV Estrategia de Testes (cobertura alvo por modulo, pytest-qt + qasync)
   - §XXI CI/CD e Qualidade Continua (gates de qualidade)
4. **Spec de referencia (predecessor)**: `specs/009-ep009-excel-integration/spec.md` — formato e nivel de detalhe esperado
5. **Estrutura de testes existente**: `tests/conftest.py`, `tests/unit/`, `tests/integration/` — fixtures e padroes atuais
6. **Domain Services**: `src/backlog_manager/domain/services/` — para entender logica a ser testada
7. **Use Cases**: `src/backlog_manager/application/use_cases/` — para mapear testes a fluxos
8. **ViewModels**: `src/backlog_manager/presentation/viewmodels/` — para testes de integracao UI
9. **Views**: `src/backlog_manager/presentation/views/` — para testes E2E com qtbot
10. **pyproject.toml**: dependencias de teste (pytest, pytest-qt, pytest-cov, pytest-asyncio)
11. **Repository Protocols**: `src/backlog_manager/domain/interfaces/repositories.py` — para verificar integridade transacional
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-010 — Testes de Integracao E2E`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: implementar uma suite de testes E2E que valide a integridade do sistema como um todo, garantindo que todos os casos de uso (UC-001 a UC-005) e cenarios de teste (CT-001 a CT-005) funcionem corretamente quando todas as camadas estao integradas.

**Este epico NAO possui RFs como escopo principal** — e um epico de qualidade/testes que VALIDA os RFs implementados nos epicos anteriores.

**Requisitos Nao-Funcionais a validar:**

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | >= 80% global |
| RNF-CONF-001 | Disponibilidade | 99% sessoes sem crash nos testes E2E |
| RNF-CONF-002 | Recuperacao de Erros | 100% erros tratados corretamente |
| RNF-PERF-001 | Tempo de Alocacao | <= 5s para 100 historias |
| RNF-PERF-002 | Responsividade UI | <= 100ms para CRUD |

**Casos de Uso a validar via E2E:**

| ID | Nome | Tipo de Teste |
|----|------|---------------|
| UC-001 | Criar e Priorizar Backlog | E2E com GUI |
| UC-002 | Executar Alocacao Automatica | E2E com GUI |
| UC-003 | Detectar e Resolver Deadlock | E2E/Integracao |
| UC-004 | Importar Backlog do Excel | E2E com GUI |
| UC-005 | Gerenciar Ondas de Entrega | E2E com GUI |

**Cenarios de Teste do SRS a implementar:**

| ID | Descricao | Tipo de Teste |
|----|-----------|---------------|
| CT-001 | Backlog Completo 20 Historias, 5 Devs | Integracao/E2E |
| CT-002 | Deteccao de Ciclo em Grafo Grande (50 nos) | Unitario/Integracao |
| CT-003 | Deadlock por Falta de Desenvolvedores | Integracao |
| CT-004 | Feriados em Sequencia (Carnaval, Sexta-Santa) | Unitario |
| CT-005 | Balanceamento com Historias de Tamanhos Diferentes | Integracao |

**Artefatos a especificar:**

| Artefato | Descricao |
|----------|-----------|
| Estrutura de testes E2E | Organizacao de diretorios e marcadores pytest |
| Fixtures de teste | Dados de teste, integracao pytest-qt + qasync |
| Testes UC-001 a UC-005 | Implementacao dos casos de uso via GUI |
| Testes CT-001 a CT-005 | Implementacao dos cenarios de teste do SRS |
| Testes de performance | Validacao de RNF-PERF-001 e RNF-PERF-002 |
| Configuracao CI/CD | Workflow GitHub Actions com xvfb |
| Relatorio de cobertura | Configuracao pytest-cov com fail-under |
| Procedimento de correcao de bugs | Politica de tratamento conforme criticidade |

**IMPORTANTE**: Este epico **reutiliza** toda a infraestrutura de testes existente (EP-001), todas as entidades, services, repositorios e use cases (EP-001 a EP-009) e a interface grafica (EP-008). Ele **adiciona** testes E2E que validam a integracao de todas as camadas e **corrige** bugs revelados pelos testes.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Cada teste deve mapear para um UC ou CT do SRS.
   Cada UC e CT do escopo deve ter pelo menos um teste correspondente. Incluir
   matriz de rastreabilidade: Teste <-> UC/CT <-> RNF.

2. **Codigo existente prevalece como baseline**: Nao redefinir entidades, services,
   repositorios ou use cases ja implementados em EP-001 a EP-009. Especificar
   apenas **novos artefatos de teste** e **extensoes** a infraestrutura existente.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na
   secao `Conflitos e Lacunas Conhecidos`, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Separacao de tipos de teste**: Definir claramente:
   - **Testes Unitarios**: Logica pura, sem I/O, mocks para dependencias
   - **Testes de Integracao**: Com banco SQLite real, sem GUI
   - **Testes E2E**: Com GUI via pytest-qt, fluxos completos de usuario

5. **Fixtures documentadas**: Cada fixture deve especificar:
   - Nome e proposito
   - Dados criados/retornados
   - Escopo (function, class, module, session)
   - Dependencias de outras fixtures

6. **Sincronizacao qasync + pytest-qt**: Especificar padrao de integracao:
   - Como criar loop asyncio compativel com Qt
   - Como aguardar operacoes async em testes
   - Exemplo de teste E2E com qtbot + await

7. **Testes de performance especificados**: Para RNF-PERF-001 e RNF-PERF-002:
   - Metodo de medicao (time.perf_counter, memory_profiler)
   - Setup (numero de historias, desenvolvedores)
   - Limite de tempo esperado
   - Assercoes quantitativas

8. **Politica de bugs**: Para cada nivel de criticidade:
   - **Simples**: Corrigir imediatamente no PR, commit descritivo
   - **Media**: Corrigir imediatamente + comentario para analise futura
   - **Critica**: Issue detalhada + plano de acao estruturante

9. **Estabilidade de testes GUI**: Especificar boas praticas:
   - Uso obrigatorio de qtbot.waitSignal/waitUntil
   - Proibicao de time.sleep()
   - Limpeza de estado entre testes
   - Tratamento de dialogos modais

10. **CI/CD configurado**: Especificar:
    - Workflow GitHub Actions
    - Setup de xvfb para testes GUI
    - Configuracao de pytest-cov com fail-under=80
    - Cache de dependencias

11. **Validacao de cobertura**: Definir:
    - Comando para verificar cobertura
    - Relatorio por modulo (domain, application, infrastructure, presentation)
    - Acoes corretivas se meta nao atingida

12. **Roundtrip Excel**: Especificar teste de roundtrip completo:
    - Exportar todos os dados (historias, devs, features, dependencias)
    - Limpar banco de dados
    - Reimportar arquivo exportado
    - Validar igualdade de todos os campos

13. **Sem sobreposicao com EP-001 a EP-009**: Nao re-especificar entidades, services,
    use cases ou componentes de UI. Especificar apenas testes que validam a
    integracao desses componentes.

14. **Tempo de execucao**: Suite completa deve rodar em < 5 minutos.
    Especificar estrategias de otimizacao se necessario.

15. **Nomenclatura de testes**: Seguir padrao:
    - `test_<uc/ct>_<cenario>_<resultado_esperado>`
    - Ex: `test_uc001_criar_historia_com_sucesso`
    - Ex: `test_ct002_detectar_ciclo_50_nos`
</rules>
