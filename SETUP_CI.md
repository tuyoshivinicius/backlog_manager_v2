# Guia de Setup CI/CD

Guia de configuracao unica para mantenedores do **Backlog Manager**. Siga os passos abaixo para configurar todos os servicos externos necessarios para o pipeline de CI/CD.

## Pre-requisitos

- Acesso de admin ao repositorio no GitHub
- Conta no [Codecov](https://codecov.io) vinculada ao GitHub
- Conta no [SonarCloud](https://sonarcloud.io) vinculada ao GitHub
- Projeto `zion-backlog-manager` existente no [PyPI](https://pypi.org) e [TestPyPI](https://test.pypi.org)

## 1. GitHub Secrets

No repositorio GitHub, acesse **Settings > Secrets and variables > Actions** e adicione:

| Secret | Onde Obter | Obrigatorio |
|--------|-----------|-------------|
| `CODECOV_TOKEN` | [codecov.io](https://codecov.io) > Settings > Upload Token | Sim |
| `SONAR_TOKEN` | [sonarcloud.io](https://sonarcloud.io) > My Account > Security > Generate Token | Nao (SonarCloud e opcional) |

### Obtendo o CODECOV_TOKEN

1. Acesse [codecov.io](https://codecov.io) e faca login com GitHub
2. Selecione o repositorio `backlog-manager-v2`
3. Va em **Settings > General**
4. Copie o **Upload Token**
5. Adicione como secret `CODECOV_TOKEN` no GitHub

### Obtendo o SONAR_TOKEN

1. Acesse [sonarcloud.io](https://sonarcloud.io) e faca login com GitHub
2. Va em **My Account > Security**
3. Gere um novo token com nome descritivo (ex: `backlog-manager-ci`)
4. Copie o token gerado
5. Adicione como secret `SONAR_TOKEN` no GitHub

## 2. OIDC Trusted Publishers (PyPI/TestPyPI)

A publicacao usa OIDC Trusted Publishers — sem tokens de longa duracao.

### Configuracao no PyPI

1. Acesse [pypi.org](https://pypi.org) e faca login
2. Va em **Manage > Settings > Publishing > Add a new publisher**
3. Preencha:
   - **Owner**: `tuyoshivinicius`
   - **Repository**: `backlog-manager-v2`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `pypi`
4. Salve

### Configuracao no TestPyPI

1. Acesse [test.pypi.org](https://test.pypi.org) e faca login
2. Va em **Manage > Settings > Publishing > Add a new publisher**
3. Preencha:
   - **Owner**: `tuyoshivinicius`
   - **Repository**: `backlog-manager-v2`
   - **Workflow name**: `publish.yml`
   - **Environment name**: `testpypi`
4. Salve

## 3. GitHub Environments

Em **Settings > Environments**, crie dois environments:

### Environment `testpypi`

- Sem protecao adicional (pre-releases podem ser publicadas livremente)

### Environment `pypi`

- **Opcional**: Adicione **Required reviewers** para exigir aprovacao manual antes de publicar no PyPI oficial
- Recomendado para releases finais em producao

## 4. Branch Protection Rules

Em **Settings > Branches > Add rule**:

### Regra para `main`

- **Branch name pattern**: `main`
- [x] Require a pull request before merging
  - [x] Require approvals: 1
- [x] Require status checks to pass before merging
  - Status checks obrigatorios: `Lint`, `Test (Python 3.11)`, `Test (Python 3.12)`, `Test (Python 3.13)`
- [x] Do not allow bypassing the above settings
- **NAO** adicionar SonarCloud como required status check (ver secao abaixo)

### Regra para `develop`

- **Branch name pattern**: `develop`
- [x] Require status checks to pass before merging
  - Status checks obrigatorios: `Lint`, `Test (Python 3.11)`, `Test (Python 3.12)`, `Test (Python 3.13)`

## 5. SonarCloud Setup (Opcional/Informacional)

O SonarCloud e configurado como check **informacional** — nao bloqueia merge.

### Criando o Projeto

1. Acesse [sonarcloud.io](https://sonarcloud.io) > **+** > **Analyze new project**
2. Selecione o repositorio `backlog-manager-v2`
3. Organization: `tuyoshivinicius`
4. Project Key sera: `tuyoshivinicius_backlog-manager-v2`
5. Selecione **Previous version** como New Code definition

### Por que Informacional?

O SonarCloud Quality Gate aparece como status check no PR, mas **NAO deve ser adicionado como required check** no branch protection. Motivos:

- Evita bloqueio do fluxo quando SonarCloud esta indisponivel
- Permite ao time avaliar os resultados sem bloquear merges
- O workflow ja usa `continue-on-error: true` no scan

Se desejar tornar obrigatorio no futuro, basta adicionar `SonarCloud Code Analysis` como required status check nas branch protection rules.

## 6. Migracao de Branches

### De `001-ep001-foundation-persistence` para `main`/`develop`

1. **Renomear branch padrao**:
   - GitHub: Settings > Default branch > Alterar para `main`
   - Ou criar `main` a partir do branch atual

2. **Criar `develop`**:
   ```bash
   git checkout main
   git checkout -b develop
   git push -u origin develop
   ```

3. **Atualizar branch protection** (conforme secao 4 acima)

4. **Comunicar** aos contribuidores sobre a mudanca de branch padrao

5. **Cleanup** (opcional, apos verificacao):
   - Remover branches de feature ja mergeadas
   - Ver [CONTRIBUTING.md](CONTRIBUTING.md) para detalhes sobre cleanup de branches historicas

## Verificacao Final

Apos completar o setup, verifique:

- [ ] Secret `CODECOV_TOKEN` configurado
- [ ] Secret `SONAR_TOKEN` configurado (se usando SonarCloud)
- [ ] Trusted Publisher configurado no PyPI (environment: `pypi`)
- [ ] Trusted Publisher configurado no TestPyPI (environment: `testpypi`)
- [ ] Environments `pypi` e `testpypi` criados no GitHub
- [ ] Branch protection configurado para `main`
- [ ] Branch protection configurado para `develop`
- [ ] Projeto criado no SonarCloud (se usando)
- [ ] CI executa com sucesso em um PR de teste
