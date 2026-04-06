## Titulo

Refatoracao do Roadmap Visualization

## Descricao

O roadmap de visualizacao do backlog precisa ser completamente refatorado para resolver problemas de performance (tela trava durante carregamento de dados), completude (historias nao aparecem na visualizacao) e design (visual desagradavel e pouco profissional). A refatoracao deve simplificar a funcionalidade removendo filtros desnecessarios, adotar uma engine de renderizacao baseada em matplotlib para graficos mais bonitos e profissionais, e garantir que todas as operacoes de I/O sejam asincronas para nao bloquear a interface. O objetivo e entregar uma visualizacao limpa, bonita e funcional que sirva como base solida para futuras melhorias.

## Atores

- **Gerente de Projeto**: visualiza o roadmap para acompanhar o progresso das historias alocadas, agrupando por feature ou componente

## Fluxos Principais

1. Gerente de Projeto abre o roadmap via menu ou atalho (Ctrl+Shift+R)
2. O sistema carrega os dados de historias e features de forma assincrona, exibindo indicador de progresso sem travar a interface
3. O sistema renderiza um grafico de timeline (Gantt-like) usando matplotlib, mostrando TODAS as historias que possuem datas calculadas
4. Gerente de Projeto visualiza as historias agrupadas por Feature (padrao) com barras coloridas por status
5. Gerente de Projeto pode alternar o agrupamento para Componente via controle na toolbar
6. Gerente de Projeto pode navegar pelo grafico (scroll horizontal/vertical e zoom)
7. Gerente de Projeto pode passar o mouse sobre uma barra para ver detalhes da historia (tooltip)

## Regras de Negocio

- TODAS as historias com start_date e end_date calculados devem aparecer no roadmap — nenhuma historia pode ser omitida
- Historias sem feature ou componente devem ser agrupadas sob "Sem classificacao"
- As cores das barras devem seguir o STATUS_PALETTE existente no design system (BACKLOG=cinza, EXECUCAO=azul, TESTES=amarelo, CONCLUIDO=verde, IMPEDIDO=vermelho)
- O carregamento de dados deve ser 100% assincrono — a dialog nunca deve travar ou congelar
- O unico filtro disponivel e o agrupamento por Feature ou Componente — nenhum outro filtro deve existir
- Indicadores visuais (overdue, critical deps, deadlines) devem ser removidos
- A persistencia de preferencias via QSettings deve ser removida (nao ha mais preferencias a salvar alem do agrupamento)
- O grafico deve ser renderizado usando matplotlib embarcado na dialog PySide6
- Cada grupo deve exibir o nome e percentual de conclusao
- A dialog deve abrir maximizada

## Escopo

**Inclui**:
- Refatoracao completa da engine de renderizacao de QGraphicsView para matplotlib
- Correcao do bug de historias faltantes na visualizacao
- Redesign visual completo do roadmap usando matplotlib com visual profissional
- Refatoracao do ViewModel para I/O 100% assincrono
- Remocao de todos os filtros de indicadores visuais (overdue, critical deps, deadlines)
- Remocao da persistencia de indicadores via QSettings
- Manutencao do filtro de agrupamento Feature/Componente
- Tooltip ao passar o mouse sobre barras de historias
- Scroll e zoom na visualizacao
- Atualizacao dos testes unitarios para a nova implementacao

**Nao inclui**:
- Adicao de novos filtros (por developer, status, sprint, etc.)
- Exportacao como imagem ou PDF
- Drag-and-drop ou edicao de historias no roadmap
- Linhas de dependencia entre historias
- Novos indicadores visuais
- Alteracoes no schema do banco de dados
- Alteracoes nos use cases existentes (ListStoriesUseCase, ListFeaturesUseCase)

## Criterios de Sucesso

- 100% das historias com datas calculadas aparecem no roadmap (zero historias faltantes)
- O carregamento de dados nao bloqueia a interface em nenhum momento
- O visual do roadmap e profissional e agradavel, usando matplotlib como engine
- O agrupamento por Feature e Componente funciona corretamente com percentual de conclusao
- Todos os testes unitarios existentes sao atualizados e passam
- A complexidade do codigo e menor que a implementacao anterior (menos classes, menos estados)
- O roadmap renderiza 200+ historias em menos de 3 segundos
