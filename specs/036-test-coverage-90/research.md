# Research: Cobertura de Testes 90% e Quality Gate SonarQube

**Feature**: 036-test-coverage-90 | **Date**: 2026-04-01

## R1. Alinhamento de Exclusões SonarQube ↔ pytest-cov

### Decision
Atualizar `sonar.coverage.exclusions` em `sonar-project.properties` para incluir os mesmos padrões que o `[tool.coverage.run].omit` do `pyproject.toml`, traduzidos para sintaxe Ant-style glob do SonarQube.

### Rationale
- **Causa raiz**: SonarQube reporta 56.7% porque conta linhas de views PySide6 (~2,838 linhas), delegates (~158 linhas), `__init__.py` (~100 linhas), interfaces abstratas (~88 linhas), `app.py` (~80 linhas) e `__main__.py` como código testável. pytest-cov exclui todos esses arquivos, reportando ~94%.
- **Impacto estimado**: Excluir ~3,264 linhas não-testáveis eleva a cobertura SonarQube de 56.7% para ~94%, resolvendo o Quality Gate imediatamente.
- **Sintaxe**: pytest-cov usa fnmatch (`*/path/*.py`); SonarQube usa Ant-style (`**/path/**`). A tradução é direta.

### Mapping de Padrões

| pytest-cov (fnmatch) | SonarQube (Ant-style) | Descrição |
|---|---|---|
| `*/tests/*` | `**/tests/**` | Arquivos de teste |
| `*/__init__.py` | `**/__init__.py` | Re-exports de módulos |
| `*/presentation/app.py` | `**/presentation/app.py` | Entry point Qt |
| `*/presentation/views/*.py` | `**/presentation/views/**` | Views PySide6 |
| `*/presentation/delegates/*.py` | `**/presentation/delegates/**` | Delegates Qt |
| `*/__main__.py` | `**/__main__.py` | Entry point CLI |
| `*/domain/interfaces/*.py` | `**/domain/interfaces/**` | Interfaces abstratas |
| `*/presentation/constants.py` | `**/presentation/constants.py` | Constantes de UI |
| (não listado) | `**/conftest.py` | Fixtures de teste (já no SonarQube) |

### Alternatives Considered

1. **Usar `sonar.exclusions` ao invés de `sonar.coverage.exclusions`**: Rejeitado — `sonar.exclusions` remove os arquivos da análise completa (bugs, code smells), não apenas da cobertura. Queremos que SonarQube continue analisando qualidade desses arquivos.
2. **Configurar exclusões via SonarCloud UI**: Rejeitado — configuração deve estar versionada no repositório para reprodutibilidade.
3. **Alterar pytest-cov para incluir mais arquivos**: Rejeitado — os arquivos excluídos são genuinamente não-testáveis unitariamente (views com dependência de display, interfaces abstratas).

---

## R2. Estratégia de Testes para Arquivos Parcialmente Cobertos

### Decision
Adicionar testes para os 16 arquivos prioritários organizados em 3 tiers por impacto e complexidade. Usar mocks headless para viewmodels, AsyncMock para use cases async, e fixtures existentes para integração.

### Rationale
- Após alinhamento de exclusões, restam ~139 linhas de código testável parcialmente coberto.
- Os arquivos estão distribuídos em 3 camadas: Application (use cases + DTOs), Domain (services) e Presentation (viewmodels) + Infrastructure.
- A infraestrutura de testes existente (factories, headless_mocks, conftest) já suporta todos os cenários necessários.

### Tier 1 — Impacto Crítico (cobertura < 70%)

| Arquivo | Cobertura | Linhas Descobertas | Estratégia |
|---|---|---|---|
| `application/use_cases/story/edit_story.py` | 44.4% | 23 | Testar caminhos de edição parcial, validação de campos opcionais |
| `infrastructure/database/sqlite_connection.py` | 65.6% | 8 | Testar error handling de conexão, retry logic |
| `application/dto/story/edit_story_dto.py` | 69.8% | 10 | Testar validação de DTOs com campos opcionais/nulos |
| `application/use_cases/story/list_stories.py` | 69.4% | 26 | Testar filtros, ordenação, paginação |

### Tier 2 — Impacto Alto (cobertura 70-85%)

| Arquivo | Cobertura | Linhas Descobertas | Estratégia |
|---|---|---|---|
| `infrastructure/logging/logger_config.py` | 74.1% | 10 | Testar configuração de rotação, formatação |
| `presentation/viewmodels/story_table_model.py` | 82.2% | 23 | Mock headless, testar roleNames, data(), flags() |
| `presentation/viewmodels/main_window_viewmodel.py` | 83.2% | 33 | Mock headless, testar comandos de menu, estados |
| `domain/services/allocation_service.py` | 84.9% | 51 | Testar edge cases de alocação, deadlock, idleness |
| `presentation/viewmodels/filter_proxy_model.py` | 84.6% | 9 | Mock headless, testar filterAcceptsRow edge cases |
| `presentation/viewmodels/manual_allocation_dialog_viewmodel.py` | 85.3% | 12 | Mock headless, testar validação de datas |
| `infrastructure/excel/excel_service.py` | 82.5% | 18 | Testar edge cases de export/import |

### Tier 3 — Gap Mínimo (cobertura 85-90%)

| Arquivo | Cobertura | Linhas Descobertas | Estratégia |
|---|---|---|---|
| `application/use_cases/allocation/execute_allocation.py` | 87% | 6 | Testar error paths |
| `application/use_cases/excel/import_excel_use_case.py` | 89% | 17 | Testar validação de formato inválido |
| `presentation/theme/theme.py` | 89.3% | 5 | Testar fallback de tema |
| `application/use_cases/scheduling/calculate_schedule.py` | 89.5% | 5 | Testar schedule com zero stories |
| `application/use_cases/allocation/get_developer_availability.py` | 89.5% | 6 | Testar developer sem alocações |

### Tier Viewmodel — Cobertura Muito Baixa (requer atenção especial)

| Arquivo | Cobertura | Linhas Descobertas | Estratégia |
|---|---|---|---|
| `presentation/viewmodels/excel_viewmodel.py` | 27.6% | 77 | Mock headless completo, testar import/export flows, error handling |
| `presentation/viewmodels/schedule_viewmodel.py` | 37.7% | 31 | Mock headless, testar load/refresh/error states |
| `presentation/viewmodels/dependency_dialog_viewmodel.py` | 46.9% | 54 | Mock headless, testar add/remove/validate dependencies |

### Alternatives Considered

1. **Modificar código de produção para injetar seams de teste**: Rejeitado — viola constraint FR-007. Apenas ajustes mínimos de testabilidade quando estritamente necessário.
2. **Usar pytest-qt com display real**: Rejeitado — viola constraint FR-005 (headless). Mocks headless são suficientes para viewmodels.
3. **Ignorar viewmodels com cobertura < 50%**: Rejeitado — viewmodels contêm lógica de apresentação significativa que deve ser validada.

---

## R3. Garantia de new_coverage >= 80% no Quality Gate

### Decision
Todos os novos arquivos de teste devem ser auto-suficientes e não precisam de cobertura adicional (são arquivos de teste, excluídos da contagem). O foco é garantir que qualquer código de produção novo ou modificado tenha >= 80% de cobertura.

### Rationale
- O Quality Gate do SonarQube verifica `new_coverage` (cobertura de código novo) com threshold de 80%.
- Esta feature não adiciona código de produção novo — apenas configuração e testes.
- Se algum ajuste mínimo de testabilidade for necessário em código de produção, ele deve ser coberto pelos próprios testes que motivaram o ajuste.

### Alternatives Considered
Nenhuma — a abordagem é direta e não requer decisões alternativas.

---

## R4. Padrões de Teste Existentes no Projeto

### Decision
Seguir rigorosamente os padrões já estabelecidos: markers pytest (`@pytest.mark.unit`, `@pytest.mark.integration`), fixtures do `conftest.py`, factories do `factories.py`, e headless mocks do `headless_mocks.py`.

### Rationale
- O projeto já possui infraestrutura madura de testes com 74 arquivos de teste.
- `conftest.py` fornece fixtures para `temp_db_path`, `db_connection`, `uow`, `container` com suporte async.
- `factories.py` fornece builders para DTOs e objetos de domínio.
- `headless_mocks.py` fornece mocks PySide6 para testes sem display.
- `pytest-asyncio` com `asyncio_mode = "auto"` elimina necessidade de decorar cada teste async.

### Alternatives Considered
1. **Criar nova infraestrutura de mocks**: Rejeitado — a infraestrutura existente é suficiente e madura.
2. **Usar monkeypatch ao invés de unittest.mock**: Ambos são válidos; preferir `unittest.mock` para consistência com testes existentes, usando `monkeypatch` apenas quando mais simples (environment variables, etc.).
