# EP-015 — Melhoria Iterativa dos Algoritmos de Alocacao e Cronograma

**Camada:** Servicos de Negocio

---

## Problema que Resolve

Os algoritmos de alocacao automatica (AllocationService) e calculo de cronograma (SchedulingService) sao os componentes mais complexos do Backlog Manager, com mais de 1.500 linhas de codigo combinadas. Embora funcionalmente completos (EP-006 e EP-007), esses algoritmos podem apresentar comportamentos subotimos em cenarios reais: distribuicao desbalanceada de historias, datas sobrepostas, historias nao alocadas, ou deadlocks inesperados. Este epico estabelece um processo colaborativo de melhoria iterativa onde Claude Code executa a aplicacao, analisa logs, e o usuario descreve o comportamento visual, permitindo identificar e implementar correcoes incrementais nos algoritmos.

## Objetivo (Valor Mensuravel)

Estabelecer processo de melhoria iterativa dos algoritmos de alocacao e cronograma:
- Infraestrutura de diagnostico: logs detalhados com metricas de execucao (AllocationMetrics)
- Dados de teste reproduziveis via seed script (EP-014)
- Ciclo iterativo: Preparar → Executar → Observar → Analisar → Implementar → Testar
- Correcoes incrementais nos algoritmos conforme problemas identificados
- Validacao de melhorias via testes unitarios e de integracao existentes
- Manter conformidade com RNF-PERF-001 (≤ 5s para 100 historias)

## Alinhamento Estrategico

Este epico refina as **capacidades 5 e 6** do produto (SRS §2.2):
- **Capacidade 5**: Calculo de Cronograma — refinamento do SchedulingService
- **Capacidade 6**: Alocacao Automatica — refinamento do AllocationService

E complementar ao EP-010 (Testes E2E), focando em melhorias de qualidade dos algoritmos.

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Alocacao automatica mais confiavel e previsivel |
| Gerente de Projeto | Cronogramas mais precisos e distribuicao equilibrada |
| Product Owner | Menos intervencoes manuais necessarias pos-alocacao |

## Jornadas / Casos de Uso Afetados

- UC-002: Executar Alocacao Automatica com Dependencias — Contribui para (melhoria de qualidade)
- CT-001: Backlog Completo 20 Historias — Contribui para (refinamento de comportamento)
- CT-003: Deadlock por Falta de Desenvolvedores — Contribui para (melhoria de deteccao)
- CT-005: Balanceamento com Tamanhos Diferentes — Contribui para (refinamento de distribuicao)

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais (Refinamento — nao sao escopo principal):**
- RF-ALOC-001 a RF-ALOC-013: Refinamento de implementacao conforme problemas identificados
- RF-SCHED-001 a RF-SCHED-006: Refinamento de implementacao conforme problemas identificados

**Requisitos Nao-Funcionais:**
- RNF-PERF-001: Manter tempo de alocacao ≤ 5s para 100 historias
- RNF-CONF-005: Utilizacao de logs para diagnostico (Constitution XVII)
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- Fluxo de Alocacao Automatica (§6.2): Validacao de conformidade
- AllocationMetrics (RF-ALOC-011): Utilizacao para diagnostico
- Constantes de limite (RF-ALOC-013): Ajuste se necessario

**Processo de Melhoria Iterativa:**

```
┌─────────────────────────────────────────────────────────────────────┐
│                    CICLO DE ITERACAO                                │
│                                                                     │
│  1. PREPARAR    →  2. EXECUTAR  →  3. OBSERVAR  →  4. ANALISAR     │
│  (seed data)       (GUI app)       (usuario ve)     (logs + desc)  │
│                                                                     │
│       ↑                                              ↓              │
│       │                                                             │
│  6. TESTAR     ←  5. IMPLEMENTAR  ←  APROVAR PLANO                 │
│  (proxima iteracao)  (codigo)                                       │
└─────────────────────────────────────────────────────────────────────┘
```

**Arquivos Criticos:**

| Arquivo | Linhas | Responsabilidade |
|---------|--------|------------------|
| src/backlog_manager/domain/services/allocation_service.py | ~1.283 | Logica principal de alocacao |
| src/backlog_manager/domain/services/scheduling_service.py | ~315 | Calculo de datas, workdays |
| src/backlog_manager/domain/services/dependency_service.py | — | Grafo de dependencias |
| src/backlog_manager/application/use_cases/allocation/execute_allocation.py | ~157 | Use case orquestrador |
| src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py | ~150 | Use case orquestrador |
| src/backlog_manager/infrastructure/logging/logger_config.py | — | Configuracao de logging |

### Fora do Escopo

- Novos requisitos funcionais (RF-xxx) → nao serao criados
- Alteracoes na interface grafica → sera tratada em outros epicos
- Testes E2E sistematicos → cobertos por EP-010
- Mudanca de estrategia de balanceamento (contagem vs SP) → decisao de design documentada

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Este epico REFINA RFs existentes, nao possui RFs como escopo principal | — |
| RF-ALOC-001..013 | Refinamento conforme problemas identificados | — |
| RF-SCHED-001..006 | Refinamento conforme problemas identificados | — |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-PERF-001 | Tempo de Alocacao | ≤ 5s para 100 historias (manter) |
| RNF-CONF-005 | Sistema de Logs | Utilizacao para diagnostico |
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomatica | ≤ 15 para funcoes de alocacao |

---

## Criterios de Aceite (Alto Nivel)

### Infraestrutura de Diagnostico
- [ ] **Dado** execucao de alocacao automatica, **Quando** consulto logs em %APPDATA%/BacklogManager/logs/, **Entao** encontro metricas detalhadas (stories_allocated, deadlocks_detected, etc.)
- [ ] **Dado** seed script executado com --clean, **Quando** inicio aplicacao, **Entao** banco contem dados reproduziveis (7 devs, 190 historias, 102 dependencias)

### Ciclo de Melhoria
- [ ] **Dado** problema identificado pelo usuario (ex: "15 historias sem desenvolvedor"), **Quando** analiso logs, **Entao** consigo correlacionar comportamento visual com metricas internas
- [ ] **Dado** diagnostico de problema, **Quando** proponho correcao, **Entao** plano inclui mudancas especificas em arquivos identificados
- [ ] **Dado** correcao implementada, **Quando** executo testes existentes, **Entao** nenhuma regressao e introduzida

### Qualidade dos Algoritmos
- [ ] **Dado** backlog com 100 historias e 10 desenvolvedores, **Quando** executo alocacao, **Entao** tempo ≤ 5 segundos (RNF-PERF-001)
- [ ] **Dado** correcao aplicada, **Quando** executo mesmos dados de teste, **Entao** comportamento melhora conforme esperado

### Conformidade
- [ ] **Dado** qualquer correcao implementada, **Quando** verifico cobertura de testes, **Entao** permanece ≥ 80%
- [ ] **Dado** funcao modificada, **Quando** verifico complexidade ciclomatica, **Entao** permanece ≤ 15

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Tempo de alocacao | Segundos | ≤ 5s (100 historias) | RNF-PERF-001 |
| Problemas corrigidos | Bugs/melhorias por iteracao | ≥ 1 por ciclo | Qualitativo |
| Regressoes | Testes quebrados | 0 | RNF-MANT-001 |
| Cobertura | % linhas cobertas | ≥ 80% | RNF-MANT-001 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Testes Unitarios | Executar suite existente apos cada correcao | RF-ALOC-* |
| Testes Unitarios | Executar suite existente apos cada correcao | RF-SCHED-* |
| Testes Integracao | Validar use cases de alocacao | UC-002 |
| Testes Performance | Verificar tempo ≤ 5s para 100 historias | RNF-PERF-001 |
| Analise de Logs | Correlacionar metricas com comportamento | RNF-CONF-005 |
| Revisao de Codigo | Validar complexidade ciclomatica ≤ 15 | RNF-MANT-003 |
| Teste Manual | Usuario valida comportamento visual na GUI | Qualitativo |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-006 | SchedulingService implementado — alvo de refinamento |
| EP-007 | AllocationService implementado — alvo de refinamento |
| EP-014 | Seed script para geracao de dados de teste reproduziveis |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Premissa | Aplicacao GUI (PySide6) — Claude Code nao pode "ver" a tela diretamente | Usuario descreve comportamento visual no chat |
| Premissa | Dados de teste reproduziveis via seed script (random seed fixo = 42) | EP-014 implementado |
| Premissa | Logs capturam metricas suficientes para diagnostico | AllocationMetrics (RF-ALOC-011) ja implementado |
| Risco | Correcao pode introduzir regressoes | Executar suite de testes completa apos cada mudanca |
| Risco | Problema pode nao ser reproduzivel com dados de teste | Usar dados reais do usuario (com permissao) ou ajustar seed |
| Risco | Correcao pode degradar performance | Medir tempo antes/depois de cada correcao |
| Premissa | Codigo bem estruturado (Clean Architecture) facilita modificacoes isoladas | Arquitetura ja estabelecida em EP-001 |
| Premissa | Usuario disponivel para feedback visual durante ciclos | Processo colaborativo requer participacao ativa |

---

## Protocolo de Comunicacao

### Formato de Descricao do Usuario

Para facilitar a analise, o usuario deve descrever:

1. **Acao executada**: "Cliquei em Alocar Desenvolvedores"
2. **Resultado visual**: "A tabela mostrou X historias alocadas, Y sem desenvolvedor"
3. **Problemas observados**: "Desenvolvedora Ana tem 30 historias, Bruno tem 5"
4. **Expectativa**: "Esperava distribuicao mais equilibrada"

### Formato de Resposta do Claude

1. **Analise dos logs**: Correlacao com comportamento descrito
2. **Diagnostico**: Causa raiz identificada no codigo
3. **Plano de correcao**: Mudancas especificas propostas
4. **Aguardar aprovacao**: Antes de implementar

---

## Comandos Uteis para Cada Iteracao

```bash
# 1. Preparar dados de teste (limpar + popular)
python scripts/seed_test_backlog.py --clean --db-path ./test_iteration.db

# 2. Executar aplicacao
backlog-manager ./test_iteration.db

# 3. Executar testes unitarios do allocation_service
poetry run pytest tests/unit/domain/services/test_allocation_service.py -v

# 4. Executar testes de integracao
poetry run pytest tests/integration/application/use_cases/allocation/ -v

# 5. Verificar cobertura
poetry run pytest --cov=src/backlog_manager --cov-report=term-missing
```
