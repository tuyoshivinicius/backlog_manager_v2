# Research: Resolver Issues SonarQube e Aprovar Quality Gate

**Branch**: `034-sonarqube-quality-gate` | **Date**: 2026-04-01

## Estado Atual do SonarQube (dados coletados via MCP)

### Quality Gate: ERROR

| Condição | Status | Threshold | Valor Atual |
|----------|--------|-----------|-------------|
| new_reliability_rating | OK | 1 | 1 |
| new_security_rating | OK | 1 | 1 |
| new_maintainability_rating | OK | 1 | 1 |
| new_duplicated_lines_density | OK | 3% | 1.7% |
| **new_security_hotspots_reviewed** | **ERROR** | **100%** | **0.0%** |

**Bloqueador único**: 0% de security hotspots revisados (threshold: 100%).

### Métricas Gerais

| Métrica | Valor |
|---------|-------|
| Lines of Code | 26.764 |
| Cognitive Complexity (total) | 1.640 |
| Code Smells | 20 |
| Bugs | 0 |
| Vulnerabilities | 0 |
| Duplicated Lines | 1.4% |
| Security Hotspots Reviewed | 0.0% |

### Issues OPEN (20 total)

| Severidade | Quantidade | Regra | Descrição |
|------------|-----------|-------|-----------|
| CRITICAL | 6 | S3776 | Complexidade cognitiva acima de 15 |
| MAJOR | 1 | S125 | Código comentado |
| MINOR | 2 | S2737, S7503 | Except vazio, async desnecessário |
| MINOR | 11 | S100, S116 | Naming conventions (mocks Qt) |

### Security Hotspots TO_REVIEW (32 total)

| Categoria | Quantidade | Severidade | Arquivos |
|-----------|-----------|------------|----------|
| Pseudo-random (S2245) | 7 | MEDIUM | `scripts/seed_test_backlog.py` |
| Regex DoS (S5852) | 1 | MEDIUM | `tests/.../test_allocation_logging.py` |
| Workflow permission (S7635) | 1 | MEDIUM | `.github/workflows/publish.yml` |
| SHA de commit (S7637) | 6 | LOW | `.github/workflows/ci.yml`, `publish.yml` |
| Diretórios públicos (S5443) | 17 | LOW | `tests/.../test_excel_viewmodel.py` |

---

## R1: Refatoração de Complexidade Cognitiva (S3776)

### R1.1: `allocation_service.py:1071` — `_run_allocation_loop` (22→≤15)

- **Decisão**: Extrair sub-funções para achatamento de nesting
- **Racional**: A função tem while→for→if→if com 4 níveis de aninhamento. A complexidade vem do bloco de alocação com branches para available_devs/adjusted.
- **Alternativas consideradas**: Reescrever com early returns — rejeitado pois o loop principal precisa manter estado de progresso.
- **Estratégia**: Extrair `_try_allocate_story()` (lógica de alocação por story) e `_process_with_available_devs()` (seleção de dev + alocação). Cada sub-função recebe o contexto necessário e retorna bool indicando progresso.

### R1.2: `extract_metrics.py:254` — `_find_circular_dependencies` (19→≤15)

- **Decisão**: Extrair helper para deduplicação de ciclos
- **Racional**: A função usa DFS com marcação de três cores e tem loop aninhado para detecção de ciclos + registro de resultados.
- **Estratégia**: Extrair `_register_cycle()` para isolar a lógica de deduplicação e adição de ciclos ao resultado.

### R1.3: `extract_metrics.py:557` — `_print_blocked_story_detail` (17→≤15)

- **Decisão**: Extrair formatação de seções
- **Racional**: Função procedural com múltiplos if/elif para formatação condicional de dependências e disponibilidade de devs.
- **Estratégia**: Extrair `_format_dependencies_section()` e `_format_devs_section()`.

### R1.4: `seed_test_backlog.py:563` — `_generate_intra_wave_deps` (16→≤15)

- **Decisão**: Extrair lógica de tentativa de dependência
- **Racional**: Loops aninhados (wave→story) com lógica condicional de filtro e criação de dependência.
- **Estratégia**: Extrair `_try_add_intra_wave_dep()` com a lógica de seleção aleatória e adição da dependência.

### R1.5: `seed_test_backlog.py:600` — `_generate_inter_wave_deps` (19→≤15)

- **Decisão**: Extrair coleta de ondas anteriores e tentativa de dependência
- **Racional**: Triple-nested (wave→story→earlier_waves) com 3 níveis de controle de fluxo.
- **Estratégia**: Extrair `_collect_earlier_wave_stories()` e `_try_add_inter_wave_dep()`.

### R1.6: `story_table_model.py:230` — `_get_display_value` (16→≤15)

- **Decisão**: Extrair formatadores especializados
- **Racional**: Match statement grande com 13 cases e ternários condicionais em cada case.
- **Estratégia**: Extrair helpers como `_format_optional_string()`, `_format_date()`, `_format_numeric_field()` para reduzir branches dentro do match. Alternativa: usar dicionário de mapeamento coluna→formatador.

---

## R2: Security Hotspots — Estratégia de Revisão

### R2.1: Pseudo-random em seed_test_backlog.py (7 hotspots) → SAFE

- **Decisão**: Marcar como SAFE
- **Racional**: O script `seed_test_backlog.py` gera dados fictícios para testes. O uso de `random` é intencional e não envolve dados sensíveis, criptografia ou segurança. Não há risco de previsibilidade de valores.

### R2.2: Regex DoS em test_allocation_logging.py (1 hotspot) → SAFE

- **Decisão**: Marcar como SAFE
- **Racional**: A regex está em um arquivo de teste unitário. O input é controlado pelo próprio teste — não há exposição a entrada de usuário externo.

### R2.3: Workflow permission em publish.yml (1 hotspot) → ACKNOWLEDGED/FIXED

- **Decisão**: Avaliar se é possível especificar secrets individualmente; se o workflow reusável exigir `secrets: inherit`, marcar como ACKNOWLEDGED com justificativa.
- **Racional**: `secrets: inherit` é necessário para que o workflow chamado (ci) acesse CODECOV_TOKEN e SONAR_TOKEN. A alternativa é enumerar os secrets explicitamente.

### R2.4: SHA de commit em GitHub Actions (6 hotspots) → FIXED

- **Decisão**: Substituir tags por SHA completo do commit correspondente
- **Racional**: Previne ataques de supply chain onde uma tag pode ser movida para apontar para código malicioso.
- **Actions a substituir**:
  - `ci.yml:25` — `snok/install-poetry@v1` → SHA
  - `ci.yml:90` — `codecov/codecov-action@v5` → SHA
  - `ci.yml:96` — `SonarSource/sonarqube-scan-action@v6` → SHA
  - `publish.yml:33` — `snok/install-poetry@v1` → SHA
  - `publish.yml:67` — `pypa/gh-action-pypi-publish@release/v1` → SHA
  - `publish.yml:90` — `pypa/gh-action-pypi-publish@release/v1` → SHA
  - **Nota**: `actions/checkout@v4`, `actions/setup-python@v5`, `actions/cache@v4`, `actions/upload-artifact@v4`, `actions/download-artifact@v4` também usam tags e devem ser substituídos.

### R2.5: Diretórios públicos em test_excel_viewmodel.py (17 hotspots) → SAFE

- **Decisão**: Marcar como SAFE
- **Racional**: Os testes usam `tmp_path` do pytest, que gera diretórios temporários seguros e isolados. Não há exposição a escrita pública em produção.

---

## R3: Code Smells

### R3.1: Código comentado em test_schema.py:86 (S125) → Remover

- **Decisão**: Remover o comentário inline ou bloco comentado
- **Racional**: Código comentado é dívida técnica que polui o codebase.

### R3.2: Except vazio em main_window.py:1408 (S2737) → Adicionar tratamento

- **Decisão**: O bloco `except asyncio.CancelledError: raise` é redundante — simplificar para `try/finally` sem o except.
- **Racional**: CancelledError propaga naturalmente; catch-and-reraise não adiciona valor.

### R3.3: Async desnecessário em test_scheduling_use_cases.py:34 (S7503) → Remover

- **Decisão**: Remover keyword `async` e decorator `@pytest.mark.asyncio`
- **Racional**: A função não contém nenhum `await`, tornando o `async` desnecessário.

### R3.4: Naming conventions em headless_mocks.py (11 issues S100/S116) → Suprimir

- **Decisão**: Configurar exclusão no `sonar-project.properties` usando `sonar.issue.ignore.multicriteria`
- **Racional**: Os métodos camelCase mimetizam a API Qt/PySide6. Renomear quebraria a compatibilidade.
- **Configuração**:
  ```properties
  sonar.issue.ignore.multicriteria=e1,e2
  sonar.issue.ignore.multicriteria.e1.ruleKey=python:S100
  sonar.issue.ignore.multicriteria.e1.resourceKey=tests/headless_mocks.py
  sonar.issue.ignore.multicriteria.e2.ruleKey=python:S116
  sonar.issue.ignore.multicriteria.e2.resourceKey=tests/headless_mocks.py
  ```

---

## R4: Configuração SonarQube Atual

### sonar-project.properties (estado atual)

```properties
sonar.organization=tuyoshivinicius
sonar.projectKey=tuyoshivinicius_backlog_manager_v2
sonar.projectName=Backlog Manager
sonar.host.url=https://sonarcloud.io
sonar.sources=src/
sonar.tests=tests/
sonar.python.version=3.13
sonar.python.coverage.reportPaths=coverage.xml
sonar.exclusions=**/tests/**,**/migrations/**,**/__pycache__/**
sonar.coverage.exclusions=**/tests/**,**/conftest.py
sonar.sourceEncoding=UTF-8
```

**Observação**: `sonar.exclusions=**/tests/**` exclui testes da análise de código-fonte, mas as issues S100/S116 em `tests/headless_mocks.py` aparecem porque o SonarQube analisa arquivos em `sonar.tests=tests/` separadamente. A supressão via `sonar.issue.ignore.multicriteria` é o mecanismo correto para ignorar regras específicas em arquivos de teste.
