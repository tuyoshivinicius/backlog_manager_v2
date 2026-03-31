# Contract: CI Workflow Reusable Interface (workflow_call)

**Arquivo**: `.github/workflows/ci.yml`
**Tipo**: GitHub Actions Reusable Workflow

## Interface

O CI workflow expoe uma interface `workflow_call` que permite que outros workflows (ex: `publish.yml`) reutilizem toda a pipeline de validacao.

### Inputs

Nenhum input obrigatorio. O workflow usa valores padrao internos.

### Secrets

| Secret | Obrigatorio | Descricao |
|--------|-------------|-----------|
| CODECOV_TOKEN | Nao | Token de upload para Codecov. Se ausente, upload e ignorado. |
| SONAR_TOKEN | Nao | Token de scan para SonarCloud. Se ausente, scan e ignorado. |

**Modo de passagem**: `secrets: inherit` (o caller propaga todos os secrets automaticamente).

### Outputs

Nenhum output explicito. O caller depende apenas do status de sucesso/falha do workflow.

### Jobs Executados

| Job | Descricao | Falha bloqueia? |
|-----|-----------|-----------------|
| lint | ruff check, ruff format --check, mypy, version-check | Sim |
| test | pytest (unit, integration, e2e) em matriz Python 3.11/3.12/3.13 | Sim |
| quality | Codecov upload, SonarCloud scan | Nao (continue-on-error) |

### Exemplo de Uso (Caller)

```yaml
jobs:
  ci:
    uses: ./.github/workflows/ci.yml
    secrets: inherit

  build:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: poetry build
```

## Contrato de Publish

### Triggers

| Trigger | Condicao | Destino |
|---------|----------|---------|
| Tag `v*.*.*-rc*` / `v*.*.*-beta*` / `v*.*.*-alpha*` | Sufixo pre-release | TestPyPI |
| Tag `v*.*.*` (sem sufixo) | Release final | PyPI + GitHub Release |
| workflow_dispatch | Input `confirm: "yes"` | PyPI (emergencia) |

### Ambientes (GitHub Environments)

| Environment | Registro Trusted Publisher | Uso |
|-------------|---------------------------|-----|
| testpypi | TestPyPI project settings | Tags pre-release |
| pypi | PyPI project settings | Tags de release final |

### Permissoes por Job

| Job | id-token | contents |
|-----|----------|----------|
| ci (workflow_call) | N/A | read |
| build | N/A | read |
| publish-testpypi | write | read |
| publish-pypi | write | read |
| github-release | N/A | write |

### Artefatos

| Artefato | Produtor | Consumidor |
|----------|----------|------------|
| coverage-report (coverage.xml) | test job | quality job |
| dist (*.whl, *.tar.gz) | build job | publish-testpypi, publish-pypi, github-release |
