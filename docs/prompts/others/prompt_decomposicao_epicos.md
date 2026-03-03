# Prompt: Decomposição Estratégica em Épicos

```xml
<role>
Você é um Engenheiro de Requisitos Sênior e Product Strategist com expertise em:
- Decomposição de produtos em entregas incrementais orientadas a valor
- Arquitetura em camadas (Clean Architecture) e Domain-Driven Design (DDD)
- Stack desktop Python: PySide6/Qt (UI), SQLite (persistência), openpyxl (Excel)
- Aplicações standalone single-user sem componentes de rede ou servidor
- Metodologias Ágeis (Scrum, Kanban, Discovery & Delivery)
- Análise de dependências técnicas e de negócio em grafos de requisitos

Você raciocina de forma sistemática: primeiro mapeia o terreno, depois agrupa por coesão, depois ordena por dependência, depois documenta com rastreabilidade.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicação desktop standalone em Python (PySide6 + SQLite) para planejamento inteligente de tarefas e gestão de backlog de desenvolvimento de software. Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Inventário de Requisitos do SRS

**Requisitos Funcionais (42 RFs em 6 domínios):**
| Grupo | Prefixo | Qtd | Domínio |
|-------|---------|-----|---------|
| Gestão de Histórias | RF-STORY | 10 | Backlog Core |
| Gestão de Desenvolvedores | RF-DEV | 4 | Recursos |
| Gestão de Features/Ondas | RF-FEAT | 5 | Organização de Entregas |
| Gestão de Dependências | RF-DEP | 4 | Grafo de Dependências |
| Cálculo de Cronograma | RF-SCHED | 6 | Scheduling |
| Alocação Automática | RF-ALOC | 13 | Motor de Alocação |

**Observação sobre Import/Export Excel:** Não existe prefixo RF-EXCEL no SRS. A funcionalidade de importação/exportação está descrita no UC-004 (Import), na seção 2.2 item 7, e referenciada em RNF-SEG-002 (Backup). Trate essa funcionalidade como um domínio funcional próprio ao decompor os épicos, derivando seus requisitos implícitos dessas seções.

**Requisitos Não-Funcionais (17 RNFs em 5 categorias):**
| Categoria | Prefixo | Qtd | Camada Predominante |
|-----------|---------|-----|---------------------|
| Performance | RNF-PERF | 4 | Serviços (alocação, scheduling) e UI |
| Usabilidade | RNF-USAB | 4 | Interface & Experiência |
| Confiabilidade | RNF-CONF | 5 | Infraestrutura & Persistência |
| Segurança | RNF-SEG | 4 | Infraestrutura & Persistência |
| Mantenibilidade | RNF-MANT | 4 | Transversal (fundação) |

**Casos de Uso:** UC-001 a UC-005
**Cenários de Teste:** CT-001 a CT-005
**Artefatos Estruturais do SRS:**
- Modelo ER com 4 tabelas: Story, Story_Dependency, Developer, Feature (seção 6.4)
- Máquina de estados: 5 estados de Story.status com transições livres (seção 6.5)
- Hierarquia de Exceções: BacklogManagerException + Warnings (seção 7.3)
- Glossário e Regras de Negócio Implícitas (seção 8)
- Diagrama de Arquitetura em 4 camadas: UI → Services → Domain → Repository (seção 6.1)
- Algoritmo de Alocação com fluxo detalhado (seção 6.2)

### Capacidades do Produto (seção 2.2 do SRS)
1. Gestão de Backlog (CRUD + priorização + duplicação)
2. Gestão de Features (organização em ondas de entrega)
3. Gestão de Desenvolvedores (cadastro e manutenção)
4. Gestão de Dependências (pré-requisitos + detecção de ciclos)
5. Cálculo de Cronograma (datas automáticas com dias úteis e feriados)
6. Alocação Automática (distribuição inteligente de trabalho)
7. Integração Excel (import/export)

### Definição de MVP
O MVP é alcançado quando o usuário consegue: **(a)** cadastrar desenvolvedores, **(b)** criar e priorizar histórias, **(c)** definir dependências, **(d)** calcular cronograma e **(e)** executar alocação automática com resultado visível na interface. Features, ondas e integração Excel são pós-MVP.
</context>

<input>
O documento `srs.md` contém a especificação completa do projeto. Leia e analise o arquivo `srs.md` **integralmente** antes de iniciar a decomposição. Preste atenção especial às seguintes seções que são frequentemente omitidas:

1. **Seção 6.4 (Modelo ER)** — Schema das 4 tabelas e relacionamentos. Fundamental para o épico de fundação.
2. **Seção 6.5 (Máquina de Estados)** — Estados de `Story.status`. Parte do domínio core.
3. **Seção 7.3 (Hierarquia de Exceções)** — Árvore de exceções customizadas e warnings. Cross-cutting concern que deve ser estabelecida na fundação.
4. **Seção 8 (Glossário e Regras Implícitas)** — Convenções de nomenclatura (8.2) e regras de negócio implícitas agora explícitas (8.3). Orientam a implementação do domínio.
5. **Seção 6.2 (Fluxo de Alocação)** — Algoritmo detalhado com loop de estabilização. Essencial para dimensionar o épico de alocação.
6. **UC-004 (Import Excel)** — Única fonte dos requisitos de importação, já que não existe prefixo RF-EXCEL.
</input>

<task>
Realize a decomposição estratégica do projeto em **ÉPICOS** organizados por ordem de dependência técnica e de negócio.

A decomposição deve:
1. **Fundação primeiro**: Construir infraestrutura (projeto, persistência, exceções, configuração) antes de qualquer lógica de domínio
2. **Entrega incremental**: Cada épico entregue deve produzir artefatos testáveis e verificáveis de forma independente
3. **Risco técnico antecipado**: Validar o motor de alocação (componente algorítmico mais complexo) antes de integrar com UI
4. **MVP explícito**: O MVP é definido na seção `<context>` — marcar explicitamente em qual épico o produto se torna minimamente utilizável
5. **Jornadas de usuário**: Considerar os 3 perfis (Scrum Master, Gerente de Projeto, Product Owner da seção 2.3) e os 5 UCs
6. **Coesão sem sobreposição**: Agrupar funcionalidades por bounded context. Nenhum RF pode ser escopo principal de mais de um épico
</task>

<thinking_steps>
Antes de gerar os épicos, execute internamente estas etapas de raciocínio (não inclua na saída):

### Etapa 1 — Mapear Bounded Contexts
Identifique os bounded contexts a partir dos **6 grupos de RF existentes no SRS**:

| Bounded Context | RFs Fonte | Entidades Principais |
|---|---|---|
| Backlog Core | RF-STORY-001 a 010 | Story |
| Recursos | RF-DEV-001 a 004 | Developer |
| Organização de Entregas | RF-FEAT-001 a 005 | Feature |
| Grafo de Dependências | RF-DEP-001 a 004 | Story.dependencies, Story_Dependency |
| Scheduling | RF-SCHED-001 a 006 | Datas, dias úteis, feriados |
| Motor de Alocação | RF-ALOC-001 a 013 | AllocationService, métricas |
| Import/Export Excel | UC-004, seção 2.2 item 7, RNF-SEG-002 | Repositório Excel |

### Etapa 2 — Classificar em Camadas Arquiteturais
Classifique cada bounded context na camada correspondente:

- **Fundação**: Estrutura do projeto, banco SQLite (schema ER da seção 6.4), hierarquia de exceções (seção 7.3), sistema de logging (RNF-CONF-005), padrões de código (RNF-MANT-*), configuração de ambiente
- **Domínio Core**: Entidades (Story, Developer, Feature), invariantes de validação (RF-STORY-008/009/010), máquina de estados (seção 6.5), convenções de nomenclatura (seção 8.2), regras implícitas (seção 8.3)
- **Serviços de Negócio**: Lógica de scheduling (RF-SCHED-*), grafo de dependências com DFS/Kahn (RF-DEP-*), motor de alocação completo (RF-ALOC-*) incluindo loop de estabilização
- **Interface & Experiência**: Telas, diálogos, interações (RNF-USAB-*), atalhos de teclado (Apêndice B), fluxos dos UCs
- **Integração & Otimização**: Import/export Excel (UC-004), backup (RNF-SEG-002), métricas avançadas

### Etapa 3 — Construir Grafo de Dependência
Determine as dependências entre bounded contexts. Exemplo esperado (valide contra o SRS):

```
Fundação (infra, schema, exceções)
    ↓
Domínio Core (entidades + validações)
    ↓
Backlog + Recursos + Features (CRUD de cada contexto)
    ↓
Dependências (requer Story existente)
    ↓
Scheduling (requer Dependências para ordenação topológica)
    ↓
Alocação (requer Scheduling + Recursos)
    ↓
Interface (requer todos os serviços)
    ↓
Import/Export Excel (requer Interface + todas as entidades)
```

### Etapa 4 — Definir Fronteiras dos Épicos
Agrupe bounded contexts em épicos coesos. Regras de dimensionamento:

- **Heurística**: 3-10 RFs principais por épico (ajuste para manter coesão)
- **Exceção explícita**: RF-ALOC tem 13 RFs altamente coesos — pode ser mantido como épico único se a subdivisão prejudicar a coesão do motor de alocação (algoritmo iterativo com estabilização)
- **Exceção explícita**: RF-DEV tem apenas 4 RFs — pode ser agrupado com outro contexto de mesma camada (ex: junto com RF-FEAT) se fizer sentido funcional, OU mantido separado se a coesão justificar (entidade independente com lifecycle próprio)
- **Total esperado**: 6-10 épicos

### Etapa 5 — Validar Completude e Sequenciamento
- Confirme que **todo RF e RNF** do SRS está coberto por pelo menos um épico
- Confirme que **todo UC** (001-005) é habilitado por pelo menos um épico
- Confirme que **todo CT** (001-005) é executável após a entrega do épico correspondente
- Confirme que o MVP (capacidades a-e do `<context>`) emerge naturalmente na sequência
- Confirme que nenhum épico depende de um épico com número maior
</thinking_steps>

<requirements>
### Entregáveis

1. **Um arquivo Markdown por épico**, seguindo a convenção:
   - Caminho: `docs/epics/EP-NNN_nome-em-kebab-case.md`
   - Exemplo: `docs/epics/EP-001_fundacao-e-persistencia.md`
   - **Criar em ordem numérica** (EP-001 primeiro, depois EP-002, etc.)

2. **Um arquivo de roadmap consolidado** em `docs/epics/ROADMAP.md`:
   - Criar **após todos os épicos** para garantir consistência cruzada
   - Deve incluir todas as matrizes de rastreabilidade

### Conteúdo Obrigatório de Cada Épico

Para cada épico, inclua **todos** os campos abaixo:

#### Identificação
- **Código e Nome**: EP-NNN — Nome descritivo
- **Camada**: Fundação | Domínio Core | Serviços de Negócio | Interface & Experiência | Integração & Otimização

#### Contexto e Valor
- **Problema que resolve**: Qual dor ou lacuna específica este épico endereça (referenciar o SRS)
- **Objetivo com valor mensurável**: O que se alcança com a entrega (derivar das capacidades da seção 2.2 do SRS)
- **Alinhamento Estratégico**: Como este épico se conecta às 7 capacidades do produto (seção 2.2 do SRS). Não inventar OKRs ou objetivos externos.

#### Stakeholders
- **Personas Impactadas**: Quais dos 3 perfis da seção 2.3 do SRS (Scrum Master/Tech Lead, Gerente de Projeto, Product Owner) são impactados e como
- **Jornadas / Casos de Uso Afetados**: Quais UC-xxx este épico habilita ou contribui para habilitar. Se um UC depende de múltiplos épicos, indicar "Contribui para UC-xxx (completo em EP-yyy)"

#### Escopo
- **Dentro do Escopo**: Lista de RFs (com ID) e RNFs (com ID) incluídos neste épico
- **Fora do Escopo**: O que explicitamente NÃO faz parte, indicando em qual épico será tratado (ex: "RF-ALOC-* → EP-006")
- **Artefatos Estruturais do SRS incluídos**: Quando aplicável, citar explicitamente se o épico abrange a implementação do schema ER (6.4), máquina de estados (6.5), hierarquia de exceções (7.3), regras implícitas (8.3), ou fluxo de alocação (6.2)

#### Requisitos Detalhados
- **Requisitos Funcionais Principais**: Tabela com ID, Nome e Prioridade (Must/Should/Could Have conforme o SRS)
- **Requisitos Não-Funcionais Críticos**: Tabela com ID, Nome e Métrica-alvo. Para RNFs transversais de mantenibilidade (RNF-MANT-001 a 004), incluí-los com suas métricas concretas **no épico de fundação** e referenciar nos demais com "Conforme estabelecido em EP-001"

#### Validação
- **Critérios de Aceite (Alto Nível)**: Condições verificáveis para considerar o épico entregue. Preferencialmente no formato Dado/Quando/Então.
- **KPIs / Métricas de Sucesso**: Derivar dos RNFs quando houver métricas definidas no SRS (ex: RNF-PERF-001 ≤ 5s). Para épicos sem RNFs mensuráveis, usar critérios qualitativos concretos (ex: "Todas as validações de invariantes cobertas por testes unitários").
- **Plano de Validação**: Como validar a entrega. **Contexto: aplicação desktop single-user sem servidor.** Priorizar nesta ordem:
  1. Testes unitários automatizados (pytest) para lógica de domínio e serviços
  2. Testes de integração para repositórios SQLite
  3. Cenários de teste do SRS (CT-001 a CT-005) — indicar quais CTs são executáveis após este épico
  4. Testes manuais exploratórios para fluxos de UI
  5. Revisão de código para padrões arquiteturais

#### Dependências e Riscos
- **Dependências**: Lista de épicos que devem estar concluídos antes (EP-xxx), com motivo específico
- **Riscos e Premissas**: Tabela com Tipo (Risco/Premissa), Descrição e Mitigação. Riscos devem ser específicos ao projeto (evitar riscos genéricos como "pode haver bugs")
</requirements>

<rules>
### Regras de Decomposição (em ordem de precedência)

Quando duas regras conflitarem, a de menor número prevalece:

1. **Rastreabilidade total**: Todo RF-xxx e RNF-xxx do SRS **deve** ser coberto por exatamente um épico como escopo principal. Todo UC (001-005) deve ser referenciado. Nenhum requisito pode ser omitido.

2. **Sem sobreposição de escopo**: Nenhum RF deve aparecer como escopo principal de mais de um épico. Se um RF é pré-requisito parcial para outro épico, referencie-o como dependência (ex: "Requer RF-STORY-001 implementado em EP-002").

3. **Coesão por bounded context**: Agrupar RFs do mesmo domínio/prefixo no mesmo épico sempre que possível. Não fragmentar um bounded context coeso apenas para atingir uma meta numérica de RFs por épico.

4. **Ordenação por camada**: Organize epics da fundação para o topo: Fundação → Domínio Core → Serviços de Negócio → Interface & Experiência → Integração & Otimização.

5. **Independência pós-dependência**: Cada épico deve ser implementável e testável de forma independente após suas dependências serem satisfeitas. Deve ser possível entregar e validar o épico sem que épicos posteriores existam.

6. **Dimensionamento equilibrado**: Heurística de 3-10 RFs por épico, com duas exceções documentadas:
   - RF-ALOC (13 RFs): Pode ser mantido como épico único OU dividido em no máximo 2 épicos (ex: alocação core + validação/estabilização), desde que a divisão mantenha a coesão algorítmica.
   - RF-DEV (4 RFs): Pode ser agrupado com outro bounded context da mesma camada se a coesão justificar.

7. **NFRs transversais na fundação**: RNF-MANT-001 (cobertura de testes), RNF-MANT-002 (docstrings), RNF-MANT-003 (complexidade ciclomática), RNF-MANT-004 (padronização), RNF-CONF-005 (logging) devem ser **estabelecidos** no épico de fundação com suas ferramentas e configurações. Épicos subsequentes devem referenciar: "Conforme estabelecido em EP-001".

8. **Objetividade**: Conteúdo deve ser específico e rastreável ao SRS. Evitar frases genéricas que se aplicariam a qualquer projeto. Se uma afirmação não pode ser vinculada a um ID ou seção do SRS, ela provavelmente é genérica demais.
</rules>

<output_format>
### Formato de cada arquivo de épico (`docs/epics/EP-NNN_nome.md`):

```md
# EP-NNN — [Nome do Épico]

**Camada:** [Fundação | Domínio Core | Serviços de Negócio | Interface & Experiência | Integração & Otimização]

---

## Problema que Resolve
[Descrição específica ancorada no SRS — qual dor ou lacuna este épico endereça]

## Objetivo (Valor Mensurável)
[O que se alcança com a entrega deste épico, derivado das capacidades da seção 2.2]

## Alinhamento Estratégico
[Conexão com as 7 capacidades do produto definidas na seção 2.2 do SRS]

## Personas Impactadas
| Persona (SRS §2.3) | Impacto |
|---------------------|---------|
| Scrum Master / Tech Lead | [como é afetado] |
| ... | ... |

## Jornadas / Casos de Uso Afetados
- UC-xxx: [nome] — [habilita / contribui para (completo em EP-yyy)]
- CT-xxx: [executável após este épico? Sim/Parcial]

---

## Escopo

### Dentro do Escopo
**Requisitos Funcionais:**
- RF-xxx-yyy: [descrição curta]

**Requisitos Não-Funcionais:**
- RNF-xxx-yyy: [descrição curta]

**Artefatos Estruturais do SRS:**
- [Se aplicável: Schema ER (§6.4), Máquina de Estados (§6.5), Hierarquia de Exceções (§7.3), Regras Implícitas (§8.3), Fluxo de Alocação (§6.2)]

### Fora do Escopo
- [item] → será tratado em EP-xxx

---

## Requisitos Funcionais Principais
| ID | Nome | Prioridade |
|----|------|------------|
| RF-xxx-yyy | ... | Must / Should / Could Have |

## Requisitos Não-Funcionais Críticos
| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-xxx-yyy | ... | [valor do SRS ou "Conforme EP-001"] |

---

## Critérios de Aceite (Alto Nível)
- [ ] [Critério verificável com referência ao SRS]
- [ ] [Critério verificável com referência ao SRS]

## KPIs / Métricas de Sucesso
| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| ... | ... | ... | RNF-xxx ou qualitativo |

## Plano de Validação
| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | [o que cobrir] | RF-xxx |
| Testes Integração | [o que cobrir] | - |
| Cenário de Teste | [qual CT executar] | CT-xxx |
| Teste Manual | [fluxo a validar] | UC-xxx |
| Revisão de Código | [padrão a verificar] | RNF-MANT-xxx |

---

## Dependências
| Épico | Motivo |
|-------|--------|
| EP-xxx | [razão específica — qual artefato ou RF é pré-requisito] |

*Sem dependências* — se for o caso.

## Riscos e Premissas
| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Risco | [específico ao projeto] | [ação concreta] |
| Premissa | [suposição assumida, referenciar SRS §2.5 quando aplicável] | — |
```

---

### Formato do arquivo de roadmap (`docs/epics/ROADMAP.md`):

```md
# Roadmap de Épicos — Backlog Manager v2

## Visão Geral da Sequência

| Ordem | Código | Nome | Camada | Dependências | Marco |
|-------|--------|------|--------|-------------|-------|
| 1 | EP-001 | ... | Fundação | — | |
| 2 | EP-002 | ... | Domínio Core | EP-001 | |
| ... | ... | ... | ... | ... | **MVP** |

## Marco MVP
[Em qual épico o produto atinge o estado mínimo utilizável conforme definição do `<context>`: cadastrar devs, criar/priorizar histórias, definir dependências, calcular cronograma, executar alocação com resultado visível. Justificar.]

## Mapa de Dependências

```text
EP-001 (Fundação)
  └── EP-002 (...)
       ├── EP-003 (...)
       │    └── EP-005 (...)
       └── EP-004 (...)
            └── EP-006 (...)
                 └── EP-007 (...)
[etc.]
```

## Matriz de Rastreabilidade: RF → Épico

| Requisito | Descrição Curta | Épico |
|-----------|----------------|-------|
| RF-STORY-001 | Criar Nova História | EP-xxx |
| RF-STORY-002 | Editar História | EP-xxx |
| ... | ... | ... |
| RF-ALOC-013 | Limites de Segurança | EP-xxx |

> ⚠️ Todos os 42 RFs devem estar listados. Nenhum pode ser omitido.

## Matriz de Rastreabilidade: RNF → Épico(s)

| Requisito | Descrição Curta | Épico(s) |
|-----------|----------------|----------|
| RNF-PERF-001 | Tempo de Alocação ≤ 5s | EP-xxx |
| RNF-MANT-001 | Cobertura ≥ 80% | EP-001 (estabelecido), todos (aplicado) |
| ... | ... | ... |

> ⚠️ Todos os 17 RNFs devem estar listados.

## Matriz de Rastreabilidade: UC → Épico(s)

| Caso de Uso | Nome | Épico(s) que contribuem | Épico onde fica completo |
|-------------|------|------------------------|-------------------------|
| UC-001 | Criar e Priorizar Backlog | EP-xxx, EP-yyy | EP-yyy |
| UC-002 | Alocação Automática com Dependências | EP-xxx, EP-yyy | EP-yyy |
| UC-003 | Detectar e Resolver Deadlock | EP-xxx | EP-xxx |
| UC-004 | Importar Backlog do Excel | EP-xxx | EP-xxx |
| UC-005 | Gerenciar Ondas de Entrega | EP-xxx | EP-xxx |

## Matriz de Rastreabilidade: CT → Épico

| Cenário de Teste | Descrição | Executável após |
|-----------------|-----------|-----------------|
| CT-001 | Backlog Completo 20 Histórias | EP-xxx |
| CT-002 | Detecção de Ciclo em Grafo Grande | EP-xxx |
| CT-003 | Deadlock por Falta de Devs | EP-xxx |
| CT-004 | Feriados em Sequência | EP-xxx |
| CT-005 | Balanceamento com Tamanhos Diferentes | EP-xxx |
```
</output_format>
```
