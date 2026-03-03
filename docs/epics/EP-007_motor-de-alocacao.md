# EP-007 — Motor de Alocação

**Camada:** Serviços de Negócio

---

## Problema que Resolve

O desafio central do Backlog Manager é distribuir automaticamente o trabalho entre desenvolvedores de forma inteligente e equilibrada. Este épico implementa o **AllocationService** completo: alocar desenvolvedores por balanceamento de carga, processar ondas sequencialmente, detectar e resolver conflitos de período, identificar deadlocks, monitorar ociosidade, e executar o loop de estabilização pós-alocação. É o componente algorítmico mais complexo do sistema.

## Objetivo (Valor Mensurável)

Implementar a capacidade de **Alocação Automática** (§2.2 item 6):
- Alocar desenvolvedores automaticamente para todas as histórias elegíveis
- Balancear carga por contagem de histórias (não por SP)
- Processar ondas sequencialmente (wave 0, 1, 2...)
- Detectar e resolver conflitos de período automaticamente
- Detectar deadlocks e emitir warnings
- Monitorar e alertar sobre ociosidade excessiva
- Executar loop de estabilização com máximo 10 passadas
- Coletar métricas detalhadas de execução
- Completar em ≤ 5 segundos para 100 histórias e 10 desenvolvedores

## Alinhamento Estratégico

Este épico implementa diretamente a **capacidade 6**: "Alocação Automática: Distribuição inteligente de trabalho entre desenvolvedores".

Após este épico, todas as 6 capacidades core do MVP estão implementadas na camada de serviços.

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Uso diário — executa alocação automática e visualiza métricas |
| Gerente de Projeto | Analisa distribuição de carga e identifica gargalos |
| Product Owner | Entende impacto da priorização na alocação |

## Jornadas / Casos de Uso Afetados

- UC-002: Alocação Automática com Dependências — **Habilita** (fluxo principal completo)
- UC-003: Detectar e Resolver Deadlock — Contribui para (detecção de deadlock na alocação)
- CT-001: Backlog Completo 20 Histórias — **Executável após este épico**
- CT-003: Deadlock por Falta de Desenvolvedores — **Executável após este épico**
- CT-005: Balanceamento com Tamanhos Diferentes — **Executável após este épico**

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-ALOC-001: Executar Alocação Automática (alocar todas as histórias elegíveis)
- RF-ALOC-002: Balanceamento de Carga (distribuir por contagem de histórias, desempate aleatório)
- RF-ALOC-003: Critério Proprietário de Dependência (priorizar dev que fez dependências, configurável)
- RF-ALOC-004: Evitar Conflitos de Período (detectar sobreposição, ajustar datas)
- RF-ALOC-005: Ajustar Datas por Indisponibilidade (incrementar +1 dia útil)
- RF-ALOC-006: Processar por Ondas (wave 0, 1, 2... sequencialmente)
- RF-ALOC-007: Detectar Deadlocks (emitir DeadlockWarning, pular para próxima onda)
- RF-ALOC-008: Detectar Ociosidade (IdlenessWarning para gaps dentro da onda)
- RF-ALOC-009: Configurar Limite de Ociosidade (max_idle_days: 2-30, padrão 3)
- RF-ALOC-010: Realocar para Minimizar Ociosidade (max 3 realocações por história)
- RF-ALOC-011: Coletar Métricas de Alocação (AllocationMetrics completo)
- RF-ALOC-012: Validação e Estabilização Pós-Alocação (loop de 10 passadas)
- RF-ALOC-013: Limites de Segurança do Algoritmo (constantes MAX_*)

**Requisitos Não-Funcionais:**
- RNF-PERF-001: Tempo de alocação ≤ 5s para 100 histórias e 10 devs
- RNF-PERF-003: Consumo de memória ≤ 150 MB para 100 histórias
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- Fluxo de Alocação Automática (§6.2): Implementação completa do fluxograma
- AllocationMetrics: Estrutura completa conforme RF-ALOC-011
- Constantes de limite conforme RF-ALOC-013

### Fora do Escopo

- Interface gráfica para alocação → será tratada em EP-008
- Integração Excel → será tratada em EP-009

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-ALOC-001 | Executar Alocação Automática | Must Have |
| RF-ALOC-002 | Balanceamento de Carga | Must Have |
| RF-ALOC-003 | Critério Proprietário de Dependência | Should Have |
| RF-ALOC-004 | Evitar Conflitos de Período | Must Have |
| RF-ALOC-005 | Ajustar Datas por Indisponibilidade | Must Have |
| RF-ALOC-006 | Processar por Ondas | Must Have |
| RF-ALOC-007 | Detectar Deadlocks | Should Have |
| RF-ALOC-008 | Detectar Ociosidade | Should Have |
| RF-ALOC-009 | Configurar Limite de Ociosidade | Should Have |
| RF-ALOC-010 | Realocar para Minimizar Ociosidade | Could Have |
| RF-ALOC-011 | Coletar Métricas de Alocação | Should Have |
| RF-ALOC-012 | Validação e Estabilização Pós-Alocação | Must Have |
| RF-ALOC-013 | Limites de Segurança do Algoritmo | Must Have |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-PERF-001 | Tempo de Alocação | ≤ 5s para 100 histórias, 10 devs |
| RNF-PERF-003 | Consumo de Memória | ≤ 150 MB para 100 histórias |
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |
| RNF-MANT-002 | Docstrings | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomática | ≤ 15 para funções de alocação |
| RNF-MANT-004 | Padronização de Código | Conforme EP-001 |

---

## Critérios de Aceite (Alto Nível)

### Alocação Básica
- [ ] **Dado** 3 histórias elegíveis e 2 devs, **Quando** executo alocação automática, **Então** todas as 3 histórias têm developer_id != NULL
- [ ] **Dado** Dev1 com 2 histórias e Dev2 com 1 história, **Quando** aloco nova história, **Então** história é atribuída a Dev2 (menos histórias)

### Processamento por Ondas
- [ ] **Dado** Feature "Auth" (onda 1) com 3 histórias e Feature "API" (onda 2) com 2 histórias, **Quando** executo alocação, **Então** todas as 3 de onda 1 são alocadas antes das 2 de onda 2
- [ ] **Dado** 2 histórias sem feature (wave=0) e 2 em onda 1, **Quando** executo alocação, **Então** wave=0 são alocadas primeiro

### Conflitos e Deadlocks
- [ ] **Dado** Dev1 com história A (02/03-04/03) e história B (03/03-05/03) - CONFLITO, **Quando** sistema resolve conflitos, **Então** B.start_date = 05/03 (após A.end_date)
- [ ] **Dado** onda 2 com 3 histórias pendentes e nenhum dev disponível, **Quando** sistema detecta que não houve progresso, **Então** emite DeadlockWarning e processa onda 3

### Métricas
- [ ] **Dado** alocação completa, **Quando** consulto métricas, **Então** tenho: total_time_seconds, stories_allocated, waves_processed, deadlocks_detected, etc.

### Performance
- [ ] **Dado** 100 histórias e 10 desenvolvedores, **Quando** executo alocação, **Então** tempo ≤ 5 segundos

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Tempo de alocação | Segundos | ≤ 5s (100 histórias) | RNF-PERF-001 |
| Histórias alocadas | % do total elegível | 100% (sem deadlock) | RF-ALOC-001 |
| Balanceamento | Desvio entre devs | Mínimo possível | RF-ALOC-002 |
| Conflitos resolvidos | % de conflitos | 100% | RF-ALOC-004 |
| Loop de estabilização | Passadas necessárias | ≤ 10 | RF-ALOC-012 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | Alocar histórias elegíveis | RF-ALOC-001 |
| Testes Unitários | Verificar balanceamento por contagem | RF-ALOC-002 |
| Testes Unitários | Testar critério DEPENDENCY_OWNER | RF-ALOC-003 |
| Testes Unitários | Detectar e resolver conflitos de período | RF-ALOC-004 |
| Testes Unitários | Ajustar data +1 dia útil | RF-ALOC-005 |
| Testes Unitários | Processar ondas em ordem | RF-ALOC-006 |
| Testes Unitários | Detectar e emitir DeadlockWarning | RF-ALOC-007 |
| Testes Unitários | Detectar gaps e emitir IdlenessWarning | RF-ALOC-008 |
| Testes Unitários | Validar limites de max_idle_days | RF-ALOC-009 |
| Testes Unitários | Testar realocação por ociosidade | RF-ALOC-010 |
| Testes Unitários | Verificar AllocationMetrics completo | RF-ALOC-011 |
| Testes Unitários | Loop de estabilização funciona | RF-ALOC-012 |
| Testes Unitários | Limites MAX_* respeitados | RF-ALOC-013 |
| Testes Performance | 100 histórias em ≤ 5s | RNF-PERF-001 |
| Testes Performance | 500 histórias em ≤ 15s | RNF-PERF-001 |
| Cenário de Teste | CT-001 completo | CT-001 |
| Cenário de Teste | CT-003 completo | CT-003 |
| Cenário de Teste | CT-005 completo | CT-005 |
| Revisão de Código | Validar fluxo conforme §6.2 | §6.2 |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Exceções AllocationException, DeadlockWarning, IdlenessWarning |
| EP-002 | Entidade Story com campos de alocação |
| EP-003 | StoryRepository para consultar e atualizar histórias |
| EP-004 | DeveloperRepository para obter lista de desenvolvedores |
| EP-005 | DependencyService para _ensure_dependencies_finished |
| EP-006 | SchedulingService para cálculo de datas e ordenação topológica |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Risco | Algoritmo pode não convergir em casos extremos | Limites MAX_* garantem término; DeadlockWarning permite continuar |
| Risco | Performance pode degradar com muitas histórias | Limite suave de 500 histórias com warning (RNF-PERF-001) |
| Premissa | Balanceamento por contagem é suficiente | Decisão de design documentada; pode evoluir para SP em versão futura |
| Premissa | Desempate aleatório é justo | Random seed pode ser fixado para testes determinísticos |
| Risco | Loop de estabilização pode ter muitas passadas | MAX_STABILIZATION_PASSES = 10 garante término |
| Premissa | Uma história por desenvolvedor por vez | Constraint do sistema (sem paralelismo por dev) |
| Risco | Complexidade ciclomática alta no AllocationService | Extrair métodos auxiliares; aceitar ≤ 15 para funções principais |
