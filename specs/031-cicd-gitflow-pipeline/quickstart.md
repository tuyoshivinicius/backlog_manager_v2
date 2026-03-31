# Quickstart: CI/CD Pipeline com GitFlow

**Feature Branch**: `031-cicd-gitflow-pipeline`

## Pre-requisitos

- Repositorio publico no GitHub
- Conta no [Codecov](https://codecov.io) vinculada ao GitHub
- Conta no [SonarCloud](https://sonarcloud.io) vinculada ao GitHub
- Projeto `zion-backlog-manager` existente no [PyPI](https://pypi.org) e [TestPyPI](https://test.pypi.org)

## Setup Rapido (Mantenedor)

### 1. Secrets do GitHub

No repositorio GitHub, acesse **Settings > Secrets and variables > Actions**:

| Secret | Onde obter |
|--------|-----------|
| `CODECOV_TOKEN` | codecov.io > Settings > Upload Token |
| `SONAR_TOKEN` | sonarcloud.io > My Account > Security > Generate Token |

### 2. Environments do GitHub

Em **Settings > Environments**, criar:

- `testpypi` — sem protecao adicional
- `pypi` — opcional: adicionar required reviewers para aprovacao manual

### 3. OIDC Trusted Publishers

**No PyPI** (pypi.org > Manage > Settings > Publishing):
- Owner: `tuyoshivinicius`
- Repository: `backlog-manager-v2`
- Workflow: `publish.yml`
- Environment: `pypi`

**No TestPyPI** (test.pypi.org > Manage > Settings > Publishing):
- Mesmo acima, mas Environment: `testpypi`

### 4. SonarCloud

1. Importar repositorio em sonarcloud.io
2. Anotar `projectKey` e `organization` (ja configurados em `sonar-project.properties`)
3. NAO adicionar como required status check no branch protection

### 5. Branch Protection

Em **Settings > Branches > Add rule**:

**Para `main`**:
- Require pull request reviews (1 reviewer)
- Require status checks: `lint`, `test`
- No direct push

**Para `develop`**:
- Require status checks: `lint`, `test`
- No direct push

## Fluxo de Desenvolvimento (Contribuidor)

### Feature

```bash
git checkout develop
git pull origin develop
git checkout -b feature/minha-feature
# ... desenvolver ...
git push -u origin feature/minha-feature
# Abrir PR para develop
```

### Release

```bash
git checkout develop
git checkout -b release/1.1.0
# Bump versao em pyproject.toml e __init__.py
git commit -m "bump: version 1.1.0"
git push -u origin release/1.1.0
# Abrir PR para main
# Apos merge em main:
git tag v1.1.0
git push origin v1.1.0
# → CI valida → publish no PyPI → GitHub Release criada
```

### Hotfix

```bash
git checkout main
git checkout -b hotfix/1.0.1
# Corrigir + bump versao
git commit -m "fix: descricao do hotfix"
git push -u origin hotfix/1.0.1
# Abrir PR para main E para develop
# Apos merge em main:
git tag v1.0.1
git push origin v1.0.1
```

### Pre-release (RC)

```bash
git tag v1.1.0-rc1
git push origin v1.1.0-rc1
# → CI valida → publish no TestPyPI
```

## Verificacao

Apos setup, verificar:

1. **CI**: Criar PR para `develop` — jobs lint, test, quality devem executar
2. **Codecov**: PR deve receber comentario de cobertura
3. **SonarCloud**: PR deve receber status check (informacional)
4. **Publish**: Criar tag `v0.1.1-rc1` — deve publicar no TestPyPI
5. **Badges**: README.md deve exibir badges funcionais no GitHub
