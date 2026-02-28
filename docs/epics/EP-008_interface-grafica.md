# EP-008 — Interface Gráfica

**Camada:** Interface & Experiência

**Marco:** MVP (Minimum Viable Product)

---

## Problema que Resolve

Todos os serviços de negócio estão implementados (EP-001 a EP-007), mas não há forma de o usuário interagir com o sistema. Este épico implementa a interface gráfica completa em PySide6/Qt: MainWindow com lista de backlog, diálogos para CRUD, botões de ação, painel de métricas, e todos os atalhos de teclado. Ao final deste épico, o produto atinge o estado de **MVP**.

## Objetivo (Valor Mensurável)

Implementar a interface gráfica que permite ao usuário:
- Visualizar e gerenciar o backlog completo
- Cadastrar e manter desenvolvedores e features
- Definir dependências entre histórias
- Configurar velocidade e data de início
- Executar alocação automática com um clique
- Visualizar resultado da alocação e métricas
- Navegar por teclado com atalhos definidos

**Marco MVP alcançado:** Usuário consegue (a) cadastrar desenvolvedores, (b) criar e priorizar histórias, (c) definir dependências, (d) calcular cronograma e (e) executar alocação automática com resultado visível.

## Alinhamento Estratégico

Este épico integra todas as 6 capacidades core do produto em uma interface usável:
- **Capacidade 1**: Gestão de Backlog (tela principal)
- **Capacidade 2**: Gestão de Features (diálogo de features)
- **Capacidade 3**: Gestão de Desenvolvedores (diálogo de desenvolvedores)
- **Capacidade 4**: Gestão de Dependências (painel de dependências)
- **Capacidade 5**: Cálculo de Cronograma (configuração e visualização)
- **Capacidade 6**: Alocação Automática (botão e painel de métricas)

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Uso diário — interface principal para todas as operações |
| Gerente de Projeto | Uso semanal — visualização de cronograma e métricas |
| Product Owner | Uso semanal — priorização de backlog e organização de features |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — **Completo** (fluxo principal na UI)
- UC-002: Alocação Automática com Dependências — **Completo** (fluxo principal na UI)
- UC-003: Detectar e Resolver Deadlock — **Completo** (visualização de warnings)
- UC-005: Gerenciar Ondas de Entrega — **Completo** (fluxo principal na UI)
- CT-001 a CT-005: **Todos executáveis** (via interface gráfica)

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- Nenhum RF novo — épico de integração de UI para RFs já implementados

**Requisitos Não-Funcionais:**
- RNF-USAB-001: Plataforma Windows 10/11
- RNF-USAB-002: Resolução mínima 1366x768
- RNF-USAB-003: Acessibilidade básica (contraste, navegação por teclado, tooltips)
- RNF-USAB-004: Curva de aprendizado ≤ 15 minutos
- RNF-PERF-002: Responsividade ≤ 100ms para CRUD, ≤ 500ms para recálculo
- RNF-PERF-004: Tempo de inicialização ≤ 3s
- RNF-CONF-001: Disponibilidade 99% (sem crashes)
- RNF-CONF-002: Recuperação de erros (mensagens claras, sem crash)

**Artefatos Estruturais do SRS:**
- Arquitetura em camadas (§6.1): Camada de Apresentação (UI) completa
- Atalhos de teclado (Apêndice B): Todos os atalhos implementados

### Fora do Escopo

- UC-004: Importar Backlog do Excel → será tratado em EP-009
- Integração Excel (Import/Export) → será tratado em EP-009

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Nenhum RF novo — integração de UI | — |

**Funcionalidades de UI a implementar:**

| Componente | Descrição | RFs Relacionados |
|------------|-----------|------------------|
| MainWindow | Janela principal com lista de backlog | RF-STORY-005 |
| StoryDialog | Diálogo para criar/editar história | RF-STORY-001/002 |
| StoryTable | Tabela com colunas: ID, Nome, SP, Status, Feature, Dev, Datas | RF-STORY-005 |
| PriorityButtons | Botões mover cima/baixo | RF-STORY-006 |
| DeveloperDialog | Diálogo para CRUD de desenvolvedores | RF-DEV-001/002/003/004 |
| FeatureDialog | Diálogo para CRUD de features | RF-FEAT-001/002/003 |
| DependencyPanel | Painel para adicionar/remover dependências | RF-DEP-001/002 |
| AllocationButton | Botão "Alocar Automaticamente" | RF-ALOC-001 |
| MetricsPanel | Painel com métricas de alocação | RF-ALOC-011 |
| WarningsPanel | Painel com DeadlockWarning, IdlenessWarning | RF-ALOC-007/008 |
| ConfigPanel | Configuração de velocidade, data início, max_idle_days | RF-SCHED-001, RF-ALOC-009 |

## Requisitos Não-Funcionais Críticos

| ID | Nome | Métrica-alvo |
|----|------|-------------|
| RNF-USAB-001 | Plataforma | Windows 10 (1903+), Windows 11 |
| RNF-USAB-002 | Resolução Mínima | 1366x768 sem cortes |
| RNF-USAB-003 | Acessibilidade | Contraste 4.5:1, navegação Tab, tooltips |
| RNF-USAB-004 | Curva de Aprendizado | ≤ 15 minutos primeira utilização |
| RNF-PERF-002 | Responsividade UI | ≤ 100ms CRUD, ≤ 500ms recálculo |
| RNF-PERF-004 | Tempo de Startup | ≤ 3s cold start |
| RNF-CONF-001 | Disponibilidade | 99% sessões sem crash |
| RNF-CONF-002 | Recuperação de Erros | Mensagens claras, sem crash |

---

## Critérios de Aceite (Alto Nível)

### MainWindow e Backlog
- [ ] **Dado** backlog com 10 histórias, **Quando** abro o sistema, **Então** vejo tabela com todas as histórias ordenadas por prioridade
- [ ] **Dado** resolução 1366x768, **Quando** abro o sistema, **Então** interface é utilizável sem cortes ou scrolls excessivos

### CRUD via Diálogos
- [ ] **Dado** botão "Nova História", **Quando** clico, **Então** diálogo StoryDialog abre com campos para Componente, Nome, SP, Feature
- [ ] **Dado** diálogo StoryDialog com dados válidos, **Quando** clico "Salvar", **Então** história é criada e aparece na tabela
- [ ] **Dado** história selecionada, **Quando** pressiono Enter ou F2, **Então** diálogo de edição abre

### Alocação
- [ ] **Dado** backlog com histórias e desenvolvedores cadastrados, **Quando** clico "Alocar Automaticamente", **Então** alocação é executada e resultados aparecem na tabela
- [ ] **Dado** alocação completa, **Quando** visualizo métricas, **Então** vejo tempo, histórias alocadas, deadlocks detectados

### Atalhos de Teclado
- [ ] **Dado** foco na aplicação, **Quando** pressiono Ctrl+N, **Então** diálogo de nova história abre
- [ ] **Dado** história selecionada, **Quando** pressiono Alt+Up, **Então** prioridade aumenta (move para cima)
- [ ] **Dado** foco na aplicação, **Quando** pressiono Ctrl+Shift+A, **Então** alocação automática é executada

### Acessibilidade
- [ ] **Dado** uso de Tab/Shift+Tab, **Quando** navego pela interface, **Então** posso acessar todos os elementos interativos
- [ ] **Dado** ícones sem texto, **Quando** passo mouse, **Então** tooltip descritivo aparece

### Performance
- [ ] **Dado** cold start, **Quando** abro aplicação, **Então** interface está pronta em ≤ 3 segundos
- [ ] **Dado** clique em "Salvar" no diálogo, **Quando** espero resposta, **Então** operação completa em ≤ 100ms

## KPIs / Métricas de Sucesso

| KPI | Métrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Startup time | Segundos | ≤ 3s | RNF-PERF-004 |
| Latência CRUD | Milissegundos | ≤ 100ms | RNF-PERF-002 |
| Latência recálculo | Milissegundos | ≤ 500ms | RNF-PERF-002 |
| Crash rate | % sessões | < 1% | RNF-CONF-001 |
| Tempo de aprendizado | Minutos | ≤ 15 | RNF-USAB-004 |

## Plano de Validação

| Tipo | Descrição | Referência SRS |
|------|-----------|----------------|
| Testes Manuais | Abrir aplicação e verificar startup time | RNF-PERF-004 |
| Testes Manuais | CRUD de história via interface | RF-STORY-001/002/003 |
| Testes Manuais | CRUD de desenvolvedor via interface | RF-DEV-001/002/003 |
| Testes Manuais | CRUD de feature via interface | RF-FEAT-001/002/003 |
| Testes Manuais | Adicionar/remover dependências | RF-DEP-001/002 |
| Testes Manuais | Executar alocação e verificar resultado | RF-ALOC-001 |
| Testes Manuais | Verificar todos os atalhos de teclado | Apêndice B |
| Testes Manuais | Testar em resolução 1366x768 | RNF-USAB-002 |
| Testes Manuais | Testar navegação por Tab | RNF-USAB-003 |
| Teste de Usabilidade | 3 usuários novos completam fluxo MVP | RNF-USAB-004 |
| Cenário de Teste | CT-001 a CT-005 via interface | CT-001 a CT-005 |
| Revisão de Código | Validar separação UI/Services | §6.1 |

---

## Dependências

| Épico | Motivo |
|-------|--------|
| EP-001 | Infraestrutura de persistência e logging |
| EP-002 | Entidades para exibição na UI |
| EP-003 | StoryService para operações de backlog |
| EP-004 | DeveloperService e FeatureService para diálogos |
| EP-005 | DependencyService para painel de dependências |
| EP-006 | SchedulingService para cálculo de datas |
| EP-007 | AllocationService para botão de alocação e métricas |

## Riscos e Premissas

| Tipo | Descrição | Mitigação |
|------|-----------|-----------|
| Premissa | PySide6 6.6.1+ funciona corretamente em Windows 10/11 | Testar em ambas as versões durante desenvolvimento |
| Risco | UI pode não ser responsiva durante operações longas | Usar QThread para operações de alocação |
| Risco | Resolução 1366x768 pode ser restritiva para muitos dados | Usar scrollbars e layout responsivo |
| Premissa | Atalhos de teclado não conflitam com atalhos do sistema | Usar combinações não padrão (Alt+Up, Ctrl+Shift+A) |
| Risco | Teste de usabilidade pode revelar problemas de UX | Iterar baseado em feedback; épico pode ter tasks de refinamento |
| Premissa | Interface em português brasileiro conforme §2.4 | Todos os textos e mensagens em PT-BR |
