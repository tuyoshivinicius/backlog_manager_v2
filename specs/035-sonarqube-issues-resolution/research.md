# Research: Resolucao de Issues SonarQube para Quality Gate

**Branch**: `035-sonarqube-issues-resolution` | **Date**: 2026-04-01

## 1. Estado Atual do SonarQube (dados coletados via MCP)

### Quality Gate Status: ERROR

| Condicao | Status | Threshold | Valor Atual |
|----------|--------|-----------|-------------|
| new_reliability_rating | OK | 1 | 1 |
| new_security_rating | OK | 1 | 1 |
| new_maintainability_rating | OK | 1 | 1 |
| new_duplicated_lines_density | OK | 3% | 1.6% |
| **new_security_hotspots_reviewed** | **ERROR** | **100%** | **94.4%** |

**Causa raiz**: 1 security hotspot TO_REVIEW (key: `AZ1I5XNA3OXD0TCP-O9_`) em `scripts/seed_test_backlog.py:572`.

### Metricas Gerais

| Metrica | Valor |
|---------|-------|
| Bugs | 0 |
| Vulnerabilities | 0 |
| Code Smells | 12 |
| Lines of Code | 26,815 |
| Duplicated Lines | 1.4% |
| Cognitive Complexity (total) | 1,611 |
| Security Hotspots Reviewed (overall) | 96.0% |

### Issues Abertas (12 total)

| # | Key | Regra | Severidade | Arquivo | Linha | Descricao |
|---|-----|-------|------------|---------|-------|-----------|
| 1 | AZ1H3y5IMsoPwz0FZVip | S3776 | CRITICAL | scripts/seed_test_backlog.py | 621 | Complexidade cognitiva 16 > 15 |
| 2-10 | (9 issues) | S100 | MINOR | tests/headless_mocks.py | 70-104 | Metodos camelCase (API Qt) |
| 11-12 | (2 issues) | S116 | MINOR | tests/headless_mocks.py | 120-123 | Fields PascalCase (enums Qt) |

### Security Hotspots

- **TO_REVIEW (1)**: `AZ1I5XNA3OXD0TCP-O9_` — S2245 (pseudorandom) em `seed_test_backlog.py:572` — uso de `random.choice()` em script de geracao de dados de teste
- **REVIEWED/SAFE (24)**: Todos os demais hotspots ja foram revisados e marcados como SAFE

## 2. Analise de Complexidade Cognitiva — `_generate_inter_wave_deps()`

### Calculo detalhado (S3776)

```python
def _generate_inter_wave_deps(...):
    count = 0
    for wave in range(2, 8):                              # +1 (for, nesting 0)
        wave_stories = story_by_wave.get(wave, [])
        earlier_waves = _collect_earlier_wave_stories(...)
        for story_id, _story_idx in wave_stories:          # +1 (for) +1 (nesting=1) = +2
            if count >= target:                             # +1 (if) +2 (nesting=2) = +3
                return count
            if earlier_waves and random.random() < 0.3:    # +1 (if) +2 (nesting=2) +1 (and) = +4
                depends_on = random.choice(earlier_waves)
                if _try_add_dependency(...):                # +1 (if) +3 (nesting=3) = +4
                    count += 1
        if count >= target:                                # +1 (if) +1 (nesting=1) = +2
            break
    return count
# TOTAL: 1 + 2 + 3 + 4 + 4 + 2 = 16
```

### Estrategia de reducao

- **Decision**: Extrair o corpo do inner loop para funcao auxiliar `_try_create_inter_wave_dep()`
- **Rationale**: Remove 1 nivel de nesting do `if _try_add_dependency` (de +4 para +2) e do `if earlier_waves and ...` (de +4 para +2), reduzindo a complexidade total da funcao principal para ~8. Abordagem recomendada pela propria regra S3776 ("Break down large functions").
- **Alternatives considered**:
  - Extrair apenas o `and` para uma funcao booleana: reduziria de 16 para 15 (exatamente no limite). Fragil — qualquer mudanca futura romperia o limite novamente.
  - Early return no outer loop: nao aplicavel — o `if count >= target: break` ja esta no final.

### Funcao auxiliar proposta

```python
def _try_create_inter_wave_dep(
    story_id: str,
    earlier_waves: list[tuple[str, int]],
    dependencies: list[tuple[str, str]],
    story_dep_count: dict[str, int],
) -> bool:
    """Attempt to create one inter-wave dependency for a story."""
    if not earlier_waves or random.random() >= 0.3:
        return False
    depends_on = random.choice(earlier_waves)
    return _try_add_dependency(story_id, depends_on[0], dependencies, story_dep_count)
```

Complexidade cognitiva da funcao auxiliar: `if not ... or ...` = +1 (if) +1 (or) = 2. Compliant.

Complexidade da funcao principal apos refatoracao:
```
for wave: +1
  for story: +2
    if count >= target: +3
    if _try_create_inter_wave_dep(): +3
      count += 1
  if count >= target: +2
# TOTAL: 1 + 2 + 3 + 3 + 2 = 11
```

## 3. Security Hotspot S2245 — Analise de Seguranca

- **Decision**: Marcar como SAFE via API SonarQube
- **Rationale**: O hotspot na linha 572 de `seed_test_backlog.py` usa `random.choice()` dentro de um script de seed para gerar dados de teste. O script usa `random.seed(RANDOM_SEED)` com seed fixo para garantir reprodutibilidade. Nao ha uso em contexto criptografico ou de seguranca. O mesmo tipo de hotspot (S2245) ja foi revisado e marcado como SAFE em 7 outras ocorrencias no mesmo arquivo.
- **Alternatives considered**: Substituir `random` por `secrets` — desnecessario e quebraria a reprodutibilidade com seed fixo.

## 4. Issues de Naming Convention (S100/S116)

- **Decision**: Marcar como ACCEPTED (Won't Fix) via API SonarQube
- **Rationale**: Os 9 metodos camelCase (`beginResetModel`, `endResetModel`, `beginInsertRows`, `endInsertRows`, `beginRemoveRows`, `endRemoveRows`, `beginGroup`, `endGroup`, `setValue`) e 2 campos PascalCase (`IniFormat`, `UserScope`) em `tests/headless_mocks.py` sao mocks que DEVEM replicar a interface da API Qt/PySide6. Renomea-los para snake_case quebraria a compatibilidade com o framework.
- **Alternatives considered**: Usar `# noqa: N802` / `# noqa: N815` (ja presente no codigo para flake8, mas SonarQube ignora esses comentarios — necessario marcar via API).

## 5. Chaves das Issues para Acoes via API

### Issues S100 (metodos camelCase) — ACCEPTED
| Metodo | Key SonarQube |
|--------|---------------|
| beginResetModel | AZ1HXJJBhkGAnEFrWQEw |
| endResetModel | AZ1HXJJBhkGAnEFrWQEx |
| beginInsertRows | AZ1HXJJBhkGAnEFrWQEz |
| endInsertRows | AZ1HXJJBhkGAnEFrWQE1 |
| beginRemoveRows | AZ1HXJJBhkGAnEFrWQE3 |
| endRemoveRows | AZ1HXJJBhkGAnEFrWQE5 |
| beginGroup | AZ1HXJJBhkGAnEFrWQE8 |
| endGroup | AZ1HXJJBhkGAnEFrWQE9 |
| setValue | AZ1HXJJBhkGAnEFrWQE- |

### Issues S116 (fields PascalCase) — ACCEPTED
| Field | Key SonarQube |
|-------|---------------|
| IniFormat | AZ1HXJJBhkGAnEFrWQFA |
| UserScope | AZ1HXJJBhkGAnEFrWQFB |

### Security Hotspot S2245 — SAFE
| Hotspot Key |
|-------------|
| AZ1I5XNA3OXD0TCP-O9_ |

### Issue S3776 — Correcao via codigo
| Issue Key |
|-----------|
| AZ1H3y5IMsoPwz0FZVip |
