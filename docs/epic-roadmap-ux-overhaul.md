# epic Input — Roadmap UX Overhaul

## Titulo

Reformulacao Visual e Navegacional do Roadmap

## Descricao

A visualizacao de roadmap atual exibe todas as 190+ historias simultaneamente sem mecanismos de filtragem, agrupamento dinamico ou codificacao visual, resultando em uma tela que contem muita informacao mas comunica quase nada. O usuario nao consegue responder perguntas basicas como "o que esta atrasado?", "o que esta bloqueado?" ou "quanto ja foi entregue?". Esta epic resolve os 11 problemas criticos de usabilidade identificados na auditoria da interface, transformando o roadmap de um diagrama estatico em uma ferramenta de acompanhamento funcional.

## Atores

- **Gestor de Projeto**: precisa visualizar o progresso geral, identificar gargalos, dependencias e atrasos para tomar decisoes de priorizacao
- **Desenvolvedor**: precisa localizar rapidamente suas historias, entender dependencias e verificar prazos

## Fluxos Principais

### Fluxo 1 — Navegacao por colapso/expansao de grupos

1. Gestor abre o roadmap e ve apenas os grupos (waves/features) como barras-resumo com percentual de conclusao
2. Gestor clica em um grupo para expandir e ver as historias individuais daquele grupo
3. Gestor clica novamente no grupo para colapsar e voltar a visao resumida
4. Sistema preserva o estado de expansao durante a sessao

### Fluxo 2 — Identificacao visual por status

1. Usuario abre o roadmap e ve barras coloridas de acordo com o status (backlog=cinza, execucao=azul, testes=amarelo, concluido=verde, impedido=vermelho)
2. Usuario identifica de relance quais historias estao bloqueadas (vermelho) e quais foram concluidas (verde)
3. Sistema exibe uma legenda de cores visivel na interface

### Fluxo 3 — Filtragem e busca

1. Usuario aplica filtros por wave, status, responsavel ou componente usando controles na toolbar
2. Sistema atualiza o grafico mostrando apenas as historias que atendem aos filtros
3. Usuario digita parte do nome de uma historia no campo de busca
4. Sistema destaca ou filtra as historias correspondentes

### Fluxo 4 — Visualizacao de progresso e dependencias

1. Usuario ve barras parcialmente preenchidas indicando o progresso de cada historia (baseado no status)
2. Usuario passa o mouse sobre uma historia e ve setas/linhas conectando-a as suas dependencias
3. Sistema exibe tooltip enriquecido com nome, status, responsavel, story points, datas, duracao e dependencias

### Fluxo 5 — Referencia temporal e orientacao

1. Usuario abre o roadmap e ve uma linha vertical destacada indicando "hoje"
2. Usuario identifica imediatamente o que ja deveria ter sido feito (a esquerda da linha) e o que esta por vir (a direita)
3. Rodape exibe resumo estatistico com historias por status, nao apenas contagem total

## Regras de Negocio

- As cores das barras devem seguir o STATUS_PALETTE ja definido no design system (BACKLOG=#E5E5E5, EXECUCAO=#DBEAFE, TESTES=#FEF3C7, CONCLUIDO=#DDF3E4, IMPEDIDO=vermelho)
- A legenda de cores deve ser sempre visivel quando ha historias renderizadas
- Grupos colapsados devem exibir uma barra-resumo que cobre o intervalo de datas min/max do grupo com o percentual de conclusao
- A linha de "hoje" deve ser visualmente distinta (cor contrastante, ex: vermelho tracejado) e presente sempre que a data atual estiver dentro do intervalo da timeline
- Labels de historias devem ter no minimo 14px de altura para legibilidade; se o espaco nao comportar, o sistema deve colapsar automaticamente o grupo
- Botoes da toolbar devem ter icone E tooltip descritivo — nenhum botao pode ficar sem identificacao visual
- Historias com status IMPEDIDO devem ter destaque visual adicional (borda ou icone de alerta)
- Filtros aplicados devem ser indicados visualmente na toolbar (ex: badge ou cor de destaque)
- Dependencias devem ser representadas por setas conectando a barra da historia predecessora a barra da historia dependente
- O tooltip deve incluir: nome, status, responsavel, story points, data inicio, data fim, duracao em dias uteis, componente e lista de dependencias

## Escopo

**Inclui**:
- Correcao de colisao e sobreposicao de rotulos (issue 1)
- Codificacao por cor baseada em status com legenda (issue 2)
- Hierarquia visual forte entre waves/grupos com separadores e indentacao (issue 3)
- Mecanismo de colapso/expansao de grupos (issues 3 e 10)
- Linha de referencia temporal "hoje" visivel e destacada (issue 6)
- Indicadores de dependencia entre historias (issue 7)
- Indicacao visual de progresso nas barras (issue 8)
- Identificacao visual dos botoes da toolbar com icones e tooltips (issue 5)
- Rodape com informacao estatistica enriquecida por status (issue 9)
- Filtros por wave, status, responsavel e componente (issue 10)
- Campo de busca por nome de historia (issue 10)
- Scroll sincronizado entre painel de labels e area de barras (issue 10)

**Nao inclui**:
- Escala temporal nao-linear ou zoom semantico (issue 4 — mitigado pelo colapso de grupos)
- Minimap/visao reduzida do Gantt (issue 10 — complexidade desproporcional ao valor)
- Responsividade para dispositivos mobile (issue 11 — aplicacao desktop PySide6)
- Drag-and-drop para reordenar historias ou alterar datas
- Edicao de historias diretamente no roadmap
- Alteracoes no schema do banco de dados
- Novos use cases na camada de aplicacao (dados ja disponiveis nos DTOs existentes)

## Criterios de Sucesso

- Todos os rotulos de historias sao legiveis sem sobreposicao quando o grupo esta expandido (zoom 100%)
- Usuario identifica o status de qualquer historia em menos de 2 segundos pela cor da barra
- Usuario localiza uma historia especifica pelo nome em menos de 5 segundos usando busca
- Linha de "hoje" e visivel sem necessidade de scroll ou zoom
- 100% dos botoes da toolbar possuem icone e tooltip descritivo
- Dependencias entre historias sao visiveis ao interagir com a barra (hover ou clique)
- Roadmap com 200+ historias renderiza em menos de 3 segundos
- Colapsar/expandir grupos responde em menos de 500ms
- Nenhum botao ou controle fica sem identificacao visual
- Rodape exibe contagem de historias por status (backlog, execucao, testes, concluido, impedido)
