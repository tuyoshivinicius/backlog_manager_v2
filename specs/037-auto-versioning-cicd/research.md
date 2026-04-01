# Research: Versionamento Automático com Git Tags e CI/CD Gitflow

**Feature**: 037-auto-versioning-cicd
**Date**: 2026-04-01

## 1. python-semantic-release (PSR) v9+ com Poetry

### Decision
Usar python-semantic-release v9+ como ferramenta de versionamento automático baseado em Conventional Commits.

### Rationale
- Suporte nativo a Poetry (`version_toml` para `pyproject.toml`)
- Atualização simultânea de múltiplos arquivos de versão (`version_variables` para `__init__.py`)
- Parser Angular/Conventional Commits built-in
- CLI com modo `--noop` para cálculo de versão sem aplicar mudanças
- Integração nativa com GitHub Actions e GITHUB_TOKEN

### Configuração no pyproject.toml

```toml
[tool.semantic_release]
version_toml = ["pyproject.toml:tool.poetry.version"]
version_variables = ["src/backlog_manager/__init__.py:__version__"]
branch = "main"
commit_message = "chore(release): v{version}"
tag_format = "v{version}"
commit_parser = "angular"

[tool.semantic_release.commit_parser_options]
allowed_tags = ["build", "chore", "ci", "docs", "feat", "fix", "perf", "style", "refactor", "test"]
minor_tags = ["feat"]
patch_tags = ["fix", "perf"]

[tool.semantic_release.remote]
type = "github"
token = { env = "GH_TOKEN" }

[tool.semantic_release.publish]
upload_to_vcs_release = false
```

### Comandos CLI

| Comando | Propósito |
|---------|-----------|
| `semantic-release --noop version --print` | Calcular próxima versão sem aplicar |
| `semantic-release version` | Bump versão, commit, tag (sem push) |
| `semantic-release version --push` | Bump + push commits e tags |

### Mapeamento Conventional Commits → Bump

| Prefixo | Bump | Exemplo |
|---------|------|---------|
| `fix:` | PATCH (0.0.X) | `fix: corrigir validação de SP` |
| `perf:` | PATCH (0.0.X) | `perf: otimizar query de alocação` |
| `feat:` | MINOR (0.X.0) | `feat: adicionar filtro por status` |
| `feat!:` / `BREAKING CHANGE:` | MAJOR (X.0.0) | `feat!: redesign API de alocação` |
| `chore:`, `docs:`, `ci:`, `test:`, `refactor:` | Nenhum | Ignorados no cálculo |

### Consideração: Tag Inicial

O repositório não possui tags. O PSR escaneia todos os commits desde o início do repo. Para evitar um bump inesperado, é necessário criar a tag `v0.1.0` no HEAD de `main` antes de habilitar o PSR. Isso ancora o ponto de partida.

### Alternatives Considered

| Alternativa | Motivo da Rejeição |
|------------|-------------------|
| commitizen | Menos integração nativa com Poetry; foco maior em convenções de commit que em release automation |
| bump2version | Sem suporte a Conventional Commits; apenas file bumping |
| release-please (Google) | Focado em monorepos; cria release PRs próprias que conflitam com nosso fluxo Gitflow |
| Manual versioning | Status quo — causa falhas de publicação quando versão não é atualizada |

---

## 2. GitHub Actions: Criação Automática de PRs

### Decision
Usar `gh pr create` e `gh pr list` para criação e verificação de PRs dentro dos workflows.

### Rationale
- `gh` CLI está pré-instalado nos runners do GitHub Actions
- GITHUB_TOKEN funciona nativamente com `gh` para operações de PR
- `gh pr list --head <branch>` permite verificar duplicatas

### Padrão Anti-Duplicata

```yaml
- name: Check/Create PR
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    EXISTING=$(gh pr list --head "$BRANCH" --base "$TARGET" --json number --jq '.[0].number')
    if [ -z "$EXISTING" ]; then
      gh pr create --title "$TITLE" --body "$BODY" --base "$TARGET" --head "$BRANCH"
    fi
```

### Auto-Merge (Feature → Develop)

```yaml
- name: Enable auto-merge
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  run: |
    PR_NUM=$(gh pr list --head "$BRANCH" --base develop --json number --jq '.[0].number')
    gh pr merge "$PR_NUM" --auto --squash
```

**Pré-requisito**: Habilitar "Allow auto-merge" nas configurações do repositório e configurar branch protection com required status checks em `develop`.

### Extração de Descrição da Branch

```bash
BRANCH="037-auto-versioning-cicd"
DESC=$(echo "$BRANCH" | sed 's/^[0-9]*-//' | tr '-' ' ')
# Resultado: "auto versioning cicd"
```

### Alternatives Considered

| Alternativa | Motivo da Rejeição |
|------------|-------------------|
| peter-evans/create-pull-request | Action de terceiros; adiciona dependência desnecessária quando `gh` já resolve |
| GitHub API direta (curl) | Mais verboso; `gh` abstrai autenticação e formatação |

---

## 3. Limitação do GITHUB_TOKEN e Disparo de Workflows

### Decision
Usar `gh workflow run` (workflow_dispatch) para disparar publish.yml após criação da tag, contornando a limitação do GITHUB_TOKEN com push events.

### Rationale
A documentação do GitHub confirma: "Events triggered by the GITHUB_TOKEN, **with the exception of workflow_dispatch and repository_dispatch**, will not create a new workflow run." Portanto:

- ❌ Push de tag via GITHUB_TOKEN → NÃO dispara publish.yml (trigger `push: tags`)
- ✅ `gh workflow run publish.yml --ref "vX.Y.Z"` via GITHUB_TOKEN → DISPARA publish.yml (trigger `workflow_dispatch`)

### Fluxo de Disparo

```
main-release.yml                          publish.yml
┌──────────────────┐                      ┌──────────────────┐
│ semantic-release  │                      │ on:              │
│ version --push    │─── cria tag ───────→ │   push: tags v*  │ ← NÃO dispara (GITHUB_TOKEN)
│                   │                      │   workflow_dispatch│ ← SIM dispara
│ gh workflow run   │──── dispatch ──────→ │     inputs:      │
│   --ref vX.Y.Z   │                      │       confirm    │
│   -f confirm=yes  │                      └──────────────────┘
└──────────────────┘
```

### Implicações

1. publish.yml **NÃO precisa ser modificado** — já tem trigger `workflow_dispatch` com input `confirm`
2. O `--ref "vX.Y.Z"` faz `github.ref` no publish.yml apontar para `refs/tags/vX.Y.Z`
3. A lógica de PyPI vs TestPyPI (`contains(github.ref, '-rc')`) funciona normalmente
4. A tag precisa existir ANTES do dispatch (semantic-release cria e pusha primeiro)

### Alternatives Considered

| Alternativa | Motivo da Rejeição |
|------------|-------------------|
| Personal Access Token (PAT) | Requer segredo extra; viola constraint FR-013 |
| workflow_call inline | Misturaria responsabilidades; publish.yml deve permanecer independente |
| repository_dispatch | Mesma exceção que workflow_dispatch, mas requer custom event type — mais complexo |

---

## 4. Concurrency Groups

### Decision
Usar `concurrency` com `cancel-in-progress: true` para feature branches; `false` para develop/main.

### Rationale
Evita race conditions na criação de PRs automáticas e economiza minutos de CI.

### Configuração

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

Para workflows de main/develop (onde cancelar é perigoso):

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: false
```

---

## 5. Modificações no ci.yml

### Decision
Remover triggers de `push` em `develop` e `main` do ci.yml, mantendo `pull_request` e `workflow_call`.

### Rationale
Os novos workflows (develop-merge.yml, main-release.yml) orquestram o CI via `workflow_call`. Manter triggers de push direto causaria execuções duplicadas.

### Antes

```yaml
on:
  push:
    branches: [develop, main, "release/*", "hotfix/*"]
  pull_request:
    branches: [develop, main]
  workflow_call:
```

### Depois

```yaml
on:
  pull_request:
    branches: [develop, main]
  workflow_call:
```

### Impacto
- PRs para develop/main continuam trigando CI via `pull_request`
- Workflows de develop/main chamam CI via `workflow_call`
- Branches release/* e hotfix/* perdem trigger de push direto (serão cobertos por PRs)

---

## 6. Branch Develop

### Decision
Criar branch `develop` a partir de `main` como primeiro passo da implementação.

### Rationale
O fluxo Gitflow requer `develop` como branch de integração. Atualmente não existe.

### Passos

```bash
git checkout main
git checkout -b develop
git push -u origin develop
```

### Configurações Necessárias no Repositório

1. **Branch protection em develop**: Requerer status checks (CI) antes de merge
2. **Allow auto-merge**: Habilitar para permitir auto-merge de feature→develop
3. **Branch protection em main**: Requerer review + status checks antes de merge
