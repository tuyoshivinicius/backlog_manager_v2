# Epic Input Template

---

## Titulo

Refatoracao da Suite de Testes para Cobertura 80% Headless

## Descricao

A suite de testes atual depende fortemente de bibliotecas graficas (PySide6/pytest-qt) para executar testes de integracao e E2E, o que impede sua execucao em ambientes de CI sem display grafico. Alem disso, a medicao de cobertura esta restrita a camada de apresentacao, resultando em 66.6% de cobertura reportada — abaixo da meta de 90% (RNF-MANT-001). Esta epic elimina a dependencia grafica dos testes, reescreve os testes de integracao como headless, remove os testes E2E graficos, e amplia a cobertura para atingir a meta em todas as camadas da arquitetura.

## Atores

- **Desenvolvedor**: executa testes localmente e no CI, precisa de feedback rapido e confiavel sem depender de display grafico
- **Pipeline CI/CD**: executa a suite de testes automaticamente a cada push/PR, atualmente ignora 55 arquivos de teste por dependencia grafica

## Cenarios de Usuario

### Cenario 1 - Analise de cobertura real do projeto (Prioridade sugerida: P1)

O desenvolvedor precisa entender a cobertura real do projeto em todas as camadas (domain, application, infrastructure, presentation) para identificar onde investir esforco de testes. Atualmente a configuracao de cobertura so mede a camada presentation, resultando em 80 dos 119 arquivos fonte sem nenhuma medicao.

1. Desenvolvedor executa o relatorio de cobertura com configuracao corrigida
2. O sistema gera relatorio incluindo todas as 4 camadas da arquitetura
3. Desenvolvedor identifica classes e fluxos com cobertura abaixo de 90%
4. O sistema apresenta lista priorizada de arquivos que precisam de mais testes

**Arquivos de cobertura a analisar:**
- Camada domain: 18 arquivos fonte (entities, services, value_objects, exceptions)
- Camada application: 54 arquivos fonte (use_cases, DTOs, interfaces)
- Camada infrastructure: 8 arquivos fonte (database, excel, logging)
- Camada presentation: 39 arquivos fonte (views, viewmodels, delegates, theme)

---

### Cenario 2 - Remocao de testes E2E graficos (Prioridade sugerida: P1)

O desenvolvedor remove os 22 testes E2E que dependem de PySide6, pytest-qt e qasync, pois esses testes nao podem ser executados em CI headless e seu valor sera substituido por testes de integracao headless.

1. Desenvolvedor identifica todos os testes E2E com dependencia grafica
2. O sistema remove os arquivos de teste E2E do diretorio `tests/e2e/`
3. Desenvolvedor preserva artefatos reutilizaveis (factories de dados sem dependencia GUI)
4. O sistema confirma que nenhum teste restante importa modulos graficos removidos

**Testes E2E a remover (22 arquivos):**
- `tests/e2e/conftest.py` (fixtures Qt/async)
- `tests/e2e/test_smoke.py`
- `tests/e2e/test_uc001_criar_priorizar_backlog.py`
- `tests/e2e/test_uc002_alocacao_automatica.py`
- `tests/e2e/test_uc003_detectar_resolver_deadlock.py`
- `tests/e2e/test_uc004_importar_excel.py`
- `tests/e2e/test_uc005_gerenciar_ondas.py`
- `tests/e2e/test_ct001_backlog_completo.py`
- `tests/e2e/test_ct002_ciclo_grafo_grande.py`
- `tests/e2e/test_ct003_deadlock_devs.py`
- `tests/e2e/test_ct004_feriados_sequencia.py`
- `tests/e2e/test_ct005_balanceamento.py`
- `tests/e2e/test_ep022_about_dialog.py`
- `tests/e2e/test_ep022_cancellation.py`
- `tests/e2e/test_ep022_dependency_indicator.py`
- `tests/e2e/test_ep022_responsive.py`
- `tests/e2e/test_ep022_rich_tooltip.py`
- `tests/e2e/test_ep022_wave_separators.py`
- `tests/e2e/test_ep023_reset_planning.py`
- `tests/e2e/test_excel_roundtrip.py`
- `tests/e2e/test_performance.py`

**Artefato a preservar:**
- `tests/e2e/factories.py` (factories de dados sem dependencia GUI — mover para `tests/factories.py`)

---

### Cenario 3 - Triagem e tratamento de testes de integracao presentation (Prioridade sugerida: P1)

O desenvolvedor analisa os 16 testes de integracao da camada presentation que dependem de widgets Qt. Para cada teste, decide entre: (a) remover se a logica ja esta coberta por outros testes headless, ou (b) reescrever como headless apenas se testa logica de negocio critica nao coberta em outro lugar. O objetivo e nao reescrever testes desnecessariamente.

1. Desenvolvedor analisa cada teste de integracao presentation existente
2. O sistema verifica se a logica testada ja esta coberta por testes unitarios de ViewModel ou use case
3. Se ja coberta: desenvolvedor remove o teste GUI (duplicacao desnecessaria)
4. Se nao coberta e testa logica de negocio: desenvolvedor reescreve como headless
5. Se testa apenas renderizacao visual: desenvolvedor remove sem reescrita

**Testes de integracao presentation a triar (16 arquivos):**
- `tests/integration/presentation/views/test_config_dialog.py`
- `tests/integration/presentation/views/test_confirm_delete_dialog.py`
- `tests/integration/presentation/views/test_date_picker.py`
- `tests/integration/presentation/views/test_dependency_dialog.py`
- `tests/integration/presentation/views/test_dependency_panel.py`
- `tests/integration/presentation/views/test_developer_dialog.py`
- `tests/integration/presentation/views/test_feature_dialog.py`
- `tests/integration/presentation/views/test_main_window.py`
- `tests/integration/presentation/views/test_main_window_excel.py`
- `tests/integration/presentation/views/test_metrics_dialog.py`
- `tests/integration/presentation/views/test_progress_dialog.py`
- `tests/integration/presentation/views/test_result_dialog.py`
- `tests/integration/presentation/views/test_status_bar.py`
- `tests/integration/presentation/views/test_story_dialog.py`
- `tests/integration/presentation/test_delegates_integration.py`
- `tests/integration/presentation/test_theme_integration.py`

---

### Cenario 4 - Triagem e tratamento de testes unitarios presentation (Prioridade sugerida: P2)

O desenvolvedor analisa os 17 testes unitarios da camada presentation que dependem de Qt. Mesma logica de triagem do cenario 3: remover testes duplicados ou puramente visuais, reescrever como headless apenas os que testam logica de negocio unica nao coberta em outro lugar.

1. Desenvolvedor analisa cada teste unitario presentation existente
2. O sistema verifica se a logica ja esta coberta por outros testes headless
3. Se ja coberta: desenvolvedor remove o teste (evita reescrita desnecessaria)
4. Se testa logica unica de ViewModel: desenvolvedor reescreve como headless com mocks para Qt
5. Se testa apenas renderizacao/layout: desenvolvedor remove sem reescrita

**Testes unitarios presentation a triar (17 arquivos):**
- `tests/unit/presentation/delegates/test_monospace_delegate.py`
- `tests/unit/presentation/delegates/test_status_badge_delegate.py`
- `tests/unit/presentation/test_column_resize.py`
- `tests/unit/presentation/theme/test_theme.py`
- `tests/unit/presentation/viewmodels/test_allocation_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_config_dialog_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_config_dialog_viewmodel_qsettings.py`
- `tests/unit/presentation/viewmodels/test_dependency_dialog_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_filter_proxy_model.py`
- `tests/unit/presentation/viewmodels/test_main_window_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_manual_allocation_dialog_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_reset_planning_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_status_bar_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_status_bar_viewmodel_sp_breakdown.py`
- `tests/unit/presentation/viewmodels/test_story_dialog_viewmodel.py`
- `tests/unit/presentation/viewmodels/test_story_table_model.py`
- `tests/unit/presentation/viewmodels/test_story_table_model_blocking.py`
- `tests/unit/presentation/views/test_confirm_reset_dialog.py`
- `tests/unit/presentation/views/test_sp_breakdown_label.py`

---

### Cenario 5 - Ampliacao de cobertura focando em fluxos criticos (Prioridade sugerida: P1)

Apos a reescrita dos testes existentes, o desenvolvedor cria novos testes headless priorizando os fluxos e classes MAIS CRITICOS — aqueles com menor cobertura e maior impacto no negocio. O foco e maximizar o retorno de cada teste escrito.

1. Desenvolvedor consulta o relatorio de cobertura atualizado
2. O sistema lista os arquivos com cobertura abaixo de 80%, ordenados por criticidade
3. Desenvolvedor cria testes headless comecando pelos ViewModels com logica de negocio critica e menor cobertura
4. O sistema confirma que a cobertura global atingiu >= 90%

**Prioridade CRITICA — fluxos de negocio com cobertura < 40% (atacar primeiro):**

| Arquivo | Cobertura atual | Linhas faltando | Criticidade |
|---------|----------------|-----------------|-------------|
| `excel_viewmodel.py` | 28% | 77 | Logica critica de import/export — fluxo de negocio principal |
| `dependency_panel.py` | 38% | 96 | Gestao de dependencias — fluxo UC-003 |
| `schedule_viewmodel.py` | 38% | 31 | Calculo de cronograma — fluxo UC-002 |
| `metrics_panel.py` | 24% | 34 | Dashboard de metricas para decisoes |
| `dependency_indicator_delegate.py` | 28% | 29 | Indicador visual de dependencias |
| `warnings_panel.py` | 29% | 27 | Exibicao de alertas criticos (deadlock, ociosidade) |
| `config_panel.py` | 33% | 42 | Configuracao de velocidade e sprints |

**Prioridade ALTA — fluxos importantes com cobertura 40-80%:**

| Arquivo | Cobertura atual | Linhas faltando | Criticidade |
|---------|----------------|-----------------|-------------|
| `feature_dialog.py` | 43% | 109 | CRUD de features/ondas — fluxo UC-005 |
| `dependency_dialog_viewmodel.py` | 47% | 54 | Logica de selecao de dependencias |
| `developer_dialog.py` | 50% | 77 | CRUD de desenvolvedores |
| `main_window.py` | 65% | 250 | Orquestracao principal (maior arquivo) |
| `dependency_dialog.py` | 68% | 29 | Dialog de dependencias |

**Prioridade MEDIA — proximos de 90% (completar por ultimo):**

| Arquivo | Cobertura atual | Linhas faltando | Criticidade |
|---------|----------------|-----------------|-------------|
| `status_badge_delegate.py` | 71% | 18 | Renderizacao de badges |
| `container.py` | 71% | 42 | Wiring de DI |
| `progress_dialog.py` | 77% | 11 | Dialog de progresso |

**Arquivos com 0% — avaliar se sao testaveis headless:**

| Arquivo | Linhas | Natureza |
|---------|--------|----------|
| `app.py` | 77 | Entry point Qt — dificil testar headless, considerar `pragma: no cover` |
| `about_dialog.py` | 46 | Dialog puramente visual — baixa prioridade |
| `rich_tooltip.py` | 56 | Widget visual — baixa prioridade |

---

### Cenario 6 - Atualizacao do CI para executar todos os testes (Prioridade sugerida: P1)

Apos a reescrita, o pipeline CI deve executar todos os testes (incluindo os de presentation) sem necessidade de display grafico, removendo os filtros `--ignore` atuais.

1. Desenvolvedor atualiza a configuracao do CI
2. O sistema remove os flags `--ignore=tests/unit/presentation` e `--ignore=tests/integration/presentation`
3. O sistema remove o flag `-p no:pytest-qt` (ou mantem se pytest-qt for removido das dependencias)
4. O pipeline executa a suite completa e reporta cobertura >= 90%

## Regras de Negocio

- Nenhum teste no repositorio pode ser skipado (`@pytest.mark.skip`, `pytest.skip()`, `skipIf`) — todos os testes devem executar e passar
- Nenhum teste no repositorio pode depender de display grafico ou bibliotecas de renderizacao para execucao
- A cobertura de codigo deve ser medida em todas as 4 camadas da arquitetura (domain, application, infrastructure, presentation)
- Testes so devem ser reescritos se cobrem logica de negocio unica nao testada em outro lugar — remover testes duplicados ou puramente visuais em vez de reescrever
- Testes reescritos devem cobrir os mesmos cenarios de negocio que os testes originais — a logica testada nao pode ser perdida, apenas a dependencia grafica removida
- Factories de dados de teste devem ser preservadas e compartilhadas entre camadas de teste
- A meta de cobertura de 90% (RNF-MANT-001) deve ser atingida e validada no CI
- Testes de ViewModels devem testar logica de negocio e transformacao de dados, nao interacao com widgets
- O marker `e2e` pode ser mantido na configuracao pytest para uso futuro, mas nenhum teste deve usa-lo

## Premissas

- Os testes existentes de domain, application e infrastructure (86 arquivos) ja estao funcionando e nao precisam de alteracao
- Os ViewModels da camada presentation contem logica de negocio testavel sem Qt (sinais podem ser mockados)
- A cobertura real do projeto (incluindo todas as camadas) pode ser significativamente diferente dos 66.6% atuais, pois a medicao atual so inclui presentation
- O CI atual (GitHub Actions) nao possui display grafico e continuara sem

## Escopo

**Inclui**:
- Correcao da configuracao de cobertura para medir todas as camadas
- Analise completa de cobertura por arquivo e identificacao de gaps
- Remocao dos 22 arquivos de teste E2E com dependencia grafica
- Reescrita dos 16 testes de integracao presentation como headless
- Reescrita dos 17 testes unitarios presentation como headless
- Criacao de novos testes para atingir 80% de cobertura
- Atualizacao do workflow CI para executar todos os testes
- Migracao de factories de dados para local compartilhado

**Nao inclui**:
- Alteracao de codigo fonte de producao (src/)
- Criacao de novos testes E2E (mesmo headless)
- Testes de performance ou stress
- Alteracao de schema de banco de dados
- Testes visuais ou de renderizacao de widgets
- Testes de acessibilidade de UI

## Casos Limite

- O que acontece se a cobertura real (todas as camadas) ja estiver acima de 90% apos corrigir a configuracao? Resposta: os cenarios de reescrita headless continuam necessarios para eliminar dependencia grafica, mas o cenario 5 (ampliacao) pode ser reduzido.
- O que acontece com ViewModels que herdam de classes Qt (QObject, QAbstractTableModel)? Resposta: testes devem mockar a classe base Qt ou usar um stub minimo que nao requer display.
- Como testar delegates que dependem de QPainter para renderizacao? Resposta: testar apenas a logica de formatacao e decisao (cores, texto, dimensoes), nao a renderizacao em si.
- O que acontece se um teste reescrito nao consegue cobrir o mesmo cenario sem Qt? Resposta: documentar como "cobertura visual-only" e excluir do escopo, contabilizando no calculo de cobertura.

## Entidades Chave

- **Suite de Testes**: conjunto de 119 arquivos de teste organizados em 3 niveis (unit, integration, e2e) e 4 camadas arquiteturais
- **Cobertura**: medicao percentual de linhas de codigo exercitadas pelos testes, configurada em `pyproject.toml` com meta de 80% (RNF-MANT-001)
- **Teste Headless**: teste que nao requer display grafico, servidor X11, ou instanciacao de QApplication para execucao
- **ViewModel**: classe da camada presentation que contem logica de negocio e transformacao de dados, intermediando Views (Qt) e Use Cases (application)

## Criterios de Sucesso

- **SC-001**: Cobertura de codigo >= 90% medida em todas as 4 camadas da arquitetura, validada no CI
- **SC-002**: Zero testes no repositorio com dependencia de display grafico — `pytest` executa 100% da suite sem QApplication ou pytest-qt
- **SC-002b**: Zero testes skipados (`skip`, `skipIf`, `xfail`) — todos os testes devem executar e passar
- **SC-003**: Pipeline CI executa todos os testes (sem flags `--ignore` para presentation) e passa com sucesso
- **SC-004**: Numero de cenarios de negocio cobertos pelos testes reescritos >= numero de cenarios cobertos pelos testes originais com GUI
- **SC-005**: Tempo de execucao da suite completa de testes no CI <= 5 minutos
