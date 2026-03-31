# UI Contract: ManualAllocationDialog

**Type**: Modal QDialog | **Trigger**: Double-click na celula Desenvolvedor (coluna 7)

## Assinatura

```python
class ManualAllocationDialog(QDialog):
    """Dialog para alocacao manual de desenvolvedor a uma historia."""

    def __init__(
        self,
        container: DIContainer,
        story_id: str,
        story_name: str,
        current_developer_id: int | None,
        current_start_date: date | None,
        current_end_date: date | None,
        parent: QWidget | None = None,
    ) -> None: ...

    # Resultado apos accept()
    @property
    def selected_developer_id(self) -> int | None: ...

    @property
    def new_start_date(self) -> date | None: ...

    @property
    def new_end_date(self) -> date | None: ...
```

## Layout

```
┌─────────────────────────────────────────────┐
│  Alocar Desenvolvedor                    [X] │
│                                              │
│  Historia: COMP-001 - Nome da historia       │
│  Periodo: 02/04/2026 - 10/04/2026           │
│                                              │
│  Data de Inicio: [==== 02/04/2026 ====] ▼   │
│                                              │
│  ▼ Livres (3)                                │
│  ┌──────────────────────────────────────┐    │
│  │ ★ Ana Silva (Recomendado)     2 hist │    │
│  │   Carlos Santos               3 hist │    │
│  │   Maria Oliveira              1 hist │    │
│  └──────────────────────────────────────┘    │
│                                              │
│  ▼ Ocupados (1)                              │
│  ┌──────────────────────────────────────┐    │
│  │ ░ João Pereira (greyed out)   4 hist │    │
│  │   └ COMP-005 (01/04 - 08/04)        │    │
│  │   └ COMP-008 (07/04 - 12/04)        │    │
│  └──────────────────────────────────────┘    │
│                                              │
│              [Cancelar]  [Confirmar]         │
└──────────────────────────────────────────────┘
```

## Comportamentos

| Acao | Resultado |
|------|-----------|
| Alterar data de inicio | Recalcula end_date, reclassifica devs livres/ocupados, atualiza recomendacao |
| Selecionar dev livre | Habilita botao Confirmar |
| Clicar dev ocupado | Nada (desabilitado, greyed out) |
| Confirmar | `accept()` com developer_id + start_date + end_date |
| Cancelar | `reject()` sem mudancas |
| Historia sem datas | Exibe mensagem: "Execute o agendamento antes de alocar manualmente." |
| Nenhum dev cadastrado | Exibe mensagem: "Nenhum desenvolvedor cadastrado." |

## Restricoes do Date Picker
- Minimo: proximo dia util apos hoje
- Bloqueia fins de semana e feriados (BRAZILIAN_HOLIDAYS_2026_2028)
- Auto-corrige para proximo dia util via SchedulingService.next_workday()
