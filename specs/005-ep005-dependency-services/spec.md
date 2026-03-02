# Feature Specification: EP-005 Gestao de Dependencias - Servicos e Aplicacao

**Feature Branch**: `005-ep005-dependency-services`
**Created**: 2026-03-01
**Status**: Draft
**Input**: Implementacao da camada de servico e aplicacao para gestao de dependencias entre historias: DependencyService (domain service) com deteccao de ciclos via DFS O(V+E), validacao cross-wave, Use Cases, DTOs Pydantic para operacoes de adicao/remocao de dependencias

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Adicionar Dependencia entre Historias (Priority: P1)

Como Scrum Master, preciso definir que uma historia depende de outra para que o sistema garanta a ordem correta de execucao e evite que uma historia seja alocada antes de seu pre-requisito estar concluido.

**Why this priority**: Adicionar dependencias e a operacao fundamental deste epico. Sem ela, nao ha como modelar pre-requisitos entre historias e o sistema de alocacao nao pode respeitar a ordem de execucao.

**Independent Test**: Pode ser testado adicionando uma dependencia entre duas historias existentes e verificando que a relacao foi persistida no banco.

**Acceptance Scenarios**:

1. **Given** historias A e B independentes no backlog, **When** adiciono dependencia B depende de A, **Then** a dependencia e registrada e get_dependencies(B) retorna ["A"]
2. **Given** historia B que ja depende de A, **When** tento adicionar novamente B depende de A, **Then** ValueError e lancado com mensagem "Dependencia B -> A ja existe"
3. **Given** historia A existente, **When** tento adicionar A depende de A (auto-dependencia), **Then** ValueError e lancado com mensagem "Historia nao pode depender de si mesma"
4. **Given** historia A existente e historia X inexistente, **When** tento adicionar A depende de X, **Then** ValueError e lancado com mensagem "Historia nao encontrada: X"
5. **Given** historia X inexistente e historia A existente, **When** tento adicionar X depende de A, **Then** ValueError e lancado com mensagem "Historia nao encontrada: X"

---

### User Story 2 - Detectar e Rejeitar Ciclos de Dependencia (Priority: P1)

Como Scrum Master, preciso que o sistema detecte automaticamente quando uma dependencia criaria um ciclo para evitar deadlocks logicos onde historias aguardam infinitamente umas pelas outras.

**Why this priority**: Deteccao de ciclos e critica para integridade do grafo de dependencias. Sem ela, ciclos poderiam travar a alocacao automatica.

**Independent Test**: Pode ser testado tentando criar um ciclo simples (A->B->A) ou complexo (A->B->C->A) e verificando que a excecao e lancada com o caminho correto.

**Acceptance Scenarios**:

1. **Given** A depende de B (A->B), **When** tento adicionar B depende de A (B->A), **Then** CyclicDependencyException e lancada com path=["A", "B", "A"]
2. **Given** A depende de B e B depende de C, **When** tento adicionar C depende de A, **Then** CyclicDependencyException e lancada com path=["A", "B", "C", "A"]
3. **Given** grafo grande com 50 nos e um ciclo escondido (no 25 fecha ciclo com no 1), **When** detecto o ciclo, **Then** tempo de execucao e menor que 100ms (CT-002)
4. **Given** A depende de B, B depende de C e D depende de C, **When** tento adicionar C depende de D, **Then** CyclicDependencyException e lancada (ciclo C->D->C)
5. **Given** grafo aciclico com dependencias A->B, A->C, B->D, C->D, **When** tento adicionar E depende de D, **Then** dependencia e adicionada com sucesso (sem ciclo)

---

### User Story 3 - Validar Dependencias entre Ondas (Priority: P2)

Como Product Owner, preciso ser alertado quando uma historia depende de outra em onda posterior para entender potenciais problemas no planejamento de entregas.

**Why this priority**: Validacao cross-wave e um warning que ajuda no planejamento mas nao impede a operacao. E secundaria em relacao a adicao basica e deteccao de ciclos.

**Independent Test**: Pode ser testado criando dependencia entre historia de onda 1 e historia de onda 2 e verificando que o warning e emitido.

**Acceptance Scenarios**:

1. **Given** historia H1 em feature de onda 1 e H2 em feature de onda 2, **When** adiciono H1 depende de H2, **Then** dependencia e adicionada e InvalidWaveDependencyException e retornada como warning
2. **Given** historia H1 em feature de onda 2 e H2 em feature de onda 1, **When** adiciono H1 depende de H2, **Then** dependencia e adicionada sem warning (onda anterior e valida)
3. **Given** historia H1 sem feature (wave=0) e H2 em feature de onda 2, **When** adiciono H1 depende de H2, **Then** dependencia e adicionada e InvalidWaveDependencyException e retornada como warning
4. **Given** historia H1 em feature de onda 1 e H2 sem feature (wave=0), **When** adiciono H1 depende de H2, **Then** dependencia e adicionada sem warning (wave 0 e considerada anterior a wave 1)

---

### User Story 4 - Remover Dependencia entre Historias (Priority: P2)

Como Scrum Master, preciso remover dependencias que nao sao mais validas quando os requisitos do projeto mudam.

**Why this priority**: Remocao e uma operacao simples mas necessaria para manutencao do grafo de dependencias.

**Independent Test**: Pode ser testado removendo uma dependencia existente e verificando que ela nao aparece mais em get_dependencies.

**Acceptance Scenarios**:

1. **Given** historia B que depende de A, **When** removo a dependencia B->A, **Then** get_dependencies(B) retorna lista vazia
2. **Given** historia B que nao depende de A, **When** tento remover dependencia B->A, **Then** ValueError e lancado com mensagem "Dependencia B -> A nao existe"
3. **Given** historia B que depende de A e C, **When** removo apenas B->A, **Then** get_dependencies(B) retorna ["C"] (outras dependencias permanecem)

---

### User Story 5 - Consultar Dependencias de uma Historia (Priority: P2)

Como Scrum Master, preciso consultar as dependencias de uma historia para entender seus pre-requisitos e planejar a execucao.

**Why this priority**: Consulta e necessaria para operacoes de leitura e exibicao na UI.

**Independent Test**: Pode ser testado adicionando dependencias e consultando via get_dependencies.

**Acceptance Scenarios**:

1. **Given** historia B que depende de A e C, **When** consulto dependencias de B, **Then** retorna ["A", "C"]
2. **Given** historia A sem dependencias, **When** consulto dependencias de A, **Then** retorna lista vazia
3. **Given** historia A que e dependencia de B e C, **When** consulto dependentes de A, **Then** retorna ["B", "C"]

---

### Edge Cases

- O que acontece quando historias envolvidas em dependencia sao deletadas? DeleteStory (EP-003) ja remove todas as dependencias via remove_all_for_story. Este epico NAO implementa operacoes bulk.
- O que acontece com dependencias durante import de Excel? Validacao de ciclos sera feita no import (EP futuros). Este epico fornece a base algoritmica.
- O que acontece se ambas as historias estao na mesma wave? Dependencia e valida, sem warning (same wave e permitido).
- O que acontece se a historia dependente nao tem feature? Wave e calculada como 0 para historias sem feature associada.

## Requirements *(mandatory)*

### Functional Requirements

#### DependencyService - Domain Service

- **FR-001**: Sistema DEVE implementar `DependencyService` como domain service em `src/backlog_manager/domain/services/dependency_service.py`
- **FR-002**: DependencyService DEVE ser uma classe que recebe os dados necessarios via parametros, mantendo o dominio sincrono quando possivel
- **FR-003**: DependencyService DEVE implementar metodo `detect_cycle(graph: dict[str, list[str]], source: str, target: str) -> list[str] | None` que retorna o caminho do ciclo ou None se nao houver ciclo
- **FR-004**: DependencyService.detect_cycle DEVE usar algoritmo DFS iterativo com complexidade O(V+E)
- **FR-005**: DependencyService.detect_cycle DEVE usar estados de nos WHITE (nao visitado), GRAY (em processamento) e BLACK (finalizado) para deteccao eficiente
- **FR-006**: DependencyService.detect_cycle DEVE construir o caminho do ciclo iniciando pelo no que fecha o ciclo, seguindo a direcao das arestas, terminando no mesmo no (ex: ["A", "B", "C", "A"])
- **FR-007**: DependencyService DEVE implementar metodo `validate_wave_dependency(story_wave: int, depends_on_wave: int) -> bool` que retorna True se dependencia e valida (depends_on_wave <= story_wave)
- **FR-008**: DependencyService DEVE implementar metodo `build_graph(dependencies: Sequence[tuple[str, str]]) -> dict[str, list[str]]` que constroi grafo de adjacencia a partir de lista de tuplas (story_id, depends_on_id)
- **FR-009**: DependencyService DEVE implementar metodo `would_create_cycle(graph: dict[str, list[str]], source: str, target: str) -> list[str] | None` que verifica se adicionar aresta source->target criaria ciclo, retornando o caminho ou None
- **FR-010**: DependencyService DEVE usar implementacao iterativa com pilha explicita para evitar stack overflow em grafos profundos

#### Use Cases - Application Layer

- **FR-020**: Sistema DEVE implementar use cases em `src/backlog_manager/application/use_cases/dependency/`
- **FR-021**: Sistema DEVE implementar `AddDependencyUseCase` que coordena validacoes e adicao de dependencia
- **FR-022**: AddDependencyUseCase DEVE validar existencia de ambas as historias via StoryRepository.exists() antes de adicionar dependencia
- **FR-023**: AddDependencyUseCase DEVE lancar ValueError com mensagem "Historia nao encontrada: {story_id}" se historia nao existe
- **FR-024**: AddDependencyUseCase DEVE buscar todas as dependencias via get_all_dependencies(), construir grafo e verificar ciclos via DependencyService.would_create_cycle()
- **FR-025**: AddDependencyUseCase DEVE lancar CyclicDependencyException com o path do ciclo se adicao criaria ciclo
- **FR-026**: AddDependencyUseCase DEVE calcular wave de cada historia envolvida: story.feature_id -> FeatureRepository.get_by_id() -> feature.wave; se feature_id e None, wave=0
- **FR-027**: AddDependencyUseCase DEVE retornar InvalidWaveDependencyException como warning (no DTO de output) se depends_on_wave > story_wave, SEM bloquear a adicao
- **FR-028**: AddDependencyUseCase DEVE persistir dependencia via StoryDependencyRepository.add() apos todas as validacoes
- **FR-029**: Sistema DEVE implementar `RemoveDependencyUseCase` que coordena remocao de dependencia
- **FR-030**: RemoveDependencyUseCase DEVE remover dependencia via StoryDependencyRepository.remove()
- **FR-031**: Sistema DEVE implementar `GetDependenciesUseCase` que retorna lista de historias das quais uma historia depende
- **FR-032**: GetDependenciesUseCase DEVE usar StoryDependencyRepository.get_dependencies() e converter IDs em DTOs com informacoes basicas
- **FR-033**: Sistema DEVE implementar `GetDependentsUseCase` que retorna lista de historias que dependem de uma historia
- **FR-034**: GetDependentsUseCase DEVE usar StoryDependencyRepository.get_dependents() e converter IDs em DTOs
- **FR-035**: Todos os use cases DEVEM ser classes async com metodo `async def execute(input_dto: InputDTO) -> OutputDTO`
- **FR-036**: Todos os use cases DEVEM receber UnitOfWork como dependencia no construtor
- **FR-037**: Todos os use cases DEVEM usar context manager do UnitOfWork para garantir transacoes atomicas

#### DTOs - Application Layer

- **FR-040**: Sistema DEVE implementar DTOs Pydantic em `src/backlog_manager/application/dto/dependency/`
- **FR-041**: Sistema DEVE implementar `AddDependencyInputDTO(BaseModel)` com campos: story_id (str), depends_on_id (str)
- **FR-042**: Sistema DEVE implementar `AddDependencyOutputDTO(BaseModel)` com campos: success (bool), story_id (str), depends_on_id (str), warning (InvalidWaveDependencyWarningDTO | None)
- **FR-043**: Sistema DEVE implementar `InvalidWaveDependencyWarningDTO(BaseModel)` com campos: story_id (str), depends_on_id (str), story_wave (int), depends_on_wave (int), message (str)
- **FR-044**: Sistema DEVE implementar `RemoveDependencyInputDTO(BaseModel)` com campos: story_id (str), depends_on_id (str)
- **FR-045**: Sistema DEVE implementar `RemoveDependencyOutputDTO(BaseModel)` com campos: success (bool)
- **FR-046**: Sistema DEVE implementar `GetDependenciesInputDTO(BaseModel)` com campos: story_id (str)
- **FR-047**: Sistema DEVE implementar `GetDependenciesOutputDTO(BaseModel)` com campos: story_id (str), dependencies (list[str])
- **FR-048**: Sistema DEVE implementar `GetDependentsInputDTO(BaseModel)` com campos: story_id (str)
- **FR-049**: Sistema DEVE implementar `GetDependentsOutputDTO(BaseModel)` com campos: story_id (str), dependents (list[str])
- **FR-050**: Todos os DTOs DEVEM usar validacao Pydantic para garantir que IDs nao sejam vazios

### Key Entities

- **DependencyService**: Domain service responsavel por regras de negocio de dependencias - deteccao de ciclos via DFS, validacao cross-wave, construcao de grafo. Recebe dados como parametros, mantendo dominio sincrono.
- **AddDependencyUseCase**: Application service que coordena adicao de dependencia com UnitOfWork. Valida existencia de historias, detecta ciclos, valida waves, persiste dependencia.
- **RemoveDependencyUseCase**: Application service que coordena remocao de dependencia.
- **GetDependenciesUseCase / GetDependentsUseCase**: Application services para consultas de leitura.
- **DTOs**: Objetos Pydantic para transporte de dados entre camadas. Input DTOs validam entrada, Output DTOs formatam saida incluindo warnings opcionais.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Usuario consegue adicionar dependencia entre duas historias existentes com validacao imediata
- **SC-002**: Sistema detecta e rejeita ciclos de dependencia com mensagem de erro contendo o caminho completo do ciclo
- **SC-003**: Deteccao de ciclo em grafo de 50 nos executa em menos de 100ms (CT-002)
- **SC-004**: Sistema emite warning quando historia depende de onda posterior, mas permite a adicao
- **SC-005**: Usuario consegue remover dependencia existente
- **SC-006**: Usuario consegue consultar lista de dependencias e dependentes de qualquer historia
- **SC-007**: Todas as operacoes sao transacionais - falhas resultam em rollback completo
- **SC-008**: Cobertura de testes unitarios do DependencyService atinge 100% das regras de negocio
- **SC-009**: Cobertura de testes de integracao dos use cases atinge 100% dos fluxos de sucesso e erro
- **SC-010**: UC-003 (Detectar e Resolver Deadlock) e executavel apos este epico

## Architectural Decisions

### ADR-001: Deteccao de Ciclos no DependencyService vs. Repository

**Contexto**: RF-DEP-003 exige deteccao de ciclos via DFS. O StoryDependencyRepository.add() atual apenas valida auto-dependencia (story_id == depends_on_id), mas NAO detecta ciclos indiretos.

**Opcoes**:
1. Deteccao de ciclo no DependencyService, repositorio apenas persiste
2. Deteccao de ciclo no repositorio (requer acesso a todo o grafo)
3. Use case coordena deteccao antes de chamar repositorio

**Decisao**: Opcao 1 - DependencyService detecta ciclos, repositorio apenas persiste

**Justificativa**:
- Separacao de responsabilidades: logica de negocio (DFS) fica no dominio
- Testabilidade: DependencyService pode ser testado em isolamento com grafos in-memory
- Repositorio permanece simples e focado em persistencia
- Use case coordena: busca grafo completo, passa para servico, depois persiste

### ADR-002: Validacao de Existencia de Historias

**Contexto**: RF-DEP-001 exige que "Dependencia deve existir no backlog". O repositorio atual NAO valida se as historias existem (assume FKs do banco).

**Opcoes**:
1. Validar via StoryRepository.exists() no use case antes de chamar servico
2. Validar no DependencyService via StoryRepository
3. Deixar FK do banco falhar (IntegrityError)

**Decisao**: Opcao 1 - Validar via StoryRepository.exists() no AddDependencyUseCase

**Justificativa**:
- Mensagem de erro mais clara que violacao de FK ("Historia nao encontrada: X")
- Fail-fast: erro antes de tentar detectar ciclos ou persistir
- DependencyService permanece sincrono, recebendo apenas dados
- Validacao e responsabilidade da camada de aplicacao

### ADR-003: Obtencao de Wave para Validacao Cross-Wave

**Contexto**: RF-DEP-004 exige validar se historia depende de onda posterior. Wave e derivada da feature associada (story.feature_id -> feature.wave). Historia sem feature tem wave=0.

**Opcoes**:
1. Receber waves como parametro do use case (pre-calculado)
2. DependencyService recebe FeatureRepository como dependencia
3. Use case consulta Feature e passa wave para DependencyService

**Decisao**: Opcao 1 - Use case calcula waves e passa para DependencyService

**Justificativa**:
- DependencyService permanece sincrono e sem dependencias de repositorio
- Use case ja tem acesso a UnitOfWork com FeatureRepository
- Wave=0 para historias sem feature e calculada no use case
- Metodo validate_wave_dependency recebe apenas inteiros (story_wave, depends_on_wave)

### ADR-004: Comportamento do Warning InvalidWaveDependencyException

**Contexto**: RF-DEP-004 diz "warning (nao bloqueante)". A dependencia deve ser adicionada mesmo com o warning.

**Opcoes**:
1. Adiciona dependencia e retorna warning no DTO de output
2. Adiciona dependencia e lanca excecao (caller decide)
3. Adiciona dependencia e loga warning

**Decisao**: Opcao 1 - Adiciona dependencia e retorna warning no AddDependencyOutputDTO

**Justificativa**:
- Warning nao bloqueante significa operacao bem-sucedida com aviso
- Output DTO contem campo `warning: InvalidWaveDependencyWarningDTO | None`
- Caller (UI) pode exibir warning ao usuario se presente
- Log tambem e emitido para rastreabilidade

### ADR-005: Formato do Caminho do Ciclo na Excecao

**Contexto**: SRS (UC-003) mostra exemplos como ["A","B","C","A"] onde primeiro e ultimo elementos sao o mesmo (inicio do ciclo).

**Opcoes**:
1. Caminho comeca e termina no no que fecha o ciclo (ex: A->B->C->A vira ["A","B","C","A"])
2. Caminho na ordem de descoberta do DFS
3. Caminho minimo do ciclo

**Decisao**: Opcao 1 - Caminho comeca e termina no no que fecha o ciclo

**Justificativa**:
- Consistente com exemplos do SRS e UC-003
- Usuario entende claramente o ciclo: "A depende de B, B depende de C, C depende de A"
- Formato ["A","B","C","A"] e util para exibicao como "A -> B -> C -> A"
- Construido durante backtrack do DFS quando ciclo e detectado

### ADR-006: DependencyService Separado vs. Extensao do StoryService

**Contexto**: Epic menciona apenas DependencyService, mas gestao de dependencias esta relacionada a historias.

**Opcoes**:
1. Criar DependencyService separado (SRP)
2. Estender StoryService com metodos de dependencia
3. Criar ambos e coordenar no use case

**Decisao**: Opcao 1 - Criar DependencyService separado

**Justificativa**:
- Single Responsibility Principle: StoryService lida com Stories, DependencyService com grafos
- DependencyService e coeso: DFS, deteccao de ciclos, validacao de waves
- StoryService permanece inalterado (EP-003)
- Use case coordena ambos servicos se necessario

### ADR-007: Operacoes Bulk de Dependencias

**Contexto**: Epic foca em adicionar/remover dependencias individuais. RF-STORY-003 (deletar historia) ja remove dependencias via remove_all_for_story().

**Opcoes**:
1. EP-005 implementa operacoes bulk
2. EP-005 NAO implementa bulk (ja coberto em EP-003)

**Decisao**: Opcao 2 - EP-005 NAO implementa operacoes bulk

**Justificativa**:
- remove_all_for_story() ja existe e e usado pelo DeleteStoryUseCase (EP-003)
- Este epico foca em adicao/remocao individual com validacoes
- Divisao clara de responsabilidade: EP-003 para CRUD de historia, EP-005 para logica de dependencias

### ADR-008: Integridade Transacional em Adicao de Dependencia

**Contexto**: Adicionar dependencia envolve: (1) validar existencia, (2) detectar ciclos (read-only), (3) validar waves, (4) persistir.

**Opcoes**:
1. Toda operacao usa UnitOfWork para atomicidade
2. Validacoes read-only fora da transacao, apenas persist dentro

**Decisao**: Opcao 1 - Toda operacao dentro do UnitOfWork

**Justificativa**:
- Consistencia: leituras e escritas veem o mesmo snapshot do banco
- Evita race conditions entre validacao e persist
- UnitOfWork ja e padrao nos use cases existentes
- Deteccao de ciclo usa grafo atualizado (get_all_dependencies dentro da transacao)

### ADR-009: Algoritmo DFS Iterativo vs. Recursivo

**Contexto**: Grafos de dependencia podem ser profundos. Python tem limite de recursao (~1000).

**Opcoes**:
1. DFS recursivo (simples mas limitado)
2. DFS iterativo com pilha explicita
3. BFS (detecta ciclos mas sem caminho direto)

**Decisao**: Opcao 2 - DFS iterativo com pilha explicita

**Justificativa**:
- Evita stack overflow em grafos profundos (backlog de 500 historias)
- Permite construcao do caminho do ciclo durante backtrack
- Complexidade O(V+E) garantida
- Pilha explicita controla estados WHITE/GRAY/BLACK

## Traceability Matrix

### Requisitos do Epico -> Requisitos Funcionais

| Requisito Epico | Requisitos Funcionais |
|-----------------|----------------------|
| RF-DEP-001: Adicionar Dependencia | FR-001 a FR-010, FR-021 a FR-028, FR-041 a FR-043 |
| RF-DEP-002: Remover Dependencia | FR-029, FR-030, FR-044, FR-045 |
| RF-DEP-003: Detectar Ciclos | FR-003 a FR-006, FR-009, FR-010, FR-024, FR-025 |
| RF-DEP-004: Validar Ondas | FR-007, FR-026, FR-027, FR-043 |

### User Stories -> Requisitos Epico

| User Story | Requisitos Epico |
|------------|-----------------|
| US-1: Adicionar Dependencia | RF-DEP-001 |
| US-2: Detectar Ciclos | RF-DEP-003 |
| US-3: Validar Ondas | RF-DEP-004 |
| US-4: Remover Dependencia | RF-DEP-002 |
| US-5: Consultar Dependencias | RF-DEP-001, RF-DEP-002 (leitura) |

## Assumptions

- StoryRepository.exists() esta implementado e funcional (EP-001)
- StoryDependencyRepository.add/remove/get_dependencies/get_dependents estao implementados (EP-001)
- UnitOfWork gerencia transacoes corretamente com commit/rollback automatico
- FeatureRepository.get_by_id() esta implementado e funcional (EP-001)
- Excecoes CyclicDependencyException e InvalidWaveDependencyException estao definidas (EP-001)
- Grafo de dependencias cabe em memoria para backlogs de ate 500 historias (premissa do epico)
- Historia sem feature_id e tratada como wave=0
- Dependencia entre historias da mesma wave e permitida sem warning

## Algorithm Specification: DFS Cycle Detection

### Estados dos Nos

```
WHITE = 0  # Nao visitado
GRAY = 1   # Em processamento (no stack de recursao)
BLACK = 2  # Finalizado (todos descendentes processados)
```

### Pseudocodigo (Iterativo)

```python
def would_create_cycle(graph, source, target) -> list[str] | None:
    """Verifica se adicionar aresta source->target criaria ciclo.

    Simula adicao da aresta e executa DFS a partir de target
    procurando caminho de volta para source.

    Returns:
        Path do ciclo [source, ..., target, source] ou None
    """
    # Simular adicao da aresta
    graph_copy = copy_graph(graph)
    graph_copy[source].append(target)

    # DFS iterativo com pilha de estados
    color = {node: WHITE for node in graph_copy}
    parent = {}
    stack = [(source, False)]  # (node, is_backtracking)

    while stack:
        node, is_backtracking = stack.pop()

        if is_backtracking:
            color[node] = BLACK
            continue

        if color[node] == GRAY:
            # Encontrou ciclo - construir caminho
            return build_cycle_path(parent, node)

        if color[node] == BLACK:
            continue

        color[node] = GRAY
        stack.append((node, True))  # Para marcar BLACK depois

        for neighbor in graph_copy.get(node, []):
            if color[neighbor] == GRAY:
                # Ciclo detectado
                parent[neighbor] = node
                return build_cycle_path(parent, neighbor)
            if color[neighbor] == WHITE:
                parent[neighbor] = node
                stack.append((neighbor, False))

    return None  # Nenhum ciclo

def build_cycle_path(parent, cycle_start) -> list[str]:
    """Constroi caminho do ciclo a partir do mapa de pais."""
    path = [cycle_start]
    current = parent.get(cycle_start)
    while current != cycle_start:
        path.append(current)
        current = parent.get(current)
    path.append(cycle_start)  # Fechar ciclo
    path.reverse()  # Ordem correta
    return path
```

### Complexidade

- **Tempo**: O(V + E) onde V = numero de historias, E = numero de dependencias
- **Espaco**: O(V) para pilha e estruturas auxiliares
- **Performance Target**: < 100ms para V=50, E=100 (CT-002)

## Test Scenarios

### Testes Unitarios - DependencyService

1. **test_detect_cycle_direct**: A->B, adicionar B->A = ciclo ["A", "B", "A"]
2. **test_detect_cycle_indirect**: A->B, B->C, adicionar C->A = ciclo ["A", "B", "C", "A"]
3. **test_no_cycle_dag**: A->B, A->C, B->D, C->D, adicionar E->D = sem ciclo
4. **test_self_dependency**: adicionar A->A = None (validado antes pelo repositorio)
5. **test_performance_50_nodes**: Grafo com 50 nos, tempo < 100ms
6. **test_validate_wave_valid**: story_wave=2, depends_wave=1 = True
7. **test_validate_wave_invalid**: story_wave=1, depends_wave=2 = False
8. **test_build_graph**: Lista de tuplas -> dict de adjacencia

### Testes de Integracao - Use Cases

1. **test_add_dependency_success**: Adiciona dependencia valida
2. **test_add_dependency_story_not_found**: Historia inexistente = ValueError
3. **test_add_dependency_cycle**: Detecta ciclo e lanca CyclicDependencyException
4. **test_add_dependency_wave_warning**: Dependencia cross-wave invalida retorna warning
5. **test_remove_dependency_success**: Remove dependencia existente
6. **test_remove_dependency_not_found**: Dependencia inexistente = ValueError
7. **test_get_dependencies**: Retorna lista correta de dependencias
8. **test_get_dependents**: Retorna lista correta de dependentes
