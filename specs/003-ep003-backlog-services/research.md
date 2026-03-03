# Research: EP-003 Gestao de Backlog - Servicos e Aplicacao

**Date**: 2026-02-28
**Status**: Complete

## Executive Summary

Este documento consolida a pesquisa tecnica realizada para o EP-003. Todas as decisoes de design ja estavam definidas na especificacao via ADRs. A pesquisa validou as abordagens e identificou padroes de implementacao a seguir.

## Research Tasks

### 1. Domain Service Pattern para StoryService

**Question**: Qual a melhor abordagem para implementar o StoryService como domain service stateless?

**Decision**: Classe Python pura com metodos async que recebem UnitOfWork como parametro

**Rationale**:
- Domain services sao stateless por definicao (Principio II - DDD)
- StoryService coordena operacoes que envolvem multiplas entidades/repositorios
- Logica de negocio (geracao de ID, calculo de prioridade) fica centralizada
- UnitOfWork injeta repositorios, mantendo o service desacoplado

**Alternatives Considered**:
1. Service com repositorios injetados diretamente - Rejeitado, viola Unit of Work pattern
2. Metodos estaticos em modulo - Rejeitado, dificulta testes e viola OOP do projeto
3. Service como singleton - Rejeitado, desnecessario para aplicacao single-user

### 2. Use Case Pattern para Application Layer

**Question**: Como estruturar os Use Cases para manter coesao e separacao de responsabilidades?

**Decision**: Uma classe por use case com metodo execute(input_dto) retornando output_dto

**Rationale**:
- Single Responsibility Principle - cada use case faz uma coisa
- Interface uniforme facilita composicao e testes
- DTOs garantem contrato claro entre camadas
- UnitOfWork como factory permite transacoes isoladas

**Alternatives Considered**:
1. Service com multiplos metodos - Rejeitado, classes grandes, dificil testar isoladamente
2. Funcoes puras - Rejeitado, sem estado, mas dificulta injecao de dependencias
3. Command pattern com handlers - Rejeitado, over-engineering para 7 operacoes

### 3. Extensao de Protocols de Repositorio

**Question**: Como estender os Protocols existentes sem quebrar implementacoes?

**Decision**: Adicionar novos metodos aos Protocols existentes e implementar nas classes concretas

**Rationale**:
- Protocols sao typing hints, nao interfaces formais - adicionar metodos e seguro
- Mypy detectara metodos faltantes nas implementacoes
- Mantem coesao - metodos relacionados a Story ficam em StoryRepository

**New Methods Required**:

| Protocol | Method | Purpose |
|----------|--------|---------|
| StoryRepository | get_max_id_number(component: str) -> int | Retorna maior NNN para componente |
| StoryRepository | get_max_priority() -> int | Retorna maior prioridade existente |
| StoryRepository | get_by_priority(priority: int) -> Story or None | Busca historia por prioridade |
| StoryDependencyRepository | remove_all_for_story(story_id: str) -> None | Remove todas dependencias |

### 4. DTOs Pydantic - Validacao e Conversao

**Question**: Como estruturar DTOs para validacao de entrada e conversao de entidades?

**Decision**: BaseModel Pydantic com validators e metodo classmethod from_entity

**Rationale**:
- Pydantic ja e dependencia do projeto (validation, serialization)
- Validators garantem tipos corretos antes de chegar ao dominio
- from_entity encapsula conversao, mantem DTOs independentes de entidades

### 5. Troca Atomica de Prioridades

**Question**: Como implementar swap de prioridades de forma atomica e segura?

**Decision**: Swap direto de valores de prioridade entre duas historias dentro de transacao

**Rationale**:
- SQLite com UnitOfWork garante atomicidade
- Swap de valores e mais simples que reordenacao de lista
- Nao cria gaps (troca 1:1)

### 6. Geracao de ID com Formato COMPONENTE-NNN

**Question**: Como gerar IDs unicos no formato COMPONENTE-NNN de forma thread-safe?

**Decision**: Query MAX + increment dentro de transacao UnitOfWork

**Rationale**:
- Single-user application, sem concorrencia real
- Transacao garante atomicidade da leitura + escrita
- Query simples e eficiente

## Decisions Summary

| Topic | Decision | ADR Reference |
|-------|----------|---------------|
| Remocao de dependencias | Metodo remove_all_for_story no repositorio | ADR-001 |
| Geracao de ID | Query get_max_id_number + increment | ADR-002 |
| Troca de prioridade | Query get_by_priority + swap no service | ADR-003 |
| Validacao de developer | Via DeveloperRepository.exists() | ADR-004 |
| Prioridade inicial | Logica no StoryService | ADR-005 |
| Campos na duplicacao | Lista explicita de copiados/resetados | ADR-006 |
| Gaps de prioridade | Aceitos apos delecao (sem compactacao) | ADR-007 |

## Dependencies Identified

Nenhuma nova dependencia necessaria. Todas as dependencias ja estao no pyproject.toml:
- pydantic ^2.0 (DTOs)
- aiosqlite ^0.19.0 (banco)
- pytest-asyncio ^0.23 (testes)

## Risks and Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Gaps de prioridade apos delecao | Medium | Low | Aceito por ADR-007, ordenacao funciona normalmente |
| ID duplicado em concorrencia | Low | Medium | Single-user app, transacao atomica |
| Ciclo de dependencias ao duplicar | Low | Low | Duplicacao nao copia dependencias |
