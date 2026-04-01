# Feature Description: Cobertura de Testes 90% e Quality Gate SonarQube

## Entrada para `/speckit.specify`

```text
Alinhar configuração de cobertura do SonarQube com pytest-cov e aumentar cobertura de testes para atingir 90% no código total, corrigindo o Quality Gate que atualmente falha.

CONTEXTO E PROBLEMA:
O Quality Gate do SonarQube está falhando porque a cobertura de novo código (new_coverage) está em 79.4%, abaixo do threshold de 80%. A cobertura total do projeto reportada pelo SonarQube é 56.7% (3,886 de 7,289 linhas cobertas). Porém, a cobertura local (pytest-cov) já atinge ~94% porque exclui corretamente arquivos que não são testáveis unitariamente (views PySide6, delegates, interfaces abstratas, __init__.py, app.py, __main__.py, constants.py). O SonarQube não possui essas mesmas exclusões em sonar.coverage.exclusions, criando uma divergência significativa entre as métricas locais e as do CI.

DADOS ATUAIS DO SONARQUBE:
- Cobertura total: 56.7%
- Cobertura de novo código: 79.4% (threshold: 80%)
- Linhas a cobrir: 7,289
- Linhas descobertas: 3,403
- Bugs: 0, Vulnerabilidades: 0, Code Smells: 0
- Duplicação: 0%

DISTRIBUIÇÃO DAS LINHAS DESCOBERTAS:
- ~2,838 linhas (83%) são de presentation/views/ (PySide6 widgets com 0% cobertura)
- ~158 linhas (5%) são de presentation/delegates/ (delegates Qt com 0% cobertura)
- ~80 linhas são de presentation/app.py (entry point Qt)
- ~88 linhas são de domain/interfaces/ (classes abstratas/contratos)
- ~100 linhas são de __init__.py (re-exports de módulos)
- ~139 linhas (~4%) são de código parcialmente coberto que pode receber testes adicionais

EXCLUSÕES JÁ CONFIGURADAS NO PYTEST-COV (pyproject.toml):
- */tests/*
- */__init__.py
- */presentation/app.py
- */presentation/views/*.py
- */presentation/delegates/*.py
- */__main__.py
- */domain/interfaces/*.py
- */presentation/constants.py

EXCLUSÕES ATUAIS DO SONARQUBE (sonar-project.properties):
- sonar.coverage.exclusions: apenas **/tests/** e **/conftest.py (faltam as exclusões de views, delegates, interfaces etc.)

FRENTE 1 - ALINHAMENTO DE EXCLUSÕES:
Configurar sonar.coverage.exclusions no sonar-project.properties para incluir os mesmos padrões que o pytest-cov omite: views PySide6, delegates, app.py, __init__.py, __main__.py, interfaces abstratas e constants.py. Isso eliminará a divergência entre métricas locais e SonarQube. Com esse alinhamento, a cobertura SonarQube deve subir de 56.7% para aproximadamente 94%, refletindo a realidade do código testável.

FRENTE 2 - TESTES PARA CÓDIGO PARCIALMENTE COBERTO:
Adicionar testes unitários e de integração para aumentar a cobertura dos arquivos que estão abaixo de 90%, solidificando a meta. Os arquivos prioritários são:
- application/use_cases/story/edit_story.py (44.4% - 23 linhas descobertas)
- application/use_cases/story/list_stories.py (69.4% - 26 linhas descobertas)
- application/dto/story/edit_story_dto.py (69.8% - 10 linhas descobertas)
- infrastructure/logging/logger_config.py (74.1% - 10 linhas descobertas)
- domain/services/allocation_service.py (84.9% - 51 linhas descobertas)
- presentation/viewmodels/main_window_viewmodel.py (83.2% - 33 linhas descobertas)
- presentation/viewmodels/story_table_model.py (82.2% - 26 linhas descobertas)
- infrastructure/excel/excel_service.py (82.5% - 18 linhas descobertas)
- application/use_cases/excel/import_excel_use_case.py (89% - 17 linhas descobertas)
- presentation/viewmodels/filter_proxy_model.py (84.6% - 9 linhas descobertas)
- presentation/viewmodels/manual_allocation_dialog_viewmodel.py (85.3% - 12 linhas descobertas)
- application/use_cases/allocation/execute_allocation.py (87% - 6 linhas descobertas)
- presentation/theme/theme.py (89.3% - 5 linhas descobertas)
- application/use_cases/scheduling/calculate_schedule.py (89.5% - 5 linhas descobertas)
- application/use_cases/allocation/get_developer_availability.py (89.5% - 6 linhas descobertas)
- infrastructure/database/sqlite_connection.py (65.6% - 8 linhas descobertas)

FRENTE 3 - GARANTIR NEW_CODE COVERAGE >= 80%:
Assegurar que todo novo código adicionado nesta feature tenha cobertura mínima de 80% (threshold do Quality Gate), preferencialmente 90%+ para manter consistência com a meta geral.

CRITÉRIOS DE SUCESSO:
1. Quality Gate do SonarQube passa (status OK) — especialmente new_coverage >= 80%
2. Cobertura total reportada pelo SonarQube atinge >= 90%
3. Cobertura local (pytest-cov) mantém-se >= 90% (fail_under existente)
4. Exclusões do SonarQube estão alinhadas com as do pytest-cov
5. Zero regressão nos indicadores de qualidade existentes (0 bugs, 0 vulnerabilidades, 0 code smells, 0% duplicação)
6. Todos os testes novos seguem os padrões existentes do projeto (markers pytest, fixtures, factories, headless mocks para viewmodels)

RESTRIÇÕES:
- Não alterar schema do banco SQLite
- Não modificar código de produção apenas para facilitar testes (exceto ajustes mínimos de testabilidade)
- Views PySide6 e delegates continuam excluídos de cobertura (testados via QA manual)
- Manter compatibilidade com Python 3.11+
- Testes devem rodar em modo headless (sem display/servidor X)
```
