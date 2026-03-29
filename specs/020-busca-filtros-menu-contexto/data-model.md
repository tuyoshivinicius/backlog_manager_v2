# Data Model: EP-020 — Busca, Filtros e Menu de Contexto

**Feature Branch**: `020-busca-filtros-menu-contexto`
**Date**: 2026-03-29

---

## Entidades Existentes (sem alteracao)

### Story (Domain Entity)

| Campo | Tipo | Descricao |
|-------|------|-----------|
| id | str | Formato COMPONENTE-NNN |
| component | str | Max 50 chars |
| name | str | Max 200 chars |
| story_points | StoryPoint | 3, 5, 8, 13 |
| priority | int | >= 0, menor = maior prioridade |
| status | StoryStatus | BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO |
| duration | int \| None | Dias uteis (calculado) |
| start_date | date \| None | Data calculada |
| end_date | date \| None | Data calculada |
| developer_id | int \| None | FK Developer |
| feature_id | int \| None | FK Feature |

### StoryOutputDTO (Application DTO)

Herda todos os campos de Story + campos enriquecidos:

| Campo | Tipo | Descricao |
|-------|------|-----------|
| developer_name | str \| None | Nome do desenvolvedor (enriched) |
| feature_name | str \| None | Nome da feature (enriched) |
| wave | int | Numero da onda (default 0) |
| dependency_ids | list[str] | IDs das dependencias |

### StoryStatus (Value Object)

```python
class StoryStatus(StrEnum):
    BACKLOG = "BACKLOG"
    EXECUCAO = "EXECUCAO"
    TESTES = "TESTES"
    CONCLUIDO = "CONCLUIDO"
    IMPEDIDO = "IMPEDIDO"
```

---

## Novas Entidades (Presentation Layer)

### FilterProxyModel

**Tipo**: QSortFilterProxyModel (Presentation/ViewModel)
**Responsabilidade**: Intermediario entre StoryTableModel e StoryTableView. Aplica filtros de texto, status e feature sem alterar o modelo original.

| Atributo | Tipo | Default | Descricao |
|----------|------|---------|-----------|
| _text_filter | str | "" | Texto de busca (case-insensitive) |
| _status_filter | str \| None | None | Status ativo (None = todos) |
| _feature_filter | int \| None | None | Feature ID ativo (None = todas) |
| _col_id | int | (resolved) | Indice da coluna ID no source model |
| _col_component | int | (resolved) | Indice da coluna Componente |
| _col_name | int | (resolved) | Indice da coluna Nome |
| _col_status | int | (resolved) | Indice da coluna Status |
| _col_feature | int | (resolved) | Indice da coluna Feature |

**Metodos Publicos**:

| Metodo | Assinatura | Descricao |
|--------|-----------|-----------|
| set_text_filter | (text: str) -> None | Define filtro de texto e invalida |
| set_status_filter | (status: str \| None) -> None | Define filtro de status e invalida |
| set_feature_filter | (feature_id: int \| None) -> None | Define filtro de feature e invalida |
| has_active_filters | @property -> bool | True se qualquer filtro esta ativo |

**Metodo Override**:

| Metodo | Descricao |
|--------|-----------|
| filterAcceptsRow(source_row, source_parent) -> bool | AND logico dos 3 filtros. Retorna True se a linha passa em todos. |

**Logica filterAcceptsRow**:

```
1. Se _text_filter nao vazio:
   - Obter valor de colunas ID, Componente, Nome do source model
   - Se nenhum contem _text_filter (case-insensitive) → return False

2. Se _status_filter nao None:
   - Obter valor da coluna Status do source model
   - Se diferente de _status_filter → return False

3. Se _feature_filter nao None:
   - Obter valor da coluna Feature do source model (feature_id via UserRole+100 ou lookup)
   - Se diferente de _feature_filter → return False

4. return True (passa em todos os filtros)
```

**Nota sobre acesso a feature_id**: O StoryTableModel.data() retorna texto para DisplayRole. Para filtrar por feature_id (inteiro), duas opcoes:
- Adicionar role customizado (UserRole+1) no StoryTableModel que retorna feature_id
- Acessar story via StoryTableModel.get_story_at(source_row).feature_id

**Decisao**: Usar `source_model.get_story_at(source_row).feature_id` — mais simples, sem alterar o StoryTableModel.

---

### FilterChip (Widget Composto)

**Tipo**: QPushButton (checkable) dentro de QButtonGroup
**Responsabilidade**: Representar filtro visual de status com contagem.

| Propriedade | Tipo | Descricao |
|-------------|------|-----------|
| objectName | "filterChip" | Para seletor QSS |
| checkable | True | Permite toggle |
| autoExclusive | True | Radio behavior via QButtonGroup |
| text | str | "Label (N)" onde N e a contagem |

**Estado Visual**:

| Estado | QSS Pseudo | Fundo | Texto |
|--------|-----------|-------|-------|
| Normal | (none) | @surface | @text-secondary |
| Hover | :hover:!checked | @neutral-100 | @text-secondary |
| Ativo | :checked | @primary | branco |

---

### SearchField (Widget)

**Tipo**: QLineEdit com configuracao especifica
**Responsabilidade**: Campo de busca incremental com icone e debounce.

| Propriedade | Valor | Descricao |
|-------------|-------|-----------|
| objectName | "searchField" | Para seletor QSS |
| placeholderText | "Buscar por ID, nome ou componente..." | PT-BR |
| fixedWidth | 240 | Largura fixa |
| clearButtonEnabled | True | Botao X para limpar |

---

### ContextMenu (Efemero)

**Tipo**: QMenu criado dinamicamente a cada right-click
**Responsabilidade**: Acoes rapidas sobre historia selecionada.

| Acao | Shortcut Hint | Separador Antes | Propriedade Especial |
|------|---------------|-----------------|---------------------|
| Editar | Enter | Nao | — |
| Duplicar | Ctrl+D | Nao | — |
| — | — | Sim | — |
| Mover Acima | Alt+Up | Nao | disabled se filtros ativos |
| Mover Abaixo | Alt+Down | Nao | disabled se filtros ativos |
| — | — | Sim | — |
| Dependencias... | — | Nao | — |
| — | — | Sim | — |
| Deletar | Delete | Nao | destructive="true", cor @error |

---

## Relacionamentos

```
StoryTableModel (source)
    │
    ▼ setSourceModel()
FilterProxyModel (proxy)
    │
    ▼ setModel()
StoryTableView (view)
    │
    ├── MonospaceDelegate (col 3 - ID)
    └── StatusBadgeDelegate (col 6 - Status)

MainWindowViewModel
    │
    ├── table_model: StoryTableModel (existente)
    ├── stories: list[StoryOutputDTO] (fonte de verdade para contagens)
    ├── duplicate_story() → DuplicateStoryUseCase (NOVO)
    └── signals: stories_changed, error_occurred (existentes)

MainWindow (View)
    │
    ├── FilterProxyModel (criado na view, interposto)
    ├── Zona 3: SearchField + FilterChips + FeatureCombo
    ├── ContextMenu (efemero, criado on-demand)
    └── Toolbar: +Duplicar action (Ctrl+D)
```

---

## Transicoes de Estado dos Filtros

```
                    ┌──────────────┐
                    │  Sem Filtros  │ (estado inicial)
                    │  text=""      │
                    │  status=None  │
                    │  feature=None │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
      ┌──────────┐  ┌──────────┐  ┌──────────┐
      │ Texto    │  │ Status   │  │ Feature  │
      │ Ativo    │  │ Ativo    │  │ Ativa    │
      └────┬─────┘  └────┬─────┘  └────┬─────┘
           │              │              │
           └──────┬───────┘              │
                  ▼                      │
          ┌──────────────┐               │
          │ Texto+Status │               │
          └──────┬───────┘               │
                 └───────────┬───────────┘
                             ▼
                   ┌──────────────────┐
                   │ Texto+Status+    │
                   │ Feature (AND)    │
                   └──────────────────┘

Qualquer combinacao e valida. AND logico sempre.
has_active_filters = True quando qualquer filtro != default
→ Mover Acima/Abaixo desabilitados
```
