<role>
Você é um Engenheiro de Software Sênior especializado em:
- Arquitetura Python com Clean Architecture (4 camadas: UI → Services → Domain → Repository)
- Banco de dados SQLite com gestão de schema, constraints e transações ACID
- Configuração de projetos Python modernos (pyproject.toml, pre-commit, pytest)
- Redação de especificações técnicas de implementação com nível de detalhe suficiente para execução direta

Você produz especificações que um desenvolvedor (ou agente de IA) consegue implementar sem precisar interpretar decisões ambíguas.
</role>

<context>
## Projeto
**Backlog Manager v2** — Aplicação desktop standalone em Python 3.11+ (PySide6 + SQLite) para planejamento inteligente de backlog de desenvolvimento. Single-user, Windows, interface PT-BR.

## Artefatos de Referência
1. **SRS completo:** `srs.md` — Contém TODOS os requisitos, modelos e regras do projeto
2. **Épico a especificar:** `docs/epics/EP-001_fundacao-e-persistencia.md` — Épico de infraestrutura/fundação
3. **Roadmap:** `docs/epics/ROADMAP.md` — Sequência de 9 épicos; EP-001 é o primeiro e **todos os demais dependem dele**

## Natureza do EP-001
Este é um **épico de infraestrutura** (sem requisitos funcionais próprios). Ele produz os alicerces técnicos que habilitam os 8 épicos subsequentes:
- **Estrutura de projeto** com 4 camadas (§6.1 do SRS)
- **Banco de dados SQLite** com schema das 4 tabelas: Story, Story_Dependency, Developer, Feature (§6.4 do SRS)
- **Hierarquia de exceções customizadas** e warnings (§7.3 do SRS)
- **Sistema de logging** com rotação em AppData (RNF-CONF-005)
- **Pipeline de qualidade de código**: pytest-cov, black, isort, pydocstyle, pre-commit (RNF-MANT-001 a 004)
- **Configuração de empacotamento** (`pyproject.toml` / `setup.cfg`) com `pip install -e .`

## RNFs Cobertos
| ID | Requisito | Métrica |
|----|-----------|---------|
| RNF-MANT-001 | Cobertura de testes | ≥ 80% linhas, 100% core |
| RNF-MANT-002 | Docstrings Google Style | 100% classes/métodos públicos |
| RNF-MANT-003 | Complexidade ciclomática | ≤ 10 (≤ 15 para alocação) |
| RNF-MANT-004 | PEP 8, Black (88 cols), isort, type hints | 0 warnings |
| RNF-CONF-003 | Integridade de dados | Transações ACID, FKs enforced |
| RNF-CONF-004 | Persistência imediata | Commit após cada operação |
| RNF-CONF-005 | Logs em AppData | Rotação 10MB, 3 arquivos |
| RNF-SEG-001 | Prepared statements | 100% das queries |
| RNF-SEG-003 | Banco em AppData | Permissões de usuário |
</context>

<input>
Leia **integralmente** os seguintes arquivos antes de iniciar a especificação:
1. `srs.md` — com atenção especial às seções: **§6.1** (arquitetura), **§6.4** (modelo ER com tipos, constraints, PKs, FKs, CHECKs), **§7.3** (hierarquia de exceções), **§8.2** (convenções de nomenclatura), **§8.3** (regras implícitas)
2. `docs/epics/EP-001_fundacao-e-persistencia.md` — escopo, critérios de aceite e plano de validação
3. `docs/epics/ROADMAP.md` — para entender o que os épicos dependentes (EP-002 a EP-009) esperam que EP-001 entregue
</input>

<task>
Crie uma **especificação técnica de implementação** para o épico EP-001, decompondo-o em **entregáveis concretos e implementáveis**.

A especificação deve ser:
- **Prescritiva**: dizer exatamente O QUE criar (nomes de arquivos, funções, classes, schemas SQL)
- **Auto-contida**: conter toda informação necessária para implementar, sem necessidade de voltar ao SRS
- **Ordenada**: os entregáveis devem estar em ordem de implementação (o que vem antes habilita o que vem depois)
- **Verificável**: cada entregável deve ter critérios de aceite testáveis
</task>

<requirements>
## Entregáveis da Especificação

Para CADA um dos entregáveis abaixo, a especificação deve conter:

### 1. Estrutura do Projeto
- Árvore de diretórios completa com os módulos/pacotes Python das 4 camadas (§6.1)
- Arquivo `__init__.py` de cada pacote com seus exports planejados
- Rationale: por que esta estrutura e não outra (ex: por que separar `domain/` de `services/`)

### 2. Configuração de Empacotamento
- Conteúdo do `pyproject.toml` (ou `setup.cfg`): dependências, extras de dev, entry points
- Lista **exata** de dependências com versões mínimas (PySide6, openpyxl, pytest, black, isort, etc.)
- Script para verificar instalação correta

### 3. Schema do Banco de Dados
- DDL SQL completo para as 4 tabelas, extraído do §6.4 do SRS, incluindo:
  - Tipos de coluna exatos (VARCHAR(20), INTEGER, DATE, etc.)
  - PRIMARY KEYs, FOREIGN KEYs com ON DELETE
  - CHECK constraints (story_points IN (3,5,8,13), priority >= 0, wave > 0, etc.)
  - UNIQUE constraints (Feature.name, Feature.wave, Story_Dependency(story_id, depends_on_id))
  - DEFAULT values (Story.status = 'BACKLOG')
- Módulo de inicialização do banco: classe/função que cria as tabelas, ativa WAL mode, ativa `PRAGMA foreign_keys = ON`
- Caminho do banco em AppData (`%LOCALAPPDATA%/BacklogManager/backlog.db` ou similar)

### 4. Hierarquia de Exceções
- Módulo Python com TODAS as exceções e warnings do §7.3:
  - `BacklogManagerException` (base)
  - `DependencyException` → `CyclicDependencyException`, `InvalidWaveDependencyException`
  - `FeatureException` → `DuplicateWaveException`, `FeatureHasStoriesException`
  - `AllocationException` → `MaxIterationsExceeded`
  - `BacklogWarning` (base warning) → `DeadlockWarning`, `IdlenessWarning`, `BetweenWavesIdlenessInfo`
- Mensagens padrão e parâmetros do construtor de cada exceção (consultando §7.2 do SRS)

### 5. Sistema de Logging
- Configuração do módulo `logging` do Python:
  - Handler: `RotatingFileHandler` em `%LOCALAPPDATA%/BacklogManager/logs/`
  - Rotação: 10MB por arquivo, retenção de 3 backups
  - Formato do log: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`
  - Níveis: DEBUG para dev, INFO para produção
- Função/classe de inicialização do logging chamada no startup da aplicação

### 6. Pipeline de Qualidade de Código
- Conteúdo do `.pre-commit-config.yaml` com hooks para: black, isort, flake8 (ou ruff), pydocstyle
- Configuração de pytest em `pyproject.toml`: paths, coverage mínimo (80%), plugins
- Configuração de black (line-length=88) e isort (compatível com black)
- Configuração de pydocstyle (Google convention)

### 7. Testes da Fundação
- Testes unitários para:
  - Criação do banco de dados e verificação do schema (todas as tabelas, colunas, constraints)
  - Hierarquia de exceções (herança, mensagens, parâmetros)
  - Inicialização do logging (criação de arquivos, formato)
- Testes de integração para:
  - CRUD básico em cada tabela (INSERT, SELECT, UPDATE, DELETE)
  - Foreign keys enforced (inserir story com developer_id inexistente deve falhar)
  - CHECK constraints (inserir story com story_points=7 deve falhar)
  - Transações ACID (rollback em caso de erro parcial)
</requirements>
