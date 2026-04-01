---
description: Automatizar workflow de ship - commit, formatacao, PR e merge na develop. (project)
allowed-tools:
  - Bash
  - Read
  - Glob
  - Grep
  - Edit
  - Write
  - AskUserQuestion
---

## Entrada do Usuario

```text
$ARGUMENTS
```

Considere a entrada do usuario antes de prosseguir (se nao estiver vazia).

---

## 0. Parse de Argumentos

Extraia de `$ARGUMENTS`:

| Flag | Default | Comportamento |
|------|---------|---------------|
| `--draft` | false | Criar PR como draft (parar apos criar o PR) |
| `--message "..."` | auto | Sobrescrever mensagem de commit |

Texto restante e tratado como descricao adicional para o commit.

---

## 1. Deteccao de Contexto

```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Branch: $CURRENT_BRANCH"
git status --short
```

Determine o modo de operacao:
- **Branch `develop`** -> `MODE=develop` (apenas commit, sem PR/merge)
- **Qualquer outra branch** -> `MODE=feature` (commit + PR + merge na develop)

Extraia o epic do nome da branch (padrao `NNN-epNNN-*`, ex: `018-ep018-layout` -> `EP-018`). Se nao seguir o padrao e nao for `develop`, pergunte via AskUserQuestion.

Verifique estado:
```bash
git log develop..HEAD --oneline  # so para MODE=feature
```

- Sem mudancas locais E sem commits alem da develop -> HALT: "Nenhuma alteracao para entregar."
- Sem mudancas locais mas com commits (MODE=feature) -> pule para Step 4.

---

## 2. Commit

```bash
git add -A
git diff --cached --stat
git diff --cached
```

Gere a mensagem de commit (ou use `--message` se fornecida):
- Prefixo: `feat(EP-NNN):`, `fix(EP-NNN):`, `docs(EP-NNN):`, `refactor(EP-NNN):` conforme o tipo
- Se `MODE=develop` e sem epic identificavel, use prefixo sem scope: `feat:`, `fix:`, etc.
- Descricao concisa em ingles

```bash
git commit -m "$(cat <<'EOF'
<tipo>(EP-NNN): <mensagem>

<descricao detalhada se necessario>
EOF
)"
```

---

## 3. Formatacao

```bash
poetry run pre-commit run --all-files 2>&1
```

Se todos passaram:
- `MODE=develop` -> pule para Step 7 (finalizar)
- `MODE=feature` -> pule para Step 4

Se falhou, corrija os problemas:
- **Auto-corrigiveis** (black, isort, whitespace, end-of-file): ja foram corrigidos pelos hooks, basta re-executar.
- **mypy**: leia o arquivo, corrija o erro de tipo via Edit, verifique com `poetry run mypy src/ --ignore-missing-imports`.
- **pydocstyle**: adicione/ajuste docstrings no estilo Google.

Re-execute `poetry run pre-commit run --all-files` apos cada rodada de correcoes. Maximo **3 tentativas**. Se ainda falhar, pergunte ao usuario se deseja continuar via AskUserQuestion.

Se houve correcoes:
```bash
git add -A
git commit -m "$(cat <<'EOF'
style(EP-NNN): fix formatting and linting issues
EOF
)"
```

- `MODE=develop` -> pule para Step 7 (finalizar)
- `MODE=feature` -> continue para Step 4

---

## 4. Pull Request (MODE=feature apenas)

```bash
git push -u origin "$(git branch --show-current)"
git log develop..HEAD --oneline
git diff develop...HEAD --stat
```

Crie o PR com titulo curto (<70 chars). Adicione `--draft` se `DRAFT_MODE`:

```bash
gh pr create --base develop --title "<titulo>" --body "$(cat <<'EOF'
## Resumo
<bullets com mudancas principais>

## Arquivos Modificados
<lista dos modulos/areas afetadas>

## Checklist
- [ ] Testes passando
- [ ] mypy sem erros
- [ ] pre-commit hooks passando
EOF
)"
```

Se `DRAFT_MODE`: exiba o link do PR e **HALT**.

---

## 5. Merge (MODE=feature apenas)

Confirme com o usuario via AskUserQuestion: "PR #<numero> pronto para merge na develop. Confirma?"

```bash
gh pr merge <PR_NUMBER> --merge --delete-branch
```

Se falhar, informe o erro e HALT.

---

## 6. Checkout develop (MODE=feature apenas)

```bash
git checkout develop
git pull origin develop
```

---

## 7. Finalizar

Exiba conforme o modo:

**MODE=feature:**
```
Ship completo!
- PR: #<numero> (<url>)
- Branch <feature_branch> mergeada e deletada
- Agora em: develop
```

**MODE=develop:**
```
Ship completo!
- Commit: <hash>
- Branch: develop
```

---

## Tratamento de Erros

Em qualquer etapa, se ocorrer erro inesperado:
1. Exiba o erro completo e em qual etapa parou
2. Sugira como retomar (ex: "Execute /ship novamente")
3. **HALT**
