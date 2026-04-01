# Data Model: Resolver Issues SonarQube e Aprovar Quality Gate

**Branch**: `034-sonarqube-quality-gate` | **Date**: 2026-04-01

## Resumo

Esta feature **não altera o modelo de dados** do Backlog Manager. Não há mudanças em:
- Schema SQLite
- Entidades de domínio
- DTOs
- Repositórios

## Artefatos de Configuração Afetados

### sonar-project.properties

| Campo | Estado Atual | Mudança |
|-------|-------------|---------|
| `sonar.issue.ignore.multicriteria` | Não existe | Adicionar para suprimir S100/S116 em `tests/headless_mocks.py` |

### .github/workflows/ci.yml

| Linha | Estado Atual | Mudança |
|-------|-------------|---------|
| Actions com tags | Tags de versão (v1, v4, v5, v6) | Substituir por SHA completo |

### .github/workflows/publish.yml

| Linha | Estado Atual | Mudança |
|-------|-------------|---------|
| Actions com tags | Tags de versão (v1, v4, release/v1) | Substituir por SHA completo |
| `secrets: inherit` (L17) | Herda todos os secrets | Avaliar especificação explícita |

## Arquivos de Código Afetados (Refatoração)

| Arquivo | Tipo de Mudança | Impacto |
|---------|----------------|---------|
| `src/.../allocation_service.py` | Extração de sub-funções | Sem mudança de interface pública |
| `scripts/extract_metrics.py` | Extração de sub-funções | Sem mudança de interface pública |
| `scripts/seed_test_backlog.py` | Extração de sub-funções | Sem mudança de interface pública |
| `src/.../story_table_model.py` | Extração de formatadores | Sem mudança de interface pública |
| `src/.../main_window.py` | Simplificação try/except | Sem mudança de comportamento |
| `tests/.../test_schema.py` | Remoção de código comentado | Sem mudança de comportamento |
| `tests/.../test_scheduling_use_cases.py` | Remoção de async | Sem mudança de comportamento |

## Transições de Estado

Não aplicável — nenhuma entidade de domínio é afetada.
