# EP-013 — Exposicao do Calculo de Cronograma na GUI

**Camada:** Interface & Experiencia

---

## Problema que Resolve

O use case `calculate_schedule` (RF-SCHED-001 a RF-SCHED-006) esta implementado e registrado no DI Container, porem nao ha forma do usuario dispara-lo pela interface grafica. O EP-008 assume que o calculo de cronograma ja foi executado antes da alocacao automatica ("backlog com historias elegiveis, datas calculadas, sem dev"), mas nao ha gatilho na GUI para isso. O fluxo esta incompleto: o usuario nao consegue calcular datas via interface antes de executar a alocacao.

A toolbar atual possui: Nova Historia, Editar, Deletar, Mover Cima/Baixo, Desenvolvedores, Features, Alocar Automaticamente — mas nenhum botao para calcular cronograma.

## Objetivo (Valor Mensuravel)

Permitir que o usuario execute o calculo de cronograma diretamente pela interface grafica:
- Botao "Calcular Cronograma" na toolbar, posicionado antes de "Alocar Automaticamente"
- Atalho de teclado Ctrl+Shift+C para acesso rapido
- Feedback via QMessageBox informando quantas historias tiveram datas calculadas
- Leitura de `velocity` e `start_date` do ConfigPanel existente

Apos este epico, o fluxo completo estara disponivel na GUI: cadastrar historias → definir dependencias → calcular cronograma → alocar automaticamente.

## Alinhamento Estrategico

Este epico completa a integracao da **capacidade 5** (Calculo de Cronograma) com a camada de Interface & Experiencia:
- EP-006 implementou o SchedulingService (backend)
- EP-008 implementou a MainWindow e ConfigPanel (frontend)
- EP-013 conecta ambos, habilitando o fluxo completo

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Uso diario — pode calcular cronograma antes de alocar desenvolvedores |
| Gerente de Projeto | Uso semanal — visualiza datas calculadas para planejamento |
| Product Owner | Uso semanal — entende impacto de priorizacao nas datas |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — **Contribui para** (calculo de datas apos priorizacao)
- UC-002: Alocacao Automatica com Dependencias — **Habilita pre-condicao** (datas calculadas antes de alocar)
- CT-001: Backlog Completo 20 Historias — **Executavel via GUI** apos este epico
- CT-004: Feriados em Sequencia — **Executavel via GUI** apos este epico

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- Nenhum RF novo — exposicao de RF-SCHED-* ja implementados

**Funcionalidades de UI a implementar:**

| Componente | Descricao | RFs Relacionados |
|------------|-----------|------------------|
| ScheduleButton | Botao "Calcular Cronograma" na toolbar | RF-SCHED-001 a RF-SCHED-006 |
| ScheduleAction | QAction com atalho Ctrl+Shift+C | RF-SCHED-001 |
| MainWindowViewModel.calculate_schedule() | Metodo async que invoca use case | RF-SCHED-001 a RF-SCHED-006 |
| Feedback Dialog | QMessageBox com resumo do calculo | RNF-CONF-002 |

**Requisitos Nao-Funcionais:**
- RNF-PERF-002: Responsividade ≤ 500ms para recalculo (ja definido)
- RNF-USAB-003: Acessibilidade (atalho de teclado, tooltip)
- RNF-CONF-002: Recuperacao de erros (mensagem clara em caso de falha)

### Fora do Escopo

- Alteracao no DI Container — factory method `create_calculate_schedule_use_case()` ja existe
- Alteracao no use case `calculate_schedule` — ja implementado em EP-006
- Alteracao no ConfigPanel — inputs `velocity` e `start_date` ja existem
- Visualizacao grafica de timeline/Gantt → fora do escopo do produto

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Nenhum RF novo — integracao de UI | — |

**Funcionalidades de integracao:**

| Item | Descricao | Validacao |
|------|-----------|-----------|
| Botao na toolbar | Icone + texto "Calcular Cronograma" | Visivel na interface |
| Atalho Ctrl+Shift+C | Atalho de teclado para acao | Funcional |
| ViewModel method | `calculate_schedule()` async | Invoca use case corretamente |
| Signal/Slot wiring | Conexao botao → ViewModel | Testavel |
| Feedback dialog | QMessageBox com resultado | Exibe contagem de historias |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-PERF-002 | Responsividade | ≤ 500ms para recalculo |
| RNF-USAB-003 | Acessibilidade | Atalho Ctrl+Shift+C, tooltip descritivo |
| RNF-CONF-002 | Recuperacao de Erros | Mensagem clara sem crash |

---

## Criterios de Aceite (Alto Nivel)

### Botao e Atalho
- [ ] **Dado** MainWindow carregada, **Quando** observo a toolbar, **Entao** vejo botao "Calcular Cronograma" posicionado antes de "Alocar Automaticamente"
- [ ] **Dado** foco na aplicacao, **Quando** pressiono Ctrl+Shift+C, **Entao** calculo de cronograma e executado
- [ ] **Dado** botao "Calcular Cronograma", **Quando** passo mouse sobre ele, **Entao** tooltip "Calcular datas de inicio e fim das historias (Ctrl+Shift+C)" aparece

### Execucao do Calculo
- [ ] **Dado** backlog com 5 historias sem datas e ConfigPanel com velocity=2 e start_date=02/03/2026, **Quando** clico "Calcular Cronograma", **Entao** todas as 5 historias tem start_date e end_date calculados
- [ ] **Dado** historias com dependencias, **Quando** calculo cronograma, **Entao** datas respeitam ordem topologica (dependencia termina antes de dependente iniciar)
- [ ] **Dado** calculo bem-sucedido, **Quando** operacao completa, **Entao** dialog exibe "X historias tiveram datas calculadas"

### Validacao de Parametros
- [ ] **Dado** ConfigPanel com velocity vazio ou invalido, **Quando** clico "Calcular Cronograma", **Entao** dialog de erro exibe mensagem clara sobre parametro invalido
- [ ] **Dado** ConfigPanel com start_date no passado, **Quando** clico "Calcular Cronograma", **Entao** calculo e executado normalmente (datas no passado sao validas)

### Atualizacao da Tabela
- [ ] **Dado** calculo executado, **Quando** operacao completa, **Entao** tabela de backlog e atualizada com novas datas visiveis

### Performance
- [ ] **Dado** backlog com 100 historias, **Quando** calculo cronograma, **Entao** operacao completa em ≤ 500ms

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Latencia recalculo | Milissegundos | ≤ 500ms | RNF-PERF-002 |
| Cobertura de testes | % linhas ViewModel | ≥ 80% | RNF-MANT-001 |
| Acessibilidade | Atalho funcional | 100% | RNF-USAB-003 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Testes Unitarios | ViewModel.calculate_schedule() com mocks | RF-SCHED-001 |
| Testes Unitarios | Validacao de parametros (velocity, start_date) | RF-SCHED-001 |
| Testes Integracao | Signal/slot connection botao → ViewModel | - |
| Testes E2E | Fluxo completo: criar historia → calcular → verificar datas | CT-001 |
| Teste Manual | Atalho Ctrl+Shift+C funcional | RNF-USAB-003 |
| Teste Manual | Tooltip visivel no botao | RNF-USAB-003 |
| Teste Manual | Dialog de feedback apos calculo | RNF-CONF-002 |
| Teste Manual | Mensagem de erro com parametros invalidos | RNF-CONF-002 |
| Revisao de Codigo | Separacao View/ViewModel (MVVM) | §6.1 |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-006 | SchedulingService e CalculateScheduleUseCase implementados |
| EP-008 | MainWindow, toolbar, ConfigPanel com inputs velocity/start_date |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Premissa | ConfigPanel ja expoe velocity e start_date como propriedades acessiveis | Verificar implementacao atual |
| Premissa | CalculateScheduleUseCase retorna contagem de historias processadas | Verificar retorno do DTO |
| Premissa | DI Container ja registra factory para use case | Verificado em container.py |
| Risco | UI pode ficar bloqueada durante calculo com muitas historias | Usar QThread ou asyncio corretamente via qasync |
| Risco | Parametros do ConfigPanel podem estar em formato invalido | Validar antes de invocar use case |
