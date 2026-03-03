# EP-004 — Gestão de Recursos: Desenvolvedores e Features

**Camada:** Domínio Core

---

## Problema que Resolve

O sistema precisa gerenciar dois tipos de recursos essenciais: **desenvolvedores** (quem executa as histórias) e **features** (como as histórias são organizadas em ondas de entrega). Este épico implementa o CRUD completo para ambas as entidades, incluindo a lógica de associação de histórias a features, validação de ondas únicas, e tratamento correto ao deletar recursos com dependências.

## Objetivo (Valor Mensurável)

Implementar as capacidades de **Gestão de Desenvolvedores** (§2.2 item 3) e **Gestão de Features** (§2.2 item 2):
- CRUD completo de desenvolvedores (cadastrar, editar, deletar, listar)
- CRUD completo de features com ondas de entrega
- Validação de unicidade de ondas (wave)
- Associação de histórias a features
- Proteção contra deleção de feature com histórias associadas
- Desalocação automática de histórias ao deletar desenvolvedor

## Alinhamento Estratégico

Este épico implementa diretamente:
- **Capacidade 2**: "Gestão de Features: Organização de histórias em ondas de entrega"
- **Capacidade 3**: "Gestão de Desenvolvedores: Cadastro e manutenção do time"

Também é pré-requisito para:
- **Capacidade 6**: Alocação Automática (requer desenvolvedores cadastrados)
- **Capacidade 5**: Cálculo de Cronograma (features definem ondas)

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Cadastra e mantém o time de desenvolvedores; organiza features em ondas |
| Gerente de Projeto | Visualiza alocação de recursos e organização de entregas |
| Product Owner | Define features e prioriza ondas de entrega |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — Contribui para (pré-condição: desenvolvedor cadastrado; associação a feature)
- UC-002: Alocação Automática — Contribui para (pré-condição: desenvolvedores cadastrados)
- UC-005: Gerenciar Ondas de Entrega — **Habilita** (fluxo principal completo)
- CT-001: Backlog Completo 20 Histórias — Contribui para (setup de desenvolvedores)
- CT-005: Balanceamento com Tamanhos Diferentes — Contribui para (setup de desenvolvedores)

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-DEV-001: Cadastrar Novo Desenvolvedor (nome obrigatório, ID auto-gerado)
- RF-DEV-002: Editar Desenvolvedor (alterar nome)
- RF-DEV-003: Deletar Desenvolvedor (desalocar histórias antes)
- RF-DEV-004: Listar Desenvolvedores
- RF-FEAT-001: Criar Nova Feature (nome único, onda > 0, onda única)
- RF-FEAT-002: Editar Feature (validar unicidade de nome e onda)
- RF-FEAT-003: Deletar Feature (somente se sem histórias)
- RF-FEAT-004: Associar Histórias a Features (1 história : 1 feature, história sem feature → wave=0)
- RF-FEAT-005: Validar Onda Única (rejeitar duplicata)

**Requisitos Não-Funcionais:**
- RNF-MANT-001 a 004: Conforme estabelecido em EP-001

**Artefatos Estruturais do SRS:**
- Utiliza schema Developer e Feature da §6.4
- Aplica regras de §8.3: onda mínima = 1, história sem feature → wave = 0

### Fora do Escopo

- RF-STORY-* → implementados em EP-002/EP-003
- RF-DEP-* → será tratado em EP-005
- RF-SCHED-* → será tratado em EP-006
- RF-ALOC-* → será tratado em EP-007
- Interface gráfica para desenvolvedores e features → será tratada em EP-008

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-DEV-001 | Cadastrar Novo Desenvolvedor | Must Have |
| RF-DEV-002 | Editar Desenvolvedor | Must Have |
| RF-DEV-003 | Deletar Desenvolvedor | Must Have |
| RF-DEV-004 | Listar Desenvolvedores | Must Have |
| RF-FEAT-001 | Criar Nova Feature | Must Have |
| RF-FEAT-002 | Editar Feature | Must Have |
| RF-FEAT-003 | Deletar Feature | Must Have |
| RF-FEAT-004 | Associar Histórias a Features | Must Have |
| RF-FEAT-005 | Validar Onda Única | Must Have |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-MANT-001 | Cobertura de Testes | Conforme EP-001 |
| RNF-MANT-002 | Docstrings | Conforme EP-001 |
| RNF-MANT-003 | Complexidade Ciclomática | Conforme EP-001 |
| RNF-MANT-004 | Padronização de Código | Conforme EP-001 |

---

## Critérios de Aceite (Alto Nível)

### Desenvolvedores
- [ ] **Dado** nome "Ana", **Quando** cadastro desenvolvedor, **Então** desenvolvedor é criado com ID único e nome="Ana"
- [ ] **Dado** desenvolvedor com ID=1 e nome="Ana", **Quando** edito nome para "Ana Silva", **Então** nome é atualizado mantendo ID
- [ ] **Dado** desenvolvedor "Ana" com 3 histórias alocadas, **Quando** deleto Ana, **Então** as 3 histórias têm developer_id=NULL
- [ ] **Dado** 3 desenvolvedores cadastrados, **Quando** listo, **Então** retorna lista com os 3

### Features
- [ ] **Dado** Feature "Login" com onda=1, **Quando** crio Feature "Cadastro" com onda=1, **Então** DuplicateWaveException é lançada
- [ ] **Dado** Feature "Core" com 5 histórias, **Quando** tento deletar, **Então** FeatureHasStoriesException é lançada
- [ ] **Dado** história sem feature associada, **Quando** consulto sua onda, **Então** wave=0
- [ ] **Dado** Feature "Auth" (onda=1), **Quando** associo história H1 a ela, **Então** H1.feature_id aponta para "Auth" e H1 herda wave=1

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| CRUD Desenvolvedores | Todas operações | 100% funcionando | RF-DEV-001 a 004 |
| CRUD Features | Todas operações | 100% funcionando | RF-FEAT-001 a 005 |
| Validação de onda | Duplicatas rejeitadas | 100% | RF-FEAT-005 |
| Integridade referencial | FK enforced | Sem violações | §6.4 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Unitários | CRUD completo de Developer | RF-DEV-001 a 004 |
| Testes Unitários | CRUD completo de Feature | RF-FEAT-001 a 005 |
| Testes Unitários | Validar DuplicateWaveException | RF-FEAT-001/005 |
| Testes Unitários | Validar FeatureHasStoriesException | RF-FEAT-003 |
| Testes Unitários | Desalocação de histórias ao deletar dev | RF-DEV-003 |
| Testes Unitários | Associar/desassociar história de feature | RF-FEAT-004 |
| Testes Unitários | Wave=0 para história sem feature | RF-FEAT-004, §8.3 |
| Testes Integração | Persistência em SQLite | RNF-CONF-003/004 |
| Cenário de Teste | UC-005 completo | UC-005 |
| Revisão de Código | Validar separação Service/Repository | §6.1 |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Schema das tabelas Developer e Feature; exceções DuplicateWaveException e FeatureHasStoriesException |
| EP-002 | Entidade Feature com validação de wave > 0 |
| EP-003 | StoryRepository para associação de histórias a features e desalocação de developer |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | Ondas são números inteiros positivos sequenciais | Validar wave > 0 na criação |
| Premissa | Uma feature pode ter múltiplas histórias, mas uma história só pode ter uma feature | Constraint UNIQUE no schema garante isso |
| Risco | Deletar desenvolvedor com muitas histórias pode ser lento | Usar transação única; batch update |
| Risco | Renomear feature pode causar confusão em relatórios históricos | Fora do escopo — sistema não mantém histórico de mudanças |
| Premissa | Ondas não precisam ser contíguas (pode existir onda 1 e 3 sem onda 2) | Permitir gaps; alocação processa ondas existentes em ordem |
