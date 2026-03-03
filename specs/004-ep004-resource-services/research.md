# Pesquisa: EP-004 Gestao de Recursos - Servicos e Aplicacao

**Data**: 2026-03-01
**Status**: Completo

## Visao Geral

Este documento consolida os achados de pesquisa para implementacao do DeveloperService, FeatureService, seus use cases e DTOs. Todas as incertezas tecnicas foram resolvidas atraves da analise dos padroes existentes no codebase dos epicos EP-001, EP-002 e EP-003.

## Tarefas de Pesquisa

### 1. Analise do Padrao de Domain Service

**Pergunta**: Como DeveloperService e FeatureService devem ser estruturados?

**Decisao**: Seguir o padrao do StoryService de EP-003

**Justificativa**:
- StoryService demonstra o padrao estabelecido para domain services
- Recebe repositorio como dependencia no construtor (baseado em Protocol)
- Usa imports TYPE_CHECKING para evitar dependencias circulares
- Metodos sao async para consistencia com operacoes de repositorio
- Encapsula logica de negocio separada dos use cases

**Alternativas Consideradas**:
- Servicos sincronos com wrappers async: Rejeitado - adiciona complexidade, inconsistente com codebase
- Servicos sem dependencia de repositorio: Rejeitado - viola principio DI, dificulta testes

**Referencia**: src/backlog_manager/domain/services/story_service.py

---

### 2. Analise do Padrao de Use Case

**Pergunta**: Como os use cases CRUD devem ser estruturados?

**Decisao**: Seguir o padrao dos story use cases de EP-003

**Justificativa**:
- Use cases recebem interface UnitOfWork via construtor
- Metodo execute recebe input DTO, retorna output DTO
- Toda persistencia acontece dentro do contexto async with uow
- Domain service e instanciado dentro do use case, recebe repositorio do UoW
- Tratamento de erros: lanca ValueError para nao encontrado, excecoes de dominio propagam

**Alternativas Consideradas**:
- Use cases sem UoW: Rejeitado - viola integridade transacional
- Use cases com acesso direto ao repositorio: Rejeitado - bypassa logica de dominio

**Referencia**: src/backlog_manager/application/use_cases/story/create_story.py

---

### 3. Analise do Padrao de DTO

**Pergunta**: Como input/output DTOs devem ser estruturados?

**Decisao**: Usar Pydantic BaseModel com field validators

**Justificativa**:
- Input DTOs usam Pydantic para validacao (decorator field_validator)
- Output DTOs incluem metodo de classe from_entity() para conversao
- Mensagens de validacao em portugues conforme constituicao
- Normalizacao de campos (ex: strip whitespace) nos validators

**Alternativas Consideradas**:
- Dataclasses para DTOs: Rejeitado - Pydantic oferece melhor validacao
- Sem validacao em DTOs: Rejeitado - viola principio fail-fast

**Referencia**: src/backlog_manager/application/dto/story/

---

### 4. Extensoes de Protocol de Repositorio

**Pergunta**: Quais novos metodos sao necessarios nos protocols de repositorio?

**Decisao**: Adicionar dois metodos conforme especificado em FR-001 e FR-002

**Metodos a Adicionar**:
1. FeatureRepository.get_by_name(name: str) -> Feature | None
   - Necessario para validacao de unicidade antes de create/update
   - Retorna None se nao encontrado (consistente com padrao get_by_wave)

2. StoryRepository.count_by_developer(developer_id: int) -> int
   - Necessario para logging do numero de historias desalocadas ao deletar desenvolvedor
   - Retorna contagem (0 se nenhuma)

**Justificativa**:
- get_by_name habilita validacao fail-fast no FeatureService
- count_by_developer permite resposta informativa de delete sem carregar todas as historias

**Alternativas Consideradas**:
- Usar get_all() e filtrar: Rejeitado - ineficiente, carrega dados desnecessarios
- Depender apenas de constraints do banco: Rejeitado - mensagens de erro pobres

**Referencia**: src/backlog_manager/domain/interfaces/repositories.py

---

### 5. Estrategia de Tratamento de Excecoes

**Pergunta**: Quais excecoes os servicos devem lancar?

**Decisao**: Usar hierarquia de excecoes existente

**Mapeamento de Excecoes**:

| Cenario | Excecao | Origem |
|---------|---------|--------|
| Desenvolvedor nao encontrado | ValueError | DeveloperService |
| Feature nao encontrada | ValueError | FeatureService |
| Wave duplicada | DuplicateWaveException | FeatureService (existente) |
| Nome de feature duplicado | ValueError | FeatureService |
| Feature tem historias | FeatureHasStoriesException | FeatureService (existente) |
| Nome/wave invalido | ValueError | Validacao da entidade |

**Justificativa**:
- ValueError para nao encontrado segue padrao EP-003 (EditStoryUseCase)
- Excecoes de dominio (DuplicateWaveException, FeatureHasStoriesException) ja existem
- Mensagens de erro consistentes em portugues

**Referencia**: src/backlog_manager/domain/exceptions/

---

### 6. Desalocacao de Historias

**Pergunta**: Como tratar desalocacao de historias ao deletar desenvolvedor?

**Decisao**: Confiar no ON DELETE SET NULL (ADR-001 na spec)

**Justificativa**:
- Schema SQLite ja tem ON DELETE SET NULL na FK developer_id
- Banco trata desalocacao atomicamente na mesma transacao
- Servico apenas precisa contar historias ANTES de deletar para resposta informativa
- Nenhum UPDATE explicito necessario - mais simples, menos propenso a erros

**Alternativas Consideradas**:
- Desalocacao explicita antes de delete: Rejeitado - redundante, adiciona complexidade
- Sem retorno de contagem: Rejeitado - usuario perde visibilidade do impacto

---

### 7. Protecao de Delecao de Feature

**Pergunta**: Como proteger delecao de feature quando existem historias?

**Decisao**: Servico valida antes de chamar delete do repositorio (ADR-002)

**Justificativa**:
- Fail-fast: detecta erro antes de tentar deletar
- Melhor mensagem de erro: pode incluir nome da feature e contagem de historias
- Repositorio tem verificacao de fallback (defesa em profundidade)

---

### 8. Estrategia de Validacao de Unicidade

**Pergunta**: Como validar unicidade de wave e nome para features?

**Decisao**: Servico valida ANTES de criar/atualizar entidade (ADR-003, ADR-004)

**Unicidade de Wave**:
- No create: verificar get_by_wave(wave), lancar DuplicateWaveException se existir
- No update: verificar get_by_wave(wave), excluir a propria (por comparacao de ID)

**Unicidade de Nome**:
- No create: verificar get_by_name(name), lancar ValueError se existir
- No update: verificar get_by_name(name), excluir a propria (por comparacao de ID)

**Ordem de Validacao** (fail-fast, mais especifico primeiro):
1. Validar wave > 0 (entidade fara isso, mas servico pode pre-verificar)
2. Verificar unicidade de wave
3. Verificar unicidade de nome
4. Criar/atualizar entidade

---

### 9. Associacao Historia-Feature

**Pergunta**: EP-004 precisa implementar associacao historia-feature?

**Decisao**: Nao - reutilizar EditStoryUseCase de EP-003 (ADR-005)

**Justificativa**:
- EP-003 ja implementa EditStoryUseCase com parametro feature_id
- Update de historia valida se feature existe via FeatureRepository
- Nenhum codigo duplicado necessario
- User Story 9 e P2 e explicitamente declara reuso

---

### 10. Assinaturas de Metodos do DeveloperService

**Pergunta**: Quais devem ser as assinaturas exatas dos metodos?

**Decisao**: Baseado nos requisitos da spec FR-012 ate FR-021

Metodos:
- __init__(developer_repo, story_repo): Recebe ambos repositorios
- create_developer(name) -> Developer: Cria entidade (sem persistir)
- update_developer(developer_id, name) -> Developer: Busca, valida, atualiza
- delete_developer(developer_id) -> int: Deleta, retorna contagem desalocada
- list_developers() -> Sequence[Developer]: Todos ordenados por nome

**Nota**: Servico precisa de DeveloperRepository e StoryRepository (para count_by_developer).

---

### 11. Assinaturas de Metodos do FeatureService

**Pergunta**: Quais devem ser as assinaturas exatas dos metodos?

**Decisao**: Baseado nos requisitos da spec FR-032 ate FR-046

Metodos:
- __init__(feature_repo): Recebe FeatureRepository
- create_feature(name, wave) -> Feature: Valida unicidade, cria entidade
- update_feature(feature_id, name=None, wave=None) -> Feature: Update parcial
- delete_feature(feature_id) -> None: Verifica sem historias, deleta
- list_features() -> Sequence[Feature]: Todas ordenadas por wave

---

## Resumo

Todas as tarefas de pesquisa concluidas. Nenhum item NEEDS CLARIFICATION restante. A implementacao ira:

1. **Seguir padroes existentes** de EP-003 para services, use cases e DTOs
2. **Estender protocols de repositorio** com get_by_name e count_by_developer
3. **Usar excecoes existentes** (DuplicateWaveException, FeatureHasStoriesException)
4. **Confiar no banco** para desalocacao de historias (ON DELETE SET NULL)
5. **Validar nos servicos** para comportamento fail-fast com erros informativos
6. **Reutilizar EP-003** para associacao historia-feature (nenhum codigo novo necessario)
