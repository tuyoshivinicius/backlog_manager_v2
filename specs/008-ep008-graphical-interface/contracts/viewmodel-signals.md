# ViewModel Signals Contract

## MainWindowViewModel

| Signal | Payload | Descricao | Emitido Quando |
|--------|---------|-----------|----------------|
| stories_changed | - | Lista de historias mudou | Apos load, create, edit, delete, move priority |
| story_selected | str (story_id) | Historia foi selecionada | Usuario clica em linha da tabela |
| loading | bool | Estado de carregamento | True no inicio, False no fim de operacao |
| error_occurred | str | Mensagem de erro | Excecao capturada |

## StoryDialogViewModel

| Signal | Payload | Descricao | Emitido Quando |
|--------|---------|-----------|----------------|
| saved | - | Historia salva com sucesso | Apos create/edit bem-sucedido |
| error_occurred | str | Mensagem de erro de validacao | Campo invalido ou erro de persistencia |
| features_loaded | list[FeatureOutputDTO] | Features carregadas | Apos carregar features para dropdown |

## AllocationViewModel

| Signal | Payload | Descricao | Emitido Quando |
|--------|---------|-----------|----------------|
| allocation_started | - | Alocacao iniciou | Inicio do execute() |
| allocation_completed | AllocationMetricsDTO | Alocacao completou | Fim bem-sucedido do execute() |
| allocation_error | str | Erro na alocacao | Excecao durante alocacao |
| warnings_updated | list[str] | Lista de warnings | Alocacao completou com warnings |
| progress_updated | float | Progresso 0.0-1.0 | (Opcional) Durante alocacao longa |

## DeveloperDialog (Inline Logic)

| Signal | Payload | Descricao | Emitido Quando |
|--------|---------|-----------|----------------|
| developers_changed | - | Lista de desenvolvedores mudou | Apos add, edit, delete |

## FeatureDialog (Inline Logic)

| Signal | Payload | Descricao | Emitido Quando |
|--------|---------|-----------|----------------|
| features_changed | - | Lista de features mudou | Apos add, edit, delete |

## DependencyPanel

| Signal | Payload | Descricao | Emitido Quando |
|--------|---------|-----------|----------------|
| dependency_added | str, str | story_id, depends_on_id | Dependencia adicionada |
| dependency_removed | str, str | story_id, depends_on_id | Dependencia removida |
| error_occurred | str | Mensagem de erro | Ciclo detectado ou erro |

## View -> ViewModel Method Calls

### MainWindowViewModel
- load_stories() -> async
- create_story(dto: CreateStoryInputDTO) -> async
- edit_story(dto: EditStoryInputDTO) -> async
- delete_story(story_id: str) -> async
- move_priority_up(story_id: str) -> async
- move_priority_down(story_id: str) -> async
- select_story(story_id: str) -> sync

### StoryDialogViewModel
- set_mode(mode: Literal["create", "edit"]) -> sync
- set_story(story: StoryOutputDTO) -> sync (para edit mode)
- save() -> async
- validate() -> bool (sync)

### AllocationViewModel
- execute(input_dto: ExecuteAllocationInputDTO) -> async
- can_execute() -> bool (sync) - retorna False se ja executando
