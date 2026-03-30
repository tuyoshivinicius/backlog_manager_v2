# Feature Specification: EP-022 — Polimento e UX Avancado

**Feature Branch**: `022-polimento-ux-avancado`
**Created**: 2026-03-30
**Status**: Draft
**Input**: EP-022 epic — polishing UX with wave grouping, rich tooltips, blocking indicators, SP breakdown, about dialog, cancellation, config persistence, and responsiveness

## User Scenarios & Testing *(mandatory)*

### User Story 1 - SP Breakdown na Status Bar (Priority: P1)

O usuario visualiza na barra de status inferior um resumo detalhado de story points agrupados por status, permitindo avaliar rapidamente a distribuicao do trabalho no backlog.

**Why this priority**: Informacao de distribuicao de SP e a metrica mais consultada pelo gestor de backlog. Visivel permanentemente, sem necessidade de interacao. Entrega valor imediato em toda sessao de uso.

**Independent Test**: Pode ser testado carregando historias com diferentes status e verificando que a status bar exibe o breakdown correto "X SP Backlog · Y SP Execucao · Z SP Concluido" com tooltip de percentuais.

**Acceptance Scenarios**:

1. **Given** backlog com 10 historias (4 BACKLOG=40SP, 3 EXECUCAO=24SP, 3 CONCLUIDO=21SP), **When** a MainWindow carrega, **Then** a status bar exibe "40 SP Backlog · 24 SP Execucao · 21 SP Concluido" e o tooltip exibe percentuais (ex: "Backlog: 47% · Execucao: 28% · Concluido: 25%").
2. **Given** backlog vazio (0 historias), **When** a MainWindow carrega, **Then** a status bar exibe "0 SP Backlog · 0 SP Execucao · 0 SP Concluido".
3. **Given** historias com status TESTES ou IMPEDIDO, **When** a status bar atualiza, **Then** esses status tambem sao incluidos no breakdown (ex: "10 SP Testes · 5 SP Impedido").

---

### User Story 2 - Indicador de Bloqueio na Coluna Dependencias (Priority: P1)

O usuario identifica visualmente quais historias estao bloqueadas por dependencias nao concluidas, vendo um icone vermelho (bloqueada), verde (livre) ou "-" (sem dependencias) na coluna Dependencias.

**Why this priority**: Identificar bloqueios e critico para gestao de backlog. Sem indicador visual, o usuario precisa verificar manualmente o status de cada dependencia, o que e lento e propenso a erros.

**Independent Test**: Pode ser testado criando historias com dependencias em diferentes status e verificando que o delegate renderiza o icone correto.

**Acceptance Scenarios**:

1. **Given** historia A depende de historia B (status BACKLOG), **When** a tabela renderiza, **Then** a coluna Dependencias de A exibe icone vermelho (circulo preenchido) + IDs das dependencias.
2. **Given** historia A depende de historia B (status CONCLUIDO), **When** a tabela renderiza, **Then** a coluna Dependencias de A exibe icone verde (circulo preenchido) + IDs das dependencias.
3. **Given** historia sem dependencias (dependency_ids vazio), **When** a tabela renderiza, **Then** a coluna Dependencias exibe "-" (sem icone).
4. **Given** historia A depende de B (CONCLUIDO) e C (EXECUCAO), **When** a tabela renderiza, **Then** a coluna Dependencias de A exibe icone vermelho (basta uma dependencia nao concluida para bloquear).

---

### User Story 3 - Persistencia de Configuracao via QSettings (Priority: P1)

O usuario configura velocidade, data de inicio e dias ociosos maximo no ConfigDialog, e esses valores sao preservados entre sessoes da aplicacao. Ao reabrir o app, os valores configurados anteriormente estao restaurados.

**Why this priority**: Configurar parametros a cada sessao e frustrante e improdutivo. Persistencia elimina trabalho repetitivo e garante consistencia entre sessoes.

**Independent Test**: Pode ser testado salvando valores no ConfigDialog, simulando reinicio da aplicacao, e verificando que os valores sao restaurados corretamente.

**Acceptance Scenarios**:

1. **Given** usuario altera velocidade para 3.5 e clica Aplicar, **When** a aplicacao e fechada e reaberta, **Then** o ConfigDialog exibe velocidade 3.5.
2. **Given** usuario altera data de inicio para 15/04/2026 e clica Aplicar, **When** a aplicacao e fechada e reaberta, **Then** o ConfigDialog exibe 15/04/2026.
3. **Given** usuario altera max_idle_days para 7 e clica Aplicar, **When** a aplicacao e fechada e reaberta, **Then** o ConfigDialog exibe 7.
4. **Given** valores corrompidos no QSettings (velocidade = 99.0, fora do range 0.1-10.0), **When** a aplicacao inicia, **Then** o valor padrao (2.0) e usado e o valor corrompido e descartado.
5. **Given** nenhum QSettings existe (primeira execucao), **When** a aplicacao inicia, **Then** os valores padrao sao usados (velocidade=2.0, start_date=hoje, max_idle_days=3).

---

### User Story 4 - Agrupamento Visual por Onda na Tabela (Priority: P2)

O usuario visualiza separadores visuais entre ondas na tabela de backlog, facilitando a identificacao de grupos de historias por onda de entrega. Cada separador exibe "Onda N" com fundo diferenciado.

**Why this priority**: Agrupamento visual melhora significativamente a legibilidade em backlogs grandes, mas nao bloqueia funcionalidade — e um refinamento de apresentacao.

**Independent Test**: Pode ser testado carregando historias de multiplas ondas e verificando que separadores visuais aparecem entre grupos de ondas distintas.

**Acceptance Scenarios**:

1. **Given** backlog com historias em ondas 1, 2 e 3, **When** a tabela renderiza, **Then** separadores visuais aparecem entre ondas com texto "Onda 1", "Onda 2", "Onda 3" e fundo diferenciado.
2. **Given** filtro de status ativo (ex: "BACKLOG"), **When** a tabela renderiza historias filtradas, **Then** separadores de onda aparecem corretamente apenas entre ondas presentes nos resultados filtrados.
3. **Given** backlog onde todas as historias pertencem a mesma onda, **When** a tabela renderiza, **Then** apenas um separador aparece no topo do grupo.
4. **Given** historias com wave=0 (sem onda atribuida), **When** a tabela renderiza, **Then** essas historias aparecem sob separador "Sem Onda".

---

### User Story 5 - Tooltip Rico na Tabela (Priority: P2)

O usuario posiciona o mouse sobre uma linha da tabela e, apos 300ms, um mini-card popup aparece com informacoes completas da historia: ID, Nome, Status (com badge), SP, Feature, Desenvolvedor, Dependencias e Datas.

**Why this priority**: Tooltip rico permite consulta rapida sem abrir dialog de edicao. Melhora produtividade mas nao e bloqueante — o usuario pode abrir o dialog para ver detalhes.

**Independent Test**: Pode ser testado posicionando o mouse sobre uma linha e verificando que o popup aparece apos 300ms com todos os campos corretos.

**Acceptance Scenarios**:

1. **Given** mouse sobre linha de historia com todos os campos preenchidos, **When** 300ms passam, **Then** popup aparece com mini-card exibindo ID, Nome, Status (badge colorido), SP, Feature, Desenvolvedor, Dependencias, Data Inicio, Data Fim.
2. **Given** popup visivel, **When** mouse move para outra linha, **Then** popup anterior desaparece e novo popup aparece apos 300ms na nova linha.
3. **Given** popup visivel, **When** mouse sai da tabela, **Then** popup desaparece imediatamente.
4. **Given** historia com campos opcionais vazios (sem desenvolvedor, sem datas), **When** popup aparece, **Then** campos vazios exibem "-" no mini-card.
5. **Given** popup proximo a borda inferior da janela, **When** popup aparece, **Then** popup e reposicionado para cima para nao ultrapassar os limites da janela.

---

### User Story 6 - Cancelamento de Operacoes Longas (Priority: P2)

O usuario pode cancelar operacoes de longa duracao (alocacao, importacao, exportacao) quando o progress dialog esta visivel por mais de 2 segundos. Um botao "Cancelar" aparece e, ao clicar, a operacao e abortada de forma segura.

**Why this priority**: Previne que o usuario fique preso em operacoes longas inesperadas. Importante para UX mas raro em uso normal com backlogs pequenos.

**Independent Test**: Pode ser testado iniciando uma operacao longa simulada e verificando que o botao Cancelar aparece apos 2s e que clicar nele aborta a operacao sem corromper dados.

**Acceptance Scenarios**:

1. **Given** operacao de alocacao em andamento por >2s, **When** progress dialog esta visivel, **Then** botao "Cancelar" aparece no dialog.
2. **Given** botao Cancelar visivel, **When** usuario clica Cancelar, **Then** operacao e abortada, progress dialog fecha, e mensagem "Operacao cancelada" e exibida.
3. **Given** operacao cancelada no meio da execucao, **When** cancelamento completa, **Then** dados nao ficam em estado inconsistente (rollback para estado anterior ao inicio da operacao).
4. **Given** operacao completa em <2s, **When** progress dialog fecha, **Then** botao Cancelar nunca e exibido.

---

### User Story 7 - Dialog "Sobre" (Priority: P3)

O usuario acessa informacoes sobre a aplicacao (nome, versao, tecnologias utilizadas, caminho do banco de dados) via menu Ajuda > Sobre.

**Why this priority**: Informacional, nao afeta funcionalidade. Util para suporte e debug, mas baixo impacto no uso diario.

**Independent Test**: Pode ser testado abrindo o menu Ajuda, clicando em "Sobre", e verificando que o dialog exibe nome, versao, tecnologias e caminho do BD.

**Acceptance Scenarios**:

1. **Given** usuario clica em Ajuda > Sobre, **When** dialog abre, **Then** exibe nome "Backlog Manager", versao (lida de pyproject.toml), versao do Python, lista de tecnologias (Python, PySide6, SQLite), e caminho completo do banco de dados.
2. **Given** aplicacao executada em modo desenvolvimento (sem pacote instalado), **When** dialog Sobre abre, **Then** versao exibe fallback "dev" em vez de erro.
3. **Given** dialog Sobre aberto, **When** usuario clica em "Fechar" ou pressiona Esc, **Then** dialog fecha.

---

### User Story 8 - Responsividade a Resize (Priority: P3)

Quando o usuario redimensiona a janela para largura inferior a 1024px, colunas menos essenciais (Componente, Onda, Duracao) sao automaticamente ocultas para preservar a legibilidade das colunas principais. Um indicador informa que colunas estao ocultas.

**Why this priority**: Caso de borda — a resolucao minima suportada e 1024x600 e a maioria dos usuarios trabalha em resolucoes maiores. Porem garante usabilidade em telas menores.

**Independent Test**: Pode ser testado redimensionando a janela para <1024px e verificando que colunas sao ocultas e restauradas ao voltar a largura original.

**Acceptance Scenarios**:

1. **Given** janela com largura >=1024px, **When** todas as 13 colunas estao visiveis, **Then** nenhuma coluna e oculta.
2. **Given** janela redimensionada para largura <1024px, **When** tabela ajusta, **Then** colunas Componente (4), Onda (2) e Duracao (12) sao ocultas.
3. **Given** colunas ocultas por resize, **When** janela e redimensionada de volta para >=1024px, **Then** colunas ocultas voltam a ser visiveis.
4. **Given** colunas ocultas, **When** usuario observa a tabela, **Then** um indicador sutil (tooltip no header ou label) informa "3 colunas ocultas".

---

### User Story 9 - Validacao de Layout em Resolucao Minima (Priority: P3)

O layout da aplicacao funciona corretamente na resolucao minima de 1024x600 sem sobreposicao ou corte de elementos nas 5 zonas (menu bar, toolbar, filter bar, tabela, status bar).

**Why this priority**: Validacao de edge case. A resolucao minima ja esta configurada (setMinimumSize). Este cenario valida que nenhum elemento e cortado.

**Independent Test**: Pode ser testado configurando a janela para 1024x600 e verificando visualmente que todas as zonas estao visiveis.

**Acceptance Scenarios**:

1. **Given** janela em 1024x600, **When** todas as 5 zonas sao renderizadas, **Then** nenhuma zona sobrepoe outra e todas sao visiveis.
2. **Given** janela em 1024x600, **When** toolbar tem muitos botoes, **Then** toolbar permite scroll horizontal em vez de cortar botoes.
3. **Given** janela em 1024x600, **When** filter bar com chips de status, **Then** todos os chips sao visiveis ou scrollable sem sobreposicao.

---

### Edge Cases

- O que acontece quando o backlog tem 0 historias? O breakdown de SP exibe "0 SP Backlog · 0 SP Execucao · 0 SP Concluido". O tooltip rico nao aparece (sem linhas para hover). O agrupamento por onda nao exibe separadores.
- O que acontece quando uma dependencia referenciada nao existe mais no modelo? O indicador de bloqueio trata dependencias nao encontradas como "nao concluidas" (bloqueada), prevenindo falsos negativos.
- O que acontece quando o QSettings esta corrompido ou inacessivel? Valores padrao sao usados silenciosamente, sem erro para o usuario.
- O que acontece quando a operacao completa exatamente no momento do cancelamento? A operacao completada tem precedencia — resultado e exibido normalmente.
- O que acontece quando o usuario maximiza a janela apos colunas ocultas? As colunas ocultas sao restauradas imediatamente ao ultrapassar o threshold de 1024px.
- O que acontece quando importlib.metadata nao encontra o pacote? O dialog "Sobre" exibe versao "dev" como fallback.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Sistema DEVE exibir breakdown de story points por status na status bar no formato "X SP Status · Y SP Status · Z SP Status" incluindo todos os 5 status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) quando houver historias com esses status.
- **FR-002**: Sistema DEVE exibir tooltip com percentuais ao posicionar o mouse sobre o breakdown de SP na status bar.
- **FR-003**: Sistema DEVE renderizar indicador de bloqueio na coluna Dependencias: icone vermelho circular quando pelo menos uma dependencia nao esta CONCLUIDO, icone verde circular quando todas as dependencias estao CONCLUIDO, e "-" quando nao ha dependencias.
- **FR-004**: Sistema DEVE exibir separadores visuais entre ondas na tabela com texto "Onda N" e fundo diferenciado, funcionando corretamente mesmo com filtros ativos do FilterProxyModel. Separadores sao visiveis apenas quando a tabela esta na ordenacao padrao (coluna Onda ascendente, que e o estado inicial da tabela — detectado via ausencia de sort indicator no header ou sort indicator na coluna Onda); ao ordenar por outra coluna, os separadores sao ocultados. Separadores permanecem visiveis mesmo quando a coluna Onda e oculta por responsividade (FR-013).
- **FR-005**: Sistema DEVE exibir tooltip rico (mini-card popup) apos 300ms de hover sobre uma linha da tabela, contendo: ID, Nome, Status (com badge colorido), SP, Feature, Desenvolvedor, Dependencias, Data Inicio, Data Fim.
- **FR-006**: Sistema DEVE ocultar o tooltip rico quando o mouse move para outra linha ou sai da tabela.
- **FR-007**: Sistema DEVE posicionar o tooltip rico dentro dos limites da janela, ajustando posicao quando proximo a bordas.
- **FR-008**: Sistema DEVE persistir configuracoes (velocidade, data inicio, max dias ociosos) ao clicar "Aplicar" no ConfigDialog e restaura-las ao iniciar a aplicacao.
- **FR-009**: Sistema DEVE validar valores restaurados do QSettings contra ranges validos (velocidade 0.1-10.0, max_idle_days 2-30) e usar valores padrao quando fora do range.
- **FR-010**: Sistema DEVE exibir botao "Cancelar" no ProgressDialog apos 2 segundos de operacao em andamento.
- **FR-011**: Sistema DEVE abortar a operacao de forma segura ao clicar "Cancelar", revertendo para o estado anterior sem corrupcao de dados. Para importacao Excel, o rollback e completo — todas as alteracoes de BD da importacao parcial sao desfeitas, retornando ao estado pre-importacao. Para exportacao, o arquivo parcial e removido. Para alocacao, o modelo em memoria reverte ao estado anterior a chamada de run_allocation() — historias recuperam seus valores pre-alocacao (datas, desenvolvedor, onda); se resultados parciais foram persistidos no BD, o rollback via UnitOfWork desfaz todas as alteracoes.
- **FR-012**: Sistema DEVE exibir dialog "Sobre" via menu Ajuda > Sobre, contendo: nome da aplicacao, versao (lida em runtime), tecnologias utilizadas, e caminho do banco de dados.
- **FR-013**: Sistema DEVE ocultar colunas Componente (4), Onda (2) e Duracao (12) quando a largura da janela for inferior a 1024px, e restaura-las quando a largura voltar a ser >= 1024px.
- **FR-014**: Sistema DEVE exibir indicador de colunas ocultas quando colunas forem ocultadas por resize.
- **FR-015**: Sistema DEVE funcionar sem sobreposicao ou corte de elementos nas 5 zonas do layout na resolucao minima de 1024x600.
- **FR-016**: Operacoes cancelaveis incluem: alocacao, importacao Excel e exportacao Excel. Calculo de cronograma NAO e cancelavel.

### Key Entities

- **SP Breakdown**: Agregacao de story points por status (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO) calculada a partir das historias carregadas no modelo. Nao e uma entidade persistida — e um calculo derivado em tempo real.
- **Blocking State**: Estado de bloqueio de uma historia determinado pela comparacao de suas dependency_ids com o status das historias correspondentes no modelo. Uma historia esta bloqueada se pelo menos uma dependencia nao tem status CONCLUIDO.
- **Config Settings**: Conjunto de configuracoes persistidas: velocity (float), start_date (date), max_idle_days (int). Complementa o padrao in-memory existente (ADR-007) como camada de persistencia.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: O usuario identifica a distribuicao de SP por status em menos de 2 segundos olhando para a status bar, sem necessidade de interacao adicional.
- **SC-002**: O usuario identifica historias bloqueadas por dependencias em menos de 1 segundo olhando para a coluna Dependencias, sem necessidade de verificar manualmente o status de cada dependencia.
- **SC-003**: O usuario consulta detalhes completos de uma historia em menos de 1 segundo via tooltip rico, sem precisar abrir o dialog de edicao.
- **SC-004**: Configuracoes do usuario sao preservadas entre 100% das sessoes da aplicacao, eliminando necessidade de reconfigurar a cada uso.
- **SC-005**: O usuario pode cancelar qualquer operacao longa (alocacao, importacao, exportacao) em ate 1 segundo apos decidir cancelar, sem perda ou corrupcao de dados.
- **SC-006**: O layout da aplicacao funciona sem sobreposicao em 100% dos tamanhos de janela entre 1024x600 e resolucoes maiores.
- **SC-007**: Separadores de onda melhoram a legibilidade do backlog, permitindo ao usuario identificar o grupo de onda de uma historia sem necessidade de ler a coluna Onda individualmente.
- **SC-008**: O dialog "Sobre" fornece todas as informacoes necessarias para suporte (versao, caminho BD) sem que o usuario precise buscar em arquivos de configuracao.
- **SC-009**: 0 regressoes em testes existentes apos implementacao dos novos componentes.
- **SC-010**: Todos os novos componentes visuais respondem em menos de 100ms, garantindo fluidez na interface.

## Traceability Matrix

| Component | RNF | Epic Criteria |
|-----------|-----|---------------|
| UX-005 Agrupamento Visual por Onda | RNF-USAB-004 (curva aprendizado) | Separadores visuais entre ondas com texto "Onda N" |
| UX-006 Tooltip Rico na Tabela | RNF-USAB-003 (tooltips descritivos), RNF-PERF-002 (renderiza <300ms) | Tooltip rico aparece apos 300ms com mini-card completo |
| UX-007 Indicador de Bloqueio | RNF-USAB-003 (indicadores visuais claros) | Indicadores vermelho/verde/"-" na coluna Dependencias |
| UX-008 SP por Status na Status Bar | RNF-PERF-002 (status bar responsiva) | Breakdown "X SP Status" com tooltip de percentuais |
| UX-009 Dialog Sobre | RNF-USAB-004 (curva aprendizado) | Dialog acessivel via menu Ajuda com versao e caminho BD |
| UX-010 Cancelamento de Operacoes | RNF-CONF-002 (recuperacao erros, sem crash) | Cancelamento funcional em operacoes >2s |
| UX-011 Persistencia de Config | RNF-USAB-004 (curva aprendizado) | Config persistida e restaurada entre sessoes |
| RSP-001 Responsividade a Resize | RNF-USAB-002 (resolucao minima — ajustada para 1024x600 neste EP) | Colunas ocultas se janela <1024px |
| RSP-002 Resolucao Minima 1024x600 | RNF-USAB-002 (resolucao minima) | Layout funcional sem sobreposicao em 1024x600 |

## Clarifications

### Session 2026-03-30

- Q: What happens to wave separators when the user sorts by a column other than wave? → A: Separators are only visible when sorted by wave (default order); hidden when sorted by another column.
- Q: For import Excel cancellation, does rollback undo all DB changes or keep already-imported rows? → A: Full rollback — undo all DB changes, backlog returns to pre-import state.
- Q: When the Onda column is hidden due to resize (<1024px), should wave separators still be visible? → A: Yes, separators always visible regardless of Onda column visibility.

## Assumptions

- O maximo de historias no backlog e ~500, conforme estabelecido em EP-019. Calculos de breakdown de SP e estado de bloqueio sao feitos em memoria sem impacto perceptivel de performance.
- O agrupamento visual por onda utiliza custom painting no delegate/view (independente do modelo), evitando conflitos com FilterProxyModel de EP-020.
- O tooltip rico obtem dados exclusivamente do modelo via index — nao realiza consultas adicionais ao banco de dados.
- O cancelamento de operacoes usa pontos seguros de cancelamento (entre iteracoes atomicas), nao no meio de transacoes de banco de dados.
- A persistencia de configuracao usa formato INI para portabilidade, em vez do Registry do Windows.
- A versao da aplicacao e lida em runtime com fallback para "dev" quando o pacote nao esta instalado.
- O caminho do banco de dados e obtido do container de dependencias (que ja possui o db_path).
- O threshold de responsividade (1024px) refere-se a largura total da janela, nao da tabela.
- Toolbar overflow em resolucao minima utiliza scroll horizontal ou agrupamento, sem ocultar botoes criticos.
- O indicador de bloqueio considera que uma dependencia nao encontrada no modelo e tratada como "nao concluida" (bloqueada), por seguranca.
