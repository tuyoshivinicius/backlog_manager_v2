<!--
  Sync Impact Report
  ===================
  Version change: (new file) → 1.0.0

  Added sections:
  - Core Principles (21 principles: I through XXI)
  - Governance (Amendment Process, Versioning, Compliance)

  Modified principles: N/A (initial creation)
  Removed sections: N/A (initial creation)

  Templates requiring updates:
  - .specify/templates/plan-template.md: ✅ Compatible (Constitution Check section exists)
  - .specify/templates/spec-template.md: ✅ Compatible (FR/NFR structure aligns)
  - .specify/templates/tasks-template.md: ✅ Compatible (phase structure supports test-first approach)

  Follow-up TODOs: None
-->

# Backlog Manager Constitution

## Princípios

### I. Clean Architecture

O Backlog Manager segue os princípios de Clean Architecture com
separação de responsabilidades em quatro camadas: Presentation
(UI), Infrastructure (I/O), Application (casos de uso) e Domain
(negócio). O fluxo de dependências é sempre de fora para dentro
(Presentation → Infrastructure → Application → Domain).

**Requisitos**:

- A camada Domain NÃO DEVE importar de Application,
  Infrastructure ou Presentation.
- A camada Application NÃO DEVE importar de Infrastructure ou
  Presentation.
- A camada Infrastructure NÃO DEVE importar de Presentation.
- Todas as dependências DEVEM usar inversão de dependência
  (interfaces/Protocols) ao cruzar limites de camadas.
- Domain DEVE ser testável sem mocks (sem dependências externas).
- Mudanças na UI ou banco de dados NÃO DEVEM afetar a lógica de
  negócio.
- Domain DEVE ser reutilizável em outros contextos (CLI, API,
  etc.).

**Referência**:

```
┌─────────────────────────────────────┐
│      Presentation Layer (UI)        │  ← PySide6
│  depende de ↓                       │
├─────────────────────────────────────┤
│    Infrastructure Layer (I/O)       │  ← SQLite, Excel, Repositories
│  depende de ↓                       │
├─────────────────────────────────────┤
│     Application Layer (Casos Uso)   │  ← Use Cases, DTOs, Interfaces
│  depende de ↓                       │
├─────────────────────────────────────┤
│      Domain Layer (Negócio)         │  ← Entities, Value Objects,
│  sem dependências externas          │    Services
└─────────────────────────────────────┘
```

**Justificativa**: Separação em camadas com dependências
unidirecionais isola a lógica de negócio de detalhes técnicos,
facilitando testes, manutenção e evolução independente de cada
camada. Violação deste princípio constitui não-conformidade.

### II. Domain-Driven Design (DDD)

O domínio do Backlog Manager é modelado usando conceitos de
Domain-Driven Design: entidades ricas, value objects imutáveis,
domain services e exceções de domínio. Invariantes são garantidas
no construtor — entidades inválidas nunca existem (fail fast).

**Requisitos**:

- Entidades DEVEM conter lógica de negócio e validações; NÃO
  DEVEM ser meros DTOs.
- Invariantes DEVEM ser garantidas no construtor das entidades.
- Value Objects DEVEM ser imutáveis e validar seus valores na
  criação; mudanças requerem novo objeto.
- Lógica que não pertence a nenhuma entidade específica DEVE
  ficar em Domain Services stateless.
- Violações de regras de negócio DEVEM lançar exceções de
  domínio específicas (ver Princípio XVI).
- A camada de domínio NÃO DEVE ter dependências de frameworks.

**Justificativa**: A lógica de negócio fica explícita, testável
isoladamente e protegida por invariantes de domínio. Violação
deste princípio constitui não-conformidade.

### III. Repository Pattern

Acesso a dados é abstraído através de interfaces de Repository
definidas na camada de domínio, com implementações concretas na
camada de infraestrutura. Este padrão desacopla a lógica de
negócio do mecanismo de persistência.

**Requisitos**:

- Interfaces de repositório DEVEM ser definidas como `Protocol`
  na camada de domínio.
- Implementações concretas DEVEM residir em Infrastructure.
- Repositórios DEVEM retornar entidades de domínio (Story,
  Developer, Feature, Configuration), nunca DTOs.
- Padrão Unit of Work DEVE ser utilizado para transações
  envolvendo múltiplos repositórios.

**Justificativa**: Desacopla a lógica de domínio do mecanismo de
persistência, habilita testes com mocks e permite trocar
implementações de armazenamento. Violação deste princípio
constitui não-conformidade.

### IV. Dependency Injection

Dependências são injetadas através do `DIContainer` centralizado,
configurado na raiz de composição (camada de apresentação ou
ponto de entrada). Componentes recebem suas dependências via
construtor em vez de criá-las internamente.

**Requisitos**:

- Componentes NÃO DEVEM criar suas dependências; DEVEM
  recebê-las via construtor.
- O container DEVE ser configurado na raiz de composição
  (camada de apresentação ou ponto de entrada).
- Todas as dependências entre camadas DEVEM passar pelo
  container.

**Justificativa**: Facilita testes e troca de implementações sem
alterar código de negócio. Violação deste princípio constitui
não-conformidade.

### V. SQLite como Banco de Dados

SQLite é o banco de dados utilizado para todos os dados
persistentes do Backlog Manager. Oferece simplicidade,
portabilidade (arquivo único, sem servidor) e zero dependências
externas (built-in no Python).

**Requisitos**:

- Todas as operações de persistência DEVEM utilizar SQLite.
- Arquivo de banco de dados (`backlog_manager.db`) DEVE estar
  localizado em diretório apropriado (`%APPDATA%` no Windows ou
  `~/.config/` no Linux).
- Schema DEVE ser definido em `infrastructure/database/schema.sql`.
- Migrações DEVEM ser versionadas e executadas automaticamente
  na inicialização da aplicação.
- Transactions (Unit of Work) DEVEM ser utilizadas para garantir
  consistência em operações múltiplas (ACID conforme
  RNF-CONF-003).

**Justificativa**: SQLite oferece simplicidade, portabilidade e
performance suficiente para o escopo do Backlog Manager,
eliminando complexidade de servidor de banco de dados externo.
Violação deste princípio constitui não-conformidade.

### VI. Packaging & Distribution (Library-First)

O Backlog Manager é uma library Python instalável via
`pip install` e publicada no PyPI. Poetry é utilizado como
gestor de dependências e para build do pacote, seguindo
versionamento semântico.

**Requisitos**:

- Poetry DEVE ser utilizado como gestor de dependências e para
  build do pacote (arquivo `pyproject.toml`).
- O pacote DEVE ser publicável via `poetry publish`.
- Todas as dependências DEVEM ser declaradas em `pyproject.toml`
  com versões pinadas quando possível.
- Entry points (CLI, scripts) DEVEM ser definidos em
  `[project.scripts]` no `pyproject.toml`.
- Package version DEVE estar em `pyproject.toml` (fonte única da
  verdade).
- Versioning semântico DEVE ser seguido: MAJOR (breaking
  changes), MINOR (novos recursos), PATCH (correções).
- `poetry build` DEVE gerar distribuição (wheel + sdist).
- `poetry publish` DEVE fazer upload para PyPI.
- CI/CD DEVE validar build antes de publicar.
- Dependências obrigatórias: `pydantic` (DTOs na Application
  layer), `aiofiles` (I/O assíncrono em Infrastructure),
  `aiosqlite` (acesso SQLite async), `openpyxl` (Excel,
  envolvido com `aiofiles`), `PySide6` (interface gráfica).
- `sqlalchemy` é opcional (ORM sobre SQLite, verificar
  compatibilidade async).

**Referência**:

```
backlog_manager_v2/              # Raiz do repositório
├── src/
│   └── backlog_manager/         # Pacote Python importável
│       ├── __init__.py
│       ├── domain/
│       ├── application/
│       ├── infrastructure/
│       └── presentation/
├── tests/                       # Fora de src/ (não empacotado)
│   ├── unit/
│   └── integration/
├── pyproject.toml               # Metadados, dependências, versão
├── CHANGELOG.md                 # Histórico de lançamentos
├── LICENSE                      # Licença do projeto
└── README.md                    # Documentação do projeto
```

```toml
[tool.poetry]
packages = [{include = "backlog_manager", from = "src"}]
```

**Justificativa**: Poetry oferece reproducibilidade, gerenciamento
de dependências robusto e integração com PyPI. Library-first
permite reutilização em múltiplos contextos (CLI, API, outros
aplicativos). Violação deste princípio constitui
não-conformidade.

### VII. Estrutura de Diretórios

O projeto utiliza o src layout recomendado pelo Poetry.
Código-fonte reside em `src/`, testes ficam na raiz do
repositório. A organização reflete as quatro camadas da
Clean Architecture.

**Requisitos**:

- Código-fonte DEVE estar em `src/backlog_manager/`.
- Testes DEVE estar em `tests/` na raiz (fora de `src/`).
- Domain DEVE conter: `entities/`, `value_objects/`, `services/`,
  `interfaces/`, `exceptions/`.
- Application DEVE conter: `use_cases/`, `dto/`, `interfaces/`.
- Infrastructure DEVE conter: `database/` (com `repositories/`,
  `migrations/`, `schema.sql`, `sqlite_connection.py`,
  `unit_of_work.py`) e `excel/`.
- Presentation DEVE conter: `views/` (janelas e dialogs PySide6),
  `viewmodels/` (lógica de apresentação).
- Testes unitários DEVEM ficar em `tests/unit/` e testes de
  integração em `tests/integration/`.

**Referência**:

```
backlog_manager_v2/                    # Raiz do repositório
├── src/
│   └── backlog_manager/               # Pacote importável
│       ├── __init__.py
│       ├── domain/
│       │   ├── __init__.py
│       │   ├── entities/              # Story, Developer, Feature
│       │   ├── value_objects/         # StoryPoint, StoryStatus
│       │   ├── services/              # BacklogSorter, ScheduleCalculator
│       │   ├── interfaces/            # Repository interfaces (Protocols)
│       │   └── exceptions/            # Domain exceptions
│       ├── application/
│       │   ├── __init__.py
│       │   ├── use_cases/
│       │   ├── dto/                   # StoryDTO, DeveloperDTO, etc.
│       │   └── interfaces/            # Interfaces de serviços externos
│       ├── infrastructure/
│       │   ├── __init__.py
│       │   ├── database/
│       │   │   ├── __init__.py
│       │   │   ├── repositories/      # Implementações SQLite
│       │   │   ├── migrations/        # Schema migrations
│       │   │   ├── schema.sql         # Schema do banco
│       │   │   ├── sqlite_connection.py
│       │   │   └── unit_of_work.py    # Transações
│       │   └── excel/
│       │       ├── __init__.py
│       │       └── openpyxl_excel_service.py
│       └── presentation/
│           ├── __init__.py
│           ├── viewmodels/            # Lógica de apresentação (MVVM)
│           └── views/                 # Janelas e dialogs PySide6
├── tests/
│   ├── __init__.py
│   ├── unit/                          # Rápidos (< 1ms), sem I/O
│   │   ├── __init__.py
│   │   ├── domain/
│   │   └── application/
│   └── integration/                   # Com I/O real (SQLite, Excel)
│       ├── __init__.py
│       └── infrastructure/
├── pyproject.toml
├── CHANGELOG.md
├── LICENSE
└── README.md
```

**Justificativa**: O src layout isola o pacote importável do
restante do repositório, evita conflitos de imports e garante
que somente código de produção seja empacotado. Violação deste
princípio constitui não-conformidade.

### VIII. Programação Assíncrona (asyncio)

Todo código que realiza operações de I/O é implementado usando
async/await com asyncio. A camada Domain permanece síncrona por
design; operações assíncronas ficam em Application e
Infrastructure.

**Requisitos**:

- Application layer DEVE usar async/await: métodos de use cases
  DEVEM retornar `Awaitable` ou ser corrotinas (`async def`).
- Infrastructure layer DEVE usar async/await: repositórios,
  serviços de Excel e operações de banco DEVEM ser assíncronas
  (`aiosqlite` para SQLite, `aiofiles` para I/O).
- Domain layer NÃO DEVE usar async/await (síncrono por design).
- Presentation layer (PySide6) DEVE coordenar com event loop de
  asyncio (integração via qasync).
- `asyncio.run()` DEVE ser chamado apenas no ponto de entrada
  (main).
- Callbacks síncronos que chamam `async` DEVEM usar
  `asyncio.create_task()` ou similares.
- NÃO DEVE usar `asyncio.run()` dentro de função assíncrona.

**Referência**:

```python
from typing import Awaitable
from collections.abc import Coroutine

async def fetch_story(story_id: int) -> Story:
    ...

def use_case_method(story_id: int) -> Awaitable[Story]:
    return fetch_story(story_id)

class StoryRepositoryAsync(Protocol):
    async def find_by_id(self, story_id: int) -> Story:
        ...
```

**Justificativa**: Programação assíncrona melhora a
responsividade em operações de I/O, evitando bloqueios, e
permite adaptação futura para arquiteturas multi-usuário.
Violação deste princípio constitui não-conformidade.

### IX. Simplicidade e Legibilidade

Código é implementado de forma simples e limpa, priorizando
legibilidade e manutenção. Os princípios KISS, DRY e YAGNI
orientam todas as decisões de implementação, favorecendo
clareza sobre complexidade.

**Requisitos**:

- A solução mais simples que resolve o problema DEVE ser
  preferida (KISS).
- Duplicação de código DEVE ser eliminada através de abstração
  apropriada (DRY).
- Funcionalidades especulativas NÃO DEVEM ser implementadas
  (YAGNI).
- Código legível DEVE ser preferido a código compacto ou
  "inteligente" que requer explicação.
- Variáveis, funções e classes DEVEM ter nomes descritivos que
  expliquem seu propósito.
- Funções DEVEM ter no máximo 30-40 linhas (exceto I/O em
  massa); uma função = uma responsabilidade.
- Comentários DEVEM explicar POR QUE, não O QUÊ.
- Valores constantes DEVEM ter nomes descritivos (sem magic
  numbers/strings).
- PEP 8 DEVE ser seguido (validador black ou flake8 em CI/CD).
- Nesting DEVE ter no máximo 3 níveis preferencialmente.
- Princípios SOLID DEVEM ser aplicados quando pertinente.

**Justificativa**: Código legível e simples reduz bugs, facilita
manutenção e onboarding, e reduz dívida técnica. Violação deste
princípio constitui não-conformidade.

### X. Type Hints Obrigatórios

Todo código Python possui type hints para segurança de tipos,
suporte de IDE e documentação inline. Mypy em modo strict valida
a conformidade continuamente.

**Requisitos**:

- Type hints DEVEM estar em todas as assinaturas de função
  (parâmetros e tipos de retorno).
- Type hints DEVEM estar em atributos de classe.
- Tipo `Any` NÃO DEVE ser utilizado a menos que absolutamente
  necessário (documentar justificativa).
- Mypy em modo strict DEVE estar habilitado.
- CI/CD DEVE falhar se mypy reportar erros.

**Justificativa**: Segurança de tipos detecta bugs em tempo de
desenvolvimento, melhora o suporte da IDE e serve como
documentação inline. Violação deste princípio constitui
não-conformidade.

### XI. Docstrings em Código Público

Classes e métodos públicos possuem docstrings que documentam
comportamento esperado, parâmetros e valores de retorno. O
formato padronizado garante consistência na documentação gerada.

**Requisitos**:

- Todas as classes públicas DEVEM ter docstrings.
- Todos os métodos públicos DEVEM ter docstrings.
- Formato Google style DEVE ser utilizado.
- Docstrings DEVEM descrever comportamento, parâmetros e
  retorno.

**Justificativa**: Documenta comportamento esperado, facilita
manutenção e habilita geração automática de documentação.
Violação deste princípio constitui não-conformidade.

### XII. Organização de Imports (isort)

Imports são organizados de forma consistente com isort,
seguindo ordem padronizada: standard library, third-party e
local. A ordenação automática evita conflitos e facilita
revisão de código.

**Requisitos**:

- Imports DEVEM ser organizados com isort.
- Ordem obrigatória: (1) Standard library, (2) Third-party,
  (3) Local.
- `isort src/backlog_manager/` DEVE ser executado antes de
  commits.

**Referência**:

```python
import datetime
from typing import Protocol

from openpyxl import Workbook

from backlog_manager.domain.entities.story import Story
```

**Justificativa**: Organização consistente de imports facilita
leitura, revisão e evita conflitos de merge. Violação deste
princípio constitui não-conformidade.

### XIII. Convenções de Nomenclatura

Nomes de classes, funções, variáveis e constantes seguem
convenções padronizadas que garantem uniformidade e
previsibilidade na navegação do código.

**Requisitos**:

- Classes e type aliases DEVEM usar PascalCase.
- Funções, métodos e variáveis DEVEM usar snake_case.
- Constantes DEVEM usar UPPER_SNAKE_CASE.
- Membros privados DEVEM usar prefixo underscore (`_`).

**Referência**:

| Tipo            | Convenção        | Exemplo                   |
|-----------------|------------------|---------------------------|
| Classes         | PascalCase       | `BacklogSorter`           |
| Funções/Métodos | snake_case       | `calculate_duration`      |
| Variáveis       | snake_case       | `story_points`            |
| Constantes      | UPPER_SNAKE_CASE | `DEFAULT_MAX_ITERATIONS`  |
| Privados        | _prefixo         | `_validate_cycle`         |
| Type Aliases    | PascalCase       | `StoryList`               |

**Justificativa**: Convenção uniforme facilita navegação, reduz
ambiguidade e alinha o projeto com os padrões da comunidade
Python. Violação deste princípio constitui não-conformidade.

### XIV. Estratégia de Testes

A meta de cobertura é 80%+ do código (mínimo aceitável: 70%,
conforme RNF-MANT-001). Módulos core (entities, services,
allocation) DEVEM ter 100% de cobertura. Testes são organizados
em unitários (rápidos, sem I/O) e de integração (com I/O real).
Testes de GUI utilizam pytest-qt integrado ao loop qasync.

**Requisitos**:

- Testes unitários DEVEM cobrir todas as entidades, value objects
  e serviços de domínio.
- Testes unitários DEVEM cobrir casos de uso (com repositórios
  mockados).
- Testes de integração DEVEM cobrir repositórios e serviços
  externos.
- Pytest DEVE ser o framework de testes, com relatórios de
  cobertura via pytest-cov.
- Testes unitários DEVEM ser rápidos (< 1ms) e sem I/O.
- Testes de integração testam integração com SQLite/Excel.
- Views (UI visual) PODEM ter cobertura menor, dada a
  complexidade de testes de framework.
- Testes que abrem janelas, diálogos ou interagem com sinais
  PySide6 DEVEM usar pytest-qt com fixtures `qtbot`/`qeventloop`.
- Testes de GUI DEVEM rodar sobre o loop qasync, aguardando
  corrotinas via `await` ou `qtbot.waitSignal`, evitando
  `time.sleep()`.
- Cada suíte de GUI DEVE documentar como pytest-qt e qasync são
  combinados (fixtures, sincronização, eventos assíncronos).

**Referência**:

```
tests/
├── unit/                      # Rápidos (< 1ms), sem I/O
│   ├── domain/
│   └── application/
└── integration/               # Com I/O real (SQLite, Excel)
    └── infrastructure/
```

| Módulo                  | Cobertura Alvo |
|-------------------------|----------------|
| domain/entities         | 100%           |
| domain/services         | 100%           |
| application/use_cases   | 100%           |
| infrastructure          | 80%            |
| presentation/viewmodels | 80%            |
| presentation/views      | 50% (mínimo)   |

**Justificativa**: Alta cobertura de testes garante
confiabilidade, detecta regressões cedo e documenta
comportamento esperado. pytest-qt com qasync mantém a suíte
homogênea e compatível com código assíncrono. Violação deste
princípio constitui não-conformidade.

### XV. Idioma

Documentação e código seguem convenções idiomáticas separadas:
documentação em português para acessibilidade da equipe, código
em inglês para alinhamento com a comunidade Python
internacional.

**Requisitos**:

- Documentação, docstrings e especificações DEVEM ser escritas
  em português.
- Código DEVE ser escrito em inglês.
- Nomes de arquivo DEVEM ser em inglês.
- Logs DEVEM ser escritos em português (ver Princípio XVII).
- Mensagens de erro exibidas ao usuário DEVEM ser em português.

**Justificativa**: Separação idiomática mantém código acessível
internacionalmente e documentação compreensível para a equipe.
Violação deste princípio constitui não-conformidade.

### XVI. Tratamento de Erros

O sistema utiliza uma hierarquia de exceções bem definida para
diferenciar erros de domínio, de infraestrutura e de aplicação.
Exceções de domínio são recuperáveis e informativas; erros de
infraestrutura são encapsulados antes de chegarem ao domínio.

**Requisitos**:

- Exceções de domínio DEVEM herdar de `BacklogManagerException`.
- Validações de entidade (ID vazio, SP inválido, etc.) DEVEM
  lançar `ValueError` com mensagem descritiva em português.
- Exceções de dependência DEVEM herdar de `DependencyException`.
- Exceções de feature DEVEM herdar de `FeatureException`.
- Exceções de alocação DEVEM herdar de `AllocationException`.
- Warnings (não-bloqueantes) DEVEM herdar de `BacklogWarning`.
- Erros de infraestrutura (I/O, banco) DEVEM ser capturados e
  convertidos em exceções de aplicação antes de propagarem.
- Mensagens de exceção DEVEM ser claras, em português, e
  indicar a causa e possível solução.
- Erros NÃO DEVEM crashar a aplicação; DEVEM ser tratados e
  exibidos ao usuário (conforme RNF-CONF-002).

**Referência**:

```python
Exception
├── ValueError  # Built-in, usado para validações de entidade
│
└── BacklogManagerException  # Base customizada
    ├── DependencyException
    │   ├── CyclicDependencyException
    │   └── InvalidWaveDependencyException
    │
    ├── FeatureException
    │   ├── DuplicateWaveException
    │   └── FeatureHasStoriesException
    │
    └── AllocationException
        └── MaxIterationsExceeded

Warning
└── BacklogWarning
    ├── DeadlockWarning
    ├── IdlenessWarning
    └── BetweenWavesIdlenessInfo
```

| Exceção                        | Condição de Disparo                    |
|--------------------------------|----------------------------------------|
| `ValueError`                   | ID/Nome/Componente vazio, SP inválido  |
| `CyclicDependencyException`    | Ciclo detectado em dependências        |
| `InvalidWaveDependencyException` | Depende de história em onda posterior |
| `DuplicateWaveException`       | Onda já existe em outra feature        |
| `FeatureHasStoriesException`   | Deletar feature com histórias          |
| `DeadlockWarning`              | Nenhum progresso na alocação da onda   |
| `IdlenessWarning`              | Gap > max_idle_days dentro da onda     |

**Justificativa**: Hierarquia de exceções clara facilita
tratamento específico de erros, melhora a experiência do
usuário com mensagens úteis e garante estabilidade da
aplicação. Violação deste princípio constitui não-conformidade.

### XVII. Logging e Observabilidade

O sistema implementa logging estruturado para diagnóstico,
auditoria e troubleshooting. Logs são persistidos em arquivo
com rotação automática, utilizando níveis padronizados.

**Requisitos**:

- Logs DEVEM ser escritos em arquivo texto simples (`.log`).
- Arquivo de log DEVE estar em `%APPDATA%/backlog_manager/` no
  Windows (ou `~/.config/backlog_manager/` no Linux).
- Rotação DEVE ocorrer por tamanho, máximo 10MB por arquivo.
- Sistema DEVE manter os últimos 3 arquivos de log.
- Formato de linha DEVE incluir: timestamp (ISO 8601), nível,
  módulo e mensagem.
- Níveis DEVEM seguir a convenção Python: DEBUG, INFO, WARNING,
  ERROR, CRITICAL.
- Mensagens de log DEVEM ser escritas em português.
- Operações críticas DEVEM gerar log INFO: alocação automática,
  import/export Excel, migrações de banco.
- Erros e exceções DEVEM gerar log ERROR com stack trace.
- Warnings de negócio (deadlock, ociosidade) DEVEM gerar log
  WARNING.
- Código de produção NÃO DEVE usar `print()`; DEVE usar logger.

**Referência**:

```python
import logging

logger = logging.getLogger(__name__)

# Formato
"%(asctime)s - %(levelname)s - %(name)s - %(message)s"

# Exemplo de uso
logger.info("Alocação automática iniciada: %d histórias", count)
logger.warning("Deadlock detectado na onda %d", wave)
logger.error("Falha ao salvar história: %s", str(exc), exc_info=True)
```

| Nível    | Uso                                           |
|----------|-----------------------------------------------|
| DEBUG    | Detalhes de execução (desabilitado em prod)   |
| INFO     | Operações normais (alocação, import/export)   |
| WARNING  | Situações anômalas recuperáveis (deadlock)    |
| ERROR    | Erros que afetam funcionalidade               |
| CRITICAL | Falhas que impedem funcionamento do sistema   |

**Justificativa**: Logging estruturado facilita diagnóstico de
problemas, auditoria de operações e análise de incidentes.
Rotação evita consumo excessivo de disco. Violação deste
princípio constitui não-conformidade.

### XVIII. Gestão de Configuração

Parâmetros configuráveis do sistema são centralizados em uma
entidade de configuração persistida, com valores padrão
sensatos e validação de limites. Configurações são acessadas
via repositório, seguindo o mesmo padrão das demais entidades.

**Requisitos**:

- Parâmetros configuráveis DEVEM ser definidos na entidade
  `Configuration` do domínio.
- Configuração DEVE ser persistida em SQLite (tabela própria).
- Valores padrão DEVEM ser definidos na entidade:
  - `velocity`: 2.0 SP/dia
  - `max_idle_days`: 3 (mínimo: 2, máximo: 30)
  - `start_date`: data atual
- Validação de limites DEVE ocorrer no construtor da entidade.
- Acesso a configuração DEVE ser via `ConfigurationRepository`.
- Use cases que dependem de configuração DEVEM receber valores
  via parâmetros, não acessar repositório diretamente.
- Alterações de configuração DEVEM ser imediatamente persistidas.

**Referência**:

```python
@dataclass
class Configuration:
    """Configuração global do sistema."""

    velocity: float = 2.0  # SP/dia
    max_idle_days: int = 3  # dias úteis
    start_date: date = field(default_factory=date.today)

    def __post_init__(self) -> None:
        if self.velocity <= 0:
            raise ValueError("Velocidade deve ser positiva")
        if not 2 <= self.max_idle_days <= 30:
            raise ValueError("max_idle_days deve estar entre 2 e 30")
```

| Parâmetro       | Tipo  | Padrão      | Limites        | Origem SRS   |
|-----------------|-------|-------------|----------------|--------------|
| `velocity`      | float | 2.0         | > 0            | RF-SCHED-001 |
| `max_idle_days` | int   | 3           | 2–30           | RF-ALOC-009  |
| `start_date`    | date  | date.today  | não nulo       | RF-SCHED-001 |

**Justificativa**: Centralização de configuração evita magic
numbers espalhados pelo código, facilita customização pelo
usuário e garante consistência de valores. Violação deste
princípio constitui não-conformidade.

### XIX. Padrões de UI/UX (PySide6)

A camada de apresentação utiliza o padrão MVVM (Model-View-
ViewModel) para separar lógica de apresentação da interface
visual. Views são responsáveis apenas por renderização e
captura de eventos; ViewModels contêm a lógica de apresentação.

**Requisitos**:

- Views (QWidget, QDialog, QMainWindow) DEVEM conter apenas
  código de UI (layout, widgets, conexão de sinais).
- Lógica de apresentação (formatação, validação de formulário,
  estado de UI) DEVE ficar em ViewModels.
- ViewModels DEVEM expor dados via properties e sinais Qt.
- Views NÃO DEVEM importar de domain ou infrastructure.
- Views DEVEM importar apenas de viewmodels e application/dto.
- Operações assíncronas DEVEM usar qasync para integração com
  Qt event loop.
- Latência de resposta DEVE ser ≤ 100ms para operações CRUD
  simples (RNF-PERF-002).
- Interface DEVE ser funcional em resolução mínima 1366x768
  (RNF-USAB-002).
- Contraste mínimo DEVE ser 4.5:1 (WCAG AA, RNF-USAB-003).
- Navegação por teclado (Tab/Shift+Tab) DEVE ser suportada.
- Tooltips descritivos DEVEM estar presentes em ícones.

**Referência**:

```python
# ViewModel
class StoryListViewModel(QObject):
    stories_changed = Signal()
    loading = Signal(bool)

    def __init__(self, list_stories_use_case: ListStoriesUseCase):
        super().__init__()
        self._use_case = list_stories_use_case
        self._stories: list[StoryDTO] = []

    @property
    def stories(self) -> list[StoryDTO]:
        return self._stories

    async def load_stories(self) -> None:
        self.loading.emit(True)
        self._stories = await self._use_case.execute()
        self.stories_changed.emit()
        self.loading.emit(False)

# View
class StoryListView(QWidget):
    def __init__(self, viewmodel: StoryListViewModel):
        super().__init__()
        self._vm = viewmodel
        self._vm.stories_changed.connect(self._refresh_table)
        self._vm.loading.connect(self._show_loading)
```

**Justificativa**: Separação View/ViewModel facilita testes de
lógica de apresentação sem depender de Qt, melhora
manutenibilidade e permite reutilização de ViewModels.
Violação deste princípio constitui não-conformidade.

### XX. Validação e Sanitização de Entrada

Toda entrada do usuário é validada e sanitizada antes de
chegar ao domínio. A sanitização ocorre na camada de
apresentação (ViewModels) ou aplicação (Use Cases), nunca
no domínio.

**Requisitos**:

- Campos de texto DEVEM ser sanitizados: trim de espaços,
  remoção de caracteres de controle.
- Queries SQL DEVEM usar parâmetros (prepared statements),
  nunca concatenação de strings.
- Entrada de arquivos Excel DEVE ser validada: formato de
  colunas, tipos de dados, limites.
- IDs de referência (developer_id, feature_id, depends_on)
  DEVEM ser validados quanto à existência antes de
  processamento.
- Strings vazias ou apenas espaços DEVEM ser rejeitadas para
  campos obrigatórios.
- Valores numéricos DEVEM ser validados quanto a limites
  (ex: story_points in {3, 5, 8, 13}).
- Datas DEVEM ser validadas quanto a formato e consistência
  (start_date <= end_date).
- Mensagens de validação DEVEM ser claras e em português.

**Referência**:

```python
# Na ViewModel ou UseCase
def sanitize_text(value: str | None) -> str:
    """Remove espaços e caracteres de controle."""
    if value is None:
        return ""
    # Remove caracteres de controle
    cleaned = "".join(c for c in value if c.isprintable() or c.isspace())
    return cleaned.strip()

def validate_story_points(value: int) -> None:
    """Valida story points conforme escala Fibonacci."""
    valid_points = {3, 5, 8, 13}
    if value not in valid_points:
        raise ValueError(
            f"Story Points deve ser 3, 5, 8 ou 13 (recebido: {value})"
        )
```

| Camada       | Responsabilidade                            |
|--------------|---------------------------------------------|
| Presentation | Sanitização de texto, formatação de entrada |
| Application  | Validação de regras de negócio              |
| Domain       | Invariantes de entidade (fail fast)         |

**Justificativa**: Validação em camadas múltiplas com
sanitização na entrada previne vulnerabilidades (SQL injection,
dados malformados) e garante que apenas dados válidos cheguem
ao domínio. Violação deste princípio constitui não-conformidade.

### XXI. CI/CD e Qualidade Contínua

O pipeline de integração contínua valida qualidade de código,
testes e segurança a cada commit. Gates de qualidade impedem
merge de código não-conforme.

**Requisitos**:

- Black DEVE ser usado para formatação (line length 88).
- isort DEVE ser usado para organização de imports.
- Mypy em modo strict DEVE validar type hints.
- pytest-cov DEVE gerar relatório de cobertura.
- Cobertura mínima DEVE ser 70%; objetivo é 80%+.
- radon DEVE validar complexidade ciclomática (máximo 10 por
  função, 15 para funções de alocação).
- pydocstyle DEVE validar presença de docstrings.
- pre-commit hooks DEVEM executar black, isort e mypy.
- CI DEVE executar em todo push e pull request.
- CI DEVE falhar se qualquer gate não passar.
- Build (poetry build) DEVE ser validado antes de release.
- Testes DEVEM ser executados em ambiente isolado (sem
  dependência de estado local).

**Referência**:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.x.x
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.x.x
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.x.x
    hooks:
      - id: mypy
        additional_dependencies: [pydantic, PySide6-stubs]
```

| Ferramenta   | Propósito                    | Gate         |
|--------------|------------------------------|--------------|
| black        | Formatação de código         | Obrigatório  |
| isort        | Organização de imports       | Obrigatório  |
| mypy         | Validação de tipos           | Obrigatório  |
| pytest-cov   | Cobertura de testes          | ≥ 70%        |
| radon        | Complexidade ciclomática     | ≤ 10 (15)    |
| pydocstyle   | Docstrings                   | Recomendado  |

**Justificativa**: Gates de qualidade automatizados garantem
consistência do código, detectam problemas cedo e reduzem
dívida técnica. Pre-commit hooks previnem commits
não-conformes. Violação deste princípio constitui
não-conformidade.

## Governance

### Processo de Emenda

- Alterações à constituição DEVEM ser documentadas com
  justificativa e aprovadas antes de aplicação.
- Toda emenda DEVE incluir plano de migração quando afetar
  código existente.

### Versionamento

A constituição segue versionamento semântico (MAJOR.MINOR.PATCH):

- **MAJOR**: remoções ou redefinições incompatíveis de princípios.
- **MINOR**: novos princípios/seções ou expansão material de
  orientação existente.
- **PATCH**: correções de redação, typos, refinamentos
  não-semânticos.

### Conformidade

- Todo PR/review DEVE verificar conformidade com esta
  constituição.
- Complexidade além do prescrito DEVE ser justificada por
  escrito.

**Version**: 1.0.0 | **Ratified**: 2026-02-28 | **Last Amended**: 2026-02-28
