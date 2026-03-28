# Prompt: Criar Especificação Técnica do EP-002

<role>
Você é um Arquiteto de Software Sênior especializado em Domain-Driven Design (DDD) e
Clean Architecture, com profundo conhecimento de Python 3.11+, dataclasses, value objects,
validação de invariantes e design de entidades ricas. Você produz especificações técnicas
precisas, rastreáveis a requisitos, e implementáveis de forma incremental.
</role>

<context>
## Projeto: Backlog Manager v2

Aplicação desktop standalone em Python (PySide6 + SQLite) para gestão de backlog.
Single-user, sem rede, interface em PT-BR, plataforma Windows.

### Stack Técnica (Definida em EP-001)
- **Linguagem**: Python 3.11+ com type hints completas
- **Packaging**: Poetry
- **Persistência**: aiosqlite (async SQLite)
- **DTOs**: Pydantic
- **Testes**: pytest + pytest-cov + pytest-asyncio
- **Qualidade**: black, isort, ruff, mypy
- **Arquitetura**: 4 camadas — Presentation → Infrastructure → Application → Domain
- **Padrões**: Repository Pattern (Protocol), DDD (entidades ricas, VOs, invariantes no construtor)

### Estado Atual do Código (Implementado em EP-001)

As entidades e value objects **já existem** com implementação básica:

**Value Objects existentes:**
- `src/backlog_manager/domain/value_objects/story_point.py` — `StoryPoint(IntEnum)` com valores {3, 5, 8, 13}
- `src/backlog_manager/domain/value_objects/story_status.py` — `StoryStatus(StrEnum)` com 4 estados: BACKLOG, IN_PROGRESS, BLOCKED, DONE

**Entidades existentes:**
- `src/backlog_manager/domain/entities/story.py` — `Story(dataclass)` com validações de ID (padrão COMPONENTE-NNN), component, name, story_points, priority. **Não possui** campo `dependencies` nem validação de auto-dependência.
- `src/backlog_manager/domain/entities/developer.py` — `Developer(dataclass)` com validação de name.
- `src/backlog_manager/domain/entities/feature.py` — `Feature(dataclass)` com validação de name e wave > 0.

**Exceções existentes:**
- Hierarquia completa em `src/backlog_manager/domain/exceptions/` (BacklogManagerException, DependencyException, FeatureException, AllocationException, etc.)

**Repositórios existentes:**
- Protocols em `src/backlog_manager/domain/interfaces/repositories.py`
- Implementações SQLite em `src/backlog_manager/infrastructure/database/repositories/`

### ⚠️ Conflitos Conhecidos (Épico vs. Código Atual)

Estes conflitos DEVEM ser resolvidos na especificação com decisão explícita:

1. **StoryStatus**: Código atual tem 4 estados em **inglês** (BACKLOG, IN_PROGRESS, BLOCKED, DONE).
   Épico EP-002 exige 5 estados **sem acento** (BACKLOG, EXECUCAO, TESTES, CONCLUIDO, IMPEDIDO)
   conforme SRS §6.5. → A spec deve definir qual versão prevalece e como migrar.

2. **Story.dependencies**: O épico exige validação de auto-dependência ("história não pode depender
   de si mesma"), mas Story **não possui** campo de dependências. Dependências são gerenciadas pela
   tabela `Story_Dependency` e pelo repositório. → A spec deve decidir se a validação fica na
   entidade, no serviço de domínio, ou no repositório.

3. **Story.duration**: Épico referencia §8.3 com regra "duração mínima = 1", mas o código atual
   aceita `duration: int | None = None`. → Definir se duration=0 é válido.

4. **Story.developer_id**: Épico menciona validação de "string vazia ou apenas espaços" para
   developer_id, mas no schema o developer_id é `INTEGER NULL`. → Clarificar se validação se
   aplica ou se é herança de uma versão anterior do SRS.
</context>

<input>
Leia e analise os seguintes arquivos **obrigatoriamente** antes de gerar a especificação:

1. **Épico fonte**: `docs/epics/EP-002_dominio-core-entidades.md` — requisitos, escopo, critérios de aceite
2. **SRS completo**: `srs.md` — seções §6.5 (máquina de estados), §8.2 (convenções), §8.3 (regras implícitas)
3. **Spec de referência (template)**: `specs/001-ep001-foundation-persistence/spec.md` — formato e nível de detalhe esperado
4. **Plan de referência (template)**: `specs/001-ep001-foundation-persistence/plan.md` — estrutura do plano de implementação
5. **Tasks de referência (template)**: `specs/001-ep001-foundation-persistence/tasks.md` — formato das tasks
6. **Código existente das entidades** (para entender o que já existe e o que precisa mudar):
   - `src/backlog_manager/domain/entities/story.py`
   - `src/backlog_manager/domain/entities/developer.py`
   - `src/backlog_manager/domain/entities/feature.py`
   - `src/backlog_manager/domain/value_objects/story_point.py`
   - `src/backlog_manager/domain/value_objects/story_status.py`
7. **Exceções existentes**: `src/backlog_manager/domain/exceptions/` (todos os arquivos)
8. **Contracts de referência**: `specs/001-ep001-foundation-persistence/contracts/` — formato dos contratos
</input>

<task>
Crie a **especificação técnica completa** para o épico `EP-002 — Domínio Core: Entidades e Validações`.

A especificação deve cobrir **exclusivamente** o escopo do épico:
- RF-STORY-008 (Validar Story Points)
- RF-STORY-009 (Gerenciar Status — máquina de estados §6.5)
- RF-STORY-010 (Validar Invariantes — ID, component, nome, prioridade, duração, auto-dependência)

**IMPORTANTE**: Este épico **não** cria entidades do zero. Ele **aprimora e completa** as
entidades já existentes (criadas como scaffolding em EP-001), adicionando:
- Validações de invariantes completas que faltam
- Máquina de estados corrigida/expandida conforme SRS §6.5
- Regras de negócio implícitas do SRS §8.3
- Testes unitários com 100% de cobertura para validações
</task>

<rules>
### Regras de Qualidade da Especificação

1. **Rastreabilidade bidirecional**: Todo FR-xxx na spec deve mapear para um RF do SRS. Todo RF do
   escopo do épico deve ter pelo menos um FR correspondente.

2. **Código existente prevalece como baseline**: Não redefinir o que já está implementado e
   funcionando. Especificar apenas **deltas** (o que adicionar, modificar ou corrigir).

3. **Conflitos resolvidos explicitamente**: Para cada conflito listado em `<context>`, a spec
   deve conter uma seção "Decisão Arquitetural" com: Contexto, Opções, Decisão, Justificativa.

4. **Mensagens de erro exatas**: Toda validação deve especificar a mensagem de erro literal
   (sem acentos, conforme §8.2).

5. **Testabilidade**: Cada FR deve ser verificável por um teste unitário específico. A spec
   deve tornar trivial derivar os testes.

6. **Sem sobreposição com EP-001 ou EP-003+**: Não re-especificar o que EP-001 já entregou
   (schema, repositórios, exceções base). Não antecipar CRUD de EP-003.

7. **Consistência de nomenclatura**: Usar os mesmos nomes de classe, método e campo já
   existentes no código. Se um rename for necessário, documentar como breaking change com
   migration path.
</rules>
