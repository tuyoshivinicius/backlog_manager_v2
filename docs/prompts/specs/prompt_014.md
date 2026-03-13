# Prompt: Criar Especificacao Tecnica do EP-014

<role>
Voce e um Engenheiro de Software Pleno/Senior especializado em Python, com foco em:
- Scripts de geracao de dados de teste (seeding) para bancos de dados SQLite
- Algoritmos de geracao de grafos aciclicos direcionados (DAG) com dependencias
- Validacao de invariantes (ciclos, waves, integridade referencial)
- Testes de integracao e performance com dados volumosos
- Clean Architecture e separacao entre scripts utilitarios e codigo de producao

Voce produz especificacoes tecnicas prescritivas, executaveis e rastreaveis, focando em
scripts de infraestrutura de testes que geram dados deterministicos e validaveis.
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
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD

### Estado Atual do Codigo (Implementado em EP-001 a EP-013)

O produto possui todas as camadas funcionais implementadas. EP-014 adiciona um **script de seed**
para popular o banco com dados de teste volumosos, permitindo validar o motor de alocacao (EP-007)
e calculo de cronograma (EP-006) em cenarios realistas.

**Schema SQLite existente (em `infrastructure/database/schema.sql`):**

```sql
CREATE TABLE Developer (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE Feature (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL UNIQUE,
    wave INTEGER NOT NULL UNIQUE CHECK (wave > 0)
);

CREATE TABLE Story (
    id VARCHAR(20) PRIMARY KEY,
    component VARCHAR(50) NOT NULL,
    name VARCHAR(200) NOT NULL,
    story_points INTEGER NOT NULL CHECK (story_points IN (3, 5, 8, 13)),
    priority INTEGER NOT NULL CHECK (priority >= 0),
    status VARCHAR(20) NOT NULL DEFAULT 'BACKLOG',
    duration INTEGER,
    start_date DATE,
    end_date DATE,
    developer_id INTEGER REFERENCES Developer(id) ON DELETE SET NULL,
    feature_id INTEGER REFERENCES Feature(id) ON DELETE SET NULL
);

CREATE TABLE Story_Dependency (
    story_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    depends_on_id VARCHAR(20) NOT NULL REFERENCES Story(id) ON DELETE CASCADE,
    PRIMARY KEY (story_id, depends_on_id),
    CHECK (story_id != depends_on_id)
);
```

**DependencyService existente (em `domain/services/dependency_service.py`):**
- `build_graph(dependencies: Sequence[tuple[str, str]]) -> dict[str, list[str]]` — constroi grafo de adjacencia
- `would_create_cycle(graph, source, target) -> list[str] | None` — detecta ciclo via DFS iterativo
- `validate_wave_dependency(story_wave, depends_on_wave) -> bool` — valida dependencia cross-wave

**Entidades de dominio existentes:**
- `Story(dataclass)`: id (str, COMPONENTE-NNN), component, name, story_points, priority, status, duration, start_date, end_date, developer_id, feature_id
- `Developer(dataclass)`: id (int | None), name
- `Feature(dataclass)`: id (int | None), name, wave

**Value Objects existentes:**
- `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `StoryStatus(StrEnum)` {BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO}

**Cenarios de teste relevantes (SRS §7.1):**
- CT-001: Backlog Completo 20 Historias — o seed expande para 150+ historias
- CT-002: Deteccao de Ciclo em Grafo Grande (50 nos < 100ms) — seed gera grafos testáveis
- CT-003: Deadlock por Falta de Desenvolvedores — seed cria cenarios propicios
- CT-005: Balanceamento com Tamanhos Diferentes — seed inclui SP variados

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **Localizacao do script de seed**: O epic define `scripts/seed_test_backlog.py` na raiz. -> A spec deve confirmar se (a) criar pasta `scripts/` na raiz do repositorio (fora de `src/`), (b) colocar em `tests/fixtures/` como parte da infraestrutura de testes, ou (c) colocar em `src/backlog_manager/infrastructure/scripts/`. Considerar que scripts de seed NAO sao empacotados no wheel de producao.

2. **Uso de INSERT direto vs. Use Cases**: O epic menciona "Seed usa INSERT direto, nao entidades" como premissa. -> A spec deve decidir se (a) usar SQL puro com `aiosqlite.execute()` diretamente, (b) usar os repositorios existentes (StoryRepository, DeveloperRepository, FeatureRepository, StoryDependencyRepository) via asyncio, ou (c) usar combinacao (repos para entidades, SQL para dependencias em massa). Considerar validacoes do repositorio vs. performance.

3. **Validacao de ciclos antes de inserir**: O epic exige "Validar antes de inserir; usar algoritmo DFS". -> A spec deve definir se (a) gerar dependencias de forma que ciclos sao impossiveis por construcao (ex: so depender de ondas anteriores ou prioridades menores), (b) gerar dependencias aleatorias e validar ciclo antes de cada insercao usando DependencyService.would_create_cycle(), ou (c) gerar todas as dependencias, validar o grafo completo no final, e rejeitar se houver ciclo. Considerar determinismo vs. complexidade.

4. **Execucao sincrona vs. assincrona**: Os repositorios existentes sao async (aiosqlite). -> A spec deve definir se o script (a) usa asyncio.run() como wrapper e codigo async internamente, (b) usa aiosqlite diretamente com async/await, ou (c) cria conexao sincrona separada (sqlite3 stdlib) para simplicidade. Considerar compatibilidade com infraestrutura existente.

5. **Determinismo e reprodutibilidade**: O epic exige "Random seed fixo (42) para reproducibilidade". -> A spec deve definir (a) como garantir que os mesmos IDs, nomes e dependencias sao gerados a cada execucao, (b) se os IDs de desenvolvedores/features (auto-increment) serao deterministicos, (c) se o script limpa dados antes de inserir (--clean flag). Documentar garantias de reproducibilidade.

6. **Distribuicao de dependencias intra-onda vs. inter-ondas**: O epic define "60% intra-onda, 40% inter-ondas". -> A spec deve detalhar o algoritmo de selecao: (a) como escolher historias candidatas para cada tipo, (b) como evitar ciclos dentro da mesma onda (intra-onda so depende de prioridade menor?), (c) como garantir que inter-ondas sempre aponta para onda anterior. Incluir pseudocodigo.

7. **Formato de IDs de historia**: O epic menciona COMPONENTE-NNN (ex: AUTH-001, USER-042). -> A spec deve definir (a) lista de componentes a usar (ex: AUTH, USER, PROD, CART, PAY, REPORT, NOTIF, API), (b) como distribuir historias entre componentes, (c) como gerar IDs sequenciais por componente. Garantir compatibilidade com formato existente.

8. **Cenario de cadeia longa de dependencias**: O epic menciona "Cadeia de dependencias longa (A→B→C→D→E) cruzando ondas". -> A spec deve definir se (a) criar cadeia longa deliberadamente como caso de teste especifico, (b) deixar a geracao aleatoria criar cadeias naturalmente, ou (c) ambos. Especificar tamanho maximo da cadeia.

9. **Flag --clean e idempotencia**: O epic define "Limpar dados existentes (opcional via flag)". -> A spec deve definir (a) se --clean deleta TODAS as tabelas ou apenas as geradas pelo seed, (b) ordem de deleção para respeitar FKs, (c) se sem --clean o script falha em banco com dados ou insere adicional. Considerar idempotencia.

10. **Log de progresso**: O epic define RF-SEED-008 "Log de Progresso". -> A spec deve definir (a) formato das mensagens de log, (b) nivel de detalhe (por entidade? por onda? totais?), (c) usar logging stdlib ou print simples. Considerar que e script CLI, nao aplicacao de producao.

11. **Metricas de validacao pos-seed**: O epic define KPIs (150-200 historias, 80-120 dependencias, 7 ondas). -> A spec deve definir (a) se o script valida essas metricas no final e reporta, (b) se falha se metricas nao forem atingidas, ou (c) apenas loga contagens para verificacao manual.

12. **Integracao com testes de performance**: O seed e usado para testar EP-006 (cronograma) e EP-007 (alocacao). -> A spec deve definir (a) se os testes de integracao chamam o seed programaticamente, (b) se o seed cria arquivo .db separado para testes, ou (c) se testes usam fixtures independentes. Considerar isolamento de testes.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-014_script-seed-teste-alocacao.md` — requisitos, escopo, criterios de aceite, algoritmo de geracao de dependencias, estrutura de dados, especificacao tecnica
2. **SRS completo**: `srs.md` — secoes:
   - §3.4 RF-DEP-003 (Detectar Ciclos de Dependencia) — para reutilizar DependencyService
   - §3.4 RF-DEP-004 (Validar Dependencias entre Ondas) — regras de wave
   - §3.5 RF-SCHED-006 (Ordenacao Topologica) — para testar apos seed
   - §3.6 RF-ALOC-001 a RF-ALOC-013 — requisitos de alocacao que o seed deve testar
   - §7.1 CT-001 a CT-005 — cenarios de teste que o seed habilita
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios:
   - §V SQLite como Banco de Dados (schema, transacoes, RNF-CONF-003)
   - §VII Estrutura de Diretorios (localizacao de scripts)
   - §XIV Estrategia de Testes (testes de integracao com SQLite real)
   - §XVII Logging e Observabilidade (formato de logs)
4. **Schema do banco**: `src/backlog_manager/infrastructure/database/schema.sql` — estrutura das tabelas, constraints, FKs
5. **DependencyService**: `src/backlog_manager/domain/services/dependency_service.py` — build_graph(), would_create_cycle() para validacao de ciclos
6. **Repository Protocols**: `src/backlog_manager/domain/interfaces/repositories.py` — StoryRepository, DeveloperRepository, FeatureRepository, StoryDependencyRepository
7. **Implementacao SQLite**: `src/backlog_manager/infrastructure/database/repositories/` — para entender como repositorios persistem dados
8. **Value Objects**: `src/backlog_manager/domain/value_objects/story_point.py`, `story_status.py` — valores validos para story_points, status
9. **Entidades**: `src/backlog_manager/domain/entities/story.py`, `developer.py`, `feature.py` — campos e validacoes
10. **Testes de integracao existentes**: `tests/integration/` — para entender padrao de testes com SQLite
11. **pyproject.toml**: dependencias e entry points do projeto
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-014 — Script de Seed para Teste de Alocacao`.

A especificacao deve cobrir **exclusivamente** o escopo do epico:
- RF-SEED-001: Inserir 7 Desenvolvedores (Ana, Bruno, Carlos, Diana, Eduardo, Fernanda, Gabriel)
- RF-SEED-002: Inserir ~30 Features distribuidas em 7 ondas (4-5 features/onda)
- RF-SEED-003: Gerar ~150-200 Historias com SP variados (3, 5, 8, 13)
- RF-SEED-004: Criar Dependencias Intra-Onda (~60% do total)
- RF-SEED-005: Criar Dependencias Inter-Ondas (~40% do total)
- RF-SEED-006: Validar Ausencia de Ciclos antes de inserir
- RF-SEED-007: Limpar Dados Existentes (--clean flag)
- RF-SEED-008: Log de Progresso durante execucao

**IMPORTANTE**: Este epico cria um **script de infraestrutura de testes**, NAO codigo de producao.
O script:
- Reside FORA de `src/backlog_manager/` (nao empacotado)
- Usa a infraestrutura existente (schema, DependencyService) para validacao
- Gera dados deterministicos para reproducibilidade
- Executa via CLI (nao via GUI)

**Artefatos a especificar:**

| Artefato | Descricao |
|----------|-----------|
| `scripts/seed_test_backlog.py` | Script principal de seed |
| Funcao `seed_database(db_path, clean)` | Funcao principal chamavel programaticamente |
| Algoritmo de geracao de dependencias | Logica para criar dependencias sem ciclos |
| Configuracao de dados (DEVELOPERS, WAVES_CONFIG, COMPONENTS) | Constantes de configuracao |
| Validacao pos-seed | Verificacao de metricas e integridade |
| Testes do script de seed | Testes para garantir que o seed funciona corretamente |

**Metricas de sucesso do script:**

| Metrica | Valor Esperado |
|---------|----------------|
| Desenvolvedores | Exatamente 7 |
| Features | ~30 (4-5 por onda) |
| Historias | 150-200 |
| Dependencias | 80-120 (60% intra, 40% inter) |
| Ciclos | 0 (validado) |
| Tempo de execucao | < 5 segundos |
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF-SEED do epico
   (RF-SEED-001 a 008). Todo RF do escopo deve ter pelo menos um FR correspondente. Incluir
   matriz de rastreabilidade.

2. **Codigo existente prevalece como baseline**: Reutilizar DependencyService.would_create_cycle()
   para validacao de ciclos. Reutilizar schema.sql para estrutura de tabelas. NAO redefinir
   entidades ou criar novos repositorios — usar INSERT direto ou repositorios existentes.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos`, a spec deve conter uma secao "Decisao Arquitetural"
   (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Algoritmo de geracao de dependencias detalhado**: Especificar com pseudocodigo:
   - Como gerar dependencias intra-onda sem ciclos
   - Como gerar dependencias inter-ondas respeitando wave anterior
   - Como validar grafo completo apos geracao
   - Como garantir distribuicao 60/40

5. **Determinismo garantido**: Especificar:
   - Uso de random.seed(42) no inicio
   - Ordem de geracao (devs -> features -> stories -> deps)
   - IDs sequenciais e previsiveis
   - Testes que validam reproducibilidade

6. **Integridade transacional**: Toda a operacao de seed DEVE usar transacao atomica:
   - BEGIN no inicio
   - COMMIT apenas se tudo suceder
   - ROLLBACK em caso de erro
   - Garantir consistencia mesmo com interrupcao

7. **Performance RNF-PERF-001**: Tempo de execucao < 5 segundos para o seed completo.
   Especificar estrategias de otimizacao:
   - Bulk inserts (executemany vs. execute em loop)
   - Desabilitar FKs durante insercao (PRAGMA foreign_keys = OFF temporariamente)
   - Indices criados apos insercao se necessario

8. **CLI bem definida**: Especificar interface de linha de comando:
   - `python scripts/seed_test_backlog.py` (usa banco padrao)
   - `--clean` para limpar dados antes
   - `--db-path PATH` para banco customizado
   - Codigos de saida (0=sucesso, 1=erro)

9. **Log de progresso estruturado**: Especificar formato de logs:
   - Timestamps ISO 8601
   - Contagens por etapa (devs, features, stories, deps)
   - Mensagem final com metricas
   - Nivel INFO para operacoes, WARNING para alertas

10. **Validacao pos-seed**: Especificar verificacoes automaticas:
    - Contagem de entidades vs. esperado
    - Validacao de ciclos (DependencyService)
    - Verificacao de FKs (feature_id, developer_id em stories)
    - Distribuicao de waves (todas as 7 ondas com features)

11. **Testes do script de seed**: Especificar testes de integracao:
    - test_seed_creates_expected_developers
    - test_seed_creates_expected_features_per_wave
    - test_seed_creates_stories_in_range
    - test_seed_creates_dependencies_without_cycles
    - test_seed_execution_time_under_5_seconds
    - test_seed_is_deterministic (rodar 2x, comparar)

12. **Separacao de producao**: O script NAO deve:
    - Importar de presentation layer
    - Usar ViewModels ou Use Cases
    - Modificar codigo em src/backlog_manager/
    - Ser incluido no pacote wheel

13. **Compatibilidade com testes existentes**: Especificar como testes de integracao
    podem usar o seed:
    - Funcao seed_database() chamavel de fixtures
    - Banco de teste isolado (tmpdir)
    - Limpeza automatica apos testes
</rules>
