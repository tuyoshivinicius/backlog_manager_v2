## Titulo

Visualização de Roadmap

## Descricao

Após finalizar o planejamento (cálculo de cronograma e alocação de desenvolvedores), o usuário precisa visualizar o roadmap completo do backlog em uma tela dedicada fullscreen. O roadmap apresenta as histórias organizadas na linha do tempo, agrupadas por feature ou componente, com indicadores de progresso, criticidade e atraso. O objetivo é oferecer uma visão panorâmica e interativa do estado do projeto, facilitando a tomada de decisão e a comunicação com stakeholders.

## Atores

- **Gestor de Projeto**: visualiza o roadmap para acompanhar progresso, identificar gargalos e comunicar cronograma à equipe e stakeholders

## Fluxos Principais

1. Gestor finaliza o planejamento (scheduling + alocação) na tela principal
2. Gestor aciona a visualização de roadmap (via menu ou botão)
3. Sistema abre tela fullscreen exibindo o gráfico de timeline com as histórias agrupadas por feature/componente
4. Gestor alterna o modo de agrupamento entre "por Feature" e "por Componente"
5. Gestor visualiza barras horizontais representando cada história posicionadas no eixo temporal (start_date → end_date)
6. Gestor identifica visualmente o percentual de conclusão de cada feature/componente através de indicador de progresso no cabeçalho do grupo
7. Gestor ativa/desativa indicadores visuais opcionais: itens em atraso, criticidade de dependências, datas/deadlines
8. Gestor passa o mouse sobre uma história e vê tooltip rico com: desenvolvedor alocado, story points, status, dependências, datas (início/fim), duração e componente
9. Gestor fecha a tela de roadmap e retorna à tela principal

## Regras de Negocio

- O roadmap só pode ser aberto se existirem histórias com datas calculadas (start_date e end_date preenchidos); caso contrário, exibir mensagem orientando o usuário a executar o planejamento primeiro
- O percentual de conclusão de uma feature/componente é calculado pela proporção de histórias com status CONCLUIDO em relação ao total de histórias do grupo
- Uma história é considerada "em atraso" quando sua end_date é anterior à data atual e seu status não é CONCLUIDO
- A criticidade de dependências deve destacar histórias que bloqueiam outras histórias (têm dependentes) e que estão com status IMPEDIDO ou em atraso
- O design do gráfico deve ser minimalista — controles e botões discretos, priorizando a área do gráfico
- Os indicadores visuais (atraso, dependências, deadlines) devem ser ativáveis/desativáveis individualmente, e a preferência do usuário deve ser persistida entre sessões
- A tela deve respeitar o design system existente (cores, tipografia, tokens do tema)

## Escopo

**Inclui**:
- Tela fullscreen dedicada ao roadmap com gráfico de timeline (Gantt-like)
- Agrupamento de histórias por feature ou por componente
- Barras horizontais representando período de cada história (start_date → end_date)
- Indicador de percentual de conclusão por grupo (feature/componente)
- Indicadores visuais opcionais: atraso, criticidade de dependências, datas/deadlines
- Toggle para ativar/desativar cada tipo de indicador visual
- Tooltip rico ao passar o mouse sobre uma história (desenvolvedor, SP, status, dependências, datas, duração, componente)
- Persistência das preferências de indicadores visuais (QSettings)
- Navegação de volta à tela principal

**Nao inclui**:
- Edição de histórias diretamente no roadmap (somente visualização)
- Drag-and-drop para reordenar ou realocar histórias
- Exportação do roadmap como imagem ou PDF
- Filtros avançados por desenvolvedor, status ou sprint
- Zoom temporal (scroll horizontal com granularidade variável)
- Integração com ferramentas externas (Jira, Linear, etc.)

## Criterios de Sucesso

- Usuário consegue abrir o roadmap e visualizar todas as histórias com datas em menos de 3 segundos
- 100% das histórias com datas calculadas aparecem posicionadas corretamente na timeline
- Percentual de conclusão exibido corresponde exatamente à proporção de histórias CONCLUIDO por grupo
- Indicadores visuais de atraso e dependência são visíveis sem necessidade de interação (quando ativados)
- Tooltip exibe todas as informações relevantes da história ao hover
- Preferências de indicadores visuais persistem entre sessões
- O layout permanece legível com backlogs de até 200 histórias
