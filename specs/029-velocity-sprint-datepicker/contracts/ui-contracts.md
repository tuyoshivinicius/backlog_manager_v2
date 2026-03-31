# UI Contracts: Velocidade em SP/Sprint e DatePicker Reutilizavel

**Feature Branch**: `029-velocity-sprint-datepicker`
**Date**: 2026-03-31

## Contract 1: DatePicker Component

### Interface Publica

```python
class DatePicker(QDateEdit):
    """Componente DatePicker reutilizavel com estilizacao Design System.

    Herda QDateEdit com configuracao padrao e estilizacao consistente.

    Signals:
        date_changed: Emitido quando a data selecionada muda (emite datetime.date).
    """

    date_changed = Signal(object)  # emits datetime.date

    def __init__(
        self,
        parent: QWidget | None = None,
        *,
        display_format: str = "dd/MM/yyyy",
        min_date: date | None = None,
        max_date: date | None = None,
    ) -> None: ...

    def get_date(self) -> date:
        """Retorna a data selecionada como datetime.date."""
        ...

    def set_date(self, value: date) -> None:
        """Define a data selecionada a partir de datetime.date."""
        ...
```

### Comportamento

| Acao | Resultado Esperado |
|------|-------------------|
| Clicar no campo | Abre calendar popup |
| Selecionar data no calendario | Atualiza campo, emite `date_changed` com `datetime.date` |
| Digitar data no campo | Aceita formato `dd/MM/yyyy`, emite `date_changed` |
| Data < min_date | Nao aceita, mantem valor anterior |
| Data > max_date | Nao aceita, mantem valor anterior |
| min_date > max_date (configuracao invalida) | Usa min_date como unico limite; max_date ignorado |

### Estilizacao

```
Fonte: DESIGN_TOKENS["font-family"], DESIGN_TOKENS["font-size-base"]
Borda: 1px solid DESIGN_TOKENS["border"]
Border radius: DESIGN_TOKENS["radius-md"]
Foco: DESIGN_TOKENS["focus-ring"]
Calendario popup: fundo DESIGN_TOKENS["background"], selecao DESIGN_TOKENS["primary"]
```

---

## Contract 2: ConfigDialog — Velocidade SP/Sprint

### Layout dos Campos de Velocidade

```
┌────────────────────────────────────────────────────┐
│ Configuracao de Alocacao                            │
│                                                     │
│  Velocidade (SP/Sprint): [  20  ▲▼]                │
│  Dias Uteis por Sprint:  [  10  ▲▼]                │
│                          = 2.0 SP/dia               │
│                                                     │
│  Data Inicio:  [ 31/03/2026 📅 ]    ← DatePicker   │
│  Max Dias Ociosos:  [  3  ▲▼] dias                 │
│                                                     │
│  [  Cancelar  ]  [  Aplicar  ]                     │
└────────────────────────────────────────────────────┘
```

### Campos de Velocidade

| Campo | Widget | Tipo | Range | Default | Sufixo |
|-------|--------|------|-------|---------|--------|
| Velocidade (SP/Sprint) | QSpinBox | int | 1-100 | 20 | " SP/Sprint" |
| Dias Uteis por Sprint | QSpinBox | int | 1-30 | 10 | " dias" |
| Velocidade derivada | QLabel | — | — | "= 2.0 SP/dia" | — |

### Comportamento Dinamico

| Evento | Resultado |
|--------|-----------|
| `sp_per_sprint.valueChanged` | Recalcula e atualiza label derivada |
| `workdays_per_sprint.valueChanged` | Recalcula e atualiza label derivada |
| Clique "Aplicar" | Transfere sp_per_sprint e workdays ao ViewModel, calcula velocity_per_day, persiste via QSettings, fecha dialog |
| Clique "Cancelar" | Fecha dialog sem salvar |

### Formula da Label Derivada

```
velocity_per_day = sp_per_sprint / workdays_per_sprint
Label text: f"= {velocity_per_day:.1f} SP/dia"
```

---

## Contract 3: ConfigPanel — Velocidade SP/Sprint

### Layout

Identico ao ConfigDialog (mesmos campos, mesmos ranges), porem:
- Dentro de QGroupBox "Configuracao de Alocacao"
- Sem botoes Aplicar/Cancelar (valores lidos via propriedades)
- In-memory only (sem persistencia QSettings)

### Propriedades Publicas

```python
@property
def velocity(self) -> float:
    """Retorna velocity_per_day derivada (SP/dia). Compatibilidade retroativa."""
    return self._sp_per_sprint_spin.value() / self._workdays_per_sprint_spin.value()

@property
def sp_per_sprint(self) -> int: ...

@sp_per_sprint.setter
def sp_per_sprint(self, value: int) -> None: ...

@property
def workdays_per_sprint(self) -> int: ...

@workdays_per_sprint.setter
def workdays_per_sprint(self, value: int) -> None: ...
```

---

## Contract 4: QSettings Schema (grupo "allocation")

### Versao Atual (apos esta feature)

| Chave | Tipo | Range | Default | Descricao |
|-------|------|-------|---------|-----------|
| `sp_per_sprint` | int | 1-100 | 20 | Story points por sprint |
| `workdays_per_sprint` | int | 1-30 | 10 | Dias uteis por sprint |
| `start_date` | str (ISO 8601) | — | date.today() | Data de inicio do projeto |
| `max_idle_days` | int | 2-30 | 3 | Max dias ociosos |

### Versao Legada (anterior a esta feature)

| Chave | Tipo | Descricao |
|-------|------|-----------|
| `velocity` | float | Velocidade em SP/dia — nao mais escrito, apenas lido para deteccao de migracao |

### Comportamento de Migracao

```python
# Pseudocodigo
if settings.contains("sp_per_sprint"):
    # Versao atual: carrega normalmente
    load sp_per_sprint, workdays_per_sprint
else:
    # Versao legada ou 1a execucao: usa defaults
    sp_per_sprint = 20
    workdays_per_sprint = 10
    # Campo "velocity" antigo e ignorado
```
