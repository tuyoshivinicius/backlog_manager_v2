# Research: Resolucao de Issues SonarQube

**Branch**: `033-sonarqube-issues-fix` | **Date**: 2026-04-01

## R1: S3516 BLOCKER - Metodo `setData()` sempre retorna False

**Decision**: Alterar o retorno final do metodo `setData()` em `story_table_model.py:178` de `return False` para `return True` quando o sinal `status_change_requested` e emitido com sucesso.

**Rationale**: O metodo `setData()` do `QAbstractTableModel` DEVE retornar `True` quando os dados foram processados com sucesso (mesmo que a atualizacao real venha via reload assincrono). O retorno constante `False` e um bug porque:
- Linha 186: `return False` (index invalido ou role != EditRole) - CORRETO
- Linha 188: `return False` (coluna != Status) - CORRETO
- Linha 192: `return False` (status nao mudou) - CORRETO
- Linha 194: `return False` (apos emitir sinal de mudanca) - BUG: deveria ser `return True`

**Alternatives considered**:
- Manter `return False` e suprimir a issue: REJEITADO - e um bug real que pode causar comportamento inesperado no Qt (ex: delegates nao receberem notificacao de commit).

---

## R2: S7502 - Tasks asyncio sem referencia (12 issues SonarQube, ~46 instancias no codigo)

**Decision**: Implementar padrao `_create_task()` em cada classe View/ViewModel que cria tasks, armazenando em `set[asyncio.Task]` com `add_done_callback` para limpeza automatica.

**Rationale**: Tasks criadas com `asyncio.create_task()` ou `asyncio.ensure_future()` sem armazenar referencia podem ser coletadas pelo garbage collector antes de completar, causando falhas silenciosas. O padrao recomendado pelo Python docs e armazenar em um conjunto.

**Pattern**:
```python
def __init__(self, ...):
    super().__init__(...)
    self._pending_tasks: set[asyncio.Task[Any]] = set()

def _create_task(self, coro: Coroutine[Any, Any, Any]) -> asyncio.Task[Any]:
    """Cria e rastreia uma task assincrona com limpeza automatica."""
    task = asyncio.create_task(coro)
    self._pending_tasks.add(task)
    task.add_done_callback(self._pending_tasks.discard)
    return task
```

**Arquivos afetados (SonarQube reporta 12, codigo tem ~46 instancias)**:
- `presentation/views/main_window.py` (4 issues SonarQube + ~25 outras instancias)
- `presentation/views/developer_dialog.py` (3 issues)
- `presentation/views/feature_dialog.py` (3 issues)
- `presentation/views/story_dialog.py` (1 issue)
- `presentation/viewmodels/manual_allocation_dialog_viewmodel.py` (2 issues, usa `ensure_future`)

**Nota**: O SonarQube reporta apenas 12 instancias, mas o codigo tem ~46. A decisao e corrigir TODAS as instancias para consistencia, nao apenas as 12 reportadas. Issues adicionais nao serao introduzidas.

**Alternatives considered**:
- Corrigir apenas as 12 reportadas: REJEITADO - deixaria o mesmo bug em outros locais.
- Usar weakref em vez de set: REJEITADO - mais complexo sem beneficio real.
- Mixin/base class para `_create_task`: Considerar se houver muita duplicacao, mas por ora manter inline em cada classe para simplicidade (KISS).

---

## R3: S7497 - CancelledError silenciado (4 issues)

**Decision**: Re-raise `CancelledError` apos limpeza de recursos em todos os 4 handlers identificados.

**Rationale**: `CancelledError` e subclasse de `BaseException` (Python 3.9+). Silencia-lo impede a propagacao correta do cancelamento na cadeia de tasks asyncio, podendo causar estados inconsistentes.

**Pattern**:
```python
except asyncio.CancelledError:
    logger.info("Operacao cancelada pelo usuario")
    self.signal_cancelled.emit()
    raise  # SEMPRE re-raise apos limpeza
finally:
    self._is_running = False  # Estado limpo independentemente
```

**Arquivos afetados**:
1. `allocation_viewmodel.py:155` - Catch + emit signal + return None → adicionar `raise`
2. `excel_viewmodel.py:187` - Import cancelado + emit → adicionar `raise`
3. `excel_viewmodel.py:242` - Export cancelado + delete partial file + emit → adicionar `raise`
4. `main_window.py:1400` - Catch + pass → adicionar `raise`

**Nota sobre `return None`**: Apos adicionar `raise`, o `return None` se torna codigo morto. Remover.

**Alternatives considered**:
- Manter silenciado e suprimir: REJEITADO - e um bug real que pode causar estados inconsistentes.
- Usar `except Exception` em vez de `except asyncio.CancelledError`: REJEITADO - CancelledError nao e subclasse de Exception desde Python 3.9.

---

## R4: S3776 - Complexidade Cognitiva (17 issues)

**Decision**: Decompor metodos complexos em submethods privados, preservando interfaces publicas identicas. Estrategia varia por nivel de complexidade.

**Rationale**: Complexidade cognitiva >15 dificulta revisao, testes e manutencao. A constituicao (Principio IX) exige funcoes de no maximo 30-40 linhas com uma responsabilidade.

### Classificacao por Complexidade e Estrategia

**Criticos (CC > 50) - Decomposicao profunda**:
| Arquivo | Linha | CC Atual | Estrategia |
|---------|-------|----------|------------|
| `scripts/extract_metrics.py` | 299 | 96 | Decompor em funcoes por tipo de metrica extraida |
| `allocation_service.py` | 926 | 79 | Decompor em etapas do algoritmo de alocacao |
| `scripts/extract_metrics.py` | 69 | 72 | Decompor em funcoes por secao do relatorio |
| `scripts/seed_test_backlog.py` | 516 | 69 | Decompor em funcoes por tipo de entidade criada |

**Altos (CC 20-50) - Decomposicao moderada**:
| Arquivo | Linha | CC Atual | Estrategia |
|---------|-------|----------|------------|
| `import_excel_use_case.py` | 57 | 39 | Extrair validacao de linhas, processamento de colunas |
| `allocation_service.py` | 740 | 36 | Extrair logica de ondas em submethods |
| `allocation_service.py` | 404 | 34 | Extrair validacao e preparacao |
| `calculate_schedule.py` | 50 | 28 | Extrair iteracao de ondas e calculo de datas |
| `allocation_service.py` | 635 | 25 | Extrair logica de resolucao de conflitos |
| `get_developer_availability.py` | 51 | 26 | Extrair calculo de disponibilidade por periodo |
| `allocation_service.py` | 558 | 23 | Extrair verificacoes de estado |
| `list_stories.py` | 67 | 23 | Extrair filtragem e ordenacao |
| `excel_service.py` | 50 | 22 | Extrair processamento de celulas |
| `scheduling_service.py` | 180 | 20 | Extrair calculo de datas uteis |

**Borderline (CC 15-20) - Decomposicao leve**:
| Arquivo | Linha | CC Atual | Estrategia |
|---------|-------|----------|------------|
| `story.py` | 44 | 18 | Extrair validacoes de campos individuais em metodos privados |
| `allocation_service.py` | 846 | 17 | Refatorar condicional em early returns |
| `story_table_model.py` | 196 | 16 | Extrair formatacao de celulas por tipo |

**Alternatives considered**:
- Suprimir com comentario: REJEITADO para producao. ACEITAVEL apenas se decomposicao alterar comportamento (edge case).
- Alterar interfaces publicas: REJEITADO - constitui breaking change.

---

## R5: S1192 - Literal duplicado em `unit_of_work.py`

**Decision**: Extrair a string `"UnitOfWork must be used as context manager"` para uma constante de classe `_CONTEXT_MANAGER_ERROR_MSG`.

**Rationale**: String duplicada 4x indica que uma mudanca futura exigiria 4 alteracoes coordenadas (viola DRY, Principio IX).

**Pattern**:
```python
class UnitOfWork:
    _CONTEXT_MANAGER_ERROR_MSG = "UnitOfWork must be used as context manager"

    def some_method(self):
        if not self._in_context:
            raise RuntimeError(self._CONTEXT_MANAGER_ERROR_MSG)
```

**Alternatives considered**:
- Constante no nivel do modulo: REJEITADO - e especifica da classe.
- Remover mensagem e usar apenas `RuntimeError()`: REJEITADO - perde informacao de debug.

---

## R6: S5890 - Type hint incorreto em `theme.py:385`

**Decision**: Alterar type hint de `IconManager` para `Optional[IconManager]` (ou `IconManager | None`).

**Rationale**: A variavel `icon_manager` e inicializada com `None` mas o type hint nao reflete isso. Type hints incorretos podem causar erros em type checkers (mypy) e confundir IDEs.

**Alternatives considered**:
- Inicializar com instancia default em vez de None: REJEITADO - pode ter side effects indesejados.

---

## R7: S1186 - Metodos vazios em testes (19 issues)

**Decision**: Adicionar docstrings explicativas em metodos vazios de mocks e fixtures de teste.

**Rationale**: Metodos vazios em mocks sao intencionais (stubs que simulam a interface Qt). Docstring documenta essa intencao.

**Pattern**:
```python
def beginResetModel(self):
    """Stub intencional: simula interface QAbstractItemModel para testes headless."""
```

**Arquivos afetados**:
- `tests/conftest.py` (3 metodos: linhas 237/250/253)
- `tests/headless_mocks.py` (12 metodos: stubs de QAbstractItemModel e QSettings)
- `tests/unit/.../test_filter_proxy_model.py` (4 metodos: linhas 144/147/150/153)

**Alternatives considered**:
- Usar `pass` com comentario inline: REJEITADO - docstring e mais pythonic e alinhado com Principio XI.
- Usar `...` (Ellipsis): Nao resolve a issue SonarQube.

---

## R8: S1244 - Comparacoes float em testes (15 issues)

**Decision**: Substituir comparacoes diretas (`==`) por `pytest.approx()`.

**Rationale**: Comparacoes diretas de float podem falhar por imprecisao de ponto flutuante, causando testes flaky.

**Pattern**:
```python
# Antes:
assert result.velocity == 2.5

# Depois:
assert result.velocity == pytest.approx(2.5)
```

**Arquivos afetados**:
- `test_config_dialog_viewmodel.py` (5 comparacoes)
- `test_config_dialog_viewmodel_qsettings.py` (5 comparacoes)
- `test_status_bar_viewmodel_sp_breakdown.py` (2 comparacoes)
- `test_schedule_viewmodel.py` (1 comparacao)
- `test_allocation_service.py` (1 comparacao)

**Nota**: Verificar se `pytest.approx` ja esta importado em cada arquivo.

**Alternatives considered**:
- `math.isclose()`: REJEITADO - `pytest.approx` e mais idiomatico e gera mensagens de erro melhores.
- Tolerancia customizada: Usar default do pytest.approx (1e-6 relativo) salvo necessidade especifica.

---

## R9: S108 - Blocos de codigo vazios (8 issues)

**Decision**: Estrategia por contexto:
- `except` vazios em producao: Adicionar comentario explicando porque a excecao e ignorada, ou logar warning
- `except` vazios em testes: Adicionar comentario explicando que e intencional
- Blocos `if/else` vazios: Remover se nao servem proposito

**Arquivos e decisoes**:
| Arquivo | Linha | Decisao |
|---------|-------|---------|
| `presentation/app.py` | 34 | Adicionar comentario ou logging |
| `presentation/views/config_panel.py` | 24 | Adicionar comentario |
| `presentation/views/metrics_panel.py` | 16 | Adicionar comentario |
| `presentation/views/warnings_panel.py` | 22 | Adicionar comentario |
| `infrastructure/database/sqlite_connection.py` | 12 | Adicionar logging de warning |
| `scripts/seed_test_backlog.py` | 39 | Adicionar comentario |
| `tests/.../test_allocation_integration.py` | 24 | Adicionar comentario |
| `tests/.../test_seed_backlog.py` | 21 | Adicionar comentario |

**Alternatives considered**:
- Remover os blocos inteiros: REJEITADO onde o try/except tem proposito de engolir excecoes esperadas.

---

## R10: S1172 - Parametros nao utilizados (4 issues)

**Decision**: Estrategia por contexto:
- Parametros de interface/contrato: Prefixar com `_` (ex: `_input_dto`)
- Parametros realmente nao usados: Remover se possivel, prefixar com `_` se faz parte de assinatura obrigatoria

**Arquivos e decisoes**:
| Arquivo | Linha | Parametro | Decisao |
|---------|-------|-----------|---------|
| `reset_planning.py` | 34 | `input_dto` | Prefixar `_input_dto` (faz parte da interface UseCase) |
| `seed_test_backlog.py` | 644 | `wave_to_feature` | Remover se nao usado, ou prefixar `_` |
| `validate_allocation_data.py` | 267 | `strict` | Remover se nao usado, ou prefixar `_` |
| `tests/factories.py` | 19 | `with_dependencies` | Prefixar `_with_dependencies` (parametro de factory) |

---

## R11: S1854 - Variaveis locais nao usadas (3 issues)

**Decision**: Remover atribuicoes desnecessarias ou substituir por `_`.

| Arquivo | Linha | Variavel | Decisao |
|---------|-------|----------|---------|
| `allocation_service.py` | 447 | `new_start` | Remover atribuicao (valor nunca lido) |
| `test_excel_service.py` | 179 | `wb` | Substituir por `_` ou remover |
| `test_dependency_service.py` | 102 | `cycle` | Substituir por `_` |

---

## R12: S125 - Codigo comentado

**Decision**: Remover codigo comentado em `tests/integration/infrastructure/database/test_schema.py:86`.

**Rationale**: Codigo comentado e ruido. Se necessario no futuro, pode ser recuperado via git history.

---

## R13: S100/S116 - Naming conventions em `headless_mocks.py` (12 issues)

**Decision**: Suprimir com `# noqa: N802` (S100) e documentar que sao overrides de API Qt que DEVE usar camelCase.

**Rationale**: Metodos como `beginResetModel`, `endInsertRows`, `setValue`, `beginGroup` etc. sao overrides da API Qt que usa camelCase por convencao. Renomear quebraria a interface. Campos `IniFormat` e `UserScope` simulam enums do Qt.

**Pattern**:
```python
def beginResetModel(self):  # noqa: N802 - Override de QAbstractItemModel (Qt camelCase)
    """Stub intencional: simula interface QAbstractItemModel para testes headless."""
```

**Nota**: Verificar se o SonarQube respeita `# noqa`. Caso contrario, considerar `# NOSONAR` ou configurar exclusao no sonar-project.properties.

**Alternatives considered**:
- Renomear para snake_case: REJEITADO - quebraria compatibilidade com API Qt.
- Excluir arquivo inteiro do SonarQube: REJEITADO - perde analise de outras regras no mesmo arquivo.

---

## R14: S7503 - Funcoes async desnecessarias (7 issues)

**Decision**: Remover `async` das funcoes e atualizar TODOS os call sites para remover `await`.

**Rationale**: Constitui melhoria de conformidade com Principio VIII (Domain DEVE ser sincrono). Funcoes que nao usam `await` nao devem ser `async`.

**ATENCAO - Impacto em call sites**: Remover `async` muda o tipo de retorno de coroutine para valor direto. TODOS os `await` nos call sites devem ser removidos simultaneamente.

### Analise de Impacto por Funcao

| Funcao | Arquivo | Call Sites |
|--------|---------|------------|
| `CalculateDurationUseCase.execute()` | `calculate_duration.py:27` | `main_window.py` (~3 locais), `feature_dialog.py`, `developer_dialog.py` |
| `DeveloperService.create_developer()` | `developer_service.py:37` | `create_developer.py:44`, testes (3 locais) |
| `StoryService.swap_priorities()` | `story_service.py:87` | `move_priority.py:56/93`, testes |
| `StoryService.validate_can_move_up()` | `story_service.py:96` | `move_priority.py:47`, testes |
| `test_excel_viewmodel` (2 funcoes) | `test_excel_viewmodel.py:265/386` | Funcoes de teste, sem call sites externos |
| `test_schedule_viewmodel` (1 funcao) | `test_schedule_viewmodel.py:110` | Funcao de teste, sem call sites externos |

**Nota especial sobre `CalculateDurationUseCase.execute()`**: Esta na camada Application que DEVE ser async (Principio VIII). Porem, nao faz I/O. Duas opcoes:
1. Remover async (resolve SonarQube, viola convencao Application layer)
2. Manter async e suprimir (mantém convencao, nao resolve SonarQube)

**Decisao**: Remover `async` - a funcao e puramente computacional, sem I/O. O principio de "Application DEVE usar async" aplica-se a operacoes de I/O, nao a calculos puros.

**Alternatives considered**:
- Adicionar `await asyncio.sleep(0)` para justificar async: REJEITADO - e um hack.
- Manter async e suprimir: REJEITADO - viola KISS.

---

## R15: S7519 - dict.fromkeys() (3 issues)

**Decision**: Substituir construcoes de dicionario por `dict.fromkeys()` onde recomendado.

**Arquivos**:
- `dependency_service.py:131-132` (2 instancias)
- `tests/integration/test_seed_backlog.py:123` (1 instancia)

**Alternatives considered**:
- Dict comprehension: Depende do contexto. `dict.fromkeys()` e mais idiomatico para chaves com valor padrao.

---

## R16: S1481 - Variaveis locais nao usadas em testes (9 issues)

**Decision**: Substituir por `_` ou remover, conforme contexto.

| Arquivo | Variavel | Qtd | Decisao |
|---------|----------|-----|---------|
| `test_config_dialog_viewmodel.py` | `msg` | 4 | Substituir por `_` |
| `test_allocation_logging.py` | `pattern` | 1 | Remover se nao necessario |
| `test_scheduling_service.py` | `end` | 4 | Substituir por `_` (resultado de unpacking) |

---

## R17: S7504 - `list()` desnecessario

**Decision**: Remover `list()` em `tests/unit/presentation/test_container.py:285` se ja e iteravel.

---

## Decisoes Transversais

### Ordem de Implementacao
A ordem segue a prioridade da spec (P1→P10), agrupando por risco e interdependencia:

1. **P1**: S3516 BLOCKER (1 arquivo, baixo risco)
2. **P2**: S7502 tasks async (7 arquivos, medio risco - muitas instancias)
3. **P3**: S7497 CancelledError (4 locais, baixo risco)
4. **P4/P5**: S3776 complexidade cognitiva (17 metodos, ALTO risco - maior volume de mudancas)
5. **P6**: S1192 literal + S5890 type hint (2 arquivos, baixo risco)
6. **P7**: S1186 metodos vazios (3 arquivos, baixo risco)
7. **P8**: S1244 float equality (5 arquivos, baixo risco)
8. **P9**: S108/S1172/S1854/S125 limpeza (12 arquivos, baixo risco)
9. **P10**: S100/S116/S7503/S7519/S1481/S7504 convencoes (10 arquivos, baixo risco)

### Validacao Pos-Implementacao
- `ruff check .` DEVE passar sem erros
- `pytest` DEVE passar sem falhas
- SonarQube re-analise DEVE mostrar 0 issues OPEN (ou justificadamente suprimidas)
- Quality Gate DEVE mudar para OK
