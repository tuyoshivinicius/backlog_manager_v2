# EP-020 — Busca, Filtros e Menu de Contexto (GUI-004)

**Camada:** Interface & Experiencia

---

## Problema que Resolve

Nao existe mecanismo de busca, filtro ou menu de contexto na interface implementada em EP-008 e refinada em EP-017/EP-018/EP-019. Com backlogs de 100+ historias, localizar uma historia por nome/componente/status exige scroll manual, prejudicando a produtividade do usuario (RNF-USAB-004: curva de aprendizado <= 15 minutos). Operacoes como Editar, Deletar e Gerenciar Dependencias sao acessiveis apenas via toolbar — nao ha right-click na tabela, quebrando convencoes de usabilidade padrao de aplicacoes desktop.

O `DuplicateStoryUseCase` (RF-STORY-004) esta implementado no backend mas nao exposto na UI. Nao ha filtros por status ou feature/onda para segmentar o backlog, dificultando a visualizacao focada em subconjuntos de historias.

A barra de filtros foi reservada (espaco vazio) em EP-018, aguardando implementacao neste epico.

## Objetivo (Valor Mensuravel)

Adicionar barra de busca incremental (filtra enquanto digita, Ctrl+F) com filtros por status (chips com contagem) e por feature/onda (dropdown). Adicionar menu de contexto no right-click da tabela com 6 acoes agrupadas. Expor a acao de Duplicar Historia na toolbar, menu de contexto e atalho Ctrl+D.

**Entregas concretas:**
- Campo de busca QLineEdit (240px, Ctrl+F) filtrando por ID, Nome ou Componente
- 6 chips de status (Todos, Backlog, Execucao, Testes, Concluido, Impedido) com contagem
- Dropdown de feature/onda combinavel com demais filtros
- QMenu de contexto com 6 acoes agrupadas por categoria
- Botao [Duplicar] na toolbar, menu de contexto e atalho Ctrl+D
- QSortFilterProxyModel para filtragem sem alterar modelo original

**Metricas de sucesso:**
- Busca filtra tabela em <= 150ms (debounce)
- Chips exibem contagem correta por status
- Menu de contexto acessivel via right-click em qualquer linha
- Acao Duplicar cria copia com sufixo " (copia)"
- Testes existentes continuam passando sem regressao

## Alinhamento Estrategico

Conexao com as capacidades do produto definidas na secao 2.2 do SRS:
- **Capacidade 1 (Gestao de Backlog)**: Busca e filtros para navegacao eficiente em backlogs grandes (RF-STORY-005)
- **Capacidade 1 (Gestao de Backlog)**: Duplicacao de historias via UI (RF-STORY-004)
- **Capacidade 2 (Gestao de Features)**: Filtro por feature/onda para visualizacao focada (RF-FEAT-004)
- **Capacidade 4 (Gestao de Dependencias)**: Acesso rapido a DependencyDialog via menu de contexto (RF-DEP-001)

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Localizacao rapida de historias especificas, duplicacao para criacao de tarefas similares |
| Gerente de Projeto | Filtragem por status para acompanhamento de progresso, visao segmentada por onda |
| Product Owner | Acesso rapido a acoes via right-click, filtro por feature para priorizacao |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — habilita (duplicacao de historia via RF-STORY-004)
- UC-001: Criar e Priorizar Backlog — contribui para (busca e filtros para navegacao)
- UC-002: Alocacao Automatica com Dependencias — contribui para (menu de contexto para dependencias)
- UC-005: Gerenciar Ondas de Entrega — contribui para (filtro por onda)
- CT-001 a CT-005: executaveis com filtragem e navegacao melhoradas

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- RF-STORY-004: Duplicar Historia — exposicao na UI (toolbar, menu contexto, Ctrl+D)
- RF-STORY-005: Listar Historias do Backlog — filtragem incremental por ID/Nome/Componente
- RF-STORY-006: Alterar Prioridade — exposicao no menu de contexto (Mover Cima/Baixo)
- RF-STORY-009: Gerenciar Status — filtragem por status via chips
- RF-DEP-001: Adicionar Dependencia — acesso via menu de contexto "Dependencias..."

**Requisitos Nao-Funcionais:**
- RNF-USAB-003: Acessibilidade basica (navegacao por teclado, atalhos Ctrl+F, Ctrl+D)
- RNF-USAB-004: Curva de aprendizado <= 15 minutos (filtros intuitivos, menu de contexto padrao)
- RNF-PERF-002: Responsividade UI <= 100ms para operacoes de filtragem
- RNF-MANT-001: Manutenibilidade (QSortFilterProxyModel, codigo organizado)

**Artefatos Estruturais:**
- Arquitetura em camadas (SRS §6.1): Camada Presentation
- Padroes UI/UX (Constitution §XIX): MVVM com proxy model

**Componentes a implementar:**

| ID      | Componente                 | Tipo  | Descricao |
|---------|----------------------------|-------|-----------|
| MW-003  | Barra de Busca/Filtros     | NOVO  | QLineEdit (240px, Ctrl+F) + chips de status + dropdown feature/onda, 36px altura total |
| MW-007  | Menu de Contexto           | NOVO  | QMenu no right-click com 6 acoes agrupadas por categoria |
| UX-001  | Duplicar Historia na UI    | NOVO  | Botao na toolbar (Grupo 1), item no menu contexto, atalho Ctrl+D |
| UX-003  | Filtros Rapidos por Status | NOVO  | 6 chips QPushButton checkable com contagem de historias por status |
| UX-004  | Filtro por Feature/Onda    | NOVO  | QComboBox dropdown com features agrupadas por onda |

### Fora do Escopo

- Agrupamento visual por onda na tabela → sera tratado em EP-022 (GUI-006)
- Tooltip rico no hover → sera tratado em EP-022 (GUI-006)
- Indicador visual de bloqueio na coluna Dependencias → sera tratado em EP-022 (GUI-006)
- Estilizacao fina de dialogs → EP-021 (GUI-005)

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| RF-STORY-004 | Duplicar Historia | Should Have |
| RF-STORY-005 | Listar Historias do Backlog | Must Have |
| RF-STORY-006 | Alterar Prioridade | Must Have |
| RF-STORY-009 | Gerenciar Status da Historia | Must Have |
| RF-DEP-001 | Adicionar Dependencia entre Historias | Must Have |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-USAB-003 | Acessibilidade Basica | Atalhos Ctrl+F e Ctrl+D funcionais, navegacao por teclado |
| RNF-USAB-004 | Curva de Aprendizado | <= 15 minutos (filtros intuitivos) |
| RNF-PERF-002 | Responsividade UI | Filtragem <= 150ms (com debounce) |
| RNF-MANT-001 | Cobertura de Testes | Testes para FilterProxyModel |

---

## Criterios de Aceite (Alto Nivel)

### Busca Incremental
- [ ] **Dado** campo de busca, **Quando** digito "AUTH", **Entao** tabela filtra para historias com "AUTH" em ID, Nome ou Componente
- [ ] **Dado** campo de busca, **Quando** pressiono Ctrl+F, **Entao** campo de busca recebe foco
- [ ] **Dado** campo de busca, **Quando** digito, **Entao** filtragem ocorre apos debounce de 150ms

### Chips de Status
- [ ] **Dado** 6 chips de status, **Quando** visualizo, **Entao** cada chip mostra contagem correta (ex: "Backlog (12)")
- [ ] **Dado** chip "Execucao", **Quando** clico, **Entao** chip fica ativo (bg @primary) e tabela filtra para status EXECUCAO
- [ ] **Dado** chip ativo + texto em busca, **Quando** verifico tabela, **Entao** filtros combinam (AND)

### Dropdown Feature/Onda
- [ ] **Dado** dropdown de features, **Quando** abro, **Entao** vejo "Todas as features" + lista de features por onda
- [ ] **Dado** feature selecionada, **Quando** verifico tabela, **Entao** apenas historias dessa feature sao exibidas
- [ ] **Dado** feature + status + busca, **Quando** combino, **Entao** filtros compostos funcionam corretamente

### Menu de Contexto
- [ ] **Dado** historia na tabela, **Quando** right-click, **Entao** QMenu aparece com 6 acoes
- [ ] **Dado** menu de contexto, **Quando** verifico estrutura, **Entao** vejo separadores entre categorias (edicao, priorizacao, relacoes, destrutiva)
- [ ] **Dado** item "Deletar", **Quando** verifico estilo, **Entao** texto em cor @error

### Duplicar Historia
- [ ] **Dado** historia selecionada, **Quando** clico Duplicar na toolbar, **Entao** copia criada com sufixo " (copia)"
- [ ] **Dado** historia selecionada, **Quando** pressiono Ctrl+D, **Entao** copia criada com sufixo " (copia)"
- [ ] **Dado** historia AUTH-001 duplicada, **Quando** verifico resultado, **Entao** nova historia tem mesmo SP, feature, mas developer_id=NULL e start_date=NULL

### Proxy Model
- [ ] **Dado** QSortFilterProxyModel, **Quando** filtragem aplicada, **Entao** StoryTableModel original nao e modificado
- [ ] **Dado** delegates do EP-019, **Quando** proxy ativo, **Entao** delegates continuam funcionando na view

### Compatibilidade
- [ ] **Dado** testes existentes, **Quando** executo suite, **Entao** todos passam sem regressao
- [ ] **Dado** DependencyDialog do EP-018, **Quando** clico "Dependencias..." no menu contexto, **Entao** dialog abre para historia selecionada

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Tempo de filtragem | Milissegundos | <= 150ms (debounce) | RNF-PERF-002 |
| Atalhos funcionais | Quantidade | 2 (Ctrl+F, Ctrl+D) | RNF-USAB-003 |
| Contagem em chips | Precisao | 100% correto | RF-STORY-005 |
| Filtros compostos | Combinacoes | Busca + Status + Feature | RF-STORY-005 |
| Testes atualizados | Testes falhando | 0 | RNF-MANT-001 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Teste Manual | Digitar texto no campo de busca: tabela filtra por ID, Nome, Componente em tempo real | RF-STORY-005 |
| Teste Manual | Clicar chip "Execucao": apenas historias em execucao visiveis, contagem correta | RF-STORY-009 |
| Teste Manual | Combinar busca "AUTH" + chip "Backlog": apenas historias AUTH com status Backlog | RF-STORY-005, RF-STORY-009 |
| Teste Manual | Selecionar feature no dropdown: tabela filtra por feature/onda | RF-FEAT-004 |
| Teste Manual | Right-click em historia: menu de contexto com 6 itens, separadores, Deletar em vermelho | RNF-USAB-003 |
| Teste Manual | Ctrl+D: historia duplicada aparece na tabela com sufixo " (copia)" | RF-STORY-004 |
| Teste Manual | Ctrl+F: campo de busca recebe foco | RNF-USAB-003 |
| Teste Manual | Menu contexto "Dependencias...": DependencyDialog abre para historia selecionada | RF-DEP-001 |
| Teste Unitario | Testar `FilterProxyModel.filterAcceptsRow()`: filtros combinados texto + status + feature | RF-STORY-005 |
| Teste Unitario | Testar contagem de chips: retorna numeros corretos por status | RF-STORY-009 |
| Teste Unitario | Testar acao Duplicar: cria copia com campos corretos (RF-STORY-004) | RF-STORY-004 |
| Revisao de Codigo | Confirmar que filtros nao alteram o modelo original (proxy pattern) | RNF-MANT-001 |
| Revisao de Codigo | Validar separacao View/ViewModel no FilterProxyModel | Constitution §XIX |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-008 | Interface grafica basica implementada — DuplicateStoryUseCase ja existe no backend |
| EP-017 | QSS centralizado (estilizacao de chips, menu de contexto, campo de busca) |
| EP-018 | Layout vertical com barra de filtros reservada (36px), DependencyDialog implementado |
| EP-019 | StoryTableModel expandido para 13 colunas — filtragem depende das colunas ID, Componente, Status, Feature, Onda |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Risco | QSortFilterProxyModel pode introduzir latencia perceptivel em backlogs > 500 historias | Filtrar com QTimer.singleShot(150ms) debounce no campo de busca. Performance aceitavel para uso single-user (RNF-PERF-001: <= 5s para 100 historias) |
| Risco | Indices de coluna no proxy podem divergir do modelo original, quebrando delegates | Delegates sao atribuidos a view (nao ao proxy) — confirmar que setItemDelegateForColumn() funciona com proxy |
| Risco | Duplicacao pode falhar silenciosamente se UseCase retornar erro | Capturar excecao e exibir mensagem de erro no Status Bar ou dialog de erro padrao (RNF-CONF-002) |
| Risco | Menu de contexto pode conflitar com selecao multipla futura | Implementar para selecao simples; selecao multipla e baixa prioridade (fora do escopo atual) |
| Premissa | DuplicateStoryUseCase esta implementado e funcional no backend | Implementado em EP-008/Application layer |
| Premissa | DependencyDialog do EP-018 aceita ID de historia como parametro | Verificar assinatura do dialog |
| Premissa | PySide6 6.6.1+ suporta QSortFilterProxyModel conforme esperado | Conforme SRS §2.4 |

---

## Especificacoes Tecnicas (Referencia)

### Arquivos Impactados

| Arquivo | Acao | Descricao |
|---------|------|-----------|
| `src/backlog_manager/presentation/views/main_window.py` | EDITAR | Adicionar barra de busca/filtros na zona 3, menu de contexto no right-click, botao Duplicar na toolbar |
| `src/backlog_manager/presentation/viewmodels/filter_proxy_model.py` | CRIAR | QSortFilterProxyModel com filtros compostos: texto (ID/Nome/Componente), status (chips), feature/onda (dropdown) |
| `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` | EDITAR | Adicionar handler para acao Duplicar, wiring ao DuplicateStoryUseCase |
| `tests/unit/presentation/test_filter_proxy_model.py` | CRIAR | Testes unitarios para FilterProxyModel |

### Barra de Busca/Filtros (MW-003) — 36px altura total

```
+---------------------------------------------------------------------------------+
| [icone lupa] Buscar...          [Todos][Backlog(12)][Execucao(5)]... [Feature/Onda v] |
+---------------------------------------------------------------------------------+
```

**Campo de busca:**
- QLineEdit#searchField, 240px largura, Ctrl+F para focar
- Filtra enquanto digita por ID, Nome ou Componente
- QSS: border 1px solid @neutral-300, border-radius @radius-md, padding 6px 12px 6px 32px (espaco para icone de lupa)
- Placeholder: "Buscar por ID, nome ou componente..."
- Debounce: 150ms via QTimer.singleShot

**Chips de status:**
- 6 QPushButton com setCheckable(True), class CSS "filterChip"
- Ativo: bg @primary, cor branca, border @primary
- Inativo: bg @neutral-100, cor @neutral-600, border @neutral-200
- Texto com contagem: "Backlog (12)"
- QSS: border-radius @radius-sm, padding 4px 12px, font-size @font-size-sm

**Dropdown feature/onda:**
- QComboBox com opcao "Todas as features" + lista de features por onda
- Formato: "Onda N - Nome da Feature"

**Layout:**
- QHBoxLayout — busca a esquerda, chips centralizados, dropdown a direita

### Menu de Contexto (MW-007) — right-click na tabela

```
+-------------------------+
| icone Editar (Enter)    |
| icone Duplicar (Ctrl+D) |
+-------------------------+
| icone Mover Acima (Alt+seta) |
| icone Mover Abaixo (Alt+seta)|
+-------------------------+
| icone Dependencias...   |
+-------------------------+
| icone Deletar (Delete)  |  <- cor @error
+-------------------------+
```

- Items de 32px altura
- Separadores agrupam: edicao, priorizacao, relacoes, destrutiva
- "Deletar" com cor de texto @error; demais @neutral-700
- QSS: bg white, border 1px solid @neutral-200, border-radius @radius-md, sombra @shadow-md

### Duplicar Historia (UX-001)

- Wiring ao `DuplicateStoryUseCase` existente
- Resultado: copia com mesmo componente, nome + sufixo " (copia)", mesmos SP e feature
- Posicoes: toolbar Grupo 1 (icone copy.svg), menu de contexto, atalho Ctrl+D
- Sem dialog intermediario — duplicacao imediata
- Feedback na Status Bar: "Historia duplicada: AUTH-001 -> AUTH-004"

### QSortFilterProxyModel (FilterProxyModel)

```python
class FilterProxyModel(QSortFilterProxyModel):
    """Proxy model para filtragem composta do backlog."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._text_filter = ""
        self._status_filter: set[str] = set()  # vazio = todos
        self._feature_id_filter: int | None = None  # None = todas

    def filterAcceptsRow(self, source_row: int, source_parent: QModelIndex) -> bool:
        """Retorna True se a linha passa em todos os filtros."""
        # Combina texto + status + feature (AND)
        ...
```

- Proxy sobre StoryTableModel
- `filterAcceptsRow()` combina texto + status + feature
- Metodos publicos: `set_text_filter()`, `set_status_filter()`, `set_feature_filter()`
- Emite signal quando filtros mudam para atualizar contagens nos chips
