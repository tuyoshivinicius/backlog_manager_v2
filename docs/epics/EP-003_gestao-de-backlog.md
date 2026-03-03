# EP-003 — Gestão de Backlog

**Camada:** Domínio Core

---

## Problema que Resolve

Com as entidades validadas em EP-002, o sistema precisa das operações CRUD completas para histórias: criar, editar, deletar, listar, duplicar e priorizar. Este épico implementa o StoryService e StoryRepository com todas as operações de negócio para gestão do backlog, incluindo geração automática de IDs no formato COMPONENTE-NNN, atribuição de prioridade inicial, e tratamento de dependências ao deletar.

## Objetivo (Valor Mensurável)

Implementar a capacidade completa de **Gestão de Backlog** (SRS §2.2 item 1):
- CRUD completo de histórias (criar, editar, deletar)
- Duplicação com novo ID e sem dados de alocação
- Listagem ordenada por prioridade
- Alteração de prioridade (mover cima/baixo)
- Atribuição manual de desenvolvedor
- Geração automática de ID no formato COMPONENTE-NNN

## Alinhamento Estratégico

Este épico implementa diretamente a **capacidade 1** do produto: "Gestão de Backlog: CRUD completo de histórias com priorização e duplicação" (§2.2). É o coração do sistema e pré-requisito para todas as funcionalidades de planejamento.

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Uso diário — cria, edita e prioriza histórias para planejamento de sprints |
| Product Owner | Uso semanal — prioriza backlog e mantém histórias atualizadas |
| Gerente de Projeto | Uso semanal — visualiza e acompanha o backlog completo |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — **Habilita** (fluxo principal passos 1-12)
- UC-002: Alocação Automática — Contribui para (pré-condição: histórias existentes)
- UC-004: Importar Backlog do Excel — Contribui para (destino das histórias importadas)
- CT-001: Backlog Completo 20 Histórias — **Executável após este épico** (criação de histórias)

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-STORY-001: Criar Nova História (ID auto-gerado COMPONENTE-NNN, prioridade inicial = max+1)
- RF-STORY-002: Editar História Existente (todos os campos exceto ID)
- RF-STORY-003: Deletar História (remover referências de dependências)
- RF-STORY-004: Duplicar História (novo ID, copiar dados, limpar alocação)
- RF-STORY-005: Listar Histórias do Backlog (ordenadas por prioridade)
- RF-STORY-006: Mover Prioridade (cima/baixo, troca com adjacente)
- RF-STORY-007: Atribuir Desenvolvedor Manualmente (validar existência, permitir desalocar)

**Requisitos Não-Funcionais:**
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- Utiliza schema Story da §6.4
- Aplica regras de §8.3: prioridade inicial = max(existentes) + 1

### Fora do Escopo

- RF-STORY-008 a 010 (validações de entidade) → implementados em EP-002
- RF-DEV-001 a 004 (CRUD de desenvolvedores) → será tratado em EP-004
- RF-FEAT-001 a 005 (CRUD de features) → será tratado em EP-004
- RF-DEP-001 a 004 (gestão de dependências além de limpeza ao deletar) → será tratado em EP-005
- Interface gráfica para backlog → será tratada em EP-008

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-STORY-001 | Criar Nova História | Must Have |
| RF-STORY-002 | Editar História Existente | Must Have |
| RF-STORY-003 | Deletar História | Must Have |
| RF-STORY-004 | Duplicar História | Should Have |
| RF-STORY-005 | Listar Histórias do Backlog | Must Have |
| RF-STORY-006 | Mover Prioridade | Must Have |
| RF-STORY-007 | Atribuir Desenvolvedor Manualmente | Should Have |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |
| RNF-MANT-002 | Docstrings | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomática | Conforme EP-001 |
| RNF-MANT-004 | Padronização de Código | Conforme EP-001 |

---

## Critérios de Aceite (Alto Nível)

- [ ] **Dado** que não existe história com componente "CORE", **Quando** crio história com Componente="CORE", Nome="Login", SP=5, **Então** história é criada com ID="CORE-001" e priority=1
- [ ] **Dado** história CORE-001 com Nome="Login", **Quando** altero Nome para "Autenticação", **Então** historia.nome == "Autenticação" e historia.id == "CORE-001" (imutável)
- [ ] **Dado** história B que depende de A, **Quando** deleto A, **Então** A é removida e B.dependencies não contém mais "A"
- [ ] **Dado** história CORE-001 com SP=5, feature="Auth", dev="Ana", start_date="2026-03-02", **Quando** duplico CORE-001, **Então** nova história CORE-002 tem SP=5, feature="Auth", dev=NULL, start_date=NULL
- [ ] **Dado** 3 histórias com prioridades 1, 2, 3, **Quando** seleciono a de prioridade 3 e movo para cima, **Então** ela passa a ter prioridade 2 e a anterior passa a ter prioridade 3
- [ ] **Dado** desenvolvedor "Dev1" cadastrado, **Quando** atribuo Dev1 a uma história, **Então** historia.developer_id == "Dev1"
- [ ] **Dado** developer_id vazio ou apenas espaços, **Quando** tento atribuir, **Então** ValueError é lançado

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Operações CRUD | Todas funcionando | 100% | RF-STORY-001/002/003 |
| Geração de ID | Formato correto | COMPONENTE-NNN | RF-STORY-001 |
| Integridade de dependências | Limpeza ao deletar | Sem referências órfãs | RF-STORY-003 |
| Duplicação | Campos copiados corretamente | Sem dados de alocação | RF-STORY-004 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | Criar história e verificar ID gerado | RF-STORY-001 |
| Testes Unitários | Editar história preservando ID | RF-STORY-002 |
| Testes Unitários | Deletar história e verificar limpeza de dependências | RF-STORY-003 |
| Testes Unitários | Duplicar história e verificar campos copiados/limpos | RF-STORY-004 |
| Testes Unitários | Listar histórias ordenadas por prioridade | RF-STORY-005 |
| Testes Unitários | Mover prioridade cima/baixo | RF-STORY-006 |
| Testes Unitários | Atribuir/desatribuir desenvolvedor | RF-STORY-007 |
| Testes Integração | Persistência de todas as operações em SQLite | RNF-CONF-003/004 |
| Cenário de Teste | CT-001 parcial — criação de 20 histórias | CT-001 |
| Revisão de Código | Validar separação Service/Repository | §6.1 |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Schema da tabela Story e Story_Dependency; repositórios base |
| EP-002 | Entidade Story com validações (RF-STORY-008/009/010 implementados) |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | Sequência de IDs é única por componente | Usar query para encontrar próximo número disponível |
| Premissa | Prioridades são sempre contíguas (1, 2, 3...) | Implementar reordenação se houver gaps |
| Risco | Deletar história com muitas dependências pode ser lento | Usar transação única; índice em Story_Dependency |
| Risco | Duplicação de história em feature com muitas histórias pode gerar ID conflitante | Validar unicidade antes de confirmar |
| Premissa | Developer pode ser atribuído mesmo que não exista (por ora) | RF-STORY-007 menciona validar existência — depende de EP-004 para validação completa |
