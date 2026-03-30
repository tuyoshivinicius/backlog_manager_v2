# Contracts: ViewModel Signals — Estilizacao de Dialogs

**Feature Branch**: `021-estilizacao-dialogs`
**Date**: 2026-03-29

---

## StoryDialogViewModel — Novos Signals

### developers_loaded

**Emitter**: `StoryDialogViewModel`
**Payload**: `list` (list[DeveloperOutputDTO])
**When**: Apos `load_developers()` completar com sucesso.
**Consumer**: `StoryDialog` — popula o combo de desenvolvedores.

```python
# ViewModel
developers_loaded = Signal(list)

async def load_developers(self) -> None:
    async with self._container.create_unit_of_work() as uow:
        use_case = self._container.create_list_developers_use_case(uow)
        result = await use_case.execute()
        self._developers = list(result.developers)
        self.developers_loaded.emit(self._developers)

# View
self._viewmodel.developers_loaded.connect(self._on_developers_loaded)

def _on_developers_loaded(self, developers: list[DeveloperOutputDTO]) -> None:
    self._developer_combo.clear()
    self._developer_combo.addItem("Nenhum", None)
    for dev in developers:
        self._developer_combo.addItem(dev.name, dev.id)
    # Pre-select current developer
    if self._viewmodel.developer_id is not None:
        index = self._developer_combo.findData(self._viewmodel.developer_id)
        if index >= 0:
            self._developer_combo.setCurrentIndex(index)
```

---

## StoryDialogViewModel — validate_field Contract

### Input/Output

```python
def validate_field(self, field_name: str) -> tuple[bool, str]:
    """Valida um campo individual.

    Args:
        field_name: Nome do campo ("component" ou "name").

    Returns:
        Tupla (is_valid, error_message). Para campos desconhecidos,
        retorna (True, "").
    """
```

### Dispatch Table

| field_name | Condicao Invalida | Retorno |
|------------|-------------------|---------|
| "component" | `self._component == ""` | `(False, "Campo obrigatorio")` |
| "component" | `len(self._component) > 50` | `(False, "Maximo de 50 caracteres")` |
| "name" | `self._name == ""` | `(False, "Campo obrigatorio")` |
| "name" | `len(self._name) > 200` | `(False, "Maximo de 200 caracteres")` |
| (qualquer outro) | — | `(True, "")` |

---

## ConfirmDeleteDialog — Factory Methods Contract

### for_story

```python
@classmethod
def for_story(
    cls,
    story_id: str,
    story_name: str,
    parent: QWidget | None = None,
) -> ConfirmDeleteDialog:
    """Cria dialog de confirmacao para exclusao de historia."""
    return cls(
        main_text=f"Excluir {story_id} — {story_name}?",
        detail_text="Esta acao nao pode ser desfeita.",
        parent=parent,
    )
```

### for_developer

```python
@classmethod
def for_developer(
    cls,
    name: str,
    parent: QWidget | None = None,
) -> ConfirmDeleteDialog:
    """Cria dialog de confirmacao para exclusao de desenvolvedor."""
    return cls(
        main_text=f"Excluir {name}?",
        detail_text="Esta acao nao pode ser desfeita.",
        parent=parent,
    )
```

### for_feature

```python
@classmethod
def for_feature(
    cls,
    name: str,
    wave: int,
    parent: QWidget | None = None,
) -> ConfirmDeleteDialog:
    """Cria dialog de confirmacao para exclusao de feature."""
    return cls(
        main_text=f"Excluir Onda {wave} — {name}?",
        detail_text="Esta acao nao pode ser desfeita.",
        parent=parent,
    )
```

---

## ProgressDialog — Public API Contract

```python
class ProgressDialog(QDialog):
    def __init__(
        self,
        message: str,
        parent: QWidget | None = None,
        indeterminate: bool = True,
    ) -> None: ...

    def update_progress(self, value: int, message: str | None = None) -> None:
        """Atualiza barra (0-100) e mensagem opcional. Alterna para modo determinado."""

    def set_indeterminate(self, indeterminate: bool) -> None:
        """Alterna entre modo determinado e indeterminado."""
```

---

## ResultDialog — Public API Contract

```python
class ResultDialog(QDialog):
    @classmethod
    def for_import(
        cls,
        stories_count: int,
        features_count: int,
        warnings_count: int,
        parent: QWidget | None = None,
    ) -> ResultDialog:
        """Cria dialog de resultado para importacao."""

    @classmethod
    def for_export(
        cls,
        file_path: str,
        parent: QWidget | None = None,
    ) -> ResultDialog:
        """Cria dialog de resultado para exportacao."""
```
