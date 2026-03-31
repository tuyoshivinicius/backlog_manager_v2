# Research: Alocacao Manual de Desenvolvedores

**Branch**: `028-manual-allocation` | **Date**: 2026-03-31

## R1: Como detectar double-click na coluna "Desenvolvedor" sem afetar edicao inline do Status

**Decision**: Conectar ao signal `doubleClicked(QModelIndex)` da StoryTableView e verificar `index.column() == 7` (Desenvolvedor). A coluna Status (6) ja usa `SelectedClicked` como edit trigger via delegate — o double-click na coluna 7 nao conflita porque Developer nao tem flag `ItemIsEditable`.

**Rationale**: O signal `doubleClicked` e emitido por `QAbstractItemView` para qualquer celula. Como Developer (col 7) nao possui `ItemIsEditable` no `flags()`, nao ha conflito com o mecanismo de edicao inline do Status (col 6). A alternativa seria sobrescrever `mouseDoubleClickEvent`, mas o signal e mais limpo e segue o padrao Qt.

**Alternatives considered**:
- Override `mouseDoubleClickEvent` na StoryTableView: mais intrusivo, requer mapeamento manual de coordenadas para indices.
- Criar delegate customizado para Developer com `createEditor()`: desnecessario — o spec pede dialog, nao editor inline.

## R2: Como calcular disponibilidade de desenvolvedores para uma data especifica

**Decision**: Reutilizar `AllocationService._has_period_overlap()` para verificar se cada desenvolvedor possui historias cujo periodo se sobrepoem com o periodo da historia-alvo. Dado uma lista de todas as historias e uma data de inicio candidata, recalcular `end_date` via `SchedulingService.calculate_story_dates()` e testar sobreposicao por desenvolvedor.

**Rationale**: A logica de overlap ja existe no dominio e e a mesma usada pela alocacao automatica. Criar logica paralela violaria DRY e potencialmente divergiria do comportamento automatico. `_has_period_overlap` e static e sem side effects, ideal para reutilizacao.

**Alternatives considered**:
- Nova funcao `is_developer_available()` no AllocationService: exigiria modificar servico de dominio existente, violando FR-010.
- Calcular no ViewModel diretamente: violaria separacao de camadas — logica de negocio ficaria na Presentation.

## R3: Como obter a recomendacao do algoritmo de alocacao para um unico story-developer pair

**Decision**: Criar um Application Use Case (`GetAllocationRecommendationUseCase`) que, dada uma historia e uma data de inicio, executa a mesma logica de selecao de `AllocationService._select_developer()` para identificar o desenvolvedor recomendado. Este use case buscara os dados necessarios (stories, developers, dependencies, config) e aplicara a estrategia configurada.

**Rationale**: FR-004 exige que a recomendacao coincida com o resultado da alocacao automatica (SC-004). Reutilizar `_select_developer` garante consistencia. Como os metodos de `AllocationService` sao static e stateless, podemos chama-los sem modificar o servico. O Use Case encapsula a obtencao dos dados e a chamada ao dominio, seguindo Clean Architecture.

**Alternatives considered**:
- Chamar `AllocationService._select_developer()` diretamente do ViewModel: violaria camadas (Presentation → Domain sem Application).
- Implementar logica de recomendacao separada: risco de divergencia com algoritmo automatico.

## R4: Como recalcular end_date ao alterar start_date na dialog

**Decision**: Usar `SchedulingService.calculate_story_dates()` com a nova start_date e os parametros existentes (velocity, dependency end dates, holidays). Esta funcao retorna `(start_date, end_date, duration)` ajustados para dias uteis.

**Rationale**: `SchedulingService` ja lida com dias uteis, feriados brasileiros e dependencias. Reutiliza-lo garante consistencia com o agendamento automatico.

**Alternatives considered**:
- Calcular duration simples via `calculate_duration()` + `add_workdays()`: nao considera dependencias corretamente.
- Nao recalcular end_date: violaria FR-008.

## R5: Como restringir date picker a dias uteis futuros

**Decision**: Usar `QDateEdit` com restricao `setMinimumDate(date.today() + 1 dia util)`. Para bloquear fins de semana e feriados, conectar ao signal `dateChanged` e ajustar automaticamente para o proximo dia util via `SchedulingService.next_workday()`. Opcionalmente, usar `QCalendarWidget` customizado que desabilita dias nao-uteis visualmente.

**Rationale**: PySide6 nao oferece restricao nativa de dias uteis em `QDateEdit`. A abordagem de auto-correcao via signal e simples e eficaz — o usuario recebe feedback visual imediato. `SchedulingService.next_workday()` ja existe e usa `BRAZILIAN_HOLIDAYS_2026_2028`.

**Alternatives considered**:
- QCalendarWidget customizado com `setDateTextFormat`: maior complexidade visual mas melhor UX. Pode ser adicionado como melhoria futura.
- Validacao apenas na confirmacao: UX inferior — usuario so descobre o erro ao confirmar.

## R6: Como persistir a alocacao manual (developer_id + start_date + end_date)

**Decision**: Usar `EditStoryUseCase` existente que ja suporta atualizacao de `developer_id`, `start_date` e `end_date` na historia. Se a data nao foi alterada, apenas persistir `developer_id` via `AssignDeveloperUseCase`.

**Rationale**: Reutilizar use cases existentes (FR-010). `EditStoryUseCase` ja valida existencia de story e developer, e persiste via Unit of Work. Nao requer criacao de novo use case de persistencia.

**Alternatives considered**:
- Novo `ManualAllocationUseCase` dedicado: redundante — `EditStoryUseCase` ja cobre o cenario.
- Chamar repositorios diretamente do ViewModel: violaria camadas.

## R7: Como a dialog obtém a estrategia de alocacao configurada no projeto

**Decision**: A estrategia `allocation_criteria` atualmente usa default `LOAD_BALANCING` no `AllocationViewModel.execute()`. O `ConfigDialogViewModel` nao persiste esse parametro em QSettings. Para a dialog de alocacao manual, o ViewModel da dialog lera o mesmo default ou, se o `ConfigDialogViewModel` for estendido para persistir `allocation_criteria`, usara o valor persistido.

**Rationale**: O spec (FR-004) diz "usar a estrategia atualmente configurada no projeto". Atualmente essa configuracao esta hardcoded como default. Para manter consistencia, a dialog deve ler o mesmo default. Se futuramente `allocation_criteria` for exposto na UI de configuracao, ambos os fluxos (manual e automatico) devem ler do mesmo local.

**Alternatives considered**:
- Hardcodar LOAD_BALANCING na dialog: funciona mas nao escala se a config for exposta.
- Adicionar campo ao ConfigDialogViewModel + QSettings: escopo maior, pode ser feito nesta feature ou como melhoria futura.

## R8: Layout da dialog — como separar desenvolvedores livres e ocupados

**Decision**: Usar `QTreeWidget` (ou `QListWidget` com secoes) com dois grupos: "Livres" (expandido) e "Ocupados" (expandido). Cada item de desenvolvedor ocupado tera sub-itens mostrando as historias que o mantem ocupado. Itens ocupados terao foreground greyed out e serao nao-selecionaveis (`Qt.ItemFlag.NoItemFlags`). O desenvolvedor recomendado recebe destaque visual (icone estrela ou badge "Recomendado").

**Rationale**: `QTreeWidget` permite agrupar itens em secoes com subitens naturalmente, ideal para mostrar historias que ocupam cada dev. Segue o design system existente usando DESIGN_TOKENS para cores e espacamentos.

**Alternatives considered**:
- Duas `QListWidget` separadas: nao permite sub-itens para historias.
- `QTableWidget`: mais complexo para hierarquia secao/subitens.
- Custom widget com QPainter: overengineering para esta necessidade.
