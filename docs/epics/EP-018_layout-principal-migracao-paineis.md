# EP-018 — Layout Principal e Migracao de Paineis (GUI-002)

**Camada:** Interface & Experiencia

---

## Problema que Resolve

A MainWindow implementada em EP-008 utiliza um QSplitter horizontal onde a tabela ocupa 70% e os paineis laterais (ConfigPanel, DependencyPanel, MetricsPanel, WarningsPanel) ocupam 30%. Nao existe Menu Bar nem Status Bar. A toolbar usa apenas texto sem icones e sem agrupamento visual. O layout desperdiça espaço lateral e nao corresponde ao padrao moderno de aplicacoes desktop (layout vertical com zonas empilhadas). Os paineis laterais devem ser migrados para dialogs modais para liberar 100% da largura para a tabela, conforme padroes de usabilidade (RNF-USAB-002, RNF-USAB-004).

## Objetivo (Valor Mensuravel)

Transformar a MainWindow em layout vertical de 5 zonas:
- Menu Bar (28px) → Toolbar (44px) → Barra de Filtros (36px, reservada) → Tabela (stretch) → Status Bar (24px)

**Entregas concretas:**
- Menu Bar com 4 menus funcionais (Arquivo, Cadastros, Ferramentas, Ajuda)
- Toolbar refatorada com icones SVG do EP-017, 5 grupos separados, ToolButtonTextBesideIcon
- Status Bar com contadores (historias, SP, ultima alocacao) e area de avisos (migra WarningsPanel)
- ConfigPanel, DependencyPanel, MetricsPanel migrados para dialogs modais
- Remocao do QSplitter horizontal — tabela ocupa 100% da largura

**Metricas de sucesso:**
- 100% das acoes acessiveis via menu E via toolbar
- Todos os paineis laterais convertidos em dialogs modais
- Testes existentes continuam passando sem regressao
- Tempo de inicializacao <= 3s (RNF-PERF-004)

## Alinhamento Estrategico

Conexao com as capacidades do produto definidas na secao 2.2 do SRS:
- **Capacidade 1 (Gestao de Backlog)**: Tabela ocupa 100% da largura, melhor visualizacao
- **Capacidade 4 (Gestao de Dependencias)**: DependencyDialog acessivel via menu/toolbar
- **Capacidade 5 (Calculo de Cronograma)**: ConfigDialog com parametros de velocidade/data
- **Capacidade 6 (Alocacao Automatica)**: MetricsDialog exibido apos alocacao, Status Bar com avisos

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Fluxo de trabalho diario otimizado — acoes rapidas via toolbar, menus com atalhos |
| Gerente de Projeto | Visualizacao de metricas em dialog modal, avisos na Status Bar |
| Product Owner | Interface mais profissional para apresentacao, navegacao por menus intuitiva |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — contribui para (melhor visualizacao da tabela)
- UC-002: Alocacao Automatica com Dependencias — contribui para (MetricsDialog pos-alocacao)
- UC-003: Detectar e Resolver Deadlock — contribui para (avisos na Status Bar)
- UC-005: Gerenciar Ondas de Entrega — contribui para (ConfigDialog para parametros)
- CT-001 a CT-005: executaveis com nova estrutura de navegacao

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- Nenhum RF novo — epico de refatoracao de UI para RFs ja implementados em EP-008

**Requisitos Nao-Funcionais:**
- RNF-USAB-002: Resolucao minima 1366x768 (layout vertical funcional)
- RNF-USAB-003: Acessibilidade (atalhos de teclado nos menus, tooltips com shortcuts)
- RNF-USAB-004: Curva de aprendizado <= 15 minutos (navegacao intuitiva)
- RNF-PERF-002: Responsividade UI <= 100ms para operacoes CRUD
- RNF-PERF-004: Tempo de startup <= 3s
- RNF-CONF-002: Recuperacao de erros (dialogs nao crasham aplicacao)

**Artefatos Estruturais:**
- Arquitetura em camadas (SRS §6.1): Refatoracao na camada Presentation
- Padroes UI/UX (Constitution §XIX): MVVM com separacao View/ViewModel
- Atalhos de teclado (SRS Apendice B): Todos mapeados nos menus

**Componentes a implementar:**

| ID      | Componente           | Tipo          | Descricao |
|---------|----------------------|---------------|-----------|
| MW-001  | Menu Bar             | NOVO          | QMenuBar com 4 menus: Arquivo (Importar/Exportar/Sair), Cadastros (Historias/Features/Devs/Configuracao), Ferramentas (Cronograma/Alocacao), Ajuda (Sobre) |
| MW-002  | Toolbar              | REFATORACAO   | Adicionar icones SVG (QIcon), ToolButtonTextBesideIcon, 5 grupos com separadores, altura 32px |
| MW-005  | Status Bar           | NOVO          | QStatusBar: contadores a esquerda, avisos a direita com popup, migra WarningsPanel |
| MW-006  | Layout Vertical      | REFATORACAO   | Remover QSplitter horizontal, converter para QVBoxLayout com 5 zonas |
| DLG-004 | ConfigDialog         | MIGRACAO      | ConfigPanel → QDialog modal (velocidade, data inicio, max dias ociosos) |
| DLG-005 | DependencyDialog     | MIGRACAO      | DependencyPanel → QDialog modal (secoes "Depende de" e "Dependentes") |
| DLG-006 | MetricsDialog        | MIGRACAO      | MetricsPanel → QDialog modal (grid de metricas, auto-show pos-alocacao) |

### Fora do Escopo

- Barra de Busca/Filtros (espaco reservado mas vazio) → sera tratado em EP-020 (GUI-004)
- Expansao da tabela para 13 colunas → sera tratado em EP-019 (GUI-003)
- Estilizacao fina dos dialogs StoryDialog, DeveloperDialog, FeatureDialog → sera tratado em EP-021 (GUI-005)
- Acao "Duplicar" na toolbar (botao reservado mas sem wiring completo) → sera tratado em EP-020 (GUI-004)
- Dialog "Sobre" → sera tratado em EP-022 (GUI-006)

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Nenhum RF novo — refatoracao de UI | — |

**Funcionalidades de UI refatoradas:**

| Componente | Descricao | RFs Relacionados (EP-008) |
|------------|-----------|---------------------------|
| Menu Bar | 4 menus com atalhos de teclado | RF-STORY-001/002/003, RF-DEV-001/002/003, RF-FEAT-001/002/003 |
| Toolbar | Icones SVG + texto, 5 grupos | RF-STORY-006, RF-ALOC-001 |
| Status Bar | Contadores + avisos | RF-ALOC-007/008/011 |
| ConfigDialog | Parametros de velocidade/data | RF-SCHED-001, RF-ALOC-009 |
| DependencyDialog | Gestao de dependencias | RF-DEP-001/002 |
| MetricsDialog | Metricas de alocacao | RF-ALOC-011 |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-USAB-002 | Resolucao Minima | 1366x768 sem cortes com novo layout |
| RNF-USAB-003 | Acessibilidade | Atalhos de teclado em todos os menus |
| RNF-USAB-004 | Curva de Aprendizado | <= 15 minutos (menus intuitivos) |
| RNF-PERF-002 | Responsividade UI | <= 100ms abertura de dialogs |
| RNF-PERF-004 | Tempo de Startup | <= 3s cold start |
| RNF-CONF-002 | Recuperacao de Erros | Dialogs nao crasham aplicacao |

---

## Criterios de Aceite (Alto Nivel)

### Layout e Estrutura
- [ ] **Dado** aplicacao iniciada, **Quando** verifico layout, **Entao** vejo 5 zonas empilhadas: Menu Bar, Toolbar, Barra Filtros (vazia), Tabela, Status Bar
- [ ] **Dado** QSplitter horizontal, **Quando** verifico codigo, **Entao** foi removido — tabela ocupa 100% da largura

### Menu Bar
- [ ] **Dado** Menu Bar, **Quando** inspeciono menus, **Entao** vejo Arquivo, Cadastros, Ferramentas, Ajuda
- [ ] **Dado** menu Arquivo, **Quando** clico Importar (Ctrl+I), **Entao** acao e executada
- [ ] **Dado** menu Ferramentas, **Quando** clico Alocar Desenvolvedores (Ctrl+Shift+A), **Entao** alocacao e executada

### Toolbar
- [ ] **Dado** toolbar, **Quando** inspeciono botoes, **Entao** vejo icones SVG do EP-017 + texto ao lado
- [ ] **Dado** toolbar, **Quando** verifico grupos, **Entao** vejo 5 grupos separados por separadores visuais
- [ ] **Dado** hover em botao, **Quando** leio tooltip, **Entao** inclui atalho de teclado (ex: "Nova Historia (Ctrl+N)")

### Status Bar
- [ ] **Dado** Status Bar, **Quando** inspeciono conteudo, **Entao** vejo contadores de historias e SP
- [ ] **Dado** alocacao executada, **Quando** verifico Status Bar, **Entao** mostra "Ultima alocacao: DD/MM/YYYY HH:MM"
- [ ] **Dado** avisos detectados, **Quando** clico na area de avisos, **Entao** popup exibe lista completa

### Dialogs Migrados
- [ ] **Dado** menu Cadastros → Configuracao, **Quando** clico, **Entao** ConfigDialog abre como modal
- [ ] **Dado** ConfigDialog, **Quando** altero velocidade e clico Aplicar, **Entao** valor e persistido
- [ ] **Dado** historia selecionada e acao Dependencias, **Quando** executo, **Entao** DependencyDialog abre
- [ ] **Dado** alocacao completa com sucesso, **Quando** verifico, **Entao** MetricsDialog surge automaticamente

### Compatibilidade
- [ ] **Dado** testes existentes do EP-008, **Quando** executo suite, **Entao** todos passam sem regressao
- [ ] **Dado** resolucao 1366x768, **Quando** abro aplicacao, **Entao** layout funcional sem cortes

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Acoes via menu | % de acoes acessiveis | 100% | RNF-USAB-003 |
| Atalhos de teclado | Atalhos mapeados | Todos do Apendice B | RNF-USAB-003 |
| Startup time | Segundos | <= 3s | RNF-PERF-004 |
| Abertura de dialog | Milissegundos | <= 100ms | RNF-PERF-002 |
| Regressao | Testes falhando | 0 | RNF-MANT-001 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Teste Manual | Navegar por todos os menus e verificar acoes | RNF-USAB-003 |
| Teste Manual | Verificar toolbar: icones renderizados, separadores visiveis | RNF-USAB-003 |
| Teste Manual | Abrir ConfigDialog via menu, alterar valores, aplicar/cancelar | RF-SCHED-001 |
| Teste Manual | Abrir DependencyDialog via toolbar/menu, adicionar/remover dependencia | RF-DEP-001/002 |
| Teste Manual | Executar Alocar Desenvolvedores e verificar MetricsDialog automatico | RF-ALOC-001/011 |
| Teste Manual | Verificar Status Bar: contadores, area de avisos, popup | RF-ALOC-007/008 |
| Teste Manual | Verificar todos os atalhos de teclado | Apendice B |
| Teste Manual | Testar em resolucao 1366x768 | RNF-USAB-002 |
| Teste Unitario | MainWindow instancia sem erro com novo layout | RNF-CONF-002 |
| Teste Unitario | ConfigDialog: valores padrao, validacao de range, signals | RF-SCHED-001 |
| Teste Unitario | MetricsDialog: renderiza metricas corretamente | RF-ALOC-011 |
| Revisao de Codigo | Confirmar remocao de imports de paineis deprecados | RNF-MANT-001 |
| Revisao de Codigo | Validar separacao View/ViewModel nos novos dialogs | Constitution §XIX |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-008 | Interface grafica basica implementada — GUI-002 refatora a estrutura existente |
| EP-017 | QSS centralizado (estilizacao dos novos widgets), icones SVG (toolbar), theme.py (cores da Status Bar) |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Risco | Migracao simultanea de 4 paineis + reestruturacao do layout pode gerar regressao dificil de isolar | Migrar paineis um a um: ConfigPanel → DependencyPanel → MetricsPanel → WarningsPanel. Testar apos cada migracao |
| Risco | Popup de avisos na Status Bar (QFrame fixado acima) pode ter problemas de posicionamento cross-platform | Usar QWidget com setWindowFlags(Qt.Popup) e calcular posicao relativa a Status Bar. Testar em multiplas resolucoes |
| Risco | Remocao do QSplitter pode quebrar logica de resize que dependia do splitter | Verificar que nenhum ViewModel ou UseCase referencia diretamente o splitter ou seus widgets filhos |
| Risco | MetricsDialog auto-show pos-alocacao pode interferir com fluxo se alocacao falhar | Exibir MetricsDialog apenas quando alocacao completa com sucesso. Em caso de erro, exibir dialog de erro |
| Premissa | PySide6 6.6.1+ suporta QMenuBar, QStatusBar, QToolBar conforme esperado | Conforme SRS §2.4 |
| Premissa | Icones SVG do EP-017 ja estao disponiveis em assets/icons/ | Dependencia explicita de EP-017 |
| Premissa | Atalhos de teclado nao conflitam com atalhos do sistema Windows | Usar combinacoes nao padrao (Alt+Up, Ctrl+Shift+A) conforme EP-008 |

---

## Especificacoes Tecnicas (Referencia)

### Arquivos Impactados

| Arquivo | Acao | Descricao |
|---------|------|-----------|
| `src/backlog_manager/presentation/views/main_window.py` | EDITAR | Refatoracao maior: adicionar QMenuBar, refatorar QToolBar com icones, adicionar QStatusBar, remover QSplitter, layout vertical |
| `src/backlog_manager/presentation/views/config_dialog.py` | CRIAR | QDialog modal migrando logica de config_panel.py |
| `src/backlog_manager/presentation/views/dependency_dialog.py` | CRIAR | QDialog modal migrando logica de dependency_panel.py |
| `src/backlog_manager/presentation/views/metrics_dialog.py` | CRIAR | QDialog modal migrando logica de metrics_panel.py |
| `src/backlog_manager/presentation/views/config_panel.py` | DEPRECAR | Manter arquivo mas remover uso em main_window.py |
| `src/backlog_manager/presentation/views/dependency_panel.py` | DEPRECAR | Manter arquivo mas remover uso em main_window.py |
| `src/backlog_manager/presentation/views/metrics_panel.py` | DEPRECAR | Manter arquivo mas remover uso em main_window.py |
| `src/backlog_manager/presentation/views/warnings_panel.py` | DEPRECAR | Funcionalidade migra para Status Bar |
| `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` | EDITAR | Ajustar wiring para novos dialogs e status bar |
| `src/backlog_manager/presentation/viewmodels/allocation_viewmodel.py` | EDITAR | Wiring para exibir MetricsDialog automaticamente pos-alocacao |

### Layout Vertical de 5 Zonas (1280x720)

```
+--------------------------------------------------+
| MENU BAR (28px altura fixa)                      |
+--------------------------------------------------+
| TOOLBAR (44px altura fixa)                       |
+--------------------------------------------------+
| BARRA DE FILTROS (36px, reservar espaco vazio)   |
+--------------------------------------------------+
| TABELA DE BACKLOG (~588px, stretch)              |
+--------------------------------------------------+
| STATUS BAR (24px altura fixa)                    |
+--------------------------------------------------+
```

### Estrutura do Menu Bar

```
Arquivo
  +-- Importar Excel (Ctrl+I)
  +-- Exportar Excel (Ctrl+E)
  +-- Sair

Cadastros
  +-- Historias (Ctrl+N)
  +-- Features
  +-- Desenvolvedores
  +-- Configuracao

Ferramentas
  +-- Calcular Cronograma (Ctrl+Shift+C)
  +-- Alocar Desenvolvedores (Ctrl+Shift+A)

Ajuda
  +-- Sobre
```

### Toolbar — 5 Grupos com Separadores

| Grupo | Acoes | Icones |
|-------|-------|--------|
| 1 — CRUD de Historias | + Nova, Editar, Deletar | plus.svg, pencil-simple.svg, trash.svg |
| 2 — Priorizacao | Mover Cima, Mover Baixo | arrow-up.svg, arrow-down.svg |
| 3 — Cadastros | Desenvolvedores, Features, Configuracao | users.svg, package.svg, gear.svg |
| 4 — Processamento | Calcular Cronograma, Alocar Devs | calendar-check.svg, shuffle.svg |
| 5 — Excel | Importar, Exportar | download-simple.svg, upload-simple.svg |

### Status Bar

- Altura fixa: 24px. Borda superior: 1px solid @neutral-200. Fundo: @neutral-100.
- Fonte: 12px, cor @neutral-600. Separador: " . " em @neutral-300.
- **Area esquerda**: "42 historias", "284 SP", "Ultima alocacao: DD/MM/YYYY HH:MM"
- **Area direita**: Aviso mais critico inline + badge contagem + popup ao clicar

### ConfigDialog (DLG-004) — 420x340px

Campos migrados de ConfigPanel:
- Velocidade (SP/dia): input numerico decimal (0.1 a 10.0, padrao 2.0)
- Data de inicio: date picker (padrao: hoje)
- Max. dias ociosos: input numerico inteiro (2 a 30, padrao 3)
- Botoes [Aplicar] [Cancelar]

### DependencyDialog (DLG-005) — 500x420px

- Titulo: "Dependencias: AUTH-001 — Nome da Historia"
- Secao "Depende de:" com lista + dropdown [+]
- Secao "Dependentes:" somente leitura
- Erro de ciclo: fundo @error-light com mensagem explicativa

### MetricsDialog (DLG-006) — 440x380px

- Titulo: "Metricas da Alocacao"
- Grid 2 colunas (label : valor weight 600)
- Metricas: Historias Alocadas (X/Y), Tempo de Execucao (X.XXs), Ondas Processadas (N), Total de Iteracoes (N), Deadlocks Detectados (N), Violacoes de Ociosidade (N/N)
- Botao [OK]
