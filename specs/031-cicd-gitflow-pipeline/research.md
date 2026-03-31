# Research: CI/CD Pipeline com GitFlow, Quality Gates e PyPI Publish

**Feature Branch**: `031-cicd-gitflow-pipeline`
**Date**: 2026-03-31

## 1. GitHub Actions Reusable Workflows (workflow_call)

**Decision**: CI workflow (`ci.yml`) tera trigger duplo — `push`/`pull_request` para execucao direta e `workflow_call` para reutilizacao pelo `publish.yml`.

**Rationale**: Um unico arquivo de workflow evita duplicacao de logica de CI. O `workflow_call` permite que o publish reutilize toda a validacao sem copiar steps.

**Alternativas consideradas**:
- Workflows separados com steps duplicados — rejeitado por violar DRY e dificultar manutencao.
- Composite actions — rejeitado por nao suportar jobs completos (apenas steps), impossibilitando a matriz de Python versions.

**Detalhes tecnicos**:
- Job que usa `uses:` (workflow_call) NAO pode ter `steps:` — delega inteiramente ao workflow chamado.
- `secrets: inherit` propaga todos os secrets do caller para o callee sem enumeracao explicita.
- `needs: ci` no job de publish garante que so executa apos CI passar.
- Variaveis `env` do caller NAO propagam para o callee — usar `inputs` se necessario.
- Limite de 4 niveis de nesting e 20 reusable workflows por caller.

## 2. OIDC Trusted Publishers para PyPI/TestPyPI

**Decision**: Usar OIDC Trusted Publishers com `pypa/gh-action-pypi-publish@release/v1` em vez de API tokens.

**Rationale**: OIDC elimina tokens de longa duracao (mais seguro), e o metodo recomendado pelo PyPI desde 2023. Nao requer rotacao de secrets.

**Alternativas consideradas**:
- API token via `PYPI_TOKEN` secret — rejeitado por ser menos seguro (token de longa duracao) e exigir rotacao manual.
- `poetry publish` — rejeitado por nao suportar OIDC; usa sistema proprio de credenciais.

**Detalhes tecnicos**:
- Permissao `id-token: write` obrigatoria no job (nao no workflow level, por principio de menor privilegio).
- `poetry build` gera artefatos em `dist/`, depois `pypa/gh-action-pypi-publish` faz upload via twine (NAO usar `poetry publish`).
- GitHub Environments (`testpypi`, `pypi`) devem corresponder exatamente ao nome registrado no Trusted Publisher do PyPI/TestPyPI.
- TestPyPI: `repository-url: https://test.pypi.org/legacy/`
- PyPI: sem `repository-url` (padrao).
- `skip-existing: true` para evitar falha em retries (409).
- Tokens OIDC NAO estao disponiveis em PRs de forks.

**Configuracao no PyPI/TestPyPI** (manual pelo mantenedor):
1. Acessar Settings > Publishing > Add Trusted Publisher
2. Informar: GitHub owner, repository, workflow filename (`publish.yml`), environment name (`pypi` ou `testpypi`)

## 3. Codecov Integration

**Decision**: Usar `codecov/codecov-action@v4` com token via `CODECOV_TOKEN` secret e `fail_ci_if_error: false`.

**Rationale**: Codecov e o servico padrao para cobertura em projetos open-source. O token e necessario desde Jan 2024 (fim do tokenless upload para repos publicos na v4).

**Alternativas consideradas**:
- Coveralls — rejeitado por menor adocao e integracao menos madura com GitHub.
- Upload manual via `codecov` CLI — rejeitado por complexidade desnecessaria.

**Detalhes tecnicos**:
- `codecov.yml` na raiz define targets (80% projeto, 80% patch), exclusoes e comentarios em PRs.
- `fail_ci_if_error: false` garante que indisponibilidade do Codecov nao bloqueia o CI.
- Coverage report em formato XML (`coverage.xml`) gerado por `pytest --cov-report=xml`.

## 4. SonarCloud Integration

**Decision**: Usar `SonarSource/sonarqube-scan-action@v5` com `continue-on-error: true` para manter como check informacional.

**Rationale**: SonarCloud oferece analise de qualidade complementar (code smells, vulnerabilidades, duplicacao). Como check opcional, agrega valor sem bloquear fluxo de desenvolvimento.

**Alternativas consideradas**:
- SonarQube self-hosted — rejeitado por complexidade operacional desnecessaria para projeto open-source.
- CodeClimate — rejeitado por menor integracao com GitHub e configuracao mais complexa.

**Detalhes tecnicos**:
- `sonar-project.properties` na raiz com `sonar.sources=src/`, `sonar.tests=tests/`, `sonar.python.coverage.reportPaths=coverage.xml`.
- `fetch-depth: 0` no checkout e obrigatorio para blame e deteccao de new code.
- Apenas `SONAR_TOKEN` como secret; `sonar.organization` e `sonar.projectKey` sao hardcoded no properties.
- NAO adicionar como required status check no branch protection — manter informacional.
- `continue-on-error: true` no step para nao falhar o job se SonarCloud estiver indisponivel.

## 5. GitHub Auto-Generated Release Notes

**Decision**: Usar `.github/release.yml` para configurar categorias de release notes baseadas em labels de PR.

**Rationale**: Solucao nativa do GitHub, sem dependencias externas. Release notes sao geradas automaticamente ao criar GitHub Release.

**Alternativas consideradas**:
- Conventional Commits + `release-please` — rejeitado por adicionar complexidade de tooling e convencao de commits.
- Changelog manual — rejeitado por ser propenso a erros e trabalho repetitivo.

**Detalhes tecnicos**:
- Categorias: Features, Bug Fixes, Documentation, CI/CD, Dependencies.
- Labels: `enhancement`, `bug`, `documentation`, `ci`, `dependencies`.
- `gh release create` com `--generate-notes` usa as categorias definidas.

## 6. Validacao de Sincronizacao de Versao

**Decision**: Step no CI que extrai versao de `pyproject.toml` e `src/backlog_manager/__init__.py` e falha se divergirem.

**Rationale**: Garante que o pacote publicado reflete a versao correta. Previne publicacao acidental com versao desatualizada.

**Alternativas consideradas**:
- `poetry-dynamic-versioning` — rejeitado por adicionar dependencia e complexidade; a versao e atualizada manualmente e infrequentemente.
- Hook de pre-commit para validar — ja coberto pelo CI; pre-commit e redundante para esta validacao.

**Detalhes tecnicos**:
- Extrair versao do `pyproject.toml` via `poetry version -s` ou `grep`.
- Extrair versao do `__init__.py` via `python -c "from backlog_manager import __version__; print(__version__)"` ou `grep`.
- Comparar e falhar com mensagem explicita se divergirem.

## 7. Matriz Python 3.11/3.12/3.13

**Decision**: Usar `strategy.matrix.python-version` com [3.11, 3.12, 3.13] no job de test.

**Rationale**: O `pyproject.toml` declara suporte para `>=3.11,<3.15`. Testar nas 3 versoes principais garante compatibilidade.

**Detalhes tecnicos**:
- Job de lint roda apenas em Python 3.11 (versao minima suportada) — nao precisa de matriz.
- Job de test roda em matriz 3.11/3.12/3.13.
- Coverage report e gerado apenas na versao 3.11 (para upload unico ao Codecov/SonarCloud).
- `fail-fast: false` para que falha em uma versao nao cancele as outras.
