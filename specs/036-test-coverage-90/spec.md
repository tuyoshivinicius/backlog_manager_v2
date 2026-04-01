# Feature Specification: Cobertura de Testes 90% e Quality Gate SonarQube

**Feature Branch**: `036-test-coverage-90`
**Created**: 2026-04-01
**Status**: Draft
**Input**: User description: "Alinhar configuracao de cobertura do SonarQube com pytest-cov e aumentar cobertura de testes para atingir 90% no codigo total, corrigindo o Quality Gate que atualmente falha."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Alinhamento de Exclusoes de Cobertura (Priority: P1)

Como desenvolvedor do projeto, quero que as exclusoes de cobertura configuradas no SonarQube reflitam exatamente as mesmas exclusoes do pytest-cov local, para que as metricas de cobertura sejam consistentes entre o ambiente local e o CI/CD, eliminando falsos negativos no Quality Gate.

**Why this priority**: Esta e a acao de maior impacto com menor esforco. A divergencia entre metricas locais (~94%) e SonarQube (56.7%) e causada exclusivamente pela falta de exclusoes no SonarQube. Corrigir isso sozinho ja deve elevar a cobertura reportada para ~94%, resolvendo o Quality Gate imediatamente.

**Independent Test**: Pode ser testado executando a analise SonarQube apos a configuracao e verificando que a cobertura reportada subiu de 56.7% para ~94%, alinhada com o pytest-cov local.

**Acceptance Scenarios**:

1. **Given** o arquivo de configuracao do SonarQube com exclusoes incompletas, **When** as exclusoes sao atualizadas para incluir views, delegates, app.py, __init__.py, __main__.py, interfaces e constants.py, **Then** a cobertura total reportada pelo SonarQube sobe de 56.7% para >= 90%.
2. **Given** as exclusoes alinhadas entre SonarQube e pytest-cov, **When** a analise e executada em ambos os ambientes, **Then** a diferenca entre as coberturas reportadas e inferior a 5 pontos percentuais.
3. **Given** as exclusoes configuradas, **When** novos arquivos de view ou delegate sao adicionados ao projeto, **Then** eles sao automaticamente excluidos da contagem de cobertura em ambos os ambientes.

---

### User Story 2 - Testes para Codigo Parcialmente Coberto (Priority: P2)

Como desenvolvedor do projeto, quero adicionar testes unitarios e de integracao para os arquivos que estao abaixo de 90% de cobertura, para solidificar a meta de cobertura e garantir que o codigo de producao esta adequadamente validado.

**Why this priority**: Apos o alinhamento de exclusoes (P1), a cobertura ja estara proxima de 94%. Porem, existem ~139 linhas de codigo testavel parcialmente coberto que representam riscos de regressao. Cobrir essas lacunas fortalece a confiabilidade do projeto e previne que futuras alteracoes facam a cobertura cair abaixo de 90%.

**Independent Test**: Pode ser testado executando pytest-cov e verificando que cada arquivo listado atingiu >= 90% de cobertura individual.

**Acceptance Scenarios**:

1. **Given** o arquivo edit_story.py com 44.4% de cobertura, **When** testes adicionais sao escritos cobrindo os caminhos nao testados, **Then** a cobertura do arquivo atinge >= 90%.
2. **Given** o arquivo list_stories.py com 69.4% de cobertura, **When** testes adicionais sao escritos, **Then** a cobertura do arquivo atinge >= 90%.
3. **Given** todos os 16 arquivos prioritarios identificados, **When** testes sao adicionados para cada um, **Then** nenhum arquivo testavel do projeto tem cobertura abaixo de 90%.
4. **Given** os novos testes escritos, **When** executados em modo headless (sem display), **Then** todos passam sem erros.

---

### User Story 3 - Garantia de Cobertura em Novo Codigo (Priority: P3)

Como desenvolvedor do projeto, quero garantir que todo codigo novo adicionado nesta feature tenha cobertura minima de 80% (threshold do Quality Gate) e preferencialmente >= 90%, para que o Quality Gate passe e a meta de cobertura seja mantida.

**Why this priority**: E uma consequencia natural das duas primeiras frentes. Todo codigo de teste e configuracao adicionado deve seguir os mesmos padroes de qualidade, garantindo que a propria feature nao degrade as metricas.

**Independent Test**: Pode ser testado verificando no SonarQube que a metrica new_coverage (cobertura de novo codigo) atinge >= 80%.

**Acceptance Scenarios**:

1. **Given** novos arquivos de teste adicionados, **When** a analise SonarQube e executada, **Then** a cobertura de novo codigo (new_coverage) e >= 80%.
2. **Given** o Quality Gate configurado com threshold de 80% para novo codigo, **When** o pipeline de CI executa, **Then** o Quality Gate reporta status OK (passa).

---

### Edge Cases

- O que acontece se um arquivo excluido de cobertura contiver logica de negocio significativa que deveria ser testada? Revisao manual das exclusoes deve confirmar que apenas codigo nao-testavel unitariamente esta excluido.
- O que acontece se os padroes de exclusao do SonarQube nao suportarem a mesma sintaxe do pytest-cov? Os padroes devem ser adaptados ao formato glob do SonarQube mantendo equivalencia semantica.
- O que acontece se testes adicionais quebrarem testes existentes? Todos os testes existentes devem continuar passando (zero regressao).
- O que acontece se um arquivo com cobertura baixa nao puder atingir 90% sem modificar codigo de producao? Documentar a limitacao e atingir a maior cobertura possivel sem alteracoes invasivas ao codigo de producao.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: As exclusoes de cobertura do SonarQube DEVEM incluir todos os mesmos padroes configurados no pytest-cov: views PySide6, delegates, app.py, __init__.py, __main__.py, interfaces abstratas e constants.py.
- **FR-002**: A configuracao de exclusoes DEVE usar padroes glob compativeis com o SonarQube que sejam semanticamente equivalentes aos padroes do pytest-cov.
- **FR-003**: Testes adicionais DEVEM ser escritos para todos os 16 arquivos prioritarios identificados com cobertura abaixo de 90%.
- **FR-004**: Todos os novos testes DEVEM seguir os padroes existentes do projeto: markers pytest, fixtures, factories e mocks headless para viewmodels.
- **FR-005**: Todos os testes DEVEM executar em modo headless, sem necessidade de display ou servidor X.
- **FR-006**: O schema do banco SQLite NAO DEVE ser alterado.
- **FR-007**: Codigo de producao NAO DEVE ser modificado apenas para facilitar testes, exceto ajustes minimos de testabilidade quando estritamente necessario.
- **FR-008**: A compatibilidade com Python 3.11+ DEVE ser mantida.
- **FR-009**: Zero regressao nos indicadores de qualidade existentes: 0 bugs, 0 vulnerabilidades, 0 code smells, 0% duplicacao.
- **FR-010**: Todo novo codigo adicionado DEVE ter cobertura minima de 80% (threshold do Quality Gate).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Quality Gate do SonarQube passa com status OK apos a entrega da feature.
- **SC-002**: Cobertura total reportada pelo SonarQube atinge >= 90%.
- **SC-003**: Cobertura de novo codigo (new_coverage) no SonarQube atinge >= 80%.
- **SC-004**: Cobertura local (pytest-cov) mantem-se >= 90%.
- **SC-005**: Diferenca entre cobertura local e SonarQube e inferior a 5 pontos percentuais.
- **SC-006**: Todos os 16 arquivos prioritarios atingem >= 90% de cobertura individual.
- **SC-007**: Zero regressao em testes existentes — 100% dos testes pre-existentes continuam passando.
- **SC-008**: Zero aumento em bugs, vulnerabilidades, code smells ou duplicacao reportados pelo SonarQube.

## Assumptions

- Os padroes glob do SonarQube (`**/pasta/**`) sao suficientes para replicar as exclusoes do pytest-cov (`*/pasta/*.py`).
- A cobertura do SonarQube subira para ~94% apos alinhamento de exclusoes, com base no calculo: das 7,289 linhas atuais, ~3,264 serao excluidas (views, delegates, app.py, __init__.py, interfaces, constants.py), restando ~4,025 linhas testaveis, das quais ~3,886 ja estao cobertas.
- Os arquivos prioritarios podem atingir >= 90% de cobertura sem alteracoes significativas no codigo de producao.
- O ambiente de CI suporta execucao de testes em modo headless.
- Os testes para viewmodels podem usar mocks headless conforme padroes ja estabelecidos no projeto.

## Constraints

- Nenhuma alteracao no schema do banco SQLite.
- Views PySide6 e delegates continuam excluidos de cobertura (testados via QA manual).
- Codigo de producao nao deve ser modificado apenas para facilitar testes.
- Compatibilidade com Python 3.11+ obrigatoria.
- Testes devem rodar em modo headless (sem display/servidor X).
