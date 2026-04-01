# Quickstart: Versionamento Automático com Git Tags e CI/CD Gitflow

**Feature**: 037-auto-versioning-cicd

## Pré-requisitos

1. Branch `develop` criada a partir de `main`
2. Tag `v0.1.0` criada no HEAD de `main` (âncora para semantic-release)
3. `python-semantic-release` adicionado como dev dependency
4. Configuração `[tool.semantic_release]` no `pyproject.toml`
5. Repositório com "Allow auto-merge" habilitado

## Fluxo de Desenvolvimento (após implementação)

### 1. Criar Feature Branch

```bash
git checkout develop
git pull origin develop
git checkout -b 042-nova-funcionalidade
```

### 2. Desenvolver e Fazer Push

```bash
# Seguir Conventional Commits
git commit -m "feat: adicionar filtro por componente"
git push origin 042-nova-funcionalidade
```

**O que acontece automaticamente**:
- `feature-ci.yml` roda lint + testes
- Se CI passa → PR criada automaticamente para `develop`
- PR é auto-mergeada (sem revisão humana)

### 3. Após Merge na Develop

**O que acontece automaticamente**:
- `develop-merge.yml` roda CI + calcula versão
- Se há commits `feat:` → versão minor incrementada
- Se há apenas `fix:` → versão patch incrementada
- PR criada para `main` com título "release: vX.Y.Z"

### 4. Review e Merge na Main

- **Revisar** a PR de release manualmente
- **Aprovar e mergear** na main

**O que acontece automaticamente**:
- `main-release.yml` roda CI + quality check
- `semantic-release` atualiza versão em `pyproject.toml` e `__init__.py`
- Commit de release criado: "chore(release): vX.Y.Z"
- Tag `vX.Y.Z` criada e pushada
- `publish.yml` disparado via `workflow_dispatch`
- Pacote publicado no PyPI
- GitHub Release criado
- PR de backmerge `main→develop` criada automaticamente

### 5. Pre-releases (Manual)

```bash
git tag v0.3.0-rc.1
git push origin v0.3.0-rc.1
# publish.yml detecta tag e publica no TestPyPI
```

## Conventional Commits — Referência Rápida

```
feat: nova funcionalidade             → minor bump (0.1.0 → 0.2.0)
fix: correção de bug                  → patch bump (0.1.0 → 0.1.1)
feat!: breaking change                → major bump (0.1.0 → 1.0.0)
chore: tarefa interna                 → sem bump
docs: documentação                    → sem bump
ci: mudança no CI                     → sem bump
test: adição/correção de testes       → sem bump
refactor: refatoração sem mudança     → sem bump
```

## Troubleshooting

| Problema | Causa Provável | Solução |
|----------|---------------|---------|
| PR duplicada criada | Race condition | Verificar concurrency groups |
| Versão não incrementou | Commits sem prefixo convencional | Verificar formato dos commits |
| publish.yml não disparou | GITHUB_TOKEN + push tag | Verificar `gh workflow run` no main-release |
| Backmerge com conflitos | Commits diretos na main | Resolver conflitos manualmente na PR |
| semantic-release falha | Sem tag âncora | Criar tag `v0.1.0` em main |
