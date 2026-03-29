# Prompt: Criar Especificacao Tecnica do EP-021 — Estilizacao de Dialogs

<role>
Voce e um Especialista em UI/UX com PySide6/Qt, com profundo conhecimento em:
- QDialog com QFormLayout/QVBoxLayout estilizado via objectNames + QSS centralizado
- QComboBox populado dinamicamente (lista de desenvolvedores + opcao neutra "Nenhum")
- Validacao em tempo real (on-blur/focusOut) com feedback visual inline (borda @error, mensagem sob campo)
- QLabel com indicador obrigatorio (*) e contagem de caracteres restantes
- QPushButton com icones SVG, hover effect via QSS, estados disabled
- QListWidget com item height customizado, hover effect, e estado vazio (QLabel sobreposto)
- QProgressBar estilizada via QSS para operacoes de import/export
- Padrao MVVM aplicado a camada de apresentacao (Views renderizam, ViewModels validam e fornecem dados)
- Estilizacao de widgets via QSS com seletores por #objectName (especificidade alta)
- Testes de GUI com pytest-qt (dialogs, signals, validacao de campos, estados visuais)
- Wiring de Use Cases existentes (ListDevelopersUseCase, AssignDeveloperUseCase) via ViewModel

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001, expandida em EP-008, EP-017, EP-019)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **UI**: PySide6 6.6.1+ com padrao MVVM
- **Async/Qt**: qasync para integracao asyncio <-> Qt event loop
- **Persistencia**: aiosqlite (async SQLite)
- **DTOs**: Pydantic
- **Testes**: pytest + pytest-cov + pytest-asyncio + pytest-qt
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD, MVVM (na Presentation)

### Estado Atual do Codigo (Implementado em EP-001 a EP-020)

**StoryDialog (EP-008):**
- `StoryDialog(container: DIContainer, mode: str, story: StoryOutputDTO | None, parent: QWidget | None)`
- Campos: Componente (QLineEdit), Nome (QLineEdit), Story Points (QComboBox: 3,5,8,13), Feature (QComboBox)
- Modo "create": todos campos editaveis. Modo "edit": Componente desabilitado
- Validacao via `StoryDialogViewModel.validate()` → retorna `(bool, str)`
- **NAO possui** campo Desenvolvedor — deve ser adicionado (RF-STORY-007)
- **NAO possui** validacao on-blur — apenas validacao ao clicar Salvar
- **NAO possui** indicador obrigatorio (*) nem contagem de caracteres
- **NAO possui** objectNames para seletores QSS

**StoryDialogViewModel (EP-008):**
- Signals: `saved`, `error_occurred(str)`, `features_loaded`
- Propriedades: `component`, `name`, `story_points`, `feature_id`
- Metodos: `set_story()`, `set_mode()`, `validate()`, `load_features()`, `save()`
- **NAO possui** propriedade `developer_id` nem metodo `load_developers()`
- **NAO possui** validacao por campo individual — apenas `validate()` global

**DeveloperDialog (EP-008):**
- Dialog modal com QListWidget para CRUD de desenvolvedores
- Botoes: Adicionar, Editar, Remover, Fechar (texto puro, sem icones)
- **NAO possui** icones SVG nos botoes
- **NAO possui** hover effect na lista
- **NAO possui** estado vazio orientativo quando lista vazia

**FeatureDialog (EP-008):**
- Dialog modal com QListWidget para CRUD de features
- Lista exibe nome simples da feature
- **NAO possui** formato "Onda N — Nome da Feature"
- **NAO possui** estado vazio orientativo

**ConfirmDeleteDialog (EP-008):**
- Dialog de confirmacao simples com texto e botoes OK/Cancel
- **NAO possui** icone de alerta (warning-triangle.svg)
- **NAO possui** botao com cor @error
- **NAO possui** texto descritivo com ID e Nome

**Progress/Result Dialogs para Import/Export:**
- **NAO existem** como componentes estilizados separados — import/export usa dialogs genericos
- Devem ser criados como componentes reutilizaveis

**Design system (EP-017):**
- `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS com cores, fontes, espacamento, raios, sombras. STATUS_PALETTE com 5 status
- `src/backlog_manager/presentation/theme/stylesheet.qss` — stylesheet centralizado (~17KB)
- Cores semanticas disponiveis: error-bg (#FECACA), error-fg (#B91C1C), warning-bg (#FEF3C7), warning-fg (#B45309), success-bg, info-bg
- Icones SVG disponiveis em `src/backlog_manager/assets/icons/`: plus.svg, pencil-simple.svg, trash.svg, x.svg, warning-triangle.svg, users.svg, etc.

**DIContainer (container.py):**
- `create_list_developers_use_case(uow)` → ListDevelopersUseCase (retorna ListDevelopersOutputDTO com lista de DeveloperOutputDTO)
- `create_assign_developer_use_case(uow)` → AssignDeveloperUseCase
- `create_list_features_use_case(uow)` → ListFeaturesUseCase
- Todos os use cases ja existem e estao registrados

**StoryOutputDTO:**
- Campos relevantes: `developer_id: int | None`, `developer_name: str | None`, `feature_id: int | None`, `feature_name: str | None`, `wave: int`

**DeveloperOutputDTO:**
- Campos: `id: int`, `name: str`

**O que NAO existe (EP-021 deve criar/modificar):**
- objectNames em widgets de dialogs para seletores QSS por #id
- Campo Desenvolvedor (QComboBox) no StoryDialog (modo edicao)
- Propriedade developer_id e metodo load_developers() no StoryDialogViewModel
- Validacao on-blur em campos obrigatorios (Componente, Nome)
- Indicadores de campo obrigatorio (*) e contagem de caracteres
- Icones SVG nos botoes do DeveloperDialog
- Hover effect na lista do DeveloperDialog
- Estados vazios orientativos em DeveloperDialog e FeatureDialog
- Formato "Onda N — Nome" na lista do FeatureDialog
- Icone warning-triangle.svg e botao vermelho no ConfirmDeleteDialog
- Texto descritivo "Excluir [ID] — [Nome]? Esta acao nao pode ser desfeita." no ConfirmDeleteDialog
- Progress dialog com QProgressBar estilizada para import/export
- Result dialog com contagens para import/export

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **StoryDialogViewModel nao possui developer_id nem load_developers()**: O ViewModel atual gerencia component, name, story_points, feature_id. Para adicionar o dropdown de Desenvolvedor, e necessario adicionar: (a) propriedade `developer_id: int | None`, (b) metodo `load_developers()` usando ListDevelopersUseCase, (c) signal `developers_loaded`. A spec deve definir se reutiliza o padrao de load_features() (signal + metodo async) ou adota abordagem diferente. Restricao: nao alterar assinatura publica existente — apenas adicionar novos membros.

2. **Validacao on-blur e responsabilidade da View ou do ViewModel?**: A constituicao §XIX define que Views renderizam e ViewModels contem logica. Validacao on-blur tem componente visual (borda vermelha, mensagem) e logico (campo vazio?). A spec deve definir: (a) View detecta focusOut e chama metodo de validacao no ViewModel, (b) ViewModel retorna resultado de validacao por campo, (c) View aplica estilo visual baseado no resultado. O ViewModel.validate() atual retorna (bool, str) global — a spec deve definir se adiciona validate_field(field_name) ou se a View faz validacao visual simples (campo vazio) independentemente.

3. **Campo Desenvolvedor apenas no modo edicao**: O epico especifica que o dropdown de Desenvolvedor aparece apenas no modo edicao (nao no modo criacao). A spec deve definir: (a) como ocultar/mostrar o campo baseado no modo, (b) se usa QComboBox.setVisible(False) no modo create ou se nao cria o widget.

4. **Botao Salvar desabilitado quando formulario invalido**: O epico especifica que [Salvar] fica desabilitado se formulario invalido. Atualmente, validacao ocorre apenas ao clicar Salvar. A spec deve definir: (a) quando re-validar (a cada focusOut? a cada textChanged?), (b) como conectar validacao com estado do botao, (c) impacto em performance (validar a cada keystroke vs debounce).

5. **Estados vazios em DeveloperDialog e FeatureDialog coexistem com QListWidget**: Quando a lista esta vazia, o QListWidget fica visivel mas vazio. A spec deve definir: (a) se usa QLabel sobreposto ao QListWidget (QStackedWidget), (b) se esconde QListWidget e mostra QLabel, ou (c) se usa item customizado no proprio QListWidget. O visual deve ser: texto @neutral-400, centralizado.

6. **ConfirmDeleteDialog e generico — usado para stories, devs e features**: O dialog deve exibir "Excluir [ID] — [Nome]?" mas devs nao tem ID textual (tem ID numerico) e features tambem tem formato diferente. A spec deve definir: (a) assinatura do construtor (aceita entity_type + display_text?), (b) formato do texto para cada tipo de entidade, (c) se mantem compatibilidade retroativa com chamadas existentes.

7. **Progress/Result Dialogs nao existem — escopo de criacao vs refatoracao**: O epico classifica como REFATORACAO (DLG-008) mas os dialogs nao existem como componentes separados. A spec deve definir: (a) se cria novos widgets (ProgressDialog, ResultDialog), (b) se integra com MainWindow ou funciona standalone, (c) como se conecta com operacoes de import/export existentes (que podem ser sincronas no momento).

8. **Import/Export pode ser sincrono — progress dialog bloqueia UI?**: Se operacoes de import/export sao sincronas, QProgressBar nao atualiza durante execucao. A spec deve definir: (a) se converte operacao para async com qasync, (b) se usa QProgressBar em modo indeterminate (sem percentual), (c) se e aceitavel bloquear brevemente.

### Alinhamento com Constituicao do Projeto

- **§I Clean Architecture**: Dialogs e ViewModels na Presentation layer. Use cases na Application layer — apenas wiring.
- **§II DDD**: Nenhuma logica de dominio nos dialogs — apenas apresentacao e validacao de entrada.
- **§IV Dependency Injection**: ListDevelopersUseCase, AssignDeveloperUseCase injetados via DIContainer.
- **§VIII Async**: Chamadas a use cases seguem padrao async existente no ViewModel.
- **§IX Simplicidade**: Estilizar dialogs existentes, nao criar novos desnecessariamente. Reusar objectNames + QSS.
- **§X Type Hints**: Todos os metodos novos com type hints completas.
- **§XIV Estrategia de Testes**: Testes unitarios para validacao de campos no ViewModel, testes para load_developers.
- **§XIX Padroes UI/UX (MVVM)**: Views renderizam, ViewModels validam. Validacao on-blur: View detecta evento, ViewModel valida, View aplica estilo.
- **§XX Validacao e Sanitizacao**: Validacao de entrada na Presentation layer (campos obrigatorios, limites de caracteres).
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-021_estilizacao-dialogs.md` — requisitos, escopo, criterios de aceite, especificacao dos componentes DLG-001 a DLG-008, UX-002, UX-012, UX-013
2. **SRS completo**: `srs.md` — secoes §3.1 RF-STORY-001 (criar historia), §3.1 RF-STORY-002 (editar historia), §3.1 RF-STORY-007 (atribuir desenvolvedor), §3.1 RF-STORY-010 (validar campos), §3.2 RF-DEV-001/002/003/004 (CRUD desenvolvedores), §3.3 RF-FEAT-001/002/003 (CRUD features), §4.2 RNF-USAB-003 (acessibilidade), §4.2 RNF-USAB-004 (curva de aprendizado), §4.3 RNF-CONF-002 (recuperacao de erros), §4.1 RNF-PERF-002 (responsividade UI <= 100ms), §4.5 RNF-MANT-001 (manutenibilidade), §8.2 (convencoes de nomenclatura)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture, §IV Dependency Injection, §VIII Async, §IX Simplicidade, §X Type Hints, §XIV Estrategia de Testes, §XIX Padroes de UI/UX (MVVM), §XX Validacao e Sanitizacao
4. **StoryDialog atual**: `src/backlog_manager/presentation/views/story_dialog.py` — layout atual, campos, construtor, conexao com ViewModel
5. **StoryDialogViewModel atual**: `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py` — signals, propriedades, validate(), save(), load_features(), padrao async
6. **DeveloperDialog atual**: `src/backlog_manager/presentation/views/developer_dialog.py` — layout, QListWidget, botoes, uso de use cases via container
7. **FeatureDialog atual**: `src/backlog_manager/presentation/views/feature_dialog.py` — layout, QListWidget, formato atual dos itens
8. **ConfirmDeleteDialog atual**: `src/backlog_manager/presentation/views/confirm_delete_dialog.py` — construtor, layout, texto, botoes, assinatura publica
9. **Design system**:
   - `src/backlog_manager/presentation/theme/theme.py` — DESIGN_TOKENS (cores semanticas: error-bg, error-fg, warning-bg, warning-fg, neutral-400), STATUS_PALETTE
   - `src/backlog_manager/presentation/theme/stylesheet.qss` — seletores QSS existentes, verificar quais ja cobrem dialogs
10. **DTOs**:
    - `src/backlog_manager/application/dto/story/story_output_dto.py` — StoryOutputDTO com campos developer_id, developer_name
    - `src/backlog_manager/application/dto/developer/developer_output_dto.py` — DeveloperOutputDTO (id, name), ListDevelopersOutputDTO
11. **DIContainer**: `src/backlog_manager/presentation/container.py` — verificar factory methods: create_list_developers_use_case, create_assign_developer_use_case
12. **ListDevelopersUseCase**: `src/backlog_manager/application/use_cases/developer/list_developers.py` — assinatura execute() -> ListDevelopersOutputDTO
13. **Icones SVG disponiveis**: `src/backlog_manager/assets/icons/` — listar icones existentes: plus.svg, pencil-simple.svg, trash.svg, x.svg, warning-triangle.svg, users.svg
14. **MainWindow atual**: `src/backlog_manager/presentation/views/main_window.py` — verificar como dialogs sao abertos (metodos _open_story_dialog, _open_developer_dialog, etc.) para garantir compatibilidade
15. **Testes existentes**:
    - `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py` — testes de validacao e save
    - `tests/integration/presentation/views/` — testes de integracao dos dialogs
16. **Spec EP-017 e EP-018**: Specs anteriores para entender baseline de design system e layout — consultar `specs/017-*/spec.md` e `specs/018-*/spec.md`
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-021 — Estilizacao de Dialogs (GUI-005)`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: estilizar todos os dialogs com visual consistente via objectNames + QSS centralizado, adicionar validacao em tempo real (on-blur) com indicadores de campo obrigatorio e estados de erro inline, adicionar estados vazios orientativos em listas de dialogs, adicionar dropdown de desenvolvedor no StoryDialog (modo edicao) conforme RF-STORY-007, e estilizar feedback de import/export Excel. Este epico **nao cria entidades, value objects, repositorios, services, delegates, FilterProxyModel ou menu de contexto** — trabalha exclusivamente na camada Presentation (Views e ViewModels dos dialogs), com wiring a Use Cases existentes na Application layer.

**Componentes a especificar:**

| ID | Componente | Tipo | Descricao |
|----|------------|------|-----------|
| DLG-001 | StoryDialog | REFATORACAO | Estilizar via QSS (objectNames), adicionar campo Desenvolvedor (QComboBox, modo edicao), validacao on-blur, indicador obrigatorio (*), area de erro inline, contagem de caracteres |
| DLG-002 | DeveloperDialog | REFATORACAO | Icones SVG nos botoes (plus, pencil, trash, x), item height 40px, hover effect via QSS, estado vazio orientativo |
| DLG-003 | FeatureDialog | REFATORACAO | Formato "Onda N — Nome da Feature" na lista, estilizacao consistente, estado vazio orientativo |
| DLG-007 | ConfirmDeleteDialog | REFATORACAO | Icone warning-triangle.svg (32x32px, cor @warning), botao [Confirmar Exclusao] bg @error + texto branco, texto descritivo "Excluir [ID] — [Nome]?" |
| DLG-008 | Progress/Result Dialogs | NOVO | ProgressDialog com QProgressBar estilizada + mensagem, ResultDialog com contagens de import/export |
| UX-002 | Atribuicao Manual Dev | NOVO | Campo "Desenvolvedor" no StoryDialog (QComboBox) com lista de devs + "Nenhum", apenas modo edicao |
| UX-012 | Validacao em Tempo Real | NOVO | On-blur: campo obrigatorio (*), erro visual inline (borda @error, mensagem em fundo @error-light), contagem de caracteres restantes |
| UX-013 | Estados Vazios | NOVO | Mensagens orientativas em DeveloperDialog e FeatureDialog quando listas vazias |

**Artefatos estruturais a especificar:**

| Artefato | Descricao |
|----------|-----------|
| StoryDialog refatorado | objectNames (#storyDialog, #btnSave, #btnCancel, #fieldComponent, #fieldName, etc.), campo Desenvolvedor (QComboBox#fieldDeveloper), validacao on-blur, indicadores obrigatorios, contagem de caracteres, area de erro inline |
| StoryDialogViewModel estendido | Nova propriedade developer_id: int \| None, metodo load_developers() async, signal developers_loaded, validacao por campo validate_field(field_name) |
| DeveloperDialog refatorado | objectNames, icones SVG nos botoes (QIcon de assets/icons/), item height 40px, hover via QSS, estado vazio (QLabel sobreposto ou QStackedWidget) |
| FeatureDialog refatorado | objectNames, formato "Onda N — Nome" nos itens da lista, estado vazio |
| ConfirmDeleteDialog refatorado | objectNames, layout com icone warning-triangle.svg a esquerda + texto descritivo a direita, botao [Confirmar Exclusao] estilizado |
| ProgressDialog (novo) | QDialog modal com QProgressBar + QLabel de mensagem, metodo update_progress(value, message) |
| ResultDialog (novo) | QDialog modal com contagens formatadas (historias, features, avisos) + botao [Fechar] |
| Seletores QSS novos/ajustados | Adicionar ao stylesheet.qss seletores para: #storyDialog, #btnSave, #btnCancel, .error-field, .error-message, .required-indicator, #btnConfirmDelete, .empty-state-label, QProgressBar customizada |
| Testes unitarios | Suite para StoryDialogViewModel (load_developers, validate_field, developer_id property) |

**Criterios de aceite do epico que devem ser cobertos:**
- StoryDialog com bordas arredondadas, espacamento 16px, padding 24px, titulo 16px weight 600
- StoryDialog em modo edicao exibe dropdown Desenvolvedor com lista de devs + "Nenhum"
- Selecionar desenvolvedor e salvar atualiza historia com developer_id
- Campos obrigatorios com asterisco (*) vermelho no label
- Campo obrigatorio vazio ao perder foco: borda @error + mensagem de erro inline
- Botao [Salvar] desabilitado quando formulario invalido
- Contagem de caracteres restantes em campos de texto (ex: "45/200")
- DeveloperDialog com icones SVG nos botoes
- DeveloperDialog com hover effect nos itens da lista
- DeveloperDialog com estado vazio quando lista vazia
- FeatureDialog com formato "Onda N — Nome da Feature"
- FeatureDialog com estado vazio quando lista vazia
- ConfirmDeleteDialog com icone warning-triangle.svg, texto "Excluir [ID] — [Nome]?", botao vermelho
- Import: progress dialog estilizado com QProgressBar durante importacao
- Import: dialog de resultado com contagens (X historias, Y features, Z avisos)
- Export: dialog de resultado com caminho do arquivo
- Todos os dialogs com objectNames para QSS
- Testes existentes passam sem regressao

**IMPORTANTE**: Este epico **nao** cria FilterProxyModel, menu de contexto, barra de busca/filtros (EP-020). **Nao** cria StoryTableModel, delegates, tooltip rico, agrupamento visual por onda (EP-019/EP-022). **Nao** cria ConfigDialog, DependencyDialog, MetricsDialog (ja estilizados em EP-018). **Nao** cria Dialog "Sobre" (EP-022). **Nao** altera logica de dominio, entidades, services ou repositorios.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo componente deve mapear para requisitos do SRS.
   Incluir matriz: Componente <-> RF/RNF <-> Criterio de Aceite do Epico.
   RF-STORY-007 -> UX-002 (campo Desenvolvedor). RF-STORY-001/002 -> DLG-001 (StoryDialog estilizado).
   RF-DEV-001/002/003/004 -> DLG-002 (DeveloperDialog). RF-FEAT-001/002/003 -> DLG-003 (FeatureDialog).
   RF-STORY-003/RF-DEV-003/RF-FEAT-003 -> DLG-007 (ConfirmDeleteDialog).
   RNF-USAB-003 -> UX-012 (validacao), UX-013 (estados vazios). RNF-CONF-002 -> UX-012 (erros inline).

2. **Codigo existente como baseline**: Nao redefinir theme.py, stylesheet.qss (estrutura base),
   entities, services, repositorios, StoryTableModel, delegates, FilterProxyModel, menu de contexto.
   Especificar apenas **refatoracao de dialogs existentes**, **novos widgets de progresso/resultado**,
   **extensao do StoryDialogViewModel**, e **novos seletores QSS**.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Validacao on-blur com separacao MVVM**: A spec deve definir claramente:
   (a) View detecta focusOut event e chama metodo de validacao,
   (b) ViewModel valida e retorna resultado por campo,
   (c) View aplica estilo visual (borda, mensagem) baseado no resultado.
   A validacao visual NAO pode estar no ViewModel. A logica de "campo vazio" NAO pode estar na View.

5. **Campo Desenvolvedor no StoryDialog — modo edicao apenas**: A spec deve definir:
   (a) QComboBox#fieldDeveloper criado mas oculto no modo create (setVisible(False)),
   (b) populado via load_developers() no modo edit,
   (c) primeiro item "Nenhum" (valor None), seguido por devs ordenados por nome,
   (d) pre-seleciona dev atual da historia sendo editada.

6. **Extensao nao-destrutiva do StoryDialogViewModel**: A spec deve garantir que:
   (a) assinatura publica existente NAO e alterada,
   (b) novos membros sao adicionados (developer_id, load_developers, developers_loaded, validate_field),
   (c) metodo save() e estendido para incluir developer_id quando em modo edicao,
   (d) testes existentes continuam passando sem modificacao.

7. **Estados vazios com QStackedWidget ou visibilidade**: A spec deve definir mecanismo
   para alternar entre lista populada e mensagem de estado vazio. Definir: quando verificar
   (apos load, apos add, apos remove), como exibir (texto @neutral-400, centralizado), e
   como restaurar lista quando primeiro item for adicionado.

8. **ConfirmDeleteDialog retrocompativel**: O dialog e usado para stories, devs e features.
   A spec deve definir: (a) construtor que aceita parametros flexiveis (entity_type, display_id, display_name),
   (b) formato do texto para cada tipo, (c) compatibilidade com chamadas existentes no MainWindow.

9. **Progress/Result Dialogs — criacao de novos widgets**: A spec deve definir:
   (a) ProgressDialog como QDialog modal com QProgressBar + QLabel,
   (b) ResultDialog como QDialog modal com QLabel formatado + botao [Fechar],
   (c) ambos com objectNames para QSS,
   (d) como se integram com operacoes de import/export existentes no MainWindow.

10. **Seletores QSS adicionados ao stylesheet existente**: A spec deve listar **todos** os novos
    seletores QSS a adicionar ao stylesheet.qss:
    - Dialogs: QDialog#storyDialog, QDialog#developerDialog, QDialog#featureDialog, QDialog#confirmDeleteDialog
    - Botoes: QPushButton#btnSave, QPushButton#btnCancel, QPushButton#btnConfirmDelete
    - Campos com erro: QLineEdit[error="true"], .error-message (QLabel)
    - Indicador obrigatorio: .required-indicator (QLabel com cor @error-fg)
    - Estado vazio: .empty-state-label (QLabel com cor @neutral-400)
    - Progresso: QProgressBar (chunk, groove)
    A spec deve garantir que novos seletores nao conflitam com existentes.

11. **Icones SVG nos botoes do DeveloperDialog e FeatureDialog**: A spec deve mapear:
    - [+ Adicionar] -> plus.svg
    - [Editar] -> pencil-simple.svg
    - [Remover] -> trash.svg
    - [Fechar] -> x.svg
    Usar QIcon com caminho relativo a assets/icons/. Definir tamanho do icone (16x16 ou 20x20).

12. **Testes unitarios para extensoes do StoryDialogViewModel**: A spec deve especificar:
    - `test_load_developers_returns_list`: load_developers popula lista
    - `test_load_developers_includes_none_option`: lista inclui opcao "Nenhum" (None)
    - `test_developer_id_property`: get/set developer_id
    - `test_validate_field_component_empty`: componente vazio retorna erro
    - `test_validate_field_name_empty`: nome vazio retorna erro
    - `test_validate_field_valid`: campo valido retorna sucesso
    - `test_save_with_developer_id`: save inclui developer_id no modo edicao
    - `test_save_without_developer`: save com developer_id=None funciona

13. **Sem sobreposicao com outros epicos**: Nao especificar:
    - FilterProxyModel, barra de busca, menu de contexto, atalhos (EP-020)
    - StoryTableModel, delegates, tooltip rico, agrupamento visual (EP-019/EP-022)
    - ConfigDialog, DependencyDialog, MetricsDialog (EP-018)
    - Dialog "Sobre" (EP-022)
    - Logica de dominio, entidades, services, repositorios

14. **Consistencia de nomenclatura**: Usar os mesmos nomes de componentes definidos no epico
    (DLG-001 a DLG-008, UX-002, UX-012, UX-013). Nomes de classes e metodos em ingles.
    Textos de interface em PT-BR. Mensagens de erro sem acentos conforme SRS §8.2.

15. **Idioma**: Todos os textos de interface (labels, mensagens de erro, estados vazios, textos de
    botoes, mensagens de progresso/resultado) DEVEM ser em portugues brasileiro sem acentos
    (conforme SRS §8.2). Codigo (classes, metodos, variaveis) DEVE ser em ingles, conforme Constituicao §XV.

16. **Padrao async para load_developers**: O metodo `load_developers()` no ViewModel deve seguir
    o mesmo padrao async dos metodos existentes (`load_features()`). Usar `asyncio.ensure_future()`
    com qasync. Emitir signal `developers_loaded` ao completar. Tratar erros com `error_occurred` signal.
</rules>
