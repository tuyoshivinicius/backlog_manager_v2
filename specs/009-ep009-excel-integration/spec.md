# Feature Specification: EP-009 Integracao Excel

**Feature Branch**: `009-ep009-excel-integration`
**Created**: 2026-03-03
**Status**: Draft
**Input**: Implementacao da capacidade de integracao Excel (Import/Export) para interoperabilidade com outras ferramentas e como mecanismo de backup manual. Este epico implementa RF-EXCEL-001 a RF-EXCEL-007 e UC-004 do SRS.

## Out of Scope

- **Outros formatos de arquivo**: CSV, JSON, XML nao sao suportados (somente .xlsx via openpyxl)
- **Integracao com ferramentas externas**: Jira, Azure DevOps, etc. (conforme §1.2 do SRS)
- **Sincronizacao automatica**: Nao ha monitoramento de arquivos externos
- **Edicao inline no Excel**: Sistema importa/exporta, nao edita diretamente
- **Novos campos no dominio**: Este epico NAO altera entidades existentes (Story, Developer, Feature)

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Importar Backlog Completo do Excel (Priority: P1)

Como Scrum Master, preciso importar um backlog existente de um arquivo Excel para o sistema, para migrar dados de planilhas existentes sem redigitacao manual.

**Why this priority**: Funcionalidade core do epico - permite migracao de dados existentes e restauracao de backups. Sem import, o sistema nao oferece interoperabilidade.

**Independent Test**: Pode ser testado criando um arquivo Excel com o formato esperado (headers na linha 1: ID, Componente, Nome, SP, Feature, Dependencias), importando-o e verificando que todas as historias foram criadas corretamente no sistema.

**Acceptance Scenarios**:

1. **Given** arquivo Excel valido com 10 historias, **When** importo o arquivo, **Then** 10 historias sao criadas no sistema com todos os campos preenchidos
2. **Given** arquivo Excel com linha sem ID, **When** importo, **Then** sistema gera ID automatico no formato COMPONENTE-NNN usando o campo Componente da linha
3. **Given** arquivo Excel com Feature "Auth" nao existente, **When** importo, **Then** Feature "Auth" e criada com wave=1 e associada as historias
4. **Given** arquivo Excel com dependencias validas (B depende de A), **When** importo, **Then** dependencias sao criadas apos todas as historias serem inseridas

---

### User Story 2 - Validar Arquivo Excel na Importacao (Priority: P1)

Como Scrum Master, preciso que o sistema valide o arquivo Excel antes de importar, para evitar corrupcao de dados por arquivos malformados.

**Why this priority**: Validacao e critica para integridade do sistema - arquivos invalidos poderiam corromper o banco de dados.

**Independent Test**: Pode ser testado tentando importar arquivos com headers ausentes, SP invalido, ciclos de dependencia e verificando que o sistema rejeita ou avisa conforme esperado.

**Acceptance Scenarios**:

1. **Given** arquivo Excel sem coluna "Nome", **When** tento importar, **Then** sistema exibe erro "Coluna obrigatoria 'Nome' nao encontrada" e nao importa nenhum dado
2. **Given** arquivo Excel com SP=7 na linha 3, **When** importo, **Then** sistema registra warning "Linha 3: SP invalido (7), linha ignorada" e continua importando as demais linhas
3. **Given** arquivo Excel onde A depende de B e B depende de A, **When** tento importar, **Then** sistema exibe erro "Ciclo de dependencia detectado: A -> B -> A" e nao importa nenhum dado
4. **Given** arquivo Excel com dependencia para ID inexistente "XYZ-999", **When** importo, **Then** sistema registra warning "Linha N: Dependencia 'XYZ-999' nao encontrada, ignorada" e continua importando

---

### User Story 3 - Exportar Backlog Completo para Excel (Priority: P1)

Como Scrum Master, preciso exportar todo o backlog para um arquivo Excel, para compartilhar dados com stakeholders e criar backups manuais.

**Why this priority**: Exportacao e essencial para backup (RNF-SEG-002) e compartilhamento de dados. Junto com import, permite roundtrip completo.

**Independent Test**: Pode ser testado criando historias, desenvolvedores e features no sistema, exportando para Excel e abrindo o arquivo no Microsoft Excel para verificar o conteudo.

**Acceptance Scenarios**:

1. **Given** backlog com 20 historias, 5 desenvolvedores e 3 features, **When** exporto para Excel, **Then** arquivo .xlsx e criado com 3 abas (Stories, Developers, Features)
2. **Given** historia com dependencias A, B, C, **When** exporto, **Then** coluna "Dependencias" contem "A;B;C" (IDs separados por ponto-e-virgula)
3. **Given** arquivo de destino ja existe, **When** exporto, **Then** sistema solicita confirmacao antes de sobrescrever
4. **Given** exportacao completa, **When** abro arquivo no Excel, **Then** todas as colunas tem headers corretos e dados formatados corretamente

---

### User Story 4 - Garantir Roundtrip Export-Import (Priority: P1)

Como Scrum Master, preciso que um arquivo exportado possa ser reimportado sem perda de dados, para usar o sistema como mecanismo de backup confiavel.

**Why this priority**: RNF-SEG-002 exige que backup via export seja restauravel. Sem roundtrip garantido, backup nao e confiavel.

**Independent Test**: Pode ser testado exportando um backlog completo, limpando o banco de dados, reimportando o arquivo e verificando que todos os dados foram restaurados identicamente.

**Acceptance Scenarios**:

1. **Given** backlog com N historias exportado, **When** reimporto em instalacao limpa, **Then** todas as N historias sao restauradas com mesmos IDs, nomes, SPs e status
2. **Given** arquivo exportado com dependencias, **When** reimporto, **Then** todas as dependencias sao restauradas corretamente
3. **Given** arquivo exportado com features/waves, **When** reimporto, **Then** features sao recriadas com mesmos nomes e waves
4. **Given** arquivo exportado com desenvolvedores alocados, **When** reimporto, **Then** alocacoes sao preservadas (developer_id associado as historias)

---

### User Story 5 - Usar Atalhos de Teclado para Import/Export (Priority: P2)

Como usuario avancado, preciso usar atalhos de teclado para import (Ctrl+I) e export (Ctrl+E), para acessar funcionalidades rapidamente sem navegar por menus.

**Why this priority**: Atalhos melhoram UX mas nao sao essenciais para funcionalidade basica. Usuarios podem usar botoes na toolbar.

**Independent Test**: Pode ser testado pressionando Ctrl+I e Ctrl+E e verificando que os dialogos de arquivo sao abertos.

**Acceptance Scenarios**:

1. **Given** MainWindow aberta, **When** pressiono Ctrl+I, **Then** dialogo de selecao de arquivo para import e aberto (filtro .xlsx)
2. **Given** MainWindow aberta, **When** pressiono Ctrl+E, **Then** dialogo de salvar arquivo para export e aberto (filtro .xlsx)
3. **Given** operacao de import em andamento, **When** pressiono Ctrl+I novamente, **Then** nada acontece (operacao em curso nao e interrompida)

---

### User Story 6 - Visualizar Feedback Durante Operacoes (Priority: P2)

Como usuario, preciso ver feedback visual durante import/export de arquivos grandes, para saber que a operacao esta em andamento e seu progresso.

**Why this priority**: Feedback visual e importante para UX mas nao impede a funcionalidade basica de import/export.

**Independent Test**: Pode ser testado importando um arquivo com 100+ historias e verificando que progress dialog e exibido durante a operacao.

**Acceptance Scenarios**:

1. **Given** import de arquivo com 100 historias, **When** operacao esta em andamento, **Then** progress dialog e exibido com percentual de linhas processadas
2. **Given** operacao de export em andamento, **When** observo a interface, **Then** cursor de espera e exibido e botoes de export/import ficam desabilitados
3. **Given** import completo com 3 warnings, **When** operacao termina, **Then** sistema exibe resumo: "50 historias importadas, 3 warnings" com detalhes

---

### Edge Cases

- O que acontece quando arquivo Excel esta corrompido? Sistema exibe erro amigavel "Arquivo invalido ou corrompido" e nao tenta processar.
- O que acontece quando arquivo tem mais de 500 historias? Sistema exibe warning "Arquivo excede limite recomendado de 500 historias. Performance pode ser impactada." e permite continuar.
- O que acontece quando arquivo tem colunas adicionais alem das obrigatorias? Sistema ignora colunas extras sem erro.
- O que acontece quando celula de SP esta vazia? Sistema registra warning e pula a linha (SP e obrigatorio).
- O que acontece quando arquivo nao e .xlsx? Sistema exibe erro "Formato de arquivo nao suportado. Use .xlsx".
- O que acontece quando usuario cancela operacao de import? Sistema aborta sem persistir dados parciais (rollback completo).
- O que acontece quando usuario cancela operacao de export? Arquivo parcial nao e criado ou e removido.
- O que acontece quando nao ha permissao de escrita no diretorio de export? Sistema exibe erro claro sobre permissao de arquivo.

## Requirements *(mandatory)*

### Functional Requirements

#### Infrastructure Layer - ExcelService

- **FR-001**: Sistema DEVE implementar `ExcelService` em `src/backlog_manager/infrastructure/excel/excel_service.py` para leitura/escrita de arquivos .xlsx via openpyxl
- **FR-002**: ExcelService DEVE implementar metodo `read_stories_from_file(file_path: Path) -> ExcelReadResult` que retorna lista de dicionarios com dados das linhas e lista de warnings
- **FR-003**: ExcelService DEVE implementar metodo `write_workbook(file_path: Path, data: ExcelExportData) -> None` que cria arquivo Excel com multiplas abas
- **FR-004**: ExcelService DEVE executar operacoes de I/O via `asyncio.to_thread()` para nao bloquear o event loop Qt
- **FR-005**: ExcelService DEVE validar que arquivo tem extensao .xlsx antes de processar
- **FR-006**: ExcelService DEVE capturar excecoes de openpyxl e converter em excecoes de aplicacao com mensagens claras

#### Application Layer - ExcelServiceProtocol

- **FR-010**: Sistema DEVE implementar `ExcelServiceProtocol(Protocol)` em `src/backlog_manager/application/interfaces/excel_service.py` para inversao de dependencia
- **FR-011**: ExcelServiceProtocol DEVE definir assinaturas de `read_stories_from_file` e `write_workbook` como metodos async

#### Application Layer - ImportExcelUseCase

- **FR-020**: Sistema DEVE implementar `ImportExcelUseCase` em `src/backlog_manager/application/use_cases/excel/import_excel_use_case.py`
- **FR-021**: ImportExcelUseCase DEVE receber `UnitOfWork` e `ExcelService` no construtor
- **FR-022**: ImportExcelUseCase DEVE validar headers obrigatorios na primeira linha: ID, Componente, Nome, SP, Feature, Dependencias (nesta ordem, case-sensitive)
- **FR-023**: ImportExcelUseCase DEVE processar arquivo em duas passadas: (1) criar historias e features, (2) adicionar dependencias
- **FR-024**: ImportExcelUseCase DEVE gerar ID automatico no formato COMPONENTE-NNN quando coluna ID estiver vazia, usando o valor da coluna Componente
- **FR-025**: ImportExcelUseCase DEVE validar SP contra valores permitidos (3, 5, 8, 13) e registrar warning para linhas invalidas
- **FR-026**: ImportExcelUseCase DEVE criar Features automaticamente com wave=1 quando referenciadas mas inexistentes
- **FR-027**: ImportExcelUseCase DEVE interpretar coluna Dependencias como IDs separados por ponto-e-virgula (;)
- **FR-028**: ImportExcelUseCase DEVE validar ciclos de dependencia no conjunto importado usando DependencyService.build_graph e detect_cycle
- **FR-029**: ImportExcelUseCase DEVE executar rollback completo se ciclo for detectado ou header ausente
- **FR-030**: ImportExcelUseCase DEVE permitir import parcial com warnings para erros nao-criticos (SP invalido, dependencia inexistente)
- **FR-031**: ImportExcelUseCase DEVE retornar `ImportExcelOutputDTO` com contagem de historias importadas, lista de warnings e lista de erros
- **FR-032**: ImportExcelUseCase DEVE ignorar linhas com ID ja existente no banco de dados, registrando warning "Linha [N]: ID '[ID]' ja existe, linha ignorada"

#### Application Layer - ExportExcelUseCase

- **FR-040**: Sistema DEVE implementar `ExportExcelUseCase` em `src/backlog_manager/application/use_cases/excel/export_excel_use_case.py`
- **FR-041**: ExportExcelUseCase DEVE receber `UnitOfWork` e `ExcelService` no construtor
- **FR-042**: ExportExcelUseCase DEVE exportar todas as historias na aba "Stories" com colunas: ID, Componente, Nome, SP, Status, Feature, Dependencias, Desenvolvedor, Data Inicio, Data Fim
- **FR-043**: ExportExcelUseCase DEVE exportar todos os desenvolvedores na aba "Developers" com colunas: ID, Nome
- **FR-044**: ExportExcelUseCase DEVE exportar todas as features na aba "Features" com colunas: ID, Nome, Wave
- **FR-045**: ExportExcelUseCase DEVE formatar coluna Dependencias como IDs separados por ponto-e-virgula (;)
- **FR-046**: ExportExcelUseCase DEVE incluir nome do desenvolvedor (nao apenas ID) na coluna Desenvolvedor para legibilidade
- **FR-047**: ExportExcelUseCase DEVE incluir nome da feature (nao apenas ID) na coluna Feature para legibilidade
- **FR-048**: ExportExcelUseCase DEVE retornar `ExportExcelOutputDTO` com caminho do arquivo criado e contagem de entidades exportadas

#### Application Layer - DTOs

- **FR-050**: Sistema DEVE implementar `ImportExcelInputDTO` com campo `file_path: Path`
- **FR-051**: Sistema DEVE implementar `ImportExcelOutputDTO` com campos: `stories_imported: int`, `features_created: int`, `warnings: list[str]`, `errors: list[str]`
- **FR-052**: Sistema DEVE implementar `ExportExcelInputDTO` com campo `file_path: Path`
- **FR-053**: Sistema DEVE implementar `ExportExcelOutputDTO` com campos: `file_path: Path`, `stories_exported: int`, `developers_exported: int`, `features_exported: int`
- **FR-054**: Sistema DEVE implementar `ExcelReadResult` (dataclass ou Pydantic) com: `rows: list[dict[str, Any]]`, `warnings: list[str]`
- **FR-055**: Sistema DEVE implementar `ExcelExportData` (dataclass ou Pydantic) com: `stories: list[dict]`, `developers: list[dict]`, `features: list[dict]`

#### Presentation Layer - ViewModels

- **FR-060**: Sistema DEVE implementar `ExcelViewModel(QObject)` em `src/backlog_manager/presentation/viewmodels/excel_viewmodel.py`
- **FR-061**: ExcelViewModel DEVE emitir signals: `import_started`, `import_completed(ImportExcelOutputDTO)`, `import_error(str)`, `export_started`, `export_completed(ExportExcelOutputDTO)`, `export_error(str)`, `progress_updated(int)` (percentual 0-100)
- **FR-062**: ExcelViewModel DEVE implementar metodo async `import_from_file(file_path: Path)` que coordena ImportExcelUseCase
- **FR-063**: ExcelViewModel DEVE implementar metodo async `export_to_file(file_path: Path)` que coordena ExportExcelUseCase
- **FR-064**: ExcelViewModel DEVE capturar excecoes e emitir signal de erro em vez de propagar

#### Presentation Layer - UI Integration

- **FR-070**: MainWindow DEVE adicionar botoes "Importar Excel" e "Exportar Excel" na toolbar
- **FR-071**: Sistema DEVE implementar atalho Ctrl+I para abrir dialogo de import
- **FR-072**: Sistema DEVE implementar atalho Ctrl+E para abrir dialogo de export
- **FR-073**: Sistema DEVE usar QFileDialog para selecao de arquivo no import (filtro: "Arquivos Excel (*.xlsx)")
- **FR-074**: Sistema DEVE usar QFileDialog para definir arquivo de destino no export (filtro: "Arquivos Excel (*.xlsx)")
- **FR-075**: Sistema DEVE exibir QProgressDialog durante operacoes de import/export com mensagem apropriada
- **FR-076**: Sistema DEVE desabilitar botoes de import/export durante operacao em andamento
- **FR-077**: Sistema DEVE exibir QMessageBox com resumo apos import (historias importadas, warnings)
- **FR-078**: Sistema DEVE exibir QMessageBox de confirmacao antes de sobrescrever arquivo existente no export
- **FR-079**: Sistema DEVE atualizar tabela de backlog automaticamente apos import bem-sucedido

#### DIContainer Extension

- **FR-080**: DIContainer DEVE registrar `ExcelService` como dependencia
- **FR-081**: DIContainer DEVE implementar factory `create_import_excel_use_case(uow: SQLiteUnitOfWork) -> ImportExcelUseCase`
- **FR-082**: DIContainer DEVE implementar factory `create_export_excel_use_case(uow: SQLiteUnitOfWork) -> ExportExcelUseCase`
- **FR-083**: DIContainer DEVE expor property `excel_viewmodel -> ExcelViewModel`

#### pyproject.toml Update

- **FR-090**: Sistema DEVE adicionar `openpyxl = "^3.1.0"` em `[tool.poetry.dependencies]`

#### Tratamento de Erros

- **FR-100**: Erro de header ausente DEVE exibir mensagem: "Coluna obrigatoria '[NOME]' nao encontrada na linha 1"
- **FR-101**: Erro de SP invalido DEVE registrar warning: "Linha [N]: Story Points invalido ([VALOR]), linha ignorada"
- **FR-102**: Erro de ciclo DEVE exibir mensagem: "Ciclo de dependencia detectado: [CAMINHO]. Nenhum dado foi importado"
- **FR-103**: Erro de dependencia inexistente DEVE registrar warning: "Linha [N]: Dependencia '[ID]' nao encontrada, ignorada"
- **FR-104**: Erro de arquivo corrompido DEVE exibir mensagem: "Arquivo invalido ou corrompido. Verifique o formato"
- **FR-105**: Erro de permissao DEVE exibir mensagem: "Sem permissao para [ler/escrever] arquivo. Verifique permissoes"

#### Formato do Arquivo Excel

- **FR-110**: Headers obrigatorios para import (aba Stories, linha 1): ID | Componente | Nome | SP | Feature | Dependencias
- **FR-111**: Coluna ID aceita valores vazios (sistema gera automaticamente)
- **FR-112**: Coluna Componente deve conter texto nao vazio para linhas sem ID
- **FR-113**: Coluna Nome deve conter texto nao vazio
- **FR-114**: Coluna SP deve conter numero inteiro (3, 5, 8 ou 13)
- **FR-115**: Coluna Feature pode estar vazia (historia sem feature)
- **FR-116**: Coluna Dependencias pode estar vazia ou conter IDs separados por ponto-e-virgula (;)
- **FR-116a**: Coluna Desenvolvedor no import e OPCIONAL e ignorada (alocacoes sao refeitas pelo AllocationEngine, nao importadas diretamente)
- **FR-117**: Export gera aba "Stories" com colunas: ID, Componente, Nome, SP, Status, Feature, Dependencias, Desenvolvedor, Data Inicio, Data Fim
- **FR-118**: Export gera aba "Developers" com colunas: ID, Nome
- **FR-119**: Export gera aba "Features" com colunas: ID, Nome, Wave

#### Observability - Logging

- **FR-120**: ImportExcelUseCase DEVE emitir log INFO ao iniciar import: "Iniciando import de arquivo: [file_path]"
- **FR-121**: ImportExcelUseCase DEVE emitir log INFO ao concluir import: "Import concluido: [N] historias importadas, [M] warnings"
- **FR-122**: ImportExcelUseCase DEVE emitir log WARNING para cada linha ignorada ou dependencia nao encontrada
- **FR-123**: ImportExcelUseCase DEVE emitir log ERROR para erros criticos (header ausente, ciclo detectado)
- **FR-124**: ExportExcelUseCase DEVE emitir log INFO ao iniciar export: "Iniciando export para: [file_path]"
- **FR-125**: ExportExcelUseCase DEVE emitir log INFO ao concluir export: "Export concluido: [N] stories, [M] developers, [K] features"
- **FR-126**: ExcelService DEVE emitir log ERROR ao capturar excecoes de openpyxl com detalhes do erro

### Key Entities

- **ExcelService**: Servico de infraestrutura que encapsula operacoes de leitura/escrita de arquivos Excel via openpyxl. Sem logica de negocio, apenas I/O.
- **ImportExcelUseCase**: Caso de uso que coordena importacao completa - validacao de formato, criacao de historias/features em duas passadas, validacao de ciclos, tratamento de warnings.
- **ExportExcelUseCase**: Caso de uso que coordena exportacao completa - busca todas as entidades, formata dados, gera arquivo com multiplas abas.
- **ExcelViewModel**: ViewModel Qt que conecta use cases de Excel a UI, gerenciando operacoes async e emitindo signals de progresso/conclusao.
- **ImportExcelOutputDTO**: DTO com resultado do import incluindo contagens e listas de warnings/erros.
- **ExportExcelOutputDTO**: DTO com resultado do export incluindo caminho do arquivo e contagens.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuario consegue importar arquivo Excel com 100 historias em menos de 10 segundos
- **SC-002**: Usuario consegue exportar backlog com 500 historias em menos de 15 segundos
- **SC-003**: Roundtrip completo (export -> import em DB limpo) preserva 100% dos dados sem perda
- **SC-004**: Import de arquivo com 10 erros de validacao completa com warnings apropriados e dados validos importados
- **SC-005**: Sistema rejeita 100% dos arquivos com ciclos de dependencia antes de persistir qualquer dado
- **SC-006**: Sistema rejeita 100% dos arquivos com headers obrigatorios ausentes com mensagem de erro clara
- **SC-007**: Operacoes de import/export nao bloqueiam interface grafica (UI permanece responsiva)
- **SC-008**: 95% dos usuarios conseguem completar import na primeira tentativa seguindo documentacao

## Architectural Decisions

### ADR-001: ExcelService na Infrastructure Layer

**Contexto**: Constituicao §I exige que I/O fique na camada Infrastructure. openpyxl e uma dependencia externa que deve ser isolada.

**Opcoes**:
1. ExcelService em Infrastructure com Protocol em Application (inversao de dependencia) - recomendado
2. Use Case usa openpyxl diretamente (viola Clean Architecture)
3. ExcelService como Domain Service (viola separacao de responsabilidades)

**Decisao**: Opcao 1 - ExcelService em `infrastructure/excel/` com `ExcelServiceProtocol` em `application/interfaces/`

**Justificativa**:
- Mantem Clean Architecture (Infrastructure para I/O)
- Permite mock do ExcelService em testes unitarios dos Use Cases
- Isola dependencia openpyxl do restante do sistema
- Facilita troca de biblioteca se necessario no futuro

### ADR-002: Formato de ID para Import sem ID

**Contexto**: UC-004 passo 6a diz "Se ID vazio: gera no formato 'US-NNN'". O StoryService existente gera IDs no formato "COMPONENTE-NNN". Ha conflito entre SRS e codigo existente.

**Opcoes**:
1. Usar formato fixo "US-NNN" para IDs gerados no import (diferente do padrao interno)
2. Usar campo Componente do Excel para gerar ID no formato "COMPONENTE-NNN" (consistente com sistema) - recomendado
3. Criar campo Componente obrigatorio no Excel e rejeitar linhas sem Componente

**Decisao**: Opcao 2 - Usar o campo Componente do Excel para gerar ID no formato COMPONENTE-NNN

**Justificativa**:
- Mantem consistencia com o formato de ID usado em todo o sistema (StoryService.generate_story_id)
- Campo Componente ja e obrigatorio no formato do Excel
- Evita ter dois formatos de ID coexistindo no sistema (US-NNN vs COMPONENTE-NNN)
- Reutiliza logica existente de geracao de ID

### ADR-003: Processamento em Duas Passadas

**Contexto**: Dependencias referenciam IDs que podem ainda nao existir durante leitura da primeira linha. Sistema precisa garantir que todos os IDs existam antes de criar dependencias.

**Opcoes**:
1. Processar tudo em uma passada com verificacao lazy de dependencias
2. Duas passadas: (1) criar historias/features, (2) criar dependencias - recomendado
3. Pre-processar arquivo para coletar todos os IDs antes de persistir

**Decisao**: Opcao 2 - Processamento em duas passadas

**Justificativa**:
- Garante que todos os IDs existam antes de tentar criar dependencias
- Permite validacao de ciclos no grafo completo antes de persistir dependencias
- Facilita rollback se ciclo for detectado (ainda nao ha dependencias no banco)
- Logica clara e facil de testar

### ADR-004: Validacao de Ciclos em Lote

**Contexto**: RF-EXCEL-005 exige validar ciclos no conjunto importado. O DependencyService.would_create_cycle() valida uma dependencia de cada vez contra grafo atual.

**Opcoes**:
1. Usar DependencyService.build_graph() para criar grafo temporario e detect_cycle() para validar - recomendado
2. Adicionar dependencias uma a uma com rollback se ciclo detectado (ineficiente)
3. Criar novo metodo no DependencyService para validacao em lote

**Decisao**: Opcao 1 - Usar metodos existentes build_graph() e detect_cycle()

**Justificativa**:
- DependencyService ja tem toda a logica necessaria (build_graph, detect_cycle)
- Nao requer alteracao no dominio existente
- Criar grafo temporario com dependencias do arquivo + existentes permite validacao completa
- Performance adequada para 500 historias

### ADR-005: Wave Default para Features Criadas Automaticamente

**Contexto**: UC-004 passo 6c diz "Cria ou associa Feature". Se Feature nao existe, deve ser criada. Qual wave atribuir?

**Opcoes**:
1. Wave fixo = 1 para todas as features criadas automaticamente - recomendado
2. Wave derivado da ordem de aparicao no arquivo
3. Exigir coluna Wave no Excel e rejeitar linhas sem wave

**Decisao**: Opcao 1 - Wave fixo = 1 como default

**Justificativa**:
- Simplicidade: todas as features auto-criadas iniciam na wave 1
- Usuario pode ajustar waves manualmente via FeatureDialog apos import
- Evita complexidade de derivar wave da ordem do arquivo
- Consistente com principio de criar minimo viavel e ajustar depois

### ADR-006: Import Incremental vs Substitutivo

**Contexto**: UC-004 FA-3 menciona "Dependencia inexistente: warning". Isso implica que import adiciona ao backlog existente (incremental), nao substitui.

**Opcoes**:
1. Import incremental: adiciona ao backlog existente, permite dependencias para IDs ja existentes - recomendado
2. Import substitutivo: limpa backlog e importa do zero
3. Usuario escolhe modo antes de importar

**Decisao**: Opcao 1 - Import incremental

**Justificativa**:
- Permite migracao gradual de dados
- Permite dependencias entre dados novos e existentes
- Usuario pode limpar backlog manualmente se desejar substituicao
- Roundtrip (export -> import limpo) funciona pois export inclui todos os dados

### ADR-007: Comportamento para SP Invalido - Import Parcial

**Contexto**: UC-004 FA-2 diz "SP invalido em linha N: sistema registra warning e pula linha". Isso implica import parcial permitido.

**Opcoes**:
1. Import parcial com warnings para erros nao-criticos (SP invalido, dependencia inexistente) - recomendado
2. Qualquer erro invalida todo o arquivo
3. Usuario escolhe comportamento antes de importar

**Decisao**: Opcao 1 - Import parcial com warnings

**Justificativa**:
- Alinhado com UC-004 FA-2 e FA-3 do SRS
- Pratico para arquivos com poucos erros
- Erros criticos (header ausente, ciclo) ainda abortam todo o import
- Usuario ve resumo de warnings no final e pode corrigir manualmente

### ADR-008: Formato de Export com Multiplas Abas

**Contexto**: RF-EXCEL-006 e RF-EXCEL-007 mencionam exportar historias, desenvolvedores e features. Arquivo unico com multiplas abas ou arquivos separados?

**Opcoes**:
1. Arquivo unico com abas "Stories", "Developers", "Features" - recomendado
2. Tres arquivos separados (stories.xlsx, developers.xlsx, features.xlsx)
3. Arquivo unico com todos os dados em uma aba

**Decisao**: Opcao 1 - Arquivo unico com multiplas abas

**Justificativa**:
- Conveniente para usuario (um arquivo = um backup)
- Estrutura clara e organizada
- Suportado nativamente pelo openpyxl (Workbook com multiple sheets)
- Facilita roundtrip: export gera um arquivo, import le do mesmo arquivo

### ADR-009: Execucao Assincrona via asyncio.to_thread

**Contexto**: Constituicao §VIII exige operacoes async. openpyxl nao e async-native.

**Opcoes**:
1. Executar openpyxl em thread separada via asyncio.to_thread() - recomendado
2. Usar aiofiles para wrap de operacoes
3. Executar sincronamente (bloquearia UI)

**Decisao**: Opcao 1 - asyncio.to_thread() para operacoes openpyxl

**Justificativa**:
- asyncio.to_thread() e a forma padrao de executar codigo sync em contexto async
- Nao bloqueia o event loop Qt
- openpyxl nao precisa de modificacoes
- aiofiles seria redundante pois openpyxl ja faz seu proprio I/O

## Traceability Matrix

### FR -> RF-EXCEL Mapping

| FR | RF-EXCEL | UC-004 |
|----|----------|--------|
| FR-020 a FR-031 | RF-EXCEL-001 (Importar Arquivo Excel) | Fluxo Principal |
| FR-022 | RF-EXCEL-002 (Validar Headers Obrigatorios) | Passo 4-5 |
| FR-024 | RF-EXCEL-003 (Gerar ID Automatico) | Passo 6a |
| FR-026 | RF-EXCEL-004 (Criar/Associar Features) | Passo 6c |
| FR-028, FR-029 | RF-EXCEL-005 (Validar Ciclos) | Passo 7, FA-4 |
| FR-040 a FR-048 | RF-EXCEL-006 (Exportar Backlog) | - |
| FR-043, FR-044 | RF-EXCEL-007 (Exportar Devs e Features) | - |

### FR -> UC-004 Fluxo Alternativo Mapping

| FR | UC-004 FA | Descricao |
|----|-----------|-----------|
| FR-022, FR-100 | FA-1 | Coluna obrigatoria ausente |
| FR-025, FR-101 | FA-2 | SP invalido (warning, pula linha) |
| FR-027, FR-103 | FA-3 | Dependencia inexistente (warning) |
| FR-028, FR-102 | FA-4 | Ciclo detectado (rejeita arquivo) |

## Clarifications

### Session 2026-03-03

- Q: Should import/export operations emit structured logs or metrics for debugging and operational monitoring? → A: Emit structured INFO/WARNING/ERROR logs via Python logging (import start/end, validation warnings, errors)
- Q: Should the system apply data sanitization beyond format validation for imported files? → A: No additional sanitization - existing format validation (SP values, headers, cycles) is sufficient for structured data without executable content

## Assumptions

- openpyxl 3.1.0+ funciona corretamente em Python 3.11+ no Windows
- Arquivos Excel gerados por Microsoft Excel 2016+ sao compativeis com openpyxl
- Usuario tem permissao de leitura/escrita nos diretorios selecionados
- Backlog maximo de 500 historias conforme limite definido em RNF-PERF-001
- Todos os Use Cases e DTOs de EP-001 a EP-008 estao implementados e funcionais
- StoryService.generate_story_id() esta disponivel e funcional
- DependencyService.build_graph() e detect_cycle() estao disponveis e funcionais
- FeatureService.create_feature() esta disponivel e funcional
- UnitOfWork gerencia transacoes corretamente com commit/rollback
- MainWindow, ViewModels e DIContainer de EP-008 estao implementados
- Atalhos Ctrl+I e Ctrl+E foram reservados em EP-008 mas nao implementados

## Test Scenarios

### Testes Unitarios - ExcelService

1. **test_excel_service_read_valid_file**: Ler arquivo valido retorna lista de dicionarios com dados corretos
2. **test_excel_service_read_missing_file**: Ler arquivo inexistente lanca excecao apropriada
3. **test_excel_service_read_corrupted_file**: Ler arquivo corrompido lanca excecao com mensagem clara
4. **test_excel_service_write_workbook**: Escrever workbook cria arquivo com abas corretas
5. **test_excel_service_write_permission_error**: Escrever sem permissao lanca excecao apropriada

### Testes Unitarios - ImportExcelUseCase

1. **test_import_valid_file**: Importar arquivo valido cria todas as historias
2. **test_import_missing_header**: Arquivo sem header obrigatorio lanca excecao e nao persiste dados
3. **test_import_invalid_sp_warning**: Linha com SP invalido gera warning e e pulada
4. **test_import_auto_generate_id**: Linha sem ID gera ID no formato COMPONENTE-NNN
5. **test_import_create_feature**: Feature inexistente e criada automaticamente com wave=1
6. **test_import_dependencies_second_pass**: Dependencias sao criadas apos todas as historias
7. **test_import_cycle_detection**: Ciclo detectado lanca excecao e executa rollback
8. **test_import_missing_dependency_warning**: Dependencia para ID inexistente gera warning
9. **test_import_partial_success**: Arquivo com alguns erros importa linhas validas
10. **test_import_empty_file**: Arquivo sem dados (apenas headers) retorna output vazio

### Testes Unitarios - ExportExcelUseCase

1. **test_export_stories**: Exportar historias gera aba "Stories" com colunas corretas
2. **test_export_developers**: Exportar desenvolvedores gera aba "Developers"
3. **test_export_features**: Exportar features gera aba "Features" com wave
4. **test_export_dependencies_format**: Dependencias sao formatadas com ponto-e-virgula
5. **test_export_empty_backlog**: Exportar backlog vazio gera arquivo com headers apenas

### Testes de Integracao

1. **test_roundtrip_complete**: Export seguido de import em DB limpo restaura todos os dados
2. **test_import_with_existing_data**: Import incremental adiciona ao backlog existente
3. **test_import_with_existing_dependencies**: Import pode referenciar IDs ja existentes no sistema
4. **test_export_large_backlog**: Export de 500 historias completa em tempo razoavel (< 15s)
5. **test_import_large_file**: Import de 500 historias completa em tempo razoavel (< 10s)

### Testes de UI (pytest-qt)

1. **test_ctrl_i_opens_import_dialog**: Atalho Ctrl+I abre QFileDialog para selecao
2. **test_ctrl_e_opens_export_dialog**: Atalho Ctrl+E abre QFileDialog para destino
3. **test_import_button_disabled_during_operation**: Botao fica desabilitado durante import
4. **test_progress_dialog_shown_during_import**: QProgressDialog e exibido durante operacao
5. **test_import_success_message**: QMessageBox exibe resumo apos import bem-sucedido
6. **test_table_refresh_after_import**: Tabela de backlog atualiza apos import
