# UI Contract: Modulo de Planejamentos

**Feature**: 045-planning-crud | **Date**: 2026-04-08

## Menu Structure

### Menu "Arquivo" (modificado)

```
Arquivo
├── Novo Planejamento        Ctrl+N      # NOVO — cria planejamento
├── Abrir Planejamento       Ctrl+O      # NOVO — lista/abre planejamentos
├── ─────────────────────
├── Importar Excel           Ctrl+I      # Existente
├── Exportar Excel           Ctrl+E      # Existente
├── ─────────────────────
└── Sair                     Ctrl+Q      # Existente
```

### Menu "Ferramentas" (modificado)

```
Ferramentas
├── Reiniciar Planejamento   Ctrl+Shift+R  # RENOMEADO (era "Novo Planejamento" com Ctrl+Shift+N)
├── Alocar Automaticamente   Ctrl+Shift+A  # Existente
├── ...                                     # Demais itens inalterados
```

## Dialogo "Novo Planejamento" (CreatePlanningDialog)

- **Tipo**: QDialog modal
- **Trigger**: Menu `Arquivo > Novo Planejamento` ou bootstrap (banco vazio)
- **Layout**:
  ```
  ┌─────────────────────────────────────┐
  │  Novo Planejamento                  │
  ├─────────────────────────────────────┤
  │  Nome: [________________________]   │
  │                                     │
  │           [Cancelar]  [Criar]       │
  └─────────────────────────────────────┘
  ```
- **Validacoes**:
  - Nome obrigatorio (botao "Criar" desabilitado se vazio)
  - Nome unico (erro exibido abaixo do campo se duplicado)
  - Max 200 caracteres
- **Retorno**: `str | None` — nome do planejamento criado, ou None se cancelado
- **Nota**: No bootstrap (primeiro uso), botao "Cancelar" eh ocultado — usuario deve criar um planejamento

## Dialogo "Abrir Planejamento" (OpenPlanningDialog)

- **Tipo**: QDialog modal
- **Trigger**: Menu `Arquivo > Abrir Planejamento`
- **Layout**:
  ```
  ┌──────────────────────────────────────────────────────────────┐
  │  Abrir Planejamento                                         │
  ├──────────────────────────────────────────────────────────────┤
  │  ┌──────────────┬───────────┬──────────────┬──────────┐     │
  │  │ Nome         │ Historias │ Modificado   │ Acoes    │     │
  │  ├──────────────┼───────────┼──────────────┼──────────┤     │
  │  │ Sprint 45 ●  │    25     │ 08/04/2026   │ ✏️  🗑️  │     │
  │  │ Sprint 44    │    18     │ 01/04/2026   │ ✏️  🗑️  │     │
  │  │ Sprint 43    │    30     │ 25/03/2026   │ ✏️  🗑️  │     │
  │  └──────────────┴───────────┴──────────────┴──────────┘     │
  │                                                              │
  │  ● = planejamento ativo (sem botao excluir)                  │
  │                                                              │
  │                        [Cancelar]  [Abrir]                   │
  └──────────────────────────────────────────────────────────────┘
  ```
- **Comportamentos**:
  - Selecao unica por clique na linha
  - Duplo-clique abre o planejamento (equivale a selecionar + "Abrir")
  - Botao "Abrir" habilitado somente com selecao
  - Coluna "Acoes": botoes icon-only (editar, excluir) via `setCellWidget`
  - Planejamento ativo indicado com bullet (●) no nome e sem botao excluir
  - Lista vazia: exibe mensagem "Nenhum planejamento encontrado"
- **Retorno**: `int | None` — ID do planejamento selecionado, ou None se cancelado

## Titulo da Janela Principal

```
Formato: "Backlog Manager — {nome_do_planejamento}"
Exemplo: "Backlog Manager — Sprint 45"
Sem planejamento: "Backlog Manager"
```

## Toolbar

- **Nenhuma alteracao na toolbar** — os novos menus ficam exclusivamente no menu bar "Arquivo"

## Sinais e Slots (ViewModel → View)

### PlanningViewModel

```python
class PlanningViewModel(QObject):
    planning_created = Signal(int, str)      # (planning_id, name)
    planning_activated = Signal(int, str)     # (planning_id, name)
    planning_renamed = Signal(int, str)       # (planning_id, new_name)
    planning_deleted = Signal(int)            # (planning_id)
    error_occurred = Signal(str)              # (error_message)
```

### MainWindowViewModel (sinais adicionados)

```python
# Sinais existentes mantidos
active_planning_changed = Signal(int, str)   # NOVO — (planning_id, name)
```
