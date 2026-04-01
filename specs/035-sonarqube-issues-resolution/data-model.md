# Data Model: Resolucao de Issues SonarQube

**Branch**: `035-sonarqube-issues-resolution` | **Date**: 2026-04-01

## Nota

Este feature nao introduz novas entidades, value objects ou alteracoes de schema. O escopo e:

1. **Refatoracao de funcao existente** — `_generate_inter_wave_deps()` em `scripts/seed_test_backlog.py` (extracao de funcao auxiliar, sem alteracao de comportamento)
2. **Acoes administrativas no SonarQube** — marcacao de issues/hotspots via API (sem impacto no codigo)

## Entidades Envolvidas (somente leitura)

### SonarQube Issue (externa ao projeto)
- **key**: string — identificador unico da issue
- **rule**: string — regra violada (S3776, S100, S116)
- **severity**: enum (CRITICAL, MINOR)
- **status**: enum (OPEN → ACCEPTED | FIXED)
- **component**: string — arquivo afetado

### SonarQube Security Hotspot (externa ao projeto)
- **key**: string — identificador unico do hotspot
- **status**: enum (TO_REVIEW → REVIEWED)
- **resolution**: enum (SAFE, FIXED, ACKNOWLEDGED)
- **ruleKey**: string — S2245

### Funcao Refatorada

**Antes**:
- `_generate_inter_wave_deps()` — complexidade cognitiva 16

**Depois**:
- `_generate_inter_wave_deps()` — complexidade cognitiva ~11
- `_try_create_inter_wave_dep()` — complexidade cognitiva ~2 (nova funcao auxiliar)

## State Transitions

```
Issue S3776:    OPEN → FIXED (via re-analise apos refatoracao)
Issues S100:    OPEN → ACCEPTED (via API, 9 issues)
Issues S116:    OPEN → ACCEPTED (via API, 2 issues)
Hotspot S2245:  TO_REVIEW → REVIEWED/SAFE (via API)
Quality Gate:   ERROR → OK (resultado esperado)
```
