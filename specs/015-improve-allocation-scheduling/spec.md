# Feature Specification: Melhoria Iterativa dos Algoritmos de Alocacao e Cronograma

**Feature Branch**: `015-improve-allocation-scheduling`
**Created**: 2026-03-12
**Status**: Draft
**Input**: User description: "EP-015: Melhoria Iterativa dos Algoritmos de Alocacao e Cronograma"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Diagnostico de Problemas via Logs Estruturados (Priority: P1)

O usuario executa a alocacao automatica e observa um comportamento inesperado (ex: distribuicao desbalanceada). Para diagnosticar o problema, o usuario consulta os logs em %APPDATA%/BacklogManager/logs/ e encontra metricas detalhadas que permitem correlacionar o comportamento visual com decisoes internas do algoritmo.

**Why this priority**: Esta e a base fundamental para qualquer ciclo de melhoria iterativa. Sem logs estruturados em pontos criticos, nao e possivel diagnosticar problemas nos algoritmos.

**Independent Test**: Pode ser testado executando a alocacao e verificando se os logs contem as metricas esperadas (AllocationMetrics) em formato estruturado.

**Acceptance Scenarios**:

1. **Given** AllocationService executa alocacao para 190 historias, **When** consulto logs apos execucao, **Then** encontro log de nivel INFO com todas as 16 metricas de AllocationMetrics (total_time_seconds, stories_allocated, deadlocks_detected, etc.)
2. **Given** AllocationService processa uma onda, **When** consulto logs em nivel DEBUG, **Then** encontro logs para cada decisao de selecao de desenvolvedor com justificativa (dependency_owner vs load_balancing)
3. **Given** ocorre deteccao de deadlock durante alocacao, **When** consulto logs, **Then** encontro log de nivel WARNING com historias envolvidas e motivo do deadlock

---

### User Story 2 - Reproducao de Cenarios com Dados de Teste (Priority: P2)

O usuario precisa reproduzir um problema identificado. Utilizando o seed script (EP-014), o usuario gera dados de teste deterministicos (random seed 42) que permitem reproduzir exatamente o mesmo cenario de alocacao.

**Why this priority**: Reproducibilidade e essencial para validar correcoes. Sem dados consistentes, nao e possivel confirmar que uma correcao realmente resolveu o problema.

**Independent Test**: Pode ser testado executando o seed script duas vezes com --clean e verificando que o banco de dados resultante e identico.

**Acceptance Scenarios**:

1. **Given** banco de dados vazio, **When** executo seed script com --clean, **Then** banco contem exatamente 7 desenvolvedores, 7 features, ~190 historias e ~102 dependencias
2. **Given** banco de dados populado, **When** executo alocacao duas vezes com mesmos parametros, **Then** resultado de alocacao e identico (mesmas atribuicoes desenvolvedor-historia)
3. **Given** problema identificado em iteracao anterior, **When** executo seed script com --clean e repito alocacao, **Then** consigo reproduzir o mesmo problema

---

### User Story 3 - Ciclo de Melhoria Iterativa Colaborativa (Priority: P2)

O usuario identifica um problema visual na alocacao (ex: "Ana tem 30 historias, Bruno tem 5"). O usuario descreve o problema usando o protocolo de comunicacao definido, e Claude Code analisa logs, identifica causa raiz, propoe correcao, e aguarda aprovacao antes de implementar.

**Why this priority**: Este e o fluxo principal de trabalho para melhorias. Define como usuario e Claude Code colaboram para identificar e corrigir problemas.

**Independent Test**: Pode ser testado simulando um ciclo completo de descricao-analise-correcao-validacao.

**Acceptance Scenarios**:

1. **Given** usuario descreve problema usando formato padrao (acao, resultado visual, problema observado, expectativa), **When** Claude Code analisa logs correspondentes, **Then** consegue correlacionar comportamento visual com metricas internas
2. **Given** diagnostico de problema concluido, **When** Claude Code propoe correcao, **Then** plano inclui arquivos especificos a modificar, mudancas propostas, e impacto esperado
3. **Given** correcao aprovada e implementada, **When** executo suite de testes, **Then** todos os testes passam sem regressoes

---

### User Story 4 - Validacao de Performance Apos Correcao (Priority: P3)

Apos cada correcao implementada, o usuario precisa validar que a performance permanece dentro dos limites estabelecidos (tempo de alocacao <= 5 segundos para 100 historias).

**Why this priority**: Garantir que melhorias nao degradem performance e requisito nao-funcional critico.

**Independent Test**: Pode ser testado executando alocacao com 100 historias e medindo tempo total.

**Acceptance Scenarios**:

1. **Given** backlog com 100 historias e 10 desenvolvedores, **When** executo alocacao automatica, **Then** AllocationMetrics.total_time_seconds <= 5.0
2. **Given** correcao implementada, **When** comparo tempo antes e depois, **Then** variacao de performance e documentada no log de correcao
3. **Given** correcao degrada performance alem do limite, **When** verifico metricas, **Then** correcao e revertida ou otimizada

---

### User Story 5 - Validacao de Cobertura e Complexidade Apos Correcao (Priority: P3)

Apos cada correcao implementada, o usuario precisa validar que a cobertura de testes permanece >= 80% e a complexidade ciclomatica das funcoes modificadas permanece <= 15.

**Why this priority**: Manter qualidade de codigo conforme requisitos nao-funcionais estabelecidos.

**Independent Test**: Pode ser testado executando comandos de cobertura e analise de complexidade.

**Acceptance Scenarios**:

1. **Given** correcao implementada, **When** executo pytest com cobertura, **Then** cobertura total >= 80%
2. **Given** funcao modificada em AllocationService, **When** verifico complexidade ciclomatica, **Then** valor <= 15
3. **Given** metricas de qualidade violadas, **When** identifico problema, **Then** correcao e ajustada para manter conformidade

---

### Edge Cases

- O que acontece quando logs estao desabilitados ou nivel e superior a DEBUG?
  - Sistema funciona normalmente, mas diagnostico detalhado nao e possivel; documentar que nivel DEBUG e necessario para ciclos de melhoria
- O que acontece quando seed script e executado sem --clean em banco com dados existentes?
  - Dados adicionais sao inseridos, potencialmente causando conflitos; seed script ja implementa este comportamento
- O que acontece quando correcao introduz regressao que so aparece em cenario especifico?
  - Suite de testes deve cobrir cenarios principais; se regressao escapar, sera identificada em proxima iteracao
- O que acontece quando problema nao e reproduzivel com dados de teste?
  - Usuario pode fornecer dump do banco real (com permissao) ou ajustar parametros do seed para simular cenario

## Requirements *(mandatory)*

### Functional Requirements

**Infraestrutura de Diagnostico:**

- **FR-001**: Sistema DEVE logar metricas completas de AllocationMetrics em nivel INFO ao final de cada execucao de alocacao
- **FR-002**: Sistema DEVE logar em nivel DEBUG cada decisao de selecao de desenvolvedor, incluindo motivo (dependency_owner, load_balancing)
- **FR-003**: Sistema DEVE logar em nivel WARNING qualquer deteccao de deadlock, incluindo historias envolvidas
- **FR-004**: Sistema DEVE logar em nivel WARNING/INFO deteccoes de ociosidade excessiva (max_idle_days)
- **FR-005**: Sistema DEVE logar em nivel INFO inicio e fim de processamento de cada onda

**Reproducibilidade:**

- **FR-006**: Sistema DEVE utilizar seed script existente (EP-014) para geracao de dados de teste reproduziveis
- **FR-007**: Sistema DEVE produzir resultados de alocacao identicos para mesmos dados de entrada e configuracao

**Processo de Melhoria (Protocolo de 6 Etapas):**

1. **Observar**: Usuario executa alocacao e observa comportamento visual
2. **Descrever**: Usuario descreve problema usando formato padrao (acao, resultado, problema, expectativa)
3. **Analisar logs**: Claude Code consulta logs estruturados para correlacionar comportamento
4. **Diagnosticar**: Claude Code identifica causa raiz baseado em metricas e decisoes logadas
5. **Propor correcao**: Claude Code apresenta plano com arquivos, mudancas e impacto esperado
6. **Validar**: Executar suite de testes e confirmar correcao sem regressoes

- **FR-008**: Sistema DEVE manter documentacao de cada correcao aplicada (problema, diagnostico, mudanca, resultado)
- **FR-009**: Sistema DEVE executar suite de testes completa antes de considerar correcao como finalizada

### Key Entities *(include if feature involves data)*

- **AllocationMetrics**: Estrutura existente com 16 campos que capturam metricas de execucao (total_time_seconds, stories_processed, stories_allocated, waves_processed, total_iterations, iterations_per_wave, allocations_by_dependency_owner, allocations_by_load_balancing, deadlocks_detected, date_adjustments, validation_reallocations, validation_dependency_fixes, validation_conflict_fixes, max_idle_violations_detected, max_idle_violations_fixed, failed_reallocations)
- **AllocationConfig**: Configuracao de alocacao (velocity, project_start_date, max_idle_days, allocation_criteria, max_iterations, random_seed)
- **Log de Correcao**: Registro de cada iteracao de melhoria contendo: problema identificado, diagnostico, mudanca aplicada, resultado

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Logs de alocacao contem todas as 16 metricas de AllocationMetrics em formato legivel
- **SC-002**: Alocacao para 190 historias (seed data) completa em <= 5 segundos
- **SC-003**: Alocacao para 100 historias completa em <= 5 segundos
- **SC-004**: 100% dos ciclos de melhoria iterativa seguem o protocolo definido (6 etapas)
- **SC-005**: Zero regressoes introduzidas por correcoes (todos os testes existentes passam)
- **SC-006**: Cobertura de testes permanece >= 80% apos correcoes
- **SC-007**: Complexidade ciclomatica de funcoes modificadas permanece <= 15
- **SC-008**: Usuario consegue correlacionar comportamento visual com logs em 100% dos casos de diagnostico
- **SC-009**: Alocacao para 500 historias (limite de escalabilidade) completa em <= 30 segundos

## Clarifications

### Session 2026-03-12

- Q: Logs de alocação podem conter dados sensíveis de desenvolvedores. Qual estratégia de proteção? → A: Sem proteção adicional (logs locais apenas, protegidos pelo sistema de arquivos do usuário)
- Q: Qual é o limite máximo de histórias que o algoritmo deve suportar com performance aceitável? → A: 500 histórias em <= 30 segundos
- Q: Quais são as 6 etapas do protocolo de melhoria iterativa (SC-004)? → A: 1-Observar, 2-Descrever, 3-Analisar logs, 4-Diagnosticar, 5-Propor correção, 6-Validar

## Assumptions

- Logs são locais e não requerem proteção adicional além do sistema de arquivos do usuário
- Logs sao armazenados em %APPDATA%/BacklogManager/logs/ conforme configuracao existente
- Seed script (EP-014) ja esta implementado e funcional
- AllocationMetrics ja possui todos os campos necessarios para diagnostico basico
- Suite de testes existente cobre cenarios principais de alocacao e cronograma
- Nivel de log DEBUG esta disponivel para diagnostico detalhado
- Usuario esta disponivel para participar ativamente nos ciclos de melhoria
- Clean Architecture ja estabelecida permite modificacoes isoladas
- Mensagens de log serao em portugues conforme Constituicao do projeto

## Out of Scope

- Criacao de novos requisitos funcionais (RF-xxx)
- Alteracoes na interface grafica
- Testes E2E sistematicos (cobertos por EP-010)
- Mudanca de estrategia de balanceamento (contagem vs SP) - decisao de design ja documentada
- Exposicao de metricas na GUI
- Sistema de tracing distribuido
- Novos campos em AllocationMetrics alem dos 16 existentes
