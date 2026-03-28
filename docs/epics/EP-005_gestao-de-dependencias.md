# EP-005 — Gestão de Dependências

**Camada:** Serviços de Negócio

---

## Problema que Resolve

Histórias de software frequentemente têm pré-requisitos: a API precisa estar pronta antes da UI que a consome. Este épico implementa o sistema completo de gestão de dependências entre histórias, incluindo: adicionar/remover dependências, **detecção de ciclos via DFS** (para evitar deadlocks lógicos), e validação de dependências entre ondas (alertar quando uma história depende de outra em onda posterior).

## Objetivo (Valor Mensurável)

Implementar a capacidade de **Gestão de Dependências** (§2.2 item 4):
- Adicionar dependências entre histórias (B depende de A)
- Remover dependências existentes
- Detectar e rejeitar ciclos de dependência com complexidade O(V+E)
- Validar e alertar sobre dependências cross-wave inválidas
- Fornecer caminho do ciclo na mensagem de erro

## Alinhamento Estratégico

Este épico implementa diretamente a **capacidade 4**: "Gestão de Dependências: Definição de pré-requisitos entre histórias com detecção de ciclos".

É pré-requisito crítico para:
- **Capacidade 5**: Cálculo de Cronograma (depende da ordenação topológica)
- **Capacidade 6**: Alocação Automática (respeita ordem de dependências)

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Define dependências técnicas entre histórias; recebe feedback imediato sobre ciclos |
| Product Owner | Entende bloqueios entre entregas; recebe alertas sobre dependências de ondas posteriores |
| Gerente de Projeto | Visualiza grafo de dependências para planejamento |

## Jornadas / Casos de Uso Afetados

- UC-002: Alocação Automática — Contribui para (dependências respeitadas na alocação)
- UC-003: Detectar e Resolver Deadlock — **Habilita** (fluxo principal e alternativo completo)
- UC-004: Importar Backlog do Excel — Contribui para (validação de ciclos no import)
- CT-002: Detecção de Ciclo em Grafo Grande — **Executável após este épico**
- CT-003: Deadlock por Falta de Devs — Parcial (dependências necessárias para cenário)

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-DEP-001: Adicionar Dependência entre Histórias (validar existência, sem auto-dependência, sem ciclo)
- RF-DEP-002: Remover Dependência (simples remoção da relação)
- RF-DEP-003: Detectar Ciclos de Dependência (algoritmo DFS O(V+E), lançar CyclicDependencyException com caminho)
- RF-DEP-004: Validar Dependências entre Ondas (alertar via InvalidWaveDependencyException quando depende de onda posterior)

**Requisitos Não-Funcionais:**
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- Utiliza tabela Story_Dependency da §6.4
- Implementa diagrama de grafo de dependências (§6.3)
- Utiliza exceções CyclicDependencyException e InvalidWaveDependencyException da §7.3

### Fora do Escopo

- RF-STORY-* → implementados em EP-002/EP-003
- RF-SCHED-* (ordenação topológica para cronograma) → será tratado em EP-006
- RF-ALOC-* (processamento de dependências na alocação) → será tratado em EP-007
- Interface gráfica para gestão de dependências → será tratada em EP-008

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-DEP-001 | Adicionar Dependência entre Histórias | Must Have |
| RF-DEP-002 | Remover Dependência | Must Have |
| RF-DEP-003 | Detectar Ciclos de Dependência | Must Have |
| RF-DEP-004 | Validar Dependências entre Ondas | Should Have |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |
| RNF-MANT-002 | Docstrings | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomática | Conforme EP-001 |
| RNF-MANT-004 | Padronização de Código | Conforme EP-001 |

---

## Critérios de Aceite (Alto Nível)

### Adicionar/Remover Dependências
- [ ] **Dado** histórias A e B independentes, **Quando** adiciono dependência B→A (B depende de A), **Então** B.dependencies contém "A"
- [ ] **Dado** história B que depende de A, **Quando** removo a dependência, **Então** B.dependencies não contém mais "A"
- [ ] **Dado** história X, **Quando** tento adicionar X→X (X depende de si mesma), **Então** ValueError é lançado

### Detecção de Ciclos
- [ ] **Dado** A→B (A depende de B), **Quando** tento adicionar B→A, **Então** CyclicDependencyException é lançada com path=["A","B","A"]
- [ ] **Dado** A→B, B→C, **Quando** tento adicionar C→A, **Então** CyclicDependencyException é lançada com path=["A","B","C","A"]
- [ ] **Dado** grafo com 50 nós e 1 ciclo escondido, **Quando** detecto ciclo, **Então** tempo < 100ms (O(V+E))

### Validação de Ondas
- [ ] **Dado** história H1 em onda 1 e H2 em onda 2, **Quando** tento adicionar H1→H2 (H1 depende de H2), **Então** InvalidWaveDependencyException é emitida como warning

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Detecção de ciclos | Tempo para grafo 50 nós | < 100ms | CT-002 |
| Complexidade do algoritmo | Big O | O(V+E) | RF-DEP-003 |
| Caminho do ciclo | Informação na exceção | Caminho completo | RF-DEP-003 |
| Validação cross-wave | Alertas emitidos | Warning (não bloqueante) | RF-DEP-004 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | Adicionar dependência válida | RF-DEP-001 |
| Testes Unitários | Remover dependência existente | RF-DEP-002 |
| Testes Unitários | Rejeitar auto-dependência | RF-DEP-001 |
| Testes Unitários | Detectar ciclo direto (A→B→A) | RF-DEP-003 |
| Testes Unitários | Detectar ciclo indireto (A→B→C→A) | RF-DEP-003 |
| Testes Unitários | Verificar caminho do ciclo na exceção | RF-DEP-003 |
| Testes Unitários | Emitir warning para dependência cross-wave | RF-DEP-004 |
| Testes Performance | Ciclo em grafo de 50 nós < 100ms | CT-002 |
| Cenário de Teste | CT-002 completo | CT-002 |
| Cenário de Teste | UC-003 completo | UC-003 |
| Revisão de Código | Validar implementação DFS correta | RF-DEP-003 |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Tabela Story_Dependency; exceções CyclicDependencyException, InvalidWaveDependencyException |
| EP-002 | Validação de auto-dependência na entidade Story |
| EP-003 | StoryRepository para consultar histórias e suas dependências |
| EP-004 | FeatureRepository para consultar ondas das features associadas às histórias |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | Grafo de dependências cabe em memória | Para backlogs de até 500 histórias, grafo é pequeno |
| Premissa | Validação de ciclo é síncrona e executada a cada adição | Otimizar se necessário com cache de estados visitados |
| Risco | Algoritmo DFS pode ter stack overflow em grafos muito profundos | Usar implementação iterativa com pilha explícita |
| Risco | Dependência cross-wave pode ser intencional (história de onda 1 prepara dados para onda 2) | RF-DEP-004 especifica warning, não bloqueio |
| Premissa | Dependência só pode ser para história existente | Validar existência antes de adicionar |
