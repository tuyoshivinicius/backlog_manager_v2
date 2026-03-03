# Prompt: Criar Especificacao Tecnica do EP-009

<role>
Voce e um Arquiteto de Software Senior especializado em integracao de sistemas e
processamento de arquivos, com profundo conhecimento em:
- Integracao com Microsoft Excel via openpyxl (leitura e escrita de .xlsx)
- Domain Services para validacao e transformacao de dados em lote
- Application Layer com Use Cases, DTOs (Pydantic) e coordenacao transacional
- Operacoes I/O assincronas em Python (aiofiles, aiosqlite)
- Clean Architecture com separacao de responsabilidades Infrastructure vs Application
- Estrategias de processamento em lote: validacao previa, rollback, two-pass processing
- Tratamento de erros em operacoes de importacao/exportacao com feedback detalhado

Voce produz especificacoes tecnicas prescritivas, rastreaveis a requisitos, e implementaveis
de forma incremental sem decisoes ambiguas.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicacao desktop standalone em Python (PySide6 + SQLite) para gestao de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Tecnica (Definida em EP-001)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **UI**: PySide6 6.10.0+ com padrao MVVM (implementado em EP-008)
- **Async/Qt**: qasync para integracao asyncio <-> Qt event loop
- **Persistencia**: aiosqlite (async SQLite)
- **DTOs**: Pydantic
- **Excel**: openpyxl (ainda NAO declarado em pyproject.toml — ver conflito #1)
- **Testes**: pytest + pytest-cov + pytest-asyncio + pytest-qt
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation -> Infrastructure -> Application -> Domain
- **Padroes**: Repository Pattern (Protocol), Unit of Work, DDD (entidades ricas, VOs, servicos de dominio), MVVM (na Presentation)

### Estado Atual do Codigo (Implementado em EP-001 a EP-008)

O produto atingiu estado de **MVP** com EP-008. Todas as capacidades core (Backlog, Features, Desenvolvedores, Dependencias, Cronograma, Alocacao, Interface Grafica) estao implementadas. EP-009 adiciona a **capacidade de integracao Excel** para import/export de dados, servindo tambem como mecanismo de backup manual.

**Entidades existentes (dominio):**
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com id (str, formato COMPONENTE-NNN), component, name, story_points, priority, status, duration (int | None), start_date (date | None), end_date (date | None), developer_id (int | None), feature_id (int | None).
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com id (auto-increment, int | None), name (max 100, nao vazio).
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com name (max 100, unico, nao vazio), wave (int > 0), id (auto-increment, int | None).

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com estados do workflow (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)
- `src/backlog_manager/domain/value_objects/brazilian_holidays.py` — `BRAZILIAN_HOLIDAYS_2026_2028` (frozenset[date])

**Domain Services existentes:**
- `src/backlog_manager/domain/services/story_service.py` — `StoryService` com `create_story()` (geracao de ID formato COMPONENTE-NNN)
- `src/backlog_manager/domain/services/developer_service.py` — `DeveloperService` com `create_developer()`
- `src/backlog_manager/domain/services/feature_service.py` — `FeatureService` com `create_feature()`
- `src/backlog_manager/domain/services/dependency_service.py` — `DependencyService` com `build_graph()`, `would_create_cycle()`, `validate_wave_dependency()` (sincrono)
- `src/backlog_manager/domain/services/scheduling_service.py` — `SchedulingService` com `calculate_duration()`, `topological_sort()`, `calculate_story_dates()`, etc. (sincrono)
- `src/backlog_manager/domain/services/allocation_service.py` — `AllocationService` com `allocate_stories()` (sincrono, recebe dados como parametros, retorna `AllocationResult`)

**Excecoes existentes:**
- `src/backlog_manager/domain/exceptions/base.py` — `BacklogManagerException`
- `src/backlog_manager/domain/exceptions/allocation.py` — `AllocationException`, `MaxIterationsExceeded`
- `src/backlog_manager/domain/exceptions/dependency.py` — `CyclicDependencyException`, `InvalidWaveDependencyException`
- `src/backlog_manager/domain/exceptions/feature.py` — `DuplicateWaveException`, `FeatureHasStoriesException`
- `src/backlog_manager/domain/exceptions/warnings.py` — `BacklogWarning`, `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo`

**Repository Protocols existentes (em `src/backlog_manager/domain/interfaces/repositories.py`):**
- `StoryRepository(Protocol)` — add, get_by_id, get_all, get_by_status, get_by_developer, get_by_feature, update, delete, exists, get_max_id_number, get_max_priority, get_by_priority, count_by_developer
- `StoryDependencyRepository(Protocol)` — add, remove, get_dependencies, get_dependents, exists, get_all_dependencies, remove_all_for_story
- `DeveloperRepository(Protocol)` — add, get_by_id, get_all, update, delete, exists
- `FeatureRepository(Protocol)` — add, get_by_id, get_by_wave, get_all, update, delete, exists, has_stories, get_by_name
- `UnitOfWork(Protocol)` — stories, developers, features, dependencies, commit, rollback, __aenter__, __aexit__

**Implementacoes SQLite existentes (infrastructure):**
- `src/backlog_manager/infrastructure/database/repositories/story_repository.py`
- `src/backlog_manager/infrastructure/database/repositories/developer_repository.py`
- `src/backlog_manager/infrastructure/database/repositories/feature_repository.py`
- `src/backlog_manager/infrastructure/database/repositories/story_dependency_repository.py`
- `src/backlog_manager/infrastructure/database/unit_of_work.py` — `SQLiteUnitOfWork`

**Use Cases existentes (23+ use cases em application/use_cases/):**
- Story: CreateStory, EditStory, DeleteStory, DuplicateStory, ListStories, MovePriority, AssignDeveloper
- Developer: CreateDeveloper, UpdateDeveloper, DeleteDeveloper, ListDevelopers
- Feature: CreateFeature, UpdateFeature, DeleteFeature, ListFeatures
- Dependency: AddDependency, RemoveDependency, GetDependencies, GetDependents
- Scheduling: CalculateDuration, CalculateStoryDates, CalculateSchedule
- Allocation: ExecuteAllocation

**DTOs Pydantic existentes (22+ DTOs em application/dto/):**
- Story: CreateStoryDTO, EditStoryDTO, StoryOutputDTO
- Developer: CreateDeveloperDTO, UpdateDeveloperDTO, DeleteDeveloperDTO, DeveloperOutputDTO, ListDevelopersDTO
- Feature: CreateFeatureDTO, FeatureOutputDTO, ListFeaturesDTO, UpdateFeatureDTO
- Dependency: AddDependencyDTO, GetDependencyDTO, RemoveDependencyDTO
- Scheduling: CalculateDurationDTO, CalculateScheduleDTO, CalculateStoryDatesDTO
- Allocation: ExecuteAllocationInputDTO, ExecuteAllocationOutputDTO, AllocationMetricsDTO

**Camada de Presentation (implementada em EP-008):**
- `src/backlog_manager/presentation/app.py` — entry point com QApplication + qasync
- `src/backlog_manager/presentation/container.py` — DIContainer para injecao de dependencias
- `src/backlog_manager/presentation/viewmodels/` — ViewModels para tabela de backlog, dialogos, painel de alocacao
- `src/backlog_manager/presentation/views/` — MainWindow, StoryDialog, DeveloperDialog, FeatureDialog, DependencyPanel, etc.

**Diretorio infrastructure/excel (NAO EXISTE — EP-009 deve criar):**
- `src/backlog_manager/infrastructure/excel/` — diretorio a ser criado com servicos de leitura/escrita Excel

**Atalhos de teclado definidos em EP-008 mas NAO implementados (reservados para EP-009):**
- Ctrl+I: Importar Excel
- Ctrl+E: Exportar Excel

### Conflitos e Lacunas Conhecidos

Estes pontos DEVEM ser resolvidos na especificacao com decisao explicita:

1. **openpyxl como dependencia**: A Constituicao §VI lista `openpyxl` como dependencia obrigatoria para Excel, mas NAO esta declarado no `pyproject.toml` atual. -> A spec deve incluir adicao de `openpyxl>=3.1.0` em `[tool.poetry.dependencies]`. Considerar se deve usar `aiofiles` para wrap async ou se openpyxl pode ser chamado em thread separada.

2. **Localizacao do servico Excel na arquitetura**: Clean Architecture define Infrastructure como camada de I/O. -> A spec deve decidir se (a) criar `infrastructure/excel/excel_service.py` com interface em `application/interfaces/excel_service.py` (Protocol), (b) criar apenas implementacao concreta em infrastructure sem abstraction, ou (c) usar servico diretamente no use case. Considerar que Excel e dependencia externa (framework) e deve ser isolado.

3. **Geracao de ID para linhas sem ID no import**: UC-004 passo 6a diz "Se ID vazio: gera no formato 'US-NNN'". O `StoryService.generate_story_id()` existente gera IDs no formato "COMPONENTE-NNN" usando o campo component da historia. -> A spec deve definir se (a) usar formato "US-NNN" fixo para IDs gerados no import (diferente do padrao interno), (b) usar o campo Componente do Excel para gerar ID no formato "COMPONENTE-NNN" (consistente com sistema), ou (c) criar campo Componente obrigatorio no Excel e rejeitar linhas sem Componente. Documentar qual formato prevalece.

4. **Processamento em duas passadas para dependencias**: O epic menciona "Processar em duas passadas: criar historias, depois dependencias" porque dependencias referenciam IDs que podem ainda nao existir durante a leitura da primeira linha. -> A spec deve detalhar o algoritmo: (a) primeira passada le todas as linhas e cria historias com IDs; (b) segunda passada adiciona dependencias usando IDs ja criados. Considerar rollback completo se ciclo for detectado na segunda passada.

5. **Validacao de ciclos no import vs. no dominio**: RF-EXCEL-005 exige validar ciclos no conjunto importado. O `DependencyService.would_create_cycle()` existente valida uma dependencia de cada vez contra o grafo atual. -> A spec deve decidir se (a) construir grafo temporario com todas as dependencias do arquivo e validar ciclo antes de persistir, (b) adicionar dependencias uma a uma e rollback se ciclo detectado (ineficiente), ou (c) criar novo metodo em DependencyService para validacao em lote. Considerar performance com 500 historias.

6. **Features criadas automaticamente no import**: UC-004 passo 6c diz "Cria ou associa Feature". O Excel tem coluna "Feature" com nome da feature. Se feature nao existe, deve ser criada. -> A spec deve definir: (a) qual wave atribuir a features criadas automaticamente (wave=1 padrao? wave derivado da posicao no arquivo?), (b) se deve usar `FeatureService.create_feature()` ou criar diretamente via repositorio, (c) como tratar conflito de wave se multiplas features forem criadas.

7. **Formato exato das colunas do Excel**: UC-004 lista headers "ID, Componente, Nome, SP, Feature, Dependencias" nesta ordem, case-sensitive. -> A spec deve especificar: (a) formato exato de cada coluna (tipos, valores permitidos), (b) como interpretar coluna "Dependencias" (IDs separados por virgula? ponto-e-virgula?), (c) se colunas adicionais devem ser ignoradas ou causar erro.

8. **SP invalido — skip vs. abort**: UC-004 FA-2 diz "SP invalido em linha N: sistema registra warning e pula linha". Isso significa que import parcial e permitido (algumas linhas importadas, outras puladas)? -> A spec deve definir se (a) import parcial com warnings e aceitavel, (b) qualquer erro invalida todo o arquivo, ou (c) usuario escolhe comportamento antes de importar. Considerar que ciclo detectado (FA-4) rejeita arquivo inteiro.

9. **Dependencia inexistente no arquivo vs. no sistema**: UC-004 FA-3 diz "Dependencia inexistente: warning (dependencia ignorada)". Isso se refere a ID de dependencia que nao esta no arquivo ou que nao existe no sistema apos import? -> A spec deve clarificar: (a) se import e incremental (adiciona ao backlog existente) ou substitutivo (limpa e recarrega), (b) se dependencia pode referenciar ID ja existente no sistema (nao presente no arquivo), (c) comportamento se ID da dependencia nao for encontrado em nenhum lugar.

10. **Export — escopo e formato de saida**: RF-EXCEL-006 e RF-EXCEL-007 mencionam exportar historias, desenvolvedores e features. -> A spec deve definir: (a) se gera arquivo unico com multiplas abas (Stories, Developers, Features) ou arquivos separados, (b) quais colunas exportar para cada entidade, (c) como representar dependencias na exportacao (coluna com IDs separados por virgula?), (d) se export inclui apenas dados ativos ou historico completo.

11. **Roundtrip — garantia de fidelidade**: Criterio de aceite diz "arquivo exportado, quando reimportado em instalacao limpa, restaura todos os dados". -> A spec deve garantir que o formato de export seja 100% compativel com o formato de import. Considerar: (a) IDs devem ser preservados na exportacao (nao regenerados), (b) wave das features deve ser incluido no export, (c) status das historias deve ser exportado.

12. **Feedback visual durante operacoes**: Import/export de 500 historias pode levar alguns segundos. -> A spec deve definir integracao com ViewModels existentes: (a) QProgressDialog com percentual de linhas processadas, (b) log de warnings/erros para exibicao ao usuario, (c) opcao de cancelar operacao em andamento.

13. **Limite de 500 historias**: O epic menciona "Limite de 500 historias com warning (RNF-PERF-001)" para arquivos muito grandes. -> A spec deve definir: (a) se limite e bloqueante ou apenas warning, (b) se contagem e do arquivo ou do total no sistema apos import, (c) se usuario pode forcar import alem do limite.

14. **Confirmacao antes de sobrescrever arquivo no export**: O epic menciona "Confirmar antes de sobrescrever". -> A spec deve definir: (a) se verificacao de arquivo existente fica na View (dialogo de arquivo padrao do sistema ja faz isso) ou na ViewModel, (b) se deve exibir QMessageBox adicional alem do dialogo do sistema.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificacao:

1. **Epico fonte**: `docs/epics/EP-009_integracao-excel.md` — requisitos, escopo, criterios de aceite, riscos e premissas
2. **SRS completo**: `srs.md` — secoes §2.2 item 7 (Integracao Excel), §2.4 (Restricoes, openpyxl), §5 UC-004 (Importar Backlog do Excel - fluxo completo e fluxos alternativos), §4.4 RNF-SEG-002 (Backup Manual)
3. **Constituicao do projeto**: `.specify/memory/constitution.md` — principios obrigatorios: §I Clean Architecture (Infrastructure layer para I/O), §VI Packaging & Distribution (openpyxl como dependencia), §VII Estrutura de Diretorios (infrastructure/excel/), §VIII Programacao Assincrona, §XVI Tratamento de Erros, §XX Validacao e Sanitizacao de Entrada
4. **Spec de referencia (predecessor)**: `specs/008-ep008-graphical-interface/spec.md` — formato, nivel de detalhe e padrao de User Stories/Acceptance Scenarios esperado
5. **StoryService existente**: `src/backlog_manager/domain/services/story_service.py` — `generate_story_id()` para entender formato de ID
6. **DependencyService existente**: `src/backlog_manager/domain/services/dependency_service.py` — `build_graph()`, `would_create_cycle()` para validacao de ciclos
7. **FeatureService existente**: `src/backlog_manager/domain/services/feature_service.py` — `create_feature()` para criacao de features no import
8. **Repository Protocols**: `src/backlog_manager/domain/interfaces/repositories.py` — todas as interfaces que os Use Cases de import/export irao consumir
9. **UnitOfWork SQLite**: `src/backlog_manager/infrastructure/database/unit_of_work.py` — para coordenacao transacional no import
10. **CreateStoryDTO**: `src/backlog_manager/application/dto/story/create_story_dto.py` — formato de criacao de historia
11. **StoryOutputDTO**: `src/backlog_manager/application/dto/story/story_output_dto.py` — formato de saida para export
12. **DeveloperOutputDTO**: `src/backlog_manager/application/dto/developer/developer_output_dto.py` — formato para export de desenvolvedores
13. **FeatureOutputDTO**: `src/backlog_manager/application/dto/feature/feature_output_dto.py` — formato para export de features
14. **MainWindow e ViewModels existentes**: `src/backlog_manager/presentation/views/` e `src/backlog_manager/presentation/viewmodels/` — para integracao dos botoes Import/Export e atalhos Ctrl+I/Ctrl+E
15. **DIContainer**: `src/backlog_manager/presentation/container.py` — para adicionar novos Use Cases de import/export
16. **pyproject.toml**: para adicionar dependencia openpyxl
</input>

<task>
Crie a **especificacao tecnica completa** para o epico `EP-009 — Integracao Excel`.

A especificacao deve cobrir **exclusivamente** o escopo do epico: implementar a capacidade de importacao e exportacao de dados via arquivos Excel (.xlsx), servindo tambem como mecanismo de backup manual.

**Requisitos Funcionais a especificar:**

| ID | Nome | Descricao |
|----|------|-----------|
| RF-EXCEL-001 | Importar Arquivo Excel | Ler arquivo .xlsx com formato definido e criar historias no sistema |
| RF-EXCEL-002 | Validar Headers Obrigatorios | Verificar presenca de colunas ID, Componente, Nome, SP, Feature, Dependencias |
| RF-EXCEL-003 | Gerar ID Automatico no Import | Gerar ID no formato correto para linhas sem ID |
| RF-EXCEL-004 | Criar/Associar Features no Import | Criar features referenciadas que nao existem; associar historias a features |
| RF-EXCEL-005 | Validar Ciclos no Import | Detectar ciclos de dependencia no conjunto importado e rejeitar arquivo |
| RF-EXCEL-006 | Exportar Backlog para Excel | Gerar arquivo .xlsx com todas as historias do backlog |
| RF-EXCEL-007 | Exportar Desenvolvedores e Features | Incluir desenvolvedores e features na exportacao |

**Requisitos Nao-Funcionais criticos:**

| ID | Nome | Metrica |
|----|------|---------|
| RNF-SEG-002 | Backup Manual | Export inclui todas as entidades; import restaura sistema integralmente |

**Artefatos a especificar:**

| Artefato | Descricao |
|----------|-----------|
| ExcelService (Infrastructure) | Servico de leitura/escrita de arquivos Excel via openpyxl |
| ExcelServiceProtocol (Application) | Interface para o servico Excel (inversao de dependencia) |
| ImportExcelUseCase | Use case para importacao completa (validacao, criacao, dependencias) |
| ExportExcelUseCase | Use case para exportacao completa (historias, devs, features) |
| ImportExcelDTO | DTO com resultado do import (historias criadas, warnings, erros) |
| ExportExcelDTO | DTO com parametros do export (path do arquivo) |
| Integracao com ViewModels | Implementacao dos atalhos Ctrl+I e Ctrl+E; botoes na toolbar |
| pyproject.toml update | Adicao de openpyxl como dependencia |

**Caso de uso do SRS que fica completo apos este epico:**
- UC-004: Importar Backlog do Excel — fluxo principal e todos os fluxos alternativos

**Cenarios de teste criticos:**
- Import de arquivo valido com N historias
- Rejeicao de arquivo com header ausente (FA-1)
- Warning e skip de linha com SP invalido (FA-2)
- Warning para dependencia inexistente (FA-3)
- Rejeicao de arquivo com ciclo (FA-4)
- Roundtrip: export seguido de import em DB limpo restaura dados identicos

**IMPORTANTE**: Este epico **cria** a camada de integracao Excel na Infrastructure e os Use Cases correspondentes na Application. Ele **reutiliza** as entidades, services e repositorios existentes (EP-001 a EP-007) e **integra** com a UI existente (EP-008) adicionando os botoes/atalhos de import e export.
</task>

<rules>
### Regras de Qualidade da Especificacao

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF-EXCEL do epico
   EP-009. Todo RF do escopo deve ter pelo menos um FR correspondente. Incluir matriz de
   rastreabilidade: FR <-> RF-EXCEL <-> UC-004.

2. **Codigo existente prevalece como baseline**: Nao redefinir entidades, value objects,
   excecoes, repositorios ou services de dominio ja implementados em EP-001 a EP-008.
   Especificar apenas **novos artefatos** (ExcelService, Use Cases de import/export, DTOs)
   e **extensoes** a ViewModels existentes para integracao de UI.

3. **Conflitos resolvidos explicitamente**: Para cada conflito/lacuna listado na secao
   `Conflitos e Lacunas Conhecidos` do contexto, a spec deve conter uma secao
   "Decisao Arquitetural" (ADR) com: Contexto, Opcoes, Decisao, Justificativa.

4. **Separacao de responsabilidades clara**: Definir com precisao o que fica em cada camada:
   - **Infrastructure (ExcelService)**: Leitura/escrita de arquivo Excel via openpyxl. Sem logica de negocio.
   - **Application (Use Cases)**: Coordenacao de ExcelService + UnitOfWork + Services. Validacao de formato.
   - **Domain (Services existentes)**: Validacao de ciclos (DependencyService), geracao de IDs (StoryService).
   - **Presentation (ViewModels)**: Integracao com botoes/atalhos, feedback visual, dialogo de arquivo.

5. **Formato de arquivo Excel especificado**: Detalhar exatamente:
   - Headers obrigatorios e ordem das colunas
   - Formato de cada coluna (string, numero, lista separada por virgula)
   - Tratamento de celulas vazias ou invalidas
   - Encoding e compatibilidade com Microsoft Excel 2016+

6. **Algoritmo de import em duas passadas**: Especificar:
   - Passada 1: Ler todas as linhas, validar headers, criar Stories (sem dependencias), criar Features
   - Passada 2: Processar coluna Dependencias, validar ciclos no grafo completo, adicionar dependencias
   - Rollback: Se ciclo detectado ou erro critico, desfazer todas as operacoes

7. **Mensagens de erro e warnings exatas**: Toda validacao deve especificar a mensagem de erro
   literal em portugues (sem acentos no codigo, conforme §8.2 do SRS). Categorizar entre:
   - Erros fatais (header ausente, ciclo) -> aborta import, exibe mensagem
   - Warnings (SP invalido, dependencia inexistente) -> registra, continua import, exibe resumo

8. **Testabilidade**: Cada FR deve ser verificavel por um teste unitario ou de integracao
   especifico. A spec deve incluir exemplos de arquivos Excel de teste (estrutura, conteudo).
   ExcelService deve ser mockavel para testes unitarios dos Use Cases.

9. **Sem sobreposicao com EP-001 a EP-008**: Nao re-especificar entidades, services, repositorios
   ou componentes de UI ja implementados. Especificar apenas a integracao (botoes, atalhos,
   chamadas de Use Case) e os novos artefatos de Excel.

10. **Consistencia de nomenclatura**: Usar os mesmos nomes de classe, metodo e campo ja
    existentes no codigo. Use Cases de import/export devem seguir padrao dos use cases existentes
    (async, UnitOfWork, DTOs Pydantic).

11. **Operacoes assincronas**: Use cases de import/export devem ser `async`. O ExcelService
    pode usar `aiofiles` para wrap de operacoes de I/O ou executar openpyxl em thread pool
    via `asyncio.to_thread()` para nao bloquear o event loop.

12. **Integridade transacional**: Import deve usar UnitOfWork para garantir atomicidade.
    Se ciclo for detectado na passada 2 ou qualquer erro critico ocorrer, rollback completo.
    Export e operacao read-only (nao precisa de transacao).

13. **Performance com 500 historias**: Import e export devem funcionar com arquivos de
    ate 500 historias em tempo razoavel (< 10s). Especificar estrategias de otimizacao
    se necessario (bulk insert, lazy loading).

14. **Roundtrip garantido**: O formato de export deve ser 100% compativel com o formato de
    import. Especificar quais campos sao exportados e como sao formatados para garantir
    que um arquivo exportado pode ser reimportado sem perda de dados.

15. **Integracao com UI existente**: Especificar:
    - Implementacao dos atalhos Ctrl+I (import) e Ctrl+E (export) reservados em EP-008
    - Botoes na toolbar da MainWindow (se nao existirem, especificar adicao)
    - Dialogo de selecao de arquivo (QFileDialog)
    - Feedback visual durante operacao (progress dialog ou statusbar)
    - Exibicao de resumo apos import (N historias importadas, M warnings)

16. **Extensao do DIContainer**: Os novos Use Cases (ImportExcel, ExportExcel) devem ser
    registrados no DIContainer existente. Especificar o grafo de dependencias completo.
</rules>
