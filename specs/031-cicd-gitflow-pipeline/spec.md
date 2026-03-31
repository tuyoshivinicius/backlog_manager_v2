# Feature Specification: CI/CD Pipeline com GitFlow, Quality Gates e PyPI Publish

**Feature Branch**: `031-cicd-gitflow-pipeline`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Implementar pipeline completo de CI/CD baseado em GitFlow com GitHub Actions, integracao com servicos de qualidade de codigo (Codecov e SonarCloud), publicacao automatizada no PyPI, e badges no README.md do projeto."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - CI automatizado em cada push/PR (Priority: P1)

Como desenvolvedor do projeto, quero que a cada push ou pull request o codigo seja automaticamente verificado (lint, testes, cobertura) para que eu tenha feedback rapido sobre a qualidade do codigo e nao precise rodar tudo manualmente.

**Why this priority**: Este e o alicerce de toda a pipeline. Sem CI funcionando, nenhuma das outras funcionalidades (quality gates, publish, badges) tem valor. Garante que o codigo na branch de integracao esta sempre saudavel.

**Independent Test**: Pode ser testado criando um PR de teste para `develop` e verificando que os jobs lint, test (Python 3.11/3.12/3.13) e quality executam corretamente no GitHub Actions.

**Acceptance Scenarios**:

1. **Given** um desenvolvedor cria um PR para `develop`, **When** o PR e aberto, **Then** os jobs de lint (ruff check, ruff format, mypy), test (unit, integration, e2e com cobertura >= 80%) e quality (Codecov upload, SonarCloud scan) executam automaticamente.
2. **Given** o job de lint falha (ex: ruff encontra violacao), **When** o desenvolvedor corrige e faz push, **Then** o CI re-executa e os status checks atualizam no PR.
3. **Given** testes rodam em matriz Python 3.11/3.12/3.13, **When** qualquer versao falha, **Then** o PR e bloqueado ate a correcao.
4. **Given** um push e feito para `develop`, `main`, `release/*` ou `hotfix/*`, **When** o push e recebido, **Then** o CI executa automaticamente.

---

### User Story 2 - Estrutura GitFlow e documentacao de branching (Priority: P2)

Como mantenedor do projeto, quero uma estrategia de branching clara baseada em GitFlow (main, develop, feature/*, release/*, hotfix/*) documentada para que todos os contribuidores sigam o mesmo fluxo de trabalho.

**Why this priority**: Define o modelo de colaboracao do projeto. Sem uma estrategia de branching, os triggers de CI/CD nao fazem sentido e o publish automatizado nao tem um fluxo de release definido.

**Independent Test**: Pode ser validado verificando que o arquivo CONTRIBUTING.md existe com instrucoes de branching e que o SETUP_CI.md contem recomendacoes de branch protection.

**Acceptance Scenarios**:

1. **Given** um novo contribuidor acessa o repositorio, **When** ele le o CONTRIBUTING.md, **Then** encontra documentacao clara do fluxo GitFlow com diagrama textual, exemplos de como criar branches, abrir PRs e fazer merge.
2. **Given** o mantenedor configura o repositorio, **When** ele segue o SETUP_CI.md, **Then** consegue configurar branch protection rules para main e develop (require PR reviews, require status checks, no direct push).
3. **Given** a migracao do branch padrao atual (`001-ep001-foundation-persistence`), **When** o CONTRIBUTING.md e consultado, **Then** contem notas sobre a migracao para main/develop e cleanup de branches historicas.
4. **Given** um desenvolvedor precisa fazer bump de versao, **When** ele consulta o CONTRIBUTING.md, **Then** encontra o processo documentado de bump de versao antes de criar tag de release.

---

### User Story 3 - Quality gates com Codecov e SonarCloud (Priority: P3)

Como mantenedor do projeto, quero integracao com Codecov (cobertura de testes) e SonarCloud (qualidade de codigo) para ter visibilidade continua sobre a saude do codigo e receber feedback automatico em PRs.

**Why this priority**: Complementa o CI com metricas de qualidade externas. Depende do CI estar funcionando (P1) mas agrega valor significativo ao fluxo de PR com comentarios automaticos e dashboards.

**Independent Test**: Pode ser testado abrindo um PR e verificando que o Codecov posta comentario de cobertura e que o SonarCloud executa analise sem erros.

**Acceptance Scenarios**:

1. **Given** o CI completa com sucesso e gera `coverage.xml`, **When** o job quality executa, **Then** o Codecov recebe o report e posta comentario no PR com delta de cobertura.
2. **Given** cobertura do projeto cai abaixo de 80%, **When** o Codecov avalia, **Then** o status check do Codecov falha no PR.
3. **Given** cobertura do patch (codigo novo) esta abaixo de 80%, **When** o Codecov avalia, **Then** o status check indica cobertura insuficiente no codigo adicionado.
4. **Given** o job quality executa o SonarCloud scan, **When** a analise completa, **Then** o SonarCloud Quality Gate aparece como status check no PR.
5. **Given** o Codecov esta temporariamente indisponivel, **When** o upload falha, **Then** o CI nao e bloqueado (fail_ci_if_error: false).

---

### User Story 4 - Publicacao automatizada no PyPI via tags (Priority: P4)

Como mantenedor do projeto, quero que ao criar uma tag semantica (vX.Y.Z) o pacote seja automaticamente publicado no PyPI, com validacao completa do CI antes da publicacao, para eliminar o processo manual de build e upload.

**Why this priority**: E o objetivo final da pipeline de release. Depende do CI (P1) e do GitFlow (P2) para ter um fluxo de release confiavel, mas e o passo que entrega valor ao usuario final (pacote disponivel no PyPI).

**Independent Test**: Pode ser testado criando uma tag `v0.1.1-rc1` e verificando que o workflow de publish executa, valida o CI, faz build e publica no TestPyPI.

**Acceptance Scenarios**:

1. **Given** uma tag `v1.0.0-rc1` e criada, **When** o workflow de publish e disparado, **Then** o CI completo e executado primeiro (lint + test + quality) e, se passar, o pacote e publicado no TestPyPI.
2. **Given** uma tag `v1.0.0` (sem sufixo) e criada, **When** o workflow de publish e disparado, **Then** o CI e validado, o pacote e publicado no PyPI oficial, e uma GitHub Release e criada automaticamente com changelog e artefatos (.whl, .tar.gz).
3. **Given** o CI falha durante a validacao da tag, **When** algum job (lint/test/quality) falha, **Then** a publicacao nao ocorre e o mantenedor e notificado.
4. **Given** uma emergencia requer publicacao imediata, **When** o mantenedor dispara o workflow manualmente via workflow_dispatch com confirmacao, **Then** a publicacao e executada apos validacao do CI.
5. **Given** a versao no `pyproject.toml` e `__init__.py` esta sincronizada, **When** o build e executado, **Then** o pacote publicado reflete a versao correta.

---

### User Story 5 - Badges de status no README (Priority: P5)

Como visitante ou potencial usuario do projeto, quero ver badges no README mostrando o status do CI, cobertura, qualidade do codigo, versao no PyPI e licenca, para avaliar rapidamente a saude e maturidade do projeto.

**Why this priority**: E a camada de apresentacao. Depende de todas as integracoes estarem configuradas (CI, Codecov, SonarCloud, PyPI) para que os badges reflitam informacoes reais.

**Independent Test**: Pode ser validado verificando que o README.md contem badges com links corretos para cada servico e que os badges renderizam corretamente no GitHub.

**Acceptance Scenarios**:

1. **Given** o README.md e visualizado no GitHub, **When** o usuario observa a area abaixo do titulo, **Then** ve badges de CI Status, Codecov, SonarCloud (Quality Gate, Maintainability, Reliability, Security), PyPI (versao, downloads), Python Version e License.
2. **Given** um badge e clicado, **When** o usuario interage, **Then** e redirecionado para o servico correspondente (GitHub Actions, Codecov, SonarCloud, PyPI, etc.).
3. **Given** o CI esta falhando, **When** o README e visualizado, **Then** o badge de CI mostra status "failing" em vermelho.

---

### User Story 6 - Preparacao do pyproject.toml para PyPI (Priority: P6)

Como mantenedor do projeto, quero que o pyproject.toml tenha metadata completa (description, classifiers, URLs, license) para que o pacote publicado no PyPI tenha uma pagina profissional e informativa.

**Why this priority**: Pre-requisito para publicacao no PyPI (P4) mas e uma tarefa pontual de configuracao sem complexidade de fluxo.

**Independent Test**: Pode ser validado executando `poetry check` e verificando que nao ha warnings sobre metadata faltante.

**Acceptance Scenarios**:

1. **Given** o pyproject.toml e verificado, **When** a secao [tool.poetry] e inspecionada, **Then** contem description, readme, license (MIT), authors, classifiers, repository e homepage.
2. **Given** os classificadores estao definidos, **When** o pacote e publicado no PyPI, **Then** aparece corretamente categorizado como Alpha, Qt for Python, Python 3.11/3.12/3.13, MIT License.
3. **Given** dist/, build/ e *.egg-info/ estao no .gitignore, **When** um build local e executado, **Then** artefatos nao sao versionados acidentalmente.

---

### Edge Cases

- O que acontece quando o Codecov ou SonarCloud estao fora do ar durante o CI? O pipeline nao deve ser bloqueado (fail_ci_if_error: false para Codecov; SonarCloud e um status check opcional/informacional e nao bloqueia merge).
- O que acontece quando uma tag e criada sem bump de versao no pyproject.toml? O pacote sera publicado com a versao antiga — documentar no CONTRIBUTING.md que bump de versao deve preceder a tag.
- O que acontece quando o publish no TestPyPI falha para uma tag rc? O publish no PyPI oficial nao deve prosseguir; o mantenedor corrige e cria nova tag.
- O que acontece se a versao no `__init__.py` diverge do `pyproject.toml`? O CI falha com erro explicito de version mismatch (FR-029). O CONTRIBUTING.md documenta a necessidade de manter ambos sincronizados.
- O que acontece com branches historicas (`001-*`, `0*`, `master`) apos migracao para GitFlow? Documentar plano de cleanup no CONTRIBUTING.md sem deletar automaticamente.
- O que acontece quando um hotfix precisa ser publicado e o develop esta a frente de main? O fluxo GitFlow preve merge do hotfix tanto em main quanto em develop, resolvendo conflitos se necessario.

## Requirements *(mandatory)*

### Functional Requirements

**GitFlow e Documentacao**:

- **FR-001**: O projeto DEVE ter um arquivo CONTRIBUTING.md documentando a estrategia de branching GitFlow (main, develop, feature/*, release/*, hotfix/*) com diagrama textual do fluxo e exemplos de uso.
- **FR-002**: O projeto DEVE ter um arquivo SETUP_CI.md com instrucoes de configuracao de branch protection rules e GitHub Secrets necessarios.
- **FR-003**: O CONTRIBUTING.md DEVE documentar o processo de versionamento semantico e bump de versao antes de criar tags de release.
- **FR-004**: O CONTRIBUTING.md DEVE incluir notas sobre a migracao do branch padrao atual e cleanup de branches historicas.

**CI Workflow**:

- **FR-005**: O sistema DEVE ter um workflow de CI (`.github/workflows/ci.yml`) que substitua o workflow existente (`tests.yml`).
- **FR-006**: O CI DEVE ser disparado em push para `develop`, `main`, `release/*`, `hotfix/*` e em PRs para `develop` e `main`.
- **FR-007**: O CI DEVE executar um job de lint com ruff check, ruff format --check e mypy.
- **FR-008**: O CI DEVE executar um job de test dependente do lint, com matriz Python 3.11/3.12/3.13, incluindo testes unit, integration e e2e (com xvfb para GUI headless).
- **FR-009**: O CI DEVE gerar relatorio de cobertura (`coverage.xml`) com threshold minimo de 80% e fazer upload como artefato.
- **FR-010**: O CI DEVE executar um job de quality dependente do test, com upload para Codecov e scan do SonarCloud.
- **FR-011**: O CI DEVE suportar `workflow_call` para reutilizacao pelo workflow de publish.
- **FR-012**: O CI DEVE usar cache de dependencias Poetry para otimizar tempo de execucao.
- **FR-029**: O CI DEVE incluir um step de validacao que falha se a versao em `pyproject.toml` divergir da versao em `src/backlog_manager/__init__.py`.

**Codecov**:

- **FR-013**: O projeto DEVE ter um arquivo `codecov.yml` com targets de cobertura de 80% para projeto e patch, exclusoes de arquivos de teste/config e comentarios automaticos em PRs.
- **FR-014**: O upload para Codecov DEVE usar token via secret `CODECOV_TOKEN` e nao bloquear o CI se indisponivel.

**SonarCloud**:

- **FR-015**: O projeto DEVE ter um arquivo `sonar-project.properties` configurado com organization, projectKey, sources, tests, cobertura e exclusoes.
- **FR-016**: O scan do SonarCloud DEVE usar token via secret `SONAR_TOKEN`.
- **FR-028**: O SonarCloud Quality Gate DEVE ser configurado como status check opcional (informacional) nos PRs — nao bloqueia merge. O SETUP_CI.md DEVE documentar esta decisao e como alterar para required se desejado.

**Publish/Release**:

- **FR-017**: O sistema DEVE ter um workflow de publish (`.github/workflows/publish.yml`) disparado por tags `v*` e workflow_dispatch manual.
- **FR-018**: O workflow de publish DEVE reutilizar o CI via workflow_call antes de prosseguir com build e publicacao.
- **FR-019**: Tags com sufixo rc/beta/alpha DEVEM publicar apenas no TestPyPI; tags de release final DEVEM publicar no PyPI oficial.
- **FR-020**: O workflow DEVE criar uma GitHub Release automaticamente com release notes auto-geradas pelo GitHub (baseadas em PR titles/labels, configuradas via `.github/release.yml`) e artefatos de build anexados, para tags de release final.
- **FR-021**: O workflow_dispatch DEVE exigir input de confirmacao para publicacoes de emergencia.
- **FR-027**: A publicacao no PyPI e TestPyPI DEVE usar OIDC Trusted Publishers (sem tokens de longa duracao), configurado via `id-token: write` permission no workflow e Trusted Publisher settings nos projetos PyPI/TestPyPI.

**PyPI Metadata**:

- **FR-022**: O `pyproject.toml` DEVE conter metadata completa: description, readme, license (MIT), authors, classifiers, repository, homepage e URLs do projeto.
- **FR-023**: Os diretorios `dist/`, `build/` e `*.egg-info/` DEVEM estar no `.gitignore`.
- **FR-024**: A versao em `pyproject.toml` e `src/backlog_manager/__init__.py` DEVE ser mantida sincronizada (documentado no CONTRIBUTING.md).

**Badges**:

- **FR-025**: O README.md DEVE conter badges de CI Status, Codecov, SonarCloud (Quality Gate, Maintainability, Reliability, Security), PyPI (versao, downloads), Python Version e License logo abaixo do titulo.
- **FR-026**: Cada badge DEVE ser um link clicavel para o servico correspondente.

### Key Entities

- **Workflow CI (`ci.yml`)**: Pipeline de integracao continua com jobs lint, test e quality. Reutilizavel via workflow_call.
- **Workflow Publish (`publish.yml`)**: Pipeline de release com jobs validate, build, publish-testpypi, publish-pypi e github-release. Disparado por tags e workflow_dispatch.
- **CONTRIBUTING.md**: Documento de referencia para contribuidores com estrategia GitFlow, versionamento e processo de release.
- **SETUP_CI.md**: Guia de configuracao unica para mantenedores (secrets para Codecov/SonarCloud, OIDC Trusted Publishers para PyPI/TestPyPI, branch protection, servicos externos).
- **codecov.yml**: Configuracao do Codecov (targets, exclusoes, comentarios em PRs).
- **sonar-project.properties**: Configuracao do SonarCloud (sources, tests, cobertura, exclusoes).
- **`.github/release.yml`**: Configuracao de categorias para auto-generated release notes do GitHub (labels → secoes do changelog).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Todo push para branches protegidas (develop, main) e todo PR dispara automaticamente os checks de lint, test e quality sem intervencao manual.
- **SC-002**: Testes executam com sucesso nas 3 versoes Python suportadas (3.11, 3.12, 3.13) com cobertura >= 80%.
- **SC-003**: PRs recebem automaticamente comentarios de cobertura do Codecov e status check do SonarCloud Quality Gate.
- **SC-004**: Criacao de uma tag semantica `v*` dispara publicacao automatizada no PyPI em menos de 15 minutos (incluindo validacao CI).
- **SC-005**: A pagina do pacote no PyPI exibe metadata completa (descricao, classificadores, URLs, licenca).
- **SC-006**: O README no GitHub exibe badges funcionais e atualizados que refletem o estado real do CI, cobertura e qualidade.
- **SC-007**: Um novo contribuidor consegue entender o fluxo de trabalho (branching, PR, release) lendo apenas o CONTRIBUTING.md.
- **SC-008**: O mantenedor consegue configurar todos os servicos externos (secrets, branch protection) seguindo o SETUP_CI.md em uma unica sessao.

## Assumptions

- O repositorio e publico no GitHub, permitindo uso gratuito do GitHub Actions, Codecov e SonarCloud.
- Os tokens de Codecov e SonarCloud serao configurados manualmente como GitHub Secrets pelo mantenedor seguindo o SETUP_CI.md. A publicacao no PyPI/TestPyPI usa OIDC Trusted Publishers (sem necessidade de tokens PyPI como secrets).
- A migracao de branches (consolidar `001-ep001-foundation-persistence` para `main`, criar `develop`) sera feita manualmente pelo mantenedor. A spec documenta o processo mas nao o automatiza.
- O projeto ja possui pre-commit configurado; nao sera alterado como parte desta feature.
- O pacote PyPI `zion-backlog-manager` ja existe (versao 0.1.0 publicada manualmente); a publicacao automatizada continuara usando o mesmo nome.
- O SonarCloud project sera criado manualmente no dashboard do SonarCloud antes de rodar o CI pela primeira vez.

## Clarifications

### Session 2026-03-31

- Q: PyPI authentication method — API token via secret ou OIDC Trusted Publishers? → A: OIDC Trusted Publishers (sem tokens de longa duracao, configurado no PyPI project settings e via `id-token: write` no workflow).
- Q: Metodo de geracao de changelog para GitHub Releases? → A: GitHub auto-generated release notes (baseadas em PR titles/labels, configuradas via `.github/release.yml`).
- Q: SonarCloud Quality Gate deve ser required ou optional status check nos PRs? → A: Optional (informacional) — reporta no PR mas nao bloqueia merge.
- Q: CI deve validar sincronizacao de versao entre `__init__.py` e `pyproject.toml`? → A: Sim — step no CI que falha se as versoes divergirem.

## Scope & Boundaries

### In Scope

- Criacao dos workflows ci.yml e publish.yml
- Remocao do workflow tests.yml (substituido por ci.yml)
- Criacao dos arquivos codecov.yml, sonar-project.properties, CONTRIBUTING.md, SETUP_CI.md e `.github/release.yml`
- Complementar metadata do pyproject.toml
- Verificar/atualizar .gitignore para dist/, build/, *.egg-info/
- Adicionar badges ao README.md

### Out of Scope

- Execucao da migracao de branches (apenas documentacao)
- Configuracao real de GitHub Secrets (apenas documentacao no SETUP_CI.md)
- Configuracao real de branch protection rules (apenas documentacao)
- Criacao de conta/projeto no SonarCloud (apenas documentacao)
- Alteracoes no pre-commit ou em hooks existentes
- Alteracoes no codigo da aplicacao (src/backlog_manager/)
- Criacao de testes automatizados para os workflows
- Alteracoes no schema do banco de dados
