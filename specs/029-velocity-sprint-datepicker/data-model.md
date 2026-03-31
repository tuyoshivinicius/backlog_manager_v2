# Data Model: Velocidade em SP/Sprint e DatePicker Reutilizavel

**Feature Branch**: `029-velocity-sprint-datepicker`
**Date**: 2026-03-31

## Entidades Impactadas

### 1. ConfigDialogViewModel (Presentation — MODIFICADO)

**Camada**: Presentation (viewmodels)
**Arquivo**: `src/backlog_manager/presentation/viewmodels/config_dialog_viewmodel.py`

#### Campos Removidos

| Campo | Tipo | Descricao |
|-------|------|-----------|
| `_velocity` | `float` | Velocidade em SP/dia (substituido por sp_per_sprint + workdays) |

#### Novos Campos

| Campo | Tipo | Default | Range | Descricao |
|-------|------|---------|-------|-----------|
| `_sp_per_sprint` | `int` | 20 | 1-100 | Story points por sprint |
| `_workdays_per_sprint` | `int` | 10 | 1-30 | Dias uteis por sprint |

#### Propriedades Derivadas

| Propriedade | Tipo | Formula | Descricao |
|-------------|------|---------|-----------|
| `velocity_per_day` | `float` | `sp_per_sprint / workdays_per_sprint` | Velocidade derivada em SP/dia (read-only) |

#### Validacoes

| Regra | Condicao | Mensagem |
|-------|----------|----------|
| SP/Sprint positivo | `sp_per_sprint >= 1` | "SP/Sprint deve ser no minimo 1." |
| SP/Sprint maximo | `sp_per_sprint <= 100` | "SP/Sprint deve ser no maximo 100." |
| Dias uteis positivo | `workdays_per_sprint >= 1` | "Dias uteis por sprint deve ser no minimo 1." |
| Dias uteis maximo | `workdays_per_sprint <= 30` | "Dias uteis por sprint deve ser no maximo 30." |

#### QSettings Persistencia

| Chave QSettings | Tipo | Grupo | Descricao |
|-----------------|------|-------|-----------|
| `allocation/sp_per_sprint` | `int` | allocation | Story points por sprint |
| `allocation/workdays_per_sprint` | `int` | allocation | Dias uteis por sprint |
| `allocation/start_date` | `str` (ISO) | allocation | Data de inicio (inalterado) |
| `allocation/max_idle_days` | `int` | allocation | Max dias ociosos (inalterado) |
| `allocation/velocity` | `float` | allocation | LEGADO — nao escrito, apenas lido para migracao |

#### Transicao de Estado (Migracao)

```
QSettings vazio (1a execucao)
  → sp_per_sprint=20, workdays_per_sprint=10

QSettings com "velocity" (versao anterior) sem "sp_per_sprint"
  → sp_per_sprint=20, workdays_per_sprint=10 (defaults seguros)

QSettings com "sp_per_sprint" e "workdays_per_sprint" (versao atual)
  → Carrega valores persistidos
```

---

### 2. DatePicker (Presentation — NOVO)

**Camada**: Presentation (views)
**Arquivo**: `src/backlog_manager/presentation/views/date_picker.py`

#### Propriedades de Configuracao

| Propriedade | Tipo | Default | Descricao |
|-------------|------|---------|-----------|
| `display_format` | `str` | `"dd/MM/yyyy"` | Formato de exibicao da data |
| `calendar_popup` | `bool` | `True` | Habilita popup de calendario |
| `min_date` | `date \| None` | `None` | Data minima permitida |
| `max_date` | `date \| None` | `None` | Data maxima permitida |

#### Signals

| Signal | Tipo | Descricao |
|--------|------|-----------|
| `date_changed` | `Signal(object)` | Emite `datetime.date` quando a data muda |

#### Estilizacao

Utiliza DESIGN_TOKENS para:
- `font-family`, `font-size-base` para tipografia
- `border` para borda do campo
- `primary` para foco e destaque do calendario
- `radius-md` para border radius

---

### 3. AllocationConfig (Domain — INALTERADO)

**Camada**: Domain (services)
**Arquivo**: `src/backlog_manager/domain/services/allocation_service.py`

Nenhuma alteracao. Continua recebendo `velocity: float` (SP/dia).

---

### 4. ExecuteAllocationInputDTO (Application — INALTERADO)

**Camada**: Application (dto)
**Arquivo**: `src/backlog_manager/application/dto/allocation/execute_allocation_dto.py`

Nenhuma alteracao. Continua recebendo `velocity: float` (SP/dia).

---

### 5. SchedulingService (Domain — INALTERADO)

**Camada**: Domain (services)
**Arquivo**: `src/backlog_manager/domain/services/scheduling_service.py`

Nenhuma alteracao. Continua usando `velocity` como SP/dia em `calculate_duration()`.

---

## Diagrama de Fluxo de Dados

```
┌──────────────────────────────────────────────────────────┐
│  Presentation Layer                                       │
│                                                           │
│  ConfigDialog / ConfigPanel                               │
│  ┌─────────────────────┐  ┌─────────────────────────┐   │
│  │ QSpinBox             │  │ QSpinBox                 │   │
│  │ SP/Sprint: [20]      │  │ Dias Uteis: [10]         │   │
│  └─────────┬───────────┘  └──────────┬──────────────┘   │
│            │ valueChanged             │ valueChanged      │
│            └──────────┬───────────────┘                   │
│                       ▼                                   │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ QLabel (read-only): "= 2.0 SP/dia"                  │ │
│  └─────────────────────────────────────────────────────┘ │
│                       │                                   │
│                       ▼ _on_apply()                       │
│  ┌─────────────────────────────────────────────────────┐ │
│  │ ConfigDialogViewModel                                │ │
│  │   sp_per_sprint = 20                                 │ │
│  │   workdays_per_sprint = 10                           │ │
│  │   velocity_per_day = 20 / 10 = 2.0  (derivado)      │ │
│  │                                                       │ │
│  │   QSettings: persiste sp_per_sprint, workdays        │ │
│  └─────────────────────┬───────────────────────────────┘ │
│                         │ velocity_per_day (float)        │
└─────────────────────────┼────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Application Layer                                       │
│  ExecuteAllocationInputDTO(velocity=2.0, ...)            │
└─────────────────────────┬───────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│  Domain Layer                                            │
│  AllocationConfig(velocity=2.0, ...)                     │
│  SchedulingService.calculate_duration(sp, velocity=2.0)  │
└─────────────────────────────────────────────────────────┘
```

## Relacionamentos

```
DatePicker ──usado-por──► ConfigDialog
DatePicker ──usado-por──► ConfigPanel
DatePicker ──usado-por──► ManualAllocationDialog
DatePicker ──importa───► DESIGN_TOKENS (theme.py)

ConfigDialogViewModel ──persiste-em──► QSettings
ConfigDialogViewModel ──produz──────► velocity_per_day (float)

ConfigDialog ──consome──► ConfigDialogViewModel
ConfigPanel  ──produz───► velocity (float, derivada de sp/sprint ÷ workdays)
```
