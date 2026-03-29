---
description: Automatizar workflow de ship - commit, formatacao, PR, review, merge e checkout da branch principal. (project)
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

Voce **DEVE** considerar a entrada do usuario antes de prosseguir (se nao estiver vazia).

---

## 0. Parse de Argumentos

Analise `$ARGUMENTS` para extrair:

| Flag | Default | Comportamento |
|------|---------|---------------|
| `--skip-review` | false | Pular etapa de code review (Step 5) |
| `--draft` | false | Criar PR como draft (parar apos Step 4) |
| `--message "..."` | auto | Sobrescrever mensagem de commit |

Qualquer texto restante e tratado como descricao adicional para o commit.

Armazene internamente:
- `SKIP_REVIEW` = true/false
- `DRAFT_MODE` = true/false
- `CUSTOM_MESSAGE` = string ou vazio
- `EXTRA_DESCRIPTION` = texto restante

---

## 1. Deteccao de Contexto

### 1.1 Identificar Branch e Epic

```bash
CURRENT_BRANCH=$(git branch --show-current)
echo "Branch: $CURRENT_BRANCH"
```

Extraia o numero do epic do nome da branch usando o padrao `NNN-epNNN-*`:
- Exemplo: `018-ep018-layout-migracao-paineis` -> `EP-018`
- Se nao seguir o padrao, pergunte ao usuario o numero do epic via AskUserQuestion

**HALT** se estiver na branch principal:
```bash
if [ "$(git branch --show-current)" = "001-ep001-foundation-persistence" ]; then
    echo "ERRO: Voce esta na branch principal."
fi
```

### 1.2 Verificar Estado

```bash
git status --short
```

- Se nao houver mudancas (staged, unstaged, untracked) E nao houver commits alem da main:
  ```bash
  git log 001-ep001-foundation-persistence..HEAD --oneline
  ```
  - Se tambem nao houver commits, HALT: "Nenhuma alteracao para entregar."
  - Se houver commits mas sem mudancas locais, pule para Step 4 (Abrir PR)

---

## 2. Commit de Todas as Alteracoes

### 2.1 Stage

```bash
git add -A
```

### 2.2 Gerar Mensagem de Commit

Se `CUSTOM_MESSAGE` fornecida, use:
```
feat(EP-NNN): <CUSTOM_MESSAGE>
```

Se nao, analise o diff para gerar automaticamente:
```bash
git diff --cached --stat
git diff --cached
```

Regras para gerar a mensagem:
- Prefixo baseado no tipo de mudanca: `feat(EP-NNN):`, `fix(EP-NNN):`, `docs(EP-NNN):`, `refactor(EP-NNN):`
- Descricao concisa em ingles (padrao do projeto)
- Inclua `EXTRA_DESCRIPTION` se fornecida

### 2.3 Criar Commit

```bash
git commit -m "$(cat <<'EOF'
feat(EP-NNN): <mensagem gerada>

<descricao detalhada se necessario>

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

Se o commit falhar por pre-commit hooks, NAO entre em panico. Prossiga para Step 3.

---

## 3. Verificar e Corrigir Formatacao

### 3.1 Executar Pre-commit

```bash
poetry run pre-commit run --all-files 2>&1
```

Se todos passaram, pule para Step 4.

### 3.2 Classificar Problemas

**Auto-corrigiveis** (hooks ja modificam os arquivos):
- `trailing-whitespace`
- `end-of-file-fixer`
- `black`
- `isort`

**Requerem intervencao manual:**
- `mypy` - erros de tipo
- `pydocstyle` - docstrings

### 3.3 Correcoes Automaticas

Re-execute pre-commit. Os hooks auto-corrigiveis (black, isort, whitespace) ja aplicaram as correcoes na primeira execucao:
```bash
poetry run pre-commit run --all-files 2>&1
```

### 3.4 Corrigir Erros de mypy

Se mypy falhou, para CADA erro:

1. Leia o arquivo indicado no erro
2. Identifique o problema:
   - **Unreachable code** (`[unreachable]`): Remover codigo morto
   - **Missing return type**: Adicionar type hint de retorno
   - **Incompatible types**: Ajustar tipos
   - **Missing imports**: Adicionar imports
3. Aplique a correcao via Edit
4. Verifique: `poetry run mypy src/ --ignore-missing-imports`

### 3.5 Corrigir Erros de pydocstyle

Se pydocstyle falhou:
- **Missing docstring**: Adicionar docstring no estilo Google
- **Wrong format**: Ajustar formato existente

### 3.6 Re-verificar

```bash
poetry run pre-commit run --all-files 2>&1
```

Repita steps 3.4-3.6 ate maximo **3 tentativas**.

Se ainda houver falhas apos 3 tentativas:
- Use AskUserQuestion: "Ainda existem erros de formatacao que nao consegui resolver automaticamente. Deseja continuar mesmo assim?"
- Opcoes: "Sim, continuar" / "Nao, parar aqui"
- Se "Nao", HALT e exiba os erros restantes

### 3.7 Commit das Correcoes

Se houve qualquer correcao:
```bash
git add -A
git commit -m "$(cat <<'EOF'
style(EP-NNN): fix formatting and linting issues

Auto-fix: black, isort, trailing whitespace, mypy, pydocstyle

Co-Authored-By: Claude Opus 4.6 (1M context) <noreply@anthropic.com>
EOF
)"
```

---

## 4. Abrir Pull Request

### 4.1 Push da Branch

```bash
git push -u origin "$(git branch --show-current)"
```

### 4.2 Analisar Mudancas para Descricao do PR

```bash
git log 001-ep001-foundation-persistence..HEAD --oneline
git diff 001-ep001-foundation-persistence...HEAD --stat
```

### 4.3 Criar PR

Gere titulo curto (<70 chars) e body com resumo das mudancas.

Se `DRAFT_MODE`:
```bash
gh pr create --base 001-ep001-foundation-persistence --title "<titulo>" --body "$(cat <<'EOF'
## Resumo
<bullets com mudancas principais>

## Arquivos Modificados
<lista dos modulos/areas afetadas>

## Checklist
- [ ] Testes unitarios passando
- [ ] Testes de integracao passando
- [ ] mypy sem erros
- [ ] pre-commit hooks passando

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)" --draft
```

Se NAO e draft:
```bash
gh pr create --base 001-ep001-foundation-persistence --title "<titulo>" --body "$(cat <<'EOF'
## Resumo
<bullets com mudancas principais>

## Arquivos Modificados
<lista dos modulos/areas afetadas>

## Checklist
- [ ] Testes unitarios passando
- [ ] Testes de integracao passando
- [ ] mypy sem erros
- [ ] pre-commit hooks passando

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

Capture o numero e URL do PR.

**Se `DRAFT_MODE`**: Exiba o link do PR ao usuario e **HALT** aqui.

---

## 5. Code Review

**Se `SKIP_REVIEW` esta ativo, pule para Step 6.**

### 5.1 Obter Diff Completo

```bash
git diff 001-ep001-foundation-persistence...HEAD
```

### 5.2 Analise

Revise o diff verificando:

**Seguranca:**
- Credenciais hardcoded ou secrets expostos
- SQL injection ou inputs nao sanitizados
- Permissoes inadequadas

**Arquitetura (Clean Architecture):**
- Dependencias na direcao correta: Domain <- Application <- Infrastructure <- Presentation
- Domain NAO importa de Infrastructure ou Presentation
- Application NAO importa de Infrastructure ou Presentation

**Qualidade:**
- Funcoes muito longas (>50 linhas)
- Duplicacao de codigo
- Nomes descritivos
- Type hints em parametros e retornos

**Testes:**
- Novos modulos tem testes correspondentes
- Testes cobrem happy path e edge cases

### 5.3 Relatorio

Apresente ao usuario:

```markdown
## Code Review

### Seguranca: OK/ATENCAO
<detalhes se houver>

### Arquitetura: OK/ATENCAO
<detalhes se houver>

### Qualidade: OK/ATENCAO
<detalhes se houver>

### Testes: OK/ATENCAO
<detalhes se houver>

### Veredicto: APROVADO / MUDANCAS SUGERIDAS
```

Se houver problemas criticos (seguranca ou violacao de arquitetura):
- Use AskUserQuestion: "Foram encontrados problemas no review. Deseja corrigir antes de mergear?"
- Opcoes: "Sim, corrigir" / "Nao, mergear assim mesmo"
- Se "Sim": aplique correcoes, commit, push, e re-execute o review

---

## 6. Merge

### 6.1 Confirmacao

Use AskUserQuestion:
- "PR #<numero> pronto para merge em 001-ep001-foundation-persistence. Confirma?"
- Opcoes: "Sim, mergear" / "Nao, cancelar"

Se "Nao", HALT.

### 6.2 Executar Merge

```bash
gh pr merge <PR_NUMBER> --merge --delete-branch
```

Se falhar (conflitos, checks):
- Informe o erro
- Sugira resolucao
- HALT

---

## 7. Checkout da Branch Principal

```bash
git checkout 001-ep001-foundation-persistence
git pull origin 001-ep001-foundation-persistence
```

Exiba mensagem final:

```
Ship completo!

- Commit: <hash>
- PR: #<numero> (<url>)
- Branch <feature_branch> mergeada e deletada
- Agora em: 001-ep001-foundation-persistence

Pronto para a proxima implementacao.
```

---

## Tratamento de Erros

Em qualquer etapa, se ocorrer um erro inesperado:
1. Exiba o erro completo
2. Informe em qual etapa o processo parou
3. Sugira como retomar (ex: "Execute /ship novamente para continuar")
4. **HALT** - nunca continue silenciosamente apos um erro
