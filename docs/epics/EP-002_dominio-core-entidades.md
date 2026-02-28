# EP-002 — Domínio Core: Entidades e Validações

**Camada:** Domínio Core

---

## Problema que Resolve

Com a infraestrutura estabelecida em EP-001, o sistema precisa das entidades de domínio que encapsulam as regras de negócio fundamentais. Este épico implementa as classes Story, Developer e Feature com todas as validações de invariantes (§8.3), a máquina de estados de Story.status (§6.5), e as validações de campos obrigatórios (RF-STORY-008, 009, 010). Sem entidades robustas, os serviços e repositórios não teriam objetos válidos para manipular.

## Objetivo (Valor Mensurável)

Implementar as 3 entidades de domínio (Story, Developer, Feature) com validações completas, garantindo que:
- Nenhuma instância inválida possa ser criada (construtor valida invariantes)
- Story Points aceita apenas valores Fibonacci válidos {3, 5, 8, 13}
- Status segue a máquina de estados definida com valores sem acento
- Auto-dependência é rejeitada no momento da criação
- 100% das validações cobertas por testes unitários

## Alinhamento Estratégico

Este épico é pré-requisito direto para:
- **Gestão de Backlog** (capacidade 1): Entidade Story com validações
- **Gestão de Features** (capacidade 2): Entidade Feature com wave validation
- **Gestão de Desenvolvedores** (capacidade 3): Entidade Developer
- **Gestão de Dependências** (capacidade 4): Validação de auto-dependência em Story

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Garantia de que histórias terão dados consistentes (SP válidos, status correto) |
| Product Owner | Confiança de que priorização e features serão persistidas corretamente |
| Gerente de Projeto | Segurança de que dados de desenvolvedores são íntegros |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — Contribui para (validações de Story)
- UC-002: Alocação Automática — Contribui para (validações de developer_id)
- UC-003: Detectar e Resolver Deadlock — Contribui para (validação de auto-dependência)
- UC-005: Gerenciar Ondas de Entrega — Contribui para (validação de wave em Feature)
- CT-001: Parcial — entidades testáveis
- CT-002: Parcial — validação de auto-dependência

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-STORY-008: Validar Story Points (valores {3, 5, 8, 13})
- RF-STORY-009: Gerenciar Status (5 estados: BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)
- RF-STORY-010: Validar Invariantes da História (ID, component, nome não vazios; prioridade ≥ 0; duration ≥ 0; sem auto-dependência)

**Requisitos Não-Funcionais:**
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- Máquina de Estados (§6.5): Implementação dos 5 estados com transições livres
- Regras Implícitas (§8.3): story_points ∈ {3,5,8,13}, wave > 0, prioridade inicial = max+1, duração mínima = 1
- Convenções de Nomenclatura (§8.2): ID no formato COMPONENTE-NNN, status em MAIÚSCULAS sem acento

### Fora do Escopo

- RF-STORY-001 a 007 (CRUD de histórias) → será tratado em EP-003
- RF-DEV-001 a 004 (CRUD de desenvolvedores) → será tratado em EP-004
- RF-FEAT-001 a 005 (CRUD de features) → será tratado em EP-004
- RF-DEP-001 a 004 (gestão de dependências) → será tratado em EP-005
- Persistência das entidades (repositórios) → já estabelecida em EP-001, utilizada em EP-003/004

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-STORY-008 | Validar Story Points | Must Have |
| RF-STORY-009 | Gerenciar Status da História | Must Have |
| RF-STORY-010 | Validar Invariantes da História | Must Have |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | 100% para módulo de entidades |
| RNF-MANT-002 | Docstrings | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomática | Conforme EP-001 |
| RNF-MANT-004 | Padronização de Código | Conforme EP-001 |

---

## Critérios de Aceite (Alto Nível)

- [ ] **Dado** valores de Story Points fora de {3,5,8,13}, **Quando** crio uma Story, **Então** ValueError é lançado com mensagem "Story Points deve ser 3, 5, 8 ou 13"
- [ ] **Dado** um ID vazio ou None, **Quando** crio uma Story, **Então** ValueError é lançado com mensagem "ID da historia nao pode ser vazio"
- [ ] **Dado** uma Story com ID "X", **Quando** adiciono "X" como dependência dela mesma, **Então** ValueError é lançado com mensagem "Historia nao pode depender de si mesma"
- [ ] **Dado** os 5 status válidos (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO), **Quando** atribuo qualquer um deles, **Então** a atribuição é aceita sem erros
- [ ] **Dado** developer_id como string vazia ou apenas espaços, **Quando** atribuo a uma Story, **Então** ValueError é lançado conforme RF-STORY-007
- [ ] **Dado** uma Feature com wave ≤ 0, **Quando** crio a Feature, **Então** erro de validação é lançado

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Cobertura de validações | % de invariantes com teste | 100% | RF-STORY-008/009/010 |
| Rejeição de dados inválidos | Testes de boundary | Todos passando | §8.3 |
| Consistência de estados | Transições válidas | 5 estados funcionais | §6.5 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | Testar criação de Story com todos os campos válidos | RF-STORY-010 |
| Testes Unitários | Testar rejeição de SP inválidos (1, 2, 4, 7, 20) | RF-STORY-008 |
| Testes Unitários | Testar todos os 5 status e transições | RF-STORY-009, §6.5 |
| Testes Unitários | Testar rejeição de ID/nome/component vazios | RF-STORY-010 |
| Testes Unitários | Testar rejeição de auto-dependência | RF-STORY-010 |
| Testes Unitários | Testar Developer com nome vazio | RF-DEV-001 implícito |
| Testes Unitários | Testar Feature com wave inválida (0, -1) | RF-FEAT-001 |
| Revisão de Código | Validar encapsulamento e imutabilidade onde aplicável | RNF-MANT-* |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Schema do banco com constraints necessárias; hierarquia de exceções (ValueError para validações) |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | Validações são síncronas e executadas no construtor | Documentar que entidades são sempre válidas após criação |
| Premissa | Status utiliza valores internos sem acento (§6.5) | Usar Enum ou constantes para garantir valores corretos |
| Risco | Validações muito restritivas podem dificultar import de dados legados | Criar factory methods com validação relaxada para import, se necessário (documentar em EP-009) |
| Risco | Mudança nos valores válidos de SP pode quebrar dados existentes | SP é definido no SRS como fixo {3,5,8,13}; não há plano de alteração |
