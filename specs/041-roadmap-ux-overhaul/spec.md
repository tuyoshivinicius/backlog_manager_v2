# Feature Specification: Roadmap UX Overhaul

**Feature Branch**: `041-roadmap-ux-overhaul`
**Created**: 2026-04-02
**Status**: Draft
**Input**: Epic "Reformulacao Visual e Navegacional do Roadmap" — auditoria identificou 11 problemas criticos de usabilidade no roadmap atual

## Clarifications

### Session 2026-04-02

- Q: Comportamento da busca — destacar ou filtrar? → A: Filtrar — apenas historias correspondentes sao exibidas, demais sao ocultadas (mesmo comportamento dos filtros por wave/status/responsavel/componente)
- Q: Criterio de agrupamento — wave, feature ou selecionavel? → A: Sempre por wave — grupos correspondem a waves existentes, sem opcao de mudar o criterio de agrupamento
- Q: Dependencias — somente diretas ou cadeia transitiva? → A: Somente diretas — setas conectam apenas dependencias de 1 nivel (predecessoras e sucessoras imediatas)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Identificacao Visual por Status (Priority: P1)

O usuario abre o roadmap e ve imediatamente barras coloridas de acordo com o status de cada historia (backlog=cinza, execucao=azul, testes=amarelo, concluido=verde, impedido=vermelho). Uma legenda de cores fica visivel na interface. Historias com status IMPEDIDO possuem destaque visual adicional (borda ou icone de alerta). O usuario identifica de relance quais historias estao bloqueadas e quais foram concluidas.

**Why this priority**: A codificacao por cor e a melhoria de maior impacto imediato — transforma o roadmap de um diagrama monocromatico em uma ferramenta de comunicacao visual. Sem isso, todas as outras melhorias perdem contexto.

**Independent Test**: Pode ser testado abrindo o roadmap com historias em diferentes status e verificando que cada barra exibe a cor correta, a legenda esta visivel e historias impedidas possuem destaque adicional.

**Acceptance Scenarios**:

1. **Given** um roadmap com historias em 5 status diferentes, **When** o usuario abre o roadmap, **Then** cada barra exibe a cor correspondente ao STATUS_PALETTE (BACKLOG=#E5E5E5, EXECUCAO=#DBEAFE, TESTES=#FEF3C7, CONCLUIDO=#DDF3E4, IMPEDIDO=vermelho)
2. **Given** historias renderizadas no roadmap, **When** o usuario observa a interface, **Then** uma legenda de cores e visivel associando cada cor ao status correspondente
3. **Given** uma historia com status IMPEDIDO, **When** renderizada no roadmap, **Then** exibe destaque visual adicional (borda diferenciada ou icone de alerta) alem da cor vermelha
4. **Given** um roadmap com historias mistas, **When** o usuario observa a tela, **Then** consegue identificar o status de qualquer historia em menos de 2 segundos pela cor

---

### User Story 2 - Colapso e Expansao de Grupos (Priority: P1)

O gestor abre o roadmap e ve apenas os grupos (waves) como barras-resumo com percentual de conclusao, sem exibir todas as 190+ historias simultaneamente. O gestor clica em um grupo para expandir e ver as historias individuais. Clica novamente para colapsar. O estado de expansao e preservado durante a sessao. Grupos colapsados exibem uma barra-resumo que cobre o intervalo de datas min/max do grupo.

**Why this priority**: Resolve o problema principal de sobrecarga de informacao — sem colapso, o usuario ve 190+ historias de uma vez, tornando o roadmap inutilizavel. E pre-requisito para que filtros e busca funcionem de forma eficiente.

**Independent Test**: Pode ser testado abrindo o roadmap, verificando que grupos aparecem colapsados por padrao com barra-resumo e percentual, expandindo/colapsando grupos individualmente e confirmando que o estado persiste durante a sessao.

**Acceptance Scenarios**:

1. **Given** um roadmap com multiplos grupos, **When** o usuario abre o roadmap, **Then** todos os grupos aparecem colapsados como barras-resumo com percentual de conclusao
2. **Given** um grupo colapsado, **When** o usuario clica no grupo, **Then** o grupo expande mostrando as historias individuais em menos de 500ms
3. **Given** um grupo expandido, **When** o usuario clica no grupo novamente, **Then** o grupo colapsa de volta a barra-resumo em menos de 500ms
4. **Given** grupos em estados variados (alguns expandidos, outros colapsados), **When** o usuario navega para outra tela e retorna ao roadmap na mesma sessao, **Then** o estado de expansao e preservado
5. **Given** um grupo colapsado com 10 historias de datas variadas, **When** renderizado, **Then** a barra-resumo cobre o intervalo de data inicio mais antiga ate data fim mais recente do grupo

---

### User Story 3 - Linha de Referencia Temporal "Hoje" (Priority: P2)

O usuario abre o roadmap e ve uma linha vertical destacada indicando a data de hoje. A linha e visualmente distinta (cor contrastante, tracejado). O usuario identifica imediatamente o que ja deveria ter sido feito (a esquerda) e o que esta por vir (a direita).

**Why this priority**: Fornece contexto temporal essencial — sem a referencia de "hoje", o usuario nao consegue avaliar atrasos ou progresso. E uma melhoria de alto impacto com complexidade relativamente baixa.

**Independent Test**: Pode ser testado abrindo o roadmap e verificando que uma linha vertical tracejada aparece na posicao correspondente a data atual, visivel sem scroll.

**Acceptance Scenarios**:

1. **Given** a data atual dentro do intervalo da timeline do roadmap, **When** o usuario abre o roadmap, **Then** uma linha vertical tracejada em cor contrastante e exibida na posicao correspondente a data de hoje
2. **Given** a linha de "hoje" renderizada, **When** o usuario observa o roadmap no zoom padrao, **Then** a linha e visivel sem necessidade de scroll horizontal
3. **Given** a data atual fora do intervalo da timeline, **When** o usuario abre o roadmap, **Then** a linha de "hoje" nao e exibida

---

### User Story 4 - Correcao de Rotulos e Hierarquia Visual (Priority: P2)

Os rotulos das historias sao legiveis sem sobreposicao quando o grupo esta expandido. A hierarquia visual entre waves e reforcada com separadores e indentacao. Labels possuem no minimo 14px de altura. Quando o espaco nao comporta os rotulos, o sistema colapsa automaticamente o grupo.

**Why this priority**: Resolve problemas fundamentais de legibilidade que comprometem toda a experiencia. Sem rotulos legiveis, a codificacao por cor e os filtros perdem utilidade.

**Independent Test**: Pode ser testado expandindo um grupo com muitas historias e verificando que nenhum rotulo se sobrepoe, todos possuem pelo menos 14px de altura e a hierarquia visual entre grupos e historias e clara.

**Acceptance Scenarios**:

1. **Given** um grupo expandido com 20+ historias, **When** renderizado no zoom 100%, **Then** nenhum rotulo se sobrepoe a outro
2. **Given** historias renderizadas, **When** inspecionadas, **Then** todos os labels possuem no minimo 14px de altura
3. **Given** um grupo com historias cujos rotulos nao cabem no espaco disponivel, **When** renderizado, **Then** o sistema colapsa automaticamente o grupo
4. **Given** o roadmap com multiplos grupos, **When** o usuario observa a interface, **Then** waves possuem separadores visuais e indentacao que diferenciam niveis hierarquicos

---

### User Story 5 - Filtragem e Busca (Priority: P2)

O usuario aplica filtros por wave, status, responsavel ou componente usando controles na toolbar. O grafico atualiza mostrando apenas historias que atendem aos filtros. O usuario digita parte do nome de uma historia no campo de busca e o sistema filtra, exibindo apenas as historias correspondentes (ocultando as demais). Filtros ativos sao indicados visualmente na toolbar.

**Why this priority**: Permite ao usuario encontrar informacao especifica rapidamente. Depende da codificacao por cor (P1) e colapso de grupos (P1) para funcionar de forma eficiente.

**Independent Test**: Pode ser testado aplicando cada tipo de filtro individualmente, combinando filtros e verificando que apenas historias correspondentes sao exibidas e que a toolbar indica filtros ativos.

**Acceptance Scenarios**:

1. **Given** o roadmap com historias de multiplos status, **When** o usuario seleciona o filtro "CONCLUIDO", **Then** apenas historias com status CONCLUIDO sao exibidas
2. **Given** filtros por wave, status, responsavel e componente disponiveis, **When** o usuario combina dois filtros, **Then** o roadmap exibe apenas historias que atendem a ambos os criterios (AND logico)
3. **Given** o campo de busca na toolbar, **When** o usuario digita "login", **Then** apenas historias cujo nome contem "login" sao exibidas (demais sao ocultadas) em menos de 5 segundos
4. **Given** um filtro aplicado, **When** o usuario observa a toolbar, **Then** o filtro ativo e indicado visualmente (badge ou cor de destaque)
5. **Given** filtros aplicados, **When** o usuario remove todos os filtros, **Then** o roadmap retorna a exibicao completa

---

### User Story 6 - Tooltip Enriquecido e Dependencias (Priority: P3)

O usuario passa o mouse sobre uma historia e ve um tooltip com informacoes detalhadas: nome, status, responsavel, story points, data inicio, data fim, duracao em dias uteis, componente e lista de dependencias. Ao interagir com a barra, setas/linhas conectam a historia as suas dependencias.

**Why this priority**: Complementa a experiencia visual com informacoes detalhadas sob demanda. Dependencias sao valiosas mas nao bloqueiam o uso basico do roadmap.

**Independent Test**: Pode ser testado passando o mouse sobre uma historia com dependencias e verificando que o tooltip exibe todas as informacoes e que setas conectam a historia as dependencias.

**Acceptance Scenarios**:

1. **Given** uma historia no roadmap, **When** o usuario passa o mouse sobre a barra, **Then** um tooltip exibe: nome, status, responsavel, story points, data inicio, data fim, duracao em dias uteis, componente e lista de dependencias
2. **Given** uma historia com dependencias, **When** o usuario interage com a barra (hover), **Then** setas/linhas conectam visualmente a historia apenas as suas dependencias diretas (1 nivel)
3. **Given** uma historia sem dependencias, **When** o usuario interage com a barra, **Then** o tooltip indica "Sem dependencias" e nenhuma seta e exibida

---

### User Story 7 - Toolbar com Icones e Rodape Estatistico (Priority: P3)

Todos os botoes da toolbar possuem icone E tooltip descritivo — nenhum botao fica sem identificacao visual. O rodape exibe resumo estatistico com contagem de historias por status (backlog, execucao, testes, concluido, impedido), nao apenas contagem total.

**Why this priority**: Melhorias de polimento que completam a experiencia mas nao sao essenciais para o uso funcional do roadmap.

**Independent Test**: Pode ser testado inspecionando cada botao da toolbar para confirmar icone e tooltip, e verificando que o rodape exibe contagem por status.

**Acceptance Scenarios**:

1. **Given** a toolbar do roadmap, **When** o usuario inspeciona cada botao, **Then** 100% dos botoes possuem icone visivel e tooltip descritivo
2. **Given** o roadmap com historias em diferentes status, **When** o usuario observa o rodape, **Then** o rodape exibe contagem de historias separada por status (backlog, execucao, testes, concluido, impedido)
3. **Given** filtros aplicados, **When** o usuario observa o rodape, **Then** o rodape reflete apenas as historias atualmente visiveis

---

### User Story 8 - Progresso Visual nas Barras (Priority: P3)

As barras das historias sao parcialmente preenchidas indicando o progresso baseado no status (backlog=0%, execucao=33%, testes=66%, concluido=100%). O preenchimento parcial e visualmente distinto dentro da barra colorida.

**Why this priority**: Adiciona uma camada extra de informacao visual. Util mas menos critico que cor de status e colapso.

**Independent Test**: Pode ser testado verificando que historias em cada status exibem o preenchimento correto dentro da barra.

**Acceptance Scenarios**:

1. **Given** uma historia com status BACKLOG, **When** renderizada, **Then** a barra exibe 0% de preenchimento
2. **Given** uma historia com status EXECUCAO, **When** renderizada, **Then** a barra exibe aproximadamente 33% de preenchimento
3. **Given** uma historia com status TESTES, **When** renderizada, **Then** a barra exibe aproximadamente 66% de preenchimento
4. **Given** uma historia com status CONCLUIDO, **When** renderizada, **Then** a barra exibe 100% de preenchimento

---

### User Story 9 - Scroll Sincronizado (Priority: P3)

O scroll entre o painel de labels (nomes das historias) e a area de barras (timeline) e sincronizado, garantindo que os nomes das historias correspondam visualmente as barras corretas independente da posicao de scroll.

**Why this priority**: Essencial para usabilidade com muitas historias, mas depende de todas as outras melhorias visuais estarem implementadas.

**Independent Test**: Pode ser testado expandindo grupos com muitas historias e fazendo scroll vertical, verificando que labels e barras permanecem alinhados.

**Acceptance Scenarios**:

1. **Given** um roadmap com mais historias do que cabem na tela, **When** o usuario faz scroll vertical na area de barras, **Then** o painel de labels acompanha o scroll na mesma proporcao
2. **Given** scroll sincronizado, **When** o usuario faz scroll no painel de labels, **Then** a area de barras acompanha o scroll na mesma proporcao

---

### Edge Cases

- O que acontece quando um grupo nao possui nenhuma historia? O grupo e exibido como barra-resumo com 0% e duracao zero (ponto unico na timeline)
- O que acontece quando todas as historias de um grupo possuem o mesmo status? A barra-resumo exibe 100% daquele status e a cor predominante
- O que acontece quando uma historia nao possui datas atribuidas? A historia e listada no grupo mas sem barra na timeline, com indicacao visual de "sem datas"
- O que acontece quando o campo de busca nao encontra resultados? O sistema exibe mensagem "Nenhuma historia encontrada" e mantem os filtros anteriores
- O que acontece quando uma dependencia referencia uma historia que esta filtrada/oculta? A seta de dependencia aponta para fora da area visivel com indicacao visual (seta tracejada ou icone de link externo)
- O que acontece com historias sem responsavel atribuido? O tooltip exibe "Sem responsavel" e o filtro por responsavel inclui opcao "Nao atribuido"
- O que acontece ao renderizar 200+ historias com todos os grupos expandidos? O sistema deve renderizar em menos de 3 segundos e colapsar automaticamente grupos cujos rotulos nao cabem no espaco

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE renderizar barras de historias com cores baseadas no status seguindo o STATUS_PALETTE definido (BACKLOG=#E5E5E5, EXECUCAO=#DBEAFE, TESTES=#FEF3C7, CONCLUIDO=#DDF3E4, IMPEDIDO=vermelho)
- **FR-002**: O sistema DEVE exibir uma legenda de cores sempre que houver historias renderizadas no roadmap
- **FR-003**: Historias com status IMPEDIDO DEVEM possuir destaque visual adicional (borda diferenciada ou icone de alerta) alem da cor
- **FR-004**: O sistema DEVE agrupar historias por wave e permitir colapso/expansao de cada grupo
- **FR-005**: Grupos colapsados DEVEM exibir barra-resumo cobrindo o intervalo min/max de datas do grupo com percentual de conclusao
- **FR-006**: O sistema DEVE preservar o estado de expansao/colapso dos grupos durante a sessao do usuario
- **FR-007**: O sistema DEVE exibir uma linha vertical tracejada em cor contrastante indicando a data de "hoje" quando a data atual estiver dentro do intervalo da timeline
- **FR-008**: Labels de historias DEVEM ter no minimo 14px de altura; grupos cujos rotulos nao cabem no espaco DEVEM ser colapsados automaticamente
- **FR-009**: O sistema DEVE resolver colisoes e sobreposicoes de rotulos quando grupos estao expandidos
- **FR-010**: O sistema DEVE fornecer hierarquia visual entre waves usando separadores e indentacao
- **FR-011**: O sistema DEVE fornecer filtros por wave, status, responsavel e componente na toolbar
- **FR-012**: O sistema DEVE fornecer campo de busca por nome de historia na toolbar
- **FR-013**: Filtros ativos DEVEM ser indicados visualmente na toolbar (badge ou cor de destaque)
- **FR-014**: O sistema DEVE exibir tooltip enriquecido ao passar o mouse sobre uma historia contendo: nome, status, responsavel, story points, data inicio, data fim, duracao em dias uteis, componente e lista de dependencias
- **FR-015**: O sistema DEVE exibir setas/linhas conectando historias as suas dependencias diretas (1 nivel — predecessoras e sucessoras imediatas) ao interagir com a barra (hover)
- **FR-016**: Todos os botoes da toolbar DEVEM possuir icone visivel e tooltip descritivo
- **FR-017**: O rodape DEVE exibir contagem de historias por status (backlog, execucao, testes, concluido, impedido), refletindo filtros aplicados
- **FR-018**: Barras de historias DEVEM indicar progresso visual baseado no status (backlog=0%, execucao=33%, testes=66%, concluido=100%)
- **FR-019**: O scroll entre o painel de labels e a area de barras DEVE ser sincronizado
- **FR-020**: O sistema DEVE renderizar roadmap com 200+ historias em menos de 3 segundos

### Key Entities

- **Grupo (Wave)**: Agrupamento logico de historias por wave com barra-resumo, percentual de conclusao e estado de expansao. Possui intervalo de datas derivado das historias filhas. O criterio de agrupamento e fixo (sempre por wave)
- **Historia (Story)**: Unidade base do roadmap com nome, status, responsavel, story points, datas de inicio/fim, componente e lista de dependencias
- **Dependencia**: Relacao direcional entre duas historias (predecessora -> dependente), representada visualmente por setas. Apenas dependencias diretas (1 nivel) sao exibidas; cadeia transitiva nao e renderizada
- **Filtro**: Criterio de selecao aplicavel por wave, status, responsavel ou componente, combinavel com logica AND

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Todos os rotulos de historias sao legiveis sem sobreposicao quando o grupo esta expandido (zoom 100%)
- **SC-002**: Usuario identifica o status de qualquer historia em menos de 2 segundos pela cor da barra
- **SC-003**: Usuario localiza uma historia especifica pelo nome em menos de 5 segundos usando busca
- **SC-004**: Linha de "hoje" e visivel sem necessidade de scroll ou zoom quando a data atual esta no intervalo da timeline
- **SC-005**: 100% dos botoes da toolbar possuem icone e tooltip descritivo
- **SC-006**: Dependencias entre historias sao visiveis ao interagir com a barra (hover)
- **SC-007**: Roadmap com 200+ historias renderiza em menos de 3 segundos
- **SC-008**: Colapsar/expandir grupos responde em menos de 500ms
- **SC-009**: Rodape exibe contagem de historias por status (backlog, execucao, testes, concluido, impedido)
- **SC-010**: Nenhum botao ou controle da toolbar fica sem identificacao visual

## Assumptions

- Os dados de historias (nome, status, responsavel, story points, datas, componente, dependencias) ja estao disponiveis nos DTOs existentes retornados pelos use cases atuais
- Nao serao necessarias alteracoes no schema do banco de dados SQLite
- Nao serao criados novos use cases na camada de aplicacao
- O STATUS_PALETTE (BACKLOG=#E5E5E5, EXECUCAO=#DBEAFE, TESTES=#FEF3C7, CONCLUIDO=#DDF3E4, IMPEDIDO=vermelho) ja esta definido no design system da aplicacao
- A progressao de status segue a ordem linear: backlog(0%) -> execucao(33%) -> testes(66%) -> concluido(100%)
- Filtros combinados utilizam logica AND (intersecao)
- O estado de expansao/colapso dos grupos e preservado apenas durante a sessao (nao persiste entre reinicializacoes da aplicacao)
- A aplicacao e exclusivamente desktop (PySide6), sem necessidade de responsividade mobile

## Constraints

- Nao inclui escala temporal nao-linear ou zoom semantico
- Nao inclui minimap/visao reduzida do Gantt
- Nao inclui responsividade para dispositivos mobile
- Nao inclui drag-and-drop para reordenar historias ou alterar datas
- Nao inclui edicao de historias diretamente no roadmap
