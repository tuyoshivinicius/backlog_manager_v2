# Quickstart: Resolucao de Issues SonarQube

**Branch**: `033-sonarqube-issues-fix` | **Date**: 2026-04-01

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- Dependencias do projeto instaladas: `poetry install`

## Executar Testes (Validacao de Regressao)

```bash
# Executar todos os testes
poetry run pytest

# Executar com cobertura
poetry run pytest --cov=src/backlog_manager --cov-report=term-missing

# Executar apenas testes unitarios (mais rapidos)
poetry run pytest tests/unit/
```

## Validar Linting

```bash
# Verificar linting com ruff
poetry run ruff check .

# Auto-corrigir issues de formatacao
poetry run ruff check --fix .
```

## Verificar Issues SonarQube Localmente

O projeto esta integrado ao SonarCloud em `tuyoshivinicius_backlog_manager_v2`.
Apos push, o SonarQube re-analisa automaticamente via CI.

Para verificar status atual:
- Quality Gate: `mcp__sonarqube__get_project_quality_gate_status`
- Issues abertas: `mcp__sonarqube__search_sonar_issues_in_projects`

## Ordem de Implementacao Recomendada

1. **S3516** (BLOCKER): `story_table_model.py` - correcao de retorno
2. **S7502** (MAJOR x12): Views/ViewModels - task tracking pattern
3. **S7497** (MAJOR x4): ViewModels/Views - CancelledError re-raise
4. **S3776** (CRITICAL x17): Decomposicao de complexidade cognitiva
5. **S1192 + S5890**: Literal duplicado + type hint
6. **S1186** (CRITICAL x19): Docstrings em metodos vazios de teste
7. **S1244** (MAJOR x15): pytest.approx() para floats
8. **S108/S1172/S1854/S125**: Limpeza de codigo
9. **S100/S116/S7503/S7519/S1481/S7504**: Convencoes e otimizacoes

## Criterios de Aceite

- [ ] 0 issues BLOCKER no SonarQube
- [ ] 0 issues CRITICAL (exceto falsos positivos documentados)
- [ ] Todos os testes existentes passam
- [ ] `ruff check .` sem erros
- [ ] Quality Gate SonarQube = OK
