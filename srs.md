# Software Requirements Specification (SRS)

## Backlog Manager

## 1. Introducao

### 1.1 Proposito

Este documento especifica os requisitos de software do **Backlog Manager**, um sistema desktop para planejamento inteligente de tarefas e gestao de backlog de desenvolvimento de software. O documento serve como contrato entre stakeholders e equipe de desenvolvimento, definindo o que o sistema deve fazer e suas restricoes operacionais.

### 1.2 Escopo

O **Backlog Manager** e uma aplicacao desktop standalone que permite:

- Gestao completa de User Stories (criar, editar, deletar, priorizar)
- Organizacao de historias em Features com ondas de entrega
- Cadastro e gerenciamento de desenvolvedores
- Gestao de dependencias entre historias com deteccao de ciclos
- Calculo automatico de cronogramas considerando dias uteis e feriados brasileiros
- Alocacao automatica de desenvolvedores
- Importacao e exportacao de dados via arquivos Excel

**Fora do escopo:**
- Integracao com ferramentas externas (Jira, Azure DevOps, etc.)
- Funcionalidades multi-usuario ou colaborativas
- Hospedagem em nuvem ou acesso remoto
- Notificacoes por email ou push


### 1.3 Definicoes, Acronimos e Abreviacoes

| Termo | Definicao |
|-------|-----------|
| **User Story** | Unidade de trabalho que descreve uma funcionalidade do ponto de vista do usuario |
| **Story Point (SP)** | Unidade de medida de complexidade/esforco usando escala Fibonacci (3, 5, 8, 13) |
| **Sprint** | Periodo fixo de trabalho (tipicamente 2 semanas) |
| **Backlog** | Lista priorizada de historias a serem desenvolvidas |
| **Feature** | Agrupamento de historias relacionadas |
| **Onda (Wave)** | Sequencia de entrega de features; onda 1 e entregue antes da onda 2 |
| **Velocidade** | Quantidade de Story Points que o time entrega por sprint |
| **Dependencia** | Relacao onde uma historia so pode iniciar apos outra terminar |
| **Alocacao** | Atribuicao de um desenvolvedor a uma historia |
| **Dia util** | Segunda a sexta-feira, excluindo feriados nacionais |
| **Deadlock** | Situacao onde nenhuma historia pode ser alocada |
| **Ociosidade** | Periodo sem trabalho alocado para um desenvolvedor |


## 2. Descricao Geral

### 2.1 Perspectiva do Produto

O Backlog Manager e uma aplicacao desktop independente (standalone) desenvolvida em Python com interface grafica PySide6/Qt. O sistema opera localmente, sem necessidade de conexao com internet ou servidores externos.

### 2.2 Funcoes do Produto

O sistema oferece as seguintes capacidades principais:

1. **Gestao de Backlog**: CRUD completo de historias com priorizacao e duplicacao
2. **Gestao de Features**: Organizacao de historias em ondas de entrega
3. **Gestao de Desenvolvedores**: Cadastro e manutencao do time
4. **Gestao de Dependencias**: Definicao de pre-requisitos entre historias
5. **Calculo de Cronograma**: Datas automaticas baseadas em velocidade e dependencias
6. **Alocacao Automatica**: Distribuicao inteligente de trabalho entre desenvolvedores
7. **Integracao Excel**: Import/export para interoperabilidade

### 2.3 Caracteristicas dos Usuarios

| Perfil | Descricao | Frequencia de Uso |
|--------|-----------|-------------------|
| **Scrum Master / Tech Lead** | Responsavel por planejar sprints e distribuir trabalho | Diaria |
| **Gerente de Projeto** | Acompanha cronograma e alocacao de recursos | Semanal |
| **Product Owner** | Prioriza backlog e define features | Semanal |

**Requisitos de conhecimento:**
- Familiaridade com metodologias ageis (Scrum/Kanban)
- Conhecimento basico de planejamento de projetos
- Nao requer conhecimento tecnico de programacao


### 2.4 Restricoes

| Tipo | Restricao |
|------|-----------|
| **Tecnologica** | Python 3.11+, PySide6 6.6.1+, SQLite |
| **Plataforma** | Windows (primario), sem suporte para Linux/macOS |
| **Idioma** | Interface em Portugues (Brasil) |
| **Localizacao** | Feriados nacionais brasileiros hardcoded |
| **Persistencia** | Banco de dados local (arquivo unico) |
| **Usuarios** | Single-user (sem controle de acesso) |

### 2.5 Suposicoes e Dependencias

**Suposicoes:**
- O usuario possui conhecimento basico de planejamento agil
- O time trabalha em horario comercial (segunda a sexta)
- Story Points seguem escala Fibonacci padrao
- Uma historia e executada por um unico desenvolvedor

**Dependencias:**
- Python 3.11 ou superior instalado
- Bibliotecas: PySide6, openpyxl
- Sistema operacional com suporte a GUI

---


## 3. Requisitos Funcionais

### 3.1 RF-STORY - Gestao de Historias

#### RF-STORY-001: Criar Nova Historia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-001 |
| **Nome** | Criar Nova Historia |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir criar uma nova historia com ID auto-gerado no formato COMPONENTE-NNN (ex: CORE-001, UI-042) |
| **Entrada** | Componente, Nome, Story Points, Feature (opcional) |
| **Saida** | Historia criada com ID unico e prioridade definida |
| **Regras** | - ID gerado automaticamente baseado no componente<br>- Prioridade inicial = max(priority) + 1<br>- Story Points deve ser valor valido (3, 5, 8, 13)<br>- Se ID nao informado no import, gera formato `US-NNN` |
| **Excecoes** | Dados invalidos: exibir mensagem de erro |
| **Criterio de Aceite** | **Dado** que nao existe historia com componente "CORE",<br>**Quando** crio historia com Componente="CORE", Nome="Login", SP=5,<br>**Entao** historia e criada com ID="CORE-001" e priority=1 |

#### RF-STORY-002: Editar Historia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-002 |
| **Nome** | Editar Historia Existente |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir editar todos os campos de uma historia exceto o ID |
| **Entrada** | ID da historia, novos valores dos campos |
| **Saida** | Historia atualizada |
| **Regras** | - ID e imutavel<br>- Validar Story Points<br>- Validar dependencias |
| **Criterio de Aceite** | **Dado** historia CORE-001 com Nome="Login",<br>**Quando** altero Nome para "Autenticacao",<br>**Entao** historia.nome == "Autenticacao" e historia.id == "CORE-001" (imutavel) |

#### RF-STORY-003: Deletar Historia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-003 |
| **Nome** | Deletar Historia |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir deletar uma historia do backlog |
| **Entrada** | ID da historia |
| **Saida** | Historia removida do sistema |
| **Regras** | - Remover referencias de dependencias em outras historias<br>- Confirmar antes de deletar |
| **Criterio de Aceite** | **Dado** historia B que depende de A,<br>**Quando** deleto A,<br>**Entao** A e removida e B.dependencies nao contem mais "A" |

#### RF-STORY-004: Duplicar Historia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-004 |
| **Nome** | Duplicar Historia |
| **Prioridade** | Should Have |
| **Descricao** | O sistema deve permitir criar copia de uma historia com novo ID |
| **Entrada** | ID da historia original |
| **Saida** | Nova historia com mesmo conteudo, novo ID e sem datas calculadas |
| **Regras** | - Novo ID auto-gerado<br>- Copiar: componente, nome, story points, status, feature<br>- Nao copiar: developer_id, start_date, end_date, duration |
| **Criterio de Aceite** | **Dado** historia CORE-001 com SP=5, feature="Auth", dev="Ana", start_date="2026-03-02",<br>**Quando** duplico CORE-001,<br>**Entao** nova historia CORE-002 tem SP=5, feature="Auth", dev=NULL, start_date=NULL |

#### RF-STORY-005: Listar Historias

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-005 |
| **Nome** | Listar Historias do Backlog |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve exibir todas as historias ordenadas por prioridade |
| **Entrada** | Nenhuma |
| **Saida** | Lista de historias com todos os campos visiveis |
| **Regras** | - Ordenar por prioridade (menor = mais prioritario)<br>- Exibir: ID, Nome, SP, Status, Feature, Dev, Datas |

#### RF-STORY-006: Alterar Prioridade

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-006 |
| **Nome** | Mover Prioridade |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir aumentar ou diminuir a prioridade de uma historia |
| **Entrada** | ID da historia, direcao (cima/baixo) |
| **Saida** | Prioridades reorganizadas |
| **Regras** | - Mover para cima: trocar com historia de prioridade imediatamente menor<br>- Mover para baixo: trocar com historia de prioridade imediatamente maior |

#### RF-STORY-007: Atribuir Desenvolvedor Manualmente

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-007 |
| **Nome** | Atribuir Desenvolvedor |
| **Prioridade** | Should Have |
| **Descricao** | O sistema deve permitir atribuir manualmente um desenvolvedor a uma historia |
| **Entrada** | ID da historia, ID do desenvolvedor |
| **Saida** | Historia com desenvolvedor alocado |
| **Regras** | - Desenvolvedor deve existir no cadastro<br>- ID do desenvolvedor nao pode ser vazio ou apenas espacos<br>- Permitir desalocar (developer_id = null) |
| **Validacao** | `ValueError` se developer_id for string vazia ou so espacos |

#### RF-STORY-008: Validar Story Points

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-008 |
| **Nome** | Validar Story Points |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve aceitar apenas valores Fibonacci validos para Story Points |
| **Valores Validos** | 3 (P), 5 (M), 8 (G), 13 (GG) |
| **Regras** | - Rejeitar valores fora da escala<br>- Exibir mensagem de erro clara |

#### RF-STORY-009: Gerenciar Status

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-009 |
| **Nome** | Gerenciar Status da Historia |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir alterar o status de uma historia |
| **Estados Internos** | `BACKLOG`, `EXECUCAO`, `TESTES`, `CONCLUIDO`, `IMPEDIDO` |
| **Exibicao UI** | BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO |
| **Regras** | - Qualquer transicao e permitida<br>- Status padrao: BACKLOG<br>- **IMPORTANTE**: Valores internos SEM acentos |

#### RF-STORY-010: Validar Campos da Entidade

| Atributo | Valor |
|----------|-------|
| **ID** | RF-STORY-010 |
| **Nome** | Validar Invariantes da Historia |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve validar campos obrigatorios no construtor da entidade |
| **Validacoes** | - ID nao pode ser vazio<br>- Component nao pode ser vazio<br>- Nome nao pode ser vazio<br>- Prioridade nao pode ser negativa<br>- Duration nao pode ser negativo<br>- Historia nao pode depender de si mesma |
| **Excecao** | `ValueError` com mensagem descritiva |

---

### 3.2 RF-DEV - Gestao de Desenvolvedores

#### RF-DEV-001: Cadastrar Desenvolvedor

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEV-001 |
| **Nome** | Cadastrar Novo Desenvolvedor |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir cadastrar um novo desenvolvedor |
| **Entrada** | Nome do desenvolvedor |
| **Saida** | Desenvolvedor criado com ID unico |
| **Regras** | - Nome obrigatorio e nao vazio<br>- ID gerado automaticamente |

#### RF-DEV-002: Editar Desenvolvedor

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEV-002 |
| **Nome** | Editar Desenvolvedor |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir editar o nome de um desenvolvedor |
| **Entrada** | ID do desenvolvedor, novo nome |
| **Saida** | Desenvolvedor atualizado |

#### RF-DEV-003: Deletar Desenvolvedor

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEV-003 |
| **Nome** | Deletar Desenvolvedor |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir remover um desenvolvedor do cadastro |
| **Entrada** | ID do desenvolvedor |
| **Saida** | Desenvolvedor removido |
| **Regras** | - Desalocar historias associadas antes de deletar<br>- Confirmar antes de deletar |

#### RF-DEV-004: Listar Desenvolvedores

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEV-004 |
| **Nome** | Listar Desenvolvedores |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve exibir lista de todos os desenvolvedores cadastrados |
| **Saida** | Lista com ID e nome dos desenvolvedores |

---




### 3.3 RF-FEAT - Gestao de Features

#### RF-FEAT-001: Criar Feature

| Atributo | Valor |
|----------|-------|
| **ID** | RF-FEAT-001 |
| **Nome** | Criar Nova Feature |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir criar uma feature com nome e numero de onda |
| **Entrada** | Nome, Onda (wave) |
| **Saida** | Feature criada com ID unico |
| **Regras** | - Nome obrigatorio e unico<br>- Onda deve ser numero positivo (> 0)<br>- Onda deve ser unica (nao duplicada) |
| **Excecoes** | DuplicateWaveException se onda ja existir |

#### RF-FEAT-002: Editar Feature

| Atributo | Valor |
|----------|-------|
| **ID** | RF-FEAT-002 |
| **Nome** | Editar Feature |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir editar nome e onda de uma feature |
| **Entrada** | ID da feature, novos valores |
| **Saida** | Feature atualizada |
| **Regras** | - Validar unicidade do nome e onda |

#### RF-FEAT-003: Deletar Feature

| Atributo | Valor |
|----------|-------|
| **ID** | RF-FEAT-003 |
| **Nome** | Deletar Feature |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir deletar uma feature que nao possui historias |
| **Entrada** | ID da feature |
| **Saida** | Feature removida |
| **Regras** | - Nao permitir deletar feature com historias associadas |
| **Excecoes** | FeatureHasStoriesException se houver historias |

#### RF-FEAT-004: Associar Historias a Features

| Atributo | Valor |
|----------|-------|
| **ID** | RF-FEAT-004 |
| **Nome** | Associar Historia a Feature |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir associar uma historia a uma feature |
| **Entrada** | ID da historia, ID da feature |
| **Saida** | Historia associada a feature |
| **Regras** | - Uma historia pode pertencer a apenas uma feature<br>- Feature pode ter multiplas historias<br>- **Historia sem feature retorna wave = 0** |

#### RF-FEAT-005: Validar Onda Unica

| Atributo | Valor |
|----------|-------|
| **ID** | RF-FEAT-005 |
| **Nome** | Validar Onda Unica |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve garantir que cada numero de onda e usado por apenas uma feature |
| **Regras** | - Rejeitar criacao/edicao que resulte em onda duplicada |

---

### 3.4 RF-DEP - Gestao de Dependencias

#### RF-DEP-001: Adicionar Dependencia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEP-001 |
| **Nome** | Adicionar Dependencia entre Historias |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir definir que uma historia depende de outra |
| **Entrada** | ID da historia, ID da dependencia (pre-requisito) |
| **Saida** | Dependencia registrada |
| **Regras** | - Historia nao pode depender de si mesma<br>- Nao criar ciclos de dependencia<br>- Dependencia deve existir no backlog |
| **Criterio de Aceite** | **Dado** historias A e B independentes,<br>**Quando** adiciono dependencia B→A (B depende de A),<br>**Entao** B.dependencies contem "A" e B.start_date >= A.end_date + 1 dia util |

#### RF-DEP-002: Remover Dependencia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEP-002 |
| **Nome** | Remover Dependencia |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve permitir remover uma dependencia existente |
| **Entrada** | ID da historia, ID da dependencia a remover |
| **Saida** | Dependencia removida |

#### RF-DEP-003: Detectar Ciclos de Dependencia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEP-003 |
| **Nome** | Detectar Ciclos de Dependencia |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve detectar e rejeitar dependencias que criariam ciclos |
| **Algoritmo** | DFS (Depth-First Search) com marcacao de estados |
| **Complexidade** | O(V+E) onde V=historias, E=dependencias |
| **Excecoes** | CyclicDependencyException com caminho do ciclo |
| **Criterio de Aceite** | **Dado** A→B (A depende de B) e B→C (B depende de C),<br>**Quando** tento adicionar C→A,<br>**Entao** sistema lanca CyclicDependencyException(path=["A","B","C","A"]) |

#### RF-DEP-004: Validar Dependencias entre Ondas

| Atributo | Valor |
|----------|-------|
| **ID** | RF-DEP-004 |
| **Nome** | Validar Dependencia de Onda |
| **Prioridade** | Should Have |
| **Descricao** | O sistema deve alertar quando uma historia depende de outra em onda posterior |
| **Regras** | - Dependencias devem estar em ondas iguais ou anteriores<br>- Emitir warning (nao bloquear) |
| **Excecoes** | InvalidWaveDependencyException |

---

### 3.5 RF-SCHED - Calculo de Cronograma

#### RF-SCHED-001: Calcular Duracao

| Atributo | Valor |
|----------|-------|
| **ID** | RF-SCHED-001 |
| **Nome** | Calcular Duracao da Historia |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve calcular a duracao em dias uteis baseado em story points e velocidade |
| **Formula** | `duration = ceil(story_points / velocity_per_day)` |
| **Minimo** | 1 dia util |
| **Criterio de Aceite** | **Dado** SP=5 e velocity=2 SP/dia,<br>**Quando** calculo duracao,<br>**Entao** duration = ceil(5/2) = 3 dias uteis |

#### RF-SCHED-002: Considerar Apenas Dias Uteis

| Atributo | Valor |
|----------|-------|
| **ID** | RF-SCHED-002 |
| **Nome** | Calcular com Dias Uteis |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve considerar apenas segunda a sexta como dias uteis |
| **Regras** | - Excluir sabados e domingos<br>- Se data inicial cair em fim de semana, avancar para segunda |
| **Criterio de Aceite** | **Dado** start_date=sabado (07/03/2026),<br>**Quando** ajusto para dia util,<br>**Entao** start_date = 09/03/2026 (segunda) |

#### RF-SCHED-003: Excluir Feriados Brasileiros

| Atributo | Valor |
|----------|-------|
| **ID** | RF-SCHED-003 |
| **Nome** | Excluir Feriados Nacionais |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve excluir feriados nacionais brasileiros do calculo |
| **Feriados** | Ano Novo, Carnaval, Sexta-feira Santa, Tiradentes, Dia do Trabalho, Corpus Christi, Independencia, Nossa Senhora Aparecida, Finados, Proclamacao da Republica, Consciencia Negra, Natal |
| **Periodo** | 2026-2028 (hardcoded) |
| **Criterio de Aceite** | **Dado** tarefa de 2 dias iniciando 20/04/2026 (segunda),<br>**Quando** calculo end_date,<br>**Entao** end_date = 22/04/2026 (pula 21/04 - Tiradentes) |

#### RF-SCHED-004: Respeitar Dependencias no Cronograma

| Atributo | Valor |
|----------|-------|
| **ID** | RF-SCHED-004 |
| **Nome** | Sequenciar por Dependencias |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve garantir que uma historia so inicia apos todas suas dependencias terminarem |
| **Regras** | - Data de inicio = max(data_fim_dependencias) + 1 dia util<br>- Processar em ordem topologica<br>- Ajuste automatico ANTES de tentar alocar (`_ensure_dependencies_finished`) |

#### RF-SCHED-005: Ajustar Data de Inicio

| Atributo | Valor |
|----------|-------|
| **ID** | RF-SCHED-005 |
| **Nome** | Ajustar para Dia Util |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve ajustar datas de inicio que caiam em dias nao uteis |
| **Regras** | - Se fim de semana: avancar para proxima segunda<br>- Se feriado: avancar para proximo dia util |

#### RF-SCHED-006: Ordenacao Topologica

| Atributo | Valor |
|----------|-------|
| **ID** | RF-SCHED-006 |
| **Nome** | Ordenar Backlog Topologicamente |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve ordenar historias respeitando dependencias e prioridades |
| **Algoritmo** | Kahn's algorithm |
| **Complexidade** | O(V+E) |
| **Regras** | - Dependencias antes de dependentes<br>- Desempate por prioridade (menor primeiro) |

---





#### RF-ALOC-001: Alocar Desenvolvedores Automaticamente

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-001 |
| **Nome** | Executar Alocacao Automatica |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve alocar desenvolvedores automaticamente para todas as historias nao alocadas |
| **Entrada** | Nenhuma (usa backlog atual) |
| **Saida** | Historias com desenvolvedores alocados e datas ajustadas |
| **Criterios de Elegibilidade** | Historia e elegivel para alocacao se:<br>- Nao tem desenvolvedor alocado<br>- Tem datas definidas (start_date e end_date)<br>- Tem story point definido |
| **Criterio de Aceite** | **Dado** 3 historias elegiveis e 2 devs,<br>**Quando** executo alocacao automatica,<br>**Entao** todas as 3 historias tem developer_id != NULL |

#### RF-ALOC-002: Balanceamento de Carga

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-002 |
| **Nome** | Balancear Carga entre Desenvolvedores |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve distribuir historias equilibradamente entre desenvolvedores |
| **Estrategia** | Alocar para desenvolvedor com menos historias |
| **Desempate** | Aleatorio (para fairness) |
| **Complexidade** | O(n*d) onde n=historias, d=desenvolvedores |
| **Decisao de Design** | Balanceamento por CONTAGEM de historias (nao por SP total). Decisao intencional: simplicidade sobre otimizacao de carga por esforco. Pode resultar em distribuicao desigual de SP entre desenvolvedores. |
| **Criterio de Aceite** | **Dado** Dev1 com 2 historias e Dev2 com 1 historia,<br>**Quando** aloco nova historia,<br>**Entao** historia e atribuida a Dev2 (menos historias) |

#### RF-ALOC-003: Criterio Proprietario de Dependencia

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-003 |
| **Nome** | Alocar por Proprietario de Dependencia |
| **Prioridade** | Should Have |
| **Descricao** | O sistema pode priorizar o desenvolvedor que implementou as dependencias da historia |
| **Beneficio** | Continuidade de contexto |
| **Configuravel** | Sim (AllocationCriteria.DEPENDENCY_OWNER) |
| **Fallback** | Balanceamento de carga se nao disponivel |

#### RF-ALOC-004: Evitar Conflitos de Periodo

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-004 |
| **Nome** | Detectar e Evitar Conflitos |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve garantir que um desenvolvedor nao tenha duas historias no mesmo periodo |
| **Validacao** | Verificar sobreposicao de datas antes de alocar |
| **Resolucao** | Ajustar data de inicio para apos termino da anterior |
| **Pos-processamento** | `_resolve_allocation_conflicts` executa ate 100 passadas para resolver sobreposicoes |
| **Criterio de Aceite** | **Dado** Dev1 com historia A (02/03-04/03) e historia B (03/03-05/03) - CONFLITO,<br>**Quando** sistema resolve conflitos,<br>**Entao** B.start_date = 05/03 (apos A.end_date) |

#### RF-ALOC-005: Ajustar Datas por Indisponibilidade

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-005 |
| **Nome** | Ajustar Datas Automaticamente |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve ajustar datas quando nao ha desenvolvedor disponivel no periodo original |
| **Estrategia** | Incrementar data de inicio em +1 dia util ate encontrar disponibilidade |
| **Limite** | Maximo de 1 ajuste por historia por iteracao |

#### RF-ALOC-006: Processar por Ondas

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-006 |
| **Nome** | Processar Ondas Sequencialmente |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve processar historias onda por onda em ordem crescente |
| **Regras** | - Onda 1 completa antes de onda 2<br>- Deadlock em uma onda nao bloqueia proximas<br>- Historias sem feature (wave=0) sao processadas primeiro |

#### RF-ALOC-007: Detectar Deadlocks

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-007 |
| **Nome** | Detectar Situacoes de Deadlock |
| **Prioridade** | Should Have |
| **Descricao** | O sistema deve detectar quando nenhuma historia pode ser alocada e emitir warning |
| **Condicao** | Nenhuma alocacao E nenhum ajuste de data na iteracao |
| **Acao** | Emitir DeadlockWarning e prosseguir para proxima onda |
| **Criterio de Aceite** | **Dado** onda 2 com 3 historias pendentes e nenhum dev disponivel,<br>**Quando** sistema detecta que nao houve progresso na iteracao,<br>**Entao** emite DeadlockWarning e processa onda 3 |

#### RF-ALOC-008: Detectar Ociosidade

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-008 |
| **Nome** | Detectar Periodos de Ociosidade |
| **Prioridade** | Should Have |
| **Descricao** | O sistema deve identificar gaps de dias uteis entre historias de um desenvolvedor |
| **Tipos** | - IdlenessWarning: dentro da mesma onda (problema)<br>- BetweenWavesIdlenessInfo: entre ondas (esperado) |
| **Calculo** | Usa `count_workdays_between` (dias ENTRE datas, exclusivo) |

#### RF-ALOC-009: Configurar Limite de Ociosidade

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-009 |
| **Nome** | Configurar Maximo de Dias Ociosos |
| **Prioridade** | Should Have |
| **Descricao** | O sistema deve permitir configurar o maximo de dias ociosos permitidos dentro de uma onda |
| **Configuracao** | max_idle_days (padrao: 3, minimo: 2, maximo: 30) |
| **Validacao** | Usado na selecao de desenvolvedor |

#### RF-ALOC-010: Realocar para Minimizar Ociosidade

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-010 |
| **Nome** | Tentar Realocacao por Ociosidade |
| **Prioridade** | Could Have |
| **Descricao** | O sistema pode tentar realocar historias para minimizar ociosidade |
| **Limite** | `MAX_REALLOCATIONS_PER_STORY = 3` |
| **Condicao** | Ociosidade excede max_idle_days |

#### RF-ALOC-011: Coletar Metricas de Alocacao

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-011 |
| **Nome** | Coletar Metricas de Performance |
| **Prioridade** | Should Have |
| **Descricao** | O sistema deve coletar metricas detalhadas durante a alocacao |
| **Metricas Coletadas** | Ver tabela abaixo |

**Estrutura AllocationMetrics:**

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `total_time_seconds` | float | Tempo total de execucao |
| `stories_processed` | int | Total de historias processadas |
| `stories_allocated` | int | Historias alocadas com sucesso |
| `waves_processed` | int | Numero de ondas processadas |
| `total_iterations` | int | Total de iteracoes do algoritmo |
| `iterations_per_wave` | Dict[int, int] | Iteracoes por onda |
| `allocations_by_dependency_owner` | int | Alocacoes por criterio DEPENDENCY_OWNER |
| `allocations_by_load_balancing` | int | Alocacoes por criterio LOAD_BALANCING |
| `deadlocks_detected` | int | Deadlocks detectados |
| `date_adjustments` | int | Ajustes de data realizados |
| `validation_reallocations` | int | Realocacoes bem-sucedidas na validacao |
| `validation_dependency_fixes` | int | Violacoes de dependencia corrigidas |
| `validation_conflict_fixes` | int | Conflitos de periodo resolvidos |
| `max_idle_violations_detected` | int | Violacoes de max_idle_days detectadas |
| `max_idle_violations_fixed` | int | Violacoes corrigidas por realocacao |
| `failed_reallocations` | int | Tentativas de realocacao que falharam |

#### RF-ALOC-012: Validacao e Estabilizacao Pos-Alocacao

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-012 |
| **Nome** | Executar Validacao Unificada |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve executar um loop de estabilizacao apos a alocacao principal |
| **Etapas** | 1. Corrigir violacoes de dependencia (`_final_dependency_check`)<br>2. Resolver conflitos de periodo (`_resolve_allocation_conflicts`)<br>3. Verificar e corrigir violacoes de max_idle_days (`_check_and_fix_idle_violations`) |
| **Limite** | `MAX_STABILIZATION_PASSES = 10` |
| **Criterio de Parada** | Loop continua ate nao haver mais ajustes ou atingir limite |

#### RF-ALOC-013: Limites de Seguranca do Algoritmo

| Atributo | Valor |
|----------|-------|
| **ID** | RF-ALOC-013 |
| **Nome** | Definir Limites de Seguranca |
| **Prioridade** | Must Have |
| **Descricao** | O sistema deve ter limites para evitar loops infinitos |
| **Constantes** | Ver tabela abaixo |

**Constantes de Limite:**

| Constante | Valor | Descricao |
|-----------|-------|-----------|
| `DEFAULT_MAX_ITERATIONS` | 1000 | Maximo de iteracoes por onda |
| `MAX_REALLOCATIONS_PER_STORY` | 3 | Evita ping-pong entre desenvolvedores |
| `MAX_STABILIZATION_PASSES` | 10 | Limite de passadas no loop de estabilizacao |
| `max_passes` (conflitos) | 100 | Limite para resolucao de conflitos de periodo |

---

## 4. Requisitos Nao-Funcionais

### 4.1 RNF-PERF - Performance

#### RNF-PERF-001: Tempo de Alocacao Automatica

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-PERF-001 |
| **Nome** | Tempo Maximo de Alocacao |
| **Metrica** | Tempo em segundos para completar alocacao automatica |
| **Objetivo** | <= 5 segundos para backlog de ate 100 historias e 10 desenvolvedores |
| **Aceitavel** | <= 15 segundos para backlog de ate 500 historias e 30 desenvolvedores |
| **Limite Suave** | 500 historias - sistema exibe warning ao ultrapassar, informando possivel degradacao de performance |
| **Comportamento Alem Limite** | Permitir operacao com aviso visual; nao bloquear criacao de novas historias |
| **Metodo de Verificacao** | Teste de performance com cronometro (time.perf_counter) |

#### RNF-PERF-002: Responsividade da Interface

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-PERF-002 |
| **Nome** | Latencia de UI |
| **Metrica** | Tempo de resposta para acoes do usuario |
| **Objetivo** | <= 100ms para operacoes CRUD simples |
| **Aceitavel** | <= 500ms para operacoes com recalculo (ex: adicionar dependencia) |
| **Metodo de Verificacao** | Profiling com Qt Performance Tools |

#### RNF-PERF-003: Consumo de Memoria

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-PERF-003 |
| **Nome** | Uso de Memoria RAM |
| **Metrica** | Memoria residente (RSS) do processo |
| **Objetivo** | <= 150 MB para backlog de ate 100 historias |
| **Aceitavel** | <= 300 MB para backlog de ate 500 historias |
| **Metodo de Verificacao** | Monitoramento via psutil ou Task Manager |

#### RNF-PERF-004: Tempo de Inicializacao

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-PERF-004 |
| **Nome** | Tempo de Startup |
| **Metrica** | Tempo ate interface estar pronta para uso |
| **Objetivo** | <= 3 segundos em cold start |
| **Aceitavel** | <= 5 segundos com banco de dados grande (500+ historias) |
| **Metodo de Verificacao** | Cronometro do primeiro render da MainWindow |

---

### 4.2 RNF-USAB - Usabilidade

#### RNF-USAB-001: Plataforma Suportada

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-USAB-001 |
| **Nome** | Sistema Operacional |
| **Requisito** | Windows 10 (build 1903+) e Windows 11 |
| **Restricao** | Linux e macOS nao sao oficialmente suportados |
| **Metodo de Verificacao** | Teste manual em Windows 10 e 11 |

#### RNF-USAB-002: Resolucao Minima de Tela

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-USAB-002 |
| **Nome** | Resolucao Minima |
| **Requisito** | 1366 x 768 pixels |
| **Recomendado** | 1920 x 1080 pixels |
| **Comportamento** | Interface deve ser utilizavel (sem cortes) na resolucao minima |
| **Metodo de Verificacao** | Teste visual em diferentes resolucoes |

#### RNF-USAB-003: Acessibilidade Basica

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-USAB-003 |
| **Nome** | Acessibilidade |
| **Requisitos** | - Contraste minimo 4.5:1 (WCAG AA)<br>- Navegacao por teclado (Tab/Shift+Tab)<br>- Atalhos de teclado para acoes principais<br>- Tooltips descritivos em icones |
| **Metodo de Verificacao** | Checklist WCAG 2.1 nivel A |

#### RNF-USAB-004: Curva de Aprendizado

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-USAB-004 |
| **Nome** | Facilidade de Uso |
| **Requisito** | Usuario com conhecimento agil deve conseguir criar e alocar backlog em ate 15 minutos na primeira utilizacao |
| **Metodo de Verificacao** | Teste de usabilidade com 3 usuarios novos |

---

### 4.3 RNF-CONF - Confiabilidade

#### RNF-CONF-001: Disponibilidade

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-CONF-001 |
| **Nome** | Uptime da Aplicacao |
| **Requisito** | Aplicacao deve iniciar e operar sem crashes em 99% das sessoes |
| **Metrica** | (Sessoes sem crash / Total de sessoes) * 100 |
| **Metodo de Verificacao** | Logs de crash e telemetria local |

#### RNF-CONF-002: Recuperacao de Erros

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-CONF-002 |
| **Nome** | Tratamento de Erros |
| **Requisitos** | - Erros nao devem crashar a aplicacao<br>- Erros devem exibir mensagem clara ao usuario<br>- Operacoes devem ser atomicas (tudo ou nada) |
| **Metodo de Verificacao** | Testes de injecao de falhas |

#### RNF-CONF-003: Integridade de Dados

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-CONF-003 |
| **Nome** | Consistencia do Banco |
| **Requisitos** | - Transacoes SQLite com ACID<br>- Nenhuma operacao deve deixar banco em estado inconsistente<br>- Foreign keys enforced |
| **Metodo de Verificacao** | Testes de interrupcao mid-operation |

#### RNF-CONF-004: Persistencia de Dados

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-CONF-004 |
| **Nome** | Salvamento Automatico |
| **Requisito** | Todas as alteracoes devem ser persistidas imediatamente apos confirmacao |
| **Comportamento** | Nao ha botao "Salvar" - operacoes sao auto-persistidas |
| **Metodo de Verificacao** | Fechar app abruptamente e verificar dados |

#### RNF-CONF-005: Logging da Aplicacao

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-CONF-005 |
| **Nome** | Sistema de Logs |
| **Formato** | Arquivo texto simples (.log) |
| **Localizacao** | Diretorio AppData do usuario |
| **Rotacao** | Por tamanho, maximo 10MB por arquivo |
| **Conteudo** | Erros, warnings, operacoes criticas (alocacao, import/export) |
| **Retencao** | Ultimos 3 arquivos de log |
| **Metodo de Verificacao** | Verificar criacao e rotacao de arquivos de log |

---

### 4.4 RNF-SEG - Seguranca

#### RNF-SEG-001: Validacao de Entrada

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-001 |
| **Nome** | Sanitizacao de Inputs |
| **Requisitos** | - Todos os campos de texto devem ser sanitizados<br>- Queries SQL devem usar parametros (prepared statements)<br>- Rejeitar caracteres de controle em campos de texto |
| **Metodo de Verificacao** | Testes com payloads maliciosos (SQLi, XSS-like) |

#### RNF-SEG-002: Backup de Dados

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-002 |
| **Nome** | Backup Manual |
| **Requisitos** | - Permitir exportacao completa do banco para arquivo<br>- Formato: SQLite dump ou Excel completo<br>- Incluir todas as entidades (historias, devs, features) |
| **Metodo de Verificacao** | Export + Import em nova instalacao |

#### RNF-SEG-003: Arquivos Locais

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-003 |
| **Nome** | Protecao de Arquivos |
| **Requisitos** | - Banco de dados em diretorio do usuario (AppData)<br>- Permissoes de arquivo somente para usuario atual<br>- Nao armazenar dados sensiveis em plain text |
| **Metodo de Verificacao** | Auditoria de permissoes de arquivo |

#### RNF-SEG-004: Compliance LGPD

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-SEG-004 |
| **Nome** | Consideracoes LGPD |
| **Requisitos** | Nao aplicavel - sistema armazena apenas identificadores internos de trabalho (nomes de desenvolvedores para alocacao), sem dados pessoais sensiveis |
| **Decisao** | Dados sao metadados de projeto, nao informacoes pessoais protegidas |

---

### 4.5 RNF-MANT - Mantenibilidade

#### RNF-MANT-001: Cobertura de Testes

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-MANT-001 |
| **Nome** | Code Coverage |
| **Objetivo** | >= 80% de cobertura de linhas |
| **Minimo** | >= 70% de cobertura de linhas |
| **Foco** | 100% nos modulos core: entities, services, allocation |
| **Metodo de Verificacao** | pytest-cov |

#### RNF-MANT-002: Documentacao de Codigo

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-MANT-002 |
| **Nome** | Docstrings |
| **Requisitos** | - Todas as classes publicas devem ter docstring<br>- Todos os metodos publicos devem ter docstring<br>- Formato: Google Style |
| **Metodo de Verificacao** | pydocstyle |

#### RNF-MANT-003: Complexidade Ciclomatica

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-MANT-003 |
| **Nome** | Complexidade de Codigo |
| **Objetivo** | Complexidade ciclomatica <= 10 por funcao |
| **Aceitavel** | Complexidade ciclomatica <= 15 para funcoes de alocacao |
| **Metodo de Verificacao** | radon cc ou flake8-cognitive-complexity |

#### RNF-MANT-004: Padronizacao de Codigo

| Atributo | Valor |
|----------|-------|
| **ID** | RNF-MANT-004 |
| **Nome** | Estilo de Codigo |
| **Requisitos** | - PEP 8 compliance<br>- Black formatter (line length 88)<br>- isort para imports<br>- Type hints em todas as assinaturas publicas |
| **Metodo de Verificacao** | pre-commit hooks |

---

## 5. Casos de Uso

### UC-001: Criar e Priorizar Backlog

| Atributo | Descricao |
|----------|-----------|
| **ID** | UC-001 |
| **Nome** | Criar e Priorizar Backlog |
| **Ator Principal** | Scrum Master / Product Owner |
| **Pre-condicoes** | Sistema inicializado, pelo menos 1 desenvolvedor cadastrado |
| **Pos-condicoes** | Backlog criado com historias priorizadas e prontas para alocacao |

**Fluxo Principal (Happy Path):**

1. Usuario acessa a tela de Backlog
2. Usuario clica em "Nova Historia"
3. Sistema exibe formulario com campos: Componente, Nome, Story Points, Feature (opcional)
4. Usuario preenche: Componente="CORE", Nome="Implementar login", SP=5
5. Sistema valida Story Points (deve ser 3, 5, 8 ou 13)
6. Sistema gera ID automatico: "CORE-001"
7. Sistema atribui prioridade = max(existentes) + 1
8. Sistema persiste historia no banco
9. Historia aparece na lista ordenada por prioridade
10. Usuario seleciona historia e clica "Mover para cima"
11. Sistema troca prioridade com historia anterior
12. Usuario repete passos 2-11 para outras historias

**Fluxos Alternativos:**

| ID | Condicao | Acao |
|----|----------|------|
| FA-1 | Story Points invalido (ex: 7) | Sistema exibe erro: "Story Points deve ser 3, 5, 8 ou 13" |
| FA-2 | Nome vazio | Sistema exibe erro: "Nome e obrigatorio" |
| FA-3 | Feature selecionada | Sistema associa historia a feature e herda onda |

**Criterios de Aceite:**

```gherkin
Cenario: Criar historia com sucesso
  Dado que estou na tela de Backlog
  E existe pelo menos 1 desenvolvedor cadastrado
  Quando crio uma historia com Componente="UI", Nome="Tela de login", SP=5
  Entao a historia e criada com ID no formato "UI-001"
  E a prioridade e max(prioridades) + 1
  E a historia aparece na lista ordenada

Cenario: Rejeitar Story Points invalido
  Dado que estou criando uma nova historia
  Quando informo Story Points = 7
  Entao o sistema exibe erro "Story Points deve ser 3, 5, 8 ou 13"
  E a historia nao e criada

Cenario: Alterar prioridade
  Dado que existem 3 historias com prioridades 1, 2, 3
  Quando seleciono a historia de prioridade 3 e clico "Mover para cima"
  Entao a historia passa a ter prioridade 2
  E a historia que tinha prioridade 2 passa a ter prioridade 3
```

---

### UC-002: Executar Alocacao Automatica com Dependencias

| Atributo | Descricao |
|----------|-----------|
| **ID** | UC-002 |
| **Nome** | Alocar Desenvolvedores Automaticamente |
| **Ator Principal** | Scrum Master / Tech Lead |
| **Pre-condicoes** | - Pelo menos 1 historia no backlog<br>- Pelo menos 1 desenvolvedor cadastrado<br>- Historias com datas calculadas (start_date, end_date) |
| **Pos-condicoes** | Todas as historias elegiveis alocadas a desenvolvedores |

**Fluxo Principal (Happy Path):**

1. Usuario configura velocidade do time (ex: 2 SP/dia)
2. Sistema calcula duracao de cada historia: `ceil(SP / velocidade)`
3. Usuario define data de inicio do projeto
4. Sistema ordena historias topologicamente (dependencias primeiro)
5. Sistema calcula datas respeitando:
   - Ordem topologica
   - Dias uteis (seg-sex)
   - Feriados brasileiros
6. Usuario clica "Alocar Automaticamente"
7. Sistema processa historias por onda (wave 0, 1, 2...)
8. Para cada historia elegivel:
   a. Busca desenvolvedor disponivel no periodo
   b. Criterio: menos historias alocadas (balanceamento)
   c. Aloca desenvolvedor e ajusta datas se necessario
9. Sistema resolve conflitos de sobreposicao
10. Sistema exibe metricas: historias alocadas, tempo total, warnings

**Fluxos Alternativos:**

| ID | Condicao | Acao |
|----|----------|------|
| FA-1 | Nenhum dev disponivel no periodo | Sistema ajusta data +1 dia util e tenta novamente |
| FA-2 | Dependencia nao concluida | Sistema aguarda dependencia e ajusta data de inicio |
| FA-3 | Criterio DEPENDENCY_OWNER ativo | Prioriza dev que fez dependencias |
| FA-4 | Max iteracoes atingido | Sistema emite DeadlockWarning e pula para proxima onda |

**Criterios de Aceite:**

```gherkin
Cenario: Alocar com dependencias
  Dado as historias:
    | ID | Nome | SP | Depende de |
    | A  | Auth | 5  | -          |
    | B  | API  | 8  | A          |
    | C  | UI   | 5  | B          |
  E os desenvolvedores: Dev1, Dev2
  E velocidade = 2 SP/dia
  E data inicio = 2026-03-02 (segunda)
  Quando executo a alocacao automatica
  Entao:
    | Historia | Dev  | Inicio     | Fim        |
    | A        | Dev1 | 2026-03-02 | 2026-03-04 |
    | B        | Dev2 | 2026-03-05 | 2026-03-12 |
    | C        | Dev1 | 2026-03-13 | 2026-03-17 |

Cenario: Excluir feriados
  Dado uma historia com SP=3 e velocidade=2 SP/dia (duracao=2 dias)
  E data inicio = 2026-04-20 (segunda antes de Tiradentes)
  Quando calculo as datas
  Entao data inicio = 2026-04-20
  E data fim = 2026-04-22 (pula 21/04 - Tiradentes)

Cenario: Balancear carga entre desenvolvedores
  Dado 4 historias independentes (A, B, C, D) com SP=3 cada
  E 2 desenvolvedores (Dev1, Dev2)
  Quando executo a alocacao
  Entao Dev1 recebe 2 historias
  E Dev2 recebe 2 historias
```

---

### UC-003: Detectar e Resolver Deadlock

| Atributo | Descricao |
|----------|-----------|
| **ID** | UC-003 |
| **Nome** | Detectar Ciclos de Dependencia |
| **Ator Principal** | Sistema (automatico) / Scrum Master (correcao) |
| **Pre-condicoes** | Usuario tentando adicionar dependencia |
| **Pos-condicoes** | Ciclo detectado e rejeitado OU dependencia adicionada |

**Fluxo Principal (Happy Path - Ciclo Detectado):**

1. Usuario seleciona historia C e clica "Adicionar Dependencia"
2. Sistema exibe lista de historias disponiveis
3. Usuario seleciona historia A como dependencia
4. Sistema executa algoritmo DFS para detectar ciclos
5. Sistema detecta ciclo: A → B → C → A
6. Sistema exibe erro: "Ciclo detectado: A → B → C → A"
7. Dependencia NAO e adicionada
8. Usuario deve escolher outra historia ou cancelar

**Fluxo Alternativo (Sem Ciclo):**

1. Usuario seleciona historia D e clica "Adicionar Dependencia"
2. Sistema exibe lista de historias disponiveis
3. Usuario seleciona historia A como dependencia
4. Sistema executa DFS - nenhum ciclo encontrado
5. Sistema adiciona dependencia: D depende de A
6. Sistema recalcula datas (D.start >= A.end + 1 dia util)

**Fluxo de Resolucao de Deadlock na Alocacao:**

1. Durante alocacao automatica, sistema detecta deadlock na onda 2
2. Condicao: nenhuma historia pode ser alocada E nenhuma data ajustada
3. Sistema emite `DeadlockWarning` com detalhes
4. Sistema pula para onda 3 e continua processamento
5. Ao final, usuario visualiza warnings no painel de metricas
6. Usuario analisa historias pendentes e corrige manualmente

**Criterios de Aceite:**

```gherkin
Cenario: Detectar ciclo direto (A → B → A)
  Dado historia A depende de B
  Quando tento adicionar dependencia B → A
  Entao sistema rejeita com erro "CyclicDependencyException"
  E exibe caminho do ciclo: "A → B → A"

Cenario: Detectar ciclo indireto (A → B → C → A)
  Dado A → B (A depende de B)
  E B → C (B depende de C)
  Quando tento adicionar C → A
  Entao sistema rejeita com "CyclicDependencyException"
  E exibe caminho: "A → B → C → A"

Cenario: Auto-dependencia rejeitada
  Dado historia X
  Quando tento adicionar X → X (X depende de si mesma)
  Entao sistema rejeita com "ValueError: Historia nao pode depender de si mesma"

Cenario: Deadlock na alocacao
  Dado 3 historias em onda 2 com dependencias circulares externas
  E nenhum desenvolvedor disponivel
  Quando executo alocacao automatica
  Entao sistema emite DeadlockWarning para onda 2
  E sistema continua processando onda 3
  E metricas mostram deadlocks_detected = 1
```

---

### UC-004: Importar Backlog do Excel

| Atributo | Descricao |
|----------|-----------|
| **ID** | UC-004 |
| **Nome** | Importar Backlog de Arquivo Excel |
| **Ator Principal** | Scrum Master / Product Owner |
| **Pre-condicoes** | Arquivo Excel no formato esperado |
| **Pos-condicoes** | Historias importadas e validadas no sistema |

**Fluxo Principal (Happy Path):**

1. Usuario clica "Importar Excel"
2. Sistema abre dialogo de selecao de arquivo
3. Usuario seleciona arquivo .xlsx
4. Sistema valida formato do arquivo (headers exatos na primeira linha)
5. Sistema le colunas com headers obrigatorios: ID, Componente, Nome, SP, Feature, Dependencias (nesta ordem, case-sensitive)
6. Para cada linha:
   a. Se ID vazio: gera no formato "US-NNN"
   b. Valida SP (3, 5, 8, 13)
   c. Cria ou associa Feature
   d. Registra dependencias (por ID)
7. Sistema valida ciclos de dependencia no conjunto importado
8. Sistema persiste todas as historias
9. Sistema exibe resumo: N historias importadas, M warnings

**Fluxos Alternativos:**

| ID | Condicao | Acao |
|----|----------|------|
| FA-1 | Coluna obrigatoria ausente | Sistema exibe erro e aborta |
| FA-2 | SP invalido em linha N | Sistema registra warning e pula linha |
| FA-3 | Dependencia inexistente | Sistema registra warning (dependencia ignorada) |
| FA-4 | Ciclo detectado no import | Sistema rejeita arquivo inteiro |

**Criterios de Aceite:**

```gherkin
Cenario: Importar arquivo valido
  Dado um arquivo Excel com 10 historias validas
  Quando importo o arquivo
  Entao 10 historias sao criadas
  E IDs sao gerados para linhas sem ID
  E Features sao criadas/associadas

Cenario: Gerar ID automatico
  Dado uma linha com ID vazio e Componente="AUTH"
  Quando importo
  Entao historia recebe ID "US-001" (ou proximo disponivel)

Cenario: Rejeitar ciclo no import
  Dado um arquivo onde A depende de B e B depende de A
  Quando tento importar
  Entao sistema exibe erro "Ciclo detectado no arquivo"
  E nenhuma historia e importada
```

---

### UC-005: Gerenciar Ondas de Entrega

| Atributo | Descricao |
|----------|-----------|
| **ID** | UC-005 |
| **Nome** | Organizar Features em Ondas |
| **Ator Principal** | Product Owner / Scrum Master |
| **Pre-condicoes** | Features e historias cadastradas |
| **Pos-condicoes** | Backlog organizado em ondas sequenciais |

**Fluxo Principal (Happy Path):**

1. Usuario acessa tela de Features
2. Usuario cria Feature "Autenticacao" com onda = 1
3. Sistema valida que onda 1 nao esta em uso
4. Usuario cria Feature "Dashboard" com onda = 2
5. Usuario associa historias a cada Feature
6. Na alocacao, sistema processa onda 1 completamente antes da onda 2
7. Historias sem feature sao processadas primeiro (wave = 0)

**Criterios de Aceite:**

```gherkin
Cenario: Onda unica por feature
  Dado Feature "Login" com onda 1
  Quando crio Feature "Cadastro" com onda 1
  Entao sistema rejeita com "DuplicateWaveException"

Cenario: Processar ondas em ordem
  Dado Feature "Auth" (onda 1) com 3 historias
  E Feature "API" (onda 2) com 2 historias
  Quando executo alocacao
  Entao todas as 3 historias de Auth sao alocadas primeiro
  E depois as 2 historias de API

Cenario: Historias sem feature (wave 0)
  Dado 2 historias sem feature
  E 2 historias em Feature "Core" (onda 1)
  Quando executo alocacao
  Entao historias sem feature sao alocadas primeiro
```

---

## 6. Diagramas e Fluxogramas

### 6.1 Arquitetura de Camadas

```
┌─────────────────────────────────────────────────────────────────┐
│                        APRESENTACAO (UI)                        │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐              │
│  │ MainWindow  │  │ StoryDialog │  │ DevDialog   │  ...         │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘              │
│         │                │                │                      │
│         └────────────────┴────────────────┘                      │
│                          │                                       │
│                    [Eventos Qt]                                  │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                     SERVICOS (Services)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐       │
│  │StoryService │  │ DevService  │  │ AllocationService   │       │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬──────────┘       │
│         │                │                    │                  │
│         └────────────────┴────────────────────┘                  │
│                          │                                       │
│              [Regras de Negocio / Validacoes]                    │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                     DOMINIO (Entities)                           │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐               │
│  │   Story     │  │  Developer  │  │   Feature   │               │
│  ├─────────────┤  ├─────────────┤  ├─────────────┤               │
│  │ id          │  │ id          │  │ id          │               │
│  │ component   │  │ name        │  │ name        │               │
│  │ name        │  └─────────────┘  │ wave        │               │
│  │ story_points│                   └─────────────┘               │
│  │ priority    │                                                 │
│  │ status      │                                                 │
│  │ dependencies│                                                 │
│  └─────────────┘                                                 │
└──────────────────────────┼───────────────────────────────────────┘
                           │
┌──────────────────────────┼───────────────────────────────────────┐
│                   PERSISTENCIA (Repository)                      │
│  ┌─────────────────┐  ┌─────────────────┐                        │
│  │ StoryRepository │  │ DevRepository   │  ...                   │
│  └────────┬────────┘  └────────┬────────┘                        │
│           │                    │                                 │
│           └────────────────────┘                                 │
│                    │                                             │
│              [SQLite / openpyxl]                                 │
└──────────────────────────────────────────────────────────────────┘
```

---

### 6.2 Fluxo de Alocacao Automatica

```
                         ┌─────────────────┐
                         │     INICIO      │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │  Ordenar historias          │
                    │  topologicamente            │
                    │  (dependencias primeiro)    │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │  Agrupar por onda           │
                    │  (wave 0, 1, 2, ...)        │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
            ┌─────────────────────────────────────────────┐
            │         PARA CADA ONDA (crescente)         │
            └─────────────────────┬───────────────────────┘
                                  │
         ┌────────────────────────┼────────────────────────┐
         │                        ▼                        │
         │     ┌──────────────────────────────────┐        │
         │     │  iteration = 0                   │        │
         │     └─────────────┬────────────────────┘        │
         │                   │                             │
         │                   ▼                             │
         │     ┌──────────────────────────────────┐        │
         │     │  ENQUANTO existir historia       │◄───┐   │
         │     │  elegivel E iteration < MAX      │    │   │
         │     └─────────────┬────────────────────┘    │   │
         │                   │                         │   │
         │                   ▼                         │   │
         │     ┌──────────────────────────────────┐    │   │
         │     │  _ensure_dependencies_finished   │    │   │
         │     │  (ajusta datas pre-alocacao)     │    │   │
         │     └─────────────┬────────────────────┘    │   │
         │                   │                         │   │
         │                   ▼                         │   │
         │     ┌──────────────────────────────────┐    │   │
         │     │  Buscar dev disponivel           │    │   │
         │     │  (menos historias = prioridade)  │    │   │
         │     └─────────────┬────────────────────┘    │   │
         │                   │                         │   │
         │           ┌───────┴───────┐                 │   │
         │           │               │                 │   │
         │           ▼               ▼                 │   │
         │     [DEV ENCONTRADO]  [NENHUM DEV]          │   │
         │           │               │                 │   │
         │           ▼               ▼                 │   │
         │     ┌──────────┐   ┌──────────────┐         │   │
         │     │ Alocar   │   │ Ajustar data │         │   │
         │     │ historia │   │ +1 dia util  │         │   │
         │     └────┬─────┘   └──────┬───────┘         │   │
         │          │                │                 │   │
         │          └────────┬───────┘                 │   │
         │                   │                         │   │
         │                   ▼                         │   │
         │     ┌──────────────────────────────────┐    │   │
         │     │  Verificar progresso:            │    │   │
         │     │  - Alocacao feita?               │    │   │
         │     │  - Data ajustada?                │    │   │
         │     └─────────────┬────────────────────┘    │   │
         │                   │                         │   │
         │           ┌───────┴───────┐                 │   │
         │           │               │                 │   │
         │           ▼               ▼                 │   │
         │     [PROGRESSO]     [SEM PROGRESSO]         │   │
         │           │               │                 │   │
         │           │               ▼                 │   │
         │           │        ┌──────────────┐         │   │
         │           │        │ DEADLOCK!    │         │   │
         │           │        │ Emitir warn  │         │   │
         │           │        │ Pular onda   │         │   │
         │           │        └──────┬───────┘         │   │
         │           │               │                 │   │
         │           ▼               │                 │   │
         │     ┌──────────┐          │                 │   │
         │     │iteration │          │                 │   │
         │     │  += 1    ├──────────┼─────────────────┘   │
         │     └──────────┘          │                     │
         │                           │                     │
         └───────────────────────────┼─────────────────────┘
                                     │
                                     ▼
                    ┌─────────────────────────────┐
                    │  ESTABILIZACAO:             │
                    │  1. _final_dependency_check │
                    │  2. _resolve_conflicts      │
                    │  3. _check_idle_violations  │
                    │  (max 10 passadas)          │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                    ┌─────────────────────────────┐
                    │  Coletar metricas           │
                    │  Emitir warnings            │
                    └─────────────┬───────────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │       FIM       │
                         └─────────────────┘
```

---

### 6.3 Grafo de Dependencias (Exemplo com Ciclo)

**Cenario Valido:**

```
    ┌───┐
    │ A │ (Auth - Onda 1)
    └─┬─┘
      │
      ▼
    ┌───┐
    │ B │ (API - Onda 1)
    └─┬─┘
      │
      ▼
    ┌───┐     ┌───┐
    │ C │────►│ D │ (UI Components - Onda 2)
    └───┘     └───┘

A → B → C → D (grafo aciclico dirigido - DAG)
Ordem de execucao: A, B, C, D
```

**Cenario com Ciclo (INVALIDO):**

```
    ┌───┐
    │ A │◄─────────────┐
    └─┬─┘              │
      │                │
      ▼                │
    ┌───┐              │
    │ B │              │
    └─┬─┘              │
      │                │
      ▼                │
    ┌───┐              │
    │ C │──────────────┘
    └───┘

A → B → C → A (CICLO!)

Deteccao via DFS:
1. Visitar A (marca como "em_processamento")
2. Visitar B (marca como "em_processamento")
3. Visitar C (marca como "em_processamento")
4. C depende de A, que esta "em_processamento"
5. CICLO DETECTADO!
6. Lanca CyclicDependencyException(path=["A", "B", "C", "A"])
```

---

### 6.4 Modelo de Dados (Entidade-Relacionamento)

```
┌─────────────────────────────────────────────────────────────────┐
│                           STORY                                 │
├─────────────────────────────────────────────────────────────────┤
│ PK  id             VARCHAR(20)   NOT NULL  "COMP-NNN"           │
│     component      VARCHAR(50)   NOT NULL                       │
│     name           VARCHAR(200)  NOT NULL                       │
│     story_points   INTEGER       NOT NULL  CHECK(IN 3,5,8,13)   │
│     priority       INTEGER       NOT NULL  CHECK(>= 0)          │
│     status         VARCHAR(20)   NOT NULL  DEFAULT 'BACKLOG'    │
│     duration       INTEGER       NULL      (dias uteis)         │
│     start_date     DATE          NULL                           │
│     end_date       DATE          NULL                           │
│ FK  developer_id   INTEGER       NULL      -> Developer.id      │
│ FK  feature_id     INTEGER       NULL      -> Feature.id        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ N:M (auto-referencia)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      STORY_DEPENDENCY                           │
├─────────────────────────────────────────────────────────────────┤
│ FK  story_id       VARCHAR(20)   NOT NULL  -> Story.id          │
│ FK  depends_on_id  VARCHAR(20)   NOT NULL  -> Story.id          │
│     UNIQUE(story_id, depends_on_id)                             │
│     CHECK(story_id != depends_on_id)                            │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         DEVELOPER                               │
├─────────────────────────────────────────────────────────────────┤
│ PK  id             INTEGER       NOT NULL  AUTOINCREMENT        │
│     name           VARCHAR(100)  NOT NULL                       │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                          FEATURE                                │
├─────────────────────────────────────────────────────────────────┤
│ PK  id             INTEGER       NOT NULL  AUTOINCREMENT        │
│     name           VARCHAR(100)  NOT NULL  UNIQUE               │
│     wave           INTEGER       NOT NULL  UNIQUE  CHECK(> 0)   │
└─────────────────────────────────────────────────────────────────┘

Relacionamentos:
- Story N:1 Developer (uma historia tem no maximo 1 dev)
- Story N:1 Feature (uma historia pertence a no maximo 1 feature)
- Story N:M Story (dependencias, via tabela STORY_DEPENDENCY)
- Feature 1:N Story (uma feature pode ter N historias)
```

---

### 6.5 Maquina de Estados - Status da Historia

```
                    ┌──────────────────────┐
                    │      BACKLOG         │ (estado inicial)
                    │  [historia criada]   │
                    └──────────┬───────────┘
                               │
            ┌──────────────────┼──────────────────┐
            │                  │                  │
            ▼                  ▼                  ▼
     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐
     │  EXECUCAO   │    │   TESTES    │    │  IMPEDIDO   │
     │[dev alocado]│    │ [em QA]     │    │ [bloqueado] │
     └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
            │                  │                  │
            │                  │                  │
            └──────────────────┼──────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │      CONCLUIDO       │ (estado final)
                    │   [historia pronta]  │
                    └──────────────────────┘

Transicoes permitidas: QUALQUER → QUALQUER
(modelo flexivel para diferentes workflows)

Valores internos (sem acento):
- BACKLOG
- EXECUCAO
- TESTES
- CONCLUIDO
- IMPEDIDO
```

---

## 7. Cenarios de Teste e Catalogo de Excecoes

### 7.1 Cenarios de Teste Praticos

#### CT-001: Backlog Completo com 20 Historias

**Setup:**

```python
# Configuracao inicial
developers = ["Ana", "Bruno", "Carlos", "Diana", "Eduardo"]
velocity = 2  # SP/dia
start_date = date(2026, 3, 2)  # Segunda-feira

# Historias por onda
wave_0 = []  # Sem feature
wave_1 = [
    Story("CORE-001", "Auth base", sp=5),
    Story("CORE-002", "Validacao", sp=3, depends=["CORE-001"]),
    Story("API-001", "Endpoints", sp=8, depends=["CORE-001"]),
    Story("API-002", "Middleware", sp=5, depends=["API-001"]),
]
wave_2 = [
    Story("UI-001", "Tela login", sp=5, depends=["CORE-002"]),
    Story("UI-002", "Dashboard", sp=8, depends=["API-002"]),
    Story("UI-003", "Componentes", sp=3),
    # ... mais 13 historias
]
```

**Resultado Esperado:**

| Metrica | Valor |
|---------|-------|
| Tempo de alocacao | < 5 segundos |
| Historias alocadas | 20/20 |
| Deadlocks | 0 |
| Distribuicao | ~4 historias por dev |

---

#### CT-002: Deteccao de Ciclo em Grafo Grande

**Setup:**

```python
# Grafo com 50 nos e 1 ciclo escondido
stories = [Story(f"S-{i:03d}", f"Historia {i}", sp=5) for i in range(50)]

# Dependencias lineares
for i in range(1, 50):
    stories[i].add_dependency(stories[i-1].id)

# Ciclo escondido: S-049 -> S-025 -> ... -> S-049
stories[25].add_dependency("S-049")  # Cria ciclo!
```

**Resultado Esperado:**

- `CyclicDependencyException` lancada
- Caminho do ciclo identificado: `S-049 -> S-048 -> ... -> S-025 -> S-049`
- Tempo de deteccao: < 100ms (DFS O(V+E))

---

#### CT-003: Deadlock por Falta de Desenvolvedores

**Setup:**

```python
developers = ["Dev1"]  # Apenas 1 desenvolvedor
stories = [
    Story("A", "Historia A", sp=5, start="2026-03-02", end="2026-03-04"),
    Story("B", "Historia B", sp=5, start="2026-03-02", end="2026-03-04"),  # Mesmo periodo!
]
```

**Resultado Esperado:**

- Historia A alocada para Dev1
- Historia B: data ajustada para 2026-03-05
- Nenhum deadlock (ajuste de data resolve)

---

#### CT-004: Feriados em Sequencia

**Setup:**

```python
# Carnaval 2026: 16-17/02 + Quarta de cinzas (18/02 ate 12h)
# Sexta-feira Santa 2026: 03/04
story = Story("X", "Tarefa", sp=8)  # 4 dias de trabalho
start_date = date(2026, 4, 1)  # Quarta antes da Sexta-feira Santa
velocity = 2
```

**Resultado Esperado:**

```
Inicio: 2026-04-01 (quarta)
Dia 1: 2026-04-01
Dia 2: 2026-04-02
-- 2026-04-03 (Sexta-feira Santa) - PULADO
-- 2026-04-04 (sabado) - PULADO
-- 2026-04-05 (domingo) - PULADO
Dia 3: 2026-04-06
Dia 4: 2026-04-07
Fim: 2026-04-07
```

---

#### CT-005: Balanceamento com Historias de Tamanhos Diferentes

**Setup:**

```python
developers = ["Dev1", "Dev2"]
stories = [
    Story("A", sp=13),  # GG - 7 dias
    Story("B", sp=3),   # P - 2 dias
    Story("C", sp=3),   # P - 2 dias
    Story("D", sp=3),   # P - 2 dias
    Story("E", sp=3),   # P - 2 dias
]
```

**Resultado Esperado (balanceamento por contagem):**

- Dev1: A, C (2 historias, 16 SP)
- Dev2: B, D, E (3 historias, 9 SP)

**Nota:** Balanceamento atual e por CONTAGEM de historias, nao por SP total.

---

### 7.2 Catalogo de Excecoes

| Excecao | Modulo | Condicao de Disparo | Mensagem Exemplo |
|---------|--------|---------------------|------------------|
| `ValueError` | Story | ID vazio ou None | "ID da historia nao pode ser vazio" |
| `ValueError` | Story | Nome vazio | "Nome da historia nao pode ser vazio" |
| `ValueError` | Story | Component vazio | "Componente nao pode ser vazio" |
| `ValueError` | Story | SP fora de [3,5,8,13] | "Story Points deve ser 3, 5, 8 ou 13" |
| `ValueError` | Story | Prioridade negativa | "Prioridade nao pode ser negativa" |
| `ValueError` | Story | Auto-dependencia | "Historia nao pode depender de si mesma" |
| `ValueError` | Story | Developer ID vazio/espacos | "Developer ID nao pode ser vazio ou apenas espacos" |
| `CyclicDependencyException` | DependencyService | Ciclo detectado | "Ciclo detectado: A → B → C → A" |
| `InvalidWaveDependencyException` | DependencyService | Depende de onda posterior | "Historia da onda 1 depende de historia da onda 2" |
| `DuplicateWaveException` | FeatureService | Onda ja existe | "Onda 3 ja esta associada a feature 'Login'" |
| `FeatureHasStoriesException` | FeatureService | Deletar feature com historias | "Feature 'Core' possui 5 historias associadas" |
| `DeadlockWarning` | AllocationService | Nenhum progresso na onda | "Deadlock detectado na onda 2: 3 historias pendentes" |
| `IdlenessWarning` | AllocationService | Gap > max_idle_days | "Dev1 ocioso por 5 dias entre CORE-001 e API-003" |
| `BetweenWavesIdlenessInfo` | AllocationService | Gap entre ondas | "Gap de 3 dias entre ondas 1 e 2 para Dev1" |

---

### 7.3 Hierarquia de Excecoes

```python
Exception
├── ValueError  # Built-in, usado para validacoes de entidade
│
└── BacklogManagerException  # Base customizada
    ├── DependencyException
    │   ├── CyclicDependencyException
    │   └── InvalidWaveDependencyException
    │
    ├── FeatureException
    │   ├── DuplicateWaveException
    │   └── FeatureHasStoriesException
    │
    └── AllocationException
        └── MaxIterationsExceeded

# Warnings (nao bloqueantes)
Warning
└── BacklogWarning
    ├── DeadlockWarning
    ├── IdlenessWarning
    └── BetweenWavesIdlenessInfo
```

---

### 7.4 Matriz de Rastreabilidade

| Requisito | Caso de Teste | Excecoes Relacionadas |
|-----------|---------------|----------------------|
| RF-STORY-001 | CT-001 | ValueError (validacoes) |
| RF-STORY-008 | CT-001 | ValueError (SP invalido) |
| RF-DEP-003 | CT-002 | CyclicDependencyException |
| RF-ALOC-001 | CT-001, CT-003 | - |
| RF-ALOC-004 | CT-003 | - |
| RF-ALOC-007 | CT-003 | DeadlockWarning |
| RF-SCHED-003 | CT-004 | - |
| RF-ALOC-002 | CT-005 | - |
| RF-FEAT-001 | - | DuplicateWaveException |
| RF-FEAT-003 | - | FeatureHasStoriesException |
| RF-DEP-004 | - | InvalidWaveDependencyException |

---

## 8. Glossario Expandido e Resolucao de Ambiguidades

### 8.1 Termos Esclarecidos

| Termo | Definicao Oficial | Nao Confundir Com |
|-------|-------------------|-------------------|
| **Desenvolvedor** | Pessoa que executa historias. Entidade cadastrada no sistema com ID e nome. | Recurso (termo generico de PM) |
| **Recurso** | NAO USAR. Termo evitado no sistema. Use "Desenvolvedor". | - |
| **Historia** | User Story - unidade de trabalho. Sinonimo oficial no sistema. | Tarefa, Item, Card |
| **Status** | Estado atual da historia no fluxo de trabalho (BACKLOG, EXECUCAO, etc.). | Estado (use Status) |
| **Estado** | NAO USAR como sinonimo de Status. Reservado para diagramas de estado. | - |
| **Onda (Wave)** | Agrupamento sequencial de features. Onda 1 entrega antes da onda 2. | Sprint, Release |
| **Wave 0** | Historias SEM feature associada. Processadas ANTES da onda 1. | Onda zero, Backlog solto |
| **Prioridade** | Ordem de importancia (1 = mais prioritaria). Inteiro positivo. | Urgencia, Severidade |
| **Alocacao** | Ato de atribuir um desenvolvedor a uma historia. | Atribuicao (sinonimo aceito) |
| **Dependencia** | Relacao onde historia B so pode iniciar apos historia A terminar. A → B significa "B depende de A". | Bloqueio, Impedimento |
| **Ciclo** | Dependencia circular (A → B → C → A). Sempre invalido. | Loop, Deadlock |
| **Deadlock** | Situacao na alocacao onde nenhuma historia pode progredir. | Ciclo (ciclo e na dependencia, deadlock e na alocacao) |
| **Ociosidade** | Periodo sem trabalho para um desenvolvedor DENTRO de uma onda. | Gap entre ondas (esperado) |
| **Dia Util** | Segunda a sexta, excluindo feriados. | Dia corrido |

### 8.2 Convencoes de Nomenclatura

| Contexto | Convencao | Exemplo |
|----------|-----------|---------|
| ID de Historia | `COMPONENTE-NNN` | CORE-001, UI-042, API-015 |
| ID de Historia (import sem ID) | `US-NNN` | US-001, US-002 |
| Status | MAIUSCULAS, sem acento | BACKLOG, EXECUCAO, CONCLUIDO |
| Nome de Feature | Texto livre, case-insensitive na busca | "Autenticacao", "Dashboard Admin" |
| Nome de Desenvolvedor | Texto livre | "Ana Silva", "joao.dev" |

### 8.3 Regras de Negocio Implicitas (Agora Explicitas)

| Regra | Valor | Origem |
|-------|-------|--------|
| Historia sem feature → wave | 0 | RF-FEAT-004 |
| Prioridade inicial | max(existentes) + 1 | RF-STORY-001 |
| Duracao minima | 1 dia util | RF-SCHED-001 |
| SP validos | {3, 5, 8, 13} | RF-STORY-008 |
| Onda minima | 1 (wave > 0) | RF-FEAT-001 |
| Uma historia por dev por vez | Sim (sem paralelismo) | RF-ALOC-004 |
| Developer pode ficar ocioso | Sim (warning emitido) | RF-ALOC-008 |
| Dependencia cross-wave | Permitida (warning se posterior) | RF-DEP-004 |

---

## 9. Clarificacoes

### Sessao 2026-02-28

- Q: Compliance/LGPD para dados de desenvolvedores? → A: Nao aplicavel - dados sao apenas identificadores internos de trabalho
- Q: Formato de importacao Excel? → A: Formato fixo com headers exatos na primeira linha (ID, Componente, Nome, SP, Feature, Dependencias)
- Q: Balanceamento por contagem vs SP total? → A: Decisao de design - balanceamento por contagem de historias e intencional
- Q: Formato e localizacao de logs? → A: Log em arquivo texto simples em AppData com rotacao por tamanho (10MB)
- Q: Comportamento ao exceder 500 historias? → A: Permitir com aviso - exibir warning ao ultrapassar limite

---

## 10. Apendices

### A. Feriados Brasileiros (2026-2028)

| Feriado | 2026 | 2027 | 2028 |
|---------|------|------|------|
| Ano Novo | 01/01 | 01/01 | 01/01 |
| Carnaval | 16-17/02 | 08-09/02 | 28-29/02 |
| Sexta-feira Santa | 03/04 | 26/03 | 14/04 |
| Tiradentes | 21/04 | 21/04 | 21/04 |
| Dia do Trabalho | 01/05 | 01/05 | 01/05 |
| Corpus Christi | 04/06 | 27/05 | 15/06 |
| Independencia | 07/09 | 07/09 | 07/09 |
| N. Sra. Aparecida | 12/10 | 12/10 | 12/10 |
| Finados | 02/11 | 02/11 | 02/11 |
| Proclamacao Rep. | 15/11 | 15/11 | 15/11 |
| Consciencia Negra | 20/11 | 20/11 | 20/11 |
| Natal | 25/12 | 25/12 | 25/12 |

### B. Atalhos de Teclado (Planejado)

| Acao | Atalho |
|------|--------|
| Nova Historia | Ctrl+N |
| Editar Selecionado | Enter ou F2 |
| Deletar Selecionado | Delete |
| Mover Prioridade Cima | Alt+Up |
| Mover Prioridade Baixo | Alt+Down |
| Executar Alocacao | Ctrl+Shift+A |
| Importar Excel | Ctrl+I |
| Exportar Excel | Ctrl+E |

---
