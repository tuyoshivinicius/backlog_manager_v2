# Feature Specification: EP-010 Testes de Integracao E2E

**Feature Branch**: `010-ep010-integration-e2e-tests`
**Created**: 2026-03-03
**Status**: Draft
**Input**: Implementacao de suite de testes E2E que valide a integridade do sistema como um todo, garantindo que todos os casos de uso (UC-001 a UC-005) e cenarios de teste (CT-001 a CT-005) funcionem corretamente quando todas as camadas estao integradas.

## Out of Scope

- **Novos RFs ou RNFs**: Este epico valida os RFs implementados em EP-001 a EP-009, nao cria novos
- **Testes de carga/stress massivos**: Fora do escopo do produto desktop
- **Testes de seguranca penetration testing**: Fora do escopo
- **Cobertura de UI visual 100%**: Views tem cobertura minima 50% (Constitution XIV)
- **Alteracao de entidades existentes**: Nao modifica Story, Developer, Feature, etc.
- **Novos casos de uso**: Apenas valida UC-001 a UC-005 existentes

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Validar Suite Completa de Testes E2E (Priority: P1)

Como Gerente de Projeto, preciso de uma suite de testes E2E que valide todas as funcionalidades do sistema de ponta a ponta, para ter confianca de que o sistema esta pronto para uso em producao.

**Why this priority**: Objetivo central do epico - garantir que o sistema completo funciona corretamente com todas as camadas integradas. Sem esta validacao, nao ha garantia de integridade.

**Independent Test**: Pode ser testado executando `pytest tests/e2e/ -v` e verificando que todos os testes passam e a cobertura atinge >= 80%.

**Acceptance Scenarios**:

1. **Given** suite de testes E2E completa, **When** executo `pytest tests/e2e/ -v`, **Then** todos os testes passam em menos de 5 minutos
2. **Given** suite de testes completa (unit + integration + e2e), **When** executo `pytest --cov=src/backlog_manager --cov-fail-under=80`, **Then** cobertura e >= 80%
3. **Given** UC-001 a UC-005 implementados, **When** executo testes E2E correspondentes, **Then** todos os fluxos principais sao validados com sucesso
4. **Given** CT-001 a CT-005 definidos no SRS, **When** executo testes correspondentes, **Then** todos os cenarios sao executados e validados

---

### User Story 2 - Executar Testes E2E via GUI com pytest-qt (Priority: P1)

Como Desenvolvedor, preciso que os testes E2E executem fluxos completos via interface grafica usando pytest-qt, para garantir que a integracao UI -> ViewModel -> UseCase -> Repository funciona corretamente.

**Why this priority**: Testes E2E com GUI sao essenciais para validar a integracao de todas as camadas, especialmente a interacao usuario-sistema.

**Independent Test**: Pode ser testado executando `pytest tests/e2e/test_uc001_criar_priorizar_backlog.py` e verificando que acoes de GUI (cliques, inputs) disparam os fluxos corretos.

**Acceptance Scenarios**:

1. **Given** MainWindow aberta via pytest-qt, **When** simulo criacao de historia via qtbot, **Then** historia e criada no banco e aparece na tabela
2. **Given** teste E2E com qtbot, **When** aguardo operacao async, **Then** uso qtbot.waitSignal ou qasync sem time.sleep()
3. **Given** dialogo modal aberto, **When** interajo via qtbot, **Then** dialogo e fechado corretamente e estado e atualizado

---

### User Story 3 - Validar Cenarios de Teste CT-001 a CT-005 (Priority: P1)

Como QA Engineer, preciso que os cenarios de teste do SRS (CT-001 a CT-005) sejam implementados como testes automatizados, para validar os casos de uso criticos do sistema.

**Why this priority**: CT-001 a CT-005 cobrem os cenarios mais criticos do sistema (alocacao, ciclos, deadlocks, feriados, balanceamento).

**Independent Test**: Cada CT pode ser executado independentemente via `pytest tests/e2e/test_ct00X_*.py`.

**Acceptance Scenarios**:

1. **Given** CT-001 setup (20 historias, 5 devs), **When** executo alocacao, **Then** tempo < 5s, todas alocadas, distribuicao balanceada
2. **Given** CT-002 setup (grafo 50 nos com ciclo), **When** detecto ciclo, **Then** CyclicDependencyException em < 100ms
3. **Given** CT-003 setup (deadlock por 1 dev), **When** aloco, **Then** data ajustada sem crash
4. **Given** CT-004 setup (feriados em sequencia), **When** calculo cronograma, **Then** feriados pulados corretamente
5. **Given** CT-005 setup (balanceamento desigual), **When** aloco, **Then** distribuicao por contagem de historias

---

### User Story 4 - Validar Testes de Performance RNF-PERF (Priority: P2)

Como Tech Lead, preciso de testes que validem os requisitos de performance (RNF-PERF-001, RNF-PERF-002), para garantir que o sistema atende aos criterios de tempo de resposta.

**Why this priority**: Performance e importante mas secundaria a funcionalidade correta.

**Independent Test**: Pode ser testado executando `pytest tests/e2e/test_performance.py -v`.

**Acceptance Scenarios**:

1. **Given** backlog com 100 historias e 10 devs, **When** executo alocacao automatica, **Then** tempo <= 5 segundos
2. **Given** operacao CRUD simples (criar historia), **When** meco tempo de resposta, **Then** latencia <= 100ms
3. **Given** teste de performance, **When** executo, **Then** resultados sao reportados com metricas quantitativas

---

### User Story 5 - Garantir Roundtrip Excel Completo (Priority: P2)

Como Scrum Master, preciso que o teste de roundtrip Excel (export -> limpar banco -> import) valide integridade total dos dados, para ter confianca no mecanismo de backup.

**Why this priority**: Roundtrip Excel e critico para backup mas ja foi parcialmente testado em EP-009.

**Independent Test**: Pode ser testado via `pytest tests/e2e/test_excel_roundtrip.py`.

**Acceptance Scenarios**:

1. **Given** backlog com historias, devs, features e dependencias, **When** exporto, limpo banco e reimporto, **Then** 100% dos dados sao restaurados identicamente
2. **Given** arquivo exportado com dependencias complexas, **When** reimporto, **Then** grafo de dependencias e identico ao original

---

### User Story 6 - Configurar CI/CD com Testes E2E (Priority: P2)

Como DevOps, preciso de configuracao CI/CD que execute testes E2E com display virtual, para garantir validacao continua a cada PR.

**Why this priority**: CI/CD e importante para qualidade continua mas nao bloqueia desenvolvimento inicial.

**Independent Test**: Pode ser testado via push de PR e verificacao do workflow GitHub Actions.

**Acceptance Scenarios**:

1. **Given** PR aberto, **When** CI executa, **Then** testes E2E rodam com xvfb e reportam resultado
2. **Given** cobertura < 80%, **When** CI executa, **Then** build falha com mensagem clara
3. **Given** teste flakey, **When** CI executa, **Then** mecanismo de retry evita falsos negativos

---

### User Story 7 - Corrigir Bugs Revelados pelos Testes (Priority: P1)

Como Desenvolvedor, preciso corrigir bugs revelados pelos testes E2E conforme politica de criticidade, para garantir que o sistema atende aos requisitos.

**Why this priority**: Correcao de bugs e parte integral do epico - testes sem correcoes nao agregam valor.

**Independent Test**: Cada bug corrigido tem teste correspondente que passa apos a correcao.

**Acceptance Scenarios**:

1. **Given** bug simples revelado pelo teste, **When** identificado, **Then** correcao aplicada no mesmo PR com commit descritivo
2. **Given** bug de criticidade media, **When** identificado, **Then** correcao aplicada E comentario para analise futura adicionado
3. **Given** bug critico, **When** identificado, **Then** issue criada com causa raiz e plano de acao estruturante

---

### Edge Cases

- O que acontece quando teste E2E timeout? Sistema cancela teste e reporta falha com detalhes do estado no momento do timeout.
- O que acontece quando fixture de teste falha? Teste e marcado como erro (nao falha) e detalhes sao logados.
- O que acontece quando display virtual nao esta disponivel? CI falha early com mensagem clara sobre xvfb.
- O que acontece quando banco de teste esta corrompido? Fixture cria banco novo isolado por teste.
- O que acontece quando cobertura nao atinge 80%? CI falha com relatorio de modulos com baixa cobertura.

## Requirements *(mandatory)*

### Functional Requirements

#### Estrutura de Testes E2E

- **FR-001**: Sistema DEVE criar diretorio `tests/e2e/` para testes E2E separados de unit e integration
- **FR-002**: Sistema DEVE adicionar marcador pytest `@pytest.mark.e2e` para testes E2E que envolvem GUI
- **FR-003**: Sistema DEVE criar `tests/e2e/conftest.py` com fixtures especificas para testes E2E
- **FR-004**: Sistema DEVE criar arquivos de teste nomeados `test_ucXXX_*.py` para casos de uso e `test_ctXXX_*.py` para cenarios de teste

#### Fixtures e Setup de Dados

- **FR-010**: Sistema DEVE criar fixture `e2e_app` que inicializa QApplication com DIContainer configurado
- **FR-011**: Sistema DEVE criar fixture `e2e_main_window` que retorna MainWindow pronta para interacao
- **FR-012**: Sistema DEVE criar fixture `e2e_populated_db` que popula banco com dados de teste padronizados
- **FR-013**: Sistema DEVE criar factory functions para geracao dinamica de historias, devs e features
- **FR-014**: Sistema DEVE garantir isolamento total entre testes (banco limpo por teste)
- **FR-015**: Fixture `qasync_loop` DEVE integrar event loop asyncio com Qt event loop

#### Integracao pytest-qt + qasync

- **FR-020**: Sistema DEVE usar `QEventLoop` do qasync para compatibilidade asyncio + Qt
- **FR-021**: Sistema DEVE usar `qtbot.waitSignal` para aguardar operacoes async em vez de time.sleep()
- **FR-022**: Sistema DEVE usar `qtbot.waitUntil` para aguardar condicoes de UI
- **FR-023**: Sistema DEVE tratar dialogos modais via `QTimer.singleShot` pattern conforme ADR-002: agendar fechamento/interacao antes de abrir o dialogo
- **FR-024**: Sistema NAO DEVE usar `time.sleep()` em nenhum teste E2E (proibido). Nota: `asyncio.sleep()` e permitido para coordenacao de event loop

#### Testes UC-001 a UC-005

- **FR-030**: Sistema DEVE implementar `test_uc001_criar_historia_com_sucesso` validando criacao via GUI
- **FR-031**: Sistema DEVE implementar `test_uc001_rejeitar_sp_invalido` validando erro de SP
- **FR-032**: Sistema DEVE implementar `test_uc001_alterar_prioridade` validando mover cima/baixo
- **FR-033**: Sistema DEVE implementar `test_uc002_alocar_com_dependencias` validando alocacao completa
- **FR-034**: Sistema DEVE implementar `test_uc002_excluir_feriados` validando calculo de datas
- **FR-035**: Sistema DEVE implementar `test_uc002_balancear_carga` validando distribuicao entre devs
- **FR-036**: Sistema DEVE implementar `test_uc003_detectar_ciclo_direto` validando rejeicao de ciclo
- **FR-037**: Sistema DEVE implementar `test_uc003_detectar_ciclo_indireto` validando caminho do ciclo
- **FR-038**: Sistema DEVE implementar `test_uc004_importar_arquivo_valido` validando import via GUI
- **FR-039**: Sistema DEVE implementar `test_uc004_rejeitar_ciclo_import` validando rollback
- **FR-040**: Sistema DEVE implementar `test_uc005_processar_ondas_em_ordem` validando sequencia

#### Testes CT-001 a CT-005

- **FR-050**: Sistema DEVE implementar `test_ct001_backlog_completo_20_historias` com setup do SRS
- **FR-051**: Sistema DEVE implementar `test_ct002_detectar_ciclo_50_nos` com grafo grande
- **FR-052**: Sistema DEVE implementar `test_ct003_deadlock_falta_devs` validando ajuste de data
- **FR-053**: Sistema DEVE implementar `test_ct004_feriados_sequencia` com Carnaval e Sexta-Santa
- **FR-054**: Sistema DEVE implementar `test_ct005_balanceamento_desigual` com SPs diferentes

#### Testes de Performance

- **FR-060**: Sistema DEVE implementar `test_perf_alocacao_100_historias_5s` medindo tempo
- **FR-061**: Sistema DEVE implementar `test_perf_crud_latencia_100ms` medindo responsividade
- **FR-062**: Sistema DEVE usar `time.perf_counter()` para medicao precisa de tempo
- **FR-063**: Sistema DEVE reportar metricas de tempo e memoria em caso de falha

#### Teste de Roundtrip Excel

- **FR-070**: Sistema DEVE implementar `test_excel_roundtrip_completo` com export/limpar/import
- **FR-071**: Sistema DEVE validar igualdade de todos os campos apos reimport
- **FR-072**: Sistema DEVE comparar grafos de dependencia pre e pos roundtrip

#### Configuracao CI/CD

- **FR-080**: Sistema DEVE criar `.github/workflows/tests.yml` com job de testes E2E
- **FR-081**: Workflow DEVE instalar xvfb e executar testes com `xvfb-run`
- **FR-082**: Workflow DEVE executar `pytest --cov --cov-fail-under=80`
- **FR-083**: Workflow DEVE fazer cache de dependencias Poetry para performance
- **FR-084**: Workflow DEVE rodar em push e pull_request para branches principais

#### Cobertura e Relatorios

- **FR-090**: Sistema DEVE gerar relatorio de cobertura por modulo
- **FR-091**: Sistema DEVE configurar `pytest-cov` com `fail-under=80`
- **FR-092**: Sistema DEVE reportar cobertura separada para domain (100% alvo), application (100% alvo), infrastructure (80% alvo), presentation/viewmodels (80% alvo), presentation/views (50% minimo)

#### Estabilidade de Testes

- **FR-100**: Sistema DEVE definir timeout maximo de 30s por teste E2E
- **FR-101**: Sistema DEVE limpar estado Qt entre testes (fechar dialogos, limpar sinais)
- **FR-102**: Sistema DEVE usar fixtures com escopo apropriado (function para isolamento)
- **FR-103**: Sistema DEVE evitar dependencias entre testes (cada teste e independente)

#### Tratamento de Bugs

- **FR-110**: Bugs simples DEVEM ser corrigidos no mesmo PR com commit descritivo
- **FR-111**: Bugs de criticidade media DEVEM ter comentario `# TODO: Analisar recorrencia em [contexto]`
- **FR-112**: Bugs criticos DEVEM gerar issue com titulo `[BUG CRITICO] descricao`, corpo com causa raiz e plano de acao

### Key Entities

- **E2E Test Suite**: Conjunto de testes que validam fluxos completos usuario-sistema
- **Test Fixture**: Funcao pytest que prepara estado inicial para testes (banco populado, app inicializada)
- **Test Scenario (CT)**: Cenario de teste do SRS com setup especifico e resultado esperado
- **Use Case Test (UC)**: Teste que valida um caso de uso completo via GUI
- **Performance Test**: Teste que mede e valida metricas quantitativas de tempo/memoria
- **Coverage Report**: Relatorio de cobertura por modulo com percentuais por camada

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Suite de testes E2E completa executa em menos de 5 minutos
- **SC-002**: Cobertura global de testes atinge >= 80% (RNF-MANT-001)
- **SC-003**: 100% dos casos de uso (UC-001 a UC-005) tem testes E2E correspondentes
- **SC-004**: 100% dos cenarios de teste (CT-001 a CT-005) sao implementados como testes automatizados
- **SC-005**: Tempo de alocacao para 100 historias e <= 5 segundos (RNF-PERF-001)
- **SC-006**: Latencia de operacoes CRUD e <= 100ms (RNF-PERF-002)
- **SC-007**: 100% dos testes E2E passam consistentemente (sem flakiness)
- **SC-008**: CI/CD executa testes E2E com sucesso em ambiente com display virtual
- **SC-009**: 100% dos bugs revelados pelos testes sao corrigidos ou documentados conforme criticidade
- **SC-010**: Roundtrip Excel preserva 100% dos dados sem perda

## Architectural Decisions

### ADR-001: Localizacao dos Testes E2E

**Contexto**: Estrutura atual tem `tests/unit/` e `tests/integration/`. Precisamos decidir onde colocar testes E2E com GUI.

**Opcoes**:
1. Criar `tests/e2e/` como diretorio separado para testes E2E com GUI
2. Adicionar testes E2E em `tests/integration/` com marcador `@pytest.mark.e2e`
3. Criar subpasta `tests/integration/e2e/`

**Decisao**: Opcao 1 - Criar `tests/e2e/` como diretorio separado

**Justificativa**:
- Separacao clara de responsabilidades (unit vs integration vs e2e)
- Facilita execucao seletiva: `pytest tests/e2e/` para E2E, `pytest tests/unit/` para rapidos
- Testes E2E sao mais lentos e podem precisar de configuracao especial (xvfb)
- Evita misturar testes de backend (integration) com testes de frontend (e2e)
- Permite configurar timeouts diferentes por diretorio

---

### ADR-002: Sincronizacao pytest-qt + qasync

**Contexto**: Constitution XIV diz que testes de GUI DEVEM rodar sobre loop qasync. Precisamos definir como combinar qtbot do pytest-qt com QEventLoop do qasync.

**Opcoes**:
1. Usar fixture `qasync_loop` que cria QEventLoop e integra com qtbot
2. Usar `asyncio.run()` dentro de cada teste (viola padrao async)
3. Executar testes sincronamente com mocks de operacoes async

**Decisao**: Opcao 1 - Usar fixture `qasync_loop` com integracao qtbot

**Justificativa**:
- Mantem consistencia com arquitetura async do sistema
- Permite uso de `await` diretamente nos testes
- qtbot.waitSignal funciona naturalmente com sinais Qt emitidos por corrotinas
- Exemplo de fixture:

```python
@pytest.fixture
def qasync_loop(qapp):
    """Create asyncio event loop integrated with Qt."""
    from qasync import QEventLoop
    loop = QEventLoop(qapp)
    asyncio.set_event_loop(loop)
    yield loop
    loop.close()

@pytest.fixture
async def e2e_main_window(qasync_loop, qtbot, temp_db_path):
    """Create MainWindow with async initialization."""
    container = DIContainer.initialize(temp_db_path)
    window = MainWindow(container)
    qtbot.addWidget(window)
    window.show()
    await asyncio.sleep(0)  # Process pending events
    return window
```

---

### ADR-003: Fixtures Compartilhadas vs. Isoladas

**Contexto**: Testes E2E precisam de banco populado. Precisamos decidir como gerar dados de teste.

**Opcoes**:
1. Criar fixtures especificas para E2E com dados padronizados (hardcoded)
2. Usar factory functions para gerar dados dinamicamente
3. Carregar dados de arquivo Excel de teste via ImportExcel

**Decisao**: Opcao 2 - Usar factory functions com dados padronizados opcionais

**Justificativa**:
- Factory functions permitem customizacao por teste
- Dados padronizados garantem reproducibilidade
- Evita dependencia de arquivos externos (Excel)
- Exemplo:

```python
def create_test_stories(count: int = 5, with_dependencies: bool = False) -> list[Story]:
    """Factory para criar historias de teste."""
    stories = [
        Story(f"TEST-{i:03d}", f"Test{i}", name=f"Historia Teste {i}", story_points=5)
        for i in range(1, count + 1)
    ]
    if with_dependencies:
        for i in range(1, len(stories)):
            stories[i].add_dependency(stories[i-1].id)
    return stories
```

---

### ADR-004: Cobertura de Views vs. ViewModels

**Contexto**: Constitution XIV define cobertura diferenciada: Views 50% minimo, ViewModels 80%. Precisamos definir como medir separadamente.

**Opcoes**:
1. Configurar pytest-cov com relatorios por diretorio
2. Usar comentarios `# pragma: no cover` em Views
3. Executar medicoes separadas e combinar

**Decisao**: Opcao 1 - Configurar pytest-cov com relatorios por modulo

**Justificativa**:
- pytest-cov suporta `--cov-report term:skip-covered` e relatorio por modulo
- Configurar em pyproject.toml:

```toml
[tool.coverage.report]
# Cobertura por modulo
[tool.coverage.html]
directory = "htmlcov"
show_contexts = true
```

- Validar manualmente no relatorio:
  - domain/* >= 100%
  - application/use_cases/* >= 100%
  - infrastructure/* >= 80%
  - presentation/viewmodels/* >= 80%
  - presentation/views/* >= 50%

---

### ADR-005: Mapeamento CT do SRS para Testes Automatizados

**Contexto**: SRS define CT-001 a CT-005 com setups especificos. Precisamos mapear para testes automatizados.

**Decisao**: Mapeamento direto com fixtures especificas por CT

| CT | Arquivo de Teste | Setup | Assercoes |
|----|------------------|-------|-----------|
| CT-001 | `test_ct001_backlog_completo.py` | 20 historias, 5 devs, 2 ondas | tempo < 5s, 20/20 alocadas, ~4 por dev |
| CT-002 | `test_ct002_ciclo_grafo_grande.py` | 50 nos, ciclo em S-025->S-049 | CyclicDependencyException, < 100ms |
| CT-003 | `test_ct003_deadlock_devs.py` | 1 dev, 2 historias mesmo periodo | data ajustada, sem deadlock |
| CT-004 | `test_ct004_feriados_sequencia.py` | Historia 8 SP, inicio 01/04/2026 | pula 03/04 (Sexta-Santa) |
| CT-005 | `test_ct005_balanceamento.py` | 2 devs, 1x13SP + 4x3SP | distribuicao por contagem |

---

### ADR-006: Testes UC via GUI - Abordagem

**Contexto**: UC-001 a UC-005 sao fluxos de usuario via interface. Precisamos decidir o nivel de simulacao.

**Opcoes**:
1. Simular cliques e inputs via qtbot (fidelidade maxima)
2. Chamar ViewModels diretamente sem simular cliques (mais estavel)
3. Combinar ambos: cliques para acoes principais, ViewModel para validacoes

**Decisao**: Opcao 3 - Abordagem hibrida

**Justificativa**:
- Simular cliques para acoes principais (criar, editar, deletar) - valida integracao UI
- Usar ViewModel diretamente para validacoes de estado - evita flakiness
- Trade-off entre fidelidade e estabilidade
- Exemplo:

```python
async def test_uc001_criar_historia_com_sucesso(qtbot, e2e_main_window):
    """Test UC-001: Criar historia via GUI."""
    window = e2e_main_window

    # Simula clique no botao Nova Historia
    qtbot.mouseClick(window.btn_new_story, Qt.LeftButton)

    # Aguarda dialogo abrir
    dialog = await qtbot.waitUntil(lambda: window.findChild(StoryDialog))

    # Preenche campos via qtbot
    qtbot.keyClicks(dialog.txt_component, "TEST")
    qtbot.keyClicks(dialog.txt_name, "Historia Teste")

    # Confirma
    qtbot.mouseClick(dialog.btn_save, Qt.LeftButton)

    # Valida via ViewModel (mais estavel que inspecionar tabela)
    assert len(window.viewmodel.stories) == 1
    assert window.viewmodel.stories[0].component == "TEST"
```

---

### ADR-007: Tratamento de Bugs - Documentacao

**Contexto**: Epico define politica de criticidade. Precisamos definir formato de documentacao.

**Decisao**: Formato padronizado por criticidade

| Criticidade | Acao Imediata | Formato de Documentacao |
|-------------|---------------|------------------------|
| Simples | Correcao no PR | Commit: `fix: [descricao curta]` |
| Media | Correcao + comentario | `# TODO(EP-010): Analisar [contexto] - [causa provavel]` |
| Critica | Issue + plano | Issue com template: Titulo, Causa Raiz, Impacto, Plano de Acao |

**Template de Issue para Bug Critico**:
```markdown
## [BUG CRITICO] Descricao curta

### Causa Raiz
[Explicacao tecnica da causa]

### Impacto
- [Lista de funcionalidades afetadas]

### Plano de Acao
1. [Acao corretiva imediata]
2. [Acao preventiva para evitar recorrencia]

### Testes Relacionados
- [ ] test_xxx que revelou o bug
- [ ] test_yyy que valida a correcao
```

---

### ADR-008: Performance dos Testes - Estrategia de Otimizacao

**Contexto**: Testes E2E com GUI sao lentos. Suite completa deve rodar em < 5 minutos.

**Decisao**: Estrategia multi-camada de otimizacao

1. **Timeout por teste**: 30s maximo (falha se exceder)
2. **Paralelizacao**: Usar `pytest-xdist` com `-n auto` para testes independentes
3. **Fixtures session-scoped**: `qapp` e `qasync_loop` com escopo `session`
4. **Pular testes lentos em pre-commit**: Marcador `@pytest.mark.slow` para testes > 10s
5. **Cache de inicializacao**: DIContainer criado uma vez por sessao

**Configuracao pyproject.toml**:
```toml
[tool.pytest.ini_options]
markers = [
    "e2e: End-to-end tests with GUI",
    "slow: Slow tests (> 10s)",
]
timeout = 30
```

---

### ADR-009: Testes de Performance - Localizacao

**Contexto**: RNF-PERF-001 e RNF-PERF-002 definem metricas quantitativas.

**Opcoes**:
1. Juntar com testes E2E em `tests/e2e/test_performance.py`
2. Criar diretorio separado `tests/performance/`
3. Executar sob demanda como subconjunto opcional

**Decisao**: Opcao 1 - Manter em `tests/e2e/test_performance.py` com marcador `@pytest.mark.perf`

**Justificativa**:
- Testes de performance usam mesma infraestrutura de E2E (GUI, banco real)
- Marcador permite execucao seletiva: `pytest -m perf`
- Simplicidade sobre separacao excessiva

**Implementacao**:
```python
@pytest.mark.perf
@pytest.mark.e2e
async def test_perf_alocacao_100_historias(e2e_populated_db):
    """RNF-PERF-001: Alocacao <= 5s para 100 historias."""
    stories = create_test_stories(100)
    developers = create_test_developers(10)

    start = time.perf_counter()
    result = await allocation_service.allocate_stories(stories, developers)
    elapsed = time.perf_counter() - start

    assert elapsed <= 5.0, f"Alocacao levou {elapsed:.2f}s (limite: 5s)"
```

---

### ADR-010: CI/CD com Display Virtual

**Contexto**: Testes com GUI precisam de display. GitHub Actions nao tem display por padrao.

**Decisao**: Usar `xvfb-run` no workflow GitHub Actions

**Configuracao `.github/workflows/tests.yml`**:
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Cache Poetry dependencies
        uses: actions/cache@v4
        with:
          path: ~/.cache/pypoetry
          key: ${{ runner.os }}-poetry-${{ hashFiles('poetry.lock') }}

      - name: Install dependencies
        run: poetry install --with dev

      - name: Install xvfb
        run: sudo apt-get install -y xvfb

      - name: Run tests with coverage
        run: |
          xvfb-run -a poetry run pytest --cov=src/backlog_manager --cov-fail-under=80 --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
```

---

### ADR-011: Estabilidade de Testes GUI (Flakiness)

**Contexto**: Testes E2E com Qt podem ser flakey por timing de eventos.

**Decisao**: Boas praticas obrigatorias para estabilidade

1. **Sempre usar qtbot.waitSignal**: Para aguardar operacoes async
2. **Nunca usar time.sleep()**: Proibido em testes E2E
3. **Garantir estado limpo**: Fixture com teardown que fecha dialogos
4. **Usar timeouts explicitos**: `qtbot.waitSignal(signal, timeout=5000)`
5. **Tratar dialogos modais**: Fechar antes de prosseguir

**Exemplo de Padrao**:
```python
async def test_com_estabilidade(qtbot, e2e_main_window):
    window = e2e_main_window

    # Aguarda sinal com timeout explicito
    with qtbot.waitSignal(window.viewmodel.stories_loaded, timeout=5000):
        await window.viewmodel.load_stories()

    # Usa waitUntil para condicoes de UI
    qtbot.waitUntil(lambda: window.table.rowCount() > 0, timeout=3000)

    # Garante dialogo fechado no teardown
    yield
    for dialog in window.findChildren(QDialog):
        dialog.close()
```

---

### ADR-012: Bugs Criticos e Refatoracao

**Contexto**: Se testes E2E revelarem bugs criticos que exigem refatoracao, podem impactar escopo.

**Decisao**: Procedimento estruturado para bugs criticos

1. **Isolar correcao**: Criar branch `fix/ep010-bug-<descricao>` se refatoracao > 1 arquivo
2. **Registrar issue**: Com template de bug critico (ADR-007)
3. **Ajustar plano**: Se correcao impactar > 2 dias, criar sub-tarefa no PR
4. **Limites de atuacao**: Bugs criticos que exigem redesign arquitetural ficam como issue para proximo epico

**Criterios de Escopo**:
- Bug corrigivel em < 4 horas: Corrigir no PR do epico
- Bug corrigivel em 4h-2 dias: Corrigir em branch separada, merge antes do PR principal
- Bug que exige > 2 dias ou redesign: Issue para proximo epico, teste marcado `@pytest.mark.skip`

---

### ADR-013: Validacao de Cobertura Final

**Contexto**: RNF-MANT-001 exige >= 80% de cobertura.

**Decisao**: Validacao automatizada com acoes corretivas

1. **Comando de verificacao**: `pytest --cov=src/backlog_manager --cov-fail-under=80`
2. **Relatorio por modulo**: `--cov-report term-missing` mostra linhas nao cobertas
3. **Acoes corretivas se meta nao atingida**:
   - Identificar modulos com cobertura < alvo
   - Adicionar testes unitarios para codigo nao coberto
   - Priorizar domain e application (devem ter 100%)

**Configuracao final em pyproject.toml**:
```toml
[tool.coverage.run]
source = ["src/backlog_manager"]
branch = true

[tool.coverage.report]
fail_under = 80
show_missing = true
exclude_lines = [
    "pragma: no cover",
    "if TYPE_CHECKING:",
    "@abstractmethod",
]
```

---

### ADR-014: Roundtrip Excel como Teste E2E

**Contexto**: UC-004 + RF-EXCEL valida import/export. Precisamos especificar teste de roundtrip.

**Decisao**: Teste de roundtrip completo com validacao de igualdade

**Implementacao**:
```python
@pytest.mark.e2e
async def test_excel_roundtrip_completo(e2e_populated_db, tmp_path):
    """Validate export -> clear -> reimport preserves all data."""
    # Setup: Backlog com todos os tipos de dados
    stories_original = await uow.story_repo.find_all()
    developers_original = await uow.developer_repo.find_all()
    features_original = await uow.feature_repo.find_all()
    dependencies_original = await uow.dependency_repo.get_all_dependencies()

    # Export
    export_path = tmp_path / "backup.xlsx"
    await export_use_case.execute(ExportExcelInputDTO(file_path=export_path))

    # Clear database
    await clear_all_data(uow)

    # Reimport
    await import_use_case.execute(ImportExcelInputDTO(file_path=export_path))

    # Validate: Stories
    stories_restored = await uow.story_repo.find_all()
    assert len(stories_restored) == len(stories_original)
    for orig, rest in zip(sorted(stories_original), sorted(stories_restored)):
        assert orig.id == rest.id
        assert orig.name == rest.name
        assert orig.story_points == rest.story_points
        # ... validar todos os campos

    # Validate: Dependencies (grafo identico)
    deps_restored = await uow.dependency_repo.get_all_dependencies()
    assert set(deps_restored) == set(dependencies_original)
```

## Traceability Matrix

### UC -> Testes E2E

| UC | Testes | RFs Validados |
|----|--------|---------------|
| UC-001 | test_uc001_criar_historia, test_uc001_alterar_prioridade, test_uc001_rejeitar_sp | RF-STORY-001 a RF-STORY-009 |
| UC-002 | test_uc002_alocar_com_dependencias, test_uc002_balancear_carga | RF-ALOC-001 a RF-ALOC-012 |
| UC-003 | test_uc003_detectar_ciclo_direto, test_uc003_ciclo_indireto | RF-DEP-003 |
| UC-004 | test_uc004_importar_valido, test_uc004_rejeitar_ciclo | RF-EXCEL-001 a RF-EXCEL-005 |
| UC-005 | test_uc005_ondas_em_ordem, test_uc005_onda_unica | RF-FEAT-001 a RF-FEAT-005 |

### CT -> Testes Automatizados

| CT | Teste | RNFs Validados |
|----|-------|----------------|
| CT-001 | test_ct001_backlog_completo_20_historias | RNF-PERF-001 |
| CT-002 | test_ct002_detectar_ciclo_50_nos | RNF-PERF-002 |
| CT-003 | test_ct003_deadlock_falta_devs | RNF-CONF-002 |
| CT-004 | test_ct004_feriados_sequencia | RF-SCHED-003 |
| CT-005 | test_ct005_balanceamento_desigual | RF-ALOC-002 |

### RNF -> Testes de Validacao

| RNF | Teste | Metrica |
|-----|-------|---------|
| RNF-MANT-001 | pytest --cov-fail-under=80 | >= 80% cobertura |
| RNF-PERF-001 | test_perf_alocacao_100_historias | <= 5s |
| RNF-PERF-002 | test_perf_crud_latencia | <= 100ms |
| RNF-CONF-001 | All E2E tests pass | 99% sessoes sem crash |
| RNF-CONF-002 | test_error_handling_* | 100% erros tratados |

## Test Scenarios

### Estrutura de Arquivos de Teste

```
tests/
├── conftest.py                    # Fixtures globais (existente)
├── unit/                          # Testes unitarios (existente)
├── integration/                   # Testes de integracao (existente)
└── e2e/                           # NOVO - Testes E2E
    ├── __init__.py
    ├── conftest.py                # Fixtures E2E (qasync_loop, e2e_app, etc.)
    ├── factories.py               # Factory functions para dados de teste
    ├── test_uc001_criar_priorizar_backlog.py
    ├── test_uc002_alocacao_automatica.py
    ├── test_uc003_detectar_resolver_deadlock.py
    ├── test_uc004_importar_excel.py
    ├── test_uc005_gerenciar_ondas.py
    ├── test_ct001_backlog_completo.py
    ├── test_ct002_ciclo_grafo_grande.py
    ├── test_ct003_deadlock_devs.py
    ├── test_ct004_feriados_sequencia.py
    ├── test_ct005_balanceamento.py
    ├── test_performance.py
    └── test_excel_roundtrip.py
```

## Assumptions

- Todas as funcionalidades de EP-001 a EP-009 estao implementadas e funcionais
- pytest-qt 4.4+ e qasync 0.27+ estao instalados e configurados
- pytest-asyncio em modo `auto` funciona com pytest-qt
- GitHub Actions suporta xvfb para testes GUI
- Cobertura atual do codigo e inferior a 80% (justifica necessidade de testes E2E)
- Testes existentes em tests/unit/ e tests/integration/ continuam funcionando
- MainWindow e dialogs aceitam interacao via qtbot
- DIContainer pode ser resetado entre testes para isolamento

## Clarifications

### Session 2026-03-03

- Q: Testes E2E devem cobrir todos os fluxos alternativos (FA) dos casos de uso? → A: Sim, fluxos alternativos criticos (validacoes, erros) devem ter testes
- Q: Testes de performance devem rodar em CI? → A: Sim, mas com tolerancia maior (ex: 10s em vez de 5s) devido a variabilidade de CI
- Q: Bugs encontrados em EP-001 a EP-009 devem ser corrigidos neste epico? → A: Sim, conforme politica de criticidade definida no epic
