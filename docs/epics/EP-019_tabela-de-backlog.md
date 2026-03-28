# EP-019 — Tabela de Backlog (GUI-003)

**Camada:** Interface & Experiencia

---

## Problema que Resolve

A tabela de backlog implementada em EP-008 utiliza QTableView com renderizacao padrao Qt, exibindo apenas 8 colunas sem delegates customizados. O status e exibido como texto puro sem diferenciacao visual (badges coloridos). IDs nao usam fonte monospace. Nao ha zebra striping, nem estado vazio orientativo, nem estilizacao de header/selecao consistente. Faltam 5 colunas essenciais para o planejamento (Prioridade, Onda, Componente, Dependencias, Duracao) que forneceriam contexto completo ao usuario (RNF-USAB-004: curva de aprendizado <= 15 minutos).

Os delegates de renderizacao customizada (`StatusBadgeDelegate`, `MonospaceDelegate`) foram criados em EP-017 mas ainda nao foram integrados na tabela, desperdicando o potencial visual da fundacao de design system.

## Objetivo (Valor Mensuravel)

Expandir o `StoryTableModel` de 8 para 13 colunas. Integrar os delegates `StatusBadgeDelegate` (badges coloridos com indicadores nao-cromaticos) e `MonospaceDelegate` (IDs em fonte monospace) criados em EP-017. Aplicar zebra striping, selecao estilizada, header estilizado e scrollbar slim via QSS. Implementar estado vazio com mensagem orientativa.

**Metricas de sucesso:**
- `StoryTableModel.columnCount()` retorna 13
- 100% das colunas com larguras e alinhamentos corretos
- Delegates integrados e funcionais nas colunas Status e ID
- Estado vazio exibido quando `rowCount() == 0`
- Testes existentes atualizados e passando sem regressao

## Alinhamento Estrategico

Conexao com as capacidades do produto definidas na secao 2.2 do SRS:
- **Capacidade 1 (Gestao de Backlog)**: Tabela principal com todas as informacoes relevantes para priorizacao e planejamento (RF-STORY-005)
- **Capacidade 4 (Gestao de Dependencias)**: Coluna de dependencias com indicador visual de bloqueio (RF-DEP-001)
- **Capacidade 5 (Calculo de Cronograma)**: Colunas de datas (Inicio, Fim, Duracao) visiveis na tabela (RF-SCHED-001)
- **Capacidade 6 (Alocacao Automatica)**: Status da historia com badges visuais claros (RF-STORY-009)

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Visualizacao completa do backlog com 13 colunas para planejamento diario |
| Gerente de Projeto | Visao clara de status via badges coloridos, datas e duracao para acompanhamento |
| Product Owner | Identificacao rapida de prioridades, ondas e dependencias para tomada de decisao |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — contribui para (visualizacao completa com 13 colunas)
- UC-002: Alocacao Automatica com Dependencias — contribui para (coluna Dependencias e indicador de bloqueio)
- UC-005: Gerenciar Ondas de Entrega — contribui para (coluna Onda visivel)
- CT-001 a CT-005: executaveis com visualizacao melhorada

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-STORY-005: Listar Historias do Backlog — expansao para 13 colunas com formatacao adequada
- RF-STORY-009: Gerenciar Status — integracao do StatusBadgeDelegate para visualizacao de status

**Requisitos Nao-Funcionais:**
- RNF-USAB-003: Acessibilidade basica (zebra striping para facilitar leitura, badges com indicadores nao-cromaticos)
- RNF-USAB-004: Curva de aprendizado <= 15 minutos (estado vazio orientativo, informacoes visiveis)
- RNF-PERF-002: Responsividade UI <= 100ms (renderizacao eficiente de delegates)
- RNF-MANT-001: Manutenibilidade (codigo organizado, testes atualizados)

**Artefatos Estruturais:**
- Arquitetura em camadas (SRS §6.1): Camada Presentation
- Padroes UI/UX (Constitution §XIX): MVVM com delegates

**Componentes a implementar:**

| ID      | Componente              | Tipo          | Descricao |
|---------|-------------------------|---------------|-----------|
| MW-004  | Tabela de Backlog       | REFATORACAO   | Expandir StoryTableModel 8→13 colunas, integrar delegates, configurar larguras/alinhamentos |
| MW-008  | Estado Vazio            | NOVO          | Overlay/placeholder na tabela quando sem historias, com mensagem orientativa |

### Fora do Escopo

- StatusBadgeDelegate e MonospaceDelegate (ja criados em EP-017 — aqui sao apenas integrados)
- Busca e filtros sobre a tabela → sera tratado em EP-020 (GUI-004)
- Tooltip rico ao hover → sera tratado em EP-022 (GUI-006)
- Agrupamento visual por onda → sera tratado em EP-022 (GUI-006)
- Indicador de bloqueio na coluna Dependencias → sera tratado em EP-022 (GUI-006)

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-STORY-005 | Listar Historias do Backlog | Must Have |
| RF-STORY-009 | Gerenciar Status da Historia | Must Have |

**Detalhamento das 13 colunas:**

| # | Coluna | Largura | Alinhamento | Delegate | Detalhes |
|---|--------|---------|-------------|----------|----------|
| 0 | Prioridade | 60px fixo | Centro | — | Numero inteiro (0 = mais prioritario) |
| 1 | Feature | 120px | Esquerda | — | Nome da feature ou "—", truncar com elipsis |
| 2 | Onda | 50px fixo | Centro | — | Numero da onda (0 = sem feature) |
| 3 | ID | 100px fixo | Esquerda | MonospaceDelegate | Formato "COMPONENTE-NNN" (ex: AUTH-001) |
| 4 | Componente | 80px | Esquerda | — | Texto ex: AUTH, API, UI |
| 5 | Nome | stretch | Esquerda | — | Minimo 200px, truncar com elipsis, QHeaderView.Stretch |
| 6 | Status | 100px fixo | Centro | StatusBadgeDelegate | Badge pill colorido com simbolo |
| 7 | Desenvolvedor | 100px | Esquerda | — | Nome do dev (nao ID), ou "—", truncar com elipsis |
| 8 | Dependencias | 120px | Esquerda | — | IDs separados por virgula ou "—", truncar com elipsis |
| 9 | SP | 40px fixo | Centro | — | Story Points (3, 5, 8 ou 13) |
| 10 | Inicio | 90px fixo | Centro | — | Data DD/MM/YYYY ou "—" |
| 11 | Fim | 90px fixo | Centro | — | Data DD/MM/YYYY ou "—" |
| 12 | Duracao | 60px fixo | Centro | — | Numero de dias uteis ou "—" |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-USAB-003 | Acessibilidade Basica | Zebra striping, badges com simbolos nao-cromaticos |
| RNF-USAB-004 | Curva de Aprendizado | Estado vazio orientativo, informacoes completas |
| RNF-PERF-002 | Responsividade UI | Renderizacao de delegates <= 16ms por celula (60fps) |
| RNF-MANT-001 | Cobertura de Testes | Testes atualizados para 13 colunas |

---

## Criterios de Aceite (Alto Nivel)

### Expansao de Colunas
- [ ] **Dado** `StoryTableModel`, **Quando** chamo `columnCount()`, **Entao** retorna 13
- [ ] **Dado** `StoryTableModel`, **Quando** chamo `headerData()` para cada coluna, **Entao** retorna nomes corretos na ordem especificada
- [ ] **Dado** historia com datas definidas, **Quando** exibo na tabela, **Entao** datas formatadas como DD/MM/YYYY

### Integracao de Delegates
- [ ] **Dado** coluna Status (indice 6), **Quando** renderiza historia com status BACKLOG, **Entao** exibe badge pill com prefixo "●" e cores corretas
- [ ] **Dado** coluna Status, **Quando** renderiza historia com status CONCLUIDO, **Entao** exibe badge pill com prefixo "✓" e cores corretas
- [ ] **Dado** coluna ID (indice 3), **Quando** renderiza ID "AUTH-001", **Entao** usa fonte monospace (JetBrains Mono ou fallback)

### Estilizacao
- [ ] **Dado** tabela com multiplas historias, **Quando** visualizo, **Entao** zebra striping visivel (linhas alternadas @neutral-0 / @neutral-150)
- [ ] **Dado** historia selecionada, **Quando** visualizo, **Entao** fundo @primary-light, texto nao invertido
- [ ] **Dado** header da tabela, **Quando** visualizo, **Entao** uppercase, @neutral-500, weight 600, border-bottom 2px

### Layout e Truncacao
- [ ] **Dado** coluna Nome, **Quando** redimensiono janela, **Entao** coluna expande/contrai (stretch)
- [ ] **Dado** texto longo em coluna Feature, **Quando** visualizo, **Entao** trunca com elipsis e tooltip mostra texto completo

### Estado Vazio
- [ ] **Dado** tabela sem historias (`rowCount() == 0`), **Quando** visualizo, **Entao** mensagem centralizada: "Nenhuma historia cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para comecar."
- [ ] **Dado** tabela sem historias, **Quando** verifico botoes de processamento, **Entao** botoes Cronograma e Alocar desabilitados visualmente

### Compatibilidade
- [ ] **Dado** testes existentes do StoryTableModel, **Quando** executo suite, **Entao** todos passam com ajustes para 13 colunas
- [ ] **Dado** resolucao 1366x768, **Quando** abro aplicacao, **Entao** tabela funcional com scrollbar horizontal se necessario

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Colunas visiveis | Numero de colunas | 13 | RF-STORY-005 |
| Delegates integrados | Colunas com delegate | 2 (Status, ID) | RNF-USAB-003 |
| Renderizacao de delegate | Tempo por celula | <= 16ms | RNF-PERF-002 |
| Testes atualizados | Testes falhando | 0 | RNF-MANT-001 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Teste Manual | Abrir aplicacao com dados: verificar 13 colunas com dados corretos | RF-STORY-005 |
| Teste Manual | Verificar badges coloridos em cada status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) | RF-STORY-009 |
| Teste Manual | Verificar IDs em fonte monospace | RNF-USAB-003 |
| Teste Manual | Abrir aplicacao sem dados: verificar estado vazio com mensagem centralizada | RNF-USAB-004 |
| Teste Manual | Redimensionar janela: coluna Nome expande/contrai, outras mantem largura fixa | RNF-USAB-002 |
| Teste Manual | Hover sobre celula truncada: tooltip exibe texto completo | RNF-USAB-003 |
| Teste Unitario | `test_column_count`: `model.columnCount() == 13` | RF-STORY-005 |
| Teste Unitario | `test_header_data`: nomes corretos para 13 colunas | RF-STORY-005 |
| Teste Unitario | `test_data_formatting`: datas DD/MM/YYYY, IDs COMPONENTE-NNN, devs por nome | RF-STORY-005 |
| Teste Unitario | `test_empty_state`: estado vazio quando rowCount() == 0 | RNF-USAB-004 |
| Revisao de Codigo | Confirmar que delegates sao atribuidos via `setItemDelegateForColumn()` nos indices corretos | Constitution §XIX |
| Revisao de Codigo | Validar separacao View/ViewModel no StoryTableModel | Constitution §XIX |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-008 | Interface grafica basica implementada — GUI-003 expande a tabela existente |
| EP-017 | StatusBadgeDelegate (DS-003), MonospaceDelegate (DS-004), QSS da tabela (DS-002), theme.py (DS-001) |
| EP-018 | Layout vertical (MW-006): tabela deve ocupar 100% da largura apos remocao do QSplitter |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Risco | Expansao 8→13 colunas pode quebrar testes existentes que verificam indices | Mapear todos os testes que referenciam indices de coluna e atualizar sistematicamente |
| Risco | Coluna Dependencias requer joins com dados de outras entidades (IDs → nomes) | Verificar se o ViewModel ja fornece dados de dependencias. Se nao, ajustar `data()` para buscar via ViewModel |
| Risco | Coluna Desenvolvedor atualmente exibe `developer_id` — precisa exibir nome | Ajustar `data()` para resolver ID → nome via dados ja carregados no modelo |
| Risco | Delegates podem conflitar com zebra striping do QSS | Testar renderizacao do badge sobre linhas alternadas. StatusBadgeDelegate deve pintar fundo do badge sobre fundo da celula |
| Risco | Estado vazio pode conflitar com o modelo da tabela | Implementar estado vazio via overlay widget ou QStackedWidget, nao no modelo |
| Premissa | PySide6 6.6.1+ suporta QStyledItemDelegate conforme esperado | Conforme SRS §2.4 |
| Premissa | Delegates do EP-017 ja estao disponiveis em presentation/delegates/ | Dependencia explicita de EP-017 |
| Premissa | StoryTableModel ja expoe dados suficientes para todas as 13 colunas | Verificar se DTO inclui todos os campos necessarios |

---

## Especificacoes Tecnicas (Referencia)

### Arquivos Impactados

| Arquivo | Acao | Descricao |
|---------|------|-----------|
| `src/backlog_manager/presentation/viewmodels/story_table_model.py` | EDITAR | Expandir `columnCount()` 8→13, atualizar `headerData()` e `data()` para 13 colunas, ajustar roles e alinhamentos |
| `src/backlog_manager/presentation/views/main_window.py` | EDITAR | Integrar delegates nas colunas Status e ID, configurar `QHeaderView` (larguras, stretch), habilitar `alternatingRowColors`, implementar overlay de estado vazio |
| `tests/unit/test_story_table_model.py` (ou equivalente) | EDITAR | Atualizar testes que verificam `columnCount() == 8` para `== 13`, adicionar testes para novas colunas |

### Estilizacao da Tabela (QSS do EP-017)

A estilizacao deve seguir o QSS definido em EP-017:
- Zebra striping: `@neutral-0` e `@neutral-150` alternados — ativar `setAlternatingRowColors(True)`
- Selecao: fundo `@primary-light` (#EEF2FF), texto `@neutral-800` (sem inversao de cores)
- Header: fundo `@neutral-100`, texto `@neutral-500` uppercase, 12px, weight 600, border-bottom 2px solid `@neutral-200`
- Grid lines: transparent (sem grid), apenas `border-bottom: 1px solid @neutral-200` por item
- Altura das linhas: 36px, header 40px
- Scrollbar: 8px width, border-radius 4px, handle `@neutral-300`
- Focus: border 2px solid `@primary` na celula focada

### Estado Vazio (MW-008)

- Mensagem centralizada na area da tabela: "Nenhuma historia cadastrada. Clique em '+ Nova' ou importe um arquivo Excel para comecar."
- Implementacao via QStackedWidget ou overlay transparente sobre QTableView
- Botoes de processamento (Cronograma, Alocar) desabilitados visualmente quando nao ha historias
- Fonte: @font-size-base, cor @neutral-400, centralizado vertical e horizontalmente

### Truncacao e Tooltip

- Colunas Nome, Feature, Dependencias, Desenvolvedor: `elideMode(Qt.ElideRight)`
- Tooltip automatico com texto completo ao hover em celulas truncadas
- Implementar via `data()` com role `Qt.ToolTipRole` retornando texto completo
