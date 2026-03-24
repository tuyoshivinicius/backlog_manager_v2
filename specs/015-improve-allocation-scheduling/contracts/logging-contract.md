# Logging Contract: EP-015 Allocation Logging

**Date**: 2026-03-12
**Type**: Internal API (Infrastructure Layer)

## Escopo

Este contrato define o formato e conteudo esperado dos logs gerados pelo `AllocationService` para suportar ciclos de melhoria iterativa.

## Formato de Log

Conforme Constituicao (Principio XVII):

```
%(asctime)s - %(levelname)s - %(name)s - %(message)s
```

Exemplo:
```
2026-03-12T14:30:00 - INFO - backlog_manager.domain.services.allocation_service - Alocacao completa: 190/190 historias (2.34s, 7 ondas, 45 iteracoes)
```

## Logs Obrigatorios (FR-001 a FR-005)

### 1. Sumario de Metricas (FR-001)

**Nivel**: INFO
**Trigger**: Final de `allocate_stories()`
**Formato**:
```
Alocacao completa: {allocated}/{processed} historias ({time}s, {waves} ondas, {iterations} iteracoes)
```

**Campos extras (structured)**:
```python
extra={
    "allocation_metrics": {
        "total_time_seconds": float,
        "stories_processed": int,
        "stories_allocated": int,
        "waves_processed": int,
        "total_iterations": int,
        "allocations_by_dependency_owner": int,
        "allocations_by_load_balancing": int,
        "deadlocks_detected": int,
        "date_adjustments": int,
        "validation_reallocations": int,
        "validation_dependency_fixes": int,
        "validation_conflict_fixes": int,
        "max_idle_violations_detected": int,
        "max_idle_violations_fixed": int,
        "failed_reallocations": int,
        "iterations_per_wave": dict[int, int]
    }
}
```

### 2. Decisao de Selecao de Desenvolvedor (FR-002)

**Nivel**: DEBUG
**Trigger**: Cada alocacao em `_select_developer()` ou `_allocate_by_wave()`
**Formato**:
```
Historia {story_id}: alocada para dev {dev_id} ({reason})
```

**Valores de `reason`**:
- `DEPENDENCY_OWNER`: Proprietario da dependencia mais recente
- `LOAD_BALANCING`: Balanceamento por contagem de historias
- `FALLBACK_LOAD_BALANCING`: Fallback quando owner nao encontrado

### 3. Deteccao de Deadlock (FR-003)

**Nivel**: WARNING
**Trigger**: `_allocate_by_wave()` quando sem progresso
**Formato**:
```
Onda {wave}: deadlock detectado - {count} historias bloqueadas: {story_ids}
```

**Campos extras (structured)**:
```python
extra={
    "deadlock": {
        "wave": int,
        "blocked_count": int,
        "blocked_stories": list[str],
        "max_iterations_reached": bool
    }
}
```

### 4. Violacao de Ociosidade (FR-004)

**Nivel**: WARNING (intra-wave) ou INFO (inter-wave)
**Trigger**: `_check_idleness()`
**Formato intra-wave**:
```
Ociosidade detectada: dev {dev_name} ({dev_id}) - {days} dias na onda {wave}
```

**Formato inter-wave**:
```
Ociosidade inter-wave: dev {dev_name} ({dev_id}) - {days} dias entre ondas {from_wave} e {to_wave}
```

### 5. Inicio/Fim de Onda (FR-005)

**Nivel**: INFO
**Trigger**: Entrada e saida de `_allocate_by_wave()`

**Formato inicio**:
```
Onda {wave}: iniciando alocacao de {count} historias
```

**Formato fim**:
```
Onda {wave}: completa - {allocated}/{total} historias em {time}s ({iterations} iteracoes)
```

## Logs Opcionais (DEBUG)

### Ajuste de Data

**Formato**:
```
Historia {story_id}: data ajustada de {old_date} para {new_date} ({reason})
```

### Resolucao de Conflito

**Formato**:
```
Conflito resolvido: historia {story_id} movida para {new_start} - {new_end}
```

### Correcao de Dependencia

**Formato**:
```
Dependencia corrigida: historia {story_id} movida apos {dep_id} ({new_start})
```

## Verificacao de Conformidade

Para verificar que os logs estao conforme este contrato:

```python
# Em testes de integracao
import re

LOG_PATTERNS = {
    "allocation_complete": r"Alocacao completa: \d+/\d+ historias \(\d+\.\d+s, \d+ ondas, \d+ iteracoes\)",
    "wave_start": r"Onda \d+: iniciando alocacao de \d+ historias",
    "wave_complete": r"Onda \d+: completa - \d+/\d+ historias em \d+\.\d+s \(\d+ iteracoes\)",
    "deadlock": r"Onda \d+: deadlock detectado - \d+ historias bloqueadas",
    "idleness_intra": r"Ociosidade detectada: dev .+ \(\d+\) - \d+ dias na onda \d+",
    "idleness_inter": r"Ociosidade inter-wave: dev .+ \(\d+\) - \d+ dias entre ondas \d+ e \d+",
}
```
