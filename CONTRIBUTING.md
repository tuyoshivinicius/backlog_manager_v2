# Guia de Contribuicao

Obrigado pelo interesse em contribuir com o **Backlog Manager**! Este documento descreve o fluxo de trabalho, estrategia de branching e processo de release do projeto.

## Fluxo GitFlow

O projeto segue o modelo **GitFlow** para gerenciamento de branches:

```text
main ─────────────────────────────────────────────── producao (tags vX.Y.Z)
  │                          ▲            ▲
  │                          │            │
  │                     merge + tag   merge + tag
  │                          │            │
  ├── release/1.0.0 ────────┘            │
  │                                       │
  ├── hotfix/1.0.1 ──────────────────────┘
  │                                       │
  │   develop ←── feature/* ──┐           │
  │     │                     │           │
  │     ├── feature/foo ──────┤           │
  │     ├── feature/bar ──────┘           │
  │     │                                 │
  │     └── (hotfix tambem faz merge aqui)┘
  │
```

### Branches

| Branch | Proposito | Origem | Destino |
|--------|-----------|--------|---------|
| `main` | Codigo em producao, cada commit e uma release | — | — |
| `develop` | Integracao de features, proximo release | `main` | `release/*` |
| `feature/*` | Desenvolvimento de novas funcionalidades | `develop` | `develop` |
| `release/*` | Preparacao de release (bump versao, fixes) | `develop` | `main` + `develop` |
| `hotfix/*` | Correcoes urgentes em producao | `main` | `main` + `develop` |

## Criando Branches

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
git pull origin develop
git checkout -b release/1.1.0
# Bump versao (ver secao Versionamento)
git commit -m "bump: version 1.1.0"
git push -u origin release/1.1.0
# Abrir PR para main
```

### Hotfix

```bash
git checkout main
git pull origin main
git checkout -b hotfix/1.0.1
# Corrigir bug + bump versao
git commit -m "fix: descricao do hotfix"
git push -u origin hotfix/1.0.1
# Abrir PR para main E para develop
```

## Pull Requests

1. Crie a branch seguindo a convencao acima
2. Faca push e abra um PR para a branch destino
3. Aguarde os checks de CI passarem (lint, test, quality)
4. Solicite review de pelo menos 1 mantenedor (para PRs em `main`)
5. Apos aprovacao, faca merge (squash ou merge commit conforme preferencia)

## Versionamento Semantico

O projeto segue [Semantic Versioning](https://semver.org/):

- **MAJOR** (X.0.0): Mudancas incompativeis na API
- **MINOR** (0.X.0): Novas funcionalidades retrocompativeis
- **PATCH** (0.0.X): Correcoes de bugs retrocompativeis

### Processo de Bump de Versao

**IMPORTANTE**: A versao DEVE ser atualizada em **dois arquivos** antes de criar a tag:

1. `pyproject.toml` — campo `version` na secao `[tool.poetry]`
2. `src/backlog_manager/__init__.py` — variavel `__version__`

```bash
# Exemplo: bump para 1.1.0
# 1. Atualizar pyproject.toml
poetry version 1.1.0

# 2. Atualizar __init__.py manualmente
# __version__ = "1.1.0"

# 3. Commit
git add pyproject.toml src/backlog_manager/__init__.py
git commit -m "bump: version 1.1.0"
```

O CI valida automaticamente que as versoes estao sincronizadas. Se divergirem, o job de lint falhara.

## Release

### Release Final

1. Criar branch `release/X.Y.Z` a partir de `develop`
2. Fazer bump de versao (ver acima)
3. Abrir PR para `main` e aguardar aprovacao
4. Apos merge em `main`, criar tag:

```bash
git checkout main
git pull origin main
git tag vX.Y.Z
git push origin vX.Y.Z
```

5. O workflow de publish dispara automaticamente:
   - CI completo (lint + test + quality)
   - Build do pacote
   - Publicacao no PyPI
   - Criacao de GitHub Release com changelog

### Pre-release (RC/Beta/Alpha)

```bash
git tag v1.1.0-rc1
git push origin v1.1.0-rc1
# → CI valida → publica no TestPyPI (nao no PyPI oficial)
```

### Merge de Volta para develop

Apos o merge de um release ou hotfix em `main`, faca merge de volta em `develop`:

```bash
git checkout develop
git pull origin develop
git merge main
git push origin develop
```

## Migracao de Branches

### Estado Atual

O branch padrao historico do repositorio e `001-ep001-foundation-persistence`. A migracao para o modelo GitFlow (`main`/`develop`) sera feita manualmente pelo mantenedor.

### Plano de Migracao

1. Renomear `001-ep001-foundation-persistence` para `main` (ou criar `main` a partir dele)
2. Criar branch `develop` a partir de `main`
3. Atualizar o branch padrao no GitHub para `main`
4. Atualizar branch protection rules (ver [SETUP_CI.md](SETUP_CI.md))
5. Comunicar aos contribuidores a mudanca

### Cleanup de Branches Historicas

Branches com prefixo numerico (`001-*`, `019-*`, etc.) sao branches de feature historicas. Apos a migracao:

- Branches ja mergeadas podem ser removidas com seguranca
- Branches com trabalho em andamento devem ser rebaseadas para `develop`
- NAO deletar branches automaticamente — revisar caso a caso
