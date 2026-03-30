# Feature Specification: Estilizacao de Dialogs

**Feature Branch**: `021-estilizacao-dialogs`
**Created**: 2026-03-29
**Status**: Draft
**Input**: EP-021 — Estilizacao de Dialogs (GUI-005): estilizar todos os dialogs com visual consistente via objectNames + QSS centralizado, adicionar validacao em tempo real (on-blur), campo Desenvolvedor no StoryDialog, estados vazios orientativos, e feedback estilizado de import/export.

---

## User Scenarios & Testing

### User Story 1 — Editar Historia com Atribuicao de Desenvolvedor (Priority: P1)

O usuario abre o dialog de edicao de uma historia existente e visualiza um campo "Desenvolvedor" (dropdown) com a lista de desenvolvedores cadastrados e a opcao "Nenhum". O usuario seleciona um desenvolvedor, salva a historia e confirma que a atribuicao foi persistida.

**Why this priority**: Atribuicao manual de desenvolvedor (RF-STORY-007) e funcionalidade de negocio critica que desbloqueia o planejamento de sprints. Sem este campo, o usuario nao consegue atribuir historias a desenvolvedores pela interface.

**Independent Test**: Pode ser testado abrindo o dialog de edicao de historia, verificando que o dropdown esta visivel e populado, selecionando um desenvolvedor, salvando e reabrindo para confirmar persistencia.

**Acceptance Scenarios**:

1. **Given** uma historia existente sem desenvolvedor atribuido, **When** o usuario abre o dialog de edicao, **Then** o campo "Desenvolvedor" aparece com "Nenhum" selecionado e a lista de desenvolvedores cadastrados.
2. **Given** o dialog de edicao aberto com campo Desenvolvedor visivel, **When** o usuario seleciona "Ana Silva" e clica "Salvar", **Then** a historia e salva com o desenvolvedor correspondente.
3. **Given** uma historia com desenvolvedor "Ana Silva" atribuido, **When** o usuario abre o dialog de edicao, **Then** o campo Desenvolvedor pre-seleciona "Ana Silva".
4. **Given** uma historia com desenvolvedor atribuido, **When** o usuario seleciona "Nenhum" e salva, **Then** a historia e salva sem desenvolvedor (desatribuicao).
5. **Given** o dialog de historia aberto em modo criacao, **When** o dialog e exibido, **Then** o campo "Desenvolvedor" NAO e visivel.

---

### User Story 2 — Validacao em Tempo Real nos Campos do Dialog de Historia (Priority: P1)

O usuario preenche o formulario de historia e recebe feedback visual imediato ao sair de campos obrigatorios vazios. Campos obrigatorios sao marcados com asterisco (*) vermelho, e a contagem de caracteres restantes e exibida. O botao Salvar fica desabilitado enquanto o formulario estiver invalido.

**Why this priority**: Validacao em tempo real (RNF-USAB-003, RNF-USAB-004) reduz erros de preenchimento e melhora a experiencia do usuario. Sem isso, o usuario so descobre erros ao clicar Salvar.

**Independent Test**: Pode ser testado abrindo o dialog de historia, clicando em um campo obrigatorio, saindo sem preencher, e verificando que a borda vermelha e a mensagem de erro aparecem. Verificar que o botao Salvar esta desabilitado.

**Acceptance Scenarios**:

1. **Given** o dialog de historia aberto (modo criacao ou edicao), **When** o usuario visualiza os labels, **Then** campos obrigatorios (Componente, Nome) exibem asterisco (*) vermelho ao lado do label.
2. **Given** o campo Componente vazio e com foco, **When** o usuario move o foco para outro campo (focusOut), **Then** o campo Componente exibe borda vermelha e mensagem "Campo obrigatorio" abaixo do campo.
3. **Given** o campo Nome com texto "abc" (3 caracteres), **When** o usuario visualiza a contagem, **Then** exibe "3/200" abaixo do campo.
4. **Given** o campo Componente com 50 caracteres (limite maximo), **When** o usuario visualiza a contagem, **Then** exibe "50/50" em cor de alerta.
5. **Given** campos obrigatorios vazios no formulario, **When** o usuario visualiza o botao Salvar, **Then** o botao esta desabilitado (cinza, nao clicavel).
6. **Given** todos os campos obrigatorios preenchidos e validos, **When** o usuario visualiza o botao Salvar, **Then** o botao esta habilitado.
7. **Given** campo Componente preenchido e valido, **When** o usuario apaga todo o texto e sai do campo, **Then** borda vermelha e mensagem de erro aparecem, e botao Salvar e desabilitado.

---

### User Story 3 — Dialogs com Estilizacao Visual Consistente (Priority: P2)

Todos os dialogs da aplicacao (historia, desenvolvedores, features, confirmacao de exclusao) exibem visual padronizado com bordas arredondadas, espacamento uniforme, e cores do design system, aplicados via identificadores de estilo centralizados.

**Why this priority**: Consistencia visual (RNF-USAB-004) e fundamental para a experiencia profissional da aplicacao, mas nao bloqueia funcionalidade.

**Independent Test**: Pode ser testado abrindo cada dialog e verificando visualmente que o estilo e consistente — bordas arredondadas, espacamento 16px, padding 24px, titulo 16px weight 600.

**Acceptance Scenarios**:

1. **Given** o usuario abre o dialog de historia, **When** o dialog e exibido, **Then** possui bordas arredondadas, espacamento interno 24px, espacamento entre campos 16px, titulo com fonte 16px weight 600.
2. **Given** o usuario abre o dialog de desenvolvedores, **When** o dialog e exibido, **Then** possui estilizacao consistente com o dialog de historia.
3. **Given** o usuario abre o dialog de features, **When** o dialog e exibido, **Then** possui estilizacao consistente.
4. **Given** o usuario abre o dialog de confirmacao de exclusao, **When** o dialog e exibido, **Then** possui estilizacao consistente.
5. **Given** qualquer dialog aberto, **When** verificado, **Then** todos os elementos visuais possuem identificadores de estilo atribuidos para customizacao centralizada.

---

### User Story 4 — Dialog de Desenvolvedores com Icones, Hover e Estado Vazio (Priority: P2)

O dialog de desenvolvedores exibe icones nos botoes de acao, efeito visual ao passar o mouse sobre itens da lista, e uma mensagem orientativa quando a lista esta vazia.

**Why this priority**: Melhora usabilidade e orientacao do usuario (RNF-USAB-003, RNF-USAB-004), mas e aprimoramento visual sobre funcionalidade ja existente.

**Independent Test**: Pode ser testado abrindo o dialog vazio e verificando a mensagem orientativa; adicionando um desenvolvedor e verificando efeito de hover; verificando icones nos botoes.

**Acceptance Scenarios**:

1. **Given** o dialog de desenvolvedores aberto, **When** o usuario visualiza os botoes, **Then** [Adicionar] exibe icone de adicao, [Editar] exibe icone de edicao, [Remover] exibe icone de lixeira, [Fechar] exibe icone de fechar (icones 16x16px).
2. **Given** a lista de desenvolvedores com itens, **When** o usuario posiciona o mouse sobre um item, **Then** o item exibe destaque visual de hover.
3. **Given** a lista de desenvolvedores com itens, **When** o usuario visualiza os itens, **Then** cada item tem altura de 40px.
4. **Given** nenhum desenvolvedor cadastrado, **When** o dialog e aberto, **Then** a area da lista exibe mensagem centralizada "Nenhum desenvolvedor cadastrado. Clique em Adicionar para comecar." em cor neutra.
5. **Given** a lista vazia com mensagem orientativa, **When** o usuario adiciona um desenvolvedor, **Then** a mensagem desaparece e o item aparece na lista.

---

### User Story 5 — Dialog de Features com Formato "Onda N — Nome" e Estado Vazio (Priority: P2)

O dialog de features exibe itens da lista no formato "Onda N — Nome da Feature" e mostra mensagem orientativa quando a lista esta vazia.

**Why this priority**: Melhora legibilidade e orientacao do usuario, mas e aprimoramento visual.

**Independent Test**: Pode ser testado abrindo o dialog com features cadastradas e verificando o formato; abrindo sem features e verificando a mensagem.

**Acceptance Scenarios**:

1. **Given** features cadastradas (ex: "Login" na onda 2), **When** o dialog de features e aberto, **Then** a lista exibe "Onda 2 — Login".
2. **Given** nenhuma feature cadastrada, **When** o dialog e aberto, **Then** a area da lista exibe mensagem centralizada "Nenhuma feature cadastrada. Clique em Adicionar para comecar." em cor neutra.
3. **Given** a lista vazia com mensagem orientativa, **When** o usuario adiciona uma feature, **Then** a mensagem desaparece e o item aparece na lista.

---

### User Story 6 — Dialog de Confirmacao de Exclusao com Alerta Visual (Priority: P2)

O dialog de confirmacao de exclusao exibe icone de alerta, texto descritivo com identificacao da entidade, e botao de confirmacao em vermelho para enfatizar a natureza destrutiva da acao.

**Why this priority**: Melhora a percepcao de risco pelo usuario (RNF-CONF-002), mas a funcionalidade de exclusao ja existe.

**Independent Test**: Pode ser testado abrindo o dialog de confirmacao para uma historia e verificando icone, texto formatado, e cor do botao.

**Acceptance Scenarios**:

1. **Given** o usuario solicita exclusao de uma historia (ID "API-001", nome "Criar endpoint"), **When** o dialog e exibido, **Then** mostra icone de alerta (32x32px) a esquerda e texto "Excluir API-001 — Criar endpoint?" a direita.
2. **Given** o dialog exibido, **When** o usuario visualiza os botoes, **Then** o botao de confirmacao exibe texto "Confirmar Exclusao" com fundo vermelho e texto branco.
3. **Given** o dialog exibido, **When** o usuario visualiza o texto complementar, **Then** exibe "Esta acao nao pode ser desfeita." abaixo do texto principal.
4. **Given** o usuario solicita exclusao de um desenvolvedor (nome "Ana Silva"), **When** o dialog e exibido, **Then** mostra texto "Excluir Ana Silva?" (sem ID numerico exposto).
5. **Given** o usuario solicita exclusao de uma feature (nome "Login", onda 2), **When** o dialog e exibido, **Then** mostra texto "Excluir Onda 2 — Login?".

---

### User Story 7 — Feedback Estilizado de Import/Export Excel (Priority: P3)

Durante importacao de Excel, o usuario visualiza um dialog de progresso com barra estilizada. Ao concluir, um dialog de resultado exibe contagens formatadas. Na exportacao, o resultado exibe o caminho do arquivo gerado.

**Why this priority**: Feedback visual de progresso e resultado melhora a experiencia, mas import/export ja funciona com dialogs genericos.

**Independent Test**: Pode ser testado executando uma importacao de Excel e verificando que o dialog de progresso aparece com barra estilizada, seguido pelo dialog de resultado com contagens.

**Acceptance Scenarios**:

1. **Given** o usuario inicia importacao de Excel, **When** a operacao comeca, **Then** um dialog de progresso modal aparece com barra estilizada e mensagem "Importando historias...".
2. **Given** a importacao em andamento, **When** o progresso atualiza, **Then** a barra de progresso reflete o estado atual e a mensagem atualiza.
3. **Given** a importacao concluida com sucesso, **When** o dialog de progresso fecha, **Then** um dialog de resultado aparece com contagens: "X historia(s) importada(s)", "Y feature(s) criada(s)", "Z aviso(s)" e botao [Fechar].
4. **Given** a exportacao concluida com sucesso, **When** o dialog de resultado e exibido, **Then** mostra "Exportacao concluida com sucesso!" e o caminho do arquivo gerado, com botao [Fechar].
5. **Given** o dialog de progresso exibido, **When** a operacao esta em andamento, **Then** o dialog nao pode ser fechado pelo usuario.

---

### Edge Cases

- O que acontece quando a lista de desenvolvedores esta vazia no dropdown do dialog de historia? O dropdown exibe apenas "Nenhum".
- O que acontece quando o usuario digita alem do limite de caracteres? O campo ja tem limite maximo configurado; a contagem exibe "50/50" em cor de alerta.
- O que acontece se o carregamento de desenvolvedores falha com erro? Uma mensagem de erro e exibida e o campo Desenvolvedor mostra apenas "Nenhum".
- O que acontece quando o usuario clica Salvar com erro de validacao ainda visivel? O botao Salvar esta desabilitado enquanto houver erros, impedindo a acao.
- O que acontece quando import/export e sincrono e bloqueia a interface? O dialog de progresso usa barra em modo indeterminado para operacoes sem percentual granular, mantendo feedback visual mesmo com bloqueio breve.
- O que acontece se o desenvolvedor atribuido a uma historia for excluido entre a abertura do dialog e o salvamento? O sistema trata via validacao do use case existente (erro capturado e exibido ao usuario).

---

## Requirements

### Functional Requirements

#### DLG-001: Dialog de Historia — Estilizacao e Campo Desenvolvedor

- **FR-001**: O sistema DEVE atribuir identificadores de estilo a todos os elementos visuais do dialog de historia para permitir estilizacao centralizada.
- **FR-002**: O dialog de historia DEVE exibir campo "Desenvolvedor" (dropdown) apenas no modo edicao, oculto no modo criacao.
- **FR-003**: O campo Desenvolvedor DEVE ser populado com a opcao "Nenhum" (sem atribuicao) como primeiro item, seguida pelos desenvolvedores cadastrados ordenados por nome.
- **FR-004**: O campo Desenvolvedor DEVE pre-selecionar o desenvolvedor atualmente atribuido a historia sendo editada, ou "Nenhum" se nenhum estiver atribuido.
- **FR-005**: Ao salvar uma historia em modo edicao, o sistema DEVE persistir a selecao de desenvolvedor (incluindo desatribuicao).
- **FR-006**: O dialog de historia DEVE exibir espacamento interno de 24px (padding), espacamento entre campos de 16px, e titulo com fonte 16px weight 600.

#### UX-002: Atribuicao Manual de Desenvolvedor

- **FR-007**: O sistema DEVE disponibilizar propriedade de identificacao do desenvolvedor selecionado no modelo de dados do dialog.
- **FR-008**: O sistema DEVE carregar a lista de desenvolvedores de forma assincrona ao abrir o dialog de edicao, reutilizando o servico existente de listagem de desenvolvedores.
- **FR-009**: O sistema DEVE notificar a interface quando a lista de desenvolvedores estiver carregada, para populacao do dropdown.
- **FR-010**: O fluxo de salvamento DEVE incluir a identificacao do desenvolvedor ao editar historia.
- **FR-011**: Ao carregar uma historia para edicao, o sistema DEVE recuperar a identificacao do desenvolvedor atribuido.

#### UX-012: Validacao em Tempo Real

- **FR-012**: Campos obrigatorios (Componente, Nome) DEVEM exibir asterisco (*) em vermelho ao lado do label.
- **FR-013**: Ao perder foco de um campo obrigatorio vazio, o sistema DEVE exibir borda vermelha no campo e mensagem "Campo obrigatorio" abaixo do campo.
- **FR-014**: Ao perder foco de um campo obrigatorio que excede o limite de caracteres, o sistema DEVE exibir mensagem "Maximo de N caracteres" com o mesmo estilo de erro.
- **FR-015**: Campos de texto DEVEM exibir contagem de caracteres no formato "N/MAX" abaixo do campo, atualizada a cada alteracao.
- **FR-016**: A contagem de caracteres DEVE exibir cor de alerta quando o campo atinge 90% ou mais do limite.
- **FR-017**: O botao Salvar DEVE ficar desabilitado quando qualquer campo obrigatorio estiver invalido (vazio ou excedendo limite).
- **FR-018**: O sistema DEVE validar campos individuais sob demanda, retornando resultado de validacao (valido/invalido) e mensagem de erro.
- **FR-019**: A revalidacao do formulario DEVE ocorrer a cada evento de perda de foco em campos obrigatorios. O estado do botao Salvar DEVE ser atualizado apos cada validacao de campo.

#### DLG-002: Dialog de Desenvolvedores — Icones, Hover, Estado Vazio

- **FR-020**: O sistema DEVE atribuir identificadores de estilo a todos os elementos visuais do dialog de desenvolvedores.
- **FR-021**: Os botoes DEVEM exibir icones: [Adicionar] = icone de adicao, [Editar] = icone de edicao, [Remover] = icone de lixeira, [Fechar] = icone de fechar (tamanho 16x16px).
- **FR-022**: Itens da lista DEVEM ter altura de 40px.
- **FR-023**: Itens da lista DEVEM exibir efeito visual de hover ao posicionar o mouse.
- **FR-024**: Quando a lista estiver vazia, o dialog DEVE exibir mensagem centralizada "Nenhum desenvolvedor cadastrado. Clique em Adicionar para comecar." em cor neutra, no lugar da lista vazia.
- **FR-025**: A mensagem de estado vazio DEVE desaparecer automaticamente quando o primeiro item for adicionado, e reaparecer quando o ultimo item for removido.

#### DLG-003: Dialog de Features — Formato "Onda N — Nome", Estado Vazio

- **FR-026**: O sistema DEVE atribuir identificadores de estilo a todos os elementos visuais do dialog de features.
- **FR-027**: Itens da lista DEVEM exibir formato "Onda N — Nome da Feature" (ex: "Onda 2 — Login").
- **FR-028**: Quando a lista estiver vazia, o dialog DEVE exibir mensagem centralizada "Nenhuma feature cadastrada. Clique em Adicionar para comecar." em cor neutra.
- **FR-029**: A mensagem de estado vazio DEVE desaparecer automaticamente quando o primeiro item for adicionado.

#### DLG-007: Dialog de Confirmacao de Exclusao — Icone, Texto Descritivo, Botao Vermelho

- **FR-030**: O sistema DEVE atribuir identificadores de estilo a todos os elementos visuais do dialog de confirmacao.
- **FR-031**: O layout DEVE exibir icone de alerta (32x32px) a esquerda e texto descritivo a direita.
- **FR-032**: O texto principal DEVE seguir o formato por tipo de entidade: historias = "Excluir {ID} — {Nome}?", desenvolvedores = "Excluir {Nome}?", features = "Excluir Onda {N} — {Nome}?".
- **FR-033**: O texto complementar DEVE exibir "Esta acao nao pode ser desfeita." abaixo do texto principal.
- **FR-034**: O botao de confirmacao DEVE exibir texto "Confirmar Exclusao" com fundo vermelho e texto branco.
- **FR-035**: O sistema DEVE suportar criacao do dialog para todos os tipos de entidade (historias, desenvolvedores, features), mantendo compatibilidade com chamadas existentes.

#### DLG-008: Dialogs de Progresso e Resultado

- **FR-036**: O sistema DEVE disponibilizar dialog de progresso modal com barra de progresso estilizada e mensagem textual.
- **FR-037**: O dialog de progresso DEVE permitir atualizacao de progresso (valor e mensagem) durante a operacao.
- **FR-038**: O dialog de progresso DEVE suportar modo indeterminado (animacao continua sem percentual) para operacoes sem granularidade de progresso.
- **FR-039**: O dialog de progresso NAO DEVE ser fechavel pelo usuario durante a operacao.
- **FR-040**: O sistema DEVE disponibilizar dialog de resultado modal com contagens formatadas e botao [Fechar].
- **FR-041**: O dialog de resultado DEVE suportar formatacao para importacao (contagens de historias, features, avisos) e exportacao (caminho do arquivo).
- **FR-042**: Ambos os dialogs DEVEM possuir identificadores de estilo para customizacao centralizada.

#### UX-013: Estados Vazios Orientativos

- **FR-043**: Dialogs de desenvolvedores e features DEVEM alternar entre lista populada e mensagem de estado vazio de forma mutuamente exclusiva.
- **FR-044**: A verificacao de estado vazio DEVE ocorrer apos cada operacao que altera a lista (carregamento, adicao, remocao).
- **FR-045**: A mensagem de estado vazio DEVE ser exibida centralizada, em cor neutra e fonte de tamanho reduzido.

#### Estilizacao Centralizada

- **FR-046**: O sistema de estilos DEVE incluir regras para todos os dialogs refatorados e novos.
- **FR-047**: O sistema de estilos DEVE incluir regras para estados de erro em campos (borda vermelha, mensagem com fundo vermelho claro).
- **FR-048**: O sistema de estilos DEVE incluir regras para: indicador de campo obrigatorio (vermelho), label de estado vazio (cor neutra, centralizado), barra de progresso (cor primaria).
- **FR-049**: O sistema de estilos DEVE incluir regras para botoes especiais: botao de confirmacao de exclusao (fundo vermelho, texto branco), botao Salvar desabilitado (fundo cinza).
- **FR-050**: Novas regras de estilo NAO DEVEM conflitar com regras existentes.

### Key Entities

- **StoryOutputDTO**: Entidade existente — campos relevantes: developer_id (identificacao do desenvolvedor, opcional), developer_name (nome do desenvolvedor, opcional). Nenhuma alteracao necessaria.
- **DeveloperOutputDTO**: Entidade existente — campos: id (identificacao), name (nome). Nenhuma alteracao necessaria.
- **Dialog de Progresso**: Novo componente de apresentacao — dialog modal com barra de progresso e mensagem.
- **Dialog de Resultado**: Novo componente de apresentacao — dialog modal com texto formatado e botao de fechamento.

---

## Architectural Decisions

### ADR-001: Extensao do Modelo de Dados do Dialog de Historia

**Context**: O modelo de dados (ViewModel) atual do dialog de historia gerencia componente, nome, story points e feature. Para o campo Desenvolvedor, e necessario adicionar propriedade de identificacao e metodo de carregamento.

**Options**:
1. Reutilizar o padrao existente de carregamento de features — metodo assincrono dedicado + notificacao dedicada
2. Carregar desenvolvedores junto com features em um unico metodo

**Decision**: Opcao 1 — reutilizar o padrao existente de carregamento de features.

**Rationale**: Consistencia com o padrao existente. Cada recurso tem seu proprio metodo de carga e notificacao, facilitando testes independentes e debug. A assinatura publica existente NAO sera alterada — apenas novos membros serao adicionados.

### ADR-002: Validacao on-blur — Separacao de Responsabilidades

**Context**: Validacao on-blur tem componente visual (borda vermelha, mensagem) e logico (campo vazio?). O padrao arquitetural define que interfaces renderizam e modelos de dados contem logica.

**Options**:
1. Interface detecta perda de foco e delega validacao ao modelo de dados — modelo retorna resultado, interface aplica estilo
2. Interface faz validacao visual simples independentemente do modelo
3. Modelo observa mudancas e notifica interface sobre validacao por campo

**Decision**: Opcao 1 — interface detecta perda de foco e delega validacao ao modelo de dados.

**Rationale**: Separacao clara de responsabilidades. A interface detecta o evento de perda de foco e chama validacao por campo no modelo. O modelo executa a logica (campo vazio? excede limite?) e retorna resultado (valido/invalido, mensagem de erro). A interface aplica o estilo visual baseado no resultado. A logica de validacao fica exclusivamente no modelo; a apresentacao visual fica exclusivamente na interface.

### ADR-003: Campo Desenvolvedor — Visibilidade por Modo

**Context**: O dropdown de Desenvolvedor aparece apenas no modo edicao. No modo criacao, o campo nao deve ser visivel.

**Options**:
1. Criar o elemento sempre, ocultar no modo criacao
2. Criar o elemento dinamicamente apenas no modo edicao
3. Adicionar/remover linha do formulario dinamicamente

**Decision**: Opcao 1 — criar sempre, ocultar no modo criacao.

**Rationale**: Simplicidade e previsibilidade. O elemento e criado uma vez na configuracao inicial, e a visibilidade e controlada com base no modo. O label e o dropdown sao agrupados em um container para controlar visibilidade conjunta.

### ADR-004: Botao Salvar Desabilitado — Estrategia de Re-validacao

**Context**: O botao Salvar deve ficar desabilitado quando o formulario esta invalido. Atualmente, validacao ocorre apenas ao clicar Salvar.

**Options**:
1. Re-validar a cada alteracao de texto (tempo real, potencial impacto em performance)
2. Re-validar a cada perda de foco (menor frequencia, alinhado com validacao on-blur)
3. Re-validar com delay a cada alteracao de texto

**Decision**: Opcao 2 — re-validar a cada perda de foco, com re-habilitacao a cada alteracao de texto.

**Rationale**: A cada perda de foco, a interface chama validacao por campo e verifica se todos os campos obrigatorios estao validos para habilitar/desabilitar o botao. Adicionalmente, a cada alteracao de texto em campos obrigatorios, o sistema re-habilita o botao SOMENTE quando o campo passa de invalido para valido — evitando feedback negativo prematuro durante a digitacao.

### ADR-005: Estados Vazios — Alternancia de Componentes

**Context**: Quando listas de desenvolvedores e features estao vazias, e necessario exibir mensagem orientativa no lugar da lista vazia.

**Options**:
1. Label sobreposto a lista com z-index
2. Componente de alternancia entre lista (indice 0) e label (indice 1)
3. Item customizado na propria lista

**Decision**: Opcao 2 — componente de alternancia.

**Rationale**: Mecanismo idiomatico para alternar entre elementos visuais mutuamente exclusivos. Indice 0 = lista, indice 1 = label centralizado com mensagem orientativa. A verificacao ocorre apos carregamento, apos adicao, apos remocao. Simples, testavel, sem hacks visuais.

### ADR-006: Dialog de Confirmacao de Exclusao — Construtor Retrocompativel

**Context**: O dialog de confirmacao atual aceita parametros especificos de historia. Ele deve suportar desenvolvedores e features tambem.

**Options**:
1. Manter construtor atual e adicionar metodos de criacao especializados (para historia, para desenvolvedor, para feature)
2. Alterar construtor para aceitar parametros genericos
3. Adicionar parametros opcionais com defaults

**Decision**: Opcao 1 — metodos de criacao especializados.

**Rationale**: Metodos especializados permitem construcao semantica clara sem alterar a logica interna. Internamente, o dialog armazena texto principal e texto complementar formatados. Os metodos especializados formatam o texto apropriado para cada entidade. Chamadas existentes sao atualizadas para usar o metodo especializado de historia. Compatibilidade retroativa garantida.

### ADR-007: Dialogs de Progresso e Resultado — Novos Componentes

**Context**: Os dialogs de progresso e resultado nao existem como componentes separados. Import/export usa dialogs genericos.

**Options**:
1. Criar componentes independentes customizados
2. Integrar progresso na barra de status
3. Reutilizar dialog de progresso nativo

**Decision**: Opcao 1 — criar componentes independentes.

**Rationale**: Componentes independentes sao reutilizaveis, testaveis, e seguem o padrao de design system com identificadores de estilo. Dialog nativo nao permite customizacao visual suficiente. A integracao com import/export existente sera feita substituindo dialogs genericos atuais.

### ADR-008: Import/Export e Progresso — Modo Indeterminado

**Context**: Se operacoes de import/export sao sincronas, a barra de progresso nao atualiza durante execucao.

**Options**:
1. Converter operacao para assincrona com progresso granular
2. Usar barra de progresso em modo indeterminado (animacao sem percentual)
3. Aceitar bloqueio breve sem feedback

**Decision**: Opcao 2 — modo indeterminado como default, com suporte a modo determinado.

**Rationale**: O dialog de progresso suporta ambos os modos. Para operacoes sincronas curtas, usa modo indeterminado que exibe animacao continua. Para operacoes que ja fornecem callbacks de progresso, suporta atualizacao com percentual. Isso evita refatoracao profunda de import/export neste epico, enquanto mantem o caminho aberto para progresso granular futuro.

---

## Traceability Matrix

| Componente | Requisitos SRS | Requisitos Funcionais | Criterios de Aceite |
|------------|---------------|----------------------|-------------------|
| DLG-001 (Dialog de Historia) | RF-STORY-001, RF-STORY-002 | FR-001 a FR-006 | Bordas arredondadas, espacamento 16px, padding 24px, titulo 16px weight 600, identificadores de estilo |
| UX-002 (Campo Desenvolvedor) | RF-STORY-007 | FR-007 a FR-011 | Dropdown com devs + "Nenhum", pre-selecao, persistencia, modo edicao apenas |
| UX-012 (Validacao em Tempo Real) | RF-STORY-010, RNF-USAB-003, RNF-CONF-002 | FR-012 a FR-019 | Asterisco (*), borda vermelha on-blur, mensagem inline, contagem caracteres, botao Salvar desabilitado |
| DLG-002 (Dialog de Desenvolvedores) | RF-DEV-001, RF-DEV-002, RF-DEV-003, RF-DEV-004 | FR-020 a FR-025 | Icones, hover 40px, estado vazio orientativo |
| DLG-003 (Dialog de Features) | RF-FEAT-001, RF-FEAT-002, RF-FEAT-003 | FR-026 a FR-029 | Formato "Onda N — Nome", estado vazio |
| DLG-007 (Dialog de Confirmacao) | RF-STORY-003, RF-DEV-003, RF-FEAT-003 | FR-030 a FR-035 | Icone alerta, texto descritivo por entidade, botao vermelho |
| DLG-008 (Progresso/Resultado) | RNF-PERF-002, RNF-CONF-002 | FR-036 a FR-042 | Barra estilizada, dialog de resultado com contagens, identificadores de estilo |
| UX-013 (Estados Vazios) | RNF-USAB-003, RNF-USAB-004 | FR-043 a FR-045 | Alternancia automatica, mensagem neutra centralizada |
| Estilizacao Centralizada | RNF-MANT-001 | FR-046 a FR-050 | Regras de estilo por identificador, sem conflitos |

---

## Success Criteria

### Measurable Outcomes

- **SC-001**: Todos os 5 dialogs existentes exibem estilizacao consistente com bordas arredondadas, espacamento padronizado e cores do design system.
- **SC-002**: O usuario consegue atribuir um desenvolvedor a uma historia em modo edicao em menos de 3 cliques (abrir dialog, selecionar dev, salvar).
- **SC-003**: Campos obrigatorios com asterisco (*) e feedback de erro on-blur sao exibidos em menos de 100ms apos o evento de perda de foco.
- **SC-004**: 100% dos elementos visuais de dialogs possuem identificadores de estilo atribuidos, permitindo customizacao exclusivamente via regras centralizadas.
- **SC-005**: Estados vazios em dialogs de desenvolvedores e features orientam o usuario sobre a proxima acao, reduzindo confusao em listas vazias.
- **SC-006**: O dialog de confirmacao de exclusao comunica claramente o risco com icone de alerta e botao vermelho, para todas as entidades.
- **SC-007**: Dialogs de progresso e resultado de import/export fornecem feedback visual claro ao usuario durante e apos operacoes.
- **SC-008**: Todos os testes existentes de dialogs e modelos de dados continuam passando sem modificacao (zero regressoes).
- **SC-009**: Novos testes cobrem carregamento de desenvolvedores, validacao por campo, propriedade de desenvolvedor e salvamento com desenvolvedor.

---

## Test Specifications

### Unit Tests — Extensoes do Modelo de Dados do Dialog de Historia

| Test | Descricao | Resultado Esperado |
|------|-----------|-------------------|
| test_load_developers_returns_list | Carregamento popula lista via servico de listagem | Notificacao emitida com lista de desenvolvedores |
| test_load_developers_includes_none_option | Lista retornada permite opcao "Nenhum" (sem atribuicao) | Primeira opcao no dropdown e "Nenhum" sem valor |
| test_load_developers_error_emits_signal | Carregamento com falha no servico | Notificacao de erro emitida com mensagem |
| test_developer_id_property_get_set | Propriedade de identificacao aceita inteiro e nulo | Getter retorna valor setado |
| test_developer_id_initial_none | Identificacao inicial e nula | Valor nulo apos inicializacao |
| test_set_story_loads_developer_id | Carregamento de historia recupera identificacao do desenvolvedor | Valor igual ao da historia carregada |
| test_validate_field_component_empty | Validacao de componente vazio | Retorna (invalido, "Campo obrigatorio") |
| test_validate_field_component_too_long | Validacao de componente com mais de 50 caracteres | Retorna (invalido, "Maximo de 50 caracteres") |
| test_validate_field_component_valid | Validacao de componente com valor valido | Retorna (valido, sem mensagem) |
| test_validate_field_name_empty | Validacao de nome vazio | Retorna (invalido, "Campo obrigatorio") |
| test_validate_field_name_too_long | Validacao de nome com mais de 200 caracteres | Retorna (invalido, "Maximo de 200 caracteres") |
| test_validate_field_name_valid | Validacao de nome com valor valido | Retorna (valido, sem mensagem) |
| test_validate_field_unknown | Validacao de campo desconhecido | Retorna (valido, sem mensagem) — campos desconhecidos sao validos |
| test_save_with_developer_id | Salvamento em modo edicao com desenvolvedor selecionado | Historia salva com identificacao do desenvolvedor |
| test_save_without_developer | Salvamento em modo edicao sem desenvolvedor | Historia salva sem desenvolvedor |
| test_validate_global_still_works | Validacao global existente continua funcionando | Retorna mesmos resultados que antes da refatoracao |

### Integration Tests — Comportamento Visual dos Dialogs

| Test | Descricao | Resultado Esperado |
|------|-----------|-------------------|
| test_story_dialog_developer_field_visible_edit_mode | Campo Desenvolvedor visivel em modo edicao | Elemento visivel |
| test_story_dialog_developer_field_hidden_create_mode | Campo Desenvolvedor oculto em modo criacao | Elemento nao visivel |
| test_story_dialog_required_indicators | Labels obrigatorios exibem asterisco | Labels de Componente e Nome contem "*" |
| test_story_dialog_error_on_blur | Erro visual ao sair de campo vazio | Campo exibe estado de erro e label de erro visivel |
| test_story_dialog_save_button_disabled | Botao Salvar desabilitado com campos invalidos | Botao nao habilitado |
| test_developer_dialog_icons | Botoes exibem icones | Cada botao tem icone nao-nulo |
| test_developer_dialog_empty_state | Lista vazia exibe mensagem orientativa | Componente de alternancia mostra label |
| test_feature_dialog_wave_format | Itens exibem formato "Onda N — Nome" | Texto do item corresponde ao formato |
| test_feature_dialog_empty_state | Lista vazia exibe mensagem orientativa | Componente de alternancia mostra label |
| test_confirm_delete_dialog_story | Dialog para historia exibe formato correto | Texto contem "Excluir API-001 — Criar endpoint?" |
| test_confirm_delete_dialog_developer | Dialog para desenvolvedor exibe formato correto | Texto contem "Excluir Ana Silva?" |
| test_confirm_delete_dialog_feature | Dialog para feature exibe formato correto | Texto contem "Excluir Onda 2 — Login?" |
| test_confirm_delete_dialog_red_button | Botao de confirmacao tem estilo de perigo | Botao possui estilo visual de perigo |
| test_progress_dialog_creation | Dialog de progresso criado com barra e mensagem | Barra de progresso e label presentes |
| test_progress_dialog_update | Atualizacao de progresso altera barra e texto | Valores refletem parametros passados |
| test_result_dialog_import | Dialog de resultado exibe contagens de importacao | Labels exibem contagens formatadas |
| test_result_dialog_export | Dialog de resultado exibe caminho de exportacao | Label exibe caminho do arquivo |

---

## Assumptions

- O servico existente de listagem de desenvolvedores retorna desenvolvedores ordenados por nome.
- O servico existente de edicao de historia aceita identificacao de desenvolvedor como parametro opcional.
- Os icones SVG necessarios ja existem no diretorio de assets do projeto.
- O gerenciador de icones ja carrega todos os icones necessarios na inicializacao.
- O sistema de estilos suporta adicao de novas regras sem necessidade de refatoracao da estrutura existente.
- Operacoes de import/export existentes podem ser adaptadas para usar novos dialogs sem alterar a logica de negocio.
- Textos de interface seguem convencao PT-BR sem acentos conforme convencoes do projeto.

---

## Scope Boundaries

### Included

- Estilizacao de dialogs de historia, desenvolvedores, features e confirmacao de exclusao
- Campo Desenvolvedor (dropdown) no dialog de historia em modo edicao
- Extensao do modelo de dados do dialog de historia (identificacao de desenvolvedor, carregamento, validacao por campo)
- Validacao on-blur com feedback visual inline
- Indicadores de campo obrigatorio (*) e contagem de caracteres
- Icones nos botoes do dialog de desenvolvedores
- Efeito de hover e estado vazio nos dialogs de desenvolvedores e features
- Formato "Onda N — Nome" no dialog de features
- Icone de alerta e botao vermelho no dialog de confirmacao
- Criacao de dialogs de progresso e resultado
- Novas regras de estilo centralizadas
- Testes unitarios e de integracao para novas funcionalidades

### Excluded

- Filtros, busca e menu de contexto (EP-020)
- Modelo de tabela, delegates, tooltip rico, agrupamento visual por onda (EP-019/EP-022)
- Dialogs de configuracao, dependencias e metricas (EP-018 — ja estilizados)
- Dialog "Sobre" (EP-022)
- Logica de dominio, entidades, value objects, services, repositorios
- Criacao de novos servicos de aplicacao — apenas integracao com servicos existentes
- Conversao de import/export para assincrono (futuro epico se necessario)
