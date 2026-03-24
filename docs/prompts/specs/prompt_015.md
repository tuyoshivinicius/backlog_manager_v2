# Prompt: Criar Especificacao Tecnica do EP-015

<role>
Voce e um Arquiteto de Software Senior especializado em Domain Services e algoritmos de otimizacao, com profundo conhecimento em:
- Algoritmos de alocacao de recursos e balanceamento de carga
- Algoritmos de scheduling e calculo de cronogramas com dependencias
- Domain Services stateless em Clean Architecture
- Diagnostico e melhoria iterativa de algoritmos complexos
- Observabilidade, logging estruturado e metricas de performance
- Testes de integracao e validacao de comportamento algoritmico
- Python assincrono (async/await) e integracao com GUI (PySide6 + qasync)

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas, com foco em diagnostico e refinamento de algoritmos.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **Persistencia**: aiosqlite (async SQLite) via `infrastructure/database/`
- **DTOs**: Pydantic ^2.0
- **Testes**: pytest + pytest-cov + pytest-asyncio
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD (entidades ricas, VOs, servicos de dominio)

### Estado Atual do Codigo (Implementado em EP-001 a EP-014)

O produto possui todas as camadas funcionais implementadas, incluindo o motor de alocacao (EP-007) e
calculo de cronograma (EP-006). EP-015 estabelece um **processo de melhoria iterativa colaborativa**
onde usuario e Claude Code trabalham juntos para identificar e corrigir comportamentos subotimos.

**AllocationService existente (~1.283 linhas em `domain/services/allocation_service.py`):**
- `AllocationConfig(dataclass)`: velocity, project_start_date, max_idle_days, allocation_criteria, max_iterations, random_seed
- `AllocationMetrics(dataclass)`: 16 campos de metricas (total_time_seconds, stories_processed, stories_allocated, waves_processed, total_iterations, iterations_per_wave, allocations_by_dependency_owner, allocations_by_load_balancing, deadlocks_detected, date_adjustments, validation_reallocations, validation_dependency_fixes, validation_conflict_fixes, max_idle_violations_detected, max_idle_violations_fixed, failed_reallocations)
- `AllocationResult(dataclass)`: allocated_stories, metrics, warnings
- `AllocationService.allocate_stories()`: metodo principal de alocacao
- Metodos auxiliares: `_is_eligible()`, `_get_story_wave()`, `_build_feature_map()`, `_group_stories_by_wave()`, `_has_period_overlap()`, `_select_developer()`, `_select_by_load_balancing()`, `_get_dependency_owner()`, etc.

**SchedulingService existente (~315 linhas em `domain/services/scheduling_service.py`):**
- `calculate_duration(story_points, velocity) -> int` — calcula duracao em dias uteis
- `is_workday(d, holidays) -> bool` — verifica se data e dia util
- `next_workday(d, holidays) -> date` — retorna proximo dia util
- `add_workdays(start_date, workdays, holidays) -> date` — avanca N dias uteis
- `count_workdays_between(start_date, end_date, holidays) -> int` — conta dias uteis entre datas
- `topological_sort(stories, dependencies) -> list[Story]` — ordenacao topologica com desempate por prioridade
- `calculate_story_dates(story, velocity, start_date, dependency_end_dates, holidays) -> tuple[date, date, int]`

**DependencyService existente (em `domain/services/dependency_service.py`):**
- `build_graph(dependencies) -> dict[str, list[str]]` — constroi grafo de adjacencia
- `would_create_cycle(graph, source, target) -> list[str] | None` — detecta se nova aresta cria ciclo
- `validate_wave_dependency(story_wave, depends_on_wave) -> bool` — valida dependencia cross-wave

**Seed Script existente (EP-014 em `scripts/seed_test_backlog.py`):**
- Gera dados de teste reproduziveis (random seed 42)
- 7 desenvolvedores, ~7 features em 7 ondas, ~190 historias, ~102 dependencias
- CLI: `--clean` para limpar dados, `--db-path` para banco customizado
- Funcao `seed_database(db_path, clean)` chamavel programaticamente

**Sistema de Logs existente (em `infrastructure/logging/logger_config.py`):**
- Logging estruturado com rotacao por tamanho (max 10MB)
- Logs em `%APPDATA%/BacklogManager/logs/`
- Niveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Formato: `%(asctime)s - %(levelname)s - %(name)s - %(message)s`

**Constantes de Limite do AllocationService:**
- `DEFAULT_MAX_ITERATIONS = 1000` — maximo de iteracoes por onda
- `MAX_REALLOCATIONS_PER_STORY = 3` — evita ping-pong entre devs
- `MAX_STABILIZATION_PASSES = 10` — limite de passadas no loop de estabilizacao
- `MAX_CONFLICT_PASSES = 100` — limite para resolucao de conflitos de periodo

**Use Case ExecuteAllocation (~157 linhas em `application/use_cases/allocation/execute_allocation.py`):**
- Coordena UnitOfWork + AllocationService + SchedulingService
- Entrada: AllocationConfigDTO
- Saida: AllocationResultDTO com metricas e warnings

**Value Objects existentes:**
- `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `StoryStatus(StrEnum)` {BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO}
- `BRAZILIAN_HOLIDAYS_2026_2028` (frozenset[date])

**Excecoes existentes:**
- `AllocationException`, `MaxIterationsExceeded` (allocation.py)
- `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo` (warnings.py)

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Natureza do epico — melhoria vs. codigo novo**: EP-015 NAO define novos requisitos funcionais (RF-xxx). E um processo de **refinamento iterativo** dos algoritmos ja implementados (RF-ALOC-001 a 013, RF-SCHED-001 a 006). -> A spec deve definir se (a) cria artefatos de codigo novos (ex: AllocationDiagnostics, melhorias de logging), (b) apenas documenta o processo colaborativo sem codigo novo, ou (c) especifica melhorias pontuais identificaveis a priori (ex: logging adicional em pontos criticos).

2. **Infraestrutura de diagnostico — logs vs. metricas vs. traces**: O epico menciona "logs detalhados com metricas de execucao (AllocationMetrics)". -> A spec deve definir se (a) AllocationMetrics ja e suficiente e apenas precisa ser exposto via logs, (b) novos campos de metricas sao necessarios, (c) logs estruturados adicionais em pontos criticos do algoritmo (ex: `logger.debug("Alocando historia %s para dev %s", story_id, dev_name)`), ou (d) sistema de tracing mais sofisticado.

3. **Protocolo de comunicacao usuario-Claude**: O epico define formato de descricao do usuario e resposta do Claude. -> A spec deve definir se (a) isso e apenas documentacao de processo (nao afeta codigo), (b) cria templates/checklists persistentes no repositorio, ou (c) especifica algum mecanismo de captura de feedback no codigo.

4. **Iteratividade vs. especificacao fixa**: EP-015 e inerentemente iterativo ("ciclo de iteracao"). -> A spec deve definir se (a) especifica apenas a infraestrutura de diagnostico e deixa melhorias para iteracoes futuras, (b) tenta antecipar melhorias comuns (ex: balanceamento por SP ao inves de contagem), ou (c) cria framework generico de melhorias. Recomendar (a).

5. **Visibilidade de metricas para usuario**: AllocationMetrics e dataclass interna. -> A spec deve definir se (a) metricas devem ser expostas na GUI (fora do escopo de EP-015), (b) metricas devem ser logadas em nivel INFO apos cada alocacao, (c) criar comando/script para analisar metricas de execucoes anteriores.

6. **Identificacao de problemas comuns**: O epico menciona "distribuicao desbalanceada de historias, datas sobrepostas, historias nao alocadas, deadlocks inesperados". -> A spec deve listar os problemas conhecidos e categoriza-los por severidade e frequencia, para priorizar melhorias.

7. **Cadeia de dependencias longa**: O epico menciona cenario de "cadeia longa de dependencias (A→B→C→D→E) cruzando ondas". -> A spec deve definir se (a) identificar este cenario como caso de teste especifico, (b) verificar se o seed script (EP-014) ja gera este cenario, ou (c) propor melhoria algoritmica especifica para lidar com cadeias longas.

8. **Validacao de melhorias**: O epico menciona "Validacao de melhorias via testes unitarios e de integracao existentes". -> A spec deve definir (a) se testes existentes sao suficientes, (b) se novos testes de caracterizacao sao necessarios, ou (c) se testes de performance devem ser formalizados.

9. **Conformidade com RNF-PERF-001**: "Manter tempo de alocacao <= 5s para 100 historias". -> A spec deve definir como medir e validar performance apos cada correcao, considerando que o seed gera ~190 historias.

10. **Relacao com EP-010 (Testes E2E)**: O epico menciona ser "complementar ao EP-010". -> A spec deve definir se (a) EP-015 depende de EP-010, (b) sao independentes e podem ser executados em paralelo, ou (c) EP-015 produz artefatos que EP-010 consumira.

11. **Balanceamento por contagem vs. SP**: RF-ALOC-002 documenta "Decisao de Design: Balanceamento por CONTAGEM de historias (nao por SP total)". -> A spec deve decidir se (a) esta decisao e final e nao sera alterada em EP-015, (b) pode ser revisada se problemas forem identificados, ou (c) criar opcao configuravel (ex: `BalancingStrategy.COUNT` vs `BalancingStrategy.STORY_POINTS`).

12. **Participacao ativa do usuario**: O epico pressupoe "Usuario disponivel para feedback visual durante ciclos". -> A spec deve considerar cenarios onde usuario nao pode participar ativamente e definir se Claude Code pode fazer diagnosticos autonomos baseados apenas em logs/metricas.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-015_melhoria-algoritmos-alocacao-cronograma.md` — processo de melhoria iterativa, ciclo de iteracao, arquivos criticos, protocolo de comunicacao, comandos uteis
2. **SRS completo**: `srs.md` — secoes:
   - §2.2 Capacidades 5 e 6 (Calculo de Cronograma, Alocacao Automatica)
   - §3.5 RF-SCHED-001 a RF-SCHED-006 (requisitos de cronograma a refinar)
   - §3.6 RF-ALOC-001 a RF-ALOC-013 (requisitos de alocacao a refinar)
   - §4.1 RNF-PERF-001 (tempo de alocacao <= 5s)
   - §4.4 RNF-MANT-001 a 004 (cobertura de testes, complexidade ciclomatica)
   - §7.1 CT-001, CT-003, CT-005 (cenarios de teste relevantes)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios:
   - §VIII Programacao Assincrona (dominio sincrono, I/O assincrono)
   - §XIV Estrategia de Testes (cobertura 80%+, testes de integracao)
   - §XVII Logging e Observabilidade (formato de logs, niveis, rotacao)
   - §XXI CI/CD e Qualidade Continua (complexidade ciclomatica <= 15 para alocacao)
4. **AllocationService**: `src/backlog_manager/domain/services/allocation_service.py` — algoritmo completo de alocacao, AllocationConfig, AllocationMetrics, AllocationResult, metodos auxiliares
5. **SchedulingService**: `src/backlog_manager/domain/services/scheduling_service.py` — calculo de datas, dias uteis, ordenacao topologica
6. **DependencyService**: `src/backlog_manager/domain/services/dependency_service.py` — grafo de dependencias, deteccao de ciclos
7. **ExecuteAllocation Use Case**: `src/backlog_manager/application/use_cases/allocation/execute_allocation.py` — coordenacao de alocacao
8. **CalculateSchedule Use Case**: `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py` — coordenacao de cronograma
9. **Seed Script**: `scripts/seed_test_backlog.py` — geracao de dados de teste reproduziveis
10. **Logger Config**: `src/backlog_manager/infrastructure/logging/logger_config.py` — configuracao de logging existente
11. **Excecoes e Warnings**: `src/backlog_manager/domain/exceptions/allocation.py`, `warnings.py` — AllocationException, DeadlockWarning, IdlenessWarning
12. **Testes existentes**:
    - `tests/unit/domain/services/test_allocation_service.py` — testes unitarios do AllocationService
    - `tests/unit/domain/services/test_scheduling_service.py` — testes unitarios do SchedulingService
    - `tests/integration/application/use_cases/allocation/` — testes de integracao de alocacao
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-015 — Melhoria Iterativa dos Algoritmos de Alocacao e Cronograma`.

A especificacao deve cobrir **exclusivamente** o escopo do epico:

**Processo de Melhoria Iterativa:**
- Ciclo: Preparar → Executar → Observar → Analisar → Implementar → Testar
- Infraestrutura de diagnostico para correlacionar comportamento visual com metricas internas
- Protocolo de comunicacao entre usuario e Claude Code

**Infraestrutura de Diagnostico:**
- Utilizacao de AllocationMetrics (RF-ALOC-011) para diagnostico
- Logging estruturado em pontos criticos dos algoritmos
- Correlacao de metricas com comportamento observado

**Refinamento de Requisitos Existentes (conforme problemas identificados):**
- RF-ALOC-001 a RF-ALOC-013: Refinamento de implementacao
- RF-SCHED-001 a RF-SCHED-006: Refinamento de implementacao

**Conformidade com Requisitos Nao-Funcionais:**
- RNF-PERF-001: Manter tempo de alocacao <= 5s para 100 historias
- RNF-MANT-001: Cobertura de testes >= 80%
- RNF-MANT-003: Complexidade ciclomatica <= 15 para funcoes de alocacao
- RNF-CONF-005: Utilizacao de logs para diagnostico

**IMPORTANTE**: Este epico **nao** cria novos requisitos funcionais. Ele **estabelece o processo e infraestrutura** para melhorar iterativamente os algoritmos ja implementados:

- **Diagnostico**: Logging aprimorado em pontos criticos do AllocationService e SchedulingService
- **Reproducibilidade**: Utilizacao do seed script (EP-014) para dados de teste consistentes
- **Validacao**: Execucao de testes existentes apos cada correcao
- **Documentacao**: Registro de problemas identificados e correcoes aplicadas

**Artefatos a especificar:**

| Artefato | Descricao |
|----------|-----------|
| Logging aprimorado em AllocationService | Pontos criticos com metricas detalhadas |
| Logging aprimorado em SchedulingService | Pontos criticos com metricas detalhadas |
| Checklist de diagnostico | Passos para correlacionar comportamento visual com logs |
| Template de relatorio de problema | Formato padronizado para descrever problemas |
| Template de plano de correcao | Formato padronizado para propor correcoes |
| Testes de caracterizacao (se necessario) | Capturar comportamento atual para detectar regressoes |

**Metricas de sucesso do processo:**

| Metrica | Valor Esperado |
|---------|----------------|
| Tempo de alocacao (190 historias, 7 devs) | <= 5 segundos |
| Cobertura de testes apos correcoes | >= 80% |
| Complexidade ciclomatica | <= 15 |
| Regressoes introduzidas | 0 |
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Natureza de refinamento, nao novos RFs**: Este epico REFINA requisitos existentes (RF-ALOC-001 a 013, RF-SCHED-001 a 006). NAO cria novos requisitos funcionais. A spec deve focar em infraestrutura de diagnostico e processo de melhoria.

2. **Codigo existente prevalece como baseline**: AllocationService, SchedulingService, DependencyService, ExecuteAllocation e CalculateSchedule ja estao implementados. A spec deve especificar apenas **melhorias de observabilidade** (logging adicional) e **processo de refinamento**, nao reescrever os servicos.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao `Conflitos e Lacunas Conhecidos`, a spec deve conter uma secao "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Logging estruturado nos pontos criticos**: Especificar exatamente onde adicionar logs no AllocationService:
   - Inicio e fim de cada onda (INFO)
   - Selecao de desenvolvedor para historia (DEBUG)
   - Deteccao de conflito de periodo (DEBUG)
   - Deteccao de deadlock (WARNING)
   - Deteccao de ociosidade (WARNING/INFO)
   - Metricas finais de alocacao (INFO)

5. **Utilizacao de AllocationMetrics**: RF-ALOC-011 ja define 16 campos de metricas. A spec deve especificar como essas metricas sao logadas/expostas para diagnostico, sem criar novos campos desnecessarios.

6. **Reproducibilidade via seed script**: O seed script (EP-014) gera dados deterministicos (random seed 42). A spec deve especificar como usar o seed para reproduzir cenarios de teste.

7. **Processo de ciclo iterativo documentado**: Especificar as 6 etapas do ciclo:
   1. PREPARAR: Executar seed script com --clean
   2. EXECUTAR: Abrir aplicacao GUI e executar alocacao
   3. OBSERVAR: Usuario descreve comportamento visual
   4. ANALISAR: Claude Code correlaciona logs com descricao
   5. IMPLEMENTAR: Propor e aplicar correcao (com aprovacao)
   6. TESTAR: Executar suite de testes para validar

8. **Performance RNF-PERF-001**: Toda correcao deve manter tempo <= 5s para 100 historias. Especificar como medir:
   - `poetry run pytest tests/unit/domain/services/test_allocation_service.py -v -k performance`
   - Verificar `AllocationMetrics.total_time_seconds`

9. **Cobertura RNF-MANT-001**: Toda correcao deve manter cobertura >= 80%. Especificar comando:
   - `poetry run pytest --cov=src/backlog_manager --cov-report=term-missing`

10. **Complexidade RNF-MANT-003**: Funcoes modificadas devem manter complexidade ciclomatica <= 15. Especificar verificacao:
    - `radon cc src/backlog_manager/domain/services/allocation_service.py -a -s`

11. **Nao antecipar problemas especificos**: A spec NAO deve tentar antecipar quais melhorias serao necessarias. Deve especificar apenas a infraestrutura e processo para identificar e corrigir problemas **quando encontrados**.

12. **Consistencia de nomenclatura**: Reutilizar nomes existentes (AllocationService, SchedulingService, AllocationMetrics, etc.). Nao criar sinonimos ou aliases.

13. **Mensagens de log em portugues**: Conforme Constituicao §XV, mensagens de log sao em portugues. Especificar exemplos de mensagens.

14. **Testes de caracterizacao (se necessario)**: Se melhorias alteram comportamento existente, criar testes que capturam estado atual para detectar regressoes inesperadas.

15. **Documentacao de correcoes**: Cada correcao aplicada deve ser documentada com: problema identificado, diagnostico, mudanca aplicada, resultado. Formato pode ser comentario no PR ou entrada em CHANGELOG.

16. **Integracao com EP-010 (Testes E2E)**: Especificar que EP-015 e independente de EP-010, mas melhorias de EP-015 facilitarao execucao de testes E2E ao garantir comportamento algoritmico mais previsivel.
</rules>
