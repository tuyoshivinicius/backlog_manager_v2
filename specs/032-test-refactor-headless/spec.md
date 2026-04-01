# Feature Specification: Refatoracao da Suite de Testes para Cobertura 90% Headless

**Feature Branch**: `032-test-refactor-headless`
**Created**: 2026-03-31
**Status**: Draft
**Input**: User description: "Refatoracao da Suite de Testes para Cobertura 90% Headless"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Correcao da Medicao de Cobertura (Priority: P1)

O desenvolvedor precisa visualizar a cobertura real do projeto em todas as camadas arquiteturais (domain, application, infrastructure, presentation). Atualmente a configuracao de cobertura mede apenas a camada presentation, deixando 80 dos 119 arquivos fonte sem medicao. Corrigir isso e pre-requisito para todas as demais atividades, pois sem dados reais nao ha como priorizar esforco.

**Why this priority**: Sem cobertura real, o desenvolvedor toma decisoes cegas sobre onde investir em testes. E o alicerce de toda a epic.

**Independent Test**: Executar o relatorio de cobertura e verificar que todas as 4 camadas aparecem no relatorio com percentuais por arquivo.

**Acceptance Scenarios**:

1. **Given** a configuracao de cobertura atual mede apenas presentation, **When** o desenvolvedor executa o relatorio de cobertura com a nova configuracao, **Then** o relatorio inclui as 4 camadas (domain, application, infrastructure, presentation) com percentuais individuais por arquivo
2. **Given** o relatorio corrigido esta disponivel, **When** o desenvolvedor consulta os resultados, **Then** pode visualizar uma lista de arquivos ordenada por cobertura, identificando os que estao abaixo de 90%
3. **Given** o relatorio corrigido esta disponivel, **When** comparado com a medicao anterior, **Then** o total de arquivos medidos passa de 39 para 119

---

### User Story 2 - Remocao de Testes E2E Graficos (Priority: P1)

O desenvolvedor remove os 22 arquivos de teste E2E que dependem de bibliotecas graficas (PySide6, pytest-qt, qasync). Esses testes nao executam em CI headless e seu valor sera substituido por testes de integracao headless. Factories de dados reutilizaveis sao preservadas e movidas para local compartilhado.

**Why this priority**: Enquanto esses testes existem, o CI ignora 55 arquivos de teste e a suite nao e confiavel. Remover e pre-requisito para ter um CI limpo.

**Independent Test**: Executar `pytest` completo e confirmar que nenhum teste E2E e coletado e nenhum import de modulos graficos existe nos testes restantes.

**Acceptance Scenarios**:

1. **Given** 22 arquivos de teste E2E existem no diretorio `tests/e2e/`, **When** o desenvolvedor executa a remocao, **Then** todos os 22 arquivos sao removidos do repositorio
2. **Given** o arquivo `tests/e2e/factories.py` contem factories de dados reutilizaveis sem dependencia GUI, **When** o desenvolvedor executa a remocao, **Then** as factories sao migradas para `tests/factories.py` e permanecem acessiveis a todos os niveis de teste
3. **Given** os testes E2E foram removidos, **When** o desenvolvedor executa `pytest` sem flags `--ignore`, **Then** nenhum erro de importacao de modulos graficos ocorre nos testes restantes

---

### User Story 3 - Triagem e Tratamento de Testes de Integracao Presentation (Priority: P1)

O desenvolvedor analisa os 16 testes de integracao da camada presentation que dependem de widgets Qt. Para cada teste, decide entre: remover se a logica ja esta coberta por outros testes headless, ou reescrever como headless se testa logica de negocio critica nao coberta em outro lugar. O objetivo e eliminar dependencia grafica sem perder cobertura de logica de negocio.

**Why this priority**: Esses testes representam a maior parte dos testes ignorados no CI. Trata-los desbloqueia a execucao completa da suite.

**Independent Test**: Executar `pytest tests/integration/` completo sem display grafico e confirmar que todos os testes passam e nenhum importa modulos graficos diretamente.

**Acceptance Scenarios**:

1. **Given** 16 testes de integracao presentation dependem de Qt, **When** o desenvolvedor analisa cada teste, **Then** cada teste e classificado como "remover" (logica ja coberta ou puramente visual) ou "reescrever headless" (logica de negocio unica)
2. **Given** um teste e classificado como "reescrever headless", **When** o desenvolvedor reescreve o teste, **Then** o novo teste cobre os mesmos cenarios de negocio sem depender de QApplication, display grafico ou pytest-qt
3. **Given** um teste e classificado como "remover", **When** o desenvolvedor remove o teste, **Then** a logica de negocio que ele testava ja esta verificavelmente coberta por outros testes headless existentes
4. **Given** todos os 16 testes foram triados, **When** o desenvolvedor executa `pytest tests/integration/` em ambiente headless, **Then** todos os testes passam sem erros

---

### User Story 4 - Triagem e Tratamento de Testes Unitarios Presentation (Priority: P2)

O desenvolvedor analisa os 17 testes unitarios da camada presentation que dependem de Qt. Mesma logica de triagem: remover testes duplicados ou puramente visuais, reescrever como headless apenas os que testam logica de negocio unica nao coberta em outro lugar.

**Why this priority**: Menor urgencia que integracao pois muitos testes unitarios de ViewModel ja testam logica sem GUI. Porem necessario para cobertura completa.

**Independent Test**: Executar `pytest tests/unit/presentation/` completo sem display grafico e confirmar que todos os testes passam.

**Acceptance Scenarios**:

1. **Given** 17 testes unitarios presentation dependem de Qt, **When** o desenvolvedor analisa cada teste, **Then** cada teste e classificado como "remover" ou "reescrever headless"
2. **Given** um teste de ViewModel e classificado como "reescrever headless", **When** o desenvolvedor reescreve, **Then** o novo teste valida logica de negocio e transformacao de dados usando mocks para dependencias Qt
3. **Given** um teste de delegate ou view puramente visual, **When** o desenvolvedor avalia, **Then** o teste e removido sem reescrita pois testa apenas renderizacao
4. **Given** todos os 17 testes foram triados, **When** o desenvolvedor executa `pytest tests/unit/presentation/` em ambiente headless, **Then** todos os testes passam sem erros

---

### User Story 5 - Ampliacao de Cobertura em Fluxos Criticos (Priority: P1)

Apos eliminar dependencias graficas, o desenvolvedor cria novos testes headless priorizando os fluxos e classes com menor cobertura e maior impacto no negocio. O foco e maximizar o retorno de cada teste escrito, comecando pelos ViewModels com logica de negocio critica e cobertura abaixo de 40%.

**Why this priority**: E a atividade que efetivamente eleva a cobertura para a meta de 90%. Sem ela, a remocao de testes graficos pode ate reduzir a cobertura global.

**Independent Test**: Executar relatorio de cobertura apos novos testes e verificar que a cobertura global atingiu >= 90%.

**Acceptance Scenarios**:

1. **Given** o relatorio de cobertura mostra arquivos criticos com cobertura < 40%, **When** o desenvolvedor cria testes headless para esses arquivos, **Then** a cobertura de cada arquivo critico atinge >= 70% individualmente, contribuindo para a meta global de >= 90%
2. **Given** os novos testes foram criados, **When** executados em ambiente headless, **Then** todos passam sem dependencia de display grafico
3. **Given** todos os novos testes estao implementados, **When** o relatorio de cobertura global e gerado, **Then** a cobertura global e >= 90%

---

### User Story 6 - Atualizacao do CI para Suite Completa (Priority: P1)

Apos a reescrita e ampliacao dos testes, o pipeline CI deve executar a suite completa sem necessidade de display grafico, removendo os filtros `--ignore` que excluem testes de presentation.

**Why this priority**: E a validacao final de que toda a epic atingiu seu objetivo — testes confiaveis executando no CI sem dependencia grafica.

**Independent Test**: Executar o pipeline CI completo e verificar que todos os testes passam e a cobertura e reportada como >= 90%.

**Acceptance Scenarios**:

1. **Given** o CI atual usa flags `--ignore=tests/unit/presentation` e `--ignore=tests/integration/presentation`, **When** o desenvolvedor remove esses flags, **Then** o pipeline executa todos os testes sem erros
2. **Given** o CI atual usa flag `-p no:pytest-qt`, **When** pytest-qt e removido das dependencias, **Then** o flag `-p no:pytest-qt` e removido do CI pois a dependencia nao existe mais
3. **Given** a suite completa executa no CI, **When** o pipeline finaliza, **Then** a cobertura global reportada e >= 90% e todos os testes passam
4. **Given** a suite completa executa no CI, **When** o pipeline finaliza, **Then** o tempo total de execucao dos testes e <= 5 minutos

---

### Edge Cases

- O que acontece se a cobertura real (todas as camadas) ja estiver acima de 90% apos corrigir a configuracao? Os cenarios de reescrita headless continuam necessarios para eliminar dependencia grafica, mas a ampliacao de cobertura (User Story 5) pode ser reduzida em escopo.
- O que acontece com ViewModels que herdam de classes Qt (QObject, QAbstractTableModel)? Testes DEVEM usar `unittest.mock.patch` para substituir classes base Qt por mocks puros — zero import de PySide6 nos testes headless.
- Como testar delegates que dependem de QPainter para renderizacao? Testar apenas a logica de formatacao e decisao (cores, texto, dimensoes), nao a renderizacao em si.
- O que acontece se um teste reescrito nao consegue cobrir o mesmo cenario sem Qt? Documentar como "cobertura visual-only" e excluir do escopo, contabilizando no calculo de cobertura.
- O que acontece se a remocao de testes E2E reduz a cobertura global? A ampliacao de cobertura (User Story 5) compensa, priorizando os mesmos fluxos que os E2E cobriam.

## Clarifications

### Session 2026-03-31

- Q: Contradicao entre `pragma: no cover` em arquivos visuais e FR-012 (zero alteracoes em src/) — como resolver? → A: Permitir excecao: `pragma: no cover` e permitido APENAS em arquivos puramente visuais listados explicitamente (app.py, about_dialog.py, rich_tooltip.py)
- Q: Estrategia de mock para ViewModels que herdam de classes Qt (QAbstractTableModel, QObject) — como testar headless? → A: Mock puro com unittest.mock.patch para substituir classes base Qt, zero import de PySide6 nos testes
- Q: Meta de 80% e por camada individual ou global agregada? → A: 90% global agregada, sem exigencia por camada individual
- Q: Onde ficam os testes reescritos de presentation (headless) na estrutura de diretorios? → A: Mesmo local original (tests/unit/presentation/ e tests/integration/presentation/) — o teste continua testando a camada presentation
- Q: Destino do pytest-qt e PySide6 como dependencias de teste apos remocao de todos os testes GUI? → A: Remover ambos das dependencias de teste (dev dependencies no pyproject.toml)

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A configuracao de cobertura DEVE medir todas as 4 camadas da arquitetura (domain, application, infrastructure, presentation), incluindo os 119 arquivos fonte
- **FR-002**: Todos os 22 arquivos de teste E2E com dependencia grafica DEVEM ser removidos do repositorio
- **FR-003**: As factories de dados de teste (`tests/e2e/factories.py`) DEVEM ser migradas para local compartilhado (`tests/factories.py`) acessivel a todos os niveis de teste
- **FR-004**: Cada teste de integracao presentation (16 arquivos) DEVE ser triado individualmente: removido se logica ja coberta por outros testes, ou reescrito como headless se testa logica de negocio unica
- **FR-005**: Cada teste unitario presentation (17 arquivos) DEVE ser triado individualmente com a mesma logica do FR-004
- **FR-005.1**: Testes reescritos como headless DEVEM permanecer nos mesmos diretorios originais (`tests/unit/presentation/`, `tests/integration/presentation/`) — a organizacao por camada arquitetural e preservada
- **FR-006**: Testes reescritos DEVEM cobrir os mesmos cenarios de negocio que os testes originais — a logica testada nao pode ser perdida
- **FR-007**: Nenhum teste no repositorio DEVE depender de display grafico, QApplication, ou pytest-qt para executar. ViewModels que herdam de classes Qt DEVEM ser testados com `unittest.mock.patch` substituindo classes base Qt por mocks puros (zero import de PySide6)
- **FR-007.1**: As dependencias pytest-qt e PySide6 DEVEM ser removidas das dev dependencies (pyproject.toml) apos a refatoracao completa dos testes
- **FR-008**: Nenhum teste no repositorio DEVE ser skipado (skip, skipIf, xfail) — todos devem executar e passar
- **FR-009**: Novos testes headless DEVEM ser criados priorizados por criticidade de negocio (criterio: arquivos com cobertura < 40% que contenham logica de negocio em ViewModels, seguidos por arquivos < 70%), visando a meta global de 90% de cobertura
- **FR-010**: O pipeline CI DEVE executar a suite completa de testes sem flags `--ignore` para presentation
- **FR-011**: A cobertura global DEVE atingir >= 90% (metrica agregada do projeto, sem exigencia por camada individual). Nota: a constituicao (XIV/XXI) define meta de 80%+ com minimo de 70%. Esta feature eleva a meta para 90% como objetivo especifico; uma emenda constitucional devera ser proposta pos-feature para alinhar.
- **FR-012**: Nenhum codigo fonte de producao (`src/`) DEVE ser alterado como parte desta feature, com EXCECAO de adicionar `# pragma: no cover` em arquivos puramente visuais nao testaveis headless (lista explicita: `app.py`, `about_dialog.py`, `rich_tooltip.py`)

### Key Entities

- **Suite de Testes**: Conjunto de arquivos de teste organizados em 3 niveis (unit, integration, e2e) e 4 camadas arquiteturais. Cada teste pertence a exatamente um nivel e uma camada.
- **Cobertura**: Medicao percentual de linhas de codigo exercitadas pelos testes, com meta global de 90%. Medida globalmente (metrica agregada do projeto).
- **Teste Headless**: Teste que nao requer display grafico, servidor X11, ou instanciacao de QApplication para execucao. Pode usar mocks para dependencias graficas.
- **ViewModel**: Classe da camada presentation que contem logica de negocio e transformacao de dados, intermediando Views (Qt) e Use Cases (application). Principal alvo de testes headless.
- **Factory de Dados**: Classe auxiliar que gera dados de teste padronizados, reutilizavel entre niveis de teste (unit, integration).

## Assumptions

- Os testes existentes de domain, application e infrastructure (86 arquivos) ja estao funcionando e nao precisam de alteracao
- Os ViewModels da camada presentation contem logica de negocio testavel sem Qt (sinais podem ser mockados)
- A cobertura real do projeto (incluindo todas as camadas) pode ser significativamente diferente dos 66.6% atuais, pois a medicao atual so inclui presentation
- O CI atual (GitHub Actions) nao possui display grafico e continuara sem
- O marker `e2e` pode ser mantido na configuracao pytest para uso futuro, mas nenhum teste deve usa-lo
- Arquivos puramente visuais (app.py, about_dialog.py, rich_tooltip.py) com 0% de cobertura DEVEM receber `pragma: no cover` — unica excecao permitida a FR-012

## Scope

**Includes**:
- Correcao da configuracao de cobertura para medir todas as camadas
- Analise completa de cobertura por arquivo e identificacao de gaps
- Remocao dos 22 arquivos de teste E2E com dependencia grafica
- Triagem e tratamento dos 16 testes de integracao presentation
- Triagem e tratamento dos 17 testes unitarios presentation
- Criacao de novos testes headless para atingir 90% de cobertura global
- Atualizacao do workflow CI para executar todos os testes
- Migracao de factories de dados para local compartilhado

**Does not include**:
- Alteracao de codigo fonte de producao (src/)
- Criacao de novos testes E2E (mesmo headless)
- Testes de performance ou stress
- Alteracao de schema de banco de dados
- Testes visuais ou de renderizacao de widgets
- Testes de acessibilidade de UI

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Cobertura de codigo global >= 90% (metrica agregada do projeto), validada no CI
- **SC-002**: Zero testes no repositorio com dependencia de display grafico — a suite completa executa sem QApplication ou bibliotecas graficas
- **SC-003**: Zero testes skipados (skip, skipIf, xfail) — todos os testes executam e passam
- **SC-004**: Pipeline CI executa todos os testes sem flags `--ignore` para presentation e passa com sucesso
- **SC-005**: Numero de cenarios de negocio cobertos pelos testes reescritos >= numero de cenarios cobertos pelos testes originais com GUI
- **SC-006**: Tempo de execucao da suite completa de testes no CI <= 5 minutos
