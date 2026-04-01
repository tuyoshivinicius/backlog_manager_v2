# Quickstart: Resolver Issues SonarQube e Aprovar Quality Gate

**Branch**: `034-sonarqube-quality-gate` | **Date**: 2026-04-01

## Pré-requisitos

- Python 3.11+
- Poetry instalado
- Dependências instaladas: `poetry install`
- Acesso ao SonarCloud (token configurado)

## Validação Local

### 1. Executar testes após refatorações

```bash
poetry run pytest tests/ -v --tb=short
```

### 2. Verificar formatação e linting

```bash
poetry run black --check src/ scripts/ tests/
poetry run isort --check-only src/ scripts/ tests/
```

### 3. Verificar complexidade cognitiva (aproximação local)

```bash
# radon para complexidade ciclomática (proxy)
poetry run radon cc src/backlog_manager/domain/services/allocation_service.py -s -n C
poetry run radon cc scripts/extract_metrics.py -s -n C
poetry run radon cc scripts/seed_test_backlog.py -s -n C
poetry run radon cc src/backlog_manager/presentation/viewmodels/story_table_model.py -s -n C
```

### 4. Validação SonarQube

A validação definitiva ocorre no SonarCloud após push:
- Quality Gate: ERROR → OK
- Security Hotspots Reviewed: 0% → 100%
- Issues OPEN: 20 → 0

### 5. Revisão de Security Hotspots

Os hotspots devem ser revisados diretamente na interface do SonarCloud ou via MCP:
- 7 pseudo-random → SAFE
- 1 regex DoS → SAFE
- 17 diretórios públicos → SAFE
- 6 SHA de commit → FIXED (após substituição)
- 1 workflow permission → ACKNOWLEDGED ou FIXED

## Ordem de Execução Recomendada

1. **Code smells simples** (S125, S2737, S7503) — correções rápidas
2. **Naming conventions** (S100/S116) — configuração sonar-project.properties
3. **Complexidade cognitiva** (S3776) — refatorações com testes
4. **GitHub Actions SHA** (S7637) — substituição de tags
5. **Security hotspots** — revisão no SonarCloud
6. **Validação final** — push e verificar Quality Gate
