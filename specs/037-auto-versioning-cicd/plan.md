# Implementation Plan: Versionamento Automático com Git Tags e CI/CD Gitflow

**Branch**: `037-auto-versioning-cicd` | **Date**: 2026-04-01 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/037-auto-versioning-cicd/spec.md`

## Summary

Implementar versionamento automático baseado em Conventional Commits usando python-semantic-release, integrado ao pipeline CI/CD Gitflow com criação automática de PRs entre branches (feature→develop→main), tagging automático, e publicação no PyPI via dispatch do publish.yml existente. Escopo puramente CI/CD — nenhuma alteração em código de produção.

## Technical Context

**Language/Version**: Python 3.13+ (runtime), GitHub Actions YAML (workflows)
**Primary Dependencies**: python-semantic-release v9+ (dev), gh CLI (pré-instalado nos runners)
**Storage**: N/A — sem alterações de banco de dados
**Testing**: Validação via dry-run do semantic-release + testes manuais de workflow
**Target Platform**: GitHub Actions (ubuntu-latest runners)
**Project Type**: CI/CD pipeline automation (workflows YAML)
**Performance Goals**: Fluxo completo (merge main → PyPI) em ≤ 15 minutos (SC-006)
**Constraints**: GITHUB_TOKEN apenas (sem PAT); publish.yml não modificado; workflows existentes não quebram
**Scale/Scope**: 3 novos workflows + 1 modificação + configuração PSR no pyproject.toml

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

### Avaliação Pré-Design

| Princípio | Aplicável | Status | Observação |
|-----------|-----------|--------|------------|
| I. Clean Architecture | ❌ Não | ✅ N/A | Escopo puramente CI/CD, sem código de produção |
| II. DDD | ❌ Não | ✅ N/A | Sem entidades de domínio |
| III. Repository Pattern | ❌ Não | ✅ N/A | Sem acesso a dados |
| IV. Dependency Injection | ❌ Não | ✅ N/A | Sem código Python novo |
| V. SQLite | ❌ Não | ✅ N/A | Sem alterações de banco |
| VI. Packaging & Distribution | ✅ Sim | ✅ OK | PSR atualiza versão no pyproject.toml (fonte única); Poetry continua como build tool |
| VII. Estrutura de Diretórios | ✅ Sim | ✅ OK | Novos arquivos em `.github/workflows/` (local padrão) |
| VIII. Async | ❌ Não | ✅ N/A | Sem código Python novo |
| IX. Simplicidade | ✅ Sim | ✅ OK | Workflows seguem KISS — cada um com responsabilidade única |
| X. Type Hints | ❌ Não | ✅ N/A | Sem código Python novo |
| XI. Docstrings | ❌ Não | ✅ N/A | Sem código Python novo |
| XII. Imports | ❌ Não | ✅ N/A | Sem código Python novo |
| XIII. Nomenclatura | ✅ Sim | ✅ OK | Nomes de workflow descritivos em inglês (feature-ci, develop-merge, main-release) |
| XIV. Testes | ⚠️ Parcial | ✅ OK | Sem testes automatizados de workflow (limitação do GitHub Actions); validação via dry-run |
| XV. Idioma | ✅ Sim | ✅ OK | Código (YAML) em inglês; documentação em português |
| XVI. Tratamento de Erros | ✅ Sim | ✅ OK | Workflows falham limpo sem efeitos colaterais (sem tags órfãs) |
| XVII. Logging | ❌ Não | ✅ N/A | GitHub Actions tem logging built-in |
| XVIII. Gestão de Configuração | ✅ Sim | ✅ OK | PSR configurado no pyproject.toml (centralizado) |
| XIX. UI/UX | ❌ Não | ✅ N/A | Sem alterações de UI |
| XX. Validação de Entrada | ❌ Não | ✅ N/A | Sem entrada de usuário |
| XXI. CI/CD e Qualidade | ✅ Sim | ✅ OK | Fortalece o pipeline existente; mantém gates de qualidade |

**Resultado**: ✅ Nenhuma violação. Todos os princípios aplicáveis estão em conformidade.

### Avaliação Pós-Design

Mesma avaliação — design não introduziu violações adicionais. O princípio VI (Packaging) é reforçado: versão passa a ser gerenciada automaticamente pelo PSR, eliminando divergência manual entre pyproject.toml e __init__.py.

## Project Structure

### Documentation (this feature)

```text
specs/037-auto-versioning-cicd/
├── plan.md              # Este arquivo
├── spec.md              # Especificação da feature
├── research.md          # Pesquisa e decisões técnicas
├── data-model.md        # Modelo conceitual do pipeline
├── quickstart.md        # Guia rápido de uso
├── contracts/           # Contratos de interface dos workflows
│   ├── feature-ci.yml
│   ├── develop-merge.yml
│   ├── main-release.yml
│   └── ci-modifications.yml
└── tasks.md             # Tarefas de implementação (gerado por /speckit.tasks)
```

### Source Code (repository root)

```text
.github/workflows/
├── ci.yml               # MODIFICAR: remover push triggers de develop/main
├── publish.yml          # MANTER: sem alterações
├── feature-ci.yml       # NOVO: CI + auto-PR para feature branches
├── develop-merge.yml    # NOVO: cálculo de versão + PR para main
└── main-release.yml     # NOVO: release + tag + dispatch publish + backmerge

pyproject.toml           # MODIFICAR: adicionar [tool.semantic_release] + dev dependency
src/backlog_manager/
└── __init__.py          # Gerenciado automaticamente pelo PSR (sem alteração manual)
```

**Structure Decision**: Todos os novos arquivos são workflows GitHub Actions em `.github/workflows/`. A única alteração em código-fonte é a configuração do PSR no `pyproject.toml` (dev dependency + seção `[tool.semantic_release]`). Nenhum arquivo de produção é alterado manualmente.

## Complexity Tracking

> Nenhuma violação de constituição identificada. Tabela não aplicável.

## Design Decisions

### D1: PSR como ferramenta de versionamento

- **Escolha**: python-semantic-release v9+
- **Alternativas rejeitadas**: commitizen (menor integração Poetry), release-please (conflita com Gitflow), bump2version (sem Conventional Commits)
- **Justificativa**: Integração nativa com Poetry, suporte a Conventional Commits, modo dry-run para cálculo de versão

### D2: workflow_dispatch para disparo do publish.yml

- **Escolha**: `gh workflow run publish.yml --ref vX.Y.Z -f confirm=yes`
- **Alternativas rejeitadas**: PAT (viola constraint), workflow_call (misturaria responsabilidades), repository_dispatch (mais complexo)
- **Justificativa**: workflow_dispatch é exceção à limitação do GITHUB_TOKEN; publish.yml já suporta workflow_dispatch com input confirm

### D3: Tag âncora v0.1.0

- **Escolha**: Criar tag `v0.1.0` no HEAD de main antes de habilitar PSR
- **Justificativa**: Sem tags existentes, PSR escaneia todos os commits desde o início do repo, causando bump inesperado. Tag âncora define o ponto de partida correto.

### D4: Separação de workflows por responsabilidade

- **Escolha**: 3 workflows separados (feature-ci, develop-merge, main-release)
- **Alternativa rejeitada**: Workflow único com condicionais complexas
- **Justificativa**: Princípio IX (Simplicidade) — cada workflow tem uma responsabilidade única e clara

### D5: ci.yml como reusable workflow

- **Escolha**: Novos workflows chamam ci.yml via `workflow_call`
- **Justificativa**: DRY — evita duplicação da lógica de lint + testes; ci.yml já suporta workflow_call
