# Quickstart: Resolucao de Issues SonarQube

## Pre-requisitos

- Python 3.11+
- Poetry instalado
- Acesso ao SonarQube (MCP tools configurados)

## Passos para implementacao

### 1. Refatorar funcao (codigo)

Editar `scripts/seed_test_backlog.py`:
- Extrair corpo do inner loop de `_generate_inter_wave_deps()` (linha 621) para nova funcao `_try_create_inter_wave_dep()`
- A funcao auxiliar deve ser inserida imediatamente antes de `_generate_inter_wave_deps()`

### 2. Validar comportamento

```bash
# Executar testes existentes
poetry run pytest tests/ -v

# Verificar que o seed script ainda funciona
poetry run python scripts/seed_test_backlog.py
```

### 3. Marcar issues no SonarQube (via MCP)

```
# Security Hotspot → SAFE
change_security_hotspot_status(hotspotKey="AZ1I5XNA3OXD0TCP-O9_", status="REVIEWED", resolution="SAFE")

# 11 Issues naming convention → ACCEPTED
change_sonar_issue_status(key="<each_key>", status="accept")
```

### 4. Verificar quality gate

Apos re-analise no SonarQube, verificar:
- `new_security_hotspots_reviewed` = 100%
- Quality Gate = OK
- Issues abertas = 0
