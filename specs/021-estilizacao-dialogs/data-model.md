# Data Model: Estilizacao de Dialogs

**Feature Branch**: `021-estilizacao-dialogs`
**Date**: 2026-03-29

---

## Entities Impactadas

### 1. EditStoryInputDTO (Modificacao)

**Arquivo**: `src/backlog_manager/application/dto/story/edit_story_dto.py`

| Campo | Tipo | Default | Validacao | Status |
|-------|------|---------|-----------|--------|
| story_id | str | — | Obrigatorio | Existente |
| name | str \| None | None | max 200, nao vazio | Existente |
| story_points | int \| None | None | {3, 5, 8, 13} | Existente |
| status | str \| None | None | enum BACKLOG/IN_PROGRESS/DONE/BLOCKED | Existente |
| duration | int \| None | None | >= 0 | Existente |
| start_date | date \| None | None | — | Existente |
| end_date | date \| None | None | — | Existente |
| feature_id | int \| None | None | — | Existente |
| **developer_id** | **int \| None** | **None** | **— (validacao no use case)** | **NOVO** |

**Nota**: Diferente dos demais campos opcionais, `developer_id` sera SEMPRE enviado pela View em modo edicao (valor do combo). O use case SEMPRE aplica o valor (ver R-010 em research.md).

### 2. StoryDialogViewModel (Modificacao)

**Arquivo**: `src/backlog_manager/presentation/viewmodels/story_dialog_viewmodel.py`

#### Novos Campos de Estado

| Campo | Tipo | Default | Descricao |
|-------|------|---------|-----------|
| _developer_id | int \| None | None | ID do desenvolvedor selecionado |
| _developers | list[DeveloperOutputDTO] | [] | Lista de desenvolvedores para dropdown |

#### Novos Signals

| Signal | Payload | Descricao |
|--------|---------|-----------|
| developers_loaded | list | Emitido apos carga de desenvolvedores |

#### Novos Metodos

| Metodo | Assinatura | Descricao |
|--------|-----------|-----------|
| developer_id (property) | `-> int \| None` | Getter/setter para developer_id |
| developers (property) | `-> list[DeveloperOutputDTO]` | Getter para lista de devs |
| load_developers | `async def load_developers() -> None` | Carrega devs via ListDevelopersUseCase |
| validate_field | `def validate_field(field_name: str) -> tuple[bool, str]` | Validacao por campo individual |

#### validate_field — Regras

| field_name | Regra Invalido | Mensagem |
|------------|---------------|----------|
| "component" | vazio | "Campo obrigatorio" |
| "component" | len > 50 | "Maximo de 50 caracteres" |
| "name" | vazio | "Campo obrigatorio" |
| "name" | len > 200 | "Maximo de 200 caracteres" |
| (outro) | — | Sempre valido (True, "") |

### 3. ProgressDialog (Novo)

**Arquivo**: `src/backlog_manager/presentation/views/progress_dialog.py`

| Atributo | Tipo | Descricao |
|----------|------|-----------|
| _progress_bar | QProgressBar | Barra de progresso estilizada |
| _message_label | QLabel | Mensagem textual atualizavel |
| _is_indeterminate | bool | Modo indeterminado (sem %) |

| Metodo | Assinatura | Descricao |
|--------|-----------|-----------|
| __init__ | `(message: str, parent: QWidget \| None = None, indeterminate: bool = True)` | Construtor |
| update_progress | `(value: int, message: str \| None = None) -> None` | Atualiza barra e mensagem |
| set_indeterminate | `(indeterminate: bool) -> None` | Alterna modo |

**Constraints**: Modal, nao fechavel pelo usuario (`setWindowFlag(Qt.WindowCloseButtonHint, False)`).

### 4. ResultDialog (Novo)

**Arquivo**: `src/backlog_manager/presentation/views/result_dialog.py`

| Atributo | Tipo | Descricao |
|----------|------|-----------|
| _title_label | QLabel | Titulo do resultado |
| _details_label | QLabel | Detalhes formatados |
| _close_button | QPushButton | Botao Fechar |

| Factory Method | Assinatura | Descricao |
|----------------|-----------|-----------|
| for_import | `(stories: int, features: int, warnings: int, parent) -> ResultDialog` | Resultado de importacao |
| for_export | `(file_path: str, parent) -> ResultDialog` | Resultado de exportacao |

### 5. ConfirmDeleteDialog (Modificacao)

**Arquivo**: `src/backlog_manager/presentation/views/confirm_delete_dialog.py`

#### Novos Elementos Visuais

| Elemento | Tipo | Descricao |
|----------|------|-----------|
| _alert_icon | QLabel (com QPixmap) | Icone de alerta 32x32px |
| _main_text | QLabel | Texto principal formatado por entidade |
| _detail_text | QLabel | "Esta acao nao pode ser desfeita." |
| _confirm_button | QPushButton | "Confirmar Exclusao" com objectName para QSS vermelho |

#### Novos Factory Methods

| Metodo | Assinatura | Texto Gerado |
|--------|-----------|--------------|
| for_story | `(story_id: str, story_name: str, parent) -> ConfirmDeleteDialog` | "Excluir {id} — {nome}?" |
| for_developer | `(name: str, parent) -> ConfirmDeleteDialog` | "Excluir {nome}?" |
| for_feature | `(name: str, wave: int, parent) -> ConfirmDeleteDialog` | "Excluir Onda {N} — {nome}?" |

### 6. DeveloperDialog (Modificacao)

**Arquivo**: `src/backlog_manager/presentation/views/developer_dialog.py`

#### Novos Elementos

| Elemento | Descricao |
|----------|-----------|
| QStackedWidget | Container alternando entre lista (idx 0) e estado vazio (idx 1) |
| QLabel (empty state) | "Nenhum desenvolvedor cadastrado. Clique em Adicionar para comecar." |
| Icones nos botoes | plus (Adicionar), pencil-simple (Editar), trash (Remover), x (Fechar) |

#### Novos objectNames

| Widget | objectName |
|--------|-----------|
| Dialog | `developer-dialog` |
| Lista | `developer-list` |
| Empty state label | `developer-empty-state` |
| Botao Adicionar | `developer-add-button` |
| Botao Editar | `developer-edit-button` |
| Botao Remover | `developer-remove-button` |
| Botao Fechar | `developer-close-button` |

### 7. FeatureDialog (Modificacao)

**Arquivo**: `src/backlog_manager/presentation/views/feature_dialog.py`

#### Novos Elementos

| Elemento | Descricao |
|----------|-----------|
| QStackedWidget | Container alternando entre lista (idx 0) e estado vazio (idx 1) |
| QLabel (empty state) | "Nenhuma feature cadastrada. Clique em Adicionar para comecar." |

#### Formato de Exibicao

Itens da lista formatados como: `"Onda {wave} — {name}"` (ex: "Onda 2 — Login").

### 8. StoryDialog (Modificacao)

**Arquivo**: `src/backlog_manager/presentation/views/story_dialog.py`

#### Novos Elementos

| Elemento | Tipo | Descricao |
|----------|------|-----------|
| Developer combo | QComboBox | Dropdown "Nenhum" + devs, visivel apenas em modo edicao |
| Developer label | QLabel | Label "Desenvolvedor" |
| Developer container | QWidget | Container para label + combo (visibilidade conjunta) |
| Required indicators | QLabel | Asterisco (*) vermelho ao lado de labels obrigatorios |
| Error labels | QLabel | Mensagem de erro inline por campo |
| Char count labels | QLabel | "N/MAX" abaixo de campos de texto |

#### objectNames Chave

| Widget | objectName |
|--------|-----------|
| Dialog | `story-dialog` |
| Campo Componente | `story-component-field` |
| Campo Nome | `story-name-field` |
| Combo Desenvolvedor | `story-developer-combo` |
| Container Desenvolvedor | `story-developer-container` |
| Error label (generico) | `field-error-label` |
| Char count label | `field-char-count` |
| Botao Salvar | `story-save-button` |

---

## QSS Additions (stylesheet.qss)

### Novas Regras

```text
/* Dialog objectNames */
#story-dialog, #developer-dialog, #feature-dialog,
#confirm-delete-dialog, #progress-dialog, #result-dialog

/* Campos de erro */
QLineEdit[error="true"], QTextEdit[error="true"]  — borda vermelha
#field-error-label  — fundo vermelho claro, texto vermelho, padding

/* Indicador obrigatorio */
#required-indicator  — cor vermelha, fonte bold

/* Estado vazio */
#developer-empty-state, #feature-empty-state  — cor neutra, centralizado

/* Botao confirmacao exclusao */
#confirm-delete-button  — fundo vermelho, texto branco

/* Barra de progresso */
#progress-bar  — cor primaria

/* Contagem de caracteres */
#field-char-count  — cor secundaria, fonte reduzida
#field-char-count[warning="true"]  — cor de alerta
```

---

## State Transitions

### StoryDialog — Validacao on-blur

```text
[Campo com foco] → focusOut → validate_field(field_name)
  ├── (True, "") → remove borda vermelha, oculta error label
  └── (False, msg) → aplica borda vermelha, exibe error label com msg
       └── re-avalia formulario → habilita/desabilita botao Salvar
```

### DeveloperDialog / FeatureDialog — Estado Vazio

```text
[Carregamento/Adicao/Remocao] → _update_empty_state()
  ├── list.count() == 0 → stacked.setCurrentIndex(1) [label]
  └── list.count() > 0  → stacked.setCurrentIndex(0) [lista]
```

### ProgressDialog — Modos

```text
[Inicio] → ProgressDialog(indeterminate=True)
  ├── update_progress(value, msg) → modo determinado, barra atualiza
  └── set_indeterminate(True) → barra em animacao continua
[Fim] → dialog.accept() [fecha automaticamente]
```
