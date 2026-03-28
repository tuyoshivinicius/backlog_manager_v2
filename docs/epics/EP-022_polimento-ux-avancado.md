# EP-022 — Polimento e UX Avancado (GUI-006)

**Camada:** Interface & Experiencia

---

## Problema que Resolve

Apos os epicos de refatoracao visual (EP-017 a EP-021), a aplicacao tem visual moderno e funcional, mas carece de acabamentos de UX avancado que completam a experiencia do usuario. Especificamente:

- Nao ha agrupamento visual por onda na tabela, dificultando a visualizacao de ondas de entrega (relacionado a UC-005)
- Nao ha tooltip rico ao hover sobre linhas da tabela, exigindo clicks para ver detalhes
- Nao ha indicador de bloqueio por dependencia na coluna Dependencias, dificultando identificacao de historias prontas para execucao (relacionado a RF-DEP-001)
- A Status Bar nao mostra breakdown de SP por status, perdendo visibilidade de progresso
- Nao ha dialog "Sobre" com informacoes da aplicacao
- Operacoes longas (alocacao, import/export) nao oferecem cancelamento, frustrando o usuario em caso de espera
- Configuracoes nao persistem entre sessoes via QSettings, exigindo reconfiguracao a cada uso
- O layout nao se adapta a resolucoes menores que 1280x720, limitando uso em notebooks menores

Estas lacunas impactam RNF-USAB-002 (resolucao minima), RNF-USAB-004 (curva de aprendizado), RNF-PERF-002 (responsividade) e RNF-CONF-002 (recuperacao de erros via cancelamento).

## Objetivo (Valor Mensuravel)

Adicionar camada de polimento de UX avancado que completa a experiencia visual e interativa da aplicacao:

- Agrupamento visual por onda (separadores na tabela entre ondas)
- Tooltip rico (mini-card no hover com dados completos da historia)
- Indicador de bloqueio na coluna Dependencias (icone vermelho/verde)
- Breakdown de SP por status na Status Bar
- Dialog "Sobre" com informacoes da aplicacao
- Cancelamento de operacoes longas (>2s)
- Persistencia de configuracao via QSettings (velocidade, data inicio, max_idle_days)
- Responsividade para resolucao minima 1024x600

**Metricas de sucesso:**
- Separadores visuais entre ondas visiveis na tabela
- Tooltip rico aparece apos 300ms de hover
- Indicadores de bloqueio (vermelho/verde) funcionais na coluna Dependencias
- SP por status visivel na Status Bar com tooltip de percentuais
- Dialog "Sobre" acessivel via menu Ajuda
- Cancelamento funcional em operacoes >2s
- Configuracao persistida e restaurada entre sessoes
- Layout funcional em 1024x600 sem sobreposicao ou corte
- Testes existentes continuam passando sem regressao

## Alinhamento Estrategico

Conexao com as capacidades do produto definidas na secao 2.2 do SRS:
- **Capacidade 1 (Gestao de Backlog)**: Agrupamento por onda, tooltip rico, indicador de bloqueio melhoram visualizacao
- **Capacidade 2 (Gestao de Features)**: Separadores por onda facilitam organizacao visual de features
- **Capacidade 4 (Gestao de Dependencias)**: Indicador de bloqueio mostra claramente historias com deps pendentes
- **Capacidade 6 (Alocacao Automatica)**: Cancelamento de operacoes longas, breakdown de SP na Status Bar
- **Transversal**: Persistencia de configuracao, responsividade, dialog "Sobre"

## Personas Impactadas

| Persona (SRS §2.3) | Impacto |
|--------------------|---------|
| Scrum Master / Tech Lead | Agrupamento por onda e indicador de bloqueio agilizam planejamento diario; cancelamento evita espera em operacoes lentas |
| Gerente de Projeto | Breakdown de SP por status fornece visao rapida de progresso; tooltip rico facilita revisao de backlog |
| Product Owner | Interface mais polida para apresentacao a stakeholders; dialog "Sobre" profissionaliza a aplicacao |

## Jornadas / Casos de Uso Afetados

- UC-001: Criar e Priorizar Backlog — contribui para (agrupamento por onda, tooltip rico)
- UC-002: Alocacao Automatica com Dependencias — contribui para (indicador de bloqueio, breakdown SP, cancelamento)
- UC-003: Detectar e Resolver Deadlock — contribui para (indicador de bloqueio mostra deps nao concluidas)
- UC-004: Importar Backlog do Excel — contribui para (cancelamento de operacoes longas)
- UC-005: Gerenciar Ondas de Entrega — contribui para (agrupamento visual por onda)
- CT-001 a CT-005: executaveis com UX avancado completo

---

## Escopo

### Dentro do Escopo

**Requisitos Funcionais:**
- Nenhum RF novo — implementacao tecnica de polimento de UX

**Requisitos Nao-Funcionais:**
- RNF-USAB-002: Resolucao Minima — interface funcional em 1024x600
- RNF-USAB-003: Acessibilidade Basica — tooltips descritivos, indicadores visuais claros
- RNF-USAB-004: Curva de Aprendizado — configuracao persistida, interface intuitiva
- RNF-PERF-002: Responsividade UI — tooltip rico renderiza em <300ms
- RNF-CONF-002: Recuperacao de Erros — cancelamento de operacoes previne espera infinita

**Artefatos Estruturais:**
- Arquitetura em camadas (SRS §6.1): Camada Presentation
- Padroes UI/UX (Constitution §XIX): MVVM, QSettings para persistencia

**Componentes a implementar:**

| ID      | Componente                   | Tipo   | Descricao |
|---------|------------------------------|--------|-----------|
| UX-005  | Agrupamento Visual por Onda  | NOVO   | Separadores visuais na tabela entre ondas (header de grupo com fundo diferenciado) |
| UX-006  | Tooltip Rico na Tabela       | NOVO   | QFrame popup com mini-card: ID, Nome, Status, SP, Feature, Desenvolvedor, Dependencias, Datas |
| UX-007  | Indicador de Bloqueio        | NOVO   | Icone na coluna Dependencias: vermelho (bloqueada), verde (livre), "-" (sem deps) |
| UX-008  | SP por Status na Status Bar  | NOVO   | Breakdown "120 SP Backlog · 80 SP Execucao · 84 SP Concluido" com tooltip percentual |
| UX-009  | Dialog Sobre                 | NOVO   | Menu Ajuda → Sobre: nome, versao, tecnologias, caminho BD |
| UX-010  | Cancelamento de Operacoes    | NOVO   | Botao [Cancelar] em progress dialogs de operacoes >2s |
| UX-011  | Persistencia de Config       | NOVO   | QSettings para salvar/restaurar velocidade, data inicio, max_idle_days |
| RSP-001 | Responsividade a resize      | NOVO   | Colunas Componente, Onda, Duracao ocultas se janela <1024px |
| RSP-002 | Resolucao minima 1024x600    | NOVO   | setMinimumSize(1024, 600), validar layout sem cortes |

### Fora do Escopo

- Drag & Drop para Priorizacao → baixa prioridade, versao futura
- Selecao Multipla + Operacoes em Lote → baixa prioridade, versao futura
- Tema Escuro → baixa prioridade, versao futura (tokens ja suportam via theme.py)
- Undo/Redo → baixa prioridade, versao futura

---

## Requisitos Funcionais Principais

| ID | Nome | Prioridade |
|----|------|------------|
| — | Nenhum RF novo — implementacao tecnica de polimento UX | — |

## Requisitos Nao-Funcionais Criticos

| ID | Nome | Metrica-alvo |
|----|------|-------------|
| RNF-USAB-002 | Resolucao Minima | Interface funcional em 1024x600 sem cortes |
| RNF-USAB-003 | Acessibilidade Basica | Tooltips descritivos, indicadores visuais claros |
| RNF-USAB-004 | Curva de Aprendizado | Configuracao persistida entre sessoes |
| RNF-PERF-002 | Responsividade UI | Tooltip rico renderiza em <300ms |
| RNF-CONF-002 | Recuperacao de Erros | Cancelamento funcional em operacoes >2s |

---

## Criterios de Aceite (Alto Nivel)

- [ ] **Dado** tabela com historias em multiplas ondas, **Quando** visualizo a tabela, **Entao** separadores visuais entre ondas sao exibidos com texto "Onda N — Nome"
- [ ] **Dado** hover sobre linha da tabela por 300ms, **Quando** tooltip aparece, **Entao** mini-card exibe ID, Nome, Status, SP, Feature, Desenvolvedor, Dependencias, Datas
- [ ] **Dado** historia com dependencias nao concluidas, **Quando** visualizo coluna Dependencias, **Entao** icone vermelho indica bloqueio
- [ ] **Dado** historia com todas dependencias concluidas, **Quando** visualizo coluna Dependencias, **Entao** icone verde indica livre para execucao
- [ ] **Dado** Status Bar visivel, **Quando** existem historias com diferentes status, **Entao** breakdown "X SP Backlog · Y SP Execucao · Z SP Concluido" e exibido
- [ ] **Dado** menu Ajuda aberto, **Quando** clico em "Sobre", **Entao** dialog exibe nome, versao, tecnologias e caminho BD
- [ ] **Dado** operacao de alocacao em execucao por >2s, **Quando** progress dialog aparece, **Entao** botao [Cancelar] esta disponivel e funcional
- [ ] **Dado** configuracao alterada (velocidade, data inicio, max_idle_days), **Quando** fecho e reabro a aplicacao, **Entao** configuracao esta restaurada
- [ ] **Dado** janela redimensionada para <1024px largura, **Quando** visualizo tabela, **Entao** colunas Componente, Onda, Duracao estao ocultas
- [ ] **Dado** resolucao 1024x600, **Quando** todas as zonas do layout sao visiveis, **Entao** nenhuma sobreposicao ou corte ocorre

## KPIs / Metricas de Sucesso

| KPI | Metrica | Meta | Fonte SRS |
|-----|---------|------|-----------|
| Separadores por onda | % tabelas com multiplas ondas que exibem separadores | 100% | UC-005 |
| Tooltip rico | Tempo de aparicao apos hover | <= 300ms | RNF-PERF-002 |
| Indicador de bloqueio | % historias com deps que exibem indicador correto | 100% | RF-DEP-001 |
| Persistencia de config | % configuracoes restauradas corretamente | 100% | RNF-USAB-004 |
| Responsividade | Testes em 1024x600 sem cortes | Pass | RNF-USAB-002 |
| Cancelamento | Operacoes cancelaveis em <500ms | Pass | RNF-CONF-002 |

## Plano de Validacao

| Tipo | Descricao | Referencia SRS |
|------|-----------|----------------|
| Teste Manual | Com multiplas ondas: verificar separadores visuais na tabela | UC-005 |
| Teste Manual | Hover sobre linha: mini-card aparece apos 300ms com dados corretos | RNF-PERF-002 |
| Teste Manual | Historia com deps nao concluidas: icone vermelho visivel | RF-DEP-001 |
| Teste Manual | Status Bar: breakdown SP por status, tooltip com percentuais | — |
| Teste Manual | Menu Ajuda → Sobre: dialog com informacoes corretas | — |
| Teste Manual | Redimensionar janela para 1024x600: layout funcional sem cortes | RNF-USAB-002 |
| Teste Manual | Alterar configuracao, fechar/reabrir: configuracao restaurada | RNF-USAB-004 |
| Teste Manual | Executar alocacao longa, clicar Cancelar: operacao abortada | RNF-CONF-002 |
| Teste Unitario | QSettings: gravar e ler valores de configuracao | RNF-USAB-004 |
| Teste Unitario | Calculo de SP breakdown por status | — |
| Revisao de Codigo | QSettings nao acessa dominio/infra (restricao de camada) | Constitution §I |
| Revisao de Codigo | Tooltip rico usa QFrame, nao QToolTip nativo | — |

---

## Dependencias

| Epico | Motivo |
|-------|--------|
| EP-017 | Design System (DS-001/DS-002): tokens de cor para separadores, indicadores, tooltip |
| EP-018 | Layout Principal (MW-005/MW-006): Status Bar para breakdown SP, layout vertical para responsividade |
| EP-019 | Tabela de Backlog (MW-004): tabela expandida 13 colunas para agrupamento por onda, tooltip rico, indicador bloqueio |
| EP-020 | Busca, Filtros e Menu de Contexto (MW-003): filtros compativeis com agrupamento por onda |
| EP-021 | Estilizacao de Dialogs (DLG-008): progress dialogs base para adicionar cancelamento |

## Riscos e Premissas

| Tipo | Descricao | Mitigacao |
|------|-----------|-----------|
| Risco | Agrupamento por onda na tabela pode conflitar com QSortFilterProxyModel (filtros de EP-020) | Implementar agrupamento na view (painting) e nao no modelo, para funcionar independente do proxy |
| Risco | Tooltip rico (QFrame popup) pode ficar posicionado fora da tela em resolucoes menores | Calcular posicao relativa a celula + ajustar para manter dentro dos bounds da janela |
| Risco | Cancelamento de operacoes assincronas pode deixar dados em estado inconsistente | Usar cancellation tokens no qasync. Se cancelamento nao for seguro, desabilitar o botao e exibir aviso |
| Risco | QSettings pode armazenar dados em local inesperado em ambientes corporativos | Documentar local de armazenamento (Registry no Windows). Usar QSettings.IniFormat como alternativa se necessario |
| Risco | Ocultar colunas ao resize pode confundir o usuario se nao houver indicacao visual | Adicionar indicador sutil na tabela ("3 colunas ocultas") ou tooltip no header |
| Premissa | EP-017 a EP-021 estao completos e funcionais | — |
| Premissa | PySide6 6.6.1+ suporta QSettings e QGraphicsDropShadowEffect conforme esperado | — |
| Premissa | Tooltip rico via QFrame permite layout complexo com grid 2 colunas | — |

---

## Especificacoes Tecnicas Detalhadas

### UX-005: Agrupamento Visual por Onda

- Separadores visuais entre ondas: linha de grupo com fundo diferenciado (@neutral-100)
- Texto "Onda N — Nome da Feature" em @neutral-500, weight 600, font-size @font-size-sm
- Implementar via custom painting no QTableView ou via rows de separacao no modelo
- Separadores devem ser nao-selecionaveis e nao-editaveis

### UX-006: Tooltip Rico na Tabela

- QFrame popup (nao QToolTip nativo — permite layout complexo)
- Conteudo: grid 2 colunas com ID (monospace), Nome, Status (badge), SP, Feature, Desenvolvedor, Dependencias, Inicio/Fim
- Dimensoes: min 280px largura, altura automatica
- Border-radius: @radius-xl (12px), sombra @shadow-md, fundo @neutral-0, border 1px solid @neutral-200
- Aparece apos 300ms de hover, desaparece ao mover o mouse para outra linha

### UX-007: Indicador de Bloqueio

- Icone na coluna Dependencias:
  - Vermelho (ou icone warning): historia tem dependencias nao concluidas (bloqueada)
  - Verde (ou icone check): todas as dependencias concluidas (livre para execucao)
  - "-": sem dependencias
- Implementar via QStyledItemDelegate ou formatacao condicional no `data()` com DecorationRole

### UX-008: SP por Status na Status Bar

- Expandir contadores na Status Bar: "120 SP Backlog · 80 SP Execucao · 84 SP Concluido"
- Tooltip no label: "Backlog: 42% · Execucao: 28% · Concluido: 30%"

### UX-009: Dialog Sobre

- Dimensoes: ~400x300px
- Conteudo: nome "Backlog Manager v2", versao (lida de pyproject.toml), tecnologias "Python 3.11 + PySide6", caminho do banco de dados
- Botao [OK]

### UX-010: Cancelamento de Operacoes

- Progress dialogs (cronograma, alocacao, import/export) incluem botao [Cancelar] se operacao > 2s
- Ao cancelar: abortar operacao, restaurar estado anterior, fechar dialog

### UX-011: Persistencia de Configuracao

- Via QSettings (mecanismo nativo do Qt)
- Valores: velocidade (SP/dia), data de inicio, max_idle_days
- Salvar ao clicar [Aplicar] no ConfigDialog
- Restaurar ao abrir a aplicacao (antes de exibir a MainWindow)

### RSP-001: Responsividade a Resize

- Se `window.width() < 1024px`: ocultar colunas Componente (4), Onda (2), Duracao (12)
- Toolbar: se botoes nao couberem, agrupar em overflow menu (QToolBar extension)

### RSP-002: Resolucao Minima 1024x600

- `setMinimumSize(1024, 600)` na MainWindow
- Validar que todas as 5 zonas ficam visiveis sem sobreposicao

---

## Arquivos Impactados

| Arquivo | Acao | Descricao |
|---------|------|-----------|
| `src/backlog_manager/presentation/views/main_window.py` | EDITAR | Agrupamento por onda (row painting/delegate), tooltip rico (QFrame popup), indicador bloqueio, SP breakdown na Status Bar, responsividade, setMinimumSize |
| `src/backlog_manager/presentation/viewmodels/story_table_model.py` | EDITAR | Suporte a agrupamento por onda (sections), dados para tooltip rico, dados de bloqueio por dependencia |
| `src/backlog_manager/presentation/views/about_dialog.py` | CRIAR | QDialog "Sobre" (nome, versao, tecnologias, caminho BD) |
| `src/backlog_manager/presentation/views/config_dialog.py` | EDITAR | Integrar QSettings para salvar/restaurar valores de configuracao |
| `src/backlog_manager/presentation/delegates/blocking_indicator_delegate.py` | CRIAR | QStyledItemDelegate para indicador de bloqueio (vermelho/verde/-) |
