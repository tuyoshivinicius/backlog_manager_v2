# Implementation Plan: Resolver Issues SonarQube e Aprovar Quality Gate

**Branch**: `034-sonarqube-quality-gate` | **Date**: 2026-04-01 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/034-sonarqube-quality-gate/spec.md`

## Summary

Resolver todas as 20 issues OPEN e revisar todos os 32 security hotspots no SonarQube para aprovar o Quality Gate (ERROR → OK). A abordagem combina refatoração de complexidade cognitiva (6 funções com S3776), correção de code smells (S125, S2737, S7503), supressão de naming conventions em mocks Qt (S100/S116), substituição de tags por SHA em GitHub Actions (S7637), e revisão de security hotspots via SonarCloud. O bloqueador único do Quality Gate é `new_security_hotspots_reviewed = 0%` (threshold: 100%).

## Technical Context

**Language/Version**: Python 3.11+ (runtime), Python 3.13 (SonarQube analysis)
**Primary Dependencies**: PySide6 ^6.10.0, qasync ^0.27.1, Pydantic ^2.0, aiosqlite, aiofiles, openpyxl
**Storage**: N/A — sem alterações de schema SQLite
**Testing**: pytest ^8.0, pytest-cov ^4.0, pytest-asyncio ^0.23
**Target Platform**: Windows desktop (PySide6), CI/CD (GitHub Actions + SonarCloud)
**Project Type**: desktop-app (library-first via Poetry)
**Performance Goals**: N/A — sem impacto de performance
**Constraints**: Refatorações não devem alterar interfaces públicas nem introduzir regressões
**Scale/Scope**: 20 issues + 32 hotspots = 52 itens a resolver; ~26.764 LOC

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Relevância | Status |
|-----------|-----------|--------|
| I. Clean Architecture | Refatorações mantêm separação de camadas | ✅ PASS |
| VII. Estrutura de Diretórios | Sem novos arquivos fora da estrutura existente | ✅ PASS |
| IX. Simplicidade e Legibilidade | Refatoração reduz complexidade → melhora legibilidade | ✅ PASS |
| XIII. Convenções de Nomenclatura | Mocks Qt mantêm camelCase (suprimidos, não renomeados) | ✅ PASS |
| XIV. Estratégia de Testes | Testes existentes devem continuar passando | ✅ PASS |
| XXI. CI/CD e Qualidade Contínua | SHA em Actions melhora segurança do pipeline | ✅ PASS |

**Gate resultado**: PASS — nenhuma violação de constituição.

## Post-Design Constitution Re-check

| Princípio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Sub-funções extraídas mantêm-se na mesma camada |
| IX. Simplicidade | ✅ PASS | Funções menores = mais legíveis e testáveis |
| XIV. Testes | ✅ PASS | Suíte existente valida ausência de regressão |
| XXI. CI/CD | ✅ PASS | SHA de commit fortalece segurança do pipeline |

## Project Structure

### Documentation (this feature)

```text
specs/034-sonarqube-quality-gate/
├── plan.md              # Este arquivo
├── spec.md              # Especificação da feature
├── research.md          # Pesquisa e decisões
├── data-model.md        # Artefatos de configuração afetados
├── quickstart.md        # Guia de validação
└── tasks.md             # Tarefas (gerado por /speckit.tasks)
```

### Source Code (repository root)

```text
# Arquivos modificados (refatoração de complexidade)
src/backlog_manager/domain/services/allocation_service.py    # S3776: _run_allocation_loop
src/backlog_manager/presentation/viewmodels/story_table_model.py  # S3776: _get_display_value
scripts/extract_metrics.py                                    # S3776: 2 funções
scripts/seed_test_backlog.py                                  # S3776: 2 funções

# Arquivos modificados (code smells)
src/backlog_manager/presentation/views/main_window.py         # S2737: except vazio
tests/integration/infrastructure/database/test_schema.py      # S125: código comentado
tests/integration/application/use_cases/test_scheduling_use_cases.py  # S7503: async desnecessário

# Arquivos de configuração
sonar-project.properties                                      # Supressão S100/S116
.github/workflows/ci.yml                                      # SHA de commit
.github/workflows/publish.yml                                 # SHA de commit + secrets
```

**Structure Decision**: Nenhum arquivo novo de código. Apenas modificações em arquivos existentes e configuração.

## Complexity Tracking

> Nenhuma violação de constituição a justificar.

| Violação | Why Needed | Simpler Alternative Rejected Because |
|----------|------------|-------------------------------------|
| N/A | N/A | N/A |
