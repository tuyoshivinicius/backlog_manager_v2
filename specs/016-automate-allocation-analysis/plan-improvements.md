# Plano de Melhorias - Skill analyze-allocation

**Data**: 2026-03-23
**Baseado em**: Execução real da skill e problemas identificados

---

## 1. Padronização de Caminhos de Banco de Dados

### Problema
Os scripts `seed_test_backlog.py`, `extract_metrics.py` e `check_deps.py` usavam caminhos diferentes para o banco de dados, causando análise de dados inconsistentes.

### Solução
Criar módulo centralizado para resolução de caminhos.

### Tarefas
- [ ] Criar `scripts/common/db_path.py` com função `get_analysis_db_path()`
- [ ] Atualizar `seed_test_backlog.py` para usar o módulo comum
- [ ] Atualizar `extract_metrics.py` para usar o módulo comum
- [ ] Atualizar `check_deps.py` para usar o módulo comum
- [ ] Adicionar flag `--db-path` consistente em todos os scripts
- [ ] Logar caminho do banco no início de cada script

### Código Proposto
```python
# scripts/common/db_path.py
from pathlib import Path
import os

def get_analysis_db_path(custom_path: Path | None = None) -> Path:
    """Get database path for analysis scripts.

    Priority:
    1. Custom path if provided
    2. Environment variable BACKLOG_DB_PATH
    3. Default app data location
    """
    if custom_path:
        return custom_path

    env_path = os.environ.get("BACKLOG_DB_PATH")
    if env_path:
        return Path(env_path)

    # Import from main app to ensure consistency
    from backlog_manager.infrastructure.database.sqlite_connection import get_database_path
    return get_database_path()
```

---

## 2. Validação de Pré-condições na Skill

### Problema
A skill executou alocação sem verificar se as histórias tinham datas calculadas, levando a diagnóstico incorreto de deadlocks.

### Solução
Adicionar etapa de validação de dados antes da análise.

### Tarefas
- [ ] Adicionar seção "Data Validation" na skill após "Pre-requisite Verification"
- [ ] Verificar se histórias têm `start_date` e `end_date`
- [ ] Verificar se developers existem
- [ ] Verificar integridade das dependências
- [ ] Gerar relatório de problemas de dados antes de prosseguir

### Atualização na Skill
```markdown
## 1.4 Data Validation

Antes de executar a alocação, validar dados:

```bash
poetry run python scripts/validate_allocation_data.py
```

**Checks obrigatórios**:
| Check | Query | Threshold |
|-------|-------|-----------|
| Stories com datas | `SELECT COUNT(*) FROM Story WHERE start_date IS NULL OR end_date IS NULL` | = 0 |
| Developers ativos | `SELECT COUNT(*) FROM Developer` | > 0 |
| Dependências válidas | Verificar que todas as dependências apontam para histórias existentes | 100% |

**Se falhar**: HALT com mensagem detalhada e sugestão de correção.
```

---

## 3. Script de Validação de Dados

### Problema
Não existe ferramenta para verificar integridade dos dados antes da análise.

### Solução
Criar script `validate_allocation_data.py`.

### Tarefas
- [ ] Criar `scripts/validate_allocation_data.py`
- [ ] Implementar checks de integridade
- [ ] Gerar relatório estruturado
- [ ] Sugerir comandos de correção

### Código Proposto
```python
# scripts/validate_allocation_data.py
"""Validate data integrity for allocation analysis."""

async def validate_data():
    """Run all validation checks."""
    checks = [
        ("Stories with dates", check_story_dates),
        ("Active developers", check_developers),
        ("Valid dependencies", check_dependencies),
        ("Feature waves", check_feature_waves),
    ]

    results = []
    for name, check_fn in checks:
        passed, message = await check_fn()
        results.append((name, passed, message))

    # Generate report
    all_passed = all(r[1] for r in results)

    print("=" * 60)
    print("DATA VALIDATION REPORT")
    print("=" * 60)
    for name, passed, message in results:
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {name}: {message}")

    if not all_passed:
        print("\nSUGGESTED FIXES:")
        # Print fix suggestions

    return all_passed
```

---

## 4. Diagnóstico Automático de Deadlocks

### Problema
A skill detecta deadlocks mas não identifica automaticamente a causa raiz.

### Solução
Adicionar análise de causa raiz para deadlocks.

### Tarefas
- [ ] Criar função `diagnose_deadlock()` no script de análise
- [ ] Categorizar causas de deadlock:
  - Histórias sem datas
  - Dependências circulares
  - Dependências para histórias inexistentes
  - Todas as histórias com dependências não satisfeitas
- [ ] Incluir diagnóstico no relatório de anomalias

### Código Proposto
```python
def diagnose_deadlock(wave: int, blocked_stories: list[str]) -> dict:
    """Diagnose the cause of a deadlock.

    Returns:
        dict with:
        - cause: str (primary cause)
        - details: list[str] (specific issues)
        - fix_suggestion: str
    """
    causes = []

    # Check 1: Stories without dates
    stories_without_dates = [s for s in blocked_stories if not has_dates(s)]
    if stories_without_dates:
        causes.append({
            "type": "MISSING_DATES",
            "count": len(stories_without_dates),
            "fix": "Execute SchedulingService.calculate_schedule() before allocation"
        })

    # Check 2: Unsatisfied dependencies
    unsatisfied = [s for s in blocked_stories if has_unsatisfied_deps(s)]
    if unsatisfied:
        causes.append({
            "type": "UNSATISFIED_DEPENDENCIES",
            "count": len(unsatisfied),
            "fix": "Allocate dependency stories first or remove blocking dependencies"
        })

    # Check 3: Circular dependencies
    circular = detect_circular_deps(blocked_stories)
    if circular:
        causes.append({
            "type": "CIRCULAR_DEPENDENCIES",
            "cycles": circular,
            "fix": "Remove one dependency from each cycle"
        })

    return {
        "wave": wave,
        "blocked_count": len(blocked_stories),
        "causes": causes,
        "primary_cause": causes[0]["type"] if causes else "UNKNOWN"
    }
```

---

## 5. Métricas em Formato JSON Estruturado

### Problema
Extração de métricas dos logs requer parsing complexo.

### Solução
Logar métricas em formato JSON para fácil extração.

### Tarefas
- [ ] Atualizar `execute_allocation.py` para logar métricas em JSON
- [ ] Criar script `parse_allocation_logs.py` para extrair métricas
- [ ] Atualizar skill para usar o novo parser

### Código Proposto
```python
# Em execute_allocation.py
logger.info(
    "ALLOCATION_METRICS_JSON: %s",
    json.dumps({
        "timestamp": datetime.now().isoformat(),
        "metrics": {
            "total_time_seconds": metrics.total_time_seconds,
            "stories_processed": metrics.stories_processed,
            # ... todas as 16 métricas
        }
    })
)
```

---

## 6. Feedback de Caminho do Banco

### Problema
Não fica claro qual banco de dados está sendo usado durante a análise.

### Solução
Adicionar logging explícito do caminho do banco.

### Tarefas
- [ ] Atualizar todos os scripts para logar caminho no início
- [ ] Adicionar verificação de existência do arquivo
- [ ] Mostrar tamanho e última modificação do arquivo

### Código Proposto
```python
def log_database_info(db_path: Path) -> None:
    """Log database file information."""
    print(f"Database: {db_path}")
    if db_path.exists():
        stat = db_path.stat()
        print(f"  Size: {stat.st_size / 1024:.1f} KB")
        print(f"  Modified: {datetime.fromtimestamp(stat.st_mtime)}")
    else:
        print("  WARNING: File does not exist!")
```

---

## 7. Atualização da Skill

### Tarefas
- [ ] Adicionar seção de validação de dados (item 2)
- [ ] Adicionar diagnóstico automático de deadlocks (item 4)
- [ ] Melhorar mensagens de erro com sugestões específicas
- [ ] Adicionar flag `--verbose` para debug detalhado

---

## Priorização

| Prioridade | Item | Justificativa |
|------------|------|---------------|
| P0 | 2, 3 | Evita diagnósticos incorretos |
| P1 | 1 | Evita confusão de dados |
| P1 | 4 | Acelera troubleshooting |
| P2 | 5 | Melhora automação |
| P2 | 6 | Facilita debug |
| P3 | 7 | Consolidação |

---

## Estimativa de Esforço

| Item | Complexidade | Arquivos Afetados |
|------|--------------|-------------------|
| 1 | Baixa | 4 scripts |
| 2 | Média | 1 skill, 1 script novo |
| 3 | Média | 1 script novo |
| 4 | Alta | allocation_service.py, extract_metrics.py |
| 5 | Baixa | execute_allocation.py |
| 6 | Baixa | 3 scripts |
| 7 | Média | 1 skill |

---

## Critérios de Aceitação

1. **Validação de dados**: Skill detecta histórias sem datas e HALT antes de alocação
2. **Caminhos consistentes**: Todos os scripts usam mesmo banco por padrão
3. **Diagnóstico de deadlock**: Relatório inclui causa raiz identificada
4. **Métricas JSON**: `grep "ALLOCATION_METRICS_JSON" logs` retorna JSON válido
5. **Feedback de banco**: Cada script mostra caminho do banco no início

---

## Atualização 2026-03-23T21:55 - Execução Real da Skill

### Problemas Identificados Durante Execução

| # | Problema | Impacto | Solução Aplicada |
|---|----------|---------|------------------|
| 1 | Logs antigos sem ALLOCATION_METRICS_JSON | Extração de métricas falhou | Adicionada seção 0 - Log Cleanup |
| 2 | Falta de tracking de progresso | Difícil acompanhar execução | Adicionada seção 0.5 + TodoWrite |
| 3 | Scripts referenciados não existem | Erros de execução | Marcados como opcionais |
| 4 | Dependência excessiva de logs | Métricas indisponíveis | Adicionado método inline (seção 7.1) |

### Mudanças Implementadas na Skill

1. **Seção 0 - Log Cleanup**: Limpa logs antigos no início para garantir dados frescos
2. **Seção 0.5 - Progress Tracking**: Uso obrigatório de TodoWrite
3. **TodoWrite em allowed-tools**: Ferramenta disponível para tracking
4. **Scripts opcionais**: `extract_metrics.py` e `validate_allocation_data.py` são opcionais
5. **Método inline de extração**: Seção 7.1 com execução direta de métricas
6. **Troubleshooting atualizado**: Soluções para logs vazios

### Métricas da Execução Real

```json
{
  "total_time_seconds": 0.0258,
  "stories_processed": 190,
  "stories_allocated": 181,
  "waves_processed": 7,
  "deadlocks_detected": 5,
  "skill_match_ratio": 0.3978,
  "max_idle_violations_detected": 54
}
```

### Anomalias Detectadas

| Severidade | Anomalia | Valor | Threshold |
|------------|----------|-------|-----------|
| CRITICAL | deadlocks_detected | 5 | > 0 |
| HIGH | max_idle_violations_detected | 54 | > 5 |
| MEDIUM | skill_match_ratio | 0.3978 | < 0.5 |

### Próximos Passos (Prioridade Atualizada)

| Prioridade | Tarefa | Status |
|------------|--------|--------|
| P0 | Criar `scripts/extract_metrics.py` | PENDENTE |
| P0 | Criar `scripts/validate_allocation_data.py` | PENDENTE |
| P1 | Criar `scripts/diagnose_dependencies.py` | PENDENTE |
| P2 | Simplificar fluxo da skill | PENDENTE |
| P3 | Adicionar testes para a skill | PENDENTE |

### Lições Aprendidas

1. **Não depender de logs externos**: Usar execução direta sempre que possível
2. **Limpar estado antes de análise**: Logs antigos confundem a análise
3. **Scripts opcionais com fallbacks**: Sempre ter alternativa inline
4. **TodoWrite é essencial**: Tracking de progresso melhora experiência
