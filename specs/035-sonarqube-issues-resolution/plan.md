# Implementation Plan: Resolucao de Issues SonarQube para Quality Gate

**Branch**: `035-sonarqube-issues-resolution` | **Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/035-sonarqube-issues-resolution/spec.md`

## Summary

Resolver todas as 12 issues abertas e 1 security hotspot pendente no SonarQube para que o quality gate do projeto passe (status OK). Envolve refatoracao de 1 funcao para reduzir complexidade cognitiva (S3776), marcacao de 11 issues de naming convention como ACCEPTED (S100/S116), e review de 1 security hotspot como SAFE (S2245). Dados coletados em tempo real via MCP SonarQube.

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite, aiofiles, openpyxl
**Storage**: SQLite (sem alteracoes de schema)
**Testing**: pytest + pytest-cov + pytest-asyncio
**Target Platform**: Windows desktop (PySide6)
**Project Type**: desktop-app (library-first, PyPI)
**Performance Goals**: N/A (escopo de qualidade de codigo)
**Constraints**: Refatoracao DEVE preservar comportamento identico com seed fixo
**Scale/Scope**: 26,815 LOC, 12 issues abertas, 1 hotspot TO_REVIEW

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Relevancia | Status |
|-----------|-----------|--------|
| I. Clean Architecture | Baixa — alteracoes em script utilitario e mocks de teste, nao em camadas da aplicacao | PASS |
| II. DDD | N/A — sem alteracoes em entidades ou dominio | PASS |
| III. Repository Pattern | N/A — sem alteracoes em repositorios | PASS |
| IV. Dependency Injection | N/A — sem alteracoes em DI | PASS |
| V. SQLite | N/A — sem alteracoes de banco | PASS |
| VI. Packaging | N/A — sem alteracoes de empacotamento | PASS |
| VII. Estrutura de Diretorios | PASS — arquivos modificados estao nos locais corretos | PASS |
| VIII. Async | N/A — script de seed e sincrono por design | PASS |
| IX. Simplicidade e Legibilidade | Alta — refatoracao melhora legibilidade reduzindo complexidade cognitiva | PASS |
| X. Type Hints | Media — funcao auxiliar DEVE ter type hints completos | PASS |
| XI. Docstrings | Media — funcao auxiliar publica DEVE ter docstring | PASS |
| XII. Imports (isort) | N/A — sem novos imports | PASS |
| XIII. Nomenclatura | Alta — issues de naming sao falso-positivos (mocks Qt, justificado) | PASS |
| XIV. Estrategia de Testes | Media — testes existentes DEVEM continuar passando | PASS |

**Gate Result**: PASS — nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

```text
specs/035-sonarqube-issues-resolution/
├── plan.md              # This file
├── research.md          # Phase 0 output — dados SonarQube + analise de complexidade
├── data-model.md        # Phase 1 output — entidades envolvidas e state transitions
├── quickstart.md        # Phase 1 output — passos de implementacao
└── tasks.md             # Phase 2 output (/speckit.tasks)
```

### Source Code (arquivos impactados)

```text
scripts/
└── seed_test_backlog.py          # Refatoracao: extrair _try_create_inter_wave_dep()

tests/
└── headless_mocks.py             # Sem alteracao de codigo (issues marcadas como ACCEPTED no SonarQube)
```

**Structure Decision**: Nenhuma alteracao estrutural. Apenas 1 arquivo modificado (`scripts/seed_test_backlog.py`) com extracao de funcao auxiliar.

## Dados SonarQube (coletados via MCP em 2026-04-01)

### Quality Gate — Condicao falhando

| Condicao | Threshold | Atual | Causa |
|----------|-----------|-------|-------|
| new_security_hotspots_reviewed | 100% | 94.4% | 1 hotspot TO_REVIEW na linha 572 de seed_test_backlog.py |

### Issues por Tipo

| Regra | Severidade | Qtd | Arquivo | Acao |
|-------|------------|-----|---------|------|
| S3776 | CRITICAL | 1 | scripts/seed_test_backlog.py:621 | Refatorar funcao (codigo) |
| S100 | MINOR | 9 | tests/headless_mocks.py | Marcar ACCEPTED (API) |
| S116 | MINOR | 2 | tests/headless_mocks.py | Marcar ACCEPTED (API) |

### Security Hotspot Pendente

| Key | Regra | Arquivo | Linha | Acao |
|-----|-------|---------|-------|------|
| AZ1I5XNA3OXD0TCP-O9_ | S2245 | scripts/seed_test_backlog.py | 572 | Marcar SAFE (API) |

## Plano de Implementacao

### Fase 1 — Refatoracao de Codigo (P1)

**Objetivo**: Reduzir complexidade cognitiva de `_generate_inter_wave_deps()` de 16 para ≤15.

**Abordagem**: Extrair corpo do inner loop para funcao auxiliar `_try_create_inter_wave_dep()`.

**Detalhes**: Ver [research.md](research.md) secao 2 para calculo completo de complexidade e funcao proposta.

**Validacao**:
1. Executar `poetry run pytest tests/ -v` — todos os testes devem passar
2. Re-analise no SonarQube — issue S3776 (key: `AZ1H3y5IMsoPwz0FZVip`) deve desaparecer

### Fase 2 — Acoes no SonarQube via API (P1/P2)

**2a. Security Hotspot → SAFE** (P1 — bloqueia quality gate)
- Key: `AZ1I5XNA3OXD0TCP-O9_`
- Justificativa: "Uso de random.choice() em script de geracao de dados de teste com seed fixo (random.seed(RANDOM_SEED)). Nao ha contexto criptografico ou de seguranca. Mesmo tipo de hotspot (S2245) ja revisado e marcado SAFE em 7 outras ocorrencias no mesmo arquivo."

**2b. Issues Naming Convention → ACCEPTED** (P2 — limpeza)
- 9 issues S100 + 2 issues S116 em `tests/headless_mocks.py`
- Justificativa: "Metodos/campos camelCase/PascalCase sao obrigatorios para compatibilidade com a API Qt/PySide6. Mocks devem replicar exatamente a interface do framework. Comentarios `# noqa: N802`/`# noqa: N815` ja presentes para flake8."
- Keys listadas em [research.md](research.md) secao 5

### Fase 3 — Verificacao Final

1. Commit e push das alteracoes de codigo
2. Aguardar re-analise no SonarQube (CI/CD trigger)
3. Verificar via MCP:
   - `get_project_quality_gate_status` → status OK
   - `search_sonar_issues_in_projects(issueStatuses=["OPEN"])` → 0 issues
   - `search_security_hotspots(status=["TO_REVIEW"])` → 0 hotspots

## Complexity Tracking

> Nenhuma violacao de constitution identificada. Tabela nao aplicavel.

## Riscos e Mitigacoes

| Risco | Probabilidade | Mitigacao |
|-------|---------------|-----------|
| Refatoracao altera comportamento de seed | Baixa | Testes existentes + verificacao manual com seed fixo |
| SonarQube rejeita marcacao de hotspot | Baixa | Justificativa tecnica detalhada + precedente (7 hotspots SAFE no mesmo arquivo) |
| Novas issues surgem apos re-analise | Baixa | Tratar no mesmo escopo se relacionadas aos arquivos modificados |
