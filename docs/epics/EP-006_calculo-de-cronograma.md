# EP-006 — Cálculo de Cronograma

**Camada:** Serviços de Negócio

---

## Problema que Resolve

Para alocar desenvolvedores e planejar entregas, o sistema precisa calcular automaticamente as datas de início e fim de cada história, considerando: duração baseada em story points e velocidade, apenas dias úteis (segunda a sexta), feriados nacionais brasileiros, e ordem de dependências. Este épico implementa o SchedulingService com todos os cálculos de cronograma.

## Objetivo (Valor Mensurável)

Implementar a capacidade de **Cálculo de Cronograma** (§2.2 item 5):
- Calcular duração em dias úteis: `ceil(SP / velocity_per_day)` com mínimo de 1 dia
- Considerar apenas dias úteis (segunda a sexta)
- Excluir feriados nacionais brasileiros (2026-2028 hardcoded)
- Respeitar dependências no sequenciamento (start_date >= max(end_date_deps) + 1)
- Ajustar datas que caem em dias não úteis
- Ordenar backlog topologicamente (Kahn's algorithm)

## Alinhamento Estratégico

Este épico implementa diretamente a **capacidade 5**: "Cálculo de Cronograma: Datas automáticas baseadas em velocidade e dependências".

É pré-requisito crítico para:
- **Capacidade 6**: Alocação Automática (requer datas calculadas para alocar)

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Obtém cronograma realista considerando dependências e feriados |
| Gerente de Projeto | Visualiza datas de entrega calculadas automaticamente |
| Product Owner | Entende impacto de priorização nas datas de entrega |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — Contribui para (cálculo de datas após priorização)
- UC-002: Alocação Automática — Contribui para (pré-condição: datas calculadas, ordenação topológica)
- CT-001: Backlog Completo 20 Histórias — Contribui para (datas calculadas)
- CT-004: Feriados em Sequência — **Executável após este épico**

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-SCHED-001: Calcular Duração da História (`duration = ceil(SP / velocity)`, mínimo 1 dia)
- RF-SCHED-002: Considerar Apenas Dias Úteis (segunda a sexta, ajustar início em fim de semana)
- RF-SCHED-003: Excluir Feriados Brasileiros (12 feriados/ano, 2026-2028 hardcoded)
- RF-SCHED-004: Respeitar Dependências no Cronograma (start >= max(end_deps) + 1 dia útil)
- RF-SCHED-005: Ajustar Data de Início (avançar para próximo dia útil se necessário)
- RF-SCHED-006: Ordenação Topológica (Kahn's algorithm, O(V+E), desempate por prioridade)

**Requisitos Não-Funcionais:**
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- Apêndice A: Lista de feriados brasileiros 2026-2028
- Regras de §8.3: duração mínima = 1 dia útil

### Fora do Escopo

- RF-ALOC-* (alocação de desenvolvedores) → será tratado em EP-007
- Interface gráfica para visualização de cronograma → será tratada em EP-008
- Feriados regionais ou configuráveis → fora do escopo do produto (§2.4)

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-SCHED-001 | Calcular Duração da História | Must Have |
| RF-SCHED-002 | Calcular com Dias Úteis | Must Have |
| RF-SCHED-003 | Excluir Feriados Nacionais | Must Have |
| RF-SCHED-004 | Sequenciar por Dependências | Must Have |
| RF-SCHED-005 | Ajustar para Dia Útil | Must Have |
| RF-SCHED-006 | Ordenar Backlog Topologicamente | Must Have |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |
| RNF-MANT-002 | Docstrings | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomática | Conforme EP-001 |
| RNF-MANT-004 | Padronização de Código | Conforme EP-001 |

---

## Critérios de Aceite (Alto Nível)

### Cálculo de Duração
- [ ] **Dado** SP=5 e velocity=2 SP/dia, **Quando** calculo duração, **Então** duration = ceil(5/2) = 3 dias úteis
- [ ] **Dado** SP=3 e velocity=5 SP/dia, **Quando** calculo duração, **Então** duration = 1 (mínimo)

### Dias Úteis
- [ ] **Dado** start_date=sábado (07/03/2026), **Quando** ajusto para dia útil, **Então** start_date = 09/03/2026 (segunda)
- [ ] **Dado** tarefa de 2 dias iniciando sexta-feira, **Quando** calculo end_date, **Então** end_date = segunda-feira seguinte

### Feriados
- [ ] **Dado** tarefa de 2 dias iniciando 20/04/2026 (segunda), **Quando** calculo end_date, **Então** end_date = 22/04/2026 (pula 21/04 - Tiradentes)
- [ ] **Dado** tarefa de 4 dias iniciando 01/04/2026, **Quando** calculo end_date, **Então** end_date = 07/04/2026 (pula 03/04 - Sexta-feira Santa, sábado e domingo)

### Dependências
- [ ] **Dado** B depende de A e A.end_date = 04/03/2026, **Quando** calculo B.start_date, **Então** B.start_date >= 05/03/2026
- [ ] **Dado** C depende de A e B, A.end=03/03 e B.end=05/03, **Quando** calculo C.start_date, **Então** C.start_date >= 06/03

### Ordenação Topológica
- [ ] **Dado** A→B→C (C depende de B, B depende de A), **Quando** ordeno topologicamente, **Então** ordem = [A, B, C]
- [ ] **Dado** duas histórias independentes com prioridades 1 e 2, **Quando** ordeno, **Então** prioridade 1 vem primeiro (desempate)

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Cálculo de duração | Fórmula correta | ceil(SP/velocity), min 1 | RF-SCHED-001 |
| Dias úteis | Exclusão de fins de semana | 100% | RF-SCHED-002 |
| Feriados | Exclusão de 12 feriados/ano | 100% | RF-SCHED-003 |
| Ordenação topológica | Complexidade | O(V+E) | RF-SCHED-006 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | Calcular duração com diferentes SP e velocidades | RF-SCHED-001 |
| Testes Unitários | Verificar duração mínima = 1 | RF-SCHED-001 |
| Testes Unitários | Ajustar data de sábado/domingo para segunda | RF-SCHED-002 |
| Testes Unitários | Testar cada um dos 12 feriados de 2026 | RF-SCHED-003 |
| Testes Unitários | Sequência de feriados (Carnaval, Sexta-Santa) | RF-SCHED-003 |
| Testes Unitários | Start_date após end_date de dependência | RF-SCHED-004 |
| Testes Unitários | Múltiplas dependências (pegar max end_date) | RF-SCHED-004 |
| Testes Unitários | Ajustar data que cai em feriado | RF-SCHED-005 |
| Testes Unitários | Ordenação topológica com Kahn | RF-SCHED-006 |
| Testes Unitários | Desempate por prioridade | RF-SCHED-006 |
| Cenário de Teste | CT-004 completo | CT-004 |
| Revisão de Código | Validar implementação Kahn's algorithm | RF-SCHED-006 |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Infraestrutura de persistência e logging |
| EP-002 | Entidade Story com campos duration, start_date, end_date |
| EP-003 | StoryRepository para consultar e atualizar histórias |
| EP-005 | DependencyService para obter grafo de dependências para ordenação topológica |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | Feriados nacionais são suficientes (sem feriados regionais) | Documentado em §2.4 como restrição |
| Premissa | Período 2026-2028 hardcoded é aceitável | Adicionar feriados de anos futuros em versões posteriores |
| Premissa | Velocidade é informada em SP/dia | Converter se necessário (ex: SP/sprint ÷ dias do sprint) |
| Risco | Carnaval e Corpus Christi têm datas móveis | Calcular via fórmula de Páscoa ou hardcode por ano |
| Risco | Kahn's algorithm pode não funcionar com ciclos | EP-005 garante que não há ciclos no grafo |
| Premissa | Ordenação topológica considera grafo completo em memória | Para 500 histórias, é viável |
