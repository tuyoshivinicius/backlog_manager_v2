# epic Input Template

## Titulo

Correcao de Problemas de Interface do Roadmap

## Descricao

O modulo de visualizacao de roadmap (timeline Gantt) apresenta 17 problemas criticos de usabilidade identificados em auditoria de interface. Os problemas afetam legibilidade, navegacao, consistencia visual e funcionalidade de controles, tornando a ferramenta impraticavel para backlogs com volume alto (190+ historias). Esta epic corrige todos os defeitos reportados para que o roadmap seja utilizavel como ferramenta de acompanhamento de projeto.

## Atores

- **Gerente de Projeto**: consulta o roadmap para acompanhar progresso, identificar gargalos e comunicar status a stakeholders. Precisa de uma visualizacao legivel e navegavel mesmo com centenas de historias.
- **Desenvolvedor**: acessa o roadmap para entender dependencias, prazos e prioridades de suas tarefas. Precisa localizar rapidamente suas historias e entender o contexto temporal.

## Fluxos Principais

### F1 — Controle de janela e espaco util (Issue #1)

1. Usuario abre o roadmap
2. O sistema exibe a janela com controles padrao de maximizar, minimizar e redimensionar
3. A janela abre ja maximizada por padrao, mas o usuario pode redimensionar livremente

**Comportamento esperado**: A janela do roadmap deve ser um QDialog com flags de janela que incluam botoes de minimizar e maximizar (Qt.WindowMinMaxButtonsHint). Deve abrir maximizada por padrao (showMaximized) mas permitir redimensionamento livre pelo usuario.

### F2 — Sistema de expandir/colapsar waves funcional (Issues #2, #3, #16)

1. Usuario clica no cabecalho de uma wave para expandir e ver as historias internas
2. O sistema expande a wave, mostrando cada historia como uma barra individual com rotulo legivel
3. Usuario clica novamente no cabecalho da wave para colapsar
4. O sistema colapsa a wave, voltando a exibir apenas a barra de resumo
5. Ao expandir multiplas waves, cada historia mantem uma altura minima legivel

**Comportamento esperado**:
- O toggle de expandir/colapsar deve funcionar como alternancia bidirecional (clique expande, segundo clique colapsa)
- Cada historia expandida deve ocupar no minimo 20px de altura para garantir legibilidade do rotulo
- Quando o conteudo total excede a area visivel, o sistema deve oferecer scroll vertical fluido
- Rotulos longos devem ser truncados com reticencias (...) mas nunca sobrepostos a rotulos adjacentes
- O container deve recalcular a altura total do grafico ao expandir/colapsar, sem comprimir linhas existentes
- Implementar modo acordeao opcional: ao expandir uma wave, as demais podem ser colapsadas automaticamente (comportamento configuravel)

### F3 — Eixo temporal adaptativo (Issue #4)

1. Usuario visualiza o roadmap em diferentes niveis de zoom
2. O sistema adapta os marcadores de data conforme o nivel de zoom e a largura disponivel

**Comportamento esperado**:
- Os marcadores de data devem ser exibidos na horizontal (sem rotacao) sempre que houver espaco suficiente
- Quando o espaco for insuficiente, rotacionar no maximo 30 graus e nunca mais que 45 graus
- O numero de marcadores deve se adaptar automaticamente a largura disponivel (usar AutoDateLocator do matplotlib ou logica equivalente)
- A granularidade deve mudar conforme o zoom: dias (zoom proximo), semanas (zoom medio), meses (zoom distante)
- Cada marcador deve sempre exibir contexto suficiente (ex: "05 Abr" e nao apenas "05")
- Minimo de 5 marcadores visiveis em qualquer nivel de zoom

### F4 — Controles de zoom com feedback claro (Issue #5)

1. Usuario utiliza os botoes de zoom ou Ctrl+Scroll para ajustar o nivel de aproximacao
2. O sistema ajusta o zoom e exibe indicacao clara do nivel atual

**Comportamento esperado**:
- Os botoes de zoom devem usar icones de lupa com + e - (nao setas direcionais)
- Exibir indicador de nivel de zoom atual (ex: "100%", "150%") proximo aos controles
- Definir limite inferior de zoom que garanta que pelo menos o nome de cada wave seja legivel
- Definir limite superior de zoom que mostre no maximo 7 dias na viewport
- Adicionar botao "Ajustar a tela" que redimensiona o zoom para mostrar todo o periodo
- Todos os botoes da toolbar devem possuir tooltips descritivos
- O botao de limpar filtros deve ter tooltip "Limpar todos os filtros" e icone reconhecivel (ex: funil com X)

### F5 — Codificacao visual por status nas barras (Issues #6, #12)

1. Usuario visualiza o roadmap e identifica o status de cada historia pela cor da barra
2. O sistema aplica cores distintas conforme o status de cada historia

**Comportamento esperado**:
- Cada barra deve ser colorida conforme o STATUS_PALETTE ja definido no design system:
  - BACKLOG: #E5E5E5 (cinza)
  - EXECUCAO: #DBEAFE (azul claro)
  - TESTES: #FEF3C7 (amarelo claro)
  - CONCLUIDO: #DDF3E4 (verde claro)
  - IMPEDIDO: vermelho com borda tracejada
- Barras devem exibir preenchimento parcial indicando progresso (0% BACKLOG, 33% EXECUCAO, 66% TESTES, 100% CONCLUIDO)
- O preenchimento parcial deve ser visualmente distinto (ex: parte preenchida em tom mais escuro da mesma cor)
- Se todas as barras estao aparecendo na mesma cor cinza apesar do codigo existir, trata-se de um bug de renderizacao que deve ser investigado e corrigido

### F6 — Legenda consistente e legivel (Issue #7)

1. Usuario consulta a legenda para entender o mapeamento de cores

**Comportamento esperado**:
- A legenda deve usar um unico tipo de simbolo para todos os status: quadrados coloridos (patches retangulares)
- Remover a mistura de simbolos diferentes (●, ►, ◆, ✓, ✕) e padronizar em retangulos coloridos seguidos do nome do status
- O tamanho dos simbolos deve ser de no minimo 12x12px
- A legenda deve seguir a tipografia e espacamento do design system da aplicacao

### F7 — Rotulos de grupo com nome da feature (Issue #8)

1. Usuario visualiza as waves e identifica o escopo funcional de cada uma

**Comportamento esperado**:
- Os rotulos dos grupos devem exibir o nome da feature ou modulo alem do numero da wave
- Formato: "Wave N — [Nome da Feature] - X% [Y historias]"
- Se uma wave contem historias de multiplas features, listar as features separadas por virgula (truncando se necessario)
- Se a informacao de feature nao estiver disponivel, manter o formato atual "Wave N" como fallback

### F8 — Consistencia com design system (Issue #9)

1. Usuario navega entre o roadmap e outras telas da aplicacao sem perceber descontinuidade visual

**Comportamento esperado**:
- Os dropdowns de filtro devem usar o estilo de QComboBox padrao da aplicacao (mesmo padding, fonte, bordas)
- A legenda deve usar a mesma tipografia e espacamento dos demais componentes
- Tooltips devem seguir o padrao visual do sistema (mesma cor de fundo, fonte, bordas arredondadas)
- O campo de busca deve incluir icone de lupa e usar o mesmo estilo visual dos inputs da aplicacao
- Os botoes da toolbar devem seguir o padrao de botoes do restante da interface (mesmo tamanho, padding, estilo)
- Aplicar o stylesheet global da aplicacao a todos os widgets do dialog

### F9 — Correcao do dropdown fantasma (Issue #10)

1. Usuario interage com o dropdown de Status sem artefatos visuais

**Comportamento esperado**:
- Nenhum retangulo vazio ou popup fantasma deve aparecer ao interagir com qualquer dropdown
- Investigar se o problema e causado por um popup/completer criado mas nao populado, ou por um widget orfao
- O dropdown deve abrir e fechar normalmente, mostrando apenas as opcoes disponiveis

### F10 — Escala temporal adaptativa a distribuicao (Issue #11)

1. Usuario visualiza historias distribuidas de forma desigual no tempo sem areas excessivamente densas ou vazias

**Comportamento esperado**:
- A escala temporal deve considerar a distribuicao real das tarefas para definir os limites iniciais de visualizacao
- Se 90% das tarefas estao concentradas em 20% do periodo, o zoom inicial deve focar nessa regiao densa
- Adicionar opcao de "Ajustar ao conteudo" que redimensiona a viewport para a regiao com maior densidade de tarefas
- Manter a possibilidade de ver o periodo completo via zoom out

### F11 — Linha de referencia "hoje" destacada (Issue #13)

1. Usuario identifica visualmente a data atual no roadmap

**Comportamento esperado**:
- A linha de "hoje" deve ser visivelmente mais espessa que as linhas de grade (minimo 2px, recomendado 2.5px)
- Usar cor vermelha ou laranja com opacidade alta (alpha >= 0.8)
- Adicionar label "Hoje" proximo ao topo da linha
- A linha deve estar em camada superior (zorder alto) para nao ser ocultada por barras
- Usar estilo tracejado diferenciado das demais linhas de grade

### F12 — Setas de dependencia melhoradas (Issue #14)

1. Usuario visualiza dependencias entre historias de forma clara

**Comportamento esperado**:
- Manter o recurso de setas de dependencia ativadas por hover (comportamento atual e positivo)
- Mudar a cor das setas de vermelho para uma cor neutra que nao sugira erro (ex: azul escuro #1E40AF ou cinza escuro #4B5563)
- Quando multiplas setas se sobrepoe a barras intermediarias, usar curvatura variavel para reduzir sobreposicao
- Adicionar opcao "Mostrar todas as dependencias" na toolbar que renderiza todas as setas simultaneamente
- Setas para dependencias fora da area visivel devem apontar para a borda com indicador de direcao

### F13 — Barra de status no rodape enriquecida (Issue #15)

1. Usuario consulta o resumo de status no rodape do roadmap

**Comportamento esperado**:
- Manter as contagens textuais por status
- Adicionar mini-barra de progresso horizontal ao lado das contagens, mostrando a proporcao visual de cada status
- Quando filtros estiverem ativos, exibir "X de Y historias (filtro ativo)" para diferenciar total filtrado do total geral
- Usar as mesmas cores do STATUS_PALETTE na mini-barra de progresso
- A fonte deve ser legivel (minimo 10pt)

### F14 — Mecanismos de navegacao para volume alto (Issue #16)

1. Usuario navega eficientemente por um backlog de 190+ historias

**Comportamento esperado**:
- A busca ("Buscar historia...") deve exibir contador de resultados (ex: "3 de 190 historias")
- Ao buscar, historias que nao correspondem devem ser ocultadas (filtro efetivo, nao apenas destaque)
- Adicionar indicador visual de posicao no scroll (minimap ou scrollbar proporcional)
- O scroll vertical do painel de rotulos e da area de barras deve ser sincronizado
- Ao expandir uma wave com muitas historias, fazer auto-scroll para que o conteudo expandido fique visivel

### F15 — Correcao da Wave 7 ausente (Issue #17)

1. Usuario visualiza todas as waves sem lacunas na numeracao

**Comportamento esperado**:
- Investigar se a Wave 7 existe nos dados mas nao esta sendo renderizada (bug de renderizacao) ou se nao existe nos dados (bug de dados)
- Se a wave existe mas esta vazia, exibi-la com indicacao "(vazia)" ou "(0 historias)"
- Se a wave foi removida intencionalmente, ajustar a numeracao para ser sequencial ou exibir nota explicativa
- A numeracao de waves nunca deve apresentar lacunas sem explicacao

## Regras de Negocio

- Todas as correcoes devem manter compatibilidade com o design system existente da aplicacao (STATUS_PALETTE, fontes, espacamentos)
- O roadmap deve permanecer funcional e legivel com backlogs de 1 a 500 historias
- A performance de renderizacao nao deve degradar: tempo maximo de 2 segundos para renderizar o grafico completo
- Filtros devem continuar operando com logica AND (comportamento existente mantido)
- O estado de expandir/colapsar das waves nao precisa persistir entre sessoes (comportamento atual mantido)
- Tooltips de barras individuais devem continuar funcionando (nome, status, desenvolvedor, pontos, datas, duracao, componente, dependencias)
- As correcoes devem ser implementadas usando matplotlib para renderizacao e PySide6 para controles, mantendo a arquitetura MVVM existente

## Escopo

**Inclui**:
- Correcao dos 17 problemas de interface identificados no relatorio de auditoria
- Ajustes nos controles de janela (maximizar, minimizar, redimensionar)
- Correcao do toggle expandir/colapsar waves
- Adaptacao do eixo temporal (granularidade, marcadores, rotacao)
- Melhoria dos controles de zoom (icones, limites, feedback)
- Aplicacao efetiva das cores de status nas barras
- Padronizacao da legenda
- Exibicao de nomes de features nos rotulos de grupo
- Alinhamento visual com design system da aplicacao
- Correcao do dropdown fantasma
- Ajuste de escala temporal para distribuicao desigual
- Destaque da linha "hoje"
- Melhoria das setas de dependencia
- Enriquecimento da barra de status
- Mecanismos de navegacao para alto volume
- Investigacao e correcao da Wave 7 ausente

**Nao inclui**:
- Edicao de historias diretamente no roadmap (drag & drop, inline edit)
- Persistencia do estado de visualizacao entre sessoes
- Exportacao do roadmap (PDF, imagem, Excel)
- Integracao com sistemas externos (Jira, Linear, etc.)
- Alteracoes no modelo de dados ou schema do banco
- Novos tipos de agrupamento (por componente, por desenvolvedor, por sprint)
- Modo de visualizacao alternativo (kanban, calendario, lista)

## Criterios de Sucesso

- Todas as 17 issues do relatorio sao resolvidas e verificaveis em teste manual
- O roadmap exibe corretamente 190 historias com todas as waves expandidas sem sobreposicao de rotulos
- O toggle expandir/colapsar funciona bidirecionalmente em todas as waves
- As barras exibem cores correspondentes ao status real de cada historia
- Os marcadores do eixo temporal sao legiveis em todos os niveis de zoom
- A janela pode ser maximizada, minimizada e redimensionada
- Nenhum artefato visual (dropdown fantasma) aparece durante a interacao
- Todos os botoes da toolbar possuem tooltips
- A linha "hoje" e visualmente distinta das linhas de grade
- O tempo de renderizacao completa nao excede 2 segundos com 190 historias
- A interface do roadmap e visualmente consistente com o restante da aplicacao
