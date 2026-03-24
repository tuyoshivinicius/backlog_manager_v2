# Quickstart: EP-015 Melhoria Iterativa dos Algoritmos de Alocacao

**Date**: 2026-03-12

## Pre-requisitos

1. Python 3.11+ instalado
2. Poetry instalado (`pip install poetry`)
3. Dependencias do projeto instaladas (`poetry install`)
4. Seed script EP-014 funcional

## Configuracao de Ambiente

```bash
# Clonar e instalar
git clone <repo-url>
cd backlog_manager_v2
poetry install

# Verificar branch
git checkout 015-improve-allocation-scheduling
```

## Ciclo de Melhoria Iterativa (Protocolo de 6 Etapas)

### Etapa 1: Observar

```bash
# Gerar dados de teste reproduziveis
poetry run python scripts/seed_test_backlog.py --clean

# Executar alocacao (via aplicacao ou testes)
poetry run pytest tests/integration/ -k "allocation" -v
```

### Etapa 2: Descrever

Formato padrao para descricao de problema:

```markdown
## Descricao do Problema

**Acao executada**: [O que foi feito]
**Resultado visual**: [O que aconteceu na GUI/output]
**Problema observado**: [Por que esta errado]
**Expectativa**: [O que deveria acontecer]
```

### Etapa 3: Analisar Logs

```bash
# Localizar diretorio de logs
# Windows: %APPDATA%/BacklogManager/logs/
# Linux: ~/.config/backlog_manager/logs/

# Visualizar logs mais recentes
cat %APPDATA%/BacklogManager/logs/backlog_manager.log | tail -100

# Filtrar por nivel
grep "WARNING" %APPDATA%/BacklogManager/logs/backlog_manager.log
grep "INFO.*allocation" %APPDATA%/BacklogManager/logs/backlog_manager.log
```

### Etapa 4: Diagnosticar

Correlacionar comportamento visual com metricas internas:

| Comportamento | Metrica Relacionada |
|---------------|---------------------|
| Distribuicao desbalanceada | `allocations_by_load_balancing` vs `allocations_by_dependency_owner` |
| Historias nao alocadas | `deadlocks_detected`, `blocked_stories` |
| Datas atrasadas | `date_adjustments`, `validation_dependency_fixes` |
| Gaps no cronograma | `max_idle_violations_detected` |

### Etapa 5: Propor Correcao

Formato de proposta:

```markdown
## Proposta de Correcao

**Arquivos a modificar**:
- `src/backlog_manager/domain/services/allocation_service.py`

**Mudancas propostas**:
1. [Descricao da mudanca 1]
2. [Descricao da mudanca 2]

**Impacto esperado**:
- Metrica X: de Y para Z
- Performance: sem impacto (ou: +N%)
```

### Etapa 6: Validar

```bash
# Executar suite de testes completa
poetry run pytest tests/ -v --cov=src/backlog_manager --cov-report=term-missing

# Verificar cobertura >= 80%
# Verificar todos os testes passam

# Re-executar seed + alocacao para confirmar correcao
poetry run python scripts/seed_test_backlog.py --clean
poetry run pytest tests/integration/ -k "allocation" -v
```

## Comandos Uteis

```bash
# Executar testes unitarios apenas
poetry run pytest tests/unit/ -v

# Executar testes de integracao apenas
poetry run pytest tests/integration/ -v

# Verificar tipos
poetry run mypy src/backlog_manager/

# Formatar codigo
poetry run black src/ tests/
poetry run isort src/ tests/

# Verificar complexidade ciclomatica
poetry run radon cc src/backlog_manager/ -a -s

# Habilitar logs DEBUG para diagnostico detalhado
# No codigo de teste:
import logging
logging.getLogger("backlog_manager").setLevel(logging.DEBUG)
```

## Metricas de Sucesso

| Criterio | Valor Esperado | Como Verificar |
|----------|---------------|----------------|
| SC-001 | 16 metricas no log | `grep "allocation_metrics" *.log` |
| SC-002 | <= 5s para 190 historias | `AllocationMetrics.total_time_seconds` |
| SC-003 | <= 5s para 100 historias | `AllocationMetrics.total_time_seconds` |
| SC-005 | Todos testes passam | `pytest` exit code 0 |
| SC-006 | Cobertura >= 80% | `pytest --cov` |
| SC-007 | CC <= 15 | `radon cc -a -s` |
| SC-009 | <= 30s para 500 historias | Teste de performance |

## Troubleshooting

## Reproducao de Cenarios

Para reproduzir exatamente uma execucao de alocacao, use `random_seed`:

```python
from backlog_manager.domain.services import AllocationConfig, AllocationService
from datetime import date

# Configuracao com seed fixo para reproducibilidade
config = AllocationConfig(
    velocity=2.0,
    project_start_date=date(2026, 3, 2),
    random_seed=42,  # Seed fixa garante mesmo resultado
)

# Duas execucoes com mesmo seed produzem resultado identico
result1 = AllocationService.allocate_stories(stories, developers, ...)
result2 = AllocationService.allocate_stories(stories, developers, ...)
# result1 == result2 (mesmas alocacoes)
```

### Passos para Reproduzir um Bug

1. **Anotar seed usado** (se nenhum especificado, gerar novo)
2. **Regenerar dados**: `poetry run python scripts/seed_test_backlog.py --clean`
3. **Executar com mesma config**:
   ```python
   config = AllocationConfig(..., random_seed=<seed_anotada>)
   ```
4. **Comparar metricas**: O resultado deve ser identico

| SC-009 | <= 30s para 500 historias | Teste de performance |

## Troubleshooting

### Logs nao aparecem

```python
# Verificar se logging foi inicializado
from backlog_manager.infrastructure.logging import setup_logging
import logging

setup_logging(level=logging.DEBUG)
```

### Diretorio de logs nao existe

```python
from backlog_manager.infrastructure.logging import get_log_directory
print(get_log_directory())  # Deve criar o diretorio se nao existir
```

### Performance degradada com DEBUG

```python
# Usar INFO em producao
setup_logging(level=logging.INFO)
```
