# Feature Specification: Versionamento Automático com Git Tags e CI/CD Gitflow

**Feature Branch**: `037-auto-versioning-cicd`
**Created**: 2026-04-01
**Status**: Draft
**Input**: User description: "Implementar versionamento automatico baseado em Conventional Commits com tags Git integrado ao pipeline CI/CD, seguindo fluxo Gitflow completo com criacao automatica de PRs e publicacao no PyPI."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Fluxo Automático Feature-to-Develop (Priority: P1)

Como desenvolvedor, ao fazer push de uma feature branch, quero que o pipeline rode lint e testes automaticamente e, se tudo passar, abra uma Pull Request para a branch develop sem intervenção manual.

**Why this priority**: Este é o ponto de entrada do fluxo Gitflow automatizado. Sem a automação de PRs de feature branches, todo o restante do pipeline depende de ação manual, anulando o propósito da automação.

**Independent Test**: Pode ser testado criando uma feature branch, fazendo push, e verificando que uma PR é criada automaticamente para develop com título adequado.

**Acceptance Scenarios**:

1. **Given** um push em uma branch de feature (ex: `037-auto-versioning-cicd`) com código válido, **When** o pipeline de CI completa com sucesso (lint + testes), **Then** uma PR é criada automaticamente da feature branch para `develop` com título formatado como "feat: <descrição-da-branch>".
2. **Given** um push em uma branch de feature que já possui PR aberta para develop, **When** o pipeline roda, **Then** nenhuma PR duplicada é criada.
3. **Given** um push em uma branch de feature com falha de lint ou testes, **When** o pipeline falha, **Then** nenhuma PR é criada automaticamente.
4. **Given** uma PR automática de feature→develop com CI verde, **When** todas as checks passam, **Then** a PR é auto-mergeada sem revisão humana.

---

### User Story 2 - Cálculo de Versão e PR Automática para Main (Priority: P1)

Como mantenedor do projeto, ao mergear uma PR na develop, quero que o sistema calcule automaticamente a próxima versão baseada nos Conventional Commits e abra uma PR para main com a versão no título.

**Why this priority**: Este é o elo central que conecta o desenvolvimento à publicação. Sem o cálculo automático de versão, o versionamento continua manual e sujeito a erros.

**Independent Test**: Pode ser testado mergeando uma PR na develop e verificando que uma PR é criada para main com a versão correta no título e lista de mudanças no body.

**Acceptance Scenarios**:

1. **Given** uma PR mergeada na develop contendo commits `feat:`, **When** o workflow de develop executa, **Then** uma PR é criada de develop para main com título "release: vX.Y.Z" onde a versão minor foi incrementada.
2. **Given** uma PR mergeada na develop contendo apenas commits `fix:`, **When** o workflow executa, **Then** a versão patch é incrementada no título da PR.
3. **Given** uma PR mergeada na develop contendo commits com `BREAKING CHANGE:` ou `feat!:`, **When** o workflow executa, **Then** a versão major é incrementada.
4. **Given** uma PR mergeada na develop contendo apenas commits sem tipo convencional (chore, docs, etc.), **When** o workflow executa, **Then** nenhum bump de versão é calculado e nenhuma PR é criada para main.

---

### User Story 3 - Release Automático na Main com Tag e Publicação (Priority: P1)

Como mantenedor do projeto, ao mergear a PR de release na main, quero que o sistema atualize automaticamente os arquivos de versão, crie uma tag Git e dispare a publicação no PyPI.

**Why this priority**: Este é o objetivo final do fluxo — garantir que cada merge na main resulte em uma release publicada sem intervenção manual, eliminando falhas de publicação por versão desatualizada.

**Independent Test**: Pode ser testado mergeando uma PR na main e verificando que os arquivos de versão são atualizados, a tag é criada e o workflow de publicação é disparado.

**Acceptance Scenarios**:

1. **Given** uma PR de release mergeada na main, **When** o workflow de main executa, **Then** a versão é atualizada no `pyproject.toml` e `__init__.py`, um commit de release é criado, e uma tag `vX.Y.Z` é pushada.
2. **Given** uma tag `vX.Y.Z` pushada (sem sufixo pre-release), **When** o workflow de publicação é disparado, **Then** o pacote é publicado no PyPI com a versão correta.
3. **Given** uma tag `vX.Y.Z-rc.1` pushada manualmente, **When** o workflow de publicação é disparado, **Then** o pacote é publicado no TestPyPI (não no PyPI).
4. **Given** uma release mergeada na main com tag criada, **When** o workflow de main completa, **Then** uma PR automática de backmerge main→develop é criada para sincronização.

---

### User Story 4 - Configuração de Conventional Commits e Semantic Release (Priority: P2)

Como mantenedor do projeto, quero que o projeto esteja configurado com python-semantic-release para que o versionamento automático funcione baseado nos padrões de Conventional Commits.

**Why this priority**: É uma dependência técnica para as stories P1, mas como configuração, pode ser testada independentemente verificando que as configurações estão corretas nos arquivos do projeto.

**Independent Test**: Pode ser testado executando `semantic-release --noop` localmente e verificando que o cálculo de versão funciona corretamente.

**Acceptance Scenarios**:

1. **Given** o projeto com python-semantic-release configurado, **When** existem commits `feat:` desde a última tag, **Then** o cálculo `--noop` retorna a próxima versão minor corretamente.
2. **Given** a configuração do semantic-release no pyproject.toml, **When** o release é executado, **Then** ambos `pyproject.toml` e `__init__.py` são atualizados com a nova versão.

---

### User Story 5 - Compatibilidade com Fluxo Manual Existente (Priority: P2)

Como mantenedor do projeto, quero que o fluxo de criação manual de tags continue funcionando, garantindo retrocompatibilidade durante e após a transição para automação.

**Why this priority**: Garante que a transição não quebre o fluxo existente, permitindo rollback para o processo manual se necessário.

**Independent Test**: Pode ser testado criando uma tag manual `vX.Y.Z` e verificando que o publish.yml é disparado normalmente.

**Acceptance Scenarios**:

1. **Given** uma tag manual `v0.2.0` criada diretamente no Git, **When** a tag é pushada, **Then** o workflow de publicação é disparado e funciona normalmente.
2. **Given** os novos workflows instalados, **When** o CI existente é chamado via pull_request trigger, **Then** funciona sem alterações de comportamento.

---

### Edge Cases

- O que acontece quando múltiplos pushes rápidos ocorrem na mesma feature branch? O workflow deve ser idempotente e não criar PRs duplicadas.
- Como o sistema se comporta quando a develop não tem novos commits convencionais desde a última tag? Nenhum bump deve ocorrer e nenhuma PR deve ser criada para main.
- O que acontece se o merge na main falha durante a criação do commit de release? O workflow deve falhar de forma limpa sem criar tags órfãs.
- Como o sistema trata conflitos de merge na PR automática develop→main? A PR é criada mas marcada com conflitos para resolução manual.
- O que acontece se a versão calculada já existe como tag no repositório? O semantic-release deve detectar isso e não criar tag duplicada.
- Como o sistema se comporta quando a conexão com PyPI falha durante a publicação? O workflow de publicação deve falhar e permitir re-execução manual.
- Múltiplos pushes rápidos na mesma branch: concurrency groups com `cancel-in-progress: true` cancelam runs anteriores automaticamente, evitando race conditions e desperdício de minutos de CI.

## Clarifications

### Session 2026-04-01

- Q: Qual padrão de nomenclatura de branches o workflow deve monitorar (`feature/*` vs padrão atual `NNN-descricao`)? → A: Manter padrão atual — workflow dispara para todas as branches exceto `main`/`develop`.
- Q: PRs automáticas devem ser auto-mergeadas ou aguardar revisão humana? → A: Auto-merge feature→develop (se CI passa); revisão manual develop→main.
- Q: Como manter develop sincronizada com main após release? → A: Criar PR automática main→develop após cada release (backmerge).
- Q: Como tags pre-release (RC/Beta/Alpha) são criadas? → A: Tags pre-release são criadas manualmente (`git tag vX.Y.Z-rc.N`); apenas o publish.yml reage ao push da tag.
- Q: Quem cria a branch develop e quando? → A: Criar `develop` a partir de `main` como parte desta feature (documentado no plano de implementação).
- Q: Como o workflow da main aciona publish.yml se GITHUB_TOKEN não dispara novos workflows? → A: Usar `gh workflow run` (workflow_dispatch) com `confirm=yes` e a ref da tag, sem modificar publish.yml.
- Q: A constraint "O release.yml existente não deve ser modificado" refere-se a qual arquivo? → A: É um erro na spec — release.yml não existe. Constraint removida.
- Q: Quais triggers de push devem ser removidos do ci.yml? → A: Remover push em `develop` e `main` apenas; manter `pull_request` e `workflow_call`.
- Q: Como tratar o input `confirm` do publish.yml no dispatch automático? → A: Passar `confirm=yes` automaticamente no `gh workflow run`, sem alterar publish.yml.
- Q: Habilitar cancelamento automático de runs anteriores via concurrency groups? → A: Sim — usar `concurrency` com `cancel-in-progress: true` para feature branches.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE executar lint (ruff check, ruff format --check, mypy) e testes com coverage em todo push para branches de feature (qualquer branch exceto `main`/`develop`).
- **FR-002**: O sistema DEVE criar automaticamente uma PR da feature branch para `develop` quando o CI passa com sucesso, com título no formato "feat: <descrição-extraída-da-branch>".
- **FR-003**: O sistema DEVE verificar se já existe uma PR aberta da feature branch para `develop` antes de criar uma nova, evitando duplicatas.
- **FR-004**: O sistema DEVE calcular a próxima versão semântica baseada nos Conventional Commits ao detectar merge na branch `develop`.
- **FR-005**: O sistema DEVE criar automaticamente uma PR de `develop` para `main` com título "release: vX.Y.Z" e body contendo a lista de mudanças incluídas.
- **FR-006**: O sistema DEVE seguir as regras de Conventional Commits para determinar o tipo de bump: `feat:` = minor, `fix:` = patch, `feat!:` ou `BREAKING CHANGE:` = major.
- **FR-007**: O sistema DEVE ignorar commits sem tipo convencional relevante (chore, docs, test, ci, refactor) no cálculo de versão.
- **FR-008**: O sistema DEVE atualizar automaticamente a versão em `pyproject.toml` e `__init__.py` ao mergear na main.
- **FR-009**: O sistema DEVE criar um commit de release com mensagem "chore(release): vX.Y.Z" e uma tag Git `vX.Y.Z` na main.
- **FR-010**: O sistema DEVE disparar o workflow de publicação existente (publish.yml) via `workflow_dispatch` usando `gh workflow run` com a ref da tag e `confirm=yes`, contornando a limitação do GITHUB_TOKEN que não dispara novos workflows via push de tag.
- **FR-011**: O sistema DEVE manter compatibilidade com tags manuais — o publish.yml deve continuar funcionando para tags criadas manualmente.
- **FR-012**: O sistema DEVE direcionar tags com sufixo pre-release (-rc, -beta, -alpha) para TestPyPI e tags de release estável para PyPI.
- **FR-013**: O sistema DEVE utilizar apenas GITHUB_TOKEN para autenticação nos workflows, sem necessidade de Personal Access Tokens.
- **FR-014**: O sistema DEVE garantir que a versão publicada seja sempre superior a 0.1.0 (já publicada no PyPI e não pode ser sobrescrita).
- **FR-015**: O sistema DEVE executar o quality check completo (incluindo análise estática) ao mergear na main, antes de criar a release.
- **FR-016**: O sistema DEVE modificar o ci.yml existente removendo triggers de push em `develop` e `main` (mantendo `pull_request` e `workflow_call` intactos), já que esses fluxos serão orquestrados pelos novos workflows.
- **FR-017**: O sistema DEVE habilitar auto-merge na PR de feature→develop quando o CI passa com sucesso, sem necessidade de revisão humana.
- **FR-018**: A PR de develop→main (release) DEVE requerer revisão e aprovação manual antes do merge.
- **FR-019**: O sistema DEVE criar automaticamente uma PR de main→develop (backmerge) após cada release na main, para manter develop sincronizada.
- **FR-020**: Tags pre-release (`-rc`, `-beta`, `-alpha`) são criadas manualmente via `git tag`; o sistema apenas reage ao push direcionando para TestPyPI.
- **FR-021**: A branch `develop` DEVE ser criada a partir de `main` como parte do plano de implementação desta feature.
- **FR-022**: Os novos workflows DEVEM utilizar `concurrency` groups com `cancel-in-progress: true` para evitar runs simultâneos na mesma branch, eliminando race conditions na criação de PRs automáticas.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O fluxo completo feature→develop→main→tag→publicação funciona sem intervenção manual em 100% dos casos de caminho feliz.
- **SC-002**: PRs automáticas são criadas em até 5 minutos após o evento trigger (push ou merge).
- **SC-003**: A versão publicada no PyPI corresponde exatamente à versão calculada pelos Conventional Commits em 100% dos casos.
- **SC-004**: Zero PRs duplicadas são criadas quando múltiplos pushes ocorrem na mesma feature branch.
- **SC-005**: A transição para versionamento automático não causa interrupção nos workflows existentes — tags manuais continuam funcionando.
- **SC-006**: O tempo total do fluxo automatizado (do merge na main até pacote disponível no PyPI) não excede 15 minutos.
- **SC-007**: Todos os tipos de bump (patch, minor, major) são calculados corretamente conforme os padrões de Conventional Commits.
- **SC-008**: Commits que não seguem Conventional Commits não geram bumps de versão indesejados.

## Assumptions

- O GITHUB_TOKEN padrão do GitHub Actions possui permissões suficientes para criar commits, tags e PRs quando configurado com as permissions adequadas no workflow.
- O python-semantic-release é compatível com a estrutura de projeto atual (Poetry + pyproject.toml).
- O formato de tag `vX.Y.Z` é consistente entre o semantic-release e o trigger do publish.yml.
- A branch develop está sempre à frente ou sincronizada com main (nunca divergente de forma incompatível), garantida pelo backmerge automático main→develop após cada release.
- Os desenvolvedores seguirão o padrão de Conventional Commits nas mensagens de commit.
- O SonarCloud quality gate existente na main continuará sendo executado como parte do fluxo de merge.

## Constraints

- Escopo puramente CI/CD — nenhuma alteração em lógica de negócio ou código de produção.
- Sem alterações no schema do banco SQLite.
- Compatibilidade com Python 3.13+.
- Uso exclusivo de GITHUB_TOKEN — sem Personal Access Tokens.
- O publish.yml existente não deve ser modificado.
- Workflows existentes não devem quebrar durante a transição.
