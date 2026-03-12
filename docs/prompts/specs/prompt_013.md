# Prompt: Exposicao do Calculo de Cronograma na GUI

<role>
Voce e um Especialista em UI/UX com PySide6/Qt e padrao MVVM, com profundo conhecimento em:
- Integracao de funcionalidades backend existentes em interfaces graficas
- PySide6 widgets (QAction, QToolBar, QShortcut, QMessageBox, signals/slots)
- Coordenacao de operacoes assincronas via qasync com Qt event loop
- Padrao MVVM aplicado a camada de apresentacao (Views delegam para ViewModels)
- Clean Architecture: Views nao importam de domain ou infrastructure
- Extensao de componentes existentes seguindo padroes ja estabelecidos no codigo
- Tratamento de erros e feedback ao usuario (RNF-CONF-002)

Voce produz especificacoes tecnicas prescritivas, minimalistas e incrementais, que estendem
codigo existente sem reescreve-lo.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica
- **Linguagem**: Python 3.11+ com type hints completas
- **UI**: PySide6 6.6.1+ com padrao MVVM
- **Async/Qt**: qasync para integracao asyncio <-> Qt event loop
- **Persistencia**: aiosqlite (async SQLite)
- **DTOs**: Pydantic ^2.0
- **Testes**: pytest + pytest-cov + pytest-asyncio + pytest-qt
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain

### Estado Atual do Codigo (Relevante para EP-013)

**Problema identificado**: O use case `CalculateScheduleUseCase` (RF-SCHED-001 a RF-SCHED-006) esta implementado e registrado no DI Container (`DIContainer.create_calculate_schedule_use_case()`), porem **nao ha forma do usuario dispara-lo pela interface grafica**. A toolbar atual possui acoes para CRUD de historias, prioridade, desenvolvedores, features, alocacao automatica e Excel — mas **nenhum botao para calcular cronograma**.

**Fluxo incompleto atual**: O usuario pode cadastrar historias → definir dependencias → **[lacuna: calcular cronograma]** → alocar automaticamente. O EP-008 assume que o calculo de cronograma ja foi executado antes da alocacao, mas nao ha gatilho na GUI para isso.

**Componentes existentes relevantes:**

1. **MainWindow** (`src/backlog_manager/presentation/views/main_window.py`):
   - Toolbar com acoes: Nova Historia, Editar, Deletar, Mover Cima/Baixo, Desenvolvedores, Features, Alocar Automaticamente, Importar/Exportar Excel
   - Metodo `_on_allocate()` como referencia para implementar `_on_calculate_schedule()`
   - Metodo `_execute_allocation()` como template para `_execute_calculate_schedule()`
   - Propriedade `_config_panel` que expoe `velocity` e `start_date`
   - Conexao com `MainWindowViewModel` via signals/slots

2. **ConfigPanel** (`src/backlog_manager/presentation/views/config_panel.py`):
   - Propriedades publicas: `velocity` (float), `start_date` (date), `max_idle_days` (int)
   - Metodo `validate()` que retorna `tuple[bool, str]`
   - Ja utilizado pelo botao "Alocar Automaticamente"

3. **DIContainer** (`src/backlog_manager/presentation/container.py`):
   - Factory method `create_calculate_schedule_use_case(uow)` ja existe (linha 419-430)
   - Retorna `CalculateScheduleUseCase` configurado com UnitOfWork

4. **CalculateScheduleUseCase** (`src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py`):
   - Metodo `execute(input_dto: CalculateScheduleInputDTO) -> CalculateScheduleOutputDTO`
   - Input: velocity (float), start_date (date), recalculate_all (bool)
   - Output: success (bool), stories_processed (int), stories_updated (int), warnings (list[str])
   - Pode lancar `CyclicDependencyException` se detectar ciclo

5. **CalculateScheduleInputDTO/OutputDTO** (`src/backlog_manager/application/dto/scheduling/calculate_schedule_dto.py`):
   - `CalculateScheduleInputDTO(velocity: float, start_date: date, recalculate_all: bool = True)`
   - `CalculateScheduleOutputDTO(success: bool, stories_processed: int, stories_updated: int, warnings: list[str])`

**Padroes ja estabelecidos no codigo:**

- Botoes de toolbar usam `QAction` com `setToolTip()` e `setShortcut()`
- Atalhos globais usam `QShortcut(QKeySequence(...), self)`
- Operacoes async sao disparadas via `QTimer.singleShot(0, lambda: asyncio.create_task(...))`
- Erros sao exibidos via `QMessageBox.warning(self, "Erro", message)`
- Sucesso de operacoes longas usa `QMessageBox.information(self, "Titulo", mensagem)`
- Reload de dados apos operacao: `await self._viewmodel.load_stories()`
- Logging no inicio de handlers: `logger.debug("Action triggered")`

### Conflitos e Lacunas Conhecidos

**Nenhum conflito arquitetural** — todos os componentes necessarios ja existem. Este epico e uma **integracao simples** de UI que adiciona:
1. Um botao na toolbar
2. Um atalho de teclado
3. Dois metodos no MainWindow (`_on_calculate_schedule` e `_execute_calculate_schedule`)
4. Feedback visual ao usuario

### Referencia de Implementacao Similar

O botao "Alocar Automaticamente" serve como **template exato** para implementar "Calcular Cronograma":

```python
# Exemplo existente em MainWindow (linhas 187-192):
self._action_allocate = QAction("Alocar Automaticamente", self)
self._action_allocate.setToolTip("Executar alocacao automatica (Ctrl+Shift+A)")
self._action_allocate.setShortcut(QKeySequence("Ctrl+Shift+A"))
self._action_allocate.triggered.connect(self._on_allocate)
toolbar.addAction(self._action_allocate)

# Handler existente (linhas 473-485):
@Slot()
def _on_allocate(self) -> None:
    logger.debug("Allocate action triggered")
    is_valid, error = self._config_panel.validate()
    if not is_valid:
        QMessageBox.warning(self, "Configuracao Invalida", error)
        return
    QTimer.singleShot(0, lambda: asyncio.create_task(self._execute_allocation()))

# Executor async existente (linhas 487-498):
async def _execute_allocation(self) -> None:
    allocation_vm = self._container.allocation_viewmodel
    await allocation_vm.execute(
        velocity=self._config_panel.velocity,
        start_date=self._config_panel.start_date,
        max_idle_days=self._config_panel.max_idle_days,
    )
    await self._viewmodel.load_stories()
```
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-013_gui-calculo-cronograma.md` — requisitos, escopo, criterios de aceite, riscos e premissas
2. **SRS**: `srs.md` — secoes:
   - §3.5 RF-SCHED-001 a RF-SCHED-006 (requisitos de calculo de cronograma)
   - §4.1 RNF-PERF-002 (responsividade ≤ 500ms para recalculo)
   - §4.2 RNF-USAB-003 (acessibilidade, atalhos de teclado, tooltips)
   - §4.3 RNF-CONF-002 (recuperacao de erros)
3. **Constituicao**: `.specify/memory/constitution.md` — principios:
   - §VIII Programacao Assincrona (async/await, QTimer.singleShot)
   - §XIV Estrategia de Testes (pytest-qt, qasync, cobertura alvo)
   - §XVI Tratamento de Erros (hierarquia de excecoes, mensagens claras)
   - §XIX Padroes de UI/UX (MVVM, Views nao importam de domain)
4. **MainWindow existente**: `src/backlog_manager/presentation/views/main_window.py` — estrutura atual da toolbar, metodo `_on_allocate` como template
5. **ConfigPanel existente**: `src/backlog_manager/presentation/views/config_panel.py` — propriedades velocity, start_date, validate()
6. **DIContainer**: `src/backlog_manager/presentation/container.py` — factory method `create_calculate_schedule_use_case()` (linha 419)
7. **CalculateScheduleUseCase**: `src/backlog_manager/application/use_cases/scheduling/calculate_schedule.py` — interface do use case, input/output DTOs
8. **CalculateScheduleDTO**: `src/backlog_manager/application/dto/scheduling/calculate_schedule_dto.py` — estrutura dos DTOs de entrada/saida
9. **MainWindowViewModel**: `src/backlog_manager/presentation/viewmodels/main_window_viewmodel.py` — verificar que nao ha metodo relacionado a schedule (confirmar que implementacao vai no MainWindow)
10. **Spec de referencia EP-008**: `specs/008-ep008-gui/spec.md` — padrao de especificacao de componentes de UI (se disponivel)
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-013 — Exposicao do Calculo de Cronograma na GUI`.

Este e um epico de **integracao minimalista** que adiciona uma funcionalidade de UI para expor um use case ja existente. A especificacao deve cobrir **exclusivamente**:

**Alteracoes em MainWindow (`main_window.py`):**

| Item | Descricao | Referencia |
|------|-----------|------------|
| `_action_calculate_schedule` | QAction "Calcular Cronograma" na toolbar, **posicionado antes** de "Alocar Automaticamente" | CA-01 |
| Atalho Ctrl+Shift+C | Configurado via `setShortcut(QKeySequence("Ctrl+Shift+C"))` | CA-02 |
| Tooltip | "Calcular datas de inicio e fim das historias (Ctrl+Shift+C)" | CA-03 |
| `_on_calculate_schedule()` | Slot que valida ConfigPanel, invoca use case, exibe feedback | CA-04 |
| `_execute_calculate_schedule()` | Metodo async que executa o calculo e atualiza tabela | CA-05 |

**Fluxo de execucao esperado:**

1. Usuario clica botao ou pressiona Ctrl+Shift+C
2. MainWindow chama `_on_calculate_schedule()`
3. Handler valida `_config_panel.validate()`
4. Se invalido: `QMessageBox.warning` com erro (CA-06)
5. Se valido: `asyncio.create_task(self._execute_calculate_schedule())`
6. `_execute_calculate_schedule()`:
   - Cria UnitOfWork via `async with self._container.create_unit_of_work() as uow:`
   - Cria use case via `self._container.create_calculate_schedule_use_case(uow)`
   - Cria input DTO: `CalculateScheduleInputDTO(velocity=..., start_date=..., recalculate_all=True)`
   - Executa `result = await use_case.execute(input_dto)`
   - Se `CyclicDependencyException`: exibir `QMessageBox.warning` com mensagem clara
   - Se sucesso: exibir `QMessageBox.information` com `{result.stories_updated} historias tiveram datas calculadas`
   - Se warnings: logar ou incluir na mensagem
   - Chama `await self._viewmodel.load_stories()` para atualizar tabela (CA-07)

**Testes a especificar:**

| Tipo | Teste | Cobertura |
|------|-------|-----------|
| Unitario | `test_on_calculate_schedule_validates_config` | Validacao de parametros invalidos |
| Unitario | `test_on_calculate_schedule_calls_use_case` | Invocacao correta do use case com mock |
| Unitario | `test_calculate_schedule_shows_success_dialog` | Feedback de sucesso |
| Unitario | `test_calculate_schedule_shows_error_on_invalid_config` | Tratamento de erro de validacao |
| Unitario | `test_calculate_schedule_handles_cyclic_dependency` | Tratamento de `CyclicDependencyException` |
| Integracao | `test_calculate_schedule_button_visible` | Presenca na toolbar com pytest-qt |
| Integracao | `test_calculate_schedule_shortcut_works` | Atalho Ctrl+Shift+C funcional |
| Integracao | `test_calculate_schedule_tooltip_correct` | Tooltip descritivo visivel |

**IMPORTANTE**: Este epico **NAO** cria:
- Use cases novos (CalculateScheduleUseCase ja existe em EP-006)
- DTOs novos (CalculateScheduleInputDTO/OutputDTO ja existem)
- Factory methods novos (create_calculate_schedule_use_case ja existe)
- Alteracoes em ConfigPanel (velocity e start_date ja sao expostos)
- ViewModels novos (seguir pattern de _on_allocate que executa direto no MainWindow)
- Alteracoes no DI Container

A especificacao deve ser **minimalista** e focada apenas nas alteracoes necessarias no arquivo `main_window.py` e nos testes correspondentes.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Codigo existente prevalece**: Nao redefinir Use Cases, DTOs, ConfigPanel ou DIContainer. Especificar apenas **adicoes** ao arquivo `main_window.py`.

2. **Seguir padroes estabelecidos**: Usar exatamente o mesmo pattern de `_on_allocate()` e `_execute_allocation()` como template. Nao inventar novos padroes.

3. **Posicionamento na toolbar**: O botao "Calcular Cronograma" DEVE aparecer **antes** de "Alocar Automaticamente", conforme especificado no epico. Isso requer adicionar a action antes do separator e da action de alocacao.

4. **Atalho de teclado**: Ctrl+Shift+C conforme definido no epico. Usar `QKeySequence("Ctrl+Shift+C")` no `setShortcut()` do QAction.

5. **Feedback visual**:
   - Sucesso: `QMessageBox.information(self, "Calculo Concluido", f"{result.stories_updated} historias tiveram datas calculadas.")`
   - Erro de validacao: `QMessageBox.warning(self, "Configuracao Invalida", error)`
   - Erro de dependencia ciclica: `QMessageBox.warning(self, "Erro", "Ciclo de dependencia detectado: ...")`
   - Erro inesperado: `QMessageBox.warning(self, "Erro", str(exception))`

6. **Integracao async correta**:
   - Usar `QTimer.singleShot(0, lambda: asyncio.create_task(...))` para disparar operacao async
   - Use case deve ser executado dentro de `async with uow:` para garantir transacao
   - Reload de tabela via `await self._viewmodel.load_stories()` apos sucesso

7. **Tratamento de erros**: Capturar `CyclicDependencyException` especificamente e exibir mensagem clara ao usuario, conforme RNF-CONF-002. Mensagens em portugues.

8. **Rastreabilidade**: Mapear implementacao para criterios de aceite do epico:
   - CA-01: Botao visivel na toolbar antes de "Alocar Automaticamente"
   - CA-02: Atalho Ctrl+Shift+C funcional
   - CA-03: Tooltip descritivo
   - CA-04: Calculo executa corretamente
   - CA-05: Dialog de feedback com contagem
   - CA-06: Erro com parametros invalidos
   - CA-07: Tabela atualizada apos calculo

9. **Testes com pytest-qt**: Especificar testes usando `qtbot` fixture. Mock do use case para testes unitarios. Testes de integracao verificam presenca de widgets e conexao de sinais.

10. **Idioma**: Textos de UI em portugues brasileiro (sem acentos por padrao do SRS §8.2). Codigo em ingles.

11. **Performance**: Operacao deve completar em ≤ 500ms para backlogs tipicos (RNF-PERF-002). Nao bloquear thread principal durante execucao (async).

12. **Sem over-engineering**: Este e um epico de integracao simples. A especificacao NAO deve incluir:
    - Novos ViewModels
    - Novos paineis ou widgets
    - Refatoracao de codigo existente
    - Features nao solicitadas no epico

13. **Logging**: Adicionar `logger.debug("Calculate schedule action triggered")` no inicio do handler, seguindo padrao existente.

14. **Consistencia com EP-008**: Este epico completa a integracao iniciada em EP-008. Manter consistencia visual e comportamental com outros botoes da toolbar.

15. **Import adicional**: Adicionar import de `CalculateScheduleInputDTO` no topo do arquivo:
    ```python
    from backlog_manager.application.dto.scheduling.calculate_schedule_dto import (
        CalculateScheduleInputDTO,
    )
    from backlog_manager.domain.exceptions import CyclicDependencyException
    ```
</rules>
