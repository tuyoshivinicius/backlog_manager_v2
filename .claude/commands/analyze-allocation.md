---
description: Automatizar ciclo de analise de alocacao - executa seed script, testes, analisa logs, identifica anomalias e propoe correcoes. (project)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - TodoWrite
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## 0. Log Cleanup (SEMPRE EXECUTAR PRIMEIRO)

**CRITICO**: Limpar logs antigos para garantir analise de dados frescos.

### 0.1 Detectar Plataforma e Caminho dos Logs

**Windows:**
```text
%APPDATA%/BacklogManager/logs/backlog_manager.log
```

**Linux:**
```text
~/.config/backlog_manager/logs/backlog_manager.log
```

### 0.2 Limpar Arquivo de Log

**Windows (Git Bash/MINGW):**
```bash
LOG_PATH="$APPDATA/BacklogManager/logs/backlog_manager.log"
if [ -f "$LOG_PATH" ]; then
    cp "$LOG_PATH" "${LOG_PATH}.bak.$(date +%Y%m%d_%H%M%S)"
    > "$LOG_PATH"
    echo "Log limpo: $LOG_PATH"
else
    mkdir -p "$(dirname "$LOG_PATH")"
    echo "Log nao existe ainda (sera criado na execucao)"
fi
```

**Linux:**
```bash
LOG_PATH="$HOME/.config/backlog_manager/logs/backlog_manager.log"
if [ -f "$LOG_PATH" ]; then
    cp "$LOG_PATH" "${LOG_PATH}.bak.$(date +%Y%m%d_%H%M%S)"
    > "$LOG_PATH"
    echo "Log limpo: $LOG_PATH"
fi
```

### 0.3 Por que Limpar?

- Logs antigos podem conter metricas de execucoes anteriores
- O marcador `ALLOCATION_METRICS_JSON` pode aparecer multiplas vezes
- Garante que as metricas extraidas sao da execucao atual
- Evita confusao com deadlocks de sessoes anteriores

---

## 0.5 Progress Tracking

**OBRIGATORIO**: Usar TodoWrite para acompanhar progresso.

Criar lista inicial:
```
1. [in_progress] Limpar logs antigos
2. [pending] Verificar pre-requisitos
3. [pending] Executar seed script
4. [pending] Executar alocacao e coletar metricas
5. [pending] Detectar anomalias
6. [pending] Gerar relatorio
7. [pending] Propor correcoes (se necessario)
```

Atualizar status conforme progresso (`in_progress` -> `completed`).

---

## 1. Pre-requisite Verification

**HALT** if any check fails with an actionable message.

### 1.1 Check Poetry Installation

```bash
poetry --version
```

- **If fails**: HALT with message: "Poetry nao encontrado. Instale via: pip install poetry"

### 1.2 Check Dependencies

```bash
poetry check
```

- **If fails**: HALT with message: "Dependencias nao instaladas. Execute: poetry install"

### 1.3 Check Required Scripts

Verify these files exist:
- `scripts/seed_test_backlog.py`
- `scripts/extract_metrics.py`
- `scripts/validate_allocation_data.py`
- `scripts/common/db_path.py`
- `tests/integration/`

- **If missing**: HALT with message: "Pre-requisitos EP-014/EP-015 nao encontrados. Verifique se os EPs anteriores foram implementados."

### 1.4 SQLite MCP (Recomendado)

Verificar se o MCP de SQLite esta configurado em `.mcp.json`:

```json
{
  "mcpServers": {
    "sqlite": {
      "command": "uvx",
      "args": ["mcp-server-sqlite", "--db-path", "backlog_manager.db"]
    }
  }
}
```

**Beneficios**:
- Queries diretas sem wrappers Python
- Output consistente entre plataformas
- Melhor tratamento de erros

**Se MCP disponivel**: PREFERIR usar MCP para todas as queries ao banco.
**Se MCP nao disponivel**: Usar fallback Python inline.

### 1.5 Data Validation (OBRIGATORIO)

**CRITICO**: Executar validacao de dados ANTES de qualquer analise de alocacao.

```bash
poetry run python scripts/validate_allocation_data.py --strict
```

**Validations Performed**:
| Check | Requirement | Threshold |
|-------|-------------|-----------|
| Stories exist | Total stories > 0 | REQUIRED |
| Stories with dates | All stories have start_date AND end_date | 100% |
| Active developers | At least 1 developer exists | > 0 |
| Valid dependencies | All dependencies point to existing stories | 100% |
| Feature waves | All features have valid wave numbers (>= 1) | 100% |
| Circular dependencies | No circular dependencies exist | 0 |

**If validation fails**:
- HALT with detailed error message
- Display fix suggestions from the validation report
- DO NOT proceed with allocation analysis

---

## 2. Argument Parsing

Parse `$ARGUMENTS` for the following flags:

| Flag | Default | Behavior |
|------|---------|----------|
| `--logs-only` | false | Skip seed script and tests, analyze existing logs only |
| `--db-path PATH` | app default | Path to database file |
| `--skip-validation` | false | Skip data validation step (use with caution) |
| `--json` | false | Output metrics in JSON format |
| `--verbose` | false | Enable verbose output with detailed diagnostics |

**Mode Selection**:
- If `--logs-only` present: Set `MODE=logs-only`
- Otherwise: Set `MODE=full`

**Database Path Priority**:
1. `--db-path` flag value (if provided)
2. `BACKLOG_DB_PATH` environment variable (if set)
3. Default app data location: `%APPDATA%/BacklogManager/data/backlog.db`

---

## 3. Log File Location Detection

Detect log file location based on platform:

### Windows

```text
%APPDATA%/BacklogManager/logs/backlog_manager.log
```

Expanded: `C:/Users/{username}/AppData/Roaming/BacklogManager/logs/backlog_manager.log`

### Linux

```text
~/.config/backlog_manager/logs/backlog_manager.log
```

### Detection Steps

1. Check current platform (Windows vs Linux)
2. Expand environment variables
3. Verify log file exists
4. If `MODE=logs-only` and no logs exist: HALT with message: "Nenhum log encontrado. Execute sem --logs-only para gerar logs."

---

## 4. Error Handling Pattern

**CRITICAL**: This skill does NOT retry automatically on failure.

For any error:
1. **HALT** execution immediately
2. **Display** clear error message with context
3. **Suggest** actionable next steps
4. **DO NOT** retry the failed operation

### Error Message Format

```text
## ERRO: {tipo_do_erro}

**Contexto**: {o_que_estava_sendo_executado}
**Erro**: {mensagem_de_erro}

### Proximos Passos
1. {acao_sugerida_1}
2. {acao_sugerida_2}
```

---

## 5. Execution Flow (MODE=full)

### 5.0 Database State Verification

Antes de executar, verificar estado do banco usando MCP SQLite (preferencial) ou fallback Python:

**Via MCP SQLite:**
```sql
SELECT
  COUNT(*) as total,
  SUM(CASE WHEN developer_id IS NOT NULL THEN 1 ELSE 0 END) as allocated,
  SUM(CASE WHEN developer_id IS NULL THEN 1 ELSE 0 END) as eligible
FROM Story;
```

**Via Fallback Python (se MCP nao disponivel):**
```bash
poetry run python -c "
import sqlite3
c = sqlite3.connect('backlog_manager.db')
r = c.execute('SELECT COUNT(*), SUM(CASE WHEN developer_id IS NOT NULL THEN 1 ELSE 0 END) FROM Story').fetchone()
print(f'Total: {r[0]}, Allocated: {r[1]}, Eligible: {r[0]-r[1]}')
"
```

**Avisos**:
- Se `eligible == 0`: Alertar "Nenhuma story elegivel para alocacao."
- Se `total == 0`: Alertar "Banco vazio. Execute seed script."

### 5.1 Execute Seed Script

```bash
poetry run python scripts/seed_test_backlog.py --clean
```

- **If fails**: HALT with error message and suggest checking pre-requisites

### 5.2 Execute Allocation Tests

```bash
poetry run pytest tests/integration/ -k allocation -v
```

- **If fails**: HALT with error message and suggest checking test configuration
- **Capture output** for analysis

### 5.3 Collect Logs

1. Navigate to log directory (from step 3)
2. Read the most recent log file
3. Extract content from last test execution

---

## 6. Execution Flow (MODE=logs-only)

Skip steps 5.1 and 5.2. Go directly to:

1. Verify logs exist (HALT if not)
2. Read most recent log file
3. Continue to metrics extraction

---

## 7. Metrics Extraction

### 7.0 Method Selection

**PREFERIR** na seguinte ordem:
1. **Script dedicado** `scripts/extract_metrics.py` (mais confiavel e completo)
2. **Logs estruturados** com `ALLOCATION_METRICS_JSON` (se disponiveis)
3. **Fallback inline** (ultimo recurso)

### 7.1 Primary Method: Extract via Script

**PREFERIR ESTE METODO** - usa script dedicado com diagnostico automatico:

```bash
poetry run python scripts/extract_metrics.py --diagnose
```

**Para output JSON** (para automacao):
```bash
poetry run python scripts/extract_metrics.py --diagnose --json
```

**Opcoes disponiveis**:
| Flag | Comportamento |
|------|---------------|
| `--diagnose` | Executa diagnostico de deadlocks se detectados |
| `--json` | Output em formato JSON estruturado |
| `--db-path PATH` | Usa caminho customizado para o banco |
| `-v, --verbose` | Output detalhado com progresso |

**Output JSON**:
```json
{
  "timestamp": "2026-03-23T...",
  "database": "/path/to/db",
  "metrics": { ... },
  "diagnosis": { ... }  // se --diagnose e deadlocks detectados
}
```

### 7.2 Alternative: Extract from Logs

Buscar metricas JSON nos logs (se limpos na secao 0):

```bash
grep "ALLOCATION_METRICS_JSON:" "$LOG_PATH" | tail -1 | sed 's/.*ALLOCATION_METRICS_JSON: //'
```

### 7.3 Fallback: Inline Execution

Se o script nao estiver disponivel, usar execucao inline:

```bash
poetry run python -c "
import asyncio
import json
from datetime import date
from backlog_manager.domain.services import AllocationService, AllocationConfig, AllocationCriteria
from backlog_manager.infrastructure.database.sqlite_connection import create_connection
from backlog_manager.infrastructure.database.repositories import *

async def run():
    conn = await create_connection()
    stories = await SQLiteStoryRepository(conn).get_all()
    devs = await SQLiteDeveloperRepository(conn).get_all()
    deps = await SQLiteStoryDependencyRepository(conn).get_all_dependencies()
    features = await SQLiteFeatureRepository(conn).get_all()

    config = AllocationConfig(velocity=2.0, project_start_date=date.today(), max_idle_days=3, random_seed=42)
    result = AllocationService.allocate_stories(list(stories), list(devs), list(deps), list(features), [], config)
    m = result.metrics
    print(json.dumps({k: getattr(m, k) for k in ['stories_processed', 'stories_allocated', 'deadlocks_detected', 'skill_match_ratio']}, indent=2))
    await conn.close()

asyncio.run(run())
"
```

### 7.4 Metricas Esperadas

| Metrica | Tipo | Descricao |
|---------|------|-----------|
| total_time_seconds | float | Tempo total de execucao |
| stories_processed | int | Total de historias processadas |
| stories_allocated | int | Historias alocadas com sucesso |
| waves_processed | int | Numero de ondas processadas |
| total_iterations | int | Total de iteracoes do algoritmo |
| allocations_by_dependency_owner | int | Alocacoes por DEPENDENCY_OWNER |
| allocations_by_load_balancing | int | Alocacoes por LOAD_BALANCING |
| deadlocks_detected | int | Deadlocks detectados |
| date_adjustments | int | Ajustes de data realizados |
| validation_reallocations | int | Realocacoes na validacao |
| validation_dependency_fixes | int | Dependencias corrigidas |
| validation_conflict_fixes | int | Conflitos resolvidos |
| max_idle_violations_detected | int | Violacoes de max_idle detectadas |
| max_idle_violations_fixed | int | Violacoes corrigidas |
| failed_reallocations | int | Realocacoes falhas |

### Derived Metric

Calculate `skill_match_ratio`:

```text
skill_match_ratio = allocations_by_dependency_owner / (allocations_by_dependency_owner + allocations_by_load_balancing)
```

---

## 8. Anomaly Detection

### 8.0 Nota sobre Deadlocks em Dados de Teste

O script `seed_test_backlog.py` pode gerar cenarios onde deadlocks sao esperados.

**Para testar cenario de sucesso**, limpar alocacoes existentes antes:
```sql
UPDATE Story SET developer_id = NULL WHERE developer_id IS NOT NULL;
```

### 8.1 Thresholds

Apply thresholds to identify anomalies:

| Metrica | Threshold | Severidade |
|---------|-----------|------------|
| deadlocks_detected | > 0 | CRITICAL |
| max_idle_violations_detected | > 5 | HIGH |
| max_idle_violations_detected | > 0 | MEDIUM |
| skill_match_ratio | < 0.5 | MEDIUM |

### Detection Rules

1. Check in order: CRITICAL -> HIGH -> MEDIUM
2. Report highest severity anomaly first
3. Multiple anomalies at same level: report all

### 8.2 Deadlock Diagnosis (se deadlocks > 0)

Se deadlocks forem detectados, analisar historias bloqueadas:

```python
# Identificar historias nao alocadas e suas dependencias
blocked_stories = [s for s in stories if s.developer_id is None]
for story in blocked_stories:
    deps = [d for d in dependencies if d[0] == story.id]
    print(f"{story.id}: depende de {[d[1] for d in deps]}")
```

**Categorias de Causa**:

| Causa | Descricao | Correcao |
|-------|-----------|----------|
| MISSING_DATES | Stories sem start_date ou end_date | Run seed_test_backlog.py --clean |
| UNSATISFIED_DEPENDENCIES | Dependencias para stories nao alocadas | Alocar dependencias primeiro |
| PERIOD_CONFLICTS | Todos devs ocupados no periodo | Ajustar datas ou adicionar devs |
| CIRCULAR_DEPENDENCIES | Ciclos de dependencia detectados | Remover uma dependencia do ciclo |

---

## 9. Report Generation

Generate structured report:

```markdown
## Relatorio de Analise de Alocacao

**Timestamp**: {YYYY-MM-DDTHH:MM:SS}
**Modo**: {full | logs-only}

### Metricas

| Metrica | Valor |
|---------|-------|
| total_time_seconds | {value} |
| stories_processed | {value} |
| stories_allocated | {value} |
| waves_processed | {value} |
| total_iterations | {value} |
| allocations_by_dependency_owner | {value} |
| allocations_by_load_balancing | {value} |
| skill_match_ratio | {value} |
| deadlocks_detected | {value} |
| date_adjustments | {value} |
| validation_reallocations | {value} |
| validation_dependency_fixes | {value} |
| validation_conflict_fixes | {value} |
| max_idle_violations_detected | {value} |
| max_idle_violations_fixed | {value} |
| failed_reallocations | {value} |

### Anomalias Identificadas

{Se nenhuma anomalia: "Nenhuma anomalia detectada."}

{Se anomalia(s):}
**{SEVERITY}**: {tipo_anomalia}
- Metrica: {nome} = {valor}
- Threshold: {operador} {valor_esperado}
- Descricao: {descricao_do_problema}

### Recomendacoes

{Lista de acoes sugeridas baseadas nas anomalias}
```

---

## 10. Correction Proposal (se anomalia detectada)

If anomalies detected, generate correction proposal:

### 10.1 Proposal Format

```markdown
## Proposta de Correcao

**Anomalia**: {tipo} ({severidade})

### Arquivos a Modificar

| Arquivo | Mudanca Proposta |
|---------|------------------|
| {path} | {descricao} |

### Codigo Proposto

{Bloco de codigo com mudancas sugeridas}

### Impacto Esperado

| Metrica | Atual | Esperado |
|---------|-------|----------|
| {metrica} | {valor} | {novo_valor} |
```

### 10.2 User Approval Flow

Use AskUserQuestion to get user decision:

**Question**: "Como deseja proceder com a proposta de correcao?"

**Options**:
- Aprovar: Aplicar a correcao proposta
- Rejeitar: Descartar proposta e encerrar
- Modificar: Ajustar a proposta antes de aplicar

### 10.3 Handle Response

- **Aprovar**: Apply the correction (Edit tool), continue to validation
- **Rejeitar**: HALT with message "Correcao descartada. Ciclo encerrado."
- **Modificar**: Ask for modifications, update proposal, re-ask for approval

---

## 11. Post-Correction Validation (se correcao aplicada)

### 11.1 Execute Test Suite

```bash
poetry run pytest tests/ -v --cov=src/backlog_manager
```

- **If fails**: Suggest rollback, do NOT proceed

### 11.2 Verify Coverage

Check coverage >= 80%

- **If fails**: Alert "Cobertura abaixo de 80%. Rollback sugerido."

### 11.3 Check Cyclomatic Complexity

```bash
poetry run radon cc src/ -a -nc
```

- Verify no function exceeds CC=15 (per constitution XXI)
- **If fails**: Alert "Complexidade ciclomatica excede 15. Rollback sugerido."

### 11.4 Re-collect Metrics

1. Re-execute seed script
2. Re-execute allocation tests
3. Extract metrics from new logs

### 11.5 Generate Comparison Table

```markdown
## Comparativo de Metricas

| Metrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| {nome} | {antes} | {depois} | {delta} |
```

### 11.6 Rollback Suggestion

If any validation fails:

```markdown
## Validacao Falhou

**Problema**: {descricao}

### Sugestao de Rollback

1. Reverter alteracoes: `git checkout -- {files}`
2. Verificar configuracao
3. Re-executar /analyze-allocation
```

---

## 12. Correction Documentation (se validacao bem-sucedida)

### 12.1 Generate Correction Log

Create file: `specs/016-automate-allocation-analysis/corrections/CORRECAO-{timestamp}.md`

Use template from: `specs/016-automate-allocation-analysis/corrections/TEMPLATE.md`

### 12.2 Fill Template Fields

Populate all sections:
- Problema Identificado
- Diagnostico
- Mudanca Aplicada
- Resultado (metricas antes/depois)
- Validacao (testes, cobertura, CC)
- Conclusao

---

## 13. Troubleshooting

### Seed Script Fails

1. Verificar `poetry install` foi executado
2. Verificar branch correto
3. Verificar permissoes de escrita no BD
4. Verificar EP-014 implementado

### Logs Not Found ou Vazios

1. Verificar se limpeza de logs foi executada (secao 0)
2. Verificar localizacao:
   - Windows: `%APPDATA%/BacklogManager/logs/`
   - Linux: `~/.config/backlog_manager/logs/`
3. Usar metodo inline de extracao (secao 7.1) ao inves de depender de logs

### Tests Fail

1. Verificar dependencias: `poetry install`
2. Verificar BD nao corrompido
3. Verificar configuracao pytest

### Windows-Specific Issues

1. **sqlite3 CLI nao disponivel**: Usar MCP SQLite ou `poetry run python -c "import sqlite3; ..."`
2. **Sintaxe de path**: Usar forward slashes `/` ou raw strings
3. **Variaveis de ambiente**:
   - PowerShell: `$env:APPDATA`
   - CMD: `%APPDATA%`
   - Bash/Git Bash: `$APPDATA`
4. **Output vazio em comandos Python**: Usar heredoc ou script externo

### MCP SQLite nao disponivel

1. Instalar: `pip install mcp-server-sqlite` ou usar `uvx mcp-server-sqlite`
2. Configurar em `.mcp.json` na raiz do projeto
3. Reiniciar Claude Code para carregar o MCP
4. **Fallback**: Usar extracao inline (secao 7.1)

### Metricas nao aparecem nos logs

**SOLUCAO**: Usar metodo inline de extracao (secao 7.1) que executa alocacao diretamente e retorna metricas sem depender de logs.

---

## 14. Queries Uteis via MCP SQLite

### Verificar Estado do Banco
```sql
SELECT
  COUNT(*) as total_stories,
  SUM(CASE WHEN developer_id IS NOT NULL THEN 1 ELSE 0 END) as allocated,
  SUM(CASE WHEN developer_id IS NULL THEN 1 ELSE 0 END) as eligible
FROM Story;
```

### Verificar Distribuicao por Wave
```sql
SELECT f.wave, COUNT(s.id) as stories,
       SUM(CASE WHEN s.developer_id IS NULL THEN 1 ELSE 0 END) as unallocated
FROM Story s
JOIN Feature f ON s.feature_id = f.id
GROUP BY f.wave
ORDER BY f.wave;
```

### Verificar Conflitos de Periodo
```sql
SELECT d.id, d.name, COUNT(s.id) as stories_in_period
FROM Developer d
LEFT JOIN Story s ON s.developer_id = d.id
  AND s.start_date <= '2026-03-16'
  AND s.end_date >= '2026-03-12'
GROUP BY d.id;
```

### Verificar Dependencias Bloqueadas
```sql
SELECT sd.story_id, sd.depends_on_id,
       s1.developer_id as story_dev,
       s2.developer_id as dep_dev
FROM Story_Dependency sd
JOIN Story s1 ON s1.id = sd.story_id
JOIN Story s2 ON s2.id = sd.depends_on_id
WHERE s1.developer_id IS NULL
  AND s2.developer_id IS NULL
LIMIT 20;
```

### Limpar Alocacoes para Teste
```sql
UPDATE Story SET developer_id = NULL;
```

---

## Correlation Table: Behavior to Metric

| Comportamento Observado | Metrica a Verificar | Acao Sugerida |
|-------------------------|---------------------|---------------|
| Historias nao alocadas | deadlocks_detected | Revisar dependencias circulares |
| Distribuicao desbalanceada | skill_match_ratio | Ajustar criterio de alocacao |
| Gaps no cronograma | max_idle_violations_detected | Ajustar max_idle_days |
| Datas atrasadas | date_adjustments | Revisar dependencias entre ondas |
| Muitas iteracoes | total_iterations | Verificar complexidade do backlog |

---

## End of Skill

After completion, report:
- Total execution time
- Anomalies found (count)
- Corrections applied (count)
- Final validation status
