# Feature Description: Versionamento Automatico com Git Tags e CI/CD Gitflow

## Entrada para `/speckit.specify`

```text
Implementar versionamento automatico baseado em Conventional Commits com tags Git integrado ao pipeline CI/CD, seguindo fluxo Gitflow completo com criacao automatica de PRs e publicacao no PyPI.

CONTEXTO E PROBLEMA:
O pacote zion-backlog-manager versao 0.1.0 ja foi publicado no PyPI e nao pode ser sobrescrito. Atualmente a versao e gerenciada manualmente no pyproject.toml e __init__.py, sem relacao com tags Git. O fluxo de CI/CD existente nao automatiza a criacao de PRs entre branches, nem incrementa versoes automaticamente. Isso causa falhas de publicacao quando a versao nao e atualizada antes do deploy.

ESTADO ATUAL DO CI/CD:
- ci.yml: Roda lint (ruff, mypy) + testes + coverage em push/PR para develop/main. Quality job roda SonarCloud apenas na main.
- publish.yml: Trigga em tags v*, roda CI, builda com Poetry, publica no TestPyPI (pre-release) ou PyPI (release), cria GitHub Release.
- Versao hardcoded: pyproject.toml (version = "0.1.0") e src/backlog_manager/__init__.py (__version__ = "0.1.0"). CI valida que ambos estao em sincronia.
- Branching: Gitflow com develop, main, feature/*, release/*, hotfix/*.
- release.yml: Categoriza release notes por labels (enhancement, bug, docs, ci, deps).

FERRAMENTAS E ESTRATEGIA:
- python-semantic-release para versionamento automatico baseado em Conventional Commits
- GitHub CLI (gh) para criacao automatica de PRs nos workflows
- Conventional Commits (feat:, fix:, BREAKING CHANGE:) para determinar bump de versao (patch/minor/major)

FLUXO PROPOSTO:

1. FEATURE BRANCH (push em feature/*):
   - CI roda lint (ruff check, ruff format --check, mypy)
   - CI roda testes com coverage
   - Se passa, workflow abre PR automaticamente de feature/* para develop (se PR nao existir)
   - Titulo da PR: "feat: <branch-description>" (extraido do nome da branch)

2. MERGE NA DEVELOP (PR mergeada em develop):
   - CI roda lint + testes + coverage (job ci existente)
   - Quality job roda Codecov
   - python-semantic-release calcula proxima versao baseado nos commits convencionais desde a ultima tag
   - Workflow abre PR automaticamente de develop para main
   - Titulo da PR inclui versao calculada: "release: v<X.Y.Z>"
   - Body da PR lista os commits/features incluidos nesta versao

3. MERGE NA MAIN (PR mergeada em main):
   - CI roda lint + testes + coverage + quality completo (SonarCloud)
   - python-semantic-release atualiza versao no pyproject.toml e __init__.py
   - Cria commit de versao: "chore(release): v<X.Y.Z>"
   - Cria tag Git: v<X.Y.Z>
   - Push da tag dispara publish.yml existente (build + PyPI + GitHub Release)

ARQUIVOS A CRIAR/MODIFICAR:

1. .github/workflows/feature-ci.yml (NOVO):
   - Trigger: push em branches feature/*
   - Jobs: lint, test, auto-pr-to-develop
   - Usa gh pr create para abrir PR para develop

2. .github/workflows/develop-merge.yml (NOVO):
   - Trigger: push em develop (detecta merge de PR)
   - Jobs: ci (reusa ci.yml), calculate-version, auto-pr-to-main
   - Usa python-semantic-release --noop para calcular versao sem aplicar
   - Usa gh pr create para abrir PR para main com versao no titulo

3. .github/workflows/main-merge.yml (NOVO):
   - Trigger: push em main (detecta merge de PR)
   - Jobs: ci (reusa ci.yml), quality, release
   - Usa python-semantic-release para: bump version, commit, tag, push
   - Tag push dispara publish.yml existente

4. .github/workflows/ci.yml (MODIFICAR):
   - Remover triggers de push direto em develop/main (sera chamado via workflow_call pelos novos workflows)
   - Manter workflow_call e pull_request triggers
   - Remover version sync check (sera gerenciado pelo semantic-release)

5. .github/workflows/publish.yml (MANTER):
   - Nenhuma alteracao necessaria — ja trigga em tags v* corretamente
   - Continua com logica de TestPyPI (pre-release) e PyPI (release)

6. pyproject.toml (MODIFICAR):
   - Adicionar configuracao do python-semantic-release:
     - version_toml = ["pyproject.toml:tool.poetry.version"]
     - version_variables = ["src/backlog_manager/__init__.py:__version__"]
     - branch = "main"
     - commit_message = "chore(release): v{version}"
     - tag_format = "v{version}"
   - Adicionar python-semantic-release como dev dependency

7. .github/release.yml (MANTER):
   - Nenhuma alteracao — categorias de release notes ja estao configuradas

CONVENTIONAL COMMITS - PADRAO EXIGIDO:
- feat: nova feature (bump minor: 0.1.0 -> 0.2.0)
- fix: correcao de bug (bump patch: 0.1.0 -> 0.1.1)
- feat!: ou BREAKING CHANGE: (bump major: 0.1.0 -> 1.0.0)
- chore:, docs:, test:, ci:, refactor: (sem bump de versao)
- Commits que nao seguem o padrao sao ignorados pelo semantic-release

PERMISSOES GITHUB:
- Workflows precisam de permissions: contents: write para criar tags e commits
- Workflows precisam de permissions: pull-requests: write para criar PRs
- GITHUB_TOKEN padrao do Actions e suficiente (nao precisa de PAT)

CRITERIOS DE SUCESSO:
1. Push em feature/* roda lint+testes e abre PR para develop automaticamente
2. Merge de PR na develop roda CI+quality e abre PR para main com versao no titulo
3. Merge de PR na main cria tag Git automaticamente com versao correta
4. Tag criada dispara publish.yml e pacote e publicado no PyPI com versao correta
5. Versao no pyproject.toml e __init__.py sao atualizadas automaticamente pelo semantic-release
6. Conventional Commits determinam corretamente o tipo de bump (patch/minor/major)
7. PRs duplicadas nao sao criadas (workflow verifica se PR ja existe antes de criar)
8. GitHub Release e criado com release notes categorizadas
9. Fluxo completo e2e: feature/* -> develop -> main -> tag -> PyPI funciona sem intervencao manual

RESTRICOES:
- Nao alterar schema do banco SQLite
- Nao alterar logica de negocio ou codigo de producao (escopo puramente CI/CD)
- Manter compatibilidade com Python 3.13+
- publish.yml deve continuar funcionando para tags manuais (backward compatible)
- Nao usar PAT (Personal Access Token) — apenas GITHUB_TOKEN
- Nao quebrar workflows existentes durante a transicao
- Pre-release tags (-rc, -beta, -alpha) continuam indo para TestPyPI
- Versao inicial apos implementacao deve ser > 0.1.0 (ja publicada no PyPI)
```
