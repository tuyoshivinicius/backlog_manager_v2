# Implementation Plan: Script de Seed para Teste de Alocação

**Branch**: `014-seed-test-backlog` | **Date**: 2026-03-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/014-seed-test-backlog/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Script Python de linha de comando para popular banco de dados SQLite com dados de teste volumosos (150-200 histórias, 80-120 dependências, 7 desenvolvedores, 30 features em 7 ondas) para validar o motor de alocação (EP-007) e cálculo de cronograma (EP-006). O script garante integridade referencial, ausência de ciclos em dependências, reproducibilidade via seed fixo (42), e utiliza transação atômica.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: aiosqlite ^0.19.0, aiofiles ^23.0 (para init_database existente)
**Storage**: SQLite via aiosqlite (reutiliza infraestrutura existente)
**Testing**: pytest ^8.0, pytest-asyncio ^0.23, pytest-cov ^4.0
**Target Platform**: Windows/Linux CLI (ambiente de desenvolvimento/teste)
**Project Type**: CLI script standalone (scripts/seed_test_backlog.py)
**Performance Goals**: Execução completa < 5 segundos (SC-001)
**Constraints**: Dependências sem ciclos (FR-005), inter-onda sempre para ondas anteriores (FR-006)
**Scale/Scope**: 7 desenvolvedores, ~30 features, 150-200 histórias, 80-120 dependências

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Princípio | Status | Observação |
|-----------|--------|------------|
| I. Clean Architecture | ✅ PASS | Script é infraestrutura/utilitário, não viola camadas |
| II. DDD | ✅ PASS | Script insere dados diretamente no banco (ferramenta de teste) |
| III. Repository Pattern | ✅ PASS | Script utilitário pode usar SQL direto (não é produção) |
| IV. Dependency Injection | N/A | Script standalone, não integra com container |
| V. SQLite | ✅ PASS | Reutiliza schema.sql existente via init_database |
| VI. Packaging | ✅ PASS | Script em `scripts/` (não empacotado) |
| VII. Estrutura de Diretórios | ✅ PASS | `scripts/` na raiz é padrão para utilitários |
| VIII. Programação Assíncrona | ✅ PASS | Usa async/await com aiosqlite |
| IX. Simplicidade | ✅ PASS | Script direto, sem abstrações desnecessárias |
| X. Type Hints | ✅ PASS | Será implementado com type hints completos |
| XI. Docstrings | ✅ PASS | Funções públicas terão docstrings Google style |
| XII. isort | ✅ PASS | Imports organizados conforme padrão |
| XIII. Nomenclatura | ✅ PASS | snake_case para funções/variáveis |
| XIV. Testes | ✅ PASS | Testes de integração em tests/integration/ |
| XV. Idioma | ✅ PASS | Código em inglês, logs em português |
| XVI. Tratamento de Erros | ✅ PASS | Mensagens claras em português |
| XVII. Logging | ✅ PASS | Usa logger para progresso |
| XVIII. Configuração | N/A | Script não altera configurações do sistema |
| XIX. UI/UX | N/A | CLI sem GUI |
| XX. Validação de Entrada | ✅ PASS | Valida argumentos CLI |
| XXI. CI/CD | ✅ PASS | Testes executados no pipeline |

**Gate Status**: ✅ APROVADO - Nenhuma violação identificada

### Post-Design Re-evaluation (Phase 1)

Após revisão dos artefatos de design (research.md, data-model.md, quickstart.md):
- ✅ Decisões de pesquisa alinhadas com constituição
- ✅ Modelo de dados reutiliza entidades existentes sem modificação
- ✅ Abordagem de geração de dependências garante DAG por construção
- ✅ Nenhuma nova tecnologia introduzida além das já aprovadas

## Project Structure

### Documentation (this feature)

```text
specs/014-seed-test-backlog/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
scripts/
└── seed_test_backlog.py    # Script principal de seed

tests/
└── integration/
    └── test_seed_backlog.py  # Testes de integração do script
```

**Structure Decision**: Script utilitário standalone em `scripts/` na raiz do repositório. Reutiliza infraestrutura existente (`sqlite_connection.py`, `init_database`) sem criar novos módulos na aplicação principal. Testes de integração validam geração de dados e ausência de ciclos.

## Complexity Tracking

> **Nenhuma violação identificada - seção não aplicável**
