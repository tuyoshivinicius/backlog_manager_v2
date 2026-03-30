# Research: Estilizacao de Dialogs

**Feature Branch**: `021-estilizacao-dialogs`
**Date**: 2026-03-29

---

## R-001: EditStoryInputDTO — Campo developer_id Ausente

**Decision**: Adicionar campo `developer_id: int | None = None` ao `EditStoryInputDTO`.

**Rationale**: O `Story` entity ja possui `developer_id: int | None = None` (story.py:39). O `StoryOutputDTO` ja expoe `developer_id` e `developer_name`. Porem o `EditStoryInputDTO` nao inclui `developer_id`, impedindo que o ViewModel persista a selecao de desenvolvedor. O `EditStoryUseCase` precisa ser verificado para confirmar se ja propaga `developer_id` para a entidade — caso contrario, tambem precisa de ajuste.

**Alternatives considered**:
- Criar novo DTO separado para edicao com desenvolvedor → rejeitado: viola DRY e o EditStoryInputDTO ja usa pattern de campos opcionais.
- Passar developer_id por outro canal (ex: use case separado) → rejeitado: fragmenta a operacao atomica de salvamento.

---

## R-002: EditStoryUseCase — Propagacao de developer_id

**Decision**: Adicionar tratamento de `developer_id` no `EditStoryUseCase.execute()`, seguindo o pattern existente dos demais campos opcionais.

**Rationale**: O use case ja segue o pattern `if input_dto.field is not None: story.field = value` para name, story_points, status, duration, etc. O campo `developer_id` precisa ser adicionado com o mesmo pattern. Como `developer_id` pode ser `None` (desatribuicao), sera necessario um sentinel value ou campo booleano para distinguir "nao fornecido" de "limpar atribuicao". O pattern recomendado e usar `UNSET` sentinel.

**Alternatives considered**:
- Usar -1 como sentinel para "limpar" → rejeitado: magic number, fragil.
- Campo booleano `clear_developer: bool = False` → rejeitado: inconsistente com pattern existente.
- Sentinel `UNSET` constant → **escolhido**: padrao Pythonic, extensivel.

---

## R-003: Padrao de objectNames para QSS

**Decision**: Atribuir `setObjectName()` a todos os widgets dos dialogs refatorados, usando convencao kebab-case com prefixo semantico.

**Rationale**: O stylesheet.qss existente ja usa objectNames para estilizacao (ex: `#warnings-badge`, `SearchField`, `FilterChip`). A convencao sera:
- Dialogs: `story-dialog`, `developer-dialog`, `feature-dialog`, `confirm-delete-dialog`, `progress-dialog`, `result-dialog`
- Campos: `story-component-field`, `story-name-field`, `story-developer-combo`
- Labels de erro: `field-error-label`
- Botoes especiais: `confirm-delete-button`
- Estado vazio: `empty-state-label`
- Barra de progresso: `progress-bar`

**Alternatives considered**:
- camelCase objectNames → rejeitado: QSS convencao usa kebab-case com #id selector.
- Classes CSS via property selectors → rejeitado: objectNames sao mais diretos para elementos unicos.

---

## R-004: Validacao on-blur — Pattern de validate_field

**Decision**: Adicionar metodo `validate_field(field_name: str) -> tuple[bool, str]` ao `StoryDialogViewModel` para validacao por campo individual.

**Rationale**: O `validate()` existente retorna erro para o primeiro campo invalido. Para validacao on-blur, cada campo precisa ser validado individualmente. O metodo retorna `(is_valid, error_message)` — a View conecta o evento `focusOut` do campo e chama `validate_field("component")`, recebendo o resultado para aplicar estilo visual. O `validate()` global continua funcionando para compatibilidade.

**Alternatives considered**:
- Validacao na View (sem ViewModel) → rejeitado: viola MVVM (logica no ViewModel).
- Signal por campo (`component_invalid`, `name_invalid`) → rejeitado: muitos signals, complexidade desnecessaria.
- Metodo unico validate_field com dispatch por nome → **escolhido**: simples, extensivel, testavel.

---

## R-005: QStackedWidget para Estados Vazios

**Decision**: Usar `QStackedWidget` com indice 0 = lista e indice 1 = label de estado vazio nos dialogs de desenvolvedores e features.

**Rationale**: Conforme ADR-005 da spec. `QStackedWidget` e o mecanismo idiomatico do Qt para alternar entre widgets mutuamente exclusivos. A verificacao `_update_empty_state()` sera chamada apos: carregamento inicial, adicao de item, remocao de item. Quando `list.count() == 0`, mostra indice 1 (label); caso contrario, indice 0 (lista).

**Alternatives considered**:
- show()/hide() em widgets separados → rejeitado: requer gerenciamento manual de layout.
- Overlay com z-index → rejeitado: hack visual, problemas de posicionamento.

---

## R-006: ConfirmDeleteDialog — Factory Methods por Entidade

**Decision**: Adicionar metodos de classe `for_story()`, `for_developer()`, `for_feature()` ao `ConfirmDeleteDialog`, mantendo compatibilidade retroativa.

**Rationale**: Conforme ADR-006 da spec. O construtor atual aceita `story_id` e `story_name`. Refatorar para construtor interno generico que aceita `main_text` e `detail_text`, com factory methods que formatam o texto por entidade:
- `for_story(story_id, story_name)` → "Excluir {id} — {nome}?"
- `for_developer(name)` → "Excluir {nome}?"
- `for_feature(name, wave)` → "Excluir Onda {N} — {nome}?"

Chamadas existentes serao atualizadas para usar `for_story()`.

**Alternatives considered**:
- Construtor com tipo de entidade enum → rejeitado: acoplamento desnecessario.
- Subclasses por entidade → rejeitado: over-engineering para dialogs simples.

---

## R-007: Dialogs de Progresso e Resultado — Novos Componentes

**Decision**: Criar `ProgressDialog` e `ResultDialog` como QDialog independentes em presentation/views/.

**Rationale**: Conforme ADR-007 e ADR-008 da spec. `ProgressDialog` encapsula `QProgressBar` + label de mensagem, suporta modo determinado (0-100%) e indeterminado (animacao). `ResultDialog` encapsula labels formatados para contagens de import ou caminho de export, com botao Fechar. Ambos terao objectNames para estilizacao via QSS.

**Alternatives considered**:
- Reusar QProgressDialog nativo → rejeitado: customizacao visual limitada, nao suporta QSS com objectNames.
- Inline na MainWindow → rejeitado: nao reutilizavel, polui a MainWindow.

---

## R-008: Icones nos Botoes do DeveloperDialog

**Decision**: Usar `IconManager.get()` existente para atribuir icones aos botoes do DeveloperDialog.

**Rationale**: O `IconManager` ja carrega todos os 16 SVGs na inicializacao. Os icones necessarios ja existem: `plus.svg` (Adicionar), `pencil-simple.svg` (Editar), `trash.svg` (Remover), `x.svg` (Fechar). Basta chamar `button.setIcon(icon_manager.get("plus"))` e `button.setIconSize(QSize(16, 16))`.

**Alternatives considered**:
- Icones inline via QPixmap → rejeitado: duplica carregamento, inconsistente com sistema existente.
- Texto unicode como icone → rejeitado: inconsistente entre plataformas.

---

## R-009: Contagem de Caracteres no StoryDialog

**Decision**: Adicionar `QLabel` abaixo de cada campo de texto com formato "N/MAX", atualizado via signal `textChanged`.

**Rationale**: A contagem de caracteres e um label simples que reflete `len(field.text())` / limite maximo. A cor muda para alerta quando >= 90% do limite. A View conecta `textChanged` do campo ao metodo que atualiza o label. Nenhuma logica de negocio no ViewModel para contagem — e puramente visual.

**Alternatives considered**:
- Contagem no ViewModel → rejeitado: e feedback visual puro, nao logica de negocio.
- Placeholder text com contagem → rejeitado: desaparece quando campo tem conteudo.

---

## R-010: Sentinel UNSET para developer_id no EditStoryInputDTO

**Decision**: Usar `_UNSET` sentinel para distinguir "campo nao fornecido" de "campo explicitamente None" no EditStoryInputDTO.developer_id.

**Rationale**: O campo `developer_id` precisa suportar 3 estados: (1) nao fornecido (manter valor atual), (2) None (desatribuir desenvolvedor), (3) inteiro (atribuir desenvolvedor). O pattern `int | None = None` existente nao distingue (1) de (2). A solucao e usar um sentinel `_UNSET` como default, e no use case checar `if input_dto.developer_id is not _UNSET`. Pydantic suporta isso via `Field(default=_UNSET)`.

**Alternatives considered**:
- Wrapper Optional[Optional[int]] → rejeitado: Pydantic nao suporta nativamente.
- Campo booleano `update_developer: bool = False` → rejeitado: padrao inconsistente com demais campos.
- Sempre enviar developer_id (mesmo que nao mudou) → **alternativa viavel**: a View sempre envia o valor atual do combo. Se o usuario nao mudou, envia o valor pre-selecionado. Isso elimina a necessidade de sentinel. **DECISAO REVISADA**: usar esta abordagem mais simples — a View sempre envia developer_id no DTO, eliminando ambiguidade.

**Decision Final**: A View sempre popula `developer_id` no `EditStoryInputDTO` com o valor atual do combo (pode ser `None` para "Nenhum" ou `int` para um dev selecionado). O use case trata `None` como desatribuicao e `int` como atribuicao. O campo no DTO sera `developer_id: int | None = None`, e o use case SEMPRE aplica o valor (diferente dos demais campos que sao condicionais). Isso e mais simples e elimina a necessidade de sentinel.
