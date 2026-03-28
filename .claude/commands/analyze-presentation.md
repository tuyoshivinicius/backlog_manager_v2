---
description: Automatizar ciclo de analise de bugs GUI - executa testes, analisa conformidade design system, detecta anomalias e propoe correcoes. (project)
allowed-tools:
  - Bash
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - AskUserQuestion
  - TodoWrite
---

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

---

## 0. Log Cleanup (SEMPRE EXECUTAR PRIMEIRO)

**CRITICO**: Limpar logs antigos para garantir analise de dados frescos.

### 0.1 Detectar Plataforma e Caminho dos Logs

**Windows:**
```text
%APPDATA%/BacklogManager/logs/backlog_manager.log
```

**Linux:**
```text
~/.config/backlog_manager/logs/backlog_manager.log
```

### 0.2 Limpar Arquivo de Log

**Windows (Git Bash/MINGW):**
```bash
LOG_PATH="$APPDATA/BacklogManager/logs/backlog_manager.log"
if [ -f "$LOG_PATH" ]; then
    cp "$LOG_PATH" "${LOG_PATH}.bak.$(date +%Y%m%d_%H%M%S)"
    > "$LOG_PATH"
    echo "Log limpo: $LOG_PATH"
else
    mkdir -p "$(dirname "$LOG_PATH")"
    echo "Log nao existe ainda (sera criado na execucao)"
fi
```

**Linux:**
```bash
LOG_PATH="$HOME/.config/backlog_manager/logs/backlog_manager.log"
if [ -f "$LOG_PATH" ]; then
    cp "$LOG_PATH" "${LOG_PATH}.bak.$(date +%Y%m%d_%H%M%S)"
    > "$LOG_PATH"
    echo "Log limpo: $LOG_PATH"
fi
```

### 0.3 Por que Limpar?

- Logs antigos podem conter erros de execucoes anteriores
- Warnings de Qt podem se acumular e confundir analise
- Garante que os erros extraidos sao da execucao atual

---

## 0.5 Progress Tracking

**OBRIGATORIO**: Usar TodoWrite para acompanhar progresso.

Criar lista inicial:
```
1. [in_progress] Limpar logs antigos
2. [pending] Verificar pre-requisitos
3. [pending] Executar testes de presentation
4. [pending] Coletar metricas de cobertura
5. [pending] Analisar conformidade design system
6. [pending] Detectar anomalias
7. [pending] Validar aderencia aos requisitos (se anomalia)
8. [pending] Gerar relatorio
9. [pending] Propor correcoes (se necessario)
```

Atualizar status conforme progresso (`in_progress` -> `completed`).

---

## 1. Pre-requisite Verification

**HALT** if any check fails with an actionable message.

### 1.1 Check Poetry Installation

```bash
poetry --version
```

- **If fails**: HALT with message: "Poetry nao encontrado. Instale via: pip install poetry"

### 1.2 Check Dependencies

```bash
poetry check
```

- **If fails**: HALT with message: "Dependencias nao instaladas. Execute: poetry install"

### 1.3 Check Required Files

Verify these files exist:
- `src/backlog_manager/presentation/app.py`
- `src/backlog_manager/presentation/theme/theme.py`
- `src/backlog_manager/presentation/theme/stylesheet.qss`
- `src/backlog_manager/assets/icons/`
- `tests/unit/presentation/`
- `tests/integration/presentation/`

- **If missing**: HALT with message: "Arquivos de presentation nao encontrados. Verifique se a camada GUI foi implementada."

### 1.4 Check pytest-qt

```bash
poetry run python -c "import pytestqt; print('pytest-qt OK')"
```

- **If fails**: HALT with message: "pytest-qt nao instalado. Execute: poetry add --group dev pytest-qt"

### 1.5 Check radon

```bash
poetry run radon --version
```

- **If fails**: HALT with message: "radon nao instalado. Execute: poetry add --group dev radon"

---

## 2. Argument Parsing

Parse `$ARGUMENTS` for the following flags:

| Flag | Default | Behavior |
|------|---------|----------|
| `--run-gui` | false | Inicia GUI para captura de logs runtime |
| `--static-only` | true | Apenas analise estatica (codigo + testes) |
| `--coverage-threshold N` | 80 | Threshold minimo de cobertura (%) |
| `--component COMP` | all | Componente especifico: views, viewmodels, delegates, theme |
| `--verbose` | false | Output detalhado com diagnosticos |
| `--json` | false | Output em formato JSON |
| `--skip-tests` | false | Pular execucao de testes (usar metricas existentes) |

**Mode Selection**:
- If `--run-gui` present: Set `MODE=runtime`
- Otherwise: Set `MODE=static`

**Component Filter**:
- `all`: Analisa todos os componentes
- `views`: Apenas `presentation/views/`
- `viewmodels`: Apenas `presentation/viewmodels/`
- `delegates`: Apenas `presentation/delegates/`
- `theme`: Apenas `presentation/theme/`

---

## 3. Execution Flow (MODE=static)

### 3.1 Execute Presentation Tests

```bash
poetry run pytest tests/unit/presentation/ tests/integration/presentation/ -v --cov=src/backlog_manager/presentation --cov-report=term-missing --cov-report=json
```

- **If fails**: Capturar output para analise de anomalias
- **Capture output**: Salvar em variavel para processamento

### 3.2 Collect Coverage Metrics

Extrair metricas do arquivo `coverage.json`:

```bash
poetry run python -c "
import json
with open('coverage.json') as f:
    data = json.load(f)
    totals = data['totals']
    print(f'Total: {totals[\"percent_covered\"]:.1f}%')
    print(f'Lines: {totals[\"covered_lines\"]}/{totals[\"num_statements\"]}')
"
```

### 3.3 Coverage by Module

Calcular cobertura por modulo:

| Modulo | Caminho | Threshold |
|--------|---------|-----------|
| views | `presentation/views/` | >= 60% |
| viewmodels | `presentation/viewmodels/` | >= 80% |
| delegates | `presentation/delegates/` | >= 80% |
| theme | `presentation/theme/` | >= 90% |

### 3.4 Analyze Design System Conformance

**3.4.1 Check Hardcoded Colors in Stylesheet**

```bash
grep -E "#[0-9A-Fa-f]{3,8}" src/backlog_manager/presentation/theme/stylesheet.qss | grep -v "@" | head -20
```

- **If matches found**: Anomaly CRITICAL - cores hardcoded

**3.4.2 Validate Placeholders**

```bash
poetry run python -c "
import re
from pathlib import Path
qss = Path('src/backlog_manager/presentation/theme/stylesheet.qss').read_text()
from backlog_manager.presentation.theme import DESIGN_TOKENS
placeholders = set(re.findall(r'@([a-zA-Z][a-zA-Z0-9-]*)', qss))
missing = placeholders - set(DESIGN_TOKENS.keys())
if missing:
    print(f'ERRO: Placeholders sem token: {missing}')
else:
    print('OK: Todos placeholders mapeados')
"
```

**3.4.3 Check WCAG AA Compliance**

```bash
poetry run pytest tests/unit/presentation/theme/test_theme.py::TestStatusPaletteWCAG -v
```

**3.4.4 Check Icons Exist**

```bash
ls -la src/backlog_manager/assets/icons/*.svg 2>/dev/null | wc -l
```

- **Expected**: 16 arquivos SVG

**3.4.5 Check Focus Rules**

```bash
grep -c ":focus" src/backlog_manager/presentation/theme/stylesheet.qss
```

- **Expected**: >= 5 regras de foco

### 3.5 Analyze Cyclomatic Complexity

```bash
poetry run radon cc src/backlog_manager/presentation/ -s -a
```

- **Threshold**: CC <= 15 (Constitution XXI)
- **Capture functions** with CC > 15 as anomalies

### 3.6 Analyze Type Hints

```bash
poetry run mypy src/backlog_manager/presentation/ --ignore-missing-imports 2>&1 | head -50
```

- **If errors**: Capturar para relatorio

---

## 4. Execution Flow (MODE=runtime)

### 4.1 Start GUI with Logging

**IMPORTANTE**: Este modo requer interacao manual. O agente deve:

1. Informar o usuario que a GUI sera iniciada
2. Instruir o usuario a realizar acoes especificas
3. Coletar logs apos fechamento

```bash
poetry run python -m backlog_manager.presentation.app 2>&1 | tee /tmp/gui_session.log &
GUI_PID=$!
echo "GUI iniciada com PID $GUI_PID"
```

### 4.2 User Interaction Instructions

Solicitar ao usuario via AskUserQuestion:

**Question**: "A GUI foi iniciada. Realize as seguintes acoes e feche a janela quando terminar:"

**Options**:
- Criar nova historia
- Editar historia existente
- Executar alocacao automatica
- Navegar por todas as abas
- Testar atalhos de teclado

### 4.3 Collect Runtime Logs

Apos usuario fechar a GUI:

```bash
# Aguardar processo terminar
wait $GUI_PID 2>/dev/null

# Coletar logs
cat "$APPDATA/BacklogManager/logs/backlog_manager.log" | tail -100
```

### 4.4 Analyze Runtime Errors

Buscar padroes de erro:

```bash
grep -iE "error|exception|warning|traceback" "$APPDATA/BacklogManager/logs/backlog_manager.log" | head -30
```

### 4.5 Performance Metrics (se disponiveis)

Buscar metricas de tempo nos logs:

```bash
grep -E "load.*ms|render.*ms|startup.*seconds" "$APPDATA/BacklogManager/logs/backlog_manager.log"
```

---

## 5. Metrics Collection Summary

### 5.1 Static Metrics

| Metrica | Fonte | Tipo |
|---------|-------|------|
| test_coverage_total | coverage.json | float (%) |
| test_coverage_views | coverage.json | float (%) |
| test_coverage_viewmodels | coverage.json | float (%) |
| test_coverage_delegates | coverage.json | float (%) |
| test_coverage_theme | coverage.json | float (%) |
| tests_passed | pytest output | int |
| tests_failed | pytest output | int |
| hardcoded_colors | grep stylesheet.qss | int |
| missing_placeholders | python script | int |
| wcag_violations | pytest theme | int |
| icons_count | ls assets/icons | int |
| focus_rules_count | grep stylesheet.qss | int |
| cc_max | radon | int |
| cc_avg | radon | float |
| type_errors | mypy | int |

### 5.2 Runtime Metrics (MODE=runtime)

| Metrica | Fonte | Tipo |
|---------|-------|------|
| startup_time_seconds | logs | float |
| errors_count | logs | int |
| warnings_count | logs | int |
| qt_warnings | logs | int |

---

## 6. Anomaly Detection

### 6.1 Thresholds

| Metrica | Condicao | Severidade |
|---------|----------|------------|
| tests_failed | > 0 | CRITICAL |
| hardcoded_colors | > 0 | CRITICAL |
| test_coverage_total | < 80% | HIGH |
| test_coverage_viewmodels | < 80% | HIGH |
| wcag_violations | > 0 | HIGH |
| missing_placeholders | > 0 | HIGH |
| cc_max | > 15 | MEDIUM |
| focus_rules_count | < 5 | MEDIUM |
| type_errors | > 0 | MEDIUM |
| icons_count | < 16 | LOW |
| startup_time_seconds | > 3.0 | LOW |

### 6.2 Detection Rules

1. Check in order: CRITICAL -> HIGH -> MEDIUM -> LOW
2. Report highest severity anomaly first
3. Multiple anomalies at same level: report all

### 6.3 Anomaly -> Code Mapping

| Anomalia | Arquivo | Area de Codigo |
|----------|---------|----------------|
| Testes falhando | tests/*/presentation/ | Test assertions |
| Cores hardcoded | theme/stylesheet.qss | Color values |
| Rendering incorreto | delegates/*.py | paint() method |
| Cores incorretas | theme/theme.py | DESIGN_TOKENS, STATUS_PALETTE |
| Layout quebrado | views/*.py | QLayout setup, sizeHint() |
| Signal nao conectado | viewmodels/*.py | Signal/slot bindings |
| Accessibility | theme/stylesheet.qss | :focus rules |
| CC alto | presentation/**/*.py | Funcoes complexas |
| Type errors | presentation/**/*.py | Type hints |

### 6.4 Baseline Capture (se anomalia detectada)

**ANTES** de investigar causa raiz, capturar baseline:

```bash
poetry run radon cc src/backlog_manager/presentation/ -s 2>&1 | head -20
```

---

## 7. Requirement Adherence Validation

**CRITICO**: Antes de propor qualquer correcao, verificar aderencia aos requisitos.

### 7.1 Sources of Requirements

| Fonte | Caminho | Secoes Relevantes |
|-------|---------|-------------------|
| Constitution | `.specify/memory/constitution.md` | Principios I, IX, XIV, XXI |
| SRS | `srs.md` | Secao 4.1 RNF-PERF, 4.2 RNF-USAB |

### 7.2 Relevant Requirements for Presentation

**Do SRS (srs.md):**

| Requisito | Descricao | Comportamento Esperado |
|-----------|-----------|------------------------|
| RNF-PERF-002 | Latencia UI | <= 100ms CRUD, <= 500ms recalculo |
| RNF-PERF-003 | Memoria | <= 150MB para 100 historias |
| RNF-PERF-004 | Startup | <= 3 segundos cold start |
| RNF-USAB-002 | Resolucao | Funcional em 1366x768 |
| RNF-USAB-003 | Acessibilidade | Contraste 4.5:1, Tab navigation, tooltips |

**Da Constitution (.specify/memory/constitution.md):**

| Principio | Relevancia para Presentation |
|-----------|------------------------------|
| I. Clean Architecture | Presentation depende de Application, nao de Infrastructure |
| IX. Simplicidade | UI minimalista, sem over-engineering |
| XIV. Testes | Cobertura 100% para viewmodels |
| XXI. CI/CD | CC maximo 15 para funcoes de GUI |

### 7.3 Diagnostic Process with Requirement Validation

**Passo 1: Identificar o comportamento anomalo**
- Qual metrica esta fora do threshold?
- O que o sistema esta fazendo vs. o que deveria fazer?

**Passo 2: Mapear para requisito especifico**
- Ler o SRS e identificar qual RNF-* descreve o comportamento esperado
- Verificar se ha principio da Constitution sendo violado

**Passo 3: Classificar o bug**

| Classificacao | Descricao | Exemplo |
|---------------|-----------|---------|
| Desvio de Requisito | Codigo nao implementa o requisito | RNF-USAB-003 diz contraste 4.5:1 mas badge tem 3.2:1 |
| Requisito Ambiguo | Requisito nao cobre o cenario | RNF-USAB-003 nao especifica qual fonte usar |
| Bug de Implementacao | Logica correta mas com defeito | sizeHint() retorna valores negativos |
| Limitacao Conhecida | Comportamento esperado | Startup > 3s com banco muito grande |

**Passo 4: Documentar evidencia**

```markdown
## Analise de Aderencia

**Anomalia**: {descricao}
**Requisito Relacionado**: {RNF-XXX ou Principio X}
**Comportamento Esperado (SRS/Constitution)**: {texto do requisito}
**Comportamento Observado**: {o que aconteceu}
**Classificacao**: {Desvio | Ambiguo | Bug | Limitacao}
**Evidencia**: {dados que comprovam}
```

---

## 8. Report Generation

Generate structured report:

```markdown
## Relatorio de Analise de Presentation (GUI)

**Timestamp**: {YYYY-MM-DDTHH:MM:SS}
**Modo**: {static | runtime}
**Componente**: {all | views | viewmodels | delegates | theme}

### Metricas de Cobertura

| Modulo | Cobertura | Threshold | Status |
|--------|-----------|-----------|--------|
| Total | {value}% | 80% | {OK/NOK} |
| views | {value}% | 60% | {OK/NOK} |
| viewmodels | {value}% | 80% | {OK/NOK} |
| delegates | {value}% | 80% | {OK/NOK} |
| theme | {value}% | 90% | {OK/NOK} |

### Metricas de Testes

| Metrica | Valor |
|---------|-------|
| tests_passed | {value} |
| tests_failed | {value} |

### Conformidade Design System

| Check | Resultado | Status |
|-------|-----------|--------|
| Cores hardcoded | {count} | {OK/CRITICAL} |
| Placeholders mapeados | {count} missing | {OK/HIGH} |
| WCAG AA compliance | {violations} | {OK/HIGH} |
| Icons SVG | {count}/16 | {OK/LOW} |
| Focus rules | {count} | {OK/MEDIUM} |

### Complexidade

| Metrica | Valor | Threshold | Status |
|---------|-------|-----------|--------|
| CC maximo | {value} | 15 | {OK/MEDIUM} |
| CC medio | {value} | 10 | {OK/INFO} |

### Type Safety

| Metrica | Valor |
|---------|-------|
| Type errors | {count} |

### Anomalias Identificadas

{Se nenhuma anomalia: "Nenhuma anomalia detectada."}

{Se anomalia(s):}
**{SEVERITY}**: {tipo_anomalia}
- Metrica: {nome} = {valor}
- Threshold: {operador} {valor_esperado}
- Arquivo: {caminho}
- Descricao: {descricao_do_problema}

### Recomendacoes

{Lista de acoes sugeridas baseadas nas anomalias}
```

---

## 9. Correction Proposal (se anomalia detectada)

### 9.0 Pre-Proposal Validation Checklist

Antes de propor uma correcao, responder:

| Pergunta | Resposta Esperada |
|----------|-------------------|
| A correcao viola algum principio da Constitution? | NAO |
| A correcao esta alinhada com os requisitos RNF-*? | SIM |
| A correcao mantem CC <= 15 (Constitution XXI)? | SIM |
| A correcao segue Clean Architecture (Constitution I)? | SIM |
| A correcao e a solucao mais simples possivel (Constitution IX)? | SIM |

### 9.1 Proposal Format

```markdown
## Proposta de Correcao

**Anomalia**: {tipo} ({severidade})

### Analise de Aderencia aos Requisitos

**Requisito Base**: {RNF-XXX ou Principio X}
**Texto do Requisito**: {citar trecho relevante}

### Validacao da Correcao Proposta

| Criterio | Status | Justificativa |
|----------|--------|---------------|
| Alinhado com RNF-* | OK/NOK | {justificativa} |
| Respeita Constitution | OK/NOK | {justificativa} |
| Solucao minima | OK/NOK | {justificativa} |
| Testavel | OK/NOK | {justificativa} |

### Arquivos a Modificar

| Arquivo | Mudanca Proposta |
|---------|------------------|
| {path} | {descricao} |

### Codigo Proposto

{Bloco de codigo com mudancas sugeridas}

### Impacto Esperado

| Metrica | Atual | Esperado |
|---------|-------|----------|
| {metrica} | {valor} | {novo_valor} |
```

### 9.2 User Approval Flow

Use AskUserQuestion to get user decision:

**Question**: "Como deseja proceder com a proposta de correcao?"

**Options**:
- Aprovar: Aplicar a correcao proposta
- Rejeitar: Descartar proposta e encerrar
- Modificar: Ajustar a proposta antes de aplicar

### 9.3 Handle Response

- **Aprovar**: Apply the correction (Edit tool), continue to validation
- **Rejeitar**: HALT with message "Correcao descartada. Ciclo encerrado."
- **Modificar**: Ask for modifications, update proposal, re-ask for approval

---

## 10. Post-Correction Validation (se correcao aplicada)

### 10.1 Execute Test Suite

```bash
poetry run pytest tests/unit/presentation/ tests/integration/presentation/ -v --cov=src/backlog_manager/presentation
```

- **If fails**: Suggest rollback, do NOT proceed

### 10.2 Verify Coverage

Check coverage >= threshold

- **If fails**: Alert "Cobertura abaixo do threshold. Rollback sugerido."

### 10.3 Check Cyclomatic Complexity

```bash
poetry run radon cc src/backlog_manager/presentation/ -a -nc
```

- Verify no function exceeds CC=15 (per constitution XXI)
- **If fails**: Alert "Complexidade ciclomatica excede 15. Rollback sugerido."

### 10.4 Re-collect Metrics

1. Re-execute tests with coverage
2. Re-run design system checks
3. Extract metrics from new results

### 10.5 Generate Comparison Table

```markdown
## Comparativo de Metricas

| Metrica | Antes | Depois | Delta |
|---------|-------|--------|-------|
| {nome} | {antes} | {depois} | {delta} |
```

### 10.6 Rollback Suggestion

If any validation fails:

```markdown
## Validacao Falhou

**Problema**: {descricao}

### Sugestao de Rollback

1. Reverter alteracoes: `git checkout -- {files}`
2. Verificar configuracao
3. Re-executar /analyze-presentation
```

---

## 11. Troubleshooting

### Testes Qt Falhando

1. Verificar QApplication inicializada:
   ```python
   @pytest.fixture(scope="session")
   def qapp():
       app = QApplication.instance() or QApplication([])
       yield app
   ```

2. Verificar fixture `qtbot` do pytest-qt:
   ```bash
   poetry add --group dev pytest-qt
   ```

3. Verificar mock de asyncio em testes:
   ```python
   @pytest.fixture(autouse=True)
   def mock_asyncio_create_task():
       with patch("asyncio.create_task", return_value=MagicMock()):
           yield
   ```

### Screenshots Nao Capturados

1. Verificar se X11/Wayland esta rodando (Linux)
2. Verificar permissoes de escrita no diretorio de destino
3. Usar `QWidget.grab()` ao inves de screenshot externo

### Event Loop Conflicts (qasync)

1. Verificar se `QEventLoop` esta configurado:
   ```python
   from qasync import QEventLoop
   loop = QEventLoop(app)
   asyncio.set_event_loop(loop)
   ```

2. Evitar `asyncio.run()` dentro de callbacks Qt
3. Usar `asyncio.create_task()` para operacoes async

### Coverage Zero para Modulo

1. Verificar se modulo esta importado nos testes
2. Verificar se `__init__.py` existe em todos os diretorios
3. Verificar caminho no `--cov=` esta correto

### Windows-Specific Issues

1. **Fonts nao encontradas**: Verificar `font-family` no stylesheet usa fontes disponiveis
2. **Icones nao aparecem**: Verificar caminhos usam `/` (forward slash)
3. **Encoding errors**: Usar `encoding="utf-8"` em todas leituras de arquivo

### pytest-qt Nao Encontrado

```bash
poetry add --group dev pytest-qt
```

### radon Nao Instalado

```bash
poetry add --group dev radon
```

---

## 12. Useful Queries

### Listar Arquivos de Presentation

```bash
find src/backlog_manager/presentation -name "*.py" | grep -v __pycache__
```

### Verificar Cobertura por Arquivo

```bash
poetry run pytest tests/unit/presentation/ --cov=src/backlog_manager/presentation --cov-report=term-missing | grep -E "^src/.*\.py"
```

### Listar Funcoes com CC Alto

```bash
poetry run radon cc src/backlog_manager/presentation/ -s | grep -E "^\s+[A-Z]" | head -20
```

### Buscar Widgets sem :focus Rules

```bash
# Listar widgets mencionados no stylesheet
grep -oE "Q[A-Z][a-zA-Z]+" src/backlog_manager/presentation/theme/stylesheet.qss | sort -u

# Verificar quais tem :focus
grep -E "Q[A-Z][a-zA-Z]+:focus" src/backlog_manager/presentation/theme/stylesheet.qss
```

### Verificar Imports de PySide6

```bash
grep -r "from PySide6" src/backlog_manager/presentation/ | grep -v __pycache__
```

### Buscar Cores Hardcoded em Python

```bash
grep -rE "#[0-9A-Fa-f]{6}" src/backlog_manager/presentation/ --include="*.py" | grep -v __pycache__
```

### Verificar Sinais Conectados

```bash
grep -rE "\.connect\(" src/backlog_manager/presentation/ --include="*.py" | grep -v __pycache__
```

### Listar Delegates

```bash
grep -l "QStyledItemDelegate\|QItemDelegate" src/backlog_manager/presentation/delegates/*.py
```

---

## Correlation Table: Behavior to Metric

| Comportamento Observado | Metrica a Verificar | Acao Sugerida |
|-------------------------|---------------------|---------------|
| Widget nao renderiza | tests_failed | Executar testes e analisar falhas |
| Cores incorretas | hardcoded_colors, wcag_violations | Verificar stylesheet.qss e theme.py |
| Layout quebrado | tests_failed | Revisar sizeHint() e QLayout setup |
| Foco nao visivel | focus_rules_count | Adicionar regras :focus no stylesheet |
| Startup lento | startup_time_seconds | Profiling com cProfile |
| Memoria alta | N/A (monitorar manualmente) | Verificar referencias circulares |
| Signal nao dispara | tests_failed | Verificar connect() e emit() |
| Delegate nao pinta | tests_failed | Verificar paint() override |

---

## End of Skill

After completion, report:
- Total execution time
- Anomalies found (count by severity)
- Corrections applied (count)
- Final validation status
- Coverage comparison (if corrections applied)
