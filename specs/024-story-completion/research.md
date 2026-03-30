# Research: Story Completion Status

**Feature**: 024-story-completion
**Date**: 2026-03-30

## Decisão 1: Onde colocar a validação de dependências para conclusão

**Decisão**: No `EditStoryUseCase`, dentro do método `execute()`, antes de aplicar a mudança de status.

**Racional**: A validação requer I/O (buscar dependências e seus status no banco), portanto pertence à camada Application (use case), não ao Domain. O Domain contribui com a exceção (`IncompleteDependencyException`), mas a orquestração é do use case — conforme Princípio I (Clean Architecture) e VIII (Async).

**Alternativas consideradas**:
- Domain Service síncrono: Rejeitado porque precisaria receber as dependências já carregadas, criando acoplamento desnecessário. O use case já tem acesso ao UoW.
- Middleware/interceptor: Over-engineering para uma validação pontual.
- Validação na Entity `Story`: Rejeitado — a entidade não tem acesso ao estado de outras entidades.

## Decisão 2: Tipo de exceção para rejeição de conclusão

**Decisão**: Nova classe `IncompleteDependencyException` herdando de `DependencyException`, com atributos `story_id`, `incomplete_dependencies` (lista de tuplas `(id, name, status)`).

**Racional**: Segue a hierarquia existente (Princípio XVI). `DependencyException` já é a base para problemas de dependência. A nova exceção carrega dados estruturados para que a UI possa exibir mensagem detalhada (FR-002, US4).

**Alternativas consideradas**:
- Reutilizar `DependencyException` genérica: Rejeitado — perda de informação estruturada para a UI.
- Retornar `Result` object em vez de exceção: Inconsistente com o padrão do projeto que usa exceções para fluxo de erro.

## Decisão 3: Filtro de histórias concluídas no scheduling

**Decisão**: No `CalculateScheduleUseCase`, alterar o filtro existente de `status != BACKLOG → continue` para `status in (CONCLUIDO, ...) → continue`, ou mais precisamente: manter apenas histórias BACKLOG (comportamento atual já correto — scheduling só processa BACKLOG).

**Racional**: O `CalculateScheduleUseCase` (linha 73) já filtra `if story.status != StoryStatus.BACKLOG: continue`. Histórias CONCLUIDO já são excluídas naturalmente. Nenhuma alteração necessária neste use case.

**Alternativas consideradas**:
- Filtro explícito para CONCLUIDO: Desnecessário — o filtro existente (`!= BACKLOG`) já exclui tudo que não é BACKLOG.

## Decisão 4: Filtro de histórias concluídas na alocação

**Decisão**: Adicionar filtro de status no `AllocationService._is_eligible()` para excluir histórias CONCLUIDO.

**Racional**: O `_is_eligible()` atual (linha 167 de `allocation_service.py`) NÃO verifica status — apenas `developer_id`, `start_date`, `end_date`, `story_points`. Uma história CONCLUIDO que tenha developer_id=None (improvável mas possível) poderia ser re-alocada. O filtro explícito garante FR-004.

**Alternativas consideradas**:
- Filtrar no `ExecuteAllocationUseCase`: Possível, mas `_is_eligible()` é o ponto semântico correto para determinar elegibilidade.
- Não filtrar (confiar que CONCLUIDO sempre tem developer_id): Frágil — uma história pode ser concluída sem alocação ou ter seu developer removido.

## Decisão 5: Comportamento ao reverter de CONCLUIDO para outro status

**Decisão**: Permitir sem restrições (FR-006). Não cascatear mudanças em dependentes (FR-008).

**Racional**: O spec é explícito: transições DE Concluído são livres. Dependentes já em CONCLUIDO permanecem inalterados. A próxima tentativa de marcar um dependente como CONCLUIDO falhará se sua dependência não estiver mais concluída.

**Alternativas consideradas**:
- Warn ao reverter se existem dependentes concluídos: Poderia ser útil, mas não está no spec. YAGNI (Princípio IX).
- Bloquear reversão se dependentes estão em CONCLUIDO: Rejeitado — contradiz FR-006.

## Decisão 6: Bug existente no EditStoryInputDTO validator

**Decisão**: Corrigir os valores permitidos no validator de status do `EditStoryInputDTO` de `("BACKLOG", "IN_PROGRESS", "DONE", "BLOCKED")` para `("BACKLOG", "EXECUCAO", "TESTES", "CONCLUIDO", "IMPEDIDO")`.

**Racional**: Bug pré-existente encontrado durante research. O validator tem valores antigos que não correspondem ao enum `StoryStatus`. Este fix é pré-requisito para que a transição de status via DTO funcione.

**Alternativas consideradas**:
- Ignorar (não é do escopo): Rejeitado — impede diretamente o funcionamento desta feature.
