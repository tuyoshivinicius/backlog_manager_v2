<role>
Voce e um engenheiro de QA senior especializado em aplicacoes desktop Qt/PySide6
e praticante de avaliacao heuristica de UX (Nielsen Norman Group). Voce domina
analise estatica de codigo GUI, triagem de defeitos E2E, e auditoria de
acessibilidade via inspecao de codigo-fonte.
</role>

<context>
## Projeto
Backlog Manager v2 — desktop Python 3.11+ com PySide6/Qt. Clean Architecture,
MVVM, DI container, signals/slots, async via qasync.

## Artefatos de Referencia
Ler ANTES de qualquer analise:

| Artefato | Caminho | Usar para |
|----------|---------|-----------|
| SRS | `srs.md` | Requisitos RF-*/RNF-* como criterio de aceite |
| Constitution | `.specify/memory/constitution.md` | 21 principios como guardrails |
| Testes E2E | `tests/e2e/` | Executar e mapear para use cases |
| Factories | `tests/e2e/factories.py` | Entender dados de teste disponiveis |
| Views | `src/backlog_manager/presentation/views/` | Alvo da inspecao UX/acessibilidade |
| ViewModels | `src/backlog_manager/presentation/viewmodels/` | Validacao, signals, async |
| Theme | `src/backlog_manager/presentation/theme/theme.py` | Design tokens, status palette |

## Requisitos-Chave (extraidos do SRS e Constitution)
| ID | Descricao | Threshold |
|----|-----------|-----------|
| RNF-PERF-002 | Latencia UI para CRUD | <= 100ms |
| RNF-PERF-004 | Cold start | <= 3s |
| RNF-USAB-003 | Acessibilidade | Contraste 4.5:1, Tab nav, tooltips |
| Principio XIV | Cobertura viewmodels | 100% |
| Principio XXI | Complexidade ciclomatica | CC <= 15 |

## Fronteiras com Skills Existentes
| Skill existente | O que JA cobre (NAO repetir) |
|-----------------|------------------------------|
| `analyze-presentation` | Cobertura de codigo por modulo, cores hardcoded no QSS, placeholders, WCAG em tokens, contagem de icones SVG, focus rules (contagem), CC via radon, type hints via mypy |
| `analyze-allocation` | Seed de dados, execucao de alocacao, metricas de log, ciclos de dependencia |

## Restricoes da Plataforma
- Opera via terminal, mas **PODE** executar GUI em modo headed para coleta de evidencias visuais quando solicitado
- Testes GUI via `pytest-qt` (`QTest` simula interacoes), com modo headless por default e headed em auditorias visuais
- Evidencias: output pytest, trechos de codigo, metricas, logs Qt, diffs, screenshots (`.png`) e video curto (`.mp4`/`.gif`) quando aplicavel
- Ferramentas de automacao visual:
  - Desktop Qt/PySide6: `pytest-qt` + `QTest` + captura de tela via Qt
  - Web flow (se existir componente web): `Playwright` ou `Selenium`
- Tools: `Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `AskUserQuestion`, `TodoWrite`
</context>

<input>
Implementar skill `.claude/commands/analyze-qa.md` com 5 dimensoes de analise
exclusivas, complementando as skills existentes.

## D1. Execucao e Triagem de Testes E2E

**Objetivo**: Executar testes end-to-end e classificar resultados por use case.

**Passos**:
1. Executar: `poetry run pytest tests/e2e/ -v --tb=short --timeout=60 2>&1`
2. Coletar: total, passed, failed, errors, skipped
3. Classificar cada falha por tipo: crash, assertion, timeout, fixture_error
4. Mapear testes para use cases do SRS (convencao: `test_uc001_*` → UC-001)
5. Gerar matriz de rastreabilidade teste ↔ use case

**Comando de mapeamento**:
```bash
# Listar testes E2E e seus use cases associados
poetry run pytest tests/e2e/ --collect-only -q 2>/dev/null | grep "::" | \
  sed 's/.*test_\(uc[0-9]*\|ct[0-9]*\|smoke\|excel\).*/\1/' | sort | uniq -c
```

---

## D2. Cobertura de Fluxos de Usuario

**Objetivo**: Identificar fluxos do SRS sem cobertura de teste E2E.

**Passos**:
1. Ler `srs.md` e extrair todos os use cases (UC-*) com fluxos principal + alternativos
2. Listar testes E2E existentes e mapear para use cases
3. Calcular: `% cobertura = fluxos_com_teste / total_fluxos * 100`
4. Classificar fluxos descobertos por risco:

| Risco | Criterio |
|-------|---------|
| CRITICAL | Fluxo manipula dados (create/update/delete) sem teste |
| HIGH | Fluxo principal de um UC sem nenhum teste |
| MEDIUM | Fluxo alternativo ou de erro sem teste |
| LOW | Fluxo de leitura (list/view) sem teste |

**Threshold**: >= 80% dos fluxos principais cobertos

---

## D3. Avaliacao Heuristica de UX (Nielsen)

**Objetivo**: Pontuar cada heuristica 1-5 via inspecao estatica do codigo PySide6.

### Rubrica de Pontuacao
| Score | Significado |
|-------|------------|
| 5 | Implementacao exemplar — padrao aplicado consistentemente em todos os widgets |
| 4 | Boa implementacao — presente na maioria dos casos, falhas pontuais |
| 3 | Implementacao parcial — padrao presente mas inconsistente ou incompleto |
| 2 | Implementacao minima — poucos casos, maioria ausente |
| 1 | Ausente ou falho — padrao nao implementado ou implementado incorretamente |

### Checklist por Heuristica com Comandos de Inspecao

**H1. Visibilidade do status do sistema**
O usuario sabe o que esta acontecendo a cada momento?
```bash
# Verificar signals de loading/error nos ViewModels
grep -rn "loading\|error_occurred\|_in_progress" src/backlog_manager/presentation/viewmodels/ --include="*.py"
# Verificar progress dialogs
grep -rn "QProgressDialog\|QProgressBar" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar atualizacoes de status bar
grep -rn "statusBar\|_status_" src/backlog_manager/presentation/views/main_window.py
# Verificar feedback de operacoes bem-sucedidas (ex: "Exportacao Concluida")
grep -rn "QMessageBox.information" src/backlog_manager/presentation/views/ --include="*.py"
```
- Checar: Todas as operacoes async tem indicador de progresso?
- Checar: Ha feedback visual apos operacoes bem-sucedidas (nao so erros)?
- Checar: Status bar mostra estatisticas atualizadas em tempo real?

**H2. Correspondencia com o mundo real**
A linguagem e familiar ao usuario? Segue convencoes do dominio?
```bash
# Verificar textos de botao e labels
grep -rn "setText\|setWindowTitle\|setPlaceholderText\|setLabelText" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar consistencia de idioma (portugues)
grep -rn "\"[A-Z][a-z]" src/backlog_manager/presentation/views/ --include="*.py" | head -40
```
- Checar: Todos os textos visiveis estao em portugues?
- Checar: Terminologia do dominio e consistente (historia/story, sprint, alocacao)?
- Checar: Unidades e formatos sao familiares (datas BR, Story Points)?

**H3. Controle e liberdade do usuario**
O usuario consegue sair de estados indesejados? Ha confirmacao antes de acoes destrutivas?
```bash
# Verificar dialogs de confirmacao antes de delete
grep -rn "ConfirmDeleteDialog\|QMessageBox.question\|QMessageBox.warning" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar botao Cancelar em todos os dialogs
grep -rn "Cancel\|Cancelar\|reject\|QDialogButtonBox" src/backlog_manager/presentation/views/ --include="*.py"
```
- Checar: Delete tem confirmacao? Todas as outras acoes destrutivas tambem?
- Checar: Todos os dialogs de formulario tem Cancelar/fechar?
- Checar: Ha undo/redo para acoes de edicao?

**H4. Consistencia e padroes**
Os mesmos elementos se comportam da mesma forma em toda a aplicacao?
```bash
# Verificar padrao de dialogs — todos seguem mesma estrutura?
grep -rn "class.*Dialog.*QDialog" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar ordem de botoes (Salvar antes de Cancelar? Ou o inverso?)
grep -rn "Salvar\|Cancelar\|Save\|Cancel\|OK" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar se todos os CRUD usam o mesmo fluxo (dialog modal)
grep -rn "\.exec()" src/backlog_manager/presentation/views/ --include="*.py"
```
- Checar: Todos os dialogs CRUD seguem o mesmo layout (campos + botoes)?
- Checar: Ordem de botoes e identica em todos os dialogs?
- Checar: Menus e toolbar estao organizados com a mesma logica?

**H5. Prevencao de erros**
O sistema previne que o usuario cometa erros?
```bash
# Verificar validacao de campos
grep -rn "setMaxLength\|validate\|setValidator\|setEnabled" src/backlog_manager/presentation/ --include="*.py" | head -30
# Verificar desabilitacao de botoes sem selecao
grep -rn "setEnabled(False)" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar se Salvar e desabilitado com campos invalidos
grep -rn "_save\|_submit\|_accept" src/backlog_manager/presentation/views/ --include="*.py"
```
- Checar: Botoes de acao sao desabilitados quando nao ha selecao na tabela?
- Checar: Formularios validam antes de permitir Salvar?
- Checar: Campos numericos impedem input de texto?

**H6. Reconhecimento ao inves de memoria**
O usuario precisa memorizar informacao ou ela esta visivel?
```bash
# Verificar tooltips em botoes e campos
grep -rn "setToolTip(" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar placeholders em inputs
grep -rn "setPlaceholderText(" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar comboboxes (opcoes visiveis vs campo livre)
grep -rn "QComboBox\|addItem\|addItems" src/backlog_manager/presentation/views/ --include="*.py"
```
- Checar: Todos os botoes da toolbar tem tooltip?
- Checar: Campos de formulario tem placeholder ou label explicativo?
- Checar: Opcoes fixas usam combobox (nao campo de texto livre)?

**H7. Flexibilidade e eficiencia de uso**
Usuarios avancados tem atalhos? Ha mais de uma forma de realizar acoes?
```bash
# Verificar keyboard shortcuts
grep -rn "QShortcut\|setShortcut\|QKeySequence" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar double-click para editar
grep -rn "doubleClicked\|itemDoubleClicked" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar context menu
grep -rn "CustomContextMenu\|contextMenu\|customContextMenuRequested" src/backlog_manager/presentation/views/ --include="*.py"
```
- Checar: Todas as acoes principais tem shortcut (Ctrl+N, F2, Del, etc.)?
- Checar: Double-click na tabela abre edicao?
- Checar: Context menu oferece acoes relevantes ao item selecionado?
- Checar: Context menu tem acoes alem de apenas "Dependencias"?

**H8. Design estetico e minimalista**
A interface mostra apenas informacao relevante?
```bash
# Contar widgets por dialog (complexidade visual)
for f in src/backlog_manager/presentation/views/*_dialog.py; do
  echo "$(basename $f): $(grep -c 'QLabel\|QPushButton\|QLineEdit\|QComboBox\|QSpinBox\|QCheckBox' "$f") widgets"
done
# Verificar agrupamento visual
grep -rn "QGroupBox\|QTabWidget\|addSeparator\|addSection" src/backlog_manager/presentation/views/ --include="*.py"
```
- Checar: Dialogs tem quantidade razoavel de campos (< 10 por view)?
- Checar: Informacao esta agrupada logicamente?
- Checar: Nao ha informacao redundante na mesma tela?

**H9. Ajuda para reconhecer, diagnosticar e recuperar erros**
Mensagens de erro sao claras e sugerem solucao?
```bash
# Coletar todas as mensagens de erro
grep -rn "QMessageBox\.\(warning\|critical\)" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar se mensagens sao especificas (nao genericas)
grep -rn "\"Erro\"" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar se erros de rede/db tem mensagem amigavel
grep -rn "except.*Exception" src/backlog_manager/presentation/ --include="*.py"
```
- Checar: Mensagens de erro descrevem O QUE deu errado (nao apenas "Erro")?
- Checar: Mensagens sugerem COMO resolver o problema?
- Checar: Exceptions nao vazam para o usuario como traceback?

**H10. Ajuda e documentacao**
Ha ajuda contextual acessivel?
```bash
# Verificar menu Ajuda
grep -rn "menu.*[Aa]juda\|menu.*[Hh]elp\|aboutQt\|about(" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar se tooltips cobrem TODOS os botoes da toolbar
grep -c "setToolTip" src/backlog_manager/presentation/views/main_window.py
# Contar acoes da toolbar vs tooltips
grep -c "addAction\|addWidget" src/backlog_manager/presentation/views/main_window.py
```
- Checar: Menu Ajuda tem conteudo funcional (nao apenas placeholder)?
- Checar: Todas as acoes da toolbar tem tooltip?
- Checar: Ha feedback textual apos operacoes demoradas?

---

## D4. Auditoria de Acessibilidade

**Objetivo**: Verificar conformidade de acessibilidade via inspecao de codigo.

### Checklist com Comandos

**4.1 Accessible Names e Descriptions**
```bash
# Buscar widgets com accessible name (ESPERADO: todos os interativos)
grep -rn "setAccessibleName\|setAccessibleDescription" src/backlog_manager/presentation/ --include="*.py"
# Contar widgets interativos que DEVERIAM ter
grep -rn "QPushButton\|QLineEdit\|QComboBox\|QSpinBox\|QCheckBox\|QTableView\|QListWidget" src/backlog_manager/presentation/views/ --include="*.py" | wc -l
```
**Criterio**: Cada widget interativo DEVE ter `setAccessibleName()`.
Ausencia total = achado HIGH.

**4.2 Tab Order**
```bash
# Buscar definicao explicita de tab order
grep -rn "setTabOrder\|setFocusPolicy\|TabFocus\|StrongFocus" src/backlog_manager/presentation/views/ --include="*.py"
# Listar dialogs com multiplos campos (candidatos a tab order)
for f in src/backlog_manager/presentation/views/*_dialog.py; do
  count=$(grep -c "QLineEdit\|QComboBox\|QSpinBox\|QPushButton" "$f")
  echo "$(basename $f): $count input widgets"
done
```
**Criterio**: Dialogs com >= 3 campos interativos DEVEM ter `setTabOrder()` explicito.
Ausencia em dialog com muitos campos = achado HIGH.

**4.3 Keyboard Shortcuts — SRS vs Implementacao**
```bash
# Extrair shortcuts implementados
grep -rn "QKeySequence\|QShortcut\|setShortcut" src/backlog_manager/presentation/views/ --include="*.py"
```
**Criterio**: Comparar shortcuts listados no SRS vs implementados no codigo. Delta = achado MEDIUM.

**4.4 Navegacao Completa por Teclado**
```bash
# Verificar keyPressEvent overrides
grep -rn "keyPressEvent\|keyReleaseEvent" src/backlog_manager/presentation/ --include="*.py"
# Verificar acoes acessiveis sem mouse (context menu via teclado?)
grep -rn "MenuKey\|Shift+F10\|contextMenuEvent" src/backlog_manager/presentation/views/ --include="*.py"
```
**Criterio**: Toda funcionalidade acessivel por mouse DEVE ser acessivel por teclado.
Context menu apenas via right-click (sem atalho de teclado) = achado MEDIUM.

---

## D5. Analise de Robustez e Edge Cases

**Objetivo**: Detectar fragilidades via analise de padroes perigosos no codigo.

### Anti-padroes a Buscar

**5.1 Empty State**
```bash
# Verificar se table model lida com lista vazia
grep -rn "rowCount\|_empty_state\|empty.*label\|Nenhuma" src/backlog_manager/presentation/ --include="*.py"
# Verificar se acoes sao desabilitadas quando tabela vazia
grep -rn "setEnabled.*rowCount\|stories_changed\|_update.*action\|_update.*empty" src/backlog_manager/presentation/ --include="*.py"
```
**Criterio**: Com 0 historias: botoes Edit/Delete/MoveUp/MoveDown devem estar desabilitados.
Label informativo deve ser visivel. Ausencia = achado HIGH.

**5.2 Validacao de Limites**
```bash
# Verificar setMaxLength nos forms
grep -rn "setMaxLength" src/backlog_manager/presentation/views/ --include="*.py"
# Comparar com validacao no ViewModel
grep -rn "max.*char\|len(.*) >" src/backlog_manager/presentation/viewmodels/ --include="*.py"
```
**Criterio**: Todo campo com `setMaxLength(N)` na view DEVE ter validacao correspondente
no ViewModel com mesmo limite. Divergencia = achado MEDIUM.

**5.3 Concorrencia e Race Conditions**
```bash
# Contar asyncio.create_task (pontos de concorrencia)
grep -rn "asyncio.create_task" src/backlog_manager/presentation/ --include="*.py"
# Verificar protecao contra double-submit
grep -rn "setEnabled(False).*save\|_in_progress\|_operation_in_progress" src/backlog_manager/presentation/ --include="*.py"
# Verificar blockSignals (ausencia pode ser risco)
grep -rn "blockSignals" src/backlog_manager/presentation/ --include="*.py"
```
**Criterio**: Cada `asyncio.create_task` DEVE ter protecao contra re-entrada
(botao desabilitado, flag _in_progress, ou guard clause). Ausencia = achado HIGH.

**5.4 Lifecycle de Dialogs**
```bash
# Verificar como dialogs sao criados e destruidos
grep -rn "\.exec()\|WA_DeleteOnClose\|deleteLater\|setAttribute" src/backlog_manager/presentation/views/ --include="*.py"
# Verificar se dialogs sempre recebem parent
grep -rn "Dialog(" src/backlog_manager/presentation/views/main_window.py
```
**Criterio**: Dialogs modais devem receber `parent=self` e ser executados com `.exec()`.
Dialog sem parent = achado MEDIUM (potencial leak, janela orfao).

**5.5 Tratamento de Erros Async**
```bash
# Verificar try/except em funcoes async chamadas por create_task
grep -rn "async def _" src/backlog_manager/presentation/ --include="*.py"
# Verificar se exceptions em tasks sao capturadas
grep -A5 "create_task" src/backlog_manager/presentation/ --include="*.py" | grep -c "try\|except"
```
**Criterio**: Toda funcao async disparada por `create_task` DEVE ter try/except
com feedback ao usuario via signal de erro. Exception silenciosa = achado HIGH.
</input>

<task>
Implemente a skill `analyze-qa.md` seguindo o padrao estrutural de
`analyze-presentation.md` (referencia para formato, convencoes, e fases):

### Estrutura de Fases

| Fase | Conteudo |
|------|----------|
| 0 | Log cleanup — mesmo script de `analyze-presentation` (Windows + Linux) |
| 0.5 | Progress tracking via TodoWrite |
| 1 | Pre-requisitos: poetry, pytest-qt, `srs.md` existe, `tests/e2e/` nao vazio |
| 2 | Argument parsing (flags abaixo) |
| 3 | **D1** — Execucao e triagem de testes E2E |
| 4 | **D2** — Cobertura de fluxos de usuario |
| 5 | **D3** — Avaliacao heuristica de UX (Nielsen, scorecard 1-5) |
| 6 | **D4** — Auditoria de acessibilidade |
| 7 | **D5** — Robustez e edge cases |
| 8 | Consolidacao de anomalias com taxonomia de severidade |
| 9 | Validacao cruzada contra SRS (RF-*/RNF-*) e Constitution |
| 10 | Relatorio em `reports/qa-report-YYYY-MM-DD.md` |
| 11 | Proposta de correcoes (somente se `--fix`) com aprovacao via AskUserQuestion |
| 12 | Validacao pos-correcao + comparativo antes/depois |

### Flags de Entrada

| Flag | Default | Descricao |
|------|---------|-----------|
| `--scope <modulo>` | all | Filtrar: views, dialogs, viewmodels, e2e, all |
| `--skip-e2e` | false | Pular execucao de testes (apenas analise estatica) |
| `--severity <nivel>` | LOW | Minimo para incluir no relatorio |
| `--fix` | false | Habilitar proposta e aplicacao de correcoes |
| `--visual-evidence` | false | Executar app/testes em modo headed e coletar screenshots/video como evidencia complementar |
| `--evidence-dir <path>` | reports/qa-evidence | Diretorio de saida para artefatos visuais |
| `--e2e-driver <qt|playwright|selenium>` | qt | Driver de automacao; usar `qt` por default para desktop |

### Taxonomia de Severidade

| Sev. | Criterios concretos |
|------|---------------------|
| CRITICAL | Teste E2E falha com crash/exception nao tratada; fluxo principal do SRS que manipula dados sem nenhum teste; exception silenciosa em async task |
| HIGH | Fluxo principal sem cobertura E2E; 0 accessible names em toda a app; heuristica Nielsen score 1/5; create_task sem protecao contra re-entrada; dialog sem parent |
| MEDIUM | Heuristica Nielsen score 2-3/5; fluxo alternativo sem teste; context menu so acessivel por mouse; divergencia setMaxLength vs validacao ViewModel |
| LOW | Tooltip ausente em widget isolado; label em idioma inconsistente; melhoria de UX sugerida |

### Template do Relatorio

```
# QA Report — Backlog Manager v2
**Data**: YYYY-MM-DD | **Escopo**: {scope} | **Modo**: {full|static-only}

## Resumo Executivo
| Metrica | Valor |
|---------|-------|
| Testes E2E | N total, N passed, N failed |
| Cobertura de fluxos | N% (N/N fluxos cobertos) |
| Nielsen (media) | N.N / 5 |
| Acessibilidade | N/N itens OK |
| Evidencia visual | N screenshots, N videos |
| Achados | N CRITICAL, N HIGH, N MEDIUM, N LOW |

## D1. Testes E2E
### Matriz de Rastreabilidade
| Use Case | Testes | Status | Tipo Defeito |
### Falhas (traceback resumido + classificacao)
### Evidencias visuais (arquivo + contexto do fluxo)

## D2. Cobertura de Fluxos
| UC | Fluxo | Coberto? | Risco |

## D3. Nielsen Scorecard
| # | Heuristica | Score | Evidencia (+) | Evidencia (-) |

## D4. Acessibilidade
| Item | Status | Detalhe |

## D5. Robustez
| Cenario | Status | Arquivo:Linha | Detalhe |

## Achados Consolidados
| ID | Sev. | Dim. | Descricao | Arquivo:Linha | Requisito |
| QA-001 | ... | ... | ... | ... | ... |

## Recomendacoes
## Proximos Passos
```

### Condicoes de HALT
- Poetry nao instalado ou `poetry check` falha
- `pytest-qt` nao importavel
- `tests/e2e/` nao existe ou vazio
- `srs.md` nao encontrado
- Se `--visual-evidence=true`: ambiente sem display/headed disponivel, ou driver visual solicitado indisponivel
</task>

<rules>
1. **NAO** repetir metricas de `analyze-presentation` — se ela ja mede (cobertura de codigo, cores hardcoded, CC, type hints, contagem de focus rules, contagem de icones), esta skill NAO mede novamente
2. Pode executar GUI e capturar evidencia visual **somente** quando `--visual-evidence` estiver ativo; em modo padrao, manter evidencia textual
3. Cada achado TEM que ter: ID (QA-NNN), severidade, dimensao (D1-D5), descricao, localizacao (arquivo:linha quando aplicavel), requisito relacionado (RF-*/RNF-*/Principio)
4. Nielsen: usar a rubrica 1-5 definida em D3; incluir TANTO evidencias positivas quanto negativas no scorecard
5. Fase 11-12 (correcao) so executa se `--fix` presente; correcoes DEVEM ser validadas contra Constitution e SRS ANTES de propor
6. Usar TodoWrite para progresso; AskUserQuestion antes de aplicar qualquer correcao
7. Idioma: secoes e textos em portugues; termos tecnicos em ingles (signal, widget, threshold, etc.)
8. Se um achado impacta multiplas dimensoes, registrar uma unica vez na dimensao mais relevante com referencia cruzada
9. Evidencia visual deve ser rastreavel ao fluxo: nomear artefatos com timestamp + UC/CT + etapa (ex.: `2026-03-29_uc001_create_story_step2.png`)
</rules>
