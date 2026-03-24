# Implementation Plan: Automacao do Ciclo de Analise de Alocacao

**Branch**: `016-automate-allocation-analysis` | **Date**: 2026-03-13 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/016-automate-allocation-analysis/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Automatizar o protocolo de 6 etapas de analise de alocacao (Observar, Descrever, Analisar Logs, Diagnosticar, Propor Correcao, Validar) atraves de um skill do Claude Code (`/analyze-allocation`). O skill executa automaticamente seed script EP-014, roda testes de alocacao, coleta e analisa logs estruturados EP-015, extrai as 16 metricas de AllocationMetrics, identifica anomalias e apresenta relatorio estruturado com propostas de correcao.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: pydantic ^2.0, aiosqlite ^0.19.0, aiofiles ^23.0, PySide6 ^6.10.0
**Storage**: SQLite (via aiosqlite) - `%APPDATA%/BacklogManager/backlog_manager.db`
**Logging**: File-based structured logging - `%APPDATA%/BacklogManager/logs/backlog_manager.log`
**Testing**: pytest ^8.0 + pytest-asyncio + pytest-cov
**Target Platform**: Windows (primary), Linux (secondary)
**Project Type**: Claude Code Skill (markdown-based, invokes Bash + Read tools)
**Performance Goals**: Ciclo completo de analise < 2 minutos (SC-001), ciclo correcao+validacao < 10 minutos (SC-007)
**Constraints**: Sem retry automatico em caso de falha; aprovacao explicita para modificacoes de codigo
**Scale/Scope**: Backlog de ate 500 historias, 7 desenvolvedores, 7 ondas

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principio | Status | Notas |
|-----------|--------|-------|
| I. Clean Architecture | ✅ PASS | Skill e externo ao codigo; nao modifica camadas existentes |
| II. Domain-Driven Design | ✅ PASS | Utiliza AllocationMetrics existente do dominio |
| III. Repository Pattern | ✅ N/A | Skill nao acessa repositorios diretamente |
| IV. Dependency Injection | ✅ N/A | Skill nao injeta dependencias |
| V. SQLite como BD | ✅ PASS | Logs em arquivo, BD nao e modificado pelo skill |
| VI. Packaging & Distribution | ✅ PASS | Skill e arquivo markdown, nao afeta pacote Python |
| VII. Estrutura de Diretorios | ✅ PASS | Skill em `.claude/commands/` seguindo convencao Claude Code |
| VIII. Programacao Assincrona | ✅ N/A | Skill invoca comandos via Bash, nao codigo async |
| IX. Simplicidade e Legibilidade | ✅ PASS | Skill segue formato padrao de templates |
| X. Type Hints Obrigatorios | ✅ N/A | Skill e markdown, nao codigo Python |
| XI. Docstrings em Codigo Publico | ✅ N/A | Skill e markdown |
| XII. Organizacao de Imports | ✅ N/A | Skill e markdown |
| XIII. Convencoes de Nomenclatura | ✅ PASS | Nome do skill segue kebab-case |
| XIV. Estrategia de Testes | ✅ PASS | Testes de integracao existentes; skill nao requer testes Python |
| XV. Idioma | ✅ PASS | Documentacao em portugues, comandos em ingles |
| XVI. Tratamento de Erros | ✅ PASS | Skill captura erros e reporta mensagens claras |
| XVII. Logging e Observabilidade | ✅ PASS | Utiliza logs estruturados existentes do EP-015 |
| XVIII. Gestao de Configuracao | ✅ N/A | Skill nao modifica configuracoes |
| XIX. Padroes de UI/UX | ✅ N/A | Skill e CLI, nao modifica GUI |
| XX. Validacao e Sanitizacao | ✅ PASS | Skill valida argumentos (--logs-only) |
| XXI. CI/CD e Qualidade | ✅ PASS | Skill valida cobertura/complexidade via comandos existentes |

**Gate Result**: ✅ PASS - Nenhuma violacao identificada.

## Project Structure

### Documentation (this feature)

\`\`\`text
specs/016-automate-allocation-analysis/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
│   └── skill-contract.md
└── tasks.md             # Phase 2 output (/speckit.tasks command)
\`\`\`

### Source Code (repository root)

\`\`\`text
.claude/
└── commands/
    └── analyze-allocation.md    # Main skill file

specs/016-automate-allocation-analysis/
└── corrections/
    └── TEMPLATE.md              # Template for correction logs
\`\`\`

**Structure Decision**: Este EP implementa um Claude Code Skill, que e um arquivo markdown em \`.claude/commands/\`. Nao requer modificacoes no codigo Python do projeto, apenas utiliza ferramentas existentes (Bash, Read) para executar comandos e ler arquivos.

## Complexity Tracking

> **Nenhuma violacao identificada - tabela vazia**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| - | - | - |
